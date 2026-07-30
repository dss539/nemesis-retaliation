# Nemesis: Retaliation - Digital Edition

## Project Overview
A faithful web-based digital adaptation of the board game Nemesis: Retaliation by Awaken Realms.
- **Live site:** https://dss539.github.io/nemesis-retaliation/
- **Repo:** https://github.com/dss539/nemesis-retaliation
- **Tech:** Vanilla JS, PeerJS (WebRTC P2P), HTML5 Canvas, CSS. No build step, no server.

## Architecture
- `index.html` — entry point, lobby + game screens
- `css/style.css` — all styling, responsive/mobile, compass picker
- `js/data.js` — game data (characters, rooms, items, events, intruders, objectives)
- `js/engine.js` — core rules engine (authoritative, runs on host)
- `js/network.js` — PeerJS multiplayer, state sync
- `js/render.js` — 2D canvas board renderer (1200x900 base, DPR-aware)
- `js/ui.js` — UI panels, modals, action bar, tab navigation, compass picker
- `js/main.js` — lobby flow, game start, screen switching

## Networking Model
- Host-authoritative: host runs the engine, clients send actions via WebRTC
- PeerJS for P2P (no server needed, just PeerJS broker for signaling)
- Full state sent to all clients — privacy is UI-layer only (renderCardArea only shows local player's hand/objectives/backpack)
- A disconnected joined player pauses the game; their slot can be reclaimed without changing state, and turn/phase progression cannot continue until it is filled.
- `serializeStateForPlayer()` exists in network.js but is no longer used (kept for reference)

## Key Design Decisions
- Privacy: display-layer only, NOT state sanitization. Host needs full state for engine. Each browser's UI only renders its own player's private info.
- Canvas: renders at devicePixelRatio for crisp text. Base coordinate space 1200x900. The fixed, mat-derived field has 23 valid room slots arranged 5/4/5/4/5 by row; each slot holds a regular 160px-wide pointy-top hexagonal Room with vertical E/W sides. Odd rows are offset by half a slot; fixed spacing reserves room for all six hex-edge Corridors. Click handling uses the same hexagonal geometry.
- Map interaction: continuous mobile pinch zoom; 10%-step buttons and desktop wheel zoom; mobile/desktop camera panning includes generous off-board slack while retaining a recovery strip; independently scrollable board/card/player/log panels
- Exploration: XCOM-style board targeting. Legal connected rooms and in-bounds empty hex neighbors in `NE`, `E`, `SE`, `SW`, `W`, and `NW` highlight directly on the map; invalid, occupied, closed-door, and off-board destinations are omitted. Rooms index exits by hex direction, and corridors store their direction from both endpoints.
- Text labels for all game state (fire, broken, secure count, intruder types, noise) — never color alone

## Game Content Status
- Base game: implemented (6 characters, 23 rooms, 90 items, 20 events, 8 mission tasks)
- Expansions: not yet (Sangrevore, Xyrians, Contractors, Insider, Stretch Goals)
- Solo/Coop mode: not yet
- Deadly mode: not yet
- AI opponents: not yet
- Card art: not yet (text-based)

## Known Limitations
- Some room effects are simplified
- Trade UI needs exchange modal (engine supports it)
- Item selection on search is auto-pick (should present choice)
- Intruder movement AI is simplified (shortest path, not full BFS)
- The fixed mat-derived room field is a gameplay boundary. It now preserves the physical mat's stepped outer silhouette, but does not reproduce every printed facility detail or authored room arrangement.

## Bugs Fixed (10 total)
1. Unjoined player slots started alive=false (broke solo/bot games) → changed to alive=true
2. Dead players could win → endGame now skips dead non-escaped players
3. No intruders appeared → event cards now draw from bag (Infestation=2, Surge=3, Nest Defense=Drone)
4. Suffocation didn't kill → now kills on next turn after oxygen hits 0
5. Queen never moved/attacked → now places in discovered room if Nest not on board
6. Exploration blocked by corridor adjacency → exploration moves bypass adjacency entirely
7. Host saw all players' objectives → moved to UI-layer privacy (display only)
8. Exploration could redraw and overwrite the already-placed Landing Zone, creating a self-loop corridor → removed Landing Zone from the undiscovered Section A pool
9. A character killed during an action retained the active turn forever → lethal action resolution now immediately advances to the next eligible player
10. Nest events could place a Drone or Queen at an undiscovered, nonexistent room ID → hidden Nest occupants are reserved and materialized when the Nest is discovered

## QA
- 4-browser Playwright test: host + 3 clients, 3 rounds, all synced, no errors
- 4-browser tactical gameplay test: 11 canvas-selected moves across 3 rounds, 23 four-way sync checks, 8 rooms/7 corridors explored, 2 legitimate player deaths advanced correctly, no browser errors (`docs/qa/tactical-4browser-results.json`)
- Hex-direction regression: six reciprocal `NE`/`E`/`SE`/`SW`/`W`/`NW` neighbors across even and odd rows; deprecated `S` rejected; valid `SE` accepted; E and NE corridors terminate exactly at their hex boundaries (`docs/qa/hex_direction_regression.js`).
- Earlier octagon/8-direction QA artifacts are historical only and superseded by the pointy-top hex renderer and the hex-direction regression above.
- Full 14-round four-browser game: 60 recorded actions, 61 sync checks, 61 graph/topology checks, five representative screenshots, and no browser errors after the hidden-Nest fix (`docs/qa/full-game-report.md`)
- Full action trace and rule/FAQ deviation audit: `docs/qa/full-game-action-log.md`, `docs/qa/full-game-action-log.json`, and `docs/qa/full-game-rules-audit.md`
- Mobile portrait/landscape QA dispatches real two-point pinch-in/pinch-out gestures and verifies map zoom, two-axis pan, touch target coordinates after panning, Fit reset, and oversized board/panel scrolling (`docs/qa/mobile_layout_qa.py`)
- Test scripts in docs/qa/ (4browser_qa.py is reusable, others gitignored)
- Playwright installed on smithers for multi-browser testing

## Rulebooks
All official PDFs and extracted text are in `docs/rulebooks/` (gitignored):
- `Nemesis_RT_Rulebook_official.pdf` — main 40-page rulebook
- `Nemesis_RT_FAQ_v1.2.pdf` — official FAQ & errata
- `rulebook_text.txt` — extracted text from main rulebook
- `faq_text.txt` — extracted text from FAQ
- Plus expansion rulebooks (Sangrevore, Xyrians, Contractors, Insider, SG, SS)

## Rules Corpus
- `docs/rules/` is the human-facing, semi-formal interpretation corpus for the base game. Start with `docs/rules/README.md`.
- Authority is explicit: official FAQ/errata overrides the official rulebook; project interpretations and any deliberate digital adaptations must be visibly labeled and may not silently change tabletop rules.
- `docs/rules/00-foundations.md` through `03-intruders-and-survival.md` provide source-backed operational rules. `open-questions.md` records genuine unresolved source ambiguities.
- `docs/rules/bug-tracker.md` tracks confirmed implementation failures. Bugs and QA failures are never intentional deviations and must be repaired, not normalized.
- `docs/rules/deviations.md` is reserved exclusively for deliberate, remaining digital adaptations.

## Git
- Identity: Derrick Southerland <dss539@users.noreply.github.com>
- Branch: main
- GitHub Pages: enabled, auto-deploys from main

## How to Resume Work
1. Read this file (`AGENTS.md`) for project context
2. Read `docs/rules/README.md` and the relevant source-backed rules record before changing game mechanics
3. Read `docs/rules/bug-tracker.md` and `docs/qa/full-game-rules-audit.md` for known rules failures
4. Read `docs/design/architecture.md` for design decisions and TODO
5. Read `docs/design/play-area-design.md` — the ACTIVE design authority for the play area surface (map, sections, room state, equal-weighting principle); it states its precedence over the older mobile-* design docs
6. Rulebook PDFs and extracted text in `docs/rulebooks/` are the primary official source; FAQ/errata takes precedence
7. To test multiplayer: use Playwright (installed on smithers), write a Python script that launches multiple headless Chromium instances. See `docs/qa/4browser_qa.py` for pattern.
8. To test locally: `python3 -m http.server 8889` then open http://localhost:8889

## Future Work
- Card art/graphics
- Full trade UI (exchange modal)
- Item choice on search (currently auto-picks first)
- Expansion content (Sangrevore, Xyrians, etc.)
- Solo/Coop objectives
- Deadly mode (dual noise values)
- Sound/music
- Proper intruder pathfinding (BFS)
- Reconnection support (player reclaiming their slot)
- Room layout should match physical game's grid positioning