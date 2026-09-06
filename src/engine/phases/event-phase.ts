/**
 * Event Phase execution for Nemesis: Retaliation.
 * Strictly adheres to RT-009, Rulebook pp. 14–15, and p. 31.
 */

import { Mulberry32 } from '../prng/mulberry32.js';
import { GameState } from '../types/state.js';
import { EventCardDefinition, EVENT_CARDS } from '../../data/events.js';

export interface EventPhaseResult {
  state: GameState;
  drawnEvent: EventCardDefinition;
  events: string[];
}

export function resolveEventPhase(state: GameState, prng: Mulberry32): EventPhaseResult {
  const events: string[] = ['=== EVENT PHASE ==='];
  let nextState: GameState = { ...state };

  // 1. Draw Event card (RT-009)
  const eventIdx = prng.nextInt(0, EVENT_CARDS.length - 1);
  const eventCard: EventCardDefinition = EVENT_CARDS[eventIdx]!;
  events.push(`Drawn Event Card: "${eventCard.title}"`);

  // 2. Intruder Movement
  if (eventCard.intruderMovementDesc) {
    events.push(`Intruder Movement: ${eventCard.intruderMovementDesc}`);
    // Intruders in corridors move into connected discovered rooms
    for (const [cid, corr] of Object.entries(nextState.board.corridors)) {
      if (corr.intruderIds.length > 0) {
        const destRoomId = corr.slotA;
        const destRoom = nextState.board.rooms[destRoomId];
        if (destRoom && destRoom.isDiscovered) {
          const intruderId = corr.intruderIds[0]!;
          const inst = nextState.intruderInstances[intruderId];
          if (inst) {
            events.push(`Intruder ${inst.type} moved from Corridor ${cid} into ${destRoom.tile?.name ?? destRoomId}`);
            nextState = {
              ...nextState,
              board: {
                ...nextState.board,
                corridors: {
                  ...nextState.board.corridors,
                  [cid]: {
                    ...corr,
                    intruderIds: corr.intruderIds.slice(1),
                  },
                },
                rooms: {
                  ...nextState.board.rooms,
                  [destRoomId]: {
                    ...destRoom,
                    intruderIds: [...destRoom.intruderIds, intruderId],
                  },
                },
              },
              intruderInstances: {
                ...nextState.intruderInstances,
                [intruderId]: {
                  ...inst,
                  location: { kind: 'room', roomId: destRoomId },
                },
              },
            };
          }
        }
      }
    }
  }

  // 3. Primary Effect
  if (eventCard.primaryEffectDesc) {
    events.push(`Primary Effect: ${eventCard.primaryEffectDesc}`);
  }

  // 4. Secondary Effect
  if (eventCard.secondaryEffectDesc) {
    events.push(`Secondary Effect: ${eventCard.secondaryEffectDesc}`);
  }

  // Transition phase to 'cleanup'
  nextState.phase = 'cleanup';

  return {
    state: nextState,
    drawnEvent: eventCard,
    events,
  };
}
