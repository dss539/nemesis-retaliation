# Nemesis: Retaliation — Digital Rewrite Architecture Proposal

**Status:** Proposed  
**Date:** 2026-09-06  
**Scope:** Base game rewrite from scratch, replacing the prototype implementation  
**Author:** Hermes Agent / Project Owner Collaboration  

---

## 1. Executive Summary

This document proposes the engineering architecture for the clean-slate rewrite of *Nemesis: Retaliation Digital Edition*. 

The rewrite replaces the legacy vanilla JS prototype (`js/data.js`, `js/engine.js`) with a modern, type-safe, mobile-first web application. It consumes the audited and reconciled rules corpus (`docs/rules/00-04`), controlled vocabulary (`docs/rules/vocabulary/`), and static taxonomy/ontology (`docs/rules/ontology/`).

Key constraints satisfied:
- **Zero server infrastructure:** Pure client-to-client P2P via WebRTC with public PeerJS cloud signaling.
- **Trusted environment:** No anti-cheat cryptography; authoritative shared state with UI-layer privacy filtering.
- **Mobile-first, desktop-rich:** Responsive "unfolding" layout that works smoothly on a 390px mobile screen while scaling to multi-pane desktop displays.
- **Deterministic state machine:** Action-reducer pattern powered by seeded PRNG, providing instant save/load, seamless hot-joining, reconnection, and turn take-backs.
- **Modern lightweight stack:** TypeScript + Vite, compiling to static assets deployable on GitHub Pages.

---

## 2. Technology Stack

| Layer | Selection | Justification |
|---|---|---|
| **Language** | TypeScript | Discriminated union typing for game actions, exhaustive pattern matching in reducers, refactoring safety across 2,100+ rules/facts. |
| **Build & Tooling** | Vite | Instant sub-second HMR dev server, fast production bundling (`dist/`), first-class PWA plugin support (`vite-plugin-pwa`). |
| **Tactical Board** | HTML5 2D Canvas | 60 FPS mobile pan/zoom and touch interactions across 23 hex rooms, corridors, and dynamic tokens without DOM thrashing. |
| **UI Components** | Lightweight Reactive (e.g., Preact / Solid) | Tiny footprint (<10 KB), fast virtual/reactive DOM for dashboards, card hands, inventory sheets, and dialogs. |
| **P2P Networking** | PeerJS (WebRTC DataChannels) | Serverless peer-to-peer data channels; uses public PeerJS broker for simple room-code discovery (`nemesis-XXXX`). |
| **Client Storage** | IndexedDB via `idb-keyval` | Asynchronous local auto-saving of snapshots and action history on every turn. |
| **Deployment** | GitHub Pages (Static Hosting) | Zero server ops or hosting costs. Single command deployment via GitHub Actions. |

---

## 3. P2P Networking & Rendezvous

### 3.1 Signaling & Room Discovery
- **Signaling Broker:** Uses the public PeerJS cloud broker (`0.peerjs.com`). It handles SDP offer/answer exchanges and STUN discovery during the 2-second initial connection handshake. Once connected, data flows directly peer-to-peer over WebRTC DataChannels.
- **Room Rendezvous UX:**
  - **Host ID:** Host registers a peer ID formatted as `nemesis-rt-<ROOM_CODE>` (e.g., `nemesis-rt-7482`).
  - **4-Character Code:** Joining players type the 4-character code into an input field.
  - **Invite Link:** Deep-link URL hash `https://<site>/#room=7482` auto-connects joiners.
  - **Optional QR Code:** Host screen can optionally display a QR code for camera scan.

### 3.2 Topology: Virtual Host (Star) with Seamless Failover
- **Star Topology:** One client acts as the **Coordinator / Virtual Host**.
- **Action Serialization:**
  1. A player client dispatches an action request `{ type, payload, senderId }` to the Coordinator over WebRTC.
  2. The Coordinator validates the action against the current state, assigns a sequential monotonic `actionId`, applies it to the state reducer, and broadcasts the confirmed `{ actionId, action }` to all peers.
  3. All peers apply the confirmed action to their local reducer.
- **Failover / Host Migration:**
  - Every client maintains the identical state snapshot and action log.
  - If the Coordinator drops (disconnect/close), peers detect the heartbeat loss and automatically elect the surviving peer with the lowest PeerJS ID as the new Coordinator. Game progress is never lost.

### 3.3 Hot-Joining & Reconnection
- **Hot-Joining:** When a new peer joins an in-progress game, the Coordinator transmits:
  1. The latest full state snapshot.
  2. The active seed state of the PRNG.
  3. The current unacknowledged action sequence number.
  The joiner hydrates their local state machine in one turn.
- **Mobile Backgrounding & Reconnection:**
  - Mobile browsers suspend WebRTC channels when locked or backgrounded.
  - On page wake/focus, the client attempts immediate WebRTC reconnect. If reconnected, it requests all action deltas since its last recorded `actionId` (or a fresh snapshot).
  - Web Wake Lock API (`navigator.wakeLock`) is acquired during active game phases to prevent the screen from turning off mid-turn.

---

## 4. State Management & Determinism

### 4.1 Pure Reducer Architecture
The core rules engine is completely decoupled from UI, DOM, and network:
```ts
function gameReducer(state: GameState, action: GameAction, prng: PRNG): GameState
```
- **Seeded PRNG:** All stochastic outcomes (Intruder bag draws, attack cards, noise rolls, exploration draws) use a deterministic seeded generator (e.g., Mulberry32). Given `(seed, actionHistory)`, any client can reproduce the exact game state turn-for-turn.
- **Undo / Step Back:** Because actions are pure events applied to a reducer, rolling back a misclick or player error simply rolls the state back to `actionId - 1`.

### 4.2 Save & Load
- **Auto-Save:** Every state mutation commits `{ snapshot, actionHistory, lastUpdated }` to browser `IndexedDB`. If a player accidentally refreshes or crashes, the local session reloads instantly.
- **Export / Import:** Players can export game state as a portable JSON file or text string, enabling campaign resumption across different devices, QA reporting, and test scenario replay.

### 4.3 UI-Layer Information Privacy
- Because players are cooperative/friendly and trusted, the engine does not perform complex cryptographic state masking.
- The authoritative `GameState` contains full board and deck state.
- The UI layer applies visibility filters:
  - Private Objectives: Rendered only if `objective.ownerId === localPlayerId`.
  - Hand / Backpack: Full details shown only to the owner; other players see card counts.
  - Decks / Intruder Bag: Face-down ordering is known to the state machine but concealed from the UI view.

---

## 5. UI Architecture: Mobile-First Unfolding Layout

### 5.1 Responsive Strategy & Display Performance
The interface uses an unfolding layout pattern sharing one reactive state store.

High-Refresh Mobile Rendering:
- Canvas animation loops synchronise via native `requestAnimationFrame`, unlocking the full display refresh rate (90 Hz, 120 Hz ProMotion / Smooth Display).
- Map interactions (pinch, pan, inertia scrolling) calculate transforms on hardware-accelerated 2D context surfaces without blocking the main event thread or garbage-collecting transient objects during active gestures.

### 5.2 Layout Breakdown
- **Mobile Viewport (<= 768px):**
  - Full-screen tactical canvas map with smooth continuous pinch and pan.
  - Collapsible, swipeable bottom drawers for Action cards, Equipment, and Room interactions.
  - Slim top bar for Round track, Phase indicator, and active turn status.
  - Haptic feedback (`navigator.vibrate`) for alarms, turn notifications, and combat alerts.
- **Desktop Viewport (> 768px):**
  - **Left Pane:** Room inspection details, available Room actions, Intruder status.
  - **Center Pane:** Full tactical map visible with zero-pan framing, smooth mouse zoom/pan, and token movement animations.
  - **Right Pane:** Active player dashboard, Hand cards, Backpack, Tactical Gear, and Private Objectives.
  - **Bottom Bar:** Round track, Intruder bag counts, and peer connection status chips.
  - Hover tooltips for instant inspection; keyboard shortcuts (`Space` to pass, `1-5` for cards, `M` for move, `Esc` to cancel).

---

## 6. Implementation Phasing: Pure Engine First, UI Second

To ensure rock-solid rules fidelity and zero throwaway work, the entire business logic and rules engine will be built, tested, and fuzz-tested headless before writing UI components.

### Stage 1: Headless Rules & State Engine (CLI / Vitest)

1. **Step 1.1: Core Types & Foundations**
   - Setup TypeScript types derived directly from approved vocabulary and ontology (`RoomId`, `CorridorId`, `ItemCard`, `ActionCard`, etc.).
   - Seeded deterministic PRNG (Mulberry32).
   - Core reducer foundation: setup, character drafting, round sequence, action costs, and turn order.

2. **Step 1.2: Spatial Engine & Exploration**
   - Hex grid coordinate math (23 pointy-top room slots, 6 directions).
   - Corridor graph, Door states, and Technical Corridors.
   - Movement action validation, Room exploration token reveals, Room tile placements, and Corridor Noise rolls.

3. **Step 1.3: Character Actions & Item Systems**
   - 60 Action cards: costs, play windows, and exact operative effects.
   - Basic actions: Move, Search, Shoot, Burst, Melee, Trade, Room Action.
   - Item deck management (Red, Yellow, Green), Backpack storage, and Tactical Gear rules.

4. **Step 1.4: Intruders, Bag Mechanics & Combat**
   - Intruder bag development and token draw procedures.
   - Intruder AI pathfinding and movement.
   - Combat resolution: Noise roll triggers, Surprise attacks, Attack cards, Damage, and Serious Wounds.
   - Event phase resolution, Contamination scan/infection, Queen health deck, and all Facility destruction/Endgame triggers.

5. **Step 1.5: Headless Engine Verification & Fuzzing**
   - Vitest test suite executing scenarios against the 2,126 audited rules and open-question interpretations.
   - Headless random bot / Monte Carlo simulation running thousands of automated games to verify termination, absence of deadlocks, and invariant preservation.
   - State serialization, IndexedDB save/load format, and action history export/import.

### Stage 2: Networking & Synchronization Layer

1. **Step 2.1: PeerJS Integration**
   - WebRTC DataChannel connection lifecycle and 4-character room codes (`nemesis-rt-XXXX`).
   - Virtual host action coordinator and monotonic sequence numbering.
   - Heartbeat monitoring and automated host migration/failover.
   - State snapshot transmission, delta action catch-up, and hot-joining.

### Stage 3: Client Rendering & User Interface

1. **Step 3.1: Tactical Canvas Renderer**
   - High-refresh rate (`requestAnimationFrame`, 90/120 Hz) Canvas 2D engine.
   - Multi-touch gesture handling (pinch, pan, inertia) on mobile; mouse pan/zoom on desktop.
   - Pointy-top hex rendering, corridor gaps, room art, and token sprites.

2. **Step 3.2: Responsive UI & Unfolding Layout**
   - Reactive UI framework setup (Preact / Solid).
   - Mobile drawers, card hand selector, action confirmation modals.
   - Desktop 3-pane layout, hover tooltips, and keyboard shortcuts.
   - PWA Service Worker offline caching and Screen Wake Lock API.

---

## 7. Approval & Next Steps

Upon owner review and approval of this proposal:
1. Update `PROJECT_STATUS.md` to transition from Rules Corpus closure to Implementation Phase 1.
2. Initialize the clean project workspace and build scaffolding.
