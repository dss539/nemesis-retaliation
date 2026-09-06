/**
 * Dice types, results, and roll semantics for Nemesis: Retaliation.
 * Derived from official rulebook p. 40 (icon glossary), p. 33 (combat), and p. 25 (noise).
 */

import { Mulberry32 } from '../prng/mulberry32.js';

export type ShootDieFace =
  | 'shootDie2'
  | 'shootDie3'
  | 'shootDie4'
  | 'shootDie5'
  | 'shootDieAmmoLoss'
  | 'shootDieCritical';

export interface ShootDieResult {
  face: ShootDieFace;
  isCritical: boolean;
  isAmmoLoss: boolean;
  numericValue?: number | undefined; // 2..5
}

export type BurstDieFace =
  | 'burstDie1'
  | 'burstDie2'
  | 'burstDie3'
  | 'burstDie4'; // 4 shares face with additional effects

export interface BurstDieResult {
  face: BurstDieFace;
  hits: number; // 1..4
  hasAdditionalEffects: boolean; // true for 4
}

export type NoiseDieFace =
  | 'noiseDie1'
  | 'noiseDie2'
  | 'noiseDie3'
  | 'noiseDie4'
  | 'noiseDieHazard';

export interface NoiseDieResult {
  face: NoiseDieFace;
  corridorValue?: number | undefined; // 1..4
  isHazard: boolean;
}

/**
 * Physical face arrays representing die sides.
 *
 * Shoot die: 8 sides.
 * Results: Critical (1), 2 (1), 3 (1), 4 (1), 5 (1), Ammo-loss (1), plus 2 balanced distribution sides (Ammo-loss / 2).
 */
export const SHOOT_DIE_FACES: readonly ShootDieFace[] = [
  'shootDieCritical',
  'shootDie2',
  'shootDie3',
  'shootDie4',
  'shootDie5',
  'shootDieAmmoLoss',
  'shootDie2',
  'shootDieAmmoLoss',
] as const;

/**
 * Burst die: 6 sides.
 * 1, 2, 2, 3, 3, 4 (with additional effects on 4).
 */
export const BURST_DIE_FACES: readonly BurstDieFace[] = [
  'burstDie1',
  'burstDie2',
  'burstDie2',
  'burstDie3',
  'burstDie3',
  'burstDie4',
] as const;

/**
 * Noise die: 10 sides.
 * 2 each of 1, 2, 3, 4, and Hazard.
 */
export const NOISE_DIE_FACES: readonly NoiseDieFace[] = [
  'noiseDie1',
  'noiseDie1',
  'noiseDie2',
  'noiseDie2',
  'noiseDie3',
  'noiseDie3',
  'noiseDie4',
  'noiseDie4',
  'noiseDieHazard',
  'noiseDieHazard',
] as const;

export function rollShootDie(prng: Mulberry32): ShootDieResult {
  const index = prng.nextInt(0, SHOOT_DIE_FACES.length - 1);
  const face = SHOOT_DIE_FACES[index]!;

  return {
    face,
    isCritical: face === 'shootDieCritical',
    isAmmoLoss: face === 'shootDieAmmoLoss',
    numericValue:
      face === 'shootDie2'
        ? 2
        : face === 'shootDie3'
        ? 3
        : face === 'shootDie4'
        ? 4
        : face === 'shootDie5'
        ? 5
        : undefined,
  };
}

export function rollBurstDie(prng: Mulberry32): BurstDieResult {
  const index = prng.nextInt(0, BURST_DIE_FACES.length - 1);
  const face = BURST_DIE_FACES[index]!;

  const hits =
    face === 'burstDie1' ? 1 : face === 'burstDie2' ? 2 : face === 'burstDie3' ? 3 : 4;

  return {
    face,
    hits,
    hasAdditionalEffects: face === 'burstDie4',
  };
}

export function rollNoiseDie(prng: Mulberry32): NoiseDieResult {
  const index = prng.nextInt(0, NOISE_DIE_FACES.length - 1);
  const face = NOISE_DIE_FACES[index]!;

  return {
    face,
    isHazard: face === 'noiseDieHazard',
    corridorValue:
      face === 'noiseDie1'
        ? 1
        : face === 'noiseDie2'
        ? 2
        : face === 'noiseDie3'
        ? 3
        : face === 'noiseDie4'
        ? 4
        : undefined,
  };
}
