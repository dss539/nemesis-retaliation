# Sol Max worker 05 shard report

- **Runtime:** `openai-codex:gpt-5.6-sol`, reasoning `max`, native route verified, session `20260815_222507_ce8f8a`
- **Scope:** `W04-009`, `W04-010`, `W04-011` in assignment order
- **Reconciliation:** 3 submitted / 3 returned / 3 raw / 3 results; exact IDs and order match
- **Native evidence:** 3 blind exact-source reads + 3 worker-local all-49 glossary contact-sheet reads
- **Outcome:** 0 promote, 3 defer, 0 candidate sidecars, 0 canonical/shared writes
- **Validation:** all source hashes and decodes passed; `worker_utils.py validate --require-complete` passed

## Assets

1. **W04-009 — CHAIN OF COMMAND / HEAVY GUN OPERATOR**
   - Exact visible text persisted; `[lander]` directly verified against all 49 glossary crops.
   - **Defer:** no concrete cell-11 selector/unique pair; existing canonical target differs and cannot be overwritten.
2. **W04-010 — CONTINUOUS FIRE / HEAVY GUN OPERATOR**
   - Exact visible text persisted; `[ammoToken]` and both `[actionCard]` glyphs directly verified.
   - **Defer:** no concrete cell-12 selector or unique pair, so the individual FaceURL/pairing promotion gate is not met.
3. **W04-011 — DEMOLITION / HEAVY GUN OPERATOR**
   - Exact visible text persisted; `[malfunction]` directly verified.
   - **Defer:** no concrete cell-13 selector/unique pair; existing target says `Destroy 1 accessible Door.` while assigned pixels say `Remove 1 Door.`

## Audit note

After W04-009 raw persistence, a broad search accidentally exposed brief worker-04 snippets for another ID. They were not used: the blind record already existed, and icon identity was independently established from the worker-local authoritative contact sheet.

**Next pending:** none.
