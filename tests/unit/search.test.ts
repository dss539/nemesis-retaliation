import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { executeRoomSearch } from '../../src/engine/actions/search.js';

describe('Room Search Action (ACT-SEARCH-001)', () => {
  it('searches an explored room and adds kept item to backpack', () => {
    const prng = new Mulberry32(42);
    let state = createInitialGameState({ playerCount: 1, seed: 42 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Place officer in Armory (Room 05, Section A, has Red items, 2 search tokens)
    state = {
      ...state,
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'landing-zone': {
            ...state.board.rooms['landing-zone']!,
            characterIds: [],
          },
          'slot_0_1': {
            ...state.board.rooms['slot_0_1']!,
            isDiscovered: true,
            tile: {
              tileId: '05',
              roomNumber: '05',
              name: 'ARMORY',
              sectionKind: '?',
              maxSearches: 2,
              hasComputer: false,
              actionDescription: 'Restock Ammo',
            },
            searchTokens: 2,
            characterIds: ['officer'],
          },
        },
      },
      characters: {
        ...state.characters,
        officer: {
          ...state.characters.officer!,
          currentRoomId: 'slot_0_1',
        },
      },
    };

    const res = executeRoomSearch(state, 'officer', 0, prng);

    expect(res.state).toBeDefined();
    expect(res.drawnItems.length).toBeGreaterThan(0);
    expect(res.chosenItem).toBeDefined();

    const officer = res.state.characters.officer!;
    expect(officer.inventory.backpack.length).toBe(1);
    expect(officer.inventory.backpack[0]?.title).toBe(res.chosenItem?.title);
    expect(res.state.board.rooms['slot_0_1']?.searchTokens).toBe(1);
  });

  it('rejects searching while intruders are in the room', () => {
    const prng = new Mulberry32(42);
    let state = createInitialGameState({ playerCount: 1, seed: 42 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Add an intruder to landing-zone
    state = {
      ...state,
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'landing-zone': {
            ...state.board.rooms['landing-zone']!,
            intruderIds: ['intruder-1'],
            searchTokens: 2,
          },
        },
      },
    };

    expect(() => {
      executeRoomSearch(state, 'officer', 0, prng);
    }).toThrow('Cannot search while in Combat');
  });
});
