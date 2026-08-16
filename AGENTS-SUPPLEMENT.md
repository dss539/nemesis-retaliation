# AGENTS.md Supplement

This file supplements `AGENTS.md` with agent-facing documentation practices. It does not replace or modify `AGENTS.md`.

## Documentation Practice

Write durable documentation only when the work produces reusable knowledge, a decision, a blocker, or meaningful project state. Do not manufacture a note merely because a session occurred.

Use the repository-wide placement policy in `readme.md` and apply these agent rules:

- Read the destination’s existing purpose before adding information.
- Put each fact in one authoritative location and link to it elsewhere instead of copying it.
- Keep project overview and navigation in `readme.md`.
- Keep current tasks, blockers, and approval gates in `todo.md`; do not use durable notes as a progress log.
- Keep TTS extraction and card-transcription procedures under `assets/tts-mod/notes/`, starting from `assets/tts-mod/readme.md`.
- Keep official rule interpretations, unresolved source questions, implementation bugs, and declared adaptations in the designated files under `docs/rules/`.
- Keep `docs/qa/` for verification evidence tied to specific checks: tests, audits, action logs, screenshots, contact sheets, and comparison artifacts. Do not place general workflow notes there.
- Put cross-project procedures in reusable Hermes skills rather than copying them into this repository.
- Preserve source conflicts as provenance. Canonical data uses the most authoritative and up-to-date applicable official source; unclear supersession, applicability, or interpretation requires a recorded human decision.
- When QA produces a reusable lesson, put the lesson once in the relevant topic note and link to the supporting QA artifact. Do not turn the QA report into the procedure manual.
- Keep readmes short and navigational. Keep topic notes stable and procedural. Keep status counts and approval state in `todo.md`.
- Before adding a note, search for an existing authoritative home. If content is misplaced, move it and repair references rather than leaving aliases or duplicate copies.
- Keep handoff prompts transactional: identify the repository, the authoritative resume documents, the current task/item, and any immediate unresolved state. Do not copy durable procedures or policy into a handoff prompt; update the authoritative document and link to it instead.

## TTS Work Resume Addendum

For TTS asset, classification, or card-transcription work:

1. Read `assets/tts-mod/readme.md`.
2. Read the relevant topic note under `assets/tts-mod/notes/`.
3. Read `todo.md` for current work and approval gates.
4. Load the `extract-game-mod-assets` skill.

Do not infer current status from historical extraction notes; `todo.md` owns current project state.
