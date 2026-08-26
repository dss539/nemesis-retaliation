#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

from semantic_green_item_validation import validate_green_item_family

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / 'docs/rules/semantics'
VOCAB = REPO / 'docs/rules/vocabulary'
ONTOLOGY = REPO / 'docs/rules/ontology'
EXPECTED = {
    'sources': 160, 'semanticNodes': 26, 'records': 232, 'sourceBacked': 99, 'withOpenQuestion': 131,
    'sourceVariants': 2, 'sourceAssertions': 732, 'conditions': 855,
    'operations': 995, 'decisions': 113, 'informationPolicies': 247,
    'costs': 11, 'targets': 328, 'openQuestionReferences': 198,
    'variantReferences': 130, 'questions': 50, 'openQuestions': 50, 'systems': 21,
    'conflicts': 33, 'unresolvedConflicts': 12,
    'roomIconDenotations': 112,
    'backlogUnits': 600, 'backlogPilotCovered': 215, 'backlogSourceBlocked': 1,
    'eventIdentities': 20, 'eventScanOccurrences': 20, 'eventLicensedOccurrences': 20,
    'eventOfficialOccurrences': 4, 'eventRecords': 20, 'eventBacklogTuples': 20,
    'explorationIdentities': 12, 'explorationScanOccurrences': 12,
    'explorationLicensedOccurrences': 12, 'explorationOfficialOccurrences': 3,
    'explorationPrintedSentences': 46, 'explorationIconOccurrences': 60,
    'explorationRecords': 12, 'explorationBacklogTuples': 12,
    'robotIdentities': 6, 'robotScanOccurrences': 6, 'robotSharedBackOccurrences': 1,
    'robotLicensedOccurrences': 6, 'robotOfficialOccurrences': 2,
    'robotPhysicalPanels': 24, 'robotOperativePanels': 12, 'robotActionOptions': 13,
    'robotPrintedSentences': 16, 'robotIconOccurrences': 23,
    'robotRecords': 6, 'robotBacklogTuples': 6,
    'attackIdentities': 20, 'attackScanOccurrences': 20,
    'attackGeneratedOccurrences': 19, 'attackDirectOccurrences': 1,
    'attackSharedBackOccurrences': 1, 'attackSourceSheets': 1, 'attackSelectorGaps': 1,
    'attackLicensedVariants': 15, 'attackLicensedFaceLinks': 20,
    'attackOfficialFaceCounterparts': 3, 'attackOfficialBackCounterparts': 1,
    'attackPhysicalPanels': 69, 'attackOperativePanels': 29,
    'attackPrintedSentences': 54, 'attackBadgeOccurrences': 57,
    'attackInlineIconOccurrences': 13, 'attackFunctionalSymbolOccurrences': 70,
    'attackSelectedNoMatches': 55, 'attackRecords': 20, 'attackBacklogTuples': 20,
    'queenHealthPhysicalOccurrences': 12, 'queenHealthUniqueFaceAssets': 10,
    'queenHealthSharedBackOccurrences': 1, 'queenHealthLicensedOccurrences': 12,
    'queenHealthOfficialFaceOccurrences': 3, 'queenHealthOfficialBackOccurrences': 2,
    'queenHealthPhysicalPanels': 24, 'queenHealthPrintedSentences': 37,
    'queenHealthLocalDisplayOccurrences': 12, 'queenHealthMatchedIconOccurrences': 16,
    'queenHealthFunctionalIconOccurrences': 28, 'queenHealthRecords': 12,
    'queenHealthBacklogTuples': 10,
    'seriousWoundPhysicalOccurrences': 27, 'seriousWoundUniqueTitles': 9,
    'seriousWoundSelectedFaceAssets': 9, 'seriousWoundSourceFaceAssets': 11,
    'seriousWoundGeneratedOccurrences': 21, 'seriousWoundDirectOccurrences': 6,
    'seriousWoundSharedBackOccurrences': 1, 'seriousWoundSourceSheets': 1,
    'seriousWoundSelectorGaps': 2, 'seriousWoundPhysicalRegions': 81,
    'seriousWoundOperativeRegions': 27, 'seriousWoundPhysicalPanels': 54,
    'seriousWoundOperativePanels': 27, 'seriousWoundPrintedSentences': 42,
    'seriousWoundFunctionalIconOccurrences': 30, 'seriousWoundMatchedIconOccurrences': 24,
    'seriousWoundUnresolvedLocalGlyphOccurrences': 6,
    'seriousWoundLicensedOccurrences': 9, 'seriousWoundOfficialFaceOccurrences': 3,
    'seriousWoundOfficialBackOccurrences': 2, 'seriousWoundRecords': 27,
    'seriousWoundBacklogTuples': 11,
    'greenItemRootOccurrences': 30, 'greenItemPhysicalOccurrences': 23,
    'greenItemExcludedHeavyOccurrences': 7, 'greenItemUniqueTitles': 8,
    'greenItemSelectedFaceAssets': 8, 'greenItemSourceFaceAssets': 14,
    'greenItemGeneratedOccurrences': 15, 'greenItemDirectOccurrences': 8,
    'greenItemSharedBackOccurrences': 1, 'greenItemSourceSheets': 1,
    'greenItemSelectorGaps': 4, 'greenItemPhysicalRegions': 69,
    'greenItemOperativeRegions': 46, 'greenItemPhysicalPanels': 85,
    'greenItemOperativePanels': 62, 'greenItemPrintedSentences': 46,
    'greenItemFunctionalIconOccurrences': 46, 'greenItemMatchedIconOccurrences': 37,
    'greenItemUnresolvedLocalGlyphOccurrences': 9,
    'greenItemLicensedOccurrences': 10, 'greenItemLicensedCopies': 30,
    'greenItemLicensedRegularCopies': 23, 'greenItemLicensedHeavyCopies': 7,
    'greenItemOfficialFaceOccurrences': 0, 'greenItemOfficialBackOccurrences': 0,
    'greenItemOfficialFamilyOccurrences': 7, 'greenItemRecords': 23,
    'greenItemBacklogTuples': 12,
}
PINNED_HELP_SOURCE_HASHES = {
    'docs/rules/source-extraction/intruder-help-sheet.json': 'e07f2703a6ad1b49c06389f79d3b1ffd6f5fd1d98604bf14b405fee49d9679e6',
    'docs/rules/source-extraction/room-help-sheet.json': 'ad3d6bb66de939fe1036ecca3fc8d8d9b41fe41e1065f7bd9611df8263480177',
    'docs/rules/source-extraction/room-help-sheet-source-fidelity-lock.json': '27c23c1c885e2ab851bef0bfb43b7471ea862af9d0308f9b3e70026320b4d8b4',
}
PINNED_EXPLORATION_SOURCE_INDEX_HASH = 'd95dc30738ce2efbb4cf696671388aaf731626f167601fdca70c6fee74dc95bd'
PINNED_ROBOT_SOURCE_INDEX_HASH = 'd5c0f1abb5794cdddebba42b38580627122a43da96f8da0ff289d5b917c9b6a4'
PINNED_ATTACK_SOURCE_INDEX_HASH = 'c7b26acaccdb08f166a5618fa9c140189239f50645e1e6601ecc7dfda210f6b3'
PINNED_QUEEN_HEALTH_SOURCE_INDEX_HASH = '74fc260e2d09f4676b186431f59d8564b7f9bb3f3e8091d50b80e003fbc29988'
PINNED_SERIOUS_WOUND_SOURCE_INDEX_HASH = '417798990fd5e9a857db6af10c2343f522b6041dc87e3231b0a7a10787c1ad27'
EXPECTED_EVENT_OCCURRENCES = {
    5609: ('SRC-EVENT-5609','assets/tts-mod/extract/v2-dl/tree/cards/game/event-099.png','0d5da2c8e1b6ccb6a30c83f9006aa924f4fc2f1f14d360d153bc5ea6f73770ed','Event_SystemFailure','SEM-EVENT-SYSTEM-FAILURE-001','SYSTEM FAILURE'),
    5610: ('SRC-EVENT-5610','assets/tts-mod/extract/v2-dl/tree/cards/game/event-009.png','92bc91f54116780d214aefd7925a46897d811f699c5921edd55f45b40deb989d','Event_NoWayOut','SEM-EVENT-NO-WAY-OUT-001','NO WAY OUT'),
    5611: ('SRC-EVENT-5611','assets/tts-mod/extract/v2-dl/tree/cards/game/event-072.png','890259ff52beb7bb5235f2efd010b4e54ee752e9d85cb27f2de2576257fa33bb','Event_TheQueenAwakens','SEM-EVENT-THE-QUEEN-AWAKENS-001','THE QUEEN AWAKENS'),
    5612: ('SRC-EVENT-5612','assets/tts-mod/extract/v2-dl/tree/cards/game/event-100.png','592afbb981cdb9bcae45812d38285a7e7cc1dd41bb21446861d51d000e9b0070','Event_ScentOfPrey','SEM-EVENT-SCENT-OF-PREY-001','SCENT OF PREY'),
    5613: ('SRC-EVENT-5613','assets/tts-mod/extract/v2-dl/tree/cards/game/event-170.png','86ba726fa9fa4a8d9ed2913f6619db2d5df1b5ad1e3c69bd0b380993c9e8967e','Event_Panic','SEM-EVENT-PANIC-001','PANIC'),
    5614: ('SRC-EVENT-5614','assets/tts-mod/extract/v2-dl/tree/cards/game/event-054.png','ac3dc8c20efc3e964383bb9956b264bf3f4a64762d8d8920f5c612d1841ec4bf','Event_LeavingTheShell','SEM-EVENT-LEAVING-THE-SHELL-001','LEAVING THE SHELL'),
    5615: ('SRC-EVENT-5615','assets/tts-mod/extract/v2-dl/tree/cards/game/event-086.png','fe6a4f8faae5efdecb02b1ec436c605f792f5f78dd332e1cf64cffc532631ab0','Event_BreakingIn','SEM-EVENT-BREAKING-IN-001','BREAKING IN'),
    5616: ('SRC-EVENT-HATCHING','assets/tts-mod/extract/v2-dl/tree/cards/game/event-090.png','45b5845d04f57b10dff6e73005be88cba0107a1a15da83f581df6531390d1ac9','Event_Hatching','SEM-EVENT-HATCHING-001','HATCHING'),
    5617: ('SRC-EVENT-5617','assets/tts-mod/extract/v2-dl/tree/cards/game/event-179.png','72a3270de96356e8ea1e64b9bf1d2b90e189a7ae6f1031d03b6db453d3f93eab','Event_EggProtection','SEM-EVENT-EGG-PROTECTION-001','EGG PROTECTION'),
    5618: ('SRC-EVENT-5618','assets/tts-mod/extract/v2-dl/tree/cards/game/event-096.png','85d08e0de5b2710ed0e1ac0295ed27da3b4d0da9eb2419aa0f0093d94f1b70d5','Event_LandingZoneExplodes','SEM-EVENT-LANDING-ZONE-EXPLODES-001','LANDING ZONE EXPLODES'),
    5619: ('SRC-EVENT-5619','assets/tts-mod/extract/v2-dl/tree/cards/game/event-139.png','53351204890c5e98381a1fc4712e574a701659ec913b5f9c3f838ac6074c9614','Event_Damage','SEM-EVENT-DAMAGE-001','DAMAGE'),
    5620: ('SRC-EVENT-5620','assets/tts-mod/extract/v2-dl/tree/cards/game/event-064.png','93bd00726c0683feb10a47c85c86055438114c3a8c5fbb33500325fa195d2158','Event_LifeSupportFailure','SEM-EVENT-LIFE-SUPPORT-FAILURE-001','LIFE SUPPORT FAILURE'),
    5621: ('SRC-EVENT-5621','assets/tts-mod/extract/v2-dl/tree/cards/game/event-052.png','22f94926170929195f8bd6cea3b09090d24121d4803f77d99636ec85bafdb0ae','Event_FireBreath','SEM-EVENT-FIRE-BREATH-001','FIRE BREATH'),
    5622: ('SRC-EVENT-5622','assets/tts-mod/extract/v2-dl/tree/cards/game/event-167.png','37bbf022f99ef62a18a5225aaf31347f6299f72672603547f51918502241f27b','Event_DamagingFire','SEM-EVENT-DAMAGING-FIRE-001','DAMAGING FIRE'),
    5623: ('SRC-EVENT-5623','assets/tts-mod/extract/v2-dl/tree/cards/game/event-172.jpg','33625882c8388c183850eaf236af6c6ffd22368d06d1875681db607bce5be07c','Event_GeneratorsOverheat','SEM-EVENT-GENERATORS-OVERHEAT-001','GENERATORS OVERHEAT'),
    5624: ('SRC-EVENT-5624','assets/tts-mod/extract/v2-dl/tree/cards/game/event-051.jpg','2eb453e8f770bbee9ab5b951fb22e952d34c1250876b88e878a461c11f7f8ded','Event_OverwhelmingEnemies','SEM-EVENT-OVERWHELMING-ENEMIES-001','OVERWHELMING ENEMIES'),
    5625: ('SRC-EVENT-5625','assets/tts-mod/extract/v2-dl/tree/cards/game/event-093.jpg','6f93c7b3d25bb4fcbf6b7d786f31172b09a65f888b9fdb707917a7fae916b868','Event_ProtectServe','SEM-EVENT-PROTECT-AND-SERVE-001','PROTECT & SERVE'),
    5626: ('SRC-EVENT-5626','assets/tts-mod/extract/v2-dl/tree/cards/game/event-006.jpg','50f71404b19fc4c65f970fffb229f8b92b2db6b73fa2daea73d90d522f12f9fc','Event_ReactorOverheating','SEM-EVENT-REACTOR-OVERHEATING-001','REACTOR OVERHEATING'),
    5627: ('SRC-EVENT-5627','assets/tts-mod/extract/v2-dl/tree/cards/game/event-166.jpg','dfeef8373c59637e6a30eeb6e6d43f47e3a138e562a520ba0e15198a35c787f9','Event_RiseOfTheMachine','SEM-EVENT-RISE-OF-THE-MACHINE-001','RISE OF THE MACHINE'),
    5628: ('SRC-EVENT-5628','assets/tts-mod/extract/v2-dl/tree/cards/game/event-058.jpg','cdf03513025769517d9a0e05ac3881120176a1d506db118fd3db50b6c82d9762','Event_ShortCircuit','SEM-EVENT-SHORT-CIRCUIT-001','SHORT CIRCUIT'),
}
EXPECTED_EVENT_QUESTION_REFS = {
    'SEM-EVENT-SYSTEM-FAILURE-001': ['SEM-Q-008'],
    'SEM-EVENT-NO-WAY-OUT-001': ['SEM-Q-007'],
    'SEM-EVENT-LEAVING-THE-SHELL-001': ['SEM-Q-006'],
    'SEM-EVENT-HATCHING-001': ['OQ-009','SEM-Q-007'],
    'SEM-EVENT-EGG-PROTECTION-001': ['OQ-007','OQ-009','SEM-Q-007'],
    'SEM-EVENT-DAMAGE-001': ['SEM-Q-008'],
    'SEM-EVENT-LIFE-SUPPORT-FAILURE-001': ['SEM-Q-008'],
    'SEM-EVENT-FIRE-BREATH-001': ['SEM-Q-009'],
    'SEM-EVENT-DAMAGING-FIRE-001': ['SEM-Q-008','SEM-Q-009'],
    'SEM-EVENT-GENERATORS-OVERHEAT-001': ['SEM-Q-008'],
    'SEM-EVENT-OVERWHELMING-ENEMIES-001': ['SEM-Q-007'],
    'SEM-EVENT-REACTOR-OVERHEATING-001': ['SEM-Q-008'],
    'SEM-EVENT-RISE-OF-THE-MACHINE-001': ['SEM-Q-010','SEM-Q-012'],
}
EXPECTED_EVENT_RECORD_DIGESTS = {
    'SEM-ECLOSION-PROCEDURE-001': '353ee18e5b0f66d237cb84c0f5af55bdf68a2e80628d51e563ce3c84d780eb4d',
    'SEM-EVENT-BREAKING-IN-001': 'da7f0f0a0ad3478b3caa3bd41efa9e9538fac69adb0a7d17201a9291d76efbd8',
    'SEM-EVENT-DAMAGE-001': 'a252b148517f13e9d9eb30fe288443f522c451101547e59cf6fb9cc519800168',
    'SEM-EVENT-DAMAGING-FIRE-001': 'e8c718ae5c00d6e8f4abccb1b864c7885a2fb56a95b89797df53a00d45f9ca89',
    'SEM-EVENT-EGG-PROTECTION-001': 'c046e6445641ec4225834dadc9f439400d9dfa6888943f893f82a06697003ffe',
    'SEM-EVENT-FIRE-BREATH-001': 'b9edf7973c9cefc9aa47fdbd385acccaf831572c63a28714115072b2c0ef8b4c',
    'SEM-EVENT-GENERAL-001': '58f8169335e0a66b9b66e6fd89ce7734f10ab8888136fd7518aeb072d3b4c5df',
    'SEM-EVENT-GENERATORS-OVERHEAT-001': '1e6055ca03a72b58d1711bc92fae0a4bb9ba57dd9fe1b1ab0e4cf80f58c81eeb',
    'SEM-EVENT-HATCHING-001': '0860d2870d18b7baca933486da02f3c8a89984cd2c4f222d8985f19c32a9c5a8',
    'SEM-EVENT-INTRUDER-MOVEMENT-001': '4c703bc0874fd8da6dcbe3317c63e415852e16ff7fb0674bfe6d1f67f614fdd9',
    'SEM-EVENT-LANDING-ZONE-EXPLODES-001': '2c8b1b9ae1df5d2d158ef9552fd46757678ffe3a00e0090773548a21c36719d4',
    'SEM-EVENT-LEAVING-THE-SHELL-001': 'a1e778e6a95c105e711da9081802de11af3b10bb7d406867d039a5a699e9ea94',
    'SEM-EVENT-LIFE-SUPPORT-FAILURE-001': 'a310c84257048566ffa23e12812626079aa5cea054759fddf5a5e1dbe8d2a678',
    'SEM-EVENT-NO-WAY-OUT-001': '35e2f08f513d5f8f3a5337adc3d29f0b1ded3dbe6201beab746e3d15af4fc33a',
    'SEM-EVENT-OVERWHELMING-ENEMIES-001': 'd12457f82c6387f60b980dd42c8a2e16269efe8e45065c2fa9930ed8deddd82c',
    'SEM-EVENT-PANIC-001': 'c5c497eac399b2e83ca96324b97bb56d6270fc2d79b83cc78caa73780494c374',
    'SEM-EVENT-PROTECT-AND-SERVE-001': '2889b8f62a546327ce5197aea65a46695e389b7c63896de3d4dfb5af62add55b',
    'SEM-EVENT-REACTOR-OVERHEATING-001': 'f84eeab2ee28282885036e0ff2a9af8f13ac0e7163980b7c8de1f96785d82623',
    'SEM-EVENT-RISE-OF-THE-MACHINE-001': '1c93407dad63f2e01b75302501ab7722b7c5ff4a7f40f8de19fd10cf9bf6090f',
    'SEM-EVENT-SCENT-OF-PREY-001': '7d70eca226175371c6bc5925d724566cca6813f73bc3e10a8bdfdf3b233cfd73',
    'SEM-EVENT-SHORT-CIRCUIT-001': '6e3445c62a1f08bfa5af65d93b3520f9dd051e596a12a53b33639f50f290737d',
    'SEM-EVENT-SYSTEM-FAILURE-001': 'adb43651ddb31059424d57517f86abb98de6b25ca10292de3e4d0e1ff9f7b936',
    'SEM-EVENT-THE-QUEEN-AWAKENS-001': 'c34b54c4f99ea51600c7aafe97fa3347c33c7e23e946e3eace460deea8380840',
    'SEM-FIRE-SPREAD-001': '6aa2dc4b0e05a34f9e63e440ed361f288eee92b87a435cd93598e1bccf0319ee',
    'SEM-INFECTION-PROCEDURE-001': 'bde76697380555865279565e575a4a2eb75321d1058c59260573b35e00da9320',
    'SEM-NOISE-HAZARD-001': '2d7aa66a6162c167575bcec4035ce796bbfcb66002322a076e712e9df2910429',
    'SEM-NOISE-MARKER-001': '2178186f1b94ce67935a1c5b0165d1dfa466ccc5f3705d33c10982a279c41407',
    'SEM-SECURE-ENTRY-001': '74836078c570e2be6c092add9fb4d027ce18b8f70ee5dad26e27c5a4ca0ae4d2',
}
EXPECTED_EXPLORATION_OCCURRENCES = {
    5629: {'sourceId':'SRC-EXPLORATION-5629','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-027.png','sha256':'3da198b348a70d64e20de051034e98aa2454ef1912df3cf18e78eaf7c4800043','guid':'f1056e','bgaKey':'ExplorationCard9','ruleId':'SEM-EXPLORATION-5629-001','roomType':'ABC','corridors':[1,2,3],'noise':[2],'roomIcons':[],'sentences':3,'icons':5,'adultCount':0,'closeDoor':False,'removeFromGame':False,'official':[]},
    5630: {'sourceId':'SRC-EXPLORATION-5630','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-107.png','sha256':'daf8fb6f2bc9836bf7d457acf909fdd033aa55e182308e61b2d59e952bbced7c','guid':'4cc309','bgaKey':'ExplorationCard10','ruleId':'SEM-EXPLORATION-5630-001','roomType':'ABC','corridors':[0,2,3],'noise':[0,3],'roomIcons':[],'sentences':4,'icons':5,'adultCount':2,'closeDoor':False,'removeFromGame':False,'official':[]},
    5631: {'sourceId':'SRC-EXPLORATION-5631','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-062.png','sha256':'b3be8596be1e99b3b520b0ce2c37e7f14a48c6a90dc4e422d32ae92592fbab38','guid':'0fc783','bgaKey':'ExplorationCard11','ruleId':'SEM-EXPLORATION-5631-001','roomType':'ABC','corridors':[2,5],'noise':[2],'roomIcons':[],'sentences':4,'icons':4,'adultCount':3,'closeDoor':False,'removeFromGame':False,'official':[]},
    5632: {'sourceId':'SRC-EXPLORATION-5632','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-031.png','sha256':'549bb22b017b6df982c3378f613294969d7043a1a87a1e4b4f5d704308d2ceb0','guid':'307c1a','bgaKey':'ExplorationCard5','ruleId':'SEM-EXPLORATION-5632-001','roomType':'ABC','corridors':[1,2],'noise':[2],'roomIcons':['malfunction'],'sentences':4,'icons':5,'adultCount':0,'closeDoor':True,'removeFromGame':False,'official':[]},
    5633: {'sourceId':'SRC-EXPLORATION-5633','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-025.png','sha256':'774b6ed8ea4492bfae38145c828ae47c61536855ec1ffb86702d1fb2d2d09d8b','guid':'caf17f','bgaKey':'ExplorationCard4','ruleId':'SEM-EXPLORATION-5633-001','roomType':'ABC','corridors':[1,2,3],'noise':[1],'roomIcons':['malfunction'],'sentences':3,'icons':5,'adultCount':0,'closeDoor':False,'removeFromGame':False,'official':[]},
    5634: {'sourceId':'SRC-EXPLORATION-5634','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-024.png','sha256':'3cfb21c76b93ba8e23abf464321e7071d73aac0c23b0dc1763702206fe80854f','guid':'d80a23','bgaKey':'ExplorationCard6','ruleId':'SEM-EXPLORATION-5634-001','roomType':'ABC','corridors':[1,3],'noise':[3],'roomIcons':['fire'],'sentences':3,'icons':5,'adultCount':0,'closeDoor':False,'removeFromGame':False,'official':['RB-P26-V01','RB-P27-V01']},
    5635: {'sourceId':'SRC-EXPLORATION-5635','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-032.png','sha256':'9c521a0ca8f9303363e69266962c20bee13b7a03cc8d05410399755ea42c684b','guid':'41c838','bgaKey':'ExplorationCard12','ruleId':'SEM-EXPLORATION-5635-001','roomType':'ABC','corridors':[1,2,4],'noise':[1],'roomIcons':[],'sentences':4,'icons':4,'adultCount':4,'closeDoor':False,'removeFromGame':False,'official':[]},
    5636: {'sourceId':'SRC-EXPLORATION-5636','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-026.png','sha256':'08445a3d8b18081d7396756f407ac058c383c3aee05bde76e80393b0af4b741d','guid':'ab7ffb','bgaKey':'ExplorationCard7','ruleId':'SEM-EXPLORATION-5636-001','roomType':'ABC','corridors':[2,3],'noise':[],'roomIcons':['fire'],'sentences':4,'icons':4,'adultCount':0,'closeDoor':True,'removeFromGame':False,'official':[]},
    5637: {'sourceId':'SRC-EXPLORATION-5637','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-037.png','sha256':'3101f9f9a5df9d01aa07073837412496355c63df94216ab1550abc6a21221516','guid':'3c770d','bgaKey':'ExplorationCard3','ruleId':'SEM-EXPLORATION-5637-001','roomType':'?','corridors':[1,3,4],'noise':[1],'roomIcons':[],'sentences':4,'icons':5,'adultCount':0,'closeDoor':False,'removeFromGame':True,'official':[]},
    5638: {'sourceId':'SRC-EXPLORATION-5638','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-036.png','sha256':'160d5d76b631d1ccbd1e4ea981313a1edbd83a6e9eda34dd825fafc2f9cbdd4d','guid':'2e1fdc','bgaKey':'ExplorationCard2','ruleId':'SEM-EXPLORATION-5638-001','roomType':'?','corridors':[0,1,3],'noise':[1],'roomIcons':['malfunction','fire'],'sentences':5,'icons':6,'adultCount':0,'closeDoor':True,'removeFromGame':True,'official':[]},
    5639: {'sourceId':'SRC-EXPLORATION-5639','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-087.png','sha256':'d52ff877e59bfda1b306074b5567b4c0bf93a0be9b4e257acc88b38f87a7c85f','guid':'2c8495','bgaKey':'ExplorationCard1','ruleId':'SEM-EXPLORATION-5639-001','roomType':'?','corridors':[0,1,3,4],'noise':[0,1,3,4],'roomIcons':['malfunction'],'sentences':4,'icons':8,'adultCount':0,'closeDoor':True,'removeFromGame':True,'official':['RB-P24-V01']},
    5640: {'sourceId':'SRC-EXPLORATION-5640','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-076.png','sha256':'e4e92cae40da14f30ee73a8f27ea8291d0861db0688ac207219fa475f24cd832','guid':'046266','bgaKey':'ExplorationCard8','ruleId':'SEM-EXPLORATION-5640-001','roomType':'ABC','corridors':[2,5],'noise':[],'roomIcons':[],'sentences':4,'icons':4,'adultCount':0,'closeDoor':True,'removeFromGame':False,'official':[]},
}
EXPECTED_EXPLORATION_RECORD_DIGESTS = {
    'SEM-EXPLORATION-5629-001': 'c67774e8b9cf5d7bff4d2f93c73e35a993eddf165c1b8fbd928ba4e95ccec37e',
    'SEM-EXPLORATION-5630-001': '227f17240e9b6b4cf1e8dfe125262794f1ef985026372b1f24be70bb43bebbb5',
    'SEM-EXPLORATION-5631-001': 'b96b3900c52310914c582ff94fbcf9de22a56016716d2ae740eb3737f3fd426e',
    'SEM-EXPLORATION-5632-001': 'f3218b560fb059cf136f525c89528c8ef1a5dbbee625bd09e9f1d7826c9c0452',
    'SEM-EXPLORATION-5633-001': '09c982f40224ec0ec1d1547ee96de4bc2b86551ce3cda4b994f45c7e7e499d0d',
    'SEM-EXPLORATION-5634-001': 'd691d6ece935fc194256bc0bf1a38bb671f38f73fe68a1de3f6640c08af0abfa',
    'SEM-EXPLORATION-5635-001': '49534f7ec83a49e71db3eb91f473a1c3cbabcdabd5eaa15be0f88634140d8c4a',
    'SEM-EXPLORATION-5636-001': '5488ab19858e5ee999dff21c5685ba2dab1c3ba716548b4db030f56ccf3ce665',
    'SEM-EXPLORATION-5637-001': 'f6e4958eb800a5d2c87909d2d6d0c2edc5432d988c7f8f628f21e855ae5c1786',
    'SEM-EXPLORATION-5638-001': 'fd8933c8bccf4c8a1bec6c3c3b9efd5c9ef95c326660c91b40211b704a925fa9',
    'SEM-EXPLORATION-5639-001': 'be75a3b593a4557f183ce4fc64859c53fb08af2e62bb822dce05de5e0de82fe2',
    'SEM-EXPLORATION-5640-001': '83c7ada5593f49b1dbde1559e658e3f0ed71f0a7bc09b7de77b80492ca81a81d',
}
EXPECTED_ROBOT_COUNTS = {
    'robotIdentities':6,'ttsFaceOccurrences':6,'directCompositeFaceSelectors':6,
    'generatedSpriteSheetCells':0,'selectorGaps':0,'ttsSharedBackOccurrences':1,
    'baseBackSelectorReferences':7,'prototypeBackSelectorReferencesExcluded':2,
    'canonicalCorpusFaces':4,'sourceBoundDraftFaces':2,'licensedDigitalOccurrences':6,
    'officialVisibleComponentOccurrences':2,'officialVisibleComponentIdentities':2,
    'physicalPanels':24,'operativePanels':12,'actionOptions':13,'printedSentences':16,
    'functionalIconOccurrences':23,'officialVisibleFaceIconOccurrences':8,
    'licensedPlaceholderOccurrences':23,'rulebookTextOccurrences':27,
    'rulebookVisualOccurrences':8,'baseFaqOccurrences':1,'excludedExpansionFaqOccurrences':2,
    'prototypeRobotCardsExcluded':2,'expansionRobotCardsExcluded':3,
    'securityRobotRoomNameCollisionsExcluded':4,'backlogTuples':6,'backlogObligationsLinked':18,
}
EXPECTED_ROBOT_OCCURRENCES = {
    506400: {'sourceId':'SRC-ROBOT-506400','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-068.jpg','sha256':'e613b1e23d25d91e1fe5ccfe925426396c0866c5a36cba91a69dcdb493f2b2a6','guid':'cd319d','rootDeckNumber':'5064','childDeckNums':['5064'],'bgaKey':'ServerRobot','ruleId':'SEM-ROBOT-SERVER-001','title':'SERVER ROBOT','sentenceIds':['RB506400-O1-S01','RB506400-O2-S01'],'optionIds':['O1','O2'],'iconRefs':['icon.robot','icon.robot','icon.computer','icon.malfunction'],'official':['RB-P03-V01-ROBOT-SERVER']},
    510800: {'sourceId':'SRC-ROBOT-510800','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-173.jpg','sha256':'0e8c91aac8c15e467bbf177ddb3b8fd06600353b3f7af2f1af933b24fb1f1386','guid':'6a5c53','rootDeckNumber':'5108','childDeckNums':['5108'],'bgaKey':'SecuringRobot','ruleId':'SEM-ROBOT-SECURING-001','title':'SECURING ROBOT','sentenceIds':['RB510800-O1-S01','RB510800-O2-S01','RB510800-O3-S01'],'optionIds':['O1','O2','O3'],'iconRefs':['icon.robot','icon.robot','icon.secure','icon.robot'],'official':[]},
    529300: {'sourceId':'SRC-ROBOT-529300','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-004.jpg','sha256':'c78d2a69189749dcd4578ee7e270b83c6115510988286431943ba6039b2abc56','guid':'5f4876','rootDeckNumber':'5293','childDeckNums':['5293'],'bgaKey':'ExplorationRobot','ruleId':'SEM-ROBOT-EXPLORATION-001','title':'EXPLORATION ROBOT','sentenceIds':['RB529300-O1-S01','RB529300-O2-S01','RB529300-O2-S02'],'optionIds':['O1','O2'],'iconRefs':['icon.robot','icon.robot'],'official':[]},
    529400: {'sourceId':'SRC-ROBOT-529400','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-137.jpg','sha256':'db583cb973497fd2fba3b588d233d7c79db48e30d51e3cb0a4483524aa89fbbb','guid':'c5b268','rootDeckNumber':'5294','childDeckNums':['5107'],'bgaKey':'TechnicalRobot','ruleId':'SEM-ROBOT-TECHNICAL-001','title':'TECHNICAL ROBOT','sentenceIds':['RB529400-O1-S01','RB529400-O2-S01'],'optionIds':['O1','O2'],'iconRefs':['icon.robot','icon.malfunction','icon.fire','icon.robot'],'official':['RB-P03-V01-ROBOT-TECHNICAL']},
    529500: {'sourceId':'SRC-ROBOT-529500','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-130.jpg','sha256':'40751b42f461036517fa1ebc098de646dcf3a58d3407a288e54bb0da0a091dfb','guid':'90c510','rootDeckNumber':'5295','childDeckNums':['5109'],'bgaKey':'MedicalRobot','ruleId':'SEM-ROBOT-MEDICAL-001','title':'MEDICAL ROBOT','sentenceIds':['RB529500-O1-S01','RB529500-O2-S01'],'optionIds':['O1','O2'],'iconRefs':['icon.robot','icon.character','icon.robot','icon.characterHealth'],'official':[]},
    529600: {'sourceId':'SRC-ROBOT-529600','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-175.jpg','sha256':'27a7014ae8011fa68b71a60365b11ca0392b4e66c7d9bdfbe46eec3a6bb21411','guid':'fbe18a','rootDeckNumber':'5296','childDeckNums':['5110'],'bgaKey':'MilitaryRobot','ruleId':'SEM-ROBOT-MILITARY-001','title':'MILITARY ROBOT','sentenceIds':['RB529600-O1-S01','RB529600-O2-S01','RB529600-O2-S02','RB529600-O2-S03'],'optionIds':['O1','O2'],'iconRefs':['icon.robot','icon.robot','icon.burstDieAdditionalEffects','icon.malfunction','icon.robot'],'official':[]},
}
EXPECTED_ROBOT_QUESTION_REFS = {
    'SEM-ROBOT-SERVER-001':['SEM-Q-013','SEM-Q-018'],
    'SEM-ROBOT-SECURING-001':['SEM-Q-013','SEM-Q-016','SEM-Q-017'],
    'SEM-ROBOT-EXPLORATION-001':['SEM-Q-013','SEM-Q-014'],
    'SEM-ROBOT-TECHNICAL-001':['SEM-Q-013','SEM-Q-019'],
    'SEM-ROBOT-MEDICAL-001':['SEM-Q-013','SEM-Q-015'],
    'SEM-ROBOT-MILITARY-001':['SEM-Q-013'],
}
EXPECTED_ROBOT_RECORD_DIGESTS = {
    'SEM-ACT-ROBOT-001':'33ff47a7627a4ac72740e494f9e4705e7eb31587890dad2a7b9f34a75ded8e5d',
    'SEM-ACT-TACTICAL-001':'1821c405707f323cfe69251b3bb2bd3c27ac615ba828dbc6c2f2277dd410c7b3',
    'SEM-ROBOT-EXPLORATION-001':'e970129e3eb71ba8ad3d19f8aafa0d6a66d25f3d7891cc6d83c63aa35e2aeeca',
    'SEM-ROBOT-MALFUNCTION-001':'9be79b5b00465585133f5b98bbdea70bb6fa8d1465d224c1f379308b75922e75',
    'SEM-ROBOT-MALFUNCTION-PLACEMENT-001':'5c7cb67aa0bd467409ec713302b3067f4caae14cc03d5c8d4438f77a6352cb62',
    'SEM-ROBOT-MEDICAL-001':'dda3cc6eb577d80c81237ce090041a72b6c1fe406a7a412c4677564bfb4be697',
    'SEM-ROBOT-MILITARY-001':'0871a479ab66e1a91db61c2b87fdd1c158ba2e5a3af6387578bb1683d78ee461',
    'SEM-ROBOT-MOVEMENT-001':'bd4067f3ba534f45eb190b99a89e7f49b2ac84da007ba8427656386abf91773b',
    'SEM-ROBOT-REVEAL-001':'42c86df72e194a4fa9756e368ae601957d621d7ffbd29382e94bf4fdf53395f4',
    'SEM-ROBOT-SECURING-001':'12f70d443d36d6c70baca7963e844bc8294c9f6b26dde38d4c418f27d940924a',
    'SEM-ROBOT-SERVER-001':'988fea5c5495daa519ba7a21ba4bf36b2d0ef2a229fd153612f80608d5228114',
    'SEM-ROBOT-SETUP-001':'f54d0fea3120855aefcccc96bd2b224ef65537368fa3eb664abfb812e8774a9c',
    'SEM-ROBOT-TACTICAL-GEAR-001':'ede891a4cb8ab75989d0ba9f331487df49e39dc324f44e472449b2bc0c45c972',
    'SEM-ROBOT-TECHNICAL-001':'fbd73f3be0af16f3ec41af5ece34b4829a47eee66ff9020fcb0c5ec18c2a07e3',
}
EXPECTED_ATTACK_COUNTS = {
    'attackOccurrences':20,'uniquePrintedTitles':8,'generatedFaceOccurrences':19,'directFaceOccurrences':1,
    'generatedSourceSheetCells':20,'selectedGeneratedCells':19,'excludedSelectorGaps':1,
    'sharedBackOccurrences':1,'sharedBackSelectorReferences':21,'sourceSheets':1,
    'canonicalCorpusFaces':1,'sourceBoundDraftFaces':19,'physicalPanels':69,'operativePanels':29,
    'printedSentences':54,'applicabilityBadgeOccurrences':57,'inlineIconOccurrences':13,
    'functionalSymbolOccurrences':70,'selectedEvidenceNoMatchOccurrences':55,
    'selectedEvidenceMatchedOccurrences':14,'licensedStructuredVariants':15,'licensedFaceLinks':20,
    'officialVisibleFaceCounterparts':3,'officialVisibleBackCounterparts':1,'officialFaceLinks':8,
    'officialRulebookTextOccurrences':9,'officialRulebookVisualObligations':2,'faqOccurrences':3,
    'excludedExpansionAttackDecks':3,'excludedUnusedGeneratedFaces':1,'backlogTuples':20,
    'backlogObligationsLinked':28,
}
EXPECTED_ATTACK_OCCURRENCES = {
    394900: ('SRC-ATTACK-394900','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-00.png','72e8782d5b98ee1d46045a4efd6c47dec40ec9aa552a3f44c894da0fdb6a2fb8','5afea3',0,'IntruderAttack_Bite','SEM-ATTACK-394900-001','BITE',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,(),('RB-P03-V01-ATTACK-BITE',),('SEM-Q-021',)),
    394901: ('SRC-ATTACK-394901','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-01.png','0ba1a8b7b73127a004bba592c091924ec985eef51eaecf85adb2282593983832','f59fca',1,'IntruderAttack_Bite','SEM-ATTACK-394901-001','BITE',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,(),('RB-P03-V01-ATTACK-BITE',),('SEM-Q-021',)),
    394902: ('SRC-ATTACK-394902','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-02.png','088924b9742db513130b51fd8750cf80ab95fd3a0f33f150287b33fcf82fe501','ca7eaf',2,'IntruderAttack_Bite','SEM-ATTACK-394902-001','BITE',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,(),('RB-P03-V01-ATTACK-BITE',),('SEM-Q-021',)),
    394903: ('SRC-ATTACK-394903','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-03.png','9c988ba455dd17dfa1dc34eb2fb26cfebb6c17c9f21cb6a60af473ca0c441afc','d4547c',3,'IntruderAttack_Bite','SEM-ATTACK-394903-001','BITE',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,(),('RB-P03-V01-ATTACK-BITE',),('SEM-Q-021',)),
    394904: ('SRC-ATTACK-394904','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-04.png','881d97fc90030383652122b2108825aea2a4b8adc610e3cee9f7c22632d12720','5e9926',4,'IntruderAttack_Bite','SEM-ATTACK-394904-001','BITE',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,(),('RB-P03-V01-ATTACK-BITE',),('SEM-Q-021',)),
    394905: ('SRC-ATTACK-394905','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-05.png','c551ca1229e55b435145ef80bf5dccc3f54e293d3a1d8edd765582fd273813ab','d98fc8',5,'IntruderAttack_Bite','SEM-ATTACK-394905-001','BITE',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,(),('RB-P03-V01-ATTACK-BITE',),('SEM-Q-021',)),
    394906: ('SRC-ATTACK-394906','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-06.png','b732ca40c7c54b4c85901c16fab368a614b278c651079135fcec192a13bccf39','aa3f4a',6,'IntruderAttack_DeadlyClaws1','SEM-ATTACK-394906-001','DEADLY CLAWS',('Adult','Drone','Queen'),('P3','P3','P4'),4,4,('icon.characterHealth',),(),('SEM-Q-021','SEM-Q-023')),
    394907: ('SRC-ATTACK-394907','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-07.png','8299612f643cc485002f3680abe8e65a581dfff1fa6895fa7368aefce9010234','58a1fa',7,'IntruderAttack_DeadlyClaws2','SEM-ATTACK-394907-001','DEADLY CLAWS',('Adult','Drone','Queen'),('P3','P3','P4'),4,5,('icon.characterHealth',),('RB-P03-V01-ATTACK-DEADLY-CLAWS',),('SEM-Q-021','SEM-Q-023')),
    394908: ('SRC-ATTACK-394908','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-08.png','29ce4c3b52ac34cd53ecaa67482df6356507eda0e168c8bb840c3af2a0ded2c3','2bc4ac',8,'IntruderAttack_DeadlyClaws3','SEM-ATTACK-394908-001','DEADLY CLAWS',('Adult','Drone','Queen'),('P3','P3','P4'),4,4,('icon.characterHealth',),(),('SEM-Q-021','SEM-Q-023')),
    394909: ('SRC-ATTACK-394909','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-09.png','11d94012916309b1d4d770012d59c8dc3ac81196826dc2cce3aab56339a1818e','a58129',9,'IntruderAttack_Fury1','SEM-ATTACK-394909-001','FURY',('Adult','Queen','Drone'),('P3','P4','P4'),4,4,('icon.characterHealth',),(),('SEM-Q-020','SEM-Q-021')),
    394910: ('SRC-ATTACK-394910','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-10.png','15e1e762d38794914d42a2a9bf1d16e8db88ce195099faff043ad4aa25bd0dc0','d78969',10,'IntruderAttack_Fury2','SEM-ATTACK-394910-001','FURY',('Adult','Queen','Drone'),('P3','P4','P4'),4,4,('icon.characterHealth',),(),('SEM-Q-020','SEM-Q-021')),
    394911: ('SRC-ATTACK-394911','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-11.png','73e6cec9de20bcc116f70de3dc46df16671a77bac9e02d1145061d8068d517f3','f8df5b',11,'IntruderAttack_Infecting','SEM-ATTACK-394911-001','INFECTING',('Adult','Queen','Drone'),('P3','P3','P4'),4,3,('icon.characterHealth',),('RB-P32-V01-ATTACK-INFECTING',),()),
    394912: ('SRC-ATTACK-394912','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-12.png','c4e671e3504c36647e657f1e2fbe1ba12bda9e4998fa763beed24b70bd4fce60','0959a7',12,'IntruderAttack_Miss','SEM-ATTACK-394912-001','MISS',(),(),3,2,(),(),('SEM-Q-024',)),
    394913: ('SRC-ATTACK-394913','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-13.png','e23333f920163dc0a9342ef6d348855b0dbb3e2b7a769ec735e3d4460c2d89cf','e8555f',13,'IntruderAttack_Scratch1','SEM-ATTACK-394913-001','SCRATCH',('Adult','Queen','Drone'),('P3','P3','P3'),3,1,(),(),()),
    394914: ('SRC-ATTACK-394914','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-14.png','241bd0d208b745a41e9ee671e55138b71669ef12b3bf8b1086922f85fc126963','09613e',14,'IntruderAttack_Scratch2','SEM-ATTACK-394914-001','SCRATCH',('Adult','Queen','Drone'),('P3','P3','P3'),3,2,('icon.characterHealth',),(),('SEM-Q-021',)),
    394915: ('SRC-ATTACK-394915','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-15.png','20ced3626bd007e388acda4ccc96dfcd59e72bcf3cf7ae84ad1693e5ba0a924d','e7be5a',15,'IntruderAttack_Scratch3','SEM-ATTACK-394915-001','SCRATCH',('Adult','Queen','Drone'),('P3','P3','P3'),3,1,('icon.characterHealth',),(),()),
    394916: ('SRC-ATTACK-394916','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-16.png','eb422e05e6ec47d486f08c873f4fd1c5427e79904f16fab88a140bd46a390e6a','b9afbe',16,'IntruderAttack_Scratch4','SEM-ATTACK-394916-001','SCRATCH',('Adult','Queen','Drone'),('P3','P3','P3'),3,1,('icon.characterHealth',),(),()),
    394918: ('SRC-ATTACK-394918','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-18.png','a5d496cfe387ac69a361b62b659047238d348f4db329583a6d3f5b562d0fbce3','f08b5b',18,'IntruderAttack_TailAttack1','SEM-ATTACK-394918-001','TAIL ATTACK',('Adult','Queen','Drone'),('P3','P3','P4'),4,3,(),(),('SEM-Q-021',)),
    394919: ('SRC-ATTACK-394919','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-19.png','8a8f393e64f6f0d5d1bf569afbff6b1737615c269b09f5e3bd11711f7e396e16','6caa45',19,'IntruderAttack_TailAttack2','SEM-ATTACK-394919-001','TAIL ATTACK',('Adult','Queen','Drone'),('P3','P3','P4'),4,4,('icon.characterHealth',),(),('SEM-Q-021',)),
    399100: ('SRC-ATTACK-399100','assets/tts-mod/extract/v2-dl/tree/cards/game/attack-022.png','8f188df6aa3b9fa96531894f49b9727ce79558e11023fba10d8758af3400319b','50e156',None,'IntruderAttack_BloodSense','SEM-ATTACK-399100-001','BLOOD SENSE',('Adult','Drone','Queen'),('P3','P4','P4'),4,4,('icon.characterHealth','icon.characterHealth','icon.intruder'),(),('SEM-Q-022',)),
}
EXPECTED_ATTACK_BODY_DIGESTS = {
    394900:'d9915a0bd1f2bbae48771a1fc26bb067bc82011e16ce6ccfa55a008f03de360d',394901:'d9915a0bd1f2bbae48771a1fc26bb067bc82011e16ce6ccfa55a008f03de360d',394902:'d9915a0bd1f2bbae48771a1fc26bb067bc82011e16ce6ccfa55a008f03de360d',394903:'d9915a0bd1f2bbae48771a1fc26bb067bc82011e16ce6ccfa55a008f03de360d',394904:'d9915a0bd1f2bbae48771a1fc26bb067bc82011e16ce6ccfa55a008f03de360d',394905:'d9915a0bd1f2bbae48771a1fc26bb067bc82011e16ce6ccfa55a008f03de360d',
    394906:'a5c001325a3906c92ffa722352f554597e6074c510ed08cc83cc74fc2cf449a8',394907:'7b2e2fac83924c93533fa2b5bd975b109571615061b76c0a16096261405273b7',394908:'ca35f3e8bfbc5d3b73ffb97eaa82816301dd9b673f20f1f38516802c329b3aef',394909:'b713d4ee27d392cf576fc8b523197fff7c25f4d3999b05dc9207fb23286cb638',394910:'4d6d15bc9b95103d5727e739854b8e30a7e7b9f042b384886ca71e641cd79cbd',394911:'2da2600e3cbf971de3c3dcb7476601d43f9d78c1f8d272fe9308945c99397f52',394912:'54b0477e15ecc4d06de4b20310bc47ec5fd4dc7ff41870c1c1ae9eff369bc67e',394913:'9c421286599daf6cb972b591f5bc44d1420016cd2afb1328438487821cc125f5',394914:'b2d7ab5df3935cad699abcdb6b5fc91ba8e46b223a023e560b0a3d7af3db940d',394915:'fd2b0b78ad1d80f5fc57322568cb70158a2a623911a3eaabb4ac5330f9020413',394916:'82545fc67a91744372c21f531f67f8f067ba359585d177c94713da0ff3c9e029',394918:'4dde86319aaefb9b84a8866db7e72648bb726b3e7ad7158ec13ccb38df739e18',394919:'c4437d99cfd8a11136c72f1bc66bec6fb5da0fa34caee4cb1ab4008d0c4f30e4',399100:'24f5851fe754c14d55fa6751c8c68b74c6a3f32ef61fdc4981729c274b7d2283',
}
EXPECTED_ATTACK_RECORD_DIGESTS = {
    'SEM-ATTACK-394900-001':'b363d61ef96b239f83e04bc00867d2943a7da868438484d802bfd54b5d888c84','SEM-ATTACK-394901-001':'cb09dbe29c77e9655279b52c6061f46013da0b1686c779b49363038be067275c','SEM-ATTACK-394902-001':'fbe74107fd5766b9812c7d78f9729c2a5c2b12bebdb82b3c5bd216ebf7de9fe1','SEM-ATTACK-394903-001':'ecfc2a2e4f1ab416634a3cebe988bb82903f48c91d4745f0445e2be65bf871f4','SEM-ATTACK-394904-001':'0fda12666d53361403fd60e597a812784b17f2fb9f7ca1725e1463d42a595dc2','SEM-ATTACK-394905-001':'a4a2b485e8ca2ae13481ec799f986e1d78ce6abe1702664086b2df7eb55681ce','SEM-ATTACK-394906-001':'363be26edf170bc7df8344817fbe313a4df63aeb06d8c6307b9b04b0a09b250c','SEM-ATTACK-394907-001':'d00202c7f465423b10f943791aa5bb62245701348345cf3701debbdfbde89d10','SEM-ATTACK-394908-001':'28c7d244ecdc45f0624c1a0a43085e4de732a11b13cb6279fd25350ea32099d6','SEM-ATTACK-394909-001':'4564b6f6b6e9a5b1e2d7e860cd4254e055689f02038d2d70a2951e11aa35441b','SEM-ATTACK-394910-001':'360814f4b3f7df57e3c00c683349a2b7204a48e2f6e4e0a0092f3d5e1ae03018','SEM-ATTACK-394911-001':'566f1d1b2ddc77b08dc741a300d8596c0f90238636d830ecc591a5e06fb6d335','SEM-ATTACK-394912-001':'f23f2616dfd0894cad070e8910f1c1c7a6011f61dd6c856041f413a84e5fdbc6','SEM-ATTACK-394913-001':'82f959a00970278f4d0e40f9769d849eceee6cfc695e06eef631dc7049b9a996','SEM-ATTACK-394914-001':'2077903a59bd34a3c7d47fdc771436be117df0f9d403e464556f5c9e8bad4a19','SEM-ATTACK-394915-001':'cffaac76cb2054586bbdfa93c2ef97e973d0d599d8922dcdaf6709e902ce1630','SEM-ATTACK-394916-001':'881b144695663b5d3e0b061517a42973b0f232d06a2df03de68a450b733628df','SEM-ATTACK-394918-001':'7e9050f736b63d7fd5c5336160fc2c4ff3cb2a6ccfad70396b8226198ac3697f','SEM-ATTACK-394919-001':'39a77c3ee127e0c3eb77a1aa0e8c4d38c29fe1f069eb32c712eb05831ad5d80b','SEM-ATTACK-399100-001':'603b47857c36fb72e6e48b244d0cb879286b105c4944fe2204322aa4ba4fd369','SEM-CONTAMINATION-GAIN-001':'de8256656ec5d3d98079726883c49e0753e9f48b469445b6db6a1fb47a763638','SEM-INT-004':'fef1c6058aaab9a28794e2d89486cb88d52f279ae686f4e77a588b7879a7b0b9',
}
EXPECTED_QUEEN_HEALTH_COUNTS = {
    'physicalFaceOccurrences':12,'uniqueFaceAssets':10,'uniqueFullCardIds':11,'uniqueCardGuids':12,
    'rootCustomDeckEntries':11,'rootUniqueFaceUrls':10,'directFaceOccurrences':12,'generatedFaceOccurrences':0,
    'sourceSheets':0,'selectorGaps':0,'sharedBackOccurrences':1,'sharedBackSelectorReferences':13,
    'canonicalCorpusAssets':1,'sourceBoundDraftAssets':9,'physicalPanels':24,'operativePanels':24,
    'printedSentences':37,'localNumberDisplayOccurrences':12,'page40MatchedIconOccurrences':16,
    'functionalIconOccurrences':28,'uniqueAssetFunctionalIconOccurrences':24,
    'selectedEvidenceNoMatchAssetOccurrences':9,'canonicalLocalUnregisteredAssetOccurrences':1,
    'characterIconOccurrences':14,'actionCardIconOccurrences':1,'malfunctionIconOccurrences':1,
    'queenIconOccurrences':0,'damageIconOccurrences':0,'burstIconOccurrences':0,'healthIconOccurrences':0,
    'licensedDigitalOccurrences':12,'licensedPlaceholderOccurrences':4,'licensedCandidateLinks':16,
    'officialVisibleFaceOccurrences':3,'officialVisibleBackOccurrences':2,'officialQueenHitsTrackSpaces':6,
    'officialTrackTerminalLocalSymbolOccurrences':2,'officialRulebookTextOccurrences':17,
    'officialRulebookVisualObligations':4,'faqOccurrences':1,'objectiveHelpOccurrences':2,
    'excludedExpansionQueenHealthDecks':3,'excludedPrototypeFaces':0,'excludedPlaceholderFaces':0,
    'excludedParentSheets':0,'excludedBaseAttackOccurrencesWithQueenApplicability':20,
    'backlogTuples':10,'backlogPhysicalFaceLinks':12,'backlogObligationsLinked':25,
}
EXPECTED_QUEEN_HEALTH_OCCURRENCES = {
    'TTS-QUEEN-HEALTH-424300-615E22-FACE': {'sequence':1,'cardId':424300,'guid':'615e22','customDeckId':'4243','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-039.png','sha256':'648b81223c8c8b65b96a4304645bfe738f2ca64ecf989c0a826111d6bf6bd506','discard':0,'bgaKeys':['QueenHealthCard1'],'ruleId':'SEM-QUEEN-HEALTH-424300-615E22-001','sentences':3,'iconRefs':[None,'icon.character'],'official':['RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL'],'bodyDigest':'0288196e016568e20f154986e3e7acea89c435985dbeee6b1a1ffa482294c78e'},
    'TTS-QUEEN-HEALTH-424500-0DD25F-FACE': {'sequence':2,'cardId':424500,'guid':'0dd25f','customDeckId':'4245','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-040.png','sha256':'ce7a5fba88dd56f5de2ae77e5fe1647324bdfa9a99ae7f55485cca35eb72b062','discard':0,'bgaKeys':['QueenHealthCard3'],'ruleId':'SEM-QUEEN-HEALTH-424500-0DD25F-001','sentences':3,'iconRefs':[None,'icon.character'],'official':['RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL'],'bodyDigest':'26fa14dfae12d957d2a584730ecabb25404294f5d90a838078ef9a0b12acda18'},
    'TTS-QUEEN-HEALTH-503700-E4AB1C-FACE': {'sequence':3,'cardId':503700,'guid':'e4ab1c','customDeckId':'5037','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-013.png','sha256':'5ad0606dff59c21b20689fc6b5b5192ef83c95f108ded91e587725bfd2c68092','discard':0,'bgaKeys':['QueenHealthCard2'],'ruleId':'SEM-QUEEN-HEALTH-503700-E4AB1C-001','sentences':3,'iconRefs':[None,'icon.character'],'official':['RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL'],'bodyDigest':'f6bf9085284274c926b9b0a8ed0477d3ab32ceed39ab7c37c04d432829bbfd31'},
    'TTS-QUEEN-HEALTH-504100-717B23-FACE': {'sequence':4,'cardId':504100,'guid':'717b23','customDeckId':'5041','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-084.png','sha256':'bcb0eeb9e86f66f8401b584385746d268641c2692392b3faeb4f93438111a62f','discard':1,'bgaKeys':['QueenHealthCard4','QueenHealthCard5'],'ruleId':'SEM-QUEEN-HEALTH-504100-717B23-001','sentences':3,'iconRefs':[None,'icon.character'],'official':['RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL','RB-P35-V02-QH-FACE-DISCARD-1-REPEL'],'bodyDigest':'69f900f3e0fc4b4058cf40269333d88e03db41169652709fd7cd17ceb3ae3e07'},
    'TTS-QUEEN-HEALTH-504200-CA5827-FACE': {'sequence':5,'cardId':504200,'guid':'ca5827','customDeckId':'5042','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-084.png','sha256':'bcb0eeb9e86f66f8401b584385746d268641c2692392b3faeb4f93438111a62f','discard':1,'bgaKeys':['QueenHealthCard4','QueenHealthCard5'],'ruleId':'SEM-QUEEN-HEALTH-504200-CA5827-001','sentences':3,'iconRefs':[None,'icon.character'],'official':['RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL','RB-P35-V02-QH-FACE-DISCARD-1-REPEL'],'bodyDigest':'69f900f3e0fc4b4058cf40269333d88e03db41169652709fd7cd17ceb3ae3e07'},
    'TTS-QUEEN-HEALTH-504000-919263-FACE': {'sequence':6,'cardId':504000,'guid':'919263','customDeckId':'5040','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-126.png','sha256':'63654c6409f88599aff333b6a54e90b3c3aaa7a29f2395ffff36eed7ab2d6e49','discard':1,'bgaKeys':['QueenHealthCard6'],'ruleId':'SEM-QUEEN-HEALTH-504000-919263-001','sentences':3,'iconRefs':[None,'icon.character'],'official':['RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL'],'bodyDigest':'49d95c5cb4a5d6acb37f2628963db3defb35086c3cf47b25dfedb0ebe21e2e4f'},
    'TTS-QUEEN-HEALTH-503900-B42831-FACE': {'sequence':7,'cardId':503900,'guid':'b42831','customDeckId':'5039','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-164.png','sha256':'4a79f992bc3e6b7493887c40b1198785673cc87ce462bbdd732b02c8e6a3cf14','discard':1,'bgaKeys':['QueenHealthCard7'],'ruleId':'SEM-QUEEN-HEALTH-503900-B42831-001','sentences':3,'iconRefs':[None,'icon.character','icon.character','icon.actionCard'],'official':['RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL'],'bodyDigest':'381827a4ef54b37b0be97c0341895699030a23d5fadd9b06c08059db46f26f7f'},
    'TTS-QUEEN-HEALTH-503800-64AE0A-FACE': {'sequence':8,'cardId':503800,'guid':'64ae0a','customDeckId':'5038','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-165.png','sha256':'763ca108996c746f141b6f505d3afee2c30be1f6f4f38b84d0118f9f76bdf765','discard':2,'bgaKeys':['QueenHealthCard9'],'ruleId':'SEM-QUEEN-HEALTH-503800-64AE0A-001','sentences':3,'iconRefs':[None,'icon.character','icon.character'],'official':[],'bodyDigest':'8a0db6dba05b54944a20e757cefd7676da2ae51ad265994c4a83fc5a36245a72'},
    'TTS-QUEEN-HEALTH-424100-A10F34-FACE': {'sequence':9,'cardId':424100,'guid':'a10f34','customDeckId':'4241','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-038.png','sha256':'fc04bf1a2920fb63ac512d209622b591cdc9f3cb9ca292c97bf874fcddbbd5c8','discard':2,'bgaKeys':['QueenHealthCard8'],'ruleId':'SEM-QUEEN-HEALTH-424100-A10F34-001','sentences':3,'iconRefs':[None,'icon.character'],'official':[],'bodyDigest':'dbfd5460f3068cd37d6b23a2de37ed5a5369e5859454bf1ea9543bb175f6dd5f'},
    'TTS-QUEEN-HEALTH-458100-6BA0A2-FACE': {'sequence':10,'cardId':458100,'guid':'6ba0a2','customDeckId':'4581','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-041.png','sha256':'929ac1204b4b7989ee051307245bf32fb5e1915a35b9afd5a73572c8ca01dc61','discard':3,'bgaKeys':['QueenHealthCard12'],'ruleId':'SEM-QUEEN-HEALTH-458100-6BA0A2-001','sentences':4,'iconRefs':[None,'icon.character','icon.malfunction'],'official':[],'bodyDigest':'153d49c08790ab6ef75121483b876ac1be7c848fb44216f7dca7dcf2edd772be'},
    'TTS-QUEEN-HEALTH-429200-48A2AE-FACE': {'sequence':11,'cardId':429200,'guid':'48a2ae','customDeckId':'4292','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-045.png','sha256':'133a975dc072a169ceed85615ab2e5a6cde0f80a23f18e61948f0a963c9e98e2','discard':3,'bgaKeys':['QueenHealthCard10','QueenHealthCard11'],'ruleId':'SEM-QUEEN-HEALTH-429200-48A2AE-001','sentences':3,'iconRefs':[None,'icon.character'],'official':[],'bodyDigest':'94eb3ec782f5d5851e0f927584b156e3304cd140b6954c5904ee71ac8ef74d06'},
    'TTS-QUEEN-HEALTH-429200-0FBF8D-FACE': {'sequence':12,'cardId':429200,'guid':'0fbf8d','customDeckId':'4292','path':'assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-045.png','sha256':'133a975dc072a169ceed85615ab2e5a6cde0f80a23f18e61948f0a963c9e98e2','discard':3,'bgaKeys':['QueenHealthCard10','QueenHealthCard11'],'ruleId':'SEM-QUEEN-HEALTH-429200-0FBF8D-001','sentences':3,'iconRefs':[None,'icon.character'],'official':[],'bodyDigest':'94eb3ec782f5d5851e0f927584b156e3304cd140b6954c5904ee71ac8ef74d06'},
}
EXPECTED_QUEEN_HEALTH_RECORD_DIGESTS = {
    'SEM-ACT-BURST-001':'259ea7a58a2f41d7fc9b04462e90a46e18d506cbb1d8cc79aaeab3fd07ebb21c',
    'SEM-ACT-SHOOT-001':'8015e439e91a95ba4223aacb33dbe3f453c2d5eb3317bb14ed32d7d42e3bdffe',
    'SEM-ACTION-CARD-DRAW-001':'d2ae2c3748ab7871a96659fc3818378ba1ebbdd5dc62c8a045d564b0a60ffdc4',
    'SEM-INTRUDER-REPEL-001':'5c030ed830b2d16b44fc662b223cca11f4f35ac443774b77f5607a83905bff8a',
    'SEM-QUEEN-ACTIVATION-001':'7d1f7fed31ee55757d6e840517aad0d651c0b120aaea37cba221d166a3a62dc6',
    'SEM-QUEEN-DEATH-001':'d2c72f0b6f49e04ce0419e43f5095bffbbca4166ce4ce021c856512042d4615e',
    'SEM-QUEEN-HEALTH-424100-A10F34-001':'b8a649795d83e4a5b81ea8f3d2b652b6ea6353f32794f39702fa4ee499a401dd',
    'SEM-QUEEN-HEALTH-424300-615E22-001':'952e3ee3c4d4361a9420dbac92635788a960db64d50ac6ab3fa0a7305ea3df9f',
    'SEM-QUEEN-HEALTH-424500-0DD25F-001':'d689da7b8918a0be98fd5956a64f4ed16610e818be28222e102a362b52a609b9',
    'SEM-QUEEN-HEALTH-429200-0FBF8D-001':'c1dd57714569d92ca5c92cab480daa7cc10c7c7940e06a10e1ffd3380cf48a05',
    'SEM-QUEEN-HEALTH-429200-48A2AE-001':'abd661d7ba0b62b50b21261706249c6174a807bbdd5067515037ef6246e8c865',
    'SEM-QUEEN-HEALTH-458100-6BA0A2-001':'b08dcd1658cccdc474396248d92bc20cf573f5c833b2aec859b132ff6eb54428',
    'SEM-QUEEN-HEALTH-503700-E4AB1C-001':'32dc716f9b167d1d12be8c72ba1ff9de856881c86c07f7b8c1774b40510c3285',
    'SEM-QUEEN-HEALTH-503800-64AE0A-001':'a3c851bbcc7b624e891cbcca6eda623d89286e01a86944a6f7221dfe8245a928',
    'SEM-QUEEN-HEALTH-503900-B42831-001':'c44df0a5d1c8824e0301014382199b2947d275cae04cacfcbd7b14330a821fcc',
    'SEM-QUEEN-HEALTH-504000-919263-001':'815993f106b52a673a9221af7013b56f6fb6b5064cbdf36e2bfde060d742187d',
    'SEM-QUEEN-HEALTH-504100-717B23-001':'945272162c3a11f63a33168429db5fc055bc3f61828de6956e0c2e37e4300bee',
    'SEM-QUEEN-HEALTH-504200-CA5827-001':'a0320ea77d122ab1e48ae7b1eeab170e44e1f03344e870441e7ed81a3c1764bc',
    'SEM-QUEEN-HEALTH-RESOLUTION-001':'e9f735aabe7706010cb14b2f390b282bb3d3579893e44a70c6ecf51cb80c6a39',
    'SEM-QUEEN-HEALTH-SETUP-001':'261da0b12938b8d328fe65c58dfca82b85bc47754e52f5fb2049f19b777dc4cb',
    'SEM-QUEEN-HIT-001':'372acf3d0fff4555ba5de4a1e06d46b1dd9b038cc936b7818357ef55183ec60a',
    'SEM-ROOM-MALFUNCTION-PLACEMENT-001':'c2954c90e774324267041aba20fa1938e2b28d26118215866048c5242eea8676',
}
EXPECTED_SERIOUS_WOUND_COUNTS = {
    'physicalFaceOccurrences':27,'uniquePrintedTitles':9,'uniqueSelectedFaceAssets':9,'sourceFaceAssets':11,
    'generatedPhysicalFaceOccurrences':21,'directPhysicalFaceOccurrences':6,'sourceSheets':1,'sourceSheetCells':9,
    'selectedGeneratedCells':7,'selectorGapCells':2,'sharedBackOccurrences':1,'sharedBackSelectorReferences':28,
    'sourceSheetSelectorReferences':22,'rootCustomDeckEntries':3,'physicalRegions':81,'operativeRegions':27,
    'physicalPanels':54,'operativePanels':27,
    'headingRegionOccurrences':27,'artworkInterfaceRegionOccurrences':27,'sourceAssetRegions':33,
    'sourceAssetPanels':22,
    'printedSentenceOccurrences':42,'sourceAssetSentenceOccurrences':16,'physicalFunctionalIconOccurrences':30,
    'physicalMatchedIconOccurrences':24,'physicalUnresolvedLocalGlyphOccurrences':6,
    'selectedAssetFunctionalIconOccurrences':10,'allSourceAssetFunctionalIconOccurrences':15,
    'allSourceAssetMatchedIconOccurrences':13,'allSourceAssetUnresolvedLocalGlyphOccurrences':2,
    'literalAnatomyOrRegionHeadingOccurrences':24,'literalConditionHeadingOccurrences':3,
    'licensedDigitalOccurrences':9,'licensedPlaceholderOccurrences':10,'licensedPhysicalIdentityLinks':0,
    'officialVisibleFaceOccurrences':3,'officialVisibleBackOccurrences':2,'officialRulebookTextOccurrences':7,
    'officialRulebookVisualObligations':7,'baseApplicableFaqOccurrences':0,'excludedExpansionFaqOccurrences':1,
    'excludedExpansionSeriousWoundDecks':0,'excludedWoundLikeExpansionComponents':1,
    'excludedParentSheetsFromFaceCount':1,'excludedBacksFromFaceCount':1,'excludedNonRulesOverlayClasses':4,
    'backlogTuples':11,'backlogPhysicalFaceLinks':27,'backlogObligationsLinked':26,'semanticPhysicalFaceRecords':27,
}
EXPECTED_SERIOUS_WOUND_ASSETS = {
    'sheet-00':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-00.png','66db7a2fc44c3a8e278b2b7fd0ae40d3932f26667b568ad3b3271b6373f80998','EYES','generated-cell-face',0,1,(), 'e7ce41d2079b7a475fb779b51db1ace1749dcf9bd45ac4683e6810e31335ddc7'),
    'sheet-01':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-01.png','42980fa5cef70e8ed40649d1495fc75c015c43f60ebb52961031d18f8f3e1564','LUNGS','generated-cell-face',1,3,('icon.oxygen','icon.lifeSupportActive','icon.oxygen',None), '27539ae22f639285a0306eace391a7b3fee5269b01fd50b81951b7c5eeeb1de7'),
    'sheet-02':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-02.png','e6ec34b2dde06f1cd76e958af3d24ee1bcc4fa177e4d214b086c70d82a8a2322','HAND','generated-cell-face',2,1,('icon.actionCard',), 'dff61b53d4d009117bbfd5b0a40f39d8f07e5716fb6c20ec56d768db4f834faa'),
    'sheet-03':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-03.png','322587af9825baec2c8786a0f5e15a657257a5633f025e694de2c962127b44f9','ARM','generated-cell-face',3,2,(), '0df3e6bdc14e09e31d507662542e8f9422087cea24f5760172c46cbb51350f5d'),
    'sheet-04':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-04.png','522c29d0874334cac9dda75c4cd0182fca35dbc7402c4b7231c1c8a6c6b1ec18','LEG','generated-cell-selector-gap-variant',4,1,('icon.intruder','icon.intruder','icon.actionCard'), '3c621db2074915f41e391377be083fd71ca711bbcaac41d139badb3c0ad3045d'),
    'sheet-05':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-05.png','69fa0f09363ab35f1e547a60e64e1b011702a7469755835bf002e0739b0a33f2','BODY','generated-cell-face',5,1,(), 'cd2765d919768c748014bedb4d4abf1a273c196b5ae2fd3651821554b678c842'),
    'sheet-06':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-06.png','1027d7f87a80b4a7d32eb40e9d336c9557c032a33ab6fdc08912a5beeb3e2dcb','KNEE','generated-cell-selector-gap-variant',6,1,('icon.secure','icon.actionCard'), '405e10bcc3c42e65d9f6578e1bee44d9702b433e138a6e19e4ff44cb040efe74'),
    'sheet-07':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-07.png','b485840032e9abcaeec0bf614e7df0e5487aa52d43005615eeb6950aed44f09f','GUTS','generated-cell-face',7,2,(), '8ffcd528173e1cc40ce3f8dadab03f290195ce46222811e483aa7beee94cc9bd'),
    'sheet-08':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-08.png','2316dd24439f588422fce16da610e59e2609973f968bf0cb7dfb18b8d8f21f40','BLEEDING','generated-cell-face',8,2,('icon.characterHealth',), 'd3152cc568e31e0fdc8ba740c1587fd84810949fc1c20abce7b0afa3981e689d'),
    'direct-4048':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-028.png','cfc93364f9ec257e07bc84989bbea9709ecdc9519d11f2bc7fd4c5b519ab3f6f','KNEE','direct-face',None,1,(None,'icon.actionCard'), '56ea72605d52330ba3458f31e226408d06c95085fda6849d380b916c4db344ac'),
    'direct-5439':('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-104.png','a8e96bccf2270724b257a20bcc55e24c2e78a161f8bb5ae6256f433c82ecd4e7','LEG','direct-face',None,1,('icon.intruder','icon.actionCard'), 'baf1a62980591ff1822b1b63fd040ea88048192f14ac76a8aea5fb2640b2a6cd'),
}
EXPECTED_SERIOUS_WOUND_GROUPS = [
    (3800,'sheet-00',['ee102c','c85059','213ca0']),
    (3807,'sheet-07',['89f2f0','4d4710','655132']),
    (3808,'sheet-08',['55f79e','68a1cf','928c60']),
    (3801,'sheet-01',['6466b5','17ccb1','5444e8']),
    (3805,'sheet-05',['351aa8','6175a8','74c9b5']),
    (404800,'direct-4048',['fd77b5','1642c4','a0a4f8']),
    (3802,'sheet-02',['ad7826','2202b4','06be60']),
    (543900,'direct-5439',['03d258','864d90','dbca72']),
    (3803,'sheet-03',['aa0b48','235eb5','6564cb']),
]
EXPECTED_SERIOUS_WOUND_OCCURRENCES = {}
_serious_wound_sequence = 1
for _card_id, _asset_key, _guids in EXPECTED_SERIOUS_WOUND_GROUPS:
    _asset_path,_asset_sha,_title,_source_role,_cell,_sentences,_icon_refs,_body_digest = EXPECTED_SERIOUS_WOUND_ASSETS[_asset_key]
    _custom_deck_id = '4048' if _asset_key == 'direct-4048' else '5439' if _asset_key == 'direct-5439' else '38'
    for _guid in _guids:
        _code = f'{_card_id}-{_guid.upper()}'
        EXPECTED_SERIOUS_WOUND_OCCURRENCES[f'TTS-SERIOUS-WOUND-{_code}-FACE'] = {
            'sequence':_serious_wound_sequence,'cardId':_card_id,'guid':_guid,'customDeckId':_custom_deck_id,
            'path':_asset_path,'sha256':_asset_sha,'title':_title,'sourceRole':_source_role,'cell':_cell,
            'ruleId':f'SEM-SERIOUS-WOUND-{_code}-001','sentences':_sentences,'iconRefs':list(_icon_refs),'bodyDigest':_body_digest,
        }
        _serious_wound_sequence += 1
EXPECTED_SERIOUS_WOUND_RECORD_DIGESTS = {
    'SEM-SERIOUS-WOUND-3800-213CA0-001':'e1cad3aac2dcaa47b0a6e104f8a9c54800ac80d8ac860509a8c9b7f81e9aa2f4',
    'SEM-SERIOUS-WOUND-3800-C85059-001':'298b286ca4236819635ef6d11c5bb9b5474307a9619a08beee4b7cff00104808',
    'SEM-SERIOUS-WOUND-3800-EE102C-001':'561b418c5b7e8b953be38f42155947a691a1d175604e4925e336fec144cd7adf',
    'SEM-SERIOUS-WOUND-3801-17CCB1-001':'37ce02dda8236a62112df782e402b32a1d00d2acd490c91c1d23dd34a500c615',
    'SEM-SERIOUS-WOUND-3801-5444E8-001':'59c16ffaed771c6bbc16052890053d245225a74954c5fe1c2f8121d8f756fa2f',
    'SEM-SERIOUS-WOUND-3801-6466B5-001':'c952ca5de7e2c6c13a5287c953614c46532552080d40de94ffee6f677386128d',
    'SEM-SERIOUS-WOUND-3802-06BE60-001':'26b92ef84a830a06429fb65844ae9ceee4f252d8a3f9500c663516cf69ae58f1',
    'SEM-SERIOUS-WOUND-3802-2202B4-001':'45614badf4ac2042bf54c09d2280b34b19720256b7f5851cc732d96cffd6780a',
    'SEM-SERIOUS-WOUND-3802-AD7826-001':'ff7cec42c8e5fcbc678db15c253093182472a42f5032e4747aebd48a52aa09b8',
    'SEM-SERIOUS-WOUND-3803-235EB5-001':'9f62589661d3b7db87ecadc9c400703b947972b54467fff0e7533a8994d24edf',
    'SEM-SERIOUS-WOUND-3803-6564CB-001':'181bc4e7aa6c5ced0ae333c9e8f2af58ca090cc4a8e6d00ab4b71381427d440d',
    'SEM-SERIOUS-WOUND-3803-AA0B48-001':'44ec89264f777e51311daf780367d55b9e8701dbb6e9a41ce09bd2741279ecaf',
    'SEM-SERIOUS-WOUND-3805-351AA8-001':'c84701932aa26229ec2db3ade4c28f83f95039b72d63c501f0ec3b65bba8340e',
    'SEM-SERIOUS-WOUND-3805-6175A8-001':'afe07bc3cb741b8edcf84c62fe9b98851229e9074cfa7f2ff5002dbe811f1d78',
    'SEM-SERIOUS-WOUND-3805-74C9B5-001':'627eb6d02d27e8efbc3863809d672326a8a5985610e9c752371ef89394f04819',
    'SEM-SERIOUS-WOUND-3807-4D4710-001':'2e3e76ec4934f11b79a901c1f820f6044feae307020087b2ea0f8cb098a75a69',
    'SEM-SERIOUS-WOUND-3807-655132-001':'b8d96e95f954822fc504b4b0b5688d8f7c3fc219cdffee816e151eb3e5bf6b1a',
    'SEM-SERIOUS-WOUND-3807-89F2F0-001':'6c9ad0a8c57d8435636d980e3480ea34a6d27dd6e5747fbb7f6995e5dd2da602',
    'SEM-SERIOUS-WOUND-3808-55F79E-001':'078cd1145b891ed0ce286350d30fdd88dc953740fca93eeb3c5906b861ec1aba',
    'SEM-SERIOUS-WOUND-3808-68A1CF-001':'7d7587b17c82861bcc0fc523d9fe3348b1f7ae229c6396b4821086eab252f742',
    'SEM-SERIOUS-WOUND-3808-928C60-001':'03e714959d4108b197d6b32589e3d0b37d4a779adb1a0e7c7ee19fc850cdd18c',
    'SEM-SERIOUS-WOUND-404800-1642C4-001':'f288f023055a7b5fddbe6adc1919916b306d54f664b1151adc1863ec713db8b0',
    'SEM-SERIOUS-WOUND-404800-A0A4F8-001':'ab9bf9d3a9ea974548fc1b00884c4bd25897242bb9c5cc375303fd59f7ce572c',
    'SEM-SERIOUS-WOUND-404800-FD77B5-001':'f4b690afc56367fc55ffae102e389178808895850d7c781193fc5d882b9cde3b',
    'SEM-SERIOUS-WOUND-543900-03D258-001':'b3002afd5094983efc6ab35619993a29a3d8986468f1d7d021839043ef6def2c',
    'SEM-SERIOUS-WOUND-543900-864D90-001':'d4487cdf3cf02cde253ca4d9d0ef52c986d314aad45d83fa3f072ab5265431dd',
    'SEM-SERIOUS-WOUND-543900-DBCA72-001':'c7ee47c644f653e5ba555b22ff14d6cc9870b8a1b531bb8ca6a4c78119776404',
    'SEM-SERIOUS-WOUND-DISCARD-001':'3c4f65750a113c44de67fa3f683974b67d9a023381b76a5708134ba0ea0b6928',
    'SEM-SERIOUS-WOUND-GAIN-001':'a74a95aabc5dfd5018f908085c5a5fe00375aa711c0744da84fc9b089bd9cc65',
    'SEM-SERIOUS-WOUND-SETUP-001':'ef7e3a3917571b72e936388e59f1b2257f5a9b6ec765bcf6e296703ef094928d',
    'SEM-SERIOUS-WOUND-STACKING-001':'42dda9b5e09a973f050c7cc7ef8295d2a6403fccb85f497103b2ae3a46055a88',
    'SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001':'0653c1bb992d67bf79f99b3955aa76bb1235851b9aefff3ed06adc6ce75e721b',
}
ALLOWED_OPERATIONS = {
    'branch','change-value','choose','draw-random','end-process','evaluate-condition',
    'inspect-private','invoke-process','invoke-selected-process','move-entity','pay-cost','end-action-window',
    'place-component','play-card','remove-component','replace-target','resolve-attacks',
    'reveal','select-target','set-state','transition-zone','shuffle','resolve-open-alternative',
}
ALLOWED_TIMING = {'before-attack-resolution','during','during-event-card-resolution','when-action-card-played','when-triggered','immediately-after-gain'}
ALLOWED_PARTIAL = {'all-or-nothing-selection','if-not-possible-fallback','ordered-complete','per-sentence-continue','replacement-effect','source-conditional-steps','per-effect-check','source-limited-components','per-selected-component','mutual-consent-per-transfer','consent-and-effect-class-gated','up-to-source-maximum','one-optional-window-per-exact-gain','per-proposed-source-merge'}
ALLOWED_TARGET_SELECTION = {'player-choice','random','deterministic-turn-order','unresolved-when-multiple','deterministic-state-filter','unresolved-order','player-choice-with-consent','player-choice-without-scan','mutual-consent','deterministic-exact-face-filter'}
ALLOWED_DECISION_SELECTION = {'player-choice','random','deterministic','unresolved','player-choice-sequential','mutual-consent','consent'}
FORBIDDEN_IMPLEMENTATION_TEXT = re.compile(r'\b(?:engine\.js|data\.js|network\.js|PeerJS|DOM|WebRTC|serialization|database schema|UI widget)\b', re.IGNORECASE)


class DuplicateJsonKeyError(ValueError):
    pass


def duplicate_rejecting_hook(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f'duplicate JSON object key: {key}')
        result[key] = value
    return result


def load(path: Path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=duplicate_rejecting_hook)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_path(reference: str | None) -> Path | None:
    if not reference:
        return None
    path = reference.split(':', 1)[0]
    if not path.startswith(('docs/', 'assets/')):
        return None
    return REPO / path


def cardinality_valid(value: dict) -> bool:
    if not isinstance(value, dict) or set(value) != {'min', 'max'}:
        return False
    minimum, maximum = value['min'], value['max']
    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 0:
        return False
    if maximum is None:
        return True
    return isinstance(maximum, int) and not isinstance(maximum, bool) and maximum >= minimum


def validate(event_source_path: Path, exploration_source_path: Path, robot_source_path: Path, attack_source_path: Path, queen_health_source_path: Path, serious_wound_source_path: Path, green_item_source_path: Path, source_path: Path, schema_path: Path, semantic_vocabulary_path: Path, room_icon_path: Path, pilots_path: Path, review_path: Path, contradictions_path: Path, coverage_path: Path, backlog_path: Path, *, reproducibility: bool) -> dict:  # pyright: ignore[reportGeneralTypeIssues]
    failures: list[dict] = []
    event_sources = load(event_source_path)
    exploration_sources = load(exploration_source_path)
    robot_sources = load(robot_source_path)
    attack_sources = load(attack_source_path)
    queen_health_sources = load(queen_health_source_path)
    serious_wound_sources = load(serious_wound_source_path)
    green_item_sources = load(green_item_source_path)
    sources_data = load(source_path)
    schema = load(schema_path)
    semantic_vocabulary = load(semantic_vocabulary_path)
    room_icon_data = load(room_icon_path)
    pilots = load(pilots_path)
    review = load(review_path)
    contradictions = load(contradictions_path)
    coverage = load(coverage_path)
    backlog = load(backlog_path)
    vocabulary = load(VOCAB / 'canonical-vocabulary.json')
    identities = load(VOCAB / 'named-component-identities.json')
    taxonomy = load(ONTOLOGY / 'taxonomy.json')
    ontology_review = load(ONTOLOGY / 'review-gates.json')

    term_ids = {item['termId'] for item in vocabulary['entries']}
    identity_ids = {item['identityObservationId'] for item in identities['records']}
    taxon_ids = {item['taxonId'] for item in taxonomy['taxa']}
    semantic_node_rows = semantic_vocabulary.get('nodes') or []
    semantic_node_ids = {item.get('semanticNodeId') for item in semantic_node_rows}
    if ontology_review.get('counts', {}).get('open') != 0:
        failures.append({'check': 'ontology prerequisite gate'})
    for relative_path, expected_hash in PINNED_HELP_SOURCE_HASHES.items():
        path = REPO / relative_path
        if not path.is_file() or sha(path) != expected_hash:
            failures.append({'check': 'pinned Help source hash', 'path': relative_path})
    if len(semantic_node_ids) != len(semantic_node_rows) or any(not re.fullmatch(r'sem\.[a-z0-9.-]+', item or '') for item in semantic_node_ids):
        failures.append({'check': 'semantic node IDs'})
    semantic_kind_counts = {kind: sum(item.get('kind') == kind for item in semantic_node_rows) for kind in ('state-value','zone','position','visibility-scope')}
    if semantic_vocabulary.get('counts') != {'nodes':26,'stateValues':19,'zones':2,'positions':2,'visibilityScopes':3} or semantic_kind_counts != {'state-value':19,'zone':2,'position':2,'visibility-scope':3}:
        failures.append({'check': 'semantic node counts'})
    for item in semantic_node_rows:
        if not item.get('label') or not item.get('sourceEvidence') or any((evidence_path(ref) is None or not evidence_path(ref).exists()) for ref in item.get('sourceEvidence') or []):
            failures.append({'check': 'semantic node provenance', 'semanticNodeId': item.get('semanticNodeId')})

    source_rows = sources_data.get('sources') or []
    source_ids = [item.get('sourceId') for item in source_rows]
    source_by_id = {item['sourceId']: item for item in source_rows}
    if len(source_ids) != len(set(source_ids)) or any(not re.fullmatch(r'SRC-[A-Z0-9-]+', item or '') for item in source_ids):
        failures.append({'check': 'source registry IDs'})
    if source_ids != sorted(source_ids):
        failures.append({'check': 'source registry ordering'})
    authority_order = sources_data.get('authorityOrder') or []
    if authority_order != ['official-errata','official-primary','official-component-reference','source-bound-component-scan','licensed-digital-secondary','project-interpretation']:
        failures.append({'check': 'authority order'})
    authority_rank = {value: index for index, value in enumerate(authority_order)}
    for source in source_rows:
        path = REPO / source.get('path', '')
        evidence = REPO / source.get('evidenceIndexPath', '')
        if not path.is_file() or sha(path) != source.get('sha256'):
            failures.append({'check': 'source tuple', 'sourceId': source.get('sourceId')})
        if not evidence.exists() or source.get('authority') not in authority_rank:
            failures.append({'check': 'source evidence/authority', 'sourceId': source.get('sourceId')})
    if sources_data.get('counts') != {'sources': len(source_rows)}:
        failures.append({'check': 'source registry declared count'})

    # Independent base-Event occurrence lock. This re-derives the family from
    # role/cardId/FaceURL provenance and checks the generated crosswalk without
    # trusting display-name uniqueness or directory placement.
    event_rows = event_sources.get('events') or []
    event_by_card = {row.get('ttsCardId'): row for row in event_rows}
    expected_event_counts = {
        'eventIdentities':20,'ttsFaceOccurrences':20,'ttsSharedBackOccurrencesExcluded':1,
        'canonicalCorpusFaces':19,'sourceBoundDraftFaces':1,'licensedDigitalOccurrences':20,
        'officialVisibleComponentOccurrences':4,'backlogTuples':20,
    }
    if event_sources.get('counts') != expected_event_counts or set(event_by_card) != set(EXPECTED_EVENT_OCCURRENCES) or len(event_by_card) != len(event_rows):
        failures.append({'check': 'Event source-index exact identity count'})
    corpus = load(REPO/'assets/tts-mod/extract/card-text-corpus.json')
    corpus_by_path = {row['sourcePath']:row for row in corpus['records']}
    provenance = load(REPO/'assets/tts-mod/extract/card-provenance-inventory.json')
    roles = load(REPO/'assets/tts-mod/extract/v2/lua_roles.json')
    base_event_role = next((row for row in roles if row.get('role') == 'eventDeck' and row.get('guid') == '0d3dae'), {})
    role_card_ids = sorted(int(value) for value in base_event_role.get('deck_nums') or [])
    if role_card_ids != list(range(5609,5629)) or base_event_role.get('n_urls') != 21:
        failures.append({'check': 'Event TTS role/cardId closure'})
    provenance_by_card = {}
    shared_event_backs = set()
    for provenance_row in provenance:
        for obj in provenance_row.get('objects') or []:
            if obj.get('key') == 'BackURL' and obj.get('guid') == '0d3dae':
                shared_event_backs.add(provenance_row.get('file'))
            if obj.get('key') != 'FaceURL' or obj.get('gmnotes') != 'event' or not obj.get('cardId') or ['DeckCustom','0d3dae',''] not in (obj.get('parent') or []):
                continue
            card_id = int(obj['cardId']) // 100
            if card_id in EXPECTED_EVENT_OCCURRENCES:
                provenance_by_card.setdefault(card_id,[]).append((provenance_row,obj))
    if set(provenance_by_card) != set(EXPECTED_EVENT_OCCURRENCES) or any(len(rows) != 1 for rows in provenance_by_card.values()) or len(shared_event_backs) != 1:
        failures.append({'check': 'Event FaceURL provenance closure'})
    bga_text = (REPO/'docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js').read_text(encoding='utf-8')
    secondary = load(REPO/'docs/rules/source-extraction/secondary-evidence-index.json')
    bga_table = next((row for row in secondary['licensedDigital']['structuredIndex']['tables'] if row.get('name') == 'EVENT_CARDS_DATA'), {})
    expected_bga_keys = {value[3] for value in EXPECTED_EVENT_OCCURRENCES.values()}
    if bga_table.get('count') != 20 or set(bga_table.get('keys') or []) != expected_bga_keys:
        failures.append({'check': 'Event licensed-digital independent index closure'})
    backlog_rows_by_id = {row.get('semanticUnitId'):row for row in backlog.get('units') or []}
    for card_id, expected in EXPECTED_EVENT_OCCURRENCES.items():
        expected_source_id,expected_path,expected_sha,expected_bga_key,expected_rule_id,expected_title = expected
        event = event_by_card.get(card_id) or {}
        actual_tuple = (event.get('sourceId'),event.get('sourcePath'),event.get('sourceSha256'),(event.get('bgaOccurrence') or {}).get('key'),event.get('semanticRuleId'),event.get('visibleTitle'))
        if actual_tuple != expected:
            failures.append({'check': 'independently locked Event occurrence crosswalk', 'ttsCardId':card_id})
        source_file = REPO/expected_path
        if not source_file.is_file() or sha(source_file) != expected_sha:
            failures.append({'check': 'Event live source hash', 'ttsCardId':card_id})
        provenance_rows = provenance_by_card.get(card_id) or []
        if provenance_rows:
            provenance_row,obj = provenance_rows[0]
            derived_path = 'assets/tts-mod/extract/v2-dl/tree/' + provenance_row.get('file','')
            if derived_path != expected_path or int(obj.get('cardId',0)) != card_id*100 or obj.get('guid') != event.get('ttsCardGuid'):
                failures.append({'check': 'Event occurrence role/provenance projection', 'ttsCardId':card_id})
        corpus_row = corpus_by_path.get(expected_path) or {}
        if corpus_row.get('sourceSha256') != expected_sha or corpus_row.get('printedData',{}).get('body') != event.get('printedBody') or not corpus_row.get('rulesTextPresent'):
            failures.append({'check': 'Event closed-corpus projection', 'ttsCardId':card_id})
        registry = source_by_id.get(expected_source_id) or {}
        if (registry.get('path'),registry.get('sha256'),registry.get('authority'),registry.get('occurrenceId'),registry.get('evidenceRecord')) != (expected_path,expected_sha,'source-bound-component-scan',f'TTS-EVENT-{card_id}-FACE',expected_sha):
            failures.append({'check': 'Event source-registry exact scan tuple', 'ttsCardId':card_id})
        sentences = event.get('sentences') or []
        if [row.get('sequence') for row in sentences] != list(range(1,len(sentences)+1)) or len({row.get('sentenceId') for row in sentences}) != len(sentences):
            failures.append({'check': 'Event source sentence IDs/order', 'ttsCardId':card_id})
        body = event.get('printedBody') or ''
        cursor = 0
        for sentence in sentences:
            start,end = sentence.get('start'),sentence.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or start < cursor or body[start:end] != sentence.get('exactText') or sentence.get('section') not in {'movement','main','secondary'}:
                failures.append({'check': 'Event exact sentence span projection', 'ttsCardId':card_id, 'sentenceId':sentence.get('sentenceId')})
            cursor = end if isinstance(end,int) else cursor
        bga = event.get('bgaOccurrence') or {}
        bga_block = bga.get('sourceBlockText') or ''
        if bga.get('sourceId') != 'SRC-BGA-EVENTS' or bga.get('sourceSha256') != sha(REPO/'docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js') or not bga_block or bga_block not in bga_text:
            failures.append({'check': 'Event licensed occurrence exact projection', 'ttsCardId':card_id})
        join = event.get('joinEvidence') or {}
        basis_text = ' '.join(join.get('basis') or []).lower()
        if join.get('titleOnlyJoin') is not False or join.get('identityJoin') != 'explicit occurrence crosswalk' or 'cardid' not in basis_text or 'sha-256' not in basis_text or 'ordered' not in basis_text:
            failures.append({'check': 'Event title-only join prohibited', 'ttsCardId':card_id})
        backlog_id = 'CARD:' + expected_sha[:16]
        backlog_row = backlog_rows_by_id.get(backlog_id) or {}
        if event.get('backlogUnitId') != backlog_id or backlog_row.get('sourcePath') != expected_path or backlog_row.get('sourceLocator') != expected_sha or backlog_row.get('pilotRuleIds') != [expected_rule_id] or backlog_row.get('status') != 'pilot-covered':
            failures.append({'check': 'Event exact backlog tuple projection', 'ttsCardId':card_id})
    expected_event_source_ids = {value[0] for value in EXPECTED_EVENT_OCCURRENCES.values()}
    actual_event_source_ids = {row.get('sourceId') for row in source_rows if row.get('occurrenceId','').startswith('TTS-EVENT-')}
    bga_registry = source_by_id.get('SRC-BGA-EVENTS') or {}
    if actual_event_source_ids != expected_event_source_ids or bga_registry.get('authority') != 'licensed-digital-secondary' or bga_registry.get('occurrenceId') != 'EVENT_CARDS_DATA':
        failures.append({'check': 'Event source-registry family closure'})
    leaving = event_by_card.get(5614) or {}
    if (leaving.get('printedBody') or '').count('[ICON: solid white rectangular block]') != 3 or (leaving.get('bgaOccurrence',{}).get('sourceBlockText') or '').count('ACTION-CARD') != 3:
        failures.append({'check': 'Leaving the Shell unresolved glyph boundary'})

    # Independent base-Exploration occurrence lock. The generated source index
    # is pinned and also re-derived from root-role/CardID/GUID/FaceURL evidence,
    # exact corpus bytes, untitled face text, literal diagrams, paired BackURL,
    # official visuals, FAQ units, backlog tuples, and the licensed table.
    expected_exploration_counts = {
        'explorationIdentities':12,'ttsFaceOccurrences':12,'ttsSharedBackOccurrences':1,
        'directFaceSelectors':12,'generatedSpriteSheetCells':0,'selectorGaps':0,
        'untitledFaces':12,'sourceBoundDraftFaces':12,'licensedDigitalOccurrences':12,
        'officialVisibleComponentOccurrences':3,'officialVisibleComponentIdentities':2,
        'faqOccurrences':8,'printedSentences':46,'sourceLocalDiagrams':12,
        'functionalIconOccurrences':60,'backlogTuples':12,
    }
    exploration_rows = exploration_sources.get('faces') or []
    exploration_by_card = {row.get('ttsCardId'):row for row in exploration_rows}
    if sha(exploration_source_path) != PINNED_EXPLORATION_SOURCE_INDEX_HASH:
        failures.append({'check':'pinned Exploration source index'})
    if exploration_sources.get('counts') != expected_exploration_counts or set(exploration_by_card) != set(EXPECTED_EXPLORATION_OCCURRENCES) or len(exploration_by_card) != len(exploration_rows):
        failures.append({'check':'Exploration source-index exact identity count'})
    base_exploration_role = next((row for row in roles if row.get('role') == 'explorationDeck' and row.get('guid') == '63add2'), {})
    exploration_role_ids = sorted(int(value) for value in base_exploration_role.get('deck_nums') or [])
    objects = load(REPO/'assets/tts-mod/extract/v2/objects.json')
    base_exploration_object = next((row for row in objects if row.get('guid') == '63add2'), {})
    if exploration_role_ids != list(range(5629,5641)) or base_exploration_role.get('n_urls') != 13 or base_exploration_object.get('parent') != []:
        failures.append({'check':'Exploration root TTS role/CardID closure'})
    expected_excluded_roles = {('xyrianExplorationDeck','6b2b69'),('explorationDeck','a24dc8'),('explorationDeck','dd1eda'),('explorationDeck','2e8e9d')}
    actual_excluded_roles = {(row.get('role'),row.get('guid')) for row in exploration_sources.get('excludedExpansionRoles') or []}
    if actual_excluded_roles != expected_excluded_roles or any('expansion' not in (row.get('scope') or '').lower() for row in exploration_sources.get('excludedExpansionRoles') or []):
        failures.append({'check':'Exploration base/expansion scope boundary'})
    exploration_provenance_by_card = {}
    exploration_deck_backs = []
    exploration_card_backs = []
    for provenance_row in provenance:
        for obj in provenance_row.get('objects') or []:
            if obj.get('key') == 'BackURL' and obj.get('guid') == '63add2':
                exploration_deck_backs.append((provenance_row,obj))
            if obj.get('key') == 'BackURL' and obj.get('gmnotes') == 'exploration' and ['Deck','63add2',''] in (obj.get('parent') or []):
                exploration_card_backs.append((provenance_row,obj))
            if obj.get('key') != 'FaceURL' or obj.get('type') != 'CardCustom' or obj.get('gmnotes') != 'exploration' or not obj.get('cardId') or ['Deck','63add2',''] not in (obj.get('parent') or []):
                continue
            card_id = int(obj['cardId']) // 100
            if card_id in EXPECTED_EXPLORATION_OCCURRENCES:
                exploration_provenance_by_card.setdefault(card_id,[]).append((provenance_row,obj))
    if set(exploration_provenance_by_card) != set(EXPECTED_EXPLORATION_OCCURRENCES) or any(len(rows) != 1 for rows in exploration_provenance_by_card.values()) or len(exploration_deck_backs) != 1 or len(exploration_card_backs) != 12:
        failures.append({'check':'Exploration FaceURL/BackURL provenance closure'})
    exploration_table = next((row for row in secondary['licensedDigital']['structuredIndex']['tables'] if row.get('name') == 'EXPLORATION_CARDS_DATA'), {})
    expected_exploration_bga_keys = {row['bgaKey'] for row in EXPECTED_EXPLORATION_OCCURRENCES.values()}
    if exploration_table.get('count') != 12 or set(exploration_table.get('keys') or []) != expected_exploration_bga_keys:
        failures.append({'check':'Exploration licensed-digital independent index closure'})
    slot_labels = {0:'upper-left',1:'upper-right',2:'right',3:'lower-right',4:'lower-left',5:'left'}
    expected_exploration_source_ids = set()
    for card_id, expected in EXPECTED_EXPLORATION_OCCURRENCES.items():
        face = exploration_by_card.get(card_id) or {}
        expected_exploration_source_ids.add(expected['sourceId'])
        actual_tuple = (face.get('sourceId'),face.get('sourcePath'),face.get('sourceSha256'),face.get('ttsCardGuid'),(face.get('bgaOccurrence') or {}).get('key'),face.get('semanticRuleId'),face.get('printedTitle'))
        expected_tuple = (expected['sourceId'],expected['path'],expected['sha256'],expected['guid'],expected['bgaKey'],expected['ruleId'],'')
        if actual_tuple != expected_tuple:
            failures.append({'check':'independently locked Exploration occurrence crosswalk','ttsCardId':card_id})
        source_file = REPO/expected['path']
        if not source_file.is_file() or sha(source_file) != expected['sha256']:
            failures.append({'check':'Exploration live source hash','ttsCardId':card_id})
        provenance_rows = exploration_provenance_by_card.get(card_id) or []
        if provenance_rows:
            provenance_row,obj = provenance_rows[0]
            derived_path = 'assets/tts-mod/extract/v2-dl/tree/' + provenance_row.get('file','')
            selector = face.get('sourceSelector') or {}
            if derived_path != expected['path'] or int(obj.get('cardId',0)) != card_id*100 or obj.get('guid') != expected['guid'] or selector.get('key') != 'FaceURL' or selector.get('objectType') != 'CardCustom' or selector.get('cardId') != card_id*100 or selector.get('guid') != expected['guid'] or selector.get('parentDeckGuid') != '63add2' or selector.get('url') != provenance_row.get('url') or selector.get('generatedSpriteSheetCell') is not False or selector.get('selectorGap') is not None:
                failures.append({'check':'Exploration exact FaceURL selector/provenance projection','ttsCardId':card_id})
        corpus_row = corpus_by_path.get(expected['path']) or {}
        if corpus_row.get('sourceSha256') != expected['sha256'] or corpus_row.get('printedData',{}).get('body') != face.get('printedBody') or corpus_row.get('printedData',{}).get('title') != '' or face.get('printedTitle') != '' or corpus_row.get('extractionState') != 'draft-full' or not corpus_row.get('rulesTextPresent'):
            failures.append({'check':'Exploration closed-corpus untitled projection','ttsCardId':card_id})
        registry = source_by_id.get(expected['sourceId']) or {}
        if (registry.get('path'),registry.get('sha256'),registry.get('authority'),registry.get('occurrenceId'),registry.get('evidenceRecord')) != (expected['path'],expected['sha256'],'source-bound-component-scan',f'TTS-EXPLORATION-{card_id}-FACE',expected['sha256']):
            failures.append({'check':'Exploration source-registry exact scan tuple','ttsCardId':card_id})
        units = face.get('sourceUnits') or []
        if [row.get('sequence') for row in units] != list(range(1,len(units)+1)) or len({row.get('unitId') for row in units}) != len(units):
            failures.append({'check':'Exploration source-unit IDs/order','ttsCardId':card_id})
        printed_units = [row for row in units if row.get('unitKind') == 'printed-sentence']
        diagrams = [row for row in units if row.get('unitKind') == 'source-local-diagram']
        procedure_lifecycle = [row for row in units if row.get('unitKind') == 'official-procedure-lifecycle']
        if len(printed_units) != expected['sentences'] or len(diagrams) != 1 or len(procedure_lifecycle) != (0 if expected['removeFromGame'] else 1):
            failures.append({'check':'Exploration exact sentence/diagram/lifecycle counts','ttsCardId':card_id})
        body = face.get('printedBody') or ''
        cursor = 0
        for unit in units:
            start,end = unit.get('start'),unit.get('end')
            if unit.get('unitKind') in {'printed-sentence','source-local-diagram'}:
                if not isinstance(start,int) or not isinstance(end,int) or start < cursor or body[start:end] != unit.get('exactText'):
                    failures.append({'check':'Exploration exact source-unit span projection','ttsCardId':card_id,'unitId':unit.get('unitId')})
                cursor = end if isinstance(end,int) else cursor
            elif unit.get('unitKind') == 'official-procedure-lifecycle' and (start is not None or end is not None or unit.get('section') != 'lifecycle'):
                failures.append({'check':'Exploration official discard source-unit projection','ttsCardId':card_id})
        diagram = diagrams[0] if diagrams else {}
        diagram_tuple = (
            diagram.get('roomType'),
            [row.get('slotIndex') for row in diagram.get('corridorSlots') or []],
            [row.get('slotIndex') for row in diagram.get('noiseSlots') or []],
            (diagram.get('roomIcons') or [])[1:],
        )
        if diagram_tuple != (expected['roomType'],expected['corridors'],expected['noise'],expected['roomIcons']) or any(row.get('slotLabel') != slot_labels.get(row.get('slotIndex')) for row in (diagram.get('corridorSlots') or []) + (diagram.get('noiseSlots') or [])):
            failures.append({'check':'independently locked Exploration source-local diagram','ttsCardId':card_id})
        icons = face.get('iconOccurrences') or []
        icon_refs = [row.get('semanticReferenceId') for row in icons]
        expected_icon_refs = ['icon.character', *[f'icon.{value}' for value in expected['roomIcons']], *(['icon.noise']*len(expected['noise'])), 'icon.secure','icon.secure']
        if (face.get('printedBody') or '').count('[noiseDieHazard]'):
            expected_icon_refs.append('icon.noiseDieHazard')
        if len(icons) != expected['icons'] or icon_refs != expected_icon_refs or [row.get('sequence') for row in icons] != list(range(1,len(icons)+1)) or len({row.get('occurrenceId') for row in icons}) != len(icons) or any(ref in {'icon.lifeSupportActive','icon.lifeSupportInactive','icon.hibernatoriumActive','icon.hibernatoriumInactive'} for ref in icon_refs):
            failures.append({'check':'Exploration exact source-local icon occurrence projection','ttsCardId':card_id})
        bga = face.get('bgaOccurrence') or {}
        bga_tuple = (bga.get('type'),bga.get('corridors'),bga.get('corridorsWithNoise'),bga.get('otherTokens'),bga.get('intrudersToAdd'),bga.get('closeDoor'),bga.get('removeFromGame'))
        if bga_tuple != (expected['roomType'],expected['corridors'],expected['noise'],expected['roomIcons'],expected['adultCount'],expected['closeDoor'],expected['removeFromGame']) or bga.get('sourceId') != 'SRC-BGA-EXPLORATION' or bga.get('sourceSha256') != sha(REPO/'docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js') or not bga.get('sourceBlockText') or (bga.get('sourceBlockText') or '') not in bga_text:
            failures.append({'check':'Exploration licensed occurrence exact field projection','ttsCardId':card_id})
        official_ids = [row.get('occurrenceId') for row in face.get('officialOccurrences') or []]
        if official_ids != expected['official']:
            failures.append({'check':'Exploration official visible-occurrence projection','ttsCardId':card_id})
        expected_faq = (["FQ-P02-U06"] if expected['closeDoor'] else []) + (["FQ-P02-U07"] if expected['removeFromGame'] else [])
        if [row.get('sourceUnitId') for row in face.get('faqOccurrences') or []] != expected_faq:
            failures.append({'check':'Exploration FAQ occurrence projection','ttsCardId':card_id})
        join = face.get('joinEvidence') or {}
        basis_text = ' '.join(join.get('basis') or []).lower()
        if join.get('titleOnlyJoin') is not False or join.get('identityJoin') != 'explicit occurrence crosswalk' or 'cardid' not in basis_text or 'guid' not in basis_text or 'sha-256' not in basis_text or 'diagram' not in basis_text or 'ordered' not in basis_text:
            failures.append({'check':'Exploration title/folder/modulo join prohibited','ttsCardId':card_id})
        backlog_id = 'CARD:' + expected['sha256'][:16]
        backlog_row = backlog_rows_by_id.get(backlog_id) or {}
        if face.get('backlogUnitId') != backlog_id or backlog_row.get('sourcePath') != expected['path'] or backlog_row.get('sourceLocator') != expected['sha256'] or backlog_row.get('pilotRuleIds') != [expected['ruleId']] or backlog_row.get('status') != 'pilot-covered':
            failures.append({'check':'Exploration exact backlog tuple projection','ttsCardId':card_id})
    actual_exploration_source_ids = {row.get('sourceId') for row in source_rows if row.get('occurrenceId','').startswith('TTS-EXPLORATION-') and row.get('occurrenceId') != 'TTS-EXPLORATION-SHARED-BACK'}
    bga_exploration_registry = source_by_id.get('SRC-BGA-EXPLORATION') or {}
    back_registry = source_by_id.get('SRC-EXPLORATION-BACK') or {}
    shared_back = exploration_sources.get('sharedBack') or {}
    expected_back_tuple = ('assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-092.jpg','41ad850b1367a2c59049ea3b62f4ff0375d28545cb963ec18bfd3cfb07048db5','BackURL','Deck','63add2',1,12,False)
    back_selector = shared_back.get('sourceSelector') or {}
    actual_back_tuple = (shared_back.get('sourcePath'),shared_back.get('sourceSha256'),back_selector.get('key'),back_selector.get('objectType'),back_selector.get('guid'),back_selector.get('deckSelectorCount'),back_selector.get('cardSelectorCount'),shared_back.get('rulesTextPresent'))
    if actual_exploration_source_ids != expected_exploration_source_ids or bga_exploration_registry.get('authority') != 'licensed-digital-secondary' or bga_exploration_registry.get('occurrenceId') != 'EXPLORATION_CARDS_DATA' or actual_back_tuple != expected_back_tuple or (back_registry.get('path'),back_registry.get('sha256'),back_registry.get('occurrenceId')) != (expected_back_tuple[0],expected_back_tuple[1],'TTS-EXPLORATION-SHARED-BACK'):
        failures.append({'check':'Exploration source-registry face/back/licensed closure'})

    # Independent base-Robot family lock. Full CardID/GUID/FaceURL/root-deck
    # tuples, not names or folders, define the six operative faces. Shared-back,
    # prototype, expansion, Room-name, and TTS runtime-state artifacts remain
    # explicit but cannot become extra rules faces.
    robot_rows = robot_sources.get('faces') or []
    robot_by_card = {row.get('ttsCardId'):row for row in robot_rows}
    if sha(robot_source_path) != PINNED_ROBOT_SOURCE_INDEX_HASH:
        failures.append({'check':'pinned Robot source index'})
    if robot_sources.get('counts') != EXPECTED_ROBOT_COUNTS or set(robot_by_card) != set(EXPECTED_ROBOT_OCCURRENCES) or len(robot_by_card) != len(robot_rows):
        failures.append({'check':'Robot source-index exact identity count'})
    base_robot_role = next((row for row in roles if row.get('role') == 'robotDeck' and row.get('guid') == '98925d'), {})
    root_robot_object = next((row for row in objects if row.get('guid') == '98925d'), {})
    expected_robot_deck_nums = ['5064','5108','5293','5294','5295','5296']
    if base_robot_role.get('deck_nums') != expected_robot_deck_nums or base_robot_role.get('n_urls') != 7 or base_robot_role.get('type') != 'DeckCustom' or root_robot_object.get('parent') != [] or root_robot_object.get('type') != 'DeckCustom':
        failures.append({'check':'Robot root Lua role/deck/container closure'})
    robot_provenance_by_card = {}
    robot_back_provenance_rows = []
    for provenance_row in provenance:
        for obj in provenance_row.get('objects') or []:
            if obj.get('key') == 'BackURL' and obj.get('guid') == '98925d':
                robot_back_provenance_rows.append(provenance_row)
            if obj.get('key') != 'FaceURL' or obj.get('type') != 'CardCustom' or not obj.get('cardId') or ['DeckCustom','98925d',''] not in (obj.get('parent') or []):
                continue
            card_id = int(obj['cardId'])
            if card_id in EXPECTED_ROBOT_OCCURRENCES:
                robot_provenance_by_card.setdefault(card_id,[]).append((provenance_row,obj))
    if set(robot_provenance_by_card) != set(EXPECTED_ROBOT_OCCURRENCES) or any(len(rows) != 1 for rows in robot_provenance_by_card.values()) or len(robot_back_provenance_rows) != 1:
        failures.append({'check':'Robot FaceURL/BackURL provenance closure'})
    robot_table = next((row for row in secondary['licensedDigital']['structuredIndex']['tables'] if row.get('name') == 'ROBOT_CARDS_DATA'), {})
    expected_robot_bga_keys = {row['bgaKey'] for row in EXPECTED_ROBOT_OCCURRENCES.values()}
    if robot_table.get('count') != 6 or set(robot_table.get('keys') or []) != expected_robot_bga_keys:
        failures.append({'check':'Robot licensed-digital independent index closure'})
    visual_source = load(REPO/'docs/rules/source-extraction/rulebook-visual-obligations.json')
    visual_by_id = {unit['occurrenceId']:unit for page in visual_source['pages'] for unit in page.get('visualUnits') or []}
    expected_robot_visual_ids = ['RB-P03-V01','RB-P05-V01','RB-P05-V02','RB-P08-V03','RB-P09-V01','RB-P12-V02','RB-P37-V01','RB-P40-V02']
    official_visual_rows = robot_sources.get('officialVisualOccurrences') or []
    if [row.get('occurrenceId') for row in official_visual_rows] != expected_robot_visual_ids or any(row.get('visualType') != (visual_by_id.get(row.get('occurrenceId')) or {}).get('type') or row.get('bbox160Dpi') != (visual_by_id.get(row.get('occurrenceId')) or {}).get('bbox') for row in official_visual_rows):
        failures.append({'check':'Robot official rulebook visual-obligation closure'})
    expected_robot_text_ids = [
        'RB-ROBOT-SETUP-01','RB-ROBOT-SETUP-02','RB-ROBOT-SETUP-03','RB-ROBOT-SETUP-04',
        'RB-ROBOT-ACTION-01','RB-ROBOT-EFFECT-01','RB-ROBOT-LOCAL-01','RB-ROBOT-COMPONENT-LIMIT-01',
        'RB-ROBOT-WOUND-01','RB-ROBOT-MALFUNCTION-01','RB-ROBOT-MALFUNCTION-02','RB-ROBOT-SECURE-01',
        'RB-ROBOT-MALFUNCTION-LIMIT-01','RB-ROBOT-INTRO-01','RB-ROBOT-REVEAL-01','RB-ROBOT-INTRUDER-01',
        'RB-ROBOT-FAMILY-01','RB-ROBOT-ACTIVATE-LOCAL-01','RB-ROBOT-ACTIVATE-REMOTE-01','RB-ROBOT-DATA-01',
        'RB-ROBOT-MALFUNCTION-P37-01','RB-ROBOT-MOVE-01','RB-ROBOT-MOVE-02','RB-ROBOT-MOVE-03',
        'RB-ROBOT-GEAR-01','RB-ROBOT-GEAR-02','RB-ROBOT-BURST-01',
    ]
    robot_text_rows = robot_sources.get('officialRulebookTextOccurrences') or []
    if [row.get('occurrenceId') for row in robot_text_rows] != expected_robot_text_ids or any(not row.get('section') or not row.get('locator') or not row.get('sourceText') for row in robot_text_rows):
        failures.append({'check':'Robot official rulebook text-occurrence closure'})
    official_pixel_locks = {
        506400: ('RB-P03-V01-ROBOT-SERVER',115,62,0.5391,0.5666,[1063.81,2798.88,1268.62,3084.55]),
        529400: ('RB-P03-V01-ROBOT-TECHNICAL',134,46,0.3433,0.5303,[1201.81,2750.24,1383.27,3024.36]),
    }
    expected_robot_source_ids = set()
    for card_id, expected in EXPECTED_ROBOT_OCCURRENCES.items():
        face = robot_by_card.get(card_id) or {}
        expected_robot_source_ids.add(expected['sourceId'])
        actual_tuple = (face.get('sourceId'),face.get('sourcePath'),face.get('sourceSha256'),face.get('ttsCardGuid'),face.get('ttsRootDeckNumber'),face.get('ttsChildObjectDeckNums'),(face.get('bgaOccurrence') or {}).get('key'),face.get('semanticRuleId'),face.get('printedTitle'))
        expected_tuple = (expected['sourceId'],expected['path'],expected['sha256'],expected['guid'],expected['rootDeckNumber'],expected['childDeckNums'],expected['bgaKey'],expected['ruleId'],expected['title'])
        if actual_tuple != expected_tuple:
            failures.append({'check':'independently locked Robot occurrence crosswalk','ttsCardId':card_id})
        source_file = REPO/expected['path']
        if not source_file.is_file() or sha(source_file) != expected['sha256']:
            failures.append({'check':'Robot live source hash','ttsCardId':card_id})
        provenance_rows = robot_provenance_by_card.get(card_id) or []
        if provenance_rows:
            provenance_row,obj = provenance_rows[0]
            selector = face.get('sourceSelector') or {}
            derived_path = 'assets/tts-mod/extract/v2-dl/tree/' + provenance_row.get('file','')
            if derived_path != expected['path'] or int(obj.get('cardId',0)) != card_id or obj.get('guid') != expected['guid'] or selector.get('key') != 'FaceURL' or selector.get('objectType') != 'CardCustom' or selector.get('cardId') != card_id or selector.get('guid') != expected['guid'] or selector.get('parentDeckGuid') != '98925d' or selector.get('url') != provenance_row.get('url') or selector.get('sideRole') != 'operative-face' or selector.get('selectorStatus') != 'exact-composite-card-reference' or selector.get('singularUrlSelector') is not False or selector.get('generatedSpriteSheetCell') is not False or selector.get('selectorGap') is not None:
                failures.append({'check':'Robot exact CardID/GUID/FaceURL selector projection','ttsCardId':card_id})
        corpus_row = corpus_by_path.get(expected['path']) or {}
        if corpus_row.get('sourceSha256') != expected['sha256'] or corpus_row.get('printedData',{}).get('body') != face.get('printedBody') or not corpus_row.get('rulesTextPresent') or corpus_row.get('extractionState') not in {'verified-canonical','draft-full'}:
            failures.append({'check':'Robot closed-corpus face projection','ttsCardId':card_id})
        registry = source_by_id.get(expected['sourceId']) or {}
        if (registry.get('path'),registry.get('sha256'),registry.get('authority'),registry.get('occurrenceId'),registry.get('evidenceRecord')) != (expected['path'],expected['sha256'],'source-bound-component-scan',f'TTS-ROBOT-{card_id}-FACE',expected['sha256']):
            failures.append({'check':'Robot source-registry exact face tuple','ttsCardId':card_id})
        panels = face.get('panels') or []
        panel_tuple = [(row.get('panelId'),row.get('readingOrder'),row.get('role'),row.get('operative')) for row in panels]
        expected_panel_tuple = [('P1',1,'title',False),('P2',2,'artwork',False),('P3',3,'first-option-rules-plaque',True),('P4',4,'remaining-options-rules-field',True)]
        if panel_tuple != expected_panel_tuple or (panels and (panels[0].get('exactText') != expected['title'] or panels[1].get('exactText') != '')):
            failures.append({'check':'Robot exact panel roles/order','ttsCardId':card_id})
        body = face.get('printedBody') or ''
        for panel in panels[2:]:
            start,end = panel.get('bodyStart'),panel.get('bodyEnd')
            if not isinstance(start,int) or not isinstance(end,int) or body[start:end] != panel.get('exactText'):
                failures.append({'check':'Robot exact panel text/span projection','ttsCardId':card_id,'panelId':panel.get('panelId')})
        sentences = face.get('sentences') or []
        if [row.get('sentenceId') for row in sentences] != expected['sentenceIds'] or [row.get('sequence') for row in sentences] != list(range(1,len(sentences)+1)) or [row.get('panelId') for row in sentences] != ['P3',*(['P4']*(len(sentences)-1))]:
            failures.append({'check':'Robot source sentence IDs/panel order','ttsCardId':card_id})
        cursor = 0
        for sentence in sentences:
            start,end = sentence.get('start'),sentence.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or start < cursor or body[start:end] != sentence.get('exactText'):
                failures.append({'check':'Robot exact sentence span projection','ttsCardId':card_id,'sentenceId':sentence.get('sentenceId')})
            cursor = end if isinstance(end,int) else cursor
        options = face.get('actionOptions') or []
        if [row.get('optionId') for row in options] != expected['optionIds'] or [row.get('sequence') for row in options] != list(range(1,len(options)+1)) or [sentence_id for option in options for sentence_id in option.get('sentenceIds') or []] != expected['sentenceIds']:
            failures.append({'check':'Robot exact option/sentence grouping','ttsCardId':card_id})
        icons = face.get('iconOccurrences') or []
        if [row.get('semanticReferenceId') for row in icons] != expected['iconRefs'] or [row.get('sequence') for row in icons] != list(range(1,len(icons)+1)) or len({row.get('occurrenceId') for row in icons}) != len(icons):
            failures.append({'check':'Robot exact source-local icon occurrence projection','ttsCardId':card_id})
        for icon in icons:
            start,end = icon.get('start'),icon.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or body[start:end] != f"[{icon.get('sourceToken')}]" or icon.get('semanticReferenceId') != f"icon.{icon.get('sourceToken')}":
                failures.append({'check':'Robot exact icon token/span projection','ttsCardId':card_id,'occurrenceId':icon.get('occurrenceId')})
        states = face.get('cardStateRoles') or {}
        if states != {'initial':'face-down-unrevealed','afterRevealTrigger':'face-up-revealed','sharedBackSourceId':'SRC-ROBOT-BACK','separateRulesFaceOnBack':False}:
            failures.append({'check':'Robot face/back and reveal-state role projection','ttsCardId':card_id})
        bga = face.get('bgaOccurrence') or {}
        if bga.get('sourceId') != 'SRC-BGA-ROBOTS' or bga.get('sourceSha256') != sha(REPO/'docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js') or not bga.get('sourceBlockText') or (bga.get('sourceBlockText') or '') not in bga_text or not isinstance(bga.get('desc'),list):
            failures.append({'check':'Robot licensed occurrence exact projection','ttsCardId':card_id})
        official_ids = [row.get('sourceOccurrenceId') for row in face.get('officialOccurrences') or []]
        if official_ids != expected['official']:
            failures.append({'check':'Robot official visible-face occurrence projection','ttsCardId':card_id})
        if card_id in official_pixel_locks:
            official = (face.get('officialOccurrences') or [{}])[0]
            pixel = official.get('pixelMatch') or {}
            expected_pixel = official_pixel_locks[card_id]
            actual_pixel = (official.get('sourceOccurrenceId'),pixel.get('ratioMatches'),pixel.get('ransacInliers'),pixel.get('inlierRatio'),pixel.get('medianReprojectionError'),pixel.get('bbox'))
            if pixel.get('renderDpi') != 300 or actual_pixel != expected_pixel:
                failures.append({'check':'Robot official face pixel-match lock','ttsCardId':card_id})
        join = face.get('joinEvidence') or {}
        basis_text = ' '.join(join.get('basis') or []).lower()
        if join.get('titleOnlyJoin') is not False or join.get('identityJoin') != 'explicit occurrence crosswalk' or any(fragment not in basis_text for fragment in ('cardid','guid','faceurl','sha-256','panel','ordered')) or any(fragment in basis_text for fragment in ('folder-only','title-only','cardid modulo')):
            failures.append({'check':'Robot title/folder/modulo join prohibited','ttsCardId':card_id})
        backlog_id = 'CARD:' + expected['sha256'][:16]
        backlog_row = backlog_rows_by_id.get(backlog_id) or {}
        if face.get('backlogUnitId') != backlog_id or backlog_row.get('sourcePath') != expected['path'] or backlog_row.get('sourceLocator') != expected['sha256'] or backlog_row.get('pilotRuleIds') != [expected['ruleId']] or backlog_row.get('status') != 'pilot-covered':
            failures.append({'check':'Robot exact backlog tuple projection','ttsCardId':card_id})
    actual_robot_source_ids = {row.get('sourceId') for row in source_rows if row.get('occurrenceId','').startswith('TTS-ROBOT-') and row.get('occurrenceId') != 'TTS-ROBOT-SHARED-BACK'}
    robot_bga_registry = source_by_id.get('SRC-BGA-ROBOTS') or {}
    robot_back_registry = source_by_id.get('SRC-ROBOT-BACK') or {}
    robot_back = robot_sources.get('sharedBack') or {}
    robot_back_selector = robot_back.get('sourceSelector') or {}
    expected_robot_back_tuple = ('assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-155.jpg','9cf67e814071c67c598456070306951e3e24cb00a274b20d736596acfeb67c39','BackURL','DeckCustom','98925d','shared-non-operative-back',1,6,2,False,False)
    actual_robot_back_tuple = (robot_back.get('sourcePath'),robot_back.get('sourceSha256'),robot_back_selector.get('key'),robot_back_selector.get('objectType'),robot_back_selector.get('guid'),robot_back_selector.get('sideRole'),robot_back_selector.get('rootDeckSelectorCount'),robot_back_selector.get('baseCardSelectorCount'),robot_back_selector.get('prototypeSelectorCountExcluded'),robot_back.get('rulesTextPresent'),robot_back.get('separateRulesFace'))
    if actual_robot_source_ids != expected_robot_source_ids or robot_bga_registry.get('authority') != 'licensed-digital-secondary' or robot_bga_registry.get('occurrenceId') != 'ROBOT_CARDS_DATA' or actual_robot_back_tuple != expected_robot_back_tuple or (robot_back_registry.get('path'),robot_back_registry.get('sha256'),robot_back_registry.get('occurrenceId')) != (expected_robot_back_tuple[0],expected_robot_back_tuple[1],'TTS-ROBOT-SHARED-BACK'):
        failures.append({'check':'Robot source-registry face/back/licensed closure'})
    runtime = robot_sources.get('ttsRuntimeStateProvenance') or {}
    role_tuples = [(row.get('role'),row.get('guid'),row.get('objectType')) for row in runtime.get('roleBindings') or []]
    reveal_runtime = runtime.get('reveal') or {}
    if role_tuples != [('robot','cbf1f3','Custom_Model'),('robotDeck','98925d','DeckCustom'),('robotToken','828c1d','Custom_Token')] or runtime.get('authorityBoundary') != 'TTS automation/provenance only; never rules authority' or (reveal_runtime.get('modelStateTransition') or {}) != {'fromGmNotes':'','toGmNotes':'active'} or (reveal_runtime.get('helperTokenStateTransition') or {}).get('toStateId') != 1 or 'not inferred' not in (reveal_runtime.get('helperTokenStateTransition') or {}).get('semanticImageIdentity',''):
        failures.append({'check':'Robot TTS runtime state/side provenance boundary'})
    faq_boundary = robot_sources.get('faqBoundary') or {}
    if [row.get('sourceUnitId') for row in faq_boundary.get('baseApplicable') or []] != ['FQ-P02-U17'] or [(row.get('sourceUnitId'),row.get('applicability')) for row in faq_boundary.get('excludedExpansion') or []] != [('FQ-P03-U15','expansion-neoflesh'),('FQ-P03-U17','expansion-neoflesh')] or 'do not resolve' not in faq_boundary.get('boundary',''):
        failures.append({'check':'Robot FAQ base/expansion applicability boundary'})
    excluded = robot_sources.get('excludedContent') or {}
    if {(row.get('guid'),row.get('cardId'),row.get('verdict')) for row in excluded.get('prototypeRobotCards') or []} != {('c24f3f',4404,'junk'),('d65fd6',4406,'junk')} or {(row.get('guid'),row.get('cardId'),row.get('verdict')) for row in excluded.get('expansionRobotCards') or []} != {('492017',591300,'expansion'),('a81e7e',591400,'expansion'),('37d67f',591500,'expansion')} or {row.get('guid') for row in excluded.get('securityRobotRoomNameCollisions') or []} != {'f4e834','9d92bc','4d4428','eb7a24'}:
        failures.append({'check':'Robot prototype/expansion/Room collision exclusion boundary'})
    robot_linked_backlog_ids = (robot_sources.get('familyCountEvidence',{}).get('backlog') or {}).get('linkedUnitIds') or []
    expected_linked_robot_backlog_ids = [
        'CARD:e613b1e23d25d91e','CARD:0e8c91aac8c15e46','CARD:c78d2a69189749dc',
        'CARD:db583cb973497fd2','CARD:40751b42f4610365','CARD:27a7014ae8011fa6',
        'RULE:ACT-ROBOT-001','RULE:ACT-TACTICAL-001','RULE:ITM-005','FAQ:FQ-P02-U17',
        *[f'VIS:{occurrence_id}' for occurrence_id in expected_robot_visual_ids],
    ]
    if robot_linked_backlog_ids != expected_linked_robot_backlog_ids or any((backlog_rows_by_id.get(unit_id) or {}).get('status') != 'pilot-covered' for unit_id in expected_linked_robot_backlog_ids):
        failures.append({'check':'Robot exact overlapping backlog-obligation closure'})

    # Independent base Intruder Attack family lock. The exact raw root-deck
    # children and full selectors define 19 generated cells plus one direct
    # face. Repeated titles, the parent sheet, the shared back, unused cell 17,
    # expansion decks, and licensed structured variants remain non-isomorphic.
    attack_rows = attack_sources.get('faces') or []
    attack_by_card = {row.get('ttsCardId'):row for row in attack_rows}
    if sha(attack_source_path) != PINNED_ATTACK_SOURCE_INDEX_HASH:
        failures.append({'check':'pinned Attack source index'})
    if attack_sources.get('counts') != EXPECTED_ATTACK_COUNTS or set(attack_by_card) != set(EXPECTED_ATTACK_OCCURRENCES) or len(attack_by_card) != len(attack_rows):
        failures.append({'check':'Attack source-index exact occurrence count'})
    expected_title_multiplicity = {'BITE':6,'BLOOD SENSE':1,'DEADLY CLAWS':3,'FURY':2,'INFECTING':1,'MISS':1,'SCRATCH':4,'TAIL ATTACK':2}
    if attack_sources.get('titleMultiplicity') != expected_title_multiplicity:
        failures.append({'check':'Attack repeated-title occurrence multiplicity lock'})
    base_attack_role = next((row for row in roles if row.get('role') == 'attacksDeck' and row.get('guid') == '34c73e'), {})
    root_attack_object = next((row for row in objects if row.get('guid') == '34c73e'), {})
    if base_attack_role.get('type') != 'DeckCustom' or base_attack_role.get('deck_nums') != ['3949','3991'] or base_attack_role.get('n_urls') != 3 or root_attack_object.get('parent') != [] or root_attack_object.get('type') != 'DeckCustom':
        failures.append({'check':'Attack root Lua role/CustomDeck closure'})
    attack_children = [row for row in objects if ['DeckCustom','34c73e',''] in (row.get('parent') or []) and row.get('gmnotes') == 'attack']
    attack_children_by_card = {int(row['card_id']):row for row in attack_children if row.get('card_id')}
    if set(attack_children_by_card) != set(EXPECTED_ATTACK_OCCURRENCES) or len(attack_children) != 20:
        failures.append({'check':'Attack exact full CardID child closure'})
    attack_table = next((row for row in secondary['licensedDigital']['structuredIndex']['tables'] if row.get('name') == 'INTRUDER_ATTACKS_DATA'), {})
    expected_attack_bga_keys = {value[5] for value in EXPECTED_ATTACK_OCCURRENCES.values()}
    if attack_table.get('count') != 15 or set(attack_table.get('keys') or []) != expected_attack_bga_keys:
        failures.append({'check':'Attack licensed-digital independent index closure'})
    attack_sheet_provenance = next((row for row in provenance if row.get('file') == 'cards/game/attack-151.jpg'), {})
    attack_back_provenance = next((row for row in provenance if row.get('file') == 'cards/game/attack-020.png'), {})
    attack_direct_provenance = next((row for row in provenance if row.get('file') == 'cards/game/attack-022.png'), {})
    if (attack_sheet_provenance.get('refs'),attack_back_provenance.get('refs'),attack_direct_provenance.get('refs')) != (20,21,2):
        failures.append({'check':'Attack FaceURL/BackURL provenance reference closure'})
    expected_attack_source_ids = set()
    for card_id,expected in EXPECTED_ATTACK_OCCURRENCES.items():
        source_id,path_value,source_sha,guid,cell,bga_key,rule_id,title,badge_types,badge_panels,panel_count,sentence_count,inline_refs,official_refs,question_refs = expected
        face = attack_by_card.get(card_id) or {}
        expected_attack_source_ids.add(source_id)
        selector = face.get('sourceSelector') or {}
        generated = selector.get('generatedCell')
        actual_tuple = (face.get('sourceId'),face.get('sourcePath'),face.get('sourceSha256'),face.get('ttsCardGuid'),(generated or {}).get('cellIndex'),(face.get('bgaOccurrence') or {}).get('key'),face.get('semanticRuleId'),face.get('printedTitle'))
        if actual_tuple != expected[:8]:
            failures.append({'check':'independently locked Attack occurrence crosswalk','ttsCardId':card_id})
        source_file = REPO/path_value
        if not source_file.is_file() or sha(source_file) != source_sha:
            failures.append({'check':'Attack live source hash','ttsCardId':card_id})
        child = attack_children_by_card.get(card_id) or {}
        expected_object_type = 'CardCustom' if cell is None else 'Card'
        expected_custom_deck = '3991' if cell is None else '3949'
        if child.get('guid') != guid or child.get('type') != expected_object_type or selector.get('key') != 'FaceURL' or selector.get('objectType') != expected_object_type or selector.get('fullCardId') != card_id or selector.get('guid') != guid or selector.get('parentDeckGuid') != '34c73e' or selector.get('customDeckId') != expected_custom_deck or selector.get('sideRole') != 'operative-face' or selector.get('cardIdModuloJoinUsed') is not False or selector.get('selectorGap') is not None:
            failures.append({'check':'Attack exact full CardID/GUID/CustomDeck selector projection','ttsCardId':card_id})
        if selector.get('backUrl') != 'https://steamusercontent-a.akamaihd.net/ugc/11924678148411699/14FCBEEBC01824DE1591E0218355C01ECC48C923/' or selector.get('url') == selector.get('backUrl'):
            failures.append({'check':'Attack FaceURL/BackURL role projection','ttsCardId':card_id})
        if cell is None:
            if generated is not None or selector.get('sourceRole') != 'direct-face' or selector.get('url') != 'https://steamusercontent-a.akamaihd.net/ugc/11925215517129770/8DF8175468EFA277EC2BD907070B7070D7810F54/':
                failures.append({'check':'Attack exact direct-face selector projection','ttsCardId':card_id})
        else:
            expected_cell_path = f'assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151_cards/card-{cell:02d}.png'
            expected_grid = {'columns':5,'rows':4,'cellWidth':827,'cellHeight':1111}
            if selector.get('sourceRole') != 'generated-cell-face' or not isinstance(generated,dict) or generated.get('sourceSheetId') != 'SRC-ATTACK-SHEET' or generated.get('sourceSheetPath') != 'assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151.jpg' or generated.get('sourceSheetSha256') != '7dd1613a0c9be312e4d4be2040469b9aac2775c9e178060a7346844bf8d23dce' or generated.get('grid') != expected_grid or generated.get('cellIndex') != cell or generated.get('row') != cell//5 or generated.get('column') != cell%5 or generated.get('cellPath') != expected_cell_path or selector.get('url') != 'https://steamusercontent-a.akamaihd.net/ugc/2468613527880234536/A0DC2BC12F4C9ECFE5AF1398ED52FD8746072DD8/':
                failures.append({'check':'Attack generated sheet/hash/grid/cell selector projection','ttsCardId':card_id})
        corpus_row = corpus_by_path.get(path_value) or {}
        if corpus_row.get('sourceSha256') != source_sha or not corpus_row.get('rulesTextPresent') or corpus_row.get('extractionState') not in {'verified-canonical','draft-full'}:
            failures.append({'check':'Attack closed-corpus occurrence projection','ttsCardId':card_id})
        body = face.get('printedBody') or ''
        if hashlib.sha256(body.encode()).hexdigest() != EXPECTED_ATTACK_BODY_DIGESTS[card_id]:
            failures.append({'check':'Attack exact body/punctuation/order drift','ttsCardId':card_id})
        panels = face.get('panels') or []
        panel_tuple = [(row.get('panelId'),row.get('readingOrder'),row.get('role'),row.get('operative')) for row in panels]
        expected_panel_tuple = [('P1',1,'title',False),('P2',2,'artwork',False),*[(f'P{index}',index,'applicability-and-effect-panel',True) for index in range(3,panel_count+1)]]
        if panel_tuple != expected_panel_tuple or (panels and panels[0].get('exactText') != title):
            failures.append({'check':'Attack exact physical panel roles/order','ttsCardId':card_id})
        for panel in panels[2:]:
            start,end = panel.get('bodyStart'),panel.get('bodyEnd')
            if not isinstance(start,int) or not isinstance(end,int) or body[start:end] != panel.get('exactText'):
                failures.append({'check':'Attack exact panel text/span projection','ttsCardId':card_id,'panelId':panel.get('panelId')})
        sentences = face.get('sentences') or []
        if len(sentences) != sentence_count or [row.get('sequence') for row in sentences] != list(range(1,sentence_count+1)) or len({row.get('sentenceId') for row in sentences}) != sentence_count:
            failures.append({'check':'Attack exact sentence IDs/order','ttsCardId':card_id})
        cursor = 0
        for sentence in sentences:
            start,end = sentence.get('start'),sentence.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or start < cursor or body[start:end] != sentence.get('exactText') or sentence.get('panelId') not in {row.get('panelId') for row in panels if row.get('operative')}:
                failures.append({'check':'Attack exact sentence text/span/panel projection','ttsCardId':card_id,'sentenceId':sentence.get('sentenceId')})
            cursor = end if isinstance(end,int) else cursor
        badges = face.get('applicabilityBadgeOccurrences') or []
        actual_badge_types = tuple((row.get('sourceScopedResolution') or {}).get('intruderType') for row in badges)
        actual_badge_panels = tuple(row.get('panelId') for row in badges)
        if actual_badge_types != badge_types or actual_badge_panels != badge_panels or [row.get('sequence') for row in badges] != list(range(1,len(badges)+1)) or any(not row.get('literalSourceToken') or not row.get('literalCyanComponentBbox') or (row.get('sourceScopedResolution') or {}).get('page40GlossaryAliasCreated') is not False or row.get('mappingScope') != f'exact Attack source occurrence TTS-ATTACK-{card_id}-FACE only' for row in badges):
            failures.append({'check':'Attack exact source-scoped applicability badge projection','ttsCardId':card_id})
        inline = face.get('inlineIconOccurrences') or []
        if tuple(row.get('semanticReferenceId') for row in inline) != inline_refs or [row.get('sequence') for row in inline] != list(range(1,len(inline)+1)) or any(row.get('mappingScope') != f'exact Attack source occurrence TTS-ATTACK-{card_id}-FACE only' for row in inline):
            failures.append({'check':'Attack exact inline icon occurrence projection','ttsCardId':card_id})
        if card_id == 394906 and (len(inline) != 1 or inline[0].get('sourceToken') != 'LOCAL_ICON:INLINE-1' or inline[0].get('semanticReferenceId') != 'icon.characterHealth' or inline[0].get('templateMatchScore') != 0.955931 or 'no-match row remains unchanged' not in inline[0].get('literalResolutionBoundary','')):
            failures.append({'check':'Attack local Character Health independent-resolution boundary'})
        selected_comparisons = face.get('selectedEvidenceComparisons') or {}
        if selected_comparisons.get('boundary') != 'Literal selected no-match/match rows are retained verbatim; source-scoped semantic projections do not rewrite them.':
            failures.append({'check':'Attack literal selected badge/icon evidence preservation','ttsCardId':card_id})
        bga = face.get('bgaOccurrence') or {}
        if bga.get('sourceId') != 'SRC-BGA-INTRUDER-ATTACKS' or bga.get('sourceSha256') != sha(REPO/'docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js') or bga.get('key') != bga_key or not bga.get('sourceBlockText') or bga.get('sourceBlockText') not in bga_text or not isinstance(bga.get('effectDesc'),list):
            failures.append({'check':'Attack licensed variant exact projection','ttsCardId':card_id})
        if tuple(face.get('officialCounterpartRefs') or []) != official_refs:
            failures.append({'check':'Attack official-visible counterpart projection','ttsCardId':card_id})
        join = face.get('joinEvidence') or {}
        basis_text = ' '.join(join.get('basis') or []).lower()
        if join.get('identityJoin') != 'explicit full occurrence crosswalk' or join.get('titleOnlyJoin') is not False or join.get('sourceCellOnlyJoin') is not False or join.get('folderOnlyJoin') is not False or join.get('cardIdModuloJoin') is not False or any(fragment not in basis_text for fragment in ('full cardid','guid','customdeck','faceurl','backurl','sheet/hash/grid/cell','ordered panels')):
            failures.append({'check':'Attack title/cell/folder/modulo join prohibited','ttsCardId':card_id})
        registry = source_by_id.get(source_id) or {}
        if (registry.get('path'),registry.get('sha256'),registry.get('authority'),registry.get('occurrenceId'),registry.get('evidenceRecord')) != (path_value,source_sha,'source-bound-component-scan',f'TTS-ATTACK-{card_id}-FACE',source_sha):
            failures.append({'check':'Attack source-registry exact face tuple','ttsCardId':card_id})
        backlog_id = 'CARD:' + source_sha[:16]
        backlog_row = backlog_rows_by_id.get(backlog_id) or {}
        if face.get('backlogUnitId') != backlog_id or backlog_row.get('sourcePath') != path_value or backlog_row.get('sourceLocator') != source_sha or backlog_row.get('pilotRuleIds') != [rule_id] or backlog_row.get('status') != 'pilot-covered':
            failures.append({'check':'Attack exact backlog tuple projection','ttsCardId':card_id})
    source_sheet = attack_sources.get('sourceSheet') or {}
    source_sheet_selector = source_sheet.get('sourceSelector') or {}
    expected_sheet_tuple = ('assets/tts-mod/extract/v2-dl/tree/cards/game/attack-151.jpg','7dd1613a0c9be312e4d4be2040469b9aac2775c9e178060a7346844bf8d23dce',[4135,4444],{'columns':5,'rows':4,'cellWidth':827,'cellHeight':1111},'FaceURL','3949',20,True)
    actual_sheet_tuple = (source_sheet.get('sourcePath'),source_sheet.get('sourceSha256'),source_sheet.get('dimensions'),source_sheet.get('grid'),source_sheet_selector.get('key'),source_sheet_selector.get('customDeckId'),source_sheet_selector.get('referenceCount'),source_sheet_selector.get('parentSheetNotRulesFace'))
    shared_back = attack_sources.get('sharedBack') or {}
    shared_back_selector = shared_back.get('sourceSelector') or {}
    expected_back_tuple = ('assets/tts-mod/extract/v2-dl/tree/cards/game/attack-020.png','3b99e8a683f506df4c33000ce62077770078f532b4c7d108846d4798c46ab6bd','BackURL','34c73e',1,20,21,False,False)
    actual_back_tuple = (shared_back.get('sourcePath'),shared_back.get('sourceSha256'),shared_back_selector.get('key'),shared_back_selector.get('guid'),shared_back_selector.get('rootDeckSelectorCount'),shared_back_selector.get('baseCardSelectorCount'),shared_back_selector.get('referenceCount'),shared_back.get('rulesTextPresent'),shared_back.get('separateRulesFace'))
    attack_sheet_registry = source_by_id.get('SRC-ATTACK-SHEET') or {}
    attack_back_registry = source_by_id.get('SRC-ATTACK-BACK') or {}
    attack_bga_registry = source_by_id.get('SRC-BGA-INTRUDER-ATTACKS') or {}
    actual_attack_source_ids = {row.get('sourceId') for row in source_rows if row.get('occurrenceId','').startswith('TTS-ATTACK-') and row.get('occurrenceId') not in {'TTS-ATTACK-GENERATED-SHEET','TTS-ATTACK-SHARED-BACK'}}
    if actual_sheet_tuple != expected_sheet_tuple or actual_back_tuple != expected_back_tuple or actual_attack_source_ids != expected_attack_source_ids or (attack_sheet_registry.get('path'),attack_sheet_registry.get('sha256'),attack_sheet_registry.get('occurrenceId')) != (expected_sheet_tuple[0],expected_sheet_tuple[1],'TTS-ATTACK-GENERATED-SHEET') or (attack_back_registry.get('path'),attack_back_registry.get('sha256'),attack_back_registry.get('occurrenceId')) != (expected_back_tuple[0],expected_back_tuple[1],'TTS-ATTACK-SHARED-BACK') or attack_bga_registry.get('occurrenceId') != 'INTRUDER_ATTACKS_DATA':
        failures.append({'check':'Attack source-registry face/sheet/back/licensed closure'})
    badge_method = attack_sources.get('badgeResolutionMethod') or {}
    if badge_method.get('mappingScope') != 'only the 57 exact badge occurrences enumerated below' or badge_method.get('familyMinimumWinningIou') != 0.8241 or badge_method.get('familyMinimumWinningMargin') != 0.3549 or badge_method.get('referenceTemplateOccurrenceIds') != ['ATK-394906-B01','ATK-394906-B02','ATK-394906-B03'] or 'no page-40' not in badge_method.get('literalNoMatchPreservation',''):
        failures.append({'check':'Attack applicability badge authority/no-alias lock'})
    official_counterparts = attack_sources.get('officialVisibleCounterparts') or []
    expected_official_ids = ['RB-P03-V01-ATTACK-BACK','RB-P03-V01-ATTACK-BITE','RB-P03-V01-ATTACK-DEADLY-CLAWS','RB-P32-V01-ATTACK-INFECTING']
    if [row.get('sourceOccurrenceId') for row in official_counterparts] != expected_official_ids or [row.get('parentOccurrenceId') for row in official_counterparts] != ['RB-P03-V01','RB-P03-V01','RB-P03-V01','RB-P32-V01']:
        failures.append({'check':'Attack official visual/text counterpart closure'})
    excluded_attack = attack_sources.get('excludedContent') or {}
    unused_cell = excluded_attack.get('unusedGeneratedCell') or {}
    expansion_decks = excluded_attack.get('expansionAttackDecks') or []
    if (unused_cell.get('cellIndex'),unused_cell.get('sourceSha256'),unused_cell.get('printedTitle'),unused_cell.get('backlogStatus')) != (17,'75dda99e22f47ea06d533242f1646707edbebf6378651002cc10a23047bfec44','SUMMONING','pending') or 'No root DeckID' not in unused_cell.get('selectorGap','') or {(row.get('guid'),row.get('scope')) for row in expansion_decks} != {('61a87c','expansion; excluded from base conclusions'),('3a25fc','expansion; excluded from base conclusions'),('9aefbc','expansion; excluded from base conclusions')}:
        failures.append({'check':'Attack unused-cell/expansion exclusion boundary'})
    attack_linked_backlog_ids = (attack_sources.get('familyCountEvidence',{}).get('backlog') or {}).get('linkedUnitIds') or []
    expected_attack_face_backlog_ids = ['CARD:'+EXPECTED_ATTACK_OCCURRENCES[card_id][2][:16] for card_id in sorted(EXPECTED_ATTACK_OCCURRENCES)]
    expected_linked_attack_backlog_ids = [*expected_attack_face_backlog_ids,'RULE:INT-004','RULE:INT-006','RULE:INT-008','FAQ:FQ-P02-U11','FAQ:FQ-P02-U16','FAQ:FQ-P02-U19','VIS:RB-P03-V01','VIS:RB-P32-V01']
    if attack_linked_backlog_ids != expected_linked_attack_backlog_ids or any((backlog_rows_by_id.get(unit_id) or {}).get('status') != 'pilot-covered' for unit_id in expected_linked_attack_backlog_ids):
        failures.append({'check':'Attack exact overlapping backlog-obligation closure'})

    # Independent base Queen Health family lock. Twelve exact physical
    # CardID/GUID occurrences project ten face assets and one shared back. The
    # duplicate assets, licensed ordinals, partial official faces, local number
    # displays, and Queen/Attack name collisions remain non-isomorphic.
    queen_rows = queen_health_sources.get('faces') or []
    queen_by_occurrence = {row.get('queenHealthOccurrenceId'):row for row in queen_rows}
    expected_queen_occurrence_ids = list(EXPECTED_QUEEN_HEALTH_OCCURRENCES)
    if sha(queen_health_source_path) != PINNED_QUEEN_HEALTH_SOURCE_INDEX_HASH:
        failures.append({'check':'pinned Queen Health source index'})
    if queen_health_sources.get('counts') != EXPECTED_QUEEN_HEALTH_COUNTS or list(queen_by_occurrence) != expected_queen_occurrence_ids or len(queen_by_occurrence) != len(queen_rows):
        failures.append({'check':'Queen Health source-index exact physical occurrence count'})
    base_queen_role = next((row for row in roles if row.get('role') == 'queenHealthDeck' and row.get('guid') == '9acd7f'), {})
    root_queen_object = next((row for row in objects if row.get('guid') == '9acd7f'), {})
    expected_queen_deck_nums = ['4241','4243','4245','4292','4581','5037','5038','5039','5040','5041','5042']
    if base_queen_role.get('type') != 'Deck' or base_queen_role.get('n_urls') != 11 or base_queen_role.get('deck_nums') != expected_queen_deck_nums or root_queen_object.get('type') != 'Deck' or root_queen_object.get('parent') != []:
        failures.append({'check':'Queen Health root Lua role/deck/container closure'})
    expected_saved_card_ids = [EXPECTED_QUEEN_HEALTH_OCCURRENCES[occurrence_id]['cardId'] for occurrence_id in expected_queen_occurrence_ids]
    raw_evidence = queen_health_sources.get('familyCountEvidence',{}).get('rawTtsDeck') or {}
    if raw_evidence.get('sourcePath') != 'assets/tts-mod/extract/nemesis_script_mod.bin' or raw_evidence.get('sourceSha256') != '8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68' or raw_evidence.get('deckIdsInSavedOrder') != expected_saved_card_ids or raw_evidence.get('savedOrderIsGameplayDeckOrder') is not False or raw_evidence.get('setupRequiresShuffle') is not True:
        failures.append({'check':'Queen Health raw DeckIDs/saved-order/setup-shuffle lock'})
    queen_children = [row for row in objects if ['Deck','9acd7f',''] in (row.get('parent') or []) and row.get('type') == 'CardCustom']
    queen_children_by_tuple = {(int(row['card_id']),row['guid']):row for row in queen_children if row.get('card_id')}
    expected_child_tuples = {(expected['cardId'],expected['guid']) for expected in EXPECTED_QUEEN_HEALTH_OCCURRENCES.values()}
    if set(queen_children_by_tuple) != expected_child_tuples or len(queen_children) != 12:
        failures.append({'check':'Queen Health exact full CardID/GUID child closure'})
    expected_expansion_roles = {('99e2ce','Neoflesh'),('3b65b3','Sangrevores'),('6963a5','Carnomorph')}
    excluded_queen_decks = (queen_health_sources.get('excludedContent') or {}).get('expansionQueenHealthDecks') or []
    if {(row.get('guid'),row.get('expansion')) for row in excluded_queen_decks} != expected_expansion_roles or any(row.get('scope') != 'expansion; excluded from base conclusions' for row in excluded_queen_decks):
        failures.append({'check':'Queen Health base/expansion role boundary'})
    queen_table = next((row for row in secondary['licensedDigital']['structuredIndex']['tables'] if row.get('name') == 'QUEEN_CARDS_DATA'), {})
    expected_queen_bga = {
        'QueenHealthCard1':(0,'Repel the Queen.'),'QueenHealthCard2':(0,'Activate the Queen.'),'QueenHealthCard3':(0,'Place the Queen back in the pool.'),
        'QueenHealthCard4':(1,'Repel the Queen.'),'QueenHealthCard5':(1,'Repel the Queen.'),'QueenHealthCard6':(1,'Add all Queen tokens to the bag.'),
        'QueenHealthCard7':(1,'Each <CHARACTER> in the Room with the Queen draws 2<ACTION-CARD>.'),'QueenHealthCard8':(2,'Repel the Queen.'),
        'QueenHealthCard9':(2,'Each <CHARACTER> in the Room with the Queen makes a Noise roll.'),'QueenHealthCard10':(3,'Activate the Queen.'),
        'QueenHealthCard11':(3,'Activate the Queen.'),'QueenHealthCard12':(3,'Place a <MALFUNCTION> in the Room with the Queen.'),
    }
    licensed_queen_rows = queen_health_sources.get('licensedDigitalOccurrences') or []
    licensed_queen_by_key = {row.get('key'):row for row in licensed_queen_rows}
    if queen_table.get('count') != 12 or set(queen_table.get('keys') or []) != set(expected_queen_bga) or list(licensed_queen_by_key) != list(expected_queen_bga):
        failures.append({'check':'Queen Health licensed-digital independent occurrence closure'})
    for key,expected in expected_queen_bga.items():
        row = licensed_queen_by_key.get(key) or {}
        if (row.get('discard'),row.get('effectDesc')) != expected or row.get('structuredOrdinalIsNotPrintedCardNumberOrDeckOrder') is not True or not row.get('sourceBlockText') or row.get('sourceBlockText') not in bga_text:
            failures.append({'check':'Queen Health licensed exact row/ordinal boundary','key':key})
    queen_provenance_by_tuple = {}
    queen_back_provenance = None
    for provenance_row in provenance:
        for obj in provenance_row.get('objects') or []:
            if obj.get('key') == 'BackURL' and obj.get('guid') == '9acd7f':
                queen_back_provenance = provenance_row
            key = (obj.get('cardId'),obj.get('guid'))
            if obj.get('key') == 'FaceURL' and key in expected_child_tuples and ['Deck','9acd7f',''] in (obj.get('parent') or []):
                queen_provenance_by_tuple[key] = (provenance_row,obj)
    if set(queen_provenance_by_tuple) != expected_child_tuples or not queen_back_provenance or queen_back_provenance.get('refs') != 13:
        failures.append({'check':'Queen Health FaceURL/BackURL provenance closure'})
    expected_queen_source_ids = set()
    expected_backlog_rules = {}
    for occurrence_id,expected in EXPECTED_QUEEN_HEALTH_OCCURRENCES.items():
        face = queen_by_occurrence.get(occurrence_id) or {}
        expected_queen_source_ids.add('SRC-QUEEN-HEALTH-'+occurrence_id.removeprefix('TTS-QUEEN-HEALTH-').removesuffix('-FACE'))
        actual_tuple = (face.get('ttsSavedSequence'),face.get('ttsCardId'),face.get('ttsCardGuid'),face.get('customDeckId'),face.get('sourcePath'),face.get('sourceSha256'),face.get('printedDiscardCount'),(face.get('bgaVariantCandidates') or {}).get('candidateKeys'),face.get('semanticRuleId'))
        expected_tuple = (expected['sequence'],expected['cardId'],expected['guid'],expected['customDeckId'],expected['path'],expected['sha256'],expected['discard'],expected['bgaKeys'],expected['ruleId'])
        if actual_tuple != expected_tuple:
            failures.append({'check':'independently locked Queen Health physical occurrence crosswalk','occurrenceId':occurrence_id})
        source_file = REPO/expected['path']
        if not source_file.is_file() or sha(source_file) != expected['sha256']:
            failures.append({'check':'Queen Health live face hash','occurrenceId':occurrence_id})
        selector = face.get('sourceSelector') or {}
        provenance_row,obj = queen_provenance_by_tuple.get((expected['cardId'],expected['guid']), ({},{}))
        derived_path = 'assets/tts-mod/extract/v2-dl/tree/' + provenance_row.get('file','')
        if derived_path != expected['path'] or selector.get('key') != 'FaceURL' or selector.get('objectType') != 'CardCustom' or selector.get('fullCardId') != expected['cardId'] or selector.get('guid') != expected['guid'] or selector.get('parentDeckGuid') != '9acd7f' or selector.get('customDeckId') != expected['customDeckId'] or selector.get('url') != provenance_row.get('url') or selector.get('sideRole') != 'operative-number-and-effect-face' or selector.get('sourceRole') != 'direct-composite-face' or selector.get('generatedSpriteSheetCell') is not False or selector.get('selectorGap') is not None or selector.get('cardIdModuloJoinUsed') is not False or selector.get('url') == selector.get('backUrl'):
            failures.append({'check':'Queen Health exact CardID/GUID/FaceURL selector projection','occurrenceId':occurrence_id})
        corpus_row = corpus_by_path.get(expected['path']) or {}
        body = face.get('printedBody') or ''
        if corpus_row.get('sourceSha256') != expected['sha256'] or corpus_row.get('printedData',{}).get('body') != body or not corpus_row.get('rulesTextPresent') or hashlib.sha256(body.encode()).hexdigest() != expected['bodyDigest']:
            failures.append({'check':'Queen Health exact body/order/punctuation lock','occurrenceId':occurrence_id})
        registry_source_id = 'SRC-QUEEN-HEALTH-'+occurrence_id.removeprefix('TTS-QUEEN-HEALTH-').removesuffix('-FACE')
        registry = source_by_id.get(registry_source_id) or {}
        if face.get('sourceId') != registry_source_id or (registry.get('path'),registry.get('sha256'),registry.get('authority'),registry.get('occurrenceId'),registry.get('evidenceRecord')) != (expected['path'],expected['sha256'],'source-bound-component-scan',occurrence_id,expected['sha256']):
            failures.append({'check':'Queen Health source-registry exact physical tuple','occurrenceId':occurrence_id})
        panels = face.get('panels') or []
        expected_panel_tuple = [('P1',1,'discard-count-and-artwork-panel',True),('P2',2,'conditional-special-effect-panel',True)]
        panel_tuple = [(row.get('panelId'),row.get('readingOrder'),row.get('role'),row.get('operative')) for row in panels]
        if panel_tuple != expected_panel_tuple or (panels and panels[0].get('heading') != 'Discard'):
            failures.append({'check':'Queen Health exact two-panel roles/order','occurrenceId':occurrence_id})
        for panel in panels:
            start,end = panel.get('bodyStart'),panel.get('bodyEnd')
            expected_panel_text = body[start:end] if isinstance(start,int) and isinstance(end,int) else None
            if panel.get('panelId') == 'P1':
                expected_panel_text = 'Discard\n' + (expected_panel_text or '')
            if not isinstance(start,int) or not isinstance(end,int) or panel.get('exactText') != expected_panel_text:
                failures.append({'check':'Queen Health exact panel body/span projection','occurrenceId':occurrence_id,'panelId':panel.get('panelId')})
        sentences = face.get('sentences') or []
        if len(sentences) != expected['sentences'] or [row.get('sequence') for row in sentences] != list(range(1,expected['sentences']+1)) or len({row.get('sentenceId') for row in sentences}) != expected['sentences']:
            failures.append({'check':'Queen Health exact source sentence count/order','occurrenceId':occurrence_id})
        cursor = 0
        for sentence in sentences:
            start,end = sentence.get('start'),sentence.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or start < cursor or body[start:end] != sentence.get('exactText') or sentence.get('panelId') not in {'P1','P2'}:
                failures.append({'check':'Queen Health exact source sentence text/panel projection','occurrenceId':occurrence_id,'sentenceId':sentence.get('sentenceId')})
            cursor = end if isinstance(end,int) else cursor
        icons = face.get('iconOccurrences') or []
        if [row.get('semanticReferenceId') for row in icons] != expected['iconRefs'] or [row.get('sequence') for row in icons] != list(range(1,len(icons)+1)) or len({row.get('occurrenceId') for row in icons}) != len(icons):
            failures.append({'check':'Queen Health exact local/icon occurrence projection','occurrenceId':occurrence_id})
        local = icons[0] if icons else {}
        if local.get('printedNumericValue') != expected['discard'] or local.get('semanticReferenceId') is not None or local.get('page40TokenAssigned') is not False or not str(local.get('sourceToken','')).startswith('LOCAL-DISCARD-DISPLAY-') or 'not a Shoot/Burst/Health/damage icon alias' not in local.get('resolutionBoundary',''):
            failures.append({'check':'Queen Health local number no-alias/value lock','occurrenceId':occurrence_id})
        for icon in icons[1:]:
            start,end = icon.get('start'),icon.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or body[start:end] != f"[{icon.get('sourceToken')}]" or icon.get('semanticReferenceId') != f"icon.{icon.get('sourceToken')}" or icon.get('page40TokenAssigned') is not True or icon.get('mappingScope') != f'exact Queen Health source occurrence {occurrence_id} only':
                failures.append({'check':'Queen Health exact matched icon token/span/scope','occurrenceId':occurrence_id,'iconId':icon.get('occurrenceId')})
        bga_candidates = face.get('bgaVariantCandidates') or {}
        candidate_rows = bga_candidates.get('candidates') or []
        if bga_candidates.get('sourceId') != 'SRC-BGA-QUEEN-HEALTH' or bga_candidates.get('sourceSha256') != sha(REPO/'docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js') or [row.get('key') for row in candidate_rows] != expected['bgaKeys'] or any(row.get('sourceBlockText') not in bga_text for row in candidate_rows) or bga_candidates.get('oneToOneCopyAssignmentAsserted') != (len(expected['bgaKeys']) == 1) or 'not printed card numbers' not in bga_candidates.get('boundary',''):
            failures.append({'check':'Queen Health licensed variant/candidate-copy boundary','occurrenceId':occurrence_id})
        if face.get('officialCounterpartRefs') != expected['official']:
            failures.append({'check':'Queen Health official-visible counterpart projection','occurrenceId':occurrence_id})
        join = face.get('joinEvidence') or {}
        basis_text = ' '.join(join.get('basis') or []).lower()
        if join.get('identityJoin') != 'exact physical occurrence and source-asset projection' or join.get('titleOnlyJoin') is not False or join.get('folderOnlyJoin') is not False or join.get('cardIdModuloJoin') is not False or join.get('bgaOrdinalJoin') is not False or any(fragment not in basis_text for fragment in ('full cardid/guid','faceurl','backurl','sha-256','ordered two-panel','candidate-set')):
            failures.append({'check':'Queen Health title/folder/modulo/BGA-ordinal join prohibited','occurrenceId':occurrence_id})
        backlog_id = 'CARD:'+expected['sha256'][:16]
        expected_backlog_rules.setdefault(backlog_id,[]).append(expected['ruleId'])
        if face.get('backlogUnitId') != backlog_id:
            failures.append({'check':'Queen Health exact backlog tuple projection','occurrenceId':occurrence_id})
    for backlog_id,rule_ids in expected_backlog_rules.items():
        expected_path = next(expected['path'] for expected in EXPECTED_QUEEN_HEALTH_OCCURRENCES.values() if 'CARD:'+expected['sha256'][:16] == backlog_id)
        expected_sha = next(expected['sha256'] for expected in EXPECTED_QUEEN_HEALTH_OCCURRENCES.values() if 'CARD:'+expected['sha256'][:16] == backlog_id)
        backlog_row = backlog_rows_by_id.get(backlog_id) or {}
        if backlog_row.get('sourcePath') != expected_path or backlog_row.get('sourceLocator') != expected_sha or backlog_row.get('pilotRuleIds') != rule_ids or backlog_row.get('status') != 'pilot-covered':
            failures.append({'check':'Queen Health exact backlog tuple projection','backlogUnitId':backlog_id})
    actual_queen_source_ids = {row.get('sourceId') for row in source_rows if row.get('occurrenceId','').startswith('TTS-QUEEN-HEALTH-') and row.get('occurrenceId') != 'TTS-QUEEN-HEALTH-SHARED-BACK'}
    queen_back = queen_health_sources.get('sharedBack') or {}
    queen_back_selector = queen_back.get('sourceSelector') or {}
    queen_back_registry = source_by_id.get('SRC-QUEEN-HEALTH-BACK') or {}
    queen_bga_registry = source_by_id.get('SRC-BGA-QUEEN-HEALTH') or {}
    objective_help_registry = source_by_id.get('SRC-OBJECTIVE-HELP') or {}
    expected_queen_back_tuple = ('assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-017.png','c02d1ae4f5add1502d16182823507ce412869a5264e134ffaa36f18d7b60b6fc','BackURL','Deck','9acd7f',1,12,13,False,False,False)
    actual_queen_back_tuple = (queen_back.get('sourcePath'),queen_back.get('sourceSha256'),queen_back_selector.get('key'),queen_back_selector.get('objectType'),queen_back_selector.get('guid'),queen_back_selector.get('rootDeckSelectorCount'),queen_back_selector.get('baseCardSelectorCount'),queen_back_selector.get('referenceCount'),queen_back.get('rulesTextPresent'),queen_back.get('separateRulesFace'),queen_back.get('numberedBack'))
    if actual_queen_source_ids != expected_queen_source_ids or actual_queen_back_tuple != expected_queen_back_tuple or (queen_back_registry.get('path'),queen_back_registry.get('sha256'),queen_back_registry.get('occurrenceId')) != (expected_queen_back_tuple[0],expected_queen_back_tuple[1],'TTS-QUEEN-HEALTH-SHARED-BACK') or queen_bga_registry.get('occurrenceId') != 'QUEEN_CARDS_DATA' or objective_help_registry.get('occurrenceId') != 'OBJECTIVE-HELP-SHEET':
        failures.append({'check':'Queen Health source-registry face/back/licensed/Objective closure'})
    official_queen = queen_health_sources.get('officialVisibleCounterparts') or []
    expected_official_queen_ids = ['RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL','RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL','RB-P03-V01-QH-BACK','RB-P35-V02-QH-FACE-DISCARD-1-REPEL','RB-P35-V02-QH-BACK']
    if [row.get('sourceOccurrenceId') for row in official_queen] != expected_official_queen_ids or [row.get('parentOccurrenceId') for row in official_queen] != ['RB-P03-V01','RB-P03-V01','RB-P03-V01','RB-P35-V02','RB-P35-V02'] or any(row.get('sourceScopedOnly') is not True for row in official_queen):
        failures.append({'check':'Queen Health official face/back occurrence closure'})
    hits_track = queen_health_sources.get('queenHitsTrack') or {}
    track_spaces = hits_track.get('spacesInPrintedOrder') or []
    local_symbols = queen_health_sources.get('officialLocalSymbols') or []
    if [row.get('printedValue') for row in track_spaces] != [0,1,2,3,4,None] or [row.get('sequence') for row in track_spaces] != list(range(1,7)) or track_spaces[-1].get('semanticReferenceId') is not None or track_spaces[-1].get('page40TokenAssigned') is not False or len(local_symbols) != 2 or any(row.get('semanticReferenceId') is not None or row.get('page40TokenAssigned') is not False or 'queen-head/blob-plus-style' not in row.get('literalAppearance','') for row in local_symbols):
        failures.append({'check':'Queen Health track/terminal local-symbol no-alias lock'})
    queen_excluded = queen_health_sources.get('excludedContent') or {}
    collision_rows = queen_excluded.get('attackAndNonHealthCollisions') or []
    if queen_excluded.get('prototypePlaceholderParentSheetBoundary') != 'The base root deck has twelve direct CardCustom children, zero generated cells, zero source sheets, zero selector gaps, and no separately selected prototype or placeholder face.' or len(collision_rows) != 4 or collision_rows[0].get('count') != 20 or 'not a thirteenth rules face' not in queen_excluded.get('sharedBackBoundary','') or 'do not collapse copies' not in queen_excluded.get('duplicateFaceBoundary',''):
        failures.append({'check':'Queen Health prototype/back/duplicate/Attack-collision exclusion boundary'})
    queen_linked_backlog_ids = (queen_health_sources.get('familyCountEvidence',{}).get('backlog') or {}).get('linkedUnitIds') or []
    expected_queen_face_backlog_ids = list(expected_backlog_rules)
    expected_linked_queen_backlog_ids = [*expected_queen_face_backlog_ids,'RULE:ACT-SHOOT-001','RULE:ACT-BURST-001','RULE:INT-001','RULE:INT-003','RULE:INT-007','RULE:INT-010','RULE:INT-011','RULE:RT-011','FAQ:FQ-P02-U03','VIS:RB-P03-V01','VIS:RB-P35-V01','VIS:RB-P35-V02','VIS:RB-P35-V03','OBJ:P1-GT-06','OBJ:P2-GT-06']
    if queen_linked_backlog_ids != expected_linked_queen_backlog_ids or any((backlog_rows_by_id.get(unit_id) or {}).get('status') != 'pilot-covered' for unit_id in expected_linked_queen_backlog_ids):
        failures.append({'check':'Queen Health exact overlapping backlog-obligation closure'})

    # Independent base Serious Wound family lock. The raw root Deck contains
    # 27 physical CardID/GUID selectors: seven selected 3x3-sheet cells with
    # three copies each and two direct faces with three copies each. Two other
    # generated cells remain selector-gap variants; title/body/modulo joins are
    # prohibited across TTS, official, and licensed occurrences.
    serious_wound_rows = serious_wound_sources.get('faces') or []
    serious_wound_by_occurrence = {row.get('seriousWoundOccurrenceId'):row for row in serious_wound_rows}
    serious_wound_assets = serious_wound_sources.get('sourceFaceAssets') or []
    serious_wound_assets_by_key = {row.get('assetKey'):row for row in serious_wound_assets}
    expected_serious_wound_ids = list(EXPECTED_SERIOUS_WOUND_OCCURRENCES)
    if sha(serious_wound_source_path) != PINNED_SERIOUS_WOUND_SOURCE_INDEX_HASH:
        failures.append({'check':'pinned Serious Wound source index'})
    if serious_wound_sources.get('counts') != EXPECTED_SERIOUS_WOUND_COUNTS or list(serious_wound_by_occurrence) != expected_serious_wound_ids or len(serious_wound_rows) != 27:
        failures.append({'check':'Serious Wound source-index exact physical occurrence count'})
    if set(serious_wound_assets_by_key) != set(EXPECTED_SERIOUS_WOUND_ASSETS) or len(serious_wound_assets_by_key) != len(serious_wound_assets):
        failures.append({'check':'Serious Wound exact source-face asset/variant closure'})
    base_wound_role = next((row for row in roles if row.get('role') == 'seriouswoundDeck' and row.get('guid') == 'b75145'), {})
    all_wound_roles = [row for row in roles if row.get('role') == 'seriouswoundDeck']
    root_wound_object = next((row for row in objects if row.get('guid') == 'b75145'), {})
    wound_children = [row for row in objects if ['Deck','b75145',''] in (row.get('parent') or []) and row.get('gmnotes') == 'wound']
    all_wound_tagged = [row for row in objects if row.get('gmnotes') == 'wound']
    expected_wound_child_tuples = {(row['cardId'],row['guid']) for row in EXPECTED_SERIOUS_WOUND_OCCURRENCES.values()}
    if len(all_wound_roles) != 1 or base_wound_role.get('type') != 'Deck' or base_wound_role.get('n_urls') != 4 or base_wound_role.get('deck_nums') != ['38','4048','5439'] or root_wound_object.get('type') != 'Deck' or root_wound_object.get('parent') != [] or len(wound_children) != 27 or len(all_wound_tagged) != 27 or {(int(row['card_id']),row['guid']) for row in wound_children} != expected_wound_child_tuples:
        failures.append({'check':'Serious Wound root Lua role/deck/tag/container closure'})
    expected_saved_wound_ids = [EXPECTED_SERIOUS_WOUND_OCCURRENCES[occurrence_id]['cardId'] for occurrence_id in expected_serious_wound_ids]
    raw_wound_evidence = serious_wound_sources.get('familyCountEvidence',{}).get('rawTtsDeck') or {}
    if raw_wound_evidence.get('sourcePath') != 'assets/tts-mod/extract/nemesis_script_mod.bin' or raw_wound_evidence.get('sourceSha256') != '8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68' or raw_wound_evidence.get('deckIdsInSavedOrder') != expected_saved_wound_ids or raw_wound_evidence.get('savedOrderIsGameplayDeckOrder') is not False or raw_wound_evidence.get('setupRequiresShuffle') is not True or raw_wound_evidence.get('physicalFaceCount') != 27:
        failures.append({'check':'Serious Wound raw DeckIDs/saved-order/setup-shuffle lock'})
    expected_title_multiplicity = {'ARM':3,'BLEEDING':3,'BODY':3,'EYES':3,'GUTS':3,'HAND':3,'KNEE':3,'LEG':3,'LUNGS':3}
    if serious_wound_sources.get('titleMultiplicity') != expected_title_multiplicity:
        failures.append({'check':'Serious Wound repeated-title multiplicity/no-collapse lock'})

    for asset_key,expected in EXPECTED_SERIOUS_WOUND_ASSETS.items():
        expected_path,expected_sha,expected_title,expected_role,expected_cell,expected_sentence_count,expected_icon_refs,expected_body_digest = expected
        asset = serious_wound_assets_by_key.get(asset_key) or {}
        actual_tuple = (asset.get('sourcePath'),asset.get('sourceSha256'),asset.get('printedTitle'),asset.get('sourceRole'),asset.get('generatedCell'))
        if actual_tuple != expected[:5] or not (REPO/expected_path).is_file() or sha(REPO/expected_path) != expected_sha:
            failures.append({'check':'Serious Wound independently locked source-face asset tuple','assetKey':asset_key})
        body = asset.get('printedBody') or ''
        if hashlib.sha256(body.encode()).hexdigest() != expected_body_digest:
            failures.append({'check':'Serious Wound exact body/punctuation/order lock','assetKey':asset_key})
        regions = asset.get('regions') or []
        if [row.get('regionId') for row in regions] != ['R1','R2','R3'] or [row.get('role') for row in regions] != ['artwork-and-diagnostic-interface','printed-heading','operative-effect'] or [row.get('operative') for row in regions] != [False,False,True] or (regions[1] if len(regions)>1 else {}).get('exactText') != expected_title or (regions[2] if len(regions)>2 else {}).get('exactText') != body or asset.get('semanticBodyPartTraitOrSeverityInferred') is not False:
            failures.append({'check':'Serious Wound exact region roles/order/no-inferred-anatomy lock','assetKey':asset_key})
        panels = asset.get('panels') or []
        if [row.get('panelId') for row in panels] != ['P1','P2'] or [row.get('role') for row in panels] != ['printed-title-panel','operative-effect-panel'] or [row.get('operative') for row in panels] != [False,True] or [row.get('regionId') for row in panels] != ['R2','R3'] or (panels[0] if panels else {}).get('exactText') != expected_title or (panels[1] if len(panels)>1 else {}).get('exactText') != body:
            failures.append({'check':'Serious Wound exact source panel roles/order/region linkage','assetKey':asset_key})
        sentences = asset.get('sentences') or []
        if len(sentences) != expected_sentence_count or [row.get('sequence') for row in sentences] != list(range(1,len(sentences)+1)) or len({row.get('sentenceId') for row in sentences}) != len(sentences):
            failures.append({'check':'Serious Wound exact sentence occurrence count/order','assetKey':asset_key})
        cursor = 0
        for sentence in sentences:
            start,end = sentence.get('start'),sentence.get('end')
            if not isinstance(start,int) or not isinstance(end,int) or start < cursor or body[start:end] != sentence.get('exactText') or sentence.get('regionId') != 'R3' or sentence.get('panelId') != 'P2':
                failures.append({'check':'Serious Wound exact sentence span/punctuation lock','assetKey':asset_key,'sentenceId':sentence.get('sentenceId')})
            cursor = end if isinstance(end,int) else cursor
        icons = asset.get('iconOccurrences') or []
        if [row.get('semanticReferenceId') for row in icons] != list(expected_icon_refs) or [row.get('sequence') for row in icons] != list(range(1,len(icons)+1)) or len({row.get('assetIconOccurrenceId') for row in icons}) != len(icons) or any((row.get('semanticReferenceId') is None) != (row.get('page40TokenAssigned') is False) or row.get('panelId') != 'P2' for row in icons):
            failures.append({'check':'Serious Wound exact source-local icon occurrence projection','assetKey':asset_key})
        selected = expected_role != 'generated-cell-selector-gap-variant'
        gap = asset.get('selectorGap')
        if asset.get('selectedByRootDeck') is not selected or (selected and gap is not None) or (not selected and (not isinstance(gap,dict) or gap.get('status') != 'explicit-no-root-DeckID-GUID-selector' or gap.get('cardIdModuloJoinUsed') is not False)):
            failures.append({'check':'Serious Wound generated selector-gap closure','assetKey':asset_key})

    expected_serious_wound_source_ids = set()
    expected_wound_backlog_rules = {}
    for occurrence_id,expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.items():
        face = serious_wound_by_occurrence.get(occurrence_id) or {}
        code = occurrence_id.removeprefix('TTS-SERIOUS-WOUND-').removesuffix('-FACE')
        expected_source_id = 'SRC-SERIOUS-WOUND-'+code
        expected_serious_wound_source_ids.add(expected_source_id)
        selector = face.get('sourceSelector') or {}
        actual_tuple = (face.get('ttsSavedSequence'),face.get('ttsCardId'),face.get('ttsCardGuid'),face.get('customDeckId'),face.get('sourcePath'),face.get('sourceSha256'),face.get('printedTitle'),selector.get('sourceRole'),selector.get('generatedCell'),face.get('semanticRuleId'))
        expected_tuple = (expected['sequence'],expected['cardId'],expected['guid'],expected['customDeckId'],expected['path'],expected['sha256'],expected['title'],expected['sourceRole'],expected['cell'],expected['ruleId'])
        if actual_tuple != expected_tuple:
            failures.append({'check':'independently locked Serious Wound physical occurrence crosswalk','occurrenceId':occurrence_id})
        if selector.get('key') != 'FaceURL' or selector.get('fullCardId') != expected['cardId'] or selector.get('guid') != expected['guid'] or selector.get('parentDeckGuid') != 'b75145' or selector.get('customDeckId') != expected['customDeckId'] or selector.get('sideRole') != 'operative-serious-wound-face' or selector.get('selectorGap') is not None or selector.get('cardIdModuloJoinUsed') is not False or selector.get('backUrl') != 'https://steamusercontent-a.akamaihd.net/ugc/2468613527880235898/A32D91672CA7CCBA01C44C27791836D0E634CE2A/':
            failures.append({'check':'Serious Wound exact CardID/GUID/FaceURL/BackURL selector projection','occurrenceId':occurrence_id})
        if expected['sourceRole'] == 'generated-cell-face':
            if selector.get('generatedSpriteSheetCell') is not True or selector.get('sourceSheetPath') != 'assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149.jpg' or selector.get('sourceSheetSha256') != 'fe8ce9585027cdde1bef962dbbafd5d615ef9ffe060d1114d1ec3fd55682349b' or selector.get('sourceSheetGrid') != {'columns':3,'rows':3} or selector.get('generatedCell') != expected['cell']:
                failures.append({'check':'Serious Wound generated sheet/hash/grid/cell selector projection','occurrenceId':occurrence_id})
        elif selector.get('generatedSpriteSheetCell') is not False or selector.get('sourceSheetPath') is not None or selector.get('generatedCell') is not None:
            failures.append({'check':'Serious Wound direct/generated face selector inversion','occurrenceId':occurrence_id})
        if hashlib.sha256((face.get('printedBody') or '').encode()).hexdigest() != expected['bodyDigest']:
            failures.append({'check':'Serious Wound exact body/punctuation/order lock','occurrenceId':occurrence_id})
        regions = face.get('regions') or []
        if len(regions) != 3 or [row.get('role') for row in regions] != ['artwork-and-diagnostic-interface','printed-heading','operative-effect'] or [row.get('operative') for row in regions] != [False,False,True] or not all(row.get('regionId','').startswith(f'SW-{expected["cardId"]}-{expected["guid"].upper()}-R') for row in regions):
            failures.append({'check':'Serious Wound exact physical region roles/order','occurrenceId':occurrence_id})
        panels = face.get('panels') or []
        if len(panels) != 2 or [row.get('role') for row in panels] != ['printed-title-panel','operative-effect-panel'] or [row.get('operative') for row in panels] != [False,True] or panels[0].get('regionId') != regions[1].get('regionId') or panels[1].get('regionId') != regions[2].get('regionId'):
            failures.append({'check':'Serious Wound exact physical panel roles/order/region linkage','occurrenceId':occurrence_id})
        if len(face.get('sentences') or []) != expected['sentences'] or [row.get('semanticReferenceId') for row in face.get('iconOccurrences') or []] != expected['iconRefs'] or any(row.get('panelId') != (panels[1].get('panelId') if len(panels)>1 else None) for row in (face.get('sentences') or []) + (face.get('iconOccurrences') or [])):
            failures.append({'check':'Serious Wound exact physical text/icon projection','occurrenceId':occurrence_id})
        join = face.get('joinEvidence') or {}
        basis = ' '.join(join.get('basis') or []).lower()
        if join.get('identityJoin') != 'exact physical occurrence and source-asset projection' or any(join.get(key) is not False for key in ('titleOnlyJoin','bodyResemblanceJoin','folderOnlyJoin','sequenceOnlyJoin','cardIdModuloJoin','licensedKeyJoin')) or any(fragment not in basis for fragment in ('full cardid/guid','faceurl','backurl','sha-256')):
            failures.append({'check':'Serious Wound title/body/folder/sequence/modulo/licensed join prohibited','occurrenceId':occurrence_id})
        if (face.get('licensedCrosswalk') or {}).get('status') != 'not-asserted' or (face.get('officialCrosswalk') or {}).get('status') != 'not-asserted' or face.get('semanticBodyPartTraitOrSeverityInferred') is not False:
            failures.append({'check':'Serious Wound authority/variant/anatomy non-join boundary','occurrenceId':occurrence_id})
        registry = source_by_id.get(expected_source_id) or {}
        if (registry.get('path'),registry.get('sha256'),registry.get('authority'),registry.get('occurrenceId'),registry.get('evidenceRecord')) != (expected['path'],expected['sha256'],'source-bound-component-scan',occurrence_id,expected['sha256']):
            failures.append({'check':'Serious Wound source-registry exact physical tuple','occurrenceId':occurrence_id})
        backlog_id = 'CARD:'+expected['sha256'][:16]
        expected_wound_backlog_rules.setdefault(backlog_id,[]).append(expected['ruleId'])
        if face.get('backlogUnitId') != backlog_id:
            failures.append({'check':'Serious Wound exact backlog tuple projection','occurrenceId':occurrence_id})

    for asset_key in ('sheet-04','sheet-06'):
        expected_path,expected_sha,*_ = EXPECTED_SERIOUS_WOUND_ASSETS[asset_key]
        expected_wound_backlog_rules['CARD:'+expected_sha[:16]] = ['SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001']
    for backlog_id,rule_ids in expected_wound_backlog_rules.items():
        expected_path = next(value[0] for value in EXPECTED_SERIOUS_WOUND_ASSETS.values() if 'CARD:'+value[1][:16] == backlog_id)
        expected_sha = next(value[1] for value in EXPECTED_SERIOUS_WOUND_ASSETS.values() if 'CARD:'+value[1][:16] == backlog_id)
        backlog_row = backlog_rows_by_id.get(backlog_id) or {}
        if backlog_row.get('sourcePath') != expected_path or backlog_row.get('sourceLocator') != expected_sha or backlog_row.get('pilotRuleIds') != rule_ids or backlog_row.get('status') != 'pilot-covered':
            failures.append({'check':'Serious Wound exact backlog tuple projection','backlogUnitId':backlog_id})

    actual_serious_wound_source_ids = {row.get('sourceId') for row in source_rows if row.get('occurrenceId','').startswith('TTS-SERIOUS-WOUND-') and '-VARIANT-' not in row.get('occurrenceId','') and row.get('occurrenceId') not in {'TTS-SERIOUS-WOUND-PARENT-SHEET-38','TTS-SERIOUS-WOUND-SHARED-BACK'}}
    sheet = serious_wound_sources.get('sourceSheet') or {}
    back = serious_wound_sources.get('sharedBack') or {}
    sheet_selector = sheet.get('sourceSelector') or {}
    back_selector = back.get('sourceSelector') or {}
    if actual_serious_wound_source_ids != expected_serious_wound_source_ids or (sheet.get('sourcePath'),sheet.get('sourceSha256'),sheet_selector.get('key'),sheet_selector.get('customDeckId'),sheet_selector.get('grid'),sheet_selector.get('referenceCount'),sheet.get('rulesFaceCounted')) != ('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149.jpg','fe8ce9585027cdde1bef962dbbafd5d615ef9ffe060d1114d1ec3fd55682349b','FaceURL','38',{'columns':3,'rows':3},22,False) or (back.get('sourcePath'),back.get('sourceSha256'),back_selector.get('key'),back_selector.get('url'),back_selector.get('rootDeckSelectorCount'),back_selector.get('baseCardSelectorCount'),back_selector.get('referenceCount'),back.get('rulesTextPresent'),back.get('separateRulesFace')) != ('assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-150.jpg','6a2376fb486c6a85f02da22f7c479b4aa7ccf6d4bd0cf0db65479cc89b3c96cb','BackURL','https://steamusercontent-a.akamaihd.net/ugc/2468613527880235898/A32D91672CA7CCBA01C44C27791836D0E634CE2A/',1,27,28,False,False):
        failures.append({'check':'Serious Wound source-registry face/sheet/back closure'})
    gap_cells = [row.get('generatedCell') for row in serious_wound_assets if not row.get('selectedByRootDeck')]
    if gap_cells != [4,6] or [row.get('cell') for row in (sheet.get('cells') or [])] != list(range(9)) or [row.get('selectedByRootDeck') for row in sheet.get('cells') or []] != [True,True,True,True,False,True,False,True,True]:
        failures.append({'check':'Serious Wound exact selected/generated-cell selector-gap lock'})
    licensed_wounds = serious_wound_sources.get('licensedDigitalOccurrences') or []
    expected_licensed_wound_keys = ['Bleeding','Leg','Arm','Eyes','Guts','Body','Hand','Knee','Lungs']
    serious_wound_table = next((row for row in secondary['licensedDigital']['structuredIndex']['tables'] if row.get('name') == 'SERIOUS_WOUNDS_DATA'), {})
    if [row.get('key') for row in licensed_wounds] != expected_licensed_wound_keys or serious_wound_table.get('count') != 9 or list(serious_wound_table.get('keys') or []) != expected_licensed_wound_keys or any(row.get('identityCrosswalkStatus') != 'independent licensed occurrence; no TTS/official identity join asserted' or not row.get('sourceBlockText') or row.get('sourceBlockText') not in bga_text for row in licensed_wounds) or serious_wound_sources.get('counts',{}).get('licensedPhysicalIdentityLinks') != 0:
        failures.append({'check':'Serious Wound licensed independent occurrence/no-title-crosswalk closure'})
    official_wounds = serious_wound_sources.get('officialVisibleCounterparts') or []
    expected_official_wound_ids = ['RB-P03-V01-SW-EYES','RB-P03-V01-SW-ARM-PARTIAL','RB-P03-V01-SW-BACK','RB-P18-V03-SW-EYES','RB-P18-V03-SW-BACK']
    if [row.get('sourceOccurrenceId') for row in official_wounds] != expected_official_wound_ids or [row.get('parentOccurrenceId') for row in official_wounds] != ['RB-P03-V01','RB-P03-V01','RB-P03-V01','RB-P18-V03','RB-P18-V03'] or any(row.get('sourceScopedOnly') is not True or row.get('physicalCopyCorrespondence') not in {'not established','shared back only'} for row in official_wounds):
        failures.append({'check':'Serious Wound official face/back occurrence authority closure'})
    faq_closure = serious_wound_sources.get('faqSearchClosure') or {}
    excluded = serious_wound_sources.get('excludedContent') or {}
    if faq_closure.get('baseApplicableOccurrences') != [] or len(faq_closure.get('excludedExpansionOccurrences') or []) != 1 or excluded.get('expansionSeriousWoundDecks') != [] or len(excluded.get('expansionWoundLikeComponents') or []) != 1 or 'not a twenty-eighth rules face' not in excluded.get('parentSheetBoundary','') or 'not a twenty-eighth rules face' not in excluded.get('sharedBackBoundary','') or 'no root DeckID/GUID selector' not in excluded.get('selectorGapBoundary',''):
        failures.append({'check':'Serious Wound FAQ/expansion/parent/back/overlay exclusion boundary'})
    serious_wound_linked_backlog_ids = (serious_wound_sources.get('familyCountEvidence',{}).get('backlog') or {}).get('linkedUnitIds') or []
    expected_linked_serious_wound_ids = [
        *['CARD:'+EXPECTED_SERIOUS_WOUND_ASSETS[key][1][:16] for key in EXPECTED_SERIOUS_WOUND_ASSETS],
        'RULE:ACT-MOVE-001','RULE:ACT-CARD-001','RULE:INT-006','RULE:INT-008','RULE:RT-007','RULE:RT-012','ROOM:03','ROOM:16',
        'VIS:RB-P03-V01','VIS:RB-P09-V01','VIS:RB-P17-V03','VIS:RB-P18-V01','VIS:RB-P18-V02','VIS:RB-P18-V03','VIS:RB-P40-V02',
    ]
    if serious_wound_linked_backlog_ids != expected_linked_serious_wound_ids or any((backlog_rows_by_id.get(unit_id) or {}).get('status') != 'pilot-covered' for unit_id in expected_linked_serious_wound_ids):
        failures.append({'check':'Serious Wound exact overlapping backlog-obligation closure'})

    required_fields = schema.get('required') or []
    schema_fields = set((schema.get('properties') or {}).keys())
    if set(required_fields) != schema_fields or schema.get('additionalProperties') is not False:
        failures.append({'check': 'semantic JSON schema closed record shape'})

    records = pilots.get('records') or []
    record_ids = [item.get('ruleId') for item in records]
    record_by_id = {item['ruleId']: item for item in records}
    if len(record_ids) != len(set(record_ids)) or any(not re.fullmatch(r'SEM-[A-Z0-9-]+', item or '') for item in record_ids):
        failures.append({'check': 'semantic rule IDs'})
    if record_ids != sorted(record_ids):
        failures.append({'check': 'semantic rule ordering'})

    question_rows = review.get('questions') or []
    question_ids = {item.get('questionId') for item in question_rows}
    if len(question_ids) != len(question_rows):
        failures.append({'check': 'semantic question IDs'})
    open_question_text = (REPO / 'docs/rules/open-questions.md').read_text(encoding='utf-8')
    for question in question_rows:
        qid = question.get('questionId')
        if not question.get('defaultProhibited') or not (question.get('blocksRuleIds') or question.get('plannedRuleIds')):
            failures.append({'check': 'semantic question no-default/linkage', 'questionId': qid})
        if qid.startswith('OQ-') and f'### {qid} ' not in open_question_text:
            failures.append({'check': 'source open-question reference', 'questionId': qid})
        for blocked in question.get('blocksRuleIds') or []:
            if blocked not in record_by_id:
                failures.append({'check': 'semantic question blocked record', 'questionId': qid, 'blocked': blocked})
        for planned in question.get('plannedRuleIds') or []:
            if not re.fullmatch(r'SEM-[A-Z0-9-]+', planned) or planned in record_by_id:
                failures.append({'check': 'semantic question planned record', 'questionId': qid, 'planned': planned})
        alternatives = question.get('alternatives') or []
        alternative_ids = [item.get('alternativeId') for item in alternatives]
        if len(alternatives) < 2 or len(alternative_ids) != len(set(alternative_ids)) or any(not item.get('description') or not item.get('support') for item in alternatives):
            failures.append({'check': 'semantic question alternatives', 'questionId': qid})
        for reference in question.get('sourceEvidenceRefs') or []:
            path = evidence_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'semantic question source evidence', 'questionId': qid, 'reference': reference})

    conflict_rows = contradictions.get('conflicts') or []
    conflict_ids = [item.get('conflictId') for item in conflict_rows]
    if conflict_ids != [f'SC-{index:03d}' for index in range(1, len(conflict_rows) + 1)]:
        failures.append({'check': 'semantic conflict IDs/order'})
    for conflict in conflict_rows:
        status = conflict.get('status')
        question_id = conflict.get('questionId')
        if status not in {'resolved-by-authority','unresolved','preserved-boundary'} or not conflict.get('difference') or not conflict.get('resolution'):
            failures.append({'check': 'semantic conflict shape', 'conflictId': conflict.get('conflictId')})
        if status == 'unresolved' and question_id not in question_ids:
            failures.append({'check': 'semantic conflict question linkage', 'conflictId': conflict.get('conflictId'), 'questionId': question_id})
        if status != 'unresolved' and question_id is not None:
            failures.append({'check': 'semantic conflict resolved question drift', 'conflictId': conflict.get('conflictId')})
        if any(rule_id not in record_by_id for rule_id in conflict.get('affectedRuleIds') or []):
            failures.append({'check': 'semantic conflict rule linkage', 'conflictId': conflict.get('conflictId')})
        for reference in conflict.get('evidenceRefs') or []:
            if reference in source_by_id:
                continue
            path = evidence_path(reference)
            if path is None or not path.exists():
                failures.append({'check': 'semantic conflict evidence', 'conflictId': conflict.get('conflictId'), 'reference': reference})
    if contradictions.get('counts') != {'conflicts':33,'resolvedByAuthority':14,'unresolved':12,'preservedBoundary':7}:
        failures.append({'check': 'semantic conflict declared counts'})

    question_by_id = {row.get('questionId'): row for row in question_rows}
    green_validation = validate_green_item_family(
        REPO, green_item_source_path, green_item_sources, source_by_id, backlog_rows_by_id,
        roles, load(REPO/'assets/tts-mod/extract/v2/objects.json'), secondary, bga_text,
        record_by_id, question_by_id, conflict_rows, coverage, failures,
    )

    for record in records:
        rule_id = record['ruleId']
        if set(record) != schema_fields:
            failures.append({'check': 'record schema fields', 'ruleId': rule_id, 'missing': sorted(schema_fields - set(record)), 'extra': sorted(set(record) - schema_fields)})
        if record.get('schemaVersion') != 1 or record.get('recordType') != 'semantic-rule' or not isinstance(record.get('recordRevision'), int) or isinstance(record.get('recordRevision'), bool) or record.get('recordRevision', 0) < 1:
            failures.append({'check': 'record schema/version', 'ruleId': rule_id})
        if record.get('status') not in schema['properties']['status']['enum'] or record.get('ruleKind') not in schema['properties']['ruleKind']['enum'] or record.get('modality') not in schema['properties']['modality']['enum']:
            failures.append({'check': 'record controlled facets', 'ruleId': rule_id})
        if record.get('implementationBoundary') != 'implementation-neutral; no engine, UI, network, storage, or serialization mapping':
            failures.append({'check': 'implementation boundary', 'ruleId': rule_id})
        searchable = json.dumps({key:value for key,value in record.items() if key != 'implementationBoundary'}, ensure_ascii=False)
        if FORBIDDEN_IMPLEMENTATION_TEXT.search(searchable):
            failures.append({'check': 'implementation leakage', 'ruleId': rule_id})
        if record.get('termRefs') != sorted(set(record.get('termRefs') or [])) or any(item not in term_ids for item in record.get('termRefs') or []):
            failures.append({'check': 'controlled term references', 'ruleId': rule_id})
        if record.get('taxonRefs') != sorted(set(record.get('taxonRefs') or [])) or any(item not in taxon_ids for item in record.get('taxonRefs') or []):
            failures.append({'check': 'taxon references', 'ruleId': rule_id})
        if record.get('namedIdentityRefs') != sorted(set(record.get('namedIdentityRefs') or [])) or any(item not in identity_ids for item in record.get('namedIdentityRefs') or []):
            failures.append({'check': 'named identity references', 'ruleId': rule_id})

        source_assertions = record.get('sourceAssertions') or []
        assertion_ids = [item.get('assertionId') for item in source_assertions]
        assertion_set = set(assertion_ids)
        assertion_by_id = {item.get('assertionId'): item for item in source_assertions}
        if not source_assertions or len(assertion_ids) != len(assertion_set) or any(not re.fullmatch(r'SA-[A-Z0-9-]+', item or '') for item in assertion_ids):
            failures.append({'check': 'source assertion IDs', 'ruleId': rule_id})
        used_authorities = []
        for item in source_assertions:
            source = source_by_id.get(item.get('sourceId'))
            if not source:
                failures.append({'check': 'source assertion source', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
                continue
            used_authorities.append(source['authority'])
            if any(item.get(field) != source.get(source_field) for field, source_field in (('sourcePath','path'),('sourceSha256','sha256'),('sourceAuthority','authority'),('sourceVersion','version'))):
                failures.append({'check': 'source assertion tuple projection', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
            if not item.get('locator') or not item.get('sourceText') or item.get('textKind') not in {'verbatim','normalized-paraphrase'}:
                failures.append({'check': 'source assertion text/locator', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
            if not item.get('supportsFields') or any(field not in schema_fields for field in item.get('supportsFields') or []):
                failures.append({'check': 'source assertion supported fields', 'ruleId': rule_id, 'assertionId': item.get('assertionId')})
            evidence = evidence_path(item.get('evidenceRecord'))
            if evidence is None or not evidence.exists():
                failures.append({'check': 'source assertion evidence record', 'ruleId': rule_id, 'assertionId': item.get('assertionId'), 'evidenceRecord': item.get('evidenceRecord')})
        if used_authorities:
            expected_highest = min(used_authorities, key=lambda value: authority_rank[value])
            if record.get('authority', {}).get('highest') != expected_highest:
                failures.append({'check': 'record authority precedence', 'ruleId': rule_id, 'expected': expected_highest, 'actual': record.get('authority', {}).get('highest')})
        if record.get('authority', {}).get('interpretation') not in {'verbatim-structure','source-composed','open-alternatives'}:
            failures.append({'check': 'record interpretation level', 'ruleId': rule_id})

        timing = record.get('timing') or {}
        if timing.get('anchorTaxonId') not in taxon_ids or timing.get('relation') not in ALLOWED_TIMING or not timing.get('windowId') or not timing.get('recurrence'):
            failures.append({'check': 'timing shape', 'ruleId': rule_id})
        participants = record.get('participants') or []
        participant_ids = [item.get('participantId') for item in participants]
        participant_set = set(participant_ids)
        if len(participant_ids) != len(participant_set):
            failures.append({'check': 'participant IDs', 'ruleId': rule_id})
        for item in participants:
            if item.get('taxonId') is not None and item.get('taxonId') not in taxon_ids:
                failures.append({'check': 'participant taxon', 'ruleId': rule_id, 'participantId': item.get('participantId')})

        conditions = record.get('preconditions') or []
        condition_ids = [item.get('conditionId') for item in conditions]
        condition_set = set(condition_ids)
        if len(condition_ids) != len(condition_set):
            failures.append({'check': 'condition IDs', 'ruleId': rule_id})
        for item in conditions:
            if item.get('scope') not in {'record-precondition','operation-guard'} or item.get('expression', {}).get('operator') not in {'predicate','all','any','not','comparison'}:
                failures.append({'check': 'condition shape', 'ruleId': rule_id, 'conditionId': item.get('conditionId')})
            if not item.get('sourceAssertionIds') or any(ref not in assertion_set for ref in item.get('sourceAssertionIds') or []):
                failures.append({'check': 'condition source linkage', 'ruleId': rule_id, 'conditionId': item.get('conditionId')})

        decisions = record.get('decisions') or []
        decision_ids = [item.get('decisionId') for item in decisions]
        decision_set = set(decision_ids)
        if len(decision_ids) != len(decision_set):
            failures.append({'check': 'decision IDs', 'ruleId': rule_id})
        for item in decisions:
            if item.get('ownerRef') not in participant_set or item.get('selectionMode') not in ALLOWED_DECISION_SELECTION or not cardinality_valid(item.get('cardinality')) or not isinstance(item.get('declineAllowed'), bool) or not item.get('visibility') or not item.get('options'):
                failures.append({'check': 'decision completeness', 'ruleId': rule_id, 'decisionId': item.get('decisionId')})

        information = record.get('informationPolicy') or []
        info_ids = [item.get('informationId') for item in information]
        if len(info_ids) != len(set(info_ids)):
            failures.append({'check': 'information policy IDs', 'ruleId': rule_id})
        for item in information:
            if not all(item.get(field) for field in ('subjectRef','audience','revealTrigger','secrecy')):
                failures.append({'check': 'information policy completeness', 'ruleId': rule_id, 'informationId': item.get('informationId')})

        costs = record.get('costs') or []
        cost_ids = [item.get('costId') for item in costs]
        if len(cost_ids) != len(set(cost_ids)):
            failures.append({'check': 'cost IDs', 'ruleId': rule_id})
        for item in costs:
            selection_ref = item.get('selectionDecisionRef')
            if item.get('payerRef') not in participant_set or item.get('resourceTermId') not in term_ids or not isinstance(item.get('quantity'), int) or item.get('quantity') < 0 or (selection_ref is not None and selection_ref not in decision_set):
                failures.append({'check': 'cost completeness', 'ruleId': rule_id, 'costId': item.get('costId')})

        targets = record.get('targets') or []
        target_ids = [item.get('targetId') for item in targets]
        target_set = set(target_ids)
        if len(target_ids) != len(target_set):
            failures.append({'check': 'target IDs', 'ruleId': rule_id})
        for item in targets:
            if any(taxon not in taxon_ids for taxon in item.get('eligibleTaxonIds') or []) or not cardinality_valid(item.get('cardinality')) or item.get('selectionMode') not in ALLOWED_TARGET_SELECTION or not item.get('visibility'):
                failures.append({'check': 'target completeness', 'ruleId': rule_id, 'targetId': item.get('targetId')})
            selector = item.get('selectorRef')
            if selector not in participant_set and selector != 'rules-system' and not str(selector).startswith('unresolved-'):
                failures.append({'check': 'target selector', 'ruleId': rule_id, 'targetId': item.get('targetId'), 'selectorRef': selector})

        operations = record.get('operations') or []
        operation_ids = [item.get('stepId') for item in operations]
        sequences = [item.get('sequence') for item in operations]
        if len(operation_ids) != len(set(operation_ids)) or sequences != list(range(1, len(operations) + 1)) or any(not re.fullmatch(r'S\d{2}', item or '') for item in operation_ids):
            failures.append({'check': 'operation IDs/order', 'ruleId': rule_id})
        for item in operations:
            if item.get('operationType') not in ALLOWED_OPERATIONS or item.get('modality') not in {'must','may','cannot','if-able','mixed'}:
                failures.append({'check': 'operation type/modality', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if any(ref not in assertion_set for ref in item.get('sourceAssertionIds') or []) or not item.get('sourceAssertionIds'):
                failures.append({'check': 'operation source linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if any('operations' not in (assertion_by_id.get(ref) or {}).get('supportsFields', []) for ref in item.get('sourceAssertionIds') or []):
                failures.append({'check': 'operation assertion support', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if any(ref not in condition_set for ref in item.get('conditionRefs') or []):
                failures.append({'check': 'operation condition linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('decisionRef') is not None and item.get('decisionRef') not in decision_set:
                failures.append({'check': 'operation decision linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('targetRef') is not None and item.get('targetRef') not in target_set:
                failures.append({'check': 'operation target linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('invokeRuleId') is not None and item.get('invokeRuleId') not in record_by_id:
                failures.append({'check': 'operation invoked rule linkage', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'invokeRuleId': item.get('invokeRuleId')})
            if any(ref not in record_by_id for ref in item.get('dispatchRuleIds') or []):
                failures.append({'check': 'operation dispatch linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('operationType') == 'transition-zone' and (not isinstance(item.get('transition'), dict) or not item['transition'].get('from') or not item['transition'].get('to')):
                failures.append({'check': 'operation transition completeness', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('operationType') == 'change-value' and not isinstance(item.get('valueChange'), dict):
                failures.append({'check': 'operation value-change completeness', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if item.get('operationType') == 'pay-cost' and item.get('objectRef') not in set(cost_ids):
                failures.append({'check': 'operation cost linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            if isinstance(item.get('objectRef'), str) and item['objectRef'].startswith('sem.') and item['objectRef'] not in semantic_node_ids and item['objectRef'] not in question_ids:
                failures.append({'check': 'operation semantic-node reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': item['objectRef']})
            repeat = item.get('repeat') or {}
            if repeat.get('untilConditionRef') and repeat['untilConditionRef'] not in condition_set:
                failures.append({'check': 'operation repeat condition linkage', 'ruleId': rule_id, 'stepId': item.get('stepId')})
            for transition_key in ('transition','valueChange'):
                payload = item.get(transition_key) or {}
                for value in payload.values():
                    if isinstance(value, str) and value.startswith('tax.') and value not in taxon_ids:
                        failures.append({'check': 'operation ontology reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': value})
                    if isinstance(value, str) and value.startswith('sem.') and value not in semantic_node_ids:
                        failures.append({'check': 'operation semantic-node reference', 'ruleId': rule_id, 'stepId': item.get('stepId'), 'value': value})
        used_decisions = {item.get('decisionRef') for item in operations if item.get('decisionRef')} | {item.get('selectionDecisionRef') for item in costs if item.get('selectionDecisionRef')}
        if used_decisions != decision_set:
            failures.append({'check': 'decision usage closure', 'ruleId': rule_id, 'unused': sorted(decision_set-used_decisions), 'unknown': sorted(used_decisions-decision_set)})

        partial = record.get('partialResolution') or {}
        if partial.get('policy') not in ALLOWED_PARTIAL or not partial.get('unit') or not partial.get('onImpossible'):
            failures.append({'check': 'partial-resolution completeness', 'ruleId': rule_id})
        if not record.get('duration') or not record.get('stacking'):
            failures.append({'check': 'duration/stacking completeness', 'ruleId': rule_id})

        unresolved = record.get('unresolvedQuestionRefs') or []
        if any(item not in question_ids for item in unresolved) or len(unresolved) != len(set(unresolved)):
            failures.append({'check': 'unresolved question linkage', 'ruleId': rule_id})
        if (record.get('status') == 'source-backed-with-open-question') != bool(unresolved):
            failures.append({'check': 'record status/question consistency', 'ruleId': rule_id})
        for variant in record.get('sourceVariants') or []:
            if variant.get('sourceId') not in source_by_id or variant.get('sourceAssertionId') not in assertion_set or not all(variant.get(field) for field in ('variantId','difference','resolution')):
                failures.append({'check': 'source variant completeness', 'ruleId': rule_id})

    # High-risk pilot fidelity invariants.
    search = record_by_id.get('SEM-ACT-SEARCH-001') or {}
    search_operations = search.get('operations') or []
    search_information = search.get('informationPolicy') or []
    search_bottom = next((item for item in search_operations if (item.get('transition') or {}).get('positionRef') == 'sem.position.deck-bottom'), {})
    if (search_bottom.get('transition') or {}).get('to') != 'tax.scaffold.zone.deck' or not any('unchosen Items must not be revealed' in item.get('secrecy','') for item in search_information) or 'SEM-Q-040' not in search.get('unresolvedQuestionRefs',[]) or not any(item.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-040' in item.get('objectRef','') for item in search_operations):
        failures.append({'check': 'Search bottom/private fidelity'})
    duck = record_by_id.get('SEM-REACTION-DUCK-001') or {}
    if duck.get('ruleKind') != 'reaction' or 'SEM-Q-001' not in duck.get('unresolvedQuestionRefs', []):
        failures.append({'check': 'Reaction replacement ambiguity fidelity'})
    move = record_by_id.get('SEM-ACT-MOVE-001') or {}
    explore = record_by_id.get('SEM-ACT-EXPLORE-001') or {}
    if 'SEM-Q-003' not in move.get('unresolvedQuestionRefs', []) or 'SEM-Q-002' not in explore.get('unresolvedQuestionRefs', []) or not any(item.get('operationType') == 'resolve-open-alternative' for item in explore.get('operations') or []):
        failures.append({'check': 'Movement/Exploration ambiguity fidelity'})
    passing = record_by_id.get('SEM-RT-007') or {}
    if not any(item.get('operationType') == 'end-action-window' for item in passing.get('operations') or []) or any(item.get('operationType') == 'end-process' for item in passing.get('operations') or []):
        failures.append({'check': 'Pass Turn-end effect fidelity'})
    endgame = record_by_id.get('SEM-ENDGAME-001') or {}
    endgame_assertion = next((item for item in endgame.get('sourceAssertions') or [] if item.get('assertionId') == 'SA-END-1'), {})
    endgame_step = next((item for item in endgame.get('operations') or [] if item.get('stepId') == 'S04'), {})
    endgame_guard = next((item for item in endgame.get('preconditions') or [] if item.get('conditionId') == 'S04-C01'), {})
    expected_endgame_assertion = {
        'locator': 'printed page 39 / lines 6238–6273',
        'supportsFields': ['preconditions','timing','operations','outcomes','unresolvedQuestionRefs'],
        'sourceText': 'Game ends at Round 14, when all players are dead/Escaped/Hibernated, or Facility destruction. Alive Escaped/Hibernated Characters resolve the listed checks in order: Infection for those without a Larva, then Eclosion for each Character that currently has a Larva. The note states that a Character may have gained a Larva “during this Sequence,” so Eclosion eligibility is evaluated when that cohort step is reached and includes a Larva gained during the preceding Infection step; then Objectives are revealed/checked and winners determined.',
        'evidenceRecord': 'docs/rulebooks/rulebook_text.txt:lines 6238–6273',
    }
    expected_endgame_step = {
        'stepId':'S04','sequence':4,'operationType':'invoke-process','modality':'must',
        'subjectRef':'each alive Escaped/Hibernated Character with a Larva when the Eclosion cohort step is reached',
        'objectRef':'Eclosion Procedure','conditionRefs':['S04-C01'],'decisionRef':None,'targetRef':None,
        'transition':None,'valueChange':None,'invokeRuleId':'SEM-ECLOSION-PROCEDURE-001','repeat':None,
        'sourceAssertionIds':['SA-END-1'],
        'notes':'Eligibility is evaluated at S04 after S03; the official note “A Character may have gained a Larva during the game or during this Sequence” excludes an endgame-start snapshot.',
    }
    expected_endgame_guard = {
        'conditionId':'S04-C01','scope':'operation-guard',
        'expression':{'operator':'predicate','args':[{'predicate':'Character has a Larva on their Character board when the Eclosion cohort step is reached, including a Larva gained during the preceding Infection step'}]},
        'sourceAssertionIds':['SA-END-1'],
    }
    if (
        any(endgame_assertion.get(key) != value for key,value in expected_endgame_assertion.items())
        or endgame_step != expected_endgame_step
        or endgame_guard != expected_endgame_guard
        or endgame.get('unresolvedQuestionRefs') != ['OQ-001']
        or (endgame.get('partialResolution') or {}).get('onImpossible') != 'source-specific; OQ-001 remains explicit for the invoked Eclosion hand check, while Larva cohort eligibility is source-resolved at S04'
        or 'OQ-002' in json.dumps({'review':review,'endgame':endgame}, ensure_ascii=False)
    ):
        failures.append({'check':'Endgame Larva step-time official-source lock'})
    intruder_help = load(REPO/'docs/rules/source-extraction/intruder-help-sheet.json')
    help_rows = {}
    for side in intruder_help['sides']:
        for column in side['columns']:
            for row in column['rows']:
                help_rows[row['occurrenceId']] = (side['sideId'], row['printedInstruction'], column['columnId'])
        row = side['bottomRow']
        help_rows[row['occurrenceId']] = (side['sideId'], row['printedInstruction'], 'bag-development')
    expected_help_rule_ids = {f'SEM-IH-{occurrence_id}' for occurrence_id in help_rows}
    actual_help_rule_ids = {rule_id for rule_id in record_by_id if rule_id.startswith('SEM-IH-')}
    if actual_help_rule_ids != expected_help_rule_ids:
        failures.append({'check': 'Intruder Help semantic closure'})
    for occurrence_id, (side, printed_text, context) in help_rows.items():
        rule_id = f'SEM-IH-{occurrence_id}'
        item = record_by_id.get(rule_id) or {}
        assertions = {row.get('assertionId'): row for row in item.get('sourceAssertions') or []}
        source_assertion = assertions.get(f'SA-{occurrence_id}') or {}
        expected_source = 'SRC-INTRUDER-HELP-QA' if side == 'queen-alive' else 'SRC-INTRUDER-HELP-QD'
        if source_assertion.get('sourceText') != printed_text or source_assertion.get('textKind') != 'verbatim' or source_assertion.get('sourceId') != expected_source:
            failures.append({'check': 'Intruder Help verbatim semantic projection', 'occurrenceId': occurrence_id})
        condition_text = json.dumps(item.get('preconditions') or [], ensure_ascii=False)
        if 'drawn token discriminator is ' not in condition_text:
            failures.append({'check': 'Intruder Help trigger discriminator', 'occurrenceId': occurrence_id})
        operations = item.get('operations') or []
        if context == 'corridor':
            for op in operations:
                if op.get('operationType') == 'place-component' and '6-equivalent Corridor capacity' not in (op.get('notes') or ''):
                    failures.append({'check': 'Intruder Help Corridor capacity', 'occurrenceId': occurrence_id})
                if op.get('operationType') == 'transition-zone' and (op.get('transition') or {}).get('positionRef') is not None:
                    failures.append({'check': 'Intruder Help non-Bag pile ordering', 'occurrenceId': occurrence_id})
        if context == 'room' and occurrence_id.endswith(('R-01','R-02')) and not any(op.get('invokeRuleId') == 'SEM-SECURE-ENTRY-001' for op in operations):
            failures.append({'check': 'Intruder Help Room Surprise Attack', 'occurrenceId': occurrence_id})
        if occurrence_id in {'QA-C-02','QD-C-02'}:
            placement = next((op for op in operations if op.get('operationType') == 'place-component'), {})
            repeat = placement.get('repeat') or {}
            if set(repeat) < {'adultCount','droneCount','corridorCapacityEquivalentLimit','tokenFaceResolutions'} or repeat.get('tokenFaceResolutions') != {'2':{'adultCount':2,'droneCount':0},'3':{'adultCount':3,'droneCount':0},'4':{'adultCount':4,'droneCount':0},'1+1':{'adultCount':1,'droneCount':1},'2+1':{'adultCount':2,'droneCount':1},'3+1':{'adultCount':3,'droneCount':1}}:
                failures.append({'check': 'Intruder Help token-back count/color', 'occurrenceId': occurrence_id})
    expected_help_dispatch = {'SEM-IH-QA-B-01','SEM-IH-QD-B-01','SEM-IH-QA-B-02','SEM-IH-QD-B-02','SEM-IH-QA-B-03','SEM-IH-QD-B-03','SEM-IH-QA-BOTTOM-01','SEM-IH-QD-BOTTOM-01'}
    bag_dispatch = {op.get('invokeRuleId') for op in (record_by_id.get('SEM-RT-011') or {}).get('operations') or [] if op.get('invokeRuleId')}
    if bag_dispatch != expected_help_dispatch:
        failures.append({'check': 'Bag Development exact Queen-side Help dispatch', 'actual': sorted(bag_dispatch)})
    expected_room_dispatch = {'SEM-IH-QA-R-01','SEM-IH-QA-R-02','SEM-IH-QD-R-01','SEM-IH-QD-R-02'}
    for source_rule in ('SEM-NOISE-HAZARD-001','SEM-ROOM-10'):
        dispatches={ref for op in (record_by_id.get(source_rule) or {}).get('operations') or [] for ref in op.get('dispatchRuleIds') or []}
        if dispatches != expected_room_dispatch:
            failures.append({'check': 'Room-context exact Help dispatch', 'ruleId': source_rule, 'actual': sorted(dispatches)})
    expected_corridor_dispatch = {'SEM-IH-QA-C-01','SEM-IH-QA-C-02','SEM-IH-QA-C-03','SEM-IH-QD-C-01','SEM-IH-QD-C-02','SEM-IH-QD-C-03'}
    noise_marker_dispatch = {ref for op in (record_by_id.get('SEM-NOISE-MARKER-001') or {}).get('operations') or [] for ref in op.get('dispatchRuleIds') or []}
    if noise_marker_dispatch != expected_corridor_dispatch:
        failures.append({'check': 'Corridor-context exact Help dispatch', 'actual':sorted(noise_marker_dispatch)})
    noise_invocations = [op.get('invokeRuleId') for op in (record_by_id.get('SEM-NOISE-001') or {}).get('operations') or [] if op.get('invokeRuleId')]
    if 'SEM-NOISE-MARKER-001' not in noise_invocations or 'SEM-NOISE-HAZARD-001' not in noise_invocations:
        failures.append({'check': 'Noise reusable marker/Hazard dispatch'})
    numeric_invocations = [op.get('invokeRuleId') for op in (record_by_id.get('SEM-NOISE-NUMERIC-CORRIDOR-001') or {}).get('operations') or [] if op.get('invokeRuleId')]
    if numeric_invocations != ['SEM-SECURE-ENTRY-001']:
        failures.append({'check': 'Numeric Noise Secure-entry dispatch'})
    room_help = load(REPO/'docs/rules/source-extraction/room-help-sheet.json')
    def room_key(value):
        return re.sub(r'[^a-z0-9]+','-',value.lower()).strip('-')
    room_identity_by_key = {}
    for identity in identities['records']:
        if 'room-title' in identity.get('observedRoleCounts', {}):
            for label in identity.get('observedLabels') or []:
                room_identity_by_key.setdefault(room_key(label), set()).add(identity['identityObservationId'])
    expected_room_ids = {f'SEM-ROOM-{entry["printedNumber"]}' for entry in room_help['entries']}
    actual_room_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r'SEM-ROOM-\d{2}', rule_id)}
    if actual_room_ids != expected_room_ids or 'SEM-USE-ROOM-001' not in record_by_id:
        failures.append({'check': 'Room Help semantic closure'})
    use_room_text = json.dumps(record_by_id.get('SEM-USE-ROOM-001') or {}, ensure_ascii=False)
    shelter_text = json.dumps(record_by_id.get('SEM-ROOM-02-SECURE') or {}, ensure_ascii=False)
    if 'occupied Room has no Malfunction marker' not in use_room_text or 'sem.state.room.always-secured' not in shelter_text or 'permanent status' not in shelter_text:
        failures.append({'check': 'Use Room/Shelter global constraints'})
    for entry in room_help['entries']:
        number = entry['printedNumber']
        item = record_by_id.get(f'SEM-ROOM-{number}') or {}
        assertion_rows = item.get('sourceAssertions') or []
        effect_id = 'SA-ROOM01-1' if number == '01' else f'SA-ROOM-{number}-E'
        effect_assertion = next((row for row in assertion_rows if row.get('assertionId') == effect_id), {})
        note_texts = [row.get('sourceText') for row in assertion_rows if re.fullmatch(rf'SA-ROOM-{number}-N\d{{2}}', row.get('assertionId',''))]
        if effect_assertion.get('sourceText') != entry['printedEffect'] or effect_assertion.get('textKind') != 'verbatim' or effect_assertion.get('sourceId') != 'SRC-ROOM-HELP':
            failures.append({'check': 'Room Help verbatim effect projection', 'room': number})
        if number != '01' and note_texts != entry['associatedNotes']:
            failures.append({'check': 'Room Help verbatim note projection', 'room': number})
        expected_identity = sorted(room_identity_by_key.get(room_key(entry['printedTitle']), set()))
        if not item.get('operations') or item.get('namedIdentityRefs') != expected_identity or len(expected_identity) != 1:
            failures.append({'check': 'Room Help semantic operation/identity', 'room': number})
    room_occurrences = {occ['occurrenceId']: occ for entry in room_help['entries'] for occ in entry['functionalIconOccurrences']}
    denotation_rows = room_icon_data.get('denotations') or []
    denotation_ids = [row.get('occurrenceId') for row in denotation_rows]
    expected_denotation_counts = {'functionalOccurrences':112,'controlledTermDenotations':107,'semanticNodeDenotations':5,'uniqueSemanticReferences':28}
    if set(denotation_ids) != set(room_occurrences) or len(denotation_ids) != len(set(denotation_ids)) or room_icon_data.get('counts') != expected_denotation_counts:
        failures.append({'check': 'Room Help icon semantic closure'})
    for row in denotation_rows:
        occurrence = room_occurrences.get(row.get('occurrenceId')) or {}
        reference = row.get('semanticReferenceId')
        valid_reference = (row.get('referenceKind') == 'controlled-term' and reference in term_ids) or (row.get('referenceKind') == 'semantic-node' and reference in semantic_node_ids)
        if not valid_reference or row.get('literalAppearance') != occurrence.get('literalAppearance') or row.get('sourceLocation') != occurrence.get('location') or row.get('mappingScope') != 'official Room Help source occurrence only':
            failures.append({'check': 'Room Help icon denotation projection', 'occurrenceId': row.get('occurrenceId')})
    denotation_by_id = {row['occurrenceId']: row['semanticReferenceId'] for row in denotation_rows}
    expected_denotation_by_id = {
        'R01-I04':'icon.fire','R03-I04':'icon.characterHealth','R05-I04':'icon.ammoToken','R05-I05':'icon.grenadeToken','R07-I04':'icon.secure','R07-I05':'icon.robot','R07-I06':'icon.robot','R08-I05':'icon.redItem','R08-I06':'icon.malfunction','R08-I07':'icon.ammoToken','R09-I05':'icon.intruder','R10-I04':'icon.noise','R11-I03':'icon.ammoToken','R13-I04':'icon.actionCard','R13-I05':'icon.oxygen','R13-I06':'icon.oxygen','R14-I01':'icon.ammoSlot','R14-I02':'icon.grenadeSlot','R14-I03':'icon.medpackSlot','R14-I04':'icon.oxygenSlot','R14-I05':'icon.lander','R15-I04':'icon.lifeSupportActive','R15-I05':'icon.lifeSupportInactive','R15-I06':'icon.fire','R16-I04':'icon.actionCard','R17-I05':'icon.robot','R18-I01':'icon.hibernatoriumActive','R18-I02':'icon.hibernatoriumActive','R19-I03':'icon.lifeSupportActive','R19-I04':'icon.lifeSupportInactive','R20-I04':'icon.computer','R20-I05':'icon.malfunction','R22-I03':'icon.lifeSupportActive','R22-I04':'icon.lifeSupportInactive','R22-I05':'icon.hibernatoriumInactive','R22-I06':'icon.hibernatoriumActive','R23-I03':'icon.lifeSupportActive','R23-I04':'icon.lifeSupportInactive','R23-I05':'icon.autodestruction','R23-I06':'icon.lifeSupportInactive','R23-I07':'icon.autodestruction','R23-I08':'icon.lifeSupportInactive','R23-I09':'icon.autodestruction','R02-I03':'sem.state.room.always-secured','R04-I04':'sem.state.room.secure-prohibited','R12-I04':'sem.state.room.secure-prohibited','R25-I01':'sem.state.room.secure-prohibited','R25-I02':'sem.state.room.malfunction-prohibited'}
    literal_expected={'bright green chamfered square containing a centered white plus sign':'icon.greenItem','gold-yellow chamfered square containing a diagonal white wrench silhouette':'icon.yellowItem','red chamfered square containing three upright white cartridge-like shapes':'icon.redItem','small cyan-blue glowing rectangular monitor-like outline with a pale inner screen and short base':'icon.computer'}
    for occurrence_id,occurrence in room_occurrences.items():
        literal_reference=literal_expected.get(occurrence.get('literalAppearance'))
        if literal_reference is not None:
            expected_denotation_by_id.setdefault(occurrence_id,literal_reference)
    if any(expected_denotation_by_id.get(occurrence_id) != reference for occurrence_id,reference in denotation_by_id.items()):
        failures.append({'check': 'independently locked Room icon denotation map'})
    if denotation_by_id.get('R08-I05') != 'icon.redItem' or denotation_by_id.get('R08-I06') != 'icon.malfunction' or denotation_by_id.get('R08-I07') != 'icon.ammoToken':
        failures.append({'check': 'Gunnery Room icon semantics'})
    room04 = record_by_id.get('SEM-ROOM-04') or {}
    if 'SEM-Q-004' not in room04.get('unresolvedQuestionRefs', []) or not any((row.get('transition') or {}).get('to') == 'tax.scaffold.zone.backpack' for row in room04.get('operations') or []):
        failures.append({'check': 'Supply Room ambiguity/storage semantics'})
    room08_text = json.dumps(record_by_id.get('SEM-ROOM-08') or {}, ensure_ascii=False)
    if 'not a Burst Action' not in room08_text or 'no Ammo token is spent' not in room08_text:
        failures.append({'check': 'Gunnery Room non-Burst/Ammo semantics'})
    if not any('kept Support Equipment to Character storage' in row.get('objectRef','') for row in (record_by_id.get('SEM-ROOM-11') or {}).get('operations') or []):
        failures.append({'check': 'Experimental Lab kept Support Equipment transition'})
    if [denotation_by_id.get(f'R14-I0{index}') for index in range(1,5)] != ['icon.ammoSlot','icon.grenadeSlot','icon.medpackSlot','icon.oxygenSlot']:
        failures.append({'check': 'Landing Zone connected-slot semantics'})
    expected_room_states = {'R02-I03':'sem.state.room.always-secured','R04-I04':'sem.state.room.secure-prohibited','R12-I04':'sem.state.room.secure-prohibited','R25-I01':'sem.state.room.secure-prohibited','R25-I02':'sem.state.room.malfunction-prohibited'}
    if any(denotation_by_id.get(occurrence_id) != reference for occurrence_id, reference in expected_room_states.items()) or 'SEM-ROOM-STATIC-PROHIBITIONS' not in record_by_id:
        failures.append({'check': 'Room static-state icon semantics'})
    room12_operations = (record_by_id.get('SEM-ROOM-12') or {}).get('operations') or []
    room12_attack_index = next((index for index,row in enumerate(room12_operations) if row.get('invokeRuleId') == 'SEM-INT-004'), None)
    room12_noise_index = next((index for index,row in enumerate(room12_operations) if row.get('invokeRuleId') == 'SEM-NOISE-001'), None)
    if room12_attack_index is None or room12_noise_index is None or room12_attack_index > room12_noise_index:
        failures.append({'check': 'Technical Corridor Entrance operation order'})
    room12_text = json.dumps(record_by_id.get('SEM-ROOM-12') or {}, ensure_ascii=False)
    if not all(fragment in room12_text for fragment in ('virtual Adult attacker with no miniature','targeting only the moved Character','Secure ignored','may be used in the normal pre-resolution window')):
        failures.append({'check': 'Technical Corridor Entrance Attack parameters/prevention'})
    for robot_room_id in ('SEM-ROOM-07','SEM-ROOM-17'):
        if 'not broken' not in json.dumps(record_by_id.get(robot_room_id) or {}, ensure_ascii=False):
            failures.append({'check': 'Robot-dependent Room broken restriction', 'ruleId': robot_room_id})
    if not (record_by_id.get('SEM-ROOM-20') or {}).get('targets') or not all(rule_id in record_by_id for rule_id in ('SEM-DATA-TOKEN-001','SEM-AUTODESTRUCTION-001','SEM-ROBOT-MALFUNCTION-001')):
        failures.append({'check': 'Server/Data/Autodestruction/Robot semantic dependencies'})
    room19_information = (record_by_id.get('SEM-ROOM-19') or {}).get('informationPolicy') or []
    if not any(row.get('audience') == 'owner-private' and 'need not share' in row.get('secrecy','') for row in room19_information):
        failures.append({'check': 'Life Support B private Anti-Aircraft ordering'})
    qd_c01_types = [row.get('operationType') for row in (record_by_id.get('SEM-IH-QD-C-01') or {}).get('operations') or []]
    if qd_c01_types[:2] != ['place-component','transition-zone']:
        failures.append({'check': 'Queen-Dead Corridor replacement order'})
    hatching = record_by_id.get('SEM-EVENT-HATCHING-001') or {}
    if hatching.get('partialResolution', {}).get('policy') != 'per-sentence-continue' or 'OQ-009' not in hatching.get('unresolvedQuestionRefs', []):
        failures.append({'check': 'Event partial/Nest ambiguity fidelity'})
    expected_event_rule_ids = {value[4] for value in EXPECTED_EVENT_OCCURRENCES.values()}
    actual_event_rule_ids = {rule_id for rule_id,item in record_by_id.items() if item.get('ruleKind') == 'event' and rule_id not in {'SEM-EVENT-GENERAL-001'}}
    if actual_event_rule_ids != expected_event_rule_ids:
        failures.append({'check': 'Event semantic record closure', 'missing':sorted(expected_event_rule_ids-actual_event_rule_ids), 'extra':sorted(actual_event_rule_ids-expected_event_rule_ids)})
    faq_event_cards = {5609,5613,5614,5615,5616,5621,5622,5626}
    for card_id,expected in EXPECTED_EVENT_OCCURRENCES.items():
        expected_source_id,_,expected_sha,_,rule_id,_ = expected
        source_event = event_by_card.get(card_id) or {}
        item = record_by_id.get(rule_id) or {}
        assertions = {row.get('assertionId'):row for row in item.get('sourceAssertions') or []}
        scan_assertion = assertions.get(f'SA-EVT-{card_id}-SCAN') or {}
        bga_assertion = assertions.get(f'SA-EVT-{card_id}-BGA') or {}
        if (scan_assertion.get('sourceId'),scan_assertion.get('sourceSha256'),scan_assertion.get('sourceText'),scan_assertion.get('textKind')) != (expected_source_id,expected_sha,source_event.get('printedBody'),'verbatim'):
            failures.append({'check': 'Event exact scan assertion projection', 'ttsCardId':card_id})
        if (bga_assertion.get('sourceId'),bga_assertion.get('sourceText'),bga_assertion.get('textKind')) != ('SRC-BGA-EVENTS',(source_event.get('bgaOccurrence') or {}).get('sourceBlockText'),'verbatim'):
            failures.append({'check': 'Event exact licensed assertion projection', 'ttsCardId':card_id})
        variants = item.get('sourceVariants') or []
        expected_variant = (f'SV-EVT-{card_id}-BGA','SRC-BGA-EVENTS',f'SA-EVT-{card_id}-BGA')
        if len(variants) != 1 or (variants[0].get('variantId'),variants[0].get('sourceId'),variants[0].get('sourceAssertionId')) != expected_variant or not variants[0].get('difference') or not variants[0].get('resolution'):
            failures.append({'check': 'Event licensed source-variant closure', 'ttsCardId':card_id})
        expected_sentence_ids = [row.get('sentenceId') for row in source_event.get('sentences') or []]
        source_section_by_sentence = {row.get('sentenceId'):row.get('section') for row in source_event.get('sentences') or []}
        operation_sentence_ids = [row.get('sourceSentenceId') for row in item.get('operations') or []]
        first_occurrence_order = list(dict.fromkeys(operation_sentence_ids))
        if not operation_sentence_ids or any(sentence_id not in source_section_by_sentence for sentence_id in operation_sentence_ids) or first_occurrence_order != expected_sentence_ids:
            failures.append({'check': 'Event semantic sentence-order projection', 'ttsCardId':card_id})
        for op in item.get('operations') or []:
            if op.get('sourceSection') != source_section_by_sentence.get(op.get('sourceSentenceId')):
                failures.append({'check': 'Event semantic sentence-section projection', 'ttsCardId':card_id, 'stepId':op.get('stepId')})
        if item.get('partialResolution') != {'policy':'per-sentence-continue','unit':'sourceSentenceId / exact printed Event-card sentence','onImpossible':'ignore exactly the impossible printed sentence and continue later sentence IDs; do not invent target-level partial resolution or a tie-break, except the explicit finite-Intruder-model rule'}:
            failures.append({'check': 'Event per-sentence continuation lock', 'ttsCardId':card_id})
        expected_questions = EXPECTED_EVENT_QUESTION_REFS.get(rule_id,[])
        if item.get('unresolvedQuestionRefs') != expected_questions or (item.get('status') == 'source-backed-with-open-question') != bool(expected_questions):
            failures.append({'check': 'Event no-default question projection', 'ttsCardId':card_id})
        expected_authority = 'official-errata' if card_id in faq_event_cards else 'official-primary'
        if item.get('authority',{}).get('highest') != expected_authority:
            failures.append({'check': 'Event authority lock', 'ttsCardId':card_id})
        target_ids = {target.get('targetId') for target in item.get('targets') or []}
        used_targets = {op.get('targetRef') for op in item.get('operations') or [] if op.get('targetRef')}
        if target_ids != used_targets:
            failures.append({'check': 'Event target usage closure', 'ttsCardId':card_id})
        if any((op.get('transition') or {}).get('to') == 'tax.scaffold.zone.discard-pile' for op in item.get('operations') or []):
            failures.append({'check': 'Event generic-discard ownership', 'ttsCardId':card_id})
    event_generic = record_by_id.get('SEM-EVENT-GENERAL-001') or {}
    generic_dispatch = next((op.get('dispatchRuleIds') for op in event_generic.get('operations') or [] if op.get('dispatchRuleIds')), None)
    expected_dispatch = [EXPECTED_EVENT_OCCURRENCES[card_id][4] for card_id in sorted(EXPECTED_EVENT_OCCURRENCES)]
    generic_discard = next((op for op in event_generic.get('operations') or [] if op.get('operationType') == 'transition-zone'), {})
    if generic_dispatch != expected_dispatch or not generic_discard.get('conditionRefs') or (generic_discard.get('transition') or {}).get('from') != 'sem.zone.card-in-resolution':
        failures.append({'check': 'Generic Event exact occurrence dispatch/discard'})
    leaving_record = record_by_id.get('SEM-EVENT-LEAVING-THE-SHELL-001') or {}
    leaving_alternatives = [op for op in leaving_record.get('operations') or [] if op.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-006' in op.get('objectRef','')]
    if len(leaving_alternatives) != 3 or 'icon.actionCard' in (leaving_record.get('termRefs') or []) or 'SEM-Q-006' not in leaving_record.get('unresolvedQuestionRefs',[]):
        failures.append({'check': 'Leaving the Shell no invented glyph default'})
    for reshuffle_rule in ('SEM-EVENT-LEAVING-THE-SHELL-001','SEM-EVENT-REACTOR-OVERHEATING-001'):
        reshuffle_ops = (record_by_id.get(reshuffle_rule) or {}).get('operations') or []
        if not any(op.get('operationType') == 'transition-zone' and (op.get('transition') or {}).get('to') == 'tax.scaffold.zone.deck' for op in reshuffle_ops) or not any(op.get('operationType') == 'shuffle' for op in reshuffle_ops):
            failures.append({'check': 'Event self-inclusive reshuffle fidelity', 'ruleId':reshuffle_rule})
    secure = record_by_id.get('SEM-SECURE-ENTRY-001') or {}
    if 'OQ-007' not in secure.get('unresolvedQuestionRefs',[]) or not any(op.get('invokeRuleId') == 'SEM-INT-004' for op in secure.get('operations') or []):
        failures.append({'check': 'Secure-entry single/multiple boundary'})
    robot = record_by_id.get('SEM-ROBOT-MALFUNCTION-001') or {}
    if 'SEM-Q-010' not in robot.get('unresolvedQuestionRefs',[]) or len(robot.get('sourceAssertions') or []) != 2 or not any(op.get('operationType') == 'resolve-open-alternative' for op in robot.get('operations') or []):
        failures.append({'check': 'Robot equal-authority contradiction boundary'})
    actual_event_lock_ids = set(EXPECTED_EVENT_RECORD_DIGESTS) & set(record_by_id)
    if actual_event_lock_ids != set(EXPECTED_EVENT_RECORD_DIGESTS):
        failures.append({'check': 'independently locked Event semantic projection', 'missing':sorted(set(EXPECTED_EVENT_RECORD_DIGESTS)-actual_event_lock_ids)})
    for rule_id,expected_digest in EXPECTED_EVENT_RECORD_DIGESTS.items():
        item = record_by_id.get(rule_id)
        actual_digest = hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest() if item else None
        if actual_digest != expected_digest:
            failures.append({'check': 'independently locked Event semantic projection', 'ruleId':rule_id})
    if any(fragment in ' '.join(coverage.get('notYetCovered') or []) for fragment in ('all 20 Events','all Events')):
        failures.append({'check': 'Event coverage stale not-yet-covered claim'})

    expected_exploration_rule_ids = {row['ruleId'] for row in EXPECTED_EXPLORATION_OCCURRENCES.values()}
    actual_exploration_rule_ids = {rule_id for rule_id in record_by_id if rule_id.startswith('SEM-EXPLORATION-')}
    if actual_exploration_rule_ids != expected_exploration_rule_ids:
        failures.append({'check':'Exploration semantic record closure','missing':sorted(expected_exploration_rule_ids-actual_exploration_rule_ids),'extra':sorted(actual_exploration_rule_ids-expected_exploration_rule_ids)})
    for card_id,expected in EXPECTED_EXPLORATION_OCCURRENCES.items():
        source_face = exploration_by_card.get(card_id) or {}
        item = record_by_id.get(expected['ruleId']) or {}
        assertions = {row.get('assertionId'):row for row in item.get('sourceAssertions') or []}
        scan_assertion = assertions.get(f'SA-EXP-{card_id}-SCAN') or {}
        bga_assertion = assertions.get(f'SA-EXP-{card_id}-BGA') or {}
        if (scan_assertion.get('sourceId'),scan_assertion.get('sourceSha256'),scan_assertion.get('sourceText'),scan_assertion.get('textKind')) != (expected['sourceId'],expected['sha256'],source_face.get('printedBody'),'verbatim'):
            failures.append({'check':'Exploration exact scan assertion projection','ttsCardId':card_id})
        if (bga_assertion.get('sourceId'),bga_assertion.get('sourceText'),bga_assertion.get('textKind')) != ('SRC-BGA-EXPLORATION',(source_face.get('bgaOccurrence') or {}).get('sourceBlockText'),'verbatim'):
            failures.append({'check':'Exploration exact licensed assertion projection','ttsCardId':card_id})
        variants = item.get('sourceVariants') or []
        expected_variants = [(f'SV-EXP-{card_id}-BGA','SRC-BGA-EXPLORATION',f'SA-EXP-{card_id}-BGA')]
        expected_variants.extend((f'SV-EXP-{card_id}-OFFICIAL-{index:02d}','SRC-RULEBOOK',f'SA-EXP-{card_id}-OFFICIAL-{index:02d}') for index in range(1,len(expected['official'])+1))
        actual_variants = [(row.get('variantId'),row.get('sourceId'),row.get('sourceAssertionId')) for row in variants]
        if actual_variants != expected_variants or any(not row.get('difference') or not row.get('resolution') for row in variants):
            failures.append({'check':'Exploration licensed/official source-variant closure','ttsCardId':card_id})
        source_units = source_face.get('sourceUnits') or []
        source_unit_by_id = {row.get('unitId'):row for row in source_units}
        operations = item.get('operations') or []
        operation_unit_ids = [row.get('sourceUnitId') for row in operations]
        first_occurrence_order = list(dict.fromkeys(operation_unit_ids))
        expected_unit_order = [row.get('unitId') for row in source_units]
        if not operations or any(unit_id not in source_unit_by_id for unit_id in operation_unit_ids) or first_occurrence_order != expected_unit_order:
            failures.append({'check':'Exploration semantic source-unit order projection','ttsCardId':card_id})
        for op in operations:
            unit = source_unit_by_id.get(op.get('sourceUnitId')) or {}
            if op.get('sourceUnitKind') != unit.get('unitKind'):
                failures.append({'check':'Exploration semantic source-unit kind projection','ttsCardId':card_id,'stepId':op.get('stepId')})
        target_ids = {row.get('targetId') for row in item.get('targets') or []}
        used_targets = {row.get('targetRef') for row in operations if row.get('targetRef')}
        if target_ids != used_targets:
            failures.append({'check':'Exploration target usage closure','ttsCardId':card_id})
        transitions = [row for row in operations if row.get('operationType') == 'transition-zone']
        expected_destination = 'tax.scaffold.zone.removed-from-game' if expected['removeFromGame'] else 'tax.scaffold.zone.discard-pile'
        if len(transitions) != 1 or (transitions[0].get('transition') or {}).get('from') != 'sem.zone.card-in-resolution' or (transitions[0].get('transition') or {}).get('to') != expected_destination or (transitions[0].get('conditionRefs') or []):
            failures.append({'check':'Exploration remove/discard lifecycle transition lock','ttsCardId':card_id})
        if expected['removeFromGame']:
            lifecycle_unit = source_unit_by_id.get(transitions[0].get('sourceUnitId')) or {}
            faq_assertion_id = f"SA-EXP-{card_id}-FAQ-U07"
            if lifecycle_unit.get('section') != 'lifecycle' or faq_assertion_id not in (transitions[0].get('sourceAssertionIds') or []) or (transitions[0].get('conditionRefs') or []) or 'still resolves when Entrance Effects are ignored' not in (transitions[0].get('notes') or ''):
                failures.append({'check':'Exploration remove-from-game scope outside Entrance effect','ttsCardId':card_id})
        condition_by_id = {row.get('conditionId'):row for row in item.get('preconditions') or []}
        for op in operations:
            unit = source_unit_by_id.get(op.get('sourceUnitId')) or {}
            if unit.get('section') != 'entrance':
                continue
            guard_text = json.dumps([condition_by_id.get(ref) for ref in op.get('conditionRefs') or []],ensure_ascii=False)
            if 'caller does not explicitly ignore Entrance Effects' not in guard_text:
                failures.append({'check':'Exploration Entrance-effect ignore guard','ttsCardId':card_id,'stepId':op.get('stepId')})
        diagram_ops = [row for row in operations if (source_unit_by_id.get(row.get('sourceUnitId')) or {}).get('unitKind') == 'source-local-diagram']
        corridor_op = next((row for row in diagram_ops if row.get('objectRef') == 'one random Corridor in each eligible source-local diagram slot'), {})
        corridor_repeat = corridor_op.get('repeat') or {}
        if corridor_repeat.get('slotIndices') != expected['corridors'] or corridor_repeat.get('assignmentOrder') != 'SEM-Q-011 unresolved' or corridor_op.get('targetRef') is None:
            failures.append({'check':'Exploration no invented multi-slot assignment default','ttsCardId':card_id})
        room_marker_ops = [row for row in diagram_ops if row.get('objectRef') == 'all source-depicted markers in the new Room']
        noise_marker_ops = [row for row in diagram_ops if row.get('objectRef') == 'source-depicted Noise markers in placed diagram Corridors']
        if bool(room_marker_ops) != bool(expected['roomIcons']) or (room_marker_ops and (room_marker_ops[0].get('targetRef') != f'T-EXP-{card_id}-NEW-ROOM' or (room_marker_ops[0].get('repeat') or {}).get('roomMarkerOccurrences') != expected['roomIcons'])):
            failures.append({'check':'Exploration Room-marker target/source occurrence projection','ttsCardId':card_id})
        if bool(noise_marker_ops) != bool(expected['noise']) or (noise_marker_ops and (noise_marker_ops[0].get('targetRef') != f'T-EXP-{card_id}-DIAGRAM-SLOTS' or (noise_marker_ops[0].get('repeat') or {}).get('noiseSlotIndices') != expected['noise'])):
            failures.append({'check':'Exploration Corridor-Noise target/source occurrence projection','ttsCardId':card_id})
        if item.get('title') != f'Untitled Exploration occurrence {card_id}' or item.get('namedIdentityRefs') or item.get('unresolvedQuestionRefs') != ['SEM-Q-011'] or item.get('status') != 'source-backed-with-open-question':
            failures.append({'check':'Exploration untitled identity/no-default question projection','ttsCardId':card_id})
        expected_authority = 'official-errata' if source_face.get('faqOccurrences') else 'official-primary'
        if item.get('authority',{}).get('highest') != expected_authority:
            failures.append({'check':'Exploration authority lock','ttsCardId':card_id})
        if expected['adultCount']:
            adult_types = [row.get('operationType') for row in operations if 'Corridor just passed through' in row.get('objectRef','')]
            if adult_types != ['remove-component','place-component'] or any(row.get('invokeRuleId') == 'SEM-SECURE-ENTRY-001' for row in operations):
                failures.append({'check':'Exploration Adult placement/Noise/no-entry-Attack order','ttsCardId':card_id})
        if expected['closeDoor'] and not any(row.get('invokeRuleId') == 'SEM-DOOR-001' and 'touching the new Room' in row.get('objectRef','') for row in operations):
            failures.append({'check':'Exploration FAQ Door scope','ttsCardId':card_id})
        if (source_face.get('printedBody') or '').count('[noiseDieHazard]') and not any(row.get('invokeRuleId') == 'SEM-NOISE-HAZARD-001' for row in operations):
            failures.append({'check':'Exploration reusable Hazard procedure','ttsCardId':card_id})
        if 'Noise roll' in (source_face.get('printedBody') or '') and not any(row.get('invokeRuleId') == 'SEM-NOISE-001' for row in operations):
            failures.append({'check':'Exploration reusable Entrance Noise procedure','ttsCardId':card_id})
        searchable = json.dumps(item,ensure_ascii=False)
        if any(fragment in searchable for fragment in ('icon.lifeSupportActive','icon.lifeSupportInactive','icon.hibernatoriumActive','icon.hibernatoriumInactive','Exploration Card 1 effect','Exploration Card 2 effect')):
            failures.append({'check':'Exploration no invented title/system icon','ttsCardId':card_id})
    generic_exploration = record_by_id.get('SEM-ACT-EXPLORE-001') or {}
    generic_exploration_dispatch = next((op.get('dispatchRuleIds') for op in generic_exploration.get('operations') or [] if op.get('dispatchRuleIds')), None)
    if generic_exploration_dispatch != [EXPECTED_EXPLORATION_OCCURRENCES[card_id]['ruleId'] for card_id in sorted(EXPECTED_EXPLORATION_OCCURRENCES)] or 'SEM-Q-002' not in generic_exploration.get('unresolvedQuestionRefs',[]):
        failures.append({'check':'Generic Exploration exact untitled occurrence dispatch/SEM-Q-002'})
    exploration_question = next((row for row in question_rows if row.get('questionId') == 'SEM-Q-011'), {})
    if exploration_question.get('defaultProhibited') is not True or exploration_question.get('blocksRuleIds') != [EXPECTED_EXPLORATION_OCCURRENCES[card_id]['ruleId'] for card_id in sorted(EXPECTED_EXPLORATION_OCCURRENCES)] or len(exploration_question.get('alternatives') or []) != 3:
        failures.append({'check':'Exploration multi-slot question no-default alternatives'})
    actual_exploration_lock_ids = set(EXPECTED_EXPLORATION_RECORD_DIGESTS) & set(record_by_id)
    if actual_exploration_lock_ids != set(EXPECTED_EXPLORATION_RECORD_DIGESTS):
        failures.append({'check':'independently locked Exploration semantic projection','missing':sorted(set(EXPECTED_EXPLORATION_RECORD_DIGESTS)-actual_exploration_lock_ids)})
    for rule_id,expected_digest in EXPECTED_EXPLORATION_RECORD_DIGESTS.items():
        item = record_by_id.get(rule_id)
        actual_digest = hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest() if item else None
        if actual_digest != expected_digest:
            failures.append({'check':'independently locked Exploration semantic projection','ruleId':rule_id,'actual':actual_digest})
    not_yet_text = ' '.join(coverage.get('notYetCovered') or [])
    if 'base Exploration' not in next((row.get('system','') for row in coverage.get('systems') or [] if expected_exploration_rule_ids.issubset(set(row.get('ruleIds') or []))), '') or any(fragment in not_yet_text for fragment in ('all 12 Exploration','all Exploration cards')):
        failures.append({'check':'Exploration coverage stale not-yet-covered claim'})

    expected_robot_rule_ids = {row['ruleId'] for row in EXPECTED_ROBOT_OCCURRENCES.values()}
    actual_robot_rule_ids = {rule_id for rule_id in record_by_id if rule_id in expected_robot_rule_ids}
    if actual_robot_rule_ids != expected_robot_rule_ids:
        failures.append({'check':'Robot semantic face-record closure','missing':sorted(expected_robot_rule_ids-actual_robot_rule_ids),'extra':sorted(actual_robot_rule_ids-expected_robot_rule_ids)})
    for card_id,expected in EXPECTED_ROBOT_OCCURRENCES.items():
        source_face = robot_by_card.get(card_id) or {}
        item = record_by_id.get(expected['ruleId']) or {}
        assertions = {row.get('assertionId'):row for row in item.get('sourceAssertions') or []}
        scan = assertions.get(f'SA-RBT-{card_id}-SCAN') or {}
        bga = assertions.get(f'SA-RBT-{card_id}-BGA') or {}
        if (scan.get('sourceId'),scan.get('sourceSha256'),scan.get('sourceText'),scan.get('textKind')) != (expected['sourceId'],expected['sha256'],source_face.get('printedBody'),'verbatim'):
            failures.append({'check':'Robot exact scan assertion projection','ttsCardId':card_id})
        if (bga.get('sourceId'),bga.get('sourceText'),bga.get('textKind')) != ('SRC-BGA-ROBOTS',(source_face.get('bgaOccurrence') or {}).get('sourceBlockText'),'verbatim'):
            failures.append({'check':'Robot exact licensed assertion projection','ttsCardId':card_id})
        variants = item.get('sourceVariants') or []
        expected_variants = [(f'SV-RBT-{card_id}-BGA','SRC-BGA-ROBOTS',f'SA-RBT-{card_id}-BGA')]
        expected_variants.extend((f'SV-RBT-{card_id}-OFFICIAL-{index:02d}','SRC-RULEBOOK',f'SA-RBT-{card_id}-OFFICIAL-{index:02d}') for index in range(1,len(expected['official'])+1))
        actual_variants = [(row.get('variantId'),row.get('sourceId'),row.get('sourceAssertionId')) for row in variants]
        if actual_variants != expected_variants or any(not row.get('difference') or not row.get('resolution') for row in variants):
            failures.append({'check':'Robot licensed/official source-variant closure','ttsCardId':card_id})
        sentence_by_id = {row.get('sentenceId'):row for row in source_face.get('sentences') or []}
        source_ops = [row for row in item.get('operations') or [] if row.get('sourceSentenceId')]
        first_sentence_order = list(dict.fromkeys(row.get('sourceSentenceId') for row in source_ops))
        if not source_ops or first_sentence_order != expected['sentenceIds'] or any(row.get('sourceSentenceId') not in sentence_by_id or row.get('sourcePanelId') != sentence_by_id.get(row.get('sourceSentenceId'),{}).get('panelId') or row.get('sourceOptionId') != sentence_by_id.get(row.get('sourceSentenceId'),{}).get('optionId') for row in source_ops):
            failures.append({'check':'Robot semantic sentence/panel/option order projection','ttsCardId':card_id})
        if item.get('unresolvedQuestionRefs') != EXPECTED_ROBOT_QUESTION_REFS[expected['ruleId']] or item.get('status') != 'source-backed-with-open-question':
            failures.append({'check':'Robot no-default question projection','ttsCardId':card_id})
        if item.get('authority',{}).get('highest') != 'official-primary':
            failures.append({'check':'Robot authority lock','ttsCardId':card_id})
        target_ids = {row.get('targetId') for row in item.get('targets') or []}
        used_targets = {row.get('targetRef') for row in item.get('operations') or [] if row.get('targetRef')}
        if target_ids != used_targets:
            failures.append({'check':'Robot target usage closure','ttsCardId':card_id})
        if item.get('partialResolution',{}).get('policy') != 'all-or-nothing-selection' or item.get('title') != expected['title'].title():
            failures.append({'check':'Robot face option legality/title projection','ttsCardId':card_id})
    activate_robot = record_by_id.get('SEM-ACT-ROBOT-001') or {}
    activation_dispatch = next((row.get('dispatchRuleIds') for row in activate_robot.get('operations') or [] if row.get('dispatchRuleIds')), None)
    activation_costs = [(row.get('costId'),row.get('quantity')) for row in activate_robot.get('costs') or []]
    if activation_dispatch != [EXPECTED_ROBOT_OCCURRENCES[card_id]['ruleId'] for card_id in sorted(EXPECTED_ROBOT_OCCURRENCES)] or activation_costs != [('COST-ACT-ROBOT-BASE',1),('COST-ACT-ROBOT-REMOTE',1)] or 'Not In Combat' not in json.dumps(activate_robot,ensure_ascii=False) or 'Data token' not in json.dumps(activate_robot,ensure_ascii=False):
        failures.append({'check':'Robot activation cost/availability/exact dispatch'})
    setup_robot = record_by_id.get('SEM-ROBOT-SETUP-001') or {}
    setup_text = json.dumps(setup_robot,ensure_ascii=False)
    if not all(fragment in setup_text for fragment in ('hidden-from-all','five unselected Robot cards unseen in box','"Ammo": 20','"Oxygen": 20','"finiteRobotModels": 1','sem.state.robot-card.unrevealed')) or not any((row.get('transition') or {}).get('to') == 'tax.scaffold.zone.removed-from-game' for row in setup_robot.get('operations') or []):
        failures.append({'check':'Robot hidden random setup/finite-component lifecycle'})
    reveal_robot = record_by_id.get('SEM-ROBOT-REVEAL-001') or {}
    reveal_information = reveal_robot.get('informationPolicy') or []
    if reveal_robot.get('unresolvedQuestionRefs') != ['SEM-Q-012'] or not any(row.get('audience') == 'hidden-from-all-before-trigger; public-after-trigger' and 'first Room connected' in row.get('revealTrigger','') for row in reveal_information) or not any(row.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-012' in row.get('objectRef','') for row in reveal_robot.get('operations') or []):
        failures.append({'check':'Robot reveal/visibility no-leak boundary'})
    movement_robot = record_by_id.get('SEM-ROBOT-MOVEMENT-001') or {}
    movement_decisions = movement_robot.get('decisions') or []
    movement_targets = movement_robot.get('targets') or []
    movement_text = json.dumps(movement_robot,ensure_ascii=False)
    if movement_robot.get('unresolvedQuestionRefs') != ['SEM-Q-013'] or len(movement_decisions) != 1 or movement_decisions[0].get('selectionMode') != 'unresolved' or movement_decisions[0].get('ownerRef') != 'P-MOVE-OWNER' or movement_decisions[0].get('cardinality') != {'min':0,'max':1} or len(movement_targets) != 1 or movement_targets[0].get('selectorRef') != 'unresolved-by-source' or movement_targets[0].get('selectionMode') != 'unresolved-when-multiple' or not all(fragment in movement_text for fragment in ('zeroStepsLegal','no Noise roll','Closed Door','Unexplored Corridor')):
        failures.append({'check':'Robot movement no invented owner/target/default'})
    robot_gear = record_by_id.get('SEM-ROBOT-TACTICAL-GEAR-001') or {}
    if not all(fragment in json.dumps(robot_gear,ensure_ascii=False) for fragment in ('same Room','robotMalfunctionDoesNotBlock','between compatible Character and Robot')):
        failures.append({'check':'Robot Tactical Gear co-location/malfunction boundary'})
    robot_malfunction = record_by_id.get('SEM-ROBOT-MALFUNCTION-001') or {}
    malfunction_placement = record_by_id.get('SEM-ROBOT-MALFUNCTION-PLACEMENT-001') or {}
    if robot_malfunction.get('unresolvedQuestionRefs') != ['SEM-Q-010'] or len(robot_malfunction.get('sourceAssertions') or []) != 2 or not any(row.get('operationType') == 'resolve-open-alternative' for row in robot_malfunction.get('operations') or []):
        failures.append({'check':'Robot equal-authority contradiction boundary'})
    malfunction_text = json.dumps(malfunction_placement,ensure_ascii=False)
    if malfunction_placement.get('unresolvedQuestionRefs') != ['SEM-Q-010','SEM-Q-012'] or not all(fragment in malfunction_text for fragment in ('14 finite Malfunctions','9 finite Fire','sem.state.robot.broken','tax.scaffold.supply-pool','SEM-Q-010','SEM-Q-012')) or 'Robot destroyed' in malfunction_text or 'destroyed Robot' in malfunction_text:
        failures.append({'check':'Robot Malfunction placement/repeat/fallback lifecycle'})
    rise = record_by_id.get('SEM-EVENT-RISE-OF-THE-MACHINE-001') or {}
    if rise.get('unresolvedQuestionRefs') != ['SEM-Q-010','SEM-Q-012'] or not any(row.get('invokeRuleId') == 'SEM-ROBOT-MALFUNCTION-PLACEMENT-001' for row in rise.get('operations') or []):
        failures.append({'check':'Rise of the Machine Robot reusable placement/pre-reveal boundary'})
    exploration_robot = record_by_id.get('SEM-ROBOT-EXPLORATION-001') or {}
    exploration_dispatch = next((row.get('dispatchRuleIds') for row in exploration_robot.get('operations') or [] if row.get('dispatchRuleIds')), None)
    if exploration_dispatch != [EXPECTED_EXPLORATION_OCCURRENCES[card_id]['ruleId'] for card_id in sorted(EXPECTED_EXPLORATION_OCCURRENCES)] or not any('ignores every Entrance-effect' in row.get('objectRef','') for row in exploration_robot.get('operations') or []) or not any('SEM-Q-014' in row.get('objectRef','') for row in exploration_robot.get('operations') or []):
        failures.append({'check':'Exploration Robot exact dispatch/Entrance/Noise boundary'})
    securing_robot = record_by_id.get('SEM-ROBOT-SECURING-001') or {}
    securing_text = json.dumps(securing_robot,ensure_ascii=False)
    if not all(fragment in securing_text for fragment in ('SEM-Q-016','SEM-Q-017','"globalFiniteSupply": 20','"perRoomMaximum": 3','"partialPlacement": "SEM-Q-017 unresolved"')):
        failures.append({'check':'Securing Robot Door/Secure no-default finite boundary'})
    server_robot = record_by_id.get('SEM-ROBOT-SERVER-001') or {}
    if not any(row.get('operationType') == 'invoke-selected-process' and row.get('dispatchRuleIds') == [f'SEM-ROOM-{index:02d}' for index in range(1,26)] and 'No second Basic-Action cost' in row.get('notes','') for row in server_robot.get('operations') or []) or any(row.get('invokeRuleId') == 'SEM-USE-ROOM-001' for row in server_robot.get('operations') or []):
        failures.append({'check':'Server Robot Room actor/cost no-default boundary'})
    medical_robot = record_by_id.get('SEM-ROBOT-MEDICAL-001') or {}
    if not any(row.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-015' in row.get('objectRef','') for row in medical_robot.get('operations') or []) or not any((row.get('valueChange') or {}).get('amount') == '0 through +2 chosen under SEM-Q-015' for row in medical_robot.get('operations') or []):
        failures.append({'check':'Medical Robot branch/restoration owner boundary'})
    technical_robot = record_by_id.get('SEM-ROBOT-TECHNICAL-001') or {}
    if not any(row.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-019' in row.get('objectRef','') for row in technical_robot.get('operations') or []) or 'automatic self-repair' not in json.dumps(technical_robot,ensure_ascii=False):
        failures.append({'check':'Technical Robot marker-target scope boundary'})
    military_robot = record_by_id.get('SEM-ROBOT-MILITARY-001') or {}
    military_types = [row.get('operationType') for row in military_robot.get('operations') or [] if row.get('sourceOptionId') == 'O2']
    if military_types != ['select-target','draw-random','change-value','invoke-process'] or not any(row.get('invokeRuleId') == 'SEM-ROBOT-MALFUNCTION-PLACEMENT-001' for row in military_robot.get('operations') or []) or 'spends no Ammo' not in json.dumps(military_robot,ensure_ascii=False):
        failures.append({'check':'Military Robot target/Hit/additional-effect order'})
    question_by_id = {row.get('questionId'):row for row in question_rows}
    robot_question_blocks = {
        'SEM-Q-012':['SEM-ROBOT-REVEAL-001','SEM-ROBOT-MALFUNCTION-PLACEMENT-001','SEM-EVENT-RISE-OF-THE-MACHINE-001'],
        'SEM-Q-013':['SEM-ROBOT-MOVEMENT-001',*[EXPECTED_ROBOT_OCCURRENCES[card_id]['ruleId'] for card_id in sorted(EXPECTED_ROBOT_OCCURRENCES)]],
        'SEM-Q-014':['SEM-ROBOT-EXPLORATION-001'],'SEM-Q-015':['SEM-ROBOT-MEDICAL-001'],
        'SEM-Q-016':['SEM-ROBOT-SECURING-001'],'SEM-Q-017':['SEM-ROBOT-SECURING-001'],
        'SEM-Q-018':['SEM-ROBOT-SERVER-001'],'SEM-Q-019':['SEM-ROBOT-TECHNICAL-001'],
    }
    for question_id,blocks in robot_question_blocks.items():
        question = question_by_id.get(question_id) or {}
        if question.get('defaultProhibited') is not True or question.get('blocksRuleIds') != blocks or len(question.get('alternatives') or []) != 3:
            failures.append({'check':'Robot ambiguity no-default alternatives/linkage','questionId':question_id})
    q10 = question_by_id.get('SEM-Q-010') or {}
    q10_alternative_ids = [row.get('alternativeId') for row in q10.get('alternatives') or []]
    if q10.get('defaultProhibited') is not True or q10.get('blocksRuleIds') != ['SEM-ROBOT-MALFUNCTION-001','SEM-ROBOT-MALFUNCTION-PLACEMENT-001','SEM-EVENT-RISE-OF-THE-MACHINE-001'] or q10_alternative_ids != ['SEM-Q-010-A','SEM-Q-010-B','SEM-Q-010-C'] or 'Page 22 controls' not in (q10.get('alternatives') or [{}])[0].get('description','') or 'Page 37 controls' not in (q10.get('alternatives') or [{},{}])[1].get('description',''):
        failures.append({'check':'SEM-Q-010 exact unresolved contradiction preservation'})
    actual_robot_lock_ids = set(EXPECTED_ROBOT_RECORD_DIGESTS) & set(record_by_id)
    if actual_robot_lock_ids != set(EXPECTED_ROBOT_RECORD_DIGESTS):
        failures.append({'check':'independently locked Robot semantic projection','missing':sorted(set(EXPECTED_ROBOT_RECORD_DIGESTS)-actual_robot_lock_ids)})
    for rule_id,expected_digest in EXPECTED_ROBOT_RECORD_DIGESTS.items():
        item = record_by_id.get(rule_id)
        actual_digest = hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest() if item else None
        if actual_digest != expected_digest:
            failures.append({'check':'independently locked Robot semantic projection','ruleId':rule_id,'actual':actual_digest})
    robot_system = next((row for row in coverage.get('systems') or [] if row.get('system') == 'base Robot card/component family'), {})
    expected_robot_system_ids = ['SEM-ACT-ROBOT-001','SEM-ROBOT-SETUP-001','SEM-ROBOT-REVEAL-001','SEM-ROBOT-MOVEMENT-001','SEM-ROBOT-TACTICAL-GEAR-001','SEM-ROBOT-MALFUNCTION-001','SEM-ROBOT-MALFUNCTION-PLACEMENT-001',*[EXPECTED_ROBOT_OCCURRENCES[card_id]['ruleId'] for card_id in sorted(EXPECTED_ROBOT_OCCURRENCES)]]
    if robot_system.get('ruleIds') != expected_robot_system_ids or any(fragment in not_yet_text for fragment in ('all Robot','Item/Robot/Attack')):
        failures.append({'check':'Robot coverage stale not-yet-covered claim'})

    expected_attack_rule_ids = {value[6] for value in EXPECTED_ATTACK_OCCURRENCES.values()}
    actual_attack_rule_ids = {rule_id for rule_id in record_by_id if rule_id.startswith('SEM-ATTACK-')}
    if actual_attack_rule_ids != expected_attack_rule_ids:
        failures.append({'check':'Attack semantic face-record closure','missing':sorted(expected_attack_rule_ids-actual_attack_rule_ids),'extra':sorted(actual_attack_rule_ids-expected_attack_rule_ids)})
    branch_families = {'BITE','DEADLY CLAWS','TAIL ATTACK'}
    for card_id,expected in EXPECTED_ATTACK_OCCURRENCES.items():
        source_id,path_value,source_sha,guid,cell,bga_key,rule_id,title,badge_types,badge_panels,panel_count,sentence_count,inline_refs,official_refs,question_refs = expected
        source_face = attack_by_card.get(card_id) or {}
        item = record_by_id.get(rule_id) or {}
        assertions = {row.get('assertionId'):row for row in item.get('sourceAssertions') or []}
        scan = assertions.get(f'SA-ATK-{card_id}-SCAN') or {}
        licensed = assertions.get(f'SA-ATK-{card_id}-BGA') or {}
        if (scan.get('sourceId'),scan.get('sourceSha256'),scan.get('sourceText'),scan.get('textKind')) != (source_id,source_sha,source_face.get('printedBody'),'verbatim'):
            failures.append({'check':'Attack exact scan assertion projection','ttsCardId':card_id})
        if (licensed.get('sourceId'),licensed.get('sourceText'),licensed.get('textKind')) != ('SRC-BGA-INTRUDER-ATTACKS',(source_face.get('bgaOccurrence') or {}).get('sourceBlockText'),'verbatim'):
            failures.append({'check':'Attack exact licensed assertion projection','ttsCardId':card_id})
        variants = item.get('sourceVariants') or []
        expected_variants = [(f'SV-ATK-{card_id}-BGA','SRC-BGA-INTRUDER-ATTACKS',f'SA-ATK-{card_id}-BGA')]
        expected_variants.extend((f'SV-ATK-{card_id}-OFFICIAL-{index:02d}','SRC-RULEBOOK',f'SA-ATK-{card_id}-OFFICIAL-{index:02d}') for index in range(1,len(official_refs)+1))
        actual_variants = [(row.get('variantId'),row.get('sourceId'),row.get('sourceAssertionId')) for row in variants]
        if actual_variants != expected_variants or any(not row.get('difference') or not row.get('resolution') for row in variants):
            failures.append({'check':'Attack licensed/official source-variant closure','ttsCardId':card_id})
        sentence_by_id = {row.get('sentenceId'):row for row in source_face.get('sentences') or []}
        operations = item.get('operations') or []
        operation_sentence_ids = [row.get('sourceSentenceId') for row in operations]
        first_sentence_order = list(dict.fromkeys(operation_sentence_ids))
        expected_sentence_order = [row.get('sentenceId') for row in source_face.get('sentences') or []]
        if not operations or first_sentence_order != expected_sentence_order or any(row.get('sourceSentenceId') not in sentence_by_id or row.get('sourcePanelId') != sentence_by_id.get(row.get('sourceSentenceId'),{}).get('panelId') for row in operations):
            failures.append({'check':'Attack semantic sentence/panel order projection','ttsCardId':card_id})
        badge_by_panel = {}
        for badge in source_face.get('applicabilityBadgeOccurrences') or []:
            badge_by_panel.setdefault(badge.get('panelId'),[]).append(badge.get('occurrenceId'))
        for op in operations:
            expected_badges = badge_by_panel.get(op.get('sourcePanelId'),[])
            if op.get('sourceApplicabilityBadgeIds') != expected_badges:
                failures.append({'check':'Attack semantic applicability badge linkage','ttsCardId':card_id,'stepId':op.get('stepId')})
        if tuple(item.get('unresolvedQuestionRefs') or []) != question_refs or (item.get('status') == 'source-backed-with-open-question') != bool(question_refs):
            failures.append({'check':'Attack no-default question projection','ttsCardId':card_id})
        expected_authority = 'official-errata' if card_id == 394912 else 'official-primary'
        if item.get('authority',{}).get('highest') != expected_authority:
            failures.append({'check':'Attack authority lock','ttsCardId':card_id})
        if item.get('decisions'):
            failures.append({'check':'Attack no invented face decision owner','ttsCardId':card_id})
        target_ids = {row.get('targetId') for row in item.get('targets') or []}
        used_targets = {row.get('targetRef') for row in operations if row.get('targetRef')}
        if target_ids != used_targets:
            failures.append({'check':'Attack target usage closure','ttsCardId':card_id})
        if title in branch_families and not any(row.get('operationType') == 'branch' for row in operations):
            failures.append({'check':'Attack condition/otherwise branch preservation','ttsCardId':card_id})
        condition_text = json.dumps(item.get('preconditions') or [],ensure_ascii=False)
        if f'TTS-ATTACK-{card_id}-FACE' not in condition_text or (badge_types and not all(f'ATK-{card_id}-B{index:02d}' in condition_text for index in range(1,len(badge_types)+1))):
            failures.append({'check':'Attack exact occurrence/applicability precondition','ttsCardId':card_id})
        if any((row.get('transition') or {}).get('to') == 'tax.scaffold.zone.discard-pile' and 'Contamination' not in row.get('objectRef','') for row in operations):
            failures.append({'check':'Attack generic draw/discard ownership','ttsCardId':card_id})
        if item.get('partialResolution',{}).get('unit') != 'one exact source panel selected by one attacking-Intruder badge occurrence' or str(card_id) not in item.get('title',''):
            failures.append({'check':'Attack occurrence title/partial-resolution lock','ttsCardId':card_id})
    generic_attack = record_by_id.get('SEM-INT-004') or {}
    generic_attack_dispatch = next((row.get('dispatchRuleIds') for row in generic_attack.get('operations') or [] if row.get('dispatchRuleIds')), None)
    expected_attack_dispatch = [EXPECTED_ATTACK_OCCURRENCES[card_id][6] for card_id in sorted(EXPECTED_ATTACK_OCCURRENCES)]
    generic_attack_discard = next((row for row in generic_attack.get('operations') or [] if row.get('operationType') == 'transition-zone'), {})
    if generic_attack_dispatch != expected_attack_dispatch or (generic_attack_discard.get('transition') or {}).get('from') != 'sem.zone.card-in-resolution' or not generic_attack_discard.get('conditionRefs') or 'still in resolution' not in generic_attack_discard.get('objectRef',''):
        failures.append({'check':'Generic Attack exact occurrence dispatch/conditional discard'})
    miss = record_by_id.get('SEM-ATTACK-394912-001') or {}
    miss_text = json.dumps(miss,ensure_ascii=False)
    if miss.get('unresolvedQuestionRefs') != ['SEM-Q-024'] or not any(row.get('operationType') == 'transition-zone' and (row.get('transition') or {}).get('to') == 'tax.scaffold.zone.deck' for row in miss.get('operations') or []) or not any(row.get('operationType') == 'shuffle' and 'including this MISS card' in row.get('objectRef','') for row in miss.get('operations') or []) or 'FQ-P02-U11' not in miss_text:
        failures.append({'check':'Attack MISS applicability/self-inclusive reshuffle boundary'})
    contamination_gain = record_by_id.get('SEM-CONTAMINATION-GAIN-001') or {}
    contamination_types = [row.get('operationType') for row in contamination_gain.get('operations') or []]
    if contamination_types != ['draw-random','transition-zone'] or (contamination_gain.get('operations') or [{},{}])[1].get('transition') != {'from':'tax.scaffold.zone.deck','to':'tax.scaffold.zone.discard-pile','positionRef':'sem.position.deck-top'} or '27' not in json.dumps(contamination_gain):
        failures.append({'check':'Attack reusable finite Contamination gain procedure'})
    question_by_id = {row.get('questionId'):row for row in question_rows}
    expected_attack_question_blocks = {
        question_id:[EXPECTED_ATTACK_OCCURRENCES[card_id][6] for card_id in sorted(EXPECTED_ATTACK_OCCURRENCES) if question_id in EXPECTED_ATTACK_OCCURRENCES[card_id][14]]
        for question_id in ('SEM-Q-020','SEM-Q-021','SEM-Q-022','SEM-Q-023','SEM-Q-024')
    }
    for question_id,blocks in expected_attack_question_blocks.items():
        question = question_by_id.get(question_id) or {}
        if question.get('defaultProhibited') is not True or question.get('blocksRuleIds') != blocks or len(question.get('alternatives') or []) != 3:
            failures.append({'check':'Attack ambiguity no-default alternatives/linkage','questionId':question_id})
    deadly = [record_by_id.get(f'SEM-ATTACK-{card_id}-001') or {} for card_id in (394906,394907,394908)]
    infecting = record_by_id.get('SEM-ATTACK-394911-001') or {}
    tails = [record_by_id.get(f'SEM-ATTACK-{card_id}-001') or {} for card_id in (394918,394919)]
    fury = [record_by_id.get(f'SEM-ATTACK-{card_id}-001') or {} for card_id in (394909,394910)]
    if not all('Adult or Drone' in json.dumps(row) and 'attacking type is Queen' in json.dumps(row) for row in deadly) or 'Adult or Queen in this exact scan occurrence' not in json.dumps(infecting) or not all('Adult or Queen in this exact scan occurrence' in json.dumps(row) and 'attacking type is Drone' in json.dumps(row) for row in tails) or not all('SEM-Q-020' in row.get('unresolvedQuestionRefs',[]) for row in fury):
        failures.append({'check':'Attack exact variant applicability/branch preservation'})
    attack_conflicts = {row.get('conflictId'):row for row in conflict_rows if row.get('conflictId') in {'SC-015','SC-016','SC-017','SC-018'}}
    if set(attack_conflicts) != {'SC-015','SC-016','SC-017','SC-018'} or attack_conflicts.get('SC-018',{}).get('questionId') != 'SEM-Q-020' or any(attack_conflicts.get(conflict_id,{}).get('status') != 'resolved-by-authority' for conflict_id in ('SC-015','SC-016','SC-017')):
        failures.append({'check':'Attack source-variant authority/conflict closure'})
    actual_attack_lock_ids = set(EXPECTED_ATTACK_RECORD_DIGESTS) & set(record_by_id)
    if actual_attack_lock_ids != set(EXPECTED_ATTACK_RECORD_DIGESTS):
        failures.append({'check':'independently locked Attack semantic projection','missing':sorted(set(EXPECTED_ATTACK_RECORD_DIGESTS)-actual_attack_lock_ids)})
    for rule_id,expected_digest in EXPECTED_ATTACK_RECORD_DIGESTS.items():
        item = record_by_id.get(rule_id)
        actual_digest = hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest() if item else None
        if actual_digest != expected_digest:
            failures.append({'check':'independently locked Attack semantic projection','ruleId':rule_id,'actual':actual_digest})
    attack_system = next((row for row in coverage.get('systems') or [] if row.get('system') == 'Intruder Attack, base Attack cards, Secure entry, and Character Health'), {})
    expected_attack_system_ids = ['SEM-INT-004','SEM-SECURE-ENTRY-001','SEM-INT-006','SEM-CONTAMINATION-GAIN-001',*[EXPECTED_ATTACK_OCCURRENCES[card_id][6] for card_id in sorted(EXPECTED_ATTACK_OCCURRENCES)]]
    if attack_system.get('ruleIds') != expected_attack_system_ids or any(fragment in not_yet_text for fragment in ('Item/Attack','remaining Item/Attack','all Attack')):
        failures.append({'check':'Attack coverage stale not-yet-covered claim'})

    expected_queen_rule_ids = {expected['ruleId'] for expected in EXPECTED_QUEEN_HEALTH_OCCURRENCES.values()}
    actual_queen_rule_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r'SEM-QUEEN-HEALTH-\d+-[A-Z0-9]+-001',rule_id)}
    if actual_queen_rule_ids != expected_queen_rule_ids:
        failures.append({'check':'Queen Health semantic physical face-record closure','missing':sorted(expected_queen_rule_ids-actual_queen_rule_ids),'extra':sorted(actual_queen_rule_ids-expected_queen_rule_ids)})
    for occurrence_id,expected in EXPECTED_QUEEN_HEALTH_OCCURRENCES.items():
        source_face = queen_by_occurrence.get(occurrence_id) or {}
        item = record_by_id.get(expected['ruleId']) or {}
        code = occurrence_id.removeprefix('TTS-QUEEN-HEALTH-').removesuffix('-FACE')
        assertions = {row.get('assertionId'):row for row in item.get('sourceAssertions') or []}
        scan = assertions.get(f'SA-QHF-{code}-SCAN') or {}
        licensed = assertions.get(f'SA-QHF-{code}-BGA') or {}
        expected_source_id = 'SRC-QUEEN-HEALTH-'+code
        if (scan.get('sourceId'),scan.get('sourceSha256'),scan.get('sourceText'),scan.get('textKind')) != (expected_source_id,expected['sha256'],source_face.get('printedBody'),'verbatim'):
            failures.append({'check':'Queen Health exact physical scan assertion projection','occurrenceId':occurrence_id})
        expected_bga_text = '\n'.join(row.get('sourceBlockText','') for row in (source_face.get('bgaVariantCandidates') or {}).get('candidates') or [])
        if (licensed.get('sourceId'),licensed.get('sourceText'),licensed.get('textKind')) != ('SRC-BGA-QUEEN-HEALTH',expected_bga_text,'verbatim'):
            failures.append({'check':'Queen Health exact licensed candidate assertion projection','occurrenceId':occurrence_id})
        variants = item.get('sourceVariants') or []
        expected_variants = [(f'SV-QHF-{code}-BGA','SRC-BGA-QUEEN-HEALTH',f'SA-QHF-{code}-BGA')]
        expected_variants.extend((f'SV-QHF-{code}-OFFICIAL-{index:02d}','SRC-RULEBOOK',f'SA-QHF-{code}-OFFICIAL-{index:02d}') for index in range(1,len(expected['official'])+1))
        if [(row.get('variantId'),row.get('sourceId'),row.get('sourceAssertionId')) for row in variants] != expected_variants or any(not row.get('difference') or not row.get('resolution') for row in variants):
            failures.append({'check':'Queen Health licensed/official source-variant closure','occurrenceId':occurrence_id})
        sentence_by_id = {row.get('sentenceId'):row for row in source_face.get('sentences') or []}
        source_ops = [row for row in item.get('operations') or [] if row.get('sourceSentenceId')]
        first_sentence_order = list(dict.fromkeys(row.get('sourceSentenceId') for row in source_ops))
        expected_sentence_order = [row.get('sentenceId') for row in source_face.get('sentences') or []]
        if not source_ops or first_sentence_order != expected_sentence_order or any(row.get('sourceSentenceId') not in sentence_by_id or row.get('sourcePanelId') != sentence_by_id.get(row.get('sourceSentenceId'),{}).get('panelId') for row in source_ops):
            failures.append({'check':'Queen Health semantic sentence/panel order projection','occurrenceId':occurrence_id})
        expected_questions = ['SEM-Q-026','SEM-Q-027'] + (['SEM-Q-028'] if expected['cardId'] == 458100 else [])
        if item.get('unresolvedQuestionRefs') != expected_questions or item.get('status') != 'source-backed-with-open-question':
            failures.append({'check':'Queen Health face no-default question projection','occurrenceId':occurrence_id})
        if item.get('authority',{}).get('highest') != 'official-primary' or item.get('title') != f'Queen Health physical occurrence {code}':
            failures.append({'check':'Queen Health face authority/physical-title lock','occurrenceId':occurrence_id})
        number_op = (item.get('operations') or [{}])[0]
        if number_op.get('operationType') != 'change-value' or (number_op.get('valueChange') or {}).get('amount') != expected['discard'] or 'source-local no-alias' not in (number_op.get('notes') or ''):
            failures.append({'check':'Queen Health semantic number/display no-alias projection','occurrenceId':occurrence_id})
        if any(row.get('operationType') == 'shuffle' for row in item.get('operations') or []) or any((row.get('transition') or {}).get('from') == 'sem.zone.card-in-resolution' for row in item.get('operations') or []):
            failures.append({'check':'Queen Health generic lifecycle ownership/no-face-reshuffle','occurrenceId':occurrence_id})
        decisions = item.get('decisions') or []
        if expected['cardId'] == 458100:
            if len(decisions) != 1 or decisions[0].get('selectionMode') != 'unresolved' or decisions[0].get('ownerRef') != 'P-BRANCH-OWNER' or not any(row.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-028' in row.get('objectRef','') for row in item.get('operations') or []):
                failures.append({'check':'Queen Health Malfunction/Unreinforce no invented branch owner/default'})
        elif decisions:
            failures.append({'check':'Queen Health no invented face decision owner','occurrenceId':occurrence_id})
        target_ids = {row.get('targetId') for row in item.get('targets') or []}
        used_targets = {row.get('targetRef') for row in item.get('operations') or [] if row.get('targetRef')}
        if target_ids != used_targets:
            failures.append({'check':'Queen Health face target usage closure','occurrenceId':occurrence_id})
    queen_resolution = record_by_id.get('SEM-QUEEN-HEALTH-RESOLUTION-001') or {}
    resolution_ops = queen_resolution.get('operations') or []
    resolution_types = [row.get('operationType') for row in resolution_ops]
    resolution_dispatch = next((row.get('dispatchRuleIds') for row in resolution_ops if row.get('dispatchRuleIds')), None)
    expected_queen_dispatch = [EXPECTED_QUEEN_HEALTH_OCCURRENCES[occurrence_id]['ruleId'] for occurrence_id in expected_queen_occurrence_ids]
    expected_resolution_component_assertions = ['SA-QH-RESOLUTION-FACE-'+occurrence_id.removeprefix('TTS-QUEEN-HEALTH-').removesuffix('-FACE') for occurrence_id in expected_queen_occurrence_ids]
    resolution_assertion_ids = [row.get('assertionId') for row in queen_resolution.get('sourceAssertions') or []]
    dispatch_op = next((row for row in resolution_ops if row.get('dispatchRuleIds')), {})
    if resolution_assertion_ids != ['SA-QH-RESOLUTION-RB',*expected_resolution_component_assertions] or dispatch_op.get('sourceAssertionIds') != ['SA-QH-RESOLUTION-RB',*expected_resolution_component_assertions]:
        failures.append({'check':'Queen Health exact dispatcher source-assertion closure'})
    additional_discard = next((row for row in resolution_ops if row.get('operationType') == 'transition-zone' and 'additional Queen Health' in row.get('objectRef','')), {})
    drawn_discard = next((row for row in resolution_ops if row.get('operationType') == 'transition-zone' and 'drawn Queen Health' in row.get('objectRef','')), {})
    reset = next((row for row in resolution_ops if row.get('operationType') == 'change-value' and 'reset to 0' in row.get('objectRef','')), {})
    if resolution_types != ['draw-random','reveal','resolve-open-alternative','transition-zone','invoke-process','resolve-open-alternative','invoke-selected-process','transition-zone','invoke-process','change-value'] or resolution_dispatch != expected_queen_dispatch or (additional_discard.get('transition') or {}) != {'from':'tax.scaffold.zone.deck','to':'tax.scaffold.zone.discard-pile'} or (additional_discard.get('repeat') or {}).get('reveal') is not False or (drawn_discard.get('transition') or {}).get('from') != 'sem.zone.card-in-resolution' or (reset.get('valueChange') or {}).get('overflowCarry') is not False or any(row.get('operationType') == 'shuffle' for row in resolution_ops):
        failures.append({'check':'Queen Health draw/hidden-discard/effect/drawn-discard/reset/no-reshuffle order lock'})
    if queen_resolution.get('unresolvedQuestionRefs') != ['SEM-Q-025','SEM-Q-026','SEM-Q-027'] or not any(row.get('audience') == 'hidden-from-all' and 'without revealing' in row.get('secrecy','') for row in queen_resolution.get('informationPolicy') or []):
        failures.append({'check':'Queen Health lifecycle visibility/no-default lock'})
    queen_hit = record_by_id.get('SEM-QUEEN-HIT-001') or {}
    hit_ops = queen_hit.get('operations') or []
    hit_change = hit_ops[0] if hit_ops else {}
    hit_repeat = hit_change.get('repeat') or {}
    if queen_hit.get('unresolvedQuestionRefs') != ['SEM-Q-025','SEM-Q-029'] or hit_repeat != {'sourceAssignedHits':'one at a time','sameActionOverflow':'ignored after trigger','crossActionCarry':True} or not any(row.get('operationType') == 'set-state' and 'ignore all later Hits' in row.get('objectRef','') for row in hit_ops) or not any(row.get('invokeRuleId') == 'SEM-QUEEN-HEALTH-RESOLUTION-001' for row in hit_ops):
        failures.append({'check':'Queen Health Hit carry/threshold/overflow/default lock'})
    shoot = record_by_id.get('SEM-ACT-SHOOT-001') or {}
    burst = record_by_id.get('SEM-ACT-BURST-001') or {}
    shoot_ops = shoot.get('operations') or []
    burst_ops = burst.get('operations') or []
    shoot_initial = next((index for index,row in enumerate(shoot_ops) if row.get('invokeRuleId') == 'SEM-QUEEN-HIT-001' and 'initial Shoot Hit' in row.get('objectRef','')), None)
    shoot_roll = next((index for index,row in enumerate(shoot_ops) if row.get('operationType') == 'draw-random'), None)
    burst_queen = next((index for index,row in enumerate(burst_ops) if row.get('invokeRuleId') == 'SEM-QUEEN-HIT-001'), None)
    burst_extra = next((index for index,row in enumerate(burst_ops) if 'additional-effects symbol' in row.get('objectRef','')), None)
    if shoot.get('unresolvedQuestionRefs') != ['SEM-Q-025','SEM-Q-029'] or burst.get('unresolvedQuestionRefs') != ['SEM-Q-025'] or shoot_initial is None or shoot_roll is None or shoot_initial >= shoot_roll or burst_queen is None or burst_extra is None or burst_queen >= burst_extra or (burst_ops[burst_queen].get('repeat') or {}).get('sameActionOverflow') != 'lost':
        failures.append({'check':'Queen Health Shoot-versus-Burst timing/allocation boundary'})
    queen_death = record_by_id.get('SEM-QUEEN-DEATH-001') or {}
    death_text = json.dumps(queen_death,ensure_ascii=False)
    if queen_death.get('unresolvedQuestionRefs') != ['SEM-Q-027'] or not all(fragment in death_text for fragment in ('last Queen Health card was discarded','Queen Health deck is empty','Facility was destroyed','Queen model','future Queen placements','Intruder Help sheet')):
        failures.append({'check':'Queen Health death/endgame/Help-state boundary'})
    queen_activation = record_by_id.get('SEM-QUEEN-ACTIVATION-001') or {}
    if [row.get('operationType') for row in queen_activation.get('operations') or []] != ['select-target','invoke-process','select-target','move-entity'] or not any(row.get('invokeRuleId') == 'SEM-INT-004' for row in queen_activation.get('operations') or []):
        failures.append({'check':'Queen Activation Attack/movement reuse boundary'})
    action_draw = record_by_id.get('SEM-ACTION-CARD-DRAW-001') or {}
    if [row.get('operationType') for row in action_draw.get('operations') or []] != ['evaluate-condition','shuffle','draw-random'] or not any(row.get('invokeRuleId') == 'SEM-ACTION-CARD-DRAW-001' and (row.get('repeat') or {}).get('perCharacter') == 2 for row in (record_by_id.get('SEM-QUEEN-HEALTH-503900-B42831-001') or {}).get('operations') or []):
        failures.append({'check':'Queen Health reusable Action-card draw/renewal order'})
    noise_face = record_by_id.get('SEM-QUEEN-HEALTH-503800-64AE0A-001') or {}
    if not any(row.get('invokeRuleId') == 'SEM-NOISE-001' and (row.get('repeat') or {}).get('completeImmediateConsequencesBeforeNext') is True for row in noise_face.get('operations') or []):
        failures.append({'check':'Queen Health per-Character Noise/immediate consequence order'})
    question_by_id = {row.get('questionId'):row for row in question_rows}
    expected_queen_question_blocks = {
        'SEM-Q-025':['SEM-ACT-SHOOT-001','SEM-ACT-BURST-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001'],
        'SEM-Q-026':['SEM-QUEEN-HEALTH-RESOLUTION-001',*expected_queen_dispatch],
        'SEM-Q-027':['SEM-QUEEN-HEALTH-RESOLUTION-001','SEM-QUEEN-DEATH-001',*expected_queen_dispatch],
        'SEM-Q-028':['SEM-QUEEN-HEALTH-458100-6BA0A2-001'],
        'SEM-Q-029':['SEM-ACT-SHOOT-001','SEM-QUEEN-HIT-001'],
    }
    for question_id,blocks in expected_queen_question_blocks.items():
        question = question_by_id.get(question_id) or {}
        if question.get('defaultProhibited') is not True or question.get('blocksRuleIds') != blocks or len(question.get('alternatives') or []) != 3:
            failures.append({'check':'Queen Health ambiguity no-default alternatives/linkage','questionId':question_id})
    queen_conflicts = {row.get('conflictId'):row for row in conflict_rows if row.get('conflictId') in {'SC-019','SC-020','SC-021','SC-022'}}
    if set(queen_conflicts) != {'SC-019','SC-020','SC-021','SC-022'} or queen_conflicts.get('SC-019',{}).get('status') != 'resolved-by-authority' or queen_conflicts.get('SC-020',{}).get('status') != 'resolved-by-authority' or (queen_conflicts.get('SC-021',{}).get('status'),queen_conflicts.get('SC-021',{}).get('questionId')) != ('unresolved','SEM-Q-027') or queen_conflicts.get('SC-022',{}).get('status') != 'preserved-boundary':
        failures.append({'check':'Queen Health source-variant authority/conflict closure'})
    actual_queen_lock_ids = set(EXPECTED_QUEEN_HEALTH_RECORD_DIGESTS) & set(record_by_id)
    if actual_queen_lock_ids != set(EXPECTED_QUEEN_HEALTH_RECORD_DIGESTS):
        failures.append({'check':'independently locked Queen Health semantic projection','missing':sorted(set(EXPECTED_QUEEN_HEALTH_RECORD_DIGESTS)-actual_queen_lock_ids)})
    for rule_id,expected_digest in EXPECTED_QUEEN_HEALTH_RECORD_DIGESTS.items():
        item = record_by_id.get(rule_id)
        actual_digest = hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest() if item else None
        if actual_digest != expected_digest:
            failures.append({'check':'independently locked Queen Health semantic projection','ruleId':rule_id,'actual':actual_digest})
    queen_system = next((row for row in coverage.get('systems') or [] if row.get('system') == 'base Queen Health card/component family'), {})
    expected_queen_system_ids = ['SEM-ACT-SHOOT-001','SEM-ACT-BURST-001','SEM-ACTION-CARD-DRAW-001','SEM-INTRUDER-REPEL-001','SEM-QUEEN-ACTIVATION-001','SEM-QUEEN-HEALTH-SETUP-001','SEM-QUEEN-HIT-001','SEM-QUEEN-HEALTH-RESOLUTION-001','SEM-QUEEN-DEATH-001',*expected_queen_dispatch]
    if queen_system.get('ruleIds') != expected_queen_system_ids or any(fragment in not_yet_text for fragment in ('all remaining Item/Queen Health','all Queen Health')):
        failures.append({'check':'Queen Health coverage stale not-yet-covered claim'})

    expected_serious_wound_rule_ids = {expected['ruleId'] for expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.values()}
    actual_serious_wound_rule_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r'SEM-SERIOUS-WOUND-\d+-[A-Z0-9]+-001',rule_id)}
    if actual_serious_wound_rule_ids != expected_serious_wound_rule_ids:
        failures.append({'check':'Serious Wound semantic physical face-record closure','missing':sorted(expected_serious_wound_rule_ids-actual_serious_wound_rule_ids),'extra':sorted(actual_serious_wound_rule_ids-expected_serious_wound_rule_ids)})
    for occurrence_id,expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.items():
        source_face = serious_wound_by_occurrence.get(occurrence_id) or {}
        item = record_by_id.get(expected['ruleId']) or {}
        code = occurrence_id.removeprefix('TTS-SERIOUS-WOUND-').removesuffix('-FACE')
        assertions = {row.get('assertionId'):row for row in item.get('sourceAssertions') or []}
        scan = assertions.get(f'SA-SWF-{code}-SCAN') or {}
        general = assertions.get(f'SA-SWF-{code}-GENERAL') or {}
        expected_source_id = 'SRC-SERIOUS-WOUND-'+code
        if (scan.get('sourceId'),scan.get('sourceSha256'),scan.get('sourceText'),scan.get('textKind')) != (expected_source_id,expected['sha256'],source_face.get('printedBody'),'verbatim') or general.get('sourceId') != 'SRC-RULEBOOK':
            failures.append({'check':'Serious Wound semantic exact scan/general assertion projection','occurrenceId':occurrence_id})
        if item.get('title') != f'Serious Wound physical occurrence {code}' or item.get('status') != 'source-backed-with-open-question' or item.get('authority',{}).get('highest') != 'official-primary' or item.get('namedIdentityRefs') != [] or item.get('sourceVariants') != []:
            failures.append({'check':'Serious Wound face authority/no-title-identity-join lock','occurrenceId':occurrence_id})
        expected_questions = ['SEM-Q-036']
        if expected['title'] in {'LUNGS','GUTS','BLEEDING'}:
            expected_questions.append('SEM-Q-037')
        if expected['title'] == 'LUNGS':
            expected_questions.insert(1,'SEM-Q-034')
        if expected['title'] == 'BODY':
            expected_questions.append('SEM-Q-035')
        if expected['cardId'] == 404800:
            expected_questions.append('SEM-Q-033')
        expected_questions = list(dict.fromkeys(expected_questions))
        if item.get('unresolvedQuestionRefs') != expected_questions:
            failures.append({'check':'Serious Wound face exact no-default question projection','occurrenceId':occurrence_id})
        operations = item.get('operations') or []
        if not operations or any(op.get('sourceSentenceId') not in {row.get('sentenceId') for row in source_face.get('sentences') or []} or op.get('sourceRegionId') != (source_face.get('regions') or [{},{},{}])[2].get('regionId') or op.get('sourcePanelId') != (source_face.get('panels') or [{},{}])[1].get('panelId') for op in operations):
            failures.append({'check':'Serious Wound face operation-to-sentence/panel/region closure','occurrenceId':occurrence_id})
        if item.get('duration',{}).get('kind') != 'persistent-while-this-physical-card-is-owned; triggered clauses recur only at their printed timing' or 'exact selected FaceURL/source SHA-256' not in item.get('stacking',{}).get('policy',''):
            failures.append({'check':'Serious Wound immediate/persistent duration and exact-duplicate stacking lock','occurrenceId':occurrence_id})
        if expected['title'] == 'LUNGS':
            local_ops = [op for op in operations if 'SEM-Q-034' in op.get('objectRef','')]
            if len(local_ops) != 1 or any(op.get('invokeRuleId') == 'SEM-INT-006' and 'local' in op.get('objectRef','').lower() for op in operations):
                failures.append({'check':'Serious Wound LUNGS local glyph no-default lock','occurrenceId':occurrence_id})
        if expected['cardId'] == 404800 and not any(op.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-033' in op.get('objectRef','') for op in operations):
            failures.append({'check':'Serious Wound KNEE local glyph no-default lock','occurrenceId':occurrence_id})
        if expected['title'] == 'BODY' and not any(op.get('operationType') == 'resolve-open-alternative' and 'SEM-Q-035' in op.get('objectRef','') for op in operations):
            failures.append({'check':'Serious Wound BODY Hand Size no-default lock','occurrenceId':occurrence_id})

    serious_wound_gain = record_by_id.get('SEM-SERIOUS-WOUND-GAIN-001') or {}
    gain_ops = serious_wound_gain.get('operations') or []
    gain_dispatch = next((op.get('dispatchRuleIds') for op in gain_ops if op.get('dispatchRuleIds')), None)
    expected_serious_wound_dispatch = [EXPECTED_SERIOUS_WOUND_OCCURRENCES[occurrence_id]['ruleId'] for occurrence_id in expected_serious_wound_ids]
    if gain_dispatch != expected_serious_wound_dispatch or [op.get('operationType') for op in gain_ops] != ['evaluate-condition','resolve-open-alternative','draw-random','resolve-open-alternative','select-target','place-component','resolve-open-alternative','change-value','resolve-open-alternative','invoke-selected-process','invoke-process','resolve-open-alternative'] or (gain_ops[4] if len(gain_ops)>4 else {}).get('objectRef') != 'leftmost Health Section without a Serious Wound' or 'all three slots' not in (gain_ops[5] if len(gain_ops)>5 else {}).get('objectRef',''):
        failures.append({'check':'Serious Wound finite draw/place/displace/activate/dispatch operation order lock'})
    if any(op.get('operationType') == 'shuffle' for op in gain_ops) or 'never reshuffle' not in serious_wound_gain.get('partialResolution',{}).get('onImpossible','') or serious_wound_gain.get('unresolvedQuestionRefs') != ['SEM-Q-030','SEM-Q-031','SEM-Q-032','SEM-Q-036','SEM-Q-038']:
        failures.append({'check':'Serious Wound lifecycle/no-reshuffle/no-default gain lock'})
    serious_wound_setup = record_by_id.get('SEM-SERIOUS-WOUND-SETUP-001') or {}
    setup_ops = serious_wound_setup.get('operations') or []
    if [op.get('operationType') for op in setup_ops] != ['shuffle','transition-zone','set-state'] or (setup_ops[0].get('repeat') or {}).get('physicalCardCount') != 27 or (setup_ops[1].get('transition') or {}).get('to') != 'tax.scaffold.zone.deck' or 'face down' not in setup_ops[1].get('objectRef',''):
        failures.append({'check':'Serious Wound exact 27-card face-down setup lock'})
    serious_wound_discard = record_by_id.get('SEM-SERIOUS-WOUND-DISCARD-001') or {}
    discard_ops = serious_wound_discard.get('operations') or []
    if [op.get('operationType') for op in discard_ops] != ['select-target','transition-zone','set-state','evaluate-condition','set-state'] or (discard_ops[1].get('transition') or {}).get('to') != 'tax.scaffold.zone.discard-pile' or 'slide' not in discard_ops[2].get('objectRef','') or 'does not move' not in discard_ops[3].get('objectRef','') or serious_wound_discard.get('decisions',[{}])[0].get('ownerRef') != 'P-OWNER':
        failures.append({'check':'Serious Wound discard/owner/slide/no-Health-move lifecycle lock'})
    serious_wound_stacking = record_by_id.get('SEM-SERIOUS-WOUND-STACKING-001') or {}
    if [op.get('operationType') for op in serious_wound_stacking.get('operations') or []] != ['evaluate-condition','set-state','evaluate-condition'] or 'exact selected FaceURL' not in json.dumps(serious_wound_stacking,ensure_ascii=False) or 'title' not in (serious_wound_stacking.get('operations') or [{},{},{}])[2].get('objectRef','').lower():
        failures.append({'check':'Serious Wound duplicate exact-asset stacking/no-title-default lock'})
    variant_boundary = record_by_id.get('SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001') or {}
    variant_rows = variant_boundary.get('sourceVariants') or []
    if variant_boundary.get('status') != 'source-variant' or len(variant_rows) != 14 or len(variant_boundary.get('sourceAssertions') or []) != 6 or len(variant_boundary.get('operations') or []) != 15 or any(row.get('sourceAssertionId') not in {assertion.get('assertionId') for assertion in variant_boundary.get('sourceAssertions') or []} for row in variant_rows) or 'no display-title' not in (variant_boundary.get('operations') or [{}])[-1].get('objectRef',''):
        failures.append({'check':'Serious Wound selector-gap/licensed/official variant preservation lock'})
    health_record = record_by_id.get('SEM-INT-006') or {}
    health_invokes = [op.get('invokeRuleId') for op in health_record.get('operations') or [] if op.get('invokeRuleId')]
    room03_invokes = [op.get('invokeRuleId') for op in (record_by_id.get('SEM-ROOM-03') or {}).get('operations') or [] if op.get('invokeRuleId')]
    room16_ops = (record_by_id.get('SEM-ROOM-16') or {}).get('operations') or []
    robot_medical_invokes = [op.get('invokeRuleId') for op in (record_by_id.get('SEM-ROBOT-MEDICAL-001') or {}).get('operations') or [] if op.get('invokeRuleId')]
    if health_invokes != ['SEM-SERIOUS-WOUND-GAIN-001','SEM-SERIOUS-WOUND-DISCARD-001'] or room03_invokes[-1:] != ['SEM-SERIOUS-WOUND-DISCARD-001'] or len(room16_ops) < 2 or room16_ops[-1].get('invokeRuleId') != 'SEM-SERIOUS-WOUND-DISCARD-001' or not room16_ops[1].get('conditionRefs') or robot_medical_invokes[-1:] != ['SEM-SERIOUS-WOUND-DISCARD-001']:
        failures.append({'check':'Serious Wound Health/Room/Surgery/Robot reusable-procedure integration lock'})
    expected_serious_wound_question_blocks = {
        'SEM-Q-030':['SEM-SERIOUS-WOUND-GAIN-001'],
        'SEM-Q-031':['SEM-SERIOUS-WOUND-GAIN-001'],
        'SEM-Q-032':['SEM-SERIOUS-WOUND-GAIN-001'],
        'SEM-Q-033':[expected['ruleId'] for expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.values() if expected['cardId']==404800],
        'SEM-Q-034':[expected['ruleId'] for expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.values() if expected['title']=='LUNGS'],
        'SEM-Q-035':[expected['ruleId'] for expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.values() if expected['title']=='BODY'],
        'SEM-Q-036':['SEM-SERIOUS-WOUND-GAIN-001',*expected_serious_wound_dispatch],
        'SEM-Q-037':[expected['ruleId'] for expected in EXPECTED_SERIOUS_WOUND_OCCURRENCES.values() if expected['title'] in {'LUNGS','GUTS','BLEEDING'}],
        'SEM-Q-038':['SEM-SERIOUS-WOUND-GAIN-001'],
    }
    for question_id,blocks in expected_serious_wound_question_blocks.items():
        question = question_by_id.get(question_id) or {}
        if question.get('defaultProhibited') is not True or question.get('blocksRuleIds') != blocks or len(question.get('alternatives') or []) != 3:
            failures.append({'check':'Serious Wound ambiguity no-default alternatives/linkage','questionId':question_id})
    serious_wound_conflicts = {row.get('conflictId'):row for row in conflict_rows if row.get('conflictId') in {'SC-023','SC-024','SC-025','SC-026','SC-027','SC-028'}}
    if set(serious_wound_conflicts) != {'SC-023','SC-024','SC-025','SC-026','SC-027','SC-028'} or [serious_wound_conflicts[key].get('status') for key in ('SC-023','SC-024','SC-025','SC-026','SC-027','SC-028')] != ['resolved-by-authority','resolved-by-authority','preserved-boundary','resolved-by-authority','unresolved','unresolved'] or serious_wound_conflicts['SC-027'].get('questionId') != 'SEM-Q-033' or serious_wound_conflicts['SC-028'].get('questionId') != 'SEM-Q-034':
        failures.append({'check':'Serious Wound source-variant authority/conflict closure'})
    actual_serious_wound_lock_ids = set(EXPECTED_SERIOUS_WOUND_RECORD_DIGESTS) & set(record_by_id)
    if actual_serious_wound_lock_ids != set(EXPECTED_SERIOUS_WOUND_RECORD_DIGESTS):
        failures.append({'check':'independently locked Serious Wound semantic projection','missing':sorted(set(EXPECTED_SERIOUS_WOUND_RECORD_DIGESTS)-actual_serious_wound_lock_ids)})
    for rule_id,expected_digest in EXPECTED_SERIOUS_WOUND_RECORD_DIGESTS.items():
        item = record_by_id.get(rule_id)
        actual_digest = hashlib.sha256(json.dumps(item,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest() if item else None
        if actual_digest != expected_digest:
            failures.append({'check':'independently locked Serious Wound semantic projection','ruleId':rule_id,'actual':actual_digest})
    serious_wound_system = next((row for row in coverage.get('systems') or [] if row.get('system') == 'base Serious Wound card/component family'), {})
    expected_serious_wound_system_ids = ['SEM-SERIOUS-WOUND-SETUP-001','SEM-SERIOUS-WOUND-GAIN-001','SEM-SERIOUS-WOUND-DISCARD-001','SEM-SERIOUS-WOUND-STACKING-001','SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001',*expected_serious_wound_dispatch]
    if serious_wound_system.get('ruleIds') != expected_serious_wound_system_ids or any(fragment in not_yet_text for fragment in ('all remaining Item/Serious Wound','all Serious Wound effects')):
        failures.append({'check':'Serious Wound coverage stale not-yet-covered claim'})
    semantic_relation_ids = set(ontology_review.get('deferredSemanticRelationIds') or [])
    if semantic_relation_ids != {'rel.phase-part-of-round','rel.round-has-phase','rel.precedes','rel.follows','rel.turn-occurs-in-phase','rel.phase-has-turn','rel.process-has-timing-window','rel.decision-owned-by','rel.owns-decision','rel.information-visible-to','rel.transition-from','rel.transition-to'}:
        failures.append({'check': 'semantic relation handoff'})

    actual_counts = {
        'sources': len(source_rows), 'semanticNodes': len(semantic_node_rows), 'records': len(records),
        'sourceBacked': sum(item.get('status') == 'source-backed' for item in records),
        'withOpenQuestion': sum(item.get('status') == 'source-backed-with-open-question' for item in records),
        'sourceVariants': sum(item.get('status') == 'source-variant' for item in records),
        'sourceAssertions': sum(len(item.get('sourceAssertions') or []) for item in records),
        'conditions': sum(len(item.get('preconditions') or []) for item in records),
        'operations': sum(len(item.get('operations') or []) for item in records),
        'decisions': sum(len(item.get('decisions') or []) for item in records),
        'informationPolicies': sum(len(item.get('informationPolicy') or []) for item in records),
        'costs': sum(len(item.get('costs') or []) for item in records),
        'targets': sum(len(item.get('targets') or []) for item in records),
        'openQuestionReferences': sum(len(item.get('unresolvedQuestionRefs') or []) for item in records),
        'variantReferences': sum(len(item.get('sourceVariants') or []) for item in records),
        'questions': len(question_rows), 'openQuestions': review.get('counts', {}).get('open'),
        'systems': len(coverage.get('systems') or []),
        'conflicts': len(conflict_rows),
        'unresolvedConflicts': sum(item.get('status') == 'unresolved' for item in conflict_rows),
        'roomIconDenotations': len(denotation_rows),
        'backlogUnits': len(backlog.get('units') or []),
        'backlogPilotCovered': sum(item.get('status') == 'pilot-covered' for item in backlog.get('units') or []),
        'backlogSourceBlocked': sum(item.get('status') == 'source-blocked' for item in backlog.get('units') or []),
        'eventIdentities': len(event_rows),
        'eventScanOccurrences': len(event_rows),
        'eventLicensedOccurrences': len({(item.get('bgaOccurrence') or {}).get('key') for item in event_rows}),
        'eventOfficialOccurrences': sum(len(item.get('officialOccurrences') or []) for item in event_rows),
        'eventRecords': len(actual_event_rule_ids),
        'eventBacklogTuples': sum((backlog_rows_by_id.get('CARD:'+value[2][:16]) or {}).get('pilotRuleIds') == [value[4]] for value in EXPECTED_EVENT_OCCURRENCES.values()),
        'explorationIdentities': len(exploration_rows),
        'explorationScanOccurrences': len(exploration_rows),
        'explorationLicensedOccurrences': len({(item.get('bgaOccurrence') or {}).get('key') for item in exploration_rows}),
        'explorationOfficialOccurrences': sum(len(item.get('officialOccurrences') or []) for item in exploration_rows),
        'explorationPrintedSentences': sum(sum(unit.get('unitKind') == 'printed-sentence' for unit in item.get('sourceUnits') or []) for item in exploration_rows),
        'explorationIconOccurrences': sum(len(item.get('iconOccurrences') or []) for item in exploration_rows),
        'explorationRecords': len(actual_exploration_rule_ids),
        'explorationBacklogTuples': sum((backlog_rows_by_id.get('CARD:'+value['sha256'][:16]) or {}).get('pilotRuleIds') == [value['ruleId']] for value in EXPECTED_EXPLORATION_OCCURRENCES.values()),
        'robotIdentities': len(robot_rows),
        'robotScanOccurrences': len(robot_rows),
        'robotSharedBackOccurrences': int(bool(robot_sources.get('sharedBack'))),
        'robotLicensedOccurrences': len({(item.get('bgaOccurrence') or {}).get('key') for item in robot_rows}),
        'robotOfficialOccurrences': sum(len(item.get('officialOccurrences') or []) for item in robot_rows),
        'robotPhysicalPanels': sum(len(item.get('panels') or []) for item in robot_rows),
        'robotOperativePanels': sum(sum(panel.get('operative') is True for panel in item.get('panels') or []) for item in robot_rows),
        'robotActionOptions': sum(len(item.get('actionOptions') or []) for item in robot_rows),
        'robotPrintedSentences': sum(len(item.get('sentences') or []) for item in robot_rows),
        'robotIconOccurrences': sum(len(item.get('iconOccurrences') or []) for item in robot_rows),
        'robotRecords': len(actual_robot_rule_ids),
        'robotBacklogTuples': sum((backlog_rows_by_id.get('CARD:'+value['sha256'][:16]) or {}).get('pilotRuleIds') == [value['ruleId']] for value in EXPECTED_ROBOT_OCCURRENCES.values()),
        'attackIdentities': len(attack_rows),
        'attackScanOccurrences': len(attack_rows),
        'attackGeneratedOccurrences': sum((item.get('sourceSelector') or {}).get('sourceRole') == 'generated-cell-face' for item in attack_rows),
        'attackDirectOccurrences': sum((item.get('sourceSelector') or {}).get('sourceRole') == 'direct-face' for item in attack_rows),
        'attackSharedBackOccurrences': int(bool(attack_sources.get('sharedBack'))),
        'attackSourceSheets': int(bool(attack_sources.get('sourceSheet'))),
        'attackSelectorGaps': attack_sources.get('counts',{}).get('excludedSelectorGaps'),
        'attackLicensedVariants': len({(item.get('bgaOccurrence') or {}).get('key') for item in attack_rows}),
        'attackLicensedFaceLinks': sum(bool(item.get('bgaOccurrence')) for item in attack_rows),
        'attackOfficialFaceCounterparts': sum(row.get('kind') != 'shared-back' for row in official_counterparts),
        'attackOfficialBackCounterparts': sum(row.get('kind') == 'shared-back' for row in official_counterparts),
        'attackPhysicalPanels': sum(len(item.get('panels') or []) for item in attack_rows),
        'attackOperativePanels': sum(sum(panel.get('operative') is True for panel in item.get('panels') or []) for item in attack_rows),
        'attackPrintedSentences': sum(len(item.get('sentences') or []) for item in attack_rows),
        'attackBadgeOccurrences': sum(len(item.get('applicabilityBadgeOccurrences') or []) for item in attack_rows),
        'attackInlineIconOccurrences': sum(len(item.get('inlineIconOccurrences') or []) for item in attack_rows),
        'attackFunctionalSymbolOccurrences': sum(len(item.get('applicabilityBadgeOccurrences') or []) + len(item.get('inlineIconOccurrences') or []) for item in attack_rows),
        'attackSelectedNoMatches': sum(len((item.get('selectedEvidenceComparisons') or {}).get('unresolvedIconOccurrences') or []) for item in attack_rows),
        'attackRecords': len(actual_attack_rule_ids),
        'attackBacklogTuples': sum((backlog_rows_by_id.get('CARD:'+value[2][:16]) or {}).get('pilotRuleIds') == [value[6]] for value in EXPECTED_ATTACK_OCCURRENCES.values()),
        'queenHealthPhysicalOccurrences': len(queen_rows),
        'queenHealthUniqueFaceAssets': len({item.get('sourceSha256') for item in queen_rows}),
        'queenHealthSharedBackOccurrences': int(bool(queen_health_sources.get('sharedBack'))),
        'queenHealthLicensedOccurrences': len(licensed_queen_rows),
        'queenHealthOfficialFaceOccurrences': sum(row.get('kind') in {'face','partial-face'} for row in official_queen),
        'queenHealthOfficialBackOccurrences': sum(row.get('kind') == 'shared-back' for row in official_queen),
        'queenHealthPhysicalPanels': sum(len(item.get('panels') or []) for item in queen_rows),
        'queenHealthPrintedSentences': sum(len(item.get('sentences') or []) for item in queen_rows),
        'queenHealthLocalDisplayOccurrences': sum(sum(icon.get('semanticReferenceId') is None for icon in item.get('iconOccurrences') or []) for item in queen_rows),
        'queenHealthMatchedIconOccurrences': sum(sum(icon.get('semanticReferenceId') is not None for icon in item.get('iconOccurrences') or []) for item in queen_rows),
        'queenHealthFunctionalIconOccurrences': sum(len(item.get('iconOccurrences') or []) for item in queen_rows),
        'queenHealthRecords': len(actual_queen_rule_ids),
        'queenHealthBacklogTuples': sum((backlog_rows_by_id.get(backlog_id) or {}).get('pilotRuleIds') == rule_ids for backlog_id,rule_ids in expected_backlog_rules.items()),
        'seriousWoundPhysicalOccurrences': len(serious_wound_rows),
        'seriousWoundUniqueTitles': len({item.get('printedTitle') for item in serious_wound_rows}),
        'seriousWoundSelectedFaceAssets': len({item.get('sourceSha256') for item in serious_wound_rows}),
        'seriousWoundSourceFaceAssets': len(serious_wound_assets),
        'seriousWoundGeneratedOccurrences': sum((item.get('sourceSelector') or {}).get('generatedSpriteSheetCell') is True for item in serious_wound_rows),
        'seriousWoundDirectOccurrences': sum((item.get('sourceSelector') or {}).get('generatedSpriteSheetCell') is False for item in serious_wound_rows),
        'seriousWoundSharedBackOccurrences': int(bool(serious_wound_sources.get('sharedBack'))),
        'seriousWoundSourceSheets': int(bool(serious_wound_sources.get('sourceSheet'))),
        'seriousWoundSelectorGaps': sum(not item.get('selectedByRootDeck') for item in serious_wound_assets),
        'seriousWoundPhysicalRegions': sum(len(item.get('regions') or []) for item in serious_wound_rows),
        'seriousWoundOperativeRegions': sum(sum(region.get('operative') is True for region in item.get('regions') or []) for item in serious_wound_rows),
        'seriousWoundPhysicalPanels': sum(len(item.get('panels') or []) for item in serious_wound_rows),
        'seriousWoundOperativePanels': sum(sum(panel.get('operative') is True for panel in item.get('panels') or []) for item in serious_wound_rows),
        'seriousWoundPrintedSentences': sum(len(item.get('sentences') or []) for item in serious_wound_rows),
        'seriousWoundFunctionalIconOccurrences': sum(len(item.get('iconOccurrences') or []) for item in serious_wound_rows),
        'seriousWoundMatchedIconOccurrences': sum(sum(icon.get('semanticReferenceId') is not None for icon in item.get('iconOccurrences') or []) for item in serious_wound_rows),
        'seriousWoundUnresolvedLocalGlyphOccurrences': sum(sum(icon.get('semanticReferenceId') is None for icon in item.get('iconOccurrences') or []) for item in serious_wound_rows),
        'seriousWoundLicensedOccurrences': len(licensed_wounds),
        'seriousWoundOfficialFaceOccurrences': sum(row.get('kind') in {'face','partial-face'} for row in official_wounds),
        'seriousWoundOfficialBackOccurrences': sum(row.get('kind') == 'shared-back' for row in official_wounds),
        'seriousWoundRecords': len(actual_serious_wound_rule_ids),
        'seriousWoundBacklogTuples': sum((backlog_rows_by_id.get(backlog_id) or {}).get('pilotRuleIds') == rule_ids for backlog_id,rule_ids in expected_wound_backlog_rules.items()),
        'greenItemRootOccurrences': len((green_item_sources.get('rootDeckEvidence') or {}).get('fullContainedSelectors') or []),
        'greenItemPhysicalOccurrences': len(green_validation['rows']),
        'greenItemExcludedHeavyOccurrences': len(green_validation['excluded']),
        'greenItemUniqueTitles': len({item.get('printedTitle') for item in green_validation['rows']}),
        'greenItemSelectedFaceAssets': len({item.get('sourceSha256') for item in green_validation['rows']}),
        'greenItemSourceFaceAssets': len(green_validation['assets']),
        'greenItemGeneratedOccurrences': sum((item.get('sourceSelector') or {}).get('generatedSpriteSheetCell') is True for item in green_validation['rows']),
        'greenItemDirectOccurrences': sum((item.get('sourceSelector') or {}).get('generatedSpriteSheetCell') is False for item in green_validation['rows']),
        'greenItemSharedBackOccurrences': int(bool(green_item_sources.get('sharedBack'))),
        'greenItemSourceSheets': int(bool(green_item_sources.get('sourceSheet'))),
        'greenItemSelectorGaps': sum(item.get('sourceRole') == 'generated-cell-selector-gap-variant' for item in green_validation['assets']),
        'greenItemPhysicalRegions': sum(len(item.get('regions') or []) for item in green_validation['rows']),
        'greenItemOperativeRegions': sum(sum(region.get('operative') is True for region in item.get('regions') or []) for item in green_validation['rows']),
        'greenItemPhysicalPanels': sum(len(item.get('panels') or []) for item in green_validation['rows']),
        'greenItemOperativePanels': sum(sum(panel.get('operative') is True for panel in item.get('panels') or []) for item in green_validation['rows']),
        'greenItemPrintedSentences': sum(len(item.get('sentences') or []) for item in green_validation['rows']),
        'greenItemFunctionalIconOccurrences': sum(len(item.get('iconOccurrences') or []) for item in green_validation['rows']),
        'greenItemMatchedIconOccurrences': sum(sum(icon.get('semanticReferenceId') is not None for icon in item.get('iconOccurrences') or []) for item in green_validation['rows']),
        'greenItemUnresolvedLocalGlyphOccurrences': sum(sum(icon.get('semanticReferenceId') is None for icon in item.get('iconOccurrences') or []) for item in green_validation['rows']),
        'greenItemLicensedOccurrences': len(green_validation['licensed']),
        'greenItemLicensedCopies': sum(item.get('nbr',0) for item in green_validation['licensed']),
        'greenItemLicensedRegularCopies': sum(item.get('nbr',0) for item in green_validation['licensed'] if not item.get('heavy') and not item.get('armor')),
        'greenItemLicensedHeavyCopies': sum(item.get('nbr',0) for item in green_validation['licensed'] if item.get('heavy') or item.get('armor')),
        'greenItemOfficialFaceOccurrences': sum(item.get('exactGreenRulesFace') is True for item in green_validation['official']),
        'greenItemOfficialBackOccurrences': sum(item.get('kind') == 'shared-back' for item in green_validation['official']),
        'greenItemOfficialFamilyOccurrences': len(green_validation['official']),
        'greenItemRecords': len(green_validation['actualRuleIds']),
        'greenItemBacklogTuples': sum((backlog_rows_by_id.get(backlog_id) or {}).get('pilotRuleIds') == rule_ids for backlog_id,rule_ids in green_validation['expectedBacklogRules'].items()),
    }
    if actual_counts != EXPECTED:
        failures.append({'check': 'hard-coded semantic pilot counts', 'expected': EXPECTED, 'actual': actual_counts})
    expected_pilot_counts = {key: actual_counts[key] for key in ('records','sourceBacked','withOpenQuestion','sourceVariants','sourceAssertions','conditions','operations','decisions','informationPolicies','costs','targets','openQuestionReferences','variantReferences')}
    if pilots.get('counts') != expected_pilot_counts or sources_data.get('counts') != {'sources': 160} or review.get('counts') != {'questions':50,'officialClarificationPreferred':21,'sourceAmbiguitiesIntroducedByPilot':29,'resolved':0,'open':50} or coverage.get('counts') != {'systems':21,'pilotRecords':232,'fullBaseSemanticCoverageClaimed':False}:
        failures.append({'check': 'declared semantic counts'})
    covered_rule_ids = [rule_id for system in coverage.get('systems') or [] for rule_id in system.get('ruleIds') or []]
    if set(covered_rule_ids) != set(record_ids) or len(covered_rule_ids) != len(set(covered_rule_ids)) or coverage.get('counts', {}).get('fullBaseSemanticCoverageClaimed') is not False:
        failures.append({'check': 'semantic pilot coverage projection'})

    backlog_units = backlog.get('units') or []
    backlog_ids = [item.get('semanticUnitId') for item in backlog_units]
    if len(backlog_ids) != len(set(backlog_ids)) or any(not item for item in backlog_ids):
        failures.append({'check': 'semantic backlog unit IDs'})
    actual_room_backlog = {item['semanticUnitId'] for item in backlog_units if item.get('channel') == 'room-help-entry'}
    expected_room_backlog = {f'ROOM:{index:02d}' for index in range(1,26)}
    actual_intruder_backlog = {item['semanticUnitId'] for item in backlog_units if item.get('channel') == 'intruder-help-instruction'}
    expected_intruder_backlog = {f'INTR:{occurrence_id}' for occurrence_id in help_rows}
    if actual_room_backlog != expected_room_backlog or actual_intruder_backlog != expected_intruder_backlog:
        failures.append({'check': 'Help semantic backlog exact IDs'})
    allowed_backlog_status = {'pending','pilot-covered','source-blocked'}
    for item in backlog_units:
        path = REPO / item.get('sourcePath', '')
        if not path.exists() or item.get('status') not in allowed_backlog_status or not item.get('channel') or not item.get('sourceLocator'):
            failures.append({'check': 'semantic backlog source/status', 'semanticUnitId': item.get('semanticUnitId')})
        if any(rule_id not in record_by_id for rule_id in item.get('pilotRuleIds') or []):
            failures.append({'check': 'semantic backlog pilot linkage', 'semanticUnitId': item.get('semanticUnitId')})
        if (item.get('status') == 'pilot-covered') != bool(item.get('pilotRuleIds')):
            failures.append({'check': 'semantic backlog status/link consistency', 'semanticUnitId': item.get('semanticUnitId')})
    blocked_units = [item for item in backlog_units if item.get('status') == 'source-blocked']
    if len(blocked_units) != 1 or not blocked_units[0].get('sourcePath','').endswith('missionTaskDeck-023.png') or 'exact-source-operative-span' not in blocked_units[0].get('blockers',[]):
        failures.append({'check': 'semantic backlog inherited source blocker'})
    expected_backlog_channels = {'card-reference-source-tuple':350,'interpreted-rule-record':54,'intruder-help-instruction':18,'objective-help-unit':45,'official-faq-unit':28,'room-help-entry':25,'rulebook-visual-obligation':80}
    expected_backlog_status = {'pending':384,'pilot-covered':215,'source-blocked':1}
    if backlog.get('counts') != {'units':600,'byChannel':expected_backlog_channels,'byStatus':expected_backlog_status}:
        failures.append({'check': 'semantic backlog declared counts'})

    if reproducibility:
        builds = []
        for seed, locale_name in (('1','C'),('777','C.utf8')):
            with tempfile.TemporaryDirectory(prefix=f'semantic-rebuild-{seed}-') as temp_dir:
                env = {**os.environ, 'LC_ALL':locale_name, 'TZ':'UTC', 'PYTHONHASHSEED':seed}
                run = subprocess.run(['python3', str(REPO / 'scripts/build_semantic_pilots.py'), '--output-dir', temp_dir], cwd=REPO, env=env, check=False, capture_output=True, text=True)
                if run.returncode != 0:
                    failures.append({'check': 'semantic rebuild execution', 'seed': seed, 'locale':locale_name, 'stderr': run.stderr})
                    continue
                backlog_run = subprocess.run(['python3', str(REPO / 'scripts/build_semantic_backlog.py'), '--output', str(Path(temp_dir) / 'backlog.json')], cwd=REPO, env=env, check=False, capture_output=True, text=True)
                if backlog_run.returncode != 0:
                    failures.append({'check': 'semantic backlog rebuild execution', 'seed': seed, 'locale':locale_name, 'stderr': backlog_run.stderr})
                    continue
                hashes = {}
                for name, tracked in [('event-source-index.json',event_source_path),('exploration-source-index.json',exploration_source_path),('robot-source-index.json',robot_source_path),('attack-source-index.json',attack_source_path),('queen-health-source-index.json',queen_health_source_path),('serious-wound-source-index.json',serious_wound_source_path),('green-item-source-index.json',green_item_source_path),('source-registry.json',source_path),('semantic-rule.schema.json',schema_path),('semantic-vocabulary.json',semantic_vocabulary_path),('room-icon-denotations.json',room_icon_path),('pilots.json',pilots_path),('review-gates.json',review_path),('contradictions.json',contradictions_path),('coverage.json',coverage_path),('backlog.json',backlog_path)]:
                    rebuilt = Path(temp_dir) / name
                    hashes[name] = sha(rebuilt) if rebuilt.is_file() else None
                    if not rebuilt.is_file() or hashes[name] != sha(tracked):
                        failures.append({'check': 'semantic reproducibility', 'seed': seed, 'locale':locale_name, 'file': name})
                builds.append(hashes)
        if len(builds) == 2 and builds[0] != builds[1]:
            failures.append({'check': 'semantic hash-seed reproducibility'})

    return {'schemaVersion':1,'passed':not failures,'checks':actual_counts,'failureCount':len(failures),'failures':failures}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--event-source-index', type=Path, default=DIR/'event-source-index.json')
    parser.add_argument('--exploration-source-index', type=Path, default=DIR/'exploration-source-index.json')
    parser.add_argument('--robot-source-index', type=Path, default=DIR/'robot-source-index.json')
    parser.add_argument('--attack-source-index', type=Path, default=DIR/'attack-source-index.json')
    parser.add_argument('--queen-health-source-index', type=Path, default=DIR/'queen-health-source-index.json')
    parser.add_argument('--serious-wound-source-index', type=Path, default=DIR/'serious-wound-source-index.json')
    parser.add_argument('--green-item-source-index', type=Path, default=DIR/'green-item-source-index.json')
    parser.add_argument('--source-registry', type=Path, default=DIR/'source-registry.json')
    parser.add_argument('--schema', type=Path, default=DIR/'semantic-rule.schema.json')
    parser.add_argument('--semantic-vocabulary', type=Path, default=DIR/'semantic-vocabulary.json')
    parser.add_argument('--room-icon-denotations', type=Path, default=DIR/'room-icon-denotations.json')
    parser.add_argument('--pilots', type=Path, default=DIR/'pilots.json')
    parser.add_argument('--review-gates', type=Path, default=DIR/'review-gates.json')
    parser.add_argument('--contradictions', type=Path, default=DIR/'contradictions.json')
    parser.add_argument('--coverage', type=Path, default=DIR/'coverage.json')
    parser.add_argument('--backlog', type=Path, default=DIR/'backlog.json')
    parser.add_argument('--skip-reproducibility', action='store_true')
    parser.add_argument('--report', action='store_true')
    args = parser.parse_args()
    try:
        report = validate(args.event_source_index,args.exploration_source_index,args.robot_source_index,args.attack_source_index,args.queen_health_source_index,args.serious_wound_source_index,args.green_item_source_index,args.source_registry,args.schema,args.semantic_vocabulary,args.room_icon_denotations,args.pilots,args.review_gates,args.contradictions,args.coverage,args.backlog,reproducibility=not args.skip_reproducibility)
    except (DuplicateJsonKeyError,json.JSONDecodeError) as error:
        report = {'schemaVersion':1,'passed':False,'checks':{},'failureCount':1,'failures':[{'check':'strict JSON parsing','error':str(error)}]}
    if args.report and args.pilots.resolve() == (DIR/'pilots.json').resolve():
        (DIR/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
