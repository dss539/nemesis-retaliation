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
- Secondary evidence: immutable BGA build 260622-1220 snapshot retained and 11 tables/298 scoped records indexed; 6 TTS structured channels hashed and bounded as provenance only.
- Final extraction audit: 9/9 channels extracted or indexed, 6/6 gate criteria passed, 1 exact-source blocker retained, 0 remaining graphical source units.
- Card-gap review: all 13 former gaps adjudicated source-bound; 9 are rules-text complete, 3 are classified non-rules, and 1 exact prototype span remains explicitly blocked. SUBMACHINE GUN punctuation was recovered as a colon without altering its icon/source conflicts.
- Vocabulary and static ontology gates subsequently passed; current semantic coverage and next work are tracked in `PROJECT_STATUS.md`.

## Extraction work status

All ordered extraction work is complete. The nine-channel closure ledger is `extraction-closure-audit.json`.
The vocabulary, static ontology, and representative semantic gates subsequently passed. Semantic source-obligation expansion is active; this extraction roadmap remains the authority only for extraction closure/order.

## Exit gate before vocabulary work

Vocabulary/aliases/taxonomy/ontology could begin only when:

- every in-scope source unit is `extracted`, `non-normative`, or an explicit `blocked` record;
- every graphical normative channel has a rendered-pixel extraction or a specific blocker;
- all card operative text gaps are closed or explicitly blocked;
- source versions and conflicts are retained independently;
- counts reconcile across PDFs, help sheets, card corpus, and structured source inventories;
- no extraction record silently embeds an alias or semantic interpretation.

## Gate outcome

**PASS.** All 6 criteria above are satisfied. Canonical vocabulary and source-scoped alias work may begin. The exact prototype `FACILITY RESTART` missing span remains blocked and may not be invented by later layers.
