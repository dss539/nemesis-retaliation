/**
 * Serious Wound cards for Nemesis: Retaliation.
 */

export interface SeriousWoundDefinition {
  id: string;
  title: string;
  bodyText: string;
}

export const SERIOUS_WOUND_CARDS: readonly SeriousWoundDefinition[] = [
  {
    id: "Bleeding",
    title: "Bleeding",
    bodyText: "Whenever you Pass: Lose 1<HP>.",
  },
  {
    id: "Leg",
    title: "Leg",
    bodyText: "The \"Make a Move\" Action from a Room with an <ANY-INTRUDER> costs you 1<ACTION-CARD> more.",
  },
  {
    id: "Arm",
    title: "Arm",
    bodyText: "You only have 1 Hand slot. If you have Items in both Hand slots, you must immediately discard items from one of them.",
  },
  {
    id: "Eyes",
    title: "Eyes",
    bodyText: "+1 to all your shoot results.",
  },
  {
    id: "Guts",
    title: "Guts",
    bodyText: "Whenever you Pass: Gain 1 Contamination.",
  },
  {
    id: "Body",
    title: "Body",
    bodyText: "During the Drawing Action Cards step, draw <ACTION-CARD> until you have 4<ACTION-CARD> in hand instead of 5.",
  },
  {
    id: "Hand",
    title: "Hand",
    bodyText: "The \"Use Item\" Action costs you 1<ACTION-CARD> more.",
  },
  {
    id: "Knee",
    title: "Knee",
    bodyText: "The \"Make a Move Cautiously Action costs you 1<ACTION-CARD> more.",
  },
  {
    id: "Lungs",
    title: "Lungs",
    bodyText: "Whenever you Pass: Lose 1<OXYGEN>. If you already have 0<OXYGEN>, lose 2<HP> instead.",
  },
];
