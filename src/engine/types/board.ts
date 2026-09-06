/**
 * Spatial and board representations for Nemesis: Retaliation.
 * Pointy-top hex grid with corridor networks and door mechanics.
 * Derived from docs/rules/00-foundations.md (FND-005, FND-006, FND-008).
 */

import {
  CharacterId,
  CorridorId,
  Direction,
  DoorState,
  IntruderInstanceId,
  RoomBackType,
  RoomId,
  Section,
} from './primitives.js';

/**
 * Cube coordinates for pointy-top regular hexagons:
 * Invariant: q + r + s === 0
 */
export interface HexCoord {
  readonly q: number;
  readonly r: number;
  readonly s: number;
}

export function createHexCoord(q: number, r: number): HexCoord {
  return { q, r, s: -q - r };
}

export interface RoomTileData {
  tileId: string;
  name: string;
  roomNumber?: string; // e.g. "08" for Gunnery Room
  sectionKind: RoomBackType;
  maxSearches: number;
  hasComputer: boolean;
  actionDescription?: string;
}

export interface RoomSlotState {
  slotId: RoomId;
  coord: HexCoord;
  section: Section;
  isLandingZone: boolean;
  isDiscovered: boolean;
  tile?: RoomTileData;
  searchTokens: number; // Remaining items to search
  fire: boolean;
  malfunction: boolean;
  secureTokens: number;
  eggTokens: number;
  dataTokens: number;
  universalMarkers: number;
  characterIds: CharacterId[];
  intruderIds: IntruderInstanceId[];
}

export interface CorridorState {
  corridorId: CorridorId;
  slotA: RoomId;
  slotB: RoomId;
  directionFromA: Direction;
  noiseValue: number; // 1..4 (0 for reinforced)
  hasNoise: boolean;
  doorState: DoorState;
  isTechnical: boolean;
  intruderIds: IntruderInstanceId[];
}

export interface BoardState {
  rooms: Record<RoomId, RoomSlotState>;
  corridors: Record<CorridorId, CorridorState>;
}
