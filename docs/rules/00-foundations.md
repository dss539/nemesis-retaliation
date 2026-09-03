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
- **Nest state:** Place all 5 Egg tokens in Section C's Eggs space.

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

## FND-011 — Player setup and game opening

- **Source:** Rulebook pp. 10–11, “Objective Setup and Character Draft,” “Character Setup,” “Support Equipment Draft,” “Beginning of the Game,” and the assembled player-area illustration (`RB-P10-004`–`RB-P11-003`).

### Help cards, Objectives, and Mission Task

1. Select, shuffle, and deal one Help card per player from the numbers appropriate to the player count. Each player reveals their card; its number is used for the Character Draft and for specified Objectives. After setup, those Objective references are the only use of Help-card player numbers.
2. Separate Objective cards into Private and Mission decks and take the Mission Task deck. From each of those three decks, remove every card whose Number of Characters exceeds the participating Character count, then shuffle each deck separately.
3. Deal each player one random Private Objective and one random Mission Objective, face-down. Return all undealt Private and Mission Objective cards to the box unseen. Keep Objective cards hidden from other players until the End of the Game; players may discuss or lie about them without showing them.
4. Draw one random Mission Task and place it face-up in the Mission Task slot on the bottom Round-track tile. Return the other Mission Task cards to the box.

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
