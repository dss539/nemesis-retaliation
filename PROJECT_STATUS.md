# Nemesis: Retaliation — Project Status

**Status date:** 2026-08-26
**Active phase:** Semantic coverage expansion (pilot gate passed)
**Active branch:** `work/card-corpus-extraction`
**Implementation status:** Frozen; a clean rewrite will begin only after rules-layer readiness and explicit approval

## Current Objective

Expand the independently reviewed semantic model from representative pilots to complete base-game source-obligation coverage while preserving variants, conflicts, and unresolved alternatives.

The current implementation remains frozen. Semantic records remain independent of any future engine/UI architecture.

## Immediate Next Deliverable

Encode the **highest-value source-clear semantic backlog** without touching blocked decisions:

- remaining setup, map, combat, Queen, Lander, procedure, Item, and component lifecycle rules not yet represented by the 145-record corpus;
- remaining source-clear card/component families outside the closed 20-card Event, 12-card Exploration, 6-card Robot, and 20-occurrence Intruder Attack families, next beginning with a mechanically bounded base Queen Health family, with explicit variants;
- Objective Help and Mission Task semantics after source-visible/occluded boundaries are preserved;
- exact FAQ overrides and per-sentence partial-resolution scope;
- source-obligation links and contradiction coverage after every batch;
- continue independent validation and source searching for the thirty open questions, but adopt no default.

Prioritize reusable procedures and cross-cutting rules before hundreds of individual component effects.

## Resume Checkpoint

- Verified semantic data checkpoint: `251b692184ad6935600c3b34faa38baefd7a5a3a` (`Add base Intruder Attack card semantics`).
- Branch `work/card-corpus-extraction` will be ten local commits ahead of `origin/work/card-corpus-extraction` after this separate progress checkpoint; nothing has been pushed. No PR or deployment exists.
- The only remaining dirty path after this progress checkpoint is `AGENTS.md`. Its protected phase update predates the checkpoint and says ten open questions instead of the verified thirty. Preserve it byte-for-byte for explicit review rather than discarding or staging it implicitly.
- Full verification passed: semantic validator with cross-seed/cross-locale rebuilds and 16 tests including Attack corruption controls; ontology validator and 4 tests; vocabulary validator; global card-corpus/vision/reproducibility validators and 24 tests; Room Help source-fidelity validator and 3 tests; FAQ/source-extraction and 9/9 closure validators; project-status validator; `git diff --check`.
- Resume with `semantic-components`: mechanically close the base Queen Health family, then expand remaining cards, Objectives/Mission Tasks, and component lifecycles while preserving variants and authority conflicts. Current source-obligation boundary is 154 covered / 445 pending / 1 source-blocked; 30 semantic questions remain no-default.

## Verified Checkpoint

### Source/card corpus

- 532 in-scope extracted assets: **148 complete + 384 deferred + 0 unaccounted**
- 390 card/reference records
- 350 records with rules/effect text
- 78 canonical image/sidecar pairs
- 259 full drafts
- 1 partial record
- 0 no-transcription records
- 52 non-rules/reference records
- Manual stratified review: **8/8 complete**
- Approved icon identifiers: **50**

### Source-extraction layer

- Extraction closure gate: **PASS**
  - 9/9 source channels extracted or indexed
  - 6/6 gate criteria passed
  - 0 remaining graphical source units
  - 1 explicit exact-source operative blocker retained
  - next phase authorized: canonical vocabulary and source-scoped aliases
- Official sources inventoried:
  - Rulebook: 40 pages
  - FAQ v1.2: 4 pages
  - Room Help Sheet: 2 pages
  - Objective Help Sheet: 2 pages
- Secondary evidence closure:
  - 4 BGA copies verified byte-identical; 1 immutable build `260622-1220` snapshot retained
  - 11 BGA tables and 298 scoped structured records indexed
  - 6 TTS structured files indexed
  - 159 Lua role records
  - 172 GMNotes tag rows / 1,267 tagged occurrences
  - 384 selected-evidence entries/runs
  - 156 corpus records explicitly preserve a BGA conflict/secondary boundary
- Player Help source: **10/10 numbered fronts extracted**
  - 1 shared functional `PASS` side
  - 1 identical instruction-text variant
  - 2 measured raster-template groups
  - 0 functional icons and 0 unreadable spans
  - explicit conflicts: TTS 10 fronts vs official 5-card inventory; obsolete phase sequence vs current rulebook
- FAQ/errata v1.2: **4/4 rendered pages extracted**
  - 59 ruling/errata units
  - 28 base-game-applicable units
  - 31 expansion-specific units retained out of base conclusions
  - 15 errata units and 44 FAQ rulings
  - 4 inline visual occurrences
  - 0 unreadable spans
- Rulebook visual census: **40/40 rendered pages classified**
  - 80 non-decorative visual units
  - 72 normative visual obligations
  - 5 worked-example visuals
  - 3 reference/navigation units
  - 0 unreadable visual spans
  - all 80 only partially represented by text extraction because graphical structure is lost
- Intruder Help Sheet: both sides extracted source-bound
- Intruder Help instructions: **18/18**
- Room Help Sheet: **25/25 entries extracted source-bound and independently locked**
  - 25 exact source projections verified
  - 25 complete audited evidence crops verified
  - 112 literal functional-icon occurrences
  - 39 effect/note icon references
  - 0 unreadable operative spans
  - corruption negative controls reject verbatim, icon, crop, provenance, unreadability, and coordinated-layout drift
- Objective Help Sheet: **45/45 source units inventoried**
  - 35 fully visible units extracted source-bound
  - 10 physically occluded units retained with explicit visibility boundaries
  - 50 full and 5 partially visible icon occurrences
  - 0 unreadable visible spans
- Card-gap review: **13/13 source tuples adjudicated**
  - 9 rules-text-complete records
  - 1 explicit exact-source operative blocker
  - 3 classified non-rules components/placeholders
  - 1 operative correction recovered (`SUBMACHINE GUN`: colon)
  - 0 remaining no-transcription records
- Four licensed-digital BGA snapshots inventoried and confirmed byte-identical
- `scripts/validate_source_extraction.py`: **passed with 0 failures**

Machine-readable evidence: `docs/rules/source-extraction/validation.json`.


### Semantic schema and expanding corpus — independently locked and passed

- 75 exact source registry tuples
- 26 semantic-only state/zone/position/visibility nodes
- 145 pilot records across 18 systems
- 83 source-backed
- 62 source-backed with open questions
- 448 source assertions / 591 structured conditions and guards
- 672 ordered operations
- 73 actor-owned decisions / 158 information policies
- 6 explicit costs / 177 target specifications
- 74 preserved source-variant references
- 30 open semantic questions with explicit alternatives and defaults prohibited
- 18 registered conflicts: 8 authority-resolved, 8 unresolved, 2 preserved boundaries
- base Event family: **20/20 identities represented**
  - 20 exact Event scan occurrences
  - 20 licensed-digital Event occurrences retained as variants
  - 4 official visible component occurrences
  - 20 Event semantic records / 20 exact Event backlog tuples
- base Exploration family: **12/12 untitled identities represented**
  - 12 exact TTS CardID/GUID/FaceURL scan occurrences and 1 shared BackURL occurrence
  - 12 licensed-digital Exploration occurrences retained as variants
  - 3 official visible occurrences across 2 component identities
  - 46 exact printed sentences / 12 source-local diagrams / 60 functional icon occurrences
  - 12 Exploration semantic records / 12 exact Exploration backlog tuples
  - 0 generated sprite-sheet cells and 0 selector gaps in the mechanically derived base family
- base Robot family: **6/6 identities represented**
  - 6 exact TTS full-CardID/GUID/FaceURL scan occurrences and 1 shared non-operative BackURL occurrence
  - 6 licensed-digital Robot occurrences retained as variants
  - 2 official visible face occurrences across 2 component identities
  - 24 physical panels / 12 operative rules panels / 13 printed options
  - 16 exact printed sentences / 23 functional icon occurrences
  - 6 Robot-face semantic records / 6 exact Robot backlog tuples
  - 7 new reusable setup, reveal, Activation, movement, Tactical Gear, and Malfunction-placement records; existing `SEM-ROBOT-MALFUNCTION-001` remains unresolved under `SEM-Q-010`
  - shared back, Lua model/helper state, two prototype cards, three expansion Robot cards, and four Security Robot Room name collisions remain excluded from the six rules faces
- base Intruder Attack family: **20/20 mechanically selected physical occurrences represented**
  - 19 exact generated-cell full-CardID/GUID/CustomDeck/FaceURL occurrences plus 1 direct Blood Sense occurrence
  - 8 printed titles with multiplicities preserved, including 6 distinct Bite copies; no title/cell/folder/modulo join
  - 1 shared non-operative BackURL, 1 parent 5×4 source sheet, and 1 unused selector-gap `SUMMONING` cell explicitly excluded from rules-face counts
  - 69 physical panels / 29 operative effect panels / 54 exact printed sentences
  - 57 literal applicability badges projected source-scoped from page-32 Adult/Drone/Queen templates, plus 13 independently resolved inline icons; all 55 selected no-match rows remain intact
  - 15 licensed structured variants linked across 20 physical occurrences, 3 official-visible face counterparts, and 1 official-visible back counterpart retained independently
  - 20 Attack-face semantic records plus reusable finite Contamination gain and exact dispatch from `SEM-INT-004`; five new no-default questions preserve Fury scope, dead-target continuation, Blood Sense timing, Deadly Claws Wound order, and MISS applicability
  - three expansion Attack decks, the parent sheet, shared back, unused `SUMMONING` cell, and duplicate evidence references remain excluded from the 20 base rules occurrences
- all 18 Intruder Help instructions represented and row-locked
- all 25 Room Help entries represented, plus generic Use Room and cross-cutting Room constraints
- all 112 source-local Room Help functional-icon occurrences mapped source-scoped without changing extraction records
- 600 source-obligation backlog units
  - 154 pilot-covered
  - 445 pending
  - 1 inherited exact-source blocker
- full base-game semantic coverage explicitly not claimed
- four-workstream independent review incorporated
- cross-seed/cross-locale byte-identical rebuilds and expanded adversarial corruption tests pass
- `scripts/validate_semantic_pilots.py`: **passed with 0 failures**

### Taxonomy/ontology — independently reviewed and passed

- 211 source-traceable taxa / 9 roots
- all 167 controlled terms mapped exactly once
- all 501 named identity observations mapped as source identities
- 50 printed-symbol denotations
- 55 static relationship shapes / 27 inverse pairs
- 14 source-backed structural assertions and constraints
- 15 semantic-scaffolding taxa for later zones, timing, decisions, visibility, lifecycle, and finite supply
- all 8 accepted aliases projected
- 0 ontology owner gates after four-workstream independent review
- 12 semantic relation IDs explicitly deferred from the static layer
- two-seed byte-identical rebuild validation and expanded corruption negative controls pass
- no triggers, ordered effect steps, costs, target selection, or state mutations encoded
- `scripts/validate_taxonomy_ontology.py`: **passed with 0 failures**

### Vocabulary proposal

- 1,853 observed source-term occurrences / 1,194 normalized exact-string keys
- 643 named-identity source occurrences / 501 exact-string groups
- 167 controlled vocabulary entries
  - 50 accepted existing icon-glossary terms
  - 117 authority-derived canonical-label proposals
- 8 alias entries
  - 8 accepted explicit/source-scoped aliases
  - 0 proposed aliases awaiting owner review
- 5 explicit non-alias guardrails
- 0 open review gates; taxonomy/ontology is authorized
- `scripts/validate_vocabulary_proposal.py`: **passed with 0 failures**

## Completed Milestones

- Downloaded, classified, and reconciled the base-game TTS asset tree.
- Completed bounded card/reference extraction for all in-scope images.
- Built a provenance-rich card-text evidence corpus with explicit canonical, draft, partial, missing, and non-rules states.
- Re-derived the official icon glossary and recorded reviewed source-scoped artwork resolutions without generalizing by appearance.
- Completed an eight-item manual review sample and applied all corrections.
- Extracted both Intruder Help Sheet sides without introducing canonical vocabulary.
- Extracted all 25 official Room Help Sheet entries with effects, notes, literal functional-icon occurrences, and reproducible visual evidence; an independent 25-entry audit found no material discrepancy, four incomplete crop extents were corrected, and a pinned fidelity lock plus corruption suite now enforces the result.
- Extracted the official Objective Help Sheet at its source boundary: all 45 units inventoried, all visible wording retained, physical occlusions explicit, repeated page terms preserved, and hidden text-layer data not promoted to visible-face evidence.
- Closed all 13 card-gap reviews at their source boundary: nine complete rules reads, three non-rules classifications, one exact-source blocker, and one recovered punctuation correction; prior selected worker evidence remains immutable history.
- Completed a blind rendered-page census of all 40 official rulebook pages and recorded 80 visual units with explicit text-layer coverage, including setup/map topology, component/card anatomy, token/die state keys, worked examples, and the 49-icon glossary.
- Extracted all 59 official FAQ/errata v1.2 units from four pages, retaining exact two-column section scope, 28 base-applicable versus 31 expansion-specific rulings, 15 errata, 44 Q&A rulings, and four source-local inline glyphs.
- Extracted all ten TTS Player Help fronts and their shared functional PASS side; proved one instruction-text variant and two raster-template groups, retained FaceURL/BackURL roles, and recorded count/phase-sequence conflicts with current official sources.
- Consolidated licensed-digital build 260622-1220 into one immutable snapshot, indexed 11 tables/298 scoped records, and closed six TTS structured channels as secondary provenance with explicit count/name/conflict boundaries.
- Passed the final nine-channel extraction closure audit: every source channel is extracted/indexed, all six gate criteria pass, no graphical units remain, and the one exact-source blocker remains explicit.
- Built and validated the vocabulary layer: 1,853 source occurrences, 501 named-identity groups, 167 controlled entries, 8 accepted aliases, and 5 non-alias guardrails; VG-001 and VG-002 are resolved.
- Built, independently reviewed, corrected, and validated the static taxonomy/ontology: 211 taxa, complete term/identity/alias mappings, 55 relationship shapes, 14 static constraints, semantic scaffolding, two-seed deterministic rebuilds, and adversarial negative controls; no owner gate remains.
- Built, independently reviewed, corrected, and validated an implementation-neutral 13-record semantic pilot across nine systems with exact source tuples, semantic state/zone nodes, explicit authority/timing/ownership/visibility/costs/targets/operations/transitions/partial resolution, two variants, seven conflicts, and nine no-default questions.
- Expanded the corpus to 24 records / 16 systems with Objective choice, Intruder/Event/Cleanup phases, generic Event resolution, Bag Development, Doors, Noise, Intruder Attacks, Health/Wounds, and Tactical Gear; covered source obligations rose from 17 to 25.
- Expanded and independently audited the corpus to 73 records / 18 systems: all 18 Intruder Help instructions, all 25 Room effects, generic Use Room, all 112 Room icon denotations, Robot/Data/Autodestruction/Nest constraints, exact FAQ overrides, and corrected per-Corridor Noise/Attack ordering; covered source obligations rose to 71 while eleven questions remain no-default.
- Closed the 20-card base Event family mechanically by TTS card ID/source tuple rather than title, retained 20 licensed variants and four official visible occurrences, encoded 88 exact printed sentences plus reusable Event procedures, and advanced source-obligation coverage to 102 while sixteen scoped questions remain no-default.
- Closed the entire 12-card base Exploration family mechanically from the root TTS deck and exact CardID/GUID/FaceURL tuples, retained the shared back, 12 licensed variants and three official visual occurrences, encoded 46 printed sentences plus 12 diagrams/60 icon occurrences without inventing titles, and advanced source-obligation coverage to 119 while seventeen questions remain no-default.
- Closed the six-card base Robot family mechanically from the root TTS role and exact full CardID/GUID/FaceURL/container tuples, retained one shared back, six licensed variants, two official visible face occurrences, literal runtime-state/prototype/expansion boundaries, 24 panels/16 sentences/23 icons, and advanced source-obligation coverage to 132 while twenty-five questions remain no-default.
- Closed the 20-occurrence base Intruder Attack family mechanically from the raw root TTS `DeckCustom`, retained repeated physical copies, 19 generated cells plus one direct face, one shared back, one unused selector-gap cell, 57 source-scoped applicability badges, 15 licensed variants and three official face counterparts, encoded 54 sentences plus reusable Contamination gain, and advanced source-obligation coverage to 154 while thirty questions remain no-default.
- Created the closed source inventory, card-gap inventory, secondary-source inventory, Room layout inventory, roadmap, and deterministic validator.

## Remaining Work — Ordered

1. **Semantic coverage expansion** — encode source-clear general rules/procedures, then component effects, while preserving questions and variants.
2. **Semantic closure audit** — completeness, contradiction, authority, citation, terminology, and scenario coverage.
3. Define implementation-readiness criteria and seek explicit approval before a clean rewrite.

Detailed phase plan: `docs/rules/source-extraction/extraction-roadmap.md`.

## Phase Gates

### Gate before vocabulary, aliases, taxonomy, or ontology — PASSED

All of the following are true:

- every in-scope source unit is `extracted`, `non-normative`, or explicitly `blocked`;
- every graphical normative channel has rendered-pixel evidence or a specific blocker;
- every operative card-text gap is closed or explicitly blocked;
- source versions and conflicts remain independent;
- counts reconcile across PDFs, help sheets, card corpus, and structured inventories;
- no extraction record silently embeds an alias or semantic interpretation.

### Gate before semantic modeling — PASSED

- controlled vocabulary and aliases reviewed;
- source terms and source-local morphology remain traceable;
- static taxonomy/ontology independently reviewed and validated;
- static relationships/cardinalities and timing/decision/visibility/lifecycle scaffold boundaries agreed;
- semantic relation IDs are explicitly deferred into this phase rather than pre-populated with guesses;
- unresolved source questions remain explicit.

### Gate before implementation

- source-backed rules coverage judged solid enough by the project owner;
- representative semantic rules and executable scenarios validate the model;
- contradiction, completeness, citation, terminology, and source-variant audits pass;
- new architecture is chosen independently of the legacy implementation;
- project owner explicitly approves starting the rewrite.

## Current Decisions and Boundaries

- Base game only; expansion extraction is deferred.
- Preserve official, TTS, licensed-digital, and other source variants independently.
- Official FAQ/errata takes precedence over the official rulebook where applicable.
- Component scans and secondary sources do not silently overwrite official text.
- Do not create canonical vocabulary or semantics during extraction.
- Artwork and interface microtext are not rules unless their placement/function establishes that they are normative.
- Current implementation files are not rules authority.
- No implementation, PR, merge, or deployment work is currently authorized.

## Known Current Blockers and Open Evidence

- One prototype `FACILITY RESTART` face visibly ends a condition at “Systems must be”; no following mark is recoverable from the exact pixels, and materially different same-title/current-official variants cannot be substituted.
- Vocabulary gates `VG-001` and `VG-002` are resolved; `PERSONAL OBJECTIVE` remains source-scoped and `Drilling Room` aliases `DRILLING STATION` with both official labels preserved.
- Thirty semantic/source questions remain explicit: OQ-001, OQ-002, OQ-003, OQ-004, OQ-007, OQ-009, and SEM-Q-001 through SEM-Q-024. They block only affected clauses/records, not unrelated coverage work.
- SEM-Q-011 retains the source-unspecified assignment of random Corridor draws and scarce finite components across multiple Exploration diagram slots; no player owner, spatial order, or additional randomization is adopted.
- SEM-Q-012 through SEM-Q-019 retain Robot reveal/effect availability, movement ownership, Exploration Noise, Medical choices, Securing Door/supply behavior, Server Room context, and Technical marker scope without defaults. SEM-Q-020 through SEM-Q-024 retain Attack scope, continuation, timing, Wound assignment, and no-badge applicability without defaults. Neoflesh-only FAQ answers remain excluded from base conclusions.
- The 25 Room Help entries versus 23 Room tiles relationship is unresolved.
- Source/version conflicts remain in several card families and must not be flattened.
- Genuine rules ambiguities remain in `docs/rules/open-questions.md`; some stale extraction blockers there must later be re-audited against newly collected evidence.

## Tracker Ownership

Use these records for different questions:

| Question | Authority |
|---|---|
| What phase are we in, what is next, and what is blocked? | `PROJECT_STATUS.md` |
| What is the ordered extraction plan? | `docs/rules/source-extraction/extraction-roadmap.md` |
| What exact source/gap counts exist? | `docs/rules/source-extraction/*.json` and `docs/rules/source-extraction/validation.json` |
| What is the detailed backlog and historical checkpoint trail? | `todo.md` |
| What rules are established? | `docs/rules/readme.md` and numbered rule files |
| What source ambiguities remain? | `docs/rules/open-questions.md` |
| What card-corpus procedures and trust states apply? | `assets/tts-mod/notes/card-text-corpus.md` |
| What was durably checkpointed? | Git on `work/card-corpus-extraction` |

`PROJECT_STATUS.md` should stay concise. Update it after meaningful changes to the active phase, immediate next deliverable, blockers, gates, or verified headline counts. Link to detailed evidence rather than copying logs.

## Resume Checklist

1. Use the `nemesis-card-corpus` workspace and hold its root lock.
2. Read this file.
3. Read `docs/rules/source-extraction/extraction-roadmap.md`.
4. Read the relevant source inventory/extraction record.
5. Load the relevant Hermes skills.
6. Perform source-bound extraction without normalization.
7. Run `python3 scripts/validate_source_extraction.py`, `python3 scripts/validate_vocabulary_proposal.py`, `python3 scripts/validate_taxonomy_ontology.py`, and `python3 scripts/validate_project_status.py` through `workspace run`.
8. Update this file only if material status changed.
9. Commit and push only within the authorized boundary; do not open a PR or deploy without explicit approval.
