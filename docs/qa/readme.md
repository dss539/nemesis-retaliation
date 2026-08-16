# QA Evidence

This directory contains reproducible verification artifacts for the project:

- test scripts and machine-readable results
- audit reports and action logs
- screenshots and visual comparisons
- source-fidelity evidence tied to a specific finding
- regression fixtures and focused verification records

Operational procedures and general lessons do not belong here. Put TTS extraction and card-transcription knowledge under `assets/tts-mod/notes/`, official rule interpretation under `docs/rules/`, project state in `todo.md`, and cross-project procedures in reusable Hermes skills.

A QA report may explain its method and conclusion, but it should remain evidence for a specific verification event rather than becoming a catch-all notebook.

Use focused subdirectories for related evidence (for example, `card-source-audits/` and
`card-icon-comparisons/`) instead of accumulating asset-specific reports at the QA root. If a QA
finding creates a reusable operating rule, link from the relevant topic note to the evidence; do
not duplicate the operating rule here.
