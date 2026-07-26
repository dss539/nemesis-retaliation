# Full-Game Rules and FAQ Audit

## Scope and evidence

This audit compares the successful four-player QA trace in `full-game-action-log.json` / `full-game-action-log.md` with:

- `docs/rulebooks/rulebook_text.txt`
- `docs/rulebooks/faq_text.txt` (official FAQ v1.2, 2026-06-08)
- the engine branches exercised by the trace

The completed run contained 60 recorded player actions, 14 complete rounds, 61 four-browser synchronization checks, and 61 graph/topology checks. It ended at the real game-over state with all four characters dead and no winners.

“Observed” means the completed trace directly demonstrates the behavior. “Latent” means the comparison found a reachable engine branch that the particular random run did not execute.

## Showstopper found and fixed

### Hidden Nest event created an off-map Intruder — fixed and rerun

The first full-game attempt reached action 40 before `Nest Defense` placed a Drone at room ID `nest` even though the Nest had not been discovered and did not exist in `state.rooms`. That violated the map/entity invariant and terminated the run.

Fix: hidden-Nest Drones and the Queen are now reserved while the Nest is undiscovered and materialized when exploration reveals it. The focused regression `docs/qa/nest_event_regression.js` passed, JavaScript syntax passed, and the full game was restarted from a fresh lobby. The successful rerun had no invalid entity locations.

This is an adaptation requirement: the physical game has a persistent hidden Nest space, while this digital map assigns room identity only when exploration fills a slot.

## Rules-faithful behavior observed

1. Turn and phase structure passed. Players received two Actions per Turn; Turns repeated in clockwise order until everyone Passed; then Intruder, Event, and Cleanup phases occurred in order. Rulebook lines 2854–2962 and 2987–2994.

2. Pass correctly ended a player’s participation for the rest of the round. Rulebook lines 3180–3186.

3. Oxygen loss and Fire damage are resolved at the end of a player Turn by the engine. Rulebook lines 2929–2934. The successful random trace did not produce a player-ending Turn in Fire, so Fire damage was not directly exercised.

4. Intruders in a shared Room attacked the first eligible Character and moved to the next after that Character died. This occurred during action 24 when Alpha died and remaining attacks transferred to Delta. Rulebook lines 3313–3323.

5. Melee gained Contamination, dealt a Hit, rolled, and caused retaliation when the Intruder survived. This was exercised 11 times. Rulebook lines 5628–5665.

6. Cautious exploration placed Secure tokens. Rulebook exploration example lines 4734–4760.

7. The game completed 14 rounds and entered Game Over when attempting to advance beyond the final round. Rulebook lines 794–796 and 3404–3407.

8. FAQ door scope is implemented correctly: a `closeDoors` entrance effect closes only corridors touching the newly discovered Room. FAQ lines 30–40.

## Deviations directly observed in the completed trace

### High — Action costs are flattened to one card

Rule: Move, Secure, Shoot, Burst, Melee, Item, Robot, Trade, and Tactical Gear cost one Action card; Use Room and Move Cautiously cost two. Rulebook lines 2870–2900 and 2921–2923.

Observed: every non-Pass action discarded exactly one card. Actions 6 and 14 (`cautiousMove`) and actions 8 and 55 (`useRoom`) each paid one card instead of two. The run therefore underpaid four Action cards.

Engine cause: `performAction` removes one card for every non-Pass action before dispatch and has no per-action cost table.

### High — Cleanup draws one card instead of refilling to five

Rule: each player draws until they have five Action cards. Rulebook lines 3398–3403.

Observed: after round 1, players with zero cards received only one. Action 24’s resulting state changed Bravo and Charlie from zero to one; thereafter most Turns consisted of one paid action plus Pass. This materially reduced the game’s tactical activity and dominated the 14-round trace.

Engine cause: `cleanupPhase` calls `drawActionCard` once per active player.

### High — Objective choice timing and card rewards are missing

Rule: a player chooses once during their Turn, before or after an Action, and the first through fourth choices draw 3/2/2/1 Action cards. Rulebook lines 3076–3094.

Observed: the application required all four objectives before the first Turn. Action 1 began with all players on exactly five cards, proving no 3/2/2/1 choice reward was applied.

Engine cause: objective selection directly assigns `chosenObjective`; it has no choice-track progression or Action-card draw.

### High — Several resolved Event cards performed no main effect

Rule: resolve movement, main effect, secondary effect, then discard. Impossible individual sentences are ignored, not the entire card. Rulebook lines 3269–3293.

Observed examples:

- `Alarm` resolved in rounds 1 and 7 without required Noise rolls for Characters in Computer Rooms.
- `Breeding` resolved in rounds 3 and 9 without adding Larvae to eligible occupied Rooms.
- `System Failure` resolved in round 4 without malfunctioning eligible Heavy Items.
- `Scent of Prey` resolved in rounds 5 and 11 without its adjacent-Intruder/noise effects.
- `Malfunction` resolved in round 14 without placing Malfunctions in Computer Rooms.

Engine cause: `resolveEvent` has explicit main-effect branches for only a subset of the 20 Event IDs; the default branch does nothing after generic movement.

### High — Exploration does not always resolve the mandatory Movement Noise roll

Rule: make a Noise roll after every Movement, including movement to a Room containing Characters or Intruders, unless a specific effect says otherwise. Rulebook lines 4702–4705.

Observed: exploration moves whose Exploration card entrance was `none` or `closeDoors` produced no Noise roll. Only cards whose entrance itself was `noiseRoll` generated Noise.

Engine cause: discovered-room movement always calls `makeNoiseRoll`; exploration calls it only when the card’s entrance field is `noiseRoll`.

### High — Exploration cards’ additional corridors are ignored

Rule: exploration places all indicated Corridors that lead to valid unexplored destinations, omitting only those that would lead to an already existing Room. Rulebook lines 4721–4733 and 4753–4760.

Observed: the final map had 13 Rooms and exactly 12 Corridors—a tree containing only the incoming edge for each discovered Room. The `corridors` layout on every Exploration card was ignored.

Engine cause: `explorationSequence` creates only the edge traversed by the Character.

This differs from the intentional fixed 7×5 octagonal presentation. Fixed slots and eight-direction targeting can remain while still honoring each card’s legal outgoing edges.

### High — Search is a generic basic action rather than the Search Action card

Rule: Search is performed through the Search Action card. It draws one Item for each Item icon, lets the player choose one, and puts unchosen cards on the bottoms of their decks without revealing them. Rulebook lines 4849–4860. Search is absent from the basic-action list at lines 2870–2900.

Observed: 12 generic `search` actions paid one arbitrary Action card, automatically kept the first draw, and made no player choice.

Engine cause: `actionSearch` is exposed as a generic Character action and auto-selects `drawnItems[0]`.

### High — Item decks contain nonexistent IDs

Observed: actions 3 and 11 reported `red_gen_24` and `red_gen_22`; action 49 reported `yellow_gen_29`. These IDs do not exist in `GAME_DATA.ITEMS`, so `addItemToPlayer` silently discarded the reward while still returning success.

Engine cause: each Item deck is generated as `type_gen_0` through `type_gen_29`, but the generated item definitions contain only red 0–19, yellow 0–24, and green 0–26; named items use unrelated IDs and are never put in the decks.

### Medium — Melee retaliation cannot be prevented

Rule: after a surviving Intruder responds, the player may place a Malfunction on a Weapon to prevent that Attack. Rulebook lines 5661–5667.

Observed: all surviving targets retaliated immediately after the 11 Melee actions; the engine never offered the prevention choice.

Engine cause: `actionMelee` contains a “for now, resolve attack” branch.

### Medium — Passing automatically discards all Contamination cards

Rule: on Pass, a player may discard any number of Action and Contamination cards. Rulebook lines 3180–3185.

Observed: Pass accepted no discard selection. The engine automatically moved all Contamination cards out of hand and offered no Action-card discard choice.

### Low — Exploration movement logs the synthetic target instead of the discovered Room

Observed: action 2 discovered `gunneryRoom` but logged “Alpha moves to explore_trace_002.” State and rendering used the correct Room; the action log/notification used the temporary target ID.

This is not a board-rule deviation but makes diagnostics and player history misleading.

## Latent deviations confirmed in reachable engine branches

These were not determinative in the successful random run and should receive focused scenarios before repair.

1. Round-14 survival: `endGame` does not kill Characters still inside the Facility when time expires. Rulebook lines 794–796 require all non-Escaped, non-Hibernated Characters to die.

2. Objective coverage: `checkObjective` implements only a subset of objective names; `checkMissionTask` implements only three task families. Valid survivors can therefore fail completed official objectives.

3. Serious Wounds: wound cards are stored, but their restrictions and ongoing effects are generally not enforced against action validation or Turn processing.

4. Secure tokens and FAQ: FAQ lines 70–72 say Secure prevents attacks when an Intruder is placed in the Room. The engine consumes Secure only during the Intruder Attack phase; surprise attacks from Noise placement bypass it. FAQ lines 96–105 also define Shelter as permanently secured, while the engine has no permanent Shelter attack-prevention branch.

5. Event movement: the engine moves all corridor Intruders and then all Room Intruders for every Event rather than selecting types/orientations from that Event card as required by rulebook lines 3279–3287.

6. Fire versus Intruders: rulebook lines 3305–3312 state Fire’s unrolled Hit cannot kill an Intruder except a Larva. The engine kills an Adult at one Fire Hit and a Drone at two.

7. Drone Room health: rulebook lines 5676–5680 say Drones are harder to kill only in Corridors and use Adult resolution in Rooms. The engine’s Melee branch requires two accumulated Hits for a Drone regardless of location.

8. Failed actions: the engine discards the payment card before action validation. A rejected action can consume a card even though the effect was illegal or impossible, conflicting with the “must be able to resolve entirely” rule at lines 3187–3197.

9. Tactical Gear: `actionUseTacticalGear` does not verify ownership or remove the chosen token, allowing repeated use of nonexistent or already-spent Gear.

10. Trade: the engine reports success but transfers no Item. FAQ lines 141–143 clarify that a traded Item is actually gained and can be used immediately.

## FAQ coverage status

Applicable and passing:

- Exploration `closeDoors` affects only doors touching the new Room (FAQ 30–40).
- Closed doors block ordinary movement.

Applicable and deviating:

- Secure-token attack prevention and Shelter permanence (FAQ 70–72 and 96–105), described above.

Not exercised by this random full game:

- Queen shooting/Health-card details (FAQ 15–20).
- Autodestruction at endgame (FAQ 26–28).
- Noise-marker resolution in unexplored corridors (FAQ 42–46).
- Effects through closed doors (FAQ 52–57).
- Action-card reshuffling nuance (FAQ 59–65).
- Lander targeting (FAQ 67–68).
- Weapon, Ammo, Tactical Gear, healing/interplay, and Trade edge cases (FAQ 114–165).

## Recommended repair order

1. Implement per-action costs and refill hands to five.
2. Restore objective timing and 3/2/2/1 choice rewards.
3. Implement all Event main/secondary effects and event-specific movement.
4. Correct movement Noise and Exploration-card edge creation.
5. Rebuild Item decks from actual `GAME_DATA.ITEMS` IDs and implement Search-card choice flow.
6. Add deferred decisions for Melee prevention, Pass discards, Search picks, and other player choices.
7. Complete endgame/objective evaluation.
8. Add focused FAQ scenarios for Secure/Shelter, Queen combat, autodestruction, closed doors, Lander, and Trade.
