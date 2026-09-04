# Fragment-coverage audit — worker instructions

You are one worker in a self-scheduling audit of official Nemesis: Retaliation source fragments against the project rules corpus. Your task supplies a worker ID and the exact runtime model/provider metadata to record.

## Claim one fragment

Work directly in the selected repository. Never acquire, inspect, wait on, or touch `.workspace.lock`.

Run this command from the repository root:

```text
python3 scripts/audit_work_steal.py claim --worker <WORKER-ID>
```

The helper randomly selects one unresolved manifest fragment, opens the existing file without creating it, obtains a nonblocking per-file flock, revalidates pathname/inode identity, and atomically moves the unchanged filename into `audit/claimed/<WORKER-ID>/` before releasing the flock. The JSON response is authoritative:

- `claimed`: review only the returned ID and path.
- `busy` or `retry`: run the claim command again; do not busy-spin or choose a path yourself.
- `empty`: stop and report your totals. Only the parent may declare global completion.

Never claim, copy, move, or edit another worker's file manually.

## Coverage question

Read the entire claimed `.txt` fragment. Answer exactly:

> Are the rules and behavior documented in this fragment fully and accurately captured already in the corpus?

Compare against:

- `docs/rules/00-foundations.md`
- `docs/rules/01-round-and-turns.md`
- `docs/rules/02-character-actions.md`
- `docs/rules/03-intruders-and-survival.md`
- `docs/rules/04-items-and-equipment.md`
- `docs/rules/icon-glossary.md`
- `docs/rules/open-questions.md`

Search the relevant corpus text thoroughly. Judge what it affirmatively says, not what it plausibly could say.

## Verdicts

Choose exactly one verdict for the whole claimed fragment:

- **pass** — every rule and behavior is affirmatively present, settled, and correct.
- **fail** — something is missing or contradicted.
- **unsure** — a potentially relevant open question or passage leaves settled/operative status unclear.

A mention in `open-questions.md` is never a pass by itself. Use pass only when separate settled corpus text fully covers the fragment. Do not resolve open questions.

## Finalize only through the helper

Use the exact model and provider supplied in your task. Give one concise evidence/gap/uncertainty sentence:

```text
python3 scripts/audit_work_steal.py finalize --worker <WORKER-ID> --id <ID> --verdict <pass|fail|unsure> --model <MODEL> --provider <PROVIDER> --evidence "<concise citation or finding>"
```

The helper writes the model/provider/evidence sidecar and routes the fragment without changing its filename. Do not write sidecars or move fragments by hand.

After a successful finalize, immediately claim another fragment. Continue until claim returns `empty`. If a tool call fails or you are interrupted, report the currently claimed ID so the parent can recover it.

## Boundaries

1. You may modify only fragments you successfully claim and their generated sidecars through the helper.
2. Do not edit the corpus, protocol, status files, helper, manifest, or unrelated audit files.
3. No OCR, vision, image, PDF, TTS, or legacy-implementation review. Use the supplied text fragment and existing text corpus only.
4. Do not repair, recut, triage, reinterpret gameplay relevance, or move anything to `repair/` or `irrelevant/`.
5. Keep findings minimal. Do not propose methodology or machinery changes.
6. On exit report worker ID; actual model/provider; counts by pass/fail/unsure; and any claimed ID left unfinished.
