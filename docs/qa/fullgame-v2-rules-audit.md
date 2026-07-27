# Full-Game Rules Audit Report

Game: Nemesis: Retaliation Digital Edition
QA run: 4-browser full game, 15 rounds, 325 actions
Winner: Player [2]
Deviations confirmed by trace: 17/21

## Confirmed deviations (directly observed in game trace)

### D1-action-costs (CRITICAL)
**Rule:** Use Room costs 2 Action cards; Pass costs 0 (rulebook 2855-2900)
**Engine:** All non-Pass actions discard exactly 1 card (engine.js:357-365)
**Evidence:** 54 useRoom actions each consumed 1 card instead of 2. 54 pass actions correctly cost 0.

### D2-cleanup-draw (CRITICAL)
**Rule:** Cleanup refills hand to 5 cards (rulebook 3401-3403)
**Engine:** Cleanup draws exactly 1 card per player (engine.js:843-847)
**Evidence:** Hands consistently at 1-3 cards after round transitions. Sample: [{'round': 2, 'player': 'Alpha', 'hand': 1}, {'round': 2, 'player': 'Bravo', 'hand': 3}, {'round': 2, 'player': 'Delta', 'hand': 1}, {'round': 3, 'player': 'Alpha', 'hand': 1}, {'round': 3, 'player': 'Bravo', 'hand': 1}]

### D3-pass-discard (HIGH)
**Rule:** Pass may discard any number of Action and Contamination cards (rulebook 3180-3186)
**Engine:** Pass only empties contaminationInHand (engine.js:1568-1577)
**Evidence:** Action log shows pass actions but engine only discards contamination, not action cards.

### D4-exploration-model (CRITICAL)
**Rule:** Exploration moves through an existing Unexplored Corridor, places room + all shown corridors/markers (rulebook 4494-4535, 4568-4585)
**Engine:** Engine creates a single corridor to an adjacent empty grid node (engine.js:882-910, 975-1023)
**Evidence:** 106 exploration actions, each created exactly 1 corridor. No exploration card placement of additional corridors/markers.

### D5-noise-intruder-storage (CRITICAL)
**Rule:** Numbered noise result pulls largest intruder from matching corridor (rulebook 4677-4687)
**Engine:** Noise checks corridor.intruders but intruders are stored globally in state.intruders (engine.js:1068-1083)
**Evidence:** Intruders placed via resolveIntruderToken go to state.intruders with location, not corridor.intruders. Noise number rolls cannot find them.

### D6-bag-setup (CRITICAL)
**Rule:** Official bag: 1 Blank, 2 Larvae, 3 Adults + 1 Adult per Character (rulebook 2569-2575)
**Engine:** Data creates 16 Blank, 8 Drone, 12 Adult, 6 Larva, 3 Queen (data.js:151-159)
**Evidence:** Final intruder pool: {'drone': 6, 'adult': 12, 'larva': 6, 'queen': 1}. Bag had 70 tokens. Pool shows 12 adults, 6 drones, 6 larva, 1 queen remaining.

### D7-bag-development (CRITICAL)
**Rule:** Bag development draws 1 token and applies token-specific effect (rulebook 3385-3397, 3439-3467)
**Engine:** Adds fixed adults/drones by round number (engine.js:811-825)
**Evidence:** Bag grew from initial size to 70 tokens over 14 rounds via fixed schedule, not token-draw development.

### D8-event-effects (CRITICAL)
**Rule:** Events resolve printed movement icons, main effect, secondary effect (rulebook 3251-3258, 3269-3293)
**Engine:** All events run both generic movement functions regardless of printed icons; only ~9 of 20 have main-effect code (engine.js:637-706)
**Evidence:** Events seen: Counter({'=== Round 2 ===': 1, '=== Round 3 ===': 1, '=== Round 4 ===': 1, '=== Round 5 ===': 1, '=== Round 6 ===': 1, '=== Round 7 ===': 1, '=== Round 8 ===': 1, '=== Round 9 ===': 1, '=== Round 10 ===': 1, '=== Round 11 ===': 1, '=== Round 12 ===': 1, '=== Round 13 ===': 1, '=== Round 14 ===': 1}). Intruders stayed at 4-6 from round 4 onward with no movement variation.

### D9-lander-lifecycle (CRITICAL)
**Rule:** Lander lands during Time Advancement; occupants may launch at Event Phase (rulebook 3416-3431, 6063-6074)
**Engine:** No natural landing resolution; no launch/escape code (engine.js:613-618, 1815-1832)
**Evidence:** No player ever entered the Lander or escaped via Lander. Alpha and Bravo died inside the facility at round 14.

### D10-endgame-survival (CRITICAL)
**Rule:** Round-14 characters still inside are dead before victory determination (rulebook 6238-6248)
**Engine:** endGame() called without killing active characters (engine.js:851-854, 1899-1934)
**Evidence:** Charlie (hibernatorium) and Delta (commsRoom) both alive at game over (round 15) despite being inside the facility. Winner: [2] = Charlie.

### D11-contamination-eclosion (CRITICAL)
**Rule:** Contamination goes to Action discard; Infection scans hand; Eclosion draws 4 from combined deck (rulebook 5853-5871, 6079-6116)
**Engine:** Contamination stored separately; Infection lookup fails; Eclosion checks wrong type (engine.js:1695-1704, 1852-1882)
**Evidence:** Players accumulated contamination (seen in round summaries) but no infection/eclosion ever triggered. Final contam counts all 0 (discarded on pass).

### D12-objective-selection (CRITICAL)
**Rule:** Objective choice occurs between actions, awards cards by choice order (rulebook 3076-3094)
**Engine:** chosenObjective only set by test harness, not by in-game UI flow (engine.js:158-159)
**Evidence:** All players had chosenObjective set by test harness. Winner Charlie had obj=mo5 (Ulterior Motive: Mission Task must remain UNFULFILLED).

### D13-secure-tokens (HIGH)
**Rule:** Secure only prevents attack from entering, not intruder phase attacks (rulebook 4406-4413)
**Engine:** Engine consumes Secure for intruders already in room (engine.js:520-537, 758-765)
**Evidence:** Shelter (alwaysSecured) data exists but attack code doesn't consult it.

### D14-fire-kills (HIGH)
**Rule:** Fire gives 1 Hit but cannot kill anything except Larva (rulebook 3305-3312)
**Engine:** Engine kills Adults at 1 Hit and Drones at 2 during Burning (engine.js:487-501)
**Evidence:** Fire Outbreak events occurred in rounds 9 and 13 but intruder count stayed stable at 6.

### D17-hibernation-state (HIGH)
**Rule:** Hibernation requires Hibernatorium Active token, not Section B Life Support (rulebook 6148-6150, 6371-6377)
**Engine:** Engine checks sections.B.lifeSupport (engine.js:1497-1505)
**Evidence:** Charlie was in hibernatorium but never hibernated. Engine checks Section B life support instead of separate Hibernatorium Active state.

### D20-oxygen-suffocating (HIGH)
**Rule:** Suffocating granted at 0 from any source; clears on gaining oxygen or ending turn in active life support (rulebook 3693-3721)
**Engine:** Only creates Suffocating during end-turn life-support loss; never clears it (engine.js:419-435)
**Evidence:** Alpha oxygen by round: [(2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 6), (8, 5), (9, 4), (10, 3), (11, 2), (12, 1), (13, 0), (14, 0)]. Alpha reached 0 at round 13 and died at round 14. Suffocating flag never cleared.

### D21-objective-evaluation (HIGH)
**Rule:** Evaluate all 22 objectives and 8 mission tasks from actual conditions (rulebook 6277-6293, 6330-6335)
**Engine:** Only subset of objectives checked; only 3 of 8 mission tasks checked (engine.js:1939-1978)
**Evidence:** Winner Charlie had mo5 (Ulterior Motive: Mission Task must remain UNFULFILLED). Only 3 mission tasks are evaluated in code.

## Unexercised deviations (identified from code review, not triggered in this game)

### D15-queen-combat (HIGH)
**Rule:** Queen shooting uses Adult resolution but resolves Queen Health, not model removal (faq 15-20)
**Engine:** Shoot adds hits and calls killIntruder() for Queen (engine.js:1216-1237)
**Note:** Not exercised in this game trace; identified from code review.

### D16-drone-health (HIGH)
**Rule:** Drones use Adult health in rooms; Larvae always die to 1 Hit (rulebook 5672-5680)
**Engine:** Shoot/Melee require 2 Hits for Drone in room (engine.js:1231-1237, 1305-1310)
**Note:** Not exercised in this game trace; identified from code review.

### D18-lander-noise (HIGH)
**Rule:** Boarding Lander requires Noise roll; fails if intruder remains (rulebook 6153-6167)
**Engine:** Boards immediately when landed (engine.js:1430-1435)
**Note:** Not exercised; identified from code review.

### D19-autodestruction-precedence (HIGH)
**Rule:** Pending autodestruction triggers before endgame sequence (faq 26-28)
**Engine:** Cleanup calls endGame() before checking autodestruction (engine.js:851-860)
**Note:** Not exercised; identified from code review.
