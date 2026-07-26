# Nemesis: Retaliation - Digital Edition

## Project Overview
A faithful web-based digital adaptation of the board game Nemesis: Retaliation by Awaken Realms.
- **Live site:** https://dss539.github.io/nemesis-retaliation/
- **Repo:** https://github.com/dss539/nemesis-retaliation
- **Tech:** Vanilla JS, PeerJS (WebRTC P2P), HTML5 Canvas, CSS. No build step, no server.

## Architecture
- `index.html` — entry point, lobby + game screens
- `css/style.css` — all styling, responsive/mobile
- `js/data.js` — game data (characters, rooms, items, events, intruders, objectives)
- `js/engine.js` — core rules engine (authoritative, runs on host)
- `js/network.js` — PeerJS multiplayer, state sync, privacy filtering
- `js/render.js` — 2D canvas board renderer
- `js/ui.js` — UI panels, modals, action bar, tab navigation
- `js/main.js` — lobby flow, game start, screen switching

## Networking Model
- Host-authoritative: host runs the engine, clients send actions via WebRTC
- PeerJS for P2P (no server needed, just PeerJS broker for signaling)
- State is sanitized per-client (hide other players' objectives, hand, backpack, decks)
- Disconnected players are skipped in turn order

## Key Design Decisions
- Privacy: `serializeStateForPlayer()` hides other players' private info and all face-down deck contents
- Mobile: bottom tab navigation (Board/Players/Cards/Log), touch support, responsive canvas
- Exploration: simplified — players pick a direction, engine draws exploration card and places room

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

## Rulebooks
All official PDFs and extracted text are in `docs/rulebooks/`:
- `Nemesis_RT_Rulebook_official.pdf` — main 40-page rulebook
- `Nemesis_RT_FAQ_v1.2.pdf` — official FAQ & errata
- `rulebook_text.txt` — extracted text from main rulebook
- `faq_text.txt` — extracted text from FAQ
- Plus expansion rulebooks (Sangrevore, Xyrians, Contractors, Insider, SG, SS)

## QA
- Two-browser Playwright test verified: join, game start, actions, turn passing, round transition, state sync, privacy
- Test script pattern: launch two Chromium instances, one hosts, one joins, verify both see same state

## Git
- Identity: Derrick Southerland <dss539@users.noreply.github.com>
- Branch: main
- GitHub Pages: enabled, auto-deploys from main

## Future Work
- Card art/graphics
- Full trade UI
- Item choice on search
- Expansion content
- Solo/Coop objectives
- Deadly mode
- Sound/music
- Proper intruder pathfinding (BFS)
- Reconnection support (player reclaiming their slot)