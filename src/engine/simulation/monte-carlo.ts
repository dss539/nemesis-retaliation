/**
 * Headless Monte Carlo simulation runner and invariant fuzzing engine.
 * Simulates thousands of automated games to verify absence of deadlocks and rule invariant preservation.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { GameAction } from '../types/actions.js';
import { createInitialGameState } from '../setup/initial-state.js';
import { gameReducer } from '../reducer.js';
import { RoomId } from '../types/primitives.js';

export interface SimulationResult {
  completed: boolean;
  roundsPlayed: number;
  totalActions: number;
  finalPhase: string;
  gameResult?: GameState['gameResult'];
  violations: string[];
}

export class MonteCarloSimulator {
  /**
   * Runs a complete simulated game from setup to termination.
   * Max steps threshold prevents infinite loops.
   */
  static runGame(playerCount: number, seed: number, maxSteps: number = 2000): SimulationResult {
    const prng = new Mulberry32(seed);
    let state = createInitialGameState({ playerCount, seed });
    let actionIdCounter = 0;
    const violations: string[] = [];

    while (!state.isGameOver && actionIdCounter < maxSteps) {
      const nextAction = this.generateBotAction(state, prng, ++actionIdCounter);
      if (!nextAction) {
        violations.push(`Deadlock: No legal action could be generated in phase ${state.phase}`);
        break;
      }

      try {
        state = gameReducer(state, nextAction);
      } catch (err: any) {
        violations.push(`Action execution error: ${err.message}`);
        break;
      }

      // Assert invariants
      const invErrors = this.checkInvariants(state);
      if (invErrors.length > 0) {
        violations.push(...invErrors);
        break;
      }

      if (state.phase === 'game-over') {
        break;
      }
    }

    return {
      completed: state.isGameOver,
      roundsPlayed: state.round,
      totalActions: actionIdCounter,
      finalPhase: state.phase,
      gameResult: state.gameResult,
      violations,
    };
  }

  private static generateBotAction(state: GameState, prng: Mulberry32, nextActionId: number): GameAction | null {
    // 1. Setup Phase: Draft characters
    if (state.phase === 'setup') {
      const activePlayer = state.players[state.activePlayerIndex]!;
      const availableChar = state.characterDraftPool[0];
      if (!availableChar) return null;
      return {
        actionId: nextActionId,
        type: 'draft_character',
        playerId: activePlayer.playerId,
        characterId: availableChar,
      };
    }

    // 2. Intruder Phase
    if (state.phase === 'intruder') {
      return {
        actionId: nextActionId,
        type: 'resolve_intruder_phase',
      };
    }

    // 3. Event Phase
    if (state.phase === 'event') {
      return {
        actionId: nextActionId,
        type: 'resolve_event_phase',
      };
    }

    // 4. Cleanup Phase
    if (state.phase === 'cleanup') {
      return {
        actionId: nextActionId,
        type: 'resolve_cleanup_phase',
      };
    }

    // 5. Player Phase
    if (state.phase === 'player') {
      const activePlayer = state.players[state.activePlayerIndex];
      if (!activePlayer || !activePlayer.characterId) return null;

      const char = state.characters[activePlayer.characterId];
      if (!char || !char.isAlive || char.hasPassed || char.hasEscaped) {
        return {
          actionId: nextActionId,
          type: 'end_player_turn',
          characterId: activePlayer.characterId,
        };
      }

      if (char.hand.length === 0) {
        return {
          actionId: nextActionId,
          type: 'pass',
          characterId: char.characterId,
        };
      }

      const room = state.board.rooms[char.currentRoomId];
      if (!room) return null;

      // In combat (Intruders in room): Shoot or Melee
      if (room.intruderIds.length > 0) {
        const targetIntruderId = room.intruderIds[0]!;
        const weapon = char.inventory.equippedWeapon;
        if (weapon && (weapon.requiresNoAmmo || (weapon.ammo ?? 0) > 0) && char.hand.length >= 1) {
          const costCard = char.hand[0]!;
          return {
            actionId: nextActionId,
            type: 'shoot',
            characterId: char.characterId,
            targetIntruderId,
            weaponId: weapon.id,
            discardCardIds: [costCard.id],
          };
        }
        if (char.hand.length >= 1) {
          const costCard = char.hand[0]!;
          return {
            actionId: nextActionId,
            type: 'melee',
            characterId: char.characterId,
            targetIntruderId,
            discardCardIds: [costCard.id],
          };
        }
      }

      // Not in combat: Try Movement
      const adjacentCorridors = Object.values(state.board.corridors).filter(
        c => (c.slotA === char.currentRoomId || c.slotB === char.currentRoomId) && c.doorState !== 'closed',
      );

      if (adjacentCorridors.length > 0 && char.hand.length >= 1 && prng.next() < 0.7) {
        const corr = adjacentCorridors[prng.nextInt(0, adjacentCorridors.length - 1)]!;
        const targetRoomId = (corr.slotA === char.currentRoomId ? corr.slotB : corr.slotA) as RoomId;
        const costCard = char.hand[0]!;
        return {
          actionId: nextActionId,
          type: 'move',
          characterId: char.characterId,
          targetRoomId,
          discardCardIds: [costCard.id],
        };
      }

      // Try Search if room has items
      if (room.searchTokens > 0 && char.hand.length >= 1 && prng.next() < 0.5) {
        const costCard = char.hand[0]!;
        return {
          actionId: nextActionId,
          type: 'search',
          characterId: char.characterId,
          discardCardIds: [costCard.id],
          chosenItemIndexToKeep: 0,
        };
      }

      // Otherwise Place Secure token or Pass
      if (char.hand.length >= 2 && prng.next() < 0.5) {
        const costCard = char.hand[0]!;
        return {
          actionId: nextActionId,
          type: 'place_secure',
          characterId: char.characterId,
          discardCardIds: [costCard.id],
        };
      }

      return {
        actionId: nextActionId,
        type: 'pass',
        characterId: char.characterId,
      };
    }

    return null;
  }

  private static checkInvariants(state: GameState): string[] {
    const errors: string[] = [];

    // 1. Oxygen and Health invariants
    for (const char of Object.values(state.characters)) {
      if (!char) continue;
      if (char.health < 0) errors.push(`Invariant violation: ${char.name} has negative health (${char.health})`);
      if (char.oxygen < 0) errors.push(`Invariant violation: ${char.name} has negative oxygen (${char.oxygen})`);
    }

    // 2. Intruder model bounds
    if (state.intruderModelsInSupply.queen < 0 || state.intruderModelsInSupply.queen > 1) {
      errors.push(`Invariant violation: Queen supply out of bounds (${state.intruderModelsInSupply.queen})`);
    }
    if (state.intruderModelsInSupply.drone < 0 || state.intruderModelsInSupply.drone > 8) {
      errors.push(`Invariant violation: Drone supply out of bounds (${state.intruderModelsInSupply.drone})`);
    }
    if (state.intruderModelsInSupply.adult < 0 || state.intruderModelsInSupply.adult > 36) {
      errors.push(`Invariant violation: Adult supply out of bounds (${state.intruderModelsInSupply.adult})`);
    }
    if (state.intruderModelsInSupply.larva < 0 || state.intruderModelsInSupply.larva > 6) {
      errors.push(`Invariant violation: Larva supply out of bounds (${state.intruderModelsInSupply.larva})`);
    }

    // 3. Bag total tokens <= 40
    const totalBagTokens = state.intruderBag.tokensInBag.length + state.intruderBag.tokensInPool.length;
    if (totalBagTokens > 40) {
      errors.push(`Invariant violation: Total bag tokens exceed 40 (${totalBagTokens})`);
    }

    // 4. Action sequence strictly incrementing
    if (state.lastActionId !== state.actionHistory.length) {
      errors.push(`Invariant violation: lastActionId mismatch (${state.lastActionId} vs history ${state.actionHistory.length})`);
    }

    return errors;
  }
}
