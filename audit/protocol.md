# Fragment-coverage audit — parent-side protocol

For the coordinator (parent). Children read only `instructions.md`.

## Unsure handling

An `unsure` verdict is recorded by the verifier, not resolved by the verifier.
The canonical fragment lives in `unsure/` with its minimal `.unsure.md`
sidecar. A later, separately assigned coordinator review determines whether it
is genuinely covered, missing, contradictory, or otherwise dispositioned.
That later review must not be folded into the verifier's task.

## Failure handling

A child's **fail** is a claim, not a fact. Handle every fail as follows:

1. **Verify.** Independently check the claim against the fragment text and
   the concise corpus before accepting it. One targeted search per claim.
2. **Triage the cause:**
   - **True gap** — the content is genuinely missing from the corpus →
     move the fragment glob to `repair/` and write a `<ID>.repair.md`
     sidecar (defect, source content, applied fix, re-check state).
     The audit records; it never repairs.
   - **Irrelevant to gameplay** — the source assertion is accurate but does
     not affect gameplay → move the fragment to `irrelevant/`. Remove its
     fail sidecar; do not add it to the corpus or send it back to verification.
   - **Slice defect** — the fragment was badly cut or contains noise →
     fix the slicing and re-run that fragment. Do not repair the corpus
     for a bad fragment.
   - **Child error** — the verified claim does not hold → correct the
     verdict, note the correction in the sidecar, move the fragment to
     `pass/`. No re-run.
3. **Repair as separate work.** Corpus edits happen as their own commit
   with the status validator run, distinct from verdict commits.
4. **One re-check, no loops.** After a repair commits, re-run or manually
   re-check the affected fragment exactly once, then proceed. When the
   re-check passes: move the fragment files back to the audit root and
   delete the `.fail.md` and `.repair.md` sidecars.
5. **Cluster rule.** If a wave shows a recurring failure pattern across
   fragments (a systemic corpus or methodology problem), stop and report
   to the owner before any repair, rather than making N small edits.

Repairs never happen inside an audit wave. Waves only produce verdicts
and file moves.