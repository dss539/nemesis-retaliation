/**
 * Official Character definitions for Nemesis: Retaliation.
 * Derived from official rulebook p. 8-10 and docs/rules/00-foundations.md.
 */

import { CharacterId } from '../engine/types/primitives.js';

export interface OfficialCharacterDefinition {
  readonly characterId: CharacterId;
  readonly name: string;
  readonly rank: number;
  readonly maxHealth: number;
  readonly startingOxygen: number;
  readonly startingWeaponKey: string;
  readonly startingArmorKey?: string;
  readonly description: string;
}

export const OFFICIAL_CHARACTERS: readonly OfficialCharacterDefinition[] = [
  {
    characterId: 'recon',
    name: 'Recon',
    rank: 1,
    maxHealth: 9,
    startingOxygen: 7,
    startingWeaponKey: 'AssaultRifle',
    description: 'Scout with Sprint ability. Fastest operative.',
  },
  {
    characterId: 'combat-engineer',
    name: 'Combat Engineer',
    rank: 2,
    maxHealth: 9,
    startingOxygen: 7,
    startingWeaponKey: 'AutomaticShotgun',
    description: 'Demolition and structural specialist. Can reinforce corridors and drill new passages.',
  },
  {
    characterId: 'medical-support',
    name: 'Medical Support',
    rank: 2,
    maxHealth: 9,
    startingOxygen: 7,
    startingWeaponKey: 'Carbine',
    description: 'Combat medic. Can heal serious wounds and resolve infection.',
  },
  {
    characterId: 'heavy-gun-operator',
    name: 'Heavy Gun Operator',
    rank: 2,
    maxHealth: 9,
    startingOxygen: 7,
    startingWeaponKey: 'BfGun',
    description: 'Heavy weapons specialist. Bonus hit on shooting and high-damage capabilities.',
  },
  {
    characterId: 'contractor',
    name: 'Contractor',
    rank: 3,
    maxHealth: 9,
    startingOxygen: 7,
    startingWeaponKey: 'Handgun',
    startingArmorKey: 'BulletproofVest',
    description: 'Versatile private contractor. Starts with 2 character items (Weapon + Armor) and skips support equipment draft.',
  },
  {
    characterId: 'officer',
    name: 'Officer',
    rank: 4,
    maxHealth: 9,
    startingOxygen: 7,
    startingWeaponKey: 'SawedoffShotgun',
    description: 'High-ranking field commander. Can issue commands to lower-ranking characters.',
  },
] as const;

export const OFFICIAL_CHARACTERS_BY_ID: Readonly<Record<CharacterId, OfficialCharacterDefinition>> =
  Object.fromEntries(OFFICIAL_CHARACTERS.map(c => [c.characterId, c])) as Record<
    CharacterId,
    OfficialCharacterDefinition
  >;
