/**
 * Initial game state creation and setup procedures for Nemesis: Retaliation.
 * Derived from official rulebook setup instructions pp. 8-10, INT-001, FND-005, FND-006, and RT-001.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import {
  CharacterId,
  PlayerId,
} from '../types/primitives.js';
import {
  BoardState,
  CorridorState,
  createHexCoord,
  RoomSlotState,
} from '../types/board.js';
import {
  GameState,
  ItemDecksState,
} from '../types/state.js';
import {
  IntruderBagState,
  IntruderToken,
  INTRUDER_MODEL_LIMITS,
  TokenBackValue,
} from '../types/intruders.js';
import { PlayerState } from '../types/characters.js';
import { BOARD_SLOTS, getValidNeighbors, makeCorridorId } from '../spatial/hex.js';
import { OFFICIAL_ROOMS_BY_NUMBER } from '../../data/rooms.js';
import { ALL_ITEMS } from '../../data/items.js';
import { ItemCard } from '../types/items.js';

export interface SetupOptions {
  gameId?: string;
  seed?: number;
  playerCount: number; // 1 to 5 players (base game)
  playerNames?: string[];
}

export function createInitialGameState(options: SetupOptions): GameState {
  const playerCount = Math.max(1, Math.min(5, options.playerCount));
  const seed = options.seed ?? Date.now();
  const prng = new Mulberry32(seed);
  const gameId = options.gameId ?? `game-${seed}`;

  // 1. Players setup
  const players: PlayerState[] = [];
  for (let i = 0; i < playerCount; i++) {
    const playerId: PlayerId = `player-${i + 1}`;
    const name = options.playerNames?.[i] ?? `Player ${i + 1}`;
    players.push({
      playerId,
      name,
      isStartingPlayer: i === 0,
    });
  }

  // 2. Character draft pool (all 6 characters shuffled)
  const allCharacters: CharacterId[] = [
    'officer',
    'combat-engineer',
    'contractor',
    'recon',
    'medical-support',
    'heavy-gun-operator',
  ];
  const characterDraftPool = prng.shuffle(allCharacters);

  // 3. Intruder Bag setup (INT-001)
  // 40 tokens total: 1 Blank, 9 Queen, 8 Drone, 16 Adult, 6 Larva
  // Initial bag: 1 Blank, 2 Larva, (3 + playerCount) Adult
  const adultBackValues: TokenBackValue[] = [
    '2', '2', '2',
    '3', '3', '3',
    '4', '4',
    '1+1', '1+1',
    '2+1', '2+1', '2+1',
    '3+1', '3+1', '3+1',
  ];

  const allAdultTokens: IntruderToken[] = adultBackValues.map((backValue, i) => ({
    id: `token-adult-${i + 1}`,
    type: 'adult',
    backValue,
  }));
  const shuffledAdults = prng.shuffle(allAdultTokens);

  const initialAdultCountInBag = 3 + playerCount;
  const bagAdults = shuffledAdults.slice(0, initialAdultCountInBag);
  const poolAdults = shuffledAdults.slice(initialAdultCountInBag);

  const allLarvaTokens: IntruderToken[] = Array.from({ length: 6 }, (_, i) => ({
    id: `token-larva-${i + 1}`,
    type: 'larva',
  }));
  const bagLarva = allLarvaTokens.slice(0, 2);
  const poolLarva = allLarvaTokens.slice(2);

  const blankToken: IntruderToken = { id: 'token-blank-1', type: 'blank' };

  const poolQueenTokens: IntruderToken[] = Array.from({ length: 9 }, (_, i) => ({
    id: `token-queen-${i + 1}`,
    type: 'queen',
  }));

  const poolDroneTokens: IntruderToken[] = Array.from({ length: 8 }, (_, i) => ({
    id: `token-drone-${i + 1}`,
    type: 'drone',
  }));

  const tokensInBag = prng.shuffle([blankToken, ...bagLarva, ...bagAdults]);
  const tokensInPool = [...poolAdults, ...poolLarva, ...poolQueenTokens, ...poolDroneTokens];

  const intruderBag: IntruderBagState = {
    tokensInBag,
    tokensInPool,
    isQueenAlive: true,
  };

  // 4. Board setup (23 slots, Landing Zone at (0, 2) in Section A)
  const rooms: Record<string, RoomSlotState> = {};
  for (const slot of BOARD_SLOTS) {
    const isLz = slot.isLandingZone;
    const lzTile = isLz ? OFFICIAL_ROOMS_BY_NUMBER['14'] : undefined;

    rooms[slot.slotId] = {
      slotId: slot.slotId,
      coord: createHexCoord(slot.x, slot.y),
      section: slot.section,
      isLandingZone: isLz,
      isDiscovered: isLz, // Landing zone begins discovered
      tile: lzTile
        ? {
            tileId: lzTile.id,
            name: lzTile.name,
            roomNumber: lzTile.roomNumber,
            sectionKind: lzTile.sectionMarker,
            maxSearches: 0,
            hasComputer: lzTile.hasComputer,
            actionDescription: lzTile.actionEffect,
          }
        : undefined,
      searchTokens: 0,
      fire: false,
      malfunction: false,
      secureTokens: 0,
      eggTokens: 0,
      dataTokens: 0,
      universalMarkers: 0,
      characterIds: [],
      intruderIds: [],
    };
  }

  // Corridors from Landing Zone to adjacent slots
  const corridors: Record<string, CorridorState> = {};
  const lzPos = { x: 0, y: 2 };
  const lzNeighbors = getValidNeighbors(lzPos);

  // Available corridor noise values: deal random 1..4
  for (const [dir, neighborPos] of Object.entries(lzNeighbors)) {
    if (!neighborPos) continue;
    const neighborSlotId = `slot_${neighborPos.x}_${neighborPos.y}`;
    const corridorId = makeCorridorId('landing-zone', neighborSlotId);
    corridors[corridorId] = {
      corridorId,
      slotA: 'landing-zone',
      slotB: neighborSlotId,
      directionFromA: dir as any,
      noiseValue: prng.nextInt(1, 4),
      hasNoise: false,
      doorState: 'open',
      isTechnical: false,
      intruderIds: [],
    };
  }

  const board: BoardState = {
    rooms,
    corridors,
  };

  // 5. Item Decks setup
  const toItemCard = (def: (typeof ALL_ITEMS)[number]): ItemCard => ({
    id: def.id,
    title: def.title,
    category: def.category,
    isHeavy: def.isHeavy,
    isWeapon: def.isWeapon,
    weaponType: def.weaponType,
    requiresNoAmmo: def.requiresNoAmmo,
    ammo: def.ammoCapacity > 0 ? def.ammoCapacity : undefined,
    maxAmmo: def.ammoCapacity > 0 ? def.ammoCapacity : undefined,
    rulesText: def.rulesText,
  });

  const redItems: ItemCard[] = [];
  const yellowItems: ItemCard[] = [];
  const greenItems: ItemCard[] = [];
  const questItems: ItemCard[] = [];

  for (const item of ALL_ITEMS) {
    const card = toItemCard(item);
    for (let c = 0; c < item.countInDeck; c++) {
      const copy: ItemCard = { ...card, id: `${card.id}-${c + 1}` };
      if (item.color === 'red') redItems.push(copy);
      else if (item.color === 'yellow') yellowItems.push(copy);
      else if (item.color === 'green') greenItems.push(copy);
      else if (item.category === 'quest') questItems.push(copy);
    }
  }

  const itemDecks: ItemDecksState = {
    red: prng.shuffle(redItems),
    yellow: prng.shuffle(yellowItems),
    green: prng.shuffle(greenItems),
    quest: questItems,
    redDiscard: [],
    yellowDiscard: [],
    greenDiscard: [],
  };

  // 6. Contamination Deck (typically 27 cards, 20 uninfected, 7 infected)
  const contaminationCards = [
    ...Array.from({ length: 20 }, (_, i) => ({ id: `contam-clean-${i + 1}`, isInfected: false })),
    ...Array.from({ length: 7 }, (_, i) => ({ id: `contam-infected-${i + 1}`, isInfected: true })),
  ];

  return {
    gameId,
    seed,
    prngState: prng.exportState(),
    phase: 'setup',
    round: 1,
    startingPlayerIndex: 0,
    activePlayerIndex: 0,
    turnActionsTaken: 0,

    players,
    characters: {},
    characterDraftPool,

    board,
    intruderBag,
    intruderInstances: {},
    intruderModelsInSupply: { ...INTRUDER_MODEL_LIMITS },
    queenTrack: { hits: 0, isAlive: true },

    itemDecks,
    eventDeck: [],
    eventDiscard: [],
    objectiveDeck: [],
    seriousWoundsDeck: [],
    contaminationDeck: prng.shuffle(contaminationCards),

    lifeSupport: { A: true, B: true, C: true },
    hibernatoriumActive: false,
    autodestruction: { isActive: false },
    antiAircraft: {
      topToken: 'active',
      bottomToken: 'active',
      isKnownByPlayerIds: [],
    },

    actionHistory: [],
    lastActionId: 0,
    isGameOver: false,
  };
}
