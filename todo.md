# Nemesis: Retaliation — Project TODO

Durable, living task list for the whole project (game development + TTS asset extraction). Update
it when tasks, blockers, approval gates, or project state change. Read `AGENTS.md` and
`AGENTS-SUPPLEMENT.md` for repository context, and `assets/tts-mod/readme.md` for the asset-workspace
entry point.

**DOCUMENTATION RULE:** Follow `readme.md` → “Documentation placement.” This file records only
current work, blockers, approval gates, and meaningful project-state changes. Do not duplicate
durable knowledge here or update it merely because a session occurred.

Active task workspace: `/home/smithers/projects/nemesis-card-corpus/`
Repository: `/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation/`
Working dir (TTS extraction): `/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation/assets/tts-mod/extract/`
Tree: `/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation/assets/tts-mod/extract/v2-dl/tree/`

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
- BF Gun is excluded from canonical data as an obsolete/prototype HGO starting item; its purple exclamation glyph does not match the current official `burstDieAdditionalEffects` glyph. Evidence: `docs/qa/card-source-audits/bf-gun-source-fidelity.md`.
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
