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
- Disconnected players are skipped in turn order
- `serializeStateForPlayer()` exists in network.js but is no longer used (kept for reference)

## Key Design Decisions
- Privacy: display-layer only, NOT state sanitization. Host needs full state for engine. Each browser's UI only renders its own player's private info.
- Canvas: renders at devicePixelRatio for crisp text. Base coordinate space 1200x900, rooms 120px. Click handler maps screen coords to base coords.
- Mobile: bottom tab navigation (Board/Players/Cards/Log), touch support, responsive canvas
- Exploration: compass/cross layout picker (N/E/S/W) matching map directions
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
- Corridor rendering: lines drawn between room centers, not properly positioned tiles
- Room connections visible as lines but corridors don't show as tiles between rooms

## Bugs Fixed (7 total)
1. Unjoined player slots started alive=false (broke solo/bot games) → changed to alive=true
2. Dead players could win → endGame now skips dead non-escaped players
3. No intruders appeared → event cards now draw from bag (Infestation=2, Surge=3, Nest Defense=Drone)
4. Suffocation didn't kill → now kills on next turn after oxygen hits 0
5. Queen never moved/attacked → now places in discovered room if Nest not on board
6. Exploration blocked by corridor adjacency → exploration moves bypass adjacency entirely
7. Host saw all players' objectives → moved to UI-layer privacy (display only)

## QA
- 4-browser Playwright test: host + 3 clients, 3 rounds, all synced, no errors
- Full 13-round single-engine test: found and fixed all 7 bugs above
- Test scripts in docs/qa/ (4browser_qa.py is reusable, others gitignored)
- Playwright installed on smithers for multi-browser testing

## Rulebooks
All official PDFs and extracted text are in `docs/rulebooks/` (gitignored):
- `Nemesis_RT_Rulebook_official.pdf` — main 40-page rulebook
- `Nemesis_RT_FAQ_v1.2.pdf` — official FAQ & errata
- `rulebook_text.txt` — extracted text from main rulebook
- `faq_text.txt` — extracted text from FAQ
- Plus expansion rulebooks (Sangrevore, Xyrians, Contractors, Insider, SG, SS)

## Git
- Identity: Derrick Southerland <dss539@users.noreply.github.com>
- Branch: main
- GitHub Pages: enabled, auto-deploys from main

## How to Resume Work
1. Read this file (AGENTS.md) for full project context
2. Read `docs/design/architecture.md` for design decisions and TODO
3. Read `docs/qa/full-game-report.md` for QA findings
4. Rulebook PDFs in `docs/rulebooks/` for rules reference
5. To test multiplayer: use Playwright (installed on smithers), write a Python script that launches multiple headless Chromium instances. See `docs/qa/4browser_qa.py` for pattern.
6. To test locally: `python3 -m http.server 8889` then open http://localhost:8889

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
- Corridor tiles rendered as proper tiles between rooms, not just lines
- Room layout should match physical game's grid positioning