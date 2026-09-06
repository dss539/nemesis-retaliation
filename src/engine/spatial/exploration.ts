/**
 * Exploration Sequence execution for Nemesis: Retaliation.
 * Strictly adheres to ACT-EXPLORE-001, SEM-Q-002, and Rulebook p. 24.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterId, CorridorId, RoomId, Section } from '../types/primitives.js';
import { RoomTileData } from '../types/board.js';
import { EXPLORATION_CARDS, ExplorationCardDefinition } from '../../data/exploration-cards.js';
import { OFFICIAL_ROOMS, RoomDefinition } from '../../data/rooms.js';
import { CORRIDOR_TILES, CorridorTileDefinition } from '../../data/corridors.js';
import { getNeighborPos, getSlotId, makeCorridorId } from './hex.js';
import { resolveNoiseRoll, spawnIntruder } from '../combat/noise.js';

export interface ExplorationResult {
  state: GameState;
  drawnCard: ExplorationCardDefinition;
  placedRoom: RoomTileData;
  events: string[];
}

export function executeExplorationSequence(
  state: GameState,
  characterId: CharacterId,
  enteredCorridorId: CorridorId,
  targetRoomId: RoomId,
  prng: Mulberry32,
  isCautious: boolean = false,
): ExplorationResult {
  const events: string[] = [];
  const char = state.characters[characterId];
  if (!char) throw new Error(`Character ${characterId} not found`);

  const targetSlot = state.board.rooms[targetRoomId];
  if (!targetSlot) throw new Error(`Target room slot ${targetRoomId} not found`);
  if (targetSlot.isDiscovered) {
    throw new Error(`Target room slot ${targetRoomId} is already discovered`);
  }

  // 1. Draw Exploration Card (ACT-EXPLORE-001 step 1)
  const cardIndex = prng.nextInt(0, EXPLORATION_CARDS.length - 1);
  const card = EXPLORATION_CARDS[cardIndex]!;
  events.push(`${char.name} drew Exploration Card ${card.number} (${card.roomType})`);

  // 2. Set up Room (ACT-EXPLORE-001 step 2)
  const roomTile = selectRoomTile(state, card.roomType, targetSlot.section, prng);
  events.push(`Discovered Room ${roomTile.roomNumber}: ${roomTile.name} in Section ${targetSlot.section}`);

  const placedRoomData: RoomTileData = {
    tileId: roomTile.id,
    name: roomTile.name,
    roomNumber: roomTile.roomNumber,
    sectionKind: roomTile.sectionMarker,
    maxSearches: roomTile.items.length * 2, // 2 items per listed item type
    hasComputer: roomTile.hasComputer,
    actionDescription: roomTile.actionEffect,
  };

  let nextBoard = { ...state.board };
  let nextRooms = { ...nextBoard.rooms };
  let nextCorridors = { ...nextBoard.corridors };

  // Determine markers to place on room (step 4)
  const hasFire = card.tokens.includes('fire');
  const hasMalfunction = card.tokens.includes('malfunction');
  const initialSecure = isCautious ? 1 : 0;

  nextRooms[targetRoomId] = {
    ...targetSlot,
    isDiscovered: true,
    tile: placedRoomData,
    fire: hasFire,
    malfunction: hasMalfunction,
    secureTokens: initialSecure,
    characterIds: [...targetSlot.characterIds, characterId],
  };

  if (hasFire) events.push(`Placed Fire marker in ${placedRoomData.name}`);
  if (hasMalfunction) events.push(`Placed Malfunction marker in ${placedRoomData.name}`);
  if (initialSecure) events.push(`Placed Secure token (Cautious movement) in ${placedRoomData.name}`);

  // 3. Set up Corridors (ACT-EXPLORE-001 step 3)
  const slotPos = { x: targetSlot.coord.q + (targetSlot.coord.r - (targetSlot.coord.r & 1)) / 2, y: targetSlot.coord.r };

  for (const dir of card.corridorDirections) {
    const neighborPos = getNeighborPos(slotPos, dir);
    if (!neighborPos) continue; // Outside facility border -> omitted

    const neighborSlotId = getSlotId(neighborPos.x, neighborPos.y);
    const corridorId = makeCorridorId(targetRoomId, neighborSlotId);

    // Skip if corridor already exists or neighbor already has a room
    if (nextCorridors[corridorId]) continue;
    const neighborSlot = nextRooms[neighborSlotId];
    if (neighborSlot && neighborSlot.isDiscovered) continue;

    // Draw random corridor tile from pool
    const corrTileIdx = prng.nextInt(0, CORRIDOR_TILES.length - 1);
    const corrTile: CorridorTileDefinition = CORRIDOR_TILES[corrTileIdx]!;

    const hasNoise = card.noiseDirections.includes(dir);

    nextCorridors[corridorId] = {
      corridorId,
      slotA: targetRoomId,
      slotB: neighborSlotId,
      directionFromA: dir,
      noiseValue: corrTile.noiseValue,
      hasNoise,
      doorState: corrTile.hasDoor ? 'open' : 'open', // New doors start open unless entrance closes them
      isTechnical: false,
      intruderIds: [],
    };

    events.push(`Placed Corridor in direction ${dir} (Noise value: ${corrTile.noiseValue}${hasNoise ? ', with Noise' : ''})`);
  }

  // 5. Move Character into new Room (ACT-EXPLORE-001 step 5)
  // Remove character from previous room
  const prevRoomId = char.currentRoomId;
  const prevRoom = nextRooms[prevRoomId];
  if (prevRoom) {
    nextRooms[prevRoomId] = {
      ...prevRoom,
      characterIds: prevRoom.characterIds.filter(id => id !== characterId),
    };
  }

  let nextState: GameState = {
    ...state,
    board: {
      ...nextBoard,
      rooms: nextRooms,
      corridors: nextCorridors,
    },
    characters: {
      ...state.characters,
      [characterId]: {
        ...char,
        currentRoomId: targetRoomId,
      },
    },
  };

  events.push(`${char.name} moved into ${placedRoomData.name}`);

  // 6. Entrance Effect (ACT-EXPLORE-001 step 6)
  // Close doors if instructed
  if (card.closeDoor) {
    events.push(`Entrance Effect: Closing all Doors touching ${placedRoomData.name}`);
    for (const [cid, corr] of Object.entries(nextState.board.corridors)) {
      if (corr.slotA === targetRoomId || corr.slotB === targetRoomId) {
        nextState.board.corridors[cid] = {
          ...corr,
          doorState: 'closed',
        };
      }
    }
  }

  // Spawn intruders in corridor passed through if instructed
  if (card.intrudersToAdd > 0) {
    events.push(`Entrance Effect: Spawning ${card.intrudersToAdd} Adult(s) in Corridor ${enteredCorridorId}!`);
    for (let i = 0; i < card.intrudersToAdd; i++) {
      const spawnRes = spawnIntruder(nextState, 'adult', { kind: 'corridor', corridorId: enteredCorridorId });
      nextState = spawnRes.state;
      events.push(...spawnRes.events);
    }
  }

  // Noise roll if explicitly instructed (SEM-Q-002)
  if (card.noiseRoll) {
    events.push(`Entrance Effect: Performing required Noise Roll`);
    const noiseRes = resolveNoiseRoll(nextState, characterId, prng);
    nextState = noiseRes.state;
    events.push(...noiseRes.events);
  }

  return {
    state: nextState,
    drawnCard: card,
    placedRoom: placedRoomData,
    events,
  };
}

function selectRoomTile(
  state: GameState,
  requiredType: ExplorationCardDefinition['roomType'],
  slotSection: Section,
  prng: Mulberry32,
): RoomDefinition {
  // Find all rooms already placed on the board
  const placedRoomNumbers = new Set(
    Object.values(state.board.rooms)
      .map(r => r.tile?.roomNumber)
      .filter((n): n is string => n !== undefined),
  );

  let candidateRooms: RoomDefinition[] = [];

  if (requiredType === '?') {
    candidateRooms = OFFICIAL_ROOMS.filter(
      r => r.sectionMarker === '?' && !placedRoomNumbers.has(r.roomNumber),
    );
  } else {
    // ABC: match section of the slot (A, B, or C)
    candidateRooms = OFFICIAL_ROOMS.filter(
      r => r.sectionMarker === slotSection && !placedRoomNumbers.has(r.roomNumber),
    );
    // If section stack is empty, fallback to '?' rooms
    if (candidateRooms.length === 0) {
      candidateRooms = OFFICIAL_ROOMS.filter(
        r => r.sectionMarker === '?' && !placedRoomNumbers.has(r.roomNumber),
      );
    }
  }

  if (candidateRooms.length === 0) {
    // Ultimate fallback if all matching rooms placed: pick any unplaced room
    candidateRooms = OFFICIAL_ROOMS.filter(r => !placedRoomNumbers.has(r.roomNumber));
  }

  const chosen = prng.draw(candidateRooms);
  if (!chosen) {
    throw new Error('No available room tiles remaining to place');
  }
  return chosen;
}
