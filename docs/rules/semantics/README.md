# Nemesis: Retaliation semantic rules corpus

This directory is the first implementation-neutral semantic layer built over the approved vocabulary and independently reviewed static ontology.

## Files

- `semantic-rule.schema.json` — closed JSON Schema shape for one semantic rule record.
- `semantic-vocabulary.json` — semantic-only states, temporary zones, deck positions, and visibility scopes that must not be confused with static ontology classes/processes.
- `room-icon-denotations.json` — source-scoped semantic projection of all 112 Room Help functional-icon occurrences; literal extraction remains unchanged.
- `event-source-index.json` — mechanically derived closure of the 20 base Event face occurrences against TTS role/card IDs, source bytes, corpus/backlog tuples, official visible occurrences, and the licensed-digital table; title-only joins are prohibited.
- `exploration-source-index.json` — mechanically derived closure of all 12 untitled base Exploration faces, their exact TTS CardID/GUID/FaceURL and shared BackURL provenance, 46 printed sentences, 12 diagrams, 60 source-local icon occurrences, official/FAQ occurrences, licensed variants, and backlog tuples; title/folder/modulo joins are prohibited.
- `robot-source-index.json` — mechanically derived closure of the six base Robot faces, one shared non-operative back, exact root-role/CardID/GUID/FaceURL/container provenance, 24 panels, 16 sentences, 23 icons, official/FAQ/runtime-state boundaries, licensed variants, exclusions, and backlog tuples; title/folder/modulo joins are prohibited.
- `attack-source-index.json` — mechanically derived closure of 20 base Intruder Attack occurrences: 19 selected 5×4-sheet cells plus one direct face, one shared back, one unused selector-gap cell, full CardID/GUID/CustomDeck/URL provenance, repeated-title multiplicity, panels/sentences, 57 source-scoped applicability badges, official counterparts, 15 licensed variants, exclusions, and backlog tuples.
- `queen-health-source-index.json` — mechanically derived closure of 12 physical base Queen Health occurrences over 10 face assets, one shared back, exact saved CardID/GUID/CustomDeck/FaceURL provenance, two-panel/count/icon locks, official track/visual/FAQ/Objective evidence, 12 independent licensed rows, duplicate-copy boundaries, exclusions, and backlog tuples.
- `serious-wound-source-index.json` — mechanically derived closure of all 27 base Serious Wound physical occurrences: 21 generated selections across seven cells of one 3×3 source sheet plus six direct LEG/KNEE copies, two explicit selector-gap cells, one shared back, 54 panels/81 regions, exact text/icons, official-visible occurrences, nine independent licensed rows, exclusions, and backlog tuples.
- `green-item-source-index.json` — mechanically derived closure of the base regular Green Item family: 23 exact physical Backpack-card occurrences from a 30-child root, seven Heavy exclusions, eight printed titles/assets, five selected and four selector-gap 3×3-sheet cells, one shared back, 46 sentences/icons, official family evidence, ten independent licensed rows, and backlog closure.
- `red-item-source-index.json` — mechanically derived closure of the full 30-child Red root: 21 source-clear regular occurrences, three explicit Heavy occurrences, six Military Taser physical-class conflicts, two sheets/two backs, seven selector gaps, 45 regular-face sentences, 27 regular physical glyphs, official/FAQ evidence, nine independent licensed rows, and backlog closure.
- `yellow-item-source-index.json` — mechanically derived closure of the full 30-child Yellow root: 24 source-clear regular occurrences, six Fire Extinguisher/Robot Controller physical-class conflicts, two 2×2 sheets, five selector gaps, one shared back plus one cell-selected UniqueBack sheet, 56 regular-face sentences, 48 regular physical glyphs, one official-visible Duct Tape face, six independent licensed rows, and backlog closure.
- `equipment-source-index.json` — mechanically derived closure of the base Heavy/Support Equipment/Weapon/Armor/Character Starting Item batch: the exact 24-card `startItemDeck` root, 40 source face assets with 16 selector gaps, 7 Character-kit occurrences, 10 color-root Heavy occurrences, 12 non-dispatchable class conflicts, 6 official-visible current occurrences, 6 non-operative back assets, 37 independent licensed rows, slot/track evidence, FAQ boundaries, and exact backlog links.
- `action-source-index.json` — mechanically derived closure of all 60 base Action physical occurrences across six Characters: seven TTS root segments, 39 direct faces, 21 selected generated cells, 29 base selector-gap variants, 40 excluded expansion cells, two 9×5 sheets, one shared back, exact anatomy/text/icons/costs, official/FAQ evidence, 60 independent licensed rows, and backlog closure.
- `objective-mission-source-index.json` — mechanically derived closure of the base competitive Objective/Mission family: 30 exact physical copies across three TTS roots, 50 source-face assets, two sheets/two backs, 18 selector gaps, nine prototype/high-count physical exclusions, 45 official Help units with the 35-visible/10-occluded boundary intact, 38 independent licensed rows, and exact Solo/Coop exclusions.
- `source-registry.json` — 468 exact source tuples, hashes, versions, authority, occurrence identities, and extraction-index links used by the corpus.
- `pilots.json` — 506 validated semantic records across 25 systems; the historical filename is retained while coverage expands.
- `review-gates.json` — 101 explicit open semantic questions with alternatives; no default is adopted.
- `contradictions.json` — 80 source/semantic conflicts: 18 authority-resolved, 30 unresolved, and 32 preserved boundaries.
- `coverage.json` — pilot scope and the large remaining base-game semantic surface.
- `backlog.json` — 600 source-obligation units across rule records, FAQ, visual obligations, Help sheets, and independent card/reference tuples; 499 are covered, 100 pending, and one source-blocked, with overlapping variants intentionally retained.
- `validation.json` — deterministic validation report.
- `independent-review.md` — four-workstream review findings and incorporated corrections.

Builder: `scripts/build_semantic_pilots.py`
Validator: `scripts/validate_semantic_pilots.py`

## Record obligations

Every pilot carries:

- base applicability and authority/interpretation level;
- exact source assertions and evidence locators;
- vocabulary, taxonomy, and named-identity references;
- timing window and participants;
- modality (`must`, `may`, `cannot`, `if-able`, or mixed);
- structured preconditions/operation guards;
- explicit decision owner, selection mode, cardinality, decline rights, and visibility;
- information/secrecy policy;
- costs, targets, and ordered operations;
- zone/state/value transitions;
- partial-resolution policy;
- duration/stacking/outcomes;
- unresolved-question and source-variant links;
- an explicit implementation-neutral boundary.

## Current coverage

The 506 records cover the original reusable-procedure set plus:

1. Round phase sequence;
2. Player Phase rotation;
3. a Player Turn;
4. Pass;
5. Move/Movement Sequence;
6. Exploration Sequence;
7. Search with owner-private candidates and deck-bottom returns;
8. Rest as a modifier over Infection Procedure;
9. Duck and Cover Reaction replacement targeting;
10. Sprinklers Control Room effect;
11. Hatching Event with per-sentence partial resolution;
12. Queen-Alive Intruder Help Room-context dispatch;
13. endgame triggers and checks;
14. Objective choice;
15. Intruder Phase;
16. Event Phase and generic Event resolution;
17. Bag Development;
18. Cleanup Phase with OQ-003;
19. Door states and blocking;
20. Noise Roll;
21. Intruder Attack;
22. Character Health, Serious Wounds, and death;
23. Tactical Gear token/slot constraints; and
24. the source-obligation links for those reusable procedures;
25. all 18 Intruder Help instruction rows, including Queen alive/dead side conditions, finite supply, front/back token data, model capacity, immediate attacks, and token lifecycle;
26. generic Use the Room plus all 25 Room Help effects;
27. all 112 Room Help functional-icon occurrences mapped source-scoped, including printed static Room properties and connected Tactical Gear slots;
28. FAQ-controlled Shelter, Drilling Station, Technical Corridor Entrance, and Nest behavior;
29. Robot Malfunction, Data-token persistence, Autodestruction, and Nest-destruction constraints; and
30. per-Corridor Noise movement/Attack ordering;
31. all 20 mechanically closed base Event face occurrences, with exact sentence/section order, one licensed-digital variant per face, and generic occurrence-based dispatch;
32. reusable Event movement, Noise-marker, Hazard, Secure-entry, Fire-spread, Infection, and Eclosion procedures needed by those faces; and
33. all 12 mechanically closed untitled base Exploration face occurrences, with exact placement/reminder/Entrance/lifecycle order, source-local six-slot diagrams and icon identities, one licensed-digital variant per face, three official visible occurrences, and occurrence-based dispatch from the generic Exploration Sequence; and
34. the complete six-face base Robot family, with one shared back, random hidden setup/reveal, local/remote Activation and Data-token costs, movement and Tactical Gear procedures, finite Malfunction/Fire/Secure handling, exact panel/sentence/icon order, six licensed variants, two official visible face occurrences, and eight new no-default questions; and
35. all 20 mechanically selected base Intruder Attack occurrences, including six distinct Bite copies and other repeated titles, 19 generated cells plus direct Blood Sense, one shared back, the excluded unused Summoning cell, 69 physical panels, 54 printed sentences, 57 source-scoped applicability badges, 13 inline icons, 15 licensed structured variants, three official-visible face counterparts, occurrence dispatch from `SEM-INT-004`, reusable Contamination gain, and five new no-default questions.
36. all 12 mechanically derived base Queen Health physical occurrences over 10 direct face assets, with two duplicate-asset pairs retained as four physical copies, one 13-reference shared back, 24 panels, 37 printed sentences, 12 source-local number displays, 16 exact page-40 icon matches, 12 independent licensed rows, three official-visible faces/two backs, Queen Hits/setup/draw/death/Activation/Repel/Shoot/Burst integration, and five new no-default questions.
37. all 27 mechanically derived base Serious Wound physical occurrences over nine selected face assets, with seven selected 3×3-sheet cells (21 physical copies), six direct LEG/KNEE copies, two unselected selector-gap cells retained as source variants, one 28-reference shared back, 54 panels/81 regions, 42 printed sentence occurrences, 30 physical functional-icon occurrences, nine independent licensed rows with zero asserted physical identity links, three official-visible faces/two backs, reusable setup/gain/discard/stacking/variant procedures, and nine new no-default questions.
38. all 23 mechanically derived base regular Green Item physical occurrences over eight selected face assets, with fifteen generated selections across five 3×3-sheet cells plus eight direct copies, four selector-gap cells, seven exact Heavy root exclusions, one 31-reference shared back, 85 panels/69 regions, 46 printed sentences and 46 physical functional icons, ten independent licensed rows preserving the aggregate 30/23/7 boundary without copy joins, reusable finite deck/Backpack/Use/One Use/Trade/Interplay/restoration/immediate-use procedures, and seven new no-default questions.
39. all 21 source-clear regular Red Item physical occurrences from the exact 30-child root, with seven generated selections across four 4×2-sheet cells plus fourteen direct copies, four Red selector-gap variants, three explicit Heavy exclusions, six Military Taser class-conflict selectors from a cross-family 2×2 sheet, two non-operative backs, 87 panels/63 regions, 45 printed sentences and 27 regular physical glyphs, nine independent licensed rows, reusable Ammo/Grenade/Anti-Aircraft procedures, and five new no-default questions.
40. all 24 source-clear regular Yellow Item physical occurrences from the exact 30-child root, with eleven generated selections across Duct Tape/Tools cells plus thirteen direct Phosphates/Oxygen Tank copies, five selector gaps across two 2×2 sheets, six Fire Extinguisher/Robot Controller class conflicts, one shared back plus one cell-selected UniqueBack sheet, 128 panels/72 regions, 56 printed sentences and 48 regular physical glyphs, one exact official-visible Duct Tape occurrence, six independent licensed rows, reusable Oxygen/Malfunction/Reinforce procedures, and six new no-default questions.
41. all 60 mechanically derived base Action physical occurrences, with 55 Character-kit selectors plus five Shared Contractor selectors, 39 direct faces, 21 selected generated cells, 29 base selector-gap variants, 40 excluded expansion cells, two parent sheets, one 273-reference shared back, 290 panels, 164 sentences, 143 physical symbols, exact setup/play/payment/draw/Reaction/Command lifecycle, 60 independent licensed rows, and eighteen new no-default questions.
42. the source-clear base competitive Objective/Mission family: 7 Mission Objective, 15 Private Objective, and 8 Mission Task physical copies; 29 source-clear physical effect records plus the one retained `FACILITY RESTART` blocker; 20 fully visible official card occurrences; 26 independent competitive licensed rows; exact setup, secrecy, discussion/lying, remove/retain, Objective Choice reward, reveal, fulfillment, Survivor/Escape, Facility destruction, checkbox, and occurrence dispatch procedures; all 45 Objective Help obligations linked without promoting ten occluded bodies; nine prototype/high-count and 38 Solo/Coop TTS physical selectors retained as exclusions; and four new no-default timing/branch questions.
43. the bounded base Heavy/Support Equipment/Weapon/Armor/Character Starting Item family: exact 24-card Support root with 22 direct and 2 generated selections, 40 source face assets including 16 selector gaps, 19 Heavy and 5 Armor Support occurrences, 12 Support Weapons (9 Ranged/3 Melee), one 72-reference shared Support back, 7 Character-kit occurrences with 5 source-clear TTS variants and 2 Automatic Shotgun/BF Gun prototype/current exclusions, 7 Green Heavy plus 3 Red Heavy source-clear color-root occurrences, 12 Red/Yellow class conflicts retained non-dispatchable, 6 official-visible current occurrences, 37 independent BGA rows, 52 source-face backlog tuples, reusable setup/draft/Hand/Armor/load/use/passive/loss/Malfunction/die-result/Grenade Launcher procedures, and 18 new no-default questions. Exact titles, bodies, punctuation, panels, local icons, slots, tracks, backs, copies, authorities, and variants remain source-scoped.

This is representative, **not full base-game semantic coverage**.

The backlog currently records 499 covered source obligations, 100 pending obligations, and one inherited exact-source blocker (`FACILITY RESTART`). The closed source-clear component batches now include the base Heavy/Equipment/Weapon/Armor/Starting Item family while retaining twelve class-conflict occurrences, two audited prototype/current conflicts, sixteen Support selector gaps, ten physically occluded official Objective card occurrences, and all Solo/Coop roots outside competitive dispatch. These are overlapping source-obligation counts, not a claim that 600 distinct game effects exist.

## Open questions carried without defaults

OQ-002 is no longer an open gate. Current official rulebook p. 39 (lines 6251–6265) orders Infection before Eclosion, applies Eclosion to each Character who “currently has a Larva,” and states that a Character may have gained a Larva “during this Sequence.” `SEM-ENDGAME-001` therefore evaluates Larva eligibility when the Eclosion cohort step is reached and includes a Larva gained during the preceding Infection step. OQ-001 and multi-Character cohort ordering remain untouched.

- OQ-001 — Eclosion existing-hand behavior;
- OQ-003 — Starting Player transfer over nonparticipants;
- OQ-004 — mid-Turn death advancement;
- OQ-007 — simultaneous multi-Intruder Secure consumption;
- OQ-009 — Nest placement before discovery;
- SEM-Q-001 — Duck and Cover replacement target when multiple other Characters are present.
- SEM-Q-002 — whether an exploratory Entrance Noise satisfies or adds to mandatory Movement Noise;
- SEM-Q-003 — which equal-largest Opportunity Attackers resolve when more than three qualify.
- SEM-Q-004 — whether Supply Room’s “You may keep 2” means optional exact-two or any subset up to two.
- SEM-Q-005 — Drilling Station new-Corridor endpoint selection.
- SEM-Q-006 — Leaving the Shell’s three white-rectangle glyph identities.
- SEM-Q-007 — finite Intruder allocation across multiple Event target spaces.
- SEM-Q-008 — finite Malfunction/fallback allocation across multiple Event target Rooms.
- SEM-Q-009 — Fire-spread source snapshot versus propagation during one Event sentence.
- SEM-Q-010 — the page-22/page-37 Robot Malfunction effect-availability contradiction.
- SEM-Q-011 — assignment/order of random Corridor draws and scarce finite components across multiple Exploration diagram slots.
- SEM-Q-012 — external Robot-referencing effects before the selected Robot face is revealed.
- SEM-Q-013 — Robot movement destination owner and multi-step route timing.
- SEM-Q-014 — Exploration Robot Noise modality and timing.
- SEM-Q-015 — Medical Robot branch and reduced-restoration decision owner.
- SEM-Q-016 — Securing Robot “accessible” Door eligibility.
- SEM-Q-017 — Securing Robot exact-two Secure placement under scarcity/capacity.
- SEM-Q-018 — Server Robot Room-effect actor, local context, and nested costs.
- SEM-Q-019 — Technical Robot Malfunction-removal target scope.
- SEM-Q-020 — Fury global-versus-attacking-Room Character scope.
- SEM-Q-021 — compound Attack-panel continuation after intermediate Character death.
- SEM-Q-022 — Blood Sense Movement check and relocation after death/interruption.
- SEM-Q-023 — Deadly Claws random Wound-to-slot and finite-deck order.
- SEM-Q-024 — MISS applicability despite having no printed Intruder-type badges.
- SEM-Q-025 — exact Queen Health trigger timing inside Shoot/Burst/other Actions.
- SEM-Q-026 — attribution of each face’s “drawn by a Character” condition.
- SEM-Q-027 — Queen death timing when the final card is drawn versus discarded.
- SEM-Q-028 — Malfunction/Unreinforce branch ownership, location dispatch, and unavailable-branch handling.
- SEM-Q-029 — identity/scope of the unmapped Queen Hits terminal/inline local glyph.
- SEM-Q-030 — Serious Wound draw/reveal/face-up placement timing.
- SEM-Q-031 — Serious Wound gain when no Health Section is empty.
- SEM-Q-032 — Wound placement while the Health marker is Heavily Injured.
- SEM-Q-033 — direct KNEE local action-glyph identity/scope.
- SEM-Q-034 — LUNGS terminal local-glyph identity.
- SEM-Q-035 — BODY “Hand Size” scope.
- SEM-Q-036 — newly placed Wound effect-activation order.
- SEM-Q-037 — Whenever-you-Pass Wound trigger order.
- SEM-Q-038 — multiple-Wound draw/placement/shortfall order.
- SEM-Q-039 — Use Item declaration/payment/reveal/effect/One Use discard order.
- SEM-Q-040 — Item color-deck exhaustion, discard recycling, and multi-draw shortage.
- SEM-Q-041 — selected Green local draw/crossed-device glyph identities.
- SEM-Q-042 — Contamination Codes Door eligibility and scarce-token allocation.
- SEM-Q-043 — restoration-amount owner under Item Interplay.
- SEM-Q-044 — Interplay “Gaining” glyph and Tactical Gear gain-target scope.
- SEM-Q-045 — ordering of multiple gained immediate-use Item windows.
- SEM-Q-046 — selected Red upper-right crossed-glyph identities and restrictions.
- SEM-Q-047 — Military Taser Red-root class/current-source correspondence.
- SEM-Q-048 — Exploring Drone target owner and remote Exploration context.
- SEM-Q-049 — Personal Log Codes target, inspector, range, and Objective secrecy.
- SEM-Q-050 — Portable Barrier Door target/override and Portable Barricade FAQ applicability.
- SEM-Q-051 — selected Yellow upper-right crossed-glyph identities and restrictions.
- SEM-Q-052 — Yellow-root Fire Extinguisher/Robot Controller physical class/current-source correspondence.
- SEM-Q-053 — Duct Tape source wording, One Use disposition, and confirmed third-Item arrangement.
- SEM-Q-054 — Duct Tape stack cardinality and later discard/loss/Malfunction/Trade lifecycle.
- SEM-Q-055 — Phosphates Empty Corridor target owner, locality, and eligibility.
- SEM-Q-056 — Tools Door target/state owner, local range, and accessibility.
- SEM-Q-057 — selected Action upper-right crossed-glyph denotations and scope.
- SEM-Q-058 — selected Search octagon identity and corresponding Item-deck mapping.
- SEM-Q-059 — Command nested-Action costs, resources, legality, and remaining choices.
- SEM-Q-060 — Reaction priority, simultaneous windows, replacement order, and stacking.
- SEM-Q-061 — Action-card continuation and discard after acting Character death/escape.
- SEM-Q-062 — Continuous Fire zero-card legality, Hit allocation, and optional Burst.
- SEM-Q-063 — Always Prepared multi-Intruder Attack order and continuation.
- SEM-Q-064 — Always Prepared Item draw privacy, optional keep, destination, and shortage.
- SEM-Q-065 — Medical Action target consent and Field Surgery payment/choice ownership.
- SEM-Q-066 — Weak Spots/Hippocratic Oath setup Hits before required attack.
- SEM-Q-067 — Officer Channel nested Command card lifecycle and Room substitution.
- SEM-Q-068 — Stay Calm local draw-glyph identity.
- SEM-Q-069 — Let’s Go companion owner, consent, Movement, and Noise/Attack scope.
- SEM-Q-070 — Taking Aim reroll scope and second-result acceptance.
- SEM-Q-071 — Explosives new-Corridor endpoint, geometry, orientation, and finite supply.
- SEM-Q-072 — Action draw shortage and multi-recipient ordering.
- SEM-Q-073 — Movement-card interrupt, prevention, companion, and continuation windows.
- SEM-Q-074 — Chain of Command Reaction cancellation cost meaning and timing.
- SEM-Q-075 — Objective `OR` branch commitment, timing, and unavailable-option handling.
- SEM-Q-076 — Ulterior Motive “remain UNFULFILLED” continuous history versus endgame snapshot.
- SEM-Q-077 — late endgame Objective choice procedure, Objective Choice reward, and chooser order.
- SEM-Q-078 — endgame chosen-Objective reveal/check order among surviving Characters.

- OQ-001, OQ-003, OQ-004, OQ-007, OQ-009, SEM-Q-010, SEM-Q-025, SEM-Q-027, SEM-Q-029, SEM-Q-030, SEM-Q-031, SEM-Q-032, SEM-Q-036, SEM-Q-037, SEM-Q-038, SEM-Q-039, SEM-Q-040, SEM-Q-042, SEM-Q-043, SEM-Q-044, SEM-Q-045, SEM-Q-047, SEM-Q-049, SEM-Q-050, SEM-Q-052 through SEM-Q-056, SEM-Q-059 through SEM-Q-067, and SEM-Q-069 through SEM-Q-077 prefer official clarification. The other SEM questions require further source searching before any owner decision.

## Fidelity boundaries exercised

- Reaction is not an Action.
- Search candidates/unchosen Items remain private and return to their respective deck bottoms despite shorter card wording.
- Rest preserves exact source variants rather than rewriting one face from another.
- Event impossibility applies per sentence and continuation is mandatory.
- All 20 Event faces preserve exact movement/main/secondary sentence order; generic draw/discard is not duplicated into each face.
- All 12 Exploration faces remain untitled and are keyed by stable occurrence identity; no BGA number, filename, folder, display name, or invented slug becomes a printed title.
- Exploration diagrams retain exact source-local Corridor/Noise slots, Room markers, reminder glyph occurrences, three independent remove-from-game sentences, and the paired non-operative back. No inactive/active system icon is inferred where none is printed.
- Robot faces are keyed by the exact root `robotDeck` role plus full CardID/GUID/FaceURL/parent-deck tuple, not display title, folder, shared URL, or CardID modulo. The anomalous child object deck numbers remain literal provenance rather than being repaired.
- The shared Robot back, Robot model, Lua helper-state token, prototype Robot cards, advanced expansion Robots, and Security Robot Room name collisions remain distinct from the six operative faces. TTS flipping/GMNotes/state-1 behavior is runtime evidence only.
- The selected Robot face and five excluded faces remain hidden exactly as setup states; no pre-reveal inspection, route choice, Door range, Secure scarcity policy, nested Room actor, or marker target is silently automated.
- `SEM-Q-010` remains unresolved. The Neoflesh-specific FAQ Robot answers are retained as expansion evidence and do not override the contradictory base rulebook passages.
- Attack faces are keyed by the exact base `attacksDeck` root plus full CardID/GUID/CustomDeck/FaceURL/generated-cell tuple, never title, folder, cell alone, or CardID modulo. Six Bite copies and every other repeated title remain distinct physical occurrences.
- The 5×4 parent sheet and shared `ATTACK / PRIMEBLOOD` BackURL are provenance/non-operative sides, not extra rules faces. Unselected cell 17 (`SUMMONING`) has no root DeckID/GUID selector and remains explicitly excluded with its source tuple intact.
- All 57 local cyan applicability badges retain their literal selected no-match/match evidence while a separate source-scoped projection uses the three page-32-labeled Adult/Drone/Queen templates. No page-40, color-wide, position-wide, or global icon alias is created.
- Deadly Claws, Infecting, Tail Attack, and Fury source differences remain explicit. Official-visible current counterparts control where applicable; exact TTS scans and all 15 lower-authority licensed records are not rewritten or flattened.
- `characterHealth` is used for the local card-06 glyph only after an independent exact-scale match to an existing page-40-backed Attack occurrence; the original unlabeled/no-match evidence remains present. The conflicting card-19 selected rows are likewise retained rather than silently repaired.
- Generic Attack draw/target/discard rules remain in `SEM-INT-004`; each face encodes only occurrence applicability and its ordered panel effect. MISS returns itself before its FAQ-controlled self-inclusive reshuffle, and generic discard applies only while a card remains in resolution.
- Queen Health identity comes from the base `queenHealthDeck` root plus exact saved physical CardID/GUID/CustomDeck/FaceURL/BackURL tuples, never the shared `Discard` heading, displayed count alone, filename, CardID modulo, or licensed key suffix. Twelve physical cards remain distinct even though `-084` and `-045` each supply two copies.
- The TTS saved order is retained as provenance but setup shuffles it; `QueenHealthCard1..12` suffixes are licensed structured keys, not printed card numbers or source-backed order. Duplicate licensed rows remain candidate sets rather than arbitrary one-to-one copy joins.
- All twelve segmented green number displays remain source-local: nine are explicit selected all-49 no-matches and the canonical face retains one preselected unregistered display. Their visible numeric values compose only with the page-35 card instruction and create no Shoot/Burst/Health/damage alias.
- The Queen Hits track remains `0,1,2,3,4,terminal-local-glyph`; both queen-head/blob-plus-style terminal/inline occurrences stay unmapped. Shoot/Burst timing, Character attribution, final-card death timing, and Malfunction/Unreinforce ownership receive no defaults.
- Generic Queen Health resolution alone owns reveal, hidden additional discards, exact physical-face dispatch, drawn-card discard, no-reshuffle finite exhaustion, and reset to exactly 0 without overflow. Bottom effects still run after death caused by additional discards; the final-draw death conflict remains SEM-Q-027.
- Serious Wound identity comes from the sole base `seriouswoundDeck` root plus exact saved full CardID/GUID/CustomDeck/FaceURL/BackURL tuples and, for generated faces, an exact sheet/hash/grid/cell selector—not title, body resemblance, folder, saved sequence, or CardID modulo. All nine printed titles have multiplicity three.
- The 3×3 parent sheet is one source asset, not a rules face. Cells 4 (LEG) and 6 (KNEE) have no root DeckID/GUID selector and remain source variants; they are never substituted for the six direct physical LEG/KNEE copies by matching title or effect.
- The shared `SERIOUS WOUND` back is one non-operative side with 28 references, not a twenty-eighth rules face. Setup shuffles exactly 27 physical cards face down; no checked rule reshuffles the separate Serious Wound discard pile.
- Exact selected FaceURL/source-byte equivalence—not display title—supplies duplicate non-stacking groups. Every physical copy remains separately selectable for discard; discard moves one owner-selected copy to the Wound discard pile, slides remaining Wounds left, does not move Health, and ends only that copy’s contribution.
- Thirty physical functional-icon occurrences retain 24 exact page-40 matches and six local no-match occurrences. The direct KNEE two-lobe glyph and LUNGS stepped-zigzag remain literal under SEM-Q-033/034; licensed placeholders and selector-gap artwork create no alias.
- Nine licensed `SERIOUS_WOUNDS_DATA` rows remain independent with zero asserted TTS physical identity links. Two official EYES faces, one partial ARM face, and two official backs control only their exact publisher occurrences; no official example identifies a TTS GUID copy.
- The reusable Wound gain procedure owns finite draw, leftmost-section placement, all-three-slot coverage, Health displacement, exact physical dispatch, and no-reshuffle shortfall while SEM-Q-030/031/032/036/038 prohibit visibility, terminal-slot, activation, and multi-Wound defaults. Emergency Room, Surgery Room, Medical Robot, and the generic Health procedure reuse the exact discard/gain lifecycle without changing Surgery branch order.
- Green root identity comes from the sole base `greenItemsDeck` Lua role plus exact raw full CardID/GUID/CustomDeck/FaceURL/BackURL tuples. The 30-child root is not flattened into 23 semantics: seven horizontal Heavy occurrences remain exact indexed exclusions, while only 23 regular/Backpack faces dispatch in this batch.
- The official 30-per-type count, TTS 30-child root, and licensed 30-copy aggregate independently reconcile to 23 regular and seven Heavy source occurrences without asserting a one-to-one TTS/BGA copy pairing. Matching title, color, body, source order, cell, multiplicity, licensed key, or `cardId % 100` never supplies identity.
- Five selected generated cells (0, 1, 3, 5, 7) retain full physical selectors; cells 2, 4, 6, and 8 remain literal selector-gap variants. The 3×3 parent sheet, shared `ITEM` back, Heavy faces, green Medpack tokens/slots, and overlays are not regular Green rules faces.
- All 23 physical occurrences retain 85 panel/69-region anatomy, exact ONE USE ONLY headings, 46 sentences, and 46 functional glyph occurrences. Thirty-seven exact matches remain controlled tokens; nine selected local no-matches remain literal under SEM-Q-041 rather than inheriting licensed ACTION-CARD/noIntruders fields.
- Regular Item gains enter unlimited owner-private Backpack storage; Use Item selects one exact copy, costs one Action card except the exact optional MEDKIT gain window, and dispatches by full occurrence. SEM-Q-039/040/043–045 prohibit invented payment/discard order, reshuffles, restoration ownership, Interplay glyph scope, and multi-window ordering.
- Voluntary discard never resolves an Item effect. Search returns unchosen candidates privately to each deck bottom, while Used/voluntarily discarded cards enter an Item discard pile; those destinations are not merged and no Green discard reshuffle/return is invented.
- Red root identity comes only from `redItemsDeck` GUID `9027ed` and exact raw full CardID/GUID/CustomDeck/FaceURL/BackURL tuples. All 30 children remain indexed; only 21 source-clear regular occurrences dispatch, while three explicit Heavy REMOTE DETONATOR and six MILITARY TASER class-conflict occurrences remain outside regular effect semantics.
- The Red root has two exact BackURL families: 24 children use the Red `ITEM` back and six Military Taser selectors use a Yellow `ITEM` back. Neither back is a rules face, and back color does not establish class, title, weapon, Ammo, or effect identity.
- CustomDeck 36 retains selected cells 1/4/6/7 and selector gaps 0/2/3/5 on its exact 4×2 sheet. CustomDeck 35 selects only cell 0 from a cross-family 2×2 Yellow sheet; cells 1/2/3 remain excluded gaps, including one non-rules cell. No gap is repaired by title, body, art, cell, folder, or modulo.
- All 21 regular Red occurrences preserve 87 panels/63 regions, 45 printed sentences, 27 physical functional glyphs, 23 exact matches, and four selected upper-right no-matches. The matched EXPLORING DRONE Not In Combat glyph and direct Grenade/Ammo tokens create no color-, position-, title-, or weapon-art-wide alias.
- The official count, exact root, and licensed aggregate all retain 30, while licensed 21 regular/9 Heavy matches only an aggregate boundary. The six portrait TTS Military Taser SPECIAL WEAPON occurrences are not rewritten from the official/ licensed Heavy same-title variants; SEM-Q-047 prohibits a copy/class default.
- Ammo, Grenade, and Anti-Aircraft procedures remain separate from Red card identity: finite token gain uses compatible slots; Ammo reload/full-half spending is explicit; Grenade rolls Burst +2 but is not a Burst Action; Anti-Aircraft order is temporary-private, verbally shareable/lie-able, never showable, and deterministic only at final top-token resolution.
- SEM-Q-039/040/044–050 prohibit invented Use/discard order, color-deck reshuffles, Interplay recipient scope, multi-window order, local-glyph restrictions, Military Taser class, Exploring Drone targets, Objective inspection access, and Portable Barrier Door rules. Unaffected clauses/copies remain encoded.
- Yellow root identity comes only from `yellowItemsDeck` GUID `fe68f3` and exact raw full CardID/GUID/CustomDeck/FaceURL/BackURL/UniqueBack tuples. All 30 children remain indexed; only 24 source-clear regular occurrences dispatch, while five Fire Extinguisher and one Robot Controller physical-class conflicts remain outside regular effect semantics.
- Eleven regular generated selections use exact CustomDeck 34 cells 0/3; thirteen regular direct copies use exact CustomDeck 3954/5320 faces. CustomDeck 33 cell 1 supplies five class conflicts. Five unselected cells—including one Red-root Military Taser cell and one blank cell—remain explicit gaps; no title/cell/modulo repair is allowed.
- Twenty-five root selectors use one shared Yellow Item back. Five Fire Extinguishers select cell 1 of a 2×2 `UniqueBack` sheet whose cell 0 is independently used by six Red-root Military Tasers; back color or cell cannot establish family, class, title, or effect identity.
- All 24 regular occurrences preserve 128 physical panels, 72 physical regions, 56 printed sentences, and 48 physical functional glyphs. Thirty-two exact matches remain controlled tokens; sixteen upper-right no-matches stay literal under SEM-Q-051 rather than inheriting licensed `noIntruders`, utility art, or another face’s match.
- Direct Oxygen Tank uses the selected source-bound `[oxygen]` then `[oxygenToken]` sequence while the same-title selector-gap/canonical normalization discrepancy remains explicit in `representationBoundary`; extraction records are not silently rewritten. Direct/sheet/licensed Oxygen, Phosphates, Robot Controller, Fire Extinguisher, Duct Tape, and Tools occurrences remain independent.
- Reusable Oxygen gain caps at 7; Oxygen-token use delegates gain before the enclosing Tactical Gear lifecycle returns the token exactly once. Malfunction removal preserves local target and conditional Interplay consent. Reinforce removes Noise before flipping a legal Empty Corridor and invents no caller target owner.
- Current official Duct Tape and FAQ precedence remain occurrence-scoped: the publisher face/third-Item ruling does not identify any TTS GUID. SEM-Q-053/054 prohibit a default for TTS self-placement versus One Use discard, beyond-third capacity, attachment topology, token loss, discard, Malfunction, Trade, and separation.
- SEM-Q-039/040/044/045 and SEM-Q-051–056 prohibit invented Use/discard order, Yellow-deck reshuffles, cross-Character Oxygen-token scope, immediate-window order, local-glyph restrictions, class correspondence, Duct lifecycle, Phosphates targets, and Tools Door ownership/range. Unaffected clauses/copies remain encoded.
- Action identity comes from six exact Character kit/deck roots plus the Shared Contractor root, full CardID/GUID/CustomDeck/FaceURL/BackURL/container tuples, and explicit sheet/hash/grid/cell selectors—not title, Character name alone, body similarity, folder/order/cell, source sheet, CardID modulo, licensed key, or aggregate multiplicity.
- The 55 kit-root and five Shared Contractor selectors compose exactly ten physical copies per base Character. TTS saved sequence is provenance only; setup shuffles each deck, and the Contractor’s two source roots remain distinct while forming one base deck under the official five-plus-five rule.
- CustomDeck 5674 retains 16 selected physical cells and 29 source-clear base selector gaps. CustomDeck 5675 retains base cells 10–14 while cells 0–9 and 15–44 remain expansion material. Parent sheets and the 273-reference shared back are provenance/non-operative sides, never extra rules faces.
- All 60 physical copies retain 290 panels, 164 sentences, 143 functional icon occurrences, zero-cost `Play an Action card` dispatch, and 22 printed additional-cost clauses. Twenty-eight Not In Combat occurrences are source-resolved; eight selected local upper-right morphologies remain literal under SEM-Q-057 and cannot inherit licensed `noIntruders` flags.
- Generic Action-card play and Reaction dispatchers alone own reveal, card-in-resolution, and final discard transitions. Search, Rest, and Duck reusable effects no longer double-discard their physical cards; FAQ authority keeps draw-triggered reshuffles before the resolving card enters its discard pile.
- Six printed Reaction panels remain distinct timing occurrences from their main Action effects. Eight printed COMMAND headings remain source text even though only seven licensed rows set `command=true`; Officer Channel’s nested Command lifecycle remains unresolved rather than flattened into that boolean.
- Sixty licensed rows remain independent with zero asserted TTS-copy links. Selected pixel evidence controls twenty-six literal transcription differences while stale corpus projections remain recorded in each face’s `representationBoundary`; official examples control only their exact publisher occurrences.
- SEM-Q-057–074 prohibit invented Action glyph, Command payment, Reaction priority, death/escape continuation, multi-target order, consent, nested-card, reroll, Corridor-placement, draw-shortage, Movement-interrupt, and cancellation-cost defaults. Every unaffected clause and exact copy remains encoded.
- Objective/Mission physical identity comes only from the exact `objectiveMissonDeck`, `objectivePersonalDeck`, and `missionTaskDeck` Lua roles plus raw root/full CardID/GUID/CustomDeck/FaceURL/BackURL/container tuples and explicit sheet/hash/grid/cell selectors. Five repeated OFFICIAL ORDER copies remain distinct; title, body, category/footer, folder/order/cell, modulo, Help position, licensed key, and multiplicity never identify or merge a copy.
- The three TTS roots retain 11 Mission, 20 Personal, and 8 Mission Task children. Exact player-count metadata and the scripted base boundary retain 7 + 15 + 8 competitive copies while preserving four high-count Mission and five Corporate prototype children as physical exclusions. The two Solo/Coop roots retain 12 + 26 exact excluded selectors without forcing them to the official 12-card inventory or the licensed 12-row subset.
- The 7×3 Objective sheet and 5×2 Mission Task sheet remain parent assets, not rules faces. Thirteen cells have base selectors and eighteen are base selector gaps; prototype root/bag selectors do not repair those gaps. The 33-reference Objective back is shared by Mission and Private roots, while the 11-reference Mission Task back remains separate and non-operative.
- `PERSONAL OBJECTIVE` projects to Private Objective only through accepted alias `AL-003` on its exact listed TTS footer tuples. Corporate prototype footers, the misspelled Lua role, BGA keys, and other sources receive no global alias. Mission Objective and Mission Task remain separate information/component categories even when one condition checks the other.
- All 45 official Help units remain independent. Thirty-five are fully visible; ten card occurrences are physically occluded. Only 20 visible card occurrences receive official face records. Occluded PDF text-layer metadata, BGA rows, and TTS scans never fill a hidden official title/body/icon/footer or identify a physical TTS copy.
- Objective identities remain owner-private from deal through choice. Showing is forbidden; discussion and lying are permitted. Removed identities do not become public discards, dead owners have no source-defined reveal, and source-authorized temporary inspection does not expose identities to other players, logs, accessibility output, notifications, unauthorized clients, or spectators.
- Ordinary Objective choice now locks the source order: privately remove one, retain the other, move the public marker down if possible, then draw the post-move 3/2/2/1/1 Action-card reward through the reusable draw lifecycle. Late endgame choice and reveal order remain SEM-Q-077/078 without a reward/order default.
- Fulfillment is checked after final Infection/Eclosion and preserves source grouping, actor identity, public Mission Task state, historical Escort checkbox, Escape-versus-Hibernation, escaped-after-death notes, Data immutability, Facility/Queen/Nest consequences, Reactor/Life Support state, Room/Corridor/path conditions, and exact current/TTS/licensed wording. SEM-Q-075/076 prohibit invented OR-branch commitment and “remain UNFULFILLED” timing.
- FAQ authority keeps remove-from-game outside the Entrance Effect, so all three removal transitions remain unconditional when Entrance Effects are ignored; close-Doors effects target only Doors touching the new Room.
- Random-Corridor and finite-component assignment across multiple diagram slots remains SEM-Q-011 with no player owner, spatial order, or additional randomness invented.
- Hatching and Egg Protection retain the Undiscovered-Nest question, and simultaneous Egg Protection entry retains OQ-007.
- Event reshuffles include the resolving card under FAQ authority; generic discard applies only if the card remains in resolution.
- `LEAVING THE SHELL` retains three literal no-match white rectangles while the lower-authority licensed Action-card placeholders remain a no-default variant.
- Licensed Event records remain independent variants; the Reactor Overheating movement-verb omission is authority-resolved without rewriting the BGA occurrence.
- Room Help extraction remains literal/source-local; semantic icon mappings live only in `room-icon-denotations.json`.
- Static Room prohibition graphics are persistent properties, not removable Secure/Malfunction components.
- Intruder Help dispatch preserves front icon, back count/color, finite supply, model capacity, immediate Attack order, and discard/return lifecycle separately.
- Basic Action costs and Action-card play/discard are not conflated.
- No engine, UI, networking, persistence, or serialization mapping appears in semantic data.

## Validation

Validation rejects duplicate JSON keys, broken hashes/citations, authority-precedence errors, stale vocabulary/ontology references, missing owners/visibility/timing, invalid cardinality, dangling decisions/targets/conditions, source-variant loss, partial-resolution drift, invented defaults, implementation leakage, coverage overclaims, and non-reproducible builds. Prior family controls remain locked. Objective/Mission controls reject dropped/duplicated copies, category/deck/title collapse, Private/Personal alias overreach, Mission Objective/Task and Solo/Coop leakage, sheet/cell/modulo/folder joins, selector/back inversion, player-count/icon/checkbox/AND-OR/body/punctuation/order drift, occluded-text promotion, visibility/owner/default invention, fulfillment/choice/reveal lifecycle drift, blocker or variant/authority loss, and coordinated backlog lowering. Two builds run under different hash seeds/locales and must be byte-identical.
