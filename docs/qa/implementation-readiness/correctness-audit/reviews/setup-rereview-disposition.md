# Audit-harness setup rereview disposition

## Rereview attempts

The first-round GLM 5.3 and DeepSeek V4 Pro 0813 reviews remain the primary external setup critiques. Both were requested through Ollama Cloud with `think: "max"`; only `message.content` was retained.

Second-round attempts were intentionally bounded and preserved:

1. A 199 KB exact evidence packet produced empty `message.content` from both models. `setup-rereview-attempt-1-failure.json` records the failure without a reasoning trace.
2. A 116 KB reduced packet again produced empty content from GLM 5.3 and DeepSeek V4 Pro 0813. The GLM failure envelope is `glm-5.3-max-setup-rereview.json`; the older helper did not persist the raw failed response.
3. A 43 KB methodology/schema packet produced a usable DeepSeek response in `deepseek-v4-pro-0813-max-setup-rereview.json`.

The DeepSeek helper's console summary reported zero findings because it looked for `review.findings`; this response used `review.new_findings`. The retained body contains seven findings and is the review authority.

## DeepSeek R2 dispositions

| Finding | Disposition | Independent check and action |
|---|---|---|
| R2-F-01 completeness findings not reconciled | Accepted | The schema's empty unresolved list was not derived from finding rows. The validator now requires exact equality with unresolved material/critical findings, derives acceptance, and has a focused mutation. |
| R2-F-02 blind batch may omit/reorder units | Rejected as a code-blind claim; test added | `validate_blind()` already requires returned IDs to equal packet IDs exactly and rejects duplicates. The short rereview omitted validator code. An omitted-unit mutation now proves enforcement. |
| R2-F-03 discrepancy root/flag constraints absent | Rejected as a code-blind claim; defense strengthened | `validate_result()` already required root causes for material/critical rows and true flags for authority inversion/hidden default. Equivalent schema conditionals and focused mutations were added. |
| R2-F-04 reviewer path/hash not paired | Accepted as defense in depth | `checked_file()` already rejected a missing hash, but all three reviewer schemas now pair path and SHA-256 conditionally. A focused mutation proves it. |
| R2-F-05 packet metadata/free text and hollow evidence | Partly accepted | Scope, authority, and document roles now use closed source-local values; each evidence row must carry nonempty exact text or pinned visual evidence. Free-form locators/search terms remain necessary source-search records and are checked by the independent packet-completeness lane. Lexical n-gram suppression remains rejected because official source wording legitimately overlaps downstream wording. |
| R2-F-06 blind behavioral dimensions may be empty/absent | Accepted | Actor/decision owner, target/cardinality/decline rights, visibility, costs/payment, ordered operations, finite supply, impossible instructions, and partial resolution are now required and nonempty. Explicit `not applicable` is required where appropriate. |
| R2-F-07 final non-matches may evade verification | Rejected as a code-blind claim; test added | `validate_result()` already requires every final minor/material/critical/blocked/presentation/preserved ambiguity/conflict row to appear in an independent verification review. `compared` is intentionally an intermediate pre-Lane-D state and cannot produce a decision. A final-unverified mutation now proves enforcement. |

## Residual limitations

- The setup rereview that succeeded did not contain validator/test source, so it could verify methodology and schemas but not cross-file enforcement. The separate read-only local code critic covers that boundary.
- The Stage 1 component sample remains non-probability and cannot establish a defect-rate bound for the approximately 199 unaudited primary component-effect units.
- Free-form source locators, literal source text, search terms, and exclusion reasons cannot be lexically constrained without risking false rejection of authoritative text. Closed paths, source hashes, source-local metadata enums, separate completeness review, and prompt isolation are the controls.
- Empty model responses are failures, not verdicts. They are retained as such and do not count as acceptance.

## Verification after R2 fixes

- 26/26 structural/content mutation controls pass.
- 6/6 decision-gate tests pass.
- The valid synthetic packet → completeness → blind → comparison chain passes Draft 2020-12 schemas and the cross-file validator.
- No semantic record, concise rule, source extraction, or game implementation file was changed by the harness fixes.
