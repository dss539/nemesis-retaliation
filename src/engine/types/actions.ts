/**
 * Player and game action envelopes for Nemesis: Retaliation.
 * Pure action pattern with discriminated unions.
 * Derived from RT-004, RT-005, RT-006, RT-007, and ACT-* rules.
 */

import { CardId, CharacterId, CorridorId, ItemId, PlayerId, RoomId } from './primitives.js';

export interface BaseAction {
  actionId: number;
  timestamp: number;
}

export interface DraftCharacterAction extends BaseAction {
  type: 'draft_character';
  playerId: PlayerId;
  characterId: CharacterId;
}

export interface MoveAction extends BaseAction {
  type: 'move';
  characterId: CharacterId;
  targetRoomId: RoomId;
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface MoveCautiouslyAction extends BaseAction {
  type: 'move_cautiously';
  characterId: CharacterId;
  targetRoomId: RoomId;
  discardCardIds: [CardId, CardId]; // Cost: 2 Action cards
  chosenCorridorId?: CorridorId; // Place noise in specific corridor if rolled
}

export interface ShootAction extends BaseAction {
  type: 'shoot';
  characterId: CharacterId;
  weaponId: ItemId;
  targetIntruderId: string;
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface BurstAction extends BaseAction {
  type: 'burst';
  characterId: CharacterId;
  weaponId: ItemId;
  targetCorridorId: CorridorId;
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface MeleeAction extends BaseAction {
  type: 'melee';
  characterId: CharacterId;
  targetIntruderId: string;
  weaponId?: ItemId; // Optional melee weapon
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface SearchAction extends BaseAction {
  type: 'search';
  characterId: CharacterId;
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface UseRoomAction extends BaseAction {
  type: 'use_room';
  characterId: CharacterId;
  discardCardIds: [CardId, CardId]; // Cost: 2 Action cards
  payload?: Record<string, unknown>;
}

export interface PlayActionCardAction extends BaseAction {
  type: 'play_action_card';
  characterId: CharacterId;
  cardId: CardId;
  payload?: Record<string, unknown>;
}

export interface PlaceSecureAction extends BaseAction {
  type: 'place_secure';
  characterId: CharacterId;
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface TradeAction extends BaseAction {
  type: 'trade';
  characterId: CharacterId;
  targetCharacterId: CharacterId;
  offeredItemIds: ItemId[];
  requestedItemIds: ItemId[];
  discardCardIds: [CardId]; // Cost: 1 Action card
}

export interface ChooseObjectiveAction extends BaseAction {
  type: 'choose_objective';
  characterId: CharacterId;
  selectedObjectiveId: CardId;
}

export interface PassAction extends BaseAction {
  type: 'pass';
  characterId: CharacterId;
  discardCardIds?: CardId[]; // May discard any number of cards upon passing
}

export interface ReactionAction extends BaseAction {
  type: 'reaction';
  characterId: CharacterId;
  cardId: CardId;
  payload?: Record<string, unknown>;
}

// System phase advancement actions
export interface EndPlayerTurnAction extends BaseAction {
  type: 'end_player_turn';
  characterId: CharacterId;
}

export interface ResolveIntruderPhaseAction extends BaseAction {
  type: 'resolve_intruder_phase';
}

export interface ResolveEventPhaseAction extends BaseAction {
  type: 'resolve_event_phase';
}

export interface ResolveCleanupPhaseAction extends BaseAction {
  type: 'resolve_cleanup_phase';
}

export type GameAction =
  | DraftCharacterAction
  | MoveAction
  | MoveCautiouslyAction
  | ShootAction
  | BurstAction
  | MeleeAction
  | SearchAction
  | UseRoomAction
  | PlayActionCardAction
  | PlaceSecureAction
  | TradeAction
  | ChooseObjectiveAction
  | PassAction
  | ReactionAction
  | EndPlayerTurnAction
  | ResolveIntruderPhaseAction
  | ResolveEventPhaseAction
  | ResolveCleanupPhaseAction;
