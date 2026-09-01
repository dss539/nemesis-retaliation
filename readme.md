# Nemesis: Retaliation — Digital Edition

A faithful digital adaptation of the board game **Nemesis: Retaliation** by Awaken Realms.

> **CURRENT STRATEGY:** Source extraction, vocabulary, ontology, and semantic-pilot work are
> complete enough for the authorized Stage 1 blind rules correctness audit; semantic expansion and
> implementation remain frozen. Stage 1 is a simple rules derivation review:
> prioritize source fidelity, blindness, deterministic evidence, and substantive rules findings,
> then move forward. Start with [`PROJECT_STATUS.md`](PROJECT_STATUS.md).

## Source authority

Canonical game data comes from the most authoritative and up-to-date applicable official source:

1. Current official FAQ, errata, amendments, or replacement text
2. Current official rulebook and official final component references
3. Older official material, with its edition and date recorded
4. Extracted TTS assets as secondary evidence, not automatic authority
5. Explicitly labeled and approved project interpretations or adaptations

Conflicting sources are preserved as provenance. If supersession, edition, applicability, or interpretation is unclear, a human decides and the decision and evidence are recorded.

## Project layout

- `PROJECT_STATUS.md` — concise current phase, next task, blockers, and readiness gates
- `AGENTS.md` — agent-facing repository context and operating instructions
- `AGENTS-SUPPLEMENT.md` — supplemental agent documentation and note-placement practices
- `todo.md` — detailed backlog and historical checkpoints
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
- Current phase, immediate next task, blockers, and readiness gates → `PROJECT_STATUS.md`
- Detailed backlog and historical checkpoints → `todo.md`
- Agent-specific repository instructions → `AGENTS.md`; supplemental documentation practices → `AGENTS-SUPPLEMENT.md`
- TTS extraction and card-transcription procedures → `assets/tts-mod/notes/`
- Official rule interpretations and unresolved source questions → `docs/rules/`
- Test output, comparison images, source audits, and reproducible verification evidence → `docs/qa/`
- Cross-project procedures → reusable Hermes skills

Use one authoritative home for each fact and link to it elsewhere. Do not copy the same lesson into multiple catch-all files. In particular:

- `AGENTS.md` and `AGENTS-SUPPLEMENT.md` are static policy/navigation only. Never put project status, current work, TODOs, checkpoints, counts, branch state, or test results in them.
- A durable procedure learned during QA belongs in the relevant topic note; `docs/qa/` keeps only the specific evidence that established or verified it.
- A source conflict and its evidence belong in a focused source audit; a concise active blocker belongs in `PROJECT_STATUS.md`, detailed work history in `todo.md`, and a genuine rules ambiguity in `docs/rules/open-questions.md`.
- `readme.md` files are concise entry points and maps, not chronological notebooks.
- Topic notes describe reusable knowledge, not running tallies or session history.
- Historical execution detail belongs in an audit or log only when it is evidence worth retaining.

When information changes category, move it rather than copying it. Update inbound links and remove the stale version in the same change.

## Future clean implementation

The legacy implementation is frozen. A new digital adaptation will be designed from scratch only after source extraction, vocabulary/alias review, taxonomy or ontology, semantic-rule modeling, and rules-readiness audits pass—and only after explicit project-owner approval. Current state and gates are tracked in [`PROJECT_STATUS.md`](PROJECT_STATUS.md).

## Disclaimer

This is a fan-made digital adaptation. Nemesis: Retaliation is designed by Adam Kwapiński and published by Awaken Realms. All game content belongs to them.
