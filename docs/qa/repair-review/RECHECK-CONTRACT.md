# Re-check contract (post-repair, one pass, no loops)

You are the single allowed post-repair re-check for a list of repaired fragment IDs. The corpus was just edited and committed; read it FRESH from disk now — do not rely on anything you remember.

## Inputs
- ID list file (given in your task).
- For each ID: fragment `audit/repair/<ID>.txt`, sidecar `audit/repair/<ID>.repair.md`.
- Corpus: `docs/rules/00-foundations.md`, `01-round-and-turns.md`, `02-character-actions.md`, `03-intruders-and-survival.md`, `04-items-and-equipment.md`, `icon-glossary.md`, `open-questions.md`.

## Per ID
Ask exactly one question: "Is the operative assertion in this fragment now fully and accurately captured by settled concise-corpus text?" Answer `covered` (cite file + record ID + the sentence) or `not-covered` (state exactly what is still missing or wrong). An `open-questions.md` mention alone is never `covered`. A source-variant row that reproduces the fragment's text verbatim in a corpus occurrence table IS coverage for that variant.

## Output
Write ONLY the file named in your task (under `docs/qa/repair-review/recheck/`). Format, one line per ID:
`<ID> | covered | <file>#<record> | <short evidence>` or
`<ID> | not-covered | <what is missing>`
End with `Total: N. Covered: N. Not-covered: N.`

Do not edit audit/, docs/rules/, or anything else. Do not move files. No /tmp, no scripts.
