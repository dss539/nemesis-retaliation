import { describe, it, expect } from 'vitest';
import {
  BOARD_SLOTS,
  BOARD_SLOTS_BY_ID,
  computeSection,
  getDirectionBetween,
  getNeighborPos,
  getOppositeDirection,
  getValidNeighbors,
  hexDistance,
  isAdjacent,
  isValidSlot,
  makeCorridorId,
} from '../../src/engine/spatial/hex.js';

describe('Hex Grid Spatial Engine', () => {
  it('defines exactly 23 board slots in a 5/4/5/4/5 layout', () => {
    expect(BOARD_SLOTS.length).toBe(23);

    const countsByRow: number[] = [0, 0, 0, 0, 0];
    for (const slot of BOARD_SLOTS) {
      countsByRow[slot.y] = (countsByRow[slot.y] ?? 0) + 1;
    }
    expect(countsByRow).toEqual([5, 4, 5, 4, 5]);
  });

  it('places Landing Zone at (0, 2) in Section A', () => {
    const lz = BOARD_SLOTS_BY_ID['landing-zone'];
    expect(lz).toBeDefined();
    expect(lz?.x).toBe(0);
    expect(lz?.y).toBe(2);
    expect(lz?.section).toBe('A');
    expect(lz?.isLandingZone).toBe(true);
  });

  it('correctly partitions slots into vertical third sections A, B, and C', () => {
    // West column (x=0) is in Section A
    expect(computeSection(0, 0)).toBe('A');
    expect(computeSection(0, 2)).toBe('A');

    // Middle column (x=2) is in Section B
    expect(computeSection(2, 0)).toBe('B');
    expect(computeSection(2, 2)).toBe('B');

    // East column (x=4) is in Section C
    expect(computeSection(4, 0)).toBe('C');
    expect(computeSection(4, 2)).toBe('C');
  });

  it('computes reciprocal neighbors and opposite directions', () => {
    const directions = ['NE', 'E', 'SE', 'SW', 'W', 'NW'] as const;
    for (const dir of directions) {
      const opp = getOppositeDirection(dir);
      expect(getOppositeDirection(opp)).toBe(dir);
    }

    // Check interior slot (2, 2) on an even row
    const centerPos = { x: 2, y: 2 };
    const neighbors = getValidNeighbors(centerPos);
    expect(Object.keys(neighbors).length).toBe(6);

    for (const [dir, neighborPos] of Object.entries(neighbors)) {
      if (!neighborPos) continue;
      const reverseDir = getDirectionBetween(neighborPos, centerPos);
      expect(reverseDir).toBe(getOppositeDirection(dir as any));
    }
  });

  it('matches odd-row and even-row neighbor expectations from regression', () => {
    // Even row (3, 2)
    expect(getNeighborPos({ x: 3, y: 2 }, 'NE')).toEqual({ x: 3, y: 1 });
    expect(getNeighborPos({ x: 3, y: 2 }, 'E')).toEqual({ x: 4, y: 2 });
    expect(getNeighborPos({ x: 3, y: 2 }, 'SE')).toEqual({ x: 3, y: 3 });
    expect(getNeighborPos({ x: 3, y: 2 }, 'SW')).toEqual({ x: 2, y: 3 });
    expect(getNeighborPos({ x: 3, y: 2 }, 'W')).toEqual({ x: 2, y: 2 });
    expect(getNeighborPos({ x: 3, y: 2 }, 'NW')).toEqual({ x: 2, y: 1 });

    // Odd row interior slot (2, 3)
    expect(getNeighborPos({ x: 2, y: 3 }, 'NE')).toEqual({ x: 3, y: 2 });
    expect(getNeighborPos({ x: 2, y: 3 }, 'E')).toEqual({ x: 3, y: 3 });
    expect(getNeighborPos({ x: 2, y: 3 }, 'SE')).toEqual({ x: 3, y: 4 });
    expect(getNeighborPos({ x: 2, y: 3 }, 'SW')).toEqual({ x: 2, y: 4 });
    expect(getNeighborPos({ x: 2, y: 3 }, 'W')).toEqual({ x: 1, y: 3 });
    expect(getNeighborPos({ x: 2, y: 3 }, 'NW')).toEqual({ x: 2, y: 2 });

    // Edge of odd row (3, 3) going East is off-board
    expect(getNeighborPos({ x: 3, y: 3 }, 'E')).toBeNull();
  });

  it('rejects off-board coordinates', () => {
    expect(isValidSlot(-1, 0)).toBe(false);
    expect(isValidSlot(5, 0)).toBe(false); // Row 0 has max 5 (0..4)
    expect(isValidSlot(4, 1)).toBe(false); // Row 1 has max 4 (0..3)
    expect(isValidSlot(0, 5)).toBe(false); // Max row is 4
  });

  it('calculates hex distance correctly', () => {
    expect(hexDistance({ x: 0, y: 2 }, { x: 0, y: 2 })).toBe(0);
    // Adjacent is distance 1
    expect(hexDistance({ x: 0, y: 2 }, { x: 1, y: 2 })).toBe(1);
    // Across the board
    const dist = hexDistance({ x: 0, y: 2 }, { x: 4, y: 2 });
    expect(dist).toBe(4);
  });

  it('determines adjacency and canonical corridor IDs', () => {
    expect(isAdjacent({ x: 0, y: 2 }, { x: 1, y: 2 })).toBe(true);
    expect(isAdjacent({ x: 0, y: 2 }, { x: 3, y: 2 })).toBe(false);

    expect(makeCorridorId('slot_A', 'slot_B')).toBe('c_slot_A__slot_B');
    expect(makeCorridorId('slot_B', 'slot_A')).toBe('c_slot_A__slot_B');
  });
});
