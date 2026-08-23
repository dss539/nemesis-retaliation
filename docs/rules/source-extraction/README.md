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
- `intruder-help-sheet.json` — verbatim source-bound extraction of both base Intruder Help Sheet sides.
- `room-help-sheet-layout.json` — visual inventory of all 25 printed Room entries; individual effects remain pending.
- `card-gap-inventory.json` — the 10 partial and 3 no-transcription card records, separated by operative versus non-operative gaps.
- `secondary-source-inventory.json` — licensed-digital and TTS structured evidence, explicitly kept below official authority.
- `extraction-roadmap.md` — ordered remaining work and the gate before vocabulary design begins.

The source extraction layer may retain literal repeated strings and variant names. Deduplication, aliases,
controlled terms, entity classes, relationships, and semantic effect structures are deliberately deferred.
