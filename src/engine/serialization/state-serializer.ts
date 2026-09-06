/**
 * State serialization and action replay engine for Nemesis: Retaliation.
 * Pure JSON export/import and deterministic action stream replaying.
 */

import { GameState } from '../types/state.js';
import { GameAction } from '../types/actions.js';
import { gameReducer } from '../reducer.js';
import { createInitialGameState } from '../setup/initial-state.js';

export class StateSerializer {
  /**
   * Serializes a GameState to a compact JSON string.
   */
  static serialize(state: GameState): string {
    return JSON.stringify(state);
  }

  /**
   * Deserializes a GameState from a JSON string with integrity checks.
   */
  static deserialize(json: string): GameState {
    const parsed = JSON.parse(json) as GameState;
    if (!parsed.gameId || !parsed.board || !parsed.characters || !parsed.phase) {
      throw new Error('Invalid GameState JSON payload: missing core properties');
    }
    return parsed;
  }

  /**
   * Exports the action history of a game.
   */
  static exportActionLog(state: GameState): { seed: number; playerCount: number; actions: GameAction[] } {
    return {
      seed: state.seed,
      playerCount: state.players.length,
      actions: state.actionHistory,
    };
  }

  /**
   * Deterministically replays an action log from the initial setup to reproduce identical game states.
   */
  static replay(log: { seed: number; playerCount: number; actions: GameAction[] }): GameState {
    let state = createInitialGameState({ playerCount: log.playerCount, seed: log.seed });

    for (const action of log.actions) {
      state = gameReducer(state, action);
    }

    return state;
  }
}
