import { describe, it, expect } from 'vitest';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { makeCorridorId } from '../../src/engine/spatial/hex.js';

describe('Movement & Exploration Reducer Actions', () => {
  it('moves into an undiscovered adjacent room and explores it', () => {
    const initial = createInitialGameState({ playerCount: 2, seed: 100 });

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

    const officer = state.characters.officer!;
    expect(officer.currentRoomId).toBe('landing-zone');
    expect(officer.hand.length).toBe(5);

    const costCardId = officer.hand[0]!.id;
    const targetRoomId = 'slot_1_2';

    // Officer moves to slot_1_2
    const nextState = gameReducer(state, {
      actionId: 3,
      type: 'move',
      characterId: 'officer',
      targetRoomId,
      discardCardIds: [costCardId],
    });

    const updatedOfficer = nextState.characters.officer!;
    expect(updatedOfficer.currentRoomId).toBe(targetRoomId);
    expect(updatedOfficer.hand.length).toBe(4);
    expect(updatedOfficer.actionsRemaining).toBe(1);
    expect(nextState.board.rooms[targetRoomId]?.isDiscovered).toBe(true);
    expect(nextState.board.rooms[targetRoomId]?.tile).toBeDefined();
  });

  it('rejects moving through a closed door', () => {
    const initial = createInitialGameState({ playerCount: 1, seed: 100 });

    let state = gameReducer(initial, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Close the door on corridor connecting landing-zone and slot_1_2
    const corridorId = makeCorridorId('landing-zone', 'slot_1_2');
    state = {
      ...state,
      board: {
        ...state.board,
        corridors: {
          ...state.board.corridors,
          [corridorId]: {
            ...state.board.corridors[corridorId]!,
            doorState: 'closed',
          },
        },
      },
    };

    const costCardId = state.characters.officer!.hand[0]!.id;

    expect(() => {
      gameReducer(state, {
        actionId: 2,
        type: 'move',
        characterId: 'officer',
        targetRoomId: 'slot_1_2',
        discardCardIds: [costCardId],
      });
    }).toThrow('Cannot pass through closed door');
  });

  it('allows moving cautiously with 2 cards and places a secure token', () => {
    const initial = createInitialGameState({ playerCount: 1, seed: 200 });

    let state = gameReducer(initial, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    const officer = state.characters.officer!;
    const costCard1 = officer.hand[0]!.id;
    const costCard2 = officer.hand[1]!.id;
    const targetRoomId = 'slot_0_1';

    const nextState = gameReducer(state, {
      actionId: 2,
      type: 'move_cautiously',
      characterId: 'officer',
      targetRoomId,
      discardCardIds: [costCard1, costCard2],
    });

    const updatedOfficer = nextState.characters.officer!;
    expect(updatedOfficer.currentRoomId).toBe(targetRoomId);
    expect(updatedOfficer.hand.length).toBe(3);
    expect(nextState.board.rooms[targetRoomId]?.secureTokens).toBe(1);
  });
});
