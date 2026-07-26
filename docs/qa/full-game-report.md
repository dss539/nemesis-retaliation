# Full Game QA Report

## Test Method
Single Playwright headless Chromium, driving the engine directly via `page.evaluate()`.
2-player game (host + unjoined bot slot), 14 rounds max, cycling through all action types.

## Game Result
- **Rounds played:** 13 (game ended before round 14 — all players dead)
- **Winners:** Both players declared winners (BUG — see below)
- **Console errors:** None

## Bugs Found

### BUG 1: Player 2 starts DEAD (CRITICAL)
Player 2 (the unjoined bot slot) shows `alive: false` from round 1 and is never playable.
The game only has one active player for the entire run.

**Root cause:** In `createGame()`, unjoined player slots are created with `alive: false`.
When the host starts the game with `startRound()`, the engine never activates unjoined players.
The `startPlayerTurn()` check `!player.alive` skips them immediately.

**Impact:** Solo play is broken. Any game with unfilled slots has dead players from the start.
The "game over" check `activePlayers.length === 0` can trigger prematurely.

**Fix:** Either (a) only create players who actually join, or (b) set `alive: true` for all
slots and let the game proceed with the host controlling unfilled slots as AI/passing.

### BUG 2: Both players declared winners despite being dead (CRITICAL)
Final state: `winners: [0, 1]` but both players have `alive: false`.

**Root cause:** In `endGame()`, the objective check runs on all players regardless of alive
status. The `checkObjective()` function for "Official Order" checks `checkMissionTask()`
which returns true if the mission task happens to be fulfilled by game state — even if
the player is dead.

**Fix:** `endGame()` should only check objectives for players who are alive OR have
escaped/hibernated. Dead players should never win.

### BUG 3: No intruders appeared all game (MAJOR)
11 rounds played, 0 intruders on the board at any point. The intruder bag has 46+ tokens
but none were ever drawn or placed.

**Root cause:** Intruders only appear via noise rolls and event card effects. The noise roll
function `makeNoiseRoll()` draws from the bag only on a Hazard result (roll > 4 on d10).
The event cards call `moveCorridorIntruders()` and `moveRoomIntruders()` but these only
move existing intruders — they don't place new ones. Event cards like "Infestation" and
"Nest Defense" that should place intruders don't have implementation for the intruder
placement part.

**Impact:** The game is not threatening. No combat, no intruder attacks, no contamination.
The core survival horror mechanic is missing.

**Fix:** Event cards need to actually draw from the intruder bag and place intruders.
Specifically: "Infestation" (ev12) should draw 2 tokens, "Intruder Surge" (ev14) should
draw 3 tokens, "Nest Defense" (ev19) should add a Drone to the Nest Room.

### BUG 4: Oxygen depletion doesn't trigger suffocation (MINOR)
Host oxygen reached 0 at round 12 but didn't die until round 13. The `suffocating` flag
was never set.

**Root cause:** In `endPlayerTurn()`, the oxygen check sets `suffocating = true` when oxygen
hits 0, but the check for suffocation death only happens on the NEXT turn's oxygen loss.
However, the player's oxygen was 0 for multiple rounds without dying.

**Fix:** When `oxygen === 0` and `suffocating === true`, the player should die on the next
oxygen loss. Need to verify the suffocation logic fires correctly.

### BUG 5: Queen appears but never moves or attacks (MINOR)
Queen awakened at round 4 (Event: Queen Awakening) and `inPlay: true` for the rest of the
game, but never appeared on the board, never moved, never attacked.

**Root cause:** `activateQueen()` in the engine adds the Queen to `state.intruders` only if
she's not already in the intruders array. But the Queen's location is set to
`{type: 'room', id: 'nest'}` — the Nest room may not be discovered/placed on the board.
The Queen activation logic checks for characters in the same room, but since the Nest
isn't on the board, she has no valid targets.

**Fix:** Ensure the Queen is placed in the Nest Room when awakened, and that the Nest Room
exists on the board (it's a Section C room that should be placed during exploration).

### BUG 6: Only 4 rooms discovered in 13 rounds (MINOR)
The game ran 13 rounds but only discovered 4 rooms and 4 corridors. The host explored
multiple times but many exploration attempts failed silently.

**Root cause:** The exploration sequence depends on the target room ID starting with
`explore_`, but the engine's `actionMove()` only allows exploration if no corridor exists
between rooms. After the first exploration, subsequent moves to `explore_*` targets fail
because the engine checks for corridor adjacency even for exploration moves.

**Fix:** The exploration logic needs to properly handle moves to undiscovered positions
without requiring existing corridors.

## What Worked
- Game creation and setup
- Objective selection
- Round structure (Player Phase → Intruder Phase → Event Phase → Cleanup)
- 20 different event cards resolved correctly
- Oxygen depletion (host went from 7 → 0 over the game)
- Room exploration (4 rooms discovered: shelter, gunneryRoom, airlock, landingZone)
- Item search (host found items)
- Item use
- Turn passing and starting player rotation
- Game over detection (all players dead/inactive)
- No JavaScript console errors
- No crashes or hangs

## Summary
The game engine runs through all 14 rounds without crashing, but has critical gameplay
bugs: no intruders appear (the core threat is missing), dead players can win, and
exploration is limited. These need to be fixed before the game is playable.