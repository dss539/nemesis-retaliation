# Stage 1 v1 baseline supersession

Date: 2026-08-29
Status: **superseded before any audit-unit lane transition**

## Preserved baseline

- The original v1 lock is preserved byte-for-byte as `audit-lock-v1.json`.
- The v1 baseline commit recorded in the preserved lock is `2fe3f0da7da6e462bbcdcca7db29571b52a2d27c`.
- The separate v1 lock commit is `3e23aebf52bac07ca54829fb49e4eb1f375bf599`.
- The deterministic population remains exactly 140 units: 56 concise rules, 28 base-applicable FAQ entries, and 56 stratified component effects.
- `progress.json` remained at `pending-blind-derivation` for all 140 units when this supersession was recorded.
- No concise rule, semantic record, or implementation file was changed by an audit judgment.

## Reason for supersession

A late independent adversarial review completed after the v1 baseline was locked and identified a critical seal-provenance defect. The finding was reproduced locally:

1. v1 validated only that each `sealedAtGitHead` value named an existing descendant of the baseline.
2. It did not require the artifact's exact bytes to exist in Git at a deterministically derived seal commit.
3. A source packet and prompt could therefore claim the baseline HEAD while being untracked or produced later.
4. For the draft `unit-001` packet and prompt, `git show 3e23aeb:<path>` failed because neither path existed at the claimed HEAD.

Two other late concerns were reassessed against the final v1 code: canonical path containment and packet citation coverage had been hardened before the baseline. They remain covered by mutation controls. Exact-quote fidelity still depends on a source-only reviewer and rendered visual evidence and will receive additional v2 controls.

## v2 repair requirements

Before any unit may leave `pending-blind-derivation`, v2 must:

1. Treat `sealedAtGitHead` as the immediate **pre-seal** HEAD and derive the artifact commit as the first direct child that introduces the exact artifact bytes.
2. Require the artifact, prompt, raw reviewer response, and referenced visual evidence to be present byte-for-byte in the appropriate derived lane commit.
3. Enforce strict Git ancestry between packet, completeness-review, blind-derivation, comparison, and separate final-adjudication lane commits.
4. Generate reviewer prompts canonically from fixed instructions plus source-only payloads and validate those bytes.
5. Add adversarial tests for uncommitted artifacts, later-modified artifacts, false seal heads, and lane-order violations.
6. Preserve the original sample selection and seed material; v2 is a control-layer repair, not a reselection.
7. Obtain and disposition fresh independent setup criticism before locking the v2 baseline.

The v1 lock must not be used to authorize audit execution.
