# Stage 1 v2 targeted review-candidate 4 disposition

- Reviewed candidate: `9af725a59b20d8d70a13487f0e588d7306ee16e6`.
- Candidate status: superseded review snapshot; no active v2 lock existed.
- Retained evidence:
  - `targeted-specialty-03-candidate4.json` — dynamic path rereview passed;
  - `targeted-specialty-05-candidate4.json` — strict model-envelope rereview passed;
  - `targeted-specialty-07-candidate4.json` — one source-only key-name leak found;
  - `targeted-specialty-10-candidate4.json` — canonical progress/history rereview passed;
  - `targeted-specialty-11-candidate4.json` — public PDF render/mutant-control rereview passed.
- The first path attempt is retained only outside Git as non-evidence because it stopped before dynamic verification. The complete r14 report supersedes it.
- The first targeted provenance worker did not return a usable final report within its bounded window. The post-lock/prebaseline-merge fix remains covered by the candidate-3 reproduced report, the committed creator/validator shared helper, focused controls, and the required holistic lock-lifecycle review; no acceptance claim relies on that incomplete targeted attempt.

## Reproduced finding and fix

`S7-C4-001` showed that the source-only inventory rejected forbidden identifiers in string values but not JSON object keys. The candidate-5 fix checks every object key against the inventory before descending, and the inventory-driven control now exercises each forbidden post-reveal identifier as both key and value. The inventory itself is derived from all non-source frozen manifest paths/targets and the closed comparison/adjudication schemas, minus only properties present in the source-packet/completeness schemas or the explicit shared reviewer provenance set.

## Verified retained boundaries

- Dangling target symlinks fail before copy and cannot create an external referent.
- Model envelope `schemaVersion` requires exact integer type; booleans and floats cannot equal version 1.
- Canonical progress bytes are independent of input key order and used by initialization/updater/history.
- The public PDF control enters `validate_packet(..., enforce_seals=True)`, rejects unrelated/wrong-page/wrong-DPI PNGs, and accepts an independent correct page/DPI render.
- All 140 units remain pending with unchanged seed, IDs, order, strata, and counts.

Candidate 5 requires a targeted source-only inventory rereview and a holistic setup/lock-lifecycle review before baseline promotion.
