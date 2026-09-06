import { describe, it, expect } from 'vitest';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer } from '../../src/engine/reducer.js';

describe('Action Card Combat Restrictions', () => {
  it('prohibits playing a combatRestricted card while in a room with an intruder', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 987 });

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

    const officer = state.characters.officer!;

    // Find a combatRestricted card in hand or force one into hand
    let restrictedCard = officer.hand.find(c => c.combatRestricted);
    if (!restrictedCard) {
      // Find one in deck and put in hand
      const fromDeck = officer.drawDeck.find(c => c.combatRestricted);
      expect(fromDeck).toBeDefined();
      state = {
        ...state,
        characters: {
          ...state.characters,
          officer: {
            ...officer,
            hand: [fromDeck!, ...officer.hand.slice(1)],
          },
        },
      };
      restrictedCard = fromDeck!;
    }

    // Place an intruder in Landing Zone (where Officer currently is)
    state = {
      ...state,
      board: {
        ...state.board,
        rooms: {
          ...state.board.rooms,
          'landing-zone': {
            ...state.board.rooms['landing-zone']!,
            intruderIds: ['intruder-test-1'],
          },
        },
      },
    };

    // Attempting to play the combatRestricted card should throw
    expect(() => {
      gameReducer(state, {
        actionId: 3,
        type: 'play_action_card',
        characterId: 'officer',
        cardId: restrictedCard!.id,
      });
    }).toThrow(/character is in combat/);
  });
});
