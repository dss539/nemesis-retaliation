import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';
import { executeRoomAction } from '../../src/engine/actions/room-actions.js';

describe('Room Actions System Across 25 Official Rooms', () => {
  it('extinguishes all fire in section via Sprinklers Control (Room 01)', () => {
    const prng = new Mulberry32(1);
    let state = createInitialGameState({ playerCount: 1, seed: 1 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Place officer in Sprinklers Control (01, Section A) and set fire in Landing Zone (Section A)
    state = {
      ...state,
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'landing-zone': {
            ...state.board.rooms['landing-zone']!,
            fire: true,
            characterIds: [],
          },
          'slot_0_1': {
            ...state.board.rooms['slot_0_1']!,
            isDiscovered: true,
            fire: true,
            tile: {
              tileId: '01',
              roomNumber: '01',
              name: 'SPRINKLERS CONTROL',
              sectionKind: '?',
              maxSearches: 2,
              hasComputer: true,
              actionDescription: 'Discard all fire from section',
            },
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

    const res = executeRoomAction(state, 'officer', prng, { targetSection: 'A' });

    expect(res.state.board.rooms['landing-zone']?.fire).toBe(false);
    expect(res.state.board.rooms['slot_0_1']?.fire).toBe(false);
    expect(res.events).toContain('Extinguished Fire in LANDING ZONE');
  });

  it('heals HP in Emergency Room (Room 03)', () => {
    const prng = new Mulberry32(2);
    let state = createInitialGameState({ playerCount: 1, seed: 2 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    // Damage officer to 5 HP and place in Emergency Room
    state = {
      ...state,
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'slot_0_1': {
            ...state.board.rooms['slot_0_1']!,
            isDiscovered: true,
            tile: {
              tileId: '03',
              roomNumber: '03',
              name: 'EMERGENCY ROOM',
              sectionKind: '?',
              maxSearches: 2,
              hasComputer: false,
              actionDescription: 'Heal wounds',
            },
            characterIds: ['officer'],
          },
        },
      },
      characters: {
        ...state.characters,
        officer: {
          ...state.characters.officer!,
          health: 5,
          currentRoomId: 'slot_0_1',
        },
      },
    };

    const res = executeRoomAction(state, 'officer', prng);

    expect(res.state.characters.officer?.health).toBe(7);
    expect(res.events).toContain('Treated in Emergency Room: healed to 7/9 HP');
  });

  it('initiates and aborts self-destruct in Reactor (Room 23)', () => {
    const prng = new Mulberry32(3);
    let state = createInitialGameState({ playerCount: 1, seed: 3 });

    state = gameReducer(state, {
      actionId: 1,
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
    });

    state = {
      ...state,
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'slot_0_1': {
            ...state.board.rooms['slot_0_1']!,
            isDiscovered: true,
            tile: {
              tileId: '23',
              roomNumber: '23',
              name: 'REACTOR',
              sectionKind: 'C',
              maxSearches: 2,
              hasComputer: false,
              actionDescription: 'Reactor control',
            },
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

    // First activation starts self-destruct
    const res1 = executeRoomAction(state, 'officer', prng);
    expect(res1.state.autodestruction.isActive).toBe(true);
    expect(res1.state.autodestruction.roundsRemaining).toBe(5);

    // Second activation aborts self-destruct
    const res2 = executeRoomAction(res1.state, 'officer', prng);
    expect(res2.state.autodestruction.isActive).toBe(false);
  });
});
