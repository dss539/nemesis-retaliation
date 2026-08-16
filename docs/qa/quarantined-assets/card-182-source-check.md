# card-182 source and classification check

Asset: `assets/tts-mod/extract/v2-dl/tree/unsorted/card-182.jpg`
TTS provenance: `BackURL` of top-level `CardCustom` GUID `c1175c`; paired `FaceURL` is the already-approved `cards/reference/objectives-help-sheet.jpg`.
Native vision: `openai-codex:gpt-5.6-sol`, session `20260815_041444_9e380a`, one image, zero tool calls.
Official source: `docs/rulebooks/Nemesis_RT_Objectives_Sheet.pdf`, two square pages.

The pixel read identified an upright composite headed `GAME TERMS` with PRIVATE OBJECTIVE cards. The official PDF text corroborates the visible private-objective titles and wording. A deterministic normalized grayscale comparison against 120-DPI renders gave:

- card-182 vs official page 1: correlation 0.140282
- card-182 vs official page 2: correlation 0.567139
- approved paired face vs official page 1: correlation 0.392486
- approved paired face vs official page 2: correlation 0.147232

The best rotation in every comparison was 0 degrees. This supports classifying card-182 as Objectives Help Sheet page 2.

Deferred content uncertainties:

- The TTS layout itself overlaps and clips portions of `INSIDER INFORMATION` and `CREW'S FAVORITE`; official PDF extraction identifies the full titles, but clipped TTS text must not be silently reconstructed.
- A recurring white pawn/flame-like mark over blue oval rings beside player-count thresholds is not in the canonical icon glossary.
- The square `A` glyph in the repeated Objective Choice instruction was not a confirmed morphological match to a canonical icon in this read.

These uncertainties affect exact content transcription, not the page-level component classification.
