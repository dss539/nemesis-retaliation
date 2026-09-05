# Foundations and Conventions

## FND-001 — Game-rule scope

- **Source:** Rulebook pp. 12–15, “Game Round Structure”; FAQ v1.2, “General rules.”
- **Plain rule:** This corpus describes the base-game rules as interpreted from the official rulebook and FAQ. Expansion, solo/co-op, and variant rules are out of scope unless a record says otherwise.
- **Authority:** Apply the precedence order in [readme.md](readme.md). The FAQ is a clarification/errata source, not a substitute for unaddressed rulebook text.

## FND-002 — Resolution language

- **Plain rule:** A rule procedure is resolved in the order written. Where the source directs a player to choose, the choice belongs to that player unless the source assigns it differently.
- **Tie-breaking:** When a rule calls for the Character first in turn order, begin with the current Starting Player and proceed clockwise.
- **Nightmare Rule:** If a ruling or order of effects remains unresolved, resolve the situation in the worst possible scenario for the players. If the result is still unclear, use the outcome worst for the Character first in Turn order.
- **Source:** Rulebook p. 13, “Turn order as tiebreaker” (extracted text lines 2995–3004); Rulebook p. 16, “Golden Rules — Nightmare Rule” (`RB-P16-001`–`RB-P16-002`).

## FND-003 — Impossible instructions

- **Plain rule:** If an Event-card sentence is impossible to resolve, ignore that sentence and continue with the remainder of that card.
- **Boundary:** This explicit partial-resolution rule is cited for Event cards. Do not generalize it to other actions without a source.
- **Source:** Rulebook p. 15, “Event card resolution” (extracted text lines 3269–3277).

## FND-004 — Official terms used in this corpus

- **Character:** an in-game player character.
- **Player:** the human participant controlling a Character.
- **Turn:** one player’s ordered opportunity to perform actions and resolve turn-end effects.
- **Round:** Player Phase, Intruder Phase, Event Phase, then Cleanup Phase.
- **Room / Corridor:** map spaces referred to by the rulebook. Their mandatory project geometry and relationship are defined by FND-005.
- **Model:** the rules term for a physical figure, whether a particular edition supplies that figure as a miniature or a standee.
- **Intruder / Primeblood:** “Intruders” is the collective rules name for alien races in the *Nemesis* universe. The alien race supplied in this box is the Primebloods; during play, “Primebloods” and “Intruders” are equivalent terms.
- **In Combat:** a Character is in a Room with at least one Intruder.
- **Character board:** During setup, a chosen Character tile is placed into a universal Character board. From that point on, the assembled tile and universal board are referred to together as one Character board.
- **Rank:** Every Character has a Rank, and game effects may refer to it. Specific Action cards may allow a higher-Rank Character to command a lower-Rank Character. The Medical Support shown in the rulebook has Rank 2.
- **Source:** Rulebook pp. 12–13 (round/turn), p. 13, “Not in Combat” (extracted text lines 2901–2906), p. 4 (component-model terminology), p. 8 (Intruders/Primebloods terminology), and p. 16, “Character” / “Name and Rank” (`RB-P16-012`, `RB-P16-015`–`RB-P16-018`).

## FND-005 — Room geometry and Corridor spacing

- **Classification:** Project fidelity invariant from the established physical Facility-map and Room-tile interpretation, re-confirmed by the user. This is not an optional digital adaptation.
- **Plain rule:** Every Room and empty Room slot must be represented as a regular pointy-top hexagon. Rooms are never octagonal.
- **Six directions:** The only Room-edge directions are `NE`, `E`, `SE`, `SW`, `W`, and `NW`.
- **Corridor spacing:** Every Room slot preserves visible space beyond all six hex edges for possible Corridors, including edges where no Corridor currently exists. An absent Corridor leaves that reserved gap empty; it does not collapse neighboring Room geometry.
- **Uniform-gap derivation:** For a regular hexagon the centre-to-edge distance (apothem) is identical on all six edges and equals half the hexagon's across-flats width. Therefore a layout produces an equal Corridor gap on all six edges only when the centre-to-centre distance is the same for E/W neighbours and for the four diagonal neighbours. With an odd-row half-step offset, that holds when `row_step = col_step × √3 ⁄ 2`, and the resulting gap on every edge is `col_step − hex_width`. A layout that sets the row step to the naive `0.75 × hex_height` yields unequal gaps and is a geometry defect.
- **Corridor extent:** A Corridor occupies only the reserved gap between two adjacent Room edges. It begins at one Room's hex edge and ends at the neighbouring Room's hex edge, and must never be drawn spanning, crossing, or passing over intervening Room slots. A Corridor connects exactly two immediately adjacent Rooms.
- **Corridor gap budget:** The reserved gap is not decorative. It must remain large enough to legibly display, simultaneously: a Door token at the Corridor end against a Room, up to six Intruder-equivalents standing in the Corridor (see 03-intruders-and-survival.md, Corridor capacity), a Noise marker, and the Corridor's Noise/reinforced value. A gap sized only for a thin connector line cannot represent legal game state and is a fidelity defect.
- **Adjacency invariant:** Hex proximity alone never makes two Rooms adjacent. Characters move between neighboring Rooms only through a legal connecting Corridor. Room and Corridor topology remains authoritative over visual proximity.
- **Facility boundary:** The right and bottom edges are Facility boundaries even where no physical border piece is placed. Rooms and Corridors may not extend beyond them.
- **Cross-Section Corridors:** A Corridor placed on a boundary between two Sections belongs to both adjacent Sections.
- **Legal-target invariant:** A UI must not present off-board, unconnected, direction-mismatched, Closed-Door-blocked, or otherwise illegal destinations as Move choices. Exploration additionally requires an empty valid Room slot, so an occupied slot is not a legal Exploration destination. This does not prohibit an ordinary Move into a discovered Room merely because another Character or an Intruder occupies it. The authoritative rules engine must independently reject illegal targets.
- **Rendering invariant:** Room outlines, empty slots, status overlays, interaction hit regions, focus treatments, movement targets, and semantic-zoom representations must all preserve the same six-sided boundary. An octagonal or eight-direction representation is a rules-fidelity defect.
- **Official source boundary:** Rulebook p. 20, “Map” and “Rooms” (extracted text lines 3915–3921 and 4007–4015), establishes that the Facility consists of Rooms connected by adjacent Corridors. Rulebook p. 24, “Exploration Sequence” (extracted text lines 4501–4516), requires Corridors indicated by an Exploration card to be omitted when they would extend outside the Facility border or lead to an already placed Room. The regular pointy-top hexagon and six named directions normalize the physical component geometry as a documented project interpretation under the authority order in [readme.md](readme.md); they are not inferred from those extracted prose passages alone.

## FND-006 — Character Draft supply

- **Source fact:** The base-game component inventory contains 6 Character Draft cards.
- **Source:** Rulebook PDF p. 3, “Standard-sized cards — Character Draft cards” (quantity); Rulebook p. 10, “Player Setup — Objective Setup and Character Draft” (setup role).
- **Setup relevance:** Character Draft cards are the finite source used by the Character Draft during player setup; do not synthesize additional draft cards beyond this supply.

## FND-007 — Base-game participation and cooperation structure

- **Source:** Rulebook p. 6, introductory game description; Rulebook p. 7, “Game Modes.”
- **Player count:** The standard base game supports 1–5 players.
- **Cooperation model:** The game is semi-cooperative, not fully cooperative. The squad has a shared Mission, while each Character also has an individual Objective whose goals may conflict with those of other Characters.
- **Consequence:** Completing the shared Mission does not make all Characters collective winners; individual Objective and survival checks still determine each Character's outcome under INT-011.

## FND-008 — Gameplay-facing physical supplies

- **Source:** Rulebook pp. 3–5, component inventory; Rulebook p. 16, “Golden Rules — Component Limits” (`RB-P16-007`–`RB-P16-009`).
- **Boundary:** These are the provided physical supplies needed to represent game state. The quantities do not, by themselves, create a shortage rule; apply the source-backed Component Limits rule below.
- **Component Limits:** Most component supplies are limited and have specific rules for exhaustion. Treat every other component as limited even if it has no special exhaustion rule. If such a component is required but none is available, that component use has no effect.
- **Unresolved boundary:** This default does not choose among eligible recipients or slots, create an allocation order, or determine how the rest of a compound or exact-quantity effect proceeds after an unavailable component use. Preserve the corresponding entries in `open-questions.md`.
- **Finite card/deck supplies:**
  - 8 Mission Task cards;
  - 22 Objective cards: 7 Mission Objectives and 15 Private Objectives;
  - 20 Event cards;
  - 20 Intruder Attack cards;
  - 27 Serious Wound cards; and
  - 12 Queen Health cards.
- **Map-tile supplies:**
  - 23 Room tiles: 3 `A`, 3 `B`, 4 `C`, and 13 `?` tiles; and
  - 40 Corridor tiles: 10 each of values 1, 2, 3, and 4.
- **Character and shared components:** 5 Character boards, 6 Character tiles, 6 Character models, and 1 Intruder bag.
- **Resolution dice:** The Burst die has 6 sides, the Shoot die has 8 sides, and the Noise die has 10 sides. Multiple physical copies of a die are convenience components and do not authorize combining their rolls unless a rule explicitly says so.
- **State-marker supplies:**
  - 9 Fire markers;
  - 14 Malfunction markers;
  - 30 Universal markers;
  - 1 Round marker;
  - 5 Egg tokens;
  - 1 Autodestruction token;
  - 1 Lander token;
  - 14 Door tokens;
  - 5 Data tokens;
  - 1 Hibernatorium token;
  - 3 Life Support tokens;
  - 2 Anti-Aircraft tokens, each with Active and Inactive faces;
  - 5 Suffocating tokens;
  - 1 Starting Player token; and
  - 5 Character Oxygen counters.
- **Other gameplay models:** 1 Robot model, 6 Larva models, and 1 Queen model. Intruder-model availability is resolved under INT-001.
- **Plain rule:** The base-game component inventory contains `60 Action cards (10 per Character)` and `12 Exploration cards`.
- **Plain rule:** The provided state-marker supply includes `30 Noise markers` and `20 Secure tokens`.
- **Plain rule:** The base-game component inventory contains `1 Undiscovered Hibernatorium tile`.
- **Plain rule:** The provided gameplay-model supply includes `8 Drones` and `36 Adult models`.
- **Source:** Rulebook pp. 3–5, component-inventory captions at `RB-P03-004`, `RB-P03-013`, `RB-P04-031`, `RB-P05-003`, `RB-P05-009`, `RB-P05-015`, and `RB-P05-034`.
- **Boundary:** The `in 4 poses` and `in 6 poses` descriptors are not encoded as gameplay supply rules. Existing `OQ-010`, `SEM-Q-011`, `SEM-Q-017`, `SEM-Q-105`, and the other boundaries named in the table remain unchanged.
- **Malfunction-marker return:** A discarded Malfunction marker returns to its pool. **Source:** Rulebook p. 23, `MALFUNCTION MARKERS — discard destination`.
- **No-marker fallback:** If no Malfunction marker is available, place Fire in the affected component’s Room if possible. **Source:** Rulebook p. 23, `MALFUNCTION MARKERS LIMIT — substitute`.
- **Weapon example:** If a Weapon must Malfunction with no marker available, its Character’s Room receives Fire instead. **Source:** Rulebook p. 23, `MALFUNCTION MARKERS LIMIT — Weapon example`.

- **Boundary:** The fallback retains the source’s `if possible` boundary and does not select behavior for a component without a Room, a Room already containing Fire, or a compound effect after the substitution.

## FND-009 — Facility setup: tracks and system state

- **Source:** Rulebook pp. 8–9, “Game Setup.”
- **Track setup:**
  1. Place the Round marker on the first Round-track slot.
  2. Place the Lander token on Round-track slot 10.
  3. Place the Autodestruction token on its corresponding slot above the Round track.
  4. Place 1 Universal marker on the topmost Objective Choice space.
  5. Place 1 Universal marker on space 0 of the Queen's Hits track.
- **Section-border state:** Place all 3 Life Support tokens inactive-side-up on their corresponding Section-border slots. Place the Hibernatorium token inactive-side-up on its corresponding Section-border slot.
- **Anti-Aircraft state:** Shuffle both Anti-Aircraft tokens, then stack both face-down in Section B's Anti-Aircraft slot.
- **Secret check:** A Character may check the Anti-Aircraft tokens in secret using the Life Support Control “B” Room. **Source:** `RB-P37-045` / Rulebook p. 37, `ANTI-AIRCRAFT SYSTEM — secret check`.
- **Swap:** A Character using the Life Support Control “B” Room may swap the Anti-Aircraft tokens. **Source:** `RB-P37-046` / Rulebook p. 37, `ANTI-AIRCRAFT SYSTEM — swap`.
- **Information:** Characters may lie about the Anti-Aircraft status. **Source:** `RB-P37-048` / Rulebook p. 37, `ANTI-AIRCRAFT SYSTEM — lie`.
- **Visibility:** A Character cannot reveal the Anti-Aircraft token faces to other players. **Source:** `RB-P37-049` / Rulebook p. 37, `ANTI-AIRCRAFT SYSTEM — no showing`.
- **Nest state:** Place all 5 Egg tokens in Section C's Eggs space.
- **Plain rule:** Find the 3 Section border pieces and 3 Round track border pieces, connect them to each other and place them on the table.
- **Plain rule:** Until Characters reach the Hibernatorium, the Robot cannot be Activated.
- **Plain rule:** Place the drawn Robot card face-down on Section A’s Robot slot.
- **Source:** Rulebook p. 8, `A. SECTIONS SETUP` steps 1, 2 note, and 8 (`RB-P08-006`–`RB-P08-009`, `RB-P08-014`, and `RB-P08-023`).
- **Boundary:** Preserve `SEM-Q-012`, `SEM-Q-106`, and `SEM-Q-107`; no Robot external-effect policy, border orientation, endpoint assignment, or special-space geometry is added by these edits.

## FND-010 — Facility setup: map tiles and shared decks

- **Source:** Rulebook pp. 8–9, “Game Setup.”
- **Corridor supply:** Shuffle all Corridor tiles and keep their non-zero-value fronts hidden before each draw.
- **Deadly Mode values:** Some Corridors have a second, smaller Noise value. Use that smaller value only in Deadly Mode.
- **Initial Corridors:** Draw 3 random Corridor tiles one at a time, connect them to the Landing Zone, and place them non-zero-value-side-up.
- **Room-tile supply:** Sort all Room tiles by their backs into A, B, C, and `?` stacks. Shuffle each stack separately and place it face-down.
- **Exploration deck:** Shuffle the Exploration deck and place it face-down.
- **Intruder Attack and Event decks:** Shuffle the Intruder Attack deck and Event deck separately and place each face-down.
- **Queen Health deck:** Shuffle all Queen Health cards and place them numbers-side-down in the Queen Health-card space on the Section C border piece.
- **Other shared decks:** Shuffle the red, green, and yellow Item decks, Contamination deck, and Serious Wound deck separately. Place each face-down on the Facility's right side.
- **Plain rule:** If any of those Corridors have a Door slot, they should be placed with the slot on an entrance to the Landing Zone.
- **Source:** Rulebook p. 8, `A. SECTIONS SETUP — step 15` (`RB-P08-048`).
- **Boundary:** Preserve `SEM-Q-107` and `SEM-Q-108`; the edit records the Door-slot orientation requirement but does not choose an entrance, owner, or assignment order.

## FND-011 — Player setup and game opening

- **Source:** Rulebook pp. 10–11, “Objective Setup and Character Draft,” “Character Setup,” “Support Equipment Draft,” “Beginning of the Game,” and the assembled player-area illustration (`RB-P10-004`–`RB-P11-003`).

### Help cards, Objectives, and Mission Task

1. Select, shuffle, and deal one Help card per player from the numbers appropriate to the player count. Each player reveals their card; its number is used for the Character Draft and for specified Objectives. After setup, those Objective references are the only use of Help-card player numbers.
2. Separate Objective cards into Private and Mission decks and take the Mission Task deck. From each of those three decks, remove every card whose Number of Characters exceeds the participating Character count, then shuffle each deck separately.
3. Deal each player one random Private Objective and one random Mission Objective, face-down. Return all undealt Private and Mission Objective cards to the box unseen. Keep Objective cards hidden from other players until the End of the Game; players may discuss or lie about them without showing them.
4. Draw one random Mission Task and place it face-up in the Mission Task slot on the bottom Round-track tile. Return the other Mission Task cards to the box.

#### Player Help reference-face source occurrences

- **Plain rule:** The Player Help faces are reference aids; retain their printed wording as separate source occurrences without treating their player-number inventory or compressed phase grouping as the canonical setup or phase procedure.
- **Source:** TTS reference faces under `assets/tts-mod/extract/v2-dl/tree/cards/reference/`, with official phase authority retained in Rulebook pp. 12–15 and the existing `RT-001`, `RT-004`–`RT-005`, `RT-008`–`RT-012` records.
- **Source / authority boundary:** The rows below are separate TTS source occurrences. The current official rulebook's canonical phase procedure remains the four-phase sequence in `RT-001`, the Player Phase and Turn procedures in `RT-004`–`RT-005`, the Intruder Phase in `RT-008`, the Event Phase and Bag Development in `RT-009` and `RT-011`, and Cleanup in `RT-012`. The TTS grouping below is preserved verbatim as a reference-face source revision and must not replace or normalize those records.
- **Printed reference-face occurrences:**

| ID | Exact source occurrence and labels | Exact printed instruction text / paired side |
|---|---|---|
| `CARD-reference-reference-card-034_cards-card-01.png` | `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-034_cards/card-01.png`; `title: YOU ARE PLAYER`; printed number `2`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement` |
| `CARD-reference-reference-card-034_cards-card-03.png` | `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-034_cards/card-03.png`; `title: YOU ARE PLAYER`; printed number `4`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND` |
| `CARD-reference-reference-card-034_cards-card-04.png` | `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-034_cards/card-04.png`; `title: - HELP CARD -`; `typeLine: YOU ARE PLAYER`; printed number `5`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND` |
| `CARD-reference-reference-card-057.png` | `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-057.png`; `title: YOU ARE PLAYER`; `typeLine: – HELP CARD –`; printed number `9`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement` |
| `CARD-reference-reference-card-125.png` | `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-125.png`; `title: YOU ARE PLAYER`; `typeLine: - HELP CARD -`; no player number is printed in this extracted card record. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement` |
| `CARD-reference-reference-card-174.png` | `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-174.png`; `title: YOU ARE PLAYER`; `typeLine: - HELP CARD -`; printed number `7`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND` |
| `PHS-10` | `sourceUnitId: PH-FRONT-10`; `sourcePath: assets/tts-mod/extract/v2-dl/tree/cards/reference/card-125.png`; `sourceSha256: 83496243f03bbd82531fa0825c729f888a5e6051a4f46af9932846834c9756ea`; `playerNumber: 10`; `topLine: - HELP CARD -`; `playerLabel: YOU ARE PLAYER`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND`<br><br>Paired BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-153.jpg`; visibleText: `PASS`. |
| `PHS-2` | `sourceUnitId: PH-FRONT-02`; `sourcePath: assets/tts-mod/extract/v2-dl/tree/cards/reference/card-034_cards/card-01.png`; `sourceSha256: eb20a78be7d6dac4c6b90d726b4bd8947d0444488eaa968bfe598818e3486e39`; `sourceSheetCellIndex: 1`; `playerNumber: 2`; `topLine: - HELP CARD -`; `playerLabel: YOU ARE PLAYER`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND`<br><br>Paired BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-153.jpg`; visibleText: `PASS`. |
| `PHS-4` | `sourceUnitId: PH-FRONT-04`; `sourcePath: assets/tts-mod/extract/v2-dl/tree/cards/reference/card-034_cards/card-03.png`; `sourceSha256: 7e1f9c3f71030864e41c170d4faec022d7d4b154b896451833d154e95fed50c4`; `sourceSheetCellIndex: 3`; `playerNumber: 4`; `topLine: - HELP CARD -`; `playerLabel: YOU ARE PLAYER`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND`<br><br>Paired BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-153.jpg`; visibleText: `PASS`. |
| `PHS-6` | `sourceUnitId: PH-FRONT-06`; `sourcePath: assets/tts-mod/extract/v2-dl/tree/cards/reference/card-094.png`; `sourceSha256: 1a3767cbe3ae3743a989a9455051b3bd7b29acdf64f5239f74ba4069366482f9`; `playerNumber: 6`; `topLine: - HELP CARD -`; `playerLabel: YOU ARE PLAYER`; exact TTS GUID/CardID retained in source extraction. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND`<br><br>Paired BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-153.jpg`; visibleText: `PASS`. |
| `PHS-7` | `sourceUnitId: PH-FRONT-07`; `sourcePath: assets/tts-mod/extract/v2-dl/tree/cards/reference/card-174.png`; `sourceSha256: 5451059f4d4ae95917b60a24cc2955e4ea74c77742374ea0b080c6d0d251cd76`; `playerNumber: 7`; `topLine: - HELP CARD -`; `playerLabel: YOU ARE PLAYER`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND`<br><br>Paired BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-153.jpg`; visibleText: `PASS`. |
| `PHS-9` | `sourceUnitId: PH-FRONT-09`; `sourcePath: assets/tts-mod/extract/v2-dl/tree/cards/reference/card-057.png`; `sourceSha256: 0303f0ca7c1b841d07c5bb4b46d1260c77bb5aaf32f668b62482ba5431a4385c`; `playerNumber: 9`; `topLine: - HELP CARD -`; `playerLabel: YOU ARE PLAYER`. | `PLAYER PHASE`<br>`Players take Turns in Order`<br>`– 2 Actions each Turn,`<br>`until all Players have passed.`<br><br>`EVENT PHASE`<br>`1) Escape`<br>`2) Fire Damage`<br>`3) Intruder Attacks`<br>`4) Event Card`<br>`5) Bag Development`<br><br>`CLEANUP PHASE`<br>`6) First Player Change`<br>`7) Drawing Cards`<br>`8) Time Advancement`<br><br>`END OF ROUND`<br><br>Paired BackURL: `assets/tts-mod/extract/v2-dl/tree/cards/reference/card-153.jpg`; visibleText: `PASS`. |

### Character Draft and Character setup

1. Shuffle all Character Draft cards. Beginning with Player 1 and continuing in ascending player-number order, deal the drafting player two cards secretly; that player chooses one as their Character and reveals it, then shuffles the unchosen card back into the deck unseen.
2. Place the chosen Character tile in a universal Character board. Put one Universal marker in the leftmost Health-track slot and set the Oxygen counter to its maximum value of 7.
3. Place the chosen Character model in the Landing Zone.
4. Shuffle that Character's Action cards and place the deck face-down to the left of the Character board. The Contractor has 5 Action cards marked `Contractor` and 5 marked `Contractor: Consultant`; this label distinction is used only by Expansions and is ignored in the base game.
5. Place the Character Item according to its Item class: place Armor in the Heavily Injured section of the Health track. Put one full-side-up Ammo token on every Ammo slot on that starting Item.

### Support Equipment and starting Tactical Gear

1. Every Character except the Contractor participates; the Contractor already starts with two Character Items.
2. Shuffle the Support Equipment deck, draw seven cards, and reveal them. Starting with the highest-numbered participating player and continuing in descending player-number order, each player chooses one card and places it according to its Item class; place chosen Armor in the Heavily Injured section of the Health track. Fill its Tactical Gear slots with compatible tokens, then remove the unchosen revealed cards from the game.
3. Each player chooses exactly four Tactical Gear tokens in any combination and places them in their Tactical Belt. This choice may be simultaneous; if simultaneous choice is unsuitable, resolve it in descending player-number order. Ammo enters full-side-up.

### Begin play

1. Each player draws five cards from their Action deck into hand.
2. Give the Starting Player token to Player 1; that player takes the first Turn.

- **Plain rule:** The Support Equipment deck may be used during the game.
- **Source:** Rulebook p. 10, `SUPPORT EQUIPMENT DRAFT — step 5` (`RB-P10-063`).
- **Boundary:** Preserve `SEM-Q-080`; no later-use timing, access owner, exhaustion, or selection procedure is invented.

## FND-012 — Facility spaces and printed map semantics

- **Source:** Rulebook pp. 19–21, “Map,” “Rooms,” “Nest,” and “Corridors” (`RB-P19-001`–`RB-P21-040`).
- **Facility and Sections:** The Facility is divided into Sections A, B, and C. Every Room occupies one Section, while a Corridor straddling a Section boundary belongs to both adjacent Sections. The right and bottom edges remain Facility boundaries even without physical border pieces.
- **Occupancy:** Characters occupy Rooms, never Corridors. Intruders may occupy Rooms or Corridors. Characters begin in the Landing Zone.
- **Initial exploration state:** At the start of the game, most of the Facility is unexplored; Rooms and Corridors are added as Characters explore.
- **Room types:** A-, B-, and C-marked Rooms are Section Rooms, belong to the matching Section, and always appear in a game. `?`-marked Rooms are random and a particular one may not appear.
- **Computer icon:** A Room's Computer icon indicates server access. It has no standalone effect, but Actions and other effects may refer to it.
- **Hibernatorium:** The Hibernatorium can provide safety to multiple Characters. It begins Undiscovered and inactive and cannot be Used in that state; see INT-009 for discovery, activation, and hibernation resolution.
- **Nest and Eggs space:** The Nest is a Section C Room containing Intruder Eggs. Section C's Eggs space is an extension of the Nest Room: a Character in the Nest is considered to share a Room with those Eggs and may interact with them as the Nest rules permit. Eggs are Heavy Items under ITM-002.
- **Reactor:** The Reactor can completely shut down Facility power. It turns off all Life Support Systems, Autodestruction, and Anti-Aircraft and prevents each from being turned on again.
- **Empty Corridor:** A Corridor is Empty exactly when it contains no Intruders. A Noise marker does not prevent an otherwise Intruder-free Corridor from being Empty.
- **Unexplored Corridor:** A Corridor connected to exactly one Room is Unexplored.
- **Facility boundary pieces:** The Section border pieces and the Round track border pieces create the borders of the Facility. No Room and no Corridor can ever be placed on those pieces. **Source:** Rulebook p. 19, `FACILITY SIZE — borders` and `FACILITY SIZE — forbidden pieces`.
- **Life Support locations:** Changing the status of those systems is possible in Life Support Control Rooms which can be found in every Section. **Source:** Rulebook p. 19, `SECTIONS — Life Support control`.
- **Section A:** Section A is an Entrance Section – where you start your mission and most likely end it. **Source:** Rulebook p. 19, `SECTION A — role`.
- **Landing Zone:** Characters can restock supplies at the Landing Zone. **Source:** Rulebook p. 19, `SECTION A — Landing Zone supplies` (`a place where Characters can restock their supplies.`).
- **Section B:** Section B is the middle Section. **Source:** Rulebook p. 19, `SECTION B — role`.
- **Map slots:** The illustration shows all slots in which Rooms and Corridors may appear. Section A occupies the left zone, Section B the middle zone, and Section C the right zone of the Facility layout. **Source:** Rulebook p. 19, `SECTIONS IN THE FACILITY — diagram coverage` and `SECTIONS IN THE FACILITY — layout`.
- **Reinforced Corridors:** A Character may Reinforce only an empty Corridor. When Reinforcing a Corridor, discard its Noise marker if present, then flip a Reinforced Corridor tile to its back. A Corridor connected to the Hibernatorium cannot be Reinforced. **Source:** Rulebook p. 21, `REINFORCED CORRIDOR — eligibility`, `REINFORCED CORRIDOR — discard Noise`, `REINFORCED CORRIDOR — flip`, and `REINFORCED CORRIDOR — Hibernatorium exception`.
- **Reinforced path check (Objective use):** When an Objective or Mission Task requires a continuous path of Reinforced Corridors between two named locations, the check considers only whether each Corridor along a connected route is Reinforced; ignore Closed Doors and Intruders along the route — they are irrelevant, only Reinforcement counts. **Source:** Official Objective Help Sheet unit `P1-MT-THE-SUPPLY-ROUTE` associated note (`OBJ-16`). Which endpoint the Objective names (Life Support Control C or Server Room) is a preserved source-variant difference recorded in INT-011.
- **Corridor identity:** A Corridor ID begins with that tile front’s standard Noise value. **Source:** Rulebook p. 21, `Corridor anatomy D — prefix`.
- **Room marker limits:** A Room can contain at most 1 Fire marker and at most 1 Malfunction marker. **Source:** Rulebook p. 23, `FIRE MARKERS — Room cap` and `MALFUNCTION MARKERS 1. ON ROOMS — cap`.

- **Boundary:** The map-slot and Corridor-ID statements describe source identity/layout and do not create an unstated placement order. Existing boundary bullets remain; these additions make the border-piece, marker-cap, and Reinforced-Corridor assertions explicit.
- **Plain rule:** When Fire is to be spread through an Open Corridor, do not place a Fire marker.
- **Plain rule:** If the Nest’s Eggs area is empty, the Nest is destroyed.
- **Plain rule:** A Fire marker in the Nest does not by itself make the Nest destroyed; if Eggs remain when the game ends, the Nest is not considered destroyed.
- **Source:** FAQ v1.2 p. 2, `FQ-P02-U09` and `FQ-P02-U20`; Rulebook p. 35, `RB-P35-031`.
- **Boundary:** Preserve `OQ-009`; these edits do not define an Undiscovered-Nest procedure and do not treat Fire alone as equivalent to an empty Eggs area.
- **Data token:** “Characters can gain a Data token using the Server Room (Section B). Once gained by a Character, a Data token cannot be lost or traded.” **Source:** Official Objective Help Sheet `P2-GT-04`.
- **Nest destruction:** “The Nest is Destroyed when the Facility is Destroyed or when there are no more Eggs as a result of Characters taking or Destroying them on the special space on the Section “C” border piece.” **Source:** Official Objective Help Sheet `P2-GT-07` and the separately retained page-1 occurrence `P1-GT-07`.

IDs satisfied: `OBJ-25`, `OBJ-28`, `OBJ-6`.
