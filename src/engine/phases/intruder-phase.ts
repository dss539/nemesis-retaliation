/**
 * Intruder Phase resolution for Nemesis: Retaliation.
 * Strictly adheres to RT-008, Rulebook pp. 14–15, and p. 25.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterId, IntruderType } from '../types/primitives.js';
import { INTRUDER_ATTACK_CARDS } from '../../data/attacks.js';

export interface IntruderPhaseResult {
  state: GameState;
  events: string[];
}

export function resolveIntruderPhase(state: GameState, prng: Mulberry32): IntruderPhaseResult {
  const events: string[] = ['=== INTRUDER PHASE ==='];
  let nextState: GameState = { ...state };

  // Step 1: Intruders Burning (RT-008 step 1)
  events.push('--- Step 1: Intruders Burning ---');
  const roomsWithFire = Object.values(nextState.board.rooms).filter(r => r.fire && r.intruderIds.length > 0);

  for (const room of roomsWithFire) {
    events.push(`Fire burning in ${room.tile?.name ?? room.slotId}: damaging ${room.intruderIds.length} intruder(s)`);
    const remainingIntruders: string[] = [];

    for (const intruderId of room.intruderIds) {
      const inst = nextState.intruderInstances[intruderId];
      if (!inst) continue;

      if (inst.type === 'larva') {
        // Larva killed by fire immediately
        events.push(`Fire incinerated Larva ${intruderId}!`);
        nextState = removeIntruderInstance(nextState, intruderId);
      } else {
        // Adult/Drone/Queen gains 1 hit
        const newHits = inst.currentHits + 1;
        events.push(`Fire dealt 1 Hit to ${inst.type} (Hits: ${newHits})`);
        nextState = {
          ...nextState,
          intruderInstances: {
            ...nextState.intruderInstances,
            [intruderId]: {
              ...inst,
              currentHits: newHits,
            },
          },
        };
        remainingIntruders.push(intruderId);
      }
    }

    // Fire in the Nest destroys 1 Egg
    if (room.tile?.roomNumber === '25' && room.eggTokens > 0) {
      events.push(`Fire in the Nest destroyed 1 Intruder Egg!`);
      nextState = {
        ...nextState,
        board: {
          ...nextState.board,
          rooms: {
            ...nextState.board.rooms,
            [room.slotId]: {
              ...room,
              eggTokens: Math.max(0, room.eggTokens - 1),
            },
          },
        },
      };
    }
  }

  // Step 2: Intruder Attacks (RT-008 step 2)
  events.push('--- Step 2: Intruder Attacks ---');
  // Order: top-left, row by row
  const orderedRoomSlots = Object.values(nextState.board.rooms).sort((a, b) => {
    if (a.coord.r !== b.coord.r) return a.coord.r - b.coord.r;
    return a.coord.q - b.coord.q;
  });

  for (const room of orderedRoomSlots) {
    if (room.intruderIds.length === 0 || room.characterIds.length === 0) continue;

    // Sort intruders by size: Queen > Drone > Adult > Larva
    const priority: Record<IntruderType, number> = {
      queen: 4,
      drone: 3,
      adult: 2,
      larva: 1,
    };

    const sortedIntruders = [...room.intruderIds]
      .map(id => nextState.intruderInstances[id])
      .filter((i): i is NonNullable<typeof i> => i !== undefined)
      .sort((a, b) => priority[b.type] - priority[a.type]);

    // Choose target character first in turn order
    const targetCharId = selectTargetCharacterInTurnOrder(nextState, room.characterIds);
    if (!targetCharId) continue;
    const targetChar = nextState.characters[targetCharId]!;

    events.push(`Intruders attacking in ${room.tile?.name ?? room.slotId}: targeting ${targetChar.name}`);

    for (const intruder of sortedIntruders) {
      // Check if room has Secure tokens (each Secure token cancels 1 attack)
      const currentRoom = nextState.board.rooms[room.slotId]!;
      if (currentRoom.secureTokens > 0) {
        events.push(`Secure token absorbed attack from ${intruder.type.toUpperCase()}! Secure token discarded.`);
        nextState = {
          ...nextState,
          board: {
            ...nextState.board,
            rooms: {
              ...nextState.board.rooms,
              [room.slotId]: {
                ...currentRoom,
                secureTokens: currentRoom.secureTokens - 1,
              },
            },
          },
        };
        continue;
      }

      // Draw Attack card
      const attackCardIdx = prng.nextInt(0, INTRUDER_ATTACK_CARDS.length - 1);
      const attackCard = INTRUDER_ATTACK_CARDS[attackCardIdx]!;
      events.push(`${intruder.type.toUpperCase()} attacks ${targetChar.name}: drew Attack "${attackCard.title}"!`);

      // Inflict 1 damage / wound
      const newHealth = Math.max(0, targetChar.health - 1);
      events.push(`${targetChar.name} suffers 1 Damage! (HP: ${newHealth}/${targetChar.maxHealth})`);

      nextState = {
        ...nextState,
        characters: {
          ...nextState.characters,
          [targetCharId]: {
            ...targetChar,
            health: newHealth,
            isAlive: newHealth > 0,
          },
        },
      };

      if (newHealth <= 0) {
        events.push(`CRITICAL CASUALTY: ${targetChar.name} has died!`);
        break;
      }
    }
  }

  // Transition phase to 'event'
  nextState.phase = 'event';

  return { state: nextState, events };
}

function selectTargetCharacterInTurnOrder(state: GameState, characterIds: CharacterId[]): CharacterId | undefined {
  if (characterIds.length === 0) return undefined;
  if (characterIds.length === 1) return characterIds[0];

  // Starting player or closest clockwise
  for (let offset = 0; offset < state.players.length; offset++) {
    const pIdx = (state.startingPlayerIndex + offset) % state.players.length;
    const player = state.players[pIdx];
    if (player?.characterId && characterIds.includes(player.characterId)) {
      return player.characterId;
    }
  }

  return characterIds[0];
}

function removeIntruderInstance(state: GameState, intruderId: string): GameState {
  const inst = state.intruderInstances[intruderId];
  if (!inst) return state;

  const nextInstances = { ...state.intruderInstances };
  delete nextInstances[intruderId];

  const nextSupply = {
    ...state.intruderModelsInSupply,
    [inst.type]: Math.min(state.intruderModelsInSupply[inst.type] + 1, 36),
  };

  let nextBoard = { ...state.board };
  if (inst.location.kind === 'room') {
    const r = nextBoard.rooms[inst.location.roomId];
    if (r) {
      nextBoard.rooms[r.slotId] = {
        ...r,
        intruderIds: r.intruderIds.filter(id => id !== intruderId),
      };
    }
  } else {
    const c = nextBoard.corridors[inst.location.corridorId];
    if (c) {
      nextBoard.corridors[c.corridorId] = {
        ...c,
        intruderIds: c.intruderIds.filter(id => id !== intruderId),
      };
    }
  }

  return {
    ...state,
    board: nextBoard,
    intruderInstances: nextInstances,
    intruderModelsInSupply: nextSupply,
  };
}
