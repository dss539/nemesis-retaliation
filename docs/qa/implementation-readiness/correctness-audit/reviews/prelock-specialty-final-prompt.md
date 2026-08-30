# Stage 1 v2 final twelve-specialty rereview brief

Review the exact second non-authoritative candidate commit named by the integrator. This is a read-only prelock correctness review, not implementation work.

For each specialty:

1. Hold the assigned task workspace's regular mode-`0600` root flock for the full review.
2. Verify assigned branch, exact candidate HEAD, and clean tracked state before reading.
3. Read `AGENTS.md`, `PROJECT_STATUS.md`, the Stage 1 methodology, candidate-1 disposition, relevant schemas/scripts/tests, and exact diff from candidate 1.
4. Provision and byte-check gitignored sources with `scripts/stage_correctness_audit_sources.py` before any test that requires them.
5. Make no repository edit, commit, push, PR, profile, implementation change, or semantic expansion.
6. Avoid pipes, heredocs, inline scripts, broad cleanup/reset/stash operations, or commands assembled from file/model output. Bounded saved probes may be written outside the repository and must be reported.
7. Reproduce every alleged defect against the exact candidate. A prose-only concern is residual risk, not an accepted finding.
8. Write the complete JSON report outside Git at the exact workspace output path supplied by the integrator. Include candidate HEAD, workspace, verdict, findings with path:line evidence and reproduction, tests run, and residual risks. Return the report path and SHA-256.
9. Release the workspace lock and terminate all child processes before returning.

Specialties:

1. pre-seal/full-history/linear Git provenance and wave seals;
2. baseline/lock supersession, starting-HEAD ancestry, immutable review closure, creator runnability;
3. canonical POSIX path/backslash/symlink containment;
4. frozen map collisions, all 56 target bindings, comparison target roles;
5. strict JSON/schema failure behavior and raw-response substantive binding;
6. declared reviewer identity, runtime provenance, and role/lane separation;
7. source-only leakage, manifest source-tuple binding, citation/evidence closure, PDF visuals;
8. deterministic 23-unit clean-match plan and missing-stratum behavior;
9. evaluator thresholds, blocker/critical/material coexistence, recurring causes, escalation;
10. progress refresh, transactional rollback, committed history, timestamps, artifact/HEAD binding;
11. mutation/control completeness and non-crashing failure behavior, phrased as authorized local correctness testing;
12. worktree-safe source staging, root resolution, methodology/status/required-command consistency.

A provider-blocked, interrupted, empty, malformed, contradictory, or finding-free reject is non-evidence and must be rerun. No candidate may be promoted until all twelve usable reports are dispositioned and the complete gate is green.
