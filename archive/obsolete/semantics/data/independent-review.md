# Independent semantic pilot review

**Review batch:** `deleg_5167f088`
**Workstreams:** schema design, system-sequence pilots, component-effect pilots, adversarial validation

## Outcome

The representative semantic pilot is suitable for coverage expansion after the corrections below. At the time of this review, no ambiguity was silently resolved and nine semantic questions remained open with explicit alternatives and defaults prohibited. OQ-002 has since been resolved directly by current official rulebook p. 39; that later source correction does not alter the original review outcome.

## Incorporated findings

1. **Record identity/versioning:** every record now carries schema version, record type, revision, stable rule ID, implementation-neutral boundary, and immutable source-tuple projection through each source assertion.

2. **Source variants:** Search and Rest variants link to exact source assertions and source tuples. Authority resolution changes the semantic procedure without rewriting lower-authority printed wording.

3. **Question alternatives:** all open questions have evidence, at least two explicit alternatives, linked current/planned semantic records, and `defaultProhibited: true`.

4. **Pass/Turn control flow:** Pass ends the remaining Action window, not mandatory Turn-end oxygen/fire processing. A second Action is skipped after Pass; Turn-end effects remain.

5. **Player Phase rotation:** the Starting Player cursor and repeat/advance behavior are explicit rather than selecting only one Player.

6. **Movement/Exploration uncertainties:**
   - SEM-Q-002 preserves one-versus-two Noise-roll readings when Entrance Effect is Noise;
   - SEM-Q-003 preserves the missing tie-break when more than three equal-largest Opportunity Attackers qualify;
   - empty Exploration deck reshuffle and source-defined Corridor omissions are explicit.

7. **Component semantics:**
   - Search uses temporary private inspection, exact-one selection under higher-authority rulebook text, deck-bottom returns, and no reveal of unchosen Items;
   - Rest composes its source-face modifier over the official Infection Procedure while preserving Medical Support wording;
   - Duck and Cover remains a Reaction, with multi-target replacement unresolved;
   - Hatching preserves per-sentence Event continuation and Undiscovered-Nest ambiguity;
   - Queen-Alive Intruder Help includes resolved-token return lifecycle.

8. **Semantic nodes:** participation/game/outcome states, temporary zones, deck positions, and visibility scopes are separately registered instead of misusing process taxa as states.

9. **Conflict register:** seven source/semantic conflicts are tracked: two authority-resolved, three unresolved, and two preserved boundaries.

10. **Validator hardening:** strict JSON, closed record shape, IDs/revisions, source tuple digests, authority precedence, vocabulary/ontology/semantic-node references, linked alternatives, variant assertions, timing/owner/visibility/cost/target completeness, operation ordering/references, partial resolution, conflict/backlog projections, implementation leakage, and two-seed reproducibility are fail-closed.

## Deliberately not resolved

- OQ-001, OQ-003, OQ-004, OQ-007, OQ-009;
- SEM-Q-001 Duck and Cover replacement target;
- SEM-Q-002 exploratory Movement Noise count;
- SEM-Q-003 equal-priority Opportunity Attack selection.

These do not prevent encoding unrelated semantic records. They block only the affected rules/planned rules until an official clarification or project-owner decision is recorded.

OQ-002 was part of the original deferred set but is now **resolved by official source**: evaluate Larva eligibility when the endgame Eclosion cohort step is reached, including a Larva gained during the preceding Infection step. The superseded endgame-start snapshot reading is retained only in `docs/rules/open-questions.md` as resolution history.

## Gate conclusion

The pilot gate passes for **coverage expansion**, not implementation readiness. The 600-unit source-obligation backlog intentionally retains overlaps and variants; only 17 source obligations are pilot-covered and one exact source remains blocked.
