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