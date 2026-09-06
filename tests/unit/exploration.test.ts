import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { executeExplorationSequence } from '../../src/engine/spatial/exploration.js';

describe('Exploration Sequence System (ACT-EXPLORE-001, SEM-Q-002)', () => {
  it('explores an undiscovered room slot and places room tile, corridors, and tokens', () => {
    const prng = new Mulberry32(42);
    const initial = createInitialGameState({ playerCount: 2, seed: 42 });

    let state = gameReducer(initial, {
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

    // Landing zone is at (0, 2). Target slot is (1, 2) [adjacent east neighbor]
    const targetRoomId = 'slot_1_2';
    const enteredCorridorId = 'c_landing-zone_slot_1_2';

    const res = executeExplorationSequence(
      state,
      'officer',
      enteredCorridorId,
      targetRoomId,
      prng,
      false,
    );

    expect(res.state).toBeDefined();
    expect(res.placedRoom).toBeDefined();
    expect(res.state.board.rooms[targetRoomId]?.isDiscovered).toBe(true);
    expect(res.state.board.rooms[targetRoomId]?.tile).toBeDefined();
    expect(res.state.characters.officer?.currentRoomId).toBe(targetRoomId);
    expect(res.events.length).toBeGreaterThan(0);
  });

  it('places a secure token when moving cautiously into an undiscovered room', () => {
    const prng = new Mulberry32(101);
    const initial = createInitialGameState({ playerCount: 1, seed: 101 });

    let state = gameReducer(initial, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const targetRoomId = 'slot_0_1';
    const enteredCorridorId = 'c_landing-zone_slot_0_1';

    const res = executeExplorationSequence(
      state,
      'officer',
      enteredCorridorId,
      targetRoomId,
      prng,
      true, // Cautious
    );

    expect(res.state.board.rooms[targetRoomId]?.secureTokens).toBe(1);
    expect(res.events).toContain('Placed Secure token (Cautious movement) in ' + res.placedRoom.name);
  });
});
