/**
 * Noise roll procedures and Noise marker resolution for Nemesis: Retaliation.
 * Derived from official rulebook p. 25, INT-002, and ACT-001/002.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterId, CorridorId, IntruderType, RoomId } from '../types/primitives.js';
import { rollNoiseDie, NoiseDieResult } from '../types/dice.js';
import { IntruderInstance } from '../types/intruders.js';

export interface NoiseResolutionResult {
  state: GameState;
  noiseRoll: NoiseDieResult;
  events: string[];
  intrusions: {
    intruderId: string;
    type: IntruderType;
    roomId: RoomId;
    isImmediateAttack: boolean;
  }[];
}

export function resolveNoiseRoll(
  state: GameState,
  characterId: CharacterId,
  prng: Mulberry32,
  forcedCorridorId?: CorridorId, // Cautious movement can choose corridor
): NoiseResolutionResult {
  const char = state.characters[characterId];
  if (!char) {
    throw new Error(`Character ${characterId} not found`);
  }

  const roomId = char.currentRoomId;
  const room = state.board.rooms[roomId];
  if (!room) {
    throw new Error(`Room ${roomId} not found on board`);
  }

  const roll = rollNoiseDie(prng);
  const events: string[] = [];
  const intrusions: NoiseResolutionResult['intrusions'] = [];

  let nextState: GameState = { ...state };

  if (roll.isHazard) {
    events.push(`${char.name} rolled Noise Die: HAZARD in ${room.slotId}`);
    const drawRes = drawAndResolveBagToken(nextState, prng, 'hazard', roomId, undefined);
    nextState = drawRes.state;
    events.push(...drawRes.events);
    intrusions.push(...drawRes.intrusions);
  } else if (roll.corridorValue !== undefined) {
    const rolledVal = roll.corridorValue;
    events.push(`${char.name} rolled Noise Die: ${rolledVal}`);

    // Find all adjacent corridors with matching noise value
    const adjacentCorridors = Object.values(nextState.board.corridors).filter(
      c => (c.slotA === roomId || c.slotB === roomId) && c.noiseValue === rolledVal,
    );

    if (adjacentCorridors.length === 0) {
      events.push(`No adjacent Corridors have Noise value ${rolledVal} - nothing happens.`);
    } else {
      for (const corridor of adjacentCorridors) {
        // If cautious movement specified corridor, prioritize it
        if (forcedCorridorId && corridor.corridorId !== forcedCorridorId) {
          continue;
        }

        // 1. If corridor contains Intruder(s), move largest into character's room
        if (corridor.intruderIds.length > 0) {
          const largestIntruderId = findLargestIntruder(nextState, corridor.intruderIds);
          if (largestIntruderId) {
            const intruder = nextState.intruderInstances[largestIntruderId]!;
            events.push(`Noise attracted ${intruder.type} from Corridor ${corridor.corridorId} into ${room.slotId}!`);

            nextState = moveIntruderToRoom(nextState, largestIntruderId, corridor.corridorId, roomId);
            intrusions.push({
              intruderId: largestIntruderId,
              type: intruder.type,
              roomId,
              isImmediateAttack: true,
            });
          }
        }
        // 2. Else if corridor already contains Noise marker, resolve it
        else if (corridor.hasNoise) {
          events.push(`Corridor ${corridor.corridorId} already had Noise: resolving Noise Marker!`);
          // Remove noise marker
          nextState = updateCorridor(nextState, corridor.corridorId, { hasNoise: false });
          // Draw and resolve token in this corridor
          const drawRes = drawAndResolveBagToken(nextState, prng, 'corridor', roomId, corridor.corridorId);
          nextState = drawRes.state;
          events.push(...drawRes.events);
          intrusions.push(...drawRes.intrusions);
        }
        // 3. Else place a Noise marker
        else {
          events.push(`Placed Noise marker in Corridor ${corridor.corridorId}`);
          nextState = updateCorridor(nextState, corridor.corridorId, { hasNoise: true });
        }
      }
    }
  }

  return {
    state: nextState,
    noiseRoll: roll,
    events,
    intrusions,
  };
}

function findLargestIntruder(state: GameState, intruderIds: string[]): string | undefined {
  const priority: Record<IntruderType, number> = {
    queen: 4,
    drone: 3,
    adult: 2,
    larva: 1,
  };

  let largestId: string | undefined;
  let highestScore = -1;

  for (const id of intruderIds) {
    const inst = state.intruderInstances[id];
    if (inst) {
      const score = priority[inst.type];
      if (score > highestScore) {
        highestScore = score;
        largestId = id;
      }
    }
  }

  return largestId;
}

function moveIntruderToRoom(
  state: GameState,
  intruderId: string,
  corridorId: CorridorId,
  roomId: RoomId,
): GameState {
  const corridor = state.board.corridors[corridorId]!;
  const room = state.board.rooms[roomId]!;
  const inst = state.intruderInstances[intruderId]!;

  return {
    ...state,
    board: {
      ...state.board,
      corridors: {
        ...state.board.corridors,
        [corridorId]: {
          ...corridor,
          intruderIds: corridor.intruderIds.filter(id => id !== intruderId),
        },
      },
      rooms: {
        ...state.board.rooms,
        [roomId]: {
          ...room,
          intruderIds: [...room.intruderIds, intruderId],
        },
      },
    },
    intruderInstances: {
      ...state.intruderInstances,
      [intruderId]: {
        ...inst,
        location: { kind: 'room', roomId },
      },
    },
  };
}

function updateCorridor(
  state: GameState,
  corridorId: CorridorId,
  patch: Partial<GameState['board']['corridors'][string]>,
): GameState {
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

export function drawAndResolveBagToken(
  state: GameState,
  prng: Mulberry32,
  context: 'corridor' | 'room' | 'hazard',
  roomId: RoomId,
  corridorId?: CorridorId,
): {
  state: GameState;
  events: string[];
  intrusions: NoiseResolutionResult['intrusions'];
} {
  const events: string[] = [];
  const intrusions: NoiseResolutionResult['intrusions'] = [];

  if (state.intruderBag.tokensInBag.length === 0) {
    events.push('Intruder bag is empty - no token drawn.');
    return { state, events, intrusions };
  }

  const tokenIndex = prng.nextInt(0, state.intruderBag.tokensInBag.length - 1);
  const token = state.intruderBag.tokensInBag[tokenIndex]!;
  const newBagTokens = [...state.intruderBag.tokensInBag];
  newBagTokens.splice(tokenIndex, 1);

  let nextState: GameState = {
    ...state,
    intruderBag: {
      ...state.intruderBag,
      tokensInBag: newBagTokens,
    },
  };

  events.push(`Drew bag token: ${token.type.toUpperCase()}${token.backValue ? ` [${token.backValue}]` : ''}`);

  // Blank token returns to bag (INT-001)
  if (token.type === 'blank') {
    events.push('Blank token drawn: returns to bag. Silence.');
    nextState.intruderBag.tokensInBag.push(token);
    return { state: nextState, events, intrusions };
  }

  // Hazard context: spawn single intruder of front type in Room (INT-002)
  if (context === 'hazard' || context === 'room') {
    const intruderType = token.type as IntruderType;
    const spawnRes = spawnIntruder(nextState, intruderType, { kind: 'room', roomId });
    nextState = spawnRes.state;
    events.push(...spawnRes.events);
    if (spawnRes.instanceId) {
      intrusions.push({
        intruderId: spawnRes.instanceId,
        type: intruderType,
        roomId,
        isImmediateAttack: true,
      });
    }
    // Discard token to pool
    nextState.intruderBag.tokensInPool.push(token);
    return { state: nextState, events, intrusions };
  }

  // Corridor context: resolve in corridor using back value (INT-001, INT-002)
  if (context === 'corridor' && corridorId) {
    const corridor = nextState.board.corridors[corridorId];
    if (corridor) {
      if (token.type === 'larva') {
        const spawnRes = spawnIntruder(nextState, 'larva', { kind: 'corridor', corridorId });
        nextState = spawnRes.state;
        events.push(...spawnRes.events);
      } else if (token.type === 'queen') {
        const spawnRes = spawnIntruder(nextState, 'queen', { kind: 'corridor', corridorId });
        nextState = spawnRes.state;
        events.push(...spawnRes.events);
      } else {
        // Adult / Drone back values
        const back = token.backValue ?? '2';
        let adultCount = 0;
        let droneCount = 0;

        if (back === '2') adultCount = 2;
        else if (back === '3') adultCount = 3;
        else if (back === '4') adultCount = 4;
        else if (back === '1+1') { adultCount = 1; droneCount = 1; }
        else if (back === '2+1') { adultCount = 2; droneCount = 1; }
        else if (back === '3+1') { adultCount = 3; droneCount = 1; }

        for (let i = 0; i < adultCount; i++) {
          const spawnRes = spawnIntruder(nextState, 'adult', { kind: 'corridor', corridorId });
          nextState = spawnRes.state;
          events.push(...spawnRes.events);
        }
        for (let i = 0; i < droneCount; i++) {
          const spawnRes = spawnIntruder(nextState, 'drone', { kind: 'corridor', corridorId });
          nextState = spawnRes.state;
          events.push(...spawnRes.events);
        }
      }
    }
    // Discard token to pool
    nextState.intruderBag.tokensInPool.push(token);
  }

  return { state: nextState, events, intrusions };
}

export function spawnIntruder(
  state: GameState,
  type: IntruderType,
  location: IntruderInstance['location'],
): {
  state: GameState;
  instanceId?: string;
  events: string[];
} {
  const events: string[] = [];

  // Check physical model limits
  const availableModels = state.intruderModelsInSupply[type];
  if (availableModels <= 0) {
    events.push(`No available ${type} models in supply - spawn skipped.`);
    return { state, events };
  }

  const instanceId = `intruder-${type}-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  const newInstance: IntruderInstance = {
    id: instanceId,
    type,
    location,
    currentHits: 0,
  };

  const updatedSupply = {
    ...state.intruderModelsInSupply,
    [type]: availableModels - 1,
  };

  const updatedInstances = {
    ...state.intruderInstances,
    [instanceId]: newInstance,
  };

  let nextBoard = { ...state.board };

  if (location.kind === 'room') {
    const room = nextBoard.rooms[location.roomId]!;
    nextBoard = {
      ...nextBoard,
      rooms: {
        ...nextBoard.rooms,
        [location.roomId]: {
          ...room,
          intruderIds: [...room.intruderIds, instanceId],
        },
      },
    };
    events.push(`Spawned ${type} in Room ${room.slotId}`);
  } else {
    const corridor = nextBoard.corridors[location.corridorId]!;
    nextBoard = {
      ...nextBoard,
      corridors: {
        ...nextBoard.corridors,
        [location.corridorId]: {
          ...corridor,
          intruderIds: [...corridor.intruderIds, instanceId],
        },
      },
    };
    events.push(`Spawned ${type} in Corridor ${corridor.corridorId}`);
  }

  return {
    state: {
      ...state,
      board: nextBoard,
      intruderInstances: updatedInstances,
      intruderModelsInSupply: updatedSupply,
    },
    instanceId,
    events,
  };
}
