# Extracted card-text corpus

This project keeps two separate data layers:

1. `cards/` is the canonical, promotion-gated catalog.
2. `assets/tts-mod/extract/card-text-corpus.json` is the complete evidence corpus. It includes canonical records, full draft transcriptions, source/reference records, and explicitly unresolved local glyphs without pretending that every record is canonical.

## Verified baseline

The current corpus is generated from `vision-progress.json`, `low-confidence-review.json`, the canonical `cards/` sidecars, the 49-identifier official icon glossary, `extract/selected-card-text-evidence.json`, and `docs/qa/card-symbol-semantic-resolutions.json`. The last two files are tracked sources of truth for selected reviewed overlays and source-scoped semantic icon aliases; ignored worker roots are optional provenance and are not needed to rebuild or validate the corpus.

- 390 card/reference image records.
- 168 individual generated card-face crops derived from 13 excluded source sheets; no parent sheet is double-counted.
- 350 records contain nonempty rules/effect text.
- 78 records are canonical image/JSON pairs.
- 249 records are full draft card transcriptions: 118 with only recognized canonical inline tokens and 131 with one or more unresolved/local tokens.
- 49 records are card backs, help/reference material, or other non-rules/non-canonical records.
- 3 records have no transcription and remain explicit rather than guessed.
- 11 records remain partial because at least one material span is explicitly illegible or clipped.

`docs/qa/card-symbol-resolution-backlog.json` inventories 513 unresolved/local token occurrences across 202 corpus or selected-evidence assets after excluding approved source-scoped semantic resolutions. Its cluster names describe visible morphology only; they are not semantic icon assignments.

## Manual sample adjudication

The five-item owner review completed and amended on 2026-08-22 is recorded in
`docs/qa/card-rules-manual-review-2026-08-22.json` and projected into each reviewed corpus
record as `evidence.manualReview`. S01 and S08 passed. S02 exposed a review-package omission only:
the canonical sidecar and corpus already stored the upper-right `notInCombat` icon. S05 records
`[ammoToken]` and normalizes its pre-release purple exclamation result to
`[burstDieAdditionalEffects]`. S06 normalizes the same purple legacy result plus its older red
ammunition-magazine result to `[burstDieAdditionalEffects]` and `[shootDieAmmoLoss]`, while
preserving literal art descriptions and the reviewed colon in provenance. The source-scoped policy
and all affected legacy weapon tuples are in `docs/qa/card-symbol-semantic-resolutions.json`.

## Rebuild and verify

Run from the repository root:

```bash
python3 assets/tts-mod/extract/analyze_card_extraction_coverage.py --output docs/qa/card-extraction-coverage.json --top 30
python3 assets/tts-mod/extract/build_card_text_corpus.py
python3 assets/tts-mod/extract/validate_card_text_corpus.py
python3 assets/tts-mod/extract/analyze_unresolved_symbols.py
python3 assets/tts-mod/extract/vision_validate.py
python3 assets/tts-mod/extract/check_card_text_corpus_reproducibility.py
```

All production workspace invocations must be launched through `workspace run nemesis-card-corpus -- ...` so the workspace flock is held.

## Trust rules

- `verified-canonical` means the record is backed by an existing canonical sidecar.
- `draft-full` means all currently visible material rules text was transcribed without an illegible/clipped marker; it is not a promotion decision.
- `draft-text-complete-symbols-unresolved` preserves exact morphology descriptions for symbols that have not passed authoritative crop/source comparison.
- `printedData` preserves text, structure, and punctuation while using canonical semantic icon tokens for source tuples approved in `docs/qa/card-symbol-semantic-resolutions.json`. Literal pre-release artwork remains in the source image, raw/selected vision evidence, and projected resolution provenance; unregistered lookalikes remain unresolved.
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

The reusable merger is `assets/tts-mod/extract/merge_staged_vision_evidence.py`; it refuses non-deferred or invalid workers, requires exact source tuples, preserves prior snapshots, updates the durable registry atomically by stable run identity, and then rebuilds the corpus. Re-merging the same validated run is idempotent. Native worker roots remain local-only and are ignored by Git; registry and corpus validation never require them.
