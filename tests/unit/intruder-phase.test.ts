import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { resolveIntruderPhase } from '../../src/engine/phases/intruder-phase.js';
import { spawnIntruder } from '../../src/engine/combat/noise.js';

describe('Intruder Phase (RT-008)', () => {
  it('damages intruders in rooms with fire and incinerates larva', () => {
    const prng = new Mulberry32(111);
    let state = createInitialGameState({ playerCount: 1, seed: 111 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Spawn 1 adult and 1 larva in Landing Zone with fire
    let spawn1 = spawnIntruder(state, 'adult', { kind: 'room', roomId: 'landing-zone' });
    let spawn2 = spawnIntruder(spawn1.state, 'larva', { kind: 'room', roomId: 'landing-zone' });
    state = spawn2.state;

    state = {
      ...state,
      phase: 'intruder',
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'landing-zone': {
            ...state.board.rooms['landing-zone']!,
            fire: true,
          },
        },
      },
    };

    const res = resolveIntruderPhase(state, prng);

    expect(res.events).toContain('=== INTRUDER PHASE ===');
    expect(res.events).toContain('--- Step 1: Intruders Burning ---');
    // Larva should be incinerated
    expect(res.state.intruderInstances[spawn2.instanceId!]).toBeUndefined();
    // Adult should have 1 hit
    expect(res.state.intruderInstances[spawn1.instanceId!]?.currentHits).toBe(1);
    expect(res.state.phase).toBe('event');
  });

  it('absorbs intruder attack using a secure token', () => {
    const prng = new Mulberry32(222);
    let state = createInitialGameState({ playerCount: 1, seed: 222 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const spawn = spawnIntruder(state, 'adult', { kind: 'room', roomId: 'landing-zone' });
    state = spawn.state;

    // Place a secure token in Landing Zone
    state = {
      ...state,
      phase: 'intruder',
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'landing-zone': {
            ...state.board.rooms['landing-zone']!,
            secureTokens: 1,
          },
        },
      },
    };

    const initialHealth = state.characters.officer!.health;
    const res = resolveIntruderPhase(state, prng);

    // Attack was absorbed by Secure token
    expect(res.state.board.rooms['landing-zone']?.secureTokens).toBe(0);
    expect(res.state.characters.officer?.health).toBe(initialHealth); // No damage taken
    expect(res.events).toContain('Secure token absorbed attack from ADULT! Secure token discarded.');
  });
});
