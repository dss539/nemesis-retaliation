# Rules-layer implementation readiness

## Current decision

**Semantic layer — archived as obsolete (2026-09-02).** The former semantic projection failed its proof-of-value gate and was moved to `archive/obsolete/semantics/` by owner decision. It is historical reference only: do not extend, rebuild, or validate it, and verify any of its claims against raw source before relying on them. The rewrite will consume the concise Markdown rules corpus (`docs/rules/00-04`).

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

## Owner's fragment-coverage review (2026-09-01)

On 2026-09-01 the project owner scrapped the previously authorized Stage 1 v2 blind correctness-audit methodology; its harness, scripts, packets, and review evidence were removed from this repository in the same change and must not be rebuilt. The frozen semantic records remain reference evidence and are not the implementation specification.

The replacement is the owner's own methodology:

> Break down source artifacts into small pieces and hand that piece to a child.
> Ask: "are the rules and behavior documented in this fragment fully and
> accurately captured already?"

No execution machinery exists for it yet. A concrete design — fragment definition and size, artifact order, child protocol, and how yes/partial/no answers are recorded — requires owner approval before build-out and must stay proportional to that single question. The 115 open questions and 88 preserved conflicts remain no-default. Solo/Coop and expansions remain outside rewrite readiness unless the owner changes scope.
