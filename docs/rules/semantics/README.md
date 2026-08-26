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
- `source-registry.json` — 75 exact source tuples, hashes, versions, authority, occurrence identities, and extraction-index links used by the corpus.
- `pilots.json` — 145 validated semantic records across 18 systems; the historical filename is retained while coverage expands.
- `review-gates.json` — thirty explicit open semantic questions with alternatives; no default is adopted.
- `contradictions.json` — eighteen source/semantic conflicts: eight authority-resolved, eight unresolved, and two preserved boundaries.
- `coverage.json` — pilot scope and the large remaining base-game semantic surface.
- `backlog.json` — 600 source-obligation units across rule records, FAQ, visual obligations, Help sheets, and independent card/reference tuples; overlapping variants are intentionally retained.
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

The 145 records cover the original reusable-procedure set plus:

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

This is representative, **not full base-game semantic coverage**.

The backlog currently records 154 covered source obligations, 445 pending obligations, and one inherited exact-source blocker (`FACILITY RESTART`). The Event, Exploration, Robot, and Intruder Attack batches link all 58 exact card tuples plus overlapping rule, FAQ, and official visual obligations. These are source-obligation counts, not a claim that 600 distinct game effects exist.

## Open questions carried without defaults

- OQ-001 — Eclosion existing-hand behavior;
- OQ-002 — endgame Larva iteration timing;
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

- OQ-001, OQ-002, OQ-003, OQ-004, OQ-007, OQ-009, and SEM-Q-010 prefer official clarification. SEM-Q-001 through SEM-Q-009 and SEM-Q-011 through SEM-Q-024 otherwise require further source searching before any owner decision.

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

Validation rejects duplicate JSON keys, broken hashes/citations, authority-precedence errors, stale vocabulary/ontology references, missing owners/visibility/timing, invalid cardinality, dangling decisions/targets/conditions, source-variant loss, partial-resolution drift, invented defaults, implementation leakage, coverage overclaims, and non-reproducible builds. Event-specific controls reject dropped records, valid-source swaps, title-only joins, sentence-order changes, invented glyph defaults, lost licensed variants, authority inversion, and coordinated backlog-count lowering. Exploration-specific controls additionally reject dropped/duplicated faces, title/folder/modulo joins, source-face swaps, FaceURL/BackURL inversion, source-unit reordering, remove-from-game scope drift, invented titles/system icons/defaults, lost variants, authority inversion, and coordinated backlog lowering. Robot-specific controls reject dropped/duplicated faces, title-only joins, face/back or runtime-state inversion, wrong GUID/CardID, sentence/panel/icon reordering or loss, reveal leakage, Malfunction contradiction flattening, invented movement owners/defaults, lost variants, authority inversion, and coordinated backlog lowering. Attack-specific controls reject dropped/duplicated occurrences, repeated-title collapse, sheet/cell swaps, modulo joins, selector drift, FaceURL/BackURL inversion, applicability swaps, count-preserving badge movement, local-icon invention/loss, body/punctuation/order drift, branch flattening, lost variants, authority inversion, invented defaults/owners, and coordinated backlog lowering. Two builds run under different hash seeds/locales and must be byte-identical.
