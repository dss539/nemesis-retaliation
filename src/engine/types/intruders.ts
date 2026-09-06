/**
 * Intruder types, tokens, models, and bag mechanics for Nemesis: Retaliation.
 * Derived from INT-001, INT-002, INT-003, and RT-008.
 */

import { IntruderType, IntruderInstanceId } from './primitives.js';

export type IntruderTokenType = IntruderType | 'blank';

export type TokenBackValue = '2' | '3' | '4' | '1+1' | '2+1' | '3+1';

export interface IntruderToken {
  id: string;
  type: IntruderTokenType;
  backValue?: TokenBackValue;
}

/**
 * Base game physical model limits (FND-008, INT-001):
 * - 1 Queen model
 * - 8 Drone models
 * - 36 Adult models
 * - 6 Larva models
 */
export const INTRUDER_MODEL_LIMITS: Readonly<Record<IntruderType, number>> = {
  queen: 1,
  drone: 8,
  adult: 36,
  larva: 6,
} as const;

/**
 * Provided Intruder-token supply (40 tokens total, INT-001):
 * - 1 Blank
 * - 9 Queen tokens
 * - 8 Drone tokens
 * - 16 Adult tokens
 * - 6 Larva tokens
 */
export const INTRUDER_TOKEN_SUPPLY: Readonly<Record<IntruderTokenType, number>> = {
  blank: 1,
  queen: 9,
  drone: 8,
  adult: 16,
  larva: 6,
} as const;

export type IntruderLocation =
  | { kind: 'room'; roomId: string }
  | { kind: 'corridor'; corridorId: string };

export interface IntruderInstance {
  id: IntruderInstanceId;
  type: IntruderType;
  location: IntruderLocation;
  currentHits: number;
}

export interface QueenTrackState {
  hits: number; // 0..12
  isAlive: boolean;
}

export interface IntruderBagState {
  tokensInBag: IntruderToken[];
  tokensInPool: IntruderToken[]; // Outside bag
  isQueenAlive: boolean;
}
