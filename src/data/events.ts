/**
 * Event cards for Nemesis: Retaliation.
 */

export interface EventCardDefinition {
  id: string;
  title: string;
  intruderMovementDesc: string;
  primaryEffectDesc: string;
  secondaryEffectDesc: string;
}

export const EVENT_CARDS: readonly EventCardDefinition[] = [
  {
    id: "Event_BreakingIn",
    title: "Breaking In",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Discard 1 <SECURE> from each Room.",
    secondaryEffectDesc: "Resolve a <NOISE> in each Unexplored Corridor.",
  },
  {
    id: "Event_Damage",
    title: "Damage",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-HOR> move.",
    primaryEffectDesc: "Place a <MALFUNCTION> in each Room with a <ANY-INTRUDER>.",
    secondaryEffectDesc: "Each <CHARACTER> in a Room without a <SECURE> resolves <HAZARD>.",
  },
  {
    id: "Event_DamagingFire",
    title: "Damaging Fire",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-ACUTE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place a <MALFUNCTION> in each Room with a <FIRE>. In each Room with a <FIRE>, spread <FIRE> through Corridors with the lowest Noise value.",
    secondaryEffectDesc: "Each <CHARACTER> in a Room without a <SECURE> resolves <HAZARD>.",
  },
  {
    id: "Event_EggProtection",
    title: "Egg Protection",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE> move.",
    primaryEffectDesc: "Place 2 Drones in the Nest \u2013 they immediately Attack if any <CHARACTER> is there. Place 1 Drone in each Unexplored Corridor in Section C.",
    secondaryEffectDesc: "Each <CHARACTER> makes a Noise roll.",
  },
  {
    id: "Event_FireBreath",
    title: "Fire Breath",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-HOR> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "In each Room with a <FIRE>, spread <FIRE> to all neighboring Rooms in Sections with an <OXYGEN-ON>.",
    secondaryEffectDesc: "Each <CHARACTER> makes a Noise roll.",
  },
  {
    id: "Event_GeneratorsOverheat",
    title: "Generators Overheat",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "In Sections with an <OXYGEN-ON>: Place a <FIRE> in each Life Support Control Room. In Sections with an <OXYGEN-OFF>: Place a <MALFUNCTION> in each Life Support Control Room.",
    secondaryEffectDesc: "Each <CHARACTER> makes a Noise roll.",
  },
  {
    id: "Event_Hatching",
    title: "Hatching",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-ACUTE> move.",
    primaryEffectDesc: "Place a Larva in the Nest \u2013 it immediately Attack if any <CHARACTER> is there. Place 1 Larva in each Unexplored Corridor ajdacent to a <CHARACTER>.",
    secondaryEffectDesc: "Resolve a <NOISE> in each Unexplored Corridor.",
  },
  {
    id: "Event_LandingZoneExplodes",
    title: "Landing Zone Explodes",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-HOR> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place a <FIRE> and a <MALFUNCTION> in the Landing Zone.",
    secondaryEffectDesc: "Place a <NOISE> in each Unexplored Corridor without a <NOISE>.",
  },
  {
    id: "Event_LeavingTheShell",
    title: "Leaving The Shell",
    intruderMovementDesc: "No <ANY-INTRUDER> moves.",
    primaryEffectDesc: "Each <CHARACTER> infected with a Larva: Gains 1 Contamination, discard all <ACTION-CARD>, and reshuffle their deck. Then, resolve the Eclosion Procedure. Each other <CHARACTER>: Draw 4<ACTION-CARD> and resolves the Infection Procedure. Then, discards all <ACTION-CARD>.",
    secondaryEffectDesc: "Reshuffle the Event deck.",
  },
  {
    id: "Event_LifeSupportFailure",
    title: "Life Support Failure",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-ACUTE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Flip all <OXYGEN-ON> to <OXYGEN-OFF>. Place a <MALFUNCTION> in each Life Support Control Room.",
    secondaryEffectDesc: "Place a <NOISE> in each Unexplored Corridor without a <NOISE>.",
  },
  {
    id: "Event_NoWayOut",
    title: "No Way Out",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-ACUTE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place 4 Adults in each non-Reinforced Corridor adjacent to the Landing Zone.",
    secondaryEffectDesc: "Each <CHARACTER> makes a Noise roll.",
  },
  {
    id: "Event_OverwhelmingEnemies",
    title: "Overwhelming Enemies",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-ACUTE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place 1 Drone in each Corridor with a <NOISE> adjacent to a <CHARACTER>.",
    secondaryEffectDesc: "Each <CHARACTER> in a Room without a <SECURE> resolves <HAZARD>.",
  },
  {
    id: "Event_Panic",
    title: "Panic",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-HOR> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Each <CHARACTER> in a Room with an <ANY-INTRUDER> or adjacent to a Corridor with an <ANY-INTRUDER>: Loses 1 <OXYGEN> or spends <AMMO>.",
    secondaryEffectDesc: "Resolve a <NOISE> in each Unexplored Corridor.",
  },
  {
    id: "Event_ProtectServe",
    title: "Protect & Serve",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-HOR> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place 2 Drones in the Room/Corridor with the Queen \u2013 they do not Attack. If there is no Queen on the map, add 2 random Drone tokens to the bag.",
    secondaryEffectDesc: "Each <CHARACTER> in a Room without a <SECURE> resolves <HAZARD>.",
  },
  {
    id: "Event_ReactorOverheating",
    title: "Reactor Overheating",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE>, <CORRIDOR-HOR> and <CORRIDOR-ACUTE>. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "If a <MALFUNCTION> is in the Cooling System Room or the Reactor Room, Activate the Autodestruction Procedure. Then, place a <MALFUNCTION> in each of these Rooms.",
    secondaryEffectDesc: "Reshuffle the Event deck.",
  },
  {
    id: "Event_RiseOfTheMachine",
    title: "Rise Of The Machine",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place a <MALFUNCTION> on the <ROBOT>. Place a <MALFUNCTION> in a Room with the <ROBOT>. Each <CHARACTER> in that Room loses 2 <HP>.",
    secondaryEffectDesc: "Place a <NOISE> in each Unexplored Corridor without a <NOISE>.",
  },
  {
    id: "Event_ScentOfPrey",
    title: "Scent Of Prey",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Resolve each <NOISE> adjacent to a <CHARACTER>.",
    secondaryEffectDesc: "Each <CHARACTER> makes a Noise roll.",
  },
  {
    id: "Event_ShortCircuit",
    title: "Short Circuit",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-GRAVE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "In Sections with an <OXYGEN-ON>: Place a <FIRE> in each Room with a <MALFUNCTION>.",
    secondaryEffectDesc: "Each <CHARACTER> in a Room without a <SECURE> resolves <HAZARD>.",
  },
  {
    id: "Event_SystemFailure",
    title: "System Failure",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-HOR> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "Place a <MALFUNCTION> in each <COMPUTER> Room.",
    secondaryEffectDesc: "Resolve a <NOISE> in each Unexplored Corridor.",
  },
  {
    id: "Event_TheQueenAwakens",
    title: "The Queen Awakens",
    intruderMovementDesc: "All <ANY-INTRUDER> in each <CORRIDOR-ACUTE> move. Then, all <ANY-INTRUDER> in every Room move.",
    primaryEffectDesc: "If the Queen is alive, add all Queen tokens to the bag.",
    secondaryEffectDesc: "Place a <NOISE> in each Unexplored Corridor without a <NOISE>.",
  },
];
