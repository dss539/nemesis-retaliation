# Nemesis: Retaliation — Project Status

**Status date:** 2026-08-24
**Active phase:** Canonical vocabulary and source-scoped aliases (extraction gate passed)
**Active branch:** `work/card-corpus-extraction`
**Implementation status:** Frozen; a clean rewrite will begin only after rules-layer readiness and explicit approval

## Current Objective

Build a source-traceable canonical vocabulary and source-scoped alias registry from the now-closed base-game extraction layer.

The current implementation remains frozen. Taxonomy/ontology relationships and semantic effect modeling remain later phases.

## Immediate Next Deliverable

Resolve the **two genuine vocabulary owner-review gates**, one at a time:

1. Decide whether `PERSONAL OBJECTIVE` on the listed prototype/TTS faces is a source-scoped alias of final official `Private Objective`.
2. Decide whether official-rulebook `Drilling Room` is an alias of the official component/FAQ title `DRILLING STATION`.

After each decision, update the alias registry and review-gate record with exact evidence. Taxonomy/ontology remains blocked until both are resolved and vocabulary validation reports zero open gates.

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


### Vocabulary proposal

- 1,853 observed source-term occurrences / 1,194 normalized exact-string keys
- 643 named-identity source occurrences / 501 exact-string groups
- 167 controlled vocabulary entries
  - 50 accepted existing icon-glossary terms
  - 117 authority-derived canonical-label proposals
- 8 alias entries
  - 6 accepted explicit/source-scoped aliases
  - 2 proposed aliases awaiting owner review
- 5 explicit non-alias guardrails
- 2 open review gates; taxonomy/ontology has not started
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
- Built and validated the first vocabulary proposal: 1,853 source occurrences, 501 named-identity groups, 167 controlled entries, 8 aliases, 5 non-alias guardrails, and 2 explicit owner-review gates; no taxonomy/ontology artifacts exist.
- Created the closed source inventory, card-gap inventory, secondary-source inventory, Room layout inventory, roadmap, and deterministic validator.

## Remaining Work — Ordered

1. **Resolve two vocabulary owner-review gates** and approve the controlled term/alias layer.
2. **Taxonomy/ontology** — define classes and relationships only after vocabulary validation reports zero open gates.
3. **Semantic rules layer** — model timing, choices, visibility, costs, targets, and state transitions after ontology review.
4. Define implementation-readiness criteria and seek explicit approval before a clean rewrite.

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

### Gate before semantic modeling

- controlled vocabulary and aliases reviewed;
- source terms and source-local morphology remain traceable;
- component taxonomy reviewed;
- ontology relationships, cardinalities, timing, decision ownership, visibility, and lifecycle concepts agreed;
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
- Vocabulary review gates `VG-001` (`PERSONAL OBJECTIVE`) and `VG-002` (`Drilling Room`) require project-owner decisions before taxonomy/ontology.
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
7. Run `python3 scripts/validate_source_extraction.py` and `python3 scripts/validate_project_status.py` through `workspace run`.
8. Update this file only if material status changed.
9. Commit and push only within the authorized boundary; do not open a PR or deploy without explicit approval.
