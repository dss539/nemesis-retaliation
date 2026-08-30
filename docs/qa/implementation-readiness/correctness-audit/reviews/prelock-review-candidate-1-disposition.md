# Stage 1 v2 prelock review-candidate 1 disposition

## Boundary

- Reviewed candidate: `5e525e12c105edb7565fa310ae16a526bc131025`.
- Candidate status: **superseded as a non-authoritative review snapshot**; it is not the v2 baseline and never had an active v2 lock.
- Review topology: twelve isolated specialty worktrees plus one separate holistic setup-review worktree.
- Every finding below remained advisory until reproduced against the canonical worktree. No audit unit left `pending-blind-derivation`.

Two attempts to obtain an additional current DeepSeek V4 Pro 0813 lock-creator review through Ollama Cloud at `think: "max"` returned empty `message.content` with `doneReason: length`. Their prompt and failure envelopes are retained; they are non-evidence and no reasoning trace was retained.

## Specialty dispositions

| Specialty | Candidate verdict/evidence state | Integrator disposition |
|---|---|---|
| 1. Pre-seal / first-parent provenance | `PROV-001`: a mutation committed and restored on a merged side branch could be hidden by path-history simplification | Reproduced. Path-history checks now use full history, merge commits after baseline are forbidden, and a merge-side-branch control rejects the bypass. |
| 2. Baseline/lock supersession and immutability | `S2-001`: lock creator crashes on undefined `sys`; `S2-002`: creator did not itself reject a missing/non-ancestor starting HEAD; `S2-003`: clean isolated worktree lacked gitignored source bytes | Reproduced. Imported `sys`; creator now invokes the pinned isolated prelock environment; missing/non-ancestor starting commits have creator-level checks/tests; a bounded source-staging helper provides and verifies gitignored sources in worker worktrees. |
| 3. Canonical path / symlink containment | `PATH-001`: literal backslashes were accepted as POSIX filename characters despite the contract | Reproduced. Validator and prompt builder now reject every backslash; focused negative control passes. |
| 4. Frozen hashes / target binding | `S4-001`: nineteen generic/item component units lacked `extractionPath`, so no required comparison target existed | Reproduced. All 56 sampled component rows now carry a manifest-frozen target; builder and validator reject any missing/non-frozen target. IDs, order, strata, and counts remain unchanged. |
| 5. Strict JSON / fail-closed behavior | `JSON-001`: a nonempty hash-pinned raw reviewer response was not bound to the substantive sealed conclusion | Reproduced. Completeness, blind, comparison, and verification raw responses must now equal the exact substantive payload sealed in their lane artifacts; unrelated hash-pinned content is rejected. |
| 6. Reviewer identity / lane-order independence | `S6-001`: human/agent IDs are provenance attestations and can be relabeled by a dishonest orchestrator | Bounded trust boundary, not treated as cryptographic identity. Final execution must record actual Hermes subagent IDs, separate workspace locks, exact prompt/response hashes, and distinct role assignments; the validator rejects reused declared identities, while the integrator independently checks the runtime handoffs. Raw-response payload binding was added so relabeling cannot substitute different conclusions silently. |
| 7. Source-only leakage / citation closure | Worker completed probes but was interrupted while attempting an out-of-scope broad temporary cleanup; its final report is non-evidence. Its reproduced probe showed unrelated allowed evidence could be assigned to a manifest-pinned component unit. | Finding independently reproduced and fixed: every FAQ/component unit with a manifest source tuple now requires direct evidence using that exact path and SHA-256. The specialty must be rerun cleanly on the final candidate. |
| 8. Deterministic 23-unit clean-match selection | Core selection reported correct; no material bypass established | Retained. Existing missing-stratum, size, uniqueness, publication-timing, and verification controls remain green. |
| 9. Evaluator thresholds/escalation | `S9-001`: blocked evidence could be masked by material/critical status precedence | Reproduced. Source-blocked derivations/rows now dominate final status, while the pure evaluator independently counts blocked, material, and critical discrepancy severities so none can mask another. |
| 10. Progress transitions / rollback / HEAD binding | `S10-001`: lock-creator crash; malformed all-pending refresh accepted incomplete shapes; committed skips/timestamp regressions were snapshot-valid | Reproduced. Creator fixed; pending refresh requires exact top-level/row contracts; post-lock validation replays first-parent progress history, rejects merges/skips/row mutation, enforces stage artifact fields, counts, and increasing timestamps. |
| 11. Mutation completeness / crash resistance | Provider safety filter blocked the reviewer before a usable verdict | Non-evidence. The specialty must be rerun with a narrower authorized correctness-testing brief on the final candidate. |
| 12. Worktree-safe paths / methodology/status | Isolated worktree could not reproduce the gate without gitignored PDFs/assets; also reproduced lock-creator crash | Reproduced. Added hash-verifying, symlink-rejecting source staging and exact methodology commands; lock creator fixed and smoke-run to its expected immutable-byte refusal. |

## Holistic setup-review disposition

The separate holistic reviewer rejected candidate 1. Its concrete blockers overlapped the reproduced undefined-`sys` lock failure and incomplete immutable coverage for v2/final setup-review evidence. The creator now includes all committed v2 historical prompts/envelopes and the source-staging helper; the final specialty/setup review artifacts will be added to `LOCKED_FILES` before baseline creation. The holistic review must be rerun on the final candidate.

## Additional control correction found by the integrator

The direct-child seal contract and the requirement that all comparisons precede adjudication imply dependency-level wave commits. The methodology now states that all artifacts at one dependency level share one pre-seal HEAD and one direct-child wave seal commit: packet/prompt wave, completeness wave, blind wave, comparison wave, then adjudication wave. A positive multi-artifact wave control passes, while later/intervening artifact introductions remain rejected.

## Verified post-fix checkpoint

- Manifest population remains 140 units: 56 concise rules, 28 FAQ units, 56 sampled component effects.
- All units remain `pending-blind-derivation`.
- 72/72 structural, provenance, response-binding, progress-history, and mutation controls pass.
- 11/11 decision-gate tests pass.
- Prelock validation passes with zero failures.
- `scripts/create_correctness_audit_lock.py` runs manifest freshness and isolated prelock validation, then correctly refuses the uncommitted post-candidate bytes; it does not create a lock.
- `scripts/stage_correctness_audit_sources.py --check` verifies 1,098 source files across the two gitignored source trees in the canonical worktree.

This checkpoint is not baseline acceptance. A second exact-candidate twelve-specialty wave and completed holistic setup review remain mandatory.
