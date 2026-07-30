# Mobile-First UI Design Report — Nemesis: Retaliation Digital Edition

> **ARCHIVED (2026-07-30).** Superseded by `../play-area-design.md`, the active design authority. Kept for citations and QA methodology only. Do not implement from this document.


**Date:** 2026-07-28
**Status:** Concept stage — prototype and automated QA complete
**Authority:** Official rulebook and FAQ v1.2 are the sole rules authority. Existing engine behavior is not.

---

## 1. Purpose and scope

This report documents a complete mobile-first UI concept for a 100%-faithful digital port of *Nemesis: Retaliation*. It covers every screen, persistent surface, interaction state, transition, and end state a player encounters from lobby through endgame. A standalone interactive prototype accompanies it at:

`docs/design/prototypes/mobile-first-ui-concept.html`

Automated QA results are at:

`docs/qa/mobile_concept_qa.py` (14 scenes × 6 viewport classes plus semantic and interaction checks; latest run: 374 passed, 0 failed, 0 warnings)

Earlier design documents — `mobile-information-classification.md` and `mobile-tactical-map-interaction.md` — established the information architecture and map interaction model. This report synthesizes those into the complete UI concept and adds the remaining surfaces, flows, and citations.

---

## 2. Design principles and citations

### 2.1 Quiet enjoyment — design that recedes

> Good design can be "invisible, serving us without drawing attention to itself."

— Don Norman, *The Design of Everyday Things*, Revised and Expanded Edition (Basic Books, 2013, ISBN 978-0-465-05065-9), Preface.
  Author page: https://jnd.org/books/the-design-of-everyday-things-revised-and-expanded-edition

**Implication:** The board, current decision, and current state should dominate. Decorative chrome, ambient animation, and non-essential panels recede. Critical state remains visible through compact, persistent representations.

### 2.2 Signifiers — perceptible cues for every interaction

> People need perceptible clues indicating what something is for, what is happening, and what alternative actions exist.

— Don Norman, "Signifiers, not affordances," *ACM Interactions* author version, JND.org.
  https://jnd.org/signifiers-not-affordances/

**Implication:** A selectable Room looks selectable. A legal target has a distinct marker. The current turn is labeled. No interactivity is inferred from artwork alone.

### 2.3 Self-evident interaction

> An interface should be as self-evident as possible — "Obvious. Self-explanatory."

— Steve Krug, *Don't Make Me Think, Revisited*, 3rd edition (New Riders/Pearson, 2014, ISBN 978-0-321-96551-6), p. 11.
  Publisher page: https://sensible.com/dont-make-me-think

**Implication:** A new player should immediately answer: *Whose turn is it? What can I select? Where can it go? How do I commit or undo?* Novel iconography or memorizable conventions are avoided.

### 2.4 Recognition over recall

> Keep elements, actions, options, labels, and needed information visible or easily retrievable.

— Jakob Nielsen, "10 Usability Heuristics for User Interface Design," Nielsen Norman Group, 1994, last reviewed 2024-01-30.
  https://www.nngroup.com/articles/ten-usability-heuristics/

**Implication:** Legal actions, costs, targets, current phase, and survival state are visible at the point of decision. The player never relies on memory of a reference screen.

### 2.5 Progressive disclosure

> Initially show only the most important options and reveal specialized or rarely used features on request.

— Jakob Nielsen, "Progressive Disclosure," Nielsen Norman Group.
  https://www.nngroup.com/articles/progressive-disclosure/

**Implication:** Current-turn essentials and legal actions are exposed. Rules reference, full log, deck counts, discard piles, and settings sit behind clearly labeled secondary controls.

### 2.6 No color as sole information channel

> Color is not used as the only visual means of conveying information, indicating an action, prompting a response, or distinguishing a visual element.

— W3C WAI, "Understanding Success Criterion 1.4.1: Use of Color," WCAG 2.2 Level A.
  https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html

**Implication — user requirement, reinforced:** Every critical state — Fire, Malfunction, Secure, Noise, Intruder type, Character identity, Section, injury level, Life Support status, target legality, phase, and participation state — uses at least two visible channels: color plus text, shape, pattern, outline, or icon. The prototype includes a grayscale toggle to verify this. The basic test: if viewed on a black-and-white screen, is it still understandable?

### 2.7 Touch targets

> As a general rule, buttons need a hit region of at least 44 × 44 pt.

— Apple, "Buttons," Human Interface Guidelines.
  https://developer.apple.com/design/human-interface-guidelines/buttons

> Material icon buttons use 48 × 48 dp target areas.

— Google, "Icon buttons — Accessibility," Material Design 3.
  https://m3.material.io/components/icon-buttons/accessibility

> WCAG 2.2 Level AA requires pointer targets of at least 24 × 24 CSS pixels.

— W3C WAI, "Understanding Success Criterion 2.5.8: Target Size (Minimum)."
  https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

**Implication:** Treat 24 CSS px as a compliance floor. Design primary controls to at least 44 × 44 CSS px in this browser prototype, while retaining the larger 48 dp Android target as the production-platform goal. The QA matrix measures every visible prototype control in every scene and tested viewport at a minimum of 44 × 44 CSS px.

### 2.8 Contrast

> Text requires at least 4.5:1 contrast against its background; large text requires at least 3:1.

— W3C WAI, "Understanding Success Criterion 1.4.3: Contrast (Minimum)."
  https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

> Visual information needed to identify controls, component states, and meaningful graphical objects requires at least 3:1 contrast.

— W3C WAI, "Understanding Success Criterion 1.4.11: Non-text Contrast."
  https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html

### 2.9 Reduced motion

> Motion animation triggered by interaction can be disabled, unless the animation is essential.

— W3C WAI, "Understanding Success Criterion 2.3.3: Animation from Interactions," WCAG 2.2 Level AAA.
  https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html

**Implication:** The prototype includes `@media (prefers-reduced-motion: reduce)` rules that suppress all transitions and animations.

### 2.10 Status messages without focus theft

> Status messages can be programmatically determined through role or properties such that they can be presented to the user by assistive technologies without receiving focus.

— W3C WAI, "Understanding Success Criterion 4.1.3: Status Messages," WCAG 2.2 Level AA.
  https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html

**Implication:** Turn changes, action results, and phase transitions use an `aria-live="polite"` region. Urgent conditions use a more assertive announcement. Neither steals focus or opens a modal for routine state.

---

## 3. Complete mobile screen architecture

The concept uses a three-zone vertical layout that adapts by scene:

```
┌─────────────────────────┐
│  STATUS STACK           │  Round, phase, turn, Life Support, Mission Task
│  (persistent, compact)  │  Suppressed at Room-detail zoom except urgent items
├─────────────────────────┤
│                         │
│  MAIN STAGE             │  Map / task / blocking state — fills remaining space
│  (flexible content)     │
│                         │
├─────────────────────────┤
│  COMMAND DOCK           │  Vitals, action buttons, hand rail
│  (persistent, compact)  │  Hidden in setup/dead/end scenes
└─────────────────────────┘
```

### 3.1 Status stack

**Elements:** Log/reference button → Round number → Phase label + Starting Player → Turn badge (YOUR TURN / SPECTATING / RESOLVING) → Life Support A/B/C pills → Autodestruction countdown → Mission Task one-line summary → Objective Choice track position → privacy-safe public roster.

**Reasoning:** Visibility of system status (Nielsen #1) requires the most important global state to be persistent and compact. The player should never wonder "what round is it?" or "whose turn is it?" Life Support and Autodestruction are survival-critical and time-critical; they earn always-visible positions. Mission Task is shared and immutable, so its one-line summary stays visible without occupying map space. The roster exposes only public Character state and total hand counts—not the Action/Contamination split, Backpack contents, or Objective faces.

**Non-color encoding:** Life Support pills use shape symbols: checkmark (✓) for Active, triangle/exclamation (!) for Damaged, X with hatching pattern for Inactive. Autodestruction uses an hourglass symbol (⌛). Turn badge uses text labels and a double-border clip-path shape.

**Adaptive suppression:** At Room-detail zoom, the status stack suppresses the Life Support row and Mission line to reclaim space, retaining only the Round/phase/turn row. Urgent conditions (Autodestruction armed, disconnection pause) override suppression.

### 3.2 Main stage — map (primary surface)

The map is the dominant interactive surface. It uses semantic zoom (three levels) as specified in `mobile-tactical-map-interaction.md`:

**Room-geometry fidelity invariant:** every Room is a regular pointy-top hexagon with exactly six edge directions: NE, E, SE, SW, W, and NW. The prototype preserves visible space at all six edges for possible Corridors. Hex proximity never invents adjacency; only a legal Corridor makes a destination reachable. Octagonal or eight-direction Room renderings are fidelity defects. See `docs/rules/00-foundations.md` FND-005.

- **Facility Overview** (< ~72 px Room size): full topology, Security, Fire, Malfunction, Characters, Robot, Corridors, Doors, Noise, Intruders, Hits, legal targets. Room prose removed.
- **Tactical Neighborhood** (~72–150 px): selected Room plus connected Corridors and neighbors. Room name, icons, function summary, statuses, occupants, available actions.
- **Room Detail** (> ~150 px): full Room function, every status and occupant, complete Corridor info. No separate modal.

**Interaction model:**
- Pinch and pan for free tactical inspection (preserved from existing engine).
- One-tap Room focus for deterministic framing.
- Zoom buttons (−, +, FIT FACILITY) as accessible alternatives.
- Navigation and action targeting are separate states. During targeting, only legal destinations receive target affordances (double-border + "MOVE" label + hatched fill pattern). Room-focus gestures cannot accidentally select a target.

**Non-color encoding for map state:**
- **Fire:** hatched diagonal fill pattern + ♨ symbol + "Fire" text in legend.
- **Malfunction:** crosshatch pattern + ⚡ symbol + "Malfunction" text in legend.
- **Secure:** double-border square shape + ▣ symbol.
- **Noise:** dashed border circle + ≈ symbol.
- **Intruders:** rotated square shape (45°) with hatched fill, distinct from circular Character occupants.
- **Doors:** Open = dashed line; Closed = thick solid line; Destroyed = X-cross marks.
- **Current Room:** solid white shell outline + "CURRENT" dashed label.
- **Legal target:** white shell + hatched interior fill + "MOVE" text label.
- **Unrevealed Room:** "?" text + "UNREVEALED" label.

### 3.3 Main stage — task surfaces (blocking decisions)

When a decision requires the player's full attention, the map is replaced by a task surface. This happens only for choices that the physical game requires the player to make:

- **Payment:** Select exactly N eligible Action cards to discard. Contamination cards are visually distinct (hatched fill + double border + "NOT ELIGIBLE" label) and are not selectable.
- **Search:** Choose one Item from drawn cards. Unchosen card text is never broadcast. The interface does not auto-pick.
- **Objective Choice:** Choose one of two Objective cards. Removal is private. The 3/2/2/1 card reward is shown and applied.
- **Resolution:** Show dice result, bag-token result, Event/Attack/Queen Health card, and ordered effect sequence. Each step is visible until acknowledged.
- **Trade:** Mutual consent transaction with private offer and public resulting equipment.

**Reasoning:** Krug's "don't make me think" principle means the current decision should occupy the full screen when it requires exclusive attention, but only then. Progressive disclosure keeps non-essential information behind secondary controls.

### 3.4 Command dock

**Elements (top to bottom):**
1. **Vitals row:** Character portrait (faceted clip-path) + player name + Character name + active wound modifiers → Health (number + segment bar) + Oxygen (number + segment bar).
2. **Action row:** Four buttons — Map, Play card, Basic action, Private. The active button has a double-border outline.
3. **Hand rail:** Horizontally scrollable private hand cards. Each production card shows its exact official face, type, name, and cost. Contamination cards use hatched fill and double borders to distinguish without color. The structural prototype deliberately uses “Official card face” placeholders where verified face transcription is not yet present; it does not invent replacement card names or effects.

**Reasoning:** Recognition over recall means the player's own survival state and available actions are always visible. The hand rail is private — other players see only total card-back count. The dock is hidden in setup, dead, and endgame scenes where it has no function.

**Non-color encoding for vitals:** Health and Oxygen use numeric values (e.g., "7/9 HP", "4 O₂") plus segment bars. Injury level is conveyed by the number itself and a text label in the identity line (e.g., "1 Serious Wound"), not by bar color.

---

## 4. Scene inventory and transitions

### 4.1 Setup and lobby

**Scene:** `setup`
**Elements:** Brand title → setup stepper (Game / Players / Characters / Objectives / Facility) → lobby card with game code, QR/link sharing, roster, and confirm button.
**Fidelity notes:** Character draft is private — only the current chooser sees their pair. Rank order is visible. The game code is always presented as text (not only QR) for non-color accessibility.
**Transition:** Confirm Character → game begins → overview scene.

### 4.2 Player turn (overview)

**Scene:** `overview`
**Elements:** Full status stack + facility map at overview zoom + context band (empty or showing current Room summary) + command dock with all actions.
**Transition:** Tap Room → room scene. Tap action button → targeting/payment/private scene. Intruder phase → intruder scene.

### 4.3 Room detail

**Scene:** `room`
**Elements:** Status stack (suppressed to Round/phase/turn only) + map zoomed to Room detail + context band showing full Room function, cost, and action buttons (Back, Use Room).
**Fidelity notes:** Full Room function text appears in place at close zoom. No separate modal. Back restores prior camera position.
**Transition:** Back → overview. Use Room → payment scene.

### 4.4 Move targeting

**Scene:** `targeting`
**Elements:** Map at neighborhood zoom + targeting context band ("Move · choose a destination" + Cancel) + only legal destinations with target affordances.
**Fidelity notes:** Navigation and targeting are separate. Invalid destinations are omitted (per AGENTS.md: "don't show invalid moves"). Pan/pinch remain available to reach off-screen legal targets.
**Transition:** Tap legal target → payment scene. Cancel → overview.

### 4.5 Card inspection

**Scene:** `hand`
**Elements:** A large, opaque, flat card face; printed timing/cost/effect region; private-state label; Close and begin-effect controls.
**Fidelity notes:** Production must reproduce the verified publisher face exactly. Beginning an effect opens only its legal printed choices; closing makes no game change. The prototype uses an explicit structural placeholder rather than inventing missing publisher text.
**Transition:** Tap a hand card or Play card → hand scene. Close → overview. Begin effect → its rule-defined target/choice state.

### 4.6 Pay action cost

**Scene:** `payment`
**Elements:** Task surface with payment grid showing all hand cards. Each card has type mark (A/R/C), name, eligibility label. Confirm enabled only when exactly the required number of eligible cards are selected.
**Fidelity notes:** Contamination cannot pay Action-card costs (RB p. 17). Cards discarded as cost do not resolve their effects (RB p. 13). The player chooses which cards — the engine must not auto-discard.
**Transition:** Confirm → resolution scene. Cancel → prior scene.

### 4.7 Search choice

**Scene:** `search`
**Elements:** Task surface with drawn Item cards. Choose one. Unchosen cards return to deck bottoms — never to discards, never broadcast.
**Fidelity notes:** Search is a Search Action-card effect, not a generic Basic Action (RB p. 28). The current engine incorrectly auto-picks (BUG-007); the concept presents the choice explicitly.
**Transition:** Confirm → resolution scene. Cancel → overview.

### 4.8 Resolution

**Scene:** `resolution`
**Elements:** Task surface showing the ordered resolution sequence — dice result, bag token, card drawn, effects applied. Each step visible until acknowledged. "Continue" returns to play.
**Fidelity notes:** Every random input and consequence remains visible until acknowledged. No silent damage, movement, or marker exhaustion.

### 4.9 Intruder phase

**Scene:** `intruder`
**Elements:** Map with phase agenda overlay (Burning → Attacks) + reaction tray at bottom ("Reaction window: 1 condition currently met" + Inspect Reaction button).
**Fidelity notes:** Reactions may be played at any point (RB p. 17). A passed player may still react (RT-003). The UI must not skip the reaction window.

### 4.10 Private state

**Scene:** `private`
**Elements:** Privacy banner + tabbed view (Objectives / Hand / Items / Wounds). Objective faces and fulfillment text are owner-only. Objective Choice has an explicit "Begin objective choice" button.
**Fidelity notes:** Other players receive only total hand size and public Character-board state. Objective faces, Action/Contamination identities, Contamination count, Backpack contents, scan results, and unrevealed components never enter another player's view model.

### 4.11 Log and reference

**Scene:** `reference`
**Elements:** Searchable reference + tabbed view (Recent log / Rules / Cards / Settings). Log entries use timestamp + description. Rules entries cite source (Rulebook page numbers).
**Fidelity notes:** The log explains what happened; reference reproduces official terminology. Neither invents legal options.

### 4.12 Reconnect

**Scene:** `reconnect`
**Elements:** Blocking state with connection-lost symbol, explanation ("No automatic Pass, replacement, or rollback"), Retry button, and diagnostic code.
**Fidelity notes:** Network disconnection is a digital policy, not a publisher rule (no official rulebook/FAQ rule exists). The concept pauses and preserves state without introducing an unofficial gameplay decision.

### 4.13 Death / spectator

**Scene:** `dead`
**Elements:** Map with "CHARACTER DEAD" + "SPECTATOR VIEW" phase agenda. No command dock. Public state and log remain available.
**Fidelity notes:** A dead Character "no longer takes part" (RB p. 18). The spectator sees public information only.

### 4.14 End of game

**Scene:** `end`
**Elements:** Blocking state with "14" or explosion symbol + ordered procedure list:
1. Apply pending Autodestruction
2. Resolve final Infection or Eclosion
3. Choose an Objective if none was chosen
4. Reveal and check each surviving Character's chosen Objective
5. Declare winners
**Fidelity notes:** The procedure follows RB pp. 38–39 and `03-intruders-and-survival.md` INT-010/011. Private material is revealed only at the rule-defined step.

---

## 5. Privacy architecture

The concept enforces a hard boundary between private and public information at the view-model level, not merely the display layer.

| Information | Owner sees | Others see |
|---|---|---|
| Objective faces | Yes (always) | No (until End of Game reveal) |
| Action/Contamination card identities | Yes | No (total hand count only) |
| Contamination count | Yes | No |
| Backpack contents | Yes | No (public only when used/traded) |
| Scan/Infection result | Yes | No (unless rulebook authorizes disclosure) |
| Search draws, unchosen Items | Yes | No |
| Anti-Aircraft token face | Yes (during legal check) | No (resolved outcome is public) |
| Robot card identity | Yes (after reveal) | No (until Hibernatorium connection) |
| Deck order, Queen Health values, bag contents | Yes (at draw) | No (until specific reveal rule) |
| Face-up equipment, Armor, Tactical Gear | Yes | Yes (public Character-board state) |
| Health, Oxygen, Serious Wounds, Larva, Data | Yes | Yes (public Character-board state) |
| Character identity, Rank, participation state | Yes | Yes |

**Known current-engine defect:** Full state is broadcast to every client (`network.js:263-276`). The concept's report flags this as a production integrity issue that must be resolved by per-viewer state sanitization before any claim of faithful secrecy.

---

## 6. Rules fidelity boundaries

The concept does not invent, simplify, or silently change any publisher rule. Specifically:

1. **No auto-pass, auto-discard, auto-search-pick, auto-trade, auto-heal, auto-replace, auto-prevent, auto-select Objective, or auto-launch Lander.**
2. **Search is a Search Action-card effect**, not a generic Basic Action (RB p. 28; BUG-007).
3. **Pass is an Action** — the player may discard any number of Action and Contamination cards (RB p. 14; RT-007).
4. **Reactions are available at any printed timing**, including "at any point" (RB p. 17; RT-003).
5. **Objective Choice is once per game, during a Turn, between Actions** (RB pp. 13–14; RT-010).
6. **Lander launch requires one occupant's affirmative decision** — no auto-launch (RB p. 37; RT-009a).
7. **Disconnected players must not be auto-passed** — no publisher rule exists; pause/preserve only.
8. **Finite supplies are rules** — no unlimited digital markers (RB pp. 15, 23).
9. **Fire cannot kill non-Larva Intruders without a die roll** (RB p. 15; FAQ General Rules #1).
10. **Effects resolve in printed sequence** — ignore only impossible instructions for Event cards (RB p. 15; FND-003).

### Unresolved source ambiguities (recorded, not guessed)

The following are documented in `docs/rules/open-questions.md` and are not resolved by the concept:

- OQ-001: Eclosion starting hand — whether pre-existing cards count
- OQ-002: Sequential Infection interaction
- OQ-003: Starting Player token passing to dead/escaped/hibernated Characters
- OQ-004: Mid-turn death advancement procedure
- OQ-006: Intruder Help Sheet token-effect transcription
- OQ-007: Simultaneous multi-Intruder entry into a secured Room
- OQ-009: Queen/Nest placement before Nest discovery
- Robot Malfunction contradiction (RB p. 23 vs p. 37)
- FAQ "Open Corridor" undefined term
- Concurrent Reaction timing priority

The concept never chooses an interpretation for these. A future implementation state that touches one must stop at the unresolved boundary and surface the recorded source conflict; this prototype does not fabricate a group ruling.

---

## 7. Desktop adaptation

Desktop inherits the same hierarchy, expanded rather than restructured:

- The map viewport expands to fill available width.
- The status stack becomes a horizontal bar (not a stacked column).
- The command dock becomes a right-aligned panel or bottom bar.
- The hand rail gains more horizontal space.
- The context band can remain visible alongside the map rather than replacing it.
- Keyboard navigation becomes primary; touch gestures remain available on hybrid devices.

No separate desktop information architecture is invented. The mobile hierarchy is the hierarchy.

---

## 8. Grayscale and non-color verification

The user's core requirement: "if this were viewed on a black and white screen, is it still understandable?"

**Prototype grayscale toggle:** The prototype includes a CSS `.grayscale` class that applies `filter: grayscale(1)` to the entire concept app. The QA harness verifies that Life Support status, current-Room status, and legal-target status retain words/symbols/patterns; it also checks the captured image pixel-by-pixel and found a maximum RGB channel spread of 0.

**Verified non-color encodings in the prototype:**

| State | Visual channels (beyond color) |
|---|---|
| Life Support Active | ✓ checkmark in bordered square |
| Life Support Damaged | ! exclamation in triangle clip-path |
| Life Support Inactive | × in circle with 45° hatching pattern |
| Fire | ♨ symbol + diagonal hatched fill |
| Malfunction | ⚡ symbol + crosshatch fill |
| Secure | ▣ symbol + double-border |
| Noise | ≈ symbol + dashed circular border |
| Intruder occupant | Rotated square (45°) + hatched fill |
| Character occupant | Circle + 2-letter initials |
| Door Open | Dashed line |
| Door Closed | Thick solid line |
| Door Destroyed | X-cross marks |
| Current Room | White shell + "CURRENT" dashed text label |
| Legal target | White shell + hatched fill + "MOVE" text |
| Action card | Clip-path corner cut + "ACTION" text label |
| Contamination card | Hatched fill + double border + "CONTAMINATION" text |
| Turn badge | "YOUR TURN" / "SPECTATING" text + double-border shape |
| Phase step | Checkmark prefix (✓) for done + "ACTIVE" text for current |
| Mission Task | "MISSION TASK" text label + one-line summary |
| Autodestruction | ⌛ hourglass symbol + "AUTO R10" text |

---

## 9. QA results

**Harness:** `docs/qa/mobile_concept_qa.py` — Playwright browser QA.

**Latest verified command:** `python3 docs/qa/mobile_concept_qa.py`

**Result: 374 passed, 0 failed, 0 warnings across 84 scene/viewport combinations.**

### Viewport matrix

Every one of the 14 scenes was exercised at all six sizes:

- 320 × 568 tiny portrait
- 360 × 800 compact portrait
- 390 × 844 standard portrait
- 412 × 915 large portrait
- 844 × 390 phone landscape
- 1180 × 600 large touch landscape / compact desktop adaptation

For every combination, the harness verifies scene construction, absence of page-level horizontal overflow, main-stage fit to the device content box, a usable main-stage height, visible controls of at least 44 × 44 CSS px, and absence of JavaScript errors.

### Interaction and semantic coverage

| Check | What it verifies | Result |
|---|---|---|
| Non-color state contract | Life Support words/symbols; Fire hatch; Malfunction crosshatch; Secure double border; Noise dashed border; Current/MOVE labels; numeric segmented vitals; labeled, double-border Contamination | PASS |
| Public roster privacy | Total hand count is present; private composition, Backpack, and Objective terms are absent | PASS |
| Room geometry | Every rendered Room has the canonical six-vertex pointy-top polygon and regular-hex ratio; neighbors and Corridors use only NE/E/SE/SW/W/NW axes; every edge retains visible Corridor spacing | PASS |
| Room focus | Tapping Armory focuses Armory while the Officer remains in Life Support Control B | PASS |
| Legal targeting | Exactly the two fixture-legal connected Rooms are interactive; all invalid Rooms are out of focus order and have no action data | PASS |
| Card inspection | A hand card opens the private card-inspection state instead of acting as a dead control | PASS |
| Payment | Confirm begins disabled, enables at exactly two selected eligible Action cards, and excludes Contamination | PASS |
| Search | Confirm begins disabled and enables only after the player chooses an Item | PASS |
| Navigation gestures | Drag pans without tactical selection; a true two-point Chromium touch gesture changes free map scale | PASS |
| Keyboard | Tab reaches a named control with a visible focus outline | PASS |
| Status feedback | Scene change is announced through `aria-live` without moving focus | PASS |
| Grayscale audit mode | Grayscale filter is active while MOVE, CURRENT, Damaged, patterns, and labels remain present | PASS |
| Grayscale capture pixels | Every pixel in the targeting capture is neutral grayscale (maximum RGB channel spread 0) | PASS |
| Reduced motion | Emulated `prefers-reduced-motion: reduce` suppresses the map transition | PASS |
| Captures | Five representative screenshots are written to `docs/qa/mobile-concept-captures/` | PASS |

### Defects found and fixed during this pass

1. A JavaScript nullish-coalescing expression initially prevented every scene from rendering. Fixed and syntax-checked.
2. The prototype-only scenario panel intruded at 844 × 390. The compact-shell breakpoint now includes phone landscape.
3. At 320–412 px widths, intrinsic grid sizing made the stage 379–550 px wide and silently clipped it inside the device. Explicit zero-minimum grid widths now make stage width equal the device content width.
4. Pointer capture on Room press swallowed Room taps. Capture is now deferred for Room-originating gestures until movement begins, preserving tap-to-focus and drag-to-pan.
5. The first hand controls were dead and used unverified sample card names. They now open a real inspection state and use explicit official-face placeholders until verified publisher transcription exists.
6. The public zero-tap roster was missing. It now displays only permitted public state and total hand counts, with turn/passed status encoded by text and border/text treatment.

### QA limitations (recorded as blockers)

- **No real-device testing:** Playwright exercises Chromium touch input but does not reproduce finger occlusion, OS edge gestures, browser toolbar changes, or hardware safe areas. The proposed 72 px / 150 px semantic-zoom thresholds remain hypotheses until real-device testing.
- **No VoiceOver/TalkBack certification:** The harness checks names, focus, and live regions but does not run a mobile screen reader.
- **No visual-understanding proof:** The grayscale capture and structural assertions verify redundant channels, but human review on a true monochrome display is still required for crowded states.
- **No multi-client privacy proof:** The prototype is single-viewer. Production requires sanitized per-viewer network fixtures and adversarial multi-browser tests.
- **No rules-engine integration:** The prototype demonstrates UI state transitions with deterministic fixtures; it does not prove the current engine resolves publisher rules correctly.
- **Representative, not exhaustive game-state fixtures:** The 14 scenes cover the complete UI architecture and highest-risk interactions, not every possible card, Room, Intruder, wound, Event, simultaneous Reaction, or crowded-Room permutation.

### Existing runtime/harness checks observed during final verification

These results are reported separately because the concept changes do not modify `index.html`, `css/`, or `js/` runtime game files:

- `MOBILE_QA_SCREENSHOTS=0 python3 docs/qa/mobile_layout_qa.py`: **PASS** — current-game mobile pinch, pan, overflow scrolling, desktop wheel zoom, and drag pan.
- `node docs/qa/hex_direction_regression.js`: **FAIL / existing investigation needed** — the script expects rendered bounds inside 1200 × 900, while current geometry reports `(182, 10.0036)` through `(1318, 1039.9964)`.
- `node docs/qa/nest_event_regression.js`: **FAIL / existing fixture or engine investigation needed** — the expected valid discovery Move returns unsuccessful at the script's line 47.
- `python3 docs/qa/art_asset_qa.py`: **BLOCKED by current lobby contract** — the harness requests five players but creates only the host; Start Game remains disabled, so its art assertions never run.

No passing claim in this report includes those three unresolved checks.

---

## 10. Blockers and open work

1. **Privacy architecture:** Full state broadcast must be replaced by per-viewer state sanitization before production.
2. **Semantic-zoom thresholds:** 72 px and 150 px values need real-device validation.
3. **Screen-reader audit:** A dedicated VoiceOver/TalkBack pass is needed.
4. **Rules-engine integration:** The concept must be connected to a rules-faithful engine that resolves the confirmed bugs in `bug-tracker.md`.
5. **Card data transcription:** Full Rest-card, Room Help-sheet, Robot-card, Intruder Help Sheet, and all card-specific text must be transcribed from official PDFs before the UI can display real card content.
6. **Open questions (OQ-001 through OQ-009):** These remain unresolved and must not be silently interpreted.
7. **Concurrent Reaction timing:** No priority protocol exists for simultaneous remote reactions. The UI should queue and present them, not resolve by network arrival order.
8. **Existing regression/harness failures:** Reconcile the hex geometry expectation, hidden-Nest fixture, and five-player art-harness setup described in the QA section before treating the whole repository as green.

---

## 11. Files

| File | Purpose |
|---|---|
| `docs/design/prototypes/mobile-first-ui-concept.html` | Interactive prototype (14 scenes, grayscale toggle, pan/pinch/zoom) |
| `docs/qa/mobile_concept_qa.py` | Playwright QA harness (84 scene/viewport combinations plus semantic and interaction checks) |
| `docs/qa/mobile-concept-captures/` | Five representative browser captures, including a grayscale targeting view |
| `docs/design/mobile-first-ui-report.md` | This report |
| `docs/design/mobile-information-classification.md` | Information inventory and Always/Sometimes classification |
| `docs/design/mobile-tactical-map-interaction.md` | Semantic zoom, Room focus, targeting separation specification |

---

## 12. Bibliography

Web sources were checked on 2026-07-28. Local rule citations use the repository's official Awaken Realms PDFs and extracted text.

1. Norman, D. A. (2013). *The Design of Everyday Things: Revised and Expanded Edition*. Basic Books. ISBN 978-0-465-05065-9.
   https://jnd.org/books/the-design-of-everyday-things-revised-and-expanded-edition

2. Norman, D. A. "Signifiers, not affordances." *ACM Interactions* author version, JND.org.
   https://jnd.org/signifiers-not-affordances/

3. Norman, D. A. and Nielsen, J. "Gestural Interfaces: A Step Backwards In Usability." *ACM Interactions* author version, JND.org.
   https://jnd.org/gestural-interfaces-a-step-backwards-in-usability/

4. Krug, S. (2014). *Don't Make Me Think, Revisited: A Common Sense Approach to Web Usability*, 3rd edition. New Riders/Pearson. ISBN 978-0-321-96551-6.
   https://sensible.com/dont-make-me-think

5. Nielsen, J. (1994, last reviewed 2024-01-30). "10 Usability Heuristics for User Interface Design." Nielsen Norman Group.
   https://www.nngroup.com/articles/ten-usability-heuristics/

6. Nielsen, J. "Progressive Disclosure." Nielsen Norman Group.
   https://www.nngroup.com/articles/progressive-disclosure/

7. Budiu, R. (2024-01-15). "Memory Recognition and Recall in User Interfaces." Nielsen Norman Group.
   https://www.nngroup.com/articles/recognition-and-recall/

8. Apple. "Buttons." Human Interface Guidelines.
   https://developer.apple.com/design/human-interface-guidelines/buttons

9. Apple. "Accessibility." Human Interface Guidelines.
   https://developer.apple.com/design/human-interface-guidelines/accessibility

10. Apple. "Motion." Human Interface Guidelines.
    https://developer.apple.com/design/human-interface-guidelines/motion

11. Google. "Icon buttons — Accessibility." Material Design 3.
    https://m3.material.io/components/icon-buttons/accessibility

12. W3C WAI. "Understanding Success Criterion 1.4.1: Use of Color." WCAG 2.2.
    https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html

13. W3C WAI. "Understanding Success Criterion 1.4.3: Contrast (Minimum)." WCAG 2.2.
    https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

14. W3C WAI. "Understanding Success Criterion 1.4.11: Non-text Contrast." WCAG 2.2.
    https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html

15. W3C WAI. "Understanding Success Criterion 2.3.3: Animation from Interactions." WCAG 2.2.
    https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html

16. W3C WAI. "Understanding Success Criterion 2.5.8: Target Size (Minimum)." WCAG 2.2.
    https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html

17. W3C WAI. "Understanding Success Criterion 4.1.3: Status Messages." WCAG 2.2.
    https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html

18. *Nemesis: Retaliation* Official Rulebook. Awaken Realms. `docs/rulebooks/Nemesis_RT_Rulebook_official.pdf`

19. *Nemesis: Retaliation* Official FAQ v1.2. Awaken Realms. `docs/rulebooks/Nemesis_RT_FAQ_v1.2.pdf`

20. Project rules corpus: `docs/rules/00-foundations.md` through `03-intruders-and-survival.md`, `open-questions.md`, `bug-tracker.md`, `deviations.md`.