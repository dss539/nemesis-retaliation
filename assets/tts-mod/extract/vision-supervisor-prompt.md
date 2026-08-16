# Nemesis: Retaliation vision-extraction supervisor prompt

This file is a transactional handoff artifact. The repository records and loaded skill named below remain authoritative if current state or durable procedures change.

Continue the Nemesis: Retaliation TTS vision-extraction work in `/home/smithers/nemesis-retaliation`.

Operate as the supervisor with exactly one long-lived vision subagent at a time. Run autonomously in YOLO mode for routine, reversible, high-confidence work. Do not ask for per-asset approval, but preserve every documented hard approval gate and never overwrite previously approved canonical data without explicit approval.

Give me an initial time estimate, maintain the session task list, update `todo.md` throughout the run, and provide concise progress updates after meaningful checkpoints.

## Current handoff state

Disk-derived state after lifecycle cleanup on 2026-08-16:

- 532 reconciled in-scope records: 134 complete, 398 deferred, 0 unaccounted.
- 64 canonical image/sidecar pairs pass deterministic validation.
- No vision worker or subagent is live.
- Workers 03 and 04 are stopped/superseded. The overlapping Worker 05 and Worker 06 shards are reconciled: Worker 06 is the sole shared-ledger lineage for card-11/12/13/15, while Worker 05 is retained as corroborating direct icon-crop evidence for card-11/12/13. Both assignments are completed and inactive.
- Reconciliation evidence is at `assets/tts-mod/extract/vision-workers/supervisor-reconciliation-workers-05-06.json`; earlier lifecycle closure evidence remains at `assets/tts-mod/extract/vision-workers/supervisor-lifecycle-cleanup.json`.
- The first queue path without accepted current-run evidence is:

`assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-16.png`

Before resuming, re-read `todo.md` for the current approval-gated foreground scope and recompute all counts from disk before changing anything.

## Required preparation

1. Read:
   - `AGENTS.md`
   - `AGENTS-SUPPLEMENT.md`
   - `todo.md`
   - `assets/tts-mod/readme.md`
   - `assets/tts-mod/notes/extraction.md`
   - `assets/tts-mod/notes/card-extraction.md`
   - `docs/rules/icon-glossary.md`
2. Load the `extract-game-mod-assets` skill and its relevant references, including `resumable-semantic-vision-batches` and `vision-card-extraction-workflow`.
3. Inspect:
   - `assets/tts-mod/extract/vision-progress.json`
   - `assets/tts-mod/extract/low-confidence-review.json`
   - `assets/tts-mod/extract/vision-validation.json`
   - `assets/tts-mod/extract/vision-workers/`
4. Check for live subagents. Do not assume the prior worker remains alive.
5. Recompute and report:
   - Total in-scope assets
   - Complete assets
   - Deferred assets
   - Unaccounted assets
   - Valid canonical sidecars
   - Queue confidence/reason breakdown
   - Exact first pending path
   - Any existing staged results

## Model and routing requirements

Use only native `openai-codex:gpt-5.6-sol` at reasoning effort `max` for vision analysis.

Never downgrade reasoning, switch models, use an auxiliary vision model, or substitute OCR-only promotion because of latency, cost, overload, retries, or throughput. If native Sol Max routing cannot be verified, stop and report the blocker.

Use the current supported, lock-protected Hermes provider-routing workflow if an override is required. Do not use the deleted `delegate_task_to_model` plugin.

For every worker run, verify and persist the actual provider, model, reasoning effort, native-image route, session identifier, and image-call provenance. A requested route is not proof that the actual route was correct.

## Supervisor and worker architecture

Run exactly one leaf subagent at a time. The subagent must not spawn further agents.

The worker should be long-lived across a bounded shard and process many assets in the same context. Do not create one worker or session per asset.

Normally analyze 2–4 explicitly labeled images in the same vision tool turn, using parallel native-image calls when supported. Every submitted image must have a stable asset ID. Require and persist one independent result for every submitted ID. After each batch, verify that submitted and returned IDs and counts match exactly.

Use one-image turns only for dense sheets, oversized images, focused icon comparisons, strict approval gates, or retries caused by omissions, truncation, context loss, or cross-image contamination.

Partition work deterministically and record each assignment before processing. Workers may write only beneath their dedicated staging directory:

`assets/tts-mod/extract/vision-workers/<worker-id>/`

The worker may create:

- Per-asset raw results
- Candidate sidecars
- Focused QA evidence
- Batch manifests
- Checkpoint files
- A shard report
- Proposed durable-note lessons

The worker must not edit:

- Canonical sidecars
- Canonical assets or filenames
- Shared manifests or catalogs
- `vision-progress.json`
- `low-confidence-review.json`
- `vision-validation.json`
- `todo.md`
- Shared durable notes

The supervisor alone must inspect staged evidence and serialize canonical sidecar installation, categorization, renames, manifests, catalogs, shared ledgers, `todo.md`, and durable-note updates.

## Subagent context rotation

Never allow the worker context to exceed 200,000 tokens.

Use 170,000 tokens as the warning threshold and 180,000 tokens as the normal handoff threshold. At or before the handoff threshold, instruct the worker to finish its current small batch, persist all results, write the exact next pending asset, and return.

If an exact context-token counter is unavailable, estimate conservatively from the live transcript and use bounded shards small enough to remain safely below 180,000 tokens. Do not gamble on reaching 200,000.

If the worker unexpectedly approaches the hard limit, steer it to checkpoint immediately. If necessary, stop or kill it after confirming that completed batches were persisted. Verify its staged files, merge accepted work, then launch one clean replacement worker with only the remaining disjoint assets and a concise handoff. Never run the old and replacement workers concurrently.

Start with a bounded shard of approximately 20–30 ordinary assets, reducing the shard for dense cards or help sheets. Learning should persist within the shard, but each replacement worker must analyze its assigned assets from the pixels rather than inheriting unverified conclusions.

## Analysis requirements

Re-examine every entry in `low-confidence-review.json`, prioritizing:

1. Genuinely low-confidence records
2. Medium-confidence records
3. High-confidence records blocked by validation or schema gates

Earlier filenames, paths, tentative identities, prior descriptions, confidence labels, and model outputs are not pixel evidence. Analyze each asset from scratch. Use TTS metadata and official sources only according to the documented source-authority workflow.

Apply the Sol Max anti-overconfidence protocol:

1. Record blind pixel observations before semantic interpretation.
2. For every proposed icon, record:
   - Location
   - Outer silhouette
   - Internal marks
   - Colors
   - Neighboring printed text
3. Name the closest plausible canonical alternative and identify a visible morphological feature that rules it out.
4. Filenames, directories, expected game logic, surrounding rules semantics, and earlier reads are not discriminating visual evidence.
5. If the pixels do not visibly distinguish an icon, describe it literally, mark the semantic identity unresolved, and defer that claim.
6. Transcribe text verbatim. Preserve capitalization, punctuation, headings, line structure where meaningful, and printed errors. Use `[illegible]` or `[clipped]`. Never reconstruct expected wording from game knowledge.
7. Keep these separate:
   - `readConfidence`
   - `classificationConfidence`
   - `uncertainties`
   - `promotionDecision`
8. Self-reported confidence is not promotion evidence. False promotion is worse than deferral. Abstention is a correct outcome.
9. Never let one image's observations leak into another image's result in a multi-image batch.
10. A batch omission, mixed identity, truncation, or unexplained inconsistency invalidates only the affected result. Retry the affected assets with a smaller batch.

## Card promotion requirements

For every otherwise promotable card sidecar:

- Resolve its TTS GUID and FaceURL/BackURL provenance.
- Inspect its paired side when allowed by the documented gate.
- Verify ownership, component family, and orientation independently of the current path.
- Compare every claimed canonical icon directly against authoritative glossary crops.
- Use focused crops for disputed icons, tiny punctuation, clipped boundaries, and visually similar glyphs.
- Use only the established minimal sidecar schema and canonical glossary tokens.
- Do not add redundant title, category, character, or footer fields when the path already encodes them.
- Do not silently normalize source text.
- Do not overwrite, delete, or reclassify previously approved canonical data without stopping for human approval.
- Record official-versus-TTS conflicts as provenance. Stop at the applicable gate if authoritative sources conflict and no documented supersession rule resolves them.

## Automatic processing authorization

For independently verified, high-confidence cases, the supervisor may install sidecars, categorize or rename assets, update catalogs and manifests, and continue without per-asset approval.

Non-card assets do not require card sidecars. Complete them when their component function and category are independently established.

If component classification is independently certain but a local visual detail remains unresolved, file the component and retain only the unresolved detail in the durable review queue when the documented workflow permits that.

Keep genuinely unresolved assets deferred with exact reasons, pixel evidence, provenance, and the next useful review action. Do not guess merely to reduce the queue.

## Checkpoint and merge discipline

After every small worker batch:

1. Confirm every assigned asset has exactly one staged result.
2. Validate staged JSON and source hashes.
3. Inspect the evidence rather than trusting the worker's summary.
4. Accept, reject, or retain each candidate as deferred.
5. Serialize canonical file changes.
6. Update `vision-progress.json` and `low-confidence-review.json` atomically.
7. Update `todo.md` with current counts and the exact next pending path.
8. Run the relevant deterministic validation.
9. Report a concise checkpoint to me.

Do not mark an asset complete merely because it was analyzed. `Complete` requires all applicable evidence, schema, provenance, pairing, catalog, and validation gates to pass.

## Durable learning

The worker may propose reusable lessons in its shard report but must not edit shared notes.

The supervisor should add a lesson to `assets/tts-mod/notes` only if it is genuinely reusable across future assets. Deduplicate it against existing guidance first. Do not store one-off asset findings as durable workflow notes.

Do not create redundant notes or session logs.

## Safety and scope

- Do not modify gameplay code.
- Do not re-extract expansions.
- Do not commit, push, open a pull request, or publish anything.
- Preserve manifest-backed source files byte-for-byte unless the documented workflow explicitly authorizes a canonical derivative.
- Do not silently change previously approved files.

## Final verification

Continue rotating clean Sol Max workers until every queue entry is either newly complete or remains explicitly deferred.

Before declaring completion, run deterministic, script-backed checks proving:

- Every in-scope asset appears exactly once as complete or deferred.
- Every deferred asset appears exactly once in `low-confidence-review.json`.
- No complete asset remains in that queue.
- Every sidecar parses and uses only established keys and valid glossary tokens.
- Every sidecar has exactly one valid paired image.
- All source hashes, URLs, manifest paths, sizes, and image decodes pass.
- Catalog and filesystem counts reconcile.
- No worker assignment remains falsely marked active.
- Previously approved files remain unchanged unless explicitly approved.

The final report must include:

- Starting complete/deferred counts
- Number re-examined
- Number newly completed
- Number still deferred
- Sidecars created
- Assets categorized or renamed
- Deferrals grouped by exact reason
- Worker contexts used and why each was rotated
- Verified provider/model/reasoning provenance
- Validation results
- Exact next resumable path, or `none`
- Any approval gates requiring my review
