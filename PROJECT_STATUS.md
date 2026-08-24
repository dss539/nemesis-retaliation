# Nemesis: Retaliation — Project Status

**Status date:** 2026-08-24
**Active phase:** Base-game source extraction
**Active branch:** `work/card-corpus-extraction`
**Implementation status:** Frozen; a clean rewrite will begin only after rules-layer readiness and explicit approval

## Current Objective

Finish source-bound extraction of all remaining base-game evidence **before** creating a canonical vocabulary, aliases, taxonomy, ontology, or semantic rules layer.

The current implementation is not being repaired or extended. It is historical behavior/QA evidence only.

## Immediate Next Deliverable

Extract the official **two-page Objective Help Sheet** into source-bound records:

- one record per Mission Objective, Private Objective, Mission Task, and game-term note;
- exact title, wording, punctuation, annotations, and `AND`/`OR` grouping;
- literal icon occurrences without canonical naming;
- Number-of-Characters threshold as printed, without aliasing it during extraction;
- unavailable-player clauses and scoped explanatory notes;
- page/grid position and rendered-page evidence;
- explicit source conflicts or unreadable spans.

Do not collapse duplicate display names or infer semantic equivalence across modes, source versions, or component families.

## Verified Checkpoint

### Source/card corpus

- 532 in-scope extracted assets: **148 complete + 384 deferred + 0 unaccounted**
- 390 card/reference records
- 350 records with rules/effect text
- 78 canonical image/sidecar pairs
- 250 full drafts
- 10 partial records
- 3 no-transcription records
- 49 non-rules/reference records
- Manual stratified review: **8/8 complete**
- Approved icon identifiers: **50**

### Source-extraction layer

- Official sources inventoried:
  - Rulebook: 40 pages
  - FAQ v1.2: 4 pages
  - Room Help Sheet: 2 pages
  - Objective Help Sheet: 2 pages
- Intruder Help Sheet: both sides extracted source-bound
- Intruder Help instructions: **18/18**
- Room Help Sheet: **25/25 entries extracted source-bound**
  - 112 literal functional-icon occurrences
  - 39 effect/note icon references
  - 0 unreadable operative spans
- Card-gap inventory: 13 records
  - 2 true operative-text gaps
  - 8 nonbody marker/structure gaps
  - 3 no-transcription classifications
- Four licensed-digital BGA snapshots inventoried and confirmed byte-identical
- `scripts/validate_source_extraction.py`: **passed with 0 failures**

Machine-readable evidence: `docs/rules/source-extraction/validation.json`.

## Completed Milestones

- Downloaded, classified, and reconciled the base-game TTS asset tree.
- Completed bounded card/reference extraction for all in-scope images.
- Built a provenance-rich card-text evidence corpus with explicit canonical, draft, partial, missing, and non-rules states.
- Re-derived the official icon glossary and recorded reviewed source-scoped artwork resolutions without generalizing by appearance.
- Completed an eight-item manual review sample and applied all corrections.
- Extracted both Intruder Help Sheet sides without introducing canonical vocabulary.
- Extracted all 25 official Room Help Sheet entries with effects, notes, literal functional-icon occurrences, and reproducible visual evidence.
- Created the closed source inventory, card-gap inventory, secondary-source inventory, Room layout inventory, roadmap, and deterministic validator.

## Remaining Work — Ordered

1. **Official Objective Help Sheet** — one record per Mission Objective, Private Objective, Mission Task, and game-term note.
2. **Card-corpus gaps** — close or explicitly block two operative gaps; classify eight nonbody gaps and three missing records.
3. **Rulebook visual obligation census** — inspect all 40 rendered pages for normative information lost by the text layer.
4. **FAQ visual confirmation** — inspect all four rendered pages for numbering, scope, examples, icons, and applicability.
5. **Player Help variants** — deduplicate exact wording while preserving player-number and source-version differences.
6. **Secondary-source closure** — consolidate one immutable BGA build snapshot and index relevant data sections; retain TTS metadata as provenance only.
7. **Extraction closure audit** — reconcile every source unit as extracted, non-normative, or explicitly blocked.
8. **Canonical vocabulary and aliases** — begin only after the extraction gate passes.
9. **Taxonomy/ontology**, then **semantic rules layer**.
10. Define implementation-readiness criteria and seek explicit approval before a clean rewrite.

Detailed phase plan: `docs/rules/source-extraction/extraction-roadmap.md`.

## Phase Gates

### Gate before vocabulary, aliases, taxonomy, or ontology

All of the following must be true:

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

- `FACILITY RESTART` and `SUBMACHINE GUN` retain true operative unreadable spans.
- Eight other partial records require artwork/metadata versus rules classification.
- Three no-transcription records require component classification.
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
