# Nemesis: Retaliation Digital Edition - Design Notes

## Architecture Decisions

### Host-Authoritative Model
- Host runs the full game engine; clients are thin (send actions, receive state)
- Chosen over client-side authority to prevent cheating and simplify conflict resolution
- Trade-off: if host disconnects, game is lost (no host migration yet)

### Privacy Filtering
- `serializeStateForPlayer(state, playerId)` in network.js
- Hides: other players' objectives, hand cards, backpack, hand slots, tactical belt, serious wounds, contamination cards
- Hides: all deck contents (event, intruder attack, serious wound, queen health, contamination, item decks)
- Hides: intruder bag contents, anti-aircraft token order, robot card (until revealed)
- Each client receives a different sanitized view of the same state

### Multiplayer Continuity
- A disconnected joined player pauses the game immediately. Their character, cards, objectives, and all other slot state remain intact.
- The game cannot start until every configured seat is filled. During a game, a connection may reclaim a disconnected joined seat; once every joined seat is connected, the game resumes from exactly the paused state.
- Disconnected players are never skipped in turn order, phase progression, or Starting Player rotation.
- Host migration is not implemented: if the host disconnects, the authoritative state is unavailable. This is a distinct limitation from client reconnection.

### Exploration System
- Current: player selects a highlighted legal destination directly on the tactical map. Exploration targets are empty neighboring nodes in all eight compass directions (`N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW`) within the fixed mat-derived slot set.
- Invalid targets are omitted by the UI and independently rejected by the authoritative engine (off-board, occupied, direction mismatch, or more than one grid step away).
- Every room has an `exits` index keyed by compass direction. Every corridor stores `directionFromRoom1` and `directionFromRoom2`, which are always opposites.
- Simplified from physical game: exploration currently creates only the edge used to enter the new room. Future rule work should apply authored exploration-card exit layouts and edge-count restrictions.

### Tactical Board Rendering
- The complete 32-bay mat layout is visible from game start as subdued empty flat-top hexagonal slots. Its stepped outer perimeter deliberately omits the physical mat's outer voids. Exploration fills a slot; it never creates or repositions the field.
- Rooms and empty slots are regular 110px-wide flat-top hexagons, with height `width × sqrt(3) / 2`. Inner walls, status overlays, movement highlights, and hit testing derive from the same geometry.
- Fixed 42px cardinal spacing also leaves open corner-to-corner space for diagonal corridors, even when no graph edge exists.
- Existing cardinal and diagonal corridors render beneath rooms and only remain visible between room boundaries; absent corridors leave the reserved gap empty.
- Movement uses direct map highlights instead of a compass modal.

### Mobile Interaction
- The viewport permits normal browser accessibility zoom outside the map; mobile accessibility is not locked with `user-scalable=no` or `maximum-scale=1`.
- A custom two-finger gesture and explicit controls scale the tactical map from 50% to 300% relative to its fitted size. Pinch is continuous and anchored under the gesture midpoint; button and mouse-wheel zoom use 10% steps. `Fit` restores the complete-board view.
- A zoomed canvas overflows inside `#canvas-wrapper`; native horizontal/vertical scrolling provides one-finger panning without changing renderer hit-test coordinates.
- On desktop, ordinary wheel input over the map zooms by 10%, while left-button dragging pans the overflow viewport. A drag threshold suppresses the synthetic tactical click on release.
- Board, player, card, and log tabs own their scrolling. Oversized content scrolls inside the active panel rather than being clipped by a fixed `100vh` layout.
- `docs/qa/mobile_layout_qa.py` exercises portrait and landscape phone viewports with real CDP two-point pinch-in/pinch-out input, map pan, touch selection after panning, Fit reset, and oversized-content reachability.

### Production Art Layer
- Game-facing art is independently generated SVG under `assets/generated/`; the gitignored research library is never loaded at runtime.
- `js/assets.js` is the semantic registry for board, room, character, intruder, card, marker, and control art. Game data IDs select assets rather than UI call sites hard-coding file names.
- The canvas preloads 35 mapped images and retains procedural fallbacks. Loading art does not alter room geometry, movement highlighting, hit testing, or authoritative game state.
- Cards and dashboards use external SVG symbols plus visible text labels. Color reinforces type and state but is not the only identifier.
- Regenerate with `scripts/generate_game_art.py`; validate with `docs/qa/art_asset_qa.py` and the existing multiplayer QA.

### Intruder AI
- Current: simplified shortest-path toward closest character
- Missing: full BFS pathfinding, proper corridor/room alternating movement, tie-breaking by corridor ID
- Missing: proper "only 1 intruder enters room" enforcement in all cases

## Game Components

### Characters (6)
1. Contractor (rank 3) — no starting support equipment, versatile
2. Recon (rank 1) — Sprint ability, scanner
3. Officer (rank 4) — Command lower-rank players
4. Medical Support (rank 2) — Rest action, field medkit
5. Heavy Gun Operator (rank 2) — Auto shotgun, bonus hit on shoot
6. Combat Engineer (rank 2) — Reinforce corridors, drill new ones

### Rooms (23)
- Section A (3): Landing Zone, Drilling Room, Life Support Control A
- Section B (4): Hibernatorium, Cooling System, Life Support Control B, Server Room
- Section C (4): Life Support Control C, Nest, Reactor, Escape Shuttle
- Random ? (12): Armory, Surgery, Lab, Gunnery, Shelter, Tech Corridor, Sprinklers, Engine, Storage, Comms, Waste Disposal, Airlock, Power Generator

### Items (90)
- Red (30): Weapons (pistols, rifles, shotguns, etc.)
- Yellow (30): Heavy/utility (duct tape, robots, armor, etc.)
- Green (30): Support/consumables (medpacks, oxygen, scanner, etc.)

### Events (20)
- Each moves intruders (corridors → rooms, rooms → corridors) + special effect
- Key events: Reactor Overheating, Queen Awakening, Hull Breach, Power Surge

### Intruder Bag
- 16 blanks (return to bag), 8 drone tokens, 12 adult tokens, 6 larva tokens, 3 queen tokens
- Bag development: add tokens each round based on round number

## TODO / Known Issues

### High Priority
- [ ] Item choice modal on search (currently auto-picks first)
- [ ] Trade exchange modal (engine works, UI doesn't)
- [ ] Full intruder pathfinding (BFS with tie-breaking by corridor ID)
- [ ] Proper corridor placement orientation from exploration cards
- [ ] Room layout should match physical game's grid positioning (3 sections, border pieces)
- [ ] Privacy section in architecture.md is outdated — privacy is now UI-layer only, not state sanitization. Update this doc.

### Medium Priority
- [x] Functional original card art, room surfaces, unit tokens, dashboard art, and semantic graphics
- [ ] Unique authored illustrations and state variants listed in `docs/art-reference/production-assets.md`
- [ ] Expansion content (Sangrevore, Xyrians, etc.)
- [ ] Solo/Coop mode objectives
- [ ] Deadly mode (dual noise values)
- [ ] Reconnection support (player reclaiming their slot)
- [ ] Host migration (if host disconnects, game is lost)
- [ ] Noise roll should actually place intruders from bag (currently only Hazard result does)
- [ ] Unjoined player slots should auto-pass turns (currently alive=true but not connected, engine skips them)

### Low Priority
- [ ] Sound effects / music
- [ ] Animations (dice rolls, card flips, intruder movement)
- [ ] Spectator mode
- [ ] Game replay / history
- [ ] Contamination card scanning UI (scanner item)
- [ ] Anti-aircraft token checking UI (Life Support Control B room)