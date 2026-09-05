# Intruders and Resolution-Critical Systems

## Intruder ordering priority

- **Largest Intruder priority:** Queen > Drone > Adult > Larva.
- **Tie-breaker:** Whenever the rules say “first in Turn order,” choose the Starting Player or the next applicable Character clockwise.
  - **Source:** Rulebook p. 13 (lines 2995–3004).
- **Event-wide order:** Effects mentioning Characters resolve in Turn order. Effects resolving Noise markers in Corridors resolve map order: top-left, then row by row.
  - **Source:** Rulebook p. 14 (lines 3294–3299).
- **Immediate-entry priority:** Whenever an Intruder is placed into or moves into a Room, it immediately tries to attack a Character there, before the enclosing effect proceeds.
  - **Source:** Rulebook p. 25 (lines 4707–4710).

## INT-001 — Intruder bag setup and token lifecycle

- **Source:** Rulebook p. 8 (lines 2565–2575, 2589–2591); Rulebook p. 15, Bag Development Queen-death note; Rulebook p. 30 (lines 5182–5198).
- **Setup:**
  - Shuffle each Intruder-type token pile separately, icon-side up.
  - Bag contents: 1 Blank, 2 Larva, 3 random Adult, plus 1 additional random Adult per participating Character.
  - Help Sheet starts on “Queen Alive” side.
- **Queen death:** When the Queen dies, Intruder-token effects change; use the Help Sheet's “Queen Dead” side for subsequent token resolution.
- **Provided Intruder-token supply:** 40 tokens total: 1 Blank, 9 Queen, 8 Drone, 16 Adult, and 6 Larva tokens.
- **Types and default scope:** The four Intruder types are Queen, Drone, Adult, and Larva. General Intruder rules are written from the Adult perspective and apply to all four types unless a rule expressly overrides them.
- **Token lifecycle:** Every bag draw resolves using the context-specific column of the Intruder Help Sheet. Resolved tokens leave the bag. Blank is the sole exception and returns to the bag. Tokens enter the bag only from their type piles and leave it back to those piles.
- **Component limits:** Place as many models of a requested type as are available, then ignore the excess.
- **Room capacity:** Unlimited.
- **Corridor capacity:** Six Intruder-equivalents; a Queen counts as four.
- **Placement at capacity:** Prioritize larger Intruders. When placing a larger Intruder into a full Corridor, remove as many smaller Intruders as necessary to make room. Any Intruder still blocked by the capacity limit remains unplaced. Movement-capacity handling is in INT-003.
- **Help Sheet extraction:** Both Queen Alive and Queen Dead sides are transcribed source-bound in `docs/rules/source-extraction/intruder-help-sheet.json`: 18 instructions with source-local token occurrences, exact front/back pairing, and zero unreadable spans. The TTS component pixels remain below official FAQ/rulebook authority and are not silently normalized.
- **Plain rule:** The Intruder Help Sheet supplies context-specific token instructions; this table records the Queen Alive source occurrence without replacing the official Help Sheet or the current `RT-011` Bag Development procedure.
- **Source:** `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-053.png`; title `THE QUEEN IS ALIVE`.

| Source column and token occurrence | Exact printed instruction |
|---|---|
| `RESOLVE IN A CORRIDOR` — unlabeled Queen marker | “Activate the Queen. If not possible – place her in the Corridor.” |
| `RESOLVE IN A CORRIDOR` — token faces `2`, `3`, `4`, `1+1`, `2+1`, `3+1` | “Place the number of Intruders shown on the token (Adults and Drones) in the Corridor.” |
| `RESOLVE IN A CORRIDOR` — Larva marker | “Place 1 Larva in the Corridor.” |
| `RESOLVE IN A ROOM` — `QUEEN` token | “Activate the Queen. If not possible – place her in the Room.” |
| `RESOLVE IN A ROOM` — `DRONE`, `ADULT`, `LARVA` tokens | “Place 1 Intruder of the type shown on the token in the Room.” |
| `BAG DEVELOPMENT` — `QUEEN` token | “Activate the Queen. If not possible – add 2 Larva tokens to the bag.” |
| `BAG DEVELOPMENT` — `DRONE`, `ADULT` tokens | “Add 2 Queen tokens to the bag.” |
| `BAG DEVELOPMENT` — `LARVA` token | “Add 2 random Drone tokens to the bag.” |
| bottom row — unlabeled dark marker | “Add 2 random Adult tokens to the bag. Add this token back to the bag.” |

- **Boundary sentence:** This TTS component scan is source-bound secondary evidence. The official rulebook p. 15 and `RT-011` govern current Bag Development, and this table must not be used to assign the bottom-row instruction to an unresolved Corridor or Room context.

### Queen-resolution source occurrences

| Resolution context | Exact source instruction |
|---|---|
| Resolve in a Corridor, Queen available | `Activate the Queen.` |
| Resolve in a Corridor, activation not possible | `If not possible – place her in the Corridor.` |
| Resolve in a Room, Queen available | `Activate the Queen.` |
| Resolve in a Room, activation not possible | `If not possible – place her in the Room.` |

- **Source:** Intruder Help Sheet anchors `INTRUDER HELP SHEET — Corridor Queen`, `INTRUDER HELP SHEET — Corridor Queen fallback`, `INTRUDER HELP SHEET — Room Queen`, and `INTRUDER HELP SHEET — Room Queen fallback`.
- **Boundary:** The phrase “If not possible” remains deliberately undefined; no availability, timing, or alternate placement default is added.

## INT-002 — Noise-based spawning and hazard spawning

- **Source:** Rulebook p. 25 (lines 4655–4701).

### Resolve Noise Marker

1. Remove Noise marker from the Corridor.
2. Draw a bag token.
3. Resolve it in that same Corridor per the Intruder Help Sheet.
4. Use the token’s back number to determine quantity; red number means Drones.
5. Discard the token to its pile unless otherwise stated (Blank returns to bag).

### Resolve Hazard

1. Draw a bag token.
2. Resolve per the Intruder Help Sheet.
3. Use the front icon only to identify Intruder type placed.
4. Ignore the back entirely.
5. Discard the token to its matching pile.

### Numeric Noise result resolution

A numeric Noise result resolves every adjacent Corridor matching that value, one Corridor at a time:
1. If it has Intruders, its largest Intruder enters the Character’s Room.
2. Else if it has Noise, resolve that Noise marker.
3. Else place Noise.

- **Noise roll after every movement:** A Noise roll occurs after every movement, including movement into a Room containing Characters and/or Intruders, unless an explicit special effect says otherwise.
  - **Source:** Rulebook p. 25 (lines 4702–4705).

## INT-003 — Intruder movement and targeting

- **Source:** Rulebook p. 30 (lines 5119–5159); Rulebook pp. 31–32 (lines 5324–5355).

### Target selection

1. Choose nearest Character by shortest route.
2. If tied and the activating Character is among the tied candidates, choose the activating Character.
3. Otherwise choose the Character first in Turn order.
4. Intruders do not move toward Characters in the Lander.
   - **Source:** FAQ v1.2, “General rules” #10 (lines 66–68).

### Group movement

1. Intruders move as a group toward the closest Character on a shortest route.
2. A normal move alternates space types: from a Corridor into an adjacent Room, or from a Room into an adjacent Corridor.
3. Closed Doors do not affect route selection.
4. If they would move through a Closed Door, destroy that Door and do not move.
5. Entering an occupied Room from a Corridor: only the largest Intruder enters.
6. If a preferred destination Corridor is full, use another equally short route if one exists. Otherwise move as many as fit and leave the rest waiting.
7. Event movement ordering: resolve Facility movement top-left to bottom-right, row by row, one Intruder group at a time.
8. If equal shortest routes, choose the one beginning with the lowest-ID Corridor/Room.

### Repel

- **Source:** Rulebook p. 31 (lines 5273–5292).
- A Character may Repel an Intruder only from that Character's Room or an adjacent Corridor.
- If the Intruder is in the source Room: the affected Character chooses its exit Corridor.
- Otherwise: move away from source; if multiple destinations, choose Corridor/Room with lowest ID.
- If traversing a Closed Door: destroy the Door; do not traverse.
- If entering an occupied Room: immediate entry attack.
- If leaving through an Unexplored Corridor: remain in place.
- **Capacity swap principle:** If necessary, larger Intruders swap places with lower forms. **Source:** Rulebook p. 21, `INTRUDER LIMITS — swap principle`.
- **Moving swap:** When moving, swap the locations of the larger and smaller Intruders. **Source:** Rulebook p. 21, `INTRUDER LIMITS — moving swap`.
- **No attack:** A location swap caused by Corridor capacity does not trigger an Intruder Attack. **Source:** Rulebook p. 21, `INTRUDER LIMITS — no Attack on swap`.

- **Boundary:** These bullets do not choose a universal placement algorithm or extend the no-Attack exception beyond the stated capacity swap.
- **Plain rule:** Queen Activation resolves as either an Attack or movement.
- **Plain rule:** When the Queen Activates, she Attacks a Character in the same Room if possible. If the Queen cannot Attack a Character in her Room, she moves once toward the closest Character.
- **Plain rule:** An Intruder in a Room with a Character does not move during normal Intruder movement.
- **Source:** Rulebook pp. 30–31 and 35, `RB-P30-036`, `RB-P31-032`, `RB-P35-033`, and `RB-P35-034`.
- **Boundary:** Preserve the existing Intruder target-selection and route rules. The source’s Attack-versus-movement disjunction and the “if possible/closest Character” limits remain explicit; no no-target or outcome-selection default is added.

## INT-004 — Intruder attacks

- **Source:** Rulebook p. 15 (lines 3313–3324); Rulebook p. 25 (lines 4707–4710); Rulebook p. 32 (lines 5393–5430); Rulebook p. 34 (lines 5662–5667).

### Attack triggers

An Intruder attack is triggered by:
1. The Intruder Attack step of the Intruder Phase.
2. An Intruder entering a Character’s Room.
3. An Intruder being placed in a Character’s Room.
4. A Character’s movement opportunity attack.
5. Failed melee retaliation prevention.
6. Other effects explicitly calling for an Intruder attack.

### Intruder Phase attacks

1. Process Rooms from the Facility’s top-left, row by row.
2. In each Room, each Intruder attacks a Character if one is present.
3. If multiple Characters are present, target the Character first in Turn order.
4. If multiple Intruders are present, resolve the largest Intruders first.
5. Those Intruders continue targeting the same first-in-order Character unless that Character dies or leaves the Room.
6. If that happens, remaining Intruders that have not yet attacked target the next Character in Turn order.

### Incoming Room entry

- If the entry arose from a player effect, target the source Character if possible.
- Otherwise target the Character first in Turn order.
- Resolve one attack unless replaced or prevented.

### Standard attack resolution

1. Draw a random Intruder Attack card.
2. Resolve the card’s effect associated with the attacking Intruder type.
3. Discard the card.
4. Reshuffle the Intruder Attack deck only when a game effect expressly instructs it.

### Rulebook-illustrated Attack effects

- **Page-18 illustrated attack — Adult, Drone, or Queen:** If the target is Heavily Injured, they die. Otherwise they gain 1 Serious Wound and 1 Contamination.
- **Infecting — Adult, Drone, or Queen:** The target loses 2 Health and gains 1 Contamination. If they are not already infected with a Larva, place 1 Larva on their Character board.

### Larva attack resolution

1. Target gains 1 Contamination into discard pile.
2. If target lacks a Larva on their Character board: place the attacking Larva on the target’s board.
3. Else: discard the attacking Larva.

### Secure tokens and attack prevention

- When an Intruder enters an occupied secured Room: discard exactly 1 Secure token; do not resolve that incoming attack.
- Secure only protects against an attack generated by entry. It does not protect against an Intruder already in the Room, including ordinary Intruder-Phase attacks.
- Discarding a Secure token for entry cannot itself be prevented.
- **Source:** Rulebook p. 23 (lines 4396–4413); FAQ v1.2, “General rules” #11 (lines 70–72).
- A Room cannot be secured while it contains an Intruder; maximum three Secure tokens.
- General attack prevention ignores the entire attack: do not apply additional effects and do not draw an Attack card.
  - **Source:** Rulebook p. 32 (lines 5418–5423).
- **FAQ distinction:** A card that prevents an Intruder attack during Movement protects only opportunity attacks, not a Hazard-result attack.
  - **Source:** FAQ v1.2, “Action cards” #3 (lines 86–89).

### Shelter permanent security

- **Source:** FAQ v1.2, “Rooms” #2 (lines 96–105).
- Shelter is “always secured” as a permanent room status, not a Secure token. It prevents attacks from incoming Intruders and cannot be discarded by Items. It is not counted for effects that count Secure tokens.
- Additional Secure tokens may be placed in Shelter (max 3); those tokens are discarded first.

- **Plain rule:** When a Larva Attacks a Character, resolve the special Larva procedure instead of drawing a standard Intruder Attack card.

### Attack-card source occurrences

| Source occurrence | Title | Exact printed effect text |
|---|---|---|
| `game-attack-022.png` | **BLOOD SENSE** | `[ICON: cyan circular portrait of low tendrilled creature] Lose 2 [characterHealth]. [ICON: cyan circular portrait of frontal horned creature] [ICON: cyan circular portrait of upright spiked creature] Lose 2 [characterHealth]. If you are Moving, place the Attacking [intruder] in the Room where you Movement ends. (It does not Attack again)` |
| `game-attack-151_cards/card-08.png` | **DEADLY CLAWS** | `[ICON: cyan circular curled quadrupedal creature glyph] [ICON: cyan circular frontal multi-limbed creature glyph] Lose 3 [characterHealth]. [ICON: cyan circular upright clawed creature glyph] If you are Heavily Injured, you die. Otherwise, get a Serious Wound on each empty Serious Wound slot to the right of your Health marker. Then, get 1 Serious Wound more.` |
| `game-attack-151_cards/card-13.png` | **SCRATCH** | `[ICON: blue circular badge with small curled pale creature glyph] [ICON: blue circular badge with upright spined pale creature glyph] [ICON: blue circular badge with broad horned pale creature glyph] Get 1 Contamination.` |
| `game-attack-151_cards/card-15.png` | **SCRATCH** | `Lose 1 [characterHealth].` |
| `game-attack-151_cards/card-16.png` | **SCRATCH** | `Lose 2 [characterHealth].` |
| `game-attack-151_cards/card-17.png` | **SUMMONING** | `[ICON: cyan circular glyph with a small curled creature] [ICON: cyan circular glyph with a spined creature] Lose 2 [characterHealth]. [ICON: cyan circular glyph with a frontal many-limbed creature] Place 1 Drone in each adjacent Corridor with Intruders. If the Room has no [character], place 1 Drone in that Room. This Drone doesn’t make a Surprise Attack.` |

- **Source:** Rulebook p. 32, `RB-P32-019`; exact TTS occurrences at `assets/tts-mod/extract/v2-dl/tree/cards/game/attack-022.png` and `game/attack-151_cards/card-08.png`, `card-13.png`, `card-15.png`, `card-16.png`, `card-17.png`.
- **Boundary:** Preserve `SEM-Q-021`, `SEM-Q-022`, `SEM-Q-023`, `SEM-Q-038`, and `SEM-Q-105` as named in the table. The table is occurrence-keyed; it does not collapse repeated titles, resolve icon applicability, or invent Wound, relocation, capacity, or continuation defaults.

## INT-005 — Opportunity attacks

- **Source:** Rulebook p. 24 (lines 4541–4558).
- **Procedure:**
  1. Before a Character moves through a chosen Corridor, collect all Intruders in the origin Room plus the chosen Corridor.
  2. Resolve attacks in descending Intruder-size order.
  3. Resolve at most 3 attacks.
  4. Then continue the movement sequence.

## INT-006 — Health, Serious Wounds, and Character death

- **Source:** Rulebook p. 16, “Character — Health track” (`RB-P16-019`–`RB-P16-020`); Rulebook p. 18 (lines 3744–3823).

### Health loss

- The Health track shows a Character's current vitality, including injuries taken and exhaustion. This descriptive use of “exhaustion” does not create a separate status or effect without another rule.
- The Health track has Healthy, Injured, and Heavily Injured sections. A Character's current state is the section containing their Health marker; the section labels have no standalone effect unless another rule refers to that state.
1. Move the Health marker n slots right.
2. When crossing into a section occupied by Armor: discard that Armor, then continue movement.
3. If the marker reaches the Skull: the Character dies.
- **Plain rule:** Move the Health marker right for Health loss and left for Health restoration.
  - **Source:** Official Rulebook p. 18, “CHARACTER’S HEALTH AND WOUNDS — marker movement,” `RB-P18-015`.

### Death

1. Remove the miniature from the board.
2. Lose all carried Items.
3. The Character loses and no longer takes part in the game.

### Serious Wounds

- Draw a random Serious Wound; place it in the leftmost health section lacking one.
- If the Health marker is in that section: move it to the first empty slot of the next section; resolve Armor loss if applicable.
- Serious Wounds reduce both current and maximum usable Health. Duplicate Wounds may exist but do not stack effects.
- On discarding a Wound: the owner chooses which one; slide remaining Wounds left. Do not move Health just because a Wound was discarded.
- Restoring Health may restore fewer points than an effect offers.

### Serious Wound effects (nine base titles)

Exact physical occurrences are in the card corpus; official and TTS wording variants are preserved per title and never merged into one "canonical" wording.

- **ARM** — You have only 1 Hand slot. If you have Items in both Hand slots, you must instantly discard the Item from one of them.
- **BLEEDING** — Whenever you Pass: lose 1 Health.
- **BODY** — Your Hand Size is 1 lower.
- **EYES** — +1 to all your Shoot results (official wording; the TTS face reads "Shoot values" — variant preserved, see conflicts).
- **GUTS** — Whenever you Pass: get 1 Contamination card.
- **HAND** — "Use Item" Action costs you 1 Action card more.
- **KNEE** — Using "Make a Move" or "Make a Move with Secure token" as your first Action in a Round costs you 1 Action card more. (One TTS variant instead reads: "Make a Move with [two overlapping white angular lobes glyph]" costs you 1 Action card more — variant preserved.)
- **LEG** — Using the "Make a Move" Action from a Room with an Intruder costs you 1 Action card more. (One TTS variant extends this to "...or through a Corridor with an Intruder" — variant preserved.)
- **LUNGS** — Whenever you Pass: lose 1 Oxygen (even in a Section with active Life Support). If you already have 0 Oxygen, lose 2 [unresolved local step-glyph on the TTS face; most plausibly Health by analogy with BLEEDING — verify against an official face before implementation].

- **Source:** Rulebook p. 18 (lines 3785–3810); exact per-occurrence text in `assets/tts-mod/extract/card-text-corpus.json` (Serious Wound family).

### Eclosion death exception

- An eclosion death during the game places one Adult in the dead Character’s Room; it may immediately attack another Character there.
- **Source:** Rulebook p. 38 (lines 6114–6116).
- The FAQ’s “Slasher” answer is Neoflesh-expansion-specific, not a base-game replacement rule.
  - **Source:** FAQ v1.2, “Neoflesh Cult” §5 (lines 198–200).

## INT-007 — Intruder health by type

- **Source:** Rulebook p. 34 (lines 5670–5687).

### Larva health

- In a Corridor: 1 Hit kills.
- In a Room: 1 Hit kills, regardless of the die roll.

### Drone health

- Killing Drones is only harder when they are in Corridors (2 Hits needed).
- Shooting them in Rooms is always resolved the same as shooting Adult Intruders.

### Queen health

- When the Queen Health marker reaches the final space (or is dealt a lethal Hit):
  1. Ignore any further Hits dealt to the Queen in that Action.
  2. Draw the top card of the Queen Health deck and resolve it.
  3. Check the number shown; discard that many additional Queen Health cards without revealing them.
  4. Resolve the effect on the bottom part of the card. This resolves even if the Queen dies.
- **Source:** Rulebook p. 35 (lines 5747–5760).
- **FAQ:** Shooting at the Queen works the same as for Adult Intruders, but resolve the Queen Health card instead of removing the miniature. Shooting with 2 Hits resolves the top Queen Health card; if the roll is 2 or fewer (or a skull), the Queen takes damage.
  - **Source:** FAQ v1.2, “General rules” #1 (lines 15–20).

### Intruder Hit markers in Corridors

- Intruders in Corridors never have left-over Hit markers placed beside them.
- An injured Intruder moving to a Corridor discards all Hit markers.
- **Source:** Rulebook p. 34 (lines 5683–5687).

### Adult health

- **Plain rule:** Each Hit assigned to an Adult in a Corridor kills 1 Adult.
- **Plain rule:** An Adult in a Corridor dies when assigned 1 Burst Hit.

### Queen tracking and lifecycle

- **Plain rule:** Do not place individual Hit markers beside the Queen model; record Queen damage on the Queen’s Hits track.
- **Plain rule:** Discard the Queen Health card that triggered the resolution.
- **Plain rule:** After resolving the Queen Health card, reset the Queen’s Hits marker to 0.
- **Plain rule:** When the Queen dies, remove her model from the game.

### Queen Health source occurrences

| Source occurrence | Exact printed/illustrated text | Authority / provenance |
|---|---|---|
| `RB-P35-011` — QUEEN HEALTH card sample | `Discard 1 additional card.` | Official Rulebook p. 35 illustration. |
| `game-queenHealthDeck-164.png` | `title: Discard; body: 1 additional cards.; section: 1 additional cards.; section: If the card was drawn by a [character].; Each [character] in the Room with the Queen Draws 2 [actionCard].` | TTS secondary `draft-full` occurrence; preserve literal extraction and conditional text as a variant. |

- **Source:** Rulebook pp. 33 and 35, `RB-P33-005`, `RB-P33-069`, `RB-P35-010`, `RB-P35-011`, `RB-P35-022`, `RB-P35-023`, and `RB-P35-025`; TTS Queen Health occurrence at `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-164.png`.
- **Boundary:** Preserve `SEM-Q-023`, `SEM-Q-025`, `SEM-Q-026`, `SEM-Q-027`, `SEM-Q-029`, `SEM-Q-038`, and `SEM-Q-105` where applicable. The official sample and TTS occurrence remain separate; no Queen Health interrupt, final-card death, actor attribution, terminal-glyph, Wound allocation, or capacity default is added.

## INT-008 — Contamination, Infection, and Eclosion

- **Source:** Rulebook p. 36 (lines 5825–5871); Rulebook p. 38 (lines 6079–6116).

### Contamination

- Gaining contamination: draw a contamination card and place it in the Character’s discard pile.
- Contamination cannot pay Action-card discard costs. It can be discarded when passing.
- Scanning identifies an Infected card only when its hidden text contains the exact word “INFECTED”; otherwise it is Not Infected.
- A Larva on a Character board has no immediate standalone penalty but affects endgame survival.

### Infection Procedure

1. Scan all Contamination cards in hand.
2. If any scanned card contains “INFECTED” and the Character has no board Larva: place one Larva on the Character board.
3. Move all Contamination cards from hand to the top of the discard pile.

### Eclosion Procedure

1. Draw 4 cards from the Action deck into hand. Do not scan them.
2. If hand contains at least 1 Contamination card:
   - The Character dies.
   - If the procedure occurred during the game: place 1 Adult in the Character’s Room; resolve the resulting entry attack.
3. Else: the Character survives; discard all cards in hand.

### Open interpretation — eclosion existing-hand behavior

The procedure says to check for Contamination “in hand” after drawing four, but does not say to clear the existing hand first. The literal reading includes pre-existing hand cards. This should be marked as an implementation interpretation or seek official clarification; do not silently assume hand emptiness.

- **Plain rule:** Contamination cards occupy space in a Character’s Action deck.
- **Plain rule:** Scanning a Contamination card by itself does not determine a universal consequence; the effect or procedure that calls for scanning specifies the consequence.
- **Plain rule:** Place a Larva only when the causing effect or procedure instructs that placement.
- **Plain rule:** Some effects, including the Surgery Room, remove a Larva from a Character.
- **Source:** Rulebook p. 36, `CONTAMINATION CARDS — deck effect`, `USING SCANNER — effect context`, and `INFECTED BY LARVA — source procedure/removal` (`RB-P36-007`, `RB-P36-015`, `RB-P36-020`, and `RB-P36-023`).
- **Boundary:** Preserve `ACT-CARD-002` for Contamination-deck identity/cost restrictions and the source-defined Infection/Eclosion procedures. The non-exhaustive “a few effects” wording does not become a complete Larva-removal list, and no deck placement or universal scanning default is added.

## INT-009 — Escape, Hibernation, and Lander

- **Source:** Rulebook p. 38 (lines 6141–6178); Rulebook p. 37 (lines 6043–6074).

### Shared escape/hibernate attempt gate

Applies to Landing Zone/Lander, Hibernatorium, and Escape Shuttle:
1. Make the required Noise roll.
2. If an Intruder is in the Character’s Room after that roll: fail; the Character remains in the Room.
3. Else: succeed according to mode.

### Lander

- Success: board the Lander and wait for Event Phase launch. Entry can be undone if an Intruder appears in the Landing Zone.
- **Boarded-model placement:** Place models of Characters aboard the Lander on the Anti-Aircraft slot. **Source:** `RB-P37-060` / Rulebook p. 37, `LANDER — boarded model`.
- Lander Characters: skip Turns but do not Pass; cannot voluntarily leave; still participate in Cleanup; automatically leave if any Intruder appears in Landing Zone.
- **Health immunity:** A Character inside the Lander cannot lose Health from any effects. **Source:** Rulebook p. 37, `LANDER — Health immunity`.
- Launch: at the very start of Event Phase, any one Character in the Lander may launch. One decision launches everyone. All boarded Characters are moved to their Character boards and marked Escaped.

### Hibernation

- **Setup source:** Rulebook p. 8, “Sections Setup,” step 2 note.
- The Hibernatorium begins Undiscovered at its linked map position; leave its Undiscovered tile there until a Character reaches it.
- While it remains Undiscovered, Noise cannot be placed in any of the three Corridors connected to it.
- When the first Character reaches the Hibernatorium, it becomes Discovered; the special Noise prohibition then ends.
- The Hibernatorium cannot be Used while Undiscovered and inactive. Once available, it can provide safety to multiple Characters.
- Success only if Hibernatorium is Active.
- Lock in pod; take no further part until endgame.
- Facility destruction can still kill a hibernating Character.

### Escape Shuttle

- Success: leave the Facility and take no further part until endgame.
- Anti-Aircraft does not affect the Escape Shuttle.
- **Life Support Control C / Hibernatorium:** Life Support Control C can turn on the Hibernatorium. **Source:** Rulebook p. 19, `SECTION B — Hibernatorium activation`.
- **Life Support Control C / Hibernatorium:** Life Support Control C can activate the Hibernatorium. **Source:** Rulebook p. 19, `SECTION C — Hibernatorium control`.
- **Escape Shuttle capacity:** The Escape Shuttle can carry only 1 Character. **Source:** Rulebook p. 19, `SECTION C — Escape Shuttle capacity`.
- **Boundary:** The two Hibernatorium bullets remain separate source occurrences. INT-009’s existing active/inactive, Undiscovered, and escape/hibernate procedures remain in force; the one-use Room Help note is preserved separately in the ACT-ROOM-001 table.

## INT-010 — Autodestruction and Facility destruction

- **Source:** Rulebook p. 38 (lines 6117–6140); Rulebook p. 7 (lines 807–825).

### Activating autodestruction

- Place the token 5 Round spaces ahead (four intervening empty spaces).
- If no such track space exists: place beyond the final space; trigger at game end instead.

### Facility destruction

1. End the game.
2. Kill all non-Escaped Characters, including Hibernating Characters.
3. Kill all Intruders including the Queen.
4. Treat every Room and Nest as destroyed.
- **Overwhelming Fire:** Running out of Fire markers when one must be placed destroys the Facility (RB p. 23, `RB-P23-010`–`RB-P23-012`); resolve the Facility-destruction consequences above.

### FAQ precedence

- If autodestruction is armed when the game ends, it still resolves before the endgame sequence.
  - **Source:** FAQ v1.2, “General rules” #3 (lines 26–28).
- **Autodestruction deactivation:** “Autodestruction can be deactivated only through a complete Facility power shutdown in the Reactor Room.” **Source:** Rulebook p. 38, `AUTODESTRUCTION PROCEDURE — deactivation requirement`.
- **Autodestruction location:** “Deactivate Autodestruction only in the Reactor Room.” **Source:** Rulebook p. 38, `AUTODESTRUCTION PROCEDURE — off location`.
- **Facility destruction (official page-2 occurrence):** “The Facility can be Destroyed in a couple of ways during the game. When it is Destroyed all Characters who have not Escaped die, all Characters who have Hibernated die, and all Intruders (including the Queen) die. The Nest is considered Destroyed. The Facility can be Destroyed as a result of the Autodestruction Procedure or when a Fire marker must be placed and there are no more Fire markers in the pool.” **Source:** Official Objective Help Sheet `P2-GT-05`.
- **Facility destruction (official page-1 occurrence):** retain the same exact text as a separate occurrence: “The Facility can be Destroyed in a couple of ways during the game. When it is Destroyed all Characters who have not Escaped die, all Characters who have Hibernated die, and all Intruders (including the Queen) die. The Nest is considered Destroyed. The Facility can be Destroyed as a result of the Autodestruction Procedure or when a Fire marker must be placed and there are no more Fire markers in the pool.” **Source:** Official Objective Help Sheet `P1-GT-05`.

The deactivation bullets remain separate: one source states the complete power-shutdown requirement and the other states the Reactor Room location. The Facility-destruction occurrence adds exact causes/consequences but does not replace the existing INT-010 sequence.

IDs satisfied: `RB-P38-025.fact`, `RB-P38-032.rule`, `OBJ-26`, `OBJ-4`.

## INT-011 — Endgame and objective resolution

- **Source:** Rulebook p. 39 (lines 6238–6335); Rulebook p. 7 (lines 786–802).

### End triggers

The game ends when:
1. Round 14 ends: every Character not Escaped and not Hibernated dies.
2. All players have died, Escaped, or Hibernated.
3. The Facility is destroyed (including autodestruction resolution).

### Endgame resolution order

1. First apply pending autodestruction, if applicable.
2. For each alive Escaped/Hibernated Character without a board Larva: move all Action-deck and discard cards into hand; resolve the Infection Procedure.
3. For each alive Escaped/Hibernated Character currently with a board Larva: gain 1 Contamination; reshuffle the entire deck (hand + discard); resolve the Eclosion Procedure.
4. For each still-alive Character: if no Objective previously chosen, choose now; reveal and check the chosen Objective.
5. Each remaining Character whose Objective is fulfilled wins.

### Official Larva eligibility timing

“Currently has a Larva” in step 3 is evaluated when step 3 is reached. A Larva acquired in the preceding step 2 Infection Procedure qualifies for eclosion. The current official rulebook expressly notes that a Character may have gained a Larva “during this Sequence,” so this is a source-resolved rule rather than an implementation interpretation. It does not determine the order in which multiple Characters resolve within either cohort and does not resolve OQ-001.

### Objective semantics

- At the start of the game, each player is dealt two hidden Objective cards: one Mission Objective and one Private Objective. Their contents are not revealed to other players before the endgame reveal unless a rule explicitly says otherwise.
- A Mission Objective corresponds to the squad's shared Mission described on the Mission Task card.
- A Private Objective contains a unique individual Objective for that Character.
- An Objective is fulfilled when all its conditions are met at the end of the game. It does not matter which player fulfilled them.
- Each player begins with one Mission Objective and one Private Objective and must choose one.
- A Mission Task is shared, face-up from setup, and immutable.
- Escape means leaving via Lander or Escape Shuttle—not hibernating.
- A Survivor did not die during play or final Eclosion.
- An Escaped Character who later dies in final Eclosion may have fulfilled an “Escape” objective condition but does not win because final winner selection is limited to remaining alive Characters.

- **Plain rule:** Preserve the Objective Help Sheet's game-term definitions and printed Objective effects as source-linked reference text; do not infer semantics beyond the printed wording or icon tokens.
- **Source:** Official Objective Help Sheet, page 2, reproduced by `assets/tts-mod/extract/v2-dl/tree/cards/reference/objectives-help-sheet-page-2.jpg`.

#### Game Terms

| Source heading | Exact printed definition |
|---|---|
| `FULFILLED` | “An Objective is fulfilled when all of its conditions are met at the end of the game. It’s not important which player fulfilled them (or even if this happens as a result of an Event or another non-player effect).” |
| `SURVIVOR` | “A Character who has not died during the game or during the final Eclosion Procedure at the End of the Game sequence. Remember that all Characters who have not Escaped (using the Lander or the Escape Shuttle) or Hibernated, die after the 14th Round.” |
| `ESCAPE` | “Characters who leave the Facility using the Lander or the Escape Shuttle, but not those who have Hibernated. It is irrelevant if they die during the final Eclosion Procedure – they still count as a Character who has Escaped.” |
| `DATA TOKEN` | “Characters can gain a Data token using the Server Room (Section B). Once gained by a Character, a Data token cannot be lost or traded.” |
| `FACILITY DESTRUCTION` | “The Facility can be Destroyed in a couple of ways during the game. When it is Destroyed, all Characters who have not Escaped die, all Characters who have Hibernated die, and all Intruders (including the Queen) die. The Nest is considered Destroyed. The Facility can be Destroyed as a result of the Autodestruction Procedure or when a Fire marker must be placed and there are no more Fire markers in the pool.” |
| `QUEEN IS DEAD` | “The Queen is considered dead when the Facility is Destroyed or when the Queen Health deck is empty. A reminder is written down on the Queen Health cards space.” |
| `NEST IS DESTROYED` | “The Nest is Destroyed when the Facility is Destroyed or when there are no more Eggs as a result of Characters taking or Destroying them on the special space on the Section “C” border piece.” |

#### Objective entries

| Source entry | Exact printed text |
|---|---|
| `QUARANTINE` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 3+`<br>`QUARANTINE`<br>“No [character] can Escape from the Facility using the [ICON: pale twin-lobed arch-like mark] (Section A).”<br>`PRIVATE OBJECTIVE`<br><br>Associated note: “No [character]” also includes your Character. Characters may still Hibernate and use the Escape Shuttle. |
| `CORPORATE CONTRACT` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 5+`<br>`CORPORATE CONTRACT`<br>“The [character] number 5 must NOT Survive (unavailable if you are the [character] number 5).”<br>`OR`<br>“You must be the only Survivor.”<br>`PRIVATE OBJECTIVE` |
| `LUXURIOUS OFFER` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 2+`<br>`LUXURIOUS OFFER`<br>“You must Survive carrying an Egg from the Nest (Section C).”<br>`PRIVATE OBJECTIVE` |
| `EXPERIMENTAL SUBJECTS` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 3+`<br>`EXPERIMENTAL SUBJECTS`<br>“All [character] who Escape from the Facility must have at least 3 Contaminations in total among them (no matter if they Survive after Escaping).”<br>`PRIVATE OBJECTIVE`<br><br>Associated note: “Count all Contaminations in all players’ decks (including yours) who have Escaped from the Facility. It is irrelevant if they die during the final Eclosion Procedure.” |
| `STATE'S EVIDENCE` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 3+`<br>`STATE'S EVIDENCE`<br>“Out of Surviving Characters you must be the only one with a Data token (from the Server Room in Section B).”<br>`PRIVATE OBJECTIVE` |
| `SHUTDOWN` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 3+`<br>`SHUTDOWN`<br>“All Life Support tokens must be [lifeSupportInactive], or removed from the game.”<br>`AND`<br>“You must have a Data token (from the Server Room in Section B).”<br>`PRIVATE OBJECTIVE`<br><br>Associated note: “You can deactivate Life Support Systems by using Life Support Control Rooms “A”, “B”, and “C”, or by shutting down the Reactor in the Reactor Room in Section C.” |
| `VENI, VIDI, VICI` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 2+`<br>`VENI, VIDI, VICI`<br>“The Nest (Section C) must be destroyed.”<br>`PRIVATE OBJECTIVE` |
| `WE'VE GOT HISTORY` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 4+`<br>`WE'VE GOT HISTORY`<br>“The lowest ranking [character] must Survive (unavailable if you are the lowest ranking [character]).”<br>`OR`<br>“The highest ranking [character] must NOT Survive (unavailable if you are the highest ranking [character]).”<br>`PRIVATE OBJECTIVE`<br><br>Associated note: “If you are the lowest ranking Character you cannot choose the first option. If you are the highest ranking Character you cannot choose the second option.” |
| `THE GREAT HUNT` | “Remove the other Objective from the game to: Progress the Objective Choice track once and draw A accordingly.”<br><br>`[ICON: white spike above blue oval] 2+`<br>`THE GREAT HUNT`<br>“The Queen must be dead.”<br>`PRIVATE OBJECTIVE` |

- **Boundary sentence:** These tables preserve the exact Objective Help source occurrence; they do not replace the official endgame procedure in `INT-011`, do not interpret the source icon descriptions as new vocabulary, and do not resolve `SEM-Q-027`.

### Objective semantics source occurrences

| Source occurrence | Exact source text | Evaluates via: |
|---|---|---|
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-056.png` | **ERADICATION:** “Queen must be killed.” AND “The Facility cannot be destroyed.” | Evaluates via: INT-007, INT-010 |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-101.jpg` | **RECONNAISSANCE:** “All Rooms of the A, B, and C type must be Discovered.” | Evaluates via: ACT-EXPLORE-001, FND-012 (Room types) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-116.jpg` | **THE SUPPLY ROUTE:** “There must be a continuous path of Reinforced Corridors from the Landing Zone (Section A) to the Life Support Control C.” AND “The Facility must NOT be destroyed.” | Evaluates via: FND-012 Reinforced Corridors (proposed, P3), INT-010 |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-123.jpg` | **ESSENTIAL DATA:** “At least 1 [ICON: compact white outlined rounded-top form with a broad rectangular torso and paired side/lower projections] with a Data token (from the Server Room in Section B) must Escape using the [ICON: broad white three-pronged mound with dark lower cutouts] (Section A).” AND “There must be no Unexplored Corridors in Section A.” | Evaluates via: ROOM-19 (proposed, P3), INT-009, INT-011 (Escape definition), RT-009a, FND-012 (Unexplored Corridor); GAP: literal TTS icon identities have no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-00.png` | **PRIMARY SAMPLES:** “At least 2 Eggs must be taken out of the Facility using the Lander or Escape Shuttle.” | Evaluates via: FND-012 (Nest and Eggs), ITM-002 (Eggs are Heavy Items), INT-009, INT-011 (Escape definition), RT-009a |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-01.png` | **PERIMETER CLEARING:** “The Reactor must be shut down.” AND “All Section Rooms A must be Explored.” | Evaluates via: FND-012 (Reactor), ROOM-22 Reactor table row (proposed, P3), ACT-EXPLORE-001, FND-012 (Room types) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-02.png` | **THE SUPPLY ROUTE:** “The path from the Landing Zone to the Server Room must be Reinforced. (There is a continuous path of Reinforced Corridors from the Landing zone to the Server Room).” AND “The Facility must not be destroyed.” | Evaluates via: FND-012 Reinforced Corridors (proposed, P3), ROOM-19 (proposed, P3), INT-010 |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-04.png` | **ESSENTIAL DATA:** “At least 1 Character with Data token from the Server Room must Escape using the Lander.” | Evaluates via: ROOM-19 (proposed, P3), INT-009, INT-011 (Escape definition), RT-009a |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-05.png` | **RETRIEVAL:** “At least 3 corpses from Hibernatorium must be in the Landing Zone.” AND “The Lander must not be destroyed.” | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a; GAP: corpses from the Hibernatorium has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-06.png` | **ERADICATION:** “Queen must be killed.” AND “The Nest must be destroyed.” | Evaluates via: INT-007, FND-012 (Nest), ACT-ROOM-001 Nest-destruction marker (proposed, P3) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-07.png` | **ESCORT MISSION:** “The Robot must reach the Reactor.” | Evaluates via: ACT-ROBOT-001 |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-08.png` | **FACILITY RESTART:** “The Hibernatorium must be [hibernatorium-active] and at least 2 Life Support Systems must be [UNRESOLVED: horizontal cyan-and-white bilateral badge with rounded white end masses, a cyan connector, and a narrow upright central slot/tab].” AND “The Facility cannot be destroyed.” | Evaluates via: INT-009 (Hibernation), FND-009, ROOM-14/18 (proposed, P3), INT-010; GAP: [hibernatorium-active] source-local state token has no corpus rule; GAP: unresolved Life Support badge has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-09.png` | **ESSENTIAL DATA:** “All Section Rooms A, B and C must be Explored.” | Evaluates via: ACT-EXPLORE-001, FND-012 (Room types) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-060.jpg` | **SELF-SERVING:** “You must be the only Survivor.” | Evaluates via: INT-011 (Survivor definition), RT-014 |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-01.png` | **OFFICIAL ORDER:** “The Mission Task must be fulfilled.” | Evaluates via: INT-011 (Objective semantics) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-04.png` | **SELF-SERVING:** “You cannot choose this Objective. You must choose the Private Objective instead.” | Evaluates via: INT-011 (Objective semantics); GAP: Objective-choice restriction has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-05.png` | **ULTERIOR MOTIVE:** “You must choose this Objective. Mission Task must not be Fulfilled.” | Evaluates via: INT-011 (Objective semantics); GAP: Objective-choice restriction has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-06.png` | **VENI, VIDI, VICI:** “The Nest must be destroyed.” | Evaluates via: FND-012 (Nest), ACT-ROOM-001 Nest-destruction marker (proposed, P3) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-08.png` | **QUARANTINE:** “No Character can Escape from the Facility using the Lander.” | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-11.png` | **WE'VE GOT HISTORY:** “You and the Character with the lowest rank must Survive. (If you are a Character with the lowest rank you must fulfill the second option from this Objective) OR The Character with the highest rank must not Survive. (If you are a Character with the highest rank you must fulfill the first option from this Objective)”. | Evaluates via: INT-011 (Survivor definition), RT-014, FND-004 (Rank); GAP: Objective option ownership has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-12.png` | **THE RIGHT MOMENT TO STRIKE:** “Character of the Player 1 cannot Survive. (If you are the Player 1 you have to fulfill the second option from this Objective) OR You have to be the only Survivor.” | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Objective option ownership has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-13.png` | **GREENER PASTURES:** “Character of the Player 2 cannot Survive. (If you are the Player 2 you have to fulfill the second option from this Objective) OR You have to be the only Survivor.” | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Objective option ownership has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-14.png` | **AN OLD FEUD:** “Character of the Player 3 cannot Survive. (If you are the Player 3 you have to fulfill the second option from this Objective) OR You have to be the only Survivor.” | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Objective option ownership has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-15.png` | **HOSTILE TAKEOVER:** “Character of the Player 4 cannot Survive. (If you are the Player 4 you have to fulfill the second option from this Objective) OR You have to be the only Survivor.” | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Objective option ownership has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-16.png` | **LAB RATS:** “All Characters who Escape from the Facility must have at least 3 Contamination cards in total.” | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a, INT-008 |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-17.png` | **INSIDER INFORMATION:** “You must be the only surviving Character with a Data token from the Server Room.” | Evaluates via: INT-011 (Survivor definition), RT-014, ROOM-19 (proposed, P3) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-18.png` | **OLD FRIEND:** “You must Escape from the Facility with at least 1 Corpse from the Hibernatorium.” | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a; GAP: corpses from the Hibernatorium has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-19.png` | **LUXURIOUS OFFER:** “You must survive with an Egg.” | Evaluates via: INT-011 (Survivor definition), RT-014, FND-012 (Nest and Eggs), ITM-002 (Eggs are Heavy Items) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-014.jpg` | **STATE'S EVIDENCE:** “You must be the only surviving Character with a Data token from the Server Room.” | Evaluates via: INT-011 (Survivor definition), RT-014, ROOM-19 (proposed, P3) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-066.jpg` | **SHUTDOWN:** “You must have a Data token (from the Server Room in Section B)” AND “All Life Support tokens must be [lifeSupportInactive] (or removed from the game).” | Evaluates via: ROOM-19 (proposed, P3), FND-009, ROOM-14/18 (proposed, P3) |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-156.jpg` | **TRAITOR IN PLAIN SIGHT:** “Player 7's Character cannot survive.” OR “Your Character is the only survivor.” Retain “What the fuck is going on?” and “You bitch.” as non-operative source text. | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Player N eligibility has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-157.jpg` | **STOLEN VALOR:** “Player 8's Character cannot survive.” OR “Your Character is the only survivor.” Retain “Anybody ever tell you you look dead, man?” as non-operative source text. | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Player N eligibility has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-158.jpg` | **RARE SPECIMEN:** “Player 6's Character cannot survive.” OR “Your Character is the only survivor.” Retain “Paralyses him, puts him in a coma, then keeps him alive.” as non-operative source text. | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Player N eligibility has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-159.jpg` | **HUNGRY FOR MORE:** “Player 9's Character cannot survive.” OR “Your Character is the only survivor.” Retain “You see, Mr. Parker and I... feel that the bonus situation has never been on an equitable level.” as non-operative source text. | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Player N eligibility has no corpus rule |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-161.jpg` | **WRONG CALL:** “Player10's Character cannot survive.” OR “Your Character is the only survivor.” Retain “I hate to bring this up, but, this is a commercial ship, not a rescue ship.” as non-operative source text, and retain the `[numberOfCharacters] 10+` source-local marker without assigning eligibility. | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Player N eligibility has no corpus rule; GAP: 10+ source-local scope marker has no corpus rule |
| Official Objective Help Sheet `P1-GT-01` | **FULFILLED:** “An Objective is fulfilled when all of its conditions are met at the end of the game. It’s not important which player fulfilled them (or even if this happens as a result of an Event or another non-player effect).” | Evaluates via: INT-011 (Objective semantics) |
| Official Objective Help Sheet `P1-MO-ULTERIOR-MOTIVE` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P1-MO-ULTERIOR-MOTIVE-I01] accordingly.”; threshold “2+” with `[P1-MO-ULTERIOR-MOTIVE-I02]`; title “ULTERIOR MOTIVE”; condition “Mission Task must remain UNFULFILLED.”; footer “MISSION OBJECTIVE”. | Evaluates via: INT-011 (Objective semantics) |
| Official Objective Help Sheet `P1-MO-SELF-SERVING` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P1-MO-SELF-SERVING-I01] accordingly.”; threshold “2+” with `[P1-MO-SELF-SERVING-I02]`; title “SELF-SERVING”; condition “You must be the only Survivor.”; footer “MISSION OBJECTIVE”. | Evaluates via: INT-011 (Survivor definition), RT-014 |
| Official Objective Help Sheet `P1-MT-THE-SUPPLY-ROUTE` | threshold “3+” with `[P1-MT-THE-SUPPLY-ROUTE-I01]`; title “THE SUPPLY ROUTE”; condition “There must be a continuous path of Reinforced Corridors from the Landing Zone (Section A) to the Life Support Control C. AND The Facility must NOT be destroyed.”; note “When checking the path from the Landing Zone to Life Support Control C ignore all Closed Doors and Intruders - they are irrelevant. Only Reinforcement counts.”; footer “MISSION TASK”. | Evaluates via: FND-012 Reinforced Corridors (proposed, P3), INT-010, 02-character-actions Doors subsection |
| Official Objective Help Sheet `P1-MT-PRIMARY-SAMPLES` | threshold “2+” with `[P1-MT-PRIMARY-SAMPLES-I01]`; title “PRIMARY SAMPLES”; condition “All [P1-MT-PRIMARY-SAMPLES-I02] who Escape from the Facility must be carrying at least 2 Eggs in total among them (no matter if they Survive after Escaping).”; footer “MISSION TASK”. | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a, FND-012 (Nest and Eggs), ITM-002 (Eggs are Heavy Items), INT-011 (Survivor definition), RT-014 |
| Official Objective Help Sheet `P1-MT-FACILITY-RESTART` | threshold “2+” with `[P1-MT-FACILITY-RESTART-I01]`; title “FACILITY RESTART”; condition “The Hibernatorium must be [P1-MT-FACILITY-RESTART-I02] (by using the Life Support Control C). AND The Reactor (Section C) must be shut down (by using the Room).”; note “Shutting down the Reactor is not marked during the game but you may check it at the End of the Game by looking if the Autodestruction token has been removed from the game.”; footer “MISSION TASK”. | Evaluates via: INT-009 (Hibernation), FND-012 (Reactor), ROOM-22 Reactor table row (proposed, P3); evaluation method: official note “Autodestruction token removed from the game” |
| Official Objective Help Sheet `P1-MT-ERADICATION` | threshold “3+” with `[P1-MT-ERADICATION-I01]`; title “ERADICATION”; condition “The Queen must be dead. AND The Facility must NOT be destroyed.”; footer “MISSION TASK”. | Evaluates via: INT-007, INT-010 |
| Official Objective Help Sheet `P2-GT-01` | retain the separate page-2 **FULFILLED** occurrence with the same exact definition as `P1-GT-01`. | Evaluates via: INT-011 (Objective semantics) |
| Official Objective Help Sheet `P2-PO-CORPORATE-CONTRACT` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-CORPORATE-CONTRACT-I01] accordingly.”; threshold “5+” with `[P2-PO-CORPORATE-CONTRACT-I02]`; title “CORPORATE CONTRACT”; condition “The [P2-PO-CORPORATE-CONTRACT-I03] number 5 must NOT Survive (unavailable if you are the [P2-PO-CORPORATE-CONTRACT-I04] number 5). OR You must be the only Survivor.”; footer “PRIVATE OBJECTIVE”. | Evaluates via: RT-002, FND-011 (Help-card numbers), INT-011 (Survivor definition), RT-014; GAP: Objective availability restriction has no corpus rule |
| Official Objective Help Sheet `P2-PO-LUXURIOUS-OFFER` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-LUXURIOUS-OFFER-I01] accordingly.”; threshold “2+” with `[P2-PO-LUXURIOUS-OFFER-I02]`; title “LUXURIOUS OFFER”; condition “You must Survive carrying an Egg from the Nest (Section C).”; footer “PRIVATE OBJECTIVE”. | Evaluates via: INT-011 (Survivor definition), RT-014, FND-012 (Nest and Eggs), ITM-002 (Eggs are Heavy Items) |
| Official Objective Help Sheet `P2-PO-QUARANTINE` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-QUARANTINE-I01] accordingly.”; threshold “3+” with `[P2-PO-QUARANTINE-I02]`; title “QUARANTINE”; condition “No [P2-PO-QUARANTINE-I03] can Escape from the Facility using the [P2-PO-QUARANTINE-I04] (Section A).”; note “No [P2-PO-QUARANTINE-I05] also includes your Character. Characters may still Hibernate and use the Escape Shuttle.”; footer “PRIVATE OBJECTIVE”. | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a |
| Official Objective Help Sheet `P2-PO-INSIDER-INFORMATION` | preserve the metadata-only condition locator “Out of Surviving Characters you must be the only one with a Data token (from the Server Room in Section B).” with the occlusion and non-visible-transcription label; do not complete the face from inference. | Evaluates via: INT-011 (Survivor definition), RT-014, ROOM-19 (proposed, P3) |
| Official Objective Help Sheet `P2-PO-SHUTDOWN` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-SHUTDOWN-I01] accordingly.”; threshold “2+” with `[P2-PO-SHUTDOWN-I02]`; title “SHUTDOWN”; condition “All Life Support tokens must be [P2-PO-SHUTDOWN-I03], or removed from the game. AND You must have a Data token (from the Server Room in Section B).”; note “You can deactivate Life Support Systems by using Life Support Control Rooms “A”, “B”, and “C”, or by shutting down the Reactor in the Reactor Room in Section C.”; footer “PRIVATE OBJECTIVE”. | Evaluates via: FND-009, ROOM-14/18 (proposed, P3), ROOM-19 (proposed, P3) |
| Official Objective Help Sheet `P2-PO-EXPERIMENTAL-SUBJECTS` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-EXPERIMENTAL-SUBJECTS-I01] accordingly.”; threshold “3+” with `[P2-PO-EXPERIMENTAL-SUBJECTS-I02]`; title “EXPERIMENTAL SUBJECTS”; condition “All [P2-PO-EXPERIMENTAL-SUBJECTS-I03] who Escape from the Facility must have at least 3 Contaminations in total among them (no matter if they Survive after Escaping).”; note “Count all Contaminations in all players’ decks (including yours) who have Escaped from the Facility. It is irrelevant if they die during the final Eclosion Procedure.”; footer “PRIVATE OBJECTIVE”. | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a, INT-008, INT-011 (Survivor definition), RT-014 |
| Official Objective Help Sheet `P2-PO-THE-GREAT-HUNT` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-THE-GREAT-HUNT-I01] accordingly.”; threshold “2+” with `[P2-PO-THE-GREAT-HUNT-I02]`; title “THE GREAT HUNT”; condition “The Queen must be dead.”; footer “PRIVATE OBJECTIVE”. | Evaluates via: INT-007 |
| Official Objective Help Sheet `P2-PO-VENI-VIDI-VICI` | top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P2-PO-VENI-VIDI-VICI-I01] accordingly.”; threshold “2+” with `[P2-PO-VENI-VIDI-VICI-I02]`; title “VENI, VIDI, VICI”; condition “The Nest (Section C) must be destroyed.”; footer “PRIVATE OBJECTIVE”. | Evaluates via: FND-012 (Nest), ACT-ROOM-001 Nest-destruction marker (proposed, P3) |
| Official Objective Help Sheet `P2-NOTE-RANKING-CHOICE` | “If you are the lowest ranking Character you cannot choose the first option. If you are the highest ranking Character you cannot choose the second option.” Retain the note as an explanatory source unit with no assigned card ownership. | Evaluates via: FND-004 (Rank); GAP: Objective option ownership has no corpus rule |
| Official Objective Help Sheet `P1-MO-OFFICIAL-ORDER-1` | retain the separately inventoried, partially occluded official occurrence with top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P1-MO-OFFICIAL-ORDER-3-I01] accordingly.”; threshold “2+” with `[P1-MO-OFFICIAL-ORDER-3-I02]`; title “OFFICIAL ORDER”; condition “The Mission Task must be fulfilled.”; footer “MISSION OBJECTIVE”. | Evaluates via: INT-011 (Objective semantics) |
| Official Objective Help Sheet `P1-MO-OFFICIAL-ORDER-2` | retain the separately inventoried, partially occluded official occurrence with top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P1-MO-OFFICIAL-ORDER-3-I01] accordingly.”; threshold “2+” with `[P1-MO-OFFICIAL-ORDER-3-I02]`; title “OFFICIAL ORDER”; condition “The Mission Task must be fulfilled.”; footer “MISSION OBJECTIVE”. | Evaluates via: INT-011 (Objective semantics) |
| Official Objective Help Sheet `P1-MO-OFFICIAL-ORDER-3` | retain the fully visible official occurrence with top instruction “Remove the other Objective from the game to: Progress the Objective Choice track once and draw [P1-MO-OFFICIAL-ORDER-3-I01] accordingly.”; threshold “2+” with `[P1-MO-OFFICIAL-ORDER-3-I02]`; title “OFFICIAL ORDER”; condition “The Mission Task must be fulfilled.”; footer “MISSION OBJECTIVE”. | Evaluates via: INT-011 (Objective semantics) |
| Rulebook p. 39 `VENI, VIDI, VICI — player count` | “VENI, VIDI, VICI is eligible at 2 or more Characters.” | Evaluates via: INT-011 (Objective semantics); GAP: Objective player-count eligibility has no corpus rule |
| Rulebook p. 39 `VENI, VIDI, VICI — requirement` | “VENI, VIDI, VICI requires the Nest in Section C to be destroyed.” | Evaluates via: FND-012 (Nest), ACT-ROOM-001 Nest-destruction marker (proposed, P3) |
| Rulebook p. 39 `VENI, VIDI, VICI — type` | “VENI, VIDI, VICI is a Private Objective.” | Evaluates via: INT-011 (Objective semantics) |
| Rulebook p. 39 `PRIMARY SAMPLES — Escape group` | “Primary Samples applies to all Characters who Escape.” | Evaluates via: INT-009, INT-011 (Escape definition), RT-009a |
| Rulebook p. 39 `PRIMARY SAMPLES — Egg requirement` | “Escaping Characters collectively must carry at least 2 Eggs.” | Evaluates via: FND-012 (Nest and Eggs), ITM-002 (Eggs are Heavy Items) |
| Rulebook p. 39 `PRIMARY SAMPLES — type` | “Primary Samples is a Mission Task.” | Evaluates via: INT-011 (Objective semantics) |

### Evaluation gaps surfaced by cross-referencing

- `literal TTS icon identities`: no corpus rule resolves the source-local icons in the ESSENTIAL DATA occurrence to Character/Lander semantics. Affected ID: `CARD-game-missionTaskDeck-game-missionTaskDeck-123.jpg`.
- `corpses from the Hibernatorium`: no corpus rule defines the corpse identity, source, or placement. Affected IDs: `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-05.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-18.png`.
- `[hibernatorium-active]` source-local state token: no corpus rule defines this literal TTS token without normalizing it to the official Hibernatorium state. Affected ID: `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-08.png`.
- `unresolved Life Support badge`: no corpus rule defines this literal TTS badge’s state meaning. Affected ID: `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-08.png`.
- `Objective-choice restriction`: no corpus rule maps the TTS instructions not to choose this Objective / to choose the Private Objective, or to choose this Objective. Affected IDs: `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-04.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-05.png`.
- `Objective option ownership`: no corpus rule assigns the printed first/second options to a player or resolves the ranking-note choice restriction. Affected IDs: `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-11.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-12.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-13.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-14.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-15.png`, `OBJ-44`.
- `Player N eligibility`: no corpus rule defines eligibility for the source references to Players 6–10. Affected IDs: `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-156.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-157.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-158.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-159.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-161.jpg`.
- `10+ source-local scope marker`: no corpus rule defines its base-game eligibility. Affected ID: `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-161.jpg`.
- `Objective availability restriction`: no corpus rule defines the unavailable-if-number-5 restriction on CORPORATE CONTRACT. Affected ID: `OBJ-30`.
- `Objective player-count eligibility`: no corpus rule maps the VENI, VIDI, VICI 2+ Character eligibility assertion. Affected ID: `RB-P39-022.fact`.

IDs satisfied: `CARD-game-missionTaskDeck-game-missionTaskDeck-056.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-101.jpg`, `CARD-game-missionTaskDeck-game-missionTaskDeck-116.jpg`, `CARD-game-missionTaskDeck-game-missionTaskDeck-123.jpg`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-00.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-01.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-02.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-04.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-05.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-06.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-07.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-08.png`, `CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-09.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-060.jpg`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-01.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-04.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-05.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-06.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-08.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-11.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-12.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-13.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-14.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-15.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-16.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-17.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-18.png`, `CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-19.png`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-014.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-066.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-156.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-157.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-158.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-159.jpg`, `CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-161.jpg`, `OBJ-0`, `OBJ-12`, `OBJ-13`, `OBJ-16`, `OBJ-17`, `OBJ-20`, `OBJ-21`, `OBJ-22`, `OBJ-30`, `OBJ-34`, `OBJ-35`, `OBJ-36`, `OBJ-38`, `OBJ-39`, `OBJ-42`, `OBJ-43`, `OBJ-44`, `OBJ-7`, `OBJ-8`, `OBJ-9`, `RB-P39-022.fact`, `RB-P39-023.rule`, `RB-P39-024.fact`, `RB-P39-027.rule`, `RB-P39-028.fact`, `RB-P39-030.fact`.

## Examples

### EX-INT-001 — Bag Development: Larva drawn

- **Given:** Bag Development draws a Larva token.
- **When:** It is resolved.
- **Then:** Do not place a Larva; add two random Drone tokens to the bag, then send the Larva token to the bottom of the Larva pile.

### EX-INT-002 — Equal routes tie-break

- **Given:** An Adult group has two equally short paths to its nearest target.
- **When:** Movement resolves.
- **Then:** Compare the first Corridor/Room of each route; choose the route whose first element has the lower ID. If it would cross a Closed Door, destroy the Door instead and leave the group in place.

### EX-INT-003 — Secure prevents entry attack

- **Given:** A Room with 2 Secure tokens is occupied by a Character, and an Intruder is placed there by a Hazard draw.
- **When:** The entry attack would resolve.
- **Then:** Discard 1 Secure token; do not resolve the attack. The Intruder remains in the Room.

### EX-INT-004 — Larva attack on infected Character

- **Given:** Two Larvae attack a Character who already has a Larva on their board.
- **When:** Each attack resolves.
- **Then:** Each attack gives Contamination; the attacking Larvae are discarded rather than added to the board.

### EX-INT-005 — Eclosion death during game

- **Given:** A Character resolves an Eclosion Procedure during the game and has Contamination in hand.
- **When:** The procedure resolves.
- **Then:** The Character dies, one Adult is placed in their Room, and it may immediately attack another Character there.

### EX-INT-006 — Autodestruction before endgame

- **Given:** Autodestruction is armed and the Round marker reaches its final space.
- **When:** End of Game would trigger.
- **Then:** Autodestruction resolves first: the Facility explodes, all non-Escaped Characters (including Hibernating) die, then the endgame sequence proceeds.