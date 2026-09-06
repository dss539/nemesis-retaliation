import { describe, it, expect } from 'vitest';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { gameReducer, gameReducerWithEvents } from '../../src/engine/reducer.js';

describe('Game Reducer & Round/Turn Loop', () => {
  it('enforces monotonic actionId sequence and logs action history', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 100 });
    expect(state.lastActionId).toBe(0);
    expect(state.actionHistory).toEqual([]);

    state = gameReducer(state, {
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
      actionId: 0,
      timestamp: 1000,
    });

    expect(state.lastActionId).toBe(1);
    expect(state.actionHistory.length).toBe(1);
    expect(state.actionHistory[0]?.actionId).toBe(1);
    expect(state.actionHistory[0]?.type).toBe('draft_character');
  });

  it('handles character draft, hands, and phase transition to player phase', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 101 });
    expect(state.phase).toBe('setup');

    // Player 1 drafts Officer
    state = gameReducer(state, {
      type: 'draft_character',
      playerId: 'player-1',
      characterId: 'officer',
      actionId: 1,
      timestamp: 1,
    });

    const officer = state.characters['officer'];
    expect(officer).toBeDefined();
    expect(officer?.playerId).toBe('player-1');
    expect(officer?.health).toBe(9);
    expect(officer?.oxygen).toBe(7);
    expect(officer?.hand.length).toBe(5);
    expect(officer?.drawDeck.length).toBe(5);
    expect(officer?.currentRoomId).toBe('landing-zone');
    expect(officer?.inventory.equippedWeapon?.title).toBe('Sawed-off Shotgun');
    expect(state.board.rooms['landing-zone']?.characterIds).toContain('officer');
    // Still in setup phase because player 2 hasn't drafted
    expect(state.phase).toBe('setup');

    // Player 2 drafts Contractor
    state = gameReducer(state, {
      type: 'draft_character',
      playerId: 'player-2',
      characterId: 'contractor',
      actionId: 2,
      timestamp: 2,
    });

    const contractor = state.characters['contractor'];
    expect(contractor).toBeDefined();
    expect(contractor?.inventory.equippedWeapon?.title).toBe('Handgun');
    expect(contractor?.inventory.equippedArmor?.title).toBe('Bulletproof Vest');

    // All drafted -> phase transitions to player phase
    expect(state.phase).toBe('player');
    expect(state.round).toBe(1);
    expect(state.activePlayerIndex).toBe(0);
  });

  it('tracks 2 actions per turn and rotates to next player', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 102 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-1', characterId: 'officer', actionId: 1, timestamp: 1 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-2', characterId: 'recon', actionId: 2, timestamp: 2 });

    const officer = state.characters['officer']!;
    expect(state.activePlayerIndex).toBe(0); // Player 1
    expect(officer.actionsRemaining).toBe(2);

    // Action 1: Officer plays action card from hand
    const cardToPlay = officer.hand[0]!;
    state = gameReducer(state, {
      type: 'play_action_card',
      characterId: 'officer',
      cardId: cardToPlay.id,
      actionId: 3,
      timestamp: 3,
    });

    expect(state.characters['officer']?.actionsRemaining).toBe(1);
    expect(state.characters['officer']?.hand.length).toBe(4);
    expect(state.characters['officer']?.discardPile.length).toBe(1);
    expect(state.activePlayerIndex).toBe(0); // Still player 1's turn

    // Action 2: Officer performs a basic action (e.g. search, discarding 1 card)
    const cardToDiscard = state.characters['officer']!.hand[0]!;
    state = gameReducer(state, {
      type: 'search',
      characterId: 'officer',
      discardCardIds: [cardToDiscard.id],
      actionId: 4,
      timestamp: 4,
    });

    // Turn finished (2 actions taken) -> automatically advanced to Player 2 (Recon)!
    expect(state.activePlayerIndex).toBe(1);
    expect(state.characters['recon']?.actionsRemaining).toBe(2);
  });

  it('handles pass action and transitions to Intruder Phase when all pass', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 103 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-1', characterId: 'officer', actionId: 1, timestamp: 1 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-2', characterId: 'recon', actionId: 2, timestamp: 2 });

    // Player 1 passes
    state = gameReducer(state, {
      type: 'pass',
      characterId: 'officer',
      actionId: 3,
      timestamp: 3,
    });

    expect(state.characters['officer']?.hasPassed).toBe(true);
    expect(state.activePlayerIndex).toBe(1); // Recon's turn

    // Player 2 passes
    const result = gameReducerWithEvents(state, {
      type: 'pass',
      characterId: 'recon',
      actionId: 4,
      timestamp: 4,
    });

    // Both passed -> Phase transitions to Intruder Phase!
    expect(result.state.phase).toBe('intruder');
    expect(result.events.some(e => e.includes('All players have passed'))).toBe(true);
  });

  it('resolves oxygen loss when Life Support is inactive (RT-005)', () => {
    let state = createInitialGameState({ playerCount: 1, seed: 104 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-1', characterId: 'officer', actionId: 1, timestamp: 1 });

    // Turn off Life Support in Section A (where Landing Zone is)
    state = {
      ...state,
      lifeSupport: { ...state.lifeSupport, A: false },
    };

    expect(state.characters['officer']?.oxygen).toBe(7);

    // Officer passes (still counts as a turn for oxygen loss)
    const result = gameReducerWithEvents(state, {
      type: 'pass',
      characterId: 'officer',
      actionId: 2,
      timestamp: 2,
    });

    // Officer lost 1 Oxygen
    expect(result.state.characters['officer']?.oxygen).toBe(6);
    expect(result.events.some(e => e.includes('lost 1 Oxygen'))).toBe(true);
  });

  it('resolves fire damage when character is in a room with fire (RT-005)', () => {
    let state = createInitialGameState({ playerCount: 1, seed: 105 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-1', characterId: 'officer', actionId: 1, timestamp: 1 });

    // Place Fire in Landing Zone
    state = {
      ...state,
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

    expect(state.characters['officer']?.health).toBe(9);

    const result = gameReducerWithEvents(state, {
      type: 'pass',
      characterId: 'officer',
      actionId: 2,
      timestamp: 2,
    });

    expect(result.state.characters['officer']?.health).toBe(8);
    expect(result.events.some(e => e.includes('Fire damage'))).toBe(true);
  });

  it('cycles through full round phases and cleanup phase (RT-001, RT-012)', () => {
    let state = createInitialGameState({ playerCount: 2, seed: 106 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-1', characterId: 'officer', actionId: 1, timestamp: 1 });
    state = gameReducer(state, { type: 'draft_character', playerId: 'player-2', characterId: 'recon', actionId: 2, timestamp: 2 });

    // Both players pass -> intruder phase
    state = gameReducer(state, { type: 'pass', characterId: 'officer', actionId: 3, timestamp: 3 });
    state = gameReducer(state, { type: 'pass', characterId: 'recon', actionId: 4, timestamp: 4 });
    expect(state.phase).toBe('intruder');

    // Resolve Intruder Phase -> event phase
    state = gameReducer(state, { type: 'resolve_intruder_phase', actionId: 5, timestamp: 5 });
    expect(state.phase).toBe('event');

    // Resolve Event Phase -> cleanup phase
    state = gameReducer(state, { type: 'resolve_event_phase', actionId: 6, timestamp: 6 });
    expect(state.phase).toBe('cleanup');

    // Resolve Cleanup Phase -> advances round, rotates starting player, draws cards, back to player phase!
    state = gameReducer(state, { type: 'resolve_cleanup_phase', actionId: 7, timestamp: 7 });
    expect(state.phase).toBe('player');
    expect(state.round).toBe(2);
    expect(state.startingPlayerIndex).toBe(1); // Rotated to Player 2 (Recon)
    expect(state.activePlayerIndex).toBe(1);
    expect(state.characters['officer']?.hasPassed).toBe(false);
    expect(state.characters['recon']?.hasPassed).toBe(false);
    expect(state.characters['officer']?.hand.length).toBe(5);
    expect(state.characters['recon']?.hand.length).toBe(5);
  });
});
