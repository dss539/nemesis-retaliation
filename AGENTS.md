# Nemesis: Retaliation — Rules Corpus and Future Rewrite

## Mission

Build a source-faithful, reviewable rules layer for the base game of *Nemesis: Retaliation*. A new digital implementation will be designed and built from scratch only after the rules layer is as solid as reasonably achievable.

**Current implementation work is out of scope.** The existing web game is a legacy prototype and may be inspected only as historical behavior or QA evidence. Its code, data, architecture, and live behavior are not authority for rules, vocabulary, ontology, or the future rewrite.

## Start Here

1. Read `PROJECT_STATUS.md` for current state, next work, blockers, and authoritative tracker locations.
2. Read `docs/rules/source-extraction/extraction-roadmap.md` for the ordered extraction phase.
3. Read `docs/rules/readme.md` for rules-corpus authority and record conventions.
4. Read `AGENTS-SUPPLEMENT.md` for documentation placement rules.
5. Load any relevant Hermes skill before acting.

Do not infer current status from historical checkpoints in `todo.md`, old implementation documents, or the live site.

## Current Strategy — Mandatory

Work in this order:

1. Extract every remaining in-scope base-game source.
2. Preserve each source, edition, and conflicting variant independently.
3. Close or explicitly block every operative transcription gap.
4. Create a canonical vocabulary and controlled aliases.
5. Build a taxonomy or ontology.
6. Build the semantic rules layer.
7. Define readiness criteria for a clean implementation.
8. Start the new implementation only after explicit project-owner approval.

Do **not** begin vocabulary, alias, taxonomy, ontology, semantic-model, architecture, engine, UI, networking, or implementation work ahead of this sequence.

## Authority and Source Discipline

For rules questions, use this precedence:

1. Applicable official FAQ/errata.
2. Official rulebook.
3. Official help sheets and visible component text.
4. Documented project interpretation in `docs/rules/`.
5. Explicitly declared adaptation.
6. Unresolved question — never silently convert this into a rule.

Source-bound TTS scans and licensed-digital data are evidence, not automatic authority over official sources. Preserve conflicts verbatim. Never combine wording merely because two effects appear similar.

During extraction:

- preserve exact wording, punctuation, grouping, layout, labels, icons, and source provenance;
- use source-local occurrence IDs only as evidence locators, not canonical terms;
- distinguish operative rules from artwork, interface decoration, microtext, and flavor text;
- mark genuinely unreadable operative content rather than reconstructing it;
- do not introduce canonical aliases or semantic interpretation into source records;
- keep expansion material out of the base-game scope unless separately authorized.

## Project Status and Tracker Ownership

- `PROJECT_STATUS.md` — concise current state, next action, blockers, phase gates, and tracker map. **This is the first-stop status authority.**
- `docs/rules/source-extraction/extraction-roadmap.md` — ordered work for the current extraction phase.
- `docs/rules/source-extraction/*.json` — exact machine-readable source inventory, gaps, provenance, and validation counts.
- `todo.md` — detailed backlog and historical checkpoints; not the first-stop status summary.
- `docs/rules/open-questions.md` — genuine unresolved source ambiguities.
- `docs/rules/` — established human-readable rule records; implementation behavior is not authority.
- Git — durable checkpoint and remote synchronization state.

Update `PROJECT_STATUS.md` whenever the active phase, next task, blocker, readiness gate, or verified headline counts materially change. Link to authoritative detail rather than duplicating long evidence or procedures.

## Active Workspace

Rules/card source work uses the task workspace:

- Workspace root: `/home/smithers/projects/nemesis-card-corpus/`
- Repository worktree: `/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation/`
- Branch: `work/card-corpus-extraction`
- Canonical lock: `/home/smithers/projects/nemesis-card-corpus/.workspace.lock`

Every worker must hold the workspace's exclusive nonblocking root flock for its full lifetime. Use `workspace run nemesis-card-corpus -- ...` for commands. Do not create a Hermes profile for this work without explicit permission.

## Current Source Set

Official base-game research sources are local and gitignored under `docs/rulebooks/`:

- `Nemesis_RT_Rulebook_official.pdf` — 40 pages
- `Nemesis_RT_FAQ_v1.2.pdf` — 4 pages
- `Nemesis_RT_Rooms_Sheet.pdf` — 2 pages
- `Nemesis_RT_Objectives_Sheet.pdf` — 2 pages
- `rulebook_text.txt` and `faq_text.txt` — extraction aids, not substitutes for rendered-page inspection

The card/reference evidence corpus and extraction provenance are under `assets/tts-mod/extract/`. Start with `assets/tts-mod/notes/card-text-corpus.md` and `docs/rules/source-extraction/README.md`.

## Current Phase

The active phase is **base-game source extraction before vocabulary design**.

The immediate deliverable is a page-by-page visual obligation census of all 40 official rulebook pages. Render each page at a fixed recorded resolution and extract normative diagrams, tables, component anatomy, icon associations, ordering arrows, examples, and graphical constraints that are absent or structurally lost in the text layer. Preserve page/region evidence and source-local occurrences; do not begin canonical naming or semantic normalization.

See `PROJECT_STATUS.md` and `docs/rules/source-extraction/extraction-roadmap.md` for the verified checkpoint and subsequent order.

## Extraction Verification

After source-extraction changes, run:

```bash
workspace run nemesis-card-corpus -- \
  bash -lc 'cd repos/nemesis-retaliation && \
    python3 scripts/validate_source_extraction.py && \
    python3 scripts/validate_project_status.py'
```

For card-corpus changes, also run the focused tests and the documented global corpus/vision validation commands in `assets/tts-mod/notes/card-text-corpus.md`.

Do not claim completion from a successful write alone. Verify source hashes, counts, required records, deterministic outputs, and visual artifacts where applicable.

## Legacy Implementation Boundary

The legacy prototype remains in `index.html`, `js/`, `css/`, and related design/QA files; the historical live site is <https://dss539.github.io/nemesis-retaliation/>. It is frozen as implementation work for the current phase.

Allowed uses:

- historical QA evidence;
- identifying past misunderstandings or missing rules;
- preserving useful non-authoritative test scenarios;
- researching prior design decisions that may later be reconsidered.

Disallowed uses during the rules phase:

- treating `js/data.js` or `js/engine.js` as source truth;
- repairing legacy implementation bugs;
- extending legacy UI, networking, content, or architecture;
- normalizing source evidence to match current code;
- assuming the future rewrite will reuse the legacy architecture.

One future-design invariant already confirmed by the project owner is that Rooms are regular pointy-top hexagons, never octagons; all six edges retain visible Corridor spacing, and illegal destinations are not offered. This remains a future fidelity requirement, not authorization to implement it now.

## Git and External Actions

- Repository: <https://github.com/dss539/nemesis-retaliation>
- Commit identity: Derrick Southerland `<dss539@users.noreply.github.com>`
- Active rules branch: `work/card-corpus-extraction`
- `main` and the GitHub Pages deployment contain the legacy implementation.

Do not open a pull request, merge, deploy, or modify production without explicit direct approval. Push only when requested or when the user has explicitly authorized that push boundary.
