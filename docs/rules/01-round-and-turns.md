# Round, Phase, and Turn Rules

## RT-001 — Round sequence

- **Source:** Rulebook pp. 12–15, “Game Round Structure” (extracted text lines 2939–2986).
- **Plain rule:** Resolve each Round in this fixed order:
  1. Player Phase.
  2. Intruder Phase.
  3. Event Phase.
  4. Cleanup Phase.
- After Cleanup’s time-advancement step, either a new Round begins or the game proceeds to End of Game.
- **Invariant:** No later phase of a Round begins before the preceding phase has completed.

## RT-002 — Turn order

- **Source:** Rulebook p. 13, “Player Phase” (extracted text lines 2987–3004).
- **Plain rule:** The Starting Player is the player holding the Starting Player token. Turn order starts with the Starting Player and continues clockwise. “First in Turn order” means the Starting Player, or the closest applicable Character clockwise from that player. Player numbers on Help cards do not establish turn order after setup.

## RT-003 — Reactions

- **Source:** Rulebook pp. 13–14, “Reactions” (extracted text lines 3067–3075).
- **Plain rule:** A player may use a Reaction at any point if its card condition is met. Resolve the Reaction effect, then discard that card. A Reaction is not an Action and does not consume either of the player’s two Actions for the Turn. A player who has Passed may still use Reactions.

## RT-004 — Player Phase

- **Source:** Rulebook p. 13, “Player Phase” (extracted text lines 2945–2962 and 2987–2994).
- **Applies when:** A new Player Phase begins.
- **Procedure:**
  1. The Starting Player takes a Turn.
  2. Continue clockwise, skipping players who have already Passed.
  3. Repeat this rotation until every player has Passed.
  4. Begin the Intruder Phase.

## RT-005 — A player Turn

- **Source:** Rulebook p. 12, “Players’ turns” (extracted text lines 2854–2864 and 2929–2934).
- **Applies when:** A player takes a Turn during the Player Phase.
- **Procedure:** Resolve in this order:
  1. Perform exactly two Actions.
  2. If the Character is in a Section with an inactive Life Support System, lose one Oxygen.
  3. If the Character is in a Room with a Fire marker, lose one Health Point.
- **Objective choice:** Once per game, a player may choose an Objective during their Turn. It is not an Action. See RT-010.
- **Invariant:** Oxygen loss precedes fire damage at turn end. A passing Turn is still a Turn for oxygen-loss and fire-damage purposes.

## RT-006 — Actions, costs, and payment timing

- **Source:** Rulebook p. 13, “Resolving Actions” (extracted text lines 2865–2927); Rulebook p. 14, “Effects” (extracted text lines 3187–3197).
- **Plain rule:** A player normally performs two Actions on their Turn and may perform the same Action more than once.
- **Action costs:**
  - Zero cards: play an Action card; Pass.
  - One card: Move; place a Secure token; Shoot in a Room; Burst at a Corridor; Melee; use an Item; activate the Robot; Trade; use Tactical Gear.
  - Two cards: use a Room; Move Cautiously.
- **Payment procedure:** Discard the required number of Action cards from hand, face up, to the discard pile; then resolve the chosen Action. Cards discarded solely as a basic-action cost do not resolve their card effects.
- **Restriction:** An effect or action may be selected only if it can be resolved entirely.
- **Restriction:** Some actions may be unavailable while in Combat (Character is in a Room with at least one Intruder). The individual action record or printed card icon must state that restriction where applicable.

## RT-007 — Pass

- **Source:** Rulebook p. 13, “Resolving Actions” (extracted text lines 2871–2875 and 2924–2927); Rulebook p. 14, “Passing” (extracted text lines 3180–3186).
- **Plain rule:** Pass is an Action, not an automatic state caused by an empty hand. A player does not Pass automatically when they have no cards in hand.
- **Procedure:** The player may discard any number of Action and Contamination cards from hand; their Turn then ends.
- **Effect:** The player has Passed and is skipped for the rest of the Player Phase. They may still use Reactions.
- **Note:** A passing Turn is still a Turn; oxygen loss and fire damage still apply.

## RT-008 — Intruder Phase

- **Source:** Rulebook pp. 14–15, “Intruder Phase” (extracted text lines 2963–2971 and 3300–3324).
- **Procedure:**
  1. Intruders Burning: each Intruder in a Room with Fire receives one Hit. Fire in the Nest destroys one Egg.
  2. Intruder Attacks: each Intruder in a Room attacks a Character there, if any.
- **Attack order:** Resolve Rooms from top-left, row by row. Within a Room, larger Intruders attack first (Queen > Drone > Adult > Larva). They initially attack the Character first in turn order; if that Character dies or leaves before remaining Intruders attack, the remaining Intruders attack the next eligible Character in turn order.
- **Clarification:** A fire Hit without a die roll cannot kill an Intruder except a Larva.

## RT-009 — Event Phase

- **Source:** Rulebook p. 15, “Event card resolution” (extracted text lines 3269–3299).
- **Procedure:** Draw the top Event card and resolve, in order:
  1. Its specified Intruder movement.
  2. Its main effect.
  3. Its secondary effect.
  4. Discard the card.
- **Impossible sentence:** Ignore an impossible sentence, then continue resolving the rest of the card.
- **Order convention:** Character effects resolve in turn order. Noise-marker effects resolve from the Facility’s top-left Corridor, row by row.

## RT-009a — Lander-launch timing exception

- **Source:** Rulebook p. 37, “Lander Launch Decision” (extracted text lines 6063–6074).
- **Plain rule:** At the very start of the Event Phase, any Character inside the Lander may decide to launch it. If launched:
  1. Remove the Lander token from the game.
  2. Move all Characters in the Lander to their Character boards.
  3. Those Characters have Escaped and take no further part until the End of Game check.
  4. One Character’s decision is sufficient; it is not a collaborative decision.

## RT-010 — Choosing an Objective

- **Source:** Rulebook pp. 13–14, “Choosing an Objective” (extracted text lines 3076–3094).
- **Plain rule:** Once per game, during their Turn, a player may choose one of their two Objective cards. This is not an Action and does not count toward the two-Action limit.
- **Timing:** Before or after any of the two Actions in a Turn, but not in the middle of one.
- **Procedure:**
  1. Take one Objective card and remove it from the game without showing it.
  2. Keep the other Objective; it must be fulfilled before the game ends.
  3. Move the marker on the Objective Choice track down by one (if possible).
  4. Draw Action cards according to the marker position: 1st player draws 3, 2nd and 3rd draw 2, 4th and 5th draw 1.
- **Invariant:** The kept Objective must be fulfilled or that player cannot be considered a winner.

## RT-011 — Bag Development

- **Source:** Rulebook p. 15, “Bag development” (extracted text lines 3385–3397); Rulebook p. 16, Bag Development table (extracted text lines 3439–3467).
- **Procedure:** Draw one random Intruder token from the bag. Resolve it using the front only, according to the Intruder Help Sheet and this table:
  - Queen (already on map): Activate the Queen. Queen (not on map): add 2 Larva tokens to bag.
  - Adult or Drone: add 2 Queen tokens to bag.
  - Larva: add 2 random Drone tokens to bag.
  - Blank: add 2 random Adult tokens to bag; return the Blank to the bag.
- Discard the drawn token to the bottom of its matching token pile (except Blank, which returns to the bag).
- **Invariant:** Tokens enter the bag from token piles and return from the bag to those piles.

## RT-012 — Cleanup Phase

- **Source:** Rulebook p. 15, “Cleanup Phase” (extracted text lines 3398–3433).
- **Procedure:**
  1. Pass the Starting Player token clockwise to the next player.
  2. Each player draws Action cards until they have five in hand. If an Action deck empties while drawing, reshuffle that Character’s discard pile to form a new Action deck and continue.
  3. Advance the Round marker one space. If the marker enters a space containing another token, resolve that token immediately.
- **Round-limit condition:** If the Round marker is already on its final space, do not advance it; proceed to End of the Game instead.

## RT-012a — Immediate entered-space token effects

- **Source:** Rulebook p. 16 (extracted text lines 3410–3431); Rulebook p. 38, “Autodestruction Procedure” (extracted text lines 6122–6140).
- **Autodestruction token:** The Facility explodes; the game ends. All Characters still inside (including hibernating Characters) die. All Rooms are destroyed. All Intruders die.
- **Lander token:** Resolve its landing attempt immediately. If anti-aircraft is inactive (or removed), the Lander lands at the Landing Zone and Characters may henceforth attempt escape through it. If active, the Lander is destroyed and removed from the game.

## RT-013 — Orders and Commands

- **Source:** Rulebook p. 13, “Orders and Commands” (extracted text lines 3095–3105).
- **Plain rule:** Some effects allow a Character to perform an Action using another Character. The owner of that effect chooses the target of the ordered Action. Characters who have Passed may still be ordered.
- **Restriction:** A command may never result in an Intruder Opportunity Attack against the ordered Character (e.g., ordering a Move out of a Room with Intruders or through a Corridor with them).

## RT-014 — Death, escape, and hibernation participation

- **Source:** Rulebook p. 18, “Character Health / Death” (extracted text lines 3750–3763); Rulebook p. 38, “Escaping/Hibernating” (extracted text lines 6141–6176); Rulebook p. 37, “Lander” (extracted text lines 6043–6062).
- **Death:** A Character dies when their Health marker reaches the Skull icon. Remove the miniature from the board; carried Items are lost; the Character loses and no longer takes part in the game.
- **Escape/hibernation:** A Character who successfully hibernates or escapes through the Escape Shuttle takes no further part until the End of Game check.
- **Lander:** A Character in the Lander is not yet escaped. Their normal Turns are skipped but they do not Pass. They still participate in Cleanup. They may be ejected if an Intruder appears in the Landing Zone.
- **Hibernation:** A hibernating Character can still die if the Facility is destroyed.

## RT-015 — End-of-game triggers

- **Source:** Rulebook p. 39, “End of the Game” (extracted text lines 6238–6273).
- **Triggers:** The game ends when either:
  1. Round 14 ends (all Characters who have not escaped or hibernated are considered dead); or
  2. All players have died, escaped, or hibernated; or
  3. The Facility is destroyed (including autodestruction).
- Then perform the End of Game sequence to determine winners.

## Digital disconnection

No official rulebook or FAQ rule defines network disconnection, reconnection, absent players, or automatic passing for disconnected players. Any such behavior is a digital-adaptation policy. See `deviations.md`.

## Examples

### EX-RT-001 — Passing still incurs oxygen loss

- **Given:** A Character is in a Section with inactive Life Support and has not yet Passed this Round.
- **When:** That player Passes.
- **Then:** They may discard any number of Action and Contamination cards, their Turn ends, they are skipped for the rest of the Round, and they lose 1 Oxygen because a passing Turn is still a Turn.

### EX-RT-002 — Passed player may react

- **Given:** A player has Passed during the Player Phase.
- **When:** A Reaction card’s condition is met later in that Round.
- **Then:** That player may play the Reaction, resolve it, and discard it; it does not count toward the normal two-Action limit.

### EX-RT-003 — Multiple Intruders and a death

- **Given:** Two Intruders and two Characters occupy the same Room, and Character A is first in Turn order.
- **When:** The first/largest Intruder kills Character A during the Intruder Attack step.
- **Then:** An Intruder in that Room that has not attacked yet attacks Character B, the next Character in Turn order.

### EX-RT-004 — Impossible portion of an Event

- **Given:** An Event card has an Intruder-movement instruction, a main effect, and a secondary effect.
- **When:** One sentence of the main effect is impossible to resolve.
- **Then:** Ignore that sentence only, continue resolving the remaining Event-card instructions in order, then discard the Event card.

### EX-RT-005 — Round marker reaches autodestruction

- **Given:** Cleanup reaches Time Advancement and the Round marker enters the Autodestruction token’s space.
- **When:** That space is entered.
- **Then:** Resolve the token immediately: the Facility is destroyed, the game ends, Characters inside it—including hibernating Characters—die, and all Intruders die.

### EX-RT-006 — Lander occupant when everyone else passes

- **Given:** One or more Characters are in the Lander and have not Passed, while every other Character has Passed.
- **When:** The Player Phase checks whether all others have Passed.
- **Then:** The Lander Characters automatically Pass and the Round ends; until then, their normal Turns are skipped but they still participate in Cleanup.

### EX-RT-007 — Objective choice reward

- **Given:** Three players have already chosen Objectives this game, and the 4th player chooses theirs during their Turn.
- **When:** The Objective Choice marker is at position 4.
- **Then:** That player draws 1 Action card as the choice reward.