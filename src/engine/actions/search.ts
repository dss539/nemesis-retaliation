/**
 * Room Search action execution for Nemesis: Retaliation.
 * Strictly adheres to ACT-SEARCH-001, Rulebook p. 12, and p. 27.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterId, ItemColor } from '../types/primitives.js';
import { ItemCard } from '../types/items.js';

export interface SearchResult {
  state: GameState;
  drawnItems: ItemCard[];
  chosenItem?: ItemCard;
  events: string[];
}

export function executeRoomSearch(
  state: GameState,
  characterId: CharacterId,
  chosenItemIndexToKeep: number,
  prng: Mulberry32,
): SearchResult {
  const events: string[] = [];
  const char = state.characters[characterId];
  if (!char) throw new Error(`Character ${characterId} not found`);

  const room = state.board.rooms[char.currentRoomId];
  if (!room) throw new Error(`Room ${char.currentRoomId} not found`);
  if (!room.isDiscovered || !room.tile) {
    throw new Error(`Cannot search an undiscovered room`);
  }

  // Preconditions
  if (room.intruderIds.length > 0) {
    throw new Error(`Cannot search while in Combat (Intruders in room)`);
  }
  if (room.searchTokens <= 0) {
    throw new Error(`Room has no search tokens remaining`);
  }
  if (room.tile.sectionKind === 'A' && room.tile.roomNumber === '14') {
    // Landing Zone has no items to search
    throw new Error(`Landing Zone cannot be searched for items`);
  }

  // Find item colors available in this room from room tile definition
  const colorsToDraw: ItemColor[] = getRoomItemColors(room.tile.roomNumber ?? '01');
  if (colorsToDraw.length === 0) {
    throw new Error(`Room ${room.tile.name} does not contain any item search types`);
  }

  const drawnItems: ItemCard[] = [];
  let nextDecks = { ...state.itemDecks };

  for (const color of colorsToDraw) {
    const deck = nextDecks[color];
    const discard = color === 'red' ? nextDecks.redDiscard : color === 'yellow' ? nextDecks.yellowDiscard : nextDecks.greenDiscard;

    let cardToDraw: ItemCard | undefined;
    if (deck.length > 0) {
      cardToDraw = deck[0];
      nextDecks = {
        ...nextDecks,
        [color]: deck.slice(1),
      };
    } else if (discard.length > 0) {
      // Reshuffle discard pile
      const reshuffled = prng.shuffle([...discard]);
      cardToDraw = reshuffled[0];
      nextDecks = {
        ...nextDecks,
        [color]: reshuffled.slice(1),
        [color === 'red' ? 'redDiscard' : color === 'yellow' ? 'yellowDiscard' : 'greenDiscard']: [],
      };
    }

    if (cardToDraw) {
      drawnItems.push(cardToDraw);
      events.push(`Drawn ${color.toUpperCase()} Item: ${cardToDraw.title}`);
    }
  }

  if (drawnItems.length === 0) {
    events.push(`All search decks for room colors are empty - no items drawn.`);
    return { state, drawnItems, events };
  }

  // Player chooses 1 item to keep
  const keepIndex = Math.min(Math.max(0, chosenItemIndexToKeep), drawnItems.length - 1);
  const keptItem = drawnItems[keepIndex]!;
  const discardedItems = drawnItems.filter((_, idx) => idx !== keepIndex);

  events.push(`${char.name} keeps ${keptItem.title} and discards ${discardedItems.map(i => i.title).join(', ') || 'none'}`);

  // Put discarded items into their respective discard piles
  let nextRedDiscard = [...nextDecks.redDiscard];
  let nextYellowDiscard = [...nextDecks.yellowDiscard];
  let nextGreenDiscard = [...nextDecks.greenDiscard];

  for (const item of discardedItems) {
    if (item.category === 'red') nextRedDiscard.push(item);
    else if (item.category === 'yellow') nextYellowDiscard.push(item);
    else if (item.category === 'green') nextGreenDiscard.push(item);
  }

  nextDecks = {
    ...nextDecks,
    redDiscard: nextRedDiscard,
    yellowDiscard: nextYellowDiscard,
    greenDiscard: nextGreenDiscard,
  };

  // Add kept item to character inventory
  const updatedInventory = {
    ...char.inventory,
    backpack: [...char.inventory.backpack, keptItem],
  };

  // Decrement room search tokens
  const nextRooms = {
    ...state.board.rooms,
    [room.slotId]: {
      ...room,
      searchTokens: Math.max(0, room.searchTokens - 1),
    },
  };

  const nextState: GameState = {
    ...state,
    board: {
      ...state.board,
      rooms: nextRooms,
    },
    itemDecks: nextDecks,
    characters: {
      ...state.characters,
      [characterId]: {
        ...char,
        inventory: updatedInventory,
      },
    },
  };

  return {
    state: nextState,
    drawnItems,
    chosenItem: keptItem,
    events,
  };
}

function getRoomItemColors(roomNumber: string): ItemColor[] {
  // Mapping of official room numbers to their search item icons
  const mapping: Record<string, ItemColor[]> = {
    '01': ['green', 'yellow'],
    '02': ['green', 'red'],
    '03': ['green'],
    '04': ['green', 'red', 'yellow'],
    '05': ['red'],
    '06': ['red', 'yellow'],
    '07': ['red', 'yellow'],
    '08': ['red'],
    '09': ['yellow'],
    '10': ['green', 'red'],
    '11': ['red', 'yellow'],
    '12': ['yellow'],
    '13': ['green'],
    '15': ['green', 'red'],
    '16': ['green'],
    '17': ['yellow'],
    '19': ['green', 'red'],
    '20': ['red', 'yellow'],
    '21': ['yellow'],
    '22': ['green', 'red'],
    '23': ['red', 'yellow'],
    '24': ['green', 'red'],
  };

  return mapping[roomNumber] ?? ['yellow'];
}
