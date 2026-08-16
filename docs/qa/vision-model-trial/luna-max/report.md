# Luna Max native-vision experiment

Date: 2026-08-15
Model: `openai-codex:gpt-5.6-luna`
Reasoning: `max`
Input: native Hermes CLI `--image` attachment
Cases: 12

## Result

Luna Max is useful for secondary OCR and review triage, but it is not reliable enough to create or promote canonical Nemesis asset sidecars unattended.

Aggregate score: 82.120/100.
Human-approved card mean: 85.180/100; median: 94.000/100.
Exact dense-sheet comparator: 72/100, versus the prior Sol result of 88/100 on the same image and conservative rubric (16 points lower).

The aggregate conceals the production-critical failures:

- Five of eight approved cards were marked high-confidence `promote`, but none of those five proposed sidecars exactly matched the approved sidecar.
- The sole exact proposed sidecar was Bulletproof Vest, which Luna unnecessarily deferred because it treated decorative graphics as unresolved symbols.
- Chain of Command confidently mapped `[lander]` to `[character]`, moved the printed COMMAND heading into a sidecar type line, and lowercased printed `Character`.
- Automatic Shotgun recognized `shootDieCritical` but failed to identify `ammoToken` and `ammoSlot` and deferred.
- Handgun failed to identify `ammoSlot` and deferred.
- The Player 6 help card omitted `END OF ROUND` from the body/sidecar while reporting high confidence.
- Explosives dropped the final printed period.
- Move Quietly and Computer Skills polluted otherwise correct minimal sidecars with owner/footer text as extra canonical fields.
- The deliberately ambiguous creature image had low identity confidence but high overall/category confidence and was marked `promote`, a critical abstention failure.

## Case scores

| Case | Tier | Score | Decision | Key result |
|---|---|---:|---|---|
| c01 | historical dense-sheet comparator | 72.000 | defer | Strong layout/completeness; player-count icons misclassified, symbol/text errors; Sol scored 88 on same image. |
| c02 | approved Explosives | 99.860 | promote | Correct icons and structure; final period omitted. |
| c03 | approved Chain of Command | 73.424 | promote | Confident semantic icon error: `lander` → `character`; sidecar structure wrong. |
| c04 | approved Move Quietly | 98.000 | promote | Text/icons correct; footer inserted as extra `lowerCenter`. |
| c05 | approved Automatic Shotgun | 56.160 | defer | `shootDieCritical` correct; `ammoToken`/`ammoSlot` unresolved. |
| c06 | approved Player 6 help card | 98.988 | promote | OCR mostly correct; `END OF ROUND` omitted from body and sidecar. |
| c07 | approved Bulletproof Vest | 90.000 | defer | Exact sidecar, but false deferral over decorative graphics. |
| c08 | approved Handgun | 67.007 | defer | Text exact; `ammoSlot` unresolved. |
| c09 | approved Computer Skills | 98.000 | promote | Text/icons correct; owner/footer inserted as extra `typeLine`. |
| c10 | unresolved Objectives sheet page 2 | 77.000 | defer | Correctly deferred clipping/non-glossary symbols; incomplete/questionable text and no page-2 identity. |
| c11 | known Life Support texture | 90.000 | promote | Correct `lifeSupportActive`; category only `map`, not `tokens/status`. |
| c12 | ambiguous creature art | 65.000 | promote | Good literal description but false promotion despite low identity confidence. |

## Throughput

All 12 calls completed and parsed. Sequential-equivalent latency was 1,356.579 seconds:

- Mean: 113.048 seconds
- Median: 85.888 seconds
- p95: 295.447 seconds
- Minimum: 15.761 seconds
- Maximum: 370.170 seconds on the dense help sheet

Max reasoning is therefore materially slower on dense sheets and still did not improve the direct comparator beyond the earlier Sol result.

## Recommendation

Do not replace the established Sol-based native-vision workflow with Luna Max for canonical extraction. Do not use Luna confidence or its `promote` decision as an unattended gate.

Luna can be used as:

- a secondary OCR reading;
- a queue-triage signal;
- a second opinion on ordinary prose;
- a literal visual-description assistant for non-card art.

Every Luna-derived canonical candidate still needs independent icon comparison, exact punctuation/text validation, strict minimal-sidecar schema validation, and a separate classification/provenance check. Dense sheets and ambiguous non-card assets should remain deferred by policy.

## Reproducibility and evidence

- Frozen protocol: `protocol.md`
- Frozen sample and SHA-256 values: `sample.json`
- Prompt template and full rendered prompt: `prompt-template.txt`, `rendered-prompt.txt`
- Runner and scorer: `run_luna_max_trial.py`, `score_luna_max_trial.py`
- Raw run records: `runs/`
- Parsed outputs: `outputs/`
- Manual scoring criteria: `manual-scores.json`
- Aggregate machine-readable scores: `scores.json`
- Redacted Hermes session exports: `sessions/`
- Session verification: `session-verification.json`

Session verification confirmed 12 unique sessions, `gpt-5.6-luna`, reasoning effort `max`, one API call per case, and zero tool calls. The images were supplied by the CLI's native `--image` path; auxiliary vision was not used.

## Limitations

This is a targeted 12-image project benchmark, not a universal vision leaderboard. Four nonstandard cases were manually scored with frozen criteria; those details are explicit in `manual-scores.json`. The Player 6 case had no canonical title gold in its minimal sidecar, so its visible title was not penalized. Automatic Shotgun is intentionally difficult and has a separately documented official-versus-TTS conflict, but Luna's missed ammo glyphs remain direct pixel/icon failures independent of that conflict.
