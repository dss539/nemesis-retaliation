# Search pilot adversarial-review disposition

## Review lanes

| Checkpoint | Model | Evidence boundary | Outcome |
|---|---|---|---|
| Pilot design | `deepseek-v4-pro:0813` | Proposed generic Event pilot and gate | Rejected as too trivial/circular; accepted. Pilot changed to Search → Item gain with preregistration and mutation testing. |
| Blind baseline | `glm-5.3-flash` | Supplied raw Search/Item excerpts only; semantic corpus withheld | 12 requirements, 8 candidate ambiguities, 9 scenarios. One ambiguity (A-8) was later disproved because the source packet omitted rulebook lines 3665–3673. |
| First implementation | `deepseek-v4-pro:0813` | Preregistration, raw-source summary, reference module, acceptance tests, mutation harness | Rejected with 10 findings and 4 must-fix findings. All findings were independently checked below. |

Model diversity is a blind-spot aid, not human-independent validation.

## DeepSeek code-review findings

| ID | Disposition | Verified action |
|---|---|---|
| F-1 | **Accepted** | Failed Armor gain now bypasses the non-Backpack visibility policy, goes to the Items discard pile, and does not expose the discarded identity. Added a focused test. |
| F-2 | **Accepted** | `action-card-revealed` is now the first persisted public event on successful resolution, before Item gain/storage events. |
| F-3 | **Accepted** | Added source gap A-9 for multiple unchosen cards returning to the same deck bottom. Zero-keep/multi-return requires an explicit ordering policy. |
| F-4 | **Accepted** | Non-Backpack visibility accepts only `public` or `owner-private`; invalid values are rejected. |
| F-5 | **Accepted** | Item Tactical Gear slot data must be an explicit array; absent/invalid data is rejected rather than treated as zero. |
| F-6 | **Not accepted as a defect** | A Room with zero Item icons cannot complete the source-required keep step. Rejecting Search follows the official “resolve entirely or do not choose” rule; no permissive zero-icon policy was added. |
| F-7 | **Accepted** | Result trace now separates applied sources from finite-component text consulted for unresolved exhaustion policy. |
| F-8 | **Accepted** | M05 now compares duplicate titles while still receiving a valid occurrence ID; it chooses the wrong same-title occurrence and is killed by the test, rather than failing on an input-type mismatch. |
| F-9 | **Accepted** | Successful results now record keep-cardinality, same-deck return-order, and non-Backpack visibility interpretations. |
| F-10 | **Accepted** | Not In Combat remains an illegal no-mutation result without attaching the unrelated A-6 gap. |

## Additional cross-layer finding

The frozen semantic comparison exposed a cross-cutting Fully Loaded rule that the first executable draft represented only as a count. Direct sources and concise `ITM-005` require exact slot compatibility and finite Tactical Gear supply; Any-slot allocation and shortages still lack complete ordering/ownership policy.

Corrections:

- explicit slot-type arrays;
- explicit token allocation for filled slots;
- compatibility validation;
- finite token-pool decrement;
- A-10 unresolved result for missing allocation/shortage;
- post-prereg mutations M15 (invent allocation), M16 (ignore compatibility), and M17 (ignore finite supply).

## Source-packet correction

The blind GLM baseline remains unchanged. Its A-8 ambiguity is classified as an input-omission artifact because rulebook lines 3665–3673 explicitly place discarded Items in the Items discard pile. M14 now mutates that source-defined destination to a wrong deck-bottom destination.

## Verification boundary

Every accepted finding has a focused test or mutation control. The model outputs are preserved verbatim as final structured answers under this directory; hidden reasoning was neither retained nor used. No reviewer edited repository files.
