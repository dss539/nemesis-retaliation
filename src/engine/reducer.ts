/**
 * Authoritative Pure Action-Reducer and Round/Turn engine for Nemesis: Retaliation.
 * Strictly adheres to RT-001, RT-002, RT-004, RT-005, RT-006, RT-007, RT-008, RT-009, and RT-012.
 */

import { GameAction } from './types/actions.js';
import { GameState } from './types/state.js';
import { CharacterId, GamePhase, PlayerId } from './types/primitives.js';
import { CharacterState } from './types/characters.js';
import { Mulberry32 } from './prng/mulberry32.js';
import { OFFICIAL_CHARACTERS_BY_ID } from '../data/characters.js';
import { ACTION_CARDS_BY_CHARACTER } from '../data/action-cards.js';
import { ALL_ITEMS_BY_KEY } from '../data/items.js';
import { ItemCard } from './types/items.js';

export interface ReducerResult {
  state: GameState;
  events: string[];
}

export function gameReducer(state: GameState, action: GameAction): GameState {
  const result = gameReducerWithEvents(state, action);
  return result.state;
}

export function gameReducerWithEvents(state: GameState, action: GameAction): ReducerResult {
  if (state.isGameOver) {
    throw new Error('Cannot dispatch actions when game is over');
  }

  // Action monotonic sequence check
  const expectedActionId = state.lastActionId + 1;
  const actionToRecord: GameAction = {
    ...action,
    actionId: expectedActionId,
    timestamp: action.timestamp || Date.now(),
  };

  const prng = new Mulberry32();
  prng.importState(state.prngState);

  const events: string[] = [];

  let nextState: GameState = {
    ...state,
    lastActionId: expectedActionId,
    actionHistory: [...state.actionHistory, actionToRecord],
  };

  switch (action.type) {
    case 'draft_character': {
      nextState = handleDraftCharacter(nextState, action.playerId, action.characterId, prng, events);
      break;
    }
    case 'play_action_card': {
      nextState = handlePlayActionCard(nextState, action.characterId, action.cardId, events);
      break;
    }
    case 'move':
    case 'move_cautiously':
    case 'shoot':
    case 'burst':
    case 'melee':
    case 'search':
    case 'use_room':
    case 'place_secure':
    case 'trade': {
      nextState = handleBasicActionCost(nextState, action.characterId, action.discardCardIds, action.type, events);
      break;
    }
    case 'pass': {
      nextState = handlePass(nextState, action.characterId, action.discardCardIds ?? [], events);
      break;
    }
    case 'end_player_turn': {
      nextState = handleEndPlayerTurn(nextState, action.characterId, events);
      break;
    }
    case 'resolve_intruder_phase': {
      nextState = handleResolveIntruderPhase(nextState, events);
      break;
    }
    case 'resolve_event_phase': {
      nextState = handleResolveEventPhase(nextState, events);
      break;
    }
    case 'resolve_cleanup_phase': {
      nextState = handleResolveCleanupPhase(nextState, prng, events);
      break;
    }
    default:
      throw new Error(`Unhandled action type: ${(action as any).type}`);
  }

  nextState.prngState = prng.exportState();
  return { state: nextState, events };
}

function handleDraftCharacter(
  state: GameState,
  playerId: PlayerId,
  characterId: CharacterId,
  prng: Mulberry32,
  events: string[],
): GameState {
  if (state.phase !== 'setup') {
    throw new Error(`Character drafting is only allowed during setup phase, current: ${state.phase}`);
  }

  const player = state.players.find(p => p.playerId === playerId);
  if (!player) {
    throw new Error(`Player ${playerId} not found`);
  }
  if (player.characterId) {
    throw new Error(`Player ${playerId} has already drafted character ${player.characterId}`);
  }

  if (!state.characterDraftPool.includes(characterId)) {
    throw new Error(`Character ${characterId} is not in the draft pool`);
  }

  const def = OFFICIAL_CHARACTERS_BY_ID[characterId];
  if (!def) {
    throw new Error(`Character definition not found for ${characterId}`);
  }

  // Initialize character deck & hand (10 cards shuffled, draw 5 into hand)
  const baseCards = ACTION_CARDS_BY_CHARACTER[characterId] ?? [];
  const actionCardCopies = baseCards.map(c => ({
    id: c.id,
    title: c.title,
    characterId: c.characterId,
    notInCombat: c.notInCombat,
    isReaction: c.isReaction,
    rulesText: c.rulesText,
  }));
  const shuffledDeck = prng.shuffle(actionCardCopies);
  const hand = shuffledDeck.slice(0, 5);
  const drawDeck = shuffledDeck.slice(5);

  // Starting Weapon
  const weaponDef = ALL_ITEMS_BY_KEY[def.startingWeaponKey];
  const startingWeapon: ItemCard | undefined = weaponDef
    ? {
        id: `start-weapon-${characterId}`,
        title: weaponDef.title,
        category: 'starting',
        isHeavy: weaponDef.isHeavy,
        isWeapon: weaponDef.isWeapon,
        weaponType: weaponDef.weaponType,
        requiresNoAmmo: weaponDef.requiresNoAmmo,
        ammo: weaponDef.ammoCapacity,
        maxAmmo: weaponDef.ammoCapacity,
        rulesText: weaponDef.rulesText,
      }
    : undefined;

  // Starting Armor (Contractor)
  const armorDef = def.startingArmorKey ? ALL_ITEMS_BY_KEY[def.startingArmorKey] : undefined;
  const startingArmor: ItemCard | undefined = armorDef
    ? {
        id: `start-armor-${characterId}`,
        title: armorDef.title,
        category: 'starting',
        isHeavy: armorDef.isHeavy,
        isWeapon: armorDef.isWeapon,
        weaponType: armorDef.weaponType,
        requiresNoAmmo: armorDef.requiresNoAmmo,
        rulesText: armorDef.rulesText,
      }
    : undefined;

  const characterState: CharacterState = {
    characterId,
    playerId,
    name: def.name,
    rank: def.rank,
    health: def.maxHealth,
    maxHealth: def.maxHealth,
    oxygen: def.startingOxygen,
    isSuffocating: false,
    seriousWounds: [],
    currentRoomId: 'landing-zone',
    hand,
    drawDeck,
    discardPile: [],
    contaminationHand: [],
    inventory: {
      equippedWeapon: startingWeapon,
      equippedArmor: startingArmor,
      backpack: [],
      tacticalGear: [],
    },
    heldObjectives: [],
    hasPassed: false,
    actionsRemaining: 2,
    isAlive: true,
    hasEscaped: false,
  };

  // Update player
  const updatedPlayers = state.players.map(p =>
    p.playerId === playerId ? { ...p, characterId } : p,
  );

  // Update room occupancy
  const lz = state.board.rooms['landing-zone']!;
  const updatedRooms = {
    ...state.board.rooms,
    'landing-zone': {
      ...lz,
      characterIds: [...lz.characterIds, characterId],
    },
  };

  const updatedCharacters = {
    ...state.characters,
    [characterId]: characterState,
  };

  const updatedPool = state.characterDraftPool.filter(c => c !== characterId);

  events.push(`${player.name} drafted ${def.name}`);

  // Check if all players have drafted
  const allDrafted = updatedPlayers.every(p => p.characterId !== undefined);

  let nextPhase: GamePhase = state.phase;
  let activePlayerIndex = state.activePlayerIndex;
  let startingPlayerIndex = state.startingPlayerIndex;

  if (allDrafted) {
    nextPhase = 'player';
    activePlayerIndex = 0;
    startingPlayerIndex = 0;
    events.push(`All players drafted. Round 1 Player Phase begins. Starting Player: ${updatedPlayers[0]!.name}`);
  }

  return {
    ...state,
    phase: nextPhase,
    activePlayerIndex,
    startingPlayerIndex,
    players: updatedPlayers,
    characters: updatedCharacters,
    characterDraftPool: updatedPool,
    board: {
      ...state.board,
      rooms: updatedRooms,
    },
  };
}

function handlePlayActionCard(
  state: GameState,
  characterId: CharacterId,
  cardId: string,
  events: string[],
): GameState {
  validatePlayerTurnAction(state, characterId);

  const char = state.characters[characterId]!;
  const cardIndex = char.hand.findIndex(c => c.id === cardId);
  if (cardIndex === -1) {
    throw new Error(`Card ${cardId} is not in ${char.name}'s hand`);
  }

  const card = char.hand[cardIndex]!;

  // RT-006: Check Not In Combat
  if (card.notInCombat) {
    const currentRoom = state.board.rooms[char.currentRoomId];
    if (currentRoom && currentRoom.intruderIds.length > 0) {
      throw new Error(`Cannot play ${card.title}: character is in combat in ${currentRoom.slotId}`);
    }
  }

  const newHand = [...char.hand];
  newHand.splice(cardIndex, 1);
  const newDiscard = [card, ...char.discardPile];

  events.push(`${char.name} played Action Card: ${card.title}`);

  const updatedChar: CharacterState = {
    ...char,
    hand: newHand,
    discardPile: newDiscard,
    actionsRemaining: char.actionsRemaining - 1,
  };

  const updatedState: GameState = {
    ...state,
    characters: {
      ...state.characters,
      [characterId]: updatedChar,
    },
    turnActionsTaken: state.turnActionsTaken + 1,
  };

  // If 2 actions taken, end turn
  if (updatedChar.actionsRemaining === 0) {
    return handleEndPlayerTurn(updatedState, characterId, events);
  }

  return updatedState;
}

function handleBasicActionCost(
  state: GameState,
  characterId: CharacterId,
  discardCardIds: string[],
  actionType: string,
  events: string[],
): GameState {
  validatePlayerTurnAction(state, characterId);

  const char = state.characters[characterId]!;
  const handIds = new Set(char.hand.map(c => c.id));

  for (const cid of discardCardIds) {
    if (!handIds.has(cid)) {
      throw new Error(`Card ${cid} required to pay for ${actionType} is not in hand`);
    }
  }

  const discardedCards = char.hand.filter(c => discardCardIds.includes(c.id));
  const newHand = char.hand.filter(c => !discardCardIds.includes(c.id));
  const newDiscard = [...discardedCards, ...char.discardPile];

  events.push(`${char.name} performed Basic Action: ${actionType} (discarded ${discardCardIds.length} card(s))`);

  const updatedChar: CharacterState = {
    ...char,
    hand: newHand,
    discardPile: newDiscard,
    actionsRemaining: char.actionsRemaining - 1,
  };

  const updatedState: GameState = {
    ...state,
    characters: {
      ...state.characters,
      [characterId]: updatedChar,
    },
    turnActionsTaken: state.turnActionsTaken + 1,
  };

  if (updatedChar.actionsRemaining === 0) {
    return handleEndPlayerTurn(updatedState, characterId, events);
  }

  return updatedState;
}

function handlePass(
  state: GameState,
  characterId: CharacterId,
  discardCardIds: string[],
  events: string[],
): GameState {
  validatePlayerTurnAction(state, characterId);

  const char = state.characters[characterId]!;
  const discardedCards = char.hand.filter(c => discardCardIds.includes(c.id));
  const newHand = char.hand.filter(c => !discardCardIds.includes(c.id));
  const newDiscard = [...discardedCards, ...char.discardPile];

  events.push(`${char.name} passed for the remainder of Round ${state.round}`);

  const updatedChar: CharacterState = {
    ...char,
    hand: newHand,
    discardPile: newDiscard,
    hasPassed: true,
    actionsRemaining: 0,
  };

  const updatedState: GameState = {
    ...state,
    characters: {
      ...state.characters,
      [characterId]: updatedChar,
    },
  };

  return handleEndPlayerTurn(updatedState, characterId, events);
}

function handleEndPlayerTurn(
  state: GameState,
  characterId: CharacterId,
  events: string[],
): GameState {
  const char = state.characters[characterId]!;
  const currentRoom = state.board.rooms[char.currentRoomId];

  let newOxygen = char.oxygen;
  let newHealth = char.health;
  let isSuffocating = char.isSuffocating;

  // RT-005 step 2: If Character is in a Section with inactive Life Support, lose 1 Oxygen
  if (currentRoom) {
    const isLifeSupportActive = state.lifeSupport[currentRoom.section];
    if (!isLifeSupportActive) {
      newOxygen = Math.max(0, newOxygen - 1);
      events.push(`${char.name} lost 1 Oxygen (Life Support inactive in Section ${currentRoom.section}). Current Oxygen: ${newOxygen}`);
      if (newOxygen === 0) {
        isSuffocating = true;
      }
    }

    // RT-005 step 3: If Character is in a Room with Fire, lose 1 HP
    if (currentRoom.fire) {
      newHealth = Math.max(0, newHealth - 1);
      events.push(`${char.name} took 1 Fire damage in ${currentRoom.slotId}. Current Health: ${newHealth}`);
    }
  }

  const updatedChar: CharacterState = {
    ...char,
    oxygen: newOxygen,
    health: newHealth,
    isSuffocating,
    isAlive: newHealth > 0,
  };

  const updatedCharacters = {
    ...state.characters,
    [characterId]: updatedChar,
  };

  // Find next player in clockwise order who has NOT passed
  const playerCount = state.players.length;
  let nextPlayerIndex = -1;

  for (let offset = 1; offset <= playerCount; offset++) {
    const candidateIdx = (state.activePlayerIndex + offset) % playerCount;
    const candidatePlayer = state.players[candidateIdx]!;
    if (candidatePlayer.characterId) {
      const candidateChar = updatedCharacters[candidatePlayer.characterId];
      if (candidateChar && candidateChar.isAlive && !candidateChar.hasPassed && !candidateChar.hasEscaped) {
        nextPlayerIndex = candidateIdx;
        break;
      }
    }
  }

  // If no players remain who can take turns, transition to Intruder Phase! (RT-004 step 3-4)
  if (nextPlayerIndex === -1) {
    events.push(`All players have passed. Transitioning to Intruder Phase.`);
    return {
      ...state,
      characters: updatedCharacters,
      phase: 'intruder',
      turnActionsTaken: 0,
    };
  }

  // Advance turn to next active player
  const nextPlayer = state.players[nextPlayerIndex]!;
  const nextChar = updatedCharacters[nextPlayer.characterId!]!;
  updatedCharacters[nextPlayer.characterId!] = {
    ...nextChar,
    actionsRemaining: 2,
  };

  events.push(`Turn passed to ${nextPlayer.name} (${nextChar.name})`);

  return {
    ...state,
    characters: updatedCharacters,
    activePlayerIndex: nextPlayerIndex,
    turnActionsTaken: 0,
  };
}

function handleResolveIntruderPhase(state: GameState, events: string[]): GameState {
  if (state.phase !== 'intruder') {
    throw new Error(`Cannot resolve Intruder Phase when in ${state.phase} phase`);
  }

  events.push(`Intruder Phase resolved.`);
  // RT-001: Next phase is Event Phase
  return {
    ...state,
    phase: 'event',
  };
}

function handleResolveEventPhase(state: GameState, events: string[]): GameState {
  if (state.phase !== 'event') {
    throw new Error(`Cannot resolve Event Phase when in ${state.phase} phase`);
  }

  events.push(`Event Phase resolved.`);
  // RT-001: Next phase is Cleanup Phase
  return {
    ...state,
    phase: 'cleanup',
  };
}

function handleResolveCleanupPhase(state: GameState, prng: Mulberry32, events: string[]): GameState {
  if (state.phase !== 'cleanup') {
    throw new Error(`Cannot resolve Cleanup Phase when in ${state.phase} phase`);
  }

  events.push(`Cleanup Phase: Advancing Starting Player and dealing cards.`);

  // 1. Advance Starting Player clockwise (RT-012 step 6)
  const newStartingPlayerIndex = (state.startingPlayerIndex + 1) % state.players.length;
  const updatedPlayers = state.players.map((p, idx) => ({
    ...p,
    isStartingPlayer: idx === newStartingPlayerIndex,
  }));

  // 2. Reset passed state and draw cards up to 5 (RT-012 step 7)
  const updatedCharacters: Partial<Record<CharacterId, CharacterState>> = {};
  for (const [cid, char] of Object.entries(state.characters)) {
    if (!char) continue;
    let hand = [...char.hand];
    let drawDeck = [...char.drawDeck];
    let discardPile = [...char.discardPile];

    while (hand.length < 5) {
      if (drawDeck.length === 0) {
        if (discardPile.length === 0) break;
        drawDeck = prng.shuffle(discardPile);
        discardPile = [];
      }
      const drawn = drawDeck.shift();
      if (drawn) hand.push(drawn);
    }

    updatedCharacters[cid as CharacterId] = {
      ...char,
      hand,
      drawDeck,
      discardPile,
      hasPassed: false,
      actionsRemaining: 2,
    };
  }

  // 3. Time advancement (RT-012 step 8)
  const nextRound = state.round + 1;
  if (nextRound > 15) {
    events.push(`Round 15 exceeded. Game Over: Time limit reached.`);
    return {
      ...state,
      phase: 'game-over',
      isGameOver: true,
      gameResult: {
        winners: [],
        losers: state.players.map(p => p.playerId),
        reason: 'Time limit reached (Round track exceeded)',
      },
    };
  }

  events.push(`Beginning Round ${nextRound} Player Phase.`);

  return {
    ...state,
    phase: 'player',
    round: nextRound,
    players: updatedPlayers,
    characters: updatedCharacters,
    startingPlayerIndex: newStartingPlayerIndex,
    activePlayerIndex: newStartingPlayerIndex,
    turnActionsTaken: 0,
  };
}

function validatePlayerTurnAction(state: GameState, characterId: CharacterId): void {
  if (state.phase !== 'player') {
    throw new Error(`Actions can only be performed during the Player Phase (current: ${state.phase})`);
  }

  const activePlayer = state.players[state.activePlayerIndex];
  if (!activePlayer || activePlayer.characterId !== characterId) {
    throw new Error(`It is not ${characterId}'s turn (active player: ${activePlayer?.playerId} / ${activePlayer?.characterId})`);
  }

  const char = state.characters[characterId];
  if (!char || !char.isAlive) {
    throw new Error(`Character ${characterId} is not alive or not found`);
  }

  if (char.hasPassed) {
    throw new Error(`Character ${characterId} has already passed this round`);
  }
}
