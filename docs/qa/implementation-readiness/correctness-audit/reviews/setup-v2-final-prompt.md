# Stage 1 v2 final holistic setup-review brief

Independently review the exact third non-authoritative candidate commit named by the integrator after the twelve candidate-3 specialty reports are available.

Hold the assigned workspace root lock for the full run, verify exact clean HEAD, stage/check the gitignored source trees with the locked helper, and inspect all Stage 1 methodology, schemas, builders, lock/progress/validator/evaluator code, candidate-1 and candidate-2 dispositions, candidate-3 specialty reports, source-staging procedure, and focused tests. Run the documented manifest, exact 92-control (or later) mutation suite, exact 15-test (or later) decision suite, prelock, source-extraction, project-status, source-staging, and diff-whitespace checks from the isolated worktree.

Assess whether the candidate can safely become the v2 baseline and whether `scripts/create_correctness_audit_lock.py` can create a lock that will validate in the immediate direct-child commit. Confirm:

- seed, 140 IDs, order, strata, and counts remain unchanged;
- all progress rows are canonical and pending;
- every reproduced candidate-1 finding is fixed or explicitly bounded without weakening the declared contract;
- all twelve final specialty reports are usable and dispositioned;
- all prelock review files are closed into the immutable set automatically;
- no lane output exists before lock;
- worker source provisioning and blind non-repository isolation are operational;
- no implementation or semantic corpus file was changed.

Return `accept`, `accept-with-fixes`, or `reject`. Every finding needs exact path:line evidence, a bounded reproduction, and a minimal fix. A finding-free reject is invalid. Write the complete JSON report outside Git at the supplied workspace output path, return its SHA-256, release the lock, and terminate all child processes. Provider-blocked, interrupted, empty, malformed, or contradictory output is non-evidence.
