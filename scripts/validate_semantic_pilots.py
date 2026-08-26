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

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / 'docs/rules/semantics'
VOCAB = REPO / 'docs/rules/vocabulary'
ONTOLOGY = REPO / 'docs/rules/ontology'
EXPECTED = {
    'sources': 44, 'semanticNodes': 22, 'records': 111, 'sourceBacked': 74, 'withOpenQuestion': 37,
    'sourceVariants': 0, 'sourceAssertions': 308, 'conditions': 391,
    'operations': 500, 'decisions': 49, 'informationPolicies': 123,
    'costs': 3, 'targets': 142, 'openQuestionReferences': 42,
    'variantReferences': 37, 'questions': 17, 'openQuestions': 17, 'systems': 18,
    'conflicts': 13, 'unresolvedConflicts': 7,
    'roomIconDenotations': 112,
    'backlogUnits': 600, 'backlogPilotCovered': 119, 'backlogSourceBlocked': 1,
    'eventIdentities': 20, 'eventScanOccurrences': 20, 'eventLicensedOccurrences': 20,
    'eventOfficialOccurrences': 4, 'eventRecords': 20, 'eventBacklogTuples': 20,
    'explorationIdentities': 12, 'explorationScanOccurrences': 12,
    'explorationLicensedOccurrences': 12, 'explorationOfficialOccurrences': 3,
    'explorationPrintedSentences': 46, 'explorationIconOccurrences': 60,
    'explorationRecords': 12, 'explorationBacklogTuples': 12,
}
PINNED_HELP_SOURCE_HASHES = {
    'docs/rules/source-extraction/intruder-help-sheet.json': 'e07f2703a6ad1b49c06389f79d3b1ffd6f5fd1d98604bf14b405fee49d9679e6',
    'docs/rules/source-extraction/room-help-sheet.json': 'ad3d6bb66de939fe1036ecca3fc8d8d9b41fe41e1065f7bd9611df8263480177',
    'docs/rules/source-extraction/room-help-sheet-source-fidelity-lock.json': '27c23c1c885e2ab851bef0bfb43b7471ea862af9d0308f9b3e70026320b4d8b4',
}
PINNED_EXPLORATION_SOURCE_INDEX_HASH = 'd95dc30738ce2efbb4cf696671388aaf731626f167601fdca70c6fee74dc95bd'
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
    'SEM-EVENT-RISE-OF-THE-MACHINE-001': ['SEM-Q-010'],
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
    'SEM-EVENT-RISE-OF-THE-MACHINE-001': 'd2027c3f7e07242fecd318223f83b1210430d3c7089d971864a5fc432dbd76c7',
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
ALLOWED_OPERATIONS = {
    'branch','change-value','choose','draw-random','end-process','evaluate-condition',
    'inspect-private','invoke-process','invoke-selected-process','move-entity','pay-cost','end-action-window',
    'place-component','play-card','remove-component','replace-target','resolve-attacks',
    'reveal','select-target','set-state','transition-zone','shuffle','resolve-open-alternative',
}
ALLOWED_TIMING = {'before-attack-resolution','during','during-event-card-resolution','when-action-card-played','when-triggered'}
ALLOWED_PARTIAL = {'all-or-nothing-selection','if-not-possible-fallback','ordered-complete','per-sentence-continue','replacement-effect','source-conditional-steps','per-effect-check','source-limited-components'}
ALLOWED_TARGET_SELECTION = {'player-choice','random','deterministic-turn-order','unresolved-when-multiple','deterministic-state-filter','unresolved-order'}
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


def validate(event_source_path: Path, exploration_source_path: Path, source_path: Path, schema_path: Path, semantic_vocabulary_path: Path, room_icon_path: Path, pilots_path: Path, review_path: Path, contradictions_path: Path, coverage_path: Path, backlog_path: Path, *, reproducibility: bool) -> dict:
    failures: list[dict] = []
    event_sources = load(event_source_path)
    exploration_sources = load(exploration_source_path)
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
    if semantic_vocabulary.get('counts') != {'nodes':22,'stateValues':15,'zones':2,'positions':2,'visibilityScopes':3} or semantic_kind_counts != {'state-value':15,'zone':2,'position':2,'visibility-scope':3}:
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
    if contradictions.get('counts') != {'conflicts':13,'resolvedByAuthority':4,'unresolved':7,'preservedBoundary':2}:
        failures.append({'check': 'semantic conflict declared counts'})

    for record in records:
        rule_id = record['ruleId']
        if set(record) != schema_fields:
            failures.append({'check': 'record schema fields', 'ruleId': rule_id, 'missing': sorted(schema_fields - set(record)), 'extra': sorted(set(record) - schema_fields)})
        if record.get('schemaVersion') != 1 or record.get('recordType') != 'semantic-rule' or not isinstance(record.get('recordRevision'), int) or isinstance(record.get('recordRevision'), bool) or record.get('recordRevision', 0) < 1:
            failures.append({'check': 'record schema/version', 'ruleId': rule_id})
        if record.get('status') not in schema['properties']['status']['enum'] or record.get('ruleKind') not in schema['properties']['ruleKind']['enum'] or record.get('modality') not in {'must','may','cannot'}:
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
            if item.get('ownerRef') not in participant_set or item.get('selectionMode') not in {'player-choice','random','deterministic','unresolved'} or not cardinality_valid(item.get('cardinality')) or not isinstance(item.get('declineAllowed'), bool) or not item.get('visibility') or not item.get('options'):
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
    search_operations = {item.get('stepId'): item for item in search.get('operations') or []}
    search_information = search.get('informationPolicy') or []
    if (search_operations.get('S04', {}).get('transition') or {}).get('to') != 'tax.scaffold.zone.deck' or (search_operations.get('S04', {}).get('transition') or {}).get('positionRef') != 'sem.position.deck-bottom' or not any('unchosen Items must not be revealed' in item.get('secrecy','') for item in search_information):
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
    }
    if actual_counts != EXPECTED:
        failures.append({'check': 'hard-coded semantic pilot counts', 'expected': EXPECTED, 'actual': actual_counts})
    expected_pilot_counts = {key: actual_counts[key] for key in ('records','sourceBacked','withOpenQuestion','sourceVariants','sourceAssertions','conditions','operations','decisions','informationPolicies','costs','targets','openQuestionReferences','variantReferences')}
    if pilots.get('counts') != expected_pilot_counts or sources_data.get('counts') != {'sources': 44} or review.get('counts') != {'questions':17,'officialClarificationPreferred':7,'sourceAmbiguitiesIntroducedByPilot':10,'resolved':0,'open':17} or coverage.get('counts') != {'systems':18,'pilotRecords':111,'fullBaseSemanticCoverageClaimed':False}:
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
    expected_backlog_status = {'pending':480,'pilot-covered':119,'source-blocked':1}
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
                for name, tracked in [('event-source-index.json',event_source_path),('exploration-source-index.json',exploration_source_path),('source-registry.json',source_path),('semantic-rule.schema.json',schema_path),('semantic-vocabulary.json',semantic_vocabulary_path),('room-icon-denotations.json',room_icon_path),('pilots.json',pilots_path),('review-gates.json',review_path),('contradictions.json',contradictions_path),('coverage.json',coverage_path),('backlog.json',backlog_path)]:
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
        report = validate(args.event_source_index,args.exploration_source_index,args.source_registry,args.schema,args.semantic_vocabulary,args.room_icon_denotations,args.pilots,args.review_gates,args.contradictions,args.coverage,args.backlog,reproducibility=not args.skip_reproducibility)
    except (DuplicateJsonKeyError,json.JSONDecodeError) as error:
        report = {'schemaVersion':1,'passed':False,'checks':{},'failureCount':1,'failures':[{'check':'strict JSON parsing','error':str(error)}]}
    if args.report and args.pilots.resolve() == (DIR/'pilots.json').resolve():
        (DIR/'validation.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
