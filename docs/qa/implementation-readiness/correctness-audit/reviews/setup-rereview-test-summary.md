# Focused audit-harness test inventory

Executed with pinned `jsonschema[format]==4.25.1` through isolated `uv`.

## Structural/content mutations — 32/32 passed

1. candidate-universe tamper rejected;
2. completeness and blind reviewer reuse rejected;
3. full valid packet → completeness → blind → comparison fixture accepted;
4. duplicate JSON key rejected;
5. empty derived requirements/scenarios rejected;
6. forbidden downstream prompt token rejected;
7. incomplete packet search record rejected;
8. one-option ambiguity rejected;
9. packet path escape rejected using a temporary path;
10. semantic/conclusion field added to packet rejected by closed schema;
11. pending unit with an attached artifact rejected;
12. material discrepancy marked accepted rejected;
13. seal-order reversal rejected;
14. selection-coverage tamper rejected;
15. pass-threshold tamper rejected;
16. visual evidence without a matching SHA-256 rejected;
17. nonexistent seal Git commit rejected;
18. model-response provider/model/reasoning/prompt provenance mismatch rejected;
19. unresolved material completeness finding falsely marked accepted rejected;
20. omitted blind batch unit rejected;
21. reviewer response path without SHA-256 rejected;
22. noncanonical packet scope plus hollow evidence rejected;
23. empty actor/decision behavioral dimension rejected;
24. material discrepancy without root cause rejected;
25. authority-inversion classification without its Boolean flag rejected;
26. final non-match without independent verification rejected;
27. `..` source-allowlist traversal rejected;
28. symlink artifact path rejected;
29. blind citation outside exact packet evidence rejected;
30. comparison evidence ID outside the packet rejected;
31. behavioral non-match with `none` severity rejected;
32. `repaired-verified` without repair/evidence proof rejected.

Command outcome: `Ran 32 tests ... OK`.

## Decision-gate controls — 8/8 passed

1. unfinished audit cannot produce a decision;
2. clean 140-unit synthetic fixture passes audited units only and selects 23 deterministic clean-match reviews;
3. one critical error forces full escalation;
4. three component material errors exceed the limit;
5. one material root cause across two families is recurring;
6. one unverified deterministic clean match blocks the decision;
7. a behavioral non-match with `none` severity fails when the pure evaluator is called directly;
8. `repaired-verified` with empty proof remains unresolved when the pure evaluator is called directly.

Command outcome: `Ran 8 tests ... OK`.

## Other verified commands

- audit manifest byte regeneration: passed, 140 units;
- real Draft 2020-12 validator pre-lock: passed, 140 pending units, zero failures;
- source extraction validator: passed, zero failures;
- vocabulary validator: passed, zero failures;
- taxonomy/ontology validator: passed, zero failures;
- semantic validator: passed, zero failures;
- project-status validator: passed, zero failures;
- `git diff --check`: passed.

The full executable test sources remain in `scripts/test_correctness_audit_mutations.py` and `scripts/test_correctness_audit_decision.py`; this reduced reviewer packet omits their bodies solely to stay within reliable model context.
