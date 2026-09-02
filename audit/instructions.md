# Fragment-coverage audit — worker instructions

You are auditing one fragment of official Nemesis: Retaliation source
material against the project rules corpus. Work only with the files named in
your task assignment.

## Input

Your task names one audit ID (for example `RB-12`). All your input files are
in this directory (`audit/`) and begin with that ID. Find them with a glob:
`RB-12.*` (never guess filenames; always glob).

The files with suffix `.txt` together are the full fragment: official source
material for one page/entry, already extracted to text. Read all of them.

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

- **pass** — every rule and behavior in the fragment is present and correct
  in the corpus. Move each input file into `pass/` and write one sidecar file
  per input file moved, named `<ID>.<suffix>.pass.md` (for example
  `RB-12.a.census.pass.md`), containing only enough to verify the evidence:
  the corpus file and section that covers the fragment (one or two lines).

- **fail** — something in the fragment is missing from the corpus, or the
  corpus contradicts the fragment. Move each input file into `fail/` and write
  one sidecar per input file, named `<ID>.<suffix>.fail.md`, briefly naming
  exactly what is missing or wrong: e.g. "no mention found anywhere" or
  "only partially satisfied by X (corpus says Y, fragment says Z)".

Keep sidecars minimal — only enough information to verify the evidence or
the gap. No long analysis, no restating the fragment.

## Rules

1. Glob your ID to collect input files; glob again when moving. Do not touch
   any file whose name does not start with your audit ID.
2. Create `pass/` or `fail/` if it does not exist.
3. Move files; do not copy or leave originals behind.
4. Do not edit any corpus file, any file outside `audit/`, or this
   instructions file. You are read-only everywhere except your own input
   files and their sidecars.
5. No OCR, no vision, no image or PDF review — text files only.
6. Answer only the coverage question. Do not propose methodology changes,
   new machinery, or corpus edits in your sidecars.
7. When finished, reply to the parent with: your audit ID, the verdict,
   and a one-sentence explanation.