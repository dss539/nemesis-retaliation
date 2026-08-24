# Remaining base-game source extraction roadmap

## Current closure point

- Official primary/errata PDFs inventoried: rulebook (40 pages), FAQ (4), Room Help Sheet (2), Objective Help Sheet (2).
- Card/reference evidence corpus: 390 records; 78 canonical, 259 full drafts, 1 partial, 0 no-transcription, 52 non-rules/reference.
- Base Intruder Help Sheet: both source-bound sides now extracted verbatim in `intruder-help-sheet.json`.
- Official Room Help Sheet: all 25 entries extracted source-bound in `room-help-sheet.json` (112 literal functional-icon occurrences, 39 effect/note references, 0 unreadable operative spans).
- Official Objective Help Sheet: all 45 source units inventoried in `objective-help-sheet.json`; 35 fully visible units extracted, 10 physical occlusions retained explicitly, 0 unreadable visible spans.
- Official rulebook visual channel: all 40 pages classified in `rulebook-visual-obligations.json`; 80 visual units (72 normative, 5 worked examples, 3 reference), 0 unreadable spans.
- Official FAQ/errata v1.2: all 4 pages and 59 ruling/errata units extracted in `faq-v1.2-source-extraction.json`; 28 base-applicable and 31 expansion-specific units, 0 unreadable spans.
- Player Help source: all 10 numbered fronts and the shared functional PASS side extracted in `player-help-source-extraction.json`; one exact text variant, two raster-template groups, 0 unreadable spans.
- Card-gap review: all 13 former gaps adjudicated source-bound; 9 are rules-text complete, 3 are classified non-rules, and 1 exact prototype span remains explicitly blocked. SUBMACHINE GUN punctuation was recovered as a colon without altering its icon/source conflicts.
- Vocabulary/taxonomy/ontology work remains intentionally unopened.

## Ordered extraction work

### P1 — Secondary evidence closure

Consolidate one immutable copy of BGA build 260622-1220, index all base-relevant structured sections, and prove the four
collected copies are exact duplicates. Close TTS structured metadata as provenance/deck-role evidence with source hashes,
record counts, and applicability boundaries. Secondary data may reveal conflicts but cannot settle them over official sources.

### P2 — Extraction closure audit

Reconcile every in-scope official page, help-sheet unit, card/reference source, Player Help occurrence, and secondary data
channel as `extracted`, `non-normative`, or explicitly `blocked`. Verify all counts, source hashes, conflicts, authority order,
and remaining blockers before opening vocabulary work.

## Exit gate before vocabulary work

Vocabulary/aliases/taxonomy/ontology may begin only when:

- every in-scope source unit is `extracted`, `non-normative`, or an explicit `blocked` record;
- every graphical normative channel has a rendered-pixel extraction or a specific blocker;
- all card operative text gaps are closed or explicitly blocked;
- source versions and conflicts are retained independently;
- counts reconcile across PDFs, help sheets, card corpus, and structured source inventories;
- no extraction record silently embeds an alias or semantic interpretation.
