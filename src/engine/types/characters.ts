/**
 * Character models and player state for Nemesis: Retaliation.
 * Derived from docs/rules/00-foundations.md and 01-round-and-turns.md.
 */

import { CharacterId, PlayerId, RoomId } from './primitives.js';
import { ActionCard, ContaminationCard, ObjectiveCard, SeriousWoundCard } from './cards.js';
import { InventoryState } from './items.js';

export interface PlayerState {
  playerId: PlayerId;
  name: string;
  characterId?: CharacterId;
  isStartingPlayer: boolean;
}

export interface CharacterDefinition {
  characterId: CharacterId;
  name: string;
  rank: number;
  maxHealth: number;
  startingOxygen: number;
  startingWeaponId: string;
  startingGearId?: string;
}

export interface CharacterState {
  characterId: CharacterId;
  playerId: PlayerId;
  name: string;
  rank: number;
  health: number;
  maxHealth: number;
  oxygen: number; // 0..5
  isSuffocating: boolean;
  seriousWounds: SeriousWoundCard[];
  currentRoomId: RoomId;
  hand: ActionCard[];
  drawDeck: ActionCard[];
  discardPile: ActionCard[];
  contaminationHand: ContaminationCard[];
  inventory: InventoryState;
  heldObjectives: ObjectiveCard[];
  selectedObjective?: ObjectiveCard;
  hasPassed: boolean;
  actionsRemaining: number; // 0, 1, or 2 during player turn
  isAlive: boolean;
  hasEscaped: boolean;
}
