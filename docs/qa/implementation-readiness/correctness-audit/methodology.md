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
- the full comparator-visible vocabulary, ontology, semantic, conflict/question, coverage/backlog, and source-index artifact hashes;
- exact family, candidate-universe, eligibility, and selected counts;
- pass thresholds and the limited claim scope.

Deterministic rank prevents outcome-driven choice **inside declared strata**; it does not prove that the strata are unbiased. Therefore `selectionCoverage` exposes every stratum's eligible and selected counts. Known limits are explicit:

- Intruder Help samples one row from each caller context, including the bottom row.
- Intruder Attack samples two of twenty source occurrences and is not guaranteed to contain two variants of one title.
- Two of eight Equipment/Starting Item slots are reserved for known-hard source/class boundaries.

After setup validation, the harness is committed once, then `audit-lock.json` is introduced in the immediate direct-child commit. It binds the manifest and immutable harness files to the baseline commit. The locked set closes over every prelock file under `correctness-audit/reviews/` automatically, while excluding the separately sealed post-lock lane root `reviews/raw/`; a late final review file therefore cannot be omitted by forgetting to edit a static list. The validator verifies that the starting HEAD and baseline remain ancestors, immutable file bytes equal the baseline, and the lock itself is unchanged from that direct-child commit. Any change requires a new audit version and an explicit disposition of the old audit.

For every later lane artifact, `sealedAtGitHead` means the immediate **pre-seal** HEAD, not the commit containing the artifact. The validator derives the seal commit as the first non-merge, first-parent direct child of that HEAD; the versioned artifact path must be absent before the seal and its current bytes must equal the bytes introduced there. Artifacts at the same dependency level may and, for a multi-unit wave, must share one wave seal commit by declaring the same pre-seal HEAD; seal commits are not required to be distinct per artifact. No later commit may introduce another artifact while claiming the earlier pre-seal HEAD, and no merge commit is permitted anywhere after the v2 baseline. Each dependent lane follows the preceding wave's derived seal commit. Packet visuals and canonical completeness prompts are committed with the packet wave; completeness responses and reviews are committed in the next wave; canonical blind prompts, responses, and derivations follow; comparison prompts/responses and all comparisons follow in Lane C; verification prompts/responses, repair proof, and final adjudications follow separately in Lane D.

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

Any PDF-derived `exactText` also requires the exact deterministic full-page PNG rendered from the same source PDF and declared 1-based `pdfPageIndex` at the locked 160 DPI; the validator rerenders that page with `pdftoppm` after the lock and requires an identical SHA-256. A crop may be added for reviewer convenience, but it cannot replace the full-page proof. The validator also checks PNG structure, chunk CRCs, terminal IEND, and nontrivial dimensions; a renamed text file or unrelated valid PNG is not visual evidence.

Concise-rule files, semantic projections, conflict dispositions, physical-class conclusions, and implementation files are not valid packet evidence. Source indexes may help the supervisor locate original bytes but are not transmitted as blind evidence.

Every packet records nonempty:

- searched source files and hashes;
- exact included locators;
- search terms;
- neighboring sections checked;
- component/visual channels checked;
- exclusions and their reasons;
- applicable FAQ units checked, where any exist.

For every FAQ or sampled component unit whose manifest row pins `sourcePath` and `sourceSha256`, at least one evidence row assigned to that exact unit must use that exact manifest source tuple. Other allowed adjacent, overriding, or negative evidence may be added, but unrelated allowed source evidence cannot satisfy the selected unit's direct-source binding.

A separate source-only critic reviews the packet under `packet-completeness-review.schema.json`. The validator reconciles every unresolved material/critical finding against `unresolvedMaterialFindingIds`; `accepted` must be false whenever that set is nonempty. The packet is eligible for derivation only when the review is accepted and has no unresolved material finding. The packet and completeness review carry hashes, UTC seal times, and Git HEADs. Every reviewer kind, including agent and human reviewers, records hash-pinned prompt and response artifacts.

A mechanical field allowlist is appropriate; an n-gram ban is not. Official text may legitimately overlap concise wording because concise rules quote official sources. The protection is source-path provenance, a closed packet schema, an isolated prompt, and a separate completeness review—not lexical suppression of authoritative text.

## Lane B — separately sealed blind derivation

An isolated reviewer receives only the accepted packet, neutral instructions, and the closed blind output contract. `scripts/build_correctness_audit_prompt.py` generates the exact prompt from locked instructions and sealed payloads; the validator recomputes those bytes. The prompt is retained under `packets/` with its SHA-256 and may not contain downstream rule paths, semantic paths, or conclusion fields.

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

The blind file is physically separate from all post-reveal comparison files. It is hashed before Lane C begins and is never rewritten. The canonical completeness prompt is introduced with the packet; its response and accepted completeness review are introduced in the next lane; the canonical blind prompt, its response, and the blind artifact are introduced in the following lane. Packet, completeness-review, prompt, response, and blind hashes remain independently addressable.

## Lane C — reveal and comparison

Only after Lane B is sealed may a different comparator inspect:

- the concise rule or FAQ projection under audit;
- relevant frozen semantic records;
- relevant semantic questions and conflicts;
- direct primary sources needed to verify a claimed mismatch.

`comparison.schema.json` is the immutable post-reveal contract. It contains only a hash reference to the sealed blind file and cannot rewrite blind requirements. It records the comparator, inspected downstream artifacts, and classified discrepancy rows, but it cannot contain verification or final-resolution fields.

Every `revealedArtifact` records canonical path, SHA-256, and a closed role. The required unit target (`downstreamPath` for concise rules or `extractionPath` for FAQ/component units) must appear exactly once as `downstream-target`. Every comparison must reveal `docs/rules/semantics/pilots.json` as the actual behavior `semantic-projection`; `review-gates.json` and `contradictions.json` may be additional semantic projections, but source extraction files, `*-source-index.json`, registries, schemas, validators, and other metadata cannot satisfy that role. Other semantic projections and source indexes must be present in the manifest's frozen hash maps; direct primary sources must already occur in the sealed source packet. Declared semantic rule, open-question, and conflict IDs are validated against the frozen `pilots.json`, `review-gates.json`, and `contradictions.json` indexes.

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

Material and critical discrepancies require a stable `rootCauseId`. Authority inversions and hidden defaults have mandatory Boolean flags and critical severity. `match` requires `none`; behavioral omission/overstatement/lost-ambiguity/flattened-conflict/packet-gap classes cannot use `none`; preserved ambiguities/conflicts and presentation-only rows retain their bounded non-defect severities. Every comparison evidence reference must resolve to the sealed source packet.

## Lane D — independent verification

A reviewer different from the completeness reviewer, blind reviewer, and comparator checks direct source evidence for:

- every critical, material, blocked, minor, and presentation-only discrepancy;
- every preserved ambiguity or conflict disposition;
- a deterministic sample of otherwise clean matches.

All 140 comparison artifacts must be sealed before any final adjudication. They use the common Lane C pre-seal HEAD and may share the single Lane C wave seal commit; the validator requires that derived comparison seal commit to be an ancestor of every adjudication pre-seal. Once all comparisons exist, `evaluate_correctness_audit.py` publishes the clean-match sample locked by `SHA-256("nemesis-stage1-lane-d-match-v1|" + auditUnitId)`:

- six clean concise-rule matches;
- three clean FAQ matches;
- one clean match from each of the fourteen component families.

The selected set must contain exactly 23 unique units. If a stratum has no clean comparison, no substitute conclusion is inferred and Stage 1 cannot pass that audit version. `audit-result.schema.json` is the separate final-adjudication contract: it references the immutable comparison by path/hash, contains verification reviews and resolution only, and cannot restate comparison or blind content. The validator derives final status consistency from the comparison rows, so a material result cannot be marked accepted. Reviewer prompts/responses are hash-pinned; reviewer identities must differ from the completeness reviewer, blind reviewer, and comparator. For model-assisted lanes, identity is the nonempty provider plus nonempty resolved `responseModel`; the requested alias is never an identity fallback, and changing a run ID or response path does not create independence. Agent/human identity is only `(kind, stable reviewerId)`; provider/channel/model/path fields cannot turn the same stable actor into a different reviewer. A `not-confirmed` verification requires a superseding comparison instead of final adjudication, and a `source-blocked` verification disposition is valid only on a source-blocked result.

The current audit version cannot repair a frozen downstream target in place. A material or critical correction requires an explicit superseding manifest/lock and rerun; an unrelated new path cannot convert an error into a pass. `not-required` and `pending` carry no repair proof, while a source-blocked resolution carries verification evidence but no repair path. `evaluate_correctness_audit.py` prevents a final pass while any core material error or selected clean match remains unresolved/unverified.

GLM 5.3 and DeepSeek V4 Pro 0813 may be used as isolated advisors/critics through Ollama Cloud with `think: "max"`. Record exact requested/response tags, provider, request mode, prompt/response hashes, and final answer. Never retain `message.thinking` or another reasoning trace. Model findings remain advisory until checked against files or primary sources.

## Reviewer batching

Several units may share one call only when:

- every submitted unit ID is returned exactly once and in order;
- no result merges evidence across unrelated units;
- packet and prompt hashes are common and recorded;
- omitted, malformed, or cross-contaminated units are retried independently;
- source-family batching does not expose downstream conclusions.

Component visuals are read only through the verified native Sol Max workflow when a fresh visual read is needed. Existing independently validated source-bound transcriptions may be supplied, but their literal/source role must remain explicit.

## Isolated-worktree source provisioning

Git worktrees do not carry the gitignored official PDFs or extracted component bytes. Before a repository-aware worker runs the audit/source checks in an isolated worktree, stage those source-only trees from the explicit local source checkout and verify them byte-for-byte:

```bash
python3 scripts/stage_correctness_audit_sources.py --source-root /home/smithers/nemesis-retaliation
python3 scripts/stage_correctness_audit_sources.py --source-root /home/smithers/nemesis-retaliation --check
```

The helper copies only `docs/rulebooks/` and `assets/tts-mod/extract/`, rejects every symlink component, verifies each file with SHA-256, and leaves tracked repository files unchanged. Missing sources are a worker-environment blocker, not permission to weaken a validator or substitute another source. Blind-derivation workspaces remain repository-free and receive only the accepted sealed packet, fixed prompt, and blind schema; they never receive these trees.

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
- no core concise-rule or FAQ material error exists in the current frozen version;
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

Use `scripts/advance_correctness_audit_progress.py`; direct manual status edits are prohibited. The updater rejects skipped transitions, verifies artifact containment and hashes, updates counts/timestamps, runs the complete validator, and rolls back on failure. Git checkpoints preserve the transition history. After the lock exists, the validator replays every first-parent `progress.json` snapshot from the baseline, rejects merges, requires exact row shapes and one-step transitions, preserves unchanged rows byte-for-byte, and enforces increasing transition timestamps and stage-appropriate artifact fields.

## Required commands

Before the baseline lock exists:

```bash
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/validate_correctness_audit.py --prelock
```

After the final reviewed baseline commit is clean and all 140 progress rows are still pending, create the lock file, stage only that file, and commit it as the baseline's immediate direct child. The creator rejects any tracked, staged, or untracked nonignored worktree state, and the post-lock validator requires the direct-child commit's complete changed-path set to contain only `audit-lock.json`:

```bash
python3 scripts/create_correctness_audit_lock.py
git add docs/qa/implementation-readiness/correctness-audit/audit-lock.json
git commit -m "chore: lock Stage 1 v2 correctness audit"
```

Then run the full validator without `--prelock`; it derives and verifies that direct-child lock commit. Do not place another commit between the baseline and lock, and do not stage the protected or unrelated worktree state.

After `audit-lock.json` is committed, omit `--prelock`.

At every checkpoint run the common checks below, using exactly one lifecycle-specific validator command:

- before the lock commit: `python3 scripts/validate_correctness_audit.py --prelock` through the pinned `uv` environment;
- after the lock commit: the same command without `--prelock`.

Prelock checkpoint:

```bash
python3 scripts/build_correctness_audit_manifest.py --check
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/validate_correctness_audit.py --prelock
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_mutations.py
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_source_only_cli.py
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_decision.py
python3 scripts/validate_source_extraction.py
python3 scripts/validate_project_status.py
git diff --check
```

Post-lock checkpoint:

```bash
python3 scripts/build_correctness_audit_manifest.py --check
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/validate_correctness_audit.py
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_mutations.py
uv run --isolated --with-requirements docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
  python3 scripts/test_correctness_audit_source_only_cli.py
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
- `comparison.schema.json` — immutable post-reveal comparison.
- `audit-result.schema.json` — later independent verification and final adjudication.
- `packets/` — packets, prompts, and completeness reviews.
- `blind/` — immutable blind derivations.
- `comparisons/` — immutable Lane C comparison records.
- `adjudications/` — separate Lane D final results.
- `reviews/raw/` — retained model final answers without reasoning traces.
- `reviews/` — setup reviews and independently verified dispositions.
- `reports/` — structural and decision reports.
