# Independent taxonomy/ontology review

**Review batch:** `deleg_0cdda6e9`
**Workstreams:** taxonomy classification, static relationship audit, ambiguity audit, validator/adversarial audit
**Scope:** read-only review of the approved vocabulary and initial ontology proposal

## Outcome

No project-owner decision blocks the static ontology. The review did find material design and validation defects, all corrected before the ontology gate was considered reviewable.

## Incorporated corrections

1. **Three levels are explicit:**
   - exact source occurrence;
   - component definition/component-set definition;
   - physical component copy/runtime entity.

   Exact strings, definitions, and copies are not `sameAs` and are connected only by explicit provenance/realization relations.

2. **Process taxonomy category errors fixed:**
   - Reaction is not an Action;
   - generic Attack and Opportunity Attack are not player Actions;
   - Shoot/Burst/Melee are both player Action types and attack processes;
   - Search is an Action-card effect, not a universal Basic Action;
   - Repel is an effect operation, not a universal Action.

3. **State/identity distinctions fixed:**
   - Section A/B/C and named special Rooms are identity kinds, not inferred universal subclasses;
   - Survivor is a participation/endgame state;
   - Escape and Hibernate retain both process and resulting-state denotations;
   - Empty Corridor means no Intruders; a Noise marker does not make it non-empty.

4. **Missing source-backed static edges added:**
   - Map ↔ Facility;
   - Section ↔ Facility;
   - Corridor ↔ one/two Sections;
   - Door ↔ Room boundary;
   - source occurrence ↔ component definition;
   - component copy ↔ definition and component set;
   - Room Help entry ↔ Room definition;
   - Action deck ↔ Character role;
   - printed icon occurrence ↔ component definition;
   - Room definition ↔ printed Section designation.

5. **Semantic relations deferred:** twelve timing/order, Turn/Phase, decision-owner, visibility, and lifecycle-transition relation IDs are reserved but absent from the static ontology. Their classes remain as scaffolding; actual relations and assertions belong to semantic modeling.

6. **Open-question cleanup:** former extraction blockers for Rest, Intruder Help, Not-in-Combat associations, and Action-deck inventory were resolved. OQ-001, OQ-002, OQ-003, OQ-004, OQ-007, and OQ-009 remain semantic/source questions and do not block static ontology.

7. **Validator hardening:**
   - strict duplicate-key JSON parsing;
   - independently locked root set;
   - sorted/unique parent, domain, and range sets;
   - acyclicity and disjointness symmetry;
   - exact controlled-term and named-identity projections;
   - accepted-alias projection closure;
   - inverse domain/range/transitivity checks;
   - nonnegative structured cardinalities;
   - source-path and assertion-reference closure;
   - forbidden semantic field/relation checks;
   - two independent rebuilds under different hash seeds/locales;
   - corruption negative controls for all high-risk contract classes.

## Gate conclusion

The static taxonomy/ontology may pass without an owner question after these corrections and deterministic validation. This does **not** authorize semantic effect modeling automatically; the next layer must carry the six genuine semantic questions explicitly and model timing, decisions, visibility, and lifecycle transitions without guessing.
