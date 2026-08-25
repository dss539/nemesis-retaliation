# Nemesis: Retaliation taxonomy and ontology proposal

This directory is the static structural layer between the approved vocabulary and future semantic rule records.

## Files

- `taxonomy.json` — 211 source-traceable taxa, including source occurrences, definitions, copies/sets, entity/component classes, process types, states, roles, values, symbols, source identity kinds, and semantic scaffolding.
- `mappings.json` — complete mappings for all 167 controlled vocabulary terms and 501 named source-identity observations.
- `ontology.json` — 55 static relationship shapes, 27 inverse pairs, and 14 source-backed structural assertions/constraints.
- `review-gates.json` — ontology review gates plus non-blocking semantic questions carried forward.
- `independent-review.md` — four-workstream review findings and incorporated corrections.
- `validation.json` — deterministic validation result.

The reproducible builder is `scripts/build_taxonomy_ontology.py`; the validator is `scripts/validate_taxonomy_ontology.py`.

## Modeling boundaries

This layer distinguishes:

- a **Player** from the controlled **Character**;
- **Characters**, **Robots**, and **Intruders**;
- physical **cards/tokens/markers/slots** from rules information printed on them;
- **Basic Actions** from **Action cards** and their printed effects;
- generic **Attack** processes from player Actions—Opportunity Attacks are not Actions;
- **Reaction** from Action, as required by the rulebook;
- Room/Corridor/Door topology from movement/access permission;
- Item physical class, source family, and function as overlapping dimensions rather than one false disjoint tree;
- source-local named identities and technical keys from canonical game classes;
- printed symbols from the concepts/components/states they denote.

Section A/B/C and named special Rooms are represented as identity kinds under their spatial class, not as universal subclasses inferred from capitalization.

## Static relationship scope

The ontology defines structural shapes such as:

- Facility/Section/Room composition;
- Corridor endpoints, adjacency, and Door placement;
- Player–Character control;
- entity occupancy constraints;
- card/content, deck membership, zones, storage, and slot occupancy;
- state and role association;
- printed-symbol denotation;
- source occurrence → definition → physical copy/component-set provenance;
- Room Help/Room definitions, Action decks/Character roles, and icon occurrences/face definitions;
- finite supply plus timing-window, decision-owner, audience-scope, and lifecycle **classes** for later use.

It does **not** instantiate card/Room/Event effects or encode their legality and resolution.

## Explicitly deferred to semantic modeling

- triggers and conditions;
- ordered effect steps and mutations;
- costs and payment selection;
- legal target calculation;
- choice options, decline rights, and tie-breaks;
- information reveal/secrecy rules per effect;
- prevention/replacement effects;
- source-specific partial-resolution behavior;
- transition triggers and exception procedures.

Twelve timing/order, Turn/Phase, decision-owner, visibility, and lifecycle-transition relation IDs are explicitly deferred and absent from the static relation set.

Open rules questions OQ-001, OQ-002, OQ-003, OQ-004, OQ-007, and OQ-009 are carried as non-blocking semantic questions. Rest, Intruder Help transcription, Not-in-Combat associations, and Action-deck source inventory are no longer extraction blockers.

## Review status

Four independent workstreams were incorporated. They found no owner decision blocking static ontology after the corrections in `independent-review.md`. The static proposal passes its gate: deterministic validation, two-seed rebuilds, and corruption tests pass with no owner gate. Semantic modeling is now the active separate phase and must carry the six genuine semantic questions explicitly.
