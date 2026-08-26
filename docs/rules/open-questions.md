# Open Rules Questions

Use this ledger for ambiguities that the official rulebook and FAQ do not settle clearly enough for the digital edition. Do not use it for already-known implementation bugs; those belong in `deviations.md` once source-cited.

## Entry format

- **Question ID:** stable identifier.
- **Question:** the smallest precise question possible.
- **Why it matters:** user-facing consequence.
- **Sources checked:** rulebook and FAQ citations.
- **Candidate readings:** distinguish evidence from inference.
- **Status:** open, awaiting official clarification, or resolved by project decision.

## Entries

### OQ-001 — Eclosion existing-hand behavior

- **Question:** Does the Eclosion Procedure check only the 4 newly drawn cards, or all cards in hand after drawing?
- **Why it matters:** A Character holding Contamination cards from prior turns would die more often under the literal reading.
- **Sources checked:** Rulebook p. 38 (lines 6099–6116). The procedure says “draw 4 cards from your Action deck” then checks for Contamination “in your hand,” but does not say to clear the existing hand first.
- **Candidate readings:**
  - (a) Literal: check all cards in hand after drawing, including pre-existing cards.
  - (b) Intent: check only the 4 newly drawn cards.
- **Status:** Open. The literal reading is (a); confirm via official ruling if (b) is desired.

### OQ-002 — Endgame Larva iteration timing

- **Question:** Does a Larva acquired in endgame step 2 (Infection) make a Character eligible for step 3 (Eclosion)?
- **Why it matters:** Determines whether a Character can die from eclosion triggered by an infection gained during the endgame sequence itself.
- **Sources checked:** Rulebook p. 39 (lines 6249–6273). The note says a Character may gain a Larva “during this Sequence.”
- **Candidate readings:**
  - (a) Sequential: evaluate “currently has a Larva” when step 3 is reached; a Larva from step 2 qualifies.
  - (b) Snapshot: evaluate Larva status as of endgame start.
- **Status:** Open, leaning toward (a) based on the rulebook note. Mark as an implementation interpretation until officially confirmed.

### OQ-003 — Starting Player token passing to dead/escaped/hibernated Characters

- **Question:** What happens when the Starting Player token would pass clockwise to a Character who is dead, escaped, or hibernated?
- **Why it matters:** Affects turn order and who acts first each Round.
- **Sources checked:** Rulebook p. 15 (lines 3398–3400) says “next player.” Rulebook p. 18 says a dead Character “no longer takes part.” No explicit procedural rule for this case.
- **Candidate readings:**
  - (a) Skip to the next eligible (alive, non-escaped, non-hibernated) Character.
  - (b) Token stays on the dead/escaped/hibernated Character and turn order proceeds from there.
- **Status:** Open. Reading (a) is the natural rules-level conclusion but is not explicitly stated.

### OQ-004 — Player Phase recalculation after mid-Turn death

- **Question:** How is a partially completed Player Phase recalculated when a Character dies during a Turn?
- **Why it matters:** Determines whether the dead Character’s remaining Turn is skipped and how turn order continues.
- **Sources checked:** Rulebook p. 13 (lines 2987–2994); Rulebook p. 18 (lines 3750–3763). The rulebook says dead Characters “no longer take part” but provides no dedicated procedural rule for mid-Phase advancement.
- **Candidate readings:**
  - (a) The dead Character has no later Turn; proceed to the next eligible Character.
  - (b) More specific advancement algorithm needed.
- **Status:** Open. Reading (a) is the safe rules-level conclusion; do not invent a more specific algorithm without a source.

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
- **Sources checked:** Rulebook p. 23 (lines 4396–4413); FAQ v1.2, “General rules” #11 (lines 70–72). The general rule says discard one Secure “whenever an Intruder enters,” but no explicit multi-Intruder simultaneous-entry example is given.
- **Candidate readings:**
  - (a) Each separate entering Intruder consumes one token.
  - (b) One token prevents the entire group.
- **Status:** Open, leaning toward (a) based on the per-entry wording.

### OQ-008 — Not-in-Combat icon associations

- **Question:** Which specific basic actions and Action cards carry the “Not in Combat” restriction?
- **Why it matters:** The rule itself is clear (no action while in a Room with an Intruder), but the text extraction lost the icon-to-action associations.
- **Sources checked:** Rulebook p. 12 (lines 2901–2920).
- **Evidence recovered:** Rulebook visual unit `RB-P12-V02` associates the restriction glyph with Place 1 Secure token, Activate the Robot, Trade, Use the Room, and Make a Move Cautiously. The card corpus retains `printedData.upperRight = notInCombat` per extracted face (42 Action-card/component-scan occurrences: 20 canonical and 22 full-draft, plus non-Action Item occurrences kept separately).
- **Status:** **Resolved as an extraction blocker.** Each association remains attached to its exact source face/version; duplicate titles do not create a global association by name.

### OQ-009 — Nest event before the Nest is discovered

- **Question:** When an official event/effect instructs placement, activation, or resolution at the Nest before it has been explored, what exact physical-game procedure applies?
- **Why it matters:** The digital edition must reproduce the physical result, rather than reserve, defer, or relocate Nest occupants as a digital design decision.
- **Sources checked:** Canonical event source tuples `event-090.png` (Hatching: place a Larva in the Nest) and `event-179.png` (Egg Protection: place 2 Drones in the Nest); rulebook and FAQ extraction. The card instructions are now readable, but no checked authoritative source states what to do if the Nest Room is not yet on the map.
- **Candidate readings:** None adopted. Reserving, deferring, relocating, or forcing discovery would each add a procedure absent from the checked sources.
- **Status:** **Open genuine semantic/source ambiguity.** The missing information is no longer card transcription; it is the physical resolution procedure for a nonexistent/Undiscovered Nest location.

### OQ-010 — Action card source inventory and authority reconciliation

- **Question:** What are the named Action card faces in each Character's 10-card deck, and each face's printed effect, Reaction, and Not-in-Combat state?
- **Why it matters:** Action cards are the player's primary resource and the only way to resolve the zero-cost `Play an Action card` Basic Action. Without real faces, the engine cannot resolve card effects and the UI cannot display a hand faithfully. See ACT-CARD-001 and BUG-023.
- **Sources checked:** `docs/rulebooks/rulebook_text.txt` — the rulebook pictures only a few example card faces rather than listing decks. Only **Sprint** (Recon) and **Duck and Cover** (Contractor: Consultant) are recoverable, plus the anatomy diagram on p. 14. The component list gives a total of 60 Action cards (line 528) with no per-Character breakdown. Web search returned no authoritative Retaliation-specific card list; results were paywalled or covered the earlier *Nemesis* game, whose card list must not be substituted.
- **Evidence recovered:** The closed card corpus preserves the source-bound component scans/variants, and immutable licensed-digital build `260622-1220` supplies 60 scoped Action-card records (10 per Character) with names, effects, Reactions, Command flags, and Not-in-Combat booleans. The rulebook independently confirms 60 total / 10 per Character.
- **Status:** **Resolved as a missing-source/data blocker, not as an authority merge.** The licensed-digital table is secondary and TTS/prototype/final-source variants remain independent. Canonical per-face wording and executable effect reconciliation belongs to the semantic layer; no face may be invented or silently rewritten.

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

### SEM-Q-002 — Exploration Entrance-effect Noise

- **Question:** When Movement explores an Undiscovered Room, does a Noise-roll Entrance Effect satisfy the post-Movement Noise requirement, or is it additional to a separate universal Noise roll?
- **Why it matters:** It determines whether an exploratory Move can cause zero, one, or two Noise rolls depending on the drawn Exploration card.
- **Official sources checked:** Current official English rulebook passages for Movement, Exploration Entrance Effects, and mandatory post-Movement Noise; official FAQ v1.2 dated 8.06.2026. The FAQ does not reconcile the passages.
- **Secondary strong lead (not an official ruling):** The licensed Board Game Arena adaptation is published by Awaken Realms, developed by Tisaac and KuWizard, and currently labeled BETA. Its example replay at release `260617-1110` (played 2026-06-22) logs exactly one roll at Move 26 when the Entrance Effect says “Make a Noise roll,” and no automatic post-Exploration roll at Move 37 when the Entrance Effect is not a Noise roll. Sources: <https://en.boardgamearena.com/archive/replay/260617-1110/?table=872060252&player=89879864&comments=> and <https://boardgamearena.com/gamepanel?game=nemesisretaliation>.
- **Status:** Open. This is a strong secondary lead for one Entrance-effect roll total and no automatic roll when the Entrance Effect is non-Noise, but it does not override the unresolved official wording. `docs/rules/semantics/review-gates.json` retains both alternatives and prohibits a default.

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
- **Sources checked:** Rulebook p. 17, “Component Limits” (lines 3538–3548); p. 24, “Set up the Corridors” and “Set up markers and tokens” (lines 4502–4522); all 12 exact base face diagrams and the licensed structured variants in `docs/rules/semantics/exploration-source-index.json`; FAQ v1.2.
- **Candidate readings:**
  - (a) The exploring player assigns each random draw or last available component to an eligible depicted slot.
  - (b) A fixed source-local order begins from the printed North orientation and proceeds in an unstated direction.
  - (c) Draws/components are randomly assigned among eligible slots.
- **Status:** Open. No checked source names an owner, start slot, direction, or additional randomization. `docs/rules/semantics/review-gates.json` prohibits a default while every exact diagram remains independently preserved.

### SEM-Q-012 — Unrevealed Robot and non-Activation effects

- **Question:** Before the first Room connects to the Hibernatorium, which external effects may target, require, or otherwise mention the face-down Robot without inspecting its identity?
- **Sources checked:** Rulebook pp. 8, 22, and 37; FAQ v1.2. The base rules prohibit Activation and inspection before reveal but do not give a general external-effect policy. The apparent Rise of the Machine/Robot answers on FAQ p. 3 are explicitly Neoflesh-expansion units and do not settle the base game.
- **Status:** Open. The card stays hidden and printed Robot Actions are unavailable; no broader external-effect default is adopted.

### SEM-Q-013 — Robot movement destination owner and route timing

- **Question:** Who chooses each neighboring Room during a Robot effect that says “Move ... up to N times,” and is a multi-step route committed up front or chosen one step at a time?
- **Sources checked:** Rulebook p. 37 and all six exact Robot faces. The rules establish adjacency, Closed-Door, Unexplored-Corridor, Intruder, and Noise constraints, but name no destination owner or route timing.
- **Status:** Open. Zero steps remains legal under “up to”; no destination or tie-break is automated.

### SEM-Q-014 — Exploration Robot Noise modality and timing

- **Question:** After the Exploration Robot traverses an Unexplored Corridor while suppressing the Entrance Effect, must, may, or never make a Noise roll, and at what point?
- **Sources checked:** Rulebook p. 37 and exact Exploration Robot face `robotDeck-004.jpg`. The rulebook says the Robot normally never rolls Noise and the Exploration Robot “could” make one, without stating modality or timing.
- **Status:** Open. This is distinct from SEM-Q-002 and receives no default.

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
- **Status:** Open. The licensed local scope is a secondary lead, not an override. No scope default is adopted.

### SEM-Q-021 — Compound Attack effects after intermediate death

- **Question:** If Health loss or a Serious Wound kills the attacked Character before a later operation in the same selected Attack panel, does that later operation still resolve?
- **Sources checked:** Exact Bite, Deadly Claws, Fury, Scratch, and Tail Attack occurrences; rulebook pp. 18 and 32; FAQ v1.2.
- **Candidate readings:**
  - (a) Stop later Character-bound operations when the Character dies and no longer participates.
  - (b) Complete the entire associated printed panel before discarding the Attack card.
  - (c) Treat coordinated Wound/Contamination outcomes as simultaneous before applying death.
- **Status:** Open. Printed order is retained, but continuation after death is default-prohibited.

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
- **Sources checked:** Rulebook pp. 33–35 (Burst, Shoot, Queen Health); FAQ v1.2 General rules #1; exact source index `docs/rules/semantics/queen-health-source-index.json`.
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
- **Status:** Open; official clarification preferred. Draw, hidden discards, lower effect, drawn-card discard, death, and reset remain separately ordered with no default.

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