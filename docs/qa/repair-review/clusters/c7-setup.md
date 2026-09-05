# c7-setup — Repair-mapping proposal

This is a proposal only. It maps each canonical fragment to its concise-corpus repair home; it does not apply any repair.

| ID | Source assertion (short verbatim quote) | Target record | Proposed edit | Boundary / open question preserved | Notes |
|---|---|---|---|---|---|
| `RB-P03-004.fact` | `60 Action cards (10 per Character)` | `FND-008 — Finite card/deck supplies` | Add the exact supply entry: `60 Action cards (10 per Character).` Source: Rulebook p. 3, `STANDARD-SIZED CARDS — Action cards parenthetical`. | `OQ-010` remains the boundary for card-face/source-variant reconciliation; this quantity does not merge licensed-digital, TTS, or other source occurrences. | Gameplay-facing: the finite Action-card supply and per-Character deck size affect setup, draws, and exhaustion. |
| `RB-P03-013.fact` | `12 Exploration cards` | `FND-008 — Finite card/deck supplies` | Add the exact supply entry: `12 Exploration cards.` Source: Rulebook p. 3, `STANDARD-SIZED CARDS — Exploration cards caption`. | `SEM-Q-011` remains open for multi-slot Corridor draws and finite-component assignment; the deck count does not choose an assignment order. | Gameplay-facing: the finite Exploration-card supply affects exploration draws and reshuffling. |
| `RB-P04-031.fact` | `8 Drones in 4 poses` | `FND-008 — Other gameplay models` | Add the exact gameplay-supply entry: `8 Drones.` Source: Rulebook p. 4, `STANDEES/MODELS — Drones caption`. Do not encode the pose count as a rule. | `SEM-Q-105` remains open for Adult/Drone allocation under model shortage; this entry establishes supply only. | The 8-model limit is gameplay-facing. The separate `4 poses` descriptor is packaging/artwork detail; see Flags. |
| `RB-P05-003.fact` | `30 Noise markers` | `FND-008 — State-marker supplies` | Add the exact supply entry: `30 Noise markers.` Source: Rulebook p. 5, `MARKERS AND TOKENS — Noise markers caption`. | `SEM-Q-011` remains open for finite-component allocation when several depicted placements compete for available components; the count does not select a placement order. | Gameplay-facing: Noise markers represent Corridor state and are a finite supply. |
| `RB-P05-009.fact` | `20 Secure tokens` | `FND-008 — State-marker supplies` | Add the exact supply entry: `20 Secure tokens.` Source: Rulebook p. 5, `MARKERS AND TOKENS — Secure tokens caption`. | `OQ-007` and `SEM-Q-017` remain open; the count does not resolve simultaneous entry, shortage, partial placement, or exact-two placement behavior. | Gameplay-facing: Secure-token exhaustion changes attack prevention and related actions. |
| `RB-P05-015.fact` | `1 Undiscovered Hibernatorium tile` | `FND-008 — Special map components` | Add the exact supply entry: `1 Undiscovered Hibernatorium tile.` Source: Rulebook p. 5, `MARKERS AND TOKENS — Undiscovered Hibernatorium tile caption`. | `SEM-Q-106` and `SEM-Q-107` remain open for border orientation and special-space connector mapping; the unique tile count does not resolve map geometry. | Gameplay-facing: the single tile establishes the unique hidden Hibernatorium state; it is not an interchangeable packaging component. |
| `RB-P05-034.fact` | `36 Adults in 6 poses` | `FND-008 — Other gameplay models` | Add the exact gameplay-supply entry: `36 Adult models.` Source: Rulebook p. 5, `STANDEES/MODELS — Adults caption`. Do not encode the pose count as a rule. | `SEM-Q-105` remains open for Adult/Drone allocation under model shortage; this entry establishes supply only. | The 36-model limit is gameplay-facing. The separate `6 poses` descriptor is packaging/artwork detail; see Flags. |
| `RB-P08-006.rule` | `Find the 3 Section border pieces and 3 Round track border pieces` | `FND-009 — Board-frame assembly` | Add the Section-border clause to the setup step: `Find the 3 Section border pieces ...` within the exact combined instruction `Find the 3 Section border pieces and 3 Round track border pieces, connect them to each other and place them on the table.` Source: Rulebook p. 8, `A. SECTIONS SETUP — step 1`. | `SEM-Q-106` remains open for border-piece orientation and the fixed Landing Zone/Hibernatorium edge crosswalk; finding the pieces does not resolve that geometry. | Gameplay-facing: these pieces establish the Facility/track board used by play. |
| `RB-P08-007.rule` | `Find the 3 Section border pieces and 3 Round track border pieces` | `FND-009 — Board-frame assembly` | Add the Round-track clause to the exact combined instruction: `Find the 3 Section border pieces and 3 Round track border pieces, connect them to each other and place them on the table.` Source: Rulebook p. 8, `A. SECTIONS SETUP — step 1`. | `SEM-Q-106` remains open for border-piece orientation and the fixed Landing Zone/Hibernatorium edge crosswalk; finding the pieces does not resolve that geometry. | Gameplay-facing: the three Round-track border pieces define the physical round-track assembly. |
| `RB-P08-008.rule` | `connect them to each other and place them on the table.` | `FND-009 — Board-frame assembly` | Add the exact connection clause: `connect them to each other`. Source: Rulebook p. 8, `A. SECTIONS SETUP — step 1`. | `SEM-Q-106` remains open for orientation and `SEM-Q-107` for special-space connector assignment; connecting the pieces does not choose those mappings. | Gameplay-facing: disconnected border pieces would not establish the Facility/track topology. |
| `RB-P08-009.rule` | `connect them to each other and place them on the table.` | `FND-009 — Board-frame assembly` | Add the exact placement continuation: `and place them on the table.` Source: Rulebook p. 8, `A. SECTIONS SETUP — step 1`. | Preserve `SEM-Q-106` and `SEM-Q-107`; the placement instruction does not settle orientation or endpoint assignment. The literal table/surface choice is not a game-state rule. | The connected board assembly is gameplay-facing; the literal `on the table` wording is packaging/playing-surface detail and is flagged below. |
| `RB-P08-014.rule` | `Until then, ... the Robot cannot be Activated.` | `FND-009 — Hibernatorium/Robot initial state` | Add the exact setup gate: `Until Characters reach the Hibernatorium, the Robot cannot be Activated.` Source: Rulebook p. 8, `A. SECTIONS SETUP — step 2 note`. | Preserve `SEM-Q-012`: this settles the pre-reach Activation prohibition only; it does not decide which other effects may target or mention the face-down Robot. | Gameplay-facing: it changes the legal availability of the Activate Robot Action before Hibernatorium reach. |
| `RB-P08-023.rule` | `place it face down on the Robot slot of the Section “A” border piece.` | `FND-009 — Robot-card setup` | Add the exact placement sentence: `Place the drawn Robot card face-down on Section A’s Robot slot.` Source: Rulebook p. 8, `A. SECTIONS SETUP — step 8`. | Preserve `SEM-Q-012`: face-down placement does not settle inspection or other non-Activation effects before the Hibernatorium is reached. | Gameplay-facing: the hidden card location is part of Robot setup and later reveal/Activation state. |
| `RB-P08-048.rule` | `If any of those Corridors have a Door slot, they should be placed with the slot on an entrance to the Landing Zone.` | `FND-010 — Initial Corridors / Door-slot orientation` | Add the exact orientation sentence after the initial Corridor draw: `If any of those Corridors have a Door slot, they should be placed with the slot on an entrance to the Landing Zone.` Source: Rulebook p. 8, `A. SECTIONS SETUP — step 15`. | Preserve `SEM-Q-107` and `SEM-Q-108`; `an entrance` does not identify a single entrance, decision owner, or deterministic assignment among multiple drawn Corridors. | Gameplay-facing: Door-slot orientation changes the initial map connection. The unresolved entrance-selection boundary is flagged below. |
| `RB-P10-063.fact` | `They may be used during the game.` | `FND-011 — Support Equipment and starting Tactical Gear` | Add the explicit corpus sentence: `The Support Equipment deck may be used during the game.` Source: Rulebook p. 10, `SUPPORT EQUIPMENT DRAFT — step 5`. | Preserve `SEM-Q-080`: this records availability only and does not define who may access the deck, when, how exhaustion works, or what later-use procedure applies. | Gameplay-facing: later availability of Support Equipment can change Item access; the pronoun’s operational scope remains bounded by `SEM-Q-080`. |
| `RB-P16-027.rule` | `Then, discard all chosen tokens` | `ACT-TACTICAL-001 — Use Tactical Gear / discard procedure` | Add the exact source sentence, including its source-stated exception: `Then, discard all chosen tokens (apart from Ammo tokens, which are moved to Weapons as a part of their effect).` Source: Rulebook p. 16, `USE ANY TACTICAL GEAR ACTION — discard`. | No additional open question is selected. Preserve the existing `ITM-005` Ammo-token rule, including that an Ammo token already loaded into a Weapon may not be moved. | Gameplay-facing: discard versus transfer determines Tactical Gear inventory after the Action. |
| `RB-P16-029.rule` | `You may also move any number of your tokens between your Tactical slots.` | `ACT-TACTICAL-001 — Use Tactical Gear / slot rearrangement` | Add the exact source sentence: `You may also move any number of your tokens between your Tactical slots.` Source: Rulebook p. 16, `USE ANY TACTICAL GEAR ACTION — rearrangement`. | No additional open question is selected. Preserve `ITM-005` slot-color compatibility and the loaded-Ammo restriction; this sentence does not authorize moving an Ammo token already loaded into a Weapon. | Gameplay-facing: slot rearrangement changes which Tactical Gear effects and storage spaces are available. |
| `RB-P40-066.fact` | `The related token can be found on Section “B” border piece.` | `icon-glossary.md — Map-Related Icons > Systems and Facility Tokens > hibernatoriumInactive` | Extend the `hibernatoriumInactive` glossary entry with the exact location sentence: `The related token can be found on Section “B” border piece.` Source: Rulebook p. 40, `ICON GLOSSARY — Hibernatorium token location`. | Preserve `SEM-Q-106` and `SEM-Q-107`; the token’s source location does not resolve border orientation or the full special-space connector crosswalk. | Gameplay-facing setup location; do not reinterpret this location note as a new Hibernatorium effect. |
| `RB-P40-073.fact` | `Medpack Tactical Gear token` | `icon-glossary.md — Tactical Gear Tokens > medpackToken` | Replace the current `medpackToken` description `Green Medpack Tactical Gear token` with: `The green medical-cross glyph denotes a Medpack Tactical Gear token (assets/icons/tactical-gear/medpack-token.png).` Source: Rulebook p. 40, `ICON GLOSSARY — Medpack Gear`. | No open question is selected; this is an identity mapping only and does not infer a healing amount or any other Medpack effect. | Gameplay-facing identity: the glyph must dispatch to the Medpack token, while its effect remains governed by the relevant Action/rule record. |

## Consolidated edits by target record

### `FND-008 — Gameplay-facing physical supplies`

- **Plain rule:** The base-game component inventory contains `60 Action cards (10 per Character)` and `12 Exploration cards`.
- **Plain rule:** The provided state-marker supply includes `30 Noise markers` and `20 Secure tokens`.
- **Plain rule:** The base-game component inventory contains `1 Undiscovered Hibernatorium tile`.
- **Plain rule:** The provided gameplay-model supply includes `8 Drones` and `36 Adult models`.
- **Source:** Rulebook pp. 3–5, component-inventory captions at `RB-P03-004`, `RB-P03-013`, `RB-P04-031`, `RB-P05-003`, `RB-P05-009`, `RB-P05-015`, and `RB-P05-034`.
- **Boundary:** The `in 4 poses` and `in 6 poses` descriptors are not encoded as gameplay supply rules. Existing `OQ-010`, `SEM-Q-011`, `SEM-Q-017`, `SEM-Q-105`, and the other boundaries named in the table remain unchanged.
- **ID satisfied:** `RB-P03-004.fact`
- **ID satisfied:** `RB-P03-013.fact`
- **ID satisfied:** `RB-P04-031.fact`
- **ID satisfied:** `RB-P05-003.fact`
- **ID satisfied:** `RB-P05-009.fact`
- **ID satisfied:** `RB-P05-015.fact`
- **ID satisfied:** `RB-P05-034.fact`

### `FND-009 — Facility setup: tracks and system state`

- **Plain rule:** Find the 3 Section border pieces and 3 Round track border pieces, connect them to each other and place them on the table.
- **Plain rule:** Until Characters reach the Hibernatorium, the Robot cannot be Activated.
- **Plain rule:** Place the drawn Robot card face-down on Section A’s Robot slot.
- **Source:** Rulebook p. 8, `A. SECTIONS SETUP` steps 1, 2 note, and 8 (`RB-P08-006`–`RB-P08-009`, `RB-P08-014`, and `RB-P08-023`).
- **Boundary:** Preserve `SEM-Q-012`, `SEM-Q-106`, and `SEM-Q-107`; no Robot external-effect policy, border orientation, endpoint assignment, or special-space geometry is added by these edits.
- **ID satisfied:** `RB-P08-006.rule`
- **ID satisfied:** `RB-P08-007.rule`
- **ID satisfied:** `RB-P08-008.rule`
- **ID satisfied:** `RB-P08-009.rule`
- **ID satisfied:** `RB-P08-014.rule`
- **ID satisfied:** `RB-P08-023.rule`

### `FND-010 — Facility setup: map tiles and shared decks`

- **Plain rule:** If any of those Corridors have a Door slot, they should be placed with the slot on an entrance to the Landing Zone.
- **Source:** Rulebook p. 8, `A. SECTIONS SETUP — step 15` (`RB-P08-048`).
- **Boundary:** Preserve `SEM-Q-107` and `SEM-Q-108`; the edit records the Door-slot orientation requirement but does not choose an entrance, owner, or assignment order.
- **ID satisfied:** `RB-P08-048.rule`

### `FND-011 — Player setup and game opening`

- **Plain rule:** The Support Equipment deck may be used during the game.
- **Source:** Rulebook p. 10, `SUPPORT EQUIPMENT DRAFT — step 5` (`RB-P10-063`).
- **Boundary:** Preserve `SEM-Q-080`; no later-use timing, access owner, exhaustion, or selection procedure is invented.
- **ID satisfied:** `RB-P10-063.fact`

### `ACT-TACTICAL-001 — Use Tactical Gear`

- **Plain rule:** Then, discard all chosen tokens (apart from Ammo tokens, which are moved to Weapons as a part of their effect). You may also move any number of your tokens between your Tactical slots.
- **Source:** Rulebook p. 16, `USE ANY TACTICAL GEAR ACTION` discard and rearrangement clauses (`RB-P16-027` and `RB-P16-029`).
- **Boundary:** Preserve `ITM-005` slot compatibility, the loaded-Ammo restriction, and the source-stated Ammo transfer exception.
- **ID satisfied:** `RB-P16-027.rule`
- **ID satisfied:** `RB-P16-029.rule`

### `icon-glossary.md — Map-Related Icons / Systems and Facility Tokens`

- **Plain rule:** The related token can be found on Section “B” border piece.
- **Source:** Rulebook p. 40, `ICON GLOSSARY — Hibernatorium token location` (`RB-P40-066`).
- **Boundary:** Preserve `SEM-Q-106` and `SEM-Q-107`; this is a source-location note, not a border-orientation or connector rule.
- **ID satisfied:** `RB-P40-066.fact`

### `icon-glossary.md — Tactical Gear Tokens / medpackToken`

- **Plain rule:** The green medical-cross glyph denotes a Medpack Tactical Gear token (`assets/icons/tactical-gear/medpack-token.png`).
- **Source:** Rulebook p. 40, `ICON GLOSSARY — Medpack Gear` (`RB-P40-073`).
- **Boundary:** Identity only; no healing amount or other Medpack semantics are inferred.
- **ID satisfied:** `RB-P40-073.fact`

## Flags

- `RB-P04-031.fact` — **Packaging-only subfact:** `in 4 poses` fails the gameplay-consequence test: changing the number of poses does not change legal game state, while the 8-Drones supply count does. The proposal retains only the gameplay-facing count.
- `RB-P05-034.fact` — **Packaging-only subfact:** `in 6 poses` fails the gameplay-consequence test: pose variety does not change legal game state, while the 36-Adult-model supply count does. The proposal retains only the gameplay-facing count.
- `RB-P08-009.rule` — **Packaging-only wording:** literal placement `on the table` does not change game state when the playing surface changes. The connected board assembly is gameplay-facing and retained; the surface wording must not be treated as a separate mechanic.
- `RB-P08-048.rule` — **Ambiguous setup choice:** `an entrance to the Landing Zone` does not identify which entrance, who chooses, or how multiple Door-bearing Corridors are assigned. Preserve `SEM-Q-108` (and the related `SEM-Q-107`) without selecting a default.
- `RB-P10-063.fact` — **Under-specified later use:** the source establishes that the Support Equipment deck may be used during the game but does not specify access, timing, exhaustion, or selection. Preserve `SEM-Q-080`; do not expand the proposed sentence into a procedure.

## Closure

IDs assigned: 19. IDs in table: 19. IDs in consolidated blocks: 19.