# Stage 1 blind correctness audit method

## Scope and decision

This audit tests whether the compact base-competitive rules layer is correct enough to support a clean rewrite. It does not revive semantic expansion and does not authorize implementation.

The locked population contains exactly 140 audit units:

- all 56 concise rules in `docs/rules/00-foundations.md` through `04-items-and-equipment.md`;
- all 28 FAQ v1.2 units already classified as base-applicable, including one `base-game-additional-mode` applicability-boundary unit;
- 56 deterministically selected component effects across every preregistered family.

The existing 529 semantic records are comparison/reference evidence only. They remain frozen and are withheld from blind derivation.

A Stage 1 pass applies **only to the 140 audited units**. The sample is not a probability sample and cannot establish a defect-rate bound for the approximately 199 unaudited primary component-effect units in the current ~255-unit planning inventory.

## Frozen selection and external lock

`scripts/build_correctness_audit_manifest.py` ranks component candidates by:

```text
SHA-256(seedMaterial | stratum | sourceIdentity)
```

The lowest required ranks are selected. Byte-identical physical copies form one effect candidate; source-different occurrences remain separate candidates. `manifest.json` pins:

- selected identities and source hashes;
- all selection-input hashes, including the FAQ PDF;
- all five concise-rule file hashes;
- frozen semantic artifact hashes;
- exact family, candidate-universe, eligibility, and selected counts;
- pass thresholds and the limited claim scope.

Deterministic rank prevents outcome-driven choice **inside declared strata**; it does not prove that the strata are unbiased. Therefore `selectionCoverage` exposes every stratum's eligible and selected counts. Known limits are explicit:

- Intruder Help samples one row from each caller context, including the bottom row.
- Intruder Attack samples two of twenty source occurrences and is not guaranteed to contain two variants of one title.
- Two of eight Equipment/Starting Item slots are reserved for known-hard source/class boundaries.

After setup validation, the harness is committed once, then `audit-lock.json` is committed separately. It binds the manifest and immutable harness files to the baseline commit. The validator verifies that the starting HEAD and baseline remain ancestors, immutable file bytes equal the baseline, and the lock has no uncommitted drift. Any change requires a new audit version and an explicit disposition of the old audit.

## Lane A — sealed source-only packet

Each bounded batch receives a packet conforming to `source-packet.schema.json`. The scope is the constant `base-competitive-stage1`; authority and document roles use closed source-local enums rather than free-form conclusions. The closed schema permits only:

- exact official rulebook/FAQ source files and locators;
- rendered official visuals;
- exact source-bound component faces or literal transcriptions;
- authority, version, base-scope, search, and exclusion metadata;
- neutral audit IDs and source-local printed labels.

Allowed evidence paths are mechanically restricted to:

- `docs/rulebooks/`;
- `docs/rules/source-extraction/`;
- `assets/tts-mod/extract/`.

Every path must be canonical repository-relative POSIX syntax: no absolute path, `.`/`..` segment, backslash normalization, or symlink component is accepted. Allowlisting is evaluated against the resolved allowed root, not by lexical prefix.

Concise-rule files, semantic projections, conflict dispositions, physical-class conclusions, and implementation files are not valid packet evidence. Source indexes may help the supervisor locate original bytes but are not transmitted as blind evidence.

Every packet records nonempty:

- searched source files and hashes;
- exact included locators;
- search terms;
- neighboring sections checked;
- component/visual channels checked;
- exclusions and their reasons;
- applicable FAQ units checked, where any exist.

A separate source-only critic reviews the packet under `packet-completeness-review.schema.json`. The validator reconciles every unresolved material/critical finding against `unresolvedMaterialFindingIds`; `accepted` must be false whenever that set is nonempty. The packet is eligible for derivation only when the review is accepted and has no unresolved material finding. The packet and completeness review carry hashes, UTC seal times, and Git HEADs.

A mechanical field allowlist is appropriate; an n-gram ban is not. Official text may legitimately overlap concise wording because concise rules quote official sources. The protection is source-path provenance, a closed packet schema, an isolated prompt, and a separate completeness review—not lexical suppression of authoritative text.

## Lane B — separately sealed blind derivation

An isolated reviewer receives only the accepted packet, neutral instructions, and the closed blind output contract. The exact prompt is retained under `packets/` with its SHA-256. It may not contain downstream rule paths, semantic paths, or conclusion fields.

`blind-derivation.schema.json` requires one returned result per submitted unit, in the same order. A source-derived unit must contain at least one cited requirement and one cited acceptance scenario. Every blind citation must exactly match a source-path/locator tuple in packet evidence assigned to that unit. A blocked unit must state the blocker instead of inventing a rule. Every unresolved point records at least two alternatives and `defaultProhibited: true`.

The reviewer derives:

- trigger, applicability, preconditions, and timing;
- actor, decision owner, targets, cardinality, and decline rights;
- public/private/transient/hidden visibility;
- costs and ordered operations;
- finite-supply, impossible-instruction, and partial-resolution behavior;
- exact authority and citations;
- unresolved alternatives with no default;
- implementation-focused acceptance scenarios.

Every behavioral dimension is nonempty in a derived requirement. When a dimension genuinely does not apply, the reviewer records an explicit source-supported `not applicable` statement instead of leaving the field empty.

The blind file is physically separate from all post-reveal comparison files. It is hashed before Lane C begins and is never rewritten. Packet, completeness-review, prompt, model response, and blind hashes remain independently addressable.

## Lane C — reveal and comparison

Only after Lane B is sealed may a different comparator inspect:

- the concise rule or FAQ projection under audit;
- relevant frozen semantic records;
- relevant semantic questions and conflicts;
- direct primary sources needed to verify a claimed mismatch.

`audit-result.schema.json` is a post-reveal contract containing only a hash reference to the sealed blind file. It cannot rewrite blind requirements.

Every comparison contains one or more classified rows:

- `match`;
- `downstream-omission`;
- `downstream-overstatement`;
- `authority-inversion`;
- `hidden-default`;
- `source-ambiguity-preserved` or `source-ambiguity-lost`;
- `source-conflict-preserved` or `source-conflict-flattened`;
- `transcription-or-packet-gap`;
- `presentation-only`.

Material and critical discrepancies require a stable `rootCauseId`. Authority inversions and hidden defaults have mandatory Boolean flags and critical severity. `match` requires `none`; behavioral omission/overstatement/lost-ambiguity/flattened-conflict/packet-gap classes cannot use `none`; preserved ambiguities/conflicts and presentation-only rows retain their bounded non-defect severities. Every comparison and verification evidence reference must resolve to the sealed source packet. The validator derives status consistency from the discrepancies, so a material result cannot be marked accepted.

`repaired-verified` is not a label-only escape. It requires at least one canonical repair path present in the sealed Git commit plus at least one known packet/verification evidence reference. `not-required` and `pending` carry no repair proof; a source-blocked resolution carries verification evidence but no repair path.

## Lane D — independent verification

A reviewer different from both the blind reviewer and comparator checks direct source evidence for:

- every critical, material, blocked, minor, and presentation-only discrepancy;
- every preserved ambiguity or conflict disposition;
- a deterministic sample of otherwise clean matches.

The match sample is locked by `SHA-256("nemesis-stage1-lane-d-match-v1|" + auditUnitId)`:

- six clean concise-rule matches;
- three clean FAQ matches;
- one clean match from each of the fourteen component families.

If a stratum has no clean accepted match, its defect is already independently reviewed and no substitute conclusion is inferred. `evaluate_correctness_audit.py` prevents a final pass while a selected clean match lacks verification.

GLM 5.3 and DeepSeek V4 Pro 0813 may be used as isolated advisors/critics through Ollama Cloud with `think: "max"`. Record exact requested/response tags, provider, request mode, prompt/response hashes, and final answer. Never retain `message.thinking` or another reasoning trace. Model findings remain advisory until checked against files or primary sources.

## Reviewer batching

Several units may share one call only when:

- every submitted unit ID is returned exactly once and in order;
- no result merges evidence across unrelated units;
- packet and prompt hashes are common and recorded;
- omitted, malformed, or cross-contaminated units are retried independently;
- source-family batching does not expose downstream conclusions.

Component visuals are read only through the verified native Sol Max workflow when a fresh visual read is needed. Existing independently validated source-bound transcriptions may be supplied, but their literal/source role must remain explicit.

## Severity and recurring patterns

### Critical

A source-supported discrepancy capable of changing legality, death/survival, victory, secrecy, actor-owned choice, irreversible timing, authority precedence, finite-supply behavior, or a mandatory no-default boundary.

### Material

A source-supported behavioral discrepancy likely to change state or player options without meeting the critical definition.

### Minor

Citation, terminology, or presentation drift that does not change behavior, visibility, timing, ownership, or state.

### Not a defect

A genuine source ambiguity/conflict preserved without a default, an explicit source blocker, or a presentational difference with equivalent behavior.

A recurring material-or-worse root cause exists in either:

- at least three audited units; or
- at least two source/component families.

One cause may not be split into cosmetic IDs to avoid escalation.

## Executable decision gate

`evaluate_correctness_audit.py` applies the preregistered thresholds. Stage 1 may pass audited units only when:

- no critical error was found;
- no authority override or hidden default was found;
- no recurring defect pattern exists;
- every core material error is repaired and reverified;
- no more than two isolated component material errors were found;
- no audited unit remains source-blocked;
- the deterministic clean-match review sample is complete.

A critical error, authority inversion, hidden default, recurring root cause, or more than two component material errors requires full-audit escalation. Isolated clustered component failures require affected-family expansion. The decision report always enumerates blockers, affected families, unfinished units, and the unaudited population boundary.

## Progress integrity

`progress.json` contains exactly one row per manifest unit and these lane states:

```text
pending-blind-derivation -> blind-derived -> compared -> final
```

Final is one of `accepted`, `material-error`, `critical-error`, or `source-blocked`.

Use `scripts/advance_correctness_audit_progress.py`; direct manual status edits are prohibited. The updater rejects skipped transitions, verifies artifact containment and hashes, updates counts/timestamps, runs the complete validator, and rolls back on failure. Git checkpoints preserve the transition history.

## Required commands

Before the baseline lock exists:

```bash
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/validate_correctness_audit.py --prelock
```

After `audit-lock.json` is committed, omit `--prelock`.

At every checkpoint run:

```bash
python3 scripts/build_correctness_audit_manifest.py --check
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/validate_correctness_audit.py
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_mutations.py
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_decision.py
python3 scripts/validate_source_extraction.py
python3 scripts/validate_project_status.py
git diff --check
```

Before the final owner decision, rerun vocabulary, ontology, semantic reproducibility/adversarial validation, all audit checks, and the decision evaluator. Frozen semantics may change only through a separately reviewed source-correction maintenance event; semantic expansion remains prohibited.

## Artifact map

- `manifest.json` — immutable population, hashes, eligibility coverage, and thresholds.
- `audit-lock.json` — external Git/baseline lock, created after the baseline commit.
- `progress.json` — lane state and artifact hashes for all 140 units.
- `source-packet.schema.json` — source-only packet allowlist.
- `packet-completeness-review.schema.json` — pre-derivation completeness decision.
- `blind-derivation.schema.json` — separately sealed source-derived requirements.
- `audit-result.schema.json` — post-reveal comparison and verification.
- `packets/` — packets, prompts, and completeness reviews.
- `blind/` — immutable blind derivations.
- `comparisons/` — post-reveal unit results.
- `reviews/raw/` — retained model final answers without reasoning traces.
- `reviews/` — setup reviews and independently verified dispositions.
- `reports/` — structural and decision reports.
