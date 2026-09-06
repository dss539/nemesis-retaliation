/**
 * Combat actions (Shoot, Burst, Melee, Trade) for Nemesis: Retaliation.
 * Strictly adheres to ACT-SHOOT-001, ACT-BURST-001, ACT-MELEE-001, ACT-TRADE-001, and Rulebook p. 33.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterId, CorridorId, ItemId } from '../types/primitives.js';
import { rollBurstDie, rollShootDie, BurstDieResult, ShootDieResult } from '../types/dice.js';
import { DoorStateMachine } from '../spatial/doors.js';
import { CharacterState } from '../types/characters.js';
import { ItemCard } from '../types/items.js';

export interface CombatActionResult {
  state: GameState;
  events: string[];
  targetKilled: boolean;
  dieRoll?: ShootDieResult | BurstDieResult;
}

export function executeShoot(
  state: GameState,
  characterId: CharacterId,
  targetIntruderId: string,
  weaponItemId: ItemId,
  prng: Mulberry32,
): CombatActionResult {
  const events: string[] = [];
  const char = state.characters[characterId];
  if (!char) throw new Error(`Character ${characterId} not found`);

  const room = state.board.rooms[char.currentRoomId];
  if (!room) throw new Error(`Room not found`);

  // Validate target intruder is in the same room
  if (!room.intruderIds.includes(targetIntruderId)) {
    throw new Error(`Target intruder ${targetIntruderId} is not in ${char.name}'s room`);
  }

  const intruder = state.intruderInstances[targetIntruderId];
  if (!intruder) throw new Error(`Intruder ${targetIntruderId} not found`);

  // Validate weapon
  const weapon = findCharacterWeapon(char, weaponItemId);
  if (!weapon || !weapon.isWeapon || weapon.weaponType !== 'ranged') {
    throw new Error(`Selected item is not a working ranged weapon`);
  }
  if (!weapon.requiresNoAmmo && (weapon.ammo ?? 0) <= 0) {
    throw new Error(`Ranged weapon has no ammo`);
  }

  events.push(`${char.name} shoots at ${intruder.type.toUpperCase()} with ${weapon.title}`);

  // 1. Deal target 1 Hit
  const newHits = intruder.currentHits + 1;
  events.push(`Dealt 1 Hit to ${intruder.type} (Total hits: ${newHits})`);

  // 2. Roll Shoot die
  const roll = rollShootDie(prng);
  events.push(`Rolled Shoot die: ${roll.face}`);

  let targetKilled = false;
  let nextState: GameState = { ...state };
  let updatedWeapon = { ...weapon };

  if (roll.isCritical) {
    events.push(`CRITICAL HIT! ${intruder.type.toUpperCase()} is killed instantly!`);
    targetKilled = true;
  } else if (roll.numericValue !== undefined) {
    if (roll.numericValue <= newHits) {
      events.push(`Rolled ${roll.numericValue} <= ${newHits} hits: ${intruder.type.toUpperCase()} is killed!`);
      targetKilled = true;
    } else {
      events.push(`Rolled ${roll.numericValue} > ${newHits} hits: ${intruder.type.toUpperCase()} survives.`);
    }
  } else if (roll.isAmmoLoss) {
    if (!weapon.requiresNoAmmo && (weapon.ammo ?? 0) > 0) {
      updatedWeapon.ammo = Math.max(0, (weapon.ammo ?? 1) - 1);
      events.push(`Shoot die Ammo-loss: spent 1 Ammo token (Remaining: ${updatedWeapon.ammo})`);
    }
  }

  // Update weapon in inventory
  nextState = updateCharacterWeapon(nextState, characterId, updatedWeapon);

  if (targetKilled) {
    nextState = removeIntruder(nextState, targetIntruderId);
  } else {
    // Update hits on intruder
    nextState = {
      ...nextState,
      intruderInstances: {
        ...nextState.intruderInstances,
        [targetIntruderId]: {
          ...intruder,
          currentHits: newHits,
        },
      },
    };
  }

  return {
    state: nextState,
    events,
    targetKilled,
    dieRoll: roll,
  };
}

export function executeBurst(
  state: GameState,
  characterId: CharacterId,
  targetCorridorId: CorridorId,
  weaponItemId: ItemId,
  prng: Mulberry32,
): CombatActionResult {
  const events: string[] = [];
  const char = state.characters[characterId];
  if (!char) throw new Error(`Character ${characterId} not found`);

  const corridor = state.board.corridors[targetCorridorId];
  if (!corridor) throw new Error(`Corridor ${targetCorridorId} not found`);

  // Adjacency check
  if (corridor.slotA !== char.currentRoomId && corridor.slotB !== char.currentRoomId) {
    throw new Error(`Corridor is not adjacent to ${char.name}'s room`);
  }

  // Door check
  if (!DoorStateMachine.allowsPassage(corridor.doorState)) {
    throw new Error(`Cannot Burst through a closed door`);
  }

  // Intruder check
  if (corridor.intruderIds.length === 0) {
    throw new Error(`No intruders in target corridor to burst at`);
  }

  // Weapon check
  const weapon = findCharacterWeapon(char, weaponItemId);
  if (!weapon || !weapon.isWeapon || weapon.weaponType !== 'ranged') {
    throw new Error(`Selected item is not a working ranged weapon`);
  }
  if (!weapon.requiresNoAmmo && (weapon.ammo ?? 0) <= 0) {
    throw new Error(`Weapon has no ammo to burst`);
  }

  // Spend 1 Ammo token (ACT-BURST-001 step 2)
  let updatedWeapon = { ...weapon };
  if (!weapon.requiresNoAmmo) {
    updatedWeapon.ammo = Math.max(0, (weapon.ammo ?? 1) - 1);
    events.push(`Spent 1 Ammo token to Burst (Remaining: ${updatedWeapon.ammo})`);
  }

  let nextState = updateCharacterWeapon(state, characterId, updatedWeapon);

  // Roll Burst die
  const roll = rollBurstDie(prng);
  events.push(`Rolled Burst die: ${roll.face} (${roll.hits} Hit(s)${roll.hasAdditionalEffects ? ', Additional Effects' : ''})`);

  let remainingHits = roll.hits;
  const killedIds: string[] = [];

  // Allocate hits among intruders in the corridor
  // Prioritize adults and larva (1 hit each)
  const currentIntruders = corridor.intruderIds.map(id => nextState.intruderInstances[id]!).filter(Boolean);

  for (const inst of currentIntruders) {
    if (remainingHits <= 0) break;

    if (inst.type === 'larva' || inst.type === 'adult') {
      remainingHits -= 1;
      killedIds.push(inst.id);
      events.push(`Burst dealt 1 Hit: killed ${inst.type.toUpperCase()}`);
    } else if (inst.type === 'drone') {
      if (remainingHits >= 2) {
        remainingHits -= 2;
        killedIds.push(inst.id);
        events.push(`Burst dealt 2 Hits: killed DRONE`);
      }
    } else if (inst.type === 'queen') {
      const hitsApplied = Math.min(remainingHits, 12 - nextState.queenTrack.hits);
      remainingHits -= hitsApplied;
      nextState = {
        ...nextState,
        queenTrack: {
          ...nextState.queenTrack,
          hits: nextState.queenTrack.hits + hitsApplied,
        },
      };
      events.push(`Burst dealt ${hitsApplied} Hit(s) to the QUEEN (Total Queen hits: ${nextState.queenTrack.hits}/12)`);
    }
  }

  // Remove killed intruders
  for (const id of killedIds) {
    nextState = removeIntruder(nextState, id);
  }

  return {
    state: nextState,
    events,
    targetKilled: killedIds.length > 0,
    dieRoll: roll,
  };
}

export function executeMelee(
  state: GameState,
  characterId: CharacterId,
  targetIntruderId: string,
  prng: Mulberry32,
): CombatActionResult {
  const events: string[] = [];
  const char = state.characters[characterId];
  if (!char) throw new Error(`Character ${characterId} not found`);

  const room = state.board.rooms[char.currentRoomId];
  if (!room || !room.intruderIds.includes(targetIntruderId)) {
    throw new Error(`Target intruder is not in the room for Melee`);
  }

  const intruder = state.intruderInstances[targetIntruderId];
  if (!intruder) throw new Error(`Intruder not found`);

  events.push(`${char.name} attacks ${intruder.type.toUpperCase()} in MELEE!`);

  // Deal 1 Hit
  const newHits = intruder.currentHits + 1;
  events.push(`Dealt 1 Melee Hit (Total hits: ${newHits})`);

  // Roll Shoot die for Melee outcome
  const roll = rollShootDie(prng);
  events.push(`Rolled Melee Shoot die: ${roll.face}`);

  let targetKilled = false;
  let nextState = { ...state };

  if (roll.isCritical) {
    events.push(`CRITICAL MELEE HIT! ${intruder.type.toUpperCase()} is killed!`);
    targetKilled = true;
  } else if (roll.numericValue !== undefined && roll.numericValue <= newHits) {
    events.push(`Rolled ${roll.numericValue} <= ${newHits} hits: ${intruder.type.toUpperCase()} is killed!`);
    targetKilled = true;
  } else {
    events.push(`Melee attack ineffective - intruder survives!`);
  }

  if (targetKilled) {
    nextState = removeIntruder(nextState, targetIntruderId);
  } else {
    // Intruder survives and counter-attacks!
    events.push(`${intruder.type.toUpperCase()} launches a Melee counter-attack!`);
    const newHealth = Math.max(0, char.health - 1);
    events.push(`${char.name} suffers 1 Serious Wound / Damage in Melee counter-attack! (HP: ${newHealth})`);

    nextState = {
      ...nextState,
      intruderInstances: {
        ...nextState.intruderInstances,
        [targetIntruderId]: {
          ...intruder,
          currentHits: newHits,
        },
      },
      characters: {
        ...nextState.characters,
        [characterId]: {
          ...char,
          health: newHealth,
          isAlive: newHealth > 0,
        },
      },
    };
  }

  return {
    state: nextState,
    events,
    targetKilled,
    dieRoll: roll,
  };
}

export function executeTrade(
  state: GameState,
  fromCharId: CharacterId,
  toCharId: CharacterId,
  itemGivenId?: ItemId,
  itemReceivedId?: ItemId,
): { state: GameState; events: string[] } {
  const events: string[] = [];
  const fromChar = state.characters[fromCharId];
  const toChar = state.characters[toCharId];
  if (!fromChar || !toChar) throw new Error('Characters not found for trade');

  if (fromChar.currentRoomId !== toChar.currentRoomId) {
    throw new Error('Characters must be in the same Room to Trade');
  }

  const room = state.board.rooms[fromChar.currentRoomId]!;
  if (room.intruderIds.length > 0) {
    throw new Error('Cannot Trade while in Combat');
  }

  let fromBackpack = [...fromChar.inventory.backpack];
  let toBackpack = [...toChar.inventory.backpack];

  if (itemGivenId) {
    const item = fromBackpack.find(i => i.id === itemGivenId);
    if (!item) throw new Error(`Item ${itemGivenId} not found in ${fromChar.name}'s inventory`);
    fromBackpack = fromBackpack.filter(i => i.id !== itemGivenId);
    toBackpack.push(item);
    events.push(`${fromChar.name} gave ${item.title} to ${toChar.name}`);
  }

  if (itemReceivedId) {
    const item = toBackpack.find(i => i.id === itemReceivedId);
    if (!item) throw new Error(`Item ${itemReceivedId} not found in ${toChar.name}'s inventory`);
    toBackpack = toBackpack.filter(i => i.id !== itemReceivedId);
    fromBackpack.push(item);
    events.push(`${toChar.name} gave ${item.title} to ${fromChar.name}`);
  }

  const nextState: GameState = {
    ...state,
    characters: {
      ...state.characters,
      [fromCharId]: {
        ...fromChar,
        inventory: {
          ...fromChar.inventory,
          backpack: fromBackpack,
        },
      },
      [toCharId]: {
        ...toChar,
        inventory: {
          ...toChar.inventory,
          backpack: toBackpack,
        },
      },
    },
  };

  return { state: nextState, events };
}

function findCharacterWeapon(char: CharacterState, itemId: string): ItemCard | undefined {
  if (char.inventory.equippedWeapon && char.inventory.equippedWeapon.id === itemId) {
    return char.inventory.equippedWeapon;
  }
  return char.inventory.backpack.find(i => i.id === itemId);
}

function updateCharacterWeapon(state: GameState, charId: CharacterId, updatedWeapon: ItemCard): GameState {
  const char = state.characters[charId]!;
  let equipped = char.inventory.equippedWeapon;
  let backpack = [...char.inventory.backpack];

  if (equipped && equipped.id === updatedWeapon.id) {
    equipped = updatedWeapon;
  } else {
    backpack = backpack.map(i => (i.id === updatedWeapon.id ? updatedWeapon : i));
  }

  return {
    ...state,
    characters: {
      ...state.characters,
      [charId]: {
        ...char,
        inventory: {
          ...char.inventory,
          equippedWeapon: equipped,
          backpack,
        },
      },
    },
  };
}

function removeIntruder(state: GameState, intruderId: string): GameState {
  const inst = state.intruderInstances[intruderId];
  if (!inst) return state;

  const nextInstances = { ...state.intruderInstances };
  delete nextInstances[intruderId];

  // Return model to supply
  const nextSupply = {
    ...state.intruderModelsInSupply,
    [inst.type]: Math.min(state.intruderModelsInSupply[inst.type] + 1, 36),
  };

  let nextBoard = { ...state.board };

  if (inst.location.kind === 'room') {
    const room = nextBoard.rooms[inst.location.roomId];
    if (room) {
      nextBoard = {
        ...nextBoard,
        rooms: {
          ...nextBoard.rooms,
          [room.slotId]: {
            ...room,
            intruderIds: room.intruderIds.filter(id => id !== intruderId),
          },
        },
      };
    }
  } else {
    const corridor = nextBoard.corridors[inst.location.corridorId];
    if (corridor) {
      nextBoard = {
        ...nextBoard,
        corridors: {
          ...nextBoard.corridors,
          [corridor.corridorId]: {
            ...corridor,
            intruderIds: corridor.intruderIds.filter(id => id !== intruderId),
          },
        },
      };
    }
  }

  return {
    ...state,
    intruderInstances: nextInstances,
    intruderModelsInSupply: nextSupply,
    board: nextBoard,
  };
}
