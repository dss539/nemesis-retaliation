# AGENTS.md Supplement

This file adds documentation rules to `AGENTS.md`. It does not override it.

## ABSOLUTE STATIC-FILE RULE

`AGENTS.md` and `AGENTS-SUPPLEMENT.md` are fixed instruction files. Never put project status, current phase, next work, TODOs, checkpoints, counts, branch state, worker state, or test results in them. Normal work sessions must not edit them; only the project owner may order a lasting change.

Where things go instead:

- Current status and next action → `PROJECT_STATUS.md`
- Tasks and history → `todo.md`
- Exact facts and numbers → generated validation reports

The rules review is the owner's fragment-coverage methodology. Do not drag helper-implementation analysis into handoffs or worker assignments.

## Documentation Practice

Write a document only when the work produced something reusable: new knowledge, a decision, a blocker, or a real change in project state. Do not write a note just because a session happened.

Follow the placement policy in `readme.md`:

- Read a destination's purpose before writing to it.
- Each fact lives in exactly one place. Link to it from anywhere else; do not copy it.
- Overview and navigation → `readme.md`.
- Current phase, next task, blockers, gates → `PROJECT_STATUS.md`. Detailed backlog and history → `todo.md`. Neither file is a session log.
- TTS extraction and transcription procedures → `assets/tts-mod/notes/` (start at `assets/tts-mod/readme.md`).
- Rule interpretations, open questions, bugs, declared adaptations → the designated files under `docs/rules/`.
- `docs/qa/` is for evidence from specific checks: tests, audits, logs, screenshots, comparison artifacts. Not general workflow notes.
- Cross-project procedures → Hermes skills, not this repository.
- Keep source conflicts verbatim as provenance. Canonical data follows the most authoritative official source. If supersession or interpretation is unclear, a human decides and the decision is recorded.
- When QA yields a reusable lesson, write it once in the relevant topic note and link the QA artifact. Do not turn the QA report into a manual.
- Keep readmes short and navigational. Headline status → `PROJECT_STATUS.md`; exact counts → machine-readable validation outputs.
- Before adding a note, search for its existing authoritative home. If content is misplaced, move it and fix the links rather than leaving copies.
- Keep handoff prompts transactional: name the repository, the authoritative resume documents, the current task, and any unresolved state. Do not copy procedures or policy into a handoff prompt — update the authoritative document and link it.

## Rules-Review Work Unit

One work unit is a batch of fragment-coverage checks, plus integrating the results, running validation, checkpointing, and cleaning up. The next session resumes from `PROJECT_STATUS.md` and committed artifacts — never from the previous transcript or old reports.

Follow the proportional-review policy in `AGENTS.md`:

- Workers check fragments: give each source fragment to a reviewer and record whether its rules and behavior are already fully and accurately captured. Do not spend workers criticizing the harness.
- Default to one worker. Use 2–4 only for genuinely independent work. Bigger waves need distinct content partitions, not several agents asking the same question.
- Give read-only reviewers the fragment text and the citation surface they need. Create workspaces or worktrees only when a worker must write repository artifacts or inspect Git behavior.
- Hold a workspace lock only while doing real work. Do not start sleep-only lock holders, and do not keep review branches with no unique commits.
- For 1–4 workers, compact results and exact artifact paths are enough. The batch-manifest/envelope/aggregate protocol is required only for larger fixed batches where exact mechanical closure clearly helps.
- Write full reports only for material findings or formal decisions. Passing reviewers return short verdicts, not repository snapshots or transcript dumps.
- Check rules claims against primary evidence. Stay inside the review's scope.
- Integrate verified corrections once, run the normal gate, remove temporary workspaces and unneeded branches, and move to the next batch.

A verified checkpoint plus a green gate means the unit is done. Do not schedule another review just because a session ended.

## TTS Work Resume Addendum

For TTS asset, classification, or card-transcription work:

1. Read `assets/tts-mod/readme.md`.
2. Read the relevant topic note under `assets/tts-mod/notes/`.
3. Read `PROJECT_STATUS.md` for the current phase and next task. Read `todo.md` only when you need detailed backlog or history.
4. Load the `extract-game-mod-assets` skill.

Do not infer current status from old extraction notes or implementation documents. `PROJECT_STATUS.md` owns the current state and links to everything else.