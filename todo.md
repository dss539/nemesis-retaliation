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
