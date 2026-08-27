# Search implementation-readiness pilot — result

## Verdict

- **H1 compact-contract sufficiency: PASS for this slice.**
- **H2 unique semantic utility: FAIL for this slice.**
- **Recommendation:** keep semantic expansion frozen. Retain the existing corpus as audit/provenance/reference material, but do not expand or use its large JSON shape as the rewrite specification.

This is a slice-scoped result, not proof that every semantic record is wrong or useless.

## Executed evidence

- 22 Node acceptance tests pass.
- 17/17 mutations are killed:
  - all preregistered M01–M14;
  - adversarial additions M15–M17 for Fully Loaded allocation, compatibility, and finite supply.
- Reference module plus acceptance and mutation tests: exactly 800 physical lines / 744 nonblank lines.
- No production file under `js/` imports or uses the reference module.
- Frozen semantic hashes remained unchanged throughout the pilot.
- `deepseek-v4-pro:0813` rejected the initial Event methodology and the first Search implementation; verified findings were fixed.
- `glm-5.3-flash` supplied the blind raw-source baseline without semantic-corpus access.

## Layer comparison

| Candidate semantic contribution | Independent evidence | Implementation effect | Utility-gate result |
|---|---|---|---|
| Draw one card per icon; corresponding deck-bottom returns | Raw rulebook, GLM baseline, concise ACT-SEARCH | Kills M01–M03 | Duplicate; compact rule/test sufficient. |
| Exact occurrence identity rather than title | Locked source indexes; preregistered scope | Kills faithful same-title M05 | Useful provenance discipline, but one stable `itemId` contract is sufficient. |
| Unchosen/candidate secrecy | Raw rulebook and `SEM-ACT-SEARCH-001` | Kills M04 | Compact public/private event assertion is sufficient. |
| Exactly-one keep | Semantic record chooses 1; rulebook says pick 1 while card says may keep 1 | Kills M13 only after an explicit interpretation policy | Semantic record hides a real source wording conflict; not unique verified value. |
| Empty-deck handling | Semantic `SEM-Q-040`; GLM A-1; component-limit and full-resolution rules | Kills M12 by returning typed unresolved state | Already visible without the large schema. |
| Regular/Heavy/Armor storage | Raw rulebook, blind baseline, concise Item rules, semantic lifecycle records | Kills M06–M10 | Duplicate; compact storage functions/tests sufficient. |
| Discarded Item destination | Semantic generic discard record helped locate omitted raw lines 3665–3673 | Kills M14 | Helpful as an index, but one compact source rule supplies the same protection. |
| Fully Loaded slot compatibility and finite supply | Raw lines 3543–3548/4899–4904/5058–5078; concise ITM-005; semantic equipment record | Kills M15–M17 | Cross-cutting discovery was useful, but the concise corpus already contained it and compact tests suffice. |
| Same-deck bottom-return order | Found by DeepSeek review | Produces typed A-9 gap | Missing from the frozen semantic Search record; evidence against completeness. |

No candidate met all four unique-utility criteria. The semantic layer sometimes made source discovery faster, but every verified benefit reduced to a short source-linked requirement or scenario. Several important boundaries were absent, under-cited, or over-resolved in the semantic projection.

## Concise-corpus correction

The pilot also falsified stale `ITM-003/004` claims that color Item decks contain only Regular Backpack cards. Locked Green/Red/Yellow source indexes preserve Heavy and class-conflict occurrences. The concise rules now separate color/source family from physical class and dispatch storage by exact occurrence.

This confirms that the human-readable corpus also needs independent source auditing; readability does not guarantee correctness.

The deterministic semantic backlog was regenerated after the experiment to project the two corrected ITM-003/004 labels. This was maintenance only: all 600 IDs, source locators, statuses, rule links, and aggregate counts remained unchanged; no semantic record, question, builder, validator, or preregistered frozen hash changed.

## What to retain

- source inventory, hashes, rendered visual evidence, and component transcription;
- authority/version boundaries;
- exact occurrence IDs and provenance;
- concise source-backed rules;
- open questions and conflicts;
- focused executable acceptance scenarios and mutations.

## What to stop

- new 300-line-per-rule JSON records;
- family-specific semantic projections without a consumer;
- validators that primarily prove generated artifacts match their own builders;
- treating backlog coverage percentage as implementation readiness.

## Next gate

Before a clean rewrite is authorized:

1. run a stratified blind correctness audit over critical subsystems and a random sample of component effects;
2. repair confirmed concise-rule defects and preserve unresolved source policy;
3. derive compact acceptance contracts during implementation, not as another complete parallel rules engine;
4. choose architecture independently of the legacy implementation and frozen semantic representation;
5. obtain explicit project-owner approval to begin the rewrite.

No deletion, rewrite, merge, push, PR, deployment, profile, config, or service change was performed.
