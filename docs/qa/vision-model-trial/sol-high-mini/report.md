# GPT-5.6 Sol High mini native-vision test

Date: 2026-08-15
Route: `openai-codex:gpt-5.6-sol`
Reasoning: `high`
Input: native Hermes CLI `--image`, one image per fresh safe-mode session
Cases: 2 frozen human-approved stress cases reused unchanged from the Luna Max benchmark

## Result

This deliberately tiny test does not qualify a production model. It tests two known icon traps only.

- Mean score: 68.859/100 (Luna Max on the identical two cases: 64.792/100).
- Median latency: 33.057 seconds; both calls ran concurrently and completed in 31.748–34.367 seconds.
- Exact proposed sidecars: 0/2.
- One promoted sidecar was not exact and contained a high-confidence semantic icon error.
- One valid approved card was conservatively deferred.

### Chain of Command (`c03`)

Score: 52.868/100. Sol transcribed the prose correctly but could not identify the inline `lander` glyph, described it literally, and deferred. This is safer than Luna Max's high-confidence false promotion of the same glyph as `character`, although it is still a false deferral and not an exact sidecar.

### Automatic Shotgun (`c05`)

Score: 84.850/100. Sol correctly identified `ammoToken` and `ammoSlot`, improving substantially over Luna Max on those symbols. However, it confidently substituted `shootDieAmmoLoss` for the approved `shootDieCritical`, changed punctuation, and promoted the sidecar with high confidence. This is a release-blocking semantic-icon failure for unattended canonical promotion.

## Scoped conclusion

Sol High is faster and slightly better than Luna Max on this two-case stress slice, but it is not safe as an unattended sidecar promoter. Its useful behavior is mixed: conservative abstention on one ambiguous glyph, but a confident semantic die-icon substitution on the other. Keep direct authoritative icon-image comparison and deterministic sidecar validation as mandatory gates.

## Evidence

- Frozen sample/hashes: `sample.json`
- Frozen prompt: `prompt-template.txt`, `rendered-prompt.txt`
- Runner/scorer: `run_sol_high_mini.py`, `score_sol_high_mini.py`
- Raw records: `runs/`
- Parsed outputs: `outputs/`
- Machine scores: `scores.json`
- Session verification: `session-verification.json`

The two session records are `20260815_080303_46a94e` and `20260815_080335_f23e48`. Session DB inspection confirmed two unique `gpt-5.6-sol` sessions with one user image request and one assistant response each, and no tool messages. The launch records preserve `reasoning=high`, safe mode, native image attachment, prompt hash, source hash, and latency.
