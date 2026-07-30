# Rules Implementation Bug Tracker

This tracks confirmed rules-implementation bugs — failures to faithfully implement the official rulebook and FAQ. These are **not** intentional deviations. Every item here must be repaired.

Source: `docs/qa/full-game-rules-audit.md` (original audit), verified against current code July 2026.

## Status legend
- **Confirmed** — still present in current code
- **Fixed** — repaired in code since audit
- **Partial** — some aspects fixed, others remain

## High severity

| ID | Area | Status | Evidence |
|----|------|--------|----------|
| BUG-001 | Action costs flattened to 1 card | Fixed | `engine.js` uses a cost table: Cautious Move and Use Room require two Action cards; other paid actions require one. |
| BUG-002 | Cleanup draw-to-five | Fixed | `engine.js:906-915` now loops while `actionHand.length < handSize`. |
| BUG-003 | Objective choice timing/rewards | Confirmed | `network.js:196-200` directly assigns chosenObjective; no turn-window, once-per-turn, track, or 3/2/2/1 card draw validation. |
| BUG-004 | 11 of 20 Event cards perform no main effect | Confirmed | `engine.js:663-732` implements 9 of 20. Missing: Scent of Prey, Short Circuit, Fire Outbreak, System Failure, Breeding, Alarm, Malfunction, Heat Wave, Blocked Passage, Emergency Lighting, Tremor. |
| BUG-005 | Exploration does not always roll Movement Noise | Fixed | `engine.js` explorationSequence now always calls `makeNoiseRoll` after placing the room and creating the incoming corridor. The card entrance effect (`noiseRoll`/`closeDoors`) is applied as an additional effect on top of the standard movement noise. |
| BUG-006 | Exploration ignores additional corridors on cards | Fixed | `engine.js` explorationSequence now reads `exCard.corridors` (N/E/S/W mapped to hex dirs: N→NW+NE, E→E, S→SE+SW, W→W). For each active direction, it creates a corridor if the neighbor slot has a room, or records `exits[dir] = true` for later backfill. Previously-placed rooms with pending exits are connected when the new room fills their target slot. |
| BUG-007 | Search is generic action, not Search Action card | Confirmed | `engine.js:1396-1427` auto-keeps `drawnItems[0]`; unchosen cards go to discard, not deck bottoms. |
| BUG-008 | Item decks contain invalid IDs | Fixed | Item decks are now constructed from defined `GAME_DATA.ITEMS` IDs by type. |

## Medium severity

| ID | Area | Status | Evidence |
|----|------|--------|----------|
| BUG-009 | Melee retaliation cannot be prevented | Confirmed | `engine.js:1386-1391` says "For now, resolve attack" and immediately retaliates. No weapon-malfunction prevention choice offered. |
| BUG-010 | Pass discards all cards automatically | Fixed | Pass accepts an optional validated selected subset of Action and Contamination cards; an omitted selection discards none. |
| BUG-011 | Failed actions consume payment card | Fixed | Action payment is restored when the attempted action fails while its actor remains alive. |
| BUG-012 | Tactical Gear: no ownership check or token removal | Fixed | Gear use validates an owned belt token, removes it, and returns it to the token pool. |
| BUG-013 | Trade transfers no item | Fixed | Trade validates ownership and recipient capacity, then transfers the selected item atomically. |
| BUG-014 | Event movement is generic, not per-card | Confirmed | `engine.js:656-660` moves all corridor then all room intruders for every event. Rulebook says card determines which intruders move and orientation. |

## Low severity

| ID | Area | Status | Evidence |
|----|------|--------|----------|
| BUG-015 | Exploration log uses synthetic target ID | Fixed | `engine.js` now logs the discovered room's display name from `GAME_DATA.ROOMS[id].name` instead of the synthetic `explore_*` id, both in the move log and the discovery log. |

## Latent / survival / endgame

| ID | Area | Status | Evidence |
|----|------|--------|----------|
| BUG-016 | Round-14 time-expiry does not kill onboard characters | Confirmed | `endGame()` at `engine.js:1997-2027` only processes escaped/hibernated; alive onboard characters never die. |
| BUG-017 | Objective/mission coverage incomplete | Confirmed | `checkObjective()` implements 7 of 15 objectives; `checkMissionTask()` implements 3 of 8 tasks. |
| BUG-018 | Serious Wounds: no health reduction or ongoing effects | Confirmed | `engine.js:1797-1803` stores wound IDs only; `data.js:230-257` defines restrictions and ongoing effects that are never enforced. |
| BUG-019 | Secure/Shelter: noise-placement path bypasses prevention | Partial | Secure works for most attack paths. `makeNoiseRoll()` at `engine.js:1143-1153` calls `resolveIntruderAttack` without Secure/Shelter check. Shelter `alwaysSecured` (`data.js:99`) has no engine reference. |
| BUG-020 | Fire kills non-Larva Intruders | Confirmed | `engine.js:506-523` kills Adults at 1 Fire hit, Drones at 2. Rulebook: Fire cannot kill any Intruder except Larva. |
| BUG-021 | Drone Room health uses Corridor rules | Confirmed | `actionShoot` at `engine.js:1301-1306` and `actionMelee` at `1375-1380` require 2 Drone hits regardless of location. Rulebook: Drone resilience applies only in corridors. |
| BUG-022 | Queen bag token placed at undiscovered Nest room | Partial | Hidden-Nest event handling works for ev19/ev20. But `resolveIntruderToken()` at `engine.js:1191-1200` sets queen.location to room `nest` even while undiscovered. |
| BUG-023 | Action deck is a placeholder that reuses Basic Action names | Confirmed | `createActionDeck()` in `engine.js` builds 10 cards from the literal strings `move`, `shoot`, `search`, `cautiousMove`, `useRoom`, `special`. These are Basic Action identifiers, not Action card faces, so cards are indistinguishable from actions in state, log, and UI, and no card has a printed effect to resolve. Violates ACT-CARD-001. Real faces are blocked on OQ-010. |

## Summary

23 audited bugs: 11 fixed, 2 partial, 10 confirmed.

Recommended repair order (from QA audit, still valid):
1. Objective choice timing and 3/2/2/1 rewards (BUG-003)
2. All 20 Event main effects and per-card movement (BUG-004, BUG-014)
3. Movement Noise on all exploration (BUG-005)
4. Exploration-card additional corridors (BUG-006)
5. Search card choice flow (BUG-007)
6. Deferred decisions: Melee prevention and Search picks (BUG-009, BUG-007)
7. Endgame deaths + objective/mission coverage (BUG-016, BUG-017)
8. Serious Wounds enforcement (BUG-018)
9. Secure/Shelter noise path + Shelter permanence (BUG-019)
10. Fire vs Intruders (BUG-020)
11. Drone room-vs-corridor health (BUG-021)
12. Queen bag token Nest handling (BUG-022)
13. Exploration log fix (BUG-015)