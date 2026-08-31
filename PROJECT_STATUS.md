# Nemesis: Retaliation — Project Status

**Status date:** 2026-08-31
**Active phase:** Stage 1 v2 baseline/lock transition, then substantive blind rules audit (semantic expansion frozen)
**Active branch:** `work/card-corpus-extraction`
**Implementation status:** Frozen; a clean rewrite will begin only after rules-layer readiness and explicit approval

## Current Objective

Run the normal prelock gate once at the current proportional-review checkpoint, create the v2 baseline/lock transition if green, and execute the authorized Stage 1 blind correctness audit over 140 substantive rules/FAQ/component units before any rewrite approval.

The current implementation remains frozen. Existing semantic records remain immutable audit/reference evidence; expansion is not recommended.

## Immediate Next Deliverable

Do **not** launch another harness review. The project owner accepted the proportional-review boundary: the normal threat model covers accidental errors, source omission, malformed/stale artifacts, anchoring, blindness, and cooperative-worker overlap—not a hostile local process racing filesystem operations.

At the current committed checkpoint, run the exact normal prelock commands in `docs/qa/implementation-readiness/correctness-audit/methodology.md`. If the repository is clean and the gate is green, use that commit as the v2 baseline, create audit-lock.json as its immediate direct child, run the post-lock gate, and begin the first substantive source-packet batch. The population remains 56 concise rules + 28 base-applicable FAQ units + 56 stratified component effects.

Evidence: `docs/qa/implementation-readiness/correctness-audit/`.

## Resume Checkpoint

- Verified semantic data checkpoint: `f3fbd28` for the Facility/map topology/setup batch integrated over the prior Combat/Attacks/Noise/Hazard data and adversarial suite.
- Branch `work/card-corpus-extraction` contains the candidate-5 disposition checkpoint (`71a5ba0`) and preserved probe sources (`a833aa5`). The project owner accepted this as sufficient to proceed after the normal gate; it must not trigger another meta-review. No audit work has been pushed; no PR or deployment exists.
- The preserved v1 baseline (`2fe3f0d`) and lock commit (`3e23aeb`) are superseded and cannot authorize execution. `docs/qa/implementation-readiness/correctness-audit/audit-lock-v1.json` is retained; no v2 lock exists.
- The v2 population is unchanged and ordered: 140 units (56 concise rules, 28 base-applicable FAQ units, 56 component effects), all `pending-blind-derivation`; no substantive audit judgment has begun.
- Candidate review history remains under `docs/qa/implementation-readiness/correctness-audit/reviews/` as evidence only. New sessions must not read or replay those reports unless diagnosing a concrete regression tied to one of them.
- The candidate-5 disposition closed the accepted source-only, lock-commit, schema/control, and status findings. Filesystem-race hardening already present is now a closed regression topic outside the ongoing threat model.
- Fresh final validation of the post-disposition checkpoint on 2026-08-31 is green: manifest freshness and prelock validation pass; all 102 mutation/provenance/path/evidence/render/wave/progress/rollback controls, the complete source-only CLI matrix and its benign controls, and all 15 decision tests pass; source extraction passes; source staging verifies 1,098 files with zero copies; project-status validation and `git diff --check` pass.
- The normal gate—not another review wave—is the remaining prerequisite to baseline promotion. Provider-blocked, interrupted, empty, malformed, or contradictory substantive audit attempts remain non-evidence.
- The core Combat/Attacks/Noise/Hazard/entry batch is integrated over the prior Heavy/Equipment work; deterministic semantic rebuilds and 48 focused/adversarial tests pass, including the new independent Combat projection.
- Resume in Stage 1: the owner accepted the recommendation to keep semantic expansion frozen and authorized the 140-unit blind correctness audit. Current source-obligation boundary remains 530 covered / 69 pending / 1 source-blocked with 115 no-default semantic questions.

## Stage 1 Execution Boundaries

- Follow the proportional-review and threat-model section in `AGENTS.md` and the methodology. Do not perform another broad harness review or exploit-style filesystem probe without explicit new authorization or a concrete in-scope failure.
- Default to one worker; use 2–4 for genuinely different substantive specialties. Larger fan-out is reserved for distinct rules/content partitions, not duplicate critics. Capacity is not a target.
- Read-only and blind workers should receive immutable bounded packets. Create separate task workspaces/worktrees only when a worker must write repository artifacts or inspect Git-specific behavior. Never use sleep-only lock holders.
- For 1–4 workers, compact results are sufficient. Use the manifest/envelope/aggregation protocol only for larger fixed batches where exact closure materially helps. Preserve full reports only for material findings or formal acceptance decisions.
- No v2 baseline or active v2 lock exists yet. A clean normal prelock gate is sufficient to promote the current checkpoint and create the active v2 lock in its immediate direct-child commit.
- Baseline/lock creation, first-parent lane seals, progress transitions, tamper controls, and final adjudication remain serial. Once v2 is locked, follow `docs/qa/implementation-readiness/correctness-audit/methodology.md` for the packet, completeness, blind derivation, comparison, and verification waves without weakening blindness or reviewer independence.
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
- `scripts/validate_source_extraction.py`: **passed with 0 failures**

Machine-readable evidence: `docs/rules/source-extraction/validation.json`.


### Semantic schema and expanding corpus — independently locked and passed

- 474 exact source registry tuples
- 26 semantic-only state/zone/position/visibility nodes
- 529 pilot records across 26 systems
- 177 source-backed
- 329 source-backed with open questions
- 23 source-variant boundary records
- 1405 source assertions / 1543 structured conditions and guards
- 2290 ordered operations
- 337 actor-owned decisions / 549 information policies
- 37 explicit costs / 556 target specifications
- 248 preserved source-variant references
- 115 open semantic questions with explicit alternatives and defaults prohibited
- 88 registered conflicts: 21 authority-resolved, 34 unresolved, 33 preserved boundaries
- base Event family: **20/20 identities represented**
  - 20 exact Event scan occurrences
  - 20 licensed-digital Event occurrences retained as variants
  - 4 official visible component occurrences
  - 20 Event semantic records / 20 exact Event backlog tuples
- base Exploration family: **12/12 untitled identities represented**
  - 12 exact TTS CardID/GUID/FaceURL scan occurrences and 1 shared BackURL occurrence
  - 12 licensed-digital Exploration occurrences retained as variants
  - 3 official visible occurrences across 2 component identities
  - 46 exact printed sentences / 12 source-local diagrams / 60 functional icon occurrences
  - 12 Exploration semantic records / 12 exact Exploration backlog tuples
  - 0 generated sprite-sheet cells and 0 selector gaps in the mechanically derived base family
- base Robot family: **6/6 identities represented**
  - 6 exact TTS full-CardID/GUID/FaceURL scan occurrences and 1 shared non-operative BackURL occurrence
  - 6 licensed-digital Robot occurrences retained as variants
  - 2 official visible face occurrences across 2 component identities
  - 24 physical panels / 12 operative rules panels / 13 printed options
  - 16 exact printed sentences / 23 functional icon occurrences
  - 6 Robot-face semantic records / 6 exact Robot backlog tuples
  - 7 new reusable setup, reveal, Activation, movement, Tactical Gear, and Malfunction-placement records; existing `SEM-ROBOT-MALFUNCTION-001` remains unresolved under `SEM-Q-010`
  - shared back, Lua model/helper state, two prototype cards, three expansion Robot cards, and four Security Robot Room name collisions remain excluded from the six rules faces
- base Intruder Attack family: **20/20 mechanically selected physical occurrences represented**
  - 19 exact generated-cell full-CardID/GUID/CustomDeck/FaceURL occurrences plus 1 direct Blood Sense occurrence
  - 8 printed titles with multiplicities preserved, including 6 distinct Bite copies; no title/cell/folder/modulo join
  - 1 shared non-operative BackURL, 1 parent 5×4 source sheet, and 1 unused selector-gap `SUMMONING` cell explicitly excluded from rules-face counts
  - 69 physical panels / 29 operative effect panels / 54 exact printed sentences
  - 57 literal applicability badges projected source-scoped from page-32 Adult/Drone/Queen templates, plus 13 independently resolved inline icons; all 55 selected no-match rows remain intact
  - 15 licensed structured variants linked across 20 physical occurrences, 3 official-visible face counterparts, and 1 official-visible back counterpart retained independently
  - 20 Attack-face semantic records plus reusable finite Contamination gain and exact dispatch from `SEM-INT-004`; five new no-default questions preserve Fury scope, dead-target continuation, Blood Sense timing, Deadly Claws Wound order, and MISS applicability
  - three expansion Attack decks, the parent sheet, shared back, unused `SUMMONING` cell, and duplicate evidence references remain excluded from the 20 base rules occurrences
- base Queen Health family: **12/12 mechanically derived physical occurrences represented**
  - 10 exact FaceURL assets under 12 full CardID/GUID/CustomDeck occurrences; two `-084` and two `-045` physical copies remain distinct
  - 1 shared non-operative BackURL with 13 provenance references; 0 generated cells, parent sheets, selector gaps, prototypes, or placeholders in the base root deck
  - 24 physical/operative panels, 37 exact printed sentences, 12 source-local number displays, and 16 exact page-40 icon matches across 28 functional occurrences
  - discard-number multiplicity is 0×3, 1×4, 2×2, 3×3; TTS saved order is provenance only because setup shuffles the deck
  - 12 licensed structured rows remain independent; duplicate keys are candidate sets rather than arbitrary copy pairings, and the Malfunction-only licensed variant does not erase the TTS Unreinforce branch
  - 3 official-visible face occurrences, 2 official-visible backs, a six-space Queen Hits track, 2 unmapped terminal/inline local symbols, 1 FAQ ruling, and 2 Queen-death Objective Help occurrences are linked source-scoped
  - 12 physical-face semantic records plus reusable setup, Shoot, Burst, Hits, resolution, death, Activation, Repel, Action-draw, and Room-Malfunction procedures; five new no-default questions retain timing, attribution, final-card death, branch ownership/location, and local-glyph scope
  - three expansion Queen Health decks, 20 Queen-applicable Attack occurrences, Queen-titled Event/Help/token/model/objective records, the shared back, and duplicate evidence references remain excluded from the 12 base rules occurrences
- base Serious Wound family: **27/27 mechanically derived physical occurrences represented**
  - 21 exact generated selections across seven cells of one 3×3 source sheet plus six direct LEG/KNEE full-CardID/GUID/CustomDeck/FaceURL occurrences; all nine printed titles retain multiplicity three
  - 9 selected face assets, 11 total source face assets, 2 explicit selector-gap cells, 1 parent sheet, and 1 shared non-operative back with 28 provenance references remain distinct
  - 54 physical panels / 81 physical regions / 27 operative panels and regions, 42 printed sentence occurrences, and 30 physical functional-icon occurrences (24 exact matches + 6 literal local no-matches)
  - nine licensed structured rows remain independent with zero asserted physical identity links; two official EYES faces, one partial ARM face, and two official backs control only their exact publisher occurrences
  - reusable finite setup/gain/discard/stacking/variant-boundary procedures integrate Character Health, Attack, Medical Robot, Emergency Room, and Surgery without inventing reshuffles, title joins, or Surgery branch order
  - nine new no-default questions retain reveal timing, full-slot/terminal displacement, local glyphs, BODY Hand Size, activation timing, Pass triggers, and multi-Wound order
  - selector-gap cells, the parent sheet, shared back, diagnostic overlays, an expansion Wound-referencing component, placeholders, and duplicate evidence references remain excluded from the 27 physical rules occurrences
- base regular Green Item family: **23/23 mechanically derived physical occurrences represented**
  - exact 30-child `greenItemsDeck` root retained as 23 regular/Backpack faces plus 7 horizontal Heavy exclusions; 15 included generated selections across five cells of one 3×3 source sheet plus 8 included direct full-CardID/GUID/CustomDeck/FaceURL occurrences
  - 8 printed titles / 8 selected face assets, 4 explicit selector-gap cells, 1 parent sheet, and 1 shared non-operative back with 31 provenance references remain distinct; repeated copies and same-title MEDKIT variants are never collapsed
  - 85 physical panels / 69 physical regions / 62 operative panels / 46 exact printed sentences / 46 physical functional-icon occurrences (37 exact matches + 9 literal local no-matches)
  - 10 licensed `deck-green` rows / 30 declared copies remain independent and aggregate-reconcile to 23 regular + 7 Heavy without a TTS copy crosswalk; no official visible exact Green face or back is claimed
  - reusable finite deck, unlimited private Backpack, Use Item, One Use Only, voluntary discard, Trade/gain, Interplay, restoration, and exact MEDKIT immediate-use procedures preserve payment, consent, target, visibility, and lifecycle boundaries
  - seven new no-default questions retain Use/discard order, deck exhaustion, selected local glyphs, Contamination Codes Door allocation, restoration ownership, Interplay gain-glyph scope, and multiple immediate-use timing
  - Heavy Items, red/yellow decks, Starting/Equipment Items, Tactical Gear, parent sheet, shared back, selector-gap variants, overlays, placeholders, and duplicate references remain excluded from the 23 regular Green rules occurrences
- base source-clear regular Red Item family: **21/21 mechanically derived physical occurrences represented**
  - exact 30-child `redItemsDeck` root retained as 21 source-clear regular faces, 3 explicit Heavy `REMOTE DETONATOR` exclusions, and 6 `MILITARY TASER` physical-class conflicts; 7 included generated selections across four cells of one 4×2 Red sheet plus 14 included direct full-CardID/GUID/CustomDeck/FaceURL occurrences
  - 7 regular printed titles / 7 selected regular face assets, 4 Red selector-gap variants, 3 cross-family Yellow-sheet selector gaps (including 1 non-rules cell), 2 parent sheets, and 2 non-operative backs remain distinct; repeated copies and same-title Ammo/Grenade/Exploring variants are never collapsed
  - 87 physical panels / 63 physical regions / 66 operative panels / 45 exact printed sentences / 27 regular physical functional-icon occurrences (23 exact matches + 4 literal local no-matches)
  - 9 licensed `deck-red` rows / 30 declared copies remain independent and aggregate-reconcile to 21 regular + 9 Heavy without a TTS copy crosswalk; one official-visible Heavy Military Taser occurrence controls only its exact publisher occurrence and identifies no TTS GUID
  - reusable finite Red-root/One Use/immediate-use, Ammo reload/spend, Grenade effect, and Anti-Aircraft hidden-order/lifecycle procedures reuse generic Backpack/Use/Trade/Interplay/Tactical Gear/Movement/Exploration/Door semantics without inventing nested costs or source identity
  - five new no-default questions retain selected local glyphs, Military Taser class/current correspondence, Exploring Drone target context, Personal Log Objective secrecy, and Portable Barrier Door/FAQ applicability; shared Item questions now cover Red exhaustion, Interplay gain scope, and multiple immediate-use windows
  - Green/Yellow decks, Starting/Equipment cards outside exact root selectors, Heavy/class-conflict effects, Tactical Gear/ammo tokens, parent sheets, backs, gaps, overlays, placeholders, and duplicate evidence references remain excluded from the 21 regular Red effect records
- base source-clear regular Yellow Item family: **24/24 mechanically derived physical occurrences represented**
  - exact 30-child `yellowItemsDeck` root retained as 24 source-clear regular faces and 6 Fire Extinguisher/Robot Controller physical-class conflicts; 11 included generated selections across Duct Tape/Tools cells plus 13 included direct Phosphates/Oxygen Tank full-CardID/GUID occurrences
  - 4 regular printed titles / 4 selected regular face assets, 5 selector gaps across two 2×2 sheets, 2 non-operative BackURL forms, and exact `UniqueBack` cell selection remain distinct; repeated copies and same-title direct/sheet variants are never collapsed
  - complete root anatomy totals 158 panels / 90 regions / 68 printed sentences / 60 functional glyphs (44 exact matches + 16 literal local no-matches); the 24 regular occurrences account for 128 panels / 72 regions / 56 sentences / 48 glyphs (32 matches + 16 no-matches)
  - 6 licensed `deck-yellow` rows / 30 declared copies remain independent and aggregate-reconcile to 24 regular + 6 Heavy without a TTS copy crosswalk; one official-visible Duct Tape occurrence controls only its exact publisher occurrence and identifies no TTS GUID
  - reusable finite Yellow-root/One Use/immediate-use, Oxygen gain/token, local Malfunction discard, and Reinforce procedures reuse generic Backpack/Use/Trade/Interplay/Tactical Gear/Door semantics without inventing target owners, class identity, or lifecycle defaults
  - six new no-default questions retain selected local glyphs, Fire Extinguisher/Robot Controller class correspondence, Duct Tape source/One Use/stacking/Trade lifecycle, Phosphates target scope, and Tools Door ownership/accessibility; shared Item questions now cover Yellow exhaustion, Oxygen-token Interplay scope, and immediate-use windows
  - Green/Red decks, Starting/Equipment cards outside exact root selectors, six class-conflict effects, Tactical Gear/tokens, parent sheets, backs, gaps, overlays, placeholders, and duplicate evidence references remain excluded from the 24 regular Yellow effect records
- complete base Action family: **60/60 mechanically derived physical occurrences represented (10 per Character)**
  - 55 exact Character-kit selectors plus 5 exact Shared Contractor selectors compose six ten-card decks; all copies retain full CardID/GUID/CustomDeck/FaceURL/BackURL/container provenance
  - 39 direct faces plus 21 selected generated cells across two 9×5 sheets; 29 source-clear base selector-gap cells and 40 expansion cells remain explicit exclusions
  - 60 selected face assets / 32 printed titles / one shared non-operative back with 273 global references; repeated and cross-Character titles never collapse physical or semantic occurrences
  - 290 physical panels / 136 operative panels / 164 exact printed sentences / 143 physical functional-icon occurrences (129 source-resolved + 14 literal local no-matches)
  - 28 source-resolved Not In Combat occurrences, 8 unresolved upper-right local morphologies, and 24 absent upper-right regions remain source-scoped; no licensed-flag default is imported
  - 60 independent licensed rows retain 6 Reactions, 7 `command=true`, and 35 `noIntruders=true` occurrences with zero asserted TTS-copy identity links; 4 official visible faces, 2 visible backs, and 8 FAQ obligations remain independent
  - 60 physical main-effect records plus exact Action setup/play/payment/draw/reshuffle/Reaction/Command dispatch and 6 Reaction-panel records; 18 new no-default questions retain glyph, payment, owner, consent, target, ordering, interruption, shortage, and lifecycle boundaries
  - expansion Character decks, draft cards, Contamination, Starting Items, parent sheets, shared back, selector gaps, cross-family cells, placeholders, and duplicate evidence references remain excluded from the 60 physical rules occurrences
- base competitive Objective/Mission family: **30/30 mechanically derived physical copies represented at their source boundary (29 source-clear + 1 exact-source blocker)**
  - exact competitive partition is 7 Mission Objective, 15 Private Objective, and 8 Mission Task copies; five OFFICIAL ORDER copies retain separate root sequence/full CardID/GUID/copy identities despite the repeated label
  - 16 generated physical copies plus 14 direct physical copies; 50 exact face assets, 13 base-selected cells, 18 base selector-gap cells, two parent sheets, and two shared backs with 33 Objective plus 11 Mission Task global references remain role-distinct
  - the three competitive TTS roots retain 11 Mission, 20 Personal, and 8 Mission Task children; four high-count Mission and five Corporate prototype selectors are explicit physical exclusions, while two Solo/Coop roots retain 12 + 26 separately excluded selectors
  - 149 physical panels / 53 exact printed sentence occurrences / 39 physical functional-icon occurrences (7 source-resolved + 32 literal local no-matches) / 1 persistent checkbox occurrence; exact Number-of-Characters metadata, AND/OR grouping, punctuation, sheet cells, source selectors, and visibility remain locked
  - all 45 official Objective Help units are linked independently: 35 fully visible and 10 physically occluded, with 20 visible card records, 50 fully visible icons, 5 partial icons, and zero promotion of hidden PDF text-layer, TTS, or BGA wording into occluded official faces
  - 38 licensed rows remain independent: 26 competitive (18 Objectives + 8 Mission Tasks) and 12 Solo/Coop exclusions, with zero asserted physical-to-licensed or physical-to-official identity links
  - 29 exact TTS physical-face, 20 official-visible-face, and 26 licensed competitive occurrence records plus reusable setup, secrecy/discussion/inspection, Objective Choice, fulfillment, Survivor/Escape, Facility destruction, Mission Task/check, and exact occurrence dispatch procedures; SEM-Q-075–078 retain OR-branch, continuous-unfulfilled, late-choice/reward, and reveal-order alternatives without defaults
  - Objective Choice now resolves private removal/retention, public track movement, then the post-move 3/2/2/1/1 Action-card reward; removed/dead-owner identities stay private, while selected Mission Tasks and source-defined endgame reveals remain public
  - the exact TTS `FACILITY RESTART` face remains the sole source-blocked physical occurrence; its materially different fully visible official and licensed occurrences are encoded independently and never substituted into the blocked pixels
- all 18 Intruder Help instructions represented and row-locked
- all 25 Room Help entries represented, plus generic Use Room and cross-cutting Room constraints
- all 112 source-local Room Help functional-icon occurrences mapped source-scoped without changing extraction records
- core Combat/Attacks/Noise/Hazard/entry batch closed at its source-clear boundary
  - paid Move/Shoot/Burst/Melee Basic Actions separated from reusable source-effect sequences
  - 9 attack classes and 6 movement classes retained without flattening; immediate entry/Secure/prevention timing is explicit
  - exact official Noise `1`/`2`/`3`/`4`/`Hazard`, Deadly dual values, Shoot/Burst/Melee result tables, Hit allocation, Intruder type Health, token front/back/context, and finite supply encoded
  - 9 rendered visual obligations closed: `RB-P24-V02`, `RB-P25-V01/V02`, `RB-P30-V01/V02`, `RB-P33-V01/V02`, `RB-P34-V01`, and `RB-P40-V01`
  - 9 new no-default questions retain Corridor/Intruder order, bag/Attack-deck exhaustion, Blank-row scope, death interruption, Larva continuation, Burst resolution, and mixed Adult/Drone allocation
  - 2 new conflicts preserve the official current Noise set versus stale unbound TTS Silence/Danger branches and the side-level Blank-panel scope boundary
  - bounded Facility/map topology and setup-state batch closed at its source boundary
    - 12 exact rulebook setup/map source segments, 21 regular rendered Room slots, 6 edge directions, and 43 reserved paired Corridor gaps
    - three Sections corrected as A/green, B/blue, and C/red; Landing Zone and Hibernatorium remain separate fixed border-piece named spaces
    - 23 Room tiles and 40 Corridor tiles retain exact subtype/value counts; Room/Corridor/round-track/Character-board/marker setup states remain distinct from later lifecycle
    - 19 selected setup/map visual obligations, including map geometry, Room/Door/marker/token faces, are source-linked without text/geometry flattening
    - 5 new no-default setup questions and 6 new conflicts preserve orientation, special-space endpoint, shortage, marker identity, and proximity/connection boundaries
  - 600 source-obligation backlog units
  - 530 pilot-covered
  - 69 pending
  - 1 inherited exact-source blocker
- full base-game semantic coverage explicitly not claimed
- four-workstream independent review incorporated
- cross-seed/cross-locale byte-identical rebuilds and expanded adversarial corruption tests pass
- `scripts/validate_semantic_pilots.py`: **passed with 0 failures**, including cross-seed/cross-locale rebuilds and 48 focused/adversarial tests

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

1. **Correctness audit** — execute the locked 140-unit stratified blind source audit.
2. Repair confirmed concise-rule defects and preserve unresolved policy as explicit gates.
3. Expand affected families or the full planning inventory only if the preregistered error thresholds require it.
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

- One prototype `FACILITY RESTART` face visibly ends a condition at “Systems must be”; no following mark is recoverable from the exact pixels, and materially different same-title/current-official variants cannot be substituted.
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

1. Use the `nemesis-card-corpus` workspace and hold its root lock only while actual workspace work is running.
2. Read this file, `AGENTS.md`, `AGENTS-SUPPLEMENT.md`, and the threat-model/proportional-execution section of `docs/qa/implementation-readiness/correctness-audit/methodology.md`. Do not read historical candidate reports unless diagnosing a named regression.
3. Verify branch, HEAD, dirty/protected scope, active workers, and that the active v2 lock file is absent; do not infer state from an old transcript.
4. Execute the Immediate Next Deliverable directly. Do not launch another harness review, create reviewer worktrees for read-only work, or run hostile-filesystem probes.
5. Run the exact normal prelock commands in the methodology. A clean green gate is sufficient to promote the current checkpoint and create the direct-child lock.
6. After the lock and post-lock gate pass, continue autonomously with a small substantive source-packet batch. Use compact results; clean temporary workers/workspaces immediately after integration.
7. Update this file only when material status changes. Commit or push only within the authorized boundary; do not open a PR or deploy without explicit approval.
