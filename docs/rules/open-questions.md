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

### SEM-Q-005 — Drilling Station new-Corridor endpoint selection

- **Question:** When the Drilling Station says to place a new Corridor leading from the Room with the Robot, who selects the legal edge or endpoint if more than one placement is possible?
- **Why it matters:** A digital implementation must not silently choose a map edge or endpoint when the checked source provides no selector or tie-break.
- **Sources checked:** Room Help entry 17 and its associated note; official FAQ Rooms #1; rulebook Robot and map-placement sections.
- **Candidate readings:**
  - (a) The player chooses a legal edge/end point.
  - (b) A physical-game placement procedure or deterministic edge rule applies.
- **Status:** Open. The semantic pilot preserves the decision as source-unspecified and adopts no default.