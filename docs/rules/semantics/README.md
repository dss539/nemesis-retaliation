# Nemesis: Retaliation semantic rules pilot

This directory is the first implementation-neutral semantic layer built over the approved vocabulary and independently reviewed static ontology.

## Files

- `semantic-rule.schema.json` — closed JSON Schema shape for one semantic rule record.
- `source-registry.json` — exact source tuples, hashes, versions, authority, and extraction-index links used by pilots.
- `pilots.json` — 13 representative rules across nine systems.
- `review-gates.json` — seven explicit open semantic questions; no default is adopted.
- `coverage.json` — pilot scope and the large remaining base-game semantic surface.
- `backlog.json` — 600 source-obligation units across rule records, FAQ, visual obligations, Help sheets, and independent card/reference tuples; overlapping variants are intentionally retained.
- `validation.json` — deterministic validation report.

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

## Pilot coverage

The 13 records cover:

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
13. endgame triggers and checks.

This is representative, **not full base-game semantic coverage**.

The backlog currently records 17 pilot-covered source obligations, 582 pending obligations, and one inherited exact-source blocker (`FACILITY RESTART`). These are source-obligation counts, not a claim that 600 distinct game effects exist.

## Open questions carried without defaults

- OQ-001 — Eclosion existing-hand behavior;
- OQ-002 — endgame Larva iteration timing;
- OQ-003 — Starting Player transfer over nonparticipants;
- OQ-004 — mid-Turn death advancement;
- OQ-007 — simultaneous multi-Intruder Secure consumption;
- OQ-009 — Nest placement before discovery;
- SEM-Q-001 — Duck and Cover replacement target when multiple other Characters are present.

The first six prefer official clarification. SEM-Q-001 requires more source searching before any owner decision.

## Fidelity boundaries exercised

- Reaction is not an Action.
- Search candidates/unchosen Items remain private and return to their respective deck bottoms despite shorter card wording.
- Rest preserves exact source variants rather than rewriting one face from another.
- Event impossibility applies per sentence and continuation is mandatory.
- Hatching’s Undiscovered-Nest case remains unresolved.
- Basic Action costs and Action-card play/discard are not conflated.
- No engine, UI, networking, persistence, or serialization mapping appears in semantic data.

## Validation

Validation rejects duplicate JSON keys, broken hashes/citations, authority-precedence errors, stale vocabulary/ontology references, missing owners/visibility/timing, invalid cardinality, dangling decisions/targets/conditions, source-variant loss, partial-resolution drift, invented defaults, implementation leakage, coverage overclaims, and non-reproducible builds. Two builds run under different hash seeds/locales and must be byte-identical.
