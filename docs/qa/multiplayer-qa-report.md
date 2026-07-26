# QA Report - Multiplayer Testing

## Test Method
Two separate Playwright Chromium browser instances on the same machine.
Browser 1 hosts, Browser 2 joins via game code. Both connect through PeerJS WebRTC.

## Test Results

### Test 1: Lobby + Join (PASS)
- Host creates game, gets 6-character code
- Client enters code, joins successfully
- Host lobby updates to show both players
- Client sees "Joined game as Player 2"

### Test 2: Game Start + State Sync (PASS)
- Host clicks Start Game
- Client auto-switches to game screen
- Both browsers show identical state: Round 1/14, playerPhase, HostPlayer's turn, 2 actions
- Both see player boards with correct health, oxygen, card counts

### Test 3: Host Action (PASS)
- Host clicks Search
- Host finds item, backpack updates
- Client receives state update, sees host's card count decrease
- Client does NOT see what item host found (privacy working)

### Test 4: Turn Passing (PASS)
- Host passes
- Both browsers show turn switched to ClientPlayer
- Client's action bar becomes enabled, host's becomes disabled

### Test 5: Client Action (PASS)
- Client clicks Search
- Client finds item (Incendiary Rounds)
- Both browsers see updated state
- Client's hand count decreases (card spent for action)

### Test 6: Round Transition (PASS)
- Client passes
- Both browsers show: Intruder Phase → Event Phase (Short Circuit) → Cleanup → Round 2
- Game logs are identical on both browsers
- Starting player rotated correctly

### Test 7: Privacy (PASS)
- Client sees own objectives and hand cards
- Client does NOT see host's objectives, hand cards, backpack contents
- All deck contents hidden (event, intruder attack, item decks, intruder bag)
- Anti-aircraft tokens hidden
- Robot card hidden until revealed

### Test 8: Disconnection (PASS - simulated)
- Client disconnects
- Host marks player as disconnected
- Game skips disconnected player in turn order
- Starting player rotation skips disconnected players

## Bugs Found and Fixed

1. **Lobby join rejected "Game is full"** — all player slots pre-filled with placeholder names
   - Fix: only create host player at setup, reserve empty slots for joiners

2. **Host lobby not showing joined players** — host never received its own lobbyState broadcast
   - Fix: call updateLobbyPlayers locally on join

3. **Client stuck on lobby after game start** — NemesisNetwork.state was never set for clients
   - Fix: store received state in onStateUpdate handler

4. **Game freezes on disconnect** — startPlayerTurn didn't check connected status
   - Fix: add !p.connected to all turn-skip conditions

5. **Privacy: full state exposed to all clients** — every player could see everyone's objectives, hand, etc.
   - Fix: serializeStateForPlayer() sanitizes state per-client

6. **Starting player rotation lands on disconnected players** — cleanupPhase only checked alive
   - Fix: also check connected status