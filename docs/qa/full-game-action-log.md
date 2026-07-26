# Full-game QA action log

Run status: **passed**
Seed: `browser-native (realized outcomes recorded in full trace)`
Players: Alpha, Bravo, Charlie, Delta
Recorded actions: 60
Synchronization checks: 61
Topology checks: 61

## Setup

- Host created deterministic four-player lobby 65JBT2.
- Bravo joined as authoritative player 1.
- Charlie joined as authoritative player 2.
- Delta joined as authoritative player 3.
- Alpha chose mo7.
- Bravo chose mo5.
- Charlie chose mo4.
- Delta chose mo1.

## Every action and result

| # | Round | Actor | Action | Result | State result | Engine log delta |
|---:|---:|---|---|---|---|---|
| 1 | 1 | Alpha | search — first search by player in landingZone | success | R1 playerPhase; next P0; actions=1; rooms=1; corridors=0; intruders=0; gameOver=False | Alpha searches and finds Combat Shotgun |
| 2 | 1 | Alpha | move — explore legal SE slot (1,1) | success | R1 playerPhase; next P1; actions=2; rooms=2; corridors=1; intruders=3; gameOver=False | drone attacks Alpha: Lose 1 Health. Gain 1 Contamination.; drone(s) appear (3); Alpha discovers gunneryRoom; Alpha moves to explore_trace_002; Bravo's turn begins |
| 3 | 1 | Bravo | search — first search by player in landingZone | success | R1 playerPhase; next P1; actions=1; rooms=2; corridors=1; intruders=3; gameOver=False | Bravo searches and finds red_gen_24 |
| 4 | 1 | Bravo | move — explore legal E slot (1,0) | success | R1 playerPhase; next P2; actions=2; rooms=3; corridors=2; intruders=3; gameOver=False | Bravo discovers laboratory; Bravo moves to explore_trace_004; Charlie's turn begins |
| 5 | 1 | Charlie | search — first search by player in landingZone | success | R1 playerPhase; next P2; actions=1; rooms=3; corridors=2; intruders=3; gameOver=False | Charlie searches and finds Armor Piercing Rounds |
| 6 | 1 | Charlie | cautiousMove — explore legal S slot (0,1) | success | R1 playerPhase; next P3; actions=2; rooms=4; corridors=3; intruders=3; gameOver=False | Charlie discovers drillingRoom; Charlie moves to explore_trace_006; Delta's turn begins |
| 7 | 1 | Delta | search — first search by player in landingZone | success | R1 playerPhase; next P3; actions=1; rooms=4; corridors=3; intruders=3; gameOver=False | Delta searches and finds Heavy Machine Gun |
| 8 | 1 | Delta | useRoom — exercise landingZone room effect | success | R1 playerPhase; next P0; actions=2; rooms=4; corridors=3; intruders=3; gameOver=False | Delta uses Landing Zone; Alpha's turn begins |
| 9 | 1 | Alpha | melee — combat: melee drone in room | success | R1 playerPhase; next P0; actions=1; rooms=4; corridors=3; intruders=3; gameOver=False | Alpha melee attacks! Roll: 6; drone attacks Alpha: Lose 1 Health. |
| 10 | 1 | Alpha | melee — combat: melee drone in room | success | R1 playerPhase; next P1; actions=2; rooms=4; corridors=3; intruders=3; gameOver=False | Alpha melee attacks! Roll: 3; drone attacks Alpha: Heavily Injured: die. Otherwise lose 3 Health.; Bravo's turn begins |
| 11 | 1 | Bravo | search — first search by player in laboratory | success | R1 playerPhase; next P1; actions=1; rooms=4; corridors=3; intruders=3; gameOver=False | Bravo searches and finds red_gen_22 |
| 12 | 1 | Bravo | move — explore legal SE slot (2,1) | success | R1 playerPhase; next P2; actions=2; rooms=5; corridors=4; intruders=3; gameOver=False | Bravo discovers engineRoom; Bravo moves to explore_trace_012; Charlie's turn begins |
| 13 | 1 | Charlie | search — first search by player in drillingRoom | success | R1 playerPhase; next P2; actions=1; rooms=5; corridors=4; intruders=3; gameOver=False | Charlie searches and finds Taser |
| 14 | 1 | Charlie | cautiousMove — explore legal S slot (0,2) | success | R1 playerPhase; next P3; actions=2; rooms=6; corridors=5; intruders=3; gameOver=False | Charlie discovers surgeryRoom; Charlie moves to explore_trace_014; Delta's turn begins |
| 15 | 1 | Delta | move — move through open graph edge to gunneryRoom | success | R1 playerPhase; next P3; actions=1; rooms=6; corridors=5; intruders=4; gameOver=False | drone attacks Alpha: Lose 1 Health. Gain 1 Contamination.; drone(s) appear; Delta moves to gunneryRoom |
| 16 | 1 | Delta | melee — combat: melee drone in room | success | R1 playerPhase; next P0; actions=2; rooms=6; corridors=5; intruders=4; gameOver=False | Delta melee attacks! Roll: 4; drone attacks Delta: Gain 1 Serious Wound and 1 Contamination.; Delta gains a Serious Wound; Alpha's turn begins |
| 17 | 1 | Alpha | melee — combat: melee drone in room | success | R1 playerPhase; next P0; actions=1; rooms=6; corridors=5; intruders=4; gameOver=False | Alpha melee attacks! Roll: 6; drone attacks Alpha: Lose 2 Health. Gain 1 Contamination. |
| 18 | 1 | Alpha | pass — no action cards | success | R1 playerPhase; next P1; actions=2; rooms=6; corridors=5; intruders=4; gameOver=False | Alpha passes; Bravo's turn begins |
| 19 | 1 | Bravo | search — first search by player in engineRoom | success | R1 playerPhase; next P1; actions=1; rooms=6; corridors=5; intruders=4; gameOver=False | Bravo searches and finds Power Drill |
| 20 | 1 | Bravo | pass — no action cards | success | R1 playerPhase; next P2; actions=2; rooms=6; corridors=5; intruders=4; gameOver=False | Bravo passes; Charlie's turn begins |
| 21 | 1 | Charlie | search — first search by player in surgeryRoom | success | R1 playerPhase; next P2; actions=1; rooms=6; corridors=5; intruders=4; gameOver=False | Charlie searches and finds First Aid Kit |
| 22 | 1 | Charlie | pass — no action cards | success | R1 playerPhase; next P3; actions=2; rooms=6; corridors=5; intruders=4; gameOver=False | Charlie passes; Delta's turn begins |
| 23 | 1 | Delta | melee — combat: melee drone in room | success | R1 playerPhase; next P3; actions=1; rooms=6; corridors=5; intruders=4; gameOver=False | Delta melee attacks! Roll: 1; drone attacks Delta: Lose 2 Health. |
| 24 | 1 | Delta | pass — no action cards | success | R2 playerPhase; next P1; actions=2; rooms=6; corridors=5; intruders=4; gameOver=False | Delta passes; -- Intruder Phase --; drone attacks Alpha: Lose 2 Health.; Alpha dies (intruder); drone attacks Delta: Lose 2 Health.; drone attacks Delta: Lose 1 Health. Gain 1 Contamination.; drone attacks Delta: Lose 1 Health.; -- Event Phase --; Event: Alarm; -- Cleanup Phase --; === Round 2 ===; Bravo's turn begins |
| 25 | 2 | Bravo | move — explore legal SW slot (1,2) | success | R2 playerPhase; next P1; actions=1; rooms=7; corridors=6; intruders=4; gameOver=False | Bravo discovers shelter; Bravo moves to explore_trace_025 |
| 26 | 2 | Bravo | pass — no action cards | success | R2 playerPhase; next P2; actions=2; rooms=7; corridors=6; intruders=4; gameOver=False | Bravo passes; Charlie's turn begins |
| 27 | 2 | Charlie | move — explore legal SE slot (1,3) | success | R2 playerPhase; next P2; actions=1; rooms=8; corridors=7; intruders=5; gameOver=False | adult attacks Charlie: Gain 1 Contamination. If no Larva, place 1 Larva.; Charlie is infected with a Larva!; adult(s) appear; Charlie discovers storageRoom; Charlie moves to explore_trace_027 |
| 28 | 2 | Charlie | pass — no action cards | success | R2 playerPhase; next P3; actions=2; rooms=8; corridors=7; intruders=5; gameOver=False | Charlie passes; Delta's turn begins |
| 29 | 2 | Delta | melee — combat: melee drone in room | success | R2 playerPhase; next P3; actions=1; rooms=8; corridors=7; intruders=5; gameOver=False | Delta melee attacks! Roll: 6; drone attacks Delta: Lose 1 Health. |
| 30 | 2 | Delta | pass — no action cards | success | R3 playerPhase; next P2; actions=2; rooms=8; corridors=7; intruders=5; gameOver=False | Delta passes; -- Intruder Phase --; drone attacks Delta: Lose 1 Health. Gain 1 Contamination.; drone attacks Delta: Heavily Injured: die. Otherwise gain 1 Serious Wound.; Delta dies (intruder); adult attacks Charlie: Lose 2 Health. Gain 1 Contamination.; -- Event Phase --; Event: Queen Awakening; The Queen awakens in the undiscovered Nest; -- Cleanup Phase --; === Round 3 ===; Charlie's turn begins |
| 31 | 3 | Charlie | melee — combat: melee adult in room | success | R3 playerPhase; next P2; actions=1; rooms=8; corridors=7; intruders=4; gameOver=False | Charlie melee attacks! Roll: 8; adult killed! |
| 32 | 3 | Charlie | pass — no action cards | success | R3 playerPhase; next P1; actions=2; rooms=8; corridors=7; intruders=4; gameOver=False | Charlie passes; Bravo's turn begins |
| 33 | 3 | Bravo | move — explore legal SE slot (2,3) | success | R3 playerPhase; next P1; actions=1; rooms=9; corridors=8; intruders=5; gameOver=False | adult attacks Bravo: Lose 2 Health.; adult(s) appear; Bravo discovers lifeSupportControlA; Bravo moves to explore_trace_033 |
| 34 | 3 | Bravo | pass — no action cards | success | R4 playerPhase; next P1; actions=2; rooms=9; corridors=8; intruders=5; gameOver=False | Bravo passes; -- Intruder Phase --; adult attacks Bravo: Lose 1 Health.; -- Event Phase --; Event: Breeding; -- Cleanup Phase --; === Round 4 ===; Bravo's turn begins |
| 35 | 4 | Bravo | melee — combat: melee adult in room | success | R4 playerPhase; next P1; actions=1; rooms=9; corridors=8; intruders=5; gameOver=False | Bravo melee attacks! Roll: 1; adult attacks Bravo: Heavily Injured: die. Otherwise gain 1 Serious Wound.; Bravo gains a Serious Wound |
| 36 | 4 | Bravo | pass — no action cards | success | R4 playerPhase; next P2; actions=2; rooms=9; corridors=8; intruders=5; gameOver=False | Bravo passes; Charlie's turn begins |
| 37 | 4 | Charlie | search — first search by player in storageRoom | success | R4 playerPhase; next P2; actions=1; rooms=9; corridors=8; intruders=5; gameOver=False | Charlie searches and finds Flashbang |
| 38 | 4 | Charlie | pass — no action cards | success | R5 playerPhase; next P2; actions=2; rooms=9; corridors=8; intruders=5; gameOver=False | Charlie passes; -- Intruder Phase --; adult attacks Bravo: Lose 2 Health.; -- Event Phase --; Event: System Failure; -- Cleanup Phase --; === Round 5 ===; Charlie's turn begins |
| 39 | 5 | Charlie | move — explore legal W slot (0,3) | success | R5 playerPhase; next P2; actions=1; rooms=10; corridors=9; intruders=5; gameOver=False | Charlie discovers airlock; Charlie moves to explore_trace_039 |
| 40 | 5 | Charlie | pass — no action cards | success | R5 playerPhase; next P1; actions=2; rooms=10; corridors=9; intruders=5; gameOver=False | Charlie passes; Bravo's turn begins |
| 41 | 5 | Bravo | melee — combat: melee adult in room | success | R5 playerPhase; next P1; actions=1; rooms=10; corridors=9; intruders=5; gameOver=False | Bravo melee attacks! Roll: 3; adult attacks Bravo: Lose 2 Health. |
| 42 | 5 | Bravo | pass — no action cards | success | R6 playerPhase; next P2; actions=2; rooms=10; corridors=9; intruders=5; gameOver=False | Bravo passes; -- Intruder Phase --; adult attacks Bravo: Heavily Injured: die. Otherwise lose 3 Health.; Bravo dies (intruder); -- Event Phase --; Event: Scent of Prey; -- Cleanup Phase --; === Round 6 ===; Charlie's turn begins |
| 43 | 6 | Charlie | search — first search by player in airlock | success | R6 playerPhase; next P2; actions=1; rooms=10; corridors=9; intruders=5; gameOver=False | Charlie searches and finds Stun Baton |
| 44 | 6 | Charlie | pass — no action cards | success | R7 playerPhase; next P2; actions=2; rooms=10; corridors=9; intruders=5; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Reactor Overheating; -- Cleanup Phase --; === Round 7 ===; Charlie's turn begins |
| 45 | 7 | Charlie | move — explore legal SE slot (1,4) | success | R7 playerPhase; next P2; actions=1; rooms=11; corridors=10; intruders=5; gameOver=False | Charlie discovers commsRoom; Charlie moves to explore_trace_045 |
| 46 | 7 | Charlie | pass — no action cards | success | R8 playerPhase; next P2; actions=2; rooms=11; corridors=10; intruders=5; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Alarm; -- Cleanup Phase --; === Round 8 ===; Charlie's turn begins |
| 47 | 8 | Charlie | move — explore legal E slot (2,4) | success | R8 playerPhase; next P2; actions=1; rooms=12; corridors=11; intruders=5; gameOver=False | Charlie discovers powerGenerator; Charlie moves to explore_trace_047 |
| 48 | 8 | Charlie | pass — no action cards | success | R9 playerPhase; next P2; actions=2; rooms=12; corridors=11; intruders=7; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Infestation; drone(s) appear; adult(s) appear; -- Cleanup Phase --; === Round 9 ===; Charlie's turn begins |
| 49 | 9 | Charlie | search — first search by player in powerGenerator | success | R9 playerPhase; next P2; actions=1; rooms=12; corridors=11; intruders=7; gameOver=False | Charlie searches and finds yellow_gen_29 |
| 50 | 9 | Charlie | pass — no action cards | success | R10 playerPhase; next P2; actions=2; rooms=12; corridors=11; intruders=7; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Breeding; -- Cleanup Phase --; === Round 10 ===; Charlie's turn begins |
| 51 | 10 | Charlie | move — explore legal E slot (3,4) | success | R10 playerPhase; next P2; actions=1; rooms=13; corridors=12; intruders=7; gameOver=False | Charlie discovers sprinklersControl; Charlie moves to explore_trace_051 |
| 52 | 10 | Charlie | pass — no action cards | success | R11 playerPhase; next P2; actions=2; rooms=13; corridors=12; intruders=7; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Power Surge; Life Support in Section B turned off; -- Cleanup Phase --; === Round 11 ===; Charlie's turn begins |
| 53 | 11 | Charlie | search — first search by player in sprinklersControl | success | R11 playerPhase; next P2; actions=1; rooms=13; corridors=12; intruders=7; gameOver=False | Charlie searches and finds Painkillers |
| 54 | 11 | Charlie | pass — no action cards | success | R12 playerPhase; next P2; actions=2; rooms=13; corridors=12; intruders=7; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Scent of Prey; -- Cleanup Phase --; === Round 12 ===; Charlie's turn begins |
| 55 | 12 | Charlie | useRoom — exercise sprinklersControl room effect | success | R12 playerPhase; next P2; actions=1; rooms=13; corridors=12; intruders=7; gameOver=False | Charlie uses Sprinklers Control; Sprinklers put out all fires |
| 56 | 12 | Charlie | pass — no action cards | success | R13 playerPhase; next P2; actions=2; rooms=13; corridors=12; intruders=7; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Nest Awakening; -- Cleanup Phase --; === Round 13 ===; Charlie's turn begins |
| 57 | 13 | Charlie | pass — no additional legal or useful action | success | R14 playerPhase; next P2; actions=2; rooms=13; corridors=12; intruders=10; gameOver=False | Charlie passes; -- Intruder Phase --; -- Event Phase --; Event: Intruder Surge; drone(s) appear; adult attacks Charlie: Lose 2 Health.; adult(s) appear; adult attacks Charlie: Heavily Injured: die. Otherwise gain 1 Serious Wound.; Charlie gains a Serious Wound; adult(s) appear; -- Cleanup Phase --; === Round 14 ===; Charlie's turn begins |
| 58 | 14 | Charlie | melee — combat: melee adult in room | success | R14 playerPhase; next P2; actions=1; rooms=13; corridors=12; intruders=10; gameOver=False | Charlie melee attacks! Roll: 4; adult attacks Charlie: Lose 2 Health. |
| 59 | 14 | Charlie | melee — combat: melee adult in room | success | R14 playerPhase; next P2; actions=2; rooms=13; corridors=12; intruders=10; gameOver=False | Charlie melee attacks! Roll: 1; adult attacks Charlie: Lose 2 Health. Gain 1 Contamination.; Charlie's turn begins |
| 60 | 14 | Charlie | pass — no action cards | success | R15 playerPhase; next P2; actions=2; rooms=13; corridors=12; intruders=10; gameOver=True | Charlie passes; -- Intruder Phase --; adult attacks Charlie: Lose 1 Health. Gain 1 Contamination.; Charlie dies (intruder); -- Event Phase --; Event: Malfunction; -- Cleanup Phase --; === Game Over === |

## Final state

```json
{
  "round": 15,
  "phase": "playerPhase",
  "currentPlayer": 2,
  "actionsRemaining": 2,
  "gameOver": true,
  "winners": [],
  "rooms": 13,
  "corridors": 12,
  "intruders": 10,
  "intruderTypes": {
    "drone": 6,
    "adult": 4
  },
  "queen": {
    "inPlay": true,
    "location": {
      "type": "pending",
      "id": "nest"
    },
    "hits": 0,
    "dead": false,
    "healthCardsRemaining": 12
  },
  "nest": {
    "eggs": 5,
    "destroyed": false,
    "pendingDrones": 0
  },
  "autodestruction": {
    "active": false,
    "token": null
  },
  "lifeSupport": {
    "A": true,
    "B": false,
    "C": true
  },
  "players": [
    {
      "id": 0,
      "name": "Alpha",
      "character": "contractor",
      "alive": false,
      "health": -1,
      "oxygen": 7,
      "location": "gunneryRoom",
      "cards": 0,
      "backpack": [],
      "gear": [
        null,
        null,
        null,
        null
      ],
      "contamination": 0,
      "seriousWounds": 0,
      "larva": false,
      "escaped": false,
      "hibernated": false,
      "inLander": false,
      "objective": "mo7",
      "objectiveComplete": null
    },
    {
      "id": 1,
      "name": "Bravo",
      "character": "recon",
      "alive": false,
      "health": -1,
      "oxygen": 7,
      "location": "lifeSupportControlA",
      "cards": 0,
      "backpack": [],
      "gear": [
        null,
        null,
        null,
        null
      ],
      "contamination": 0,
      "seriousWounds": 1,
      "larva": false,
      "escaped": false,
      "hibernated": false,
      "inLander": false,
      "objective": "mo5",
      "objectiveComplete": null
    },
    {
      "id": 2,
      "name": "Charlie",
      "character": "officer",
      "alive": false,
      "health": 0,
      "oxygen": 2,
      "location": "sprinklersControl",
      "cards": 0,
      "backpack": [],
      "gear": [
        null,
        null,
        null,
        null
      ],
      "contamination": 1,
      "seriousWounds": 1,
      "larva": true,
      "escaped": false,
      "hibernated": false,
      "inLander": false,
      "objective": "mo4",
      "objectiveComplete": null
    },
    {
      "id": 3,
      "name": "Delta",
      "character": "medicalSupport",
      "alive": false,
      "health": 1,
      "oxygen": 7,
      "location": "gunneryRoom",
      "cards": 0,
      "backpack": [],
      "gear": [
        null,
        null,
        null,
        null
      ],
      "contamination": 1,
      "seriousWounds": 1,
      "larva": false,
      "escaped": false,
      "hibernated": false,
      "inLander": false,
      "objective": "mo1",
      "objectiveComplete": null
    }
  ]
}
```

## Runtime failures

- None detected.

## Browser errors

- None detected.
