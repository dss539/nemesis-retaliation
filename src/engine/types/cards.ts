/**
 * Card models for Nemesis: Retaliation.
 * Derived from docs/rules/02-character-actions.md, 01-round-and-turns.md, and card-text-corpus.
 */

import { CardId, CharacterId, Direction } from './primitives.js';

export interface ActionCard {
  id: CardId;
  title: string;
  characterId: CharacterId | 'support';
  usableInCombat: boolean; // True if usable in combat; false if prohibited when intruders are present in character's room
  isReaction: boolean;
  rulesText: string;
}

export interface ContaminationCard {
  id: CardId;
  isInfected: boolean; // Hidden until scanned or resolved at rest/game end
}

export interface SeriousWoundCard {
  id: CardId;
  title: string;
  isTreated: boolean;
  effectText: string;
}

export type EventIntruderMovement =
  | Direction
  | 'corridorEW'
  | 'corridorNESW'
  | 'corridorNWSE'
  | 'all';

export interface EventCard {
  id: CardId;
  title: string;
  intruderMovement: EventIntruderMovement;
  mainEffect: string;
  secondaryEffect: string;
}

export interface ObjectiveCard {
  id: CardId;
  title: string;
  minCharacters?: number;
  restrictedForPlayerNumber?: number;
  goalDescription: string;
}
