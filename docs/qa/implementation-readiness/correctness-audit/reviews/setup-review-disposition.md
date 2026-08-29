# Audit-harness setup review disposition

## Review boundary

Two isolated Ollama Cloud reviewers received the original setup prompt before any audit unit was derived:

- `deepseek-v4-pro:0813`, `think: "max"` — verdict `reject`, 19 findings;
- `glm-5.3`, `think: "max"` — verdict `accept-with-fixes`, 10 findings.

Their final JSON answers and exact prompt are retained in `reviews/`. Provider reasoning traces were not retained. The reviews are advisory; each finding below was checked against the actual builder, schemas, validator, and method.

## Accepted shared findings

The following overlapping findings were accepted and corrected:

| Topic | DeepSeek | GLM | Disposition |
|---|---|---|---|
| Mutable/self-consistent lock is not external evidence | F-01, F-10 | F-002 | Add a two-commit Git baseline plus `audit-lock.json`; validator binds immutable bytes to the baseline commit and checks ancestry/drift. |
| Blind conclusions could leak through loose packets | F-02 | F-004 | Add a closed source-packet schema, allowed source-path prefixes, forbidden downstream prompt tokens, and source-only completeness review. Manifest selection metadata is supervisor-only and is never sent to the blind reviewer. |
| FAQ source/population insufficiently pinned | F-03, F-12 | questions | Pin the FAQ PDF in selection inputs; retain all 28 IDs; capture page index directly while iterating pages rather than by dictionary-value membership. Independently reassess applicability during the FAQ packet audit. |
| Strata hide eligibility/known-hard boundaries | F-04, F-05 | F-003 | Publish eligible/selected counts, sample all four Intruder Help contexts including bottom row, sample Attack source occurrences directly, reserve two Equipment slots for source/class boundaries, and state the non-probability/sample limitations. |
| Blind derivation embedded in editable final result | F-06 | F-009 | Split source packet, completeness review, prompt, blind derivation, raw model response, and post-reveal comparison into separately hashed artifacts. |
| Hollow results and skipped lanes could pass | F-07 | F-001 | Add conditional minimum requirements/scenarios, explicit source-blocked records, exact current-state references, and a transactional lane-transition script. |
| Declared JSON Schema was not actually enforced | F-07 | F-007 | Validate every artifact with pinned `jsonschema` Draft 2020-12 plus project-specific cross-file checks. |
| Path/hash containment was incomplete | F-08 | F-009 | Verify real resolved containment and SHA-256 for packet, prompt, completeness, blind, comparison, and model-response paths. |
| Thresholds/root causes were prose only | F-09 | F-006 | Add mandatory root-cause IDs, authority/default flags, executable recurring-pattern logic, exact clean-match sampling, and a decision evaluator. |
| Result mutations were too narrow | F-11 | F-008 | Replace the suite with an end-to-end valid fixture plus 15 content/integrity mutations and six decision-threshold tests. |
| Status transitions were not mechanically constrained | F-18 | F-001 | Add `advance_correctness_audit_progress.py`; it rejects skipped transitions, validates after each update, and rolls back failures. Git checkpoints retain history. |
| Final claim could overstate unaudited components | F-19 | F-010 | Require an audited-units-only claim, source-blocker enumeration, affected-family reporting, and approximately 199 unaudited primary component units in the current planning inventory. |

## Accepted DeepSeek-only findings

- **F-14 — source-universe drift:** accepted in part. The manifest now publishes independently hard-coded candidate-universe counts and hashes every source index/input. Existing full source-index/extraction validators remain required; Stage 1 does not claim to re-audit every unselected source byte.
- **F-15 — concise titles leak conclusions:** accepted. Concise-rule manifest labels are neutralized to the rule ID. Blind packets use neutral audit IDs and direct source locators only.
- **F-16 — visual evidence was not enforced:** accepted. Packet schema supports source-bound visual paths, and packets must record all component/visual channels checked. Actual visual sufficiency is assessed batch by batch before blind derivation.

## Rejected or bounded findings

- **DeepSeek F-13 — Action card source path implies wrong Character. Rejected.** Some exact card occurrences come from a shared extracted source sheet stored beneath a historical folder name. Character attribution comes from the exact TTS occurrence/deck tuple, not the directory name. Packets must include the exact crop/occurrence evidence, so a path label cannot establish identity.
- **DeepSeek F-17 — alternate seed must reproduce the same sample. Rejected as stated.** A different audit seed is supposed to choose a different sample. Reproducibility means identical inputs and the fixed seed produce byte-identical output. Hash-seed/locale controls remain appropriate for implementation determinism; alternate audit seeds are sensitivity analysis, not an integrity proof.
- **GLM F-004 — n-gram scan against concise/semantic text. Rejected.** Official source wording may legitimately overlap concise rules that quote it. Such a scan creates false positives and does not prove provenance. Closed fields, exact source paths/hashes, isolated prompts, and independent completeness review provide the enforceable boundary.
- **GLM F-003 — audit multiple occurrences for each selected Attack title. Bounded rather than adopted.** The fixed quota is two Attack units, not four. The builder now samples all twenty source occurrences directly and states that same-title flattening detection is not guaranteed. Any Attack defect triggers affected-family expansion.

## Residual limitations before audit

- The audit inherits the already validated source indexes as its candidate inventories; it does not independently re-extract all component roots.
- Model diversity is a blind-spot aid, not human-independent validation.
- Git anchoring detects later drift but cannot prove the human seed was never inspected before the first baseline. The seed, selection algorithm, prompt, and initial model critiques are preserved for review.
- A Stage 1 pass remains limited to the 140 audited units.

## Verification added after review

- 26/26 structural/content mutations pass.
- 6/6 decision-gate tests pass.
- A valid synthetic packet → completeness → blind → comparison chain passes the real schemas and validator.
- Semantic leakage fields, incomplete search records, empty derivations, one-option ambiguities, path escapes, reviewer reuse, seal-order reversal, severity downgrade, threshold drift, universe drift, and selection-coverage drift are all rejected.
