# Sol Max Vision Shard Report — W01-024

- **Processed:** 1 (`W01-024`)
- **Decision:** **DEFER**
- **Runtime:** native `openai-codex:gpt-5.6-sol`, reasoning `max`, session `20260815_213825_14ef69`; one native-image turn; no auxiliary vision, OCR canonical evidence, Qwen, or downgrade.
- **Source:** `assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-00.png`
- **SHA-256:** `de97374d9cc8ed9f9141a4539386fd6b8979b4230f4eee8ae04925622fc07fed`
- **Decode:** 1052×1433 RGB PNG, one frame, upright.

## Fresh pixel read

- **Title:** `ANYTHING USEFUL?`
- **Body:**
  ```text
  Move.
  If you Explored a new Room, draw 1 Item for
  each [ICON: solid white chamfered eight-sided polygon with no visible internal mark] in that Room.
  Keep 1 and discard the rest.
  ```
- **Footer:** `RECON`
- **Proposed classification:** Recon character Action-card face. The `heavy-gun-operator` directory is provenance for a shared multi-owner sheet, not ownership evidence.

## Why deferred

1. The upper-right glyph is a large red X over a mostly occluded short white horizontal form. `notInCombat` is plausible, but the visible pixels and authoritative glossary do not independently establish that semantic identity.
2. The inline glyph is a solid white chamfered/eight-sided polygon with no internal marks. It does not match the glossary's colored Item badges or any other defined entry.
3. The shared FaceURL sheet and common Action BackURL are resolved, but cell 0 cannot safely be assigned to one TTS Card GUID by the unreliable CardID-to-cell shortcut.

No semantic icon tokens were emitted and no sidecar was staged or promoted.

## Provenance and drift

Blind observations were persisted before reading predecessor or TTS metadata. Worker-02 raw was retained only as attempt/failure provenance and did not influence this read or decision.

During closure, the supervisor expanded `assignment.json` from 1 to 12 assets. W01-024's `(assetId, sourcePath, SHA-256)` tuple and live bytes remained identical. The 11 appended IDs were not processed because this delegated shard explicitly says to process exactly W01-024 and stop. The supervisor then made a metadata-only rewrite with the same 12 tuples, marked this shard `stopped-partial`, recorded 1 merged result and 11 remaining assets, and superseded it with `sol-max-worker-04`. Drift evidence is in `metadata/assignment-drift-001.json`, `metadata/assignment-drift-002.json`, and `metadata/assignment-drift-adjudication-001.json`.

## Validation

- Pre-report artifact validation passed with zero JSON failures.
- Source hash/decode, exact path, exact visible text, defer state, empty semantic-icon-token set, one-ID count reconciliation, and native runtime contract all passed.
- Every mutation issued by this session targeted `sol-max-worker-03/` only. Concurrent supervisor updates to shared ledgers and worker-02 files were observed; worker-03 did not make them.
- Final report self-validation: **passed** — 16 JSON files parsed; final assignment hash/tuple/status, source hash/decode, defer invariants, report existence, and worker-local mutation confinement all matched.

## Reports

- JSON: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/vision-workers/sol-max-worker-03/shard-report.json`
- Markdown: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/vision-workers/sol-max-worker-03/shard-report.md`
- Normalized result: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/vision-workers/sol-max-worker-03/results/W01-024.json`
- Blind raw: `/home/smithers/nemesis-retaliation/assets/tts-mod/extract/vision-workers/sol-max-worker-03/raw/W01-024.json`
