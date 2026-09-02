# Archived semantic layer — obsolete, not live

**Archived 2026-09-02 by owner decision.** This directory is a trash heap of
history, not a working layer. Nothing here is live, maintained, or authoritative.

## Why it was archived

- The Search→Item proof-of-value pilot (`docs/qa/implementation-readiness/search-pilot/`)
  failed the unique-utility gate: every verified semantic contribution reduced to a
  short source-linked rule plus a focused scenario. The pilot also documented
  semantic records hiding a real source wording conflict and missing a boundary.
- The owner decided the rewrite will consume the concise Markdown rules corpus
  (`docs/rules/00-04 *.md`), not this semantic projection.
- The 2026-09-02 fragment-coverage audit confirmed concise-corpus gaps (e.g. ARM/EYES
  Serious Wound effects) that the semantic layer's existence would have masked.

## What is here

- `data/` — the 26-file semantic corpus: schema, pilots, source indexes,
  contradictions, coverage, backlog, review gates, validation.
- `scripts/` — the 34 builders/validators/tests that generated and checked it.

## Rules

- Do not extend, rebuild, validate, or "repair" anything here.
- It may be consulted as a historical finding aid during concise-corpus repair;
  its claims are NOT authoritative and must be re-verified against raw source.
- The semantic validation previously enforced by `validate_project_status.py`
  was removed with the archive. Its counts are preserved in Git history.