# Fragment-coverage audit — parent-side protocol

For the coordinator (parent). Children read only `instructions.md`.

## Frozen verification drain

Keep the concise corpus, manifest, verifier instructions, and claim helper frozen while workers are active. Verifiers may modify only fragments they have durably claimed and the matching generated verdict sidecars. Corpus repairs, triage, status edits, commits, and other shared writes happen centrally after the drain stops.

The owner chooses worker count and model mix. Work stealing coordinates files; it does not impose a provider-concurrency ceiling.

## Race-safe self-claiming

Canonical unresolved inputs are the manifest-listed `.txt` files directly under `audit/`. Every worker repeatedly invokes:

```text
python3 scripts/audit_work_steal.py claim --worker <WORKER-ID>
```

One helper invocation performs the entire short claim transaction:

1. shuffle currently visible unresolved manifest files;
2. open a selected existing path read-only, without `O_CREAT`;
3. attempt `LOCK_EX | LOCK_NB` on that file descriptor;
4. after acquiring the flock, compare `fstat(fd)` with the current root pathname's device/inode and reject a vanished, replaced, or symlinked path;
5. atomically rename the unchanged filename into `audit/claimed/<worker-id>/` on the same filesystem while the descriptor remains flocked;
6. fsync the affected directories, then unlock and close the descriptor.

A lost race never creates a replacement file. Contenders retry other randomly ordered candidates with bounded jitter. A worker stops only when the helper reports no visible root candidate; the parent alone determines global completion.

The durable claim directory, not a long-lived flock process, records ownership during later LLM/tool calls. Workers never use `.workspace.lock`.

## Finalization and sidecars

Workers choose only `pass`, `fail`, or `unsure` and invoke the helper's `finalize` command. The helper requires the exact runtime model and provider and writes:

```text
Model: `<actual-model>`
Provider: `<actual-provider>`
Evidence: <minimal citation, gap, or uncertainty>
```

Canonical naming remains unchanged:

- `<name>.txt` → `<name>.pass.md` in `audit/pass/`
- `<name>.txt` → `<name>.fail.md` in `audit/fail/`
- `<name>.txt` → `<name>.unsure.md` in `audit/unsure/`

The helper stages and fsyncs the sidecar, installs it without overwrite, then atomically moves the uniquely owned fragment into the same verdict directory. The parent reconciles any interruption between these operations before accepting closure.

## Abandoned-claim recovery

After a worker exits, fails, or is interrupted, run:

```text
python3 scripts/audit_work_steal.py recover --worker <WORKER-ID>
```

Recovery is parent-only. It completes a final move when a canonical sidecar proves finalization had started; otherwise it returns the unchanged abandoned fragment to the audit root. It refuses conflicts or duplicate verdict residues. Recovered fragments may be claimed by another worker.

Before declaring the drain complete, the parent verifies:

- no manifest fragment remains at the audit root;
- `audit/claimed/` has no active or abandoned fragment;
- every manifest entry has exactly one canonical fragment location;
- every pass/fail/unsure fragment has its exact sidecar;
- there are no orphaned or opposite-verdict sidecars;
- every new sidecar identifies its actual runtime model and provider.

## Unsure handling

An `unsure` verdict is recorded by the verifier, not resolved by the verifier. The canonical fragment lives in `unsure/` with its minimal `.unsure.md` sidecar. A later, separately assigned coordinator review determines whether it is genuinely covered, missing, contradictory, or otherwise dispositioned. That later review must not be folded into the verifier's task.

## Failure handling

A child's **fail** is a claim, not a fact. Handle every fail as follows:

1. **Verify.** Independently check the claim against the fragment text and concise corpus before accepting it. One targeted search per claim.
2. **Triage the cause:**
   - **True gap** — move the fragment glob to `repair/` and write a `<ID>.repair.md` sidecar (defect, source content, applied fix, re-check state). The audit records; it never repairs.
   - **Irrelevant to gameplay** — move the fragment to `irrelevant/`. Remove its fail sidecar; do not add it to the corpus or send it back to verification.
   - **Slice defect** — fix slicing and re-run that fragment. Do not repair the corpus for a bad fragment.
   - **Child error** — correct the verdict, note the correction in the sidecar, and move the fragment to `pass/`. No re-run.
3. **Repair as separate work.** Corpus edits happen as their own commit with the status validator run, distinct from verdict commits.
4. **One re-check, no loops.** After a repair commits, return the affected fragment to the audit root without fail/repair sidecars and assign one fresh independent re-check.
5. **Cluster rule.** If a drain shows a recurring failure pattern, stop and report to the owner before repair rather than making N small edits.

Repairs never happen inside an active verification drain. The drain only produces verdicts and file moves.
