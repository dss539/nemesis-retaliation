import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { resolveCleanupPhase } from '../../src/engine/phases/cleanup-phase.js';

describe('Cleanup Phase (RT-012)', () => {
  it('passes starting player token clockwise and refills hands up to 5', () => {
    const prng = new Mulberry32(444);
    let state = createInitialGameState({ playerCount: 2, seed: 444 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });
    state = gameReducer(state, {
      actionId: 2,
      type: 'draft_character',
      playerId: 'player-2',
      characterId: 'recon',
    });

    // Officer has 5 cards, discard 2 cards
    const officer = state.characters.officer!;
    state = {
      ...state,
      phase: 'cleanup',
      characters: {
        ...state.characters,
        officer: {
          ...officer,
          hand: officer.hand.slice(0, 3), // Only 3 cards left
          discardPile: officer.hand.slice(3),
        },
      },
    };

    const res = resolveCleanupPhase(state, prng);

    expect(res.state.round).toBe(2);
    expect(res.state.startingPlayerIndex).toBe(1); // Passed to player 2
    expect(res.state.characters.officer?.hand.length).toBe(5); // Refilled to 5
    expect(res.state.phase).toBe('player');
  });

  it('triggers game over when round 15 expires', () => {
    const prng = new Mulberry32(555);
    let state = createInitialGameState({ playerCount: 1, seed: 555 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    state = {
      ...state,
      phase: 'cleanup',
      round: 15,
    };

    const res = resolveCleanupPhase(state, prng);

    expect(res.state.round).toBe(16);
    expect(res.state.isGameOver).toBe(true);
    expect(res.state.phase).toBe('game-over');
    expect(res.events).toContain('TIME LIMIT REACHED: 15 rounds expired. Evacuation failed!');
  });
});
