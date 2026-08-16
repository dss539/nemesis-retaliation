# TTS Mod Assets

This directory contains the Tabletop Simulator source save, parsed metadata, downloaded base-game assets, and the operational notes used to extract and validate them.

## Current status

- Base-game v2 asset tree is complete: 444 files, approximately 0.93 GB.
- Do not re-download the asset set unless the existing files are lost or a newer source is deliberately selected.
- Expansion content is intentionally excluded for now.
- Vision-based transcription uses native Sol Max in one persistent verified session, normally with 2–4 explicitly labeled images per turn and separate persisted results per asset. One-image turns are reserved for dense/large assets, strict gates, focused checks, or confusion retries.
- Eighteen card JSON entries are cataloged and all 18 have been human-reviewed. The count excludes card backs and rejected prototype components. Automatic Shotgun has a documented official-versus-TTS conflict; its canonical JSON representation remains a human decision.

Project-level progress and open work are tracked in [`../../todo.md`](../../todo.md).

## Source authority

TTS assets are extraction inputs, not automatic canonical game data. During routine card review,
validate directly against the card image and established icon glossary. Do not perform an official-
source cross-check or request an extra consultation unless confidence is low, something is unknown,
or the available evidence conflicts. When one of those triggers applies:

1. Transcribe the asset exactly.
2. Cross-reference the current applicable official FAQ/errata, rulebook, and official component references.
3. Use the most authoritative and up-to-date applicable official source for canonical data.
4. Preserve conflicting source text as provenance.
5. Escalate unclear supersession, applicability, or interpretation to a human and record the decision.

## Directory map

- `extract/` — source save and extraction work products
- `extract/v2/` — parsed object, Lua-role, and classification metadata
- `extract/v2-dl/tree/` — downloaded and categorized base-game asset tree
- `notes/extraction.md` — detailed extraction history, binary format, classification rules, cleanup log, and expansion recovery notes
- `notes/card-extraction.md` — card-reading, icon, punctuation, rotation, and source-fidelity lessons

QA evidence such as comparison images and source audits belongs in [`../../docs/qa/`](../../docs/qa/), not in these operational notes.

## Resume guide

For TTS extraction or classification work:

1. Read this file.
2. Read [`notes/extraction.md`](notes/extraction.md) for the detailed workflow and known pitfalls.
3. Read [`../../todo.md`](../../todo.md) for current work and gates.
4. Load the `extract-game-mod-assets` skill.

For card transcription work, also read [`notes/card-extraction.md`](notes/card-extraction.md) and the canonical icon glossary at [`../../docs/rules/icon-glossary.md`](../../docs/rules/icon-glossary.md).

## Documentation placement

Follow the repository-wide policy in [`../../readme.md`](../../readme.md) → “Documentation
placement.” Within this workspace, keep this file as the entry point, put topic-specific operating
knowledge under `notes/`, and keep generated/extracted artifacts under `extract/`. Specific audits
and comparison evidence remain under `docs/qa/`.

When an audit reveals a reusable lesson, add only the generalized procedure to the relevant topic
note and link to the audit as evidence. Keep card-by-card findings, screenshots, crops, hashes, and
one-time verification details in `docs/qa/`. Keep current counts, blockers, and approval gates only
in `todo.md`.
