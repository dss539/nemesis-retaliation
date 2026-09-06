import { describe, it, expect } from 'vitest';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { StateSerializer } from '../../src/engine/serialization/state-serializer.js';

describe('State Serialization & Deterministic Action Replay', () => {
  it('serializes and deserializes a GameState without data loss', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 777 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const json = StateSerializer.serialize(state);
    expect(typeof json).toBe('string');
    expect(json.length).toBeGreaterThan(100);

    const restored = StateSerializer.deserialize(json);
    expect(restored.gameId).toBe(state.gameId);
    expect(restored.phase).toBe(state.phase);
    expect(restored.characters.officer?.characterId).toBe('officer');
    expect(restored.board.rooms['landing-zone']?.isDiscovered).toBe(true);
  });

  it('exports action log and replays deterministically to identical final state', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 888 });

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

    // Pass turn
    state = gameReducer(state, {
      actionId: 3,
      type: 'pass',
      characterId: 'officer',
    });

    const log = StateSerializer.exportActionLog(state);
    expect(log.actions.length).toBe(3);

    const replayed = StateSerializer.replay(log);
    expect(replayed.lastActionId).toBe(state.lastActionId);
    expect(replayed.phase).toBe(state.phase);
    expect(replayed.activePlayerIndex).toBe(state.activePlayerIndex);
    expect(replayed.characters.officer?.hasPassed).toBe(true);
  });
});
