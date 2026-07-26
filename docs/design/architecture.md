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

### Exploration System
- Current: player picks a cardinal direction, engine draws exploration card, places room at that position
- Simplified from physical game: doesn't handle corridor placement orientation precisely
- Future: should use actual exploration card layout for corridor placement

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
- [ ] Corridor tiles rendered as proper tiles between rooms, not just lines between centers
- [ ] Room layout should match physical game's grid positioning (3 sections, border pieces)
- [ ] Privacy section in architecture.md is outdated — privacy is now UI-layer only, not state sanitization. Update this doc.

### Medium Priority
- [ ] Card art / graphics
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