/**
 * Pointy-top hex grid math and topology for Nemesis: Retaliation.
 * 23 fixed board slots in a 5/4/5/4/5 arrangement across Sections A, B, and C.
 * Derived from official rulebook p. 19-21 and docs/rules/00-foundations.md (FND-005, FND-006).
 */

import { Direction, Section } from '../types/primitives.js';

export interface GridPos {
  readonly x: number;
  readonly y: number;
}

export interface BoardSlotDefinition {
  readonly slotId: string;
  readonly x: number;
  readonly y: number;
  readonly section: Section;
  readonly isLandingZone: boolean;
}

/**
 * 23-slot fixed field, 5/4/5/4/5, odd rows offset half a step right.
 * Landing Zone is fixed at (0, 2) in Section A.
 */
export const BOARD_SLOTS: readonly BoardSlotDefinition[] = (() => {
  const slots: BoardSlotDefinition[] = [];
  for (let y = 0; y < 5; y++) {
    const cols = y % 2 === 0 ? 5 : 4;
    for (let x = 0; x < cols; x++) {
      const section = computeSection(x, y);
      const isLandingZone = x === 0 && y === 2;
      const slotId = isLandingZone ? 'landing-zone' : `slot_${x}_${y}`;
      slots.push({ slotId, x, y, section, isLandingZone });
    }
  }
  return slots;
})();

export const BOARD_SLOTS_BY_ID: Readonly<Record<string, BoardSlotDefinition>> =
  Object.fromEntries(BOARD_SLOTS.map(s => [s.slotId, s]));

/**
 * Section partition: vertical thirds across the facility.
 * c = x + (y % 2 ? 0.5 : 0)
 * c < 1.25 -> Section A (West / Entrance)
 * c < 2.75 -> Section B (Middle)
 * c >= 2.75 -> Section C (East / Core)
 */
export function computeSection(x: number, y: number): Section {
  const c = x + (y % 2 !== 0 ? 0.5 : 0);
  if (c < 1.25) return 'A';
  if (c < 2.75) return 'B';
  return 'C';
}

/**
 * Validates if given coordinates correspond to one of the 23 valid board slots.
 */
export function isValidSlot(x: number, y: number): boolean {
  if (y < 0 || y >= 5) return false;
  const maxCols = y % 2 === 0 ? 5 : 4;
  return x >= 0 && x < maxCols;
}

/**
 * Gets the canonical slot ID for a grid position.
 */
export function getSlotId(x: number, y: number): string {
  return (x === 0 && y === 2) ? 'landing-zone' : `slot_${x}_${y}`;
}

/**
 * Returns the opposite direction for a pointy-top hexagon.
 */
export function getOppositeDirection(dir: Direction): Direction {
  switch (dir) {
    case 'NE': return 'SW';
    case 'E':  return 'W';
    case 'SE': return 'NW';
    case 'SW': return 'NE';
    case 'W':  return 'E';
    case 'NW': return 'SE';
  }
}

/**
 * Returns the grid coordinates of the neighbor in the given direction, or null if off-board.
 */
export function getNeighborPos(pos: GridPos, dir: Direction): GridPos | null {
  const odd = pos.y % 2 !== 0;
  let targetX = pos.x;
  let targetY = pos.y;

  switch (dir) {
    case 'W':
      targetX = pos.x - 1;
      break;
    case 'E':
      targetX = pos.x + 1;
      break;
    case 'NW':
      targetX = odd ? pos.x : pos.x - 1;
      targetY = pos.y - 1;
      break;
    case 'NE':
      targetX = odd ? pos.x + 1 : pos.x;
      targetY = pos.y - 1;
      break;
    case 'SW':
      targetX = odd ? pos.x : pos.x - 1;
      targetY = pos.y + 1;
      break;
    case 'SE':
      targetX = odd ? pos.x + 1 : pos.x;
      targetY = pos.y + 1;
      break;
  }

  if (isValidSlot(targetX, targetY)) {
    return { x: targetX, y: targetY };
  }
  return null;
}

/**
 * Returns all valid on-board neighbors with their connecting directions.
 */
export function getValidNeighbors(pos: GridPos): Partial<Record<Direction, GridPos>> {
  const result: Partial<Record<Direction, GridPos>> = {};
  const directions: Direction[] = ['NE', 'E', 'SE', 'SW', 'W', 'NW'];
  for (const dir of directions) {
    const neighbor = getNeighborPos(pos, dir);
    if (neighbor) {
      result[dir] = neighbor;
    }
  }
  return result;
}

/**
 * Checks if two positions are adjacent on the hex grid.
 */
export function isAdjacent(a: GridPos, b: GridPos): boolean {
  const neighbors = getValidNeighbors(a);
  return Object.values(neighbors).some(n => n?.x === b.x && n?.y === b.y);
}

/**
 * Finds the direction from pos A to adjacent pos B, or null if not adjacent.
 */
export function getDirectionBetween(from: GridPos, to: GridPos): Direction | null {
  const neighbors = getValidNeighbors(from);
  for (const [dir, pos] of Object.entries(neighbors)) {
    if (pos && pos.x === to.x && pos.y === to.y) {
      return dir as Direction;
    }
  }
  return null;
}

/**
 * Converts offset (x, y) to cube coordinates (q, r, s) for distance calculations.
 * Odd-r layout (odd rows shifted right by +1/2).
 */
export function toCubeCoord(pos: GridPos): { q: number; r: number; s: number } {
  const q = pos.x - (pos.y - (pos.y & 1)) / 2;
  const r = pos.y;
  const s = -q - r;
  return { q, r, s };
}

/**
 * Calculates hex distance (minimum number of room hops) between two slots.
 */
export function hexDistance(a: GridPos, b: GridPos): number {
  const aCube = toCubeCoord(a);
  const bCube = toCubeCoord(b);
  return Math.max(
    Math.abs(aCube.q - bCube.q),
    Math.abs(aCube.r - bCube.r),
    Math.abs(aCube.s - bCube.s),
  );
}

/**
 * Generates a canonical Corridor ID between two slots.
 */
export function makeCorridorId(slotAId: string, slotBId: string): string {
  return slotAId < slotBId ? `c_${slotAId}__${slotBId}` : `c_${slotBId}__${slotAId}`;
}
