import { describe, it, expect } from 'vitest';
import { Mulberry32 } from '../../src/engine/prng/mulberry32.js';
import {
  rollShootDie,
  rollBurstDie,
  rollNoiseDie,
  SHOOT_DIE_FACES,
  BURST_DIE_FACES,
  NOISE_DIE_FACES,
} from '../../src/engine/types/dice.js';

describe('Dice rolling', () => {
  it('correctly maps Shoot die faces', () => {
    const prng = new Mulberry32(101);
    for (let i = 0; i < 100; i++) {
      const result = rollShootDie(prng);
      expect(SHOOT_DIE_FACES).toContain(result.face);
      if (result.isCritical) {
        expect(result.face).toBe('shootDieCritical');
        expect(result.numericValue).toBeUndefined();
      } else if (result.isAmmoLoss) {
        expect(result.face).toBe('shootDieAmmoLoss');
        expect(result.numericValue).toBeUndefined();
      } else {
        expect([2, 3, 4, 5]).toContain(result.numericValue);
      }
    }
  });

  it('correctly maps Burst die faces', () => {
    const prng = new Mulberry32(202);
    for (let i = 0; i < 100; i++) {
      const result = rollBurstDie(prng);
      expect(BURST_DIE_FACES).toContain(result.face);
      expect(result.hits).toBeGreaterThanOrEqual(1);
      expect(result.hits).toBeLessThanOrEqual(4);
      if (result.hasAdditionalEffects) {
        expect(result.hits).toBe(4);
        expect(result.face).toBe('burstDie4');
      }
    }
  });

  it('correctly maps Noise die faces', () => {
    const prng = new Mulberry32(303);
    for (let i = 0; i < 100; i++) {
      const result = rollNoiseDie(prng);
      expect(NOISE_DIE_FACES).toContain(result.face);
      if (result.isHazard) {
        expect(result.face).toBe('noiseDieHazard');
        expect(result.corridorValue).toBeUndefined();
      } else {
        expect([1, 2, 3, 4]).toContain(result.corridorValue);
      }
    }
  });
});
