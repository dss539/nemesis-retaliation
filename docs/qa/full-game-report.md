# Full-Game Four-Browser QA Report

## Outcome

The full-game QA passed after one showstopper fix and a complete fresh-lobby rerun.

- Players: 4 independent Chromium processes (`Alpha`, `Bravo`, `Charlie`, `Delta`)
- Networking: real PeerJS host/client lobby; host-authoritative engine
- Completion: 14 full rounds, Game Over at round counter 15
- Recorded player actions: 60
- Successful actions: 60
- Rejected actions: 0
- Four-browser synchronization checks: 61/61
- Board/entity topology checks: 61/61
- Browser console errors: 0
- Page exceptions: 0
- Final result: all four Characters dead; no winners

## Action coverage

- Search: 12
- Move/explore: 11
- Cautious Move/explore: 2
- Use Room: 2
- Melee: 11
- Pass: 22

The full sequential action/result history, including action parameters, before/after summaries, and all automatic engine-log effects caused by each action, is in:

- `docs/qa/full-game-action-log.md`
- `docs/qa/full-game-action-log.json`

## Showstopper and retry

The first run stopped after action 40 when the `Nest Defense` Event created a Drone at the nonexistent `nest` room before the Nest had been discovered.

The engine now reserves hidden-Nest Drones and the Queen while the Nest is undiscovered, then materializes them when exploration reveals the Nest. The focused hidden-Nest regression passed. The full game was then restarted from a new four-player lobby and completed without further showstoppers.

## Representative screenshots

- `docs/qa/full-game-initial.png` — initial four-player state
- `docs/qa/full-game-crisis.png` — first multi-Intruder crisis
- `docs/qa/full-game-midgame.png` — expanded map and ongoing casualties
- `docs/qa/full-game-final.png` — host’s final Game Over state
- `docs/qa/full-game-client-final.png` — independent client’s synchronized final state

## Final state

- Rooms: 13
- Corridors: 12
- Intruders: 10 (6 Drones, 4 Adults)
- Queen: awakened but pending in the still-undiscovered Nest
- Nest: 5 Eggs, not destroyed
- Life Support: A active, B inactive, C active
- Autodestruction: inactive
- Alpha: dead in Gunnery Room
- Bravo: dead in Life Support Control A
- Charlie: dead in Sprinklers Control
- Delta: dead in Gunnery Room

## Rules audit

The detailed comparison against the official rulebook extraction and FAQ v1.2 is in:

- `docs/qa/full-game-rules-audit.md`

The round loop, phase order, Pass behavior, Intruder attack transfer, Melee core sequence, cautious Secure placement, 14-round limit, and close-door FAQ scope matched.

The largest observed deviations were:

1. Use Room and Cautious Move cost one Action card instead of two.
2. Cleanup draws one card instead of refilling to five.
3. Objective selection is forced before gameplay and omits the 3/2/2/1 card rewards.
4. Several Event cards log but do not resolve their main effects.
5. Exploration does not always make the mandatory Movement Noise roll.
6. Exploration ignores the card’s additional corridors.
7. Search is a generic action, auto-picks, and can draw nonexistent Item IDs.
8. Melee retaliation cannot be prevented with a Weapon Malfunction.
9. Pass auto-discards Contamination without a player choice.

These rules deviations were documented but not changed during this task because they are broad gameplay work rather than showstopper fixes.
