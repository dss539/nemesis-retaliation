# c3-facility — repair-mapping proposal

This is a proposal only. No repair is applied to `docs/rules/` or to the source evidence.

| ID | Source assertion (short verbatim quote) | Target record | Proposed edit | Boundary / open question preserved | Notes |
|---|---|---|---|---|---|
| CARD-game-exploration-game-exploration-025.png | `body: Place A/B/C Room depending on your Section.`<br>`[character] [malfunction]`<br>`[noise]`<br>`Reminder: Place 1 [secure] if you are Moving with [secure].`<br>`Make a Noise roll.` | `ACT-EXPLORE-001` — Exploration-card source table | Add the exact source-occurrence row shown in the consolidated block; retain the bracketed tokens literally. | `SEM-Q-002` remains open on whether this Entrance-effect Noise roll is additional to the universal post-Movement Noise requirement. No token meaning is inferred. | Source variant/card face: `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-025.png`. |
| CARD-game-exploration-game-exploration-062.png | `body: Place A/B/C Room depending on your Section.`<br>`[character]`<br>`[noise]`<br>`Entrance Effect: Place 3 Adults in the Corridor you have just passed through. Then, make a Noise roll.` | `ACT-EXPLORE-001` — Exploration-card source table | Add the exact source-occurrence row shown in the consolidated block; retain the bracketed tokens and the separate Entrance Effect. | `SEM-Q-002` remains open on Noise-roll multiplicity; the Entrance Effect does not settle the general post-Movement wording. | Source variant/card face: `assets/tts-mod/extract/v2-dl/tree/cards/game-exploration-062.png`. |
| CARD-game-exploration-game-exploration-107.png | `body: Place A/B/C Room depending on your Section.`<br>`[noise]`<br>`[character]`<br>`[noise]`<br>`Entrance Effect: Place 2 Adults in the Corridor you have just passed through. Then, make a Noise roll.` | `ACT-EXPLORE-001` — Exploration-card source table | Add the exact source-occurrence row shown in the consolidated block; retain order, quantities, bracketed tokens, and the separate Entrance Effect. | `SEM-Q-002` remains open on Noise-roll multiplicity; no canonical card wording is substituted. | Source variant/card face: `assets/tts-mod/extract/v2-dl/tree/cards/game-exploration-107.png`. |
| RB-P19-006.fact | `The Section border pieces and the Round track border pieces create the borders of the Facility.` | `FND-012` — Facility boundary bullet | Add: `The Section border pieces and the Round track border pieces create the borders of the Facility.` | The existing FND-012 boundary statement covers the right and bottom edges but not this border-piece assertion; coordinator re-check is required. | Rulebook p. 19, `FACILITY SIZE — borders`. |
| RB-P19-007.rule | `No Room and no Corridor can ever be placed on those pieces` | `FND-012` — Facility boundary bullet | Add: `No Room and no Corridor can ever be placed on those pieces.` | The referent is the border pieces in the preceding sentence; do not broaden it to other blocked spaces. | Rulebook p. 19, `FACILITY SIZE — forbidden pieces`. |
| RB-P19-012.rule | `Changing the status of those systems is possible in Life Support Control Rooms which can be found in every Section.` | `FND-012` — Section facilities / Life Support bullet | Add: `Changing the status of those systems is possible in Life Support Control Rooms which can be found in every Section.` | The sentence records where the change is possible; it does not define the exact Room Action, range, or token face. | Rulebook p. 19, `SECTIONS — Life Support control`. |
| RB-P19-016.fact | `Section A is an Entrance Section – where you start your mission and most likely end it.` | `FND-012` — Section roles bullet | Add: `Section A is an Entrance Section – where you start your mission and most likely end it.` | “Most likely end it” is retained as source wording and is not converted into an endgame condition. | Rulebook p. 19, `SECTION A — role`. |
| RB-P19-018.fact | `a place where Characters can restock their supplies.` | `FND-012` — Landing Zone bullet | Add: `Characters can restock supplies at the Landing Zone.` Cite the source fragment verbatim alongside the new sentence. | The fragment does not specify which supplies or a cost; no inventory or replenishment procedure is invented. | Rulebook p. 19, `SECTION A — Landing Zone supplies`. |
| RB-P19-020.fact | `Drilling Room – A Room which allows drilling new Corridors.` | `ACT-ROOM-001` — named Room statements | Add: `The Drilling Room permits new Corridors to be drilled.` | `SEM-Q-005` remains open on who selects a legal new-Corridor endpoint when more than one is possible. | Rulebook p. 19, `SECTION A — Drilling Room`. |
| RB-P19-022.fact | `It also allows putting out fires.` | `ACT-ROOM-001` — named Room statements | Add: `Life Support Control A can remove Fire.` | The exact range is stated on the Room tile/Help Sheet, not in this sentence; do not infer a range from this fragment. | Rulebook p. 19, `SECTION A — Life Support Control A fire`. |
| RB-P19-023.fact | `Surgery Room – Provides the easiest way to discard Serious Wounds` | `ACT-ROOM-001` — named Room statements | Add: `The Surgery Room can discard Serious Wounds.` | “Easiest” is retained as source commentary; no comparative cost or priority is added. | Rulebook p. 19, `SECTION A — Surgery Room`. |
| RB-P19-024.fact | `and even a Larva Infection if it were to occur.` | `ACT-ROOM-001` — named Room statements | Add: `The Surgery Room can remove a Larva Infection.` | Keep this rulebook assertion separate from the exact Room Help effect that removes a Larva and scans Contaminations. | Rulebook p. 19, `SECTION A — Surgery Room infection`. |
| RB-P19-025.fact | `Section B is the middle Section` | `FND-012` — Section roles bullet | Add: `Section B is the middle Section.` | The statement is positional; it does not prescribe a digital coordinate system. | Rulebook p. 19, `SECTION B — role`. |
| RB-P19-031.rule | `it can be turned on in Life Support Control “C”.` | `INT-009` — Hibernatorium activation | Add: `Life Support Control C can turn on the Hibernatorium.` | This records the activation capability only; active/inactive and Undiscovered-state handling remains in INT-009. | Rulebook p. 19, `SECTION B — Hibernatorium activation`. |
| RB-P19-033.fact | `Life Support Control “B” – Turns on/off Life Support Systems in Section B.` | `ACT-ROOM-001` — named Room statements | Add: `Life Support Control B changes Section B’s Life Support state.` | Do not collapse this Section B occurrence into the distinct Section A or C source wording. | Rulebook p. 19, `SECTION B — Life Support Control B`. |
| RB-P19-034.fact | `You can also check and change the status of Anti-Aircraft systems here.` | `ACT-ROOM-001` — named Room statements | Add: `Life Support Control B can inspect and change the Anti-Aircraft system.` | “Here” is resolved only by the source anchor to Life Support Control B; no remote range is inferred. | Rulebook p. 19, `SECTION B — Anti-Aircraft`. |
| RB-P19-035.fact | `Server Room – Its most important function is allowing you to gather a Data token required for some Objectives.` | `ACT-ROOM-001` — named Room statements | Add: `The Server Room can provide a Data token used by some Objectives.` | The fragment does not define a Data-token limit or an Objective-specific prerequisite. | Rulebook p. 19, `SECTION B — Server Room`. |
| RB-P19-038.fact | `You can also turn on the Hibernatorium here.` | `INT-009` — Hibernatorium activation | Add: `Life Support Control C can activate the Hibernatorium.` | Keep this occurrence separate from the distinct Rulebook p. 19 activation sentence; no additional activation timing is inferred. | Rulebook p. 19, `SECTION C — Hibernatorium control`. |
| RB-P19-045.fact | `but only for 1 person.` | `INT-009` — Escape Shuttle capacity | Add: `The Escape Shuttle can carry only 1 Character.` | The capacity assertion does not by itself define the Noise-roll gate or the shuttle’s one-use lifecycle. | Rulebook p. 19, `SECTION C — Escape Shuttle capacity`. |
| RB-P19-046.fact | `This illustration shows all slots in which Rooms and Corridors may appear.` | `FND-012` — map-layout bullet | Add: `The illustration shows all slots in which Rooms and Corridors may appear.` | This records the illustrated slot inventory; it does not invent a draw order or placement algorithm. | Rulebook p. 19, `SECTIONS IN THE FACILITY — diagram coverage`. |
| RB-P19-047.fact | `SECTION A / SECTION B / SECTION C` | `FND-012` — map-layout bullet | Add: `Section A occupies the left zone, Section B the middle zone, and Section C the right zone of the Facility layout.` | The layout statement is preserved as source-backed orientation, not as a replacement for the physical slot diagram. | Rulebook p. 19, `SECTIONS IN THE FACILITY — layout`. |
| RB-P20-018.fact | `Other Icons – Rooms may also feature some other icons, showing special rules` | `ACT-ROOM-001` — Room-tile special-icon rules | Add: `Rooms may feature other icons showing special rules.` | “Other” remains relative to the Room-tile anatomy passage; the icon inventory is not expanded here. | Rulebook p. 20, `Room-tile anatomy F`. |
| RB-P20-019.rule | `Such Rooms are never Secured` | `ACT-ROOM-001` — Room-tile special-icon rules | Add: `A Room with the crossed-Secure special icon is never Secured.` | Preserve the source glyph association; do not generalize the restriction to every Room without that icon. | Rulebook p. 20, `Room special icon — no Securing`. |
| RB-P20-021.rule | `These Rooms can never be broken.` | `ACT-ROOM-001` — Room-tile special-icon rules | Add: `A Room with the crossed-Malfunction special icon cannot be broken.` | Preserve the crossed-Malfunction glyph association and distinguish it from an ordinary Room Malfunction marker. | Rulebook p. 20, `Room special icon — unbreakable`. |
| RB-P20-022.rule | `A Malfunction marker is never placed on them.` | `ACT-ROOM-001` — Room-tile special-icon rules | Add: `A Room with the crossed-Malfunction special icon cannot receive a Malfunction marker.` | This is a placement prohibition for the marked Room; it does not resolve other component-specific Malfunction rules. | Rulebook p. 20, `Room special icon — no Malfunction marker`. |
| RB-P20-023.rule | `Flip an [Active/Inactive Life Support token glyph] in Section A.` | `ACT-ROOM-001` — Room-tile special-icon/effect statements | Add the printed effect exactly as: `Flip an [Active/Inactive Life Support token glyph] in Section A.` | The bracketed glyph remains unresolved/source-local; the effect does not settle whether it is optional beyond the Room Action’s choice structure. | Rulebook p. 20, `LIFE SUPPORT CONTROL “A” tile — first effect`. |
| RB-P20-034.rule | `may be picked up using the Nest Room Action.` | `ACT-ROOM-001` — Nest statements | Add: `A Character may pick up an Egg with the Nest Room Action.` | `OQ-009` remains open for official effects that target the Nest before it is discovered; this edit does not choose a pre-discovery procedure. | Rulebook p. 20, `NEST — pickup`. |
| RB-P20-036.rule | `by using the Nest’s Room Action` | `ACT-ROOM-001` — Nest statements | Add: `Use the Nest Room Action to remove Eggs for Nest destruction.` | `OQ-009` remains open for pre-discovery Nest effects; the source does not supply a replacement location or discovery procedure here. | Rulebook p. 20, `NEST — destruction method`. |
| RB-P20-037.rule | `When there are no more Eggs there, place a Universal marker on the Eggs space` | `ACT-ROOM-001` — Nest statements | Add: `When the Eggs space is empty, place a Universal marker on it.` | The marker is a Nest-destruction marker only in conjunction with the next source assertion; no earlier trigger is added. | Rulebook p. 20, `NEST — destruction marker`. |
| RB-P20-038.fact | `this signifies the Nest being destroyed.` | `ACT-ROOM-001` — Nest statements | Add: `A Universal marker on the empty Eggs space signifies that the Nest is destroyed.` | `OQ-009` remains open for effects aimed at an Undiscovered Nest; destruction meaning is not extended beyond this marker state. | Rulebook p. 20, `NEST — marker meaning`. |
| RB-P20-039.rule | `It stays destroyed even if other effects would add new Eggs there.` | `ACT-ROOM-001` — Nest statements | Add: `Once destroyed, the Nest remains destroyed even if Eggs are later added.` | This permanence statement does not resolve how a later Egg-placement effect is physically handled before discovery; retain `OQ-009`. | Rulebook p. 20, `NEST — permanence`. |
| RB-P21-013.rule | `Empty Corridors may be Reinforced by Characters during the game.` | `FND-012` — Corridor-state bullets | Add: `A Character may Reinforce only an empty Corridor.` | “Empty” retains the existing FND-012 definition (no Intruders); no additional Noise restriction is inferred. | Rulebook p. 21, `REINFORCED CORRIDOR — eligibility`. |
| RB-P21-014.rule | `When a Corridor is Reinforced, discard a Noise marker from it (if there is any)` | `FND-012` — Corridor-state bullets | Add: `When Reinforcing a Corridor, discard its Noise marker if present.` | The conditional “if there is any” is preserved; no marker is created when none is present. | Rulebook p. 21, `REINFORCED CORRIDOR — discard Noise`. |
| RB-P21-015.rule | `flip it to the other side.` | `FND-012` — Corridor-state bullets | Add: `Flip a Reinforced Corridor tile to its back.` | The back is source-marked `REINFORCED`; no alternate value or orientation is inferred. | Rulebook p. 21, `REINFORCED CORRIDOR — flip`. |
| RB-P21-020.rule | `Corridors leading to the Hibernatorium can never be Reinforced.` | `FND-012` — Corridor-state bullets | Add: `A Corridor connected to the Hibernatorium cannot be Reinforced.` | This exception is limited to Hibernatorium-connected Corridors; no broader special-Room exception is added. | Rulebook p. 21, `REINFORCED CORRIDOR — Hibernatorium exception`. |
| RB-P21-029.fact | `this number always starts with the Corridor front Noise value.` | `FND-012` — Corridor identity bullet | Add: `A Corridor ID begins with that tile front’s standard Noise value.` | This is an identity/provenance rule, not a new Noise-resolution result; Deadly Mode values remain separately scoped. | Rulebook p. 21, `Corridor anatomy D — prefix`. |
| RB-P21-036.rule | `The larger Intruders swap places with lower forms if necessary` | `INT-003` — capacity movement bullets | Add: `If necessary, larger Intruders swap places with lower forms.` | The source does not define every placement/movement context or a new destination selector; retain the exact capacity-swap boundary. | Rulebook p. 21, `INTRUDER LIMITS — swap principle`. |
| RB-P21-037.rule | `When moving, simply swap their places` | `INT-003` — capacity movement bullets | Add: `When moving, swap the locations of the larger and smaller Intruders.` | Keep the moving-swap instruction distinct from initial placement at capacity; do not generalize it to every displacement. | Rulebook p. 21, `INTRUDER LIMITS — moving swap`. |
| RB-P21-038.rule | `this DOES NOT cause Intruder Attacks` | `INT-003` — capacity movement bullets | Add: `A location swap caused by Corridor capacity does not trigger an Intruder Attack.` | The no-Attack consequence is retained only for this capacity swap; other entry/movement attacks remain governed by INT-004. | Rulebook p. 21, `INTRUDER LIMITS — no Attack on swap`. |
| RB-P22-011.rule | `Effects that specifically call out “any object in the Facility” ... still work` | `ACT-MOVE-001` — Doors / Blocking Path subsection | Add: `Effects that specifically call out “any object in the Facility” still work even when the target is behind a Closed Door.` | Preserve the conflict with the existing Closed-Door blocking bullet; this proposal records the explicit Facility-wide exception and does not reconcile its scope. | Rulebook p. 22, `BLOCKING PATH — Facility-wide exception`. |
| RB-P22-021.rule | `If there is a Closed Door, it may be Destroyed` | `ACT-MOVE-001` — Doors subsection | Add: `Only a Closed Door can be Destroyed.` | This states Destroy eligibility; it does not authorize a universal Destroy Door Action or select an actor. | Rulebook p. 22, `INTERACTING WITH DOORS — Destroy eligibility`. |
| RB-P23-008.fact | `Each Room may contain only 1 Fire marker.` | `FND-012` — Room marker limits | Add: `A Room can contain at most 1 Fire marker.` | The cap is per Room and does not define the Fire-supply exhaustion consequence. | Rulebook p. 23, `FIRE MARKERS — Room cap`. |
| RB-P23-010.rule | `If at any point you must place a Fire marker and there are no more Fire markers available` | `RT-015` — Overwhelming Fire end trigger | Add the trigger clause exactly in the consolidated text: `If at any point you must place a Fire marker and there are no more Fire markers available, the game ends.` | This fragment is completed by the adjacent end fragment; no additional Fire trigger or replacement marker is inferred. | Rulebook p. 23, `OVERWHELMING FIRE — trigger`. |
| RB-P23-012.rule | `the game ends.` | `RT-015` — Overwhelming Fire end trigger | Add the consequence sentence exactly in the consolidated text: `If at any point you must place a Fire marker and there are no more Fire markers available, the game ends.` | Keep the causal trigger and end consequence together without turning either fragment into a separate trigger. | Rulebook p. 23, `OVERWHELMING FIRE — end`. |
| RB-P23-021.rule | `When discarded they go back to the pool.` | `FND-008` — state-marker supply/lifecycle bullet | Add: `A discarded Malfunction marker returns to its pool.` | No finite-pool allocation or replacement behavior is inferred. | Rulebook p. 23, `MALFUNCTION MARKERS — discard destination`. |
| RB-P23-023.fact | `Each Room may only contain 1 Malfunction marker.` | `FND-012` — Room marker limits | Add: `A Room can contain at most 1 Malfunction marker.` | The cap is per Room; it does not override the distinct component-specific rules for Items, Robots, or Weapons. | Rulebook p. 23, `MALFUNCTION MARKERS 1. ON ROOMS — cap`. |
| RB-P23-052.rule | `place a Fire marker in the Room instead, if possible.` | `FND-008` — component-limit fallback bullet | Add: `If no Malfunction marker is available, place Fire in the affected component’s Room if possible.` | Preserve `if possible`; no behavior is selected when the affected component has no Room or when the Room already has Fire. | Rulebook p. 23, `MALFUNCTION MARKERS LIMIT — substitute`. |
| RB-P23-053.fact | `You must place a Malfunction marker on your Weapon and there are no more markers available. You instead place a Fire marker in your Room.` | `FND-008` — component-limit fallback bullet | Add: `If a Weapon must Malfunction with no marker available, its Character’s Room receives Fire instead.` | This is a Weapon example of the preceding fallback, not a replacement for the general component-limit sentence. | Rulebook p. 23, `MALFUNCTION MARKERS LIMIT — Weapon example`. |
| RB-P24-018.fact | `Exploration cards do not always show the Corridor the Character has Moved through` | `ACT-EXPLORE-001` — Exploration-card diagram note | Add: `Exploration cards do not always show the Corridor the Character has Moved through.` | This is a diagram/interpretation note; it does not remove the triggering Corridor from the movement procedure. | Rulebook p. 24, `EXPLORATION SEQUENCE — card purpose note`. |
| RB-P24-044.fact | `This icon is not used in the base game` | `ACT-EXPLORE-001` — base-game icon boundary | Add: `The Insider icon has no base-game function.` | Flagged as gameplay-irrelevant for base-game resolution; retain for source fidelity and do not assign expansion behavior. | Rulebook p. 24, `EXPLORATION SEQUENCE 6 — Insider icon`. |
| RB-P24-045.rule | `ignore it.` | `ACT-EXPLORE-001` — base-game icon boundary | Add: `Ignore the Insider icon in base-game play.` | Flagged as gameplay-irrelevant for base-game resolution; no effect is invented for the unused icon. | Rulebook p. 24, `EXPLORATION SEQUENCE 6 — ignore`. |
| RB-P25-040.rule | `Activate the Queen.` | `INT-001` — Intruder Help Sheet Queen-resolution table | Add the Corridor-resolution row exactly as shown in the consolidated table. | The row is specific to a Queen token resolved in a Corridor while the Queen is available; no Room-resolution wording is merged into it. | Intruder Help Sheet, `INTRUDER HELP SHEET — Corridor Queen`. |
| RB-P25-041.rule | `If not possible – place her in the Corridor.` | `INT-001` — Intruder Help Sheet Queen-resolution table | Add the Corridor fallback exactly as shown in the consolidated table. | “If not possible” is left undefined; no reason for impossibility or alternate placement procedure is chosen. | Intruder Help Sheet, `INTRUDER HELP SHEET — Corridor Queen fallback`. |
| RB-P25-044.rule | `Activate the Queen.` | `INT-001` — Intruder Help Sheet Queen-resolution table | Add the Room-resolution row exactly as shown in the consolidated table. | Keep this Room occurrence separate from the Corridor occurrence even though the activation sentence is identical. | Intruder Help Sheet, `INTRUDER HELP SHEET — Room Queen`. |
| RB-P25-045.rule | `If not possible – place her in the Room.` | `INT-001` — Intruder Help Sheet Queen-resolution table | Add the Room fallback exactly as shown in the consolidated table. | “If not possible” is left undefined; no reason for impossibility or alternate placement procedure is chosen. | Intruder Help Sheet, `INTRUDER HELP SHEET — Room Queen fallback`. |
| ROOM-0 | `printedEffect: Discard all [R01-I04] from a chosen Section.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact Room Help row for entry 0: `SPRINKLERS CONTROL` — `Discard all [R01-I04] from a chosen Section.` | Keep `[R01-I04]` source-local; artwork-only details are not promoted into a rule. | Room Help Sheet, entry 0, printed number 01. |
| ROOM-12 | `printedEffect: Discard all [R13-I04] and spend 2 [R13-I05] to remove all Contaminations from your deck and discard pile without scanning.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 12, `DECONTAMINATION ROOM`: `Discard all [R13-I04] and spend 2 [R13-I05] to remove all Contaminations from your deck and discard pile without scanning.` Add the associated note exactly: `You may not perform this Room Action if you have 1 [R13-I06] or fewer (if you would gain a Suffocation token as a result).` | Preserve all source-local tokens and the “1 ... or fewer” condition; no icon meaning or alternate Oxygen procedure is inferred. | Room Help Sheet, entry 12, printed number 13. |
| ROOM-14 | `printedEffect: Flip an [R15-I04] / [R15-I05] in Section A. OR Discard a [R15-I06] from any Room in the Facility.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 14, `LIFE SUPPORT CONTROL "A"`: `Flip an [R15-I04] / [R15-I05] in Section A. OR Discard a [R15-I06] from any Room in the Facility.` Add the associated note exactly: `With this Room’s top effect you can activate or deactivate the Life Support System in the “A” Section.` | Preserve the exact “any Room in the Facility” wording; Closed-Door reachability remains subject to the distinct Facility-wide/blocking boundary and is not reinterpreted here. | Room Help Sheet, entry 14, printed number 15. |
| ROOM-15 | `printedEffect: Discard all [R16-I04] to remove a Larva from your Character board and scan all Contaminations in your deck and discard pile. Remove the Infected ones from the game. OR Discard 1 Serious Wound.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 15, `SURGERY ROOM`, with the full printed effect and associated notes reproduced in the consolidated table. | Keep this exact Room Help occurrence separate from the Rulebook’s “easiest way” and “Larva Infection” assertions; do not merge the source wordings. | Room Help Sheet, entry 15, printed number 16. |
| ROOM-16 | `printedEffect: Place a new Corridor leading from the Room with the [R17-I05].` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 16, `DRILLING STATION`: `Place a new Corridor leading from the Room with the [R17-I05].` Add the associated note exactly: `This Corridor may be placed leading to an already Discovered Room or to an Undiscovered Room.` | `SEM-Q-005` remains open on endpoint/edge selection; the note does not authorize a digital tie-break. | Room Help Sheet, entry 16, printed number 17. |
| ROOM-17 | `printedEffect: Make a Noise roll to Hibernate.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 17, `HIBERNATORIUM`: `Make a Noise roll to Hibernate.` Add the associated note and cross-reference exactly in the consolidated table. | Keep `[R18-I01]` and `[R18-I02]` literal; INT-009 retains the Hibernatorium state and failed-after-roll condition. | Room Help Sheet, entry 17, printed number 18. |
| ROOM-18 | `printedEffect: Flip an [R19-I03] / [R19-I04] in Section B. OR Look at both Anti-Aircraft tokens and place them in any order.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 18, `LIFE SUPPORT CONTROL "B"`, with the full printed effect and associated notes reproduced in the consolidated table. | Preserve the “any order” and disclosure note; do not collapse it into the distinct Rulebook Anti-Aircraft sentence. | Room Help Sheet, entry 18, printed number 19. |
| ROOM-19 | `printedEffect: Use any Discovered [R20-I04] Room in the Facility. OR Gain a Data token (if you don’t have one).` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 19, `SERVER ROOM`, with the full printed effect and associated note reproduced in the consolidated table. | Keep `[R20-I04]` and `[R20-I05]` source-local and retain the “Discovered” and “if you don’t have one” limits. | Room Help Sheet, entry 19, printed number 20. |
| ROOM-2 | `printedEffect: Restore 2 [R03-I04]. OR Discard 1 Serious Wound.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 2, `EMERGENCY ROOM`: `Restore 2 [R03-I04]. OR Discard 1 Serious Wound.` | Keep the two printed alternatives separate and retain `[R03-I04]` without interpreting it here. | Room Help Sheet, entry 2, printed number 03. |
| ROOM-20 | `printedEffect: Activate the Autodestruction Procedure.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 20, `COOLING SYSTEM`: `Activate the Autodestruction Procedure.` Add its exact page-38 cross-reference. | INT-010 governs the procedure; this row does not restate or alter the autodestruction timing. | Room Help Sheet, entry 20, printed number 21. |
| ROOM-22 | `printedEffect: Remove all [R23-I03], [R23-I04], [R23-I05], and both Anti-Aircraft tokens from the game.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 22, `REACTOR`, with the full printed effect and associated notes reproduced in the consolidated table. | Keep every `[R23-I..]` token literal and preserve the permanent “cannot be turned on again” note; do not infer which token each placeholder names. | Room Help Sheet, entry 22, printed number 23. |
| ROOM-23 | `printedEffect: Make a Noise roll to get into the Escape Shuttle.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 23, `ESCAPE SHUTTLE`: `Make a Noise roll to get into the Escape Shuttle.` Add the exact failed-roll, one-use, and page-38 cross-reference notes. | INT-009 retains the shared escape gate; the one-use note is not merged into the separate Rulebook capacity assertion. | Room Help Sheet, entry 23, printed number 24. |
| ROOM-3 | `printedEffect: Draw 1 Green, 1 Red, and 1 Yellow Item. You may keep 2 of them and discard the rest.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 3, `SUPPLY ROOM`: `Draw 1 Green, 1 Red, and 1 Yellow Item. You may keep 2 of them and discard the rest.` | Preserve the quantities and the keep/discard choice; Item-deck semantics remain under the Item records. | Room Help Sheet, entry 3, printed number 04. |
| ROOM-4 | `printedEffect: Gain any number of [R05-I04] and [R05-I05].` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 4, `ARMORY`: `Gain any number of [R05-I04] and [R05-I05].` Add the exact Tactical Gear-slot/discard note. | Preserve “any number” and the finite-slot note; no scarcity allocation order is selected. | Room Help Sheet, entry 4, printed number 05. |
| ROOM-6 | `printedEffect: Place 1 [R07-I04] in the Room with the [R07-I05]. OR Reinforce an empty Corridor adjacent to the Room with the [R07-I06].` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 6, `SECURITY ROBOT ROOM`, with both alternatives exactly as printed. | Keep all `[R07-I..]` occurrences literal; the separate Reinforced-Corridor eligibility rule remains explicit. | Room Help Sheet, entry 6, printed number 07. |
| ROOM-7 | `printedEffect: Choose a Corridor adjacent to a Room with a [R08-I05] and without a [R08-I06]. Roll a Burst die and deal Hits equal to the result in that Corridor.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 7, `GUNNERY ROOM`, with the full effect and exact note that rolling a Burst die is not a Burst Action. | Preserve the distinction between “roll a Burst die” and a Burst Action; no Ammo cost is added. | Room Help Sheet, entry 7, printed number 08. |
| ROOM-9 | `printedEffect: Resolve or discard [R10-I04] from a chosen Corridor in the Facility.` | `ACT-ROOM-001` — per-Room source table near FND-012 | Add the exact row for entry 9, `ALARM ROOM`: `Resolve or discard [R10-I04] from a chosen Corridor in the Facility.` | Keep the token literal and do not infer which Noise/Intruder object it denotes. | Room Help Sheet, entry 9, printed number 10. |

## Consolidated edits by target record

### ACT-EXPLORE-001 — Exploration-card source table and diagram boundary

Satisfies: `CARD-game-exploration-game-exploration-025.png`, `CARD-game-exploration-game-exploration-062.png`, `CARD-game-exploration-game-exploration-107.png`, `RB-P24-018.fact`, `RB-P24-044.fact`, `RB-P24-045.rule`.

Add a compact source-occurrence table. These are separate card faces; the bracketed tokens are retained literally and are not normalized:

| Source occurrence | Exact source text to add |
|---|---|
| `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-025.png` | `Place A/B/C Room`<br>`depending on your Section.`<br>`[character] [malfunction]`<br>`[noise]`<br>`Reminder:`<br>`Place 1 [secure] if you are Moving with [secure].`<br>`Make a Noise roll.` |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-062.png` | `Place A/B/C Room`<br>`depending on your Section.`<br>`[character]`<br>`[noise]`<br>`Reminder:`<br>`Place 1 [secure] if you are Moving with [secure].`<br>`Entrance Effect:`<br>`Place 3 Adults in the Corridor`<br>`you have just passed through.`<br>`Then, make a Noise roll.` |
| `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-107.png` | `Place A/B/C Room`<br>`depending on your Section.`<br>`[noise]`<br>`[character]`<br>`[noise]`<br>`Reminder:`<br>`Place 1 [secure] if you are Moving with [secure].`<br>`Entrance Effect:`<br>`Place 2 Adults in the Corridor`<br>`you have just passed through.`<br>`Then, make a Noise roll.` |

Add these separate source-backed notes:

- **Diagram note:** Exploration cards do not always show the Corridor the Character has Moved through. **Source:** Rulebook p. 24, `EXPLORATION SEQUENCE — card purpose note`.
- **Base-game icon boundary:** The Insider icon has no base-game function. **Source:** Rulebook p. 24, `EXPLORATION SEQUENCE 6 — Insider icon`.
- **Base-game resolution:** Ignore the Insider icon in base-game play. **Source:** Rulebook p. 24, `EXPLORATION SEQUENCE 6 — ignore`.

The card rows remain source occurrences/variants; they do not replace the official Exploration Sequence. `SEM-Q-002` remains open on whether a Noise-roll Entrance Effect is additional to the universal post-Movement Noise requirement.

### FND-012 — Facility spaces, Sections, Corridor states, and map markers

Satisfies: `RB-P19-006.fact`, `RB-P19-007.rule`, `RB-P19-012.rule`, `RB-P19-016.fact`, `RB-P19-018.fact`, `RB-P19-025.fact`, `RB-P19-046.fact`, `RB-P19-047.fact`, `RB-P21-013.rule`, `RB-P21-014.rule`, `RB-P21-015.rule`, `RB-P21-020.rule`, `RB-P21-029.fact`, `RB-P23-008.fact`, `RB-P23-023.fact`.

Add the following explicit bullets to the existing FND-012 record:

- **Facility boundary pieces:** The Section border pieces and the Round track border pieces create the borders of the Facility. No Room and no Corridor can ever be placed on those pieces. **Source:** Rulebook p. 19, `FACILITY SIZE — borders` and `FACILITY SIZE — forbidden pieces`.
- **Life Support locations:** Changing the status of those systems is possible in Life Support Control Rooms which can be found in every Section. **Source:** Rulebook p. 19, `SECTIONS — Life Support control`.
- **Section A:** Section A is an Entrance Section – where you start your mission and most likely end it. **Source:** Rulebook p. 19, `SECTION A — role`.
- **Landing Zone:** Characters can restock supplies at the Landing Zone. **Source:** Rulebook p. 19, `SECTION A — Landing Zone supplies` (`a place where Characters can restock their supplies.`).
- **Section B:** Section B is the middle Section. **Source:** Rulebook p. 19, `SECTION B — role`.
- **Map slots:** The illustration shows all slots in which Rooms and Corridors may appear. Section A occupies the left zone, Section B the middle zone, and Section C the right zone of the Facility layout. **Source:** Rulebook p. 19, `SECTIONS IN THE FACILITY — diagram coverage` and `SECTIONS IN THE FACILITY — layout`.
- **Reinforced Corridors:** A Character may Reinforce only an empty Corridor. When Reinforcing a Corridor, discard its Noise marker if present, then flip a Reinforced Corridor tile to its back. A Corridor connected to the Hibernatorium cannot be Reinforced. **Source:** Rulebook p. 21, `REINFORCED CORRIDOR — eligibility`, `REINFORCED CORRIDOR — discard Noise`, `REINFORCED CORRIDOR — flip`, and `REINFORCED CORRIDOR — Hibernatorium exception`.
- **Corridor identity:** A Corridor ID begins with that tile front’s standard Noise value. **Source:** Rulebook p. 21, `Corridor anatomy D — prefix`.
- **Room marker limits:** A Room can contain at most 1 Fire marker and at most 1 Malfunction marker. **Source:** Rulebook p. 23, `FIRE MARKERS — Room cap` and `MALFUNCTION MARKERS 1. ON ROOMS — cap`.

The map-slot and Corridor-ID statements describe source identity/layout and do not create an unstated placement order. Existing boundary bullets remain; these additions make the border-piece, marker-cap, and Reinforced-Corridor assertions explicit.

### ACT-ROOM-001 — named Room statements, Room-tile special rules, Nest rules, and per-Room table

Satisfies: `RB-P19-020.fact`, `RB-P19-022.fact`, `RB-P19-023.fact`, `RB-P19-024.fact`, `RB-P19-033.fact`, `RB-P19-034.fact`, `RB-P19-035.fact`, `RB-P20-018.fact`, `RB-P20-019.rule`, `RB-P20-021.rule`, `RB-P20-022.rule`, `RB-P20-023.rule`, `RB-P20-034.rule`, `RB-P20-036.rule`, `RB-P20-037.rule`, `RB-P20-038.fact`, `RB-P20-039.rule`, `ROOM-0`, `ROOM-12`, `ROOM-14`, `ROOM-15`, `ROOM-16`, `ROOM-17`, `ROOM-18`, `ROOM-19`, `ROOM-2`, `ROOM-20`, `ROOM-22`, `ROOM-23`, `ROOM-3`, `ROOM-4`, `ROOM-6`, `ROOM-7`, `ROOM-9`.

Add these separate named-source statements; similar effects remain separate source occurrences:

- **Drilling Room:** The Drilling Room permits new Corridors to be drilled. **Source:** Rulebook p. 19, `SECTION A — Drilling Room`.
- **Life Support Control A:** Life Support Control A can remove Fire. **Source:** Rulebook p. 19, `SECTION A — Life Support Control A fire`.
- **Surgery Room:** The Surgery Room can discard Serious Wounds. **Source:** Rulebook p. 19, `SECTION A — Surgery Room`.
- **Surgery Room infection:** The Surgery Room can remove a Larva Infection. **Source:** Rulebook p. 19, `SECTION A — Surgery Room infection`.
- **Life Support Control B:** Life Support Control B changes Section B’s Life Support state. **Source:** Rulebook p. 19, `SECTION B — Life Support Control B`.
- **Anti-Aircraft:** Life Support Control B can inspect and change the Anti-Aircraft system. **Source:** Rulebook p. 19, `SECTION B — Anti-Aircraft`.
- **Server Room:** The Server Room can provide a Data token used by some Objectives. **Source:** Rulebook p. 19, `SECTION B — Server Room`.
- **Room special icons:** Rooms may feature other icons showing special rules. A Room with the crossed-Secure special icon is never Secured. A Room with the crossed-Malfunction special icon cannot be broken and cannot receive a Malfunction marker. **Source:** Rulebook p. 20, `Room-tile anatomy F`, `Room special icon — no Securing`, `Room special icon — unbreakable`, and `Room special icon — no Malfunction marker`.
- **Life Support Control A printed effect:** `Flip an [Active/Inactive Life Support token glyph] in Section A.` **Source:** Rulebook p. 20, `LIFE SUPPORT CONTROL “A” tile — first effect`. The glyph remains source-local.
- **Nest pickup:** A Character may pick up an Egg with the Nest Room Action. **Source:** Rulebook p. 20, `NEST — pickup`.
- **Nest destruction method:** Use the Nest Room Action to remove Eggs for Nest destruction. **Source:** Rulebook p. 20, `NEST — destruction method`.
- **Nest destruction marker:** When the Eggs space is empty, place a Universal marker on it. A Universal marker on the empty Eggs space signifies that the Nest is destroyed. Once destroyed, the Nest remains destroyed even if Eggs are later added. **Source:** Rulebook p. 20, `NEST — destruction marker`, `NEST — marker meaning`, and `NEST — permanence`.

Add this compact source-bound Room Help table near FND-012/ACT-ROOM-001. Preserve the source-local `[R..-I..]` tokens exactly; omit only the fragments explicitly marked artwork-only in the source records.

| Entry | Printed section marker | Printed number / title | Exact printed effect | Exact associated note or cross-reference |
|---|---|---|---|---|
| 0 | `?` | `01 — SPRINKLERS CONTROL` | `Discard all [R01-I04]`<br>`from a chosen Section.` | — |
| 12 | `?` | `13 — DECONTAMINATION ROOM` | `Discard all [R13-I04] and spend 2 [R13-I05]`<br>`to remove all Contaminations`<br>`from your deck`<br>`and discard pile`<br>`without scanning.` | `You may not perform this Room Action if you have 1 [R13-I06] or fewer (if you would gain a Suffocation token as a result).` |
| 14 | `A` | `15 — LIFE SUPPORT CONTROL "A"` | `Flip an [R15-I04] / [R15-I05] in Section A.`<br>`OR`<br>`Discard a [R15-I06] from any Room`<br>`in the Facility.` | `With this Room’s top effect you can activate or deactivate the Life Support System in the “A” Section.` |
| 15 | `A` | `16 — SURGERY ROOM` | `Discard all [R16-I04] to remove a Larva`<br>`from your Character board and scan`<br>`all Contaminations in your deck`<br>`and discard pile.`<br>`Remove the Infected ones from the game.`<br>`OR`<br>`Discard`<br>`1 Serious Wound.` | `You can’t perform this Room’s top effect if you don’t have a Larva on your Character board. However, you don’t need to have any Contamination cards to perform it. \| After performing the Action, place the remaining scanned Contaminations back in your deck and then reshuffle the whole deck.` |
| 16 | `A` | `17 — DRILLING STATION` | `Place a new Corridor`<br>`leading from the Room`<br>`with the [R17-I05].` | `This Corridor may be placed leading to an already Discovered Room or to an Undiscovered Room.` |
| 17 | `B` | `18 — HIBERNATORIUM` | `Make a Noise roll to Hibernate.` | `You can only perform this Room’s effect if the Hibernatorium is [R18-I01]. The Hibernatorium can be turned [R18-I02] in Life Support Control C. \| If there is an Intruder in your Room after the Noise roll, this Action fails.`<br>Cross-reference: `More on Hibernating - see Hibernating (page 38).` |
| 18 | `B` | `19 — LIFE SUPPORT CONTROL "B"` | `Flip an [R19-I03] / [R19-I04] in Section B.`<br>`OR`<br>`Look at both Anti-Aircraft tokens`<br>`and place them`<br>`in any order.` | `With this Room’s top effect you can activate or deactivate the Life Support System in the “B” Section. \| Remember that the top Anti-Aircraft token indicates the current status of the Anti-Aircraft system. \| You are not required to share how tokens are placed, nor if you have swapped them or not.` |
| 19 | `B` | `20 — SERVER ROOM` | `Use any Discovered [R20-I04] Room`<br>`in the Facility.`<br>`OR`<br>`Gain a Data token`<br>`(if you don’t have one).` | `Please note that you may not use a Room with a [R20-I05] in this way.` |
| 2 | `?` | `03 — EMERGENCY ROOM` | `Restore 2 [R03-I04].`<br>`OR`<br>`Discard`<br>`1 Serious Wound.` | — |
| 20 | `B` | `21 — COOLING SYSTEM` | `Activate the Autodestruction`<br>`Procedure.` | Cross-reference: `More on Autodestruction Procedure - see page 38.` |
| 22 | `C` | `23 — REACTOR` | `Remove`<br>`all [R23-I03], [R23-I04], [R23-I05],`<br>`and both Anti-Aircraft tokens`<br>`from the game.` | `After removing these tokens: treat all Sections as [R23-I06]. Treat the Anti-Aircraft System as Inactive. \| Remove the [R23-I07] token even if it is already on the Round track. \| [R23-I08], Anti-Aircraft and [R23-I09] cannot be turned on again.` |
| 23 | `C` | `24 — ESCAPE SHUTTLE` | `Make a Noise roll to get into`<br>`the Escape Shuttle.` | `If there is an Intruder in your Room after the Noise roll, this Action fails. \| When a Character Escapes using the Escape Shuttle, the Escape Shuttle cannot be used again in that game – there is only 1 shuttle available.`<br>Cross-reference: `More on “getting into the Escape Shuttle” – see Escaping (page 38).` |
| 3 | `?` | `04 — SUPPLY ROOM` | `Draw 1 Green, 1 Red, and 1 Yellow Item.`<br>`You may keep 2 of them`<br>`and discard`<br>`the rest.` | — |
| 4 | `?` | `05 — ARMORY` | `Gain any number`<br>`of [R05-I04] and [R05-I05].` | `All gained Tactical Gear tokens must be placed in empty Tactical Gear slots. You may discard any number of your Tactical Gear tokens once, before or during this Action.` |
| 6 | `?` | `07 — SECURITY ROBOT ROOM` | `Place 1 [R07-I04] in the Room with the [R07-I05].`<br>`OR`<br>`Reinforce an empty Corridor`<br>`adjacent to the Room`<br>`with the [R07-I06].` | — |
| 7 | `?` | `08 — GUNNERY ROOM` | `Choose a Corridor adjacent to a Room`<br>`with a [R08-I05] and without a [R08-I06].`<br>`Roll a Burst die and deal Hits equal`<br>`to the result in that Corridor.` | `Note that “roll a Burst die” does not mean a Burst Action, so it does not require spending [R08-I07].` |
| 9 | `?` | `10 — ALARM ROOM` | `Resolve or discard [R10-I04]`<br>`from a chosen Corridor`<br>`in the Facility.` | — |

`OQ-009` remains open for the physical resolution of official effects that target an Undiscovered Nest. `SEM-Q-005` remains open for the Drilling Station endpoint selector. The table does not translate any `[R..-I..]` placeholder into a canonical icon or effect beyond the exact source text.

### INT-009 — Hibernatorium and Escape Shuttle statements

Satisfies: `RB-P19-031.rule`, `RB-P19-038.fact`, `RB-P19-045.fact`.

Add these separate bullets:

- **Life Support Control C / Hibernatorium:** Life Support Control C can turn on the Hibernatorium. **Source:** Rulebook p. 19, `SECTION B — Hibernatorium activation`.
- **Life Support Control C / Hibernatorium:** Life Support Control C can activate the Hibernatorium. **Source:** Rulebook p. 19, `SECTION C — Hibernatorium control`.
- **Escape Shuttle capacity:** The Escape Shuttle can carry only 1 Character. **Source:** Rulebook p. 19, `SECTION C — Escape Shuttle capacity`.

The two Hibernatorium bullets remain separate source occurrences. INT-009’s existing active/inactive, Undiscovered, and escape/hibernate procedures remain in force; the one-use Room Help note is preserved separately in the ACT-ROOM-001 table.

### INT-003 — Intruder capacity movement and swap

Satisfies: `RB-P21-036.rule`, `RB-P21-037.rule`, `RB-P21-038.rule`.

Add these separate bullets:

- **Capacity swap principle:** If necessary, larger Intruders swap places with lower forms. **Source:** Rulebook p. 21, `INTRUDER LIMITS — swap principle`.
- **Moving swap:** When moving, swap the locations of the larger and smaller Intruders. **Source:** Rulebook p. 21, `INTRUDER LIMITS — moving swap`.
- **No attack:** A location swap caused by Corridor capacity does not trigger an Intruder Attack. **Source:** Rulebook p. 21, `INTRUDER LIMITS — no Attack on swap`.

These bullets do not choose a universal placement algorithm or extend the no-Attack exception beyond the stated capacity swap.

### ACT-MOVE-001 — Doors / Blocking Path subsection

Satisfies: `RB-P22-011.rule`, `RB-P22-021.rule`.

Add these separate bullets to the existing Doors subsection:

- **Facility-wide exception:** Effects that specifically call out “any object in the Facility” still work even when the target is behind a Closed Door. **Source:** Rulebook p. 22, `BLOCKING PATH — Facility-wide exception`.
- **Destroy eligibility:** Only a Closed Door can be Destroyed. **Source:** Rulebook p. 22, `INTERACTING WITH DOORS — Destroy eligibility`.

The first bullet is an explicit source exception and remains visibly distinct from the existing general Closed-Door blocking bullet. No conflict is silently resolved by this proposal.

### RT-015 — Overwhelming Fire end trigger

Satisfies: `RB-P23-010.rule`, `RB-P23-012.rule`.

Add:

- **Overwhelming Fire:** If at any point you must place a Fire marker and there are no more Fire markers available, the game ends. **Source:** Rulebook p. 23, `OVERWHELMING FIRE — trigger` and `OVERWHELMING FIRE — end`.

The two adjacent fragments are combined only to make the source’s trigger and consequence explicit; no additional trigger is added.

### FND-008 — component-limit marker lifecycle and fallback

Satisfies: `RB-P23-021.rule`, `RB-P23-052.rule`, `RB-P23-053.fact`.

Add these separate bullets:

- **Malfunction-marker return:** A discarded Malfunction marker returns to its pool. **Source:** Rulebook p. 23, `MALFUNCTION MARKERS — discard destination`.
- **No-marker fallback:** If no Malfunction marker is available, place Fire in the affected component’s Room if possible. **Source:** Rulebook p. 23, `MALFUNCTION MARKERS LIMIT — substitute`.
- **Weapon example:** If a Weapon must Malfunction with no marker available, its Character’s Room receives Fire instead. **Source:** Rulebook p. 23, `MALFUNCTION MARKERS LIMIT — Weapon example`.

The fallback retains the source’s `if possible` boundary and does not select behavior for a component without a Room, a Room already containing Fire, or a compound effect after the substitution.

### INT-001 — Intruder Help Sheet Queen-resolution table

Satisfies: `RB-P25-040.rule`, `RB-P25-041.rule`, `RB-P25-044.rule`, `RB-P25-045.rule`.

Add a context-separated table without merging the identical activation sentences:

| Resolution context | Exact source instruction |
|---|---|
| Resolve in a Corridor, Queen available | `Activate the Queen.` |
| Resolve in a Corridor, activation not possible | `If not possible – place her in the Corridor.` |
| Resolve in a Room, Queen available | `Activate the Queen.` |
| Resolve in a Room, activation not possible | `If not possible – place her in the Room.` |

**Source:** Intruder Help Sheet anchors `INTRUDER HELP SHEET — Corridor Queen`, `INTRUDER HELP SHEET — Corridor Queen fallback`, `INTRUDER HELP SHEET — Room Queen`, and `INTRUDER HELP SHEET — Room Queen fallback`.

The phrase “If not possible” remains deliberately undefined; no availability, timing, or alternate placement default is added.

## Flags

- `CARD-game-exploration-game-exploration-025.png`, `CARD-game-exploration-game-exploration-062.png`, `CARD-game-exploration-game-exploration-107.png`: secondary card-face/source-variant records contain literal bracketed tokens whose semantics are not resolved here, and `SEM-Q-002` remains open on whether an Entrance-effect Noise roll is additional. Consequence test: the proposed table preserves the printed card occurrences but must not become a canonical interpretation of token meaning or Noise timing.
- `RB-P19-006.fact`, `RB-P19-007.rule`: partially covered by the existing FND-012 right/bottom Facility-boundary text, but the explicit border-piece boundary and placement prohibition are absent. Coordinator re-check is required rather than dropping either ID.
- `RB-P19-022.fact`: the fragment explicitly says the exact Fire-removal range is stated on the Room tile/Help Sheet, not in the rulebook sentence. The proposal records capability only.
- `RB-P20-023.rule`: the printed `[Active/Inactive Life Support token glyph]` remains a source-local unresolved token; no icon meaning is supplied.
- `RB-P20-034.rule`, `RB-P20-036.rule`, `RB-P20-037.rule`, `RB-P20-038.fact`, `RB-P20-039.rule`: `OQ-009` remains open for placement/activation/destruction effects involving an Undiscovered Nest. Consequence test: the exact discovered-Nest assertions are useful, but no pre-discovery physical procedure may be inferred.
- `RB-P21-036.rule`, `RB-P21-037.rule`, `RB-P21-038.rule`: the source distinguishes a larger/lower-form capacity swap and a moving swap but does not define every displacement context. The three bullets preserve that boundary and do not choose a broader algorithm.
- `RB-P22-011.rule`: explicit Facility-wide effects through Closed Doors conflict in scope with the existing general Closed-Door blocking bullet. Both statements must remain visible for coordinator adjudication.
- `RB-P23-052.rule`: `if possible` leaves the no-Room/already-Fire/compound-effect cases open; the proposal does not fill that gap.
- `RB-P24-044.fact`, `RB-P24-045.rule`: explicitly gameplay-irrelevant to base-game resolution. Consequence test: they change no base-game state, but retaining the source boundary prevents an unused/expansion icon from acquiring a fabricated effect.
- `RB-P25-041.rule`, `RB-P25-045.rule`: “If not possible” does not state why Queen activation is impossible. The fallbacks are recorded verbatim without selecting a condition.
- `ROOM-14`: “from any Room in the Facility” is preserved literally; its access interaction with Closed Doors must not be silently merged with a different source occurrence.
- `ROOM-16`: the exact Drilling Station effect and its already-/Undiscovered-Room note are source-complete, but `SEM-Q-005` leaves endpoint/edge selection unresolved.

## Closure

IDs assigned: 72. IDs in table: 72. IDs in consolidated blocks: 72.
