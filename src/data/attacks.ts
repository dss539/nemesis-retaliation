/**
 * Intruder Attack cards for Nemesis: Retaliation.
 */

export interface IntruderAttackCard {
  id: string;
  title: string;
  rulesText: string;
}

export const INTRUDER_ATTACK_CARDS: readonly IntruderAttackCard[] = [
  {
    id: "IntruderAttack_Bite",
    title: "Bite",
    rulesText: "intruder-adult intruder-drone intruder-queen If you are Heavily Injured, you die. Otherwise, gain 1 Serious Wound and 1 Contamination.",
  },
  {
    id: "IntruderAttack_DeadlyClaws1",
    title: "Deadly Claws",
    rulesText: "intruder-adult Lose 1<HP>. intruder-drone If you are Heavily Injured, you die. If you are Injured, gain 1 Serious Wound Otherwise, gain 2 Serious Wounds. intruder-queen Lose 1<HP>.",
  },
  {
    id: "IntruderAttack_DeadlyClaws2",
    title: "Deadly Claws",
    rulesText: "intruder-adult Lose 2<HP>. Gain 1 Contamination. intruder-drone If you are Heavily Injured, you die. If you are Injured, gain 1 Serious Wound Otherwise, gain 2 Serious Wounds. intruder-queen Lose 2<HP>. Gain 1 Contamination.",
  },
  {
    id: "IntruderAttack_DeadlyClaws3",
    title: "Deadly Claws",
    rulesText: "intruder-adult Lose 3<HP>. intruder-drone If you are Heavily Injured, you die. If you are Injured, gain 1 Serious Wound Otherwise, gain 2 Serious Wounds. intruder-queen Lose 3<HP>.",
  },
  {
    id: "IntruderAttack_Fury1",
    title: "Fury",
    rulesText: "intruder-adult Lose 1<HP>. Gain 1 Contamination. intruder-drone intruder-queen All Heavily Injured <CHARACTER> in your Room die Each other <CHARACTER> in the Room gain 1 Serious Wound and 1 Contamination.",
  },
  {
    id: "IntruderAttack_Fury2",
    title: "Fury",
    rulesText: "intruder-adult Lose 2<HP>. Gain 1 Contamination. intruder-drone intruder-queen All Heavily Injured <CHARACTER> in your Room die Each other <CHARACTER> in the Room gain 1 Serious Wound and 1 Contamination.",
  },
  {
    id: "IntruderAttack_Infecting",
    title: "Infecting",
    rulesText: "intruder-adult intruder-drone Lose 2<HP>. intruder-queen Gain 1 Contamination. If you are not infected with a Larva, place 1 Larva on your character board.",
  },
  {
    id: "IntruderAttack_Miss",
    title: "Miss",
    rulesText: "intruder-adult intruder-drone intruder-queen Nothing happens. Reshuffle the Intuder Attack deck.",
  },
  {
    id: "IntruderAttack_Scratch1",
    title: "Scratch",
    rulesText: "intruder-adult intruder-drone intruder-queen Gain 1 Contamination.",
  },
  {
    id: "IntruderAttack_Scratch2",
    title: "Scratch",
    rulesText: "intruder-adult intruder-drone intruder-queen Lose 1<HP> Gain 1 Contamination.",
  },
  {
    id: "IntruderAttack_Scratch3",
    title: "Scratch",
    rulesText: "intruder-adult intruder-drone intruder-queen Lose 1<HP>",
  },
  {
    id: "IntruderAttack_Scratch4",
    title: "Scratch",
    rulesText: "intruder-adult intruder-drone intruder-queen Lose 2<HP>",
  },
  {
    id: "IntruderAttack_BloodSense",
    title: "Blood Sense",
    rulesText: "intruder-adult Lose 2<HP>. intruder-drone intruder-queen Lose 2<HP>. If you are Moving, place the Attacking <ANY-INTRUDER> in the Room where your Movement ends (it does not attack again).",
  },
  {
    id: "IntruderAttack_TailAttack1",
    title: "Tail Attack",
    rulesText: "intruder-adult intruder-drone Gain 1 Contamination. intruder-queen If you are Injured or Heavily Injured, you die. Otherwise, gain 1 Serious Wound and 1 Contamination.",
  },
  {
    id: "IntruderAttack_TailAttack2",
    title: "Tail Attack",
    rulesText: "intruder-adult intruder-drone Lose 1<HP>. Gain 1 Contamination. intruder-queen If you are Injured or Heavily Injured, you die. Otherwise, gain 1 Serious Wound and 1 Contamination.",
  },
];
