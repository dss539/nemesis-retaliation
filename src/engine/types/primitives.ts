/**
 * Primitive game domain types and IDs for Nemesis: Retaliation.
 * Derived from official rulebook and docs/rules/00-foundations.md.
 */

/**
 * Six pointy-top regular hexagon directions.
 * Rooms are regular pointy-top hexagons with visible corridor spacing on all 6 edges.
 * (FND-005)
 */
export type Direction = 'NE' | 'E' | 'SE' | 'SW' | 'W' | 'NW';

export const ALL_DIRECTIONS: readonly Direction[] = ['NE', 'E', 'SE', 'SW', 'W', 'NW'] as const;

/**
 * Facility sections: A, B, and C.
 */
export type Section = 'A' | 'B' | 'C';

export const ALL_SECTIONS: readonly Section[] = ['A', 'B', 'C'] as const;

/**
 * Identifiers
 */
export type PlayerId = string;

export type CharacterId =
  | 'officer'
  | 'combat-engineer'
  | 'contractor'
  | 'recon'
  | 'medical-support'
  | 'heavy-gun-operator';

export const ALL_CHARACTER_IDS: readonly CharacterId[] = [
  'officer',
  'combat-engineer',
  'contractor',
  'recon',
  'medical-support',
  'heavy-gun-operator',
] as const;

export type RoomId = string;
export type CorridorId = string;
export type CardId = string;
export type ItemId = string;
export type TokenId = string;
export type IntruderInstanceId = string;

/**
 * Room back kinds (FND-008, FND-010): A, B, C, or ?
 */
export type RoomBackType = 'A' | 'B' | 'C' | '?';

/**
 * Item types: Red (military/weapons), Yellow (technical/survival), Green (medical/scientific).
 */
export type ItemColor = 'red' | 'yellow' | 'green';

/**
 * Door physical states:
 * - open: free passage
 * - closed: blocks movement and line-of-sight/bursting
 * - destroyed: permanently open
 */
export type DoorState = 'open' | 'closed' | 'destroyed';

/**
 * Intruder classification:
 * Queen > Drone > Adult > Larva (INT-001, RT-008).
 */
export type IntruderType = 'queen' | 'drone' | 'adult' | 'larva';

export const INTRUDER_TYPE_ORDER: readonly IntruderType[] = [
  'queen',
  'drone',
  'adult',
  'larva',
] as const;

/**
 * Game phase within a round (RT-001):
 * 1. Player Phase
 * 2. Intruder Phase
 * 3. Event Phase
 * 4. Cleanup Phase
 */
export type GamePhase =
  | 'setup'
  | 'player'
  | 'intruder'
  | 'event'
  | 'cleanup'
  | 'game-over';
