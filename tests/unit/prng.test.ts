import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';

describe('Mulberry32 PRNG', () => {
  it('produces deterministic output given identical seeds', () => {
    const rng1 = new Mulberry32(12345);
    const rng2 = new Mulberry32(12345);

    const values1 = Array.from({ length: 10 }, () => rng1.next());
    const values2 = Array.from({ length: 10 }, () => rng2.next());

    expect(values1).toEqual(values2);
  });

  it('produces different sequences for different seeds', () => {
    const rng1 = new Mulberry32(12345);
    const rng2 = new Mulberry32(54321);

    const val1 = rng1.next();
    const val2 = rng2.next();

    expect(val1).not.toEqual(val2);
  });

  it('generates next() values strictly in [0, 1)', () => {
    const rng = new Mulberry32(42);
    for (let i = 0; i < 1000; i++) {
      const val = rng.next();
      expect(val).toBeGreaterThanOrEqual(0);
      expect(val).toBeLessThan(1);
    }
  });

  it('generates nextInt() within inclusive bounds', () => {
    const rng = new Mulberry32(999);
    for (let i = 0; i < 500; i++) {
      const val = rng.nextInt(3, 7);
      expect(val).toBeGreaterThanOrEqual(3);
      expect(val).toBeLessThanOrEqual(7);
      expect(Number.isInteger(val)).toBe(true);
    }
  });

  it('rolls dice within 1..sides', () => {
    const rng = new Mulberry32(777);
    const rolls = Array.from({ length: 200 }, () => rng.rollDie(6));
    expect(rolls.every(r => r >= 1 && r <= 6)).toBe(true);
    expect(new Set(rolls).size).toBe(6); // All 6 sides hit in 200 rolls
  });

  it('shuffles arrays deterministically without mutation', () => {
    const rng1 = new Mulberry32(1337);
    const rng2 = new Mulberry32(1337);
    const original = ['A', 'B', 'C', 'D', 'E', 'F'];

    const shuffled1 = rng1.shuffle(original);
    const shuffled2 = rng2.shuffle(original);

    expect(original).toEqual(['A', 'B', 'C', 'D', 'E', 'F']); // Unmutated
    expect(shuffled1).toEqual(shuffled2);
    expect(shuffled1.sort()).toEqual([...original].sort());
  });

  it('draws items without replacement', () => {
    const rng = new Mulberry32(888);
    const deck = [1, 2, 3, 4, 5];
    const drawn = rng.draw(deck);

    expect(drawn).toBeDefined();
    expect(deck).not.toContain(drawn);
    expect(deck.length).toBe(4);
  });

  it('supports state export and hydration', () => {
    const rng1 = new Mulberry32(2026);
    // Advance 50 steps
    for (let i = 0; i < 50; i++) rng1.next();

    const snapshot = rng1.exportState();
    const nextFiveFromRng1 = Array.from({ length: 5 }, () => rng1.next());

    // Hydrate new instance with exported state
    const rng2 = new Mulberry32(0);
    rng2.importState(snapshot);
    const nextFiveFromRng2 = Array.from({ length: 5 }, () => rng2.next());

    expect(nextFiveFromRng2).toEqual(nextFiveFromRng1);
  });
});
