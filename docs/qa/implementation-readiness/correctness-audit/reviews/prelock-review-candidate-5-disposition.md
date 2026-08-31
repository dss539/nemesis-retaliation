# Stage 1 v2 review-candidate 5 disposition

- Reviewed candidate: `d78e91e9f0d29eab7e9d838d4fc043ba73518cec`.
- Batch: `stage1-v2-candidate5-wave1`.
- Exact batch closure: 8/8 registered workers returned; seven reports are usable evidence and one worker (`c5-r06`) is recorded as interrupted/non-evidence because its final response was blocked after writing its report.
- Aggregated usable findings: 10 (`3 blocker`, `3 issues`, `1 reject`, plus duplicated findings across specialties); the interrupted path report supplied five additional leads.
- Candidate disposition: **rejected as a v2 baseline**. No v2 lock was created and no audit unit left `pending-blind-derivation`.
- Preserved evidence: `reviews/candidate5-wave1/`; `batch-summary.json` is the exact envelope aggregation, while `c5-r06-interrupted-report-lead.json` is not counted as an accepted worker report.

## Consolidated findings and disposition

### 1. Source-only prompt blindness was not closed

Accepted findings: `S7-C5-001`, `C5-R02-001`, `C5-BLIND-CLI-001`, and `C5-MEC-001` describe overlapping forms of one boundary failure.

Candidate 5 rejected exact forbidden object keys but admitted every post-reveal identifier when punctuation-delimited inside a member name. It also globally removed `claim`, `severity`, and `disposition` from the value inventory because those names are legitimate completeness-review keys, allowing them in source-packet strings. The real completeness and blind CLI probes proved absent outputs were created and sentinel outputs overwritten.

Disposition: fixed in the post-review checkpoint.

- Each source-only payload is now validated against its own closed JSON schema before prompt construction.
- The independently derived value/key inventory retains all 57 forbidden paths and 33 closed post-reveal identifiers; schema properties are no longer globally removed from value scanning.
- Exact legitimate keys are exempted only after the payload passes its own schema. Punctuation-wrapped identifier keys still fail the lexical boundary predicate.
- Prompt inputs and instructions are read once through descriptor-relative, no-follow regular-file reads and the validated bytes are the bytes framed into the prompt.
- Prompt output uses a descriptor-relative temporary regular file and atomic replacement; a post-check symlink cannot redirect the write.
- `scripts/test_correctness_audit_source_only_cli.py` exercises the actual CLI entry point across every derived path and identifier, packet and completeness locations, key/value representations, completeness/blind modes, and absent/sentinel outputs: 1,080 rejection cases plus benign writes.

### 2. The lock commit could include unrelated unreviewed content

Accepted duplicate findings: `C5-R04-001` and `C5-ANCESTRY-001`.

The lock creator did not require a clean index/worktree, and post-lock validation checked the lock artifact but not the complete changed-path set of its direct-child commit. Isolated probes committed `readme.md` beside `audit-lock.json` and still passed validation.

Disposition: fixed.

- Lock creation now rejects any tracked, staged, or untracked nonignored worktree state before validation and rechecks cleanliness immediately before writing the lock file.
- Post-lock validation requires the derived direct-child lock commit to change exactly `docs/qa/implementation-readiness/correctness-audit/audit-lock.json`.
- Temporary-Git controls cover dirty, staged, and untracked creator state plus mixed-path and lock-only commit path sets.

### 3. Pathname check/use races remained

The `c5-r06` report is retained as an interrupted/non-evidence report. Its five leads (`PATH-004` through `PATH-008`) were independently reproduced by the serial integrator against exact candidate 5; the reproduction is `c5-r06-integrator-reproduction.json`.

Disposition: accepted and fixed.

- Source and target trees are traversed relative to pinned directory descriptors with `O_DIRECTORY` and `O_NOFOLLOW`.
- Source files are opened with `O_NOFOLLOW`, read from one descriptor, and rejected if their descriptor metadata changes during the read.
- Target writes use a temporary no-follow regular file and descriptor-relative atomic replacement in the pinned directory.
- Intermediate and final target swaps cannot redirect writes outside the worktree; final symlinks are replaced rather than followed.
- Prompt packet reads, instruction reads, and output writes use the same descriptor-relative principles.
- Focused controls exercise source-file swaps, final/intermediate target swaps, prompt packet swaps, and final output symlinks.

### 4. Mutation and status evidence overstated candidate 5

Accepted findings: `C5-R07-001`, `C5-MEC-002`, `C5-ANCESTRY-002`, and `C5-MEC-003`.

Candidate 5 replaced the public source-packet `additionalProperties` mutation kill with only a prompt-token assertion, derived the alleged exhaustive test universe from the function under test, and left contradictory current-state text claiming candidate 5 was still dirty and pending.

Disposition: fixed.

- A separate public-validator control now injects a neutral unknown packet field and requires the closed-schema diagnostic; the physical-class prompt-preflight control remains separate.
- The inventory control independently recomputes the complete universe from manifest sections, unit fields, closed schemas, fixed sets, and explicit shared identifiers; it asserts exact equality and stable counts of 57 paths and 33 identifiers.
- The real-CLI matrix supplies the per-member absent/sentinel write-order control that candidate 5 lacked.
- `PROJECT_STATUS.md` and `todo.md` now identify candidate 5 as rejected, this integration as an unreviewed post-disposition checkpoint, and the absence of any v2 lock.

## Verification boundary

The post-review checkpoint is not a reviewed baseline and is not authorized for lock creation. Its final local gate requires:

1. current 140-unit manifest and all-pending progress;
2. prelock validator pass;
3. all mutation/provenance/path/evidence/render/progress/rollback controls;
4. the complete 1,080-case source-only real-CLI matrix and benign controls;
5. all 15 decision tests;
6. source-extraction validation;
7. exact 1,098-file source-staging check with zero copies;
8. project-status validation and `git diff --check`.

No second review wave, baseline promotion, lock creation, packet work, or post-lock lane was started in this bounded session.
