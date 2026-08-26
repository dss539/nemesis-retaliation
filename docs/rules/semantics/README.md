# Nemesis: Retaliation semantic rules corpus

This directory is the first implementation-neutral semantic layer built over the approved vocabulary and independently reviewed static ontology.

## Files

- `semantic-rule.schema.json` — closed JSON Schema shape for one semantic rule record.
- `semantic-vocabulary.json` — semantic-only states, temporary zones, deck positions, and visibility scopes that must not be confused with static ontology classes/processes.
- `room-icon-denotations.json` — source-scoped semantic projection of all 112 Room Help functional-icon occurrences; literal extraction remains unchanged.
- `event-source-index.json` — mechanically derived closure of the 20 base Event face occurrences against TTS role/card IDs, source bytes, corpus/backlog tuples, official visible occurrences, and the licensed-digital table; title-only joins are prohibited.
- `exploration-source-index.json` — mechanically derived closure of all 12 untitled base Exploration faces, their exact TTS CardID/GUID/FaceURL and shared BackURL provenance, 46 printed sentences, 12 diagrams, 60 source-local icon occurrences, official/FAQ occurrences, licensed variants, and backlog tuples; title/folder/modulo joins are prohibited.
- `source-registry.json` — 44 exact source tuples, hashes, versions, authority, occurrence identities, and extraction-index links used by the corpus.
- `pilots.json` — 111 validated semantic records across 18 systems; the historical filename is retained while coverage expands.
- `review-gates.json` — seventeen explicit open semantic questions with alternatives; no default is adopted.
- `contradictions.json` — thirteen source/semantic conflicts: four authority-resolved, seven unresolved, and two preserved boundaries.
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

The 99 records cover the original reusable-procedure set plus:

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
33. all 12 mechanically closed untitled base Exploration face occurrences, with exact placement/reminder/Entrance/lifecycle order, source-local six-slot diagrams and icon identities, one licensed-digital variant per face, three official visible occurrences, and occurrence-based dispatch from the generic Exploration Sequence.

This is representative, **not full base-game semantic coverage**.

The backlog currently records 119 covered source obligations, 480 pending obligations, and one inherited exact-source blocker (`FACILITY RESTART`). The Event and Exploration batches link all 32 exact card tuples plus overlapping rule, FAQ, and official visual obligations. These are source-obligation counts, not a claim that 600 distinct game effects exist.

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

- OQ-001, OQ-002, OQ-003, OQ-004, OQ-007, OQ-009, and SEM-Q-010 prefer official clarification. SEM-Q-001 through SEM-Q-009 and SEM-Q-011 otherwise require further source searching before any owner decision.

## Fidelity boundaries exercised

- Reaction is not an Action.
- Search candidates/unchosen Items remain private and return to their respective deck bottoms despite shorter card wording.
- Rest preserves exact source variants rather than rewriting one face from another.
- Event impossibility applies per sentence and continuation is mandatory.
- All 20 Event faces preserve exact movement/main/secondary sentence order; generic draw/discard is not duplicated into each face.
- All 12 Exploration faces remain untitled and are keyed by stable occurrence identity; no BGA number, filename, folder, display name, or invented slug becomes a printed title.
- Exploration diagrams retain exact source-local Corridor/Noise slots, Room markers, reminder glyph occurrences, three independent remove-from-game sentences, and the paired non-operative back. No inactive/active system icon is inferred where none is printed.
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

Validation rejects duplicate JSON keys, broken hashes/citations, authority-precedence errors, stale vocabulary/ontology references, missing owners/visibility/timing, invalid cardinality, dangling decisions/targets/conditions, source-variant loss, partial-resolution drift, invented defaults, implementation leakage, coverage overclaims, and non-reproducible builds. Event-specific controls reject dropped records, valid-source swaps, title-only joins, sentence-order changes, invented glyph defaults, lost licensed variants, authority inversion, and coordinated backlog-count lowering. Exploration-specific controls additionally reject dropped/duplicated faces, title/folder/modulo joins, source-face swaps, FaceURL/BackURL inversion, source-unit reordering, remove-from-game scope drift, invented titles/system icons/defaults, lost variants, authority inversion, and coordinated backlog lowering. Two builds run under different hash seeds/locales and must be byte-identical.
