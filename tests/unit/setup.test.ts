import { describe, it, expect } from 'vitest';
import { createInitialGameState } from '../../src/engine/setup/initial-state.js';
import { INTRUDER_TOKEN_SUPPLY } from '../../src/engine/types/intruders.js';

describe('Game Setup & Initial State', () => {
  it('creates a deterministic initial state for 3 players given a seed', () => {
    const state1 = createInitialGameState({ playerCount: 3, seed: 424242 });
    const state2 = createInitialGameState({ playerCount: 3, seed: 424242 });

    expect(state1).toEqual(state2);
    expect(state1.players.length).toBe(3);
    expect(state1.players[0]?.isStartingPlayer).toBe(true);
    expect(state1.players[1]?.isStartingPlayer).toBe(false);
    expect(state1.players[2]?.isStartingPlayer).toBe(false);
  });

  it('sets up the Intruder Bag according to INT-001', () => {
    for (const playerCount of [1, 2, 3, 4, 5]) {
      const state = createInitialGameState({ playerCount, seed: 1000 + playerCount });
      const bag = state.intruderBag;

      const blankCount = bag.tokensInBag.filter(t => t.type === 'blank').length;
      const larvaCount = bag.tokensInBag.filter(t => t.type === 'larva').length;
      const adultCount = bag.tokensInBag.filter(t => t.type === 'adult').length;
      const queenCount = bag.tokensInBag.filter(t => t.type === 'queen').length;
      const droneCount = bag.tokensInBag.filter(t => t.type === 'drone').length;

      // INT-001: 1 Blank, 2 Larva, (3 + playerCount) Adult
      expect(blankCount).toBe(1);
      expect(larvaCount).toBe(2);
      expect(adultCount).toBe(3 + playerCount);
      expect(queenCount).toBe(0);
      expect(droneCount).toBe(0);

      // Verify total token counts across bag + pool equals physical supply (40 tokens)
      const allTokens = [...bag.tokensInBag, ...bag.tokensInPool];
      expect(allTokens.length).toBe(40);

      for (const [type, expectedTotal] of Object.entries(INTRUDER_TOKEN_SUPPLY)) {
        const count = allTokens.filter(t => t.type === type).length;
        expect(count).toBe(expectedTotal);
      }

      expect(bag.isQueenAlive).toBe(true);
    }
  });

  it('initializes the board with Landing Zone discovered at (0, 2) in Section A', () => {
    const state = createInitialGameState({ playerCount: 2, seed: 999 });
    const lz = state.board.rooms['landing-zone'];

    expect(lz).toBeDefined();
    expect(lz?.isLandingZone).toBe(true);
    expect(lz?.isDiscovered).toBe(true);
    expect(lz?.section).toBe('A');
    expect(lz?.coord).toEqual({ q: 0, r: 2, s: -2 });
    expect(lz?.tile?.roomNumber).toBe('14');
    expect(lz?.tile?.name).toBe('LANDING ZONE');

    // All other 22 slots are undiscovered
    const otherRooms = Object.values(state.board.rooms).filter(r => !r.isLandingZone);
    expect(otherRooms.length).toBe(22);
    expect(otherRooms.every(r => !r.isDiscovered)).toBe(true);

    // Corridors connect Landing Zone to its neighbors
    const corridors = Object.values(state.board.corridors);
    expect(corridors.length).toBeGreaterThan(0);
    expect(corridors.every(c => c.slotA === 'landing-zone' || c.slotB === 'landing-zone')).toBe(true);
    expect(corridors.every(c => c.noiseValue >= 1 && c.noiseValue <= 4)).toBe(true);
  });

  it('initializes item and contamination decks', () => {
    const state = createInitialGameState({ playerCount: 4, seed: 123 });

    expect(state.itemDecks.red.length).toBeGreaterThan(0);
    expect(state.itemDecks.yellow.length).toBeGreaterThan(0);
    expect(state.itemDecks.green.length).toBeGreaterThan(0);

    // Contamination deck has 27 cards (20 clean, 7 infected)
    expect(state.contaminationDeck.length).toBe(27);
    const infected = state.contaminationDeck.filter(c => c.isInfected).length;
    expect(infected).toBe(7);
  });

  it('initializes facility systems active by default', () => {
    const state = createInitialGameState({ playerCount: 2, seed: 555 });
    expect(state.lifeSupport).toEqual({ A: true, B: true, C: true });
    expect(state.hibernatoriumActive).toBe(false);
    expect(state.autodestruction.isActive).toBe(false);
    expect(state.round).toBe(1);
    expect(state.phase).toBe('setup');
  });
});
