/**
 * Authoritative GameState interface for Nemesis: Retaliation.
 * Pure serializable state representing complete game progress.
 */

import {
  CharacterId,
  GamePhase,
  IntruderType,
  PlayerId,
  Section,
} from './primitives.js';
import { BoardState } from './board.js';
import { CharacterState, PlayerState } from './characters.js';
import {
  ContaminationCard,
  EventCard,
  ObjectiveCard,
  SeriousWoundCard,
} from './cards.js';
import { ItemCard } from './items.js';
import {
  IntruderBagState,
  IntruderInstance,
  QueenTrackState,
} from './intruders.js';
import { GameAction } from './actions.js';

export interface AntiAircraftState {
  topToken: 'active' | 'inactive';
  bottomToken: 'active' | 'inactive';
  isKnownByPlayerIds: PlayerId[];
}

export interface AutodestructionState {
  isActive: boolean;
  roundsRemaining?: number;
}

export interface ItemDecksState {
  red: ItemCard[];
  yellow: ItemCard[];
  green: ItemCard[];
  quest: ItemCard[];
  redDiscard: ItemCard[];
  yellowDiscard: ItemCard[];
  greenDiscard: ItemCard[];
}

export interface GameResult {
  winners: PlayerId[];
  losers: PlayerId[];
  reason: string;
}

export interface GameState {
  gameId: string;
  seed: number;
  prngState: { seed: number; calls: number };
  phase: GamePhase;
  round: number; // 1..15
  startingPlayerIndex: number;
  activePlayerIndex: number;
  turnActionsTaken: number; // 0, 1, or 2

  players: PlayerState[];
  characters: Partial<Record<CharacterId, CharacterState>>;
  characterDraftPool: CharacterId[];

  board: BoardState;
  intruderBag: IntruderBagState;
  intruderInstances: Record<string, IntruderInstance>;
  intruderModelsInSupply: Record<IntruderType, number>;
  queenTrack: QueenTrackState;

  itemDecks: ItemDecksState;
  eventDeck: EventCard[];
  eventDiscard: EventCard[];
  objectiveDeck: ObjectiveCard[];
  seriousWoundsDeck: SeriousWoundCard[];
  contaminationDeck: ContaminationCard[];

  lifeSupport: Record<Section, boolean>;
  hibernatoriumActive: boolean;
  autodestruction: AutodestructionState;
  antiAircraft: AntiAircraftState;

  actionHistory: GameAction[];
  lastActionId: number;
  isGameOver: boolean;
  gameResult?: GameResult;
}
