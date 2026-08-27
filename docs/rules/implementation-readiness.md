# Rules-layer implementation readiness

## Current decision

**Semantic coverage expansion is frozen.** The source extraction, provenance, vocabulary, ontology, and existing 529 semantic records remain immutable evidence during the readiness experiment. No additional semantic families or records should be added until the project owner reviews a measured proof-of-value result.

This freeze does not discard the rules work. It separates three claims that were previously conflated:

1. the sources were captured faithfully;
2. the rules interpretation is correct;
3. the large semantic representation materially improves implementation.

The source-extraction gate has evidence for claim 1. Claims 2 and 3 require separate testing.

## Active method

Use a **compact, source-linked executable contract plus acceptance scenarios** for one difficult vertical slice. Compare it against:

- raw official sources;
- a blind baseline derived without the semantic corpus;
- the concise Markdown rules;
- the frozen semantic records.

Pre-register the hypotheses, defects, metrics, and stop conditions before writing the executable contract. Preserve unresolved source policy as an explicit blocked result rather than inventing a convenient implementation default.

## First pilot

The first slice is **Search Action-card resolution through Item gain/storage**. It was selected instead of generic Event resolution because it exercises:

- Action legality and lifecycle;
- random draws from multiple finite decks;
- exact physical occurrence identity;
- player-owned selection;
- hidden candidate and Backpack information;
- deck-bottom return to the corresponding deck;
- regular, Heavy, and Armor storage dispatch;
- optional displacement decisions;
- source conflict and unresolved exhaustion/storage timing.

The executable artifact is a disposable reference contract outside `js/`. It must not be imported by the current or future production engine.

Detailed preregistration and review evidence: `docs/qa/implementation-readiness/search-pilot/`.

## Readiness gates

### Correctness gate

A pilot passes correctness only if:

- every implemented behavior has a raw official-source citation;
- every source omission or conflict is represented as unresolved rather than defaulted;
- every pre-registered production-relevant mutation is rejected by a focused acceptance test;
- the reference implementation is deterministic and leaves source/semantic artifacts unchanged;
- adversarial findings are dispositioned against source and executed evidence.

### Semantic utility gate

The large semantic projection demonstrates unique implementation utility in this pilot only if all are true:

1. it contains an implementation-relevant requirement or ambiguity absent from both the locked blind baseline and concise Markdown corpus;
2. that contribution is verified directly against raw official source;
3. translating it into an acceptance test kills a pre-registered or independently proposed production-relevant defect;
4. the same benefit cannot be obtained more simply by adding one compact source-linked requirement or scenario.

Provenance richness, deterministic regeneration, or restating English as JSON does not by itself pass this gate.

### Complexity gate

- No production implementation changes.
- No changes to semantic JSON, builders, validators, vocabulary, or ontology.
- Reference implementation plus focused tests must remain at or below 800 non-generated lines.
- Total pilot-specific code, tests, contracts, and reports must remain below 1,500 non-generated lines, excluding verbatim external-review evidence.
- No new general schema, ontology, rule language, or reusable framework may be introduced by the pilot.

### Decision boundary

A passed pilot does not authorize the rewrite or further semantic expansion. It yields a source-backed recommendation for the project owner. A failed utility gate freezes further semantic projection work while retaining useful extraction, provenance, questions, conflicts, and concise rules.

## Adversarial review protocol

Use isolated reviewers at meaningful checkpoints:

1. before implementation, attack pilot selection, hypotheses, and stop conditions;
2. derive one baseline blind to the semantic corpus;
3. after implementation, attack source fidelity, test strength, and mutation coverage;
4. verify reviewer findings independently before changing artifacts.

Model diversity is useful for finding blind spots but is not human-independent validation. Record the exact model tag, supplied evidence boundary, finding, disposition, and verification result.

## First-pilot outcome

The Search → Item gain pilot is complete. The compact contract passed 22 acceptance tests and killed 17 mutations within the 800-line cap. The semantic utility gate failed for this slice: no verified semantic contribution provided implementation protection that could not be replaced by a short source-linked rule and focused scenario. Semantic expansion remains frozen pending the project-owner gate.

Detailed result: `docs/qa/implementation-readiness/search-pilot/utility-report.md`.

## Proposed correctness audit after the owner gate

Do not audit all 529 semantic records. They are frozen reference evidence, not the proposed implementation specification.

### Stage 1 — 140-unit decision audit

Audit blindly against original sources:

- all **56 concise rule records** across foundations, rounds/turns, actions, intruders/survival, and Items;
- all **28 base-applicable FAQ units**;
- **56 stratified component effects**: 5 Rooms, 4 Intruder Help rows, 4 Events, 3 Exploration cards, 2 Robots, 2 Intruder Attacks, 2 Queen Health faces, 2 Serious Wounds, 6 Green/Red/Yellow Item faces, 12 Action cards, 6 Objectives/Mission Tasks, and 8 Equipment/Starting Item faces.

The 115 open questions and 88 conflicts are triaged through the affected audited clauses; they are not 203 additional independent audit units.

Stage 1 may pass without expansion only if it finds zero critical errors, zero invented authority overrides, zero hidden defaults, no recurring defect pattern, and at most two isolated material errors in the component sample.

### Escalation boundary

If Stage 1 finds a critical or recurring problem, expand the affected family. Escalate to the full audit only when defects appear systemic. The full base competitive planning inventory is approximately **339 primary units**: 84 core rule/FAQ units plus 255 distinct gameplay/component effects. Byte-identical copies need mechanical reconciliation, not redundant semantic review; source-different same-title occurrences remain separate.

Solo/Coop and expansions remain outside initial rewrite readiness unless the owner changes scope.
