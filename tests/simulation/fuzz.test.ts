import { describe, it, expect } from 'vitest';
import { MonteCarloSimulator } from '../../src/engine/simulation/monte-carlo.js';

describe('Headless Monte Carlo Fuzz Testing (Invariants & Deadlock Freedom)', () => {
  it('runs automated 1-player games to completion without invariant violations', () => {
    for (let i = 0; i < 5; i++) {
      const seed = 1000 + i;
      const res = MonteCarloSimulator.runGame(1, seed, 1000);
      expect(res.violations).toEqual([]);
      expect(res.totalActions).toBeGreaterThan(5);
    }
  });

  it('runs automated 2-player games to completion without invariant violations', () => {
    for (let i = 0; i < 5; i++) {
      const seed = 2000 + i;
      const res = MonteCarloSimulator.runGame(2, seed, 1000);
      expect(res.violations).toEqual([]);
      expect(res.totalActions).toBeGreaterThan(10);
    }
  });

  it('runs automated 3-player and 4-player games preserving all invariants', () => {
    const res3 = MonteCarloSimulator.runGame(3, 3001, 1000);
    expect(res3.violations).toEqual([]);

    const res4 = MonteCarloSimulator.runGame(4, 4001, 1000);
    expect(res4.violations).toEqual([]);
  });
});
