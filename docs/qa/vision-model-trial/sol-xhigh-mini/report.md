# GPT-5.6 Sol X-High mini native-vision test

Date: 2026-08-15
Route: `openai-codex:gpt-5.6-sol`
Reasoning: `xhigh`
Input: native Hermes CLI `--image`, one image per fresh safe-mode session
Cases: 2 frozen human-approved icon-stress cases reused unchanged from the Luna Max and Sol High benchmarks

## Result

This deliberately tiny test does not qualify a production model. It tests two known icon traps only.

- Mean score: 69.099/100.
- Comparator means on the identical cases: Sol High 68.859/100; Luna Max 64.792/100.
- Median latency: 64.314 seconds; calls completed in 48.717–79.911 seconds.
- Exact proposed sidecars: 0/2.
- One promoted sidecar contained a high-confidence semantic icon error.
- One valid approved card was conservatively deferred.

### Chain of Command (`c03`)

Score: 52.416/100. Sol transcribed the prose but could not identify the inline `lander` glyph, described it literally, and deferred at medium overall confidence. This is a safe abstention rather than a false promotion, but it is still a false deferral and not an exact sidecar.

### Automatic Shotgun (`c05`)

Score: 85.782/100. Sol identified `ammoToken` and `ammoSlot`, but substituted `shootDieAmmoLoss` for the approved `shootDieCritical` and promoted the result at high overall confidence. It also changed punctuation/line structure and added a noncanonical `typeLine` field to the minimal sidecar candidate. This remains a release-blocking semantic-icon failure for unattended canonical promotion.

## Scoped conclusion

X-High produced essentially the same outcome as High on this slice (+0.240 points) while nearly doubling median latency (64.314 versus 33.057 seconds). It repeated both behavioral outcomes: safe abstention on the Lander trap and confident false promotion on the Shoot-die trap. This tiny result gives no evidence that X-High is preferable to High for production extraction, and neither is safe for unattended sidecar promotion.

## Evidence

- Frozen sample/hashes: `sample.json`
- Frozen prompt: `prompt-template.txt`, `rendered-prompt.txt`
- Runner/scorer: `run_sol_xhigh_mini.py`, `score_sol_xhigh_mini.py`
- Raw records: `runs/`
- Parsed outputs: `outputs/`
- Machine scores: `scores.json`
- Exact-sidecar check: `exact-sidecar-check.json`
- Session verification: `session-verification.json`

The session records are `20260815_080952_b85aa4` and `20260815_080952_dbd7b2`. Session DB inspection confirmed two unique `gpt-5.6-sol` sessions, each with one user image request, one assistant response, one API call, and zero tool calls. The launch records preserve `reasoning=xhigh`, safe mode, native image attachment, prompt hash, source hash, and latency.
