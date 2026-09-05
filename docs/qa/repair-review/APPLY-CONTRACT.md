# Repair-application contract (per cluster)

You are applying an owner-approved, coordinator-reviewed proposal to the concise rules corpus. The proposal is authoritative for WHAT to add; you decide only WHERE within the named record and minimal wording glue.

## Inputs
- Proposal: `docs/qa/repair-review/clusters/<cluster>.md`, section `## Consolidated edits by target record`. Apply every block there. Ignore the per-ID table except to resolve ambiguity.
- Corpus files you may edit: `docs/rules/00-foundations.md`, `01-round-and-turns.md`, `02-character-actions.md`, `03-intruders-and-survival.md`, `04-items-and-equipment.md`, `icon-glossary.md` (only if the proposal names it), `open-questions.md` (only to ADD a boundary sentence the proposal names; never remove or close an entry).
- Do NOT touch `audit/`, `PROJECT_STATUS.md`, `todo.md`, any `docs/qa/` file, `source-extraction/`, or any other cluster file. No /tmp. No ad hoc scripts; use read_file / patch / write_file.

## Rules
1. Insert each block's text into the named record (e.g. `## FND-012 — …`) as new bullets/subsections at the end of that record, before the next `## ` heading. Keep the corpus voice (`- **Plain rule:**`, `- **Source:**`, `- **Boundary:**`). Card/Room/Objective occurrence tables go in as markdown tables under a `### <name> source occurrences` subsection inside the named record.
2. Copy proposed sentences verbatim. Do not paraphrase, shorten, merge two rows, or "clean up" a literal `[…]` token. Preserve `“ ”` quotes and `<br>` line breaks in table cells.
3. Where the proposal says a sentence conflicts with existing text, ADD the new sentence and leave the existing one; do not delete or reconcile.
4. Where the proposal says a target record does not exist (`NEW …`), create it at the end of the named file with the next free ID in that prefix.
5. If two blocks in the proposal target the same record, merge them under that record without dropping any sentence.
6. If a block's placement is genuinely ambiguous or its text is internally contradictory, still apply it in the most literal place and list the item under `UNCERTAIN` in your final answer. Never skip a block.
7. After editing, run `python3 scripts/validate_project_status.py` from repo root and report the `passed` value. Then run `git diff --stat -- docs/rules` and report it.

## Final answer format
- Blocks applied: N of N (count the `### ` headings in the Consolidated section).
- Files changed with line deltas.
- UNCERTAIN: list (or "none").
- Validator passed: true/false.
