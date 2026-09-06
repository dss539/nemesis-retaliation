/**
 * Cleanup Phase execution for Nemesis: Retaliation.
 * Strictly adheres to RT-012, Rulebook pp. 14–15, and endgame triggers.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { CharacterState } from '../types/characters.js';

export interface CleanupPhaseResult {
  state: GameState;
  events: string[];
}

export function resolveCleanupPhase(state: GameState, prng: Mulberry32): CleanupPhaseResult {
  const events: string[] = ['=== CLEANUP PHASE ==='];
  let nextState: GameState = { ...state };

  // 1. Advance Starting Player token clockwise (RT-012)
  const newStartingPlayerIndex = (state.startingPlayerIndex + 1) % state.players.length;
  events.push(`Passed Starting Player token clockwise to Player ${newStartingPlayerIndex + 1}`);

  const updatedPlayers = state.players.map((p, idx) => ({
    ...p,
    isStartingPlayer: idx === newStartingPlayerIndex,
  }));

  // 2. Reset hasPassed for all characters & refill hands to 5 Action cards (RT-012)
  const updatedCharacters: Partial<Record<string, CharacterState>> = {};

  for (const [cid, char] of Object.entries(state.characters)) {
    if (!char) continue;

    let currentHand = [...char.hand];
    let currentDraw = [...char.drawDeck];
    let currentDiscard = [...char.discardPile];

    // Draw up to 5 Action cards
    const cardsNeeded = Math.max(0, 5 - currentHand.length);
    if (cardsNeeded > 0) {
      if (currentDraw.length < cardsNeeded && currentDiscard.length > 0) {
        // Reshuffle discard pile into draw deck
        events.push(`Reshuffled ${char.name}'s discard pile into draw deck`);
        const reshuffled = prng.shuffle([...currentDiscard]);
        currentDraw = [...currentDraw, ...reshuffled];
        currentDiscard = [];
      }

      const drawn = currentDraw.slice(0, cardsNeeded);
      currentDraw = currentDraw.slice(cardsNeeded);
      currentHand = [...currentHand, ...drawn];
      events.push(`${char.name} drew ${drawn.length} card(s) to refill hand to ${currentHand.length}`);
    }

    updatedCharacters[cid] = {
      ...char,
      hasPassed: false,
      actionsRemaining: 2,
      hand: currentHand,
      drawDeck: currentDraw,
      discardPile: currentDiscard,
    };
  }

  // 3. Autodestruction countdown
  let updatedAutodestruction = { ...state.autodestruction };
  let isGameOver = state.isGameOver;
  let gameResult = state.gameResult;

  if (updatedAutodestruction.isActive && updatedAutodestruction.roundsRemaining !== undefined) {
    const remaining = updatedAutodestruction.roundsRemaining - 1;
    updatedAutodestruction.roundsRemaining = remaining;
    events.push(`AUTODESTRUCTION COUNTDOWN: ${remaining} round(s) remaining!`);

    if (remaining <= 0) {
      events.push(`FACILITY DETONATION! Autodestruction timer reached zero. The Facility explodes!`);
      isGameOver = true;
      gameResult = {
        winners: [],
        losers: state.players.map(p => p.playerId),
        reason: 'Facility destroyed by Autodestruction',
      };
    }
  }

  // 4. Advance Round track (RT-012)
  const nextRound = state.round + 1;
  events.push(`Advanced Round Track to Round ${nextRound}/15`);

  if (nextRound > 15 && !isGameOver) {
    events.push(`TIME LIMIT REACHED: 15 rounds expired. Evacuation failed!`);
    isGameOver = true;
    gameResult = {
      winners: [],
      losers: state.players.map(p => p.playerId),
      reason: 'Time limit expired (15 rounds reached)',
    };
  }

  nextState = {
    ...nextState,
    round: nextRound,
    phase: isGameOver ? 'game-over' : 'player',
    startingPlayerIndex: newStartingPlayerIndex,
    activePlayerIndex: newStartingPlayerIndex,
    turnActionsTaken: 0,
    players: updatedPlayers,
    characters: updatedCharacters,
    autodestruction: updatedAutodestruction,
    isGameOver,
    gameResult,
  };

  return { state: nextState, events };
}
