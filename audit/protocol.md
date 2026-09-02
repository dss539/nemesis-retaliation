# Fragment-coverage audit — parent-side protocol

For the coordinator (parent). Children read only `instructions.md`.

## Failure handling

A child's **fail** is a claim, not a fact. Handle every fail as follows:

1. **Verify.** Independently check the claim against the fragment text and
   the concise corpus before accepting it. One targeted search per claim.
2. **Triage the cause:**
   - **True gap** — the content is genuinely missing from the corpus →
     add a repair entry to `todo.md` (target file, section, what to add,
     the fragment's source citation). The audit records; it never repairs.
   - **Slice defect** — the fragment was badly cut or contains noise →
     fix the slicing and re-run that fragment. Do not repair the corpus
     for a bad fragment.
   - **Child error** — the verified claim does not hold → correct the
     verdict, note the correction in the sidecar, move the fragment to
     `pass/`. No re-run.
3. **Repair as separate work.** Corpus edits happen as their own commit
   with the status validator run, distinct from verdict commits.
4. **One re-check, no loops.** After a repair commits, re-run or manually
   re-check the affected fragment exactly once, then proceed.
5. **Cluster rule.** If a wave shows a recurring failure pattern across
   fragments (a systemic corpus or methodology problem), stop and report
   to the owner before any repair, rather than making N small edits.

Repairs never happen inside an audit wave. Waves only produce verdicts
and file moves.