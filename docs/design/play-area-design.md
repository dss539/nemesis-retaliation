# Play Area Design — Current Authority

**Date:** 2026-07-30
**Status:** Active design authority for the play area surface (map, sections, room state presentation, and the chrome immediately around the map).
**Origin:** From-scratch brainstorm session; deliberately not anchored to prior implementations.

## Relationship to other documents

- `mobile-information-classification.md` — **valid and foundational.** Its Always / Sometimes / Not-visible inventory and privacy boundary definitions are inputs to this document.
- `mobile-tactical-map-interaction.md` — **largely compatible.** Its continuous camera + semantic zoom levels + room-focus model remains adopted. Where it implies urgency promotion (principle 6, "urgent global danger must remain visible" as elevated emphasis), the Equal Weighting principle below overrides: urgent state must remain *visible*, never *amplified*.
- `mobile-first-ui-report.md` — **historical concept, not binding.** Consult for citations and viewport QA methodology only. Its specific screen layouts do not constrain this design.
- `architecture.md` — engineering record; unchanged by this document.
- `docs/rules/` — rules authority for *what* is tracked. This document only decides *how* it is shown.

## Core principle: decompose the mat, don't replicate it

The physical mat co-locates three kinds of information because cardboard has no alternative:

1. **Spatial truth** — rooms, corridors, doors, occupants (characters, intruders, robot), fire, malfunction, noise, secure state, eggs/nest, objective-relevant markers.
2. **Global scalars** — round track, phase, per-section Life Support status, mission task, event/queen state.
3. **Piles** — decks, discards, token supplies, the corridor insert, the intruder bag.

On a phone these are decomposed: the map carries all spatial truth; global scalars live in slim persistent chrome; piles live behind one gesture. Fidelity is to the *information* and to the mat's *visual language* (dark substrate, neon room outlines, jigsaw silhouettes, industrial iconography) — not to its physical arrangement.

## Equal Weighting principle (player-confirmed, overriding)

All shared game state renders at equal visual weight, as on the physical table. No pulsing, no severity-based promotion, no derived warning banners (e.g. no "oxygen failing" alert). If Life Support is inactive, the evidence is the neutral status marker in its dedicated spot and any broken marker on the room — noticing it is the player's job.

**Rationale:** some hidden objectives succeed precisely because other players forget things. UI assistance that polices shared state would materially weaken those objectives.

**Scope:** applies to shared state only. A player's own private information (their objective chip, their HUD strip) may be organized for their convenience — that is personal note-keeping, not table assistance.

## The mat background: fixed field, jigsaw sockets, printed sections

Observed from official playmat photography (`art-references/official-gamefound/update-35/003…jpg`, `004…jpg`):

- Dark low-glare field; rooms as neon-outlined hex silhouettes with jigsaw interlock nubs.
- Section boundaries are **two bright continuous seam lines** through the socket grid — visibly brighter/whiter than room outlines. No per-section color fill is evident. The seam line, not tint, carries the grouping.
- A printed frame surrounds the field; border structures adjacent to the field hold status/track components ("Facility and Section border pieces" per the information classification).

Digital treatment:

1. **Fixed layout.** The 23 valid room slots (5/4/5/4/5, pointy-top hexes, odd-row half offset) are a fixed, printed property of the background. Exploration never creates or moves slots.
2. **Jigsaw sockets.** Unexplored slots render as empty printed sockets — the mat's outline with interlock nubs visible, clearly awaiting a tile. An explored room's tile visually clicks into its socket. This is simultaneously faithful, a free affordance (empty socket = potentially explorable), and it keeps the facility silhouette legible from turn one.
3. **Printed sections.** Sections A/B/C render mat-style: a bright seam line at each boundary (echoing the physical print) plus a printed section label on the background. Membership is legible before any room in the section is explored. Per the accessibility rule, the seam + label carry the information; any tint is reinforcement only.
4. **Life Support linkage.** Each section's label area includes its Life Support glyph so the section→LS-room dependency is learnable without the rulebook. Neutral and always-on — printed, not promoted.

## Per-section Life Support status spots

The physical mat gives section oxygen status its **own dedicated spot** (border pieces holding Life Support tokens), separate from any Malfunction marker on the Life Support room itself. The digital play area mirrors this:

- Each section has a fixed status spot at the map border adjacent to that section, showing its Life Support token state (active/inactive) at all times, at neutral weight.
- The broken/malfunction state of the Life Support *room* renders on the room tile like any other room damage. The two indicators are distinct facts and both are shown, as on the table.
- Oxygen loss consequences (per `docs/rules/01-round-and-turns.md`: inactive LS section → lose 1 Oxygen at turn end) are the engine's concern; the map only shows the states.

## Section-limited abilities

Because sections are printed and always legible, ability targeting needs no new vocabulary: when a section-limited ability is aimed, the existing legal-target highlighting simply falls within the section. Invalid targets remain omitted (never shown-disabled), per the established targeting rule.

## Room state grammar

The pileup problem: one hex may hold identity, fire, malfunction, per-edge doors, adjacent noise, multiple characters, multiple intruders, and objective-relevant markers. Physical tables solve this with token stacking and leaning in; we replace "lean in" with a deliberate grammar.

1. **Fixed positional zones.** Every room uses the same internal layout — e.g. room name/icon along the bottom edge; hazard badges (fire, malfunction, secure) in a fixed corner; occupants in the center; special markers in a fixed remaining zone. Learn one room, speed-read the ship. (Exact zone assignments to be settled during visual design; the invariant is *sameness across all rooms*.)
2. **Badges are glyph + text, never color alone.** A fire badge is a flame glyph; tint reinforces but never carries. (Established project rule.)
3. **Semantic zoom** (adopting `mobile-tactical-map-interaction.md`): rendered room size selects information density. Far zoom keeps the survival-critical set — hazard badges, intruder silhouette + count, character dots. Near zoom adds names, door states, item/egg markers. Threshold rule of thumb: anything that can kill you this round survives every zoom level — *at neutral weight*.
4. **Cap and overflow.** The occupant zone shows at most ~3 tokens; beyond that, one token plus a "+N" count. The tap-to-focus room detail view is the authoritative full list (exact intruder types, floor items, who carries what). Map = index; focused room = truth. Detail renders inside the focused room, not a floating overlay (adopted from the map-interaction spec).
5. **Edges own connection state.** Doors and noise are properties of connections, not rooms. They render in the reserved inter-hex gap: noise markers in the corridor gap, door state at the room edge. Never inside the hex, so they don't compete with occupants.

## Around-the-map chrome (play-area-adjacent)

- **Top bar:** round/phase and other global scalars, neutral weight, no promotion.
- **Player roster:** the local player's row is rich (HP, injuries, hand-slot silhouettes, card count, oxygen); other players appear as compact rows/chips showing **public** info only — portrait, visible HP/injuries, and openly carried items. **Egg-carrying gets an at-a-glance icon on both the roster chip and the character's map token** — it's public, high-consequence state.
- **Objective chip:** the local player's private objective(s) as a pinned one-line chip, expandable on tap. Private info, so Equal Weighting does not apply. Optionally the map marks objective-relevant rooms with a subtle ring — visible to that player only.
- **Actions:** the actions list is always visible and primary; cards are secondary in a drawer that peeks its top edge (established preference). 
- **Piles/decks:** behind one gesture (drawer or tab), consistent with the classification doc's "Sometimes" tier.

## Focused room view (tap-to-truth)

The authoritative detail view for a single room. Decisions:

1. **Renders in place.** Camera zooms to the room; the hex itself becomes the detail canvas. No floating overlay (adopted from the map-interaction spec).
2. **Inspector only.** Read-only. Actions stay in the persistent action bar with map targeting; "look" and "do" never share a tap.
3. **Any explored room, any time.** Matches leaning over the table. Privacy boundary holds: backpacks hidden, open-carried items shown.
4. **Contents:** full occupant list (exact intruder types, carried items incl. eggs), floor items, fire/malfunction/secure, egg/nest state, per-edge door states, and full room-effect wording (rules-corpus text, labeled if interpretation) — the home of "Sometimes"-tier reference info.
5. **One grammar, two densities.** Same fixed-zone layout as the small glyph, expanded — occupants center with labels, hazards in their corner, effect text along the bottom, doors on their edges. The focused view is the glyph magnified, not a new vocabulary.
6. **Adjacent noise shown.** Noise values on the six adjacent corridors render in the focused view (player-confirmed) — equivalent to reading physically adjacent tiles while leaning in; not assistance.

## Character dashboard (decomposed)

Physical board reference: `art-references/community-bgg/9017222-dashboards.jpg` — character tile center, hand slots top corners, tactical belt left edge, printed basic-actions list with discard costs right side, action discard + oxygen dial right edge, health track along the bottom split into Healthy / Injured / Heavily Injured sections with serious-wound slots.

Decisions:

1. **Split by lifecycle.** Body state (health section, oxygen, wounds, statuses) → always-on HUD strip. Equipment (hands, belt) → HUD silhouettes, tap to expand. Basic-actions list → the persistent action bar, costs inline. Backpack/discard → card drawer. No single dashboard screen in normal play.
2. **Health as sections, not a number.** Three labeled segments (Healthy/Injured/Heavily Injured) with the marker in one and wounds occupying section slots — rules operate on sections (wound placement, armor), so a bare HP number misrepresents the mechanic.
3. **Full-body view on tap.** Tapping own HUD strip opens the complete dashboard: expanded health track, named serious wounds, oxygen dial, statuses, hands, belt, backpack. Other players tapping your roster chip see the same layout privacy-filtered (no backpack, no hand cards). One layout, two privacy levels — same pattern as glyph vs focused room.
4. **Oxygen always visible** (0–7 dial value) on own strip, next to health.
5. **Printed actions reference preserved** (player-confirmed): the full basic-actions list with discard costs appears as static reference inside the expanded dashboard view, mimicking the physical board's teaching role. The action bar remains the contextual/legal-actions surface.

## Decisions log (this session)

| # | Decision |
|---|----------|
| 1 | Decompose the mat (map + chrome + drawers); reject the single-replica-mat approach except as icon/style inspiration. |
| 2 | Equal Weighting: shared state never editorialized; visible ≠ amplified. Overrides prior urgency-promotion concepts. |
| 3 | Life Support is room/section damage state, not a timer; no derived countdown or warning UI. |
| 4 | Per-section LS status spots at the map border, mirroring the physical mat's dedicated spots; distinct from room malfunction markers. |
| 5 | Sections printed on the background: bright seam lines (as on the mat) + labels + LS glyph; legible pre-exploration; carries section-limited ability targeting for free. |
| 6 | Unexplored slots = printed jigsaw sockets; explored tiles click in. |
| 7 | Room state grammar: fixed positional zones, glyph+text badges, semantic zoom, cap-and-overflow, tap-to-focus room detail as authoritative view. |
| 8 | Doors and noise render in the inter-hex gap (connection-owned), never inside rooms. |
| 9 | Roster shows other players' public state incl. egg-carrying icons (roster + map token). |
| 10 | Private objective chip pinned for the local player only. |

## Open questions

- Exact fixed-zone assignments inside the room hex (which corner gets hazards, where markers sit) — to be settled with visual mock-ups against real congested states.
- Whether section labels use the official A/B/C naming visually or a diegetic label style.
- Placement of the three per-section LS status spots for portrait vs landscape (border-adjacent is the principle; exact anchoring TBD).
- How the objective ring (private map annotation) interacts with Equal Weighting — currently justified as private note-keeping; revisit if it feels like assistance creep.
