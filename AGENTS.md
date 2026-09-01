# Nemesis: Retaliation — Static Agent Policy

## ABSOLUTE FILE-ROLE BOUNDARY — NEVER PUT PROJECT STATE HERE

**`AGENTS.md` IS STATIC POLICY AND NAVIGATION ONLY. IT MUST NEVER TRACK PROJECT STATUS, PROGRESS, OR TODOS.**

This is a hard repository rule, not a style preference. A normal work session must **not edit `AGENTS.md`**. Edit it only when the project owner explicitly requests a lasting policy or navigation change.

Never add, update, or mirror any of the following in this file:

- current or active phase;
- status dates, branch names, commit IDs, candidates, baselines, or lock state;
- immediate next action, deliverable, resume checkpoint, handoff state, or blocker;
- TODOs, checklists, backlog items, completed milestones, or future-work lists;
- worker/process/workspace state;
- latest test results, validation outcomes, counts, tallies, or inventory totals;
- current source sets, current gaps, current readiness, or current implementation status.

Mutable information has safe, non-instruction-file homes:

- `PROJECT_STATUS.md` — current phase, workspace/branch, next action, blockers, gates, current checkpoint, and concise verified status;
- `todo.md` — detailed backlog, checklists, and historical checkpoints;
- generated JSON/reports — exact counts, hashes, inventories, and validation results;
- topic authorities under `docs/` or `assets/tts-mod/notes/` — reusable domain knowledge and procedures.

Do not duplicate dynamic information here “for convenience.” Do not update this file during handoff. Do not turn a current decision into permanent agent policy unless the owner explicitly says it is enduring. If a status or TODO edit appears to require changing `AGENTS.md`, that is an error: use the files above instead.

## Mission and Scope

Build a source-faithful, reviewable rules layer for the base game of *Nemesis: Retaliation*. A new digital implementation will be designed and built from scratch only after the rules layer is as solid as reasonably achievable and the project owner explicitly approves implementation.

**Implementation work is out of scope unless the project owner explicitly approves it.** The existing web game is a legacy prototype and may be inspected only as historical behavior or QA evidence. Its code, data, architecture, and live behavior are not authority for rules, vocabulary, ontology, or the future rewrite.

## Start Here

1. Read `PROJECT_STATUS.md` for all mutable state and the exact next action.
2. Read `todo.md` only when detailed backlog or historical context is needed.
3. Read `docs/rules/readme.md` for rules-corpus authority and record conventions.
4. For audit work, read the owner's fragment-coverage review in `docs/rules/implementation-readiness.md`.
5. Read `AGENTS-SUPPLEMENT.md` for static documentation and handoff practices.
6. Load the relevant Hermes skill before acting.

Never infer current state from this file, historical candidate reports, old implementation documents, prior transcripts, or the live site.

## Authority and Source Discipline

For rules questions, use this precedence:

1. Applicable official FAQ/errata.
2. Official rulebook.
3. Official help sheets and visible component text.
4. Documented project interpretation in `docs/rules/`.
5. Explicitly declared adaptation.
6. Unresolved question — never silently convert this into a rule.

Source-bound TTS scans and licensed-digital data are evidence, not automatic authority over official sources. Preserve conflicts verbatim. Never combine wording merely because two effects appear similar.

During extraction:

- preserve exact wording, punctuation, grouping, layout, labels, icons, and source provenance;
- use source-local occurrence IDs only as evidence locators, not canonical terms;
- distinguish operative rules from artwork, interface decoration, microtext, and flavor text;
- mark genuinely unreadable operative content rather than reconstructing it;
- do not introduce canonical aliases or semantic interpretation into source records;
- keep expansion material out of base-game scope unless separately authorized.

## Proportional Review Policy — Mandatory

**RULES REVIEW ONLY.** Review the game rules, their source evidence, the derivation, and substantive differences. Helper scripts and worker infrastructure are not review subjects.

The project optimizes for source fidelity and forward progress, not unrelated review-harness analysis.

- Preserve source provenance, blindness where required, deterministic outputs, closed schemas, exact citations, and independent verification of substantive non-matches.
- Keep reviews on game rules, source evidence, derivation, and substantive differences. Do not investigate unrelated helper implementation properties.
- Existing helper regression controls may run in the normal gate; do not deepen or rereview them merely for more assurance.
- One reproducible candidate, one proportionate review when needed, one serial disposition, and one green normal gate are sufficient. Do not create audit-of-the-audit loops.
- Default to one worker. Use 2–4 for genuinely independent specialties. Use larger fan-out only for distinct substantive partitions with a real elapsed-time benefit. Worker count is a ceiling, never a target.
- Read-only reviewers should receive immutable bounded packets rather than writable worktrees.
- Retain compact passing results and evidence needed for material findings. Do not preserve repository clones, transcript dumps, duplicated snapshots, or no-op branches.
- Integrate verified corrections once, run the normal gate, remove temporary workspaces, and return to substantive source/rules work.

The only authorized audit protocol is the owner's fragment-coverage review in `docs/rules/implementation-readiness.md`.

## Workspace and Concurrency Discipline

Use the active workspace, branch, and lock named by `PROJECT_STATUS.md`.

- Acquire the workspace's exclusive nonblocking root flock before operating below that workspace.
- Hold locks only during actual work; never create sleep-only lock holders.
- Workspace locks prevent ordinary overlap; they do not expand review scope.
- Create separate workspaces/worktrees only for concurrent workers that must write repository artifacts or inspect Git-specific behavior.
- Read-only and blind work should use bounded immutable packets or repository-free directories.
- Do not create a Hermes profile without explicit permission.
- Remove temporary workspaces and branch anchors without unique commits immediately after integration.

## Documentation Ownership

- `PROJECT_STATUS.md` owns all current status and resume state.
- `todo.md` owns detailed tasks and history.
- `docs/rules/` owns source-backed rule records, interpretations, open questions, bugs, and declared adaptations.
- `docs/qa/` owns reproducible verification evidence, not general workflow policy.
- `assets/tts-mod/notes/` owns TTS extraction and transcription procedures.
- Reusable cross-project procedures belong in Hermes skills.

Use one authoritative home per fact and link to it elsewhere. Never copy mutable state into an agent instruction file.

## Legacy Implementation Boundary

Allowed uses of the legacy prototype:

- historical QA evidence;
- identifying past misunderstandings or missing rules;
- preserving useful non-authoritative test scenarios;
- researching design decisions that may later be reconsidered.

Disallowed during rules work:

- treating `js/data.js` or `js/engine.js` as source truth;
- repairing or extending the legacy implementation;
- normalizing source evidence to match current code;
- assuming the future rewrite will reuse the legacy architecture.

Future design authorities live under `docs/design/`; they are not authorization to implement now.

## Verification and External Actions

Do not claim completion from a successful write alone. Run the domain checks named by `PROJECT_STATUS.md` and the relevant methodology/topic authority. Verify source hashes, required records, deterministic outputs, and visual evidence where applicable.

Repository: <https://github.com/dss539/nemesis-retaliation>

Do not open a pull request, merge, deploy, modify production, or create a Hermes profile without explicit direct approval. Push only inside an explicitly authorized push boundary.
