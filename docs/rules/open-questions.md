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
- **Candidate readings:** N/A — requires visual PDF/card inspection.
- **Status:** Open. Inspect the physical Rest Action card or a high-quality scan before formalizing its full effect.

### OQ-006 — Intruder Help Sheet encounter table transcription

- **Question:** What are the exact per-token effects for the Queen-alive and Queen-dead sides of the Intruder Help Sheet in each draw context (noise marker, hazard, bag development, other)?
- **Why it matters:** The Help Sheet is normative for token resolution, but its graphical layout did not survive text extraction.
- **Sources checked:** Rulebook p. 30 (lines 5182–5188); Rulebook p. 35 (lines 5764–5772).
- **Candidate readings:** N/A — requires transcription from the physical Help Sheet or PDF artwork.
- **Status:** Open. Transcribe the table before implementing token-resolution mechanics.

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
- **Candidate readings:** N/A — requires visual PDF/card inspection.
- **Status:** Open. Validate from the rulebook PDF or card faces.

### OQ-009 — Nest event before the Nest is discovered

- **Question:** When an official event/effect instructs placement, activation, or resolution at the Nest before it has been explored, what exact physical-game procedure applies?
- **Why it matters:** The digital edition must reproduce the physical result, rather than reserve, defer, or relocate Nest occupants as a digital design decision.
- **Sources checked:** Current extracted rulebook text did not yield the relevant event-card resolution. The official event card and any FAQ clarification must be inspected directly.
- **Candidate readings:** None adopted. The physical-game procedure is authoritative.
- **Status:** Open, pending transcription of the relevant official event card/rule/FAQ text.

### OQ-010 — Action card faces are not recoverable from extracted text

- **Question:** What are the named Action card faces in each Character's 10-card deck, and each face's printed effect, Reaction, and Not-in-Combat state?
- **Why it matters:** Action cards are the player's primary resource and the only way to resolve the zero-cost `Play an Action card` Basic Action. Without real faces, the engine cannot resolve card effects and the UI cannot display a hand faithfully. See ACT-CARD-001 and BUG-023.
- **Sources checked:** `docs/rulebooks/rulebook_text.txt` — the rulebook pictures only a few example card faces rather than listing decks. Only **Sprint** (Recon) and **Duck and Cover** (Contractor: Consultant) are recoverable, plus the anatomy diagram on p. 14. The component list gives a total of 60 Action cards (line 528) with no per-Character breakdown. Web search returned no authoritative Retaliation-specific card list; results were paywalled or covered the earlier *Nemesis* game, whose card list must not be substituted.
- **Candidate readings:** None adopted. Inventing card faces is explicitly forbidden by the corpus coverage discipline.
- **Status:** Open. Requires transcription from the physical cards or an official card-list export. Until then, unverified faces must be labelled as unverified in prototypes and must not be committed to `data.js` as if authoritative.