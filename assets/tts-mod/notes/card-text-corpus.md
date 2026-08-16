# Extracted card-text corpus

This project keeps two separate data layers:

1. `cards/` is the canonical, promotion-gated catalog.
2. `assets/tts-mod/extract/card-text-corpus.json` is the complete evidence corpus. It includes canonical records, full draft transcriptions, source/reference records, and explicitly unresolved local glyphs without pretending that every record is canonical.

## Verified baseline

The current corpus is generated from `vision-progress.json`, `low-confidence-review.json`, the canonical `cards/` sidecars, and the 49-identifier official icon glossary.

- 390 card/reference image records.
- 168 individual generated card-face crops derived from 13 excluded source sheets; no parent sheet is double-counted.
- 352 records contain nonempty rules/effect text.
- 64 records are canonical image/JSON pairs.
- 276 records are full draft card transcriptions: 142 with only recognized canonical inline tokens and 134 with one or more unresolved/local tokens.
- 48 records are card backs, help/reference material, or other non-rules/non-canonical records.
- 2 records have no transcription and remain explicit rather than guessed.
- 0 partial rules-text records after structured effect/COMMAND/REACTION panels are counted correctly.

`docs/qa/card-symbol-resolution-backlog.json` inventories 227 unresolved/local token occurrences across 136 rules-bearing image assets. Its cluster names describe visible morphology only; they are not semantic icon assignments.

## Rebuild and verify

Run from the repository root:

```bash
python3 assets/tts-mod/extract/analyze_card_extraction_coverage.py --output docs/qa/card-extraction-coverage.json --top 30
python3 assets/tts-mod/extract/build_card_text_corpus.py
python3 assets/tts-mod/extract/validate_card_text_corpus.py
python3 assets/tts-mod/extract/analyze_unresolved_symbols.py
python3 assets/tts-mod/extract/vision_validate.py
```

All production workspace invocations must be launched through `workspace run nemesis-card-corpus -- ...` so the workspace flock is held.

## Trust rules

- `verified-canonical` means the record is backed by an existing canonical sidecar.
- `draft-full` means all currently visible material rules text was transcribed without an illegible/clipped marker; it is not a promotion decision.
- `draft-text-complete-symbols-unresolved` preserves exact morphology descriptions for symbols that have not passed authoritative crop/source comparison.
- Raw `printedData` is retained without silent normalization so structured panels and unusual layouts are not flattened away.
- Every record links to the source path and source SHA-256. The validator rehashes and decodes all 390 source images and reconciles every complete/deferred ledger record.
- Canonical promotion still requires exact text, authoritative icon identity, component/side provenance, schema validity, and no unresolved source conflict.

## Selected deferred vision overlay

Worker `sol-max-direct-worker-08-20260816T065316Z` completed a staging-only native-image read of four existing corpus tuples using `openai-codex:gpt-5.6-sol` at `max` reasoning. It produced 4 blind raw records, 4 adjudicated results, 4 contact sheets, and 8 native image calls across 8 isolated session IDs. The required closure audit passed through its documented multi-session adapter; the original sealed runtime and per-call IDs remain in the worker root.

The overlay is evidence-only: all four records remain `promotionDecision: defer`, and no canonical sidecar, ledger, queue, source image, or catalog entry was changed. It materializes the selected comparison in `selectedExtraction` and `evidence.selectedExtraction` so consumers do not need to traverse worker files. It records 6 verified icon occurrences, 6 unresolved/no-match occurrences, and 1 explicit conflict with an earlier unsupported upper-right label.

Notable results:

- `attack-151_cards/card-06.png` / DEADLY CLAWS: official rendered rulebook page 32 directly matches the three circular glyphs to ADULT, DRONE, and QUEEN. The inline health-like glyph remains unnamed because the page shows no authoritative visible label for it.
- `heavy-gun-operator-045_cards/card-13.png` / DEMOLITION: the cog-like glyph matches the authoritative MALFUNCTION crop.
- `heavy-gun-operator-045_cards/card-16.png` / REPAIRS: ACTION-CARD and MALFUNCTION match; the upper-right crossed emblem remains unresolved and conflicts with the prior unsupported `notInCombat` label, which is preserved as historical evidence rather than silently removed.
- `heavy-gun-operator-045_cards/card-00.png` / ANYTHING USEFUL?: the solid chamfered body glyph matches none of the authorized green/red/yellow item crops, and the upper-right emblem matches none of the authorized not-in-combat crop.

The reusable merger is `assets/tts-mod/extract/merge_staged_vision_evidence.py`; it refuses non-deferred or invalid workers, requires exact source tuples, preserves prior snapshots, and writes only a deferred evidence overlay. Native worker roots remain local-only and are ignored by Git.
