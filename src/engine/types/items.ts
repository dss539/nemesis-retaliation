/**
 * Items, weapons, and equipment for Nemesis: Retaliation.
 * Derived from docs/rules/04-items-and-equipment.md and 00-foundations.md.
 */

import { ItemColor, ItemId } from './primitives.js';

export type ItemDeckColor = ItemColor;

export type ItemCategory = ItemDeckColor | 'starting' | 'quest' | 'support';

export type WeaponType = 'ranged' | 'melee';

export interface ItemCard {
  id: ItemId;
  title: string;
  category: ItemCategory;
  isHeavy: boolean;
  isWeapon: boolean;
  weaponType?: WeaponType | undefined;
  requiresNoAmmo?: boolean | undefined;
  ammo?: number | undefined;
  maxAmmo?: number | undefined;
  hasMalfunction?: boolean | undefined;
  isOneUse?: boolean | undefined;
  rulesText: string;
}

export interface InventoryState {
  equippedWeapon?: ItemCard | undefined;
  equippedArmor?: ItemCard | undefined;
  heavyItem?: ItemCard | undefined; // At most one heavy item in hands
  backpack: ItemCard[]; // Limit: 2 items (or expanded with tactical gear)
  tacticalGear: ItemCard[];
}
