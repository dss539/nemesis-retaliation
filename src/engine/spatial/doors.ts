/**
 * Door state machine and passage validation for Nemesis: Retaliation.
 * Derived from docs/rules/02-character-actions.md:Doors and rulebook p. 22.
 */

import { DoorState } from '../types/primitives.js';

export class DoorStateMachine {
  /**
   * Checks if a door allows movement or bursting passage.
   * Open and destroyed doors allow passage; closed doors block passage.
   */
  static allowsPassage(state: DoorState): boolean {
    return state === 'open' || state === 'destroyed';
  }

  /**
   * Opens a door. Destroyed doors remain destroyed.
   */
  static open(state: DoorState): DoorState {
    if (state === 'destroyed') return 'destroyed';
    return 'open';
  }

  /**
   * Closes a door. Destroyed doors cannot be closed.
   */
  static close(state: DoorState): DoorState {
    if (state === 'destroyed') {
      throw new Error('A destroyed door cannot be closed');
    }
    return 'closed';
  }

  /**
   * Destroys a door. Only closed doors can be destroyed (Rulebook p. 22).
   */
  static destroy(state: DoorState): DoorState {
    if (state !== 'closed') {
      throw new Error(`Only a closed door can be destroyed (current: ${state})`);
    }
    return 'destroyed';
  }
}
