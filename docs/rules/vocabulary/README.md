# Nemesis: Retaliation vocabulary proposal

This directory is the first post-extraction layer. It proposes controlled labels and source-scoped aliases while preserving every source occurrence and named component identity separately.

## Files

- `source-term-inventory.json` — 1,853 observed labels, headings, titles, source keys, and GMNotes occurrences. `normalizedKey` is editorial matching only; it is not an identity or alias assertion.
- `named-component-identities.json` — Room/card/reference/BGA-key observations grouped only by normalized exact-string equality.
- `canonical-vocabulary.json` — 50 already accepted icon-glossary terms plus 117 authority-derived canonical-label proposals.
- `alias-registry.json` — accepted explicit/source-scoped aliases, proposed aliases requiring review, and explicit non-alias guardrails.
- `vocabulary-review-gates.json` — owner decisions and evidence; VG-001 is resolved and VG-002 remains open.
- `coverage.json` — mechanical coverage and intentional non-canonicalization report.

## Authority and boundaries

FAQ/errata overrides the rulebook where applicable; the rulebook overrides official component references only at the general-rules level; exact component names and visible source variants remain traceable. TTS and licensed-digital keys are secondary.

This layer does **not** define:

- taxonomy or class hierarchy;
- ontology relationships;
- broader/narrower or part-whole relations;
- cardinalities;
- timing, choice, visibility, or state-transition semantics;
- executable effects;
- implementation mappings.

`editorialSection` is navigation only. It is not a term class.

## Alias safety

Aliases require explicit official equivalence, exact source-tuple evidence, or owner approval. They are never generalized from color, silhouette, directory, GMNotes tag, structured key, or duplicate display name.

The existing reviewed legacy artwork mappings remain restricted to the exact source tuples in `docs/qa/card-symbol-semantic-resolutions.json`.

## Current review gate

Resolved:

- `VG-001`: accepted `PERSONAL OBJECTIVE` → `Private Objective`, restricted to the exact listed TTS/prototype source tuples. Original wording and provenance remain preserved.

Still open:

- `VG-002`: `Drilling Room` → the named official component `DRILLING STATION`.

Taxonomy/ontology work must not begin until VG-002 is resolved and the vocabulary validator reports no open review gates.
