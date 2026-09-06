# Nemesis: Retaliation — Project TODO

Detailed backlog and historical checkpoint ledger for the project. Read `PROJECT_STATUS.md` first
for the current phase, immediate next task, blockers, and readiness gates. Update this file for detailed
backlog changes or durable checkpoint history; do not make it duplicate the concise status summary. Read
`AGENTS.md` and `AGENTS-SUPPLEMENT.md` for operating rules, and `assets/tts-mod/readme.md` for the
asset-workspace entry point.

**DOCUMENTATION RULE:** Follow `readme.md` → “Documentation placement.” `PROJECT_STATUS.md` owns
the concise current state. This file owns detailed backlog and historical checkpoints. Do not duplicate
durable knowledge here or update it merely because a session occurred.

Current workspace, branch, and immediate next action: see `PROJECT_STATUS.md`.

## Status legend
- [ ] = not started
- [~] = in progress
- [x] = done

---

## DONE (v2 + v3)
- [x] Parse save → objects.json, lua_script.lua, lua_roles.json, gmnotes_taxonomy.json
- [x] Classify base vs expansion (Lua-authoritative) → classification.json, url_verdicts.json
- [x] Download base assets (444 files, 0.93 GB) → v2-dl/tree/
- [x] v3 category cleanup: rename -discard decks to live-deck names (attack/event/exploration/
      greenitem/reditem/yellowitem/seriouswound)
- [x] Move 9 player-help + intruderHelp cards → cards/reference/
- [x] Review and file all 7 quarantined cards/components; `unsorted/` is empty
      (4 help sheets, 1 beveled marker cube, and 2 Life Support state textures)
- [x] Resolve action folder: 12 coop-objective → objectiveCoop/, 1 contamination → contamination/,
      shared action-154 sheet split (base cells 10-14 kept), card back → action/back.jpg
- [x] Split 13 sprite sheets into 163 individual card PNGs (native res, *_cards/ subfolders)
- [x] Write expansion re-add guide (`assets/tts-mod/notes/extraction.md` §15) + cleanup log (§14)
- [x] Re-extract all 49 icons from official rulebook p. 40 at 400 DPI; replace the untrusted
      crops in `assets/icons/` and correct `docs/rules/icon-glossary.md`
- [x] Audit known Qwen-dependent vision claims with native GPT-5.6: correct OQ-011's Technical
      Corridor detail, re-read the three sampled Item cards, remove Qwen routing guidance, and
      retain the controlled model trial only as historical QA evidence

---

## DONE — Vision card-text extraction (2026-08-15)
The asset pass read every in-scope canonical image and produced structured card data or an exact
durable review deferral.

**STATUS (2026-08-15T06:09:23Z):** Complete. All 532 in-scope assets are reconciled: 111
high-confidence complete, 421 explicitly deferred, and 0 unaccounted. The canonical `cards/`
catalog now contains 63 valid image/JSON pairs (18 previously approved plus 45 created in this
pass). Durable per-asset state is in `assets/tts-mod/extract/vision-progress.json`; the deduplicated
421-entry human-review queue is `assets/tts-mod/extract/low-confidence-review.json`; validation
evidence is `assets/tts-mod/extract/vision-validation.json`. Exact next resumable position: none.

**Baseline inventory (2026-08-15T04:59:55Z):** 545 PNG/JPEG files on disk; 13 documented source
sprite sheets excluded because their canonical children already exist; 532 in-scope canonical image
assets (390 cards, 142 other images). At baseline, 23 were previously complete (18 approved card
sidecars plus 5 previously reviewed/classified non-card/reference assets), 1 was already deferred,
and 508 were pending. Exact baseline next position:
`assets/tts-mod/extract/v2-dl/tree/bags/adult-007.png`.

**Vision checkpoint (2026-08-15T05:11:35Z):** 66 new native reads persisted, 0 vision
failures, and 442 assets still awaiting first read. Exact next unresolved position:
`assets/tts-mod/extract/v2-dl/tree/bags/gameBox-022.jpg`.

**Vision checkpoint (2026-08-15T05:22:31Z):** 149 native reads persisted, 1
recoverable provider-overload failure remained queued for retry, and 358 assets still awaited first
read. Exact next unresolved position:
`assets/tts-mod/extract/v2-dl/tree/cards/character/officer-041.png`.

**Vision checkpoint (2026-08-15T05:38:48Z):** 277 native reads persisted, 1
recoverable provider-overload retry remained, and 230 assets still awaited first read. Exact next
unresolved position:
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-091.jpg`.

**Procedure:** Follow `assets/tts-mod/notes/card-extraction.md`; use
`docs/rules/icon-glossary.md` for canonical icon names. This TODO intentionally does not duplicate
the transcription, rotation, icon-comparison, punctuation, or source-authority workflow.

**Running tally:**
- Canonical image/JSON pairs: 63 total — 18 previously human-approved and preserved unchanged, plus 45 newly created from uniformly high-confidence pixel reads with valid minimal sidecars. `Move Quietly` was approved with the correction that its upper-right `notInCombat` symbol uses the crossed-out-Intruder variant, not the crossed-out-gun variant. `Bulletproof Vest`, `Handgun`, `Duck and Cover`, Contractor Consultant `Computer Skills`, `Always Prepared`, `Forcing Fire`, and `Secure` were approved unchanged; the canonical Bulletproof Vest face uses “gain a Serious Wound,” while its conflicting TTS BackURL is retained as provenance in `docs/qa/card-source-audits/bulletproof-vest-face-back.md`. The false `cards/character/combat-engineer/starting-item.*` entry was removed with human approval after it was definitively traced to the BackURL of Automatic Shotgun object `2059a7`; the image is retained only as provenance at `docs/qa/card-source-audits/automatic-shotgun-tts-back.png`.
- This pass verified 60 non-upright assets by rotating lossless staging pixels before the final transcription; manifest-backed sources stayed byte-identical, and any promoted canonical card copy is upright.
- Source images rotated upright: 5 (Combat Engineer Starting Item/Automatic Shotgun back, Automatic Shotgun face, Contractor Handgun, obsolete BF Gun face, Heavy Gun Operator Starting Item/BF Gun back).
- BF Gun is excluded from canonical data as an obsolete/prototype HGO starting item; its purple exclamation artwork differs from the current `burstDieAdditionalEffects` glyph but is retained as an approved source-specific semantic alias. Evidence: `docs/qa/card-source-audits/bf-gun-source-fidelity.md` and `docs/qa/card-symbol-semantic-resolutions.json`.
- Automatic Shotgun still has a documented official-vs-TTS text conflict; its TTS JSON remains unchanged pending a human-approved canonical-data representation. Evidence: `docs/qa/card-source-audits/automatic-shotgun-source-fidelity.md`.
- Icons flagged UNCERTAIN in canonical catalog entries: 0.
- Card-extraction notes: `assets/tts-mod/notes/card-extraction.md`

## DONE — Luna Max native-vision experiment (2026-08-15)
- [x] Froze and ran a blinded 12-image benchmark through native
      `openai-codex:gpt-5.6-luna` at reasoning effort `max`; auxiliary vision was not used.
- [x] Verified 12 unique Luna/max sessions, one API call per case, zero tool calls, parseable outputs,
      frozen source/sidecar hashes, and complete scoring evidence.
- [x] Result: 82.120/100 overall; 85.180/100 mean on eight human-approved cards; 72/100 on the
      exact dense-sheet comparator where the prior Sol run scored 88/100. None of Luna's five
      high-confidence promoted sidecars exactly matched approved data, and ambiguous creature art was
      false-promoted. Luna is approved only as secondary OCR/triage evidence, not unattended canonical
      promotion. Report: `docs/qa/vision-model-trial/luna-max/report.md`.

## DONE — GPT-5.6 Sol High mini vision test (2026-08-15)
- [x] Ran two frozen, blinded icon-stress cases through native `openai-codex:gpt-5.6-sol`
      at reasoning effort `high`: 68.859/100 mean and 31.748–34.367 seconds per call.
- [x] Result: 0/2 exact sidecars. Sol safely deferred an unresolved `lander` glyph, but confidently
      promoted Automatic Shotgun with `shootDieAmmoLoss` substituted for `shootDieCritical`.
      This tiny test does not qualify Sol for unattended promotion. Report:
      `docs/qa/vision-model-trial/sol-high-mini/report.md`.

## DONE — GPT-5.6 Sol X-High and Max mini vision tests (2026-08-15)
- [x] Ran the same two frozen, blinded icon-stress cases at reasoning efforts `xhigh` and `max`,
      preserving the Sol High prompt, image/gold hashes, native-image route, and scorer.
- [x] X-High: 69.099/100 mean, 48.717–79.911 seconds, 0/2 exact sidecars; it repeated High's safe
      Lander deferral and unsafe high-confidence Shoot-die promotion.
- [x] Max: 80.166/100 mean, 76.733–98.741 seconds, 0/2 exact sidecars; both high-confidence
      promotions used a wrong semantic icon. Four fresh sessions were verified with one native-image
      API call and zero tools each. Reports: `docs/qa/vision-model-trial/sol-xhigh-mini/report.md` and
      `docs/qa/vision-model-trial/sol-max-mini/report.md`.

## DONE — Extracted card-text evidence corpus (2026-08-16)
- [x] Recomputed and validated the live baseline: 532 total in-scope images, 134 complete, 398 deferred, 0 unaccounted, and 64 valid canonical image/JSON pairs.
- [x] Built `assets/tts-mod/extract/card-text-corpus.json` with 390 card/reference image records linked to source SHA-256 evidence. Parent sprite sheets are excluded; 168 generated records are individual faces from 13 source sheets.
- [x] Classified 64 canonical records and 276 full draft card transcriptions. Across all record types, 352 contain nonempty rules/effect text; there are no partial rules-text records after structured effect/COMMAND/REACTION panels are recognized.
- [x] Added deterministic corpus/coverage validators and `docs/qa/card-symbol-resolution-backlog.json`, which preserves 227 unresolved/local glyph occurrences across 136 rules-bearing image assets as morphology-only evidence.
- [x] Documented schema, trust states, rebuild commands, and promotion boundaries in `assets/tts-mod/notes/card-text-corpus.md`.

## IN PROGRESS — Re-examine deferred assets with Sol Max
- [~] Re-examine the deduplicated entries in
      `assets/tts-mod/extract/low-confidence-review.json` using one supervisor and one long-lived native
      `openai-codex:gpt-5.6-sol` worker at `max` reasoning. The worker processes 2–4 stable-ID assets
      per vision turn in an isolated staging area; the supervisor alone serializes canonical merges and
      shared-ledger updates. Never downgrade. Replace the worker with a clean context before it exceeds
      200k tokens. Starting queue: 421; first assigned path:
      `assets/tts-mod/extract/v2-dl/tree/bags/adult-007.png`.
- [~] Apply the morphology-first anti-overconfidence gate from
      `assets/tts-mod/notes/card-extraction.md`: self-reported confidence is not evidence; unresolved
      text/icons/provenance remain deferred rather than guessed.
- [~] Continuously checkpoint worker-local results, then update `vision-progress.json`,
      `low-confidence-review.json`, this TODO, and exact next position at each supervised merge.
      Finish with deterministic ledger/queue/sidecar/catalog/manifest reconciliation.

**Supervisor checkpoint (2026-08-15T22:38:36Z):** Recomputed 532 in-scope assets from disk and
validated all source hashes/decodes. Worker 03’s clean `W01-024` retry was merged as a conservative
defer. Worker 04 produced eight valid staged reads; seven were merged as defers, and `W04-007`
(`TAKING AIM — RECON`) passed an explicit supervisor promotion gate and was copied to a new canonical
image/sidecar pair with the extraction source preserved byte-identically. The frozen Worker 05 shard
then independently reread `W05-001` through `W05-004` from the exact source pixels using four direct
native Sol Max image turns. All four remain deferred: `CHAIN OF COMMAND`, `DEMOLITION`, `SCOUTING`,
and `SEARCH`. Their W05 results now supersede the older W04 evidence pointers for those exact four
source tuples; no candidate sidecars were created. Current partition: 134 complete, 398 deferred,
0 unaccounted; 64/64 canonical sidecars valid; no source files moved or renamed.

The Worker 05 root was reused by a foreign W04-009 through W04-011 replacement assignment after its
frozen W05-001 through W05-004 lineage had completed. The frozen lineage is the selected merged
evidence for its own four tuples. The replacement assignment also completed three valid deferred reads,
but it remains held and unmerged because it overlaps Worker 06. Worker 06 (`deleg_547cfe00`) completed
four valid worker-local Sol Max deferred reads; three overlap that Worker 05 replacement shard and the
fourth is a neighboring heavy-gun-operator card cell. Because Worker 06 was outside the requested
card-176 approval-gated scope, none of these held results were merged or used as card-176 evidence.

**Lifecycle cleanup (2026-08-16T02:43:34Z):** No worker or related subagent is live. Stale dispatch
records for Workers 03–06 were closed; the current Worker 05 and Worker 06 assignments are explicitly
`completed-held-unmerged`, and historical raw/results/reports were preserved. No shared ledger, queue,
canonical card, source asset, or semantic decision changed. Audit:
`assets/tts-mod/extract/vision-workers/supervisor-lifecycle-cleanup.json`.

**Worker 05/06 reconciliation (2026-08-16T03:20:33Z):** The held overlap is resolved. Worker 06 is
the sole shared-ledger lineage for card-11, card-12, card-13, and card-15; all four validated results
remain deferred. Worker 05's independent card-11/12/13 reads agree on the source tuples, titles,
printed owner, material text, and defer decisions, and are retained as corroborating direct
authoritative-icon-crop evidence. No canonical file, source image, sidecar, category, or filename was
changed. Current partition remains 134 complete, 398 deferred, and 0 unaccounted, with 64 canonical
sidecar/image pairs. Exact next re-examination path:
`assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-16.png`.
Audit: `assets/tts-mod/extract/vision-workers/supervisor-reconciliation-workers-05-06.json`.

**W09 deferred-card checkpoint (2026-08-18T09:59:16Z):** Worker
`sol-max-persistent-worker-09-20260818T085918Z-723f40` re-examined the exact generated-card
cells `card-18.png` through `card-25.png` with verified native
`openai-codex:gpt-5.6-sol` at `max`. All eight validated selections remain deferred; no canonical
sidecar, source image, classification, or filename changed. The durable registry now contains 12
selected entries/runs; the deterministic 390-record corpus contains 10 verified and 11 unresolved
icon occurrences from W09, with six prior-snapshot conflicts preserved. Re-merging is idempotent.
Exact next forward genuinely unselected position is
`low-confidence-review.json` `entries[22]`:
`assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-27.png`
(SHA-256 `be41f58fd5e1bc3231001c5940ac5d6464ff8d625b08b45a0edc6311b2466354`).

**W10 deferred-card checkpoint (2026-08-18T11:03:10Z):** Worker
`sol-max-persistent-worker-10-20260818T101016Z-8cf704` re-examined the exact generated-card
cells `card-27.png`, `card-28.png`, `card-29.png`, `card-31.png`, `card-32.png`,
`card-33.png`, `card-34.png`, and `card-37.png` with one clean isolated native
`openai-codex:gpt-5.6-sol` blind session at `max` plus post-blind authoritative comparisons.
All eight validated selections remain deferred; no canonical sidecar, source image, classification,
or filename changed. The durable registry now contains 20 selected entries/runs; the deterministic
390-record corpus contains 7 verified and 6 unresolved W10 icon occurrences, with four
prior-snapshot conflicts preserved. An identical re-merge is idempotent. Exact next forward
genuinely unselected position is `low-confidence-review.json` `entries[30]`:
`assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-38.png`
(SHA-256 `0552286f57fa7bd931211671372be695a22592dce514cd0fcdb61af9932d5bbb`).

**W11 deferred-card checkpoint (2026-08-18T12:32:49Z):** Worker
`sol-max-persistent-worker-11-20260818T113243Z-2e4d25` re-examined `card-38.png`,
`card-39.png`, `card-40.png`, `card-41.png`, `card-43.png`, `card-44.png`,
`medical-support-011.png`, and `medical-support-022.jpg` with one isolated native
`openai-codex:gpt-5.6-sol` blind session at `max` plus 12 post-blind native reference calls.
All eight selected results remain deferred; no canonical sidecar, source/canonical card byte,
classification, or filename changed. Registry/corpus counts are 28/390 with 11 verified and 6
unresolved W11 icon occurrences and zero prior-snapshot conflicts; identical re-merge is idempotent.
Exact next forward genuinely unselected position is `low-confidence-review.json` `entries[38]`:
`assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-023.jpg`
(SHA-256 `71ed551e4eed6b33469b286d8dc0d2ddcc910cef22fb522097a0a24ae2ba0f72`).

**W12 deferred-card checkpoint (2026-08-19T04:24:34Z):** Worker
`sol-max-persistent-worker-12-20260818T124945Z-bba552` re-examined queue entries 38–45. The first
four immutable reads remain byte-identical in the original native `openai-codex:gpt-5.6-sol`/`max`
session; after that session acquired a failed fifth user turn (4 API calls, 9 messages), it was never
resumed. Entries W12-005..008 used one fresh tools-disabled session (4 API calls, 8 messages, zero
tools), and 13 post-blind native reference calls were separately audited. Seven assigned images now
have exact rules-bearing text and authoritative icon morphology; the eighth is exactly classified as
the non-rules `STARTING ITEM` / `OFFICER` BackURL paired to SAWED-OFF SHOTGUN. The selected
evidence records 17 verified icon comparison groups covering 20 placements and 0 unresolved
assigned-image glyphs. All eight promotions remain deferred: W12-005 conflicts with a protected
exact-path canonical sidecar, W12-006/007 retain differing same-title source conflicts, and the other
sources lack an authoritative edition/supersession gate. No canonical sidecar or source image changed.
Registry/corpus counts are 36/390; local projection, shared merge, identical re-merge, and two explicit
corpus rebuilds are byte-idempotent. Each W12 tuple remains exactly once in both progress and the
398-entry low-confidence ledger; the global partition remains 134 complete, 398 deferred, 0
unaccounted. Exact next genuinely unselected position is `low-confidence-review.json` `entries[46]`:
`assets/tts-mod/extract/v2-dl/tree/cards/character/officer-009.png`
(SHA-256 `636b473e04f0e0f43bad9d30767092b44f3e822c924ff74f7e1f3c728bfbd6b0`).

**W13 deferred-card checkpoint (2026-08-19T05:04:58Z):** Worker
`sol-max-persistent-worker-13-20260819T042908Z-b4de5f` completed queue indices
46–53 in one fresh tool-disabled native `openai-codex:gpt-5.6-sol` max session
(`20260819_043155_256a9b`; 8 API calls, 16 messages, zero tools), followed by
12 DB-audited native post-blind image reads. It preserved seven exact
rules-bearing sources plus one exact non-rules Recon starting-item back, with 15
authoritatively matched icon groups and one explicit unresolved group: STAY CALM's
solid white upright card/tile does not directly match the official `actionCard`
`A` crop and remains literal rather than inferred. Edition-sensitive text was
preserved, including FIRE AT WILL's `neighbouring`, CHAIN OF COMMAND's unhyphenated
`lower ranking` and printed `Burst. (you make all choices).`, and the direct
FaceURL/BackURL relationship between the Recon back and ASSAULT RIFLE. A protected
OFFICER CHAIN OF COMMAND target conflict was recorded without overwrite. All eight
promotion decisions remain `defer`; no canonical sidecar was created or changed.
The defer-only registry merge was locally projected, independently rebuilt, and
shared-merged twice byte-idempotently: selected evidence now contains 44 exact
tuple entries/runs, while the deterministic corpus remains 390 records. All eight
W13 tuples remain exactly once in `vision-progress.json`, exactly once in the
398-entry low-confidence queue, and exactly once in the selected evidence registry;
the deterministic global partition remains 532 = 134 complete + 398 deferred + 0
unaccounted. The next eligible exact tuple is queue index 54,
`assets/tts-mod/extract/v2-dl/tree/cards/character/recon-019.png`
(SHA-256 `b2361593ff5f03a812f76a73900beda2dcd7e99091d13209ca8d10e487dfe8ef`).

**W14 deferred-card checkpoint (2026-08-19T05:43:21Z):** Worker
`sol-max-persistent-worker-14-20260819T050936Z-5dcf03` completed queue indices
54–61 in one fresh tool-disabled native `openai-codex:gpt-5.6-sol` max session
(`20260819_051216_124afe`; 8 API calls, 16 messages, zero tools), followed by
15 DB-audited native post-blind image reads. Four assigned images now have exact
rules-bearing text with 8 authoritative icon groups covering 11 placements and
zero unresolved assigned-image symbols: Recon CHAIN OF COMMAND, ASSAULT RIFLE,
SHOOT FIRST, and SCOUTING. The other four are exactly classified non-rules
character-selection faces (`PICK OFFICER`, `PICK H. GUN OPERATOR`, `PICK MEDICAL
SUPPORT`, and `PICK UAV OPERATOR`) and were not promoted into rules sidecars. Seven
tuples have one concrete paired-side relationship; generated cell 6 (`PICK MEDICAL
SUPPORT`) has no concrete CardID selector and retains only generic shared CHARACTER
DRAFT back evidence. All eight promotion decisions remain `defer`; no canonical
sidecar, source image, or protected tracked target changed. The registry merge was
projected, independently rebuilt, and shared-merged twice byte-idempotently:
selected evidence now contains 52 exact tuple entries/runs, while the deterministic
corpus remains 390 records. Each W14 tuple remains exactly once in progress, the
398-entry low-confidence queue, and selected evidence; the global partition remains
532 = 134 complete + 398 deferred + 0 unaccounted. The next eligible exact tuple is
queue index 62, `assets/tts-mod/extract/v2-dl/tree/cards/character/recon-051.png`
(SHA-256 `318546349ba9ded87455d6608112a0cdb7a5bf826eff07c64c106ed1289ec32d`).

**W15 deferred-card checkpoint (2026-08-19T06:40:47Z):** Worker
`sol-max-persistent-worker-15-20260819T054617Z-ac4db5` completed queue indices
62–69 in one clean tool-disabled native `openai-codex:gpt-5.6-sol` max session
(`20260819_054756_b8fea8`; 8 API calls, 16 messages, zero tools), followed by audited
post-blind side, pair, official-source, and glossary evidence. Seven sources are exact
rules-bearing faces: Recon DEMOLITION, Contractor SEARCH and DEMOLITION, BLOOD SENSE,
and three BITE cells. `ATTACK / PRIMEBLOOD` is exactly the shared non-rules BackURL.
Five direct icon groups are authoritatively matched. Thirteen local glyph occurrences
remain explicit no-matches rather than inferred: SEARCH's solid chamfered polygon,
three BLOOD SENSE cyan badges, and three cyan badges in each BITE cell. Before the
shared write, the tentative merge was rolled back to the sealed W14 preimage and the
normalized W15 evidence was rebuilt so every unresolved occurrence has its own exact
location/morphology comparison row. All eight promotion decisions remain `defer`;
no canonical sidecar, source image, category, filename, or protected target changed.
Private projection, independent rebuild, shared merge, and identical re-merge are
byte-idempotent: selected evidence now contains 60 exact tuple entries/runs and the
corpus remains 390 records. Each W15 tuple occurs exactly once in progress, the
398-entry low-confidence queue, selected evidence, and its exact corpus overlay; the
global partition remains 532 = 134 complete + 398 deferred + 0 unaccounted. The next
eligible exact tuple is queue index 70,
`assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-03.png`
(SHA-256 `9c988ba455dd17dfa1dc34eb2fb26cfebb6c17c9f21cb6a60af473ca0c441afc`).

**W16 deferred-card checkpoint (2026-08-19T07:35:56Z):** Worker
`sol-max-persistent-worker-16-20260819T064958Z-3c1388` completed exact queue indices
70–72 and 74–78; index 73 was already selected by an earlier exact-tuple run and was
mechanically skipped. Blind reads used one clean tool-disabled native
`openai-codex:gpt-5.6-sol` max session (`20260819_065934_a4c431`; 8 API calls,
16 messages, zero tools), followed by audited post-blind side, pair,
official-source, and glossary evidence. All eight sources are rules-bearing generated
attack FaceURL cells: three BITE, two DEADLY CLAWS, two FURY, and one INFECTING.
Each has one exact CardID/GUID selector and one direct `ATTACK / PRIMEBLOOD` BackURL.
Five inline white glyph groups are authoritatively matched to `characterHealth`.
Twenty-four cyan local badge occurrences—three per face—remain explicit no-matches,
each preserving its exact location and morphology; no semantic badge names were
invented. All eight promotion decisions remain `defer`; no canonical sidecar, source
image, category, filename, or protected target changed. Private projection,
independent rebuild, shared merge, and identical re-merge are byte-idempotent:
selected evidence now contains 68 exact tuple entries/runs and the corpus remains
390 records. Each W16 tuple occurs exactly once in progress, the 398-entry
low-confidence queue, selected evidence, and its exact corpus overlay; the global
partition remains 532 = 134 complete + 398 deferred + 0 unaccounted. The next
eligible exact tuple is queue index 79,
`assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-13.png`
(SHA-256 `e23333f920163dc0a9342ef6d348855b0dbb3e2b7a769ec735e3d4460c2d89cf`).

**W17 deferred-card checkpoint (2026-08-19T08:23:01Z):** Worker
`sol-max-persistent-worker-17-20260819T074018Z-35053f` completed exact queue indices
79–86. Blind reads used one clean tool-disabled native `openai-codex:gpt-5.6-sol`
max session (`20260819_074348_1e30be`; 8 API calls, 16 messages, zero tools),
followed by 11 audited native post-blind side, official-source, glossary, and focused
comparison calls in session `20260819_062132_c0f4f3`. Seven sources are
rules-bearing generated attack FaceURL cells 13–19: four `SCRATCH`, one `SUMMONING`,
and two `TAIL ATTACK`. Source pixels visibly correct the blind `SCRAICH` title to
`SCRATCH` on cells 13–16; immutable blind wrappers remain unchanged and each correction
is explicit. Six attack cells have one exact CardID/GUID selector; `SUMMONING` cell 17
has deck-level `ATTACK / PRIMEBLOOD` BackURL provenance and no direct cell-17 selector.
The eighth source is a shared `CONTAMINATION` FaceURL used by 27 CardCustom objects and
paired to the shared `ACTION` BackURL. It has no rules body; its large red patterned
field is preserved as a non-text component graphic, not assigned a fabricated token.
Five inline white groups match `characterHealth`, and the SUMMONING shield matches the
official page-40 `secure` token. Twenty-one cyan local badge occurrences—three on each
attack face—remain explicit no-matches preserving exact location/morphology; no semantic
badge names were invented. All eight promotion decisions remain `defer`; no canonical
sidecar, source image, category, filename, or protected target changed. Private
projection, independent rebuild, shared merge, and identical re-merge are
byte-idempotent: selected evidence now contains 76 exact tuple entries/runs and the
corpus remains 390 records. Each W17 tuple occurs exactly once in progress, the
398-entry low-confidence queue, selected evidence, and its exact corpus overlay; the
global partition remains 532 = 134 complete + 398 deferred + 0 unaccounted. The next
eligible exact tuple is queue index 87,
`assets/tts-mod/extract/v2-dl/tree/cards/game/event-051.jpg`
(SHA-256 `2eb453e8f770bbee9ab5b951fb22e952d34c1250876b88e878a461c11f7f8ded`).

**W18 mixed promotion/defer checkpoint (2026-08-20T05:27:57Z):** Recovery worker
`sol-max-persistent-worker-18-recovery-20260820T044726Z-p176060-5eb908` sealed the
following exact low-confidence queue tuples from stale partial source worker
`sol-max-persistent-worker-18-20260819T083241Z-XgS4ri`:
- index 87, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-051.jpg`,
  SHA-256 `2eb453e8f770bbee9ab5b951fb22e952d34c1250876b88e878a461c11f7f8ded`;
- index 88, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-054.png`,
  SHA-256 `ac3dc8c20efc3e964383bb9956b264bf3f4a64762d8d8920f5c612d1841ec4bf`;
- index 89, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-058.jpg`,
  SHA-256 `cdf03513025769517d9a0e05ac3881120176a1d506db118fd3db50b6c82d9762`;
- index 90, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-064.png`,
  SHA-256 `93bd00726c0683feb10a47c85c86055438114c3a8c5fbb33500325fa195d2158`;
- index 91, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-072.png`,
  SHA-256 `890259ff52beb7bb5235f2efd010b4e54ee752e9d85cb27f2de2576257fa33bb`;
- index 92, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-086.png`,
  SHA-256 `fe6a4f8faae5efdecb02b1ec436c605f792f5f78dd332e1cf64cffc532631ab0`;
- index 93, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-090.png`,
  SHA-256 `45b5845d04f57b10dff6e73005be88cba0107a1a15da83f581df6531390d1ac9`;
- index 94, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-093.jpg`,
  SHA-256 `6f93c7b3d25bb4fcbf6b7d786f31172b09a65f888b9fdb707917a7fae916b868`.
All eight are rules-bearing event FaceURL faces and zero are non-rules sources; each exact
CardCustom selector resolves to the shared `EVENT / PRIMEBLOOD` BackURL. Byte-identical
blind evidence came from one clean tool-disabled native `openai-codex:gpt-5.6-sol` max
session (`20260819_083610_6461bd`; 8 API calls, 16 messages, zero tools). Historical
post-blind session `20260819_062132_c0f4f3` supplied 15 audited attachments; the recovery
supervisor (PID 176060; session ID unexposed) added 14 direct native Sol-Max/max contact,
focused, paired-side, and official-page attachments. Forty-nine visual occurrences match
authoritative glossary tokens. Three featureless white rectangular occurrences on
`LEAVING THE SHELL` remain three separate explicit no-match rows; no semantic token was
inferred. Two non-text graphics and one art-field correction are preserved. Seven faces
(`OVERWHELMING ENEMIES`, `SHORT CIRCUIT`, `LIFE SUPPORT FAILURE`, `THE QUEEN AWAKENS`,
`BREAKING IN`, `HATCHING`, and `PROTECT & SERVE`) passed every promotion gate and gained
byte-preserving canonical images plus minimal sidecars; `LEAVING THE SHELL` remains
`defer`. Private projection, independent corpus rebuild, shared merge, and identical
re-merge are byte-idempotent. A stale all-PNG target assertion and a post-merge Git-scope
assertion each stopped safely; the latter restored the complete W17 shared/canonical/QA
preimage before a clean reapply. Final closure has zero standard-auditor errors/warnings;
10 focused tests and all eight documented coverage/corpus/unresolved/vision/reproducibility
commands pass, including 532/532 source decodes and an exact eight-record corpus diff.
Selected evidence now has 77 entries/runs, the deterministic corpus remains 390 records,
canonical sidecars/images total 71 pairs, and the partition is 532 = 141 complete + 391
deferred + 0 unaccounted (queue 391). Sealed data commit:
`1ca57c57d506151d712794555f72a66817ea7146`. Blocker: none. The next eligible exact tuple
is original queue index 95 / current projected queue index 88,
`assets/tts-mod/extract/v2-dl/tree/cards/game/event-096.png`
(SHA-256 `85d08e0de5b2710ed0e1ac0295ed27da3b4d0da9eb2419aa0f0093d94f1b70d5`).

**W19 mixed promotion/defer checkpoint (2026-08-20T06:14:49Z):** Worker
`sol-max-persistent-worker-19-20260820T053136Z-p176060-d62d87` sealed these exact
current low-confidence queue tuples:
- index 88, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-096.png`,
  SHA-256 `85d08e0de5b2710ed0e1ac0295ed27da3b4d0da9eb2419aa0f0093d94f1b70d5`;
- index 89, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-099.png`,
  SHA-256 `0d5da2c8e1b6ccb6a30c83f9006aa924f4fc2f1f14d360d153bc5ea6f73770ed`;
- index 90, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-100.png`,
  SHA-256 `592afbb981cdb9bcae45812d38285a7e7cc1dd41bb21446861d51d000e9b0070`;
- index 91, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-139.png`,
  SHA-256 `53351204890c5e98381a1fc4712e574a701659ec913b5f9c3f838ac6074c9614`;
- index 92, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-167.png`,
  SHA-256 `37bbf022f99ef62a18a5225aaf31347f6299f72672603547f51918502241f27b`;
- index 93, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-170.png`,
  SHA-256 `86ba726fa9fa4a8d9ed2913f6619db2d5df1b5ad1e3c69bd0b380993c9e8967e`;
- index 94, `assets/tts-mod/extract/v2-dl/tree/cards/game/event-179.png`,
  SHA-256 `72a3270de96356e8ea1e64b9bf1d2b90e189a7ae6f1031d03b6db453d3f93eab`;
- index 95, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-024.png`,
  SHA-256 `3cfb21c76b93ba8e23abf464321e7071d73aac0c23b0dc1763702206fe80854f`.
All eight sources are rules-bearing and zero are non-rules: seven exact base event FaceURLs
pair to `EVENT / PRIMEBLOOD`, and one exact exploration FaceURL pairs to
`EXPLORATION / PRIMEBLOOD`. Blind reads used one clean persistent tool-disabled native
`openai-codex:gpt-5.6-sol` max session (`20260820_053305_a121de`; 8 API calls,
16 messages, zero tools); the current supervisor session ID remained unexposed and made
11 direct post-blind contact, paired-side, and official-page attachments. Fifty-three
visual occurrences match authoritative glossary tokens, zero occurrences remain
unresolved/no-match, and the exploration room-and-branches outline is preserved as one
non-text explanatory schematic. `SYSTEM FAILURE` also has two Carnomorph reuse refs and
one unresolved expansion BackURL; those are separated from its exact base selector/back
and do not collapse the provenance. Official rulebook page 3 directly reproduces
`SCENT OF PREY` without conflict. Seven event faces (`LANDING ZONE EXPLODES`,
`SYSTEM FAILURE`, `SCENT OF PREY`, `DAMAGE`, `DAMAGING FIRE`, `PANIC`, and
`EGG PROTECTION`) passed every promotion gate and gained byte-preserving canonical images
plus minimal sidecars. The untitled exploration face remains `defer` because no printed
unique title/slug establishes a canonical filename, despite complete text and five matched
glyph occurrences. Private projection, independent corpus rebuild, shared merge, and
identical re-merge are byte-idempotent. A hand-supplied exploration-back hash and a generic
FAQ phrase classification each failed closed before producing shared evidence, then were
re-derived from live bytes/context. Final closure has zero standard-auditor errors/warnings;
10 focused tests and all eight documented global commands pass, with 532/532 source
decodes, no W19 source left in the symbol backlog, and an exact eight-record corpus diff.
Selected evidence now has 78 entries/runs, corpus remains 390 records, canonical pairs
total 78, and the partition is 532 = 148 complete + 384 deferred + 0 unaccounted
(queue 384). Sealed data commit: `65733230d733ec0aa12b3435f4cb086f4251e8e0`.
Blocker: none. The next eligible exact tuple is original queue index 96 / current projected
queue index 89, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-025.png`
(SHA-256 `774b6ed8ea4492bfae38145c828ae47c61536855ec1ffb86702d1fb2d2d09d8b`).

**W20 defer-only exploration checkpoint (2026-08-20T07:11:58Z):** Recovery worker
`sol-max-persistent-worker-20-retry-20260820T062826Z-p176060-d74a21` sealed these exact
current low-confidence queue tuples:
- index 89, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-025.png`,
  SHA-256 `774b6ed8ea4492bfae38145c828ae47c61536855ec1ffb86702d1fb2d2d09d8b`;
- index 90, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-026.png`,
  SHA-256 `08445a3d8b18081d7396756f407ac058c383c3aee05bde76e80393b0af4b741d`;
- index 91, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-027.png`,
  SHA-256 `3da198b348a70d64e20de051034e98aa2454ef1912df3cf18e78eaf7c4800043`;
- index 92, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-031.png`,
  SHA-256 `549bb22b017b6df982c3378f613294969d7043a1a87a1e4b4f5d704308d2ceb0`;
- index 93, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-032.png`,
  SHA-256 `9c521a0ca8f9303363e69266962c20bee13b7a03cc8d05410399755ea42c684b`;
- index 94, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-036.png`,
  SHA-256 `160d5d76b631d1ccbd1e4ea981313a1edbd83a6e9eda34dd825fafc2f9cbdd4d`;
- index 95, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-037.png`,
  SHA-256 `3101f9f9a5df9d01aa07073837412496355c63df94216ab1550abc6a21221516`;
- index 96, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-062.png`,
  SHA-256 `b3be8596be1e99b3b520b0ce2c37e7f14a48c6a90dc4e422d32ae92592fbab38`.
All eight are rules-bearing exploration FaceURLs and zero are non-rules; each has one exact
CardCustom selector and the shared `EXPLORATION / PRIMEBLOOD` BackURL. The first W20
session (`20260820_061821_0b24be`) was rejected before any wrapper was sealed because the
legacy empty `--toolsets ''` value fell back to normal CLI tools and made two `skill_view`
calls. Neutral smoke session `20260820_062541_38a2e9` proved `--toolsets none` produced
one API call, two messages, zero tools, no Tools system-prompt section, and no exposed
`skill_view`; the extraction workflow reference was corrected accordingly. Fresh production
session `20260820_062933_d6e177` then completed 8 API calls, 16 messages, zero tools, and
eight immutable wrappers. The supervisor session ID remained unexposed and made nine direct
post-blind contact/paired-side attachments. Thirty-eight glyph occurrences match the
canonical glossary, zero remain unresolved/no-match, and nine non-text graphics are
preserved (eight room/topology schematics plus one clipped corner motif). Every blind top
“Place…” field is explicitly reallocated from `title` into operative body text; no unique
printed title/slug is visible on any face. All eight promotion decisions therefore remain
`defer`; no canonical image, sidecar, source byte, category, or filename changed. Private
projection, independent corpus rebuild, defer-only shared merge, and identical re-merge are
byte-idempotent. Final closure has zero standard-auditor errors/warnings; 10 focused tests
and all eight documented global commands pass, with 532/532 source decodes, no W20 source
left in the symbol backlog, and an exact eight-record corpus diff. Lifecycle and queue stay
532 = 148 complete + 384 deferred + 0 unaccounted (queue 384); selected evidence rises to
86 entries/runs, corpus remains 390 records, and canonical pairs remain 78. Sealed data
commit: `947a4b129105521efd0cb2f4bae56dfa8068de47`. Blocker: none. The next eligible exact
tuple is current queue index 97,
`assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-076.png`
(SHA-256 `e4e92cae40da14f30ee73a8f27ea8291d0861db0688ac207219fa475f24cd832`).

**W21 defer-only mixed checkpoint (2026-08-20T08:04:20Z):** Worker
`sol-max-persistent-worker-21-20260820T071414Z-p176060-72cd88` sealed these exact
current low-confidence queue tuples:
- index 97, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-076.png`,
  SHA-256 `e4e92cae40da14f30ee73a8f27ea8291d0861db0688ac207219fa475f24cd832`;
- index 98, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-087.png`,
  SHA-256 `d52ff877e59bfda1b306074b5567b4c0bf93a0be9b4e257acc88b38f87a7c85f`;
- index 99, `assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-107.png`,
  SHA-256 `daf8fb6f2bc9836bf7d457acf909fdd033aa55e182308e61b2d59e952bbced7c`;
- index 100, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-029.png`,
  SHA-256 `10a73a40826de71ecab5b5cae848de1083bb8466e50a3db927db61fdc89aa546`;
- index 101, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-115.png`,
  SHA-256 `ddedb8819e921206d38f6d89ea9690638fab53faa7a666fc8e2e2d1874566431`;
- index 102, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-120.png`,
  SHA-256 `5db3229a26df87dc4eca7b317b12d785632ab780dc770db3ec5fc7c6d373b34a`;
- index 103, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-00.png`,
  SHA-256 `59518a4d288b71cf979eae47d49f5cf098864f2a8c8b105c5e519be565a72044`;
- index 104, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-02.png`,
  SHA-256 `55b5781d25288fd9ac949e546581dfecf40466c910fd2f8bbe9b01b451338a6b`.
All eight are rules-bearing and zero are non-rules: three exact exploration FaceURLs pair
to `EXPLORATION / PRIMEBLOOD`; three standalone green-item FaceURLs and two generated
green-item cells use the shared `ITEM` back. Blind reads used one persistent smoke-proven
zero-tool native `openai-codex:gpt-5.6-sol` max session (`20260820_071539_1c3638`;
8 API calls, 16 messages, zero tools); the unexposed supervisor session made ten direct
post-blind card/back attachments. Twenty-three visual occurrences match canonical glossary
tokens. Four unresolved functional occurrences remain four separate explicit no-match rows:
Heavy Oxygen Tank's red-X/device, Adrenaline Injection's blank rectangle, and generated
Caffeine Pills' red-X/device plus blank rectangle. Eight non-text graphics are preserved.
All eight decisions remain `defer`: the three exploration faces lack unique printed slugs;
Heavy Oxygen Tank has a no-match; standalone/generated Caffeine Pills are conflicting
same-title variants; approved canonical Medkit has different operative text and was not
overwritten; Adrenaline has a no-match; generated Caffeine cell 2 also has no exact CardID
selector. No canonical file, source byte, category, or filename changed. V1 post-merge
validation rolled the complete shared/QA state back after art-only photographed microtext
abstentions were mistakenly retained in operative `visibleText.illegibleSpans`. V2 clears
only those 11 art-only span entries while preserving blind raw and
`nonRulesIllustrationDetails`; operative text, comparisons, and four unresolved occurrences
are unchanged. V2 standard closure, private projection, independent rebuild, shared merge,
and identical re-merge all pass byte-idempotently. Ten focused tests and all eight global
commands pass with 532/532 source decodes, exact eight-record corpus scope, and exactly the
three W21 assets carrying four no-match occurrences retained in the symbol backlog.
Lifecycle/canonical counts remain 532 = 148 complete + 384 deferred + 0 unaccounted,
queue 384, corpus 390, and canonical pairs 78; selected evidence rises to 94 entries/runs.
Sealed data commit: `2b1f853e5dba8a9fae2e67989a0efb011333e8d0`. Blocker: none. The next eligible exact
tuple is current queue index 105,
`assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-04.png`
(SHA-256 `760e3b4e3e0c4e1b7910b3582a487d747b50a39bf382adf72769225d863438c1`).

**W22 defer-only generated-green/mission-task checkpoint (2026-08-20T09:18:11Z):** Worker
`sol-max-persistent-worker-22-20260820T080700Z-p176060-79e991` resumed from its intact,
immutable evidence root and closed these exact current low-confidence queue tuples:
- index 105, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-04.png`,
  SHA-256 `760e3b4e3e0c4e1b7910b3582a487d747b50a39bf382adf72769225d863438c1`;
- index 106, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-06.png`,
  SHA-256 `3ed05ec380152f89ac3af2f4a648327d369a7a94db456f801e328027c81482f1`;
- index 107, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-07.png`,
  SHA-256 `16941a0010c6dca8e2114c2c3a091649df27d88ab4b52883e9a7b8326cd3de57`;
- index 108, `assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-08.png`,
  SHA-256 `259b1c8fa4f9bc3194f2150511a981d734e421ae3eb1afb03f2d20175f2c035a`;
- index 109, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-023.png`,
  SHA-256 `eaa728ca02c48c33e27e99fe2ef58c9668e7b8532316d3c6d3c93248a86b627a`;
- index 110, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-056.png`,
  SHA-256 `09eb22e4ef093e0f8f27fc0995b2d323dd9ed5c8e847fdcf18750c13b3c8d066`;
- index 111, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-101.jpg`,
  SHA-256 `da1772dcacfcc25d6e4ba8a61fc292f78764a196d08a0ed5e6170cb5a2b48504`;
- index 112, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-110.png`,
  SHA-256 `910da6e4468d14603c7e513d76eb7f856535defece8d46c011f88c6972d6e302`.

The sealed clean blind lineage remains session `20260820_080847_8bb239`: 8 API calls,
16 messages, zero tools, and eight byte-preserved mode-`0400` wrappers. Forty immutable
resume-preimage records rehash exactly. Generated cells 4/6/8 have zero direct selectors;
cell 7 has three. All four mission-task faces have one exact FaceURL selector and resolve to
the generic shared `MISSION TASK` back; generated green faces resolve to the generic `ITEM`
back. Direct post-blind p.40 and official Objectives Help Sheet comparisons partition all 31
blind morphology occurrences exactly once: 7 authoritative matches, 13 explicit one-to-one
no-match rows, 10 non-text component graphics, and 1 artwork-display morphology detail.
Seven artwork-only microtext/detail abstentions are retained outside operative material text.

All eight promotion decisions remain `defer`. EMERGENCY LIFE SUPPORT CODES verifies
`computer` and `malfunction`, but its crossed title device and both Flip glyphs remain
no-matches, cell 4 has no direct selector, and its protected target conflicts. MEDKIT verifies
`characterHealth`, but its crossed title device remains a no-match, cell 6 has no direct
selector, and its operative text conflicts with approved Medkit. STIMULANTS verifies
`characterHealth`, but its crossed device and blank Draw rectangle remain no-matches despite
three selectors. SYNTHETIC FOOD retains two functional no-matches and six artwork graphics,
and cell 8 has no selector. FACILITY RESTART verifies `hibernatoriumActive`, but preserves a
material assigned-face `[illegible]` requirement, an unmatched local player-count composite,
and an official-vs-assigned art/layout revision mismatch; official wording was not substituted.
ERADICATION retains its assigned “Queen must be killed / Facility cannot be destroyed” text,
which conflicts directly with official “The Queen must be dead / Facility must NOT be
destroyed,” plus an unmatched player-count composite. RECONNAISSANCE is visually and
textually identical to the official component, but the material local player-count composite
has no established canonical token or mission-task sidecar field. ESCORT MISSION is likewise
source-identical and verifies `robot` and `character`, but its player-count composite and
markable checkbox remain two separate unglossed/no-match occurrences. No canonical image,
sidecar, source byte, category, filename, or candidate file changed.

Worker closure and the reusable native-worker auditor pass with zero errors/warnings. The
private defer-only projection and independent corpus rebuild are byte-identical. The shared
merge passed a 4-write trial apply, deliberate 4-write exact rollback to the sealed clean
preimage, 4-write committed apply, and a zero-write identical re-merge. Ten focused tests and
all eight global validation commands pass; 532/532 sources decode, the recursive corpus diff
is exactly the eight W22 paths, every W22 path remains in the symbol backlog, and all 13
no-match occurrences survive in selected evidence and corpus overlays. Lifecycle/canonical
counts remain 532 = 148 complete + 384 deferred + 0 unaccounted, queue 384, corpus 390,
and canonical pairs 78; selected evidence rises from 94 to 102 entries/runs. Predecessor
checkpoint HEAD was `e4350bb5eec7f88381c4c4aa8c493e5476ddcb8c`; sealed data commit is
`c27ff5c141363354032b03606378a4166a85255e`. This entry is committed separately in the
following todo-only checkpoint commit (its self-hash cannot be embedded in its own content).
Operational blocker: none. Canonical-promotion blockers are the exact per-card gates above.
No W23 work was started. The next eligible exact tuple is current queue index 113,
`assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-116.jpg`
(SHA-256 `c1adf21143fb353e2253fa99feb8f50b93fb246d8d0bd91701690a4033c658e6`).

The requested approval-gated review target
`assets/tts-mod/extract/v2-dl/tree/unsorted/card-176.jpg` is absent from the live tree. A candidate
source matching the durable 2132x2142 trial dimensions is available at
`assets/tts-mod/extract/v2-dl/unsorted/12772722847183197372.jpg` and
`assets/archive/tts-mod-v1/cards/intruder/exploring-drone/exploring-drone-009.jpg`; the current
canonical tree alias is `assets/tts-mod/extract/v2-dl/tree/cards/reference/objectives-help-sheet.jpg`.
These aliases are not treated as semantic evidence. No fresh pixel read has been performed because
this approval-gated foreground session is `gpt-5.6-luna`, while the project requires verifiable native
`openai-codex:gpt-5.6-sol` at max and forbids a delegated approval-gated read. This is the current
blocker; no move, rename, catalog, sidecar, or canonical-data change was made for card-176.

Every current queue entry records the exact source path, SHA-256/provenance handle, confidently visible
pixels/text, all material uncertainties, the skip reason, and current native-vision evidence. The queue
includes the pre-existing clipped `cards/reference/objectives-help-sheet-page-2.jpg` review and all
transcription, icon, orientation, ownership, category, filename, variant, or component-function
ambiguities.

## SOURCE RESEARCH — Public authority audit (2026-08-20)

An independent web-research lane found the following sources. The Awaken Realms FAQ,
Objectives Help Sheet, BGA static data, and Tabletop Simulator format documentation were
directly fetched for verification in this follow-up; Gamefound/update links remain cited
as research leads. No corpus, canonical card, sidecar, or source asset was changed by this
research note.

- Awaken Realms current download manifest: https://awakenrealms.com/data/files.json
  Use as the discovery root for current rulebooks, FAQ/errata, and component sheets.
- Awaken Realms official current English rulebook:
  https://awakenrealms.com/images/download/Nemesis_Retaliation/ENG/Nemesis_RT_Rulebook_210x285mm_bleed3mm%20%5B40%20pages%5D%20%5Blowres%5D.pdf
  Primary source for final core inventory, printed wording, and card-back/deck
  relationships; PDF extraction loses some normative symbols, so visual review remains
  required.
- Awaken Realms official Retaliation FAQ v1.2, dated 8.06.2026:
  https://awakenrealms.com/images/download/Nemesis_Retaliation/ENG/RETALIATION_FAQ_297x214mm_bleed3mm_%5B3%20pages%5D%20v1.2_lowres.pdf
  Directly resolves several rules/errata questions, including Artificial Fever,
  malfunction/computer interaction, event timing, and item/gear interpretations.
- Awaken Realms official Objectives Help Sheet:
  https://awakenrealms.com/images/download/Nemesis_Retaliation/ENG/Nemesis_RT_Objective_Sheet_285x285mm_bleed3mm%20%5B2%20pages%5D
  Preferred source for Mission Task/Objective wording and terminology. It is more
  authoritative than TTS OCR, but symbols and layout still require visual checking.
- Board Game Arena licensed digital implementation, build 260622-1220:
  https://x.boardgamearena.net/data/themereleases/current/games/nemesisretaliation/260622-1220/modules/js/staticData.js
  This versioned secondary source contains structured definitions for Action, Event,
  Item, Objective, Exploration, Robot, Intruder Attack, Queen, and Serious Wound data,
  with named placeholders. It is a transcription lead, not a print-production master;
  digital adaptation or transcription errors remain possible. Import only with explicit
  `licensed-digital-secondary` provenance and visually verify disputed text/icons.
- Tabletop Simulator platform semantics:
  https://kb.tabletopsimulator.com/custom-content/save-file-format
  Confirms the general CustomDeck/Card fields and supports FaceURL/BackURL analysis,
  but cannot establish that a particular mod assigned the correct image to a field.
- Official Gamefound development updates provide supersession context:
  https://gamefound.com/en/projects/awaken-realms/nemesis-retaliation/updates/21
  https://gamefound.com/en/projects/awaken-realms/nemesis-retaliation/updates/32
  https://gamefound.com/en/projects/awaken-realms/nemesis-retaliation/updates/35
  https://gamefound.com/en/projects/awaken-realms/nemesis-retaliation/updates/36
  https://gamefound.com/en/projects/awaken-realms/nemesis-retaliation/updates/37
  The official TTS/prototype material is historical development evidence, not final
  authority. Campaign-era counts and prototype wording must not override the current
  retail rulebook/FAQ/component sheets.

Concrete backlog guidance: use the current Awaken Realms rulebook plus FAQ v1.2 and
component sheets as the primary hierarchy; use BGA only as a labeled secondary lead;
preserve TTS/community disagreements as provenance conflicts. The research lane found
no complete official publisher card-face atlas or print-production card master, and
PDF extraction still loses normative symbols. Automatic Shotgun is independently aligned
between the current official rulebook and BGA, but no automatic canonical promotion was
made. Recheck every candidate visually and preserve uncertainty before changing data.

**W23 defer-only mission-task checkpoint (2026-08-20T20:40:39Z):** Worker
`sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3` selected the first eight
previously unselected exact tuples from current queue index 113, with no selected-tuple skips:
- index 113, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-116.jpg`,
  SHA-256 `c1adf21143fb353e2253fa99feb8f50b93fb246d8d0bd91701690a4033c658e6`;
- index 114, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-123.jpg`,
  SHA-256 `1f8bb94fc434f1bd7861d76fe7db86cd7174f9c36ca1aaaf03601952896f4597`;
- index 115, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-138.jpg`,
  SHA-256 `41e770cd697f8226ffcc5bbcab0abee6612e525a6fc23cf3d0906f3ff456dcc8`;
- index 116, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-00.png`,
  SHA-256 `c2d4bb142b03891040b8bf52a7cb4b1457b8e040b187abd2c1be003e4a1d9d2c`;
- index 117, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-01.png`,
  SHA-256 `3cd13d793b369d06429494d3d04f991e454349be0cfc4b05805029e6b03261c3`;
- index 118, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-02.png`,
  SHA-256 `11d743898e231415232b6ad79ab88c1e4d0e31f277c0a0385abb27a997d47b48`;
- index 119, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-03.png`,
  SHA-256 `2b2042f9604da8c62c67c80b9953fe959c4c82ac93a56f2e258c473f85248e9f`;
- index 120, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-04.png`,
  SHA-256 `3ff9ae783d02bbc700c294c837917e9d3037034dcd7b45ea571ed295430128d2`.

Neutral smoke session `20260820_185733_87625e` verified one API call, two messages,
zero tools, exact `openai-codex:gpt-5.6-sol` at `max`, and no stored Tools/tool-name marker.
The sealed blind lineage is session `20260820_190057_7927a4`: 8 API calls, 16 messages,
zero tools, and eight byte-preserved mode-`0400` wrappers. Post-blind coordinate evidence is
split across sessions `20260820_193010_a77e8d` (1 call/2 messages/0 tools) and
`20260820_193416_50af34` (7/14/0); official/glossary contact evidence is split across
`20260820_194841_5f9531` (1/2/0) and `20260820_195524_a763ec` (7/14/0). All production
sessions independently verify the same provider/model/reasoning and native direct-image route.
The split sessions preserve valid first wrappers after local helper/parser failures and retry only
the untouched suffix; the failed pre-dispatch/CLI attempts made no accepted image inference.

All eight sources are rules-bearing Mission Task faces; none is a non-rules component. The first
three resolve to exact FaceURL selectors `d6eed2`/CardID `585900`, `a9faad`/`581800`, and
`ca25da`/`530400` under deck `eabc1d`. The five generated faces resolve exactly to source sheet
`missionTaskDeck-160.jpg`, CustomDeck key `3938`, and cells 0–4, but no reliable unique
per-cell GUID/CardID selector is established. Their candidate object references are preserved,
not guessed. All eight resolve structurally to FaceURL with the same saved BackURL; that old CDN
BackURL is now HTTP 404, so paired-side pixels could not be inspected. Current publisher
rulebook, FAQ v1.2, and Objectives Help Sheet bytes match the live Awaken Realms downloads;
BGA build `260622-1220` is retained only as licensed-digital secondary evidence.

All 15 blind morphology occurrences reconcile exactly once: 2 p.40 matches (`character` and
`lander`, both on ESSENTIAL DATA), 8 explicit one-to-one no-match rows for the ringed local
player-count composites, 4 non-text component graphics, and 1 artwork-only morphology detail.
Artwork microtext/display abstentions remain outside operative material text. Every one of the
eight promotion decisions is `defer`:
- THE SUPPLY ROUTE (`missionTaskDeck-116`) and ESSENTIAL DATA (`missionTaskDeck-123`) match
  the current official operative wording, but each retains the unmatched player-count composite
  and unavailable paired-side pixels.
- PRIMARY SAMPLES (`missionTaskDeck-138`) conflicts with current official wording requiring
  escaping Characters to carry at least two Eggs, and also retains those shared blockers.
- generated PRIMARY SAMPLES uses `ALL` instead of official `2+`, retains the older Egg-removal
  wording, and has no exact per-cell object selector.
- generated PERIMETER CLEARING uses `ALL` instead of official `2+` and conflicts with the final
  “all 3 A-type Rooms must be Discovered”/Reactor condition; its selector is unresolved.
- generated THE SUPPLY ROUTE uses `ALL` instead of official `3+`, changes the final wording,
  and has no exact per-cell selector.
- generated SABOTAGE has no current official Mission Task counterpart and no exact selector.
- generated ESSENTIAL DATA omits the official second condition requiring no Unexplored
  Corridors in Section A and has no exact selector.
No official wording was substituted into assigned art. No canonical image, sidecar, source byte,
category, filename, protected target, or candidate file changed.

The reusable native-worker closure auditor reports zero errors and zero warnings. The private
projection and independent corpus rebuild are byte-identical and change exactly the eight assigned
corpus records recursively. Shared merge completed 4 trial writes, 4 exact rollback writes,
4 committed writes, and a zero-write identical re-merge. Ten focused tests and all eight global
validation commands pass; 532/532 source images decode, 390/390 corpus source hashes verify,
corpus builds are byte-stable, all eight W23 paths survive in the symbol backlog, and all eight
no-match occurrences remain explicit in selected evidence, corpus overlays, and backlog output.
Lifecycle/canonical counts remain 532 = 148 complete + 384 deferred + 0 unaccounted, queue 384,
corpus 390, and canonical pairs 78; selected evidence rises from 102 to 110 entries/runs.
Predecessor checkpoint HEAD was `48854fdd86478c1f74b614e9daa8faaa6d0beee1`; sealed data
commit is `65fff3b486ec9f59b7b1bd10f8486af4d8e91f80`. This entry is committed separately in the
following todo-only checkpoint commit, whose self-hash cannot appear in its own content.
Operational blocker: none. Canonical-promotion blockers are the exact per-card gates above.
Nothing was pushed or deployed, and no W24 work was started. The next eligible exact tuple is
current queue index 121,
`assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-05.png`
(SHA-256 `6876c41ee8d1f660f4c2ba8012c8caf0f2ccb55ca7677dfcccfb2a69e4c43e42`).

**W24 defer-only mission/objective checkpoint (2026-08-20T22:33:19Z):** Worker
`sol-max-persistent-worker-24-20260820T204740Z-p273022-2cf4d5` selected the first eight
previously unselected exact tuples walking forward from current queue index 121. There were no
selected-tuple skips. Assignment SHA-256 is
`fc2111a11af990a6d2f12f6e66a66c32b39ac5614ad9249abaa86f696874bff9`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`698d4141580f094c6bf2b44fb5603fa058a9e44ad0835802cce820b73870f3ae`:
- index 121, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-05.png`,
  SHA-256 `6876c41ee8d1f660f4c2ba8012c8caf0f2ccb55ca7677dfcccfb2a69e4c43e42`;
- index 122, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-06.png`,
  SHA-256 `f2bde768819f1158a25be0304bced07328ae7dd23b71247ebafd8fb76e9fd586`;
- index 123, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-07.png`,
  SHA-256 `fd728cde25c6429689b8c4d1208c269e80aa2031a0f2a538f9f03b9ff6769c85`;
- index 124, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-08.png`,
  SHA-256 `e3f3266defff5ad4ade7327a85ebc8878d10bcd18ad85816212c60300472ad68`;
- index 125, `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-09.png`,
  SHA-256 `5de3719f349157e4b5cda76358b68c59278ca278084c7779fed2507a3b229f4c`;
- index 126, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-003.jpg`,
  SHA-256 `be548264f79b37dd7db8ed726fcc1e9caf03c7cc20b1a4ec8ff40663935ee614`;
- index 127, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-012.jpg`,
  SHA-256 `58e9ded17f0841413f205e30c4cc63e47b23376d4be733d6fc5042c5610a04a7`;
- index 128, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-015.jpg`,
  SHA-256 `71d47a2a9ebaee6f8bca6aa88413647e8b796e37cd9ecd175d505cf1ec7e1076`.

Neutral smoke session `20260820_204938_a5f885` verified 1 API call, 2 messages, 0 tools,
exact `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name marker.
Production evidence comprises 26 native one-image calls, 52 messages, and 0 tools across five
independently DB-verified sessions: blind `20260820_205125_8df2c2` (8/16/0), bbox
`20260820_211134_a57195` (8/16/0), negative Robot-glyph check
`20260820_212425_121224` (1/2/0), glossary/paired-side contact
`20260820_213254_c88eac` (8/16/0), and negative official CLEAN-UP pixel locator
`20260820_215230_f9ad7b` (1/2/0). The strict helper assertions rejected the two valid negative
answers after inference; their wrappers were salvaged immutably with DB provenance rather than
retried or promoted. W24-003 visibly prints the word `Robot`, so no omitted morphology was added.
The current rulebook's searchable CLEAN-UP text layer is behind an occluding FACEOFF card in the
rendered pixels, so it is not claimed as visible primary face evidence. A broad prior-semantic search
occurred only after all eight blind wrappers were sealed; it is disclosed in worker metadata, its
snippets were ignored, and every later claim was re-derived from sealed W24 pixels plus direct
structured/publisher evidence.

All eight sources are rules-bearing; non-rules count is zero. W24-001..005 are FaceURL-generated
cells 5–9 of `missionTaskDeck-160.jpg`, deck GUID `eabc1d`, CustomDeck key `3938`, grid 5x2.
No authoritative structured mapping establishes a unique per-cell GUID/CardID selector, so candidate
selectors are preserved but not guessed. W24-006/007/008 resolve exactly to FaceURL selectors
`4ede1f`/CardID `533700`, `87ec86`/`533500`, and `49ba8f`/`533600` under deck `e22eaa`.
The nested save establishes each exact FaceURL/BackURL pair. All eight paired-side pixels were
inspected and classify as generic MISSION TASK or SOLO / COOP card backs without operative face
text. The live Awaken Realms manifest and downloaded current rulebook, FAQ v1.2, and Objectives
Help Sheet bytes match tracked hashes; BGA build `260622-1220` is retained only as labeled
licensed-digital secondary evidence.

All 26 blind morphology occurrences reconcile exactly once: 3 p.40 matches
(`map/hibernatorium-active` on W24-004, `general/character` on W24-006, and
`map/life-support-active` on W24-008), 6 explicit one-to-one no-match rows (the five ringed
Number-of-Characters composites plus W24-004's noncanonical Life Support pictogram), 11 non-text
component graphics, and 6 artwork-only details. Fourteen illustration/display abstentions remain
separate from operative text. Every promotion decision is `defer`:
- RETRIEVAL (W24-001) has no current publisher or BGA counterpart, no exact generated-cell
  selector, and an unmatched player-count composite.
- ERADICATION (W24-002) says the Queen must be killed and the Nest destroyed, materially
  conflicting with the current requirement that the Queen be dead and the Facility not be
  destroyed; its selector and player-count composite are unresolved.
- ESCORT MISSION (W24-003) omits Section C, “at least once,” the checkbox, and the second
  Character-with-Data escape condition; its selector and player-count composite are unresolved.
- FACILITY RESTART (W24-004) substitutes an at-least-two-Life-Support/Facility-not-destroyed
  condition for the current Life Support Control C/Reactor-shut-down requirement; it also has an
  unmatched player-count composite, a noncanonical Life Support pictogram, and no exact selector.
- ESSENTIAL DATA (W24-005) carries an all-rooms-explored condition under the wrong title instead
  of the current Data-token/Lander/no-Unexplored-Corridors requirements; its selector and
  player-count composite are unresolved.
- SCIENTIFIC SAMPLE (W24-006) has an exact selector and matched Character glyph, but only
  licensed-digital secondary wording support and no approved Solo/Coop target schema.
- CLEAN UP (W24-007) has an exact selector and no unresolved material glyph, but the apparent
  publisher card is pixel-occluded by FACEOFF; only secondary wording support remains and no
  approved Solo/Coop target schema exists.
- CLOSEDOWN (W24-008) has an exact selector and matched Life-Support-active glyph, but the FAQ
  supplies only the CLOSEDOWN/SHUTDOWN coexistence erratum, not visible primary face wording;
  BGA remains secondary and no approved Solo/Coop target schema exists.
No official wording was substituted into assigned art. No canonical image, sidecar, source byte,
category, filename, protected target, or candidate file changed.

Result assembly preflighted in workspace-local disposable clones before authoritative writes. The
reusable native-worker auditor's v1 adapter reported eight structural missing-field errors and zero
warnings; v2 then failed during adapter construction before invoking the auditor. Both views and
hash-linked failure metadata are preserved. The v3 compatibility view adds only the auditor-required
adapter fields and passes with 0 errors/0 warnings while preserving original runtime/session evidence
and result semantic digests. Private projection and independent corpus rebuild are byte-identical and
change exactly the eight assigned corpus records recursively. Shared merge completed 4 trial writes,
4 exact rollback writes, 4 committed writes, and a zero-write identical re-merge. The final
all-script audit passes 14 adapted and 11 fresh W24 scripts with no stale W23/W22 IDs, roots, hashes,
queue constants, titles, family assumptions, or direct-runner semantic leakage.

Ten focused tests and all eight documented global validation commands pass. The baseline and final
runs verify 532/532 source decodes, 390/390 corpus source hashes, reproducible/byte-stable corpus
builds, exact selected-evidence/corpus/queue/progress partitions, six unresolved no-match rows across
five backlog source paths, exact recursive eight-record scope, unchanged canonical source hashes,
and exact eight-file generated Git scope. Lifecycle/canonical counts remain 532 = 148 complete +
384 deferred + 0 unaccounted, queue 384, corpus 390, and canonical image/sidecar pairs 78; selected
evidence rises from 110 to 118 entries/runs. Predecessor checkpoint HEAD was
`9703a36481aa6fcb7490115d239ed5b777d4d856`; sealed data/QA commit is
`e84b37f637ca96e316bee8b83db0844bb1f4a2ac`. This entry is committed separately in the following
todo-only checkpoint commit, whose self-hash cannot appear in its own content.

Operational blocker: none. Canonical-promotion blockers are the exact per-card gates above. Nothing
was pushed or deployed, and no W25 work was started. The next eligible exact tuple is current queue
index 129, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-016.jpg`
(SHA-256 `755d74a481252909758bba60332e041aa0128d05536848d2160efb7dba7f76a0`).

**W25 defer-only Solo/Coop checkpoint (2026-08-21T00:01:50Z):** Worker
`sol-max-persistent-worker-25-20260820T224038Z-p308509-d39bf7` selected the first eight
previously unselected exact tuples walking forward from current queue index 129. There were no
selected-tuple skips. Assignment SHA-256 is
`202de85cbd87a114ce0289f42e30c9e3518b4ac8fc69ef1e7d953cdffa75a778`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`08fb01989c7cb0a3eb2acb26859be43acdf211985799e0f960ee46c5909c3230`:
- W25-001, index 129, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-016.jpg`,
  SHA-256 `755d74a481252909758bba60332e041aa0128d05536848d2160efb7dba7f76a0`;
- W25-002, index 130, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-061.jpg`,
  SHA-256 `399d5d96682f95850f3214635aa0616fe0c20309ddf2f2a2a79751300a75f09b`;
- W25-003, index 131, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-063.jpg`,
  SHA-256 `a9db66daeecae3e039e4e72b8f0e1ceb8d7fad4e46c6679b9eb0624b394d6155`;
- W25-004, index 132, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-078.jpg`,
  SHA-256 `f046bb036d1a7b3556faf8d3e48858ef6827590015f5721c919e018b22fb3862`;
- W25-005, index 133, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-081.jpg`,
  SHA-256 `e86422969d427c2f63defa0ff927e8f69b13040260a95b8ebf3df5712a7d7a5b`;
- W25-006, index 134, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-109.jpg`,
  SHA-256 `5a5d5ed6d8b686f5c6a702ccae176eac320bf8dc2e63303eb22cc18636f2dc19`;
- W25-007, index 135, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-113.jpg`,
  SHA-256 `62bc7df50a5d5b5075561f5b63c11603086aa3f3e335d05d346a10dfd797fa9c`;
- W25-008, index 136, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-132.jpg`,
  SHA-256 `48a564f347ba9aaf02fbb14c555ebdce7114bfc8e1a3eb06badbd87fa480c1fa`.

Neutral smoke session `20260820_224435_382a9f` verified 1 API call, 2 messages, 0 tools,
exact `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name marker.
Production evidence totals 20 native image calls, 40 messages, and 0 tools across four
independently DB-verified sessions: blind `20260820_224505_f47c2f` (8/16/0), bbox
`20260820_231125_6e36f5` (8/16/0), p.40 contact `20260820_232654_1c2354` (3/6/0),
and rendered publisher-primary audit `20260820_233320_60a676` (1/2/0). All eight blind
wrappers are byte-preserved mode `0400`; each turn re-read assignment bytes and live source
hash before attachment. No OCR, Qwen, auxiliary vision, model/reasoning downgrade, shared
provider mutation, or failed/partial production read was used.

All eight sources are rules-bearing direct Solo/Coop FaceURLs; non-rules count is zero,
generated-cell count is zero, and every face has an exact GUID/CardID selector under deck
`e22eaa`: W25-001 `73b187`/`533200`; W25-002 `ca6754`/`532600`; W25-003
`45f411`/`533000`; W25-004 `0a7868`/`533400`; W25-005 `f2908a`/`533100`;
W25-006 `837e63`/`532800`; W25-007 `0067c3`/`532900`; W25-008
`fb3106`/`532700`. All share one hash-identical BackURL at
`objectiveCoop/objectiveCoop-065.png` (SHA-256
`290d5e37d0e39ec94737865b14fb7dfe2c0e9c37e882839708d43766b9be1939`), inspected as a
SOLO/COOP card back with no operative face text. Live Awaken Realms bytes exactly match tracked
rulebook `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`, FAQ v1.2
`611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives
Help Sheet `30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364` hashes. BGA
build `260622-1220` (SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae`) remains labeled
licensed-digital secondary evidence only.

All 71 blind morphology occurrences reconcile exactly once: 3 authoritative p.40 matches
(`robot` on W25-003, `character` on W25-004, and `hibernatoriumActive` on W25-008),
0 explicit no-match/unresolved rows, 4 non-text component graphics, and 64 artwork-only details.
The 151 repeated/clipped/illegible quarantine-art transcription notes remain separate from
operative text. Publisher-primary face status is 1 exact counterpart, 1 same-title non-counterpart,
and 6 absent; BGA secondary status is 4 exact and 4 material conflicts. Every promotion decision
is `defer` and no candidate/canonical file was staged:
- SHUTDOWN (W25-001) exactly matches BGA's Solo/Coop wording, but the current publisher
  same-title pixels are a different `2+ PRIVATE OBJECTIVE`; FAQ v1.2 names the coexistence
  erratum without reproducing this face. Source gate and target-schema gate remain blocked.
- NO CORNER UNCOVERED (W25-002) exactly matches BGA secondary wording, but no current
  publisher-primary face was located and no approved Solo/Coop sidecar schema exists.
- SYSTEMS BACKUP (W25-003) has a verified `robot` glyph, but BGA prints the plural title
  `Systems Backups`; no publisher-primary face or approved target schema exists.
- CULINARY SAMPLE (W25-004) has a verified `character` glyph, but assigned art says `with an Egg`
  while BGA says `carrying an Egg`; no publisher-primary face or approved target schema exists.
- DEEP SEARCH (W25-005) exactly matches BGA secondary wording, but no current
  publisher-primary face or approved Solo/Coop target schema exists.
- FACEOFF (W25-006) exactly matches visible current rulebook pixels and BGA (`The Queen must be
  dead.`), so its source-fidelity gate passes; promotion remains blocked solely by the absence of an
  approved Solo/Coop sidecar schema.
- ENTRANCE INSPECTION (W25-007) says there must be no Unexplored Corridors in Section A, while
  BGA requires all A-type Rooms Discovered; no publisher-primary face or approved schema exists.
- SAFETY PROCEDURE (W25-008) has a verified `hibernatoriumActive` glyph, but assigned art has no
  terminal period after the parenthetical while BGA does; no publisher-primary face or approved
  target schema exists.
No official wording was substituted into assigned art; source conflicts comprise six explicit rows
across five assets and remain verbatim in durable evidence.

The reusable native-worker closure auditor passes with 0 errors/0 warnings. Private projection and
an independent corpus rebuild are byte-identical and change exactly the eight assigned corpus records
recursively. Shared merge completed 4 trial writes, 4 exact rollback writes, 4 committed writes, and
a zero-write identical re-merge. Ten focused tests and all eight documented global validation
commands pass; 532/532 sources decode, 390/390 corpus source hashes verify, corpus builds are
byte-stable, deferred/queue and selected/corpus partitions reconcile, canonical source hashes and
78 canonical image/sidecar pairs remain unchanged, and generated Git scope is exactly eight files.
The first all-script audit correctly failed only because its expected blind-runner audit artifact had
not been generated; that immutable failure is preserved. A fresh immutable direct-runner audit then
passes all checks, and all-script audit v2 passes 14 adapted plus 8 fresh W25 scripts (24-script
inventory including the two audit drivers) with 0 errors/0 warnings and no stale prior-batch constants
or semantic leakage.

Lifecycle counts remain 532 = 148 complete + 384 deferred + 0 unaccounted; queue 384, corpus 390,
and canonical pairs 78. Selected evidence rises from 118 to 126 entries/runs; W25 promotion/defer
count is 0/8. Predecessor checkpoint HEAD was `eef7eab5d14f6f3ba203f1229a0994607a0f0f78`;
sealed data/QA/shared-scope commit is `f5f6118d1928fad0602a50d197eb0632baa78c63`. This
entry is committed separately in the following todo-only checkpoint commit, whose self-hash cannot
appear in its own content. Operational blocker: none; canonical-promotion blockers are the exact
per-card gates above. Nothing was pushed or deployed, and no W26 work was started. The next eligible
exact tuple is current queue index 137,
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-178.jpg`
(SHA-256 `67c96f43ec41729b3434a24add8db95f668b2b5439c792aaedaddb56ff462472`).

**W26 defer-only Solo/Coop checkpoint (2026-08-21T04:58:35Z):** Worker
`sol-max-persistent-worker-26-20260821T035155Z-p324953-703c35` selected the first eight
previously unselected exact tuples walking forward from current queue index 137. There were no
selected-tuple skips. Assignment SHA-256 is
`ee3d7a61c99c4f05e29267e6907929209933abb5dd035306ada2720b6e82f2e1`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`c30d79ce3bad574a9b03c3dba9dd35a318b993f867b3546bd3fc3a9d898072e5`:
- W26-001, index 137, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-178.jpg`,
  SHA-256 `67c96f43ec41729b3434a24add8db95f668b2b5439c792aaedaddb56ff462472`;
- W26-002, index 138, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-002.jpg`,
  SHA-256 `440b9019aaf9e1f23b875bef44c774bb9a115152cad09f18ac375532dcfbb281`;
- W26-003, index 139, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-007.jpg`,
  SHA-256 `8400349f06425fb6a54a67bb8739041c0844ac8168fb2597ffbcc329df9e0586`;
- W26-004, index 140, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-008.jpg`,
  SHA-256 `de92b135888db44819874a9b74b871523442f22c6544e09a60619d1db75dd305`;
- W26-005, index 141, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-011.jpg`,
  SHA-256 `5f0a1dc38e2aec5bdd902112fb2cecd44cc4b3a495ff1c43f25dfb8ed075c5db`;
- W26-006, index 142, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-048.jpg`,
  SHA-256 `09f5b6cab2381b31842e877334f5d9270260de7fa305277c24e4f170ef540829`;
- W26-007, index 143, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-049.jpg`,
  SHA-256 `65802ba4b1bad2d405689998f9d4b89f83dec85ad1139925c2d61f388c096fa8`;
- W26-008, index 144, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-071.jpg`,
  SHA-256 `0fe579f8c7d045db65c4c8b44b954417ac93a7c10ef6268d273878bfb2a4bc87`.

Neutral smoke session `20260821_035414_2cfe03` verified 1 API call, 2 messages, 0 tools,
exact `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name marker.
Production evidence totals 27 native image calls, 54 messages, and 0 tools across four
independently DB-verified sessions: blind `20260821_035527_19a361` (8/16/0), bbox
`20260821_041250_a76226` (8/16/0), p.40 contact `20260821_042610_3a2653` (8/16/0),
and rendered publisher-primary audit `20260821_042954_c85a25` (3/6/0). Every blind turn
re-read frozen assignment bytes and the live source hash before attaching one image; all eight
wrappers are byte-preserved mode `0400`. No OCR, Qwen, auxiliary vision, model/reasoning
downgrade, shared-provider mutation, or failed/partial production image read was used.

All eight sources are rules-bearing direct FaceURLs; non-rules count is zero, generated-cell count
is zero, and every face has an exact GUID/CardID selector. W26-001 is under deck `e22eaa` with
selector `00c5e5`/`533300`; W26-002 through W26-008 are under deck `831e19` with selectors
`885ed3`/`534700`, `9bce12`/`535400`, `dd8d81`/`535100`, `5322b1`/`556500`,
`944b8d`/`534100`, `ad2265`/`557200`, and `74041c`/`534400`, respectively. All share
one hash-identical inspected BackURL at `objectiveCoop/objectiveCoop-065.png` (SHA-256
`290d5e37d0e39ec94737865b14fb7dfe2c0e9c37e882839708d43766b9be1939`), whose pixels
show a MISSION TASK card back without operative face text. Live Awaken Realms bytes exactly
match tracked rulebook `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`,
FAQ v1.2 `611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`,
and Objectives Help Sheet `30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`
hashes. BGA build `260622-1220` (SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae`) remains labeled
licensed-digital secondary evidence only.

All 32 blind morphology occurrences reconcile exactly once: 8 authoritative p.40 matches
(`character` x6, `lander` x1, and `shootDieCritical` x1), 0 explicit no-match/unresolved rows,
8 non-text component graphics, and 16 artwork-only details. The 24 repeated/clipped/illegible
component-art notes remain separate from operative text. Publisher-primary counterpart status is
0 exact, 0 conflicting/non-counterpart, and 8 absent; BGA secondary status is 1 exact, 0 material
conflicts, and 7 absent. No official wording was substituted into assigned art. Every promotion
decision is `defer`; no candidate/canonical file was staged:
- CRUCIAL INTELLIGENCE (W26-001) has verified `character` and `lander` glyphs and exactly
  matches the current BGA Solo/Coop record, but no current publisher-primary face/operative
  wording was located and no approved Solo/Coop sidecar schema exists.
- GENETIC UPLOAD (W26-002) has no material inline glyph; no current publisher-primary face or
  exact current BGA Solo/Coop counterpart was located, and no approved target schema exists.
- OUT OF SPACE (W26-003) has a verified `character` glyph; no current publisher-primary face or
  exact current BGA Solo/Coop counterpart was located, and no approved target schema exists.
- ONE FOR ALL (W26-004) has a verified `character` glyph; no current publisher-primary face or
  exact current BGA Solo/Coop counterpart was located, and no approved target schema exists.
- FIREWALL (W26-005) has a verified `character` glyph; no current publisher-primary face or exact
  current BGA Solo/Coop counterpart was located, and no approved target schema exists.
- COWARD (W26-006) has a verified `character` glyph; no current publisher-primary face or exact
  current BGA Solo/Coop counterpart was located, and no approved target schema exists.
- SECOND RESCUE (W26-007) has a verified `character` glyph; no current publisher-primary face or
  exact current BGA Solo/Coop counterpart was located, and no approved target schema exists.
- ELITE SHOOTERS (W26-008) has a verified `shootDieCritical` glyph; no current
  publisher-primary face or exact current BGA Solo/Coop counterpart was located, and no approved
  target schema exists.
There are no material TTS/publisher/BGA wording conflicts in this batch. The exact promotion
gates remain absence of a current publisher-primary counterpart for every asset, absence of an
exact current licensed-secondary counterpart for W26-002 through W26-008, and the unsupported
canonical Solo/Coop sidecar schema for all eight.

The reusable native-worker closure auditor passes with 0 errors/0 warnings. Its successful output
was preserved through a hash-linked closure continuation after a report-only `runId` field-shape
error. Earlier disposable adapter failures (one list/object normalization mismatch and two stale
closure constants) are preserved under `metadata/failures/`; no immutable vision evidence or
shared bytes were affected. Private projection and independent corpus rebuild are byte-identical
and change exactly the eight assigned corpus records recursively. Shared merge completed 4 trial
writes, 4 exact rollback writes, 4 committed writes, and a zero-write identical re-merge. Ten
focused tests and all eight documented global validation commands pass; 532/532 sources decode,
390/390 corpus source hashes verify, corpus builds are byte-stable, reproducibility passes,
deferred/queue and selected/corpus partitions reconcile, canonical source hashes and 78 canonical
image/sidecar pairs remain unchanged, and generated Git scope is exactly eight files. The first
all-script audit failed closed on its own deliberate prior-worker reference, v2 passed its then-live
inventory, and final audit passes all 16 adapted plus 10 fresh W26 scripts (26 total) with 0
errors/0 warnings and no stale prior-batch constants or blind semantic leakage.

Lifecycle counts remain 532 = 148 complete + 384 deferred + 0 unaccounted; queue 384, corpus 390,
and canonical pairs 78. Selected evidence rises from 126 to 134 entries/runs; W26 promotion/defer
count is 0/8. Predecessor checkpoint HEAD was `10c33ad17df1e5a54f13b19aea358344eb6c4c64`;
sealed data/QA/shared-scope commit is `6bcb14739e69eca7ecb27b20e0eae9aac704ffaa`. This entry
is committed separately in the following todo-only checkpoint commit, whose self-hash cannot
appear in its own content. Operational blocker: none; canonical-promotion blockers are the exact
per-card gates above. Nothing was pushed or deployed, and no W27 work was started. The next
eligible exact tuple is current queue index 145,
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-075.jpg`
(SHA-256 `1aeaa05448d03a083f8c585a4ccaaf2bef716c21cfe0b44c86d169583e3599c1`).

**W27 defer-only Solo/Coop Mission Task checkpoint (2026-08-21):** Worker
`sol-max-persistent-worker-27-20260821T054548Z-p346913-ace062` selected the first eight
previously unselected exact tuples walking forward from current queue index 145. There were no
selected-tuple skips and no wraparound. Assignment SHA-256 is
`0beb1008314ea4ee617c2737b32a4ba7300d1b079306201d4ce0f10aef593a4e`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`cf0b6c06acb916fae4a91c340932eb4bc058ba6b44f084b27e189ab4c102c483`:
- W27-001, index 145, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-075.jpg`,
  SHA-256 `1aeaa05448d03a083f8c585a4ccaaf2bef716c21cfe0b44c86d169583e3599c1`;
- W27-002, index 146, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-077.jpg`,
  SHA-256 `3268218a1f202c8bd6b76fb41356d8dee4e4e3fbc07bcb6381c5411c27f27860`;
- W27-003, index 147, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-079.jpg`,
  SHA-256 `6148e0cddb908bdb607aef3626cdf42300513e4c1b89b6ef3e929c29aaff1e1e`;
- W27-004, index 148, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-080.jpg`,
  SHA-256 `c73369d75953efcf42ab762e58fa99dc1db798ab3aa52d8d3995e562a41374a0`;
- W27-005, index 149, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-082.jpg`,
  SHA-256 `6fc50e739e56f4d1245f6f603a57dc69c3045f77de594925b54dd55c94e00c3e`;
- W27-006, index 150, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-089.jpg`,
  SHA-256 `80bd7e8c886855f77086b42930d9903b61fab3bcb98817eac23002296baeb46f`;
- W27-007, index 151, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-102.jpg`,
  SHA-256 `ec97601c529803b11a6445cb9f22939e5192723af3d78b91410c07a267999c6a`;
- W27-008, index 152, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-103.jpg`,
  SHA-256 `5b99b1dab8c5987946aa64b83efd0afe579583bfaa13ea569e470df10c3bd832`.

Neutral smoke session `20260821_055044_471a8d` verified 1 API call, 2 messages, 0 tools,
exact `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name marker.
Production evidence totals 15 direct native image calls, 30 messages, and 0 tools across four
independently DB-verified sessions: blind `20260821_055301_4de870` (8/16/0), focused bbox
`20260821_062716_22a82f` (2/4/0), exhaustive all-49 p.40 contact
`20260821_063250_159a74` (2/4/0), and publisher-primary visible-page audit
`20260821_063740_918fc9` (3/6/0). Every blind turn re-read frozen assignment bytes and the
live source hash before attaching one image; all eight wrappers and raw copies are byte-preserved
mode `0400`. No OCR, Qwen, auxiliary vision, model/reasoning downgrade, shared-provider mutation,
or failed/partial production image read was used.

All eight sources are rules-bearing direct FaceURLs; non-rules and generated-cell counts are zero.
Every face resolves to one exact CardCustom GUID/CardID selector under deck `831e19`:
W27-001 `687177`/`535000`; W27-002 `9aa0dd`/`534000`; W27-003
`0e82e9`/`535500`; W27-004 `d992ce`/`535200`; W27-005
`4230c8`/`534800`; W27-006 `0af5f9`/`535300`; W27-007
`b608be`/`533900`; W27-008 `b73d96`/`534200`. All share one
hash-identical inspected BackURL at
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-065.png`
(SHA-256 `290d5e37d0e39ec94737865b14fb7dfe2c0e9c37e882839708d43766b9be1939`),
whose pixels show a generic `SOLO / COOP MISSION TASK` card back with no operative rules text.
The face footer plus paired back establish the source family as Solo/Coop Mission Task; no
filename/folder alias was used as semantic evidence.

All 66 enumerated blind morphology occurrences reconcile exactly once: 2 authoritative p.40
matches, 0 explicit no-match rows, and 64 artwork-only warning/tape details. W27-001
`NOT TAKING ANY CHANCE` matches its inline glyph to `robot`; W27-008 `DEN HUNT` matches its
inline glyph to `character`. Sixteen additional non-text frame/glow graphics are preserved
separately rather than double-counted in the 66-occurrence ledger, along with 183 non-rules
illustration/background transcription details. The other exact assigned titles are
`COMPLETE MAPPING`, `PREDATORS`, `ORGANIC SUPPLY`, `HQ TAKE BACK`, `OUR STAND`, and
`COLLECTORS`.

Fresh Awaken Realms bytes exactly match tracked rulebook
`e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`, FAQ v1.2
`611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives
Help Sheet `30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`
hashes. Visible-pixel review of rulebook page 3 and both Objectives Help Sheet pages, plus exact-title
searches over all three fresh text derivatives, found zero current publisher-primary counterparts for
the eight assigned titles. Current BGA build `260622-1220` (SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae`) contains 35
keyed mission/objective display-name records and likewise has zero exact-title counterparts. Generic
wording overlap was not promoted as identity. Current-authority wording-conflict count is zero; source
support is absent rather than conflicting.

Five conflicts with the prior unselected corpus snapshot are preserved explicitly: W27-001 corrects
prior `[lander]` to directly matched `[robot]`; W27-008 corrects prior `[robot]` to directly matched
`[character]`; W27-002 preserves visibly straight quotation marks around `"?"` against the prior
curly quotes; and W27-003/W27-005 leave the illustrated warning marks semantically unnamed instead
of retaining prior unsupported `biohazard` labels. The historical printedData remains provenance;
no approved canonical file was overwritten. All eight promotion decisions remain `defer` because
no exact current publisher-primary or licensed-digital title counterpart exists and the repository has
no approved Solo/Coop Mission Task canonical image/sidecar schema or directory. No candidate,
canonical image, sidecar, source byte, category, or filename was created or changed.

The reusable native-worker closure auditor passes through its hash-linked compatibility view with
0 errors/0 warnings; original assignment/runtime/raw/result evidence is unchanged. Independent worker
closure parses 97 worker JSON files and passes exact source/session/morphology/conflict/lifecycle checks.
Private projection and independent corpus rebuild are byte-identical and change exactly the eight
assigned corpus records recursively. Shared merge completed 4 trial writes, 4 exact rollback writes,
4 committed writes, and a zero-write identical re-merge. Ten focused tests and all eight documented
global validation commands pass; 532/532 sources decode, 390/390 corpus source hashes verify, two
explicit corpus builds are byte-identical at
`f664a32167dcad9acffcb2496a0f3eadb5b256b302554323f689967a9f618ebc`, W27 paths are absent
from the unresolved-symbol backlog, canonical source hashes are unchanged, and generated Git scope is
exactly eight files. Final stale-constant audit passes all 24 W27 scripts with 0 errors/0 warnings; its
first self-referential `w26-` allow-list failure is preserved worker-locally, as are one corrected
BGA duplicate-display-name assertion and one pre-execution result-builder syntax failure. None changed
shared or immutable evidence.

Lifecycle counts remain 532 = 148 complete + 384 deferred + 0 unaccounted; queue 384, selected
registry/corpus overlays 142, genuinely unselected queue tuples 242, corpus 390, canonical pairs 78,
and deferred re-examinations 116. The unresolved-symbol backlog now contains 246 occurrences across
135 assets. Predecessor checkpoint HEAD was `68cd74a36a5fea1f0c9c4e2c75fce98e0bd57194`; sealed
data/QA/shared-scope commit is `2a6ab17c29a7eeb89d5ca6c3aa13f496d417916e`. This entry is
committed separately in the following todo-only checkpoint commit, whose self-hash cannot appear in
its own content. Operational blocker: none. Canonical-promotion blockers are the exact source-support
and schema gates above. Nothing was pushed or deployed, and no W28 work was started. The next eligible
exact tuple is current queue index 153,
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-105.jpg`
(SHA-256 `608248600b4d9fdb4e49112bbab74f616978ceb2335dbbe6bbb9275741fc9138`);
wraparound was not required.

**W28 defer-only Solo/Coop Mission Task checkpoint (2026-08-21T08:01:08Z):** Worker
`sol-max-persistent-worker-28-20260821T071525Z-p362032-1fed87` selected the first eight
previously unselected exact tuples walking forward from current queue index 153. There were no
selected-tuple skips and no wraparound. Assignment SHA-256 is
`1d6d31b21832dd450be874ac52e7d3193299644c4f07d703255118ca2a1506b7`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`ad1264da86be4d97f13249bf177b37af6d87b0adea8e033f7e02f089702b10dc`:
- W28-001, index 153, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-105.jpg`,
  SHA-256 `608248600b4d9fdb4e49112bbab74f616978ceb2335dbbe6bbb9275741fc9138`;
- W28-002, index 154, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-106.jpg`,
  SHA-256 `32405644fa1317e3363cba6318edf2231f15a5d2b3f6ac1a2f28e54eddbae250`;
- W28-003, index 155, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-111.jpg`,
  SHA-256 `538b3413171bb3c6f529e91068cd3fe1487f6bc366dc41163b04e54764917983`;
- W28-004, index 156, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-119.jpg`,
  SHA-256 `ff09f521ece8fb88ff0a703907158121a0d850341101ded2919eac85e89bc480`;
- W28-005, index 157, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-121.jpg`,
  SHA-256 `4dc870d681bf40276145b0e0c9c051397eccd38a836b5fb43fc8c4b5107e3473`;
- W28-006, index 158, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-122.jpg`,
  SHA-256 `de4d97fbae3b2bd3514fae4d51bad194d461f6df9d8d26ac9c34ea2328d92548`;
- W28-007, index 159, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-124.jpg`,
  SHA-256 `33b4d988858b45215a8de460c1cf0ff8ec24aa5343e09c698b913f0b83443e3c`;
- W28-008, index 160, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-127.jpg`,
  SHA-256 `5e73b9b5b7a9f089da13689c0e7717927339b9802669807fd8226e3f9bc08559`.

Neutral smoke session `20260821_071717_d657fc` verified 1 API call, 2 messages, 0 tools,
exact `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name marker.
Production evidence totals 16 direct native image calls, 32 messages, and 0 tools across three
independently DB-verified sessions: blind `20260821_071741_437876` (8/16/0), exhaustive
all-49 p.40 contact `20260821_074543_a084dd` (5/10/0), and publisher-primary rendered-page
audit `20260821_074851_078999` (3/6/0). Every blind turn re-read frozen assignment bytes and
the live source hash before attaching one image; all eight wrappers and raw copies are byte-preserved
mode `0400`. No OCR, Qwen, auxiliary vision, model/reasoning downgrade, shared-provider mutation,
or failed/partial production image read was used.

All eight sources are rules-bearing direct FaceURLs; non-rules and generated-cell counts are zero.
Every face resolves to one exact CardCustom GUID/CardID selector under deck `831e19`:
W28-001 `805300`/`557300`; W28-002 `8f872c`/`535600`; W28-003
`f4c940`/`536200`; W28-004 `057afa`/`536400`; W28-005
`00ed69`/`535900`; W28-006 `db4ced`/`536100`; W28-007
`80784d`/`557100`; W28-008 `3b99d9`/`536000`. All share one
hash-identical inspected BackURL at
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoop/objectiveCoop-065.png`
(SHA-256 `290d5e37d0e39ec94737865b14fb7dfe2c0e9c37e882839708d43766b9be1939`),
whose pixels show a generic card back with no operative rules text and support the saved BackURL role.
The face footer plus paired back establishes the source family as Solo/Coop Mission Task; no
filename/folder alias was used as semantic evidence.

All 69 enumerated blind morphology occurrences reconcile exactly once: 5 authoritative p.40
matches, 0 explicit no-match rows, and 64 artwork-only warning/tape details. `character` matches on
THIRD RESCUE (W28-001), RECKLESS (W28-002), TACTICAL DECISION (W28-006), and RESCUE
(W28-007); `lander` matches on SCHEDULE (W28-004). TECHNICAL SUPPLY (W28-003), SECRET
ROOMS (W28-005), and SECURED PERIMETER (W28-008) contain no material inline glyph. Twenty-four
additional non-text frame/glow graphics and 176 clipped/repeated background details remain separate
from the 69-occurrence ledger and operative text.

Fresh Awaken Realms bytes exactly match tracked rulebook
`e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`, FAQ v1.2
`611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives
Help Sheet `30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`
hashes. Both Objectives Help Sheet pages visibly lack all eight exact titles; rulebook page 3 is
`occluded-not-visible` and is not promoted from its searchable layer. All exact titles are absent from
the three fresh publisher text derivatives and from the 35 display-name records in BGA build
`260622-1220` (SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae`). Current-authority
wording-conflict count is zero; support is absent rather than conflicting, and no official/BGA wording
was substituted into assigned art.

Four conflicts with the prior unselected corpus snapshot remain explicit historical evidence:
W28-004 replaces the morphology-only `[ICON: white spacecraft-like silhouette]` with directly matched
`[lander]`; W28-001, W28-007, and W28-008 leave illustrated warning/tape marks semantically unnamed
instead of retaining prior unsupported `biohazard` labels. All eight promotion decisions remain
`defer`: none has an exact current publisher-primary or licensed-digital title counterpart, and the
repository has no approved Solo/Coop Mission Task canonical image/sidecar schema or directory. No
candidate, canonical image, sidecar, source byte, category, or filename was created or changed.

The reusable native-worker closure auditor passes through its hash-linked compatibility view with
0 errors/0 warnings; original assignment/runtime/raw/result evidence remains unchanged. Independent
closure parsed 92 worker JSON files before reports and 97 after the worker checkpoint; the final
read-only precommit probe parsed 115. The all-script audit passes 22 W28 scripts with 0 errors/0
warnings and no stale prior-batch constants or blind semantic lookup. Private projection and
independent corpus rebuild are byte-identical and change exactly the eight assigned corpus records
recursively. Shared merge completed 4 trial writes, 4 exact rollback writes, 4 committed writes, and
a zero-write identical re-merge.

Ten focused tests and all eight documented global validation commands pass; 532/532 sources decode,
390/390 corpus source hashes verify, two explicit corpus builds are byte-identical at
`7682341cea1c29e913b1526c8e2654693bc60c002a066c0dec87e7dbd4edbc6a`, W28 paths are absent
from the unresolved-symbol backlog, canonical source hashes are unchanged, and generated Git scope is
exactly eight files. Lifecycle counts remain 532 = 148 complete + 384 deferred + 0 unaccounted;
queue 384, selected registry/corpus overlays 150, genuinely unselected queue tuples 234, corpus 390,
canonical pairs 78, and deferred re-examinations 124. The unresolved-symbol backlog now contains
241 occurrences across 131 assets.

Predecessor checkpoint HEAD was `95bfa2f5c3f2543c3e6fb2e071cc97229ffbfb72`; sealed
data/QA/shared-scope commit is `52be699ce769253997773da762fedd5f1c12a0fc`. This entry is
committed separately in the following todo-only checkpoint commit, whose self-hash does not appear in
its own content. Recovered local helper failures (line-wrapped cursor parsing and two shell-quoting
adaptation attempts) are preserved worker-locally and made no accepted inference or shared-state
change. Operational blocker: none; canonical-promotion blockers are the exact source-support and
schema gates above. Nothing was pushed or deployed, and no W29 work was started. The next eligible
exact tuple is current queue index 161,
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-129.jpg`
(SHA-256 `2f5eb390fbcbd4babb0979f41528a77773dda68c3794d77d23a15a0663daaf29`);
wraparound was not required.

**W29 defer-only mixed objective checkpoint (2026-08-21T10:08:58Z):** Worker
`sol-max-persistent-worker-29-20260821T080826Z-p346900-1f117c` selected the first sixteen
previously unselected exact tuples walking forward from current queue index 161. There were no
selected-tuple skips and no wraparound. Assignment SHA-256 is
`86b678a0e0a8d98fd6da36ad44647f0e590ae5038bbe62ddcfcb35d6e3d3d62b`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`d1b47e4d6aa63d587e39c335a130a90b478da0cac0d3f90c1327b5e098d530e0`:
- W29-001, index 161, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-129.jpg`,
  SHA-256 `2f5eb390fbcbd4babb0979f41528a77773dda68c3794d77d23a15a0663daaf29`;
- W29-002, index 162, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-168.jpg`,
  SHA-256 `a0ac21b0a010c13f03e0c6365ea922b3093f7084d800ce636a4f38c829324835`;
- W29-003, index 163, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveCoopCustomDeck-169.jpg`,
  SHA-256 `f223acb6260191bedb9ecc04e9020aa20210776e179ab51a4eb37b81b2de9b82`;
- W29-004, index 164, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-060.jpg`,
  SHA-256 `a9fd755086b0399a89adcb5d2ed4e351674cfb2a039d7bd148c268d6a1252001`;
- W29-005, index 165, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-070.jpg`,
  SHA-256 `f62fadd79394572a6f593e17f9a2470cf03d99f833cb3145253a7c19f6f0bb25`;
- W29-006, index 166, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-00.png`,
  SHA-256 `10357f3fdbce0dd9b6bfd9f297c965234e6cfbad9427d917a7b6b29384952a7d`;
- W29-007, index 167, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-01.png`,
  SHA-256 `fd4010eb58756e3de8ddb635a7325e569401d9244c37627d659f52d369dd9522`;
- W29-008, index 168, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-02.png`,
  SHA-256 `76866355163159b1cadefc9cde089972b36bea6af9c41a2e5dd636cae7d6d663`;
- W29-009, index 169, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-03.png`,
  SHA-256 `d27fc8c094ad7030557fe0d9fad0edffeee0c289ca181f05d5fba28db45bd064`;
- W29-010, index 170, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-04.png`,
  SHA-256 `2274d4d189d85a2a885478757d7aa13b07c48b912663a264c1dc7c0f9b2702b4`;
- W29-011, index 171, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-05.png`,
  SHA-256 `be5a8b408b777fd45b519176f4851b1e3af42b8f6a011470fc4b361d0d2cf10c`;
- W29-012, index 172, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-06.png`,
  SHA-256 `ee17501afeb2c1fbdc1d63378869644b9cdc9cc34c14e688c8bc0284d4093368`;
- W29-013, index 173, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-07.png`,
  SHA-256 `1633b48e698f6a00101d5189f5de7b05e4250f39d3f8df30f6c952b654f33848`;
- W29-014, index 174, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-08.png`,
  SHA-256 `0992c5b74134390a6b8dc6bb0794f40037a0e8f6b46d6268a64b26c2b975b0b8`;
- W29-015, index 175, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-09.png`,
  SHA-256 `30c6cf858a1428f2817cca3afb8959973ff59a81932d94918cc31a8b10b1a38f`;
- W29-016, index 176, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-10.png`,
  SHA-256 `27ea16e7ccca56021ba1b7189c0d8b3359102995caa169a15184c74e22574c6d`.

Neutral smoke session `20260821_081017_264a52` verified 1 API call, 2 messages, 0 tools,
exact native `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name
marker. Production evidence totals 45 direct native image calls, 90 messages, and 0 tools across
five independently DB-verified sessions: blind `20260821_081033_ca695b` (16/32/0), exhaustive
all-49 contact `20260821_084809_6004af` (16/32/0), publisher pages prefix
`20260821_090021_ca773d` (4/8/0), publisher pages suffix `20260821_091404_0c3ce7`
(3/6/0), and focused display text `20260821_092737_65f4bf` (6/12/0). The prefix publisher
session was retired after a post-inference helper-contract failure; its valid fourth response was
salvaged byte-exact from the read-only session DB, zero semantic fields changed, and only the three
untouched pages ran in the fresh suffix session. Every blind turn reread frozen assignment bytes and
the live source hash; all 16 wrappers/raw copies are mode `0400`. No OCR, Qwen, auxiliary vision,
model/reasoning downgrade, shared-provider mutation, or repeated accepted page read was used.

All 16 sources are rules-bearing and zero are non-rules: 3 Solo/Coop Mission Task faces, 8 Mission
Objective faces, and 5 Personal Objective faces. Five are downloaded FaceURLs and 11 are generated
cells of `objectiveMissonDeck-162.jpg`. W29-001/002/003 have singular exact selectors
`21b528`/`533800`, `ff8d9c`/`534500`, and `8c531f`/`599200`. W29-004 preserves exact
duplicate GUIDs `37829f` and `c600ff` for CardID `529900`; W29-005 preserves `d711ab` and
`263495` for CardID `553000`. The generated cells preserve both deck lineages (`fae6cf` and
`263314`) and every candidate reference, but no CardID-modulo or other unsupported per-cell selector
was inferred. All 16 FaceURL roles and paired BackURLs are resolved. Direct pixels classify the first
three paired sides as `SOLO / COOP / MISSION TASK` backs (SHA-256
`290d5e37d0e39ec94737865b14fb7dfe2c0e9c37e882839708d43766b9be1939`) and the
other 13 as `OBJECTIVE` backs (SHA-256
`7de29dc173947c5c01c3b95d7c63dfed1bdbc1b5571b233b2f10d9c02efb91a5`), all with zero
operative rules text.

All 43 enumerated blind morphologies reconcile exactly once: 5 authoritative page-40 matches
(`character` x4 on BEST BUDDIES and NO ONE LEFT BEHIND; `grenadeToken` x1 on EXPLODING
SOLUTION), 15 explicit one-to-one no-match rows, and 23 artwork-only details. Sixty-seven separate
non-text component graphics remain separate. W29-004 through W29-014 each retain one no-match
round-topped white form over blue rings; W29-015 retains that occurrence plus the unmatched white
three-section Life Support capsule; W29-016 retains the ringed form plus the visibly labeled `OR`
divider as an unmatched page-40 occurrence. Six focused 3x rereads independently classify the
central blue displays on W29-006..011 as environmental artwork, not operative setup text; prior draft
setup wording was not reused. The durable analyzer now serializes selected unresolved occurrences
one-for-one, suppresses stale legacy tokens for selected records, and preserves historical selected
`match`/`no-match`/`uncertain` compatibility. W29 contributes exactly 15 selected no-match backlog
rows across 13 source paths.

Fresh Awaken Realms bytes exactly match tracked rulebook
`e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`, FAQ v1.2
`611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives
Help Sheet `30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`.
Current publisher-primary component pixels exactly support W29-004..009, materially conflict with
W29-010..015, and provide no visible exact counterpart for W29-001..003 or W29-016. BGA build
`260622-1220` (SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae`) independently has
the same 6 exact / 6 conflict / 4 absent split as labeled licensed-digital secondary evidence.
Eight visible publisher conflict rows and 14 total publisher/BGA conflict rows are preserved verbatim;
27 conflicts with the prior unselected corpus snapshot are also explicit. No official/BGA wording was
substituted into assigned art.

Every promotion decision is `defer`; no candidate, canonical image, sidecar, source byte, category,
or filename changed. W29-001..003 and W29-016 lack a current exact publisher/BGA title counterpart;
W29-010..015 conflict with current publisher pixels; W29-004..015 retain at least one no-match;
W29-004/005 lack a singular direct selector; W29-006..016 lack exact generated-cell selectors; and
all 16 lack an approved canonical schema/directory for their objective family. The worker closure and
hash-linked reusable native-worker auditor pass with 0 errors/0 warnings. Final script audit passes
46 W29 scripts with 0 errors/0 warnings and no stale prior-batch constants or blind semantic lookup.
Private projection, independent corpus rebuild, and v4 shared merge are byte-idempotent; the final
merge performed 4 trial writes, 4 exact rollback writes, 4 committed writes, and a zero-write
identical re-merge. Fail-closed helper/validator attempts and three exact shared/QA rollback cycles
are preserved worker-locally; each restored the sealed W28 preimage before repair and none altered
immutable vision evidence or canonical/source bytes.

Eleven focused tests and all eight documented global validation commands pass; 532/532 source
images decode, 390/390 corpus source hashes verify, and two explicit corpus builds are byte-identical
at `7f4e3574dd6fd8f27112db3de4298a1100f279073306cee240e71e7a5b235ea0`.
Exact recursive corpus scope is 16 assigned records; canonical hashes and 78 image/sidecar pairs are
unchanged; final generated/code Git scope is exactly 10 files. Lifecycle counts remain
532 = 148 complete + 384 deferred + 0 unaccounted; queue 384, selected registry/corpus overlays
166, genuinely unselected queue tuples 218, corpus 390, canonical pairs 78, and deferred
re-examinations 140. The reconciled unresolved-symbol backlog contains 212 occurrences across 126
assets, including the exact 15 W29 rows.

Predecessor checkpoint HEAD was `fc2bf4e4c9dd46dca62f1490819dbf1f3197582c`; sealed
data/QA/shared/code commit is `2d778ab4953b51df4383e907e21e2b8d044ce629`. This entry is
committed separately in the following todo-only checkpoint commit, whose self-hash does not appear in
its own content. Operational blocker: none; canonical-promotion blockers are the exact per-family,
source-conflict, unresolved-morphology, and selector gates above. Nothing was pushed or deployed,
and no W30 work was started. The next eligible exact tuple is current queue index 177,
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-11.png`
(SHA-256 `d6ccc53b53a98ce5e212d701c0523d8a2a343d1e6d759318585a8dc278b316b2`);
wraparound was not required.

**W30 defer-only personal/private-objective checkpoint (2026-08-21T11:19:20Z):** Worker
`sol-max-persistent-worker-30-20260821T102147Z-p346900-971773` selected the first sixteen
previously unselected exact tuples walking forward from current queue index 177. There were no
selected-tuple skips and no wraparound. Assignment SHA-256 is
`42004efb7c7e573cd3ab53a45421c2d2a4af428e078d9a1f7e6d6d09ce5fc0fc`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is
`9e3e82a0c349917648bc7edc6e3cbcb829548441a6769c49e6da93d6bd989844`:
- W30-001, index 177, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-11.png`,
  SHA-256 `d6ccc53b53a98ce5e212d701c0523d8a2a343d1e6d759318585a8dc278b316b2`;
- W30-002, index 178, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-12.png`,
  SHA-256 `0c8456bddc9b959a53b9cd56994555a71f8f2595b9361416e1c6985c8e749092`;
- W30-003, index 179, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-13.png`,
  SHA-256 `36f51a02097dfa1beadb7519fd46df8aade3c8132583a8e74ca3b4a9cac14727`;
- W30-004, index 180, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-14.png`,
  SHA-256 `9a2ab1c3cb5d743381be7df987e96f47bdeaf729d82fe18052409b42d42d762d`;
- W30-005, index 181, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-15.png`,
  SHA-256 `1f94620da15b61eaa4dce6ba5533b57c38502cb6112599cba09786659db7f083`;
- W30-006, index 182, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-16.png`,
  SHA-256 `9e42ffc3f4c75305c8eae3d8f25856d3625cc112c9b231ad4030708ff4952446`;
- W30-007, index 183, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-17.png`,
  SHA-256 `0d8879f3bcd2191607423ce00eaa1e4da150c151b3f5583c661903a3568b8168`;
- W30-008, index 184, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-18.png`,
  SHA-256 `d7066d565c1617eee42cfca1a8099623975ecdaed9d63fae9563cd7f4b0c3b23`;
- W30-009, index 185, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-19.png`,
  SHA-256 `518f750e52720a13a626822da482dc87879fa47751cad7d583e482e315b8e5b8`;
- W30-010, index 186, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-20.png`,
  SHA-256 `86c8acf32ca511709d86d2633a6f586259fe52c82c0f2c08775d9fb0788649ec`;
- W30-011, index 187, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-014.jpg`,
  SHA-256 `628fc9f78b4a26e405034fcf3f0d855b010d7125e173d79fbcca6c3668e95892`;
- W30-012, index 188, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-043.jpg`,
  SHA-256 `de1213ee6a5b5489a9c7463e9532d2d4ae40b07975db38b9472f72d590f6218c`;
- W30-013, index 189, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-066.jpg`,
  SHA-256 `616161bbdb4c758a5b864d514cf12087c7de6cbc293287558a261fd0bbe5960a`;
- W30-014, index 190, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-091.jpg`,
  SHA-256 `9958d19068c020fd4fa6410016726bb697d55a30328e80c06f8d3885b9fa0f4b`;
- W30-015, index 191, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-095.jpg`,
  SHA-256 `144260585a868a5317b9f4a49b9b8942dc9373158237e72063fdc5388edac197`;
- W30-016, index 192, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-156.jpg`,
  SHA-256 `e5400e99d8671d21bdb4e16506a4533e4f4405e0a402217b039ba3326fcf178b`.

Neutral smoke session `20260821_102358_fb906f` verified 1 API call, 2 messages, 0 tools,
exact native `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored Tools/tool-name
marker. Production evidence totals 39 direct native image calls, 78 messages, and 0 tools across
three independently DB-verified sessions: blind `20260821_102416_61ceea` (16/32/0), exhaustive
all-49 contact plus paired-side inspection `20260821_104731_543f84` (16/32/0), and current
publisher rendered-page audit `20260821_105701_c44f35` (7/14/0). Every blind turn reread the
frozen assignment and live source hash before attachment; all 16 wrappers/raw copies are mode
`0400`. No OCR, Qwen, auxiliary vision, model/reasoning downgrade, shared-provider mutation,
failed production turn, or session split was used.

All 16 assigned sources are rules-bearing FaceURLs and zero are non-rules. W30-001..010 are
generated cells 11–20 of `objectiveMissonDeck-162.jpg` across exact deck lineages `263314` and
`fae6cf`; every candidate reference is preserved, but no singular per-cell selector is inferred.
W30-011..016 are downloaded FaceURLs with exact GUID/CardID selectors, respectively:
`6fd912`/`530100`, `72e954`/`529700`, `e5ecaa`/`530000`, `0df957`/`590600`,
`e0580b`/`529800`, and `6ffcf3`/`447900`, all under deck `263314`. Every exact reference set,
FaceURL role, and paired BackURL is resolved. The shared paired side was directly inspected as a
generic `OBJECTIVE` back with no operative rules text at SHA-256
`7de29dc173947c5c01c3b95d7c63dfed1bdbc1b5571b233b2f10d9c02efb91a5`.
W30-001..015 visibly belong to the Personal/Private Objective family; W30-016 visibly carries a
`PROTOTYPE` watermark and nonstandard `C O R P O R A T E` footer and is preserved as prototype
evidence rather than normalized.

All 18 enumerated functional morphologies reconcile exactly once: 2 authoritative page-40 matches
(`lifeSupportInactive` on SHUTDOWN and `actionCard` in THE GREAT HUNT's separate instruction
panel) and 16 explicit one-to-one no-match rows. The no-match on every assigned face is the same
material ringed player-count emblem: a white round-topped/flared upright form over nested cyan-blue
oval rings that directly differs from the articulated page-40 `character` crop. No player-count
semantic token was invented. Fifty-seven separate non-text component graphics, 91 artwork details,
and 25 non-rules illustration/text abstentions are preserved outside operative objective text.

Fresh Awaken Realms manifest downloads exactly match tracked rulebook
`e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`, FAQ v1.2
`611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives
Help Sheet `30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`
bytes. Current visible publisher components exactly support only THE GREAT HUNT, materially conflict
with W30-001/009/010/011/012/013/015, and provide no visible exact counterpart for the other eight.
Current BGA build `260622-1220` (SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae`) is exact only for
THE GREAT HUNT, materially conflicts with twelve assigned faces, and has no exact-title record for
LAB RATS, OLD FRIEND, or TRAITOR IN PLAIN SIGHT. Seven publisher-primary and 19 total
publisher/BGA conflict rows remain verbatim. Three discrepancies with the prior unselected corpus
snapshot are also explicit: one on W30-003 and two on the visibly prototyped W30-016. No official or
BGA wording was substituted into assigned art.

Every promotion decision is `defer`; no candidate or canonical image, sidecar, source byte, category,
or filename changed. Every face retains the unresolved ringed player-count occurrence and lacks an
approved Personal/Private/Corporate Objective canonical schema/directory; W30-001..010 additionally
lack singular cell selectors; fifteen faces lack an exact current publisher-primary source-fidelity
pass; seven have direct publisher wording conflicts; and W30-016 is visibly prototype-marked. THE
GREAT HUNT's exact current publisher/BGA wording and matched `actionCard` still do not override its
unresolved player-count emblem or missing target-schema gate.

Core and independent worker closure pass, and the reusable native-worker auditor passes through its
hash-linked compatibility view with 0 errors/0 warnings while original evidence stays unchanged.
Private projection and independent corpus rebuild are byte-identical and change exactly the sixteen
assigned corpus records recursively. Shared merge completed 4 trial writes, 4 exact rollback writes,
4 committed writes, and a zero-write identical re-merge. Eleven focused tests and all eight
documented global validation commands pass; 532/532 source images decode, 390/390 corpus source
hashes verify, all sixteen no-match rows survive in selected evidence/corpus/backlog, canonical
source hashes and 78 image/sidecar pairs remain unchanged, and two explicit corpus builds are
byte-identical at `a7f0dd93541e8b438a0bdfe2c51835d7c6daa89411a450b0c2c61834649c7409`.
Final generated/QA Git scope was exactly eight files.

Lifecycle counts remain 532 = 148 complete + 384 deferred + 0 unaccounted; queue 384, selected
registry/corpus overlays 182, genuinely unselected queue tuples 202, corpus 390, canonical pairs 78,
and deferred re-examinations 156. The reconciled unresolved-symbol backlog contains 227 occurrences
across 141 assets. Predecessor checkpoint HEAD was
`b44712a5fd93644fc3d85006bde61be204a62e2e`; sealed data/QA/shared-scope commit is
`7ff22eaf5781a2568d75b67a05e10aad8d45433f`. This entry is committed separately in the
following todo-only checkpoint commit, whose self-hash does not appear in its own content.
Operational blocker: none; canonical-promotion blockers are the exact per-family, source-conflict,
ringed-player-count, generated-selector, prototype, and schema gates above. Nothing was pushed or
deployed, and no W31 work was started. The next eligible exact tuple is current queue index 193,
`assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-157.jpg`
(SHA-256 `f420a43cbda8bc562b02eb0656f0f1cf80bdd97d95092a9ad84a69e12c089b02`);
wraparound was not required.

**W31 defer-only mixed-component checkpoint (2026-08-21T13:53:16.910066Z):** Worker
`sol-max-persistent-worker-31-20260821T112612Z-p346900-b7e2c9` selected the first thirty-two previously unselected exact tuples walking
forward from current queue index 193. There were no selected-tuple skips and no wraparound.
Assignment SHA-256 is `a6566f985e87fd12afbea784086f92256a538041de04cf30c0fd8a7909c408e2`; ordered
`(assetId, sourcePath, sourceSha256)` tuple digest is `682962d7aef01167e25c1be0a9b866836cef98877916c6ca731607d00f8e59ff`:
- W31-001, index 193, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-157.jpg`,
  SHA-256 `f420a43cbda8bc562b02eb0656f0f1cf80bdd97d95092a9ad84a69e12c089b02`;
- W31-002, index 194, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-158.jpg`,
  SHA-256 `8d2cfe3ee15534d8388721d1de501f9611146adffaf51f6c3588bccede1b2f73`;
- W31-003, index 195, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-159.jpg`,
  SHA-256 `fc0a267123d785703162e31ecfb91b68d3a43c9b53c3a2532cc6dc4932a7457f`;
- W31-004, index 196, `assets/tts-mod/extract/v2-dl/tree/cards/game/objectivePersonalDeck-161.jpg`,
  SHA-256 `3aec90a31ada20f22218d01aab15694a3be8c41a831a578db6c4d607cc42085a`;
- W31-005, index 197, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-013.png`,
  SHA-256 `5ad0606dff59c21b20689fc6b5b5192ef83c95f108ded91e587725bfd2c68092`;
- W31-006, index 198, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-038.png`,
  SHA-256 `fc04bf1a2920fb63ac512d209622b591cdc9f3cb9ca292c97bf874fcddbbd5c8`;
- W31-007, index 199, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-040.png`,
  SHA-256 `ce7a5fba88dd56f5de2ae77e5fe1647324bdfa9a99ae7f55485cca35eb72b062`;
- W31-008, index 200, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-041.png`,
  SHA-256 `929ac1204b4b7989ee051307245bf32fb5e1915a35b9afd5a73572c8ca01dc61`;
- W31-009, index 201, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-045.png`,
  SHA-256 `133a975dc072a169ceed85615ab2e5a6cde0f80a23f18e61948f0a963c9e98e2`;
- W31-010, index 202, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-084.png`,
  SHA-256 `bcb0eeb9e86f66f8401b584385746d268641c2692392b3faeb4f93438111a62f`;
- W31-011, index 203, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-126.png`,
  SHA-256 `63654c6409f88599aff333b6a54e90b3c3aaa7a29f2395ffff36eed7ab2d6e49`;
- W31-012, index 204, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-164.png`,
  SHA-256 `4a79f992bc3e6b7493887c40b1198785673cc87ce462bbdd732b02c8e6a3cf14`;
- W31-013, index 205, `assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-165.png`,
  SHA-256 `763ca108996c746f141b6f505d3afee2c30be1f6f4f38b84d0118f9f76bdf765`;
- W31-014, index 206, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-059.png`,
  SHA-256 `e9ca2730644b069ebdfc3e5002b3a7656fc1a37035c38eebf7062e2f78f59651`;
- W31-015, index 207, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-112.png`,
  SHA-256 `b728051696f6e41cefa58c203125c1470a3a48c589820b5b8a82cbf18c28681c`;
- W31-016, index 208, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-117.png`,
  SHA-256 `9eb1ddc91a26bc4581a12f685edce6d1858b93770f576c3be3062a30f293d2db`;
- W31-017, index 209, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-00.png`,
  SHA-256 `7408e9ff7bbbfbea602627c74881c561ca7df151626bb160d2a8ceca1d1f24c0`;
- W31-018, index 210, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-01.png`,
  SHA-256 `4d61a4e3a38bc7cb5ecf52f452457c59ecc7c95755d25ee380238d7835caba77`;
- W31-019, index 211, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-02.png`,
  SHA-256 `441834df437ddff13e8fe8d485e615df7b67730aa1903610fbd474ee73d0161c`;
- W31-020, index 212, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-03.png`,
  SHA-256 `8f1f1ba0b8958061a8fb1ac0bea5972f6d090db76b56f4eb148ff0a8a337d992`;
- W31-021, index 213, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-05.png`,
  SHA-256 `e54b40f88c76cacea72d0ef10c82beb8c9170bb1d9db7d092c3557738492a79f`;
- W31-022, index 214, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-06.png`,
  SHA-256 `e149151bec4cb0d41875581b66864e5f2dd1465e169158ff46ce62f7aedc7c91`;
- W31-023, index 215, `assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-07.png`,
  SHA-256 `af3fa0947175239122c8d9a9075e39a3cc30f45a83d5838638619fafc4a67fb7`;
- W31-024, index 216, `assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-155.jpg`,
  SHA-256 `9cf67e814071c67c598456070306951e3e24cb00a274b20d736596acfeb67c39`;
- W31-025, index 217, `assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-173.jpg`,
  SHA-256 `0e8c91aac8c15e467bbf177ddb3b8fd06600353b3f7af2f1af933b24fb1f1386`;
- W31-026, index 218, `assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-175.jpg`,
  SHA-256 `27a7014ae8011fa68b71a60365b11ca0392b4e66c7d9bdfbe46eec3a6bb21411`;
- W31-027, index 219, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-028.png`,
  SHA-256 `cfc93364f9ec257e07bc84989bbea9709ecdc9519d11f2bc7fd4c5b519ab3f6f`;
- W31-028, index 220, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-104.png`,
  SHA-256 `a8e96bccf2270724b257a20bcc55e24c2e78a161f8bb5ae6256f433c82ecd4e7`;
- W31-029, index 221, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-00.png`,
  SHA-256 `66db7a2fc44c3a8e278b2b7fd0ae40d3932f26667b568ad3b3271b6373f80998`;
- W31-030, index 222, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-01.png`,
  SHA-256 `42980fa5cef70e8ed40649d1495fc75c015c43f60ebb52961031d18f8f3e1564`;
- W31-031, index 223, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-02.png`,
  SHA-256 `e6ec34b2dde06f1cd76e958af3d24ee1bcc4fa177e4d214b086c70d82a8a2322`;
- W31-032, index 224, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-03.png`,
  SHA-256 `322587af9825baec2c8786a0f5e15a657257a5633f025e694de2c962127b44f9`;

Neutral smoke session `20260821_112810_c4cebc` verified 1 API call, 2 messages,
0 tools, exact native `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored
Tools/tool-name marker. Production evidence totals 43 native-image API calls, 86 messages,
and 0 tools across four independently DB-verified sessions:
- blind `20260821_112834_379457` (32/64/0), one persistent one-image lineage with 32 mode-`0400` wrappers;
- upright retry `20260821_123248_7e41e3` (1/2/0), a fresh isolated lossless CCW-90 reread of W31-016;
- exhaustive all-49 contact `20260821_125353_fc9ee8` (8/16/0), four assets per turn with exact per-ID outputs;
- rendered publisher-primary audit `20260821_132524_1f9d93` (2/4/0), covering rulebook p.3 and both Objectives-sheet pages.
No OCR, Qwen, auxiliary vision, model/reasoning downgrade, shared-provider mutation, or
unverified route was used. A complete batch-2 contact response was salvaged after a helper
rejected basename-only reference paths; exactly five token-to-path normalizations changed no
semantic token, verdict, source text, or immutable blind evidence.

All 32 source roles are recursively resolved from the live TTS save: 31 FaceURLs and 1
shared Robot BackURL; 11 sources are generated cells and 21 downloaded assets. Exact
GUID/CardID source selectors are singular for 11
sources, while all reference sets are preserved and 29
are structurally complete. W31-024 has seven exact FaceURL counterparts but only two
counterpart pixel assets in the extracted base tree; that partial set is explicit. Rules/non-rules
counts are 31/1.

All 89 blind morphology occurrences reconcile exactly once:
42 authoritative p.40 matches, 30 explicit
one-to-one no-match rows, 13 non-text component graphics,
and 4 artwork-only details. Thirty-five discrepancies with
the prior unselected corpus snapshot remain explicit; no previous approved record was overwritten.

Fresh Awaken Realms bytes match tracked rulebook `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`,
FAQ v1.2 `611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives sheet
`30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`. Current publisher rendered
support is 24 absent counterparts, 5 occluded/unreadable Queen faces, 2 material wording
conflicts (EYES and ARM), and 1 different-family card-back lookalike; zero source-fidelity
gates pass. BGA build `260622-1220` at SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae` remains labeled secondary evidence.
The durable evidence preserves 24 publisher/BGA conflict rows.

All 32 promotion decisions remain `defer`; no candidate or canonical image/sidecar/source byte,
category, or filename changed. Exact blockers include: four visibly prototype-marked Corporate
objectives absent from current publisher/BGA data; Queen faces lacking complete visible primary
counterparts and retaining local no-match frames; red Items with missing/renamed or conflicting
current support plus unresolved/local glyphs and generated-selector gaps; a partial Robot-back
counterpart set and no primary Robot faces; Serious Wound primary/BGA wording conflicts and local
glyph/selector gaps; and no approved canonical schema/directory for any assigned family.

Worker core, independent closure, and the reusable native-worker auditor all pass with 0 errors/
0 warnings. Private projection and independent corpus rebuild are byte-identical and change
exactly 32 assigned corpus records recursively. Shared merge completed 4 trial writes, 4 exact
rollback writes, 4 committed writes, and a zero-write identical re-merge. Eleven focused tests
and all eight documented global validation commands pass; 532/532 source images decode,
390/390 corpus source hashes verify, canonical source hashes and 78 image/sidecar pairs remain
unchanged, and two explicit corpus builds are byte-identical at `6cb4933195c68596d3b364d2900dab68f820245e5eaa57a725ef33bd5a224d69`.
Final generated/QA Git scope is exactly eight files.

Lifecycle counts remain 532 = 148 complete + 384
deferred + 0 unaccounted; queue 384, selected
registry/corpus overlays 214, genuinely unselected queue tuples
170, corpus 390, canonical pairs
78, and deferred re-examinations 188.
The unresolved-symbol backlog contains 237 occurrences
across 148 assets. Predecessor checkpoint HEAD was
`66c6ff5f262ade3fe2fcef6d4f9ef5c343f24abe`; sealed data/QA/shared-scope commit is `6b634039223f9cbb022f70baa61b557d2f01225d`. This entry is
committed separately in the following todo-only checkpoint commit, whose self-hash does not
appear in its own content. Operational blocker: none; canonical-promotion blockers are the exact
per-family, source-conflict, unresolved-morphology, selector, prototype, counterpart-coverage,
and schema gates above. Nothing was pushed or deployed, and no W32 work was started. The next
eligible exact tuple is current queue index 225,
`assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-04.png`
(SHA-256 `522c29d0874334cac9dda75c4cd0182fca35dbc7402c4b7231c1c8a6c6b1ec18`); wraparound was not required.

**W32 defer-only Serious-Wound/Starting-Item checkpoint (2026-08-21T17:14:57.289068Z):** Worker
`sol-max-persistent-worker-32-20260821T135953Z-p441103-69bcb8` resumed the exact run-budget-blocked W32 root and selected the first
thirty-two previously unselected tuples walking forward from current queue index 225.
There were no selected-tuple skips and no wraparound. Assignment SHA-256 is
`4aa548e182de01e4098d5caa1cfdc54709d90cc1067415582a06b48ae05cc135`; ordered `(assetId, sourcePath, sourceSha256)` tuple digest is
`8b5991b07c9016284dc781c4baf1bd6cd4f7bc4f17848f4a46250ae7737d8ed1`:
- W32-001, index 225, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-04.png`,
  SHA-256 `522c29d0874334cac9dda75c4cd0182fca35dbc7402c4b7231c1c8a6c6b1ec18`;
- W32-002, index 226, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-05.png`,
  SHA-256 `69fa0f09363ab35f1e547a60e64e1b011702a7469755835bf002e0739b0a33f2`;
- W32-003, index 227, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-06.png`,
  SHA-256 `1027d7f87a80b4a7d32eb40e9d336c9557c032a33ab6fdc08912a5beeb3e2dcb`;
- W32-004, index 228, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-07.png`,
  SHA-256 `b485840032e9abcaeec0bf614e7df0e5487aa52d43005615eeb6950aed44f09f`;
- W32-005, index 229, `assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-08.png`,
  SHA-256 `2316dd24439f588422fce16da610e59e2609973f968bf0cb7dfb18b8d8f21f40`;
- W32-006, index 230, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-005.png`,
  SHA-256 `36a33ad974b4fa96f009c0e95d17cc1427cd11de20e8643b229308c820477d44`;
- W32-007, index 231, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-030.png`,
  SHA-256 `ee004244a4cec9773d43252e7a453a9f31bd327a7f53eb59bd37eade341fe9be`;
- W32-008, index 232, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-033.png`,
  SHA-256 `7f1de79bbc5d8b86dae03d33deede52be56bfbc3a3c400a39b0bb5b03d8df2c3`;
- W32-009, index 233, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-042.png`,
  SHA-256 `f3761d0effff2a9bf05c4287450f8fb0e094740d2aa4052d82345fa4c09c2054`;
- W32-010, index 234, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-044.png`,
  SHA-256 `9870476ca19f38b2a7d15aca06626d722de38d83da8fcf84086a4f2ee2827dee`;
- W32-011, index 235, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-046.jpg`,
  SHA-256 `d9ce7bcc345521deeafc88c1ed7f99603e3248163a9d9dfd5fa7fd1cbf3879ba`;
- W32-012, index 236, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-055.jpg`,
  SHA-256 `17b9fc374296328f209b6ed96401dba47dd7857f9f1cb368f3345ade2d064207`;
- W32-013, index 237, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-067.jpg`,
  SHA-256 `80e0ab88527496e12287c919b33086d2bd4d4541359cad0630b2ce018695919b`;
- W32-014, index 238, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-073.jpg`,
  SHA-256 `dce11eecbc243970622af2db06d5df5e391497447a8c008bd9f125e008d92591`;
- W32-015, index 239, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-074.jpg`,
  SHA-256 `4dbee4ea11d5f223eca9a58cced91f37bab63f4296910cd0cbc0838acfc487e3`;
- W32-016, index 240, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-083.jpg`,
  SHA-256 `be3301f672e5fd689ca2b7e194e1b85ad020c66f57277fe9edd352d2078eb43f`;
- W32-017, index 241, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-085.jpg`,
  SHA-256 `6b691da92363fc2a538eb04ea0b97a51c3b205812b4ac5ffef1fd68381494b96`;
- W32-018, index 242, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-088.jpg`,
  SHA-256 `05992188d794ace180101b74074f39591315eedc251168c875dac483bd9bb9dc`;
- W32-019, index 243, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-098.jpg`,
  SHA-256 `b33ad7170c41977661089b1185297844101256e24e0c5cfab19e84fb6f7bd2fb`;
- W32-020, index 244, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-108.jpg`,
  SHA-256 `c3ffc0cdcb17206a2467a5faaf300fa53f4264d752977b5b69628ae3a6fc532d`;
- W32-021, index 245, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-114.jpg`,
  SHA-256 `fdb8cddc0b047d292fb79a60219340d5e5d7d1d1dfba32e7b779d9c775901f3f`;
- W32-022, index 246, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-118.jpg`,
  SHA-256 `42adf5a01f1bdb0ab7ef892fc91c29c33403b97f4e03537c33c8f8f0e413a96e`;
- W32-023, index 247, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-131.png`,
  SHA-256 `ea5cd7dad241bea8eea7d5897764485bab2bb616f1ee2ba8c39b9695f9118870`;
- W32-024, index 248, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-136.jpg`,
  SHA-256 `a763510f880bdd497fa9d3fb625a7fbab88294e32b9a638a702b4ac96e372401`;
- W32-025, index 249, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-141.jpg`,
  SHA-256 `725e788f3970d9699dd40fe12a86841748807e69d75007e98394bce41f60f7e6`;
- W32-026, index 250, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-01.png`,
  SHA-256 `b9889286435b7adad61e79c9e3985c06d2e770833c37339eaaa9c5edf04d0c54`;
- W32-027, index 251, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-02.png`,
  SHA-256 `5800849bb493d6000460ccf76c31d4cbc94c70a9a42586f13f606193b6afa6b8`;
- W32-028, index 252, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-03.png`,
  SHA-256 `91857d78dd2e2dabd20dce496309d854c921a846db8708f24477189a8f3f4ac1`;
- W32-029, index 253, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-05.png`,
  SHA-256 `8230ba5b1c59f7a9b136b3a2f1c14b4414f7ba918944684cd78e0ab199e1656a`;
- W32-030, index 254, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-06.png`,
  SHA-256 `4ceab051ce520564a2a1dd312b65f665f76bf29b4a0a6eb94c2a7fbf37943478`;
- W32-031, index 255, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-07.png`,
  SHA-256 `7b823f5dd37c1464ad713cb07e60b0731264d1f87ca87901c1e4c86bdd993f19`;
- W32-032, index 256, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-08.png`,
  SHA-256 `dcca8ddf8c75047dd93d61660d237b5460c0566331e2d29fdd1cd26f61853f7b`;

Neutral smoke session `20260821_140040_c040c1` verified 1 API call, 2 messages,
0 tools, exact native `openai-codex:gpt-5.6-sol` at reasoning `max`, and no stored
Tools/tool-name marker. Production evidence totals 89
native-image API calls, 178 messages, and 0 tools across four
independently DB-verified sessions:
- blind `20260821_140128_f6f95e` (32/64/0), 32 immutable one-image wrappers;
- upright retry `20260821_153213_19cbe6` (22/44/0), 22 lossless CCW-90 rereads while source bytes remained unchanged;
- exhaustive all-49 contact `20260821_163558_f8e0fc` (32/64/0), exactly eight four-asset primary calls plus 24 focused context-strip retries;
- publisher-primary page audit `20260821_170818_302ebd` (3/6/0), directly inspecting rulebook pages 3, 18, and 29.
The contact closure reconciles 55 functional occurrences and
43 reference-path-only normalizations;
semantic token, verdict, and source-text changes are all zero. The predecessor unsealed contact
attempt remains failure provenance with zero accepted calls/wrappers/verdicts. No OCR, Qwen,
auxiliary vision, model/reasoning downgrade, or shared-provider mutation was used.

All 32 source roles are recursively resolved from live structured TTS data: 31 FaceURLs and 1
shared Starting Item BackURL; 12 generated cells and
20 downloaded assets. Singular exact GUID/CardID selectors
exist for 19 sources; all
32 exact reference sets are preserved.
Every tuple has counterpart pixels, with 31
complete counterpart sets and one explicitly partial shared-back face set. Rules/non-rules counts
are 31/1.

All 184 accepted morphology occurrences reconcile exactly once:
43 authoritative p.40 matches, 12
explicit one-to-one no-match rows, 103 non-text component
graphics, and 26 artwork-only details. The durable prior-snapshot
comparison preserves 30 discrepancies; no previous approved
record or canonical file was overwritten.

Fresh Awaken Realms bytes match tracked rulebook `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`,
FAQ v1.2 `611ae20dc0b3e04f3c0d99f294a92fc95460c042565b12d1c808b1282ae0e0d8`, and Objectives sheet
`30f3d4116a9c4dc3a53fb5e920995c24aa747988c915dc5fba6261cbd7dca364`. Current rendered publisher
status counts are `{"absent": 30, "exact-component-counterpart": 1, "same-family-operative-text-unreadable": 1}`; current BGA
build `260622-1220` at SHA-256
`18cd8f4a2883d4f6662ed170095ff07e0d9f5da508064ed1d6bfc124f5a274ae` remains licensed-digital secondary evidence
with status counts `{"exact-title-material-text-conflict": 21, "exact-title-text-exact": 4, "no-exact-title-record": 6, "not-applicable-to-generic-back": 1}`.
The evidence preserves 29 publisher/BGA/TTS-variant
conflict rows verbatim; renamed or fuzzy titles were never substituted.

All 32 promotion decisions remain `defer`; no candidate or canonical image/sidecar/source byte,
category, or filename changed. Blocking gates are explicit per result: 12 unresolved local glyph
occurrences, 13 non-singular selector cases, one partial counterpart set, current-source absences/
conflicts or incomplete visible support, one generic non-rules BackURL, same-title TTS variants,
and no approved canonical destination/schema for this unattended mixed family.

Worker core, independent closure, and the reusable native-worker auditor pass with 0 errors/
0 warnings. Private projection and independent corpus rebuild are byte-identical and change
exactly 32 assigned corpus records recursively. Shared merge completed 4 trial writes, 4 exact
rollback writes, 4 committed writes, and a zero-write identical re-merge. Eleven focused tests
and all eight documented global validation commands pass; 532/532 source images decode,
390/390 corpus source hashes verify, all 78 canonical image/sidecar pair hashes remain unchanged,
and two explicit corpus builds are byte-identical at `662fb1a21e60da414363dc7ce373e11941461e4636f711cc4c39d4aca0a7fea0`. Final
generated/QA Git scope is exactly eight files. The worker inventory covers
828 pre-inventory files plus its sole self-exclusion.

Lifecycle counts remain 532 = 148 complete + 384
deferred + 0 unaccounted; queue 384, selected
registry/corpus overlays 246, genuinely unselected queue tuples
138, corpus 390, canonical pairs
78, and deferred re-examinations 220.
The unresolved-symbol backlog contains 217 occurrences
across 139 assets. Predecessor checkpoint HEAD was
`24795fbc8dba1de99bef552245c2ed80a166de31`; sealed data/QA/shared-scope commit is `1123b31fe8bf6b43833fe21ccac8dd42fff323e5`. This completion entry is
committed separately in the following todo-only checkpoint commit, whose self-hash does not
appear in its own content. Operational blocker: none. Nothing was pushed or deployed, no W33
work was started, and the next eligible exact tuple is current queue index
257, `assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-09.png`
(SHA-256 `4d9d0a3fc8807394cda0765d34ebbe84e7e7dd38f57ac7cfa2c810fcc83598ed`); wraparound was not required.

**W33 final-completion checkpoint (2026-08-22T00:43:51.299394Z):** Worker
`sol-max-persistent-worker-33-20260821T172305Z-p465856-36ac0c` completed the exact immutable 138-tuple final assignment. Assignment SHA-256 is
`41a354f78f7e88dc4f35ea3d0ba80581751b5e184e1afa9c54621b659ac03b9d` and ordered `(assetId, sourcePath, sourceSha256)` tuple digest is
`17e234503230a4a37e6dcb0c94e55b828b4081381edf0e361ffa2af4fb8aa967`. No W34 worker or next tuple exists.

W33-106 recovered through the explicitly authorized large-input route after six exact-source provider
overload sessions. Its original `tokens/boarderTile-002.png` remained byte-identical at
`b3f6694e56943a95525dc14b8c432a1509e243aea43764ab677e26734bab26ba` (9895×9264,
23465920 bytes). The sole accepted upload derivative is lossless PNG
`1e15d2cc9366808072a91faa5899e80b4011c0519ac1ff8a218d8f0062884284` (4096×3835,
5231386 bytes), produced by the recorded aspect-preserving LANCZOS
4096px-bound transform. Session `20260821_232016_14d96d` verified 1 API call, 2 messages, and 0 tools.

Accepted production evidence totals 260 unique sessions, 264 native-image
API calls, 528 accepted messages, and 0 tools across blind, 11 lossless orientation
retries, 104 independent all-49 contact adjudications, and 11 single-page publisher audits. The separate
non-production route smoke is 1 session / 1 API call / 2 messages / 0 tools. Excluded
evidence totals 10 known sessions, 3 DB-counted API calls,
16 messages (including 3 historical
unserved messages inside accepted blind sessions), and 0 tools. This excludes the
W33-022 timeout, six W33-106 overload sessions, and three context-stripped multi-image publisher calls;
all are preserved as failure provenance and none supplied accepted semantics. No OCR, Qwen, auxiliary
vision, model/reasoning downgrade, or shared provider/config mutation was used.

All 138 decisions are conservative `defer`; promotions/canonical changes are 0. The immutable results
reconcile 589 enumerated morphologies exactly once: 557 functional
occurrences split into 232 authoritative page-40 matches and
325 explicit no-match rows, plus 32 non-text component
morphologies and 0 artwork morphologies. Conflicts preserved verbatim:
42 prior-snapshot, 79 total source-authority/variant,
including 11 publisher-primary, 64 BGA-secondary, and
4 same-title TTS-variant rows. No approved file was overwritten or reclassified.

Generic recursive provenance resolves all 138 exact URL reference sets across 1 bag, 32 cards, 8
figures, 42 models, 33 tiles, and 22 tokens; 42 applicable paired-side sets have complete pixels and 13
sources retain explicit state-alternate evidence. The selected-evidence registry now covers every 384
queue tuple while the intentionally card/reference-only corpus remains 390 records: exactly 32 W33
corpus members receive overlays and 106 non-corpus selections remain registry/QA evidence without
fabricated corpus rows. Final lifecycle is 532 = 148 complete +
384 deferred + 0 unaccounted; queue 384, selected
384, genuinely unselected 0, canonical pairs
78.

Reusable native-worker audit, independent closure, private projection, transactional trial/rollback/
commit/zero-write remerge, and final validation all pass with 0 errors/0 warnings. Eleven focused tests
and all eight global commands pass; 532/532 images decode, 390/390 corpus hashes verify, two corpus
builds are byte-identical at `59d56b3995255fdf4956c0110bfd383a5c0f3ebd099d8047d372dc02f6429208`, unresolved occurrence cardinality is exact,
and all 78 canonical pair hashes remain unchanged. Sealed data/QA/shared/code commit:
`585740242f1a6bbdb6780dea3b5a38ee8eb8a7cb`. This TODO entry is committed separately because it cannot embed its own hash.
Nothing was pushed, no PR/deploy/profile/config/service/production action occurred, the worktree was
clean at checkpoint, no worker remained live, and there is no next tuple or W34.


**Manual card-rules sample adjudication (begun 2026-08-22T05:59:25Z; amended 2026-08-22T10:35:35Z):** The project owner reviewed seven
stratified sample items. S01 (DAMAGING FIRE) and S08 (STARTING ITEM back) passed. S02 (REST) exposed
a review-package defect, not a corpus defect: its canonical sidecar and corpus already stored the
upper-right `notInCombat` icon, and the package's false text-only label was corrected. S05 (GATLING
GUN) maps the red Ammo occurrence to `[ammoToken]` and its pre-release purple exclamation result
to `[burstDieAdditionalEffects]`. S06 (PLASMA GUN) maps the same purple legacy result and the older
red ammunition-magazine result to `[burstDieAdditionalEffects]` and `[shootDieAmmoLoss]`; the
following punctuation is a colon, and its false illegible span remains removed. The same
source-scoped artwork aliases were audited across the related legacy weapon faces without changing
canonical card promotion status. S03 later passed. S04 retained its tightly kerned apostrophe and
resolved the official Number of Characters metadata symbol as `[numberOfCharacters]`; its prototype
status remains deferred. S07 passed the exact TTS LEG text and all three icon mappings; scan-overlay
microtext and green/callout graphics are artwork, not rules, so that source is now draft-full while its
licensed-digital wording conflict and deferred status remain. All eight sample items are reviewed. Durable evidence:
`docs/qa/card-rules-manual-review-2026-08-22.json` and
`docs/qa/card-symbol-semantic-resolutions.json`.

The lifecycle partition remains 532 = 148 complete + 384 deferred + 0 unaccounted; canonical pairs
remain 78. The rebuilt 390-record corpus has 350 rules-bearing records, 250 full drafts, 10 partial
drafts, 3 no-transcription records, and 49 non-rules/reference records. All six documented global
corpus/vision commands pass, including 532/532 source decodes, 390/390 corpus hashes, and two
byte-identical builds. Nothing was pushed, deployed, promoted to production, or changed outside the
task workspace.

## DONE — Official Room Help Sheet source extraction (2026-08-24T05:46:42Z)

- [x] Extracted all 25 printed Room entries from the official two-page PDF without canonical naming or semantic normalization.
- [x] Preserved exact effects, AND/OR grouping, 18 entries with notes, 5 cross-references, 112 source-local functional-icon occurrences, and 39 effect/note references.
- [x] Regenerated both 300-DPI pages and all 25 crops from the official PDF; source/page/crop hashes, entry numbers, titles, layout joins, placeholders, occurrence IDs, and counts pass deterministic validation.
- [x] Confirmed 0 unreadable operative spans. The unresolved 25 help-sheet entries versus 23 Room tiles relationship remains explicit rather than inferred.
- [x] Durable extraction: `docs/rules/source-extraction/room-help-sheet.json`. Next source: official Objective Help Sheet.

## DONE — Official Objective Help Sheet source extraction (2026-08-24T06:27:29Z)

- [x] Inventoried 45 official source units: 14 GAME TERMS page occurrences, 7 Mission Objective physical cards, 8 Mission Tasks, 15 Private Objectives, and 1 shared explanatory note.
- [x] Extracted all 35 fully visible units with exact wording and source-local icon occurrences; retained 10 physically occluded cards with direct fragments, explicit occlusion, and a hard PDF-text-layer/visible-face boundary.
- [x] Preserved five physical OFFICIAL ORDER copies and seven pixel-identical repeated GAME TERMS occurrences as separate source units.
- [x] Regenerated both 300-DPI pages and all 45 crops; source/page/crop hashes, category counts, unit IDs, placeholders, occurrences, duplicate-page equivalence, and visibility counts pass deterministic validation.
- [x] Durable extraction: `docs/rules/source-extraction/objective-help-sheet.json`. Next source work: 13 card-gap records.

## DONE — Base card-gap source adjudication (2026-08-24T07:01:08Z)

- [x] Re-reviewed all 13 former card-gap source tuples from exact pixels: 9 rules-text-complete, 3 classified non-rules, and 1 exact-source operative blocker.
- [x] Recovered `SUBMACHINE GUN` punctuation as a colon on a lossless upright derivative; immutable selected worker evidence remains preserved separately.
- [x] Classified unreadable Serious Wound scan microtext, Mission Task background displays, and Character-card display microtext as artwork/interface material outside operative rules.
- [x] Classified one robot card back and two near-uniform black placeholders as non-rules; no card/reference record remains untranscribed/unclassified.
- [x] Preserved the prototype `FACILITY RESTART` incomplete clause and all materially different source variants without substitution.
- [x] Corpus rebuild: 390 records, 259 full drafts, 1 partial, 0 no-transcription, 52 non-rules/reference; focused and deterministic validators pass.

## DONE — Official rulebook visual obligation census (2026-08-24T07:42:23Z)

- [x] Rendered and inspected all 40 official rulebook pages blind at 160 DPI before consulting text extraction.
- [x] Recorded 80 source-local visual units: 72 normative obligations, 5 worked examples, and 3 reference/navigation units; 0 material visual spans are unreadable.
- [x] Captured setup/map topology, card/component anatomy, state/face/color/orientation keys, action/die tables, movement examples, scanner overlay, Queen/Health tracks, and the 49-icon glossary without semantic normalization.
- [x] Compared 353 printed labels against page-local and checked-in text extraction; all 80 units are only partially represented because their graphical relationships are lost.
- [x] Deterministic validator regenerates all 40 page images/text segments and checks every hash, page, bbox, ID, count, representative obligation, and glossary total.

## DONE — Official FAQ/errata v1.2 source extraction (2026-08-24T08:07:32Z)

- [x] Rendered all 4 FAQ pages at 200 DPI and extracted cover metadata (`V1.2`, `8.06.2026`) plus all 59 ruling/errata units.
- [x] Preserved two-column reading order, section headings, numbering, exact Q/A or correction text, bboxes, and 4 inline glyph occurrences omitted by text extraction.
- [x] Partitioned applicability: 28 base-game units and 31 expansion-specific units; expansion rulings remain retained but outside base conclusions.
- [x] Classified 15 errata units and 44 FAQ rulings with 0 unreadable spans; FAQ authority remains above conflicting rulebook text.
- [x] Deterministic validator regenerates all 4 page renders/text segments and verifies hashes, counts, section totals, scopes, bboxes, IDs, and representative base/expansion rulings.

## DONE — Player Help source-occurrence extraction (2026-08-24T08:24:36Z)

- [x] Extracted ten distinct numbered Player Help fronts (players 1–10) and the exact shared functional `PASS` BackURL side.
- [x] Verified all fronts belong to TTS bag `d8a0fb` (`playerHelpCards`); players 1–5 are generated FaceURL sheet cells and players 6–10 have individual FaceURL GUID/CardID tuples.
- [x] Proved one exact instruction-text variant and two measured raster-template groups while retaining every numbered source occurrence independently.
- [x] Preserved source conflicts: TTS has ten fronts while the current rulebook inventory says five; TTS phase labels/order materially differ from the current rulebook.
- [x] Deterministic validator checks hashes, dimensions, TTS roles, paired side, text equivalence, template metrics, corpus projection, canonical Player 6, and conflict records; 0 unreadable spans.

## DONE — Secondary-evidence closure (2026-08-24T08:24:36Z)

- [x] Copied one byte-identical BGA build `260622-1220` snapshot into the repository; all 4 collected runtime copies share SHA-256 `18cd8f4a…` and size 85,433 bytes.
- [x] Evaluated and indexed all 11 BGA top-level data tables (298 scoped keys), field/type shapes, placeholder strings, duplicate display names, and count boundaries against physical sources.
- [x] Indexed 6 TTS structured evidence files, 159 Lua role records, 172 GMNotes tag rows / 1,267 occurrences, classification/object structure, card provenance, and 384 selected-evidence entries/runs.
- [x] Recorded 156 corpus records with an explicit BGA conflict/secondary boundary; display names remain labels, never source keys.
- [x] Secondary evidence is mechanically closed but remains below FAQ/rulebook/help-sheet/component authority.

## DONE — Final base-source extraction closure (2026-08-24T08:24:36Z)

- [x] Reconciled 9 source channels: official FAQ, rulebook, Room Help, Objective Help, Intruder Help, Player Help, card/reference corpus, licensed-digital snapshot, and TTS structured evidence.
- [x] All 9 channels are extracted/indexed; all 6 extraction-gate criteria pass; no graphical source units remain.
- [x] One exact prototype `FACILITY RESTART` operative span remains explicitly blocked and may not be invented downstream.
- [x] Authority order, applicability, component/front/back roles, source conflicts, and count boundaries remain explicit.
- [x] Extraction gate decision: PASS — canonical vocabulary and source-scoped alias work may begin. This does not approve taxonomy, ontology, semantics, implementation, PR, merge, or deployment.

## DONE — Canonical vocabulary proposal (2026-08-24T09:25:59Z)

- [x] Inventoried 1,853 observed source-term occurrences across all closed official/component/card/secondary channels.
- [x] Separated 643 named component/title/key occurrences into 501 exact-string-only identity groups.
- [x] Proposed 167 controlled vocabulary entries: 50 accepted existing icon terms and 117 authority-derived labels.
- [x] Registered 8 accepted aliases plus 5 non-alias guardrails; no appearance-wide or duplicate-name aliasing is permitted.
- [x] Validation passes with no taxonomy/ontology/semantic artifacts.
- [x] Owner gate VG-001: accepted `PERSONAL OBJECTIVE` → source-scoped alias of `Private Objective` for exact listed tuples; original wording/provenance preserved.
- [x] Owner gate VG-002: accepted `Drilling Room` → alias of named component `DRILLING STATION`; both official labels preserved.

## DONE — Taxonomy/ontology proposal (2026-08-24T23:02:00Z)

- [x] Define 202 source-traceable taxa over approved vocabulary and named identities.
- [x] Map all 167 controlled terms and 501 named identity observations.
- [x] Define 45 source-supported relationships, 20 inverse pairs, and 14 static constraints without semantic effects.
- [x] Validate provenance, acyclicity, uniqueness, domains/ranges, cardinalities, complete mappings, and byte-identical rebuilds.
- [x] Add corruption negative controls for cycles, missing mappings, bad inverses/ranges/cardinalities, missing sources, and semantic leakage.
- [x] Incorporate four independent taxonomy, ontology, ambiguity, and validator audits.
- [x] Correct process/category errors, add occurrence/definition/copy levels and missing static edges, and defer 12 semantic relation IDs.
- [x] Conclude no genuine owner gate blocks the static ontology after corrections.

## DONE — Semantic rules schema and pilot (2026-08-24)

- [x] Define the closed source-traceable semantic record/schema contract.
- [x] Encode 13 representative Round/Turn, movement/exploration, card, Room, Event, Intruder Help, and endgame pilots.
- [x] Carry six existing genuine questions plus one pilot-discovered ambiguity explicitly with defaults prohibited.
- [x] Add strict validation, two-seed deterministic rebuilds, and adversarial negative controls.
- [x] Build a 600-unit source-obligation backlog: 17 pilot-covered, 582 pending, 1 exact-source blocked.
- [x] Incorporate independent schema, system-pilot, component-pilot, and validator audits.
- [x] Add exact source-tuple assertions, semantic state/zone nodes, explicit question alternatives, conflict register, and stronger validation.
- [x] Defer owner decisions; no unrelated semantic work is blocked by the nine scoped questions.

## FROZEN — Semantic coverage expansion (2026-08-25 through 2026-08-27)

- [x] Expanded the corpus through source-clear general procedures, Room/Intruder Help, Event, Exploration, Robot, Intruder Attack, Queen Health, Serious Wound, Green/Red/Yellow Item, Action, competitive Objective/Mission, Heavy/Equipment, Combat, and Facility/setup batches.
- [x] Reached the verified frozen boundary: 529 semantic records, 530 covered / 69 pending / 1 source-blocked obligations, 115 no-default questions, and 88 conflicts.
- [x] Preserved exact physical occurrences, source variants, authority boundaries, and deterministic/adversarial validation.
- [x] Froze expansion after the Search proof-of-value failed to demonstrate unique implementation utility for the large semantic representation.
- [x] The project owner accepted the measured recommendation to keep semantic expansion frozen; do not add semantic records or families unless that decision is explicitly reversed.

## SUPERSEDED — Stage 1 blind rules correctness audit (2026-08-29 to 2026-09-01)

- [x] Preregister and execute the Search → Item gain proof-of-value without production changes.
- [x] Pass 22/22 acceptance tests and kill 17/17 mutations within the 800-line cap.
- [x] Use `deepseek-v4-pro:0813` for adversarial plan/code review and `glm-5.3-flash` for a blind raw-source baseline; independently verify and disposition findings.
- [x] Correct stale concise Item-class rules and retain the semantic corpus as audit/reference evidence rather than implementation authority.
- [x] Owner gate: accepted the recommendation to keep semantic expansion frozen and authorized Stage 1.
- [x] Preserve and explicitly supersede the v1 baseline/lock after reproducing its artifact-seal provenance defect; retain `audit-lock-v1.json` as history only.
- [x] Finish the deterministic v2 control layer without changing the seed or 140-unit population. Candidate 5 was rejected and dispositioned; the owner accepted the green post-disposition checkpoint for progression under the proportional-review policy. The population remains 56 concise rules + 28 FAQ units + 56 component effects, all pending.
- [x] Regenerate `manifest.json` and the canonical all-pending v2 `progress.json`; the generated inputs add the 23-unit clean-match plan, freeze the expanded comparator inputs, and refresh only the intended methodology/builder selection-input hashes without changing the 140 unit IDs, order, strata, or counts.
- [x] Complete and disposition the one authorized eight-worker candidate-5 review wave. Preserve exact batch closure, seven usable reports, one interrupted/non-evidence report, all bounded probes, and the consolidated disposition under `docs/qa/implementation-readiness/correctness-audit/reviews/`.
- [x] Repair the accepted candidate-5 findings: payload-specific closed-schema source-only preflight; full 57-path/33-identifier lexical inventory; 1,080-case real-CLI absent/sentinel matrix; descriptor-relative stable reads and atomic writes; clean lock creation and exact lock-commit path validation; independent mutation inventory; strict packet-schema control; current status text.
- [x] Restore a completely green post-disposition prelock gate. Verified 2026-08-31: manifest freshness and prelock validation pass; all 102 mutation/provenance/path/evidence/render/wave/progress/rollback controls, both source-only CLI tests, and all 15 decision tests pass; source extraction, exact 1,098-file source staging, project status, and `git diff --check` pass.
- [x] Owner decision: no further broad harness review or candidate/rereview loop. Stage 1 is a simple rules derivation review; helper implementation details are outside its scope.
- [x] Instruction-role repair: `AGENTS.md` and `AGENTS-SUPPLEMENT.md` now contain static policy/navigation only; mutable state lives in `PROJECT_STATUS.md` and tasks/history in `todo.md`. `scripts/validate_project_status.py` rejects dynamic headings, metadata, or checklist items in either instruction file.
- [x] Promote clean baseline `a38a9ff28b96ab26975675e47701728ecc0bd095`, create direct-child lock commit `0380196b727ef1a864cb31d3a3f54773d835e5e5` containing only `audit-lock.json`, and pass the complete post-lock gate with all 140 units still `pending-blind-derivation`.
- [x] Stop after the single candidate-5 review wave and serial disposition; no second review wave, post-lock lane, profile, PR, push, merge, deployment, semantic expansion, or implementation work was started.
- [x] 2026-09-01 owner decision: the entire Stage 1 v2 blind-audit methodology above is scrapped — the correctness-audit tree, its ten dedicated scripts, the generic Ollama audit-review runner, the candidate-review evidence, and the uncommitted packet-001 review artifacts were deleted in one teardown commit. The cancelled Lane A–D, escalation, and 339-unit expansion items are dead and will not be executed.
- [x] Replacement methodology (owner's own): break source artifacts into small fragments, hand each fragment to a child worker, and ask whether the fragment's rules and behavior are already fully and accurately captured. No sealing, packet, completeness-review, or comparison machinery may be rebuilt.
- [x] 2026-09-02 rulebook slice: integrated the former extraction worktree into `main`, removed the old 78 paired page-level rulebook inputs, four old rulebook pass artifacts, three slicing scripts, and obsolete slicing task/stage artifacts, then visually inspected all 40 official PDF pages and wrote 1,597 atomic files directly under `audit/` (686 facts and 911 rules; pages 1-2 correctly empty).
- [x] Reconciled `audit/manifest.json` to 2,129 total entries and validated contiguous per-page IDs, one assertion block per file, classification agreement, nonempty source/visual provenance, no within-page exact duplicates, no stale rulebook IDs, and no missing manifest targets against source SHA-256 `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`.
- [x] 2026-09-03 verifier waves processed 134 distinct rulebook fragments. The latest 100-item wave recorded 23 pass, 66 fail, and 11 unsure with no worker or closure errors.
- [x] 2026-09-03 triaged all 66 failures from that wave: repaired 47 gameplay-relevant corpus gaps in commit `6a54e92` and returned those exact fragments to the audit root; moved 19 packaging/reference-only assertions to `audit/irrelevant/` without fail sidecars.
- [x] 2026-09-03 follow-up wave assigned 10 items each to 10 workers: all 47 prior repairs passed fresh verification; 53 new fragments recorded 10 pass, 41 fail, and 2 unsure with no worker or closure errors.
- [x] 2026-09-03 triaged all 41 new failures: repaired 33 gameplay-relevant setup and terminology gaps in commit `0a412a1` and returned those exact fragments to the audit root; moved 8 assembly, expansion, insert-placement, or table-layout assertions to `audit/irrelevant/` without fail sidecars.
- [x] 2026-09-03 targeted follow-up sent 20 of those 33 repaired fragments to 10 direct verifiers, two fragments each; all 20 passed with no fail, unsure, worker, or closure errors.
- [x] 2026-09-03 independently triaged all 21 remaining recorded failures: repaired 18 gameplay-facing finite card/deck and Room/Corridor supply gaps in commit `0ce5c45`; moved the Solo/Coop-only Objective supply and two physical border-piece quantities to `audit/irrelevant/` without fail sidecars.
- [x] 2026-09-03 500-child attempt assigned 1,000 unique rulebook fragments. It closed 197 pass and 14 unsure verdicts, produced 133 fail claims, and left 656 assignments without canonical verdicts after widespread provider HTTP 429 failures and interruption; two fragment-without-sidecar cases were returned to the audit root.
- [x] 2026-09-03 independently triaged all 133 fail claims: repaired 121 gameplay/state gaps as systemic topic clusters in commit `9e9148d`, moved 12 non-operative layout/recommendation/commentary/flavor fragments to `audit/irrelevant/`, performed one direct post-commit re-check per repair, and returned all 121 repaired fragments to the audit root. No fail or repair artifact remains.
- [x] 2026-09-03 completed fresh verification of all 146 repaired-priority fragments: 146 pass, 0 fail, 0 unsure, and 0 unreviewed. The 11 fragments initially blocked by obsolete workspace-lock instructions all passed in a later owner-authorized lock-free retry.
- [x] 2026-09-03 completed the separate fixed 100-worker/200-fragment GLM assignment at provider-safe concurrency. Final dispositions are 181 pass and 19 gameplay-irrelevant, with 0 fail, 0 unsure, 0 repair, and 0 unreviewed. All accepted corpus gaps were repaired centrally, independently re-verified once, and checkpointed in `1dbd572`; batches of at most 10 `glm-5.3-flash:cloud` children produced no observed provider throttling.
- [x] Reconciled all 2,129 manifest entries after both waves: 1,404 root, 634 pass, 0 fail, 29 unsure, 62 irrelevant, and 0 repair; every entry has one canonical location, every verdict-routed fragment has its matching sidecar, and no sidecar is orphaned. Rulebook-only counts are 872 root, 634 pass, 29 unsure, and 62 irrelevant.
- [x] Owner gate: the owner authorized the 100 Luna Max + 100 GLM 5.3 Flash Max self-scheduling drain of all 1,404 remaining root fragments.
- [x] Separately re-triaged disputed prior irrelevant dispositions `RB-P08-042` and `RB-P09-002`: both are non-operative table/insert placement conveniences and remain gameplay-irrelevant.
- [ ] After the fragment-coverage review passes, choose a clean architecture independently and obtain explicit owner approval before implementation.

## DONE — Intruder Help and Room semantic audit closure (2026-08-25)

- [x] Added typed Queen-side/context/token dispatch for all 18 Intruder Help rows, including numbered token-back Adult/Drone quantities, Room immediate-Attack ordering, finite Corridor capacity/model limits, and exact token lifecycle.
- [x] Removed the exceptional QA-R-01 projection and required the same exact verbatim/source/lifecycle validation for every Help row.
- [x] Added source-backed Room assertions for higher-authority rulebook/FAQ constraints, including Shelter, Drilling Station, Technical Corridor Entrance, Data tokens, Autodestruction, Nest destruction, Room availability, Door state, Health restoration, Equipment storage, and hidden Anti-Aircraft information.
- [x] Added explicit Room targets, optional choices, finite supplies, linked intrinsic Oxygen payment, Support Equipment storage/discard transitions, Surgery return-then-reshuffle order, and per-Corridor Noise/Attack ordering.
- [x] Added independent exact Room icon denotation locks and adversarial checks for count-preserving semantic swaps, dispatch substitutions, missing operation assertions, and stale coverage projections.
- [x] Final generated semantic checkpoint: 73 records / 18 systems / 281 operations / 48 decisions / 20 targets; 11 open questions, 8 conflicts, 71 pilot-covered backlog units.

## DONE — Base Event semantic batch (2026-08-26)

- [x] Derived 20 base Event face identities from TTS role/card IDs, FaceURL provenance, closed corpus/hash tuples, backlog rows, and the 20-key licensed table; excluded the one shared non-operative back.
- [x] Preserved 20 exact component scans, 20 licensed-digital variants, four official visible component occurrences, and 88 movement/main/secondary sentences without title-only joins.
- [x] Added 20 Event records plus seven reusable movement, Noise, Hazard, Secure-entry, Fire-spread, Infection, and Eclosion procedures; retained five newly exposed questions and three conflicts with defaults prohibited.
- [x] Final generated checkpoint: 99 records / 18 systems / 397 operations / 49 decisions / 98 targets; 16 questions, 11 conflicts, and 102 covered / 497 pending / 1 blocked obligations. Event-specific corruption controls and two-seed rebuilds pass.

## DONE — Independent Room Help fidelity hardening (2026-08-24T10:04:12Z)

- [x] Independent 25-entry audit found no material discrepancy in wording, punctuation, grouping, notes, cross-references, 112 icon occurrences, 39 inline references, or unreadability status.
- [x] Extended evidence crops for entries 05, 08, 11, and 12 to include all of their own notes.
- [x] Added a pinned independent source-fidelity lock, full PDF text-layer/render identity checks, exact per-entry projections, provenance checks, and hard-coded completeness totals.
- [x] Added negative controls proving coordinated extraction/layout edits, missing icons, blank/semantic morphology, unreadability drift, incomplete crops, and bad provenance are rejected.

## REPAIR QUEUE — fragment-coverage audit findings

Moved to `audit/repair/`: each verified true gap gets its fragment files plus a
`<ID>.repair.md` sidecar (defect, source content, applied fix, re-check state).
Do not add repair entries here.

## LATER — Expansions (re-add when user wants them)
- [ ] Re-extract expansion content from save (see `assets/tts-mod/notes/extraction.md` §15 for all deck GUIDs, intruder bags,
      shared action-154 cells, and classification pitfalls)
- [ ] Split expansion sprite sheets (per-lifeform decks have their own 5-face sheets)

## OPEN QUESTIONS (from `assets/tts-mod/notes/extraction.md` §13)
- How canonical Automatic Shotgun data should represent the official `RANGED WEAPON, HEAVY` and
  official effect while retaining the conflicting TTS transcription as provenance
- BOOM! row-key icons — die faces or intruder symbols?
- queenhealth Motherbrain icons (intruder head + blob-with-plus)
- Purpose of art-only "CHARACTER DRAFT" card
- Why vision_analyze strips images (Hermes-side context management?)

## 2026-09-04 — Active self-scheduling fragment drain

- [x] Define and test the same-call claim transaction: open existing fragment, nonblocking per-file flock, pathname/inode revalidation, atomic same-filesystem move, then unlock.
- [x] Document `audit/claimed/<worker-id>/`, model/provider sidecars, and abandoned-claim recovery.
- [x] Drain all 1,404 unresolved root fragments with 100 Luna Max and 100 GLM 5.3 Flash Max workers. Raw closure: 2,129 total = 1,579 pass + 359 fail + 129 unsure + 62 irrelevant; root/repair/claimed are 0 and no verifier worker remains live.
- [x] Recover exited-worker claims and reconcile raw manifest/sidecar closure: every manifest ID has exactly one canonical location and every pass/fail/unsure fragment has its exact sidecar, with no orphaned or opposite-verdict residue.
- [x] Independently dispositioned all 359 fail claims and 129 unsure verdicts; corrected the named scope-exclusion and malformed-evidence pass defects. Final mechanical state: 2,129 total = 1,579 pass + 332 repair + 56 genuine unsure + 157 irrelevant + 5 root slice defects; fail/claimed are 0.
- [x] Assigned all 332 repairs exactly once to mutually exclusive behavioral clusters: 14 reference/help-sheet phase sequence and lookup behavior; 67 escape, endgame, Objectives, and Mission Tasks; 72 Facility topology, Rooms, exploration, Doors, and map markers; 57 Character, Robot, Command, and Action-card behavior; 52 Items, equipment, storage, Health, and Tactical Gear; 51 Intruder, combat, Event, contamination, and Queen behavior; 19 setup, finite supplies, component identities, and icons. Sum: 332.
- [x] Confirmed all 56 remaining unsure fragments against their exact applicable unresolved source/semantic boundary and rewrote their sidecars to identify coordinator review. Every repair sidecar contains the verbatim source assertion and records `Applied fix: not yet applied` / `Re-check: pending`; no concise-corpus edit was made.
- [x] Prepared an approval-ready five-item reslice packet at `docs/qa/fragment-reslice-review/README.md`, with exact proposed records, source hashes, visible/occluded boundaries, source-role constraints, and explicit post-approval actions. No canonical audit or source-extraction artifact changed.
- [x] Owner approved P1–P5. Retired `OBJ-29`, `OBJ-31`, and `OBJ-32` from the rules-verification manifest while preserving their source-extraction provenance; installed the approved full pixel-bound slices for Heavy Gun Operator `DEMOLITION` and the TTS-source `FACILITY RESTART` variant. Manifest total is 2,126; the two replacement slices remain at root for exactly one fresh verifier each.
- [x] Gave P4 and P5 exactly one fresh independent Luna Max verdict each. Both failed because their source-variant behavior/provenance boundaries are absent from the frozen concise corpus; coordinator triage confirmed both as repair claims. Final reslice closure: 2,126 = 1,579 pass + 334 repair + 56 unsure + 157 irrelevant; root/fail/claimed are 0.
- [x] Prepared the approval-ready source-to-rule mapping for all 334 confirmed repair claims at `docs/qa/repair-review/README.md` (P1–P7, one per cluster) with per-cluster files under `docs/qa/repair-review/clusters/` (14 + 68 + 72 + 58 + 52 + 51 + 19 = 334). Each ID has a verbatim source quote, target record, exact proposed sentence(s), and preserved boundary; consolidated per-record edit blocks; flags; and a mechanically verified closure line. Seven drafters (Luna) produced the cluster files in parallel; the coordinator regenerated the `.ids` lists from the repair sidecars, verified every ID appears in its cluster file at least twice (table + block), and spot-checked verbatim fidelity for RB-P16-027, RB-P22-011, OBJ-20, startItemDeck-055, ROOM-3, and the RB-P37 Robot/Anti-Aircraft rows. `docs/rules/` and `audit/` were not modified.
- [x] Owner decision on P1–P7 (approved 2026-09-05). Planned procedure: apply the cluster's consolidated edits in one repair commit, run the normal gate, single re-check per repaired ID against the freshly reread corpus, return passing fragments to the audit root without repair sidecars, one fresh verifier each.
- [x] Owner approved P1–P7 (with P2 amended to add `Evaluates via:` cross-references; flavor text retained) and delegated the remainder autonomously. Applied all seven clusters (`0c3a288`, `5889755`, `02ff0de`), re-checked 334/334, returned all to root, ran fresh verification in three waves, dispositioned 17 fails (15 → unsure on open questions, 2 repaired + re-verified), and closed at **2,126 = 1,863 pass + 106 unsure + 157 irrelevant** (`scripts/audit_closure_check.py`).
- [x] Opened OQ-013 (Hibernatorium corpses) and OQ-014 (Objective N+ / player-number eligibility) from P2 cross-referencing gaps.
- [x] Ran two isolated Ollama Cloud critics over the full repair diff; verified and fixed four findings (`02c003b`, `0e97617`), rejected one. Wrote `docs/qa/repair-review/OWNER-NOTES.md` and `docs/qa/repair-review/UNSURE-LEDGER.md`.
- [x] Owner: read OWNER-NOTES; ruled on corpse scope (OQ-013: excluded as expansion/add-on); researched and documented BGG consensus project interpretations for key unsure questions (SEM-Q-002, SEM-Q-059, OQ-014, SEM-Q-027, SEM-Q-013, SEM-Q-014, SEM-Q-020, SEM-Q-021, OQ-003). Rules layer ready for rewrite architecture gate.
- [x] Owner approved `rewrite-architecture-proposal.md` (2026-09-06): begin clean rewrite implementation from scratch.

---

## IMPLEMENTATION PHASE 1: Headless Rules & State Engine (Active)

### Stage 1.1: Core Types & Foundations
- [x] Initialize project configuration (`package.json`, `tsconfig.json`, `vite.config.ts`, `vitest.config.ts`) with zero runtime server deps.
- [x] Port/derive TypeScript types from `docs/rules/vocabulary/` and `docs/rules/ontology/` (Rooms, Corridors, Characters, Items, Intruders, Actions).
- [x] Implement deterministic seeded PRNG (`Mulberry32`) with state export/hydration and test coverage.
- [x] Implement Game State interfaces: Players, Decks, Bag, Board, Objective assignments.
- [x] Implement pure Action-Reducer pattern: Action envelope, dispatch validation, monotonic sequence numbering.
- [x] Implement Game Setup reducer (Player count 1-5, Character drafting, Starting item distribution, Deck initialization, Bag initialization).

### Stage 1.2: Spatial Engine & Exploration
- [x] Hex coordinate math (pointy-top 23 room slots, axial coordinates, neighbors, distance).
- [x] Corridor network graph, Door state machine (Open, Closed, Destroyed), Technical Corridors.
- [x] Movement action validation (Adjacency, Doors, in-combat movement rules, escaped characters).
- [x] Room exploration token reveals, Room tile assignment (Site 1 vs Site 2), Exploration effects.
- [x] Corridor Noise roll mechanics and Noise marker placement.

### Stage 1.3: Character Actions & Item Systems
- [x] Action card data model & full base deck definitions (60 Action cards across 5 characters + Support).
- [x] Basic actions: Move, Search, Shoot, Burst, Melee, Trade, Room Action, Pass.
- [x] Action cost mechanics: Card discards, Oxygen/Energy costs, Ammo tracking.
- [x] Item decks (Red, Yellow, Green, Crafting/Quest items), Backpack limits, and Tactical Gear.
- [x] Room Action execution across all 20+ Room types.

### Stage 1.4: Intruders, Bag Mechanics & Combat
- [x] Intruder bag development, token extraction, and spawn procedures.
- [x] Intruder AI movement, pathfinding, and target prioritization.
- [x] Combat mechanics: Surprise attacks, Attack card deck, Damage distribution, Serious Wounds.
- [x] Event phase sequencing: Round track advancement, Intruder attacks, Fire spread, Event card resolution.
- [x] Infection checks, Queen health, Autodestruction, and Endgame conditions.

### Stage 1.5: Verification, Serialization & Fuzzing
- [x] Automated headless unit & scenario test suite in Vitest covering all core rules (63 tests across 18 test files).
- [x] Fuzz tester / headless Monte Carlo runner simulating multi-player full games without invariant violation or deadlock.
- [x] Snapshot serialization, storage persistence layer (memory/localStorage/IndexedDB), JSON action log export/import.

---

## IMPLEMENTATION PHASE 2: Networking & Peer-to-Peer Synchronization Layer (Pending)

### Stage 2.1: PeerJS Integration & Connection Lifecycle
- [x] PeerJS client setup with 4-character room codes (`nemesis-rt-XXXX`).
- [x] Host-coordinator message envelope, heartbeat monitoring, and connection keep-alive.
- [x] Monotonic sequence numbering and action broadcast.
- [x] Automated host migration / failover when host disconnects.
- [x] State snapshot serialization, delta action replay, and hot-join synchronization.

---

## IMPLEMENTATION PHASE 3: Client Rendering & User Interface (Pending)

### Stage 3.1: Tactical Canvas Renderer
- [x] High-refresh rate (`requestAnimationFrame`, 60/90/120 Hz) Canvas 2D engine.
- [x] Pointy-top hex room slot rendering, corridor passages, door states, and room artwork.
- [x] Multi-touch gesture handling (pinch-to-zoom, pan, inertia) on mobile; mouse wheel/drag on desktop.
- [x] Visual overlays: legal movement destinations, line of sight, combat targeting, and noise indicators.

### Stage 3.2: Responsive UI & Unfolding Layout
- [x] Reactive UI layer (hand manager, action picker, inventory drawers).
- [x] Mobile bottom-sheet drawers and modal action confirmation dialogs.
- [x] Desktop multi-pane layout with persistent board, action panel, and card inspect.
- [x] State persistence and room code multiplayer connection.

---

## IMPLEMENTATION PHASE 4: CI/CD & GitHub Pages Deployment (Active)

### Stage 4.1: Pipeline & Automation
- [x] Configure Vite build pipeline with `/nemesis-retaliation/` base path.
- [x] Setup GitHub Actions workflow for typecheck, testing, and GitHub Pages deployment.
- [x] Enable GitHub Pages with workflow deployment source.
- [x] Push commits to `origin/main`.
- [x] Monitor GitHub Actions pipeline run and verify green status.
- [x] Verify live site on GitHub Pages (`https://dss539.github.io/nemesis-retaliation/`).
