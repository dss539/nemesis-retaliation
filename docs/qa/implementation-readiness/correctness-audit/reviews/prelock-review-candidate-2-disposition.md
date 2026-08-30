# Stage 1 v2 prelock review-candidate 2 disposition

## Boundary

- Reviewed candidate: `ee42f3522859d1dd7ce782c801023cb71fd53071`.
- Candidate status: **superseded as a non-authoritative review snapshot**; it is not the v2 baseline and never had an active v2 lock.
- Evidence: twelve complete reports retained as `final-specialty-01-candidate2.json` through `final-specialty-12-candidate2.json`.
- All reports were produced under separate task-workspace root flocks against the exact candidate. No audit unit left `pending-blind-derivation`.

## Disposition summary

| Specialty | Disposition |
|---|---|
| 1 — Git provenance / wave seals | Accepted `PROV-002`: prebaseline history now uses full-history traversal and rejects merges from locked starting HEAD through baseline. Accepted `WAVE-001`: active packet, completeness, blind, comparison, and adjudication artifacts must each resolve to one shared dependency-wave seal commit. |
| 2 — lock lifecycle | Accepted `S2-004`: intentionally gitignored frozen source inputs are now verified as allowed local source paths against manifest SHA-256 after lock; only tracked frozen artifacts require baseline Git blobs. |
| 3 / 12 — paths and source staging | Accepted prompt-output and source-root/intermediate-symlink findings. Prompt output now requires canonical repository-relative POSIX syntax and no symlink components. Source staging checks the raw source-root and every source prefix before resolution and rejects backslashes. The prelock/post-lock command matrices are now separate. |
| 4 — target roles | Accepted `S4-002`: only `pilots.json`, `review-gates.json`, and `contradictions.json` can carry semantic-projection; every comparison must reveal `pilots.json` as behavior projection. Source indexes cannot satisfy that role. |
| 5 / 11 — strict failure behavior | Accepted strict model-envelope and malformed-input findings. The model envelope has an exact success-key/type contract; artifact semantic checks stop on schema failure; non-object manifest/progress inputs fail normally. Additional controls cover malformed containers. |
| 6 — reviewer identity | Accepted both declared-metadata bypasses. Agent/human identity is `(kind, stable reviewerId)` only. Model identity is nonempty provider plus nonempty resolved `responseModel`; requested aliases never substitute for missing resolution. Runtime attribution remains an explicit integrator trust boundary. |
| 7 — blindness / evidence closure | Accepted both findings. Canonical prompt construction performs source-only content preflight for packet and completeness payloads before writing either prompt. Packet evidence IDs are unique; evidence IDs and source path/SHA maps remain keyed by audit unit for comparison, verification, resolution, and primary-source reveals. |
| 8 — deterministic clean sample | Passed with no finding; unchanged. |
| 9 — decision reporting | Accepted two minor enumeration findings. Incomplete and complete reports always emit unfinished units, source blockers, affected families, and unaudited boundary. Recurring-root units contribute to affected families. |
| 10 — progress history | Accepted all three findings. Strict UTC `Z` timestamps are required; committed progress must use canonical bytes; a newly attached artifact must exist and hash-match at the transition commit and derive from an earlier/equal seal commit. |
| 11 — control coverage | Added substantive-response mutations for completeness, blind, and verification; decision boundary/recurrence/override/default/report tests; updater rollback test; deterministic PDF page rendering; malformed-container controls. |
| 11 — PDF visual source | PDF exactText now carries `pdfPageIndex` and locked 160-DPI metadata. Post-lock validation rerenders the exact full source PDF page with `pdftoppm` and requires the evidence PNG SHA-256 to match, so an arbitrary valid PNG cannot satisfy the contract. |

## Current focused gate

After integrating candidate-2 findings:

- manifest population remains 140 units in the original order and strata;
- all 140 progress rows remain pending;
- 92/92 mutation, provenance, path, response, evidence, render, wave, progress-history, and rollback controls pass;
- 15/15 decision tests pass;
- prelock structural validation passes with zero failures.

Candidate 3 must be committed, re-reviewed, and accepted before it can become the baseline. No v2 lock exists.
