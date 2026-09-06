/**
 * Queen Health cards for Nemesis: Retaliation.
 */

export interface QueenCardDefinition {
  id: string;
  title: string;
  healthModifier: number;
  effectDesc: string;
}

export const QUEEN_HEALTH_CARDS: readonly QueenCardDefinition[] = [
  {
    id: "QueenHealthCard1",
    title: "QueenHealthCard1",
    healthModifier: 0,
    effectDesc: "Repel the Queen.",
  },
  {
    id: "QueenHealthCard2",
    title: "QueenHealthCard2",
    healthModifier: 0,
    effectDesc: "Activate the Queen.",
  },
  {
    id: "QueenHealthCard3",
    title: "QueenHealthCard3",
    healthModifier: 0,
    effectDesc: "Place the Queen back in the pool.",
  },
  {
    id: "QueenHealthCard4",
    title: "QueenHealthCard4",
    healthModifier: 0,
    effectDesc: "Repel the Queen.",
  },
  {
    id: "QueenHealthCard5",
    title: "QueenHealthCard5",
    healthModifier: 0,
    effectDesc: "Repel the Queen.",
  },
  {
    id: "QueenHealthCard6",
    title: "QueenHealthCard6",
    healthModifier: 0,
    effectDesc: "Add all Queen tokens to the bag.",
  },
  {
    id: "QueenHealthCard7",
    title: "QueenHealthCard7",
    healthModifier: 0,
    effectDesc: "Each <CHARACTER> in the Room with the Queen draws 2<ACTION-CARD>.",
  },
  {
    id: "QueenHealthCard8",
    title: "QueenHealthCard8",
    healthModifier: 0,
    effectDesc: "Repel the Queen.",
  },
  {
    id: "QueenHealthCard9",
    title: "QueenHealthCard9",
    healthModifier: 0,
    effectDesc: "Each <CHARACTER> in the Room with the Queen makes a Noise roll.",
  },
  {
    id: "QueenHealthCard10",
    title: "QueenHealthCard10",
    healthModifier: 0,
    effectDesc: "Activate the Queen.",
  },
  {
    id: "QueenHealthCard11",
    title: "QueenHealthCard11",
    healthModifier: 0,
    effectDesc: "Activate the Queen.",
  },
  {
    id: "QueenHealthCard12",
    title: "QueenHealthCard12",
    healthModifier: 0,
    effectDesc: "Place a <MALFUNCTION> in the Room with the Queen.",
  },
];
