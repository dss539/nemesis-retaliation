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
- `source-registry.json` — 160 exact source tuples, hashes, versions, authority, occurrence identities, and extraction-index links used by the corpus.
- `pilots.json` — 232 validated semantic records across 21 systems; the historical filename is retained while coverage expands.
- `review-gates.json` — fifty explicit open semantic questions with alternatives; no default is adopted.
- `contradictions.json` — thirty-three source/semantic conflicts: fourteen authority-resolved, twelve unresolved, and seven preserved boundaries.
- `coverage.json` — pilot scope and the large remaining base-game semantic surface.
- `backlog.json` — 600 source-obligation units across rule records, FAQ, visual obligations, Help sheets, and independent card/reference tuples; 215 are covered, 384 pending, and one source-blocked, with overlapping variants intentionally retained.
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

The 232 records cover the original reusable-procedure set plus:

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

This is representative, **not full base-game semantic coverage**.

The backlog currently records 215 covered source obligations, 384 pending obligations, and one inherited exact-source blocker (`FACILITY RESTART`). The Event, Exploration, Robot, Intruder Attack, Queen Health, Serious Wound, and regular Green Item batches link 91 exact card/source tuples plus overlapping rule, FAQ, Help, and official visual obligations. These are source-obligation counts, not a claim that 600 distinct game effects exist.

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
- SEM-Q-040 — Green Item deck exhaustion, discard recycling, and multi-draw shortage.
- SEM-Q-041 — selected Green local draw/crossed-device glyph identities.
- SEM-Q-042 — Contamination Codes Door eligibility and scarce-token allocation.
- SEM-Q-043 — restoration-amount owner under Item Interplay.
- SEM-Q-044 — Interplay “Gaining” glyph and regular MEDKIT recipient scope.
- SEM-Q-045 — ordering of multiple gained immediate-use Item windows.

- OQ-001, OQ-003, OQ-004, OQ-007, OQ-009, SEM-Q-010, SEM-Q-025, SEM-Q-027, SEM-Q-029, SEM-Q-030, SEM-Q-031, SEM-Q-032, SEM-Q-036, SEM-Q-037, SEM-Q-038, SEM-Q-039, SEM-Q-040, SEM-Q-042, SEM-Q-043, SEM-Q-044, and SEM-Q-045 prefer official clarification. The other SEM questions require further source searching before any owner decision.

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

Validation rejects duplicate JSON keys, broken hashes/citations, authority-precedence errors, stale vocabulary/ontology references, missing owners/visibility/timing, invalid cardinality, dangling decisions/targets/conditions, source-variant loss, partial-resolution drift, invented defaults, implementation leakage, coverage overclaims, and non-reproducible builds. Event-, Exploration-, Robot-, Attack-, Queen-Health-, and Serious-Wound-specific controls retain their prior family locks. Green Item controls reject dropped/duplicated/reordered copies, repeated-title collapse, sheet/cell swaps, title/color/body/folder/order/cell/modulo/licensed joins, selector or FaceURL/BackURL drift, regular/Heavy leakage, panel/region/icon swaps, body/punctuation/order drift, optionality/owner/default invention, payment/discard/stacking/reshuffle/multi-window drift, variant/authority loss, and coordinated backlog lowering. Two builds run under different hash seeds/locales and must be byte-identical.
