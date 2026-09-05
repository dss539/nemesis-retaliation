#!/usr/bin/env bash
# Coordinator disposition of the 15 Objective-family fail claims from verifier wave R3.
set -e
cd /home/smithers/nemesis-retaliation
S=scripts/audit_fail_to_unsure.py
CORPSE="the exact TTS face is captured verbatim in INT-011; the corpse component/mechanic has no base-game official source and is held open as OQ-013 (possible add-on content), so operative status is genuinely unsettled rather than missing."
CHOICE="the exact TTS face is captured verbatim in INT-011; the choose/cannot-choose instruction is a source-variant Objective-selection restriction with no official base-game counterpart, and Objective eligibility semantics are held open as OQ-014."
OWN="the exact TTS face is captured verbatim in INT-011 together with the official ranking note (OBJ-44); which player the first/second option binds to is an explicitly preserved open boundary, not an omission."
PLAYERN="the exact TTS face is captured verbatim in INT-011; it references Player 6-10 which exceeds the base game's 1-5 player count (FND-007), so the face is a prototype/expansion-scope variant whose base-game eligibility is held open as OQ-014."
BADGE="the exact TTS face is captured verbatim in INT-011 with its unresolved badge preserved literally and its conflict with official P1-MT-FACILITY-RESTART recorded; the badge identity is an open source question, not a corpus omission."
python3 $S CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-05.png "$CORPSE"
python3 $S CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-18.png "$CORPSE"
python3 $S CARD-game-missionTaskDeck-game-missionTaskDeck-160_cards-card-08.png "$BADGE"
python3 $S CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-04.png "$CHOICE"
python3 $S CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-05.png "$CHOICE"
for n in 11 12 13 14 15; do python3 $S CARD-game-objectiveMissonDeck-game-objectiveMissonDeck-162_cards-card-$n.png "$OWN"; done
for n in 157 158 159 161; do python3 $S CARD-game-objectivePersonalDeck-game-objectivePersonalDeck-$n.jpg "$PLAYERN"; done
python3 $S RB-P39-022.fact "the 2+ threshold is captured verbatim in INT-011 and the setup-time removal filter exists in FND-011; whether N+ has any in-play effect is held open as OQ-014."
ls audit/fail/
