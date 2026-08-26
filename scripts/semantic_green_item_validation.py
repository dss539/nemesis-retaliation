from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re


PINNED_GREEN_ITEM_SOURCE_INDEX_HASH = "62074d2aa9cf18f1abf2cbb99bddc000ab25552122c99973bf760ebe2b0bef2b"

EXPECTED_GREEN_ITEM_COUNTS = {
    "rootPhysicalOccurrences": 30,
    "physicalFaceOccurrences": 23,
    "excludedHeavyPhysicalOccurrences": 7,
    "uniquePrintedTitles": 8,
    "uniqueSelectedFaceAssets": 8,
    "sourceFaceAssets": 14,
    "generatedPhysicalFaceOccurrences": 15,
    "directPhysicalFaceOccurrences": 8,
    "sourceSheets": 1,
    "sourceSheetCells": 9,
    "selectedGeneratedCells": 5,
    "selectorGapCells": 4,
    "sharedBackOccurrences": 1,
    "sharedBackSelectorReferences": 31,
    "sourceSheetSelectorReferences": 16,
    "rootCustomDeckEntries": 8,
    "physicalRegions": 69,
    "operativeRegions": 46,
    "physicalPanels": 85,
    "operativePanels": 62,
    "oneUseHeadingOccurrences": 23,
    "useDiscardPassiveReactionHeadingOccurrences": 0,
    "printedSentenceOccurrences": 46,
    "physicalFunctionalIconOccurrences": 46,
    "physicalMatchedIconOccurrences": 37,
    "physicalUnresolvedLocalGlyphOccurrences": 9,
    "selectorGapFunctionalIconOccurrences": 11,
    "selectorGapMatchedIconOccurrences": 3,
    "selectorGapUnresolvedLocalGlyphOccurrences": 8,
    "licensedDigitalOccurrences": 10,
    "licensedDigitalPhysicalCopies": 30,
    "licensedRegularOccurrences": 8,
    "licensedRegularPhysicalCopies": 23,
    "licensedHeavyOccurrences": 2,
    "licensedHeavyPhysicalCopies": 7,
    "officialInventoryCopiesPerType": 30,
    "officialVisibleFaceOccurrences": 0,
    "officialVisibleBackOccurrences": 0,
    "officialFamilyVisualOccurrences": 7,
    "baseApplicableFaqOccurrences": 3,
    "excludedExpansionFaqOccurrences": 4,
    "backlogTuples": 12,
    "backlogPhysicalFaceLinks": 23,
    "backlogObligationsLinked": 30,
    "semanticPhysicalFaceRecords": 23,
}

# path, sha, title, source role, cell, physical class, selected regular,
# panel count, sentence count, ordered semantic icon refs, exact composite text digest
EXPECTED_GREEN_ITEM_ASSETS = {
    "direct-5365": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-140.png",
        "2cc81469849101f8897fffdefef06ed62960f92af2266b7ad7f1fa89b2c7934c",
        "EMERGENCY LIFE\nSUPPORT CODES", "direct-regular-face", None, "regular-item", True, 3, 1,
        ("icon.notInCombat", "icon.computer", "icon.malfunction", "icon.lifeSupportActive", "icon.lifeSupportInactive"),
        "7075f787640d64716e2ca09f7ad3aab145fe26527e58aef792a2eb2f138a3cfd",
    ),
    "direct-5366": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-115.png",
        "ddedb8819e921206d38f6d89ea9690638fab53faa7a666fc8e2e2d1874566431",
        "CAFFEINE PILLS", "direct-regular-face", None, "regular-item", True, 3, 1,
        ("icon.notInCombat", "icon.actionCard"),
        "0073c285fa9afb049e01150c53662476ae21cedba673de44aef2e2d8309b6759",
    ),
    "direct-5367": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-120.png",
        "5db3229a26df87dc4eca7b317b12d785632ab780dc770db3ec5fc7c6d373b34a",
        "MEDKIT", "direct-regular-face", None, "regular-item", True, 5, 3,
        ("icon.notInCombat", "icon.characterHealth", "icon.medpackToken"),
        "2a2485746fad4a7f001492245bfa58fc4cd443a68451d72f0a485e2acecfab3f",
    ),
    "direct-heavy-medkit": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-035.png",
        "ca12aaf3395c1212911f0b86e867115e98df6f60c74a4f8921714db40ad214bc",
        "MEDKIT", "direct-heavy-face-excluded", None, "heavy-item", False, 3, 1,
        ("icon.notInCombat", "icon.characterHealth"),
        "fcbb9160bb63726abc4f39920cd599cf9300876090a629f233a7ca4b5a7fd063",
    ),
    "direct-heavy-oxygen": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-029.png",
        "10a73a40826de71ecab5b5cae848de1083bb8466e50a3db927db61fdc89aa546",
        "HEAVY OXYGEN TANK", "direct-heavy-face-excluded", None, "heavy-item", False, 3, 1,
        (None, "icon.oxygen"),
        "961b861631df204012fa986a0d0bbfe9306ffd9c1a7de8e0de0845a44858d3cd",
    ),
    "sheet-00": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-00.png",
        "59518a4d288b71cf979eae47d49f5cf098864f2a8c8b105c5e519be565a72044",
        "ADRENALINE\nINJECTION", "generated-cell-regular-face", 0, "regular-item", True, 3, 3,
        (None,), "ae4de040e1b2bc69f0aafc9d3e26da613fcf2913743a7836383399a7ecd6ba26",
    ),
    "sheet-01": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-01.png",
        "612e58e8d7efb308d09796e5ebb446cc2cd8b3ca94f8896a5e430756c1895b7d",
        "ANTISEPTIC", "generated-cell-regular-face", 1, "regular-item", True, 3, 1,
        ("icon.notInCombat",), "56a3f1d975b05a7df4a3774cd072bbd795a69650141f0f50de44588712519b1b",
    ),
    "sheet-02": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-02.png",
        "55b5781d25288fd9ac949e546581dfecf40466c910fd2f8bbe9b01b451338a6b",
        "CAFFEINE PILLS", "generated-cell-selector-gap-variant", 2, "regular-item", False, 3, 1,
        (None, None), "11e3ca0f3b0ebcaa09a542332bec280586e9d7e52ee453768e886ac0b37e0cef",
    ),
    "sheet-03": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-03.png",
        "87852c831e4a52729fa393b5a858d0b127b3e8ec0c587eec134a453793ab6353",
        "CONTAMINATION\nCODES", "generated-cell-regular-face", 3, "regular-item", True, 3, 2,
        ("icon.notInCombat", "icon.computer", "icon.malfunction"),
        "55b9d914b9fbf4873dd19d19df9869cd65b22acc200465a0efbf495f68446ab7",
    ),
    "sheet-04": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-04.png",
        "760e3b4e3e0c4e1b7910b3582a487d747b50a39bf382adf72769225d863438c1",
        "EMERGENCY LIFE SUPPORT CODES", "generated-cell-selector-gap-variant", 4, "regular-item", False, 3, 3,
        (None, "icon.computer", "icon.malfunction", None, None),
        "92ccf8760d64275f8312f0f10b543da017cdd14508942d4b726941ff797773d5",
    ),
    "sheet-05": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-05.png",
        "a342222859d525d1b38440578ff50d890ddc76070dc1c5fd463e307c50c01da5",
        "MEDICAL\nSTAPLER", "generated-cell-regular-face", 5, "regular-item", True, 4, 2,
        ("icon.characterHealth",), "615883ed9b7dede85a180eef3cf96e29b659acfb830f3b760690777b828e47d0",
    ),
    "sheet-06": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-06.png",
        "3ed05ec380152f89ac3af2f4a648327d369a7a94db456f801e328027c81482f1",
        "MEDKIT", "generated-cell-selector-gap-variant", 6, "regular-item", False, 4, 2,
        (None, "icon.characterHealth"), "4c87c22209cdbadde822db0a2c38b1162f1bf5bc3ddd5aed0df4988299001de8",
    ),
    "sheet-07": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-07.png",
        "16941a0010c6dca8e2114c2c3a091649df27d88ab4b52883e9a7b8326cd3de57",
        "STIMULANTS", "generated-cell-regular-face", 7, "regular-item", True, 4, 2,
        (None, "icon.characterHealth", None), "880ba2b6ba95da6d16b1efa6373053e4bd7f3894a88a55bb56f92bafdbd03d7b",
    ),
    "sheet-08": (
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-08.png",
        "259b1c8fa4f9bc3194f2150511a981d734e421ae3eb1afb03f2d20175f2c035a",
        "SYNTHETIC FOOD", "generated-cell-selector-gap-variant", 8, "regular-item", False, 3, 1,
        (None, None), "1a56aa54f872e845e90b6fe92b4f599fae9f4036523e39d732adcb6c91f475e0",
    ),
}

# root sequence, full CardID, GUID, CustomDeck ID, asset key, included regular
EXPECTED_GREEN_ITEM_ROOT = [
    (1, 536500, "dc077a", "5365", "direct-5365", True),
    (2, 536600, "d4829e", "5366", "direct-5366", True),
    (3, 536600, "f2503b", "5366", "direct-5366", True),
    (4, 536600, "4995a3", "5366", "direct-5366", True),
    (5, 536700, "96f194", "5367", "direct-5367", True),
    (6, 536700, "63664d", "5367", "direct-5367", True),
    (7, 536700, "a35eff", "5367", "direct-5367", True),
    (8, 536700, "7aba7a", "5367", "direct-5367", True),
    (9, 415900, "9bd717", "4159", "direct-heavy-medkit", False),
    (10, 415900, "339846", "4159", "direct-heavy-medkit", False),
    (11, 416000, "c8e79c", "4160", "direct-heavy-medkit", False),
    (12, 416100, "61a77c", "4161", "direct-heavy-medkit", False),
    (13, 400100, "4ff8a4", "4001", "direct-heavy-oxygen", False),
    (14, 400100, "4b18b1", "4001", "direct-heavy-oxygen", False),
    (15, 400100, "1ceccd", "4001", "direct-heavy-oxygen", False),
    (16, 3700, "eabba4", "37", "sheet-00", True),
    (17, 3700, "7e1c40", "37", "sheet-00", True),
    (18, 3700, "cefcf6", "37", "sheet-00", True),
    (19, 3701, "2e0877", "37", "sheet-01", True),
    (20, 3701, "2f0205", "37", "sheet-01", True),
    (21, 3701, "e2e7d7", "37", "sheet-01", True),
    (22, 3703, "c1bef4", "37", "sheet-03", True),
    (23, 3705, "824be4", "37", "sheet-05", True),
    (24, 3705, "b9c9df", "37", "sheet-05", True),
    (25, 3705, "6f0675", "37", "sheet-05", True),
    (26, 3705, "271ced", "37", "sheet-05", True),
    (27, 3705, "1a13ab", "37", "sheet-05", True),
    (28, 3707, "79581a", "37", "sheet-07", True),
    (29, 3707, "64df0b", "37", "sheet-07", True),
    (30, 3707, "30f2f8", "37", "sheet-07", True),
]

EXPECTED_GREEN_ITEM_REUSABLE_RULE_IDS = [
    "SEM-GREEN-ITEM-DECK-001",
    "SEM-REGULAR-ITEM-BACKPACK-001",
    "SEM-USE-ITEM-001",
    "SEM-GREEN-ITEM-ONE-USE-001",
    "SEM-ITEM-VOLUNTARY-DISCARD-001",
    "SEM-ITEM-TRADE-GAIN-001",
    "SEM-ITEM-INTERPLAY-001",
    "SEM-RESTORE-HEALTH-001",
    "SEM-GREEN-ITEM-IMMEDIATE-USE-001",
    "SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001",
]

# Filled from the independently generated, reviewed projection. Includes Search
# because this batch adds its explicit Green-deck exhaustion no-default gate.
EXPECTED_GREEN_ITEM_RECORD_DIGESTS: dict[str, str] = {
    "SEM-ACT-SEARCH-001": "dde0f860199caec057477654cd682ee18c6341ff1da4999a0eb660257e5a1bcc",
    "SEM-GREEN-ITEM-3700-7E1C40-001": "5c497697a359c324757eb7371599a3bee0963b4d3e263dc1186dbb06eefbd00c",
    "SEM-GREEN-ITEM-3700-CEFCF6-001": "7ff15f4cbd1e3eb1b3f30677fa6a118ca32a7bdcab73164cacc8bacc363e6c63",
    "SEM-GREEN-ITEM-3700-EABBA4-001": "ab4c5a659e2ec7ef66d8b459fb27711a817c616c4e815b60fbe909c46f11d2ad",
    "SEM-GREEN-ITEM-3701-2E0877-001": "9f5f920c3964c5c01d82975f37f1030c11c2a744e6cdc053ac6abd3d8b558475",
    "SEM-GREEN-ITEM-3701-2F0205-001": "58f048fbd827a7f077c15c06b45cff2c92125cb3475c17d048fa4e1d7b37c84d",
    "SEM-GREEN-ITEM-3701-E2E7D7-001": "aa2f495fc0b9937548f98785b691fab6e1f3f2d6c5dbb1e3b9d9a0c48541ac06",
    "SEM-GREEN-ITEM-3703-C1BEF4-001": "c418d06c1180432b25b82916e20b4b5d838353700013726b8ca6c79de84f69b4",
    "SEM-GREEN-ITEM-3705-1A13AB-001": "2447f3a89a195ff9117c49b98dfc6f6c89a6bf21e472a48243cb1c345d4d74c3",
    "SEM-GREEN-ITEM-3705-271CED-001": "624e1d3648763063dbf1cb78e640382c0b618d651abba6326016667767f6ea24",
    "SEM-GREEN-ITEM-3705-6F0675-001": "b7c81544fffce8820d0340622afb7a9280e79d3e659e960f03c4f65de1c7e342",
    "SEM-GREEN-ITEM-3705-824BE4-001": "18d9be6b044453e4935451f3639c25c05cea2214f95cddaeb0e7f9df53accfbe",
    "SEM-GREEN-ITEM-3705-B9C9DF-001": "dda8de8a925b92ff9af90ab39b5eabb9a3e1e97464329c17e05671f2c7922bd0",
    "SEM-GREEN-ITEM-3707-30F2F8-001": "bac82cf9a1166a395005eb92877d253eb5de77004f6bc5f39ce2fc5c21352da2",
    "SEM-GREEN-ITEM-3707-64DF0B-001": "7fbcb0621d0ef5847d281fae0488766e7e58bc6be9ad766573925f5ac6a4268d",
    "SEM-GREEN-ITEM-3707-79581A-001": "98506a13f2ce69f2deed910a3f30f067b3032c148bb989f9d44bcc4e3e751d7b",
    "SEM-GREEN-ITEM-536500-DC077A-001": "831e3671ffa5a88ec7e5eb02409c7e7b33405ee7de96d45f43e3d7b140715b8c",
    "SEM-GREEN-ITEM-536600-4995A3-001": "035aef7552c55c6ae2c1f5152b4c7970d56b5c4613df2a74b9cb384f3687059e",
    "SEM-GREEN-ITEM-536600-D4829E-001": "b4633f5a64bd56631c4d00d3b8f243220e33d00c2b3b190a61d8d25360c22c25",
    "SEM-GREEN-ITEM-536600-F2503B-001": "f8744ee31f861306db3f2d5e28a96e493fa167f7ff71400d391bdfede808bf52",
    "SEM-GREEN-ITEM-536700-63664D-001": "89f303dcefdbed9d7459acb285968a5ac4c4816e8b337dba8b62c77d843d3c8e",
    "SEM-GREEN-ITEM-536700-7ABA7A-001": "368fa6bc63546f793db50f9fa2befbc467038ab37c4e72e2237fa53f71e001c6",
    "SEM-GREEN-ITEM-536700-96F194-001": "d29b23b344135663321977ff31b3ab7cdaa556c2d6d4ffe63499c5ea2a74911a",
    "SEM-GREEN-ITEM-536700-A35EFF-001": "42b29778ffe6ce5a9ddaca0c18db9c70949759da278cf7c83ccc049ef8c6b9dc",
    "SEM-GREEN-ITEM-DECK-001": "e7d5ae3bdd44bfca92d732ddfb0b0a1d11aa877901775e8aca1c0128f230d0d5",
    "SEM-GREEN-ITEM-IMMEDIATE-USE-001": "573e920a43d1cd9fc96dea4404721f537d2be0df9695c6e240d01eccd3aa3e0b",
    "SEM-GREEN-ITEM-ONE-USE-001": "4becefcc234b3d79849e517ef00a54b9e956b40bb514cc22de2a18c17e9e1212",
    "SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001": "eff7408269b01aef8e11c470c95cd2cb4ce5ceceb8a3cf6bb6e2139b5fb49765",
    "SEM-ITEM-INTERPLAY-001": "32d807b142fd5590e9895600d680fc198528d0ebdf9043872eca040efbb0c7a2",
    "SEM-ITEM-TRADE-GAIN-001": "0ca46870c3dff50cf649d74724bd41087382bb80955eda32a0bb08d92f5eff9a",
    "SEM-ITEM-VOLUNTARY-DISCARD-001": "bfd02f8ce71ec824b9ce4f1fb61ede73003e6eaed3356e6e294edc85ed162df0",
    "SEM-REGULAR-ITEM-BACKPACK-001": "df430b81ed6580ac93c77f906affb8638464294ddc84f9945085b2cc94d3a190",
    "SEM-RESTORE-HEALTH-001": "ad41f5d9d717bfa419b8fb882c122f62ea0783e1ba5eba02a81f5b188573e3ca",
    "SEM-USE-ITEM-001": "34b9b0c38b32a6c77cbb30f9c2c3649318e115a3de654c4a29214fb39e77ff14",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _code(card_id: int, guid: str) -> str:
    return f"{card_id}-{guid.upper()}"


def _occurrence(card_id: int, guid: str, regular: bool) -> str:
    code = _code(card_id, guid)
    return f"TTS-GREEN-ITEM-{code}-FACE" if regular else f"TTS-GREEN-ITEM-EXCLUDED-HEAVY-{code}-FACE"


def _source_id(card_id: int, guid: str, regular: bool) -> str:
    code = _code(card_id, guid)
    return f"SRC-GREEN-ITEM-{code}" if regular else f"SRC-GREEN-ITEM-EXCLUDED-HEAVY-{code}"


def _rule_id(card_id: int, guid: str) -> str:
    return f"SEM-GREEN-ITEM-{_code(card_id, guid)}-001"


def validate_green_item_family(
    repo: Path,
    source_path: Path,
    source: dict,
    source_by_id: dict[str, dict],
    backlog_by_id: dict[str, dict],
    roles: list[dict],
    objects: list[dict],
    secondary: dict,
    bga_text: str,
    record_by_id: dict[str, dict],
    question_by_id: dict[str, dict],
    conflict_rows: list[dict],
    coverage: dict,
    failures: list[dict],
) -> dict:
    faces = source.get("faces") or []
    excluded = source.get("excludedHeavyFaces") or []
    assets = source.get("sourceFaceAssets") or []
    assets_by_key = {row.get("assetKey"): row for row in assets}
    expected_regular = [row for row in EXPECTED_GREEN_ITEM_ROOT if row[5]]
    expected_heavy = [row for row in EXPECTED_GREEN_ITEM_ROOT if not row[5]]
    expected_face_ids = [_occurrence(card_id, guid, True) for _, card_id, guid, _, _, _ in expected_regular]
    expected_heavy_ids = [_occurrence(card_id, guid, False) for _, card_id, guid, _, _, _ in expected_heavy]
    face_by_id = {row.get("greenItemOccurrenceId"): row for row in faces}
    heavy_by_id = {row.get("greenItemOccurrenceId"): row for row in excluded}

    if _sha(source_path) != PINNED_GREEN_ITEM_SOURCE_INDEX_HASH:
        failures.append({"check": "pinned Green Item source index"})
    if source.get("counts") != EXPECTED_GREEN_ITEM_COUNTS or list(face_by_id) != expected_face_ids or list(heavy_by_id) != expected_heavy_ids:
        failures.append({"check": "Green Item source-index exact physical/root/Heavy occurrence count"})
    if set(assets_by_key) != set(EXPECTED_GREEN_ITEM_ASSETS) or len(assets_by_key) != len(assets):
        failures.append({"check": "Green Item exact source-face asset/variant closure"})

    role_rows = [row for row in roles if row.get("role") == "greenItemsDeck"]
    root_object = next((row for row in objects if row.get("guid") == "17400d"), {})
    child_objects = [row for row in objects if ["Deck", "17400d", ""] in (row.get("parent") or []) and row.get("gmnotes") == "greenitem"]
    all_green_tagged = [row for row in objects if row.get("gmnotes") == "greenitem"]
    expected_child_tuples = {(card_id, guid) for _, card_id, guid, _, _, _ in EXPECTED_GREEN_ITEM_ROOT}
    expected_deck_nums = ["37", "4001", "4159", "4160", "4161", "5365", "5366", "5367"]
    if (
        len(role_rows) != 1
        or role_rows[0].get("guid") != "17400d"
        or role_rows[0].get("type") != "Deck"
        or role_rows[0].get("gmnotes") != "greenitemDiscard"
        or role_rows[0].get("n_urls") != 7
        or role_rows[0].get("deck_nums") != expected_deck_nums
        or root_object.get("type") != "Deck"
        or root_object.get("parent") != []
        or len(child_objects) != 30
        or len(all_green_tagged) != 30
        or {(int(row["card_id"]), row["guid"]) for row in child_objects} != expected_child_tuples
    ):
        failures.append({"check": "Green Item root Lua role/deck/tag/container closure"})

    root = source.get("rootDeckEvidence") or {}
    expected_saved_ids = [card_id for _, card_id, _, _, _, _ in EXPECTED_GREEN_ITEM_ROOT]
    expected_selectors = [
        {
            "rootSequence": sequence,
            "fullCardId": card_id,
            "guid": guid,
            "customDeckId": custom_deck_id,
            "batchDisposition": "included-regular" if regular else "excluded-heavy",
        }
        for sequence, card_id, guid, custom_deck_id, _, regular in EXPECTED_GREEN_ITEM_ROOT
    ]
    if (
        root.get("sourceId") != "SRC-GREEN-ITEM-ROOT-DECK"
        or root.get("ttsRole") != "greenItemsDeck"
        or root.get("rootGuid") != "17400d"
        or root.get("rawSavePath") != "assets/tts-mod/extract/nemesis_script_mod.bin"
        or root.get("rawSaveSha256") != "8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68"
        or root.get("savedDeckIds") != expected_saved_ids
        or root.get("fullContainedSelectors") != expected_selectors
        or root.get("rootOrderIsGameplayOrder") is not False
        or sorted((root.get("customDeckTuples") or {})) != expected_deck_nums
    ):
        failures.append({"check": "Green Item exact raw DeckIDs/full-selector/saved-order lock"})

    expected_title_multiplicity = {
        "ADRENALINE\nINJECTION": 3,
        "ANTISEPTIC": 3,
        "CAFFEINE PILLS": 3,
        "CONTAMINATION\nCODES": 1,
        "EMERGENCY LIFE\nSUPPORT CODES": 1,
        "MEDICAL\nSTAPLER": 5,
        "MEDKIT": 4,
        "STIMULANTS": 3,
    }
    if source.get("titleMultiplicity") != expected_title_multiplicity:
        failures.append({"check": "Green Item repeated-title/copy multiplicity no-collapse lock"})

    for asset_key, expected in EXPECTED_GREEN_ITEM_ASSETS.items():
        path, source_sha, title, source_role, cell, physical_class, selected_regular, panel_count, sentence_count, icon_refs, body_digest = expected
        asset = assets_by_key.get(asset_key) or {}
        actual = (
            asset.get("sourcePath"), asset.get("sourceSha256"), asset.get("printedTitle"), asset.get("sourceRole"),
            asset.get("generatedCell"), asset.get("physicalClass"), asset.get("selectedRegular"),
        )
        if actual != expected[:7] or not (repo / path).is_file() or _sha(repo / path) != source_sha:
            failures.append({"check": "Green Item independently locked source-face asset tuple", "assetKey": asset_key})
        recomputed_text_digest = _digest({
            "title": asset.get("printedTitle"), "typeLine": asset.get("typeLine"),
            "upperRight": asset.get("upperRight"), "body": asset.get("printedBody"),
        })
        if asset.get("printedBodyDigest") != body_digest or recomputed_text_digest != body_digest:
            failures.append({"check": "Green Item exact title/body/punctuation/order lock", "assetKey": asset_key})
        regions = asset.get("regions") or []
        if (
            [row.get("regionId") for row in regions] != ["R1", "R2", "R3"]
            or [row.get("role") for row in regions] != ["artwork-and-interface", "identity-trait-and-restriction", "operative-effect-body"]
            or [row.get("operative") for row in regions] != [False, True, True]
            or (regions[1] if len(regions) > 1 else {}).get("printedTitle") != title
            or (regions[2] if len(regions) > 2 else {}).get("exactText") != asset.get("printedBody")
        ):
            failures.append({"check": "Green Item exact source region/anatomy roles/order", "assetKey": asset_key})
        panels = asset.get("panels") or []
        if (
            len(panels) != panel_count
            or [row.get("readingOrder") for row in panels] != list(range(1, len(panels) + 1))
            or [row.get("role") for row in panels[:2]] != ["artwork-panel", "identity-trait-restriction-panel"]
            or [row.get("operative") for row in panels[:2]] != [False, True]
            or any(row.get("regionId") != "R3" or row.get("operative") is not True for row in panels[2:])
            or asset.get("panelDigest") != _digest(panels)
        ):
            failures.append({"check": "Green Item exact source panel roles/order/region linkage", "assetKey": asset_key})
        sentences = asset.get("sentences") or []
        body = asset.get("printedBody") or ""
        if len(sentences) != sentence_count or [row.get("sequence") for row in sentences] != list(range(1, sentence_count + 1)):
            failures.append({"check": "Green Item exact printed sentence occurrence count/order", "assetKey": asset_key})
        cursor = 0
        panel_ids = {row.get("panelId") for row in panels[2:]}
        for sentence in sentences:
            start, end = sentence.get("start"), sentence.get("end")
            if (
                not isinstance(start, int) or not isinstance(end, int) or start < cursor
                or body[start:end] != sentence.get("exactText")
                or sentence.get("regionId") != "R3"
                or sentence.get("panelId") not in panel_ids
            ):
                failures.append({"check": "Green Item exact sentence span/punctuation/panel lock", "assetKey": asset_key, "sentenceId": sentence.get("sentenceId")})
            cursor = end if isinstance(end, int) else cursor
        icons = asset.get("iconOccurrences") or []
        if (
            tuple(row.get("semanticReferenceId") for row in icons) != icon_refs
            or [row.get("sequence") for row in icons] != list(range(1, len(icons) + 1))
            or len({row.get("assetIconOccurrenceId") for row in icons}) != len(icons)
            or any((row.get("semanticReferenceId") is None) != (row.get("page40TokenAssigned") is False) for row in icons)
            or asset.get("iconDigest") != _digest([
                {key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")}
                for icon in icons
            ])
        ):
            failures.append({"check": "Green Item exact source-local icon occurrence projection", "assetKey": asset_key})
        gap = asset.get("selectorGap")
        expected_gap = source_role == "generated-cell-selector-gap-variant"
        if (
            asset.get("selectedByRootDeck") is expected_gap
            or (expected_gap and (not isinstance(gap, dict) or gap.get("status") != "explicit-no-root-DeckID-GUID-selector" or gap.get("cardIdModuloJoinUsed") is not False))
            or (not expected_gap and gap is not None)
        ):
            failures.append({"check": "Green Item generated selector/selector-gap closure", "assetKey": asset_key})

    expected_backlog_rules: dict[str, list[str]] = {}
    expected_regular_source_ids = set()
    family_sequence = 0
    for sequence, card_id, guid, custom_deck_id, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT:
        occurrence_id = _occurrence(card_id, guid, regular)
        row = (face_by_id if regular else heavy_by_id).get(occurrence_id) or {}
        asset = assets_by_key[asset_key]
        source_id = _source_id(card_id, guid, regular)
        selector = row.get("sourceSelector") or {}
        if regular:
            family_sequence += 1
            expected_regular_source_ids.add(source_id)
        expected_tuple = (
            sequence, family_sequence if regular else None, card_id, guid, custom_deck_id, asset_key,
            "included-regular-green-item-face" if regular else "excluded-heavy-item-face",
            _rule_id(card_id, guid) if regular else None,
        )
        actual_tuple = (
            row.get("rootSequence"), row.get("familySequence"), row.get("ttsCardId"), row.get("ttsCardGuid"),
            row.get("customDeckId"), row.get("sourceAssetKey"), row.get("batchDisposition"), row.get("semanticRuleId"),
        )
        if actual_tuple != expected_tuple:
            failures.append({"check": "independently locked Green Item physical occurrence crosswalk", "occurrenceId": occurrence_id})
        if (
            row.get("sourceId") != source_id
            or row.get("sourcePath") != asset.get("sourcePath")
            or row.get("sourceSha256") != asset.get("sourceSha256")
            or row.get("physicalClass") != ("regular-item" if regular else "heavy-item")
            or selector.get("key") != "FaceURL"
            or selector.get("fullCardId") != card_id
            or selector.get("guid") != guid
            or selector.get("parentDeckGuid") != "17400d"
            or selector.get("customDeckId") != custom_deck_id
            or selector.get("backUrl") != "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235748/220899EB4989F76566E84DE9851C764359F18ECC/"
            or selector.get("sideRole") != ("operative-regular-green-item-face" if regular else "excluded-heavy-item-face")
            or selector.get("selectorGap") is not None
            or selector.get("cardIdModuloJoinUsed") is not False
        ):
            failures.append({"check": "Green Item exact CardID/GUID/FaceURL/BackURL selector projection", "occurrenceId": occurrence_id})
        expected_cell = EXPECTED_GREEN_ITEM_ASSETS[asset_key][4]
        if expected_cell is not None:
            if (
                selector.get("generatedSpriteSheetCell") is not True
                or selector.get("sourceSheetPath") != "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181.jpg"
                or selector.get("sourceSheetSha256") != "dc20f486f91b122ed9e0fed0a5b1219b8227877d5d624595423ef8f285523140"
                or selector.get("sourceSheetGrid") != {"columns": 3, "rows": 3}
                or selector.get("generatedCell") != expected_cell
            ):
                failures.append({"check": "Green Item generated sheet/hash/grid/cell selector projection", "occurrenceId": occurrence_id})
        elif selector.get("generatedSpriteSheetCell") is not False or selector.get("sourceSheetPath") is not None or selector.get("generatedCell") is not None:
            failures.append({"check": "Green Item direct/generated face selector inversion", "occurrenceId": occurrence_id})
        recomputed = _digest({
            "title": row.get("printedTitle"), "typeLine": row.get("typeLine"),
            "upperRight": row.get("upperRight"), "body": row.get("printedBody"),
        })
        if row.get("printedBodyDigest") != EXPECTED_GREEN_ITEM_ASSETS[asset_key][10] or recomputed != EXPECTED_GREEN_ITEM_ASSETS[asset_key][10]:
            failures.append({"check": "Green Item exact physical title/body/punctuation/order lock", "occurrenceId": occurrence_id})
        regions = row.get("regions") or []
        panels = row.get("panels") or []
        if (
            len(regions) != 3
            or [item.get("role") for item in regions] != ["artwork-and-interface", "identity-trait-and-restriction", "operative-effect-body"]
            or [item.get("operative") for item in regions] != [False, True, True]
            or not all(item.get("regionId", "").startswith(f"GI-{card_id}-{guid.upper()}-R") for item in regions)
        ):
            failures.append({"check": "Green Item exact physical region roles/order", "occurrenceId": occurrence_id})
        if (
            len(panels) != EXPECTED_GREEN_ITEM_ASSETS[asset_key][7]
            or [item.get("role") for item in panels[:2]] != ["artwork-panel", "identity-trait-restriction-panel"]
            or [item.get("operative") for item in panels[:2]] != [False, True]
            or panels[0].get("regionId") != regions[0].get("regionId")
            or panels[1].get("regionId") != regions[1].get("regionId")
            or any(item.get("regionId") != regions[2].get("regionId") for item in panels[2:])
            or row.get("panelDigest") != _digest(panels)
        ):
            failures.append({"check": "Green Item exact physical panel roles/order/region linkage", "occurrenceId": occurrence_id})
        if (
            len(row.get("sentences") or []) != EXPECTED_GREEN_ITEM_ASSETS[asset_key][8]
            or tuple(item.get("semanticReferenceId") for item in row.get("iconOccurrences") or []) != EXPECTED_GREEN_ITEM_ASSETS[asset_key][9]
            or any(item.get("panelId") not in {panel.get("panelId") for panel in panels} for item in (row.get("sentences") or []) + (row.get("iconOccurrences") or []))
        ):
            failures.append({"check": "Green Item exact physical sentence/panel/icon projection", "occurrenceId": occurrence_id})
        join = row.get("joinEvidence") or {}
        if (
            join.get("identityJoin") != "exact raw root physical occurrence and exact source-asset projection"
            or any(join.get(key) is not False for key in (
                "titleOnlyJoin", "colorOnlyJoin", "bodyResemblanceJoin", "folderOnlyJoin", "sourceOrderOnlyJoin",
                "generatedCellOnlyJoin", "cardIdModuloJoin", "licensedKeyJoin",
            ))
            or (row.get("licensedCrosswalk") or {}).get("status") != "not-asserted"
            or (row.get("officialCrosswalk") or {}).get("status") != "not-asserted"
        ):
            failures.append({"check": "Green Item title/color/body/folder/order/cell/modulo/licensed join prohibited", "occurrenceId": occurrence_id})
        registry = source_by_id.get(source_id) or {}
        if (
            registry.get("path"), registry.get("sha256"), registry.get("authority"),
            registry.get("occurrenceId"), registry.get("evidenceRecord"),
        ) != (asset.get("sourcePath"), asset.get("sourceSha256"), "source-bound-component-scan", occurrence_id, asset.get("sourceSha256")):
            failures.append({"check": "Green Item source-registry exact physical tuple", "occurrenceId": occurrence_id})
        backlog_id = "CARD:" + asset["sourceSha256"][:16]
        if row.get("backlogUnitId") != backlog_id:
            failures.append({"check": "Green Item exact backlog tuple projection", "occurrenceId": occurrence_id})
        if regular:
            expected_backlog_rules.setdefault(backlog_id, []).append(_rule_id(card_id, guid))
        elif (backlog_by_id.get(backlog_id) or {}).get("status") != "pending":
            failures.append({"check": "Green Item Heavy/item-family exclusion leakage", "occurrenceId": occurrence_id})

    for asset_key in ("sheet-02", "sheet-04", "sheet-06", "sheet-08"):
        asset = assets_by_key[asset_key]
        expected_backlog_rules["CARD:" + asset["sourceSha256"][:16]] = ["SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001"]
    for backlog_id, rule_ids in expected_backlog_rules.items():
        asset = next(item for item in assets if "CARD:" + item["sourceSha256"][:16] == backlog_id)
        backlog = backlog_by_id.get(backlog_id) or {}
        if (
            backlog.get("sourcePath") != asset.get("sourcePath")
            or backlog.get("sourceLocator") != asset.get("sourceSha256")
            or backlog.get("pilotRuleIds") != rule_ids
            or backlog.get("status") != "pilot-covered"
        ):
            failures.append({"check": "Green Item exact backlog tuple projection", "backlogUnitId": backlog_id})

    sheet = source.get("sourceSheet") or {}
    back = source.get("sharedBack") or {}
    if (
        (sheet.get("sourceId"), sheet.get("sourcePath"), sheet.get("sourceSha256"), sheet.get("selectorReferences"), sheet.get("selectedCells"), sheet.get("selectorGapCells"), sheet.get("separateRulesFace"))
        != ("SRC-GREEN-ITEM-SHEET", "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181.jpg", "dc20f486f91b122ed9e0fed0a5b1219b8227877d5d624595423ef8f285523140", 16, [0, 1, 3, 5, 7], [2, 4, 6, 8], False)
        or (back.get("sourceId"), back.get("sourcePath"), back.get("sourceSha256"), back.get("selectorReferences"), back.get("rulesTextPresent"), back.get("separateRulesFace"))
        != ("SRC-GREEN-ITEM-BACK", "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-152.jpg", "084784c5fc1d4e15dcd70062cf2470b4d140bb6b0643a833af9c9e72d54e579c", 31, False, False)
    ):
        failures.append({"check": "Green Item parent-sheet/back/selector-gap closure"})
    for source_id, expected_path, expected_sha, occurrence_id in (
        ("SRC-GREEN-ITEM-ROOT-DECK", "assets/tts-mod/extract/nemesis_script_mod.bin", "8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68", "TTS-GREEN-ITEM-ROOT-DECK"),
        ("SRC-GREEN-ITEM-SHEET", sheet.get("sourcePath"), sheet.get("sourceSha256"), "TTS-GREEN-ITEM-PARENT-SHEET-37"),
        ("SRC-GREEN-ITEM-BACK", back.get("sourcePath"), back.get("sourceSha256"), "TTS-GREEN-ITEM-SHARED-BACK"),
    ):
        registry = source_by_id.get(source_id) or {}
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId")) != (expected_path, expected_sha, occurrence_id):
            failures.append({"check": "Green Item source-registry root/sheet/back closure", "sourceId": source_id})
    for cell in (2, 4, 6, 8):
        source_id = f"SRC-GREEN-ITEM-VARIANT-37-CELL-{cell:02d}"
        asset = assets_by_key[f"sheet-{cell:02d}"]
        registry = source_by_id.get(source_id) or {}
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId")) != (asset.get("sourcePath"), asset.get("sourceSha256"), f"TTS-GREEN-ITEM-VARIANT-37-CELL-{cell:02d}"):
            failures.append({"check": "Green Item source-registry selector-gap closure", "sourceId": source_id})

    licensed = source.get("licensedDigitalOccurrences") or []
    expected_bga = [
        ("AdrenalineInjection", 3, False), ("Antiseptic", 3, False), ("CaffeinePills", 3, False),
        ("EmergencyLifeSupportCodes", 1, False), ("HeavyOxygenTank", 3, True),
        ("MedicalStapler", 5, False), ("Medkit", 4, True), ("Medpack", 4, False),
        ("Stimulants", 3, False), ("TerminationCodes", 1, False),
    ]
    items_table = next((row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row.get("name") == "ITEMS_DATA"), {})
    if (
        [(row.get("key"), row.get("nbr"), row.get("heavy")) for row in licensed] != expected_bga
        or items_table.get("count") != 57
        or any(row.get("identityCrosswalkStatus") != "independent licensed occurrence; no TTS/official physical identity join asserted" or not row.get("sourceBlockText") or row.get("sourceBlockText") not in bga_text for row in licensed)
        or sum(row.get("nbr", 0) for row in licensed) != 30
        or sum(row.get("nbr", 0) for row in licensed if not row.get("heavy") and not row.get("armor")) != 23
        or sum(row.get("nbr", 0) for row in licensed if row.get("heavy") or row.get("armor")) != 7
    ):
        failures.append({"check": "Green Item licensed independent rows/30-23-7/no-crosswalk closure"})
    bga_registry = source_by_id.get("SRC-BGA-GREEN-ITEMS") or {}
    if bga_registry.get("occurrenceId") != "ITEMS_DATA:deck-green" or bga_registry.get("evidenceRecord") != "ITEMS_DATA":
        failures.append({"check": "Green Item licensed source-registry closure"})

    official = source.get("officialVisibleCounterparts") or []
    if (
        [row.get("sourceOccurrenceId") for row in official] != ["RB-P03-V01", "RB-P09-V01", "RB-P12-V02", "RB-P28-V02", "RB-P28-V03", "RB-P29-V01", "RB-P40-V02"]
        or any(row.get("exactGreenRulesFace") is not False for row in official)
        or source.get("counts", {}).get("officialVisibleFaceOccurrences") != 0
        or source.get("counts", {}).get("officialVisibleBackOccurrences") != 0
    ):
        failures.append({"check": "Green Item official family/no-exact-face authority closure"})
    faq = source.get("faqSearchClosure") or {}
    if [row.get("sourceUnitId") for row in faq.get("baseApplicableOccurrences") or []] != ["FQ-P02-U04", "FQ-P03-U04", "FQ-P03-U07"] or len(faq.get("excludedExpansionOccurrences") or []) != 4:
        failures.append({"check": "Green Item FAQ base/expansion applicability closure"})

    expected_overlap = [
        "RULE:ACT-ITEM-001", "RULE:ACT-TRADE-001", "RULE:ITM-001", "RULE:ITM-002", "RULE:ITM-003", "RULE:ITM-004", "RULE:ITM-006", "RULE:ITM-008",
        "FAQ:FQ-P02-U04", "FAQ:FQ-P03-U04", "FAQ:FQ-P03-U07",
        "VIS:RB-P03-V01", "VIS:RB-P09-V01", "VIS:RB-P12-V02", "VIS:RB-P28-V02", "VIS:RB-P28-V03", "VIS:RB-P29-V01", "VIS:RB-P40-V02",
    ]
    expected_linked = sorted(set([*expected_backlog_rules, *expected_overlap]))
    backlog_ledger = (source.get("familyCountEvidence", {}).get("backlog") or {})
    if (
        backlog_ledger.get("linkedUnitIds") != expected_linked
        or backlog_ledger.get("faceTupleCount") != 8
        or backlog_ledger.get("variantTupleCount") != 4
        or backlog_ledger.get("physicalFaceLinkCount") != 23
        or backlog_ledger.get("obligationCount") != 30
        or any((backlog_by_id.get(unit_id) or {}).get("status") != "pilot-covered" for unit_id in expected_linked)
    ):
        failures.append({"check": "Green Item exact overlapping backlog-obligation closure"})

    expected_rule_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, _, regular in EXPECTED_GREEN_ITEM_ROOT if regular]
    actual_rule_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r"SEM-GREEN-ITEM-\d+-[A-Z0-9]+-001", rule_id)}
    if actual_rule_ids != set(expected_rule_ids):
        failures.append({"check": "Green Item semantic physical face-record closure", "missing": sorted(set(expected_rule_ids) - actual_rule_ids), "extra": sorted(actual_rule_ids - set(expected_rule_ids))})

    for _, card_id, guid, _, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT:
        if not regular:
            continue
        occurrence_id = _occurrence(card_id, guid, True)
        source_face = face_by_id.get(occurrence_id) or {}
        rule_id = _rule_id(card_id, guid)
        rule = record_by_id.get(rule_id) or {}
        code = _code(card_id, guid)
        assertions = {row.get("assertionId"): row for row in rule.get("sourceAssertions") or []}
        scan = assertions.get(f"SA-GIF-{code}-SCAN") or {}
        general = assertions.get(f"SA-GIF-{code}-GENERAL") or {}
        if (
            (scan.get("sourceId"), scan.get("sourceSha256"), scan.get("sourceText"), scan.get("textKind"))
            != (_source_id(card_id, guid, True), EXPECTED_GREEN_ITEM_ASSETS[asset_key][1], source_face.get("printedBody"), "verbatim")
            or general.get("sourceId") != "SRC-RULEBOOK"
            or rule.get("authority", {}).get("highest") != "official-primary"
            or rule.get("sourceVariants") != []
        ):
            failures.append({"check": "Green Item face exact scan/general/authority/no-variant projection", "occurrenceId": occurrence_id})
        expected_questions = {
            "direct-5367": ["SEM-Q-043", "SEM-Q-044", "SEM-Q-045"],
            "sheet-00": ["SEM-Q-041"],
            "sheet-03": ["SEM-Q-042"],
            "sheet-05": ["SEM-Q-043"],
            "sheet-07": ["SEM-Q-041", "SEM-Q-043"],
        }.get(asset_key, [])
        if rule.get("unresolvedQuestionRefs") != expected_questions or rule.get("status") != ("source-backed-with-open-question" if expected_questions else "source-backed"):
            failures.append({"check": "Green Item face exact optionality/owner/no-default question projection", "occurrenceId": occurrence_id})
        sentence_ids = {row.get("sentenceId") for row in source_face.get("sentences") or []}
        panel_ids = {row.get("panelId") for row in source_face.get("panels") or []}
        region_ids = {row.get("regionId") for row in source_face.get("regions") or []}
        operations = rule.get("operations") or []
        if not operations or any(op.get("sourceSentenceId") not in sentence_ids or op.get("sourcePanelId") not in panel_ids or op.get("sourceRegionId") not in region_ids for op in operations):
            failures.append({"check": "Green Item face operation-to-sentence/panel/region closure", "occurrenceId": occurrence_id})
        if "same title/body/multiplicity creates no identity or stacking key" not in rule.get("stacking", {}).get("policy", ""):
            failures.append({"check": "Green Item physical-copy/no-title stacking lock", "occurrenceId": occurrence_id})
        if asset_key in {"sheet-00", "sheet-07"}:
            if "icon.actionCard" in rule.get("termRefs", []) or not any(op.get("operationType") == "resolve-open-alternative" and "SEM-Q-041" in op.get("objectRef", "") for op in operations):
                failures.append({"check": "Green Item local glyph no-default/no-licensed-placeholder lock", "occurrenceId": occurrence_id})

    use = record_by_id.get("SEM-USE-ITEM-001") or {}
    use_ops = use.get("operations") or []
    use_dispatch = next((op.get("dispatchRuleIds") for op in use_ops if op.get("dispatchRuleIds")), [])
    if (
        use_dispatch[:len(expected_rule_ids)] != expected_rule_ids
        or len(use_dispatch) != len(set(use_dispatch))
        or [op.get("operationType") for op in use_ops] != ["select-target", "resolve-open-alternative", "pay-cost", "reveal", "invoke-selected-process", "invoke-selected-process"]
        or use_ops[-1].get("dispatchRuleIds") != ["SEM-GREEN-ITEM-ONE-USE-001", "SEM-RED-ITEM-ONE-USE-001", "SEM-YELLOW-ITEM-ONE-USE-001"]
        or use.get("costs", [{}])[0].get("quantity") != 1
        or use.get("decisions", [{}])[0].get("ownerRef") != "P-PLAYER"
        or use.get("unresolvedQuestionRefs") != ["SEM-Q-039"]
    ):
        failures.append({"check": "Green Item Use/payment/reveal/dispatch/owner/order lock"})
    one_use = record_by_id.get("SEM-GREEN-ITEM-ONE-USE-001") or {}
    one_use_ops = one_use.get("operations") or []
    if (
        [op.get("operationType") for op in one_use_ops] != ["resolve-open-alternative", "transition-zone", "evaluate-condition"]
        or (one_use_ops[1].get("transition") or {}).get("to") != "tax.scaffold.zone.discard-pile"
        or one_use.get("unresolvedQuestionRefs") != ["SEM-Q-039"]
        or "return to deck/bottom" not in one_use.get("partialResolution", {}).get("onImpossible", "")
    ):
        failures.append({"check": "Green Item One Use lifecycle/discard/no-return order lock"})
    deck = record_by_id.get("SEM-GREEN-ITEM-DECK-001") or {}
    deck_ops = deck.get("operations") or []
    if (
        [op.get("operationType") for op in deck_ops] != ["shuffle", "transition-zone", "set-state", "evaluate-condition", "resolve-open-alternative", "draw-random", "evaluate-condition"]
        or (deck_ops[0].get("repeat") or {}).get("rootPhysicalCardCount") != 30
        or (deck_ops[0].get("repeat") or {}).get("regularBatchFaceCount") != 23
        or (deck_ops[0].get("repeat") or {}).get("excludedHeavyCount") != 7
        or deck.get("unresolvedQuestionRefs") != ["SEM-Q-040"]
        or any(op.get("operationType") == "shuffle" and "discard" in op.get("objectRef", "").lower() for op in deck_ops[1:])
    ):
        failures.append({"check": "Green Item finite deck/root-class/exhaustion/no-reshuffle lock"})
    backpack = record_by_id.get("SEM-REGULAR-ITEM-BACKPACK-001") or {}
    if "unlimited" not in json.dumps(backpack, ensure_ascii=False).lower() or "owner-private" not in json.dumps(backpack, ensure_ascii=False):
        failures.append({"check": "Green Item Backpack unlimited/private/reveal lock"})
    trade = record_by_id.get("SEM-ITEM-TRADE-GAIN-001") or {}
    interplay = record_by_id.get("SEM-ITEM-INTERPLAY-001") or {}
    restore = record_by_id.get("SEM-RESTORE-HEALTH-001") or {}
    immediate = record_by_id.get("SEM-GREEN-ITEM-IMMEDIATE-USE-001") or {}
    voluntary = record_by_id.get("SEM-ITEM-VOLUNTARY-DISCARD-001") or {}
    if (
        not any(decision.get("selectionMode") == "mutual-consent" for decision in trade.get("decisions") or [])
        or trade.get("unresolvedQuestionRefs") != ["SEM-Q-045", "SEM-Q-054"]
        or not any(decision.get("selectionMode") == "consent" and decision.get("declineAllowed") for decision in interplay.get("decisions") or [])
        or interplay.get("unresolvedQuestionRefs") != ["SEM-Q-044"]
        or restore.get("decisions", [{}])[0].get("ownerRef") != "P-RULES"
        or restore.get("decisions", [{}])[0].get("selectionMode") != "unresolved"
        or restore.get("unresolvedQuestionRefs") != ["SEM-Q-043"]
        or immediate.get("decisions", [{}])[0].get("cardinality") != {"min": 0, "max": 1}
        or immediate.get("decisions", [{}])[0].get("declineAllowed") is not True
        or immediate.get("unresolvedQuestionRefs") != ["SEM-Q-045"]
        or any(op.get("invokeRuleId") for op in voluntary.get("operations") or [])
    ):
        failures.append({"check": "Green Item consent/restore-owner/immediate-option/voluntary-no-use lock"})

    variant = record_by_id.get("SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001") or {}
    variant_rows = variant.get("sourceVariants") or []
    if (
        variant.get("status") != "source-variant"
        or len(variant_rows) != 21
        or len(variant.get("sourceAssertions") or []) != 13
        or len(variant.get("operations") or []) != 22
        or any(row.get("sourceAssertionId") not in {item.get("assertionId") for item in variant.get("sourceAssertions") or []} for row in variant_rows)
        or "no title, color, body" not in (variant.get("operations") or [{}])[-1].get("objectRef", "")
    ):
        failures.append({"check": "Green Item Heavy/gap/licensed variant preservation lock"})

    medkit_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT if regular and asset_key == "direct-5367"]
    adrenaline_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT if regular and asset_key == "sheet-00"]
    stimulant_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT if regular and asset_key == "sheet-07"]
    restore_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT if regular and asset_key in {"direct-5367", "sheet-05", "sheet-07"}]
    contamination_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, asset_key, regular in EXPECTED_GREEN_ITEM_ROOT if regular and asset_key == "sheet-03"]
    expected_question_blocks = {
        "SEM-Q-039": ["SEM-USE-ITEM-001", "SEM-GREEN-ITEM-ONE-USE-001"],
        "SEM-Q-040": ["SEM-GREEN-ITEM-DECK-001", "SEM-ACT-SEARCH-001"],
        "SEM-Q-041": [*adrenaline_ids, *stimulant_ids],
        "SEM-Q-042": contamination_ids,
        "SEM-Q-043": ["SEM-RESTORE-HEALTH-001", *restore_ids],
        "SEM-Q-044": ["SEM-ITEM-INTERPLAY-001", *medkit_ids],
        "SEM-Q-045": ["SEM-ITEM-TRADE-GAIN-001", "SEM-GREEN-ITEM-IMMEDIATE-USE-001", *medkit_ids],
    }
    for question_id, blocks in expected_question_blocks.items():
        question = question_by_id.get(question_id) or {}
        actual_blocks = question.get("blocksRuleIds") or []
        combined_family_question = question_id in {"SEM-Q-039", "SEM-Q-040", "SEM-Q-044", "SEM-Q-045"}
        if question.get("defaultProhibited") is not True or (actual_blocks[:len(blocks)] != blocks if combined_family_question else actual_blocks != blocks) or len(question.get("alternatives") or []) != 3:
            failures.append({"check": "Green Item ambiguity no-default alternatives/linkage", "questionId": question_id})

    green_conflicts = {row.get("conflictId"): row for row in conflict_rows if row.get("conflictId") in {"SC-029", "SC-030", "SC-031", "SC-032", "SC-033"}}
    if (
        set(green_conflicts) != {"SC-029", "SC-030", "SC-031", "SC-032", "SC-033"}
        or [green_conflicts[key].get("status") for key in ("SC-029", "SC-030", "SC-031", "SC-032", "SC-033")]
        != ["preserved-boundary", "unresolved", "resolved-by-authority", "preserved-boundary", "preserved-boundary"]
        or green_conflicts.get("SC-030", {}).get("questionId") != "SEM-Q-041"
    ):
        failures.append({"check": "Green Item source-variant authority/conflict closure"})

    if EXPECTED_GREEN_ITEM_RECORD_DIGESTS:
        if not set(EXPECTED_GREEN_ITEM_RECORD_DIGESTS).issubset(record_by_id):
            failures.append({"check": "independently locked Green Item semantic projection", "missing": sorted(set(EXPECTED_GREEN_ITEM_RECORD_DIGESTS) - set(record_by_id))})
        for rule_id, expected_digest in EXPECTED_GREEN_ITEM_RECORD_DIGESTS.items():
            item = record_by_id.get(rule_id)
            actual_digest = _digest(item) if item else None
            if actual_digest != expected_digest:
                failures.append({"check": "independently locked Green Item semantic projection", "ruleId": rule_id, "actual": actual_digest})

    system = next((row for row in coverage.get("systems") or [] if row.get("system") == "base regular Green Item card/component family"), {})
    expected_system_ids = [*EXPECTED_GREEN_ITEM_REUSABLE_RULE_IDS, *expected_rule_ids]
    not_yet = " ".join(coverage.get("notYetCovered") or [])
    if system.get("ruleIds") != expected_system_ids or "23-occurrence regular Green Item" not in not_yet or "seven Heavy Green occurrences" not in not_yet:
        failures.append({"check": "Green Item coverage/Heavy-boundary/no-full-coverage claim"})

    return {
        "rows": faces,
        "assets": assets,
        "excluded": excluded,
        "licensed": licensed,
        "official": official,
        "actualRuleIds": actual_rule_ids,
        "expectedBacklogRules": expected_backlog_rules,
    }
