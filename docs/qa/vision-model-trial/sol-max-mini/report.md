# GPT-5.6 Sol Max mini native-vision test

Date: 2026-08-15
Route: `openai-codex:gpt-5.6-sol`
Reasoning: `max`
Input: native Hermes CLI `--image`, one image per fresh safe-mode session
Cases: 2 frozen human-approved icon-stress cases reused unchanged from the Luna Max, Sol High, and Sol X-High benchmarks

## Result

This deliberately tiny test does not qualify a production model. It tests two known icon traps only.

- Mean score: 80.166/100.
- Comparator means on the identical cases: Sol X-High 69.099/100; Sol High 68.859/100; Luna Max 64.792/100.
- Median latency: 87.737 seconds; calls completed in 76.733–98.741 seconds.
- Exact proposed sidecars: 0/2.
- Both outputs were promoted at high overall confidence with a wrong semantic icon.

### Chain of Command (`c03`)

Score: 74.549/100. Sol recovered the prose with high text similarity but substituted `autodestruction` for the approved inline `lander` glyph. It reported no uncertainty and promoted the result at high overall/icon confidence. The higher score reflects better prose fidelity and the expected promote decision, not a safe canonical result.

### Automatic Shotgun (`c05`)

Score: 85.782/100. Sol identified `ammoToken` and `ammoSlot`, but substituted `shootDieAmmoLoss` for the approved `shootDieCritical`. It reported no uncertainty and promoted the result at high overall/icon confidence. It also changed punctuation/line structure and added a noncanonical `typeLine` field to the minimal sidecar candidate.

## Scoped conclusion

Max scored substantially higher than High and X-High on this two-case slice because it promoted both cards and transcribed Chain of Command more closely. Operationally, it was less safe: both high-confidence promotions contained a semantic icon error. Max also raised median latency to 87.737 seconds, 2.65 times High's 33.057 seconds. The result does not support unattended canonical promotion or establish Max as the preferred extraction setting; direct authoritative icon-image comparison and deterministic sidecar validation remain mandatory.

## Evidence

- Frozen sample/hashes: `sample.json`
- Frozen prompt: `prompt-template.txt`, `rendered-prompt.txt`
- Runner/scorer: `run_sol_max_mini.py`, `score_sol_max_mini.py`
- Raw records: `runs/`
- Parsed outputs: `outputs/`
- Machine scores: `scores.json`
- Exact-sidecar check: `exact-sidecar-check.json`
- Session verification: `session-verification.json`

The session records are `20260815_080952_010ea8` and `20260815_080953_335c25`. Session DB inspection confirmed two unique `gpt-5.6-sol` sessions, each with one user image request, one assistant response, one API call, and zero tool calls. The launch records preserve `reasoning=max`, safe mode, native image attachment, prompt hash, source hash, and latency.
