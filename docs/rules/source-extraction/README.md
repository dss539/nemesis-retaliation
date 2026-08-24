# Base-game source extraction

This directory closes the **extraction layer** before any canonical vocabulary, alias registry, taxonomy,
ontology, or semantic rule model is designed.

## Rules

1. Preserve each source and version independently.
2. Transcribe printed wording, punctuation, layout, labels, and source-local visual occurrences.
3. Source-local occurrence IDs are evidence locators, **not canonical terms**.
4. Do not merge TTS, official PDF, licensed-digital, or other wording merely because the effects appear similar.
5. Record authority and provenance for every extraction.
6. Mark actual unreadable operative material explicitly; do not classify artwork microtext as rules.
7. Implementation files are not sources of rule truth.
8. Base game only. Expansion sources require a separate extraction scope.

## Files

- `base-source-inventory.json` — closed inventory of current base-game source channels and their extraction status.
- `faq-v1.2-source-extraction.json` — full four-page FAQ/errata extraction with base-game versus expansion applicability preserved.
- `intruder-help-sheet.json` — verbatim source-bound extraction of both base Intruder Help Sheet sides.
- `room-help-sheet-layout.json` — visual page/grid inventory of all 25 printed Room entries.
- `room-help-sheet.json` — complete source-bound extraction of all 25 Room effects, notes, literal functional-icon occurrences, and visual evidence.
- `objective-help-sheet-layout.json` — page/layout and visibility inventory for 45 Objective Help source units.
- `objective-help-sheet.json` — source-bound extraction of 35 fully visible units plus explicit pixel/text-layer boundaries for 10 physically occluded card occurrences.
- `player-help-source-extraction.json` — ten numbered Player Help fronts, shared functional PASS side, template equivalence, TTS roles, and source conflicts.
- `rulebook-visual-obligations.json` — blind rendered-page census of all 40 official rulebook pages and explicit comparison against text extraction.
- `card-gap-adjudications.json` — source-bound pixel decisions for all 13 former card-gap records, with artwork/rules boundaries and immutable prior-read provenance.
- `card-gap-inventory.json` — closed projection of those 13 reviews: 9 rules-text-complete, 3 classified non-rules, and 1 exact-source operative blocker.
- `secondary-source-inventory.json` — licensed-digital and TTS structured evidence, explicitly kept below official authority.
- `extraction-roadmap.md` — ordered remaining work and the gate before vocabulary design begins.

The source extraction layer may retain literal repeated strings and variant names. Deduplication, aliases,
controlled terms, entity classes, relationships, and semantic effect structures are deliberately deferred.
