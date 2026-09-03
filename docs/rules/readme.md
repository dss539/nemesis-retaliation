# Nemesis: Retaliation — Rules Interpretation Corpus

## Purpose

This corpus is the project’s human-readable, semi-formal interpretation of the official *Nemesis: Retaliation* rules. It bridges the publisher’s natural-language rulebook and FAQ with unambiguous game behavior.

It is not a replacement rulebook and does not claim legal or publishing authority. The official publications remain the primary sources.

## Authority and precedence

For a rule conflict, use this order:

1. Official FAQ/errata applicable to the question.
2. Official rulebook.
3. A documented project interpretation in this corpus.
4. A documented digital adaptation or simplification in `deviations.md`.
5. An unresolved issue, which must not silently become a rule.

The current application is evidence of existing behavior only. It is not authority for what the game rule should be.

## Reading a rule record

Each record uses the following fields:

- **Rule ID** — stable identifier for discussion, scenarios, and future traceability.
- **Source** — official document and page/section; extracted-text lines may be supplied as a locator aid.
- **Plain rule** — concise human statement.
- **Applies when** — explicit conditions and timing.
- **Procedure** — ordered resolution.
- **Exceptions / clarifications** — stated overrides or scoped limits.
- **Invariant** — a condition that must remain true whenever the rule applies, if useful.
- **Examples** — Given / When / Then applications.
- **Open interpretation** — ambiguity intentionally left visible pending an authoritative source or project decision.

The wording “must,” “may,” and “cannot” is deliberate:

- **must**: required resolution;
- **may**: a player choice or permitted option;
- **cannot**: forbidden outcome;
- **if able**: resolve only if the stated condition can be met.

## Corpus map

- `00-foundations.md` — scope, terminology, relevant finite setup supplies, Room geometry, Corridor spacing/extent, and cross-cutting conventions (FND-001–006).
- `01-round-and-turns.md` — round sequence, phases, turns, pass, actions, cleanup, death, endgame triggers (RT-001–015, 7 examples).
- `02-character-actions.md` — all player action procedures: move, explore, search, shoot, burst, melee, trade, doors, noise, plus Action card identity (ACT-*-001, ACT-CARD-001–002, 8 examples).
- `03-intruders-and-survival.md` — intruder bag, movement, attacks, health, contamination, eclosion, escape, endgame resolution (INT-001–011, 6 examples).
- `04-items-and-equipment.md` — source-backed Item physical classes, source families, storage, Tactical Gear, and Item Icons (ITM-001–008).
- `deviations.md` — deliberate digital adaptations only; currently one recorded proposal. Implementation bugs never belong there.
- `open-questions.md` — source ambiguities and resolved former extraction/vision questions; semantic no-default gates are enumerated authoritatively in the archived `archive/obsolete/semantics/data/review-gates.json` (historical reference; verify against raw source before relying on any record).
- `sources.md` — source editions and citation conventions.
- `vocabulary/` — approved controlled terms, aliases, source-term inventory, named identity observations, and validation.
- `ontology/` — independently reviewed taxonomy/ontology, complete vocabulary/identity/alias mappings, static relationship shapes, constraints, and validation.
- `archive/obsolete/semantics/` — the former semantic layer, archived as obsolete 2026-09-02; historical reference only, never a live authority.

## Vocabulary proposal

The post-extraction controlled-term proposal is under `docs/rules/vocabulary/`. Start with `vocabulary/README.md`.
It currently contains source-term evidence, named identity observations, 167 canonical-label entries, source-scoped aliases,
coverage, validation, and two owner-review gates. It deliberately contains no taxonomy, ontology, or semantic-effect model.

## Rule ID conventions

- FND-### — foundations and conventions
- RT-### — round, phase, and turn rules
- ACT-NAME-### — character action rules
- ACT-CARD-### — Action card object rules (distinct from Basic Actions)
- INT-### — intruder and resolution-critical system rules
- EX-TYPE-### — worked examples
- KNOWN-DEV-### — known deviations from official rules
- MAP-ADAPT-###, NEST-ADAPT-###, DISCONNECT-### — intentional digital adaptations
- OQ-### — open questions

## Coverage discipline

A rule enters the corpus only when it has a source citation or is explicitly labeled as a project decision. When source text is ambiguous, preserve the ambiguity and add an open question rather than inventing a definitive mechanic.

Extraction, controlled vocabulary, and static ontology gates are passed. The existing implementation-neutral semantic corpus is frozen at 529 records / 530 covered obligations while its practical value is tested. The Search → Item gain proof-of-value is complete: compact source-linked tests passed, while unique semantic implementation utility was not demonstrated. Semantic expansion remains frozen at the owner gate; no production work is authorized. See `implementation-readiness.md`.
