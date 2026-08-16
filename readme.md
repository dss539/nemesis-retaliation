# Nemesis: Retaliation — Digital Edition

A faithful digital adaptation of the board game **Nemesis: Retaliation** by Awaken Realms.

> **STATUS (2026-08-09):** The inaccurate first-pass implementation is archived under
> `archive/obsolete/`. The project is being rebuilt from canonical sources.

## Source authority

Canonical game data comes from the most authoritative and up-to-date applicable official source:

1. Current official FAQ, errata, amendments, or replacement text
2. Current official rulebook and official final component references
3. Older official material, with its edition and date recorded
4. Extracted TTS assets as secondary evidence, not automatic authority
5. Explicitly labeled and approved project interpretations or adaptations

Conflicting sources are preserved as provenance. If supersession, edition, applicability, or interpretation is unclear, a human decides and the decision and evidence are recorded.

## Project layout

- `AGENTS.md` — agent-facing repository context and operating instructions
- `AGENTS-SUPPLEMENT.md` — supplemental agent documentation and note-placement practices
- `todo.md` — current work, blockers, and gates
- `assets/tts-mod/readme.md` — TTS asset workspace entry point and current status
- `assets/tts-mod/notes/` — topic-specific extraction and card-transcription knowledge
- `assets/tts-mod/extract/` — source save, parsed metadata, and downloaded assets
- `docs/rulebooks/` — official PDFs and extracted text
- `docs/rules/` — source-backed rule interpretation, open questions, bugs, and declared deviations
- `docs/qa/` — verification evidence, test results, screenshots, and audit reports
- `archive/obsolete/` — archived first-pass implementation; reference only

## Documentation placement

Write durable documentation when new reusable knowledge, a decision, a blocker, or meaningful project state actually exists. Do not create or duplicate notes merely because a session occurred.

- Project overview and navigation → this `readme.md`
- Current tasks, blockers, and approval gates → `todo.md`
- Agent-specific repository instructions → `AGENTS.md`; supplemental documentation practices → `AGENTS-SUPPLEMENT.md`
- TTS extraction and card-transcription procedures → `assets/tts-mod/notes/`
- Official rule interpretations and unresolved source questions → `docs/rules/`
- Test output, comparison images, source audits, and reproducible verification evidence → `docs/qa/`
- Cross-project procedures → reusable Hermes skills

Use one authoritative home for each fact and link to it elsewhere. Do not copy the same lesson into multiple catch-all files. In particular:

- A durable procedure learned during QA belongs in the relevant topic note; `docs/qa/` keeps only the specific evidence that established or verified it.
- A source conflict and its evidence belong in a focused source audit; any still-open decision belongs in `todo.md` or `docs/rules/open-questions.md`, depending on whether it is a work gate or a rules question.
- `readme.md` files are concise entry points and maps, not chronological notebooks.
- Topic notes describe reusable knowledge, not running tallies or session history.
- Historical execution detail belongs in an audit or log only when it is evidence worth retaining.

When information changes category, move it rather than copying it. Update inbound links and remove the stale version in the same change.

## Planned implementation

The digital adaptation will be rebuilt from the canonical sources above. Current priorities and approval gates are tracked in [`todo.md`](todo.md).

## Disclaimer

This is a fan-made digital adaptation. Nemesis: Retaliation is designed by Adam Kwapiński and published by Awaken Realms. All game content belongs to them.
