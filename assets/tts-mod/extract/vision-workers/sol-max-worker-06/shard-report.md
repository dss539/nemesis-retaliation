# Sol Max Worker 06 — W06-001 through W06-004

## Outcome

- **Processed:** 4/4 exactly once
- **Promotable:** 0
- **Deferred:** 4
- **Non-card complete:** 0
- **Next pending:** none
- **Candidate sidecars:** none

## Native runtime

`openai-codex:gpt-5.6-sol`, reasoning `max`, session `20260815_224527_5f5db3`; four exact one-image native attachments reconciled 4 submitted / 4 returned. No auxiliary vision, Qwen, OCR canonical evidence, or model downgrade was used.

## Pixel findings

1. **W06-001 — CHAIN OF COMMAND** — action-card family, printed footer `HEAVY GUN OPERATOR`; deferred.
2. **W06-002 — CONTINUOUS FIRE** — action-card family, printed footer `HEAVY GUN OPERATOR`; deferred.
3. **W06-003 — DEMOLITION** — action-card family, printed footer `HEAVY GUN OPERATOR`; deferred.
4. **W06-004 — FORCING FIRE** — action-card family, printed footer `HEAVY GUN OPERATOR`; deferred.

All four supplied images are upright and their material text is readable. Canonical icon tokens were not promoted without direct authoritative-crop confirmation.

## Common blockers

- The shared 9×5 source sheet is established as a `FaceURL`, but generated cells 11, 12, 13, and 15 have no concrete selecting `Card`/`CardCustom` record and therefore no exact cell GUID.
- Parsed records provide only a generic shared action back, not a unique cell-specific pair for any assigned cell.
- Each card has at least one unresolved material icon: W06-001 white ship-like silhouette; W06-002 red ammo token/slot form plus unverified white A card forms; W06-003 cog-like form; W06-004 red ammo token/slot form.

## Validation and artifacts

- Assignment and live source hashes match; all four PNGs decode with expected 1052×1433 RGB metadata.
- Raw/result IDs and counts reconcile exactly; no duplicate or missing result exists.
- Pre-report deterministic validation passed with unchanged Git status/diff fingerprints and all recorded mutation targets under this worker root.
- Final post-report deterministic validation passed.

Primary artifacts:

- `metadata/runtime.json`
- `raw/W06-001.json` … `raw/W06-004.json`
- `results/W06-001.json` … `results/W06-004.json`
- `batches/pre-report-validation.json`
- `batches/final-validation.json`
- `shard-report.json`
