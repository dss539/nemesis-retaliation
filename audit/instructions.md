# Fragment-coverage audit — worker instructions

You are auditing one fragment of official Nemesis: Retaliation source
material against the project rules corpus. Work only with the files named in
your task assignment.

## Input

Your task names one audit ID. Rulebook IDs use `RB-P<PDF-page>-<sequence>`
(for example `RB-P12-001`) and live directly under `audit/`; every rulebook
file contains exactly one visually harvested fact or rule. Other source IDs
remain directly under `audit/` and may comprise more than one file. Resolve
the exact input path with a glob and never guess filenames.

The matched `.txt` file or files are the full fragment. Read all of them.

## The question

For the fragment as a whole, answer exactly one question:

> Are the rules and behavior documented in this fragment fully and accurately
> captured already in the corpus?

The corpus to compare against:

- `docs/rules/00-foundations.md`
- `docs/rules/01-round-and-turns.md`
- `docs/rules/02-character-actions.md`
- `docs/rules/03-intruders-and-survival.md`
- `docs/rules/04-items-and-equipment.md`
- `docs/rules/icon-glossary.md` (icon meanings)
- `docs/rules/open-questions.md` (ambiguities already recorded — do not
  report these as gaps)

Search the corpus thoroughly (read the relevant rule files; grep for key
terms). Verdicts must reflect what the corpus actually says, not what it
plausibly could say.

## Verdict and action

Exactly one verdict per fragment (not per input file):

- **pass** — every rule and behavior in the fragment is affirmatively present,
  settled, and correct in the corpus. Move each input file into `pass/` and
  write one sidecar file per input file moved, named `<ID>.<suffix>.pass.md`
  (for example `RB-P12-001.fact.pass.md`), containing only enough to verify
  the evidence: the corpus file and section that covers the fragment (one or
  two lines).

- **fail** — something in the fragment is missing from the corpus, or the
  corpus contradicts the fragment. Move each input file into `fail/` and write
  one sidecar per input file, named `<ID>.<suffix>.fail.md`, briefly naming
  exactly what is missing or wrong: e.g. "no mention found anywhere" or
  "only partially satisfied by X (corpus says Y, fragment says Z)".

- **unsure** — you find a potentially relevant entry in `open-questions.md`,
  or another corpus passage whose settled/operative status is unclear, and
  therefore cannot confidently classify the fragment as pass or fail. Move
  each input file into `unsure/` and write one sidecar per input file named
  `<ID>.<suffix>.unsure.md`, citing the potentially relevant entry and briefly
  stating what remains uncertain. Do not decide or resolve the open question.

A mention in `open-questions.md` is never a pass by itself. Use **pass** only
when another clearly settled corpus record fully and accurately captures the
fragment; otherwise route the open-question match to **unsure**.

Keep sidecars minimal — only enough information to verify the evidence, gap,
or uncertainty. No long analysis, no restating the fragment.

## Rules

1. Glob your ID to collect input files; glob again when moving. Do not touch
   any file whose name does not start with your audit ID.
2. Create `pass/`, `fail/`, or `unsure/` if the required destination does not exist.
3. Move files; do not copy or leave originals behind.
4. Do not edit any corpus file, any file outside `audit/`, or this
   instructions file. You are read-only everywhere except your own input
   files and their sidecars.
5. No OCR, no vision, no image or PDF review — text files only.
6. Answer only the coverage question. Do not propose methodology changes,
   new machinery, or corpus edits in your sidecars.
7. When finished, reply to the parent with: your audit ID, the verdict
   (`pass`, `fail`, or `unsure`),
   and a one-sentence explanation.