# Nemesis: Retaliation — Project Status

**Status date:** 2026-09-06
**Active phase:** Implementation Phase 1 — Clean Rewrite Architecture (Stage 1: Headless Rules & State Engine)
**Active branch:** `main`
**Implementation status:** Active (Approved by owner on 2026-09-06: rewrite-architecture-proposal.md accepted)

## Active Workspace

- Workspace root: `/home/smithers/nemesis-retaliation/`
- Repository worktree: `/home/smithers/nemesis-retaliation/`
- Branch: `main`
- Canonical lock: `/home/smithers/nemesis-retaliation/.workspace.lock`

## Current Objective

Implementation Phase 1 & 2 operational. Vitest test suite passes 73/73 tests. Playwright E2E suite passes 12/12 tests covering initial load, player HUD/cards, turn rotation, multi-viewport responsive framing (mobile/tablet/desktop), multi-touch pinch gesture stabilization, on-screen camera controls, diagnostics overlay, and two-client P2P action synchronization.

## Immediate Next Deliverable

Stage 3 & 4 full game loop expansion and additional interactive action flows (movement targeting, exploration card resolution, combat rolls) over live P2P network layer.

## Resume Checkpoint

- The former `work/card-corpus-extraction` worktree content is integrated into `main`; the removed worktree is absent from `git worktree list`. The latest concise-corpus repair commit is `1dbd572`.
- The prior 78 paired rulebook audit inputs, four rulebook pass artifacts, three slicing scripts, and obsolete rulebook slicing task/stage artifacts are deleted in the current atomic-audit checkpoint.
- The official 40-page rulebook was rendered temporarily and inspected page by page with vision. Pages 1-2 contain no gameplay facts or rules; pages 3-40 yielded 1,597 atomic records: 686 facts and 911 rules.
- `audit/manifest.json` contains 1,597 rulebook records and 2,126 records overall after the owner-approved retirement of three physically occluded, non-verifiable Objective Help Sheet occurrences; their source-extraction provenance records remain unchanged.
- Atomic-slice validation passes: contiguous per-page IDs, one assertion block per file, filename/classification agreement, required source and visual provenance, no within-page duplicate assertions, and source PDF SHA-256 `e3cda0d7a91bd090cec45dbc8ce89e2015e2202173357c374ff49365f9c29ddd`.
- The 2026-09-03 500-child attempt assigned 1,000 unique rulebook fragments. It closed 197 pass and 14 unsure verdicts and produced 133 fail claims; 656 assignments remained without a canonical verdict after widespread provider HTTP 429 failures and interruption. Two transient fragment-without-sidecar cases were returned to the audit root.
- All 133 fail claims were independently triaged: 121 gameplay/state gaps clustered around setup, map semantics, Event/Attack examples, Oxygen/Tactical Gear, exploration, Malfunctions, and Item traits/effects; 12 layout-convenience, recommendation, frequency-commentary, or flavor assertions were gameplay-irrelevant. Commit `9e9148d` repairs the 121 gaps across the concise corpus; each passed one direct post-commit re-check and returned to the audit root.
- The 146 repaired-priority fragments are complete: 146 pass, 0 fail, 0 unsure, 0 unreviewed. Eight initial workers were blocked by obsolete workspace-lock instructions; all 11 affected fragments passed in a later owner-authorized lock-free retry.
- The separate 100-worker GLM assignment is complete: all 200 unique fragments are dispositioned as 181 pass and 19 gameplay-irrelevant, with 0 fail, 0 unsure, 0 repair, and 0 unreviewed. Every genuine gap was repaired centrally and passed one independent re-verification; provider-safe waves of at most 10 children had no observed HTTP 429 failures.
- The raw self-scheduling verifier drain is complete and no verifier worker remains live. Across all source channels, all 2,129 manifest entries reconcile as 0 root, 1,579 pass, 359 fail, 129 unsure, 62 irrelevant, 0 repair, and 0 claimed, with unique locations, matching verdict sidecars, and no orphaned or opposite-verdict sidecars. Fail and unsure are unconfirmed verifier claims pending coordinator disposition; the concise corpus remains frozen.
- Raw-verdict drain checkpoint: commit `52bcf773af1128e3740af181d94ecc37ce28c26f` records the mechanically closed pre-disposition state above.
- Coordinator disposition is complete. All 2,129 manifest entries now reconcile as **1,579 pass, 332 repair, 56 unsure, 157 irrelevant, 5 root slice defects, 0 fail, and 0 claimed**. Every repair has a verbatim source assertion, `Applied fix: not yet applied`, and `Re-check: pending`; every remaining unsure sidecar explicitly records coordinator review and the applicable unresolved boundary. No corpus repair has been applied.
- The 332 repairs are assigned exactly once to seven mutually exclusive behavioral clusters: **14** reference/help-sheet phase sequence and lookup behavior; **67** escape, endgame, Objectives, and Mission Tasks; **72** Facility topology, Rooms, exploration, Doors, and map markers; **57** Character, Robot, Command, and Action-card behavior; **52** Items, equipment, storage, Health, and Tactical Gear; **51** Intruder, combat, Event, contamination, and Queen behavior; **19** setup, finite supplies, component identities, and icons. The cluster sum is **332**.
- Owner approved P1–P5 from `docs/qa/fragment-reslice-review/README.md`. `OBJ-29`, `OBJ-31`, and `OBJ-32` were retired from the rules-verification manifest because their physical official occurrences expose no complete operative assertion; their source-extraction provenance remains unchanged. The Heavy Gun Operator `DEMOLITION` and TTS-source `FACILITY RESTART` root slices were replaced with the approved pixel-bound records and each received exactly one fresh Luna Max verifier. Both failed because the frozen concise corpus omits their source-variant rules/boundaries, so they were independently converted to repair claims. Current mechanical state: **2,126 total = 1,579 pass + 334 repair + 56 unsure + 157 irrelevant; 0 root, 0 fail, and 0 claimed**.
- The 334-repair source-to-rule mapping (`docs/qa/repair-review/README.md`, P1–P7) was presented; the owner amended P2 to add `Evaluates via:` cross-references (surfacing OQ-013 corpses and OQ-014 Objective eligibility), kept Private Objective flavor text, then delegated the remainder autonomously. All seven clusters were applied to `docs/rules/` (commits `0c3a288`, `5889755`, `02ff0de`; +565/−5 lines), each ID passed one post-repair re-check (`docs/qa/repair-review/recheck/`, 334/334 covered), and all 334 fragments returned to the audit root for one fresh verifier each.
- Fresh verification closed with 17 fail claims, all coordinator-dispositioned: 15 Objective-family faces converted to unsure (their gap is an open question — OQ-013/OQ-014/OBJ-44 — not an omission), 2 true gaps repaired (`RB-P14-021` Rise of the Machine Health loss; `OBJ-16` Reinforced-path check) and re-verified pass. **Final mechanical state: 2,126 = 1,863 pass + 106 unsure + 157 irrelevant; 0 root, 0 fail, 0 repair, 0 claimed**, confirmed by `scripts/audit_closure_check.py`. Owner-facing notes: `docs/qa/repair-review/OWNER-NOTES.md`.
- Two isolated Ollama Cloud critics (DeepSeek V4 Pro 0813, GLM 5.3; max reasoning, read-only, diff + cited rulebook pages) reviewed the full repair diff (`docs/qa/repair-review/critics/`). Four findings verified against source and corrected in `02c003b` and `0e97617` (Fire At Will citation scope, Supply Route note scope, unsourced "loaded" Grenade qualifier, p. 23 Robot Malfunction exception); one rejected (FAQ `FQ-P03-U07` is verbatim official text). The 106 unsure fragments are grouped by governing open question in `docs/qa/repair-review/UNSURE-LEDGER.md`.
- The resource monitor covered the 26m18s verifier window. Peak CPU was 26.306%, peak one-minute load 2.175, minimum available memory 21,274,458,112 bytes, and peak WebUI RSS 2,925,813,760 bytes. NVMe utilization peaked at 71.756% with 4 ms maximum read await and 27.008 ms maximum write await; host saturation was not the wave limiter.

## Execution Boundaries

- Follow the owner's fragment-coverage review in `docs/rules/implementation-readiness.md`. The former Stage 1 v2 blind correctness-audit methodology was scrapped by the owner: its harness, scripts, packets, and review evidence were deleted and must not be rebuilt. Review rules and source evidence only.
- The owner decides worker count per wave.
- Verifiers operate directly in the defined repository audit folders and self-claim one canonical manifest fragment at a time through `scripts/audit_work_steal.py`. The helper uses only a short per-fragment flock during an atomic same-filesystem move into `audit/claimed/<worker-id>/`; verifiers must not acquire, inspect, wait on, or touch `.workspace.lock`. Serialize only genuinely shared writes such as corpus repairs and status updates. Do not use `/tmp`, copied packets, ad hoc directories, or verifier worktrees.
- Do not create Hermes profiles, expand semantics, touch the legacy implementation, open a PR, merge, deploy, or push unless separately authorized. A stop/status request preempts worker launches, integration, and autonomous successor handoff immediately.

## Verified Checkpoint

### Source/card corpus

- 532 in-scope extracted assets: **148 complete + 384 deferred + 0 unaccounted**
- 390 card/reference records
- 350 records with rules/effect text
- 78 canonical image/sidecar pairs
- 259 full drafts
- 1 partial record
- 0 no-transcription records
- 52 non-rules/reference records
- Manual stratified review: **8/8 complete**
- Approved icon identifiers: **50**

### Source-extraction layer

- Extraction closure gate: **PASS**
  - 9/9 source channels extracted or indexed
  - 6/6 gate criteria passed
  - 0 remaining graphical source units
  - 1 explicit exact-source operative blocker retained
  - next phase authorized: canonical vocabulary and source-scoped aliases
- Official sources inventoried:
  - Rulebook: 40 pages
  - FAQ v1.2: 4 pages
  - Room Help Sheet: 2 pages
  - Objective Help Sheet: 2 pages
- Secondary evidence closure:
  - 4 BGA copies verified byte-identical; 1 immutable build `260622-1220` snapshot retained
  - 11 BGA tables and 298 scoped structured records indexed
  - 6 TTS structured files indexed
  - 159 Lua role records
  - 172 GMNotes tag rows / 1,267 tagged occurrences
  - 384 selected-evidence entries/runs
  - 156 corpus records explicitly preserve a BGA conflict/secondary boundary
- Player Help source: **10/10 numbered fronts extracted**
  - 1 shared functional `PASS` side
  - 1 identical instruction-text variant
  - 2 measured raster-template groups
  - 0 functional icons and 0 unreadable spans
  - explicit conflicts: TTS 10 fronts vs official 5-card inventory; obsolete phase sequence vs current rulebook
- FAQ/errata v1.2: **4/4 rendered pages extracted**
  - 59 ruling/errata units
  - 28 base-game-applicable units
  - 31 expansion-specific units retained out of base conclusions
  - 15 errata units and 44 FAQ rulings
  - 4 inline visual occurrences
  - 0 unreadable spans
- Rulebook visual census: **40/40 rendered pages classified**
  - 80 non-decorative visual units
  - 72 normative visual obligations
  - 5 worked-example visuals
  - 3 reference/navigation units
  - 0 unreadable visual spans
  - all 80 only partially represented by text extraction because graphical structure is lost
- Intruder Help Sheet: both sides extracted source-bound
- Intruder Help instructions: **18/18**
- Room Help Sheet: **25/25 entries extracted source-bound and independently locked**
  - 25 exact source projections verified
  - 25 complete audited evidence crops verified
  - 112 literal functional-icon occurrences
  - 39 effect/note icon references
  - 0 unreadable operative spans
  - corruption negative controls reject verbatim, icon, crop, provenance, unreadability, and coordinated-layout drift
- Objective Help Sheet: **45/45 source units inventoried**
  - 35 fully visible units extracted source-bound
  - 10 physically occluded units retained with explicit visibility boundaries
  - 50 full and 5 partially visible icon occurrences
  - 0 unreadable visible spans
- Card-gap review: **13/13 source tuples adjudicated**
  - 9 rules-text-complete records
  - 1 explicit exact-source operative blocker
  - 3 classified non-rules components/placeholders
  - 1 operative correction recovered (`SUBMACHINE GUN`: colon)
  - 0 remaining no-transcription records
- Four licensed-digital BGA snapshots inventoried and confirmed byte-identical

Machine-readable evidence: `docs/rules/source-extraction/validation.json`.


### Semantic layer — archived 2026-09-02

- The semantic projection (26 data files, 34 scripts, 529 records) failed its
  proof-of-value gate and is **archived as obsolete** under
  `archive/obsolete/semantics/` (owner decision, 2026-09-02). It is not a live
  layer; do not extend, rebuild, or validate it.
- Its historical counts remain recoverable in Git history and in the archived
  `archive/obsolete/semantics/data/validation.json`.
- The rewrite will consume the concise Markdown rules corpus (`docs/rules/00-04`).
- The 115 open no-default questions and 88 preserved conflicts from the semantic
  layer remain tracked here and in `docs/rules/open-questions.md`; none adopts a default.

### Taxonomy/ontology — independently reviewed and passed

- 211 source-traceable taxa / 9 roots
- all 167 controlled terms mapped exactly once
- all 501 named identity observations mapped as source identities
- 50 printed-symbol denotations
- 55 static relationship shapes / 27 inverse pairs
- 14 source-backed structural assertions and constraints
- 15 semantic-scaffolding taxa for later zones, timing, decisions, visibility, lifecycle, and finite supply
- all 8 accepted aliases projected
- 0 ontology owner gates after four-workstream independent review
- 12 semantic relation IDs explicitly deferred from the static layer
- two-seed byte-identical rebuild validation and expanded corruption negative controls pass
- no triggers, ordered effect steps, costs, target selection, or state mutations encoded
- `scripts/validate_taxonomy_ontology.py`: **passed with 0 failures**

### Vocabulary proposal

- 1,853 observed source-term occurrences / 1,194 normalized exact-string keys
- 643 named-identity source occurrences / 501 exact-string groups
- 167 controlled vocabulary entries
  - 50 accepted existing icon-glossary terms
  - 117 authority-derived canonical-label proposals
- 8 alias entries
  - 8 accepted explicit/source-scoped aliases
  - 0 proposed aliases awaiting owner review
- 5 explicit non-alias guardrails
- 0 open review gates; taxonomy/ontology is authorized
- `scripts/validate_vocabulary_proposal.py`: **passed with 0 failures**

## Completed Milestones

- Downloaded, classified, and reconciled the base-game TTS asset tree.
- Completed bounded card/reference extraction for all in-scope images.
- Built a provenance-rich card-text evidence corpus with explicit canonical, draft, partial, missing, and non-rules states.
- Re-derived the official icon glossary and recorded reviewed source-scoped artwork resolutions without generalizing by appearance.
- Completed an eight-item manual review sample and applied all corrections.
- Extracted both Intruder Help Sheet sides without introducing canonical vocabulary.
- Extracted all 25 official Room Help Sheet entries with effects, notes, literal functional-icon occurrences, and reproducible visual evidence; an independent 25-entry audit found no material discrepancy, four incomplete crop extents were corrected, and a pinned fidelity lock plus corruption suite now enforces the result.
- Extracted the official Objective Help Sheet at its source boundary: all 45 units inventoried, all visible wording retained, physical occlusions explicit, repeated page terms preserved, and hidden text-layer data not promoted to visible-face evidence.
- Closed all 13 card-gap reviews at their source boundary: nine complete rules reads, three non-rules classifications, one exact-source blocker, and one recovered punctuation correction; prior selected worker evidence remains immutable history.
- Completed a blind rendered-page census of all 40 official rulebook pages and recorded 80 visual units with explicit text-layer coverage, including setup/map topology, component/card anatomy, token/die state keys, worked examples, and the 49-icon glossary.
- Extracted all 59 official FAQ/errata v1.2 units from four pages, retaining exact two-column section scope, 28 base-applicable versus 31 expansion-specific rulings, 15 errata, 44 Q&A rulings, and four source-local inline glyphs.
- Extracted all ten TTS Player Help fronts and their shared functional PASS side; proved one instruction-text variant and two raster-template groups, retained FaceURL/BackURL roles, and recorded count/phase-sequence conflicts with current official sources.
- Consolidated licensed-digital build 260622-1220 into one immutable snapshot, indexed 11 tables/298 scoped records, and closed six TTS structured channels as secondary provenance with explicit count/name/conflict boundaries.
- Passed the final nine-channel extraction closure audit: every source channel is extracted/indexed, all six gate criteria pass, no graphical units remain, and the one exact-source blocker remains explicit.
- Built and validated the vocabulary layer: 1,853 source occurrences, 501 named-identity groups, 167 controlled entries, 8 accepted aliases, and 5 non-alias guardrails; VG-001 and VG-002 are resolved.
- Built, independently reviewed, corrected, and validated the static taxonomy/ontology: 211 taxa, complete term/identity/alias mappings, 55 relationship shapes, 14 static constraints, semantic scaffolding, two-seed deterministic rebuilds, and adversarial negative controls; no owner gate remains.
- Built, independently reviewed, corrected, and validated an implementation-neutral 13-record semantic pilot across nine systems with exact source tuples, semantic state/zone nodes, explicit authority/timing/ownership/visibility/costs/targets/operations/transitions/partial resolution, two variants, seven conflicts, and nine no-default questions.
- Expanded the corpus to 24 records / 16 systems with Objective choice, Intruder/Event/Cleanup phases, generic Event resolution, Bag Development, Doors, Noise, Intruder Attacks, Health/Wounds, and Tactical Gear; covered source obligations rose from 17 to 25.
- Expanded and independently audited the corpus to 73 records / 18 systems: all 18 Intruder Help instructions, all 25 Room effects, generic Use Room, all 112 Room icon denotations, Robot/Data/Autodestruction/Nest constraints, exact FAQ overrides, and corrected per-Corridor Noise/Attack ordering; covered source obligations rose to 71 while eleven questions remain no-default.
- Closed the 20-card base Event family mechanically by TTS card ID/source tuple rather than title, retained 20 licensed variants and four official visible occurrences, encoded 88 exact printed sentences plus reusable Event procedures, and advanced source-obligation coverage to 102 while sixteen scoped questions remain no-default.
- Closed the entire 12-card base Exploration family mechanically from the root TTS deck and exact CardID/GUID/FaceURL tuples, retained the shared back, 12 licensed variants and three official visual occurrences, encoded 46 printed sentences plus 12 diagrams/60 icon occurrences without inventing titles, and advanced source-obligation coverage to 119 while seventeen questions remain no-default.
- Closed the six-card base Robot family mechanically from the root TTS role and exact full CardID/GUID/FaceURL/container tuples, retained one shared back, six licensed variants, two official visible face occurrences, literal runtime-state/prototype/expansion boundaries, 24 panels/16 sentences/23 icons, and advanced source-obligation coverage to 132 while twenty-five questions remain no-default.
- Closed the 20-occurrence base Intruder Attack family mechanically from the raw root TTS `DeckCustom`, retained repeated physical copies, 19 generated cells plus one direct face, one shared back, one unused selector-gap cell, 57 source-scoped applicability badges, 15 licensed variants and three official face counterparts, encoded 54 sentences plus reusable Contamination gain, and advanced source-obligation coverage to 154 while thirty questions remain no-default.
- Closed the 12-occurrence base Queen Health family mechanically from the raw root TTS `Deck`, retained 10 face assets as 12 physical CardID/GUID occurrences, one shared back, duplicate-copy and licensed-ordinal boundaries, 24 panels/37 sentences/28 functional symbols, official track/card/FAQ/Objective counterparts, reusable Queen combat/lifecycle procedures, and advanced source-obligation coverage to 174 while thirty-five questions remain no-default.
- Closed the 27-occurrence base Serious Wound family mechanically from the raw root TTS `Deck`, retained all repeated physical copies, seven selected generated cells plus six direct LEG/KNEE copies, two selector-gap source variants, one parent sheet/shared back, 54 panels/81 regions/42 sentences/30 physical symbols, independent official/licensed occurrences, reusable finite gain/discard/stacking lifecycle, and advanced source-obligation coverage to 189 while forty-four questions remained no-default at that batch checkpoint.
- Closed the 23-occurrence base regular Green Item family mechanically from the raw 30-child TTS `Deck`, retained all repeated physical copies, five selected generated cells plus eight direct copies, four selector-gap variants, seven Heavy exclusions, one parent sheet/shared back, 85 panels/69 regions/46 sentences/46 physical symbols, independent official/licensed evidence, reusable finite deck/Backpack/Use/Trade/Interplay/restoration lifecycle, and advanced source-obligation coverage to 215 while fifty questions remain no-default.
- Closed the 21-occurrence source-clear regular Red Item family mechanically from the raw 30-child TTS `Deck`, retained all repeated physical copies, seven selected generated copies plus fourteen direct copies, four Red selector gaps, three Heavy and six class-conflict root exclusions, two parent sheets/two backs, 87 panels/63 regions/45 sentences/27 regular physical symbols, independent official/licensed evidence, reusable Ammo/Grenade/Anti-Aircraft lifecycle, and advanced source-obligation coverage to 235 while fifty-five questions remain no-default.
- Closed the 24-occurrence source-clear regular Yellow Item family mechanically from the raw 30-child TTS `Deck`, retained all repeated physical copies, eleven selected generated copies plus thirteen direct copies, five selector gaps, six class-conflict root exclusions, two parent sheets and shared/UniqueBack forms, 128 regular panels/72 regions/56 sentences/48 physical symbols, independent official/licensed evidence, reusable Oxygen/Malfunction/Reinforce/Duct lifecycle boundaries, and advanced source-obligation coverage to 246 while sixty-one questions remain no-default.
- Closed the complete 60-occurrence base Action family mechanically from six Character kits plus the Shared Contractor root, retained 39 direct faces, 21 exact generated selections, 29 base selector-gap variants, 40 excluded expansion cells, two parent sheets, one 273-reference shared back, 290 panels/164 sentences/143 physical symbols, 60 independent licensed rows, exact setup/play/payment/draw/Reaction/Command lifecycle, and advanced source-obligation coverage to 348 while seventy-nine questions remain no-default.
- Closed the source-clear base competitive Objective/Mission family mechanically from three exact TTS roots, retained all 30 physical copies (29 source-clear plus one blocker), 50 source-face assets, 18 base selector gaps, nine prototype/high-count and 38 Solo/Coop physical exclusions, two parent sheets/two backs, 149 panels/53 sentences/39 physical symbols, all 45 official Help units with ten occlusions intact, 38 independent licensed rows, exact setup/secrecy/choice/fulfillment/endgame lifecycle, and advanced source-obligation coverage to 443 while eighty-three questions remain no-default.
- Closed the bounded base Heavy/Support Equipment/Weapon/Armor/Character Starting Item family: exact 24-card Support root with 22 direct and 2 generated selections, 40 source face assets/16 selector gaps, 19 Heavy and 5 Armor Support occurrences, 12 Support Weapons (9 Ranged/3 Melee), one 72-reference shared back, 7 Character-kit occurrences with 5 source-clear TTS variants and 2 Automatic Shotgun/BF Gun prototype/current exclusions, 7 Green Heavy plus 3 Red Heavy source-clear occurrences, 12 Red/Yellow class conflicts kept non-dispatchable, 6 current official-visible occurrences, 37 independent licensed rows, reusable setup/draft/Hand/Armor/load/use/passive/loss/Malfunction/die-result/Grenade Launcher records, and 18 no-default questions; semantic validation and exact root/kit/class/backlog locks pass at 499 covered / 100 pending / 1 blocked.
- Closed core Combat, Character/Intruder Attacks, Movement/Opportunity timing, Noise/Hazard spawning, and Intruder entry procedures: split paid Basic Actions from reusable sequences, retained exact attack/movement classes and FAQ scope, encoded official die result keys, Deadly values, Hit/type/token/component lifecycles, closed 11 exact backlog obligations, and advanced coverage to 510 / 89 / 1 while nine new questions remain no-default.
- Created the closed source inventory, card-gap inventory, secondary-source inventory, Room layout inventory, roadmap, and deterministic validator.

## Remaining Work — Ordered

1. **Coordinator disposition** — independently classify every fail and unsure verdict, correct the named pass defects, and report recurring confirmed-gap clusters to the owner.
2. Repair only the owner-authorized confirmed-gap clusters and preserve unresolved policy as explicit gates.
3. Expand affected families only if fragment-coverage findings require it.
4. Choose the new architecture independently and seek explicit approval before implementation.

Detailed phase plan: `docs/rules/source-extraction/extraction-roadmap.md`.

## Phase Gates

### Gate before vocabulary, aliases, taxonomy, or ontology — PASSED

All of the following are true:

- every in-scope source unit is `extracted`, `non-normative`, or explicitly `blocked`;
- every graphical normative channel has rendered-pixel evidence or a specific blocker;
- every operative card-text gap is closed or explicitly blocked;
- source versions and conflicts remain independent;
- counts reconcile across PDFs, help sheets, card corpus, and structured inventories;
- no extraction record silently embeds an alias or semantic interpretation.

### Gate before semantic modeling — PASSED

- controlled vocabulary and aliases reviewed;
- source terms and source-local morphology remain traceable;
- static taxonomy/ontology independently reviewed and validated;
- static relationships/cardinalities and timing/decision/visibility/lifecycle scaffold boundaries agreed;
- semantic relation IDs are explicitly deferred into this phase rather than pre-populated with guesses;
- unresolved source questions remain explicit.

### Gate before implementation

- source-backed rules coverage judged solid enough by the project owner;
- representative semantic rules and executable scenarios validate the model;
- contradiction, completeness, citation, terminology, and source-variant audits pass;
- new architecture is chosen independently of the legacy implementation;
- project owner explicitly approves starting the rewrite.

## Current Decisions and Boundaries

- Base game only; expansion extraction is deferred.
- Preserve official, TTS, licensed-digital, and other source variants independently.
- Official FAQ/errata takes precedence over the official rulebook where applicable.
- Component scans and secondary sources do not silently overwrite official text.
- Do not create canonical vocabulary or semantics during extraction.
- Artwork and interface microtext are not rules unless their placement/function establishes that they are normative.
- Current implementation files are not rules authority.
- No implementation, PR, merge, or deployment work is currently authorized.

## Known Current Blockers and Open Evidence

- The owner-approved five-fragment reslice and its fresh verification are complete. Three physically occluded official occurrences were retired from verification without altering source provenance; both corrected source variants failed and are now confirmed repair claims. Corpus repair remains blocked pending the owner's decision on the review packet at `docs/qa/repair-review/README.md`; material judgment calls (packaging sub-facts, Closed-Door Facility-wide exception, Robot Malfunction wording conflict, same-title Objective/Item variant conflicts, Private Objective flavor text) are itemized there.
- The source-blocked `FACILITY RESTART` prototype is `assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-023.png`, which ends at “Systems must be.” The separate generated `missionTaskDeck-160_cards/card-08.png` face contains a fully visible but unmatched source-local badge and materially conflicts with official Objective Help Sheet unit `P1-MT-FACILITY-RESTART`; these occurrences must remain separate.
- Vocabulary gates `VG-001` and `VG-002` are resolved; `PERSONAL OBJECTIVE` remains source-scoped and `Drilling Room` aliases `DRILLING STATION` with both official labels preserved.
- 115 semantic/source questions remain explicit: OQ-001, OQ-003, OQ-004, OQ-007, OQ-009, and SEM-Q-001 through SEM-Q-110. They block only affected clauses/records, not unrelated coverage work.
- OQ-002 is resolved by current official rulebook p. 39 (lines 6251–6265): evaluate Larva eligibility when the Eclosion cohort step is reached, including a Larva gained during the preceding Infection step. OQ-001 and multi-Character cohort ordering remain unresolved and unchanged.
- SEM-Q-011 retains the source-unspecified assignment of random Corridor draws and scarce finite components across multiple Exploration diagram slots; no player owner, spatial order, or additional randomization is adopted.
- SEM-Q-012 through SEM-Q-019 retain Robot reveal/effect availability, movement ownership, Exploration Noise, Medical choices, Securing Door/supply behavior, Server Room context, and Technical marker scope without defaults. SEM-Q-020 through SEM-Q-024 retain Attack scope, continuation, timing, Wound assignment, and no-badge applicability. SEM-Q-025 through SEM-Q-029 retain Queen Health trigger timing, Character attribution, final-card death, Malfunction/Unreinforce ownership/location, and terminal-glyph scope. Neoflesh-only FAQ answers remain excluded from base conclusions.
- SEM-Q-030 through SEM-Q-038 retain Serious Wound reveal/placement visibility, no-empty-section and Heavily-Injured displacement, direct KNEE/LUNGS local glyphs, BODY Hand Size scope, effect activation timing, Pass-trigger order, and grouped multi-Wound ordering without defaults.
- SEM-Q-039 through SEM-Q-045 retain Use/One Use payment-reveal-effect-discard order, finite Item color-deck exhaustion, selected Green local glyphs, Contamination Codes Door eligibility/allocation, Interplay restoration ownership and gain-glyph scope, and multiple immediate-use Item timing without defaults.
- SEM-Q-046 through SEM-Q-050 retain selected Red upper-right glyph restrictions, Military Taser class/current-source correspondence, Exploring Drone target context, Personal Log Objective inspection/secrecy, and Portable Barrier Door/FAQ applicability without defaults. SEM-Q-040, SEM-Q-044, and SEM-Q-045 now also cover Red color-deck exhaustion, Tactical Gear gain-target scope, and Red immediate-use windows.
- SEM-Q-051 through SEM-Q-056 retain selected Yellow upper-right glyph restrictions, Fire Extinguisher/Robot Controller class correspondence, Duct Tape source/One Use/stacking/Trade lifecycle, Phosphates Corridor targeting, and Tools Door ownership/accessibility without defaults. SEM-Q-040, SEM-Q-044, and SEM-Q-045 now also cover Yellow color-deck exhaustion, Oxygen-token gain-target scope, and Yellow immediate-use windows.
- SEM-Q-057 through SEM-Q-074 retain Action-card upper-right and Search/draw glyphs, Command costs/owners, Reaction priority, death/escape continuation, multi-target order, consent, nested Command lifecycle, rerolls, Corridor placement, finite draw shortage, Movement interrupts, and cancellation payment timing without defaults.
- SEM-Q-075 through SEM-Q-078 retain Objective OR-branch commitment/availability, Ulterior Motive continuous-versus-endgame fulfillment timing, late Objective choice/reward/chooser ordering, and endgame reveal/check ordering without defaults.
- SEM-Q-079 through SEM-Q-096 retain Heavy/Equipment roster, supply, capacity, lifecycle, glyph, target, Weapon-result, Malfunction, Grenade Launcher, and Motion Tracker boundaries without defaults.
- SEM-Q-097 through SEM-Q-105 retain numeric-Noise Corridor order, Intruder-bag and Attack-deck exhaustion, side-level Blank scope, Movement interruption, equal-size Intruder order, dead-Larva continuation, Burst multi-target resolution, and mixed Adult/Drone allocation without defaults.
- SEM-Q-106 through SEM-Q-110 retain Section-border/special-space orientation and endpoint crosswalk, initial Landing Zone Door entrance assignment, setup shortage/replacement/atomicity, and unnamed Room/Exploration/Suppression marker identity without defaults.
- The 25 Room Help entries versus 23 physical Room tiles relationship is resolved: the two additional entries are the fixed Landing Zone and Hibernatorium named-space effects, not extra Room tiles.
- Source/version conflicts remain in several card families and must not be flattened.
- Genuine rules ambiguities remain in `docs/rules/open-questions.md`; some stale extraction blockers there must later be re-audited against newly collected evidence.

## Tracker Ownership

Use these records for different questions:

| Question | Authority |
|---|---|
| What phase are we in, what is next, and what is blocked? | `PROJECT_STATUS.md` |
| What is the ordered extraction plan? | `docs/rules/source-extraction/extraction-roadmap.md` |
| What exact source/gap counts exist? | `docs/rules/source-extraction/*.json` and `docs/rules/source-extraction/validation.json` |
| What is the detailed backlog and historical checkpoint trail? | `todo.md` |
| What rules are established? | `docs/rules/readme.md` and numbered rule files |
| What source ambiguities remain? | `docs/rules/open-questions.md` |
| What card-corpus procedures and trust states apply? | `assets/tts-mod/notes/card-text-corpus.md` |
| What was durably checkpointed? | Git on `work/card-corpus-extraction` |

`PROJECT_STATUS.md` should stay concise. Update it after meaningful changes to the active phase, immediate next deliverable, blockers, gates, or verified headline counts. Link to detailed evidence rather than copying logs.

## Resume Checklist

1. Use `/home/smithers/nemesis-retaliation/` and hold its canonical root lock only while actual workspace work is running.
2. Read this file, `AGENTS.md`, `AGENTS-SUPPLEMENT.md`, and the owner's fragment-coverage review in `docs/rules/implementation-readiness.md`. Do not read historical candidate reports unless diagnosing a named regression; they are recoverable only from Git history.
3. Verify branch, HEAD, dirty/protected scope, and active workers; do not infer state from an old transcript.
4. Execute the Immediate Next Deliverable directly. Do not rebuild the scrapped audit machinery, create reviewer worktrees for read-only work, or run hostile-filesystem probes.
5. Keep fragment-coverage review work simple and its evidence compact: fragment text in, yes/partial/no answer with citations out. Clean temporary worker directories immediately after verified integration.
6. Update this file only when material status changes. Commit or push only within the authorized boundary; do not open a PR or deploy without explicit approval.
