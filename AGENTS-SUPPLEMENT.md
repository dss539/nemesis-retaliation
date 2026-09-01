# AGENTS.md Supplement

This file supplements `AGENTS.md` with agent-facing documentation practices. It does not replace or modify `AGENTS.md`.

## ABSOLUTE STATIC-FILE RULE

**NEVER PUT PROJECT STATUS, CURRENT PHASE, NEXT WORK, TODO ITEMS, CHECKPOINTS, COUNTS, BRANCH/HEAD STATE, WORKER STATE, OR TEST RESULTS IN `AGENTS.md` OR `AGENTS-SUPPLEMENT.md`.** These are static instruction files. Normal work sessions must not edit them. Mutable state belongs in `PROJECT_STATUS.md`; tasks and history belong in `todo.md`; exact facts belong in generated reports.

The rules-layer review is the owner's fragment-coverage methodology. Do not add unrelated helper-implementation analysis to handoffs or worker assignments.

## Documentation Practice

Write durable documentation only when the work produces reusable knowledge, a decision, a blocker, or meaningful project state. Do not manufacture a note merely because a session occurred.

Use the repository-wide placement policy in `readme.md` and apply these agent rules:

- Read the destination’s existing purpose before adding information.
- Put each fact in one authoritative location and link to it elsewhere instead of copying it.
- Keep project overview and navigation in `readme.md`.
- Keep the concise current phase, immediate next task, blockers, and readiness gates in `PROJECT_STATUS.md`. Keep detailed backlog and historical checkpoints in `todo.md`; do not use either file as a raw session log.
- Keep TTS extraction and card-transcription procedures under `assets/tts-mod/notes/`, starting from `assets/tts-mod/readme.md`.
- Keep official rule interpretations, unresolved source questions, implementation bugs, and declared adaptations in the designated files under `docs/rules/`.
- Keep `docs/qa/` for verification evidence tied to specific checks: tests, audits, action logs, screenshots, contact sheets, and comparison artifacts. Do not place general workflow notes there.
- Put cross-project procedures in reusable Hermes skills rather than copying them into this repository.
- Preserve source conflicts as provenance. Canonical data uses the most authoritative and up-to-date applicable official source; unclear supersession, applicability, or interpretation requires a recorded human decision.
- When QA produces a reusable lesson, put the lesson once in the relevant topic note and link to the supporting QA artifact. Do not turn the QA report into the procedure manual.
- Keep readmes short and navigational. Keep topic notes stable and procedural. Keep verified headline status in `PROJECT_STATUS.md`; exact generated counts belong in machine-readable validation outputs, with links rather than duplicated logs.
- Before adding a note, search for an existing authoritative home. If content is misplaced, move it and repair references rather than leaving aliases or duplicate copies.
- Keep handoff prompts transactional: identify the repository, the authoritative resume documents, the current task/item, and any immediate unresolved state. Do not copy durable procedures or policy into a handoff prompt; update the authoritative document and link to it instead.

## Rules-Review Autonomous Work Unit

One work unit is a substantive fragment-coverage batch plus its serial integration, validation, durable checkpoint, and cleanup. The next session resumes from `PROJECT_STATUS.md` and committed repository artifacts, not the previous transcript or historical candidate reports.

Apply the mandatory proportional-review policy in `AGENTS.md`:

- Spend workers on fragment coverage checks — handing each source fragment to a child and recording whether its rules and behavior are already fully and accurately captured — not duplicate harness criticism.
- Default to one worker and use 2–4 only for real independent specialties. Larger waves require distinct content partitions, not multiple agents asking the same question.
- Give read-only fragment reviewers the fragment text and the citation surface they need. Create task workspaces/worktrees only when a worker must write repository artifacts or inspect Git-specific behavior.
- Hold workspace locks only for actual work. Do not start sleep-only lock holders or preserve review branches that contain no unique commits.
- For 1–4 workers, compact structured results and exact artifact paths are sufficient. The `hermes-worker-result-batch-manifest` / envelope / aggregate protocol is required only for larger fixed batches where exact mechanical closure materially helps.
- Write full durable reports only for material findings, formal acceptance decisions, or evidence needed to reproduce them. Passing reviewers should return compact verdicts and checks, not repository snapshots or transcript dumps.
- Verify source/rules claims against primary evidence. Keep reviews within the rules-derivation scope.
- Integrate verified corrections once, run the documented normal gate, remove temporary workspaces and unneeded branches immediately, and continue to the next substantive batch.

Fresh-session handoff remains autonomous after a verified checkpoint, but it must not schedule another meta-review merely because a prior session ended. An ordinary green gate is a completion condition, not an invitation to seek another assurance layer.

## TTS Work Resume Addendum

For TTS asset, classification, or card-transcription work:

1. Read `assets/tts-mod/readme.md`.
2. Read the relevant topic note under `assets/tts-mod/notes/`.
3. Read `PROJECT_STATUS.md` for the current phase and next task, then `todo.md` only when detailed backlog or historical checkpoint context is needed.
4. Load the `extract-game-mod-assets` skill.

Do not infer current status from historical extraction notes or old implementation documents; `PROJECT_STATUS.md` owns the concise current state and links to the detailed authorities.
