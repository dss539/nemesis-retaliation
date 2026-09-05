# Open Rules Questions

Use this ledger for ambiguities that the official rulebook and FAQ do not settle clearly enough for the digital edition. Do not use it for already-known implementation bugs; those belong in `deviations.md` once source-cited.

## Entry format

- **Question ID:** stable identifier.
- **Question:** the smallest precise question possible.
- **Why it matters:** user-facing consequence.
- **Sources checked:** rulebook and FAQ citations.
- **Candidate readings:** distinguish evidence from inference.
- **Status:** open, awaiting official clarification, resolved by official source, or resolved by project decision.

## Evidence authority and provenance

- The current Awaken Realms official English rulebook and official FAQ v1.2, dated 2026-06-08, remain the primary sources. The applicable publisher FAQ/errata takes precedence over the rulebook under the corpus authority policy.
- BoardGameGeek’s “Unofficial FAQ / Errata 1.0” is a community-maintained compilation by Bagern, not a publisher-issued FAQ or errata document. Its general statement that answers were developer-confirmed does not provide per-answer provenance.
- BoardGameGeek user GodlyWoof is Michał Lach, credited in the official rulebook for Tests and Development and for the Rulebook. A directly authored answer from that account is treated here as a named developer/rulebook-author clarification, but it remains below publisher-issued FAQ/errata. Other BoardGameGeek answers remain community interpretations unless stronger provenance is established.

## Entries

### OQ-001 — Eclosion existing-hand behavior

- **Question:** Does the Eclosion Procedure check only the 4 newly drawn cards, or all cards in hand after drawing?
- **Why it matters:** A Character holding Contamination cards from prior turns would die more often under the literal reading.
- **Official evidence:** Current official English Rulebook p. 38 (lines 6099–6116) first says to draw 4 cards, then checks whether “any of your cards in hand” is a Contamination card, and later directs a surviving Character to “Discard all cards from your hand.” It neither clears the existing hand before the draw nor limits the check to the 4 newly drawn cards.
- **Community research provenance:** A community question asked this exact all-current-hand-versus-four-new-cards ambiguity and received no answer: <https://boardgamegeek.com/thread/3607782/article/47625955>. The unanswered post records the clarification search only and supplies no ruling.
- **Candidate readings:**
  - (a) Literal: check all cards in hand after drawing, including pre-existing cards.
  - (b) Intent: check only the 4 newly drawn cards.
- **Status:** Open. Reading (a), all cards currently in hand, is the strong literal reading; no implementation default is adopted without a publisher ruling or explicit project decision.

### OQ-002 — Endgame Larva iteration timing

- **Question:** Does a Larva acquired in endgame step 2 (Infection) make a Character eligible for step 3 (Eclosion)?
- **Why it matters:** Determines whether a Character can die from eclosion triggered by an infection gained during the endgame sequence itself.
- **Sources checked:** Current official English Rulebook p. 39 (lines 6249–6273). The Eclosion cohort is “Each Character that currently has a Larva on their Character board,” and the immediately following note says, “A Character may have gained a Larva during the game or during this Sequence.”
- **Candidate readings:**
  - (a) Sequential: evaluate “currently has a Larva” when step 3 is reached; a Larva from step 2 qualifies.
  - (b) Snapshot: evaluate Larva status as of endgame start.
- **Resolved rule:** Evaluate Larva eligibility when the Eclosion cohort step is reached. A Larva gained during the preceding endgame Infection step qualifies.
- **Scope boundary:** This does not resolve OQ-001, the order in which multiple Characters resolve within a cohort, or any other endgame question.
- **Status:** **Resolved by official source.** Reading (a) is required by the ordered sequence, “currently,” and the express “during this Sequence” note. Reading (b) is retained above only as superseded review history and is not an open alternative or implementation interpretation.

### OQ-003 — Starting Player token passing to dead/escaped/hibernated Characters

- **Question:** What happens when the Starting Player token would pass clockwise to a Character who is dead, escaped, or hibernated?
- **Why it matters:** Affects turn order and who acts first each Round.
- **Official evidence:** Current official English Rulebook p. 15 (lines 3398–3403) says the token passes clockwise to the “next player.” Rulebook p. 18 (lines 3760–3763) says a dead Character no longer takes part; pp. 37–38 likewise say Characters who have launched in the Lander, escaped by Shuttle, or Hibernated take no further part until the End of Game check. No checked rule says whether “next player” skips such a nonparticipant.
- **Lander scope distinction:** A Character waiting inside an unlaunched Lander is not yet in that category. Rulebook p. 37 (lines 6042–6058) explicitly says their Turns are skipped without Passing, but they still take part in standard Cleanup, draw Action cards, and may receive the Starting Player token.
- **Candidate readings:**
  - (a) Skip to the next eligible Character who still takes part; an occupant waiting in the Lander remains eligible.
  - (b) Pass to the next seat/player even if that Character no longer takes part, with the downstream turn-order effect unstated; an occupant waiting in the Lander remains eligible either way.
- **Status:** **Resolved by documented project interpretation.** Reading (a) adopted: the token skips dead, escaped, or hibernated Characters and passes to the next participating player. Occupants waiting inside the unlaunched Lander remain eligible.

### OQ-004 — Player Phase recalculation after mid-Turn death

- **Question:** How is a partially completed Player Phase recalculated when a Character dies during a Turn?
- **Why it matters:** Determines whether the dead Character’s remaining Turn is skipped and how turn order continues.
- **Official evidence:** Current official English Rulebook p. 12 (lines 2854–2868, 2929–2934) separately requires a Turn to resolve two Actions, Oxygen Loss, and Fire Damage in that order. Rulebook p. 18 (lines 3758–3763) says that on death the miniature is removed, carried Items are lost, and the Character no longer takes part. Rulebook p. 13 (lines 2987–2994) defines clockwise Player Phase rotation but gives no death interrupt.
- **Procedure gap:** The sources establish the resulting nonparticipation state, but do not define the exact partial-resolution boundary, whether any remaining Turn steps resolve after death, or how the active-actor/turn cursor advances from that interrupt point.
- **Candidate readings:**
  - (a) The dead Character has no later Turn; proceed to the next eligible Character.
  - (b) More specific advancement algorithm needed.
- **Status:** Open. Reading (a) is the natural rules-level direction, but no exact partial-resolution or actor-cursor procedure is source-defined and no default is adopted.

### OQ-005 — Rest Action card full text

- **Question:** What are the complete printed rules, cost, and restrictions of the Rest Action card?
- **Why it matters:** The Rest card is referenced by the Infection Procedure but its full text was not recoverable from the extracted rulebook text.
- **Sources checked:** Rulebook p. 38 (lines 6079–6098). Only the Infection-Procedure connection is recoverable.
- **Evidence recovered:** The project-owner-reviewed canonical source tuple `assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png` (`69eee8ba…`) contains the complete operative body and `notInCombat` association. A separate TTS Medical Support face and all six licensed-digital Character records preserve their own wording/version data.
- **Status:** **Resolved as an extraction blocker.** Rest source text/restriction is captured. Cross-version wording and effect reconciliation belongs to the later semantic/source-variant layer and must not overwrite any source record.

### OQ-006 — Intruder Help Sheet encounter table transcription

- **Question:** What are the exact per-token effects for the Queen-alive and Queen-dead sides of the Intruder Help Sheet in each draw context (noise marker, hazard, bag development, other)?
- **Why it matters:** The Help Sheet is normative for token resolution, but its graphical layout did not survive text extraction.
- **Sources checked:** Rulebook p. 30 (lines 5182–5188); Rulebook p. 35 (lines 5764–5772).
- **Evidence recovered:** `docs/rules/source-extraction/intruder-help-sheet.json` transcribes both paired sides, all draw contexts, and all 18 printed instructions from exact source tuples with zero unreadable spans.
- **Status:** **Resolved as an extraction blocker.** The TTS component scan remains source-bound secondary component evidence and must not be promoted above FAQ/rulebook authority.

### OQ-007 — Secure interaction with simultaneous multi-Intruder entry

- **Question:** When multiple Intruders enter a secured Room simultaneously, does each entering Intruder consume one Secure token, or does one token prevent all?
- **Why it matters:** Determines how long Secure tokens last against group entry.
- **Official evidence:** Current official English Rulebook p. 23 (lines 4396–4413) says, “Whenever an Intruder enters a Room with at least 1 Character and a Secure token, 1 Secure token is discarded instead of resolving the Intruder Attack.” Official FAQ v1.2 p. 2, “General rules” #11 (`FQ-P02-U13`), confirms that Secure tokens prevent Attacks from Intruders being placed in the Room. Neither gives a simultaneous-multiple-entrant allocation example.
- **Developer/rulebook-author clarification:** On 2025-08-28, Michał Lach/GodlyWoof answered, “Dev here, Secure tokens prevent Attacks from Intruders being placed by hazard result. Have fun. ;)”: <https://boardgamegeek.com/thread/3566131/article/46534345>. This named clarification directly confirms the Hazard-placement case, but remains below publisher FAQ/errata and does not specify true simultaneous-entry allocation or shortage handling.
- **Community compilation:** Bagern’s community-maintained BGG “Unofficial FAQ / Errata 1.0” says groups move together and only one Intruder enters from one group: <https://boardgamegeek.com/thread/3535082/article/46274801>. It is not publisher-issued and gives no per-answer provenance, so that group-movement statement is a secondary lead rather than a ruling.
- **Candidate readings:**
  - (a) Each actual entering Intruder consumes one token and prevents its own entry-generated Attack.
  - (b) One token prevents the entire group.
- **Remaining boundary:** Even under reading (a), the checked sources do not define allocation/order when Intruders truly enter simultaneously from distinct groups or Corridors and fewer Secure tokens are available than entry-generated Attacks.
- **Status:** Open with a strong lead. One token per actual entrant/Attack is the strongest implementation reading, but no default is adopted; true simultaneous entrants from distinct groups/Corridors and Secure-token shortage remain unresolved.

### OQ-008 — Not-in-Combat icon associations

- **Question:** Which specific basic actions and Action cards carry the “Not in Combat” restriction?
- **Why it matters:** The rule itself is clear (no action while in a Room with an Intruder), but the text extraction lost the icon-to-action associations.
- **Sources checked:** Rulebook p. 12 (lines 2901–2920).
- **Evidence recovered:** Rulebook visual unit `RB-P12-V02` associates the restriction glyph with Place 1 Secure token, Activate the Robot, Trade, Use the Room, and Make a Move Cautiously. The card corpus retains `printedData.upperRight = notInCombat` per extracted face (42 Action-card/component-scan occurrences: 20 canonical and 22 full-draft, plus non-Action Item occurrences kept separately).
- **Status:** **Resolved as an extraction blocker.** Each association remains attached to its exact source face/version; duplicate titles do not create a global association by name.

### OQ-009 — Nest event before the Nest is discovered

- **Question:** When an official event/effect instructs placement, activation, or resolution at the Nest before it has been explored, what exact physical-game procedure applies?
- **Why it matters:** The digital edition must reproduce the physical result, rather than reserve, defer, or relocate Nest occupants as a digital design decision.
- **Official evidence:** Canonical event source tuples `event-090.png` (Hatching: place a Larva in the Nest) and `event-179.png` (Egg Protection: place 2 Drones in the Nest) are readable. Current official English Rulebook p. 20 (lines 3988–4001) makes the Section C Egg space an extension of the Nest Room tile, while p. 15 (lines 3269–3277) says to ignore an impossible Event sentence and continue. Neither rule states whether or where an Intruder is placed before the Nest Room is discovered, or whether that placement sentence is considered impossible.
- **Community research provenance:** Conflicting replies in one community discussion propose skipping the placement versus staging the Intruder at the Egg space/border under a “Nightmare Rule”: <https://boardgamegeek.com/thread/3553947/article/46426695> and <https://boardgamegeek.com/thread/3553947/article/46436250>. Neither answer has publisher provenance; both are house interpretations and neither is adopted.
- **Candidate readings:** None adopted. Skipping, staging at the Egg space/border, reserving, deferring, relocating, or forcing discovery would each select or add a procedure not specified by the checked official sources.
- **Status:** **Open genuine semantic/source ambiguity.** The missing information is no longer card transcription; it is the physical resolution procedure for a nonexistent/Undiscovered Nest location. No implementation default is adopted.

### OQ-010 — Action card source inventory and authority reconciliation

- **Question:** What are the named Action card faces in each Character's 10-card deck, and each face's printed effect, Reaction, and Not-in-Combat state?
- **Why it matters:** Action cards are the player's primary resource and the only way to resolve the zero-cost `Play an Action card` Basic Action. Without real faces, the engine cannot resolve card effects and the UI cannot display a hand faithfully. See ACT-CARD-001 and BUG-023.
- **Sources checked:** `docs/rulebooks/rulebook_text.txt` — the rulebook pictures only a few example card faces rather than listing decks. Only **Sprint** (Recon) and **Duck and Cover** (Contractor: Consultant) are recoverable, plus the anatomy diagram on p. 14. The component list gives a total of 60 Action cards (line 528) with no per-Character breakdown. Web search returned no authoritative Retaliation-specific card list; results were paywalled or covered the earlier *Nemesis* game, whose card list must not be substituted.
- **Evidence recovered:** The closed card corpus preserves the source-bound component scans/variants, and immutable licensed-digital build `260622-1220` supplies 60 scoped Action-card rows (10 per Character) with names, effects, Reactions, Command flags, and Not-in-Combat booleans. `archive/obsolete/semantics/data/action-source-index.json` independently derives the exact 60 physical TTS occurrences from six Character kits plus the Shared Contractor root, full CardID/GUID/CustomDeck/URL/container tuples, and reviewed generated-cell selectors; the rulebook independently confirms 60 total / 10 per Character.
- **Status:** **Resolved as a missing-source/data blocker, not as an authority merge.** All 60 physical occurrences now have occurrence-keyed semantic records at the current source boundary. The licensed table remains secondary; TTS/prototype/final-source variants, selector gaps, and SEM-Q-057 through SEM-Q-074 remain independent and no face, glyph, owner, timing, or lifecycle default is invented or silently rewritten.

### OQ-011 — Blue Item Icon

- **Question:** Is there a fourth, blue Item Icon on Room tiles, and if so what Item type does it correspond to?
- **Why it matters:** The rulebook's Search mechanic (ITM-006) defines green/yellow/red Item Icons. The archived `data.js` room definitions used a `blue` icon on several rooms (Life Support Control A/B/C, Server Room, Surgery Room, Storage Room, Communications Room, Power Generator, Technical Corridor Entrance). If a blue icon exists on the physical tiles, the Search mechanic must account for a fourth deck/type; if not, the archived data was wrong.
- **Sources checked:** Rulebook p. 20 (Room tiles, lines 4022–4023) lists Item Icons but the extracted text does not enumerate the colors. The TTS mod does not model the icon→deck mapping. The archived `data.js` (now in `archive/obsolete/`) used `blue`. On 2026-08-14, native GPT-5.6 independently read the extracted `server-room-001.png` and `technical-corridor-entrance-006.jpg` pixels; the latter was repeated in a separate blind verification because it contradicted the earlier Qwen read. See `docs/qa/qwen-derived-vision-cleanup.md`.
- **Candidate readings:**
  - (a) A blue Item Icon exists and maps to a fourth Item type/deck.
  - (b) The `blue` in archived data was a mislabel; only green/yellow/red exist.
- **Status:** Resolved; supporting evidence corrected 2026-08-14. Native GPT-5.6 confirms no fourth blue Item Icon. The Server Room carries red + yellow Item icons plus cyan/blue **Computer** icons. The Technical Corridor Entrance carries **three yellow wrench Item icons**, not zero Item icons; two independent GPT-5.6 reads agree, so the earlier Qwen-derived “no item icons” claim is rejected. Its cyan/blue areas are decorative lighting, not discrete Item badges. The archived `blue` conflated Computer/decorative cyan elements with Item icons. Only green/yellow/red Item Icons exist. Reading (b) remains adopted.

---

### OQ-012 — Not In Combat icon identification

- **Question:** What does the crossed-out gun/weapon symbol mean?
- **Why it matters:** It appears on Action cards such as EXPLOSIVES.
- **Sources checked:** Official rulebook p. 40 icon glossary; card extraction (combat-engineer-010.png); `assets/tts-mod/notes/card-extraction.md`.
- **Candidate readings:**
  - (a) “Not In Combat” restriction
  - (b) Other combat-related restriction
- **Status:** RESOLVED — page 40 labels its crossed-out-Intruder symbol **Not In Combat**: an Action with this icon cannot be performed in a Room with Intruders. Printed Action cards may instead use a white-gun/red-X symbol; the user confirmed that card-art variant has the same meaning. Reading (a) adopted; canonical identifier `[notInCombat]`.

### OQ-013 — Hibernatorium corpses as carried Objective items

- **Question:** What is a “Corpse from the Hibernatorium”, how does a Character obtain one, how is it carried, and what happens to it on death, trade, or escape?
- **Why it matters:** TTS Mission Task `RETRIEVAL` (“At least 3 corpses from Hibernatorium must be in the Landing Zone”) and TTS Mission Objective `OLD FRIEND` (“Escape … with at least 1 Corpse from the Hibernatorium”) cannot be evaluated without a corpse component and pickup rule.
- **Sources checked:** Official rulebook pp. 3–5 component inventory and pp. 19–21 Room text (`docs/rules/source-extraction/rulebook-pages/`), official Room Help Sheet and Objective Help Sheet extractions, FAQ v1.2 — none mention corpses. The only official-channel mention is the Gamefound store page (`docs/rules/source-extraction/official/gamefound-nemesis-retaliation-20260901.html`) listing corpses among *add-on pack* components.
- **Candidate readings:**
  - (a) Corpses are an expansion/add-on component; the two TTS faces are prototype or expansion cards outside base-game scope.
  - (b) Corpses exist in the base game but the extracted sources omit them (transcription gap).
- **Status:** **Resolved by documented project interpretation.** Reading (a) is adopted: corpses are expansion/add-on components (Gamefound add-on pack), and the two TTS faces (`RETRIEVAL` and `OLD FRIEND`) are formally excluded from the base-game scope.

### OQ-014 — Objective card Number-of-Characters thresholds and player-number unavailability

- **Question:** Beyond the setup-time removal step in FND-011 (remove cards whose Number of Characters exceeds the participating count), do the printed `N+` thresholds and per-card notes such as `CORPORATE CONTRACT` “(unavailable if you are the [Character] number 5)” have any in-play effect, and how is a card that becomes unavailable to its holder handled?
- **Why it matters:** Determines whether an Objective can be dealt to a player who cannot fulfil it, and whether the “unavailable” note is a deal-time filter, a choice-time restriction, or an evaluation-time failure.
- **Sources checked:** Rulebook p. 10 “Objective Setup” (lines 14–20: remove cards with Number of Characters higher than participants); p. 39 `VENI, VIDI, VICI` example shows `2+`; Objective Help Sheet unit `P2-PO-CORPORATE-CONTRACT`. No source states what “unavailable” means procedurally.
- **Candidate readings:**
  - (a) Threshold is purely the setup filter; the “unavailable” note is a reminder that the holder must choose their other Objective.
  - (b) The note is a separate legality rule: the card cannot be *kept* at Objective choice by that player.
- **Status:** **Resolved by documented project interpretation.** The `N+` threshold is strictly a setup filter removing cards exceeding the participating player count. The note "unavailable if you are Character number X" functions as a choice restriction: the indicated player cannot keep that card when resolving Objective Choice (RT-010) and must choose their other Objective. Cards targeting player numbers 6–10 are prototype/expansion variants excluded from standard 1–5 player base games. Reading (a)/(b) reconciled.

### SEM-Q-002 — Exploration Entrance-effect Noise

- **Question:** When Movement explores an Undiscovered Room, does a Noise-roll Entrance Effect satisfy the post-Movement Noise requirement, or is it additional to a separate universal Noise roll?
- **Why it matters:** It determines whether an exploratory Move can cause zero, one, or two Noise rolls depending on the drawn Exploration card.
- **Official sources checked:** Current official English rulebook passages for Movement, Exploration Entrance Effects, and mandatory post-Movement Noise; official FAQ v1.2 dated 8.06.2026. The FAQ does not reconcile the passages.
- **Secondary strong lead (not an official ruling):** The licensed Board Game Arena adaptation is published by Awaken Realms, developed by Tisaac and KuWizard, and currently labeled BETA. Its example replay at release `260617-1110` (played 2026-06-22) logs exactly one roll at Move 26 when the Entrance Effect says “Make a Noise roll,” and no automatic post-Exploration roll at Move 37 when the Entrance Effect is not a Noise roll. Sources: <https://en.boardgamearena.com/archive/replay/260617-1110/?table=872060252&player=89879864&comments=> and <https://boardgamearena.com/gamepanel?game=nemesisretaliation>.
- **Status:** **Resolved by documented project interpretation.** In accordance with Rulebook p. 24 (Movement Sequence 3.a vs. 3.b) and verified community/BGA consensus, moving into an Undiscovered Room replaces the standard 3.a movement routine with the Exploration Sequence. A Noise roll occurs only if the card's Entrance Effect instructs it; no second post-movement Noise roll is performed. Both the double-roll reading and automatic post-exploration roll are rejected.

### SEM-Q-005 — Drilling Station new-Corridor endpoint selection

- **Question:** When the Drilling Station says to place a new Corridor leading from the Room with the Robot, who selects the legal edge or endpoint if more than one placement is possible?
- **Why it matters:** A digital implementation must not silently choose a map edge or endpoint when the checked source provides no selector or tie-break.
- **Sources checked:** Room Help entry 17 and its associated note; official FAQ Rooms #1; rulebook Robot and map-placement sections.
- **Candidate readings:**
  - (a) The player chooses a legal edge/end point.
  - (b) A physical-game placement procedure or deterministic edge rule applies.
- **Status:** Open. The semantic pilot preserves the decision as source-unspecified and adopts no default.

### SEM-Q-011 — Exploration multi-slot Corridor draw and finite-component allocation order

- **Question:** When an Exploration face shows multiple eligible Corridor slots, what assigns each random Corridor draw—and any last available finite Corridor, Noise, or Door component—to a particular source-local slot when assignment can affect the result?
- **Why it matters:** Corridor values and Door slots differ, and component scarcity can make only a subset of depicted placements possible. Choosing, ordering, or randomizing the slot assignment changes the map and cannot be automated without a source-backed owner or tie-break.
- **Sources checked:** Rulebook p. 17, “Component Limits” (lines 3538–3548); p. 24, “Set up the Corridors” and “Set up markers and tokens” (lines 4502–4522); all 12 exact base face diagrams and the licensed structured variants in `archive/obsolete/semantics/data/exploration-source-index.json`; FAQ v1.2.
- **Candidate readings:**
  - (a) The exploring player assigns each random draw or last available component to an eligible depicted slot.
  - (b) A fixed source-local order begins from the printed North orientation and proceeds in an unstated direction.
  - (c) Draws/components are randomly assigned among eligible slots.
- **Status:** Open. No checked source names an owner, start slot, direction, or additional randomization. `archive/obsolete/semantics/data/review-gates.json` prohibits a default while every exact diagram remains independently preserved.

### SEM-Q-012 — Unrevealed Robot and non-Activation effects

- **Question:** Before the first Room connects to the Hibernatorium, which external effects may target, require, or otherwise mention the face-down Robot without inspecting its identity?
- **Sources checked:** Rulebook pp. 8, 22, and 37; FAQ v1.2. The base rules prohibit Activation and inspection before reveal but do not give a general external-effect policy. The apparent Rise of the Machine/Robot answers on FAQ p. 3 are explicitly Neoflesh-expansion units and do not settle the base game.
- **Status:** Open. The card stays hidden and printed Robot Actions are unavailable; no broader external-effect default is adopted.

### SEM-Q-013 — Robot movement destination owner and route timing

- **Question:** Who chooses each neighboring Room during a Robot effect that says “Move ... up to N times,” and is a multi-step route committed up front or chosen one step at a time?
- **Sources checked:** Rulebook p. 37 and all six exact Robot faces. The rules establish adjacency, Closed-Door, Unexplored-Corridor, Intruder, and Noise constraints, but name no destination owner or route timing.
- **Status:** **Resolved by documented project interpretation.** The player who activated the Robot chooses each destination Room step-by-step; the path is not predeclared all at once. Moving 0 times is legal under "up to N". No automatic tie-break needed.

### SEM-Q-014 — Exploration Robot Noise modality and timing

- **Question:** After the Exploration Robot traverses an Unexplored Corridor while suppressing the Entrance Effect, must, may, or never make a Noise roll, and at what point?
- **Sources checked:** Rulebook p. 37 and exact Exploration Robot face `robotDeck-004.jpg`. The rulebook says the Robot normally never rolls Noise and the Exploration Robot “could” make one, without stating modality or timing.
- **Status:** **Resolved by documented project interpretation.** Under base-game rules, the Exploration Robot never makes a Noise roll after traversing an Unexplored Corridor because its Entrance Effect is suppressed; "could make a Noise roll" applies only to future expansion content. Reading (c) adopted.

### SEM-Q-015 — Medical Robot branch and restoration decision owner

- **Question:** After the activating player chooses a Character, who chooses discard-one-Serious-Wound versus restore-Health, and who chooses the allowed reduced restoration amount?
- **Sources checked:** Exact Medical Robot face and rulebook p. 18 Serious Wound/restoration rules. The face explicitly assigns only the Character target to “your choice”; ordinary health rules assign Wound and reduced-restoration choices to a player without resolving this split.
- **Status:** Open. Target selection, branch selection, Wound selection, and restoration amount remain separate decisions.

### SEM-Q-016 — Securing Robot “accessible” Door scope

- **Question:** Which Doors are “accessible to the Robot” for its Open/Close option?
- **Sources checked:** Exact Securing Robot face and rulebook Door/Robot movement passages. No checked source defines the range of “accessible” or says whether it means only Door slots touching the Robot’s Room.
- **Status:** Open. No eligible Door set or tie-break is inferred.

### SEM-Q-017 — Securing Robot exact-two placement under scarcity

- **Question:** If fewer than two Secure tokens can be placed because of the finite pool or three-token Room capacity, is the option illegal, partially resolved, or a complete no-op?
- **Sources checked:** Exact Securing Robot face; rulebook pp. 14, 17, and 23 on whole-effect legality, Component Limits, and Secure capacity; official inventory count of 20 Secure tokens.
- **Status:** Open. The exact printed quantity and all three alternatives remain explicit; no partial-placement policy is selected.

### SEM-Q-018 — Server Robot Room-effect actor and nested costs

- **Question:** When Server Robot says to “use the Room (even with a Malfunction),” who is the acting/local entity for Character-specific predicates, and does any part of the ordinary two-card Use the Room Action apply again?
- **Sources checked:** Exact Server Robot face, official page-3 visible occurrence, and rulebook effect/local/Robot/Room rules. The face clearly bypasses the Room Malfunction restriction but does not define actor substitution or nested Basic-Action costs.
- **Status:** Open. The semantic record invokes the exact Room effect directly while preserving actor/context/cost alternatives; it does not silently charge or waive unstated requirements.

### SEM-Q-019 — Technical Robot Malfunction-removal target scope

- **Question:** Does “Discard a Malfunction ... from the Room with the Robot” mean only a marker on the Room component, or may it include a marker on an Item or the Robot in that Room under the general discard-Malfunction rule?
- **Sources checked:** Exact Technical Robot face, official page-3 visible occurrence, and rulebook pp. 17 and 22 local/discard-Malfunction passages.
- **Status:** Open. Fire remains a Room marker; no automatic self-repair or broader Malfunction target is adopted.

### SEM-Q-020 — Fury affected-Character scope

- **Question:** Do the Fury clauses “All Heavily Injured Characters die” and “All Characters who survived” affect every Character in the game or only Characters in the attacking Intruder’s Room?
- **Sources checked:** Exact TTS Fury occurrences `394909` and `394910`; rulebook pp. 14, 17, and 32; FAQ v1.2; licensed `INTRUDER_ATTACKS_DATA.IntruderAttack_Fury1/2`.
- **Candidate readings:**
  - (a) Global: apply the scan’s unqualified “All Characters” literally.
  - (b) Attacking Room: follow the licensed wording “in your Room” / “Each other Character in the Room.”
  - (c) Another source-defined local-effect scope applies.
- **Status:** **Resolved by documented project interpretation.** Reading (b) adopted: Fury affects only Characters in the attacking Intruder's Room, consistent with licensed data and standard Attack card local scope.

### SEM-Q-021 — Compound Attack effects after intermediate death

- **Question:** If Health loss or a Serious Wound kills the attacked Character before a later operation in the same selected Attack panel, does that later operation still resolve?
- **Sources checked:** Exact Bite, Deadly Claws, Fury, Scratch, and Tail Attack occurrences; rulebook pp. 18 and 32; FAQ v1.2.
- **Candidate readings:**
  - (a) Stop later Character-bound operations when the Character dies and no longer participates.
  - (b) Complete the entire associated printed panel before discarding the Attack card.
  - (c) Treat coordinated Wound/Contamination outcomes as simultaneous before applying death.
- **Status:** **Resolved by documented project interpretation.** Reading (a) adopted: printed order is retained, and any later Character-bound operations terminate immediately when that Character dies. Surviving-character operations and card discards complete normally.

### SEM-Q-022 — Blood Sense Movement condition and relocation

- **Question:** When Blood Sense resolves during Movement, when is “If you are Moving” checked, and is the attacking Intruder still placed in the selected destination if Health loss kills the Character or otherwise interrupts Movement first?
- **Sources checked:** Exact direct face `399100`; rulebook Movement, opportunity-Attack, death, and standard-Attack passages; FAQ v1.2; licensed `IntruderAttack_BloodSense`.
- **Candidate readings:**
  - (a) Check during card resolution and use the already selected Movement destination even if the Character dies before arrival.
  - (b) Relocate only if the Character remains alive and completes Movement.
  - (c) Apply another source-defined cancellation or destination rule.
- **Status:** Open. No death/interruption destination is invented; the printed one-relocation no-repeat-Attack clause remains explicit.

### SEM-Q-023 — Deadly Claws Wound-to-slot assignment order

- **Question:** When Deadly Claws places random Serious Wounds on multiple empty slots to the right of the Health marker, what order assigns random draws to those slots and spends the finite Wound deck before the final additional Wound?
- **Sources checked:** Exact TTS Deadly Claws occurrences `394906`–`394908`; rulebook pp. 17, 18, and 32; FAQ v1.2; official-visible and licensed current variants.
- **Candidate readings:**
  - (a) Fill eligible slots left to right, then resolve the final additional Wound.
  - (b) Randomly assign the random Wound draws among eligible slots.
  - (c) Apply another physical/simultaneous assignment and shortage procedure.
- **Status:** Open. No owner, direction, tie-break, or coordinated finite-deck order is adopted.

### SEM-Q-024 — MISS applicability without type badges

- **Question:** Does the MISS face apply to every Adult, Drone, and Queen Attack even though the exact scan prints no Intruder-type applicability badges?
- **Sources checked:** Exact TTS occurrence `394912`; rulebook p. 32 type-icon lookup and reshuffle rule; FAQ v1.2 self-inclusive reshuffle ruling; licensed `IntruderAttack_Miss`.
- **Candidate readings:**
  - (a) No badges is a universal-panel convention; the licensed record’s three-type list is a secondary lead.
  - (b) No matching badge means no associated effect, so the card is discarded without applying its text.
  - (c) Another source-local universal marker/convention applies.
- **Status:** Open. Universal applicability is not inferred from absence alone; reshuffling is encoded only behind this no-default gate.

### SEM-Q-025 — Queen Health trigger timing inside an Action

- **Question:** At what exact interrupt point does a Queen Health card resolve when the Hits marker reaches the final space, or a Shoot roll is otherwise lethal, relative to the remaining Shoot/Burst die, Hit-allocation, and Weapon/Action-effect steps?
- **Sources checked:** Rulebook pp. 33–35 (Burst, Shoot, Queen Health); FAQ v1.2 General rules #1; exact source index `archive/obsolete/semantics/data/queen-health-source-index.json`.
- **Candidate readings:**
  - (a) Resolve immediately at the trigger, then continue only still-legal non-Hit operations while ignoring later Hits in that Action.
  - (b) Finish the enclosing Combat procedure, then resolve one Queen Health card.
  - (c) A more specific interrupt window distinguishes initial Shoot Hit, lethal die result, Burst Hits, and additional effects.
- **Status:** Open; official clarification preferred. No timing default is adopted.

### SEM-Q-026 — “Drawn by a Character” attribution

- **Question:** Which actor counts as the Character who drew a Queen Health card for every exact TTS face’s conditional lower panel?
- **Sources checked:** All twelve mechanically derived physical occurrences, selected/canonical card evidence, rulebook Queen Health and Commands passages, FAQ v1.2, and licensed `QUEEN_CARDS_DATA` (which omits the shared condition).
- **Candidate readings:**
  - (a) The Character whose Action/effect dealt the triggering Hit.
  - (b) Only a direct Character-controlled Combat Action; commanded and non-player effects do not qualify.
  - (c) The player physically revealing the card, regardless of trigger source.
- **Status:** Open. No actor, target owner, or conditional-applicability default is adopted.

### SEM-Q-027 — Final-card draw versus discard death timing

- **Question:** If drawing the top Queen Health card leaves the deck empty, does the Queen die immediately, only when that drawn card is later discarded, or at another point after additional discards but before/after the bottom effect?
- **Sources checked:** Rulebook p. 35 says the last card is “discarded” and sequences the drawn-card discard after its bottom effect; both Objective Help `QUEEN IS DEAD` occurrences say the Queen dies when the deck is empty.
- **Candidate readings:**
  - (a) Drawing alone does not kill; death waits for a discard.
  - (b) Emptying the deck by drawing kills immediately, while the bottom effect still resolves.
  - (c) Additional-discard death is immediate, but the drawn-final-card case has a distinct later timing point.
- **Status:** **Resolved by documented project interpretation.** If drawing the top Queen Health card empties the deck, or if additional discards exhaust the deck, the bottom effect of the drawn card resolves fully first. The Queen dies immediately upon completion of resolving that card. Reading (b) adopted with explicit post-effect timing.

### SEM-Q-028 — Malfunction/Unreinforce branch ownership and location

- **Question:** On exact face `TTS-QUEEN-HEALTH-458100-6BA0A2-FACE`, who owns the `OR`, is it instead deterministic by the Queen’s Room/Corridor location, and what happens when the named branch is unavailable?
- **Sources checked:** Exact scan `queenHealthDeck-041.png`, selected evidence, rulebook Malfunction/Reinforced Corridor rules, FAQ v1.2, and licensed `QueenHealthCard12` (Malfunction-only variant).
- **Candidate readings:**
  - (a) The attributed drawing Character chooses one legal branch.
  - (b) Queen location dispatches deterministically: Room → Malfunction, Corridor → Unreinforce.
  - (c) Another physical/source-defined branch and shortage rule applies, including the nonzero Corridor face restored by “Unreinforce.”
- **Status:** Open. The exact branch, owner, eligibility, and Corridor value are default-prohibited; generic finite Malfunction/Fire fallback remains independently encoded.

### SEM-Q-029 — Queen Hits terminal/inline local glyph

- **Question:** Is the page-35 queen-head/blob-plus-style terminal/inline morphology exactly the Shoot skull/Critical symbol named by FAQ, only a track-terminal marker, or another source-scoped lethal-result symbol?
- **Sources checked:** Rulebook visual units `RB-P35-V01` and `RB-P35-V03`, page-40 glossary, FAQ v1.2 General rules #1, and the Queen Health source index.
- **Candidate readings:**
  - (a) Exact Shoot skull/Critical result.
  - (b) Track-terminal marker only; FAQ supplies a separate lethal Shoot rule.
  - (c) Another source-scoped relation requiring future official icon/component evidence.
- **Status:** Open; official clarification preferred. The two literal occurrences remain unmapped and create no page-40, color-wide, shape-wide, or global alias.

### SEM-Q-030 — Serious Wound draw, reveal, and face-up placement timing

- **Question:** At what exact point does a random Serious Wound become public/face up between the face-down draw, placement, Health displacement, and effect activation?
- **Sources checked:** Rulebook pp. 9 and 18; official visual `RB-P18-V03`; all exact base selectors and faces in `archive/obsolete/semantics/data/serious-wound-source-index.json`; FAQ v1.2.
- **Candidate readings:** (a) reveal immediately after drawing; (b) place first and reveal after placement/displacement; (c) another source-defined visibility sequence.
- **Status:** Open; official clarification preferred. The unselected deck fronts and order remain hidden, and no digital face-up default is adopted.

### SEM-Q-031 — Serious Wound gain with no empty Health Section

- **Question:** If all three Health Sections already contain Serious Wounds, is another Wound drawn, and if so where does it go or what consequence replaces placement?
- **Sources checked:** Rulebook p. 18 Serious Wound placement and p. 17 Component Limits; official Health/placement visuals; FAQ v1.2.
- **Candidate readings:** (a) no draw/placement; (b) draw followed by a source-defined discard, replacement, overflow, or death consequence; (c) another physical placement procedure.
- **Status:** Open; official clarification preferred. No fourth slot, replacement, automatic death, or discard destination is invented.

### SEM-Q-032 — Wound placement while the Health marker is Heavily Injured

- **Question:** When a Wound is placed in the occupied Heavily Injured Section, what is the “first empty slot in the next Section,” given that the track instead ends at the Skull?
- **Sources checked:** Rulebook p. 18 Health/death/Wound prose and visuals `RB-P18-V01`/`RB-P18-V03`; FAQ v1.2.
- **Candidate readings:** (a) displace to the Skull and die; (b) placement/displacement is impossible because no next Section exists; (c) another terminal procedure applies.
- **Status:** Open; official clarification preferred. Death is not inferred solely from track adjacency.

### SEM-Q-033 — Direct KNEE local action glyph identity and scope

- **Question:** What exact Action is denoted by the unmatched two-overlapping-angular-lobes glyph on the three direct KNEE physical copies?
- **Sources checked:** Direct face `seriouswound-028.png`, its three full CardID/GUID selectors, all-49 icon comparison, unselected sheet cell 6, licensed `SERIOUS_WOUNDS_DATA.Knee`, rulebook, and FAQ v1.2.
- **Candidate readings:** (a) Make a Move Cautiously or a source-scoped cautious-movement Action; (b) another movement/action subtype; (c) remain literal and undispatched until exact evidence exists.
- **Status:** Open. The recognized Secure glyph on selector-gap cell 6 and the licensed wording are separate variants, not aliases for the direct glyph.

### SEM-Q-034 — LUNGS terminal local glyph identity

- **Question:** What quantity/effect is denoted by the standalone stepped-zigzag glyph after “lose 2” on the three LUNGS physical copies?
- **Sources checked:** Exact generated cell 1 and its three selectors, all-49 icon comparison, page-40 Character Health crop, licensed `SERIOUS_WOUNDS_DATA.Lungs`, rulebook, and FAQ v1.2.
- **Candidate readings:** (a) Character Health, as licensed `<HP>` suggests; (b) another local health/status quantity; (c) preserve only the literal operation pending exact evidence.
- **Status:** Open. The glyph did not exactly match the registered Character Health cross-plus-heartbeat morphology; expected effect logic is not evidence.

### SEM-Q-035 — BODY “Hand Size” semantic scope

- **Question:** Does “Your Hand Size is 1 lower” modify only Cleanup refill, impose a persistent maximum with an excess-card procedure, or affect another rule-defined quantity?
- **Sources checked:** Exact BODY sheet cell 5 and three physical selectors; Cleanup rules; licensed `SERIOUS_WOUNDS_DATA.Body`; rulebook and FAQ v1.2.
- **Candidate readings:** (a) draw to 4 instead of 5 during Cleanup, as licensed data says; (b) maximum hand size 4 plus an unstated excess-card rule; (c) another source-defined scope.
- **Status:** Open. The literal TTS modifier is retained, but the licensed Cleanup-only behavior is not promoted above it and no discard cap is invented.

### SEM-Q-036 — Serious Wound effect activation order

- **Question:** When does a newly placed Wound’s immediate/persistent effect begin relative to reveal, placement, Health displacement, Armor loss, and Character death?
- **Sources checked:** Rulebook p. 18; all 27 physical occurrences and exact effect regions; official visuals; FAQ v1.2.
- **Candidate readings:** (a) complete placement/displacement/death before activating the effect; (b) activate immediately on placement; (c) another source-defined interrupt sequence, including continuation after death.
- **Status:** Open; official clarification preferred. Placement and effect activation remain separately structured with no default.

### SEM-Q-037 — Whenever-you-Pass Wound trigger order

- **Question:** In what order do active LUNGS, GUTS, and BLEEDING effects resolve relative to optional Pass discards, setting Passed, ending the Action window, and mandatory Turn-end Oxygen/Fire?
- **Sources checked:** Rulebook Passing/Turn sequence; all nine exact Pass-trigger Wound occurrences; FAQ v1.2.
- **Candidate readings:** (a) trigger at Pass declaration before optional discards; (b) complete Pass, then resolve Wounds before Turn-end consequences; (c) another order among multiple active triggers and Turn-end effects.
- **Status:** Open; official clarification preferred. No simultaneous-trigger owner or ordering rule is invented.

### SEM-Q-038 — Multiple Serious Wound draw, placement, and shortfall order

- **Question:** When one source requests several Serious Wounds, are they each fully resolved in source order, all drawn before assignment, or handled by another simultaneous procedure—especially if the deck/slots run short or an earlier Wound causes death?
- **Sources checked:** Rulebook pp. 17–18; all Serious Wound selectors/faces; multi-Wound Attack effects; FAQ v1.2; `SEM-Q-023` for Deadly Claws’ narrower slot-assignment issue.
- **Candidate readings:** (a) complete each singular gain before the next; (b) draw all available cards first, then assign/place/activate; (c) another source-defined simultaneous/shortfall procedure.
- **Status:** Open; official clarification preferred. `SEM-Q-023` remains independently open; neither question supplies a default for the other.

### SEM-Q-039 — Use Item and One Use Only ordering

- **Question:** What is the exact order of Item declaration, Backpack reveal, Action-card payment, printed effect resolution, and the One Use Only discard transition—including the free immediate-use window and discard-pile face visibility?
- **Sources checked:** Rulebook pp. 12, 17, 28–29; all 23 exact regular Green physical occurrences in `archive/obsolete/semantics/data/green-item-source-index.json`; FAQ v1.2.
- **Candidate readings:** (a) reveal/pay, resolve, then discard; (b) pay/discard when Used, then resolve from the resolution zone; (c) another source-defined order.
- **Status:** Open; official clarification preferred. No payment, reveal, effect, discard, or visibility order is defaulted.

### SEM-Q-040 — Item color-deck exhaustion and multi-draw shortage

- **Question:** When a Green, Red, or later Yellow draw is required but the finite color deck has insufficient cards, is the enclosing Action illegal, do available draws resolve with unavailable cards doing nothing, does the affected discard pile return/reshuffle, or does another procedure apply—and how are scarce cards assigned across multiple requests/decks?
- **Sources checked:** Rulebook pp. 9, 17, and 28; exact 30-child Green and Red TTS roots and their independent 30-copy licensed multiplicities; FAQ v1.2. TTS discard-return helpers remain runtime evidence only.
- **Status:** Open; official clarification preferred. No reshuffle, return, partial-draw assignment, or exhausted-deck policy is adopted.

### SEM-Q-041 — Selected Green local draw and crossed-device glyphs

- **Question:** What exact components/restrictions are denoted by the blank draw rectangles on selected ADRENALINE INJECTION/STIMULANTS faces and the crossed upper-right device on selected STIMULANTS copies?
- **Sources checked:** Exact generated cells 0 and 7, all selected physical CardID/GUID selectors, selected all-glossary no-match evidence, page-40 glossary, FAQ v1.2, and licensed Adrenaline/Stimulants rows.
- **Candidate readings:** (a) Action cards and Not In Combat, following lower-authority licensed fields; (b) another source-local card/restriction identity; (c) remain literal and undispatched pending exact evidence.
- **Status:** Open. Licensed placeholders/flags do not overwrite the explicit TTS no-matches; no color-, position-, title-, or expected-logic alias is created.

### SEM-Q-042 — Contamination Codes Door eligibility and allocation

- **Question:** Does selected TTS CONTAMINATION CODES obey ordinary Door-slot/Destroyed-Door rules, override them, or use another procedure—and which adjacent Corridors receive finite Door tokens if not all placements are possible?
- **Sources checked:** Exact generated cell 3/CardID 3703/GUID `c1bef4`; rulebook Door, whole-effect, local-effect, and Component Limits rules; FAQ v1.2; independent licensed `TerminationCodes` row.
- **Candidate readings:** (a) ordinary Door constraints and whole-effect legality; (b) an override like the independent licensed row; (c) source-defined partial placement/allocation.
- **Status:** Open; official clarification preferred. The licensed one-copy row has no physical identity crosswalk and supplies no default.

### SEM-Q-043 — Restoration-amount owner under Item Interplay

- **Question:** When one Character uses an Item to restore a consenting co-located Character, who chooses the amount from zero through the printed maximum: the Item user, the receiving Character’s owner, or another actor?
- **Sources checked:** Rulebook pp. 18 and 29; FAQ v1.2 Items/Tactical Gear #8; exact regular MEDKIT, MEDICAL STAPLER, and STIMULANTS occurrences.
- **Status:** Open; official clarification preferred. Target, consent, branch, Serious Wound selection, and restoration amount remain distinct decisions.

### SEM-Q-044 — Interplay “Gaining” glyph and Tactical Gear gain-target scope

- **Question:** What is the exact rendered glyph/object after “Gaining” in the rulebook’s four Interplay classes, and does it authorize regular MEDKIT, AMMO MAGAZINE, and GRENADE Tactical Gear gain branches on another consenting Character?
- **Sources checked:** Official rulebook p. 29 rendered Interplay area/text extraction, FAQ v1.2 Items/Tactical Gear #8, exact regular MEDKIT/AMMO MAGAZINE/GRENADE occurrences, and page-40 glossary.
- **Status:** Open; official rendered-pixel clarification/extraction preferred. The missing local glyph is not inferred from the token’s green color or expected medical role.

### SEM-Q-045 — Multiple gained immediate-use windows

- **Question:** When one Trade/effect causes several Items with immediate-use permissions to be gained, are gain/use windows resolved one by one, are all gains completed before the recipient orders windows, or does another simultaneous timing rule apply?
- **Sources checked:** Exact four regular MEDKIT, seven AMMO MAGAZINE, and five GRENADE occurrences; FAQ v1.2 Items/Tactical Gear #5; rulebook Trade/Interplay and Action timing.
- **Status:** Open; official clarification preferred. Each may-window remains independently declineable; no automatic order, stacking, or merged multi-Item resolution is adopted.

### SEM-Q-046 — Selected Red upper-right crossed-glyph identities and use restrictions

- **Question:** What exact restrictions are denoted by the selected source-local upper-right crossed glyphs on ANTI-AIRCRAFT CODES, PERSONAL LOG CODES, and PORTABLE BARRIER?
- **Sources checked:** Exact selected cells 1, 6, and 7 of Red CustomDeck 36; selected all-glossary no-match evidence; exact direct EXPLORING DRONE Not In Combat match; page-40 glossary; FAQ v1.2; licensed `noIntruders` fields.
- **Candidate readings:** (a) Not In Combat, following licensed data; (b) no semantic restriction until exact evidence exists; (c) another source-local restriction.
- **Status:** Open. The three morphologies remain literal no-matches; the independently matched EXPLORING DRONE glyph creates no position-, color-, title-, or shape-wide alias.

### SEM-Q-047 — Military Taser Red-root physical class and current-source correspondence

- **Question:** How should the six exact Red-root MILITARY TASER selectors be classified and resolved when their portrait TTS face says `ONE USE ONLY. SPECIAL WEAPON`, while the official page-29 occurrence and licensed six-copy row are Heavy and print materially different effects?
- **Sources checked:** Raw `redItemsDeck` full CardID/GUID/CustomDeck 35 selectors; generated Yellow-sheet cell 0; official rulebook p. 29 visual `RB-P29-V01`; licensed `ITEMS_DATA.MilitaryTaser`; FAQ v1.2.
- **Candidate readings:** (a) preserve each exact TTS occurrence as a regular Backpack Special Weapon; (b) treat the six as current Heavy copies; (c) leave all six non-dispatchable until an exact edition/copy correspondence is established.
- **Status:** Open; official clarification or an exact current component crosswalk is required. Title equality and matching six-copy aggregates do not establish physical identity.

### SEM-Q-048 — Exploring Drone neighboring target owner and remote Exploration context

- **Question:** Who selects the neighboring Room for direct EXPLORING DRONE, which neighboring Room/Corridor states are eligible, and what exact caller context is passed into the Exploration Sequence when Character Movement and the Entrance effect are both suppressed?
- **Sources checked:** Exact two direct root selectors/face; unselected same-title Red-sheet cell 3; all twelve Exploration faces; rulebook pp. 22 and 24–25; FAQ v1.2; licensed `ExploringDrone` row.
- **Candidate readings:** (a) the Item user selects one source-legal neighboring Undiscovered Room/slot; (b) a deterministic/random rule selects it; (c) another source-defined remote-Exploration context applies.
- **Status:** Open. Exact Exploration-card occurrence dispatch remains preserved; no target owner, Door/Corridor override, title join, or secondary wording default is adopted.

### SEM-Q-049 — Personal Log Codes target, inspector, range, and Objective secrecy

- **Question:** Who chooses the Character, who may inspect that Character’s Objective cards, what range applies, and may any inspected identity be revealed or logged?
- **Sources checked:** Exact selected PERSONAL LOG CODES face; rulebook Local Effects and Objective secrecy/choice rules; FAQ v1.2; licensed row stating “of 1 Character of your choice in the Facility.”
- **Candidate readings:** (a) the Item user selects a local Character and privately inspects; (b) the Item user selects any Character in the Facility; (c) the chosen Character’s owner or another actor owns selection/inspection.
- **Status:** Open; official clarification preferred. Inspection remains temporary private information with no public reveal, client/log/accessibility/spectator exposure, Objective movement, choice, or fulfillment effect.

### SEM-Q-050 — Portable Barrier Door target, override, and Portable Barricade FAQ applicability

- **Question:** Who selects the Door for exact TTS PORTABLE BARRIER, what counts as eligible/accessible, does the effect override Destroyed/no-slot rules, and does FAQ v1.2’s differently named “Portable Barricade” post-open ruling apply?
- **Sources checked:** Exact two selected root occurrences; rulebook Local Effects, whole-effect, Component Limits, and Door rules; FAQ `FQ-P03-U08`; licensed `ITEMS_DATA.PortableBarrier`.
- **Candidate readings:** (a) ordinary local Door eligibility with an Item-user choice; (b) licensed destroyed/no-slot override plus FAQ gone-after-open lifecycle; (c) another source-defined owner/range/finite/lifecycle rule.
- **Status:** Open; official clarification preferred. No target, override, FAQ identity, marker allocation, or re-close lifecycle is defaulted.

### SEM-Q-051 — Selected Yellow upper-right crossed-glyph identities and restrictions

- **Question:** What exact restrictions are denoted by the source-local upper-right crossed glyphs on selected DUCT TAPE, direct PHOSPHATES, and TOOLS occurrences?
- **Sources checked:** Exact root selectors/faces, selected all-glossary no-match evidence, current official Duct Tape occurrence `RB-P28-V03`, page-40 glossary, FAQ v1.2, and licensed `noIntruders` fields.
- **Candidate readings:** (a) Not In Combat, following licensed/current-source leads; (b) no semantic restriction until exact source-scoped evidence exists; (c) another source-local restriction.
- **Status:** Open. Sixteen physical no-match occurrences remain literal; direct Robot Controller and selector-gap Oxygen Tank matches create no position-, color-, title-, or utility-art-wide alias.

### SEM-Q-052 — Yellow-root Fire Extinguisher/Robot Controller physical class

- **Question:** How should five portrait FIRE EXTINGUISHER selectors and one portrait no-HEAVY ROBOT CONTROLLER selector be classified when licensed same-title rows classify all six copies as Heavy?
- **Sources checked:** Raw `yellowItemsDeck` full CardID/GUID/CustomDeck selectors, exact source faces, official regular/Heavy rules, licensed `ITEMS_DATA`, and the 30/24/6 aggregate reconciliation in `archive/obsolete/semantics/data/yellow-item-source-index.json`.
- **Candidate readings:** (a) exact TTS regular Backpack occurrences; (b) current Heavy copies using licensed class/effects; (c) non-dispatchable class/source conflicts pending an exact current crosswalk.
- **Status:** Open; official clarification or exact current component evidence required. Title, Yellow back, utility art, and aggregate multiplicity supply no default.

### SEM-Q-053 — Duct Tape source wording and One Use disposition

- **Question:** Does exact TTS DUCT TAPE place itself and another Heavy Item under an anchor, or does current official/FAQ composition discard Duct Tape as One Use while stacking Heavy Items without it?
- **Sources checked:** Five exact root selectors, selected TTS face, current official face `RB-P28-V03`, rulebook One Use/Heavy rules, and FAQ `FQ-P03-U05` permitting a third Item in one Hand.
- **Candidate readings:** (a) current official/FAQ effect plus ordinary One Use discard; (b) exact TTS self-placement despite the generic discard rule; (c) another source-defined reconciliation/arrangement.
- **Status:** Open; official clarification preferred. No official occurrence identifies a TTS GUID copy, so source variants remain independent.

### SEM-Q-054 — Duct Tape stack cardinality and later lifecycle

- **Question:** After Duct Tape creates a multi-Heavy-Item Hand stack, what is its maximum size and what happens when a member is discarded, lost, malfunctioned, traded, or separated?
- **Sources checked:** FAQ `FQ-P03-U05`; rulebook One Use, Hand capacity, Item loss/Tactical Gear, voluntary discard, and Trade rules; exact Duct Tape occurrences.
- **Candidate readings:** (a) repeatably add one Item with no fixed cap and preserve remaining attachment; (b) exactly three Items maximum and separate/reapply capacity when any member leaves; (c) another source-defined topology, maximum, ownership, token-loss, transfer, and separation procedure.
- **Status:** Open; official clarification preferred. Generic Item/Trade rules do not silently define a stacked-group lifecycle.

### SEM-Q-055 — Phosphates Corridor target owner and scope

- **Question:** Who selects the Empty Corridor for direct PHOSPHATES, and must it be adjacent/local and reachable without crossing a Closed Door?
- **Sources checked:** Five exact direct selectors, unselected same-title sheet cell 2, rulebook Local Effects/Reinforced Corridor/Closed Door rules, FAQ `FQ-P02-U10`, and licensed `ITEMS_DATA.Phosphates`.
- **Candidate readings:** (a) Item user chooses one adjacent source-legal Empty Corridor; (b) exact unqualified TTS wording uses another local scope/owner; (c) another source-defined target/range rule.
- **Status:** Open; official clarification preferred. The direct Fire branch, selector-gap Secure branch, and licensed adjacency wording remain independent.

### SEM-Q-056 — Tools Door target/state owner and accessibility

- **Question:** Who selects the Door and Open/Closed state for TOOLS, and what local/accessibility range and ordinary Door constraints apply?
- **Sources checked:** Six exact root selectors, rulebook Local Effects and Door rules, FAQ v1.2, and licensed `ITEMS_DATA.Tools` with its `accessible Door` qualifier.
- **Candidate readings:** (a) Item user chooses one ordinary accessible/local Door and state; (b) a deterministic/local rule selects it; (c) another source-defined owner/range/eligibility rule.
- **Status:** Open; official clarification preferred. No Portable Barrier override or Robot-specific accessibility rule is imported.

## Heavy/Equipment/Weapon/Armor/Starting Item batch questions

The following 18 semantic questions were added by the bounded Heavy/Equipment/Weapon/Armor/Starting Item source audit. Their exact alternatives, affected records, and `defaultProhibited` flags are authoritative in `archive/obsolete/semantics/data/review-gates.json`; no default is adopted:

- **SEM-Q-079** — complete current Character Item roster, owner, and source-copy crosswalk;
- **SEM-Q-080** — remaining Support Equipment deck access, exhaustion, and later use;
- **SEM-Q-081** — Hand capacity with Duct Tape, Bayonet, gains, discard, and attachment topology;
- **SEM-Q-082** — Armor break, damage, attached-token loss, replacement, and terminal Health order;
- **SEM-Q-083** — exact TTS Tactical Gear slot type/count and non-card tracks;
- **SEM-Q-084** — Fully Loaded Any-slot choice, simultaneous allocation, and finite shortage;
- **SEM-Q-085** — Trade/transfer capacity, owner consent, attachments, and Character Item replacement;
- **SEM-Q-086** — passive Item visibility, duration, duplicate stacking, trigger order, and Malfunction suppression;
- **SEM-Q-087** — death, escape, Starting Item loss destination, replacement, and recovery;
- **SEM-Q-088** — Weapon trigger timing, added-result order, targeting, allocation, and continuation;
- **SEM-Q-089** — Weapon Malfunction repair, destruction destination, attached-token return, and pending-effect continuation;
- **SEM-Q-090** — Grenade Launcher token count, before/instead timing, variant scope, and the malfunction exception;
- **SEM-Q-091** — source-local Heavy/Weapon glyph identities and restrictions;
- **SEM-Q-092** — Supporting Robot Controller and Portable Device actor/reveal/remote context;
- **SEM-Q-093** — Security, Entrenching, and Engineering target/owner/scarce-component order;
- **SEM-Q-094** — RPG, Remote Detonator, and Military Taser area targets/allocation/continuation;
- **SEM-Q-095** — Motion Tracker target, Hazard suppression, Noise equality, and Encounter timing;
- **SEM-Q-096** — active/One Use Heavy payment, effect, discard/remove, and partial-resolution order.

The batch preserves the 12 Red/Yellow physical class conflicts, the two audited Automatic Shotgun/BF Gun prototype/current conflicts, all Support selector gaps, and all independent TTS/current-official/licensed variants without converting any of those boundaries into a default.

## Core Combat, Attacks, and Noise/Hazard batch questions

The bounded core Combat/Attacks/Noise/Hazard source audit added nine no-default questions. Exact alternatives, affected rule IDs, evidence tuples, and `defaultProhibited` flags are authoritative in `archive/obsolete/semantics/data/review-gates.json`:

- **SEM-Q-097** — order among multiple matching Corridors in one numeric Noise result;
- **SEM-Q-098** — required Intruder-token draw when the Intruder bag is empty;
- **SEM-Q-099** — side-level Blank Help-row applicability in Corridor and Room draws;
- **SEM-Q-100** — remaining Opportunity Attacks and Movement after mover death, escape, or other participation loss;
- **SEM-Q-101** — standard Intruder Attack draw when the finite Attack deck is empty;
- **SEM-Q-102** — order among equal-size Intruders in an Intruder Phase Room cohort;
- **SEM-Q-103** — Shoot/Melee roll and added-effect continuation after an initial Hit kills a Room Larva;
- **SEM-Q-104** — Burst multi-target Hit resolution order, Queen interrupt, and continuation;
- **SEM-Q-105** — Adult/Drone allocation when mixed token-back counts meet Corridor capacity or exact-type model shortage.

Official Retaliation Noise semantics remain the closed `1`/`2`/`3`/`4`/`Hazard` set. Preserved TTS Lua branches containing `Silence unless Slimed`, `DANGER`, or `Mars Surface` are unbound lower-authority runtime provenance, not open current-rule alternatives. The Blank token always returns to the bag; only the side-level panel’s add-Adults applicability outside Bag Development remains unresolved under SEM-Q-099.

## Facility/map topology and setup-state batch questions

The bounded Facility/map batch added five no-default questions. Exact alternatives, affected records, and `defaultProhibited` flags are authoritative in `archive/obsolete/semantics/data/review-gates.json`:

- **SEM-Q-106** — Section-border orientation and the fixed Landing Zone/Hibernatorium edge crosswalk. The p.19 diagram shows one three-section arrangement and distinct special border-piece spaces, but the checked setup prose does not say whether border pieces may rotate or assign every special-space edge to a regular Corridor endpoint.
- **SEM-Q-107** — Special-space Corridor endpoints and fixed-space connector assignment. The Landing Zone and Hibernatorium are named Room spaces in the rules but are not regular variable hex slots in the rendered geometry; no complete text-labeled endpoint crosswalk was recovered.
- **SEM-Q-108** — Initial Landing Zone entrance selection for Corridor Door-slot orientation. Setup says a Door slot is placed toward “an entrance to the Landing Zone” but does not identify a single entrance, a player choice, or a deterministic assignment among multiple drawn Corridors.
- **SEM-Q-109** — Setup component shortage, replacement, and simultaneous placement atomicity. Setup prescribes exact quantities and placements, while the generic Component Limits rule addresses unavailable components in effects; no source extends that fallback to setup or defines replacement/partial-group behavior.
- **SEM-Q-110** — Unnamed Room-marker, Exploration-marker, or Suppression-marker component identity. The checked inventory and map-marker prose name Fire, Malfunction, Noise, Secure, Universal, and the Undiscovered Hibernatorium tile, but no separate generic marker identity or face/placement rule was established.

Status: all five remain open, with no orientation, endpoint, shortage, marker identity, or replacement default adopted. The batch resolved the 25 Room Help-entry versus 23 physical Room-tile count boundary by retaining Landing Zone and Hibernatorium as the two additional fixed-space effects.