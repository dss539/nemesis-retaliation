# Remaining base-game source extraction roadmap

## Current closure point

- Official primary/errata PDFs inventoried: rulebook (40 pages), FAQ (4), Room Help Sheet (2), Objective Help Sheet (2).
- Card/reference evidence corpus: 390 records; 78 canonical, 250 full drafts, 10 partial, 3 no-transcription, 49 non-rules/reference.
- Base Intruder Help Sheet: both source-bound sides now extracted verbatim in `intruder-help-sheet.json`.
- Official Room Help Sheet: both pages inventoried as 25 source entries in `room-help-sheet-layout.json`; effects/notes remain pending.
- Card gaps: 2 records contain unreadable markers in operative body text; 8 partial records have markers outside operative body text; 3 records have no transcription.
- Vocabulary/taxonomy/ontology work remains intentionally unopened.

## Ordered extraction work

### P1 — Official Room Help Sheet

Extract both pages visually and structurally. Produce one source record per Room with exact title, section/type,
printed effect, options, icons, restrictions, and page position. Preserve differences from TTS Room assets.

### P2 — Official Objective Help Sheet

Extract every Mission Objective, Private Objective, Mission Task, and game-term note as a separate source record.
Preserve count thresholds, unavailable-player clauses, OR/AND grouping, annotations, and page layout. Do not collapse
same-name entries across scope or mode.

### P3 — Card-corpus gaps

Work from `card-gap-inventory.json`:

1. Resolve the 2 true operative-text gaps from pixels and applicable official component evidence.
2. Review the 8 nonbody partials to separate artwork/interface microtext from rules.
3. Classify the 3 no-transcription records as rules-bearing, card back, blank/render failure, or other component evidence.
4. Preserve all TTS/publisher/licensed-digital conflicts separately.

### P4 — Official rulebook visual obligation census

Audit all 40 rendered pages, not only the text layer. Extract normative diagrams, component anatomy, tables, card/icon
associations, ordering arrows, examples, and graphical constraints that are missing from `rulebook_text.txt`.

### P5 — Official FAQ visual confirmation

Audit all 4 rendered pages to verify numbering, scope, icon associations, examples, and expansion applicability.

### P6 — Player Help cards and duplicate source variants

Extract and deduplicate exact wording while retaining player-number and source-version differences. Do not normalize the
TTS card's phase labels against the current rulebook during extraction.

### P7 — Secondary evidence closure

Consolidate one immutable copy of BGA build 260622-1220, index its relevant data sections, and retain TTS structured
metadata as provenance/deck-role evidence. Secondary data may reveal conflicts but cannot settle them over official sources.

## Exit gate before vocabulary work

Vocabulary/aliases/taxonomy/ontology may begin only when:

- every in-scope source unit is `extracted`, `non-normative`, or an explicit `blocked` record;
- every graphical normative channel has a rendered-pixel extraction or a specific blocker;
- all card operative text gaps are closed or explicitly blocked;
- source versions and conflicts are retained independently;
- counts reconcile across PDFs, help sheets, card corpus, and structured source inventories;
- no extraction record silently embeds an alias or semantic interpretation.
