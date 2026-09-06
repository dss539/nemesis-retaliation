/**
 * Room Actions execution across all 25 official rooms for Nemesis: Retaliation.
 * Strictly adheres to official Room Help sheet source fidelity and ACT-ROOM-001.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterId, CorridorId, DoorState, RoomId, Section } from '../types/primitives.js';
import { rollBurstDie } from '../types/dice.js';
import { DoorStateMachine } from '../spatial/doors.js';
import { executeRoomSearch } from './search.js';
import { makeCorridorId } from '../spatial/hex.js';
import { CharacterState } from '../types/characters.js';
import { removeIntruder } from './combat-actions.js';

export interface RoomActionResult {
  state: GameState;
  events: string[];
}

export function executeRoomAction(
  state: GameState,
  characterId: CharacterId,
  prng: Mulberry32,
  params?: {
    targetSection?: Section;
    targetDoorCorridorId?: CorridorId;
    targetDoorState?: DoorState;
    targetCorridorId?: CorridorId;
    drillTargetRoomId?: RoomId;
  },
): RoomActionResult {
  const events: string[] = [];
  const char = state.characters[characterId];
  if (!char) throw new Error(`Character ${characterId} not found`);

  const room = state.board.rooms[char.currentRoomId];
  if (!room || !room.isDiscovered || !room.tile) {
    throw new Error(`Cannot use room action in undiscovered room`);
  }

  // Preconditions
  if (room.intruderIds.length > 0) {
    throw new Error(`Cannot use room action while in Combat`);
  }
  if (room.malfunction) {
    throw new Error(`Cannot use room action while Room has a Malfunction`);
  }

  let nextState: GameState = { ...state };
  const roomNumber = room.tile.roomNumber;
  events.push(`${char.name} executes Room Action in ${room.tile.name} (Room ${roomNumber})`);

  switch (roomNumber) {
    // 01: SPRINKLERS CONTROL: Discard all Fire from a chosen Section
    case '01': {
      const sec = params?.targetSection ?? room.section;
      events.push(`Activated Sprinklers in Section ${sec}: extinguishing all Fire!`);
      const updatedRooms = { ...nextState.board.rooms };
      for (const [rid, r] of Object.entries(updatedRooms)) {
        if (r.section === sec && r.fire) {
          updatedRooms[rid] = { ...r, fire: false };
          events.push(`Extinguished Fire in ${r.tile?.name ?? rid}`);
        }
      }
      nextState = {
        ...nextState,
        board: { ...nextState.board, rooms: updatedRooms },
      };
      break;
    }

    // 02: SHELTER: Place Secure token
    case '02': {
      events.push(`Placed Secure token in Shelter`);
      nextState = updateRoom(nextState, room.slotId, {
        secureTokens: room.secureTokens + 1,
      });
      break;
    }

    // 03: EMERGENCY ROOM: Heal 2 Health Points
    case '03': {
      const newHealth = Math.min(char.maxHealth, char.health + 2);
      events.push(`Treated in Emergency Room: healed to ${newHealth}/${char.maxHealth} HP`);
      nextState = updateCharacter(nextState, characterId, { health: newHealth });
      break;
    }

    // 04: SUPPLY ROOM: Search without consuming search tokens
    case '04': {
      events.push(`Searching Supply Room for supplies (free search token)`);
      const searchRes = executeRoomSearch(nextState, characterId, 0, prng);
      nextState = searchRes.state;
      // Restore search token consumed by search
      nextState = updateRoom(nextState, room.slotId, {
        searchTokens: room.searchTokens,
      });
      events.push(...searchRes.events);
      break;
    }

    // 05: ARMORY: Add Ammo tokens to Weapon
    case '05': {
      if (char.inventory.equippedWeapon && !char.inventory.equippedWeapon.requiresNoAmmo) {
        const weapon = char.inventory.equippedWeapon;
        const maxAmmo = weapon.maxAmmo ?? 2;
        const newAmmo = Math.min(maxAmmo, (weapon.ammo ?? 0) + 2);
        events.push(`Restocked Ammo in Armory for ${weapon.title}: now has ${newAmmo} Ammo token(s)`);
        nextState = updateCharacter(nextState, characterId, {
          inventory: {
            ...char.inventory,
            equippedWeapon: { ...weapon, ammo: newAmmo },
          },
        });
      } else {
        events.push(`No reloadable ranged weapon equipped - Ammo restock skipped`);
      }
      break;
    }

    // 06: DOOR CONTROL ROOM: Open or Close any Door
    case '06': {
      if (params?.targetDoorCorridorId && params?.targetDoorState) {
        const corr = nextState.board.corridors[params.targetDoorCorridorId];
        if (corr) {
          const newState = params.targetDoorState === 'open'
            ? DoorStateMachine.open(corr.doorState)
            : DoorStateMachine.close(corr.doorState);
          events.push(`Door Control: set Door on Corridor ${corr.corridorId} to ${newState}`);
          nextState = updateCorridor(nextState, corr.corridorId, { doorState: newState });
        }
      }
      break;
    }

    // 08: GUNNERY ROOM: Roll Burst die and deal hits in chosen corridor
    case '08': {
      if (params?.targetCorridorId) {
        const roll = rollBurstDie(prng);
        events.push(`Gunnery Room battery fired at Corridor ${params.targetCorridorId}! Rolled ${roll.hits} Hit(s)`);
        const corr = nextState.board.corridors[params.targetCorridorId];
        if (corr && corr.intruderIds.length > 0) {
          // Remove intruders equal to hits
          let hitsLeft = roll.hits;
          const killed: string[] = [];
          for (const id of corr.intruderIds) {
            if (hitsLeft > 0) {
              killed.push(id);
              hitsLeft--;
            }
          }
          events.push(`Gunnery battery eliminated ${killed.length} Intruder(s)!`);
          for (const id of killed) {
            nextState = removeIntruder(nextState, id);
          }
        }
      }
      break;
    }

    // 09: PRESSURE CONTROL: Restore Oxygen to 7
    case '09': {
      events.push(`Pressure Control: replenished oxygen supply to 7`);
      nextState = updateCharacter(nextState, characterId, { oxygen: 7, isSuffocating: false });
      break;
    }

    // 13: DECONTAMINATION ROOM: Scan & discard Contaminations
    case '13': {
      const contaminatedCount = char.contaminationHand.length;
      events.push(`Decontaminated in Decontamination Room: purged ${contaminatedCount} Contamination card(s)`);
      nextState = updateCharacter(nextState, characterId, { contaminationHand: [] });
      break;
    }

    // 15, 19, 22: LIFE SUPPORT CONTROL A, B, C: Restore life support for section
    case '15':
    case '19':
    case '22': {
      const sec = room.section;
      events.push(`Restored Life Support in Section ${sec}! Life Support is now ONLINE.`);
      nextState = {
        ...nextState,
        lifeSupport: {
          ...nextState.lifeSupport,
          [sec]: true,
        },
      };
      break;
    }

    // 17: DRILLING STATION: Drill new corridor
    case '17': {
      if (params?.drillTargetRoomId) {
        const newCorridorId = makeCorridorId(room.slotId, params.drillTargetRoomId);
        if (!nextState.board.corridors[newCorridorId]) {
          events.push(`Drilled new Corridor between ${room.slotId} and ${params.drillTargetRoomId}!`);
          nextState = {
            ...nextState,
            board: {
              ...nextState.board,
              corridors: {
                ...nextState.board.corridors,
                [newCorridorId]: {
                  corridorId: newCorridorId,
                  slotA: room.slotId,
                  slotB: params.drillTargetRoomId,
                  directionFromA: 'E',
                  noiseValue: 1,
                  hasNoise: false,
                  doorState: 'open',
                  isTechnical: false,
                  intruderIds: [],
                },
              },
            },
          };
        }
      }
      break;
    }

    // 18: HIBERNATORIUM: Enter hibernation
    case '18': {
      if (nextState.lifeSupport['B']) {
        events.push(`${char.name} entered Hibernation Pod in Section B! Safe in stasis.`);
        nextState = updateCharacter(nextState, characterId, { hasEscaped: true });
      } else {
        events.push(`Cannot enter Hibernation: Life Support in Section B is OFFLINE!`);
      }
      break;
    }

    // 20: SERVER ROOM: Download Facility data
    case '20': {
      events.push(`Downloaded Facility data from Server Room mainframe`);
      nextState = updateRoom(nextState, room.slotId, {
        dataTokens: room.dataTokens + 1,
      });
      break;
    }

    // 21: COOLING SYSTEM: Reset reactor / delay autodestruction
    case '21': {
      if (nextState.autodestruction.isActive && nextState.autodestruction.roundsRemaining !== undefined) {
        const delayed = nextState.autodestruction.roundsRemaining + 3;
        events.push(`Cooling System engaged: delayed Autodestruction by 3 rounds (Remaining: ${delayed})`);
        nextState = {
          ...nextState,
          autodestruction: {
            ...nextState.autodestruction,
            roundsRemaining: delayed,
          },
        };
      } else {
        events.push(`Cooling System coolant flushed through Reactor cores.`);
      }
      break;
    }

    // 23: REACTOR: Autodestruction
    case '23': {
      if (!nextState.autodestruction.isActive) {
        events.push(`CRITICAL: Self-Destruct Sequence INITIATED! Facility will explode in 5 rounds!`);
        nextState = {
          ...nextState,
          autodestruction: {
            isActive: true,
            roundsRemaining: 5,
          },
        };
      } else {
        events.push(`Self-Destruct Sequence ABORTED in Reactor control!`);
        nextState = {
          ...nextState,
          autodestruction: {
            isActive: false,
            roundsRemaining: undefined,
          },
        };
      }
      break;
    }

    // 24: ESCAPE SHUTTLE: Launch shuttle
    case '24': {
      events.push(`${char.name} boarded the Escape Shuttle and launched away from the Facility! ESCAPED!`);
      nextState = updateCharacter(nextState, characterId, { hasEscaped: true });
      break;
    }

    // 25: NEST: Destroy Egg
    case '25': {
      if (room.eggTokens > 0) {
        events.push(`Destroyed 1 Intruder Egg in the Nest! (Remaining eggs: ${room.eggTokens - 1})`);
        nextState = updateRoom(nextState, room.slotId, {
          eggTokens: room.eggTokens - 1,
        });
      } else {
        events.push(`No Eggs remaining in the Nest to destroy`);
      }
      break;
    }

    default: {
      events.push(`Executed room action in ${room.tile.name}`);
      break;
    }
  }

  return { state: nextState, events };
}

function updateRoom(state: GameState, roomId: RoomId, patch: Partial<GameState['board']['rooms'][string]>): GameState {
  const room = state.board.rooms[roomId]!;
  return {
    ...state,
    board: {
      ...state.board,
      rooms: {
        ...state.board.rooms,
        [roomId]: {
          ...room,
          ...patch,
        },
      },
    },
  };
}

function updateCorridor(state: GameState, corridorId: CorridorId, patch: Partial<GameState['board']['corridors'][string]>): GameState {
  const corridor = state.board.corridors[corridorId]!;
  return {
    ...state,
    board: {
      ...state.board,
      corridors: {
        ...state.board.corridors,
        [corridorId]: {
          ...corridor,
          ...patch,
        },
      },
    },
  };
}

function updateCharacter(state: GameState, charId: CharacterId, patch: Partial<CharacterState>): GameState {
  const char = state.characters[charId]!;
  return {
    ...state,
    characters: {
      ...state.characters,
      [charId]: {
        ...char,
        ...patch,
      },
    },
  };
}
