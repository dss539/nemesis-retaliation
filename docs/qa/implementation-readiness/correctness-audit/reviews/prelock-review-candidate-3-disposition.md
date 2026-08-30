# Stage 1 v2 prelock review-candidate 3 disposition

- Reviewed candidate: `6a13b9e6f57307a76756cf90da2aaa7682aa699b`.
- Evidence: `final-specialty-01-candidate3.json` through `final-specialty-12-candidate3.json`.
- Result: five specialties passed with no finding; seven findings were reproduced and fixed before candidate 4. Candidate 3 is superseded and never had an active v2 lock.

| Finding | Disposition |
|---|---|
| `PROV-002` — post-lock validator accepted a merge before baseline | Accepted. Post-lock `validate_lock()` now applies the same `starting_head_failures()` linear-history/merge contract as the creator. |
| `PATH-003` — dangling final target symlink | Accepted. Source staging rejects any symlink component regardless of referent existence and refuses symlink final targets before copying. |
| `S5-C3-001` — boolean `schemaVersion` equals integer 1 in Python | Accepted. Model envelope version now requires exact `int` type excluding `bool`; focused boolean control added. |
| `S7-C3-001` — partial source-only denylist | Accepted. Forbidden paths are derived from the manifest's non-source frozen maps/targets and implementation roots; post-reveal identifiers are derived from the closed comparison/adjudication schemas minus an explicit shared-source allowlist. Both prompt modes run the same inventory preflight before writing. |
| `S10-R3-001` — progress key order was not canonical | Accepted. Canonical progress serialization sorts keys; manifest initialization and updater writes use the same bytes, and history compares committed bytes to this canonical form. |
| `S11-C3-001` — PDF control bypassed public validator | Accepted. The committed test invokes `validate_packet(..., enforce_seals=True)` with an unrelated valid PNG, an independent correct page-1/160-DPI `pdftoppm` render, a wrong page, and wrong DPI. |
| `S12-R12-C3-001` — status/brief future-tense | Accepted as documentation drift. Candidate-4/baseline status identifies candidate 3 as superseded and the containing commit as the reviewed baseline transition rather than instructing creation of an already-existing candidate. |

Additional controls added during disposition cover: prebaseline merged deleted lane history, split dependency waves, strict model-envelope keys/types, source-only inventory coverage, unit-scoped evidence, four raw-response lanes, malformed containers/top-levels, exact decision boundaries/reporting, updater rollback, and transition-artifact-at-commit binding.

The focused gate remains 140 all-pending units with the original seed, IDs, order, strata, and counts. Candidate 4 requires targeted rereview of specialties 1, 3, 5, 7, 10, and 11 plus a holistic setup/lock-lifecycle review before it can be the baseline.
