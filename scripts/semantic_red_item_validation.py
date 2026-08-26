from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


PINNED_RED_ITEM_SOURCE_INDEX_HASH = "35a167b27291bdb7cf5d119d036018c9a7537ec8e4e7b5eba3d546a247f8f929"

EXPECTED_RED_ITEM_COUNTS = {
    "rootPhysicalOccurrences": 30,
    "regularPhysicalFaceOccurrences": 21,
    "excludedHeavyPhysicalOccurrences": 3,
    "physicalClassConflictOccurrences": 6,
    "currentOfficialLicensedHeavyAggregate": 9,
    "uniqueRegularPrintedTitles": 7,
    "uniqueSelectedRegularFaceAssets": 7,
    "sourceFaceAssets": 16,
    "rulesBearingSourceFaceAssets": 15,
    "nonRulesSourceCells": 1,
    "generatedRegularPhysicalFaceOccurrences": 7,
    "directRegularPhysicalFaceOccurrences": 14,
    "generatedClassConflictPhysicalOccurrences": 6,
    "directHeavyPhysicalOccurrences": 3,
    "sourceSheets": 2,
    "sourceSheetCells": 12,
    "selectedGeneratedCells": 5,
    "redSelectorGapCells": 4,
    "crossFamilySelectorGapCells": 3,
    "rootBackAssets": 2,
    "redBackPhysicalSelectors": 24,
    "yellowBackPhysicalSelectors": 6,
    "redBackGlobalSelectorReferences": 25,
    "yellowBackGlobalSelectorReferences": 13,
    "redSheetGlobalSelectorReferences": 8,
    "yellowSheetGlobalSelectorReferences": 13,
    "rootCustomDeckEntries": 13,
    "physicalRegions": 63,
    "operativeRegions": 42,
    "physicalPanels": 87,
    "operativePanels": 66,
    "oneUseHeadingOccurrences": 21,
    "specialWeaponHeadingOccurrences": 15,
    "branchSeparatorHeadingOccurrences": 5,
    "useDiscardPassiveReactionHeadingOccurrences": 0,
    "printedSentenceOccurrences": 45,
    "physicalFunctionalIconOccurrences": 27,
    "physicalMatchedIconOccurrences": 23,
    "physicalUnresolvedLocalGlyphOccurrences": 4,
    "redSelectorGapFunctionalIconOccurrences": 9,
    "redSelectorGapMatchedIconOccurrences": 2,
    "redSelectorGapUnresolvedLocalGlyphOccurrences": 7,
    "crossFamilyGapFunctionalIconOccurrences": 5,
    "classConflictFunctionalIconOccurrences": 12,
    "excludedHeavyFunctionalIconOccurrences": 18,
    "licensedDigitalOccurrences": 9,
    "licensedDigitalPhysicalCopies": 30,
    "licensedRegularOccurrences": 7,
    "licensedRegularPhysicalCopies": 21,
    "licensedHeavyOccurrences": 2,
    "licensedHeavyPhysicalCopies": 9,
    "officialInventoryCopiesPerType": 30,
    "officialVisibleRegularFaceOccurrences": 0,
    "officialVisibleHeavySameTitleOccurrences": 1,
    "officialVisibleBackOccurrences": 0,
    "officialFamilyVisualOccurrences": 14,
    "baseApplicableFaqOccurrences": 6,
    "excludedExpansionFaqOccurrences": 4,
    "backlogTuples": 11,
    "backlogPhysicalFaceLinks": 21,
    "backlogObligationsLinked": 43,
    "semanticPhysicalFaceRecords": 21,
}

# root sequence, full CardID, GUID, CustomDeck ID, source asset, batch disposition
EXPECTED_RED_ITEM_ROOT = [
    (1, 3500, "37723a", "35", "yellow-sheet-00", "excluded-physical-class-conflict"),
    (2, 3500, "d1fe22", "35", "yellow-sheet-00", "excluded-physical-class-conflict"),
    (3, 3500, "173951", "35", "yellow-sheet-00", "excluded-physical-class-conflict"),
    (4, 3500, "179555", "35", "yellow-sheet-00", "excluded-physical-class-conflict"),
    (5, 3500, "2f5802", "35", "yellow-sheet-00", "excluded-physical-class-conflict"),
    (6, 3500, "fa1a60", "35", "yellow-sheet-00", "excluded-physical-class-conflict"),
    (7, 531600, "0c0643", "5316", "direct-heavy-remote", "excluded-heavy-item-face"),
    (8, 531500, "810d80", "5315", "direct-heavy-remote", "excluded-heavy-item-face"),
    (9, 531400, "5df671", "5314", "direct-heavy-remote", "excluded-heavy-item-face"),
    (10, 543800, "01970b", "5438", "direct-ammo", "included-regular-red-item-face"),
    (11, 543800, "d8d841", "5438", "direct-ammo", "included-regular-red-item-face"),
    (12, 543800, "43ac80", "5438", "direct-ammo", "included-regular-red-item-face"),
    (13, 543800, "ea2857", "5438", "direct-ammo", "included-regular-red-item-face"),
    (14, 543800, "af5a2d", "5438", "direct-ammo", "included-regular-red-item-face"),
    (15, 543800, "eaf654", "5438", "direct-ammo", "included-regular-red-item-face"),
    (16, 543800, "ee51d1", "5438", "direct-ammo", "included-regular-red-item-face"),
    (17, 3601, "2bc2db", "36", "red-sheet-01", "included-regular-red-item-face"),
    (18, 530700, "ed1060", "5307", "direct-exploring", "included-regular-red-item-face"),
    (19, 530800, "301a8b", "5308", "direct-exploring", "included-regular-red-item-face"),
    (20, 3604, "82349f", "36", "red-sheet-04", "included-regular-red-item-face"),
    (21, 3604, "8bfa0b", "36", "red-sheet-04", "included-regular-red-item-face"),
    (22, 3604, "1df1c5", "36", "red-sheet-04", "included-regular-red-item-face"),
    (23, 530900, "9cda71", "5309", "direct-grenade", "included-regular-red-item-face"),
    (24, 531000, "ebc22d", "5310", "direct-grenade", "included-regular-red-item-face"),
    (25, 531100, "5108bc", "5311", "direct-grenade", "included-regular-red-item-face"),
    (26, 531200, "11f04f", "5312", "direct-grenade", "included-regular-red-item-face"),
    (27, 531300, "dc960f", "5313", "direct-grenade", "included-regular-red-item-face"),
    (28, 3606, "ea89da", "36", "red-sheet-06", "included-regular-red-item-face"),
    (29, 3607, "3dad95", "36", "red-sheet-07", "included-regular-red-item-face"),
    (30, 3607, "7afbe8", "36", "red-sheet-07", "included-regular-red-item-face"),
]

# path, sha, title, source role, cell, physical class, selected disposition,
# panel count, sentence count, exact ordered semantic icon refs, composite text digest
EXPECTED_RED_ITEM_ASSETS = {
    "direct-ammo": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-059.png", "e9ca2730644b069ebdfc3e5002b3a7656fc1a37035c38eebf7062e2f78f59651", "AMMO MAGAZINE", "direct-regular-face", None, "regular-item", "included-regular", 4, 2, ("icon.ammoToken",), "a26167a1ac83077f6375f1881914e6df3be159fa85f82fb5ea8ad2d2df1a5ec2"),
    "direct-exploring": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-112.png", "b728051696f6e41cefa58c203125c1470a3a48c589820b5b8a82cbf18c28681c", "EXPLORING\nDRONE", "direct-regular-face", None, "regular-item", "included-regular", 4, 2, ("icon.notInCombat",), "4522724897f3cbba69e03d70254bd8a73877d3f217a68633a838ccc32faeaa5e"),
    "direct-grenade": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-128.png", "3eef2e9fb435151291841b16a1785b5ac98f999c09bcb9f9c5a03b7b61d83ab1", "GRENADE", "direct-regular-face", None, "regular-item", "included-regular", 5, 3, ("icon.grenadeToken", "icon.grenadeToken"), "3fe1815185b6d270256aea4f9160df7e7426369ad7845b5e2f07386814c47133"),
    "direct-heavy-remote": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-117.png", "9eb1ddc91a26bc4581a12f685edce6d1858b93770f576c3be3062a30f293d2db", "REMOTE DETONATOR", "direct-heavy-face-excluded", None, "heavy-item", "excluded-heavy", 3, 3, (None, "icon.secure", "icon.shootDieCritical", "icon.intruder", "icon.character", "icon.characterHealth"), "1cd1a4a657cd230d30c988dd882ddf536cce892521b6bf89d25c57cd6075294f"),
    "yellow-sheet-00": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-00.png", "41183eb8c34b083a45ccebaab4428902aaba2e8b2d1cceb168f2f2d99880fa0d", "MILITARY TASER", "generated-cell-physical-class-conflict", 0, "source-conflicted-portrait-special-weapon-versus-current-heavy", "class-conflict-excluded", 5, 2, ("icon.intruder", None), "cdc24ff4f065ad649e9d7d266a33b0dfe2cc62d9e4c5e2cffe986c4a9e553cf2"),
    "yellow-sheet-01": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-01.png", "326e23792c922ed04dd2d52ebf272c83d4cf8840cfc752b1b7d8cce136a50bea", "FIRE EXTINGUISHER", "generated-cell-cross-family-selector-gap", 1, "cross-family-yellow-special-weapon", "cross-family-gap-excluded", 5, 2, ("icon.fire", "icon.intruder"), "f7fed2bc2b55c6b21bb7bacd8257c4c53fb9d8010c2a1b4a265431822e0b2765"),
    "yellow-sheet-02": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-02.png", "6dc2643df6e90da076d79f330df888f4264607d560d367df8a89f57256eaadac", "ROBOT CONTROLLER", "generated-cell-cross-family-selector-gap", 2, "cross-family-yellow-item", "cross-family-gap-excluded", 5, 2, (None, "icon.robot", "icon.robot"), "e1340cc2c1bc19f2959148017b8e96ff7e97606dfe2d599b6e33dc85bbb7e379"),
    "yellow-sheet-03": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-03.png", "77223a77d61181cd144bd508dfcbfe91e135e093395d15e8b9957ce51669d8c4", "", "generated-cell-cross-family-non-rules-gap", 3, "cross-family-non-rules-cell", "cross-family-gap-excluded", 2, 0, (), "ba2aff362390241ac3f717eaf5641f75aade976372881087589497041efd1cc2"),
    "red-sheet-00": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-00.png", "7408e9ff7bbbfbea602627c74881c561ca7df151626bb160d2a8ceca1d1f24c0", "AMMO MAGAZINE", "generated-cell-selector-gap-variant", 0, "regular-item", "red-selector-gap", 4, 2, ("icon.ammoToken",), "eb6e917564f2734309ddfb267d05ea1a3945443f91310653cd847231ece77c5c"),
    "red-sheet-01": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-01.png", "4d61a4e3a38bc7cb5ecf52f452457c59ecc7c95755d25ee380238d7835caba77", "ANTI-AIRCRAFT\nCODES", "generated-cell-regular-face", 1, "regular-item", "included-regular", 4, 2, (None, "icon.computer", "icon.malfunction"), "da1977f9c5776735900e1c4d31f54ddc6b5a28666e6b2f29867e4037de99fea7"),
    "red-sheet-02": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-02.png", "441834df437ddff13e8fe8d485e615df7b67730aa1903610fbd474ee73d0161c", "CLAYMORE\nMINE", "generated-cell-selector-gap-variant", 2, "regular-item", "red-selector-gap", 3, 2, (None, None, "icon.intruder", None), "7d6dfea75d404cbb3040ff98003e8c94cefb5bea6825c0e9776352f15215da3f"),
    "red-sheet-03": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-03.png", "8f1f1ba0b8958061a8fb1ac0bea5972f6d090db76b56f4eb148ff0a8a337d992", "EXPLORING\nDRONE", "generated-cell-selector-gap-variant", 3, "regular-item", "red-selector-gap", 3, 1, (None,), "26fb1a1881ba772b9423b4f6b605e03c59b7f99087de362824b88d1c34b1bc0d"),
    "red-sheet-04": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-04.png", "fe73d2d8b678f1d731e9fad4b8e2ecfbe4c37a8487fc0ad8eca1c1627bd9cd46", "FLASHBANG", "generated-cell-regular-face", 4, "regular-item", "included-regular", 4, 2, (), "173e87beec0015967d8cd4e087753fa0a71b6bb0e8836ba3402df32ae2720513"),
    "red-sheet-05": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-05.png", "e54b40f88c76cacea72d0ef10c82beb8c9170bb1d9db7d092c3557738492a79f", "GRENADE", "generated-cell-selector-gap-variant", 5, "regular-item", "red-selector-gap", 5, 3, (None, None, None), "4d331222c21c3758f28cea7a633b1ebddb3ebf2215bb62fe9d8d46d49193e18f"),
    "red-sheet-06": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-06.png", "e149151bec4cb0d41875581b66864e5f2dd1465e169158ff46ce62f7aedc7c91", "PERSONAL\nLOG CODES", "generated-cell-regular-face", 6, "regular-item", "included-regular", 4, 2, (None, "icon.computer", "icon.malfunction"), "52bc5d75c394600753e91b15ba949de1af8132e3f2f8891e46cfb9daef30f10a"),
    "red-sheet-07": ("assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-07.png", "af3fa0947175239122c8d9a9075e39a3cc30f45a83d5838638619fafc4a67fb7", "PORTABLE\nBARRIER", "generated-cell-regular-face", 7, "regular-item", "included-regular", 3, 1, (None,), "be738e6b72bc65b47c4b45284fb30cdf3d04a8f7b3538a305a7b5e321691f66f"),
}

EXPECTED_RED_ITEM_REUSABLE_RULE_IDS = [
    "SEM-RED-ITEM-DECK-001", "SEM-RED-ITEM-ONE-USE-001", "SEM-AMMO-TOKEN-LIFECYCLE-001",
    "SEM-GRENADE-TOKEN-EFFECT-001", "SEM-ANTI-AIRCRAFT-TOKEN-STATE-001",
    "SEM-RED-ITEM-IMMEDIATE-USE-001", "SEM-RED-ITEM-VARIANT-BOUNDARIES-001",
]

EXPECTED_RED_ITEM_RECORD_DIGESTS: dict[str, str] = {
    "SEM-USE-ITEM-001": "34b9b0c38b32a6c77cbb30f9c2c3649318e115a3de654c4a29214fb39e77ff14",
    "SEM-ITEM-TRADE-GAIN-001": "0ca46870c3dff50cf649d74724bd41087382bb80955eda32a0bb08d92f5eff9a",
    "SEM-ACT-TACTICAL-001": "23da207776a84f3bc7fa9e1851b28db427779cc7b92a401a3e40e19fb11a3f9e",
    "SEM-RED-ITEM-DECK-001": "cc027bdd1bc81134bd7c1e60ae249ac517cb4a51c8b9200b42ba26fb10900526",
    "SEM-RED-ITEM-ONE-USE-001": "87023177bf157ddc9468ad3c19e2904228355bb8c0aad6d74a2fffd58463e8d2",
    "SEM-RED-ITEM-IMMEDIATE-USE-001": "ce461f76df9803824e5dcb3a483de08bce75ab614bb62976ddbb6f2207fb42a6",
    "SEM-AMMO-TOKEN-LIFECYCLE-001": "558e6e8c50833aab2aa5830b5bfedc03ee36f571ac3ed3d60cd2efef685760cb",
    "SEM-GRENADE-TOKEN-EFFECT-001": "dc89d59126edba19c5a3fb9e96e7dd843b00c93fb49e3acddb3089fd9b3d2623",
    "SEM-ANTI-AIRCRAFT-TOKEN-STATE-001": "2eee551eacb4ab3330f716fb964b17fcf1cb00ad7eea7c1bc11deaa5346ca538",
    "SEM-RED-ITEM-VARIANT-BOUNDARIES-001": "6c8f26a32bd84dbaba119f7c4429a7b39c5dbddb6f80321ba70f4e4f98ecb342",
    "SEM-RED-ITEM-543800-01970B-001": "0c85be7b068ffa5918d0023c559d59bbf38c78fa7dee3e273712fa76d2deeff1",
    "SEM-RED-ITEM-543800-D8D841-001": "edbb6c652d1eecc3fb283ac844967c9b3bfaf9016cd55cad43088628e9c21211",
    "SEM-RED-ITEM-543800-43AC80-001": "9c8458f80e5ce871fda6411f4af775268fc9bfc2d75218bb19abadb769c87044",
    "SEM-RED-ITEM-543800-EA2857-001": "de18e384647f3a2799aadf849495ece1461156f71e1c770a4ff09e639e1c36b6",
    "SEM-RED-ITEM-543800-AF5A2D-001": "ebfe9af8588e282648e26701cd65654753a8e4592c605f8937a7f2df37817a17",
    "SEM-RED-ITEM-543800-EAF654-001": "534d8d768c345098ac1a8a3704c91e0ebee31f8a0f05bced6180d4ff1b657529",
    "SEM-RED-ITEM-543800-EE51D1-001": "374f1e908a8588f9e219a7005280f6f97bb268d03169ee3450de560395fa9a21",
    "SEM-RED-ITEM-3601-2BC2DB-001": "62bec8d3928aa35dae4133fa005a24a647a5ac1f17b1891950c0a80ae49fd347",
    "SEM-RED-ITEM-530700-ED1060-001": "98dc10c7dd4bd87b9db13613446ae4fd3c08268fd4da39d04ed942b770474593",
    "SEM-RED-ITEM-530800-301A8B-001": "9fd358837d459d80a0522b647a1f07c05dc7d247918efc40216abae55b1b49b7",
    "SEM-RED-ITEM-3604-82349F-001": "8a464828967a1147df39bbdaf168ae58f05174d360870661d22c2c59bcb28346",
    "SEM-RED-ITEM-3604-8BFA0B-001": "54fdd87a4d09cf4b96de555713d7911a1739658b64633099cc51f768758a3638",
    "SEM-RED-ITEM-3604-1DF1C5-001": "83b3048c0cc00509eeb6b38e354d3dc83cf6e2f13458ddcd12dcae21271b4160",
    "SEM-RED-ITEM-530900-9CDA71-001": "46921882655d333c8e4c5e17e868059723490040b93cb869e664802340282dae",
    "SEM-RED-ITEM-531000-EBC22D-001": "67dcb1f2ea1ed6a34c136f6fe4a05f55ed26b59572fd71a2c6e75932987d1235",
    "SEM-RED-ITEM-531100-5108BC-001": "65bebc101a4bcdf9b7c7fc4a446b3b107712e5791de2890612233aad1dd3008b",
    "SEM-RED-ITEM-531200-11F04F-001": "73c1d9595705a7e93a926f2f1fb63572abf663aeedac9e13e53994c8ac9e0ec3",
    "SEM-RED-ITEM-531300-DC960F-001": "62edb8efd4dba5fad06d1025d28323c01e7f3e3b6f057902d35d7fb524f84075",
    "SEM-RED-ITEM-3606-EA89DA-001": "7268a101af93b55ad6955675ddc81d90df93b1ee2f06070b09893a7dd07ecb96",
    "SEM-RED-ITEM-3607-3DAD95-001": "83ec275b0cbe4a6d06085edaa7e8491bb1e16b95a9dafaa57b327e0063465592",
    "SEM-RED-ITEM-3607-7AFBE8-001": "2c5ff2367500e6d7db7f7f41b98ecfc9d2b419ea0997e69b9d796ba6dfcf5fc9",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _code(card_id: int, guid: str) -> str:
    return f"{card_id}-{guid.upper()}"


def _rule_id(card_id: int, guid: str) -> str:
    return f"SEM-RED-ITEM-{_code(card_id, guid)}-001"


def _physical_kind(disposition: str) -> str:
    if disposition == "included-regular-red-item-face":
        return "regular"
    if disposition == "excluded-heavy-item-face":
        return "heavy"
    return "class-conflict"


def _occurrence(card_id: int, guid: str, disposition: str) -> str:
    code = _code(card_id, guid)
    kind = _physical_kind(disposition)
    if kind == "regular":
        return f"TTS-RED-ITEM-{code}-FACE"
    if kind == "heavy":
        return f"TTS-RED-ITEM-EXCLUDED-HEAVY-{code}-FACE"
    return f"TTS-RED-ITEM-CLASS-CONFLICT-{code}-FACE"


def _source_id(card_id: int, guid: str, disposition: str) -> str:
    code = _code(card_id, guid)
    kind = _physical_kind(disposition)
    if kind == "regular":
        return f"SRC-RED-ITEM-{code}"
    if kind == "heavy":
        return f"SRC-RED-ITEM-EXCLUDED-HEAVY-{code}"
    return f"SRC-RED-ITEM-CLASS-CONFLICT-{code}"


def validate_red_item_family(
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
    heavy = source.get("excludedHeavyFaces") or []
    class_conflicts = source.get("physicalClassConflictFaces") or []
    assets = source.get("sourceFaceAssets") or []
    assets_by_key = {row.get("assetKey"): row for row in assets}
    physical_by_sequence = {row.get("rootSequence"): row for row in [*faces, *heavy, *class_conflicts]}

    if _sha(source_path) != PINNED_RED_ITEM_SOURCE_INDEX_HASH:
        failures.append({"check": "pinned Red Item source index"})
    if source.get("counts") != EXPECTED_RED_ITEM_COUNTS or len(physical_by_sequence) != 30 or sorted(physical_by_sequence) != list(range(1, 31)):
        failures.append({"check": "Red Item source-index exact physical/root/class occurrence count"})
    if set(assets_by_key) != set(EXPECTED_RED_ITEM_ASSETS) or len(assets_by_key) != len(assets):
        failures.append({"check": "Red Item exact source-face asset/variant closure"})

    role_rows = [row for row in roles if row.get("role") == "redItemsDeck"]
    root_object = next((row for row in objects if row.get("guid") == "9027ed"), {})
    child_objects = [row for row in objects if ["Deck", "9027ed", ""] in (row.get("parent") or []) and row.get("gmnotes") == "reditem"]
    expected_children = {(card_id, guid) for _, card_id, guid, _, _, _ in EXPECTED_RED_ITEM_ROOT}
    expected_deck_nums = ["35", "36", "5307", "5308", "5309", "5310", "5311", "5312", "5313", "5314", "5315", "5316", "5438"]
    if (
        len(role_rows) != 1 or role_rows[0].get("guid") != "9027ed" or role_rows[0].get("type") != "Deck"
        or role_rows[0].get("gmnotes") != "reditemDiscard" or role_rows[0].get("n_urls") != 8
        or role_rows[0].get("deck_nums") != expected_deck_nums or root_object.get("type") != "Deck"
        or root_object.get("parent") != [] or len(child_objects) != 30
        or {(int(row["card_id"]), row["guid"]) for row in child_objects} != expected_children
    ):
        failures.append({"check": "Red Item root Lua role/deck/tag/container closure"})

    root = source.get("rootDeckEvidence") or {}
    expected_saved_ids = [row[1] for row in EXPECTED_RED_ITEM_ROOT]
    expected_selectors = [
        {"rootSequence": sequence, "fullCardId": card_id, "guid": guid, "customDeckId": custom_id,
         "batchDisposition": "included-regular" if disposition == "included-regular-red-item-face" else "excluded-heavy" if disposition == "excluded-heavy-item-face" else "class-conflict-excluded"}
        for sequence, card_id, guid, custom_id, _, disposition in EXPECTED_RED_ITEM_ROOT
    ]
    if (
        root.get("sourceId") != "SRC-RED-ITEM-ROOT-DECK" or root.get("ttsRole") != "redItemsDeck"
        or root.get("rootGuid") != "9027ed" or root.get("rawSavePath") != "assets/tts-mod/extract/nemesis_script_mod.bin"
        or root.get("rawSaveSha256") != "8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68"
        or root.get("savedDeckIds") != expected_saved_ids or root.get("fullContainedSelectors") != expected_selectors
        or root.get("rootOrderIsGameplayOrder") is not False or sorted((root.get("customDeckTuples") or {})) != expected_deck_nums
    ):
        failures.append({"check": "Red Item exact raw DeckIDs/full-selector/saved-order lock"})

    expected_titles = {
        "AMMO MAGAZINE": 7, "ANTI-AIRCRAFT\nCODES": 1, "EXPLORING\nDRONE": 2,
        "FLASHBANG": 3, "GRENADE": 5, "PERSONAL\nLOG CODES": 1, "PORTABLE\nBARRIER": 2,
    }
    if source.get("titleMultiplicity") != expected_titles:
        failures.append({"check": "Red Item repeated-title/copy multiplicity no-collapse lock"})

    for asset_key, expected in EXPECTED_RED_ITEM_ASSETS.items():
        path, source_sha, title, source_role, cell, physical_class, selected_disposition, panel_count, sentence_count, icon_refs, text_digest = expected
        asset = assets_by_key.get(asset_key) or {}
        actual = (asset.get("sourcePath"), asset.get("sourceSha256"), asset.get("printedTitle"), asset.get("sourceRole"), asset.get("generatedCell"), asset.get("physicalClass"), asset.get("selectedDisposition"))
        if actual != expected[:7] or not (repo / path).is_file() or _sha(repo / path) != source_sha:
            failures.append({"check": "Red Item independently locked source-face asset tuple", "assetKey": asset_key})
        recomputed_text = _digest({"title": asset.get("printedTitle"), "typeLine": asset.get("typeLine"), "upperRight": asset.get("upperRight"), "body": asset.get("printedBody")})
        if asset.get("printedBodyDigest") != text_digest or recomputed_text != text_digest:
            failures.append({"check": "Red Item exact title/body/punctuation/order lock", "assetKey": asset_key})
        regions = asset.get("regions") or []
        panels = asset.get("panels") or []
        sentences = asset.get("sentences") or []
        icons = asset.get("iconOccurrences") or []
        if [row.get("regionId") for row in regions] != ["R1", "R2", "R3"] or [row.get("role") for row in regions] != ["artwork-and-interface", "identity-trait-and-restriction", "operative-effect-body"]:
            failures.append({"check": "Red Item exact source region/anatomy roles/order", "assetKey": asset_key})
        if len(panels) != panel_count or [row.get("readingOrder") for row in panels] != list(range(1, panel_count + 1)) or asset.get("panelDigest") != _digest(panels):
            failures.append({"check": "Red Item exact source panel roles/order/region linkage", "assetKey": asset_key})
        if len(sentences) != sentence_count or [row.get("sequence") for row in sentences] != list(range(1, sentence_count + 1)):
            failures.append({"check": "Red Item exact printed sentence occurrence count/order", "assetKey": asset_key})
        body = asset.get("printedBody") or ""
        cursor = 0
        for sentence in sentences:
            start, end = sentence.get("start"), sentence.get("end")
            if not isinstance(start, int) or not isinstance(end, int) or start < cursor or body[start:end] != sentence.get("exactText") or sentence.get("panelId") not in {row.get("panelId") for row in panels}:
                failures.append({"check": "Red Item exact sentence span/punctuation/panel lock", "assetKey": asset_key, "sentenceId": sentence.get("sentenceId")})
            cursor = end if isinstance(end, int) else cursor
        if tuple(row.get("semanticReferenceId") for row in icons) != icon_refs or [row.get("sequence") for row in icons] != list(range(1, len(icons) + 1)) or asset.get("iconDigest") != _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in icons]):
            failures.append({"check": "Red Item exact source-local icon occurrence projection", "assetKey": asset_key})
        gap = asset.get("selectorGap")
        selected = selected_disposition in {"included-regular", "excluded-heavy", "class-conflict-excluded"}
        if asset.get("selectedByRootDeck") is not selected or (not selected and (not isinstance(gap, dict) or gap.get("status") != "explicit-no-root-DeckID-GUID-selector" or gap.get("cardIdModuloJoinUsed") is not False)) or (selected and gap is not None):
            failures.append({"check": "Red Item generated selector/selector-gap closure", "assetKey": asset_key})

    expected_backlog_rules: dict[str, list[str]] = {}
    regular_sequence = 0
    for sequence, card_id, guid, custom_id, asset_key, disposition in EXPECTED_RED_ITEM_ROOT:
        row = physical_by_sequence.get(sequence) or {}
        asset = assets_by_key[asset_key]
        kind = _physical_kind(disposition)
        if kind == "regular":
            regular_sequence += 1
        expected_tuple = (sequence, regular_sequence if kind == "regular" else None, card_id, guid, custom_id, asset_key, disposition, _rule_id(card_id, guid) if kind == "regular" else None)
        actual_tuple = (row.get("rootSequence"), row.get("familySequence"), row.get("ttsCardId"), row.get("ttsCardGuid"), row.get("customDeckId"), row.get("sourceAssetKey"), row.get("batchDisposition"), row.get("semanticRuleId"))
        occurrence_id = _occurrence(card_id, guid, disposition)
        if actual_tuple != expected_tuple or row.get("redItemOccurrenceId") != occurrence_id:
            failures.append({"check": "independently locked Red Item physical occurrence crosswalk", "occurrenceId": occurrence_id})
        selector = row.get("sourceSelector") or {}
        expected_back = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235323/E2B2763353C8DD3A6DD329CCEC256500AEF64B8A/" if kind == "class-conflict" else "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235610/413F1511B1E70F81E0F7C17B3F7653DA1631AF3E/"
        actual_selector_tuple = (row.get("sourceId"), row.get("sourcePath"), row.get("sourceSha256"), selector.get("key"), selector.get("fullCardId"), selector.get("guid"), selector.get("parentDeckGuid"), selector.get("customDeckId"), selector.get("backUrl"), selector.get("selectorGap"), selector.get("cardIdModuloJoinUsed"))
        expected_selector_tuple = (_source_id(card_id, guid, disposition), asset.get("sourcePath"), asset.get("sourceSha256"), "FaceURL", card_id, guid, "9027ed", custom_id, expected_back, None, False)
        if actual_selector_tuple != expected_selector_tuple:
            failures.append({
                "check": "Red Item exact CardID/GUID/FaceURL/BackURL selector projection",
                "occurrenceId": occurrence_id,
                "actual": actual_selector_tuple,
                "expected": expected_selector_tuple,
                "elementEqual": [actual == expected for actual, expected in zip(actual_selector_tuple, expected_selector_tuple)],
            })
        expected_cell = EXPECTED_RED_ITEM_ASSETS[asset_key][4]
        if expected_cell is not None:
            expected_sheet = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146.jpg" if custom_id == "35" else "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148.jpg"
            expected_grid = {"columns": 2, "rows": 2} if custom_id == "35" else {"columns": 4, "rows": 2}
            if selector.get("generatedSpriteSheetCell") is not True or selector.get("sourceSheetPath") != expected_sheet or selector.get("sourceSheetGrid") != expected_grid or selector.get("generatedCell") != expected_cell:
                failures.append({"check": "Red Item generated sheet/hash/grid/cell selector projection", "occurrenceId": occurrence_id})
        elif selector.get("generatedSpriteSheetCell") is not False or selector.get("sourceSheetPath") is not None or selector.get("generatedCell") is not None:
            failures.append({"check": "Red Item direct/generated face selector inversion", "occurrenceId": occurrence_id})
        physical_text_digest = _digest({"title": row.get("printedTitle"), "typeLine": row.get("typeLine"), "upperRight": row.get("upperRight"), "body": row.get("printedBody")})
        if (
            row.get("printedBodyDigest") != EXPECTED_RED_ITEM_ASSETS[asset_key][10]
            or physical_text_digest != EXPECTED_RED_ITEM_ASSETS[asset_key][10]
            or len(row.get("panels") or []) != EXPECTED_RED_ITEM_ASSETS[asset_key][7]
            or row.get("panelDigest") != _digest(row.get("panels") or [])
            or len(row.get("sentences") or []) != EXPECTED_RED_ITEM_ASSETS[asset_key][8]
            or tuple(icon.get("semanticReferenceId") for icon in row.get("iconOccurrences") or []) != EXPECTED_RED_ITEM_ASSETS[asset_key][9]
            or row.get("iconDigest") != _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in row.get("iconOccurrences") or []])
        ):
            failures.append({"check": "Red Item exact physical panel/body/icon projection", "occurrenceId": occurrence_id})
        join = row.get("joinEvidence") or {}
        if join.get("identityJoin") != "exact raw root physical occurrence and exact source-asset projection" or any(join.get(key) is not False for key in ("titleOnlyJoin", "colorOnlyJoin", "weaponOrAmmoAppearanceJoin", "bodyResemblanceJoin", "folderOnlyJoin", "sourceOrderOnlyJoin", "generatedCellOnlyJoin", "cardIdModuloJoin", "licensedKeyJoin")):
            failures.append({"check": "Red Item title/color/weapon-art/body/folder/order/cell/modulo/licensed join prohibited", "occurrenceId": occurrence_id})
        registry = source_by_id.get(_source_id(card_id, guid, disposition)) or {}
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId")) != (asset.get("sourcePath"), asset.get("sourceSha256"), occurrence_id):
            failures.append({"check": "Red Item source-registry exact physical tuple", "occurrenceId": occurrence_id})
        backlog_id = "CARD:" + asset["sourceSha256"][:16]
        if row.get("backlogUnitId") != backlog_id:
            failures.append({"check": "Red Item exact backlog tuple projection", "occurrenceId": occurrence_id})
        if kind == "regular":
            expected_backlog_rules.setdefault(backlog_id, []).append(_rule_id(card_id, guid))
        elif (backlog_by_id.get(backlog_id) or {}).get("status") != "pending" or row.get("semanticRuleId") is not None:
            failures.append({"check": "Red Item regular/Heavy/class-conflict leakage", "occurrenceId": occurrence_id})

    for asset_key in ("red-sheet-00", "red-sheet-02", "red-sheet-03", "red-sheet-05"):
        asset = assets_by_key[asset_key]
        expected_backlog_rules["CARD:" + asset["sourceSha256"][:16]] = ["SEM-RED-ITEM-VARIANT-BOUNDARIES-001"]
    for backlog_id, rule_ids in expected_backlog_rules.items():
        backlog = backlog_by_id.get(backlog_id) or {}
        asset = next(item for item in assets if "CARD:" + item["sourceSha256"][:16] == backlog_id)
        if backlog.get("sourcePath") != asset.get("sourcePath") or backlog.get("sourceLocator") != asset.get("sourceSha256") or backlog.get("pilotRuleIds") != rule_ids or backlog.get("status") != "pilot-covered":
            failures.append({"check": "Red Item exact backlog tuple projection", "backlogUnitId": backlog_id})

    sheets = source.get("sourceSheets") or []
    backs = source.get("rootBacks") or []
    expected_sheets = [
        ("SRC-RED-ITEM-SHEET-36", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148.jpg", "8658b7bf1c82e78e4c916bd70e6e02627f2f0b7ced4d788850e514346911c78e", [1, 4, 6, 7], [0, 2, 3, 5]),
        ("SRC-RED-ITEM-CROSS-FAMILY-SHEET-35", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146.jpg", "d71c7a4ad3490071787104e2cec054d4fc4f00ac7d15232c45b570aefe57d591", [0], [1, 2, 3]),
    ]
    actual_sheets = [(row.get("sourceId"), row.get("sourcePath"), row.get("sourceSha256"), row.get("rootSelectedCells") or row.get("redRootSelectedCells"), row.get("selectorGapCells") or row.get("crossFamilySelectorGapCells")) for row in sheets]
    expected_backs = [
        ("SRC-RED-ITEM-BACK", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-147.jpg", "7be0b51d4a87f7a9c2d5e6dc3d3f5eae3d33afeb1fa6fff3d552c0f444d921cb", 24, 25),
        ("SRC-RED-ITEM-CROSS-FAMILY-YELLOW-BACK", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-143.jpg", "4a4be058786fcf3e2195ef66a4052ebbf721946ed5d4b4bb3b624f3c4d5fbf6a", 6, 13),
    ]
    actual_backs = [(row.get("sourceId"), row.get("sourcePath"), row.get("sourceSha256"), row.get("rootPhysicalSelectors"), row.get("globalSelectorReferences")) for row in backs]
    if actual_sheets != expected_sheets or actual_backs != expected_backs or any(row.get("separateRulesFace") is not False for row in [*sheets, *backs]):
        failures.append({"check": "Red Item parent-sheet/back/selector-gap closure"})

    licensed = source.get("licensedDigitalOccurrences") or []
    expected_bga = [("Ammo", 7, False), ("AntiaircraftCodes", 1, False), ("ExploringDrone", 2, False), ("Flashbang", 3, False), ("Grenade", 5, False), ("MilitaryTaser", 6, True), ("PersonalLogCodes", 1, False), ("PortableBarrier", 2, False), ("RemoteDetonator", 3, True)]
    items_table = next((row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row.get("name") == "ITEMS_DATA"), {})
    if [(row.get("key"), row.get("nbr"), row.get("heavy")) for row in licensed] != expected_bga or items_table.get("count") != 57 or any(row.get("sourceBlockText") not in bga_text or row.get("identityCrosswalkStatus") != "independent licensed occurrence; no TTS/official physical identity join asserted" for row in licensed) or sum(row.get("nbr", 0) for row in licensed) != 30 or sum(row.get("nbr", 0) for row in licensed if not row.get("heavy") and not row.get("armor")) != 21 or sum(row.get("nbr", 0) for row in licensed if row.get("heavy") or row.get("armor")) != 9:
        failures.append({"check": "Red Item licensed independent rows/30-21-9/no-crosswalk closure"})

    official = source.get("officialVisibleCounterparts") or []
    expected_official_ids = ["RB-P03-V01", "RB-P05-V01", "RB-P09-V01", "RB-P12-V02", "RB-P16-V02", "RB-P16-V03", "RB-P17-V01", "RB-P28-V02", "RB-P28-V03", "RB-P29-V01", "RB-P29-V03", "RB-P33-V03", "RB-P37-V02", "RB-P40-V02"]
    faq = source.get("faqSearchClosure") or {}
    if [row.get("sourceOccurrenceId") for row in official] != expected_official_ids or any(row.get("exactTtsPhysicalCrosswalk") is not False for row in official) or [row.get("sourceUnitId") for row in faq.get("baseApplicableOccurrences") or []] != ["FQ-P02-U04", "FQ-P02-U10", "FQ-P03-U04", "FQ-P03-U06", "FQ-P03-U07", "FQ-P03-U08"] or len(faq.get("excludedExpansionOccurrences") or []) != 4:
        failures.append({"check": "Red Item official/FAQ authority and occurrence closure"})

    backlog_ledger = (source.get("familyCountEvidence", {}).get("backlog") or {})
    linked_ids = backlog_ledger.get("linkedUnitIds") or []
    if (
        backlog_ledger.get("faceTupleCount") != 7 or backlog_ledger.get("variantTupleCount") != 4
        or backlog_ledger.get("physicalFaceLinkCount") != 21 or backlog_ledger.get("obligationCount") != 43 or len(linked_ids) != 43
        or any((backlog_by_id.get(unit_id) or {}).get("status") != "pilot-covered" for unit_id in linked_ids)
        or backlog_ledger.get("crossFamilyPendingUnitIds") != ["CARD:326e23792c922ed0"]
        or backlog_ledger.get("crossFamilyCoveredByYellowUnitIds") != ["CARD:6dc2643df6e90da0"]
        or (backlog_by_id.get("CARD:326e23792c922ed0") or {}).get("status") != "pending"
        or (backlog_by_id.get("CARD:6dc2643df6e90da0") or {}).get("status") != "pilot-covered"
    ):
        failures.append({"check": "Red Item exact overlapping backlog-obligation closure"})

    expected_rule_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, _, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face"]
    actual_rule_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r"SEM-RED-ITEM-\d+-[A-Z0-9]+-001", rule_id)}
    if actual_rule_ids != set(expected_rule_ids):
        failures.append({"check": "Red Item semantic physical face-record closure", "missing": sorted(set(expected_rule_ids) - actual_rule_ids), "extra": sorted(actual_rule_ids - set(expected_rule_ids))})

    expected_questions_by_asset = {
        "direct-ammo": ["SEM-Q-044", "SEM-Q-045"],
        "red-sheet-01": ["SEM-Q-046"],
        "direct-exploring": ["SEM-Q-048"],
        "red-sheet-04": ["SEM-Q-002"],
        "direct-grenade": ["SEM-Q-044", "SEM-Q-045"],
        "red-sheet-06": ["SEM-Q-046", "SEM-Q-049"],
        "red-sheet-07": ["SEM-Q-046", "SEM-Q-050"],
    }
    for sequence, card_id, guid, _, asset_key, disposition in EXPECTED_RED_ITEM_ROOT:
        if disposition != "included-regular-red-item-face":
            continue
        occurrence_id = _occurrence(card_id, guid, disposition)
        source_face = physical_by_sequence.get(sequence) or {}
        rule = record_by_id.get(_rule_id(card_id, guid)) or {}
        assertions = {row.get("assertionId"): row for row in rule.get("sourceAssertions") or []}
        scan = assertions.get(f"SA-RIF-{_code(card_id, guid)}-SCAN") or {}
        if (scan.get("sourceId"), scan.get("sourceSha256"), scan.get("sourceText"), scan.get("textKind")) != (_source_id(card_id, guid, disposition), EXPECTED_RED_ITEM_ASSETS[asset_key][1], source_face.get("printedBody"), "verbatim") or rule.get("authority", {}).get("highest") != "official-primary" or rule.get("sourceVariants") != []:
            failures.append({"check": "Red Item face exact scan/general/authority/no-variant projection", "occurrenceId": occurrence_id})
        expected_questions = expected_questions_by_asset[asset_key]
        if rule.get("unresolvedQuestionRefs") != expected_questions or rule.get("status") != ("source-backed-with-open-question" if expected_questions else "source-backed"):
            failures.append({"check": "Red Item face exact optionality/owner/no-default question projection", "occurrenceId": occurrence_id})
        sentence_ids = {row.get("sentenceId") for row in source_face.get("sentences") or []}
        panel_ids = {row.get("panelId") for row in source_face.get("panels") or []}
        region_ids = {row.get("regionId") for row in source_face.get("regions") or []}
        operations = rule.get("operations") or []
        if not operations or any(op.get("sourceSentenceId") not in sentence_ids or op.get("sourcePanelId") not in panel_ids or op.get("sourceRegionId") not in region_ids for op in operations):
            failures.append({"check": "Red Item face operation-to-sentence/panel/region closure", "occurrenceId": occurrence_id})
        if "same title/body/multiplicity creates no identity or stacking key" not in rule.get("stacking", {}).get("policy", ""):
            failures.append({"check": "Red Item physical-copy/no-title stacking lock", "occurrenceId": occurrence_id})
        if asset_key in {"red-sheet-01", "red-sheet-06", "red-sheet-07"}:
            inferred_terms = {"icon.notInCombat", "icon.ammoToken", "icon.grenadeToken", "icon.shootDieAmmoLoss", "icon.shootDieCritical", "term.weapon"}
            if inferred_terms.intersection(rule.get("termRefs", [])) or "SEM-Q-046" not in rule.get("unresolvedQuestionRefs", []) or not any(op.get("operationType") == "resolve-open-alternative" and "SEM-Q-046" in op.get("objectRef", "") for op in operations):
                failures.append({"check": "Red Item local glyph no-default/no-weapon-ammo inference lock", "occurrenceId": occurrence_id})

    use = record_by_id.get("SEM-USE-ITEM-001") or {}
    use_ops = use.get("operations") or []
    use_dispatch = next((op.get("dispatchRuleIds") for op in use_ops if op.get("stepId") == "S05"), None)
    lifecycle_dispatch = next((op.get("dispatchRuleIds") for op in use_ops if op.get("stepId") == "S06"), None)
    if not use_dispatch or use_dispatch[-45:-24] != expected_rule_ids or lifecycle_dispatch != ["SEM-GREEN-ITEM-ONE-USE-001", "SEM-RED-ITEM-ONE-USE-001", "SEM-YELLOW-ITEM-ONE-USE-001"] or [op.get("operationType") for op in use_ops] != ["select-target", "resolve-open-alternative", "pay-cost", "reveal", "invoke-selected-process", "invoke-selected-process"] or use.get("unresolvedQuestionRefs") != ["SEM-Q-039"]:
        failures.append({"check": "Red Item shared Use/payment/reveal/dispatch/lifecycle lock"})
    trade = record_by_id.get("SEM-ITEM-TRADE-GAIN-001") or {}
    trade_dispatch = (trade.get("operations") or [{}])[-1].get("dispatchRuleIds")
    tactical = record_by_id.get("SEM-ACT-TACTICAL-001") or {}
    if trade_dispatch != ["SEM-GREEN-ITEM-IMMEDIATE-USE-001", "SEM-RED-ITEM-IMMEDIATE-USE-001", "SEM-YELLOW-ITEM-IMMEDIATE-USE-001"] or tactical.get("authority", {}).get("highest") != "official-errata" or not any(row.get("selectionMode") == "player-choice-sequential" for row in tactical.get("decisions") or []) or "one selected token at a time" not in json.dumps(tactical, ensure_ascii=False):
        failures.append({"check": "Red Item Trade/immediate and Tactical Gear sequential reuse lock"})

    deck = record_by_id.get("SEM-RED-ITEM-DECK-001") or {}
    deck_ops = deck.get("operations") or []
    one_use = record_by_id.get("SEM-RED-ITEM-ONE-USE-001") or {}
    immediate = record_by_id.get("SEM-RED-ITEM-IMMEDIATE-USE-001") or {}
    ammo = record_by_id.get("SEM-AMMO-TOKEN-LIFECYCLE-001") or {}
    grenade = record_by_id.get("SEM-GRENADE-TOKEN-EFFECT-001") or {}
    anti = record_by_id.get("SEM-ANTI-AIRCRAFT-TOKEN-STATE-001") or {}
    if [op.get("operationType") for op in deck_ops] != ["shuffle", "transition-zone", "set-state", "evaluate-condition", "resolve-open-alternative", "draw-random", "resolve-open-alternative", "evaluate-condition"] or (deck_ops[0].get("repeat") or {}) != {"rootPhysicalCardCount": 30, "regularBatchFaceCount": 21, "excludedHeavyCount": 3, "physicalClassConflictCount": 6} or deck.get("unresolvedQuestionRefs") != ["SEM-Q-040", "SEM-Q-047"] or any(op.get("operationType") == "shuffle" and "discard" in op.get("objectRef", "").lower() for op in deck_ops[1:]):
        failures.append({"check": "Red Item lifecycle/stacking/reshuffle lock"})
    if [op.get("operationType") for op in one_use.get("operations") or []] != ["resolve-open-alternative", "transition-zone", "evaluate-condition"] or (one_use.get("operations") or [{}, {}])[1].get("transition", {}).get("to") != "tax.scaffold.zone.discard-pile" or one_use.get("unresolvedQuestionRefs") != ["SEM-Q-039"]:
        failures.append({"check": "Red Item One Use discard/no-return order lock"})
    if (immediate.get("decisions") or [{}])[0].get("cardinality") != {"min": 0, "max": 1} or (immediate.get("decisions") or [{}])[0].get("declineAllowed") is not True or immediate.get("unresolvedQuestionRefs") != ["SEM-Q-045"]:
        failures.append({"check": "Red Item immediate optionality/multi-window lock"})
    ammo_types = [op.get("operationType") for op in ammo.get("operations") or []]
    if ammo_types != ["select-target", "transition-zone", "evaluate-condition", "set-state", "transition-zone"] or "Full Ammo token becomes Half-full" not in json.dumps(ammo) or "loaded Ammo cannot be moved" not in json.dumps(ammo):
        failures.append({"check": "Red Item Ammo reload/full-half/discard lifecycle lock"})
    grenade_types = [op.get("operationType") for op in grenade.get("operations") or []]
    if grenade_types != ["select-target", "draw-random", "change-value", "change-value", "evaluate-condition"] or (grenade.get("authority") or {}).get("highest") != "official-errata" or "numeric Burst result plus 2" not in json.dumps(grenade) or "not a Burst Action" not in json.dumps(grenade):
        failures.append({"check": "Red Item Grenade target/+2/special/no-Burst inference lock"})
    if [op.get("operationType") for op in anti.get("operations") or []] != ["shuffle", "set-state", "inspect-private", "choose", "set-state", "inspect-private", "transition-zone", "place-component", "transition-zone"] or "may be lies" not in json.dumps(anti) or "cannot be shown" not in json.dumps(anti) or (anti.get("decisions") or [{}])[0].get("options") != ["ACTIVE above INACTIVE", "INACTIVE above ACTIVE"]:
        failures.append({"check": "Red Item Anti-Aircraft private-order/show/lie/lifecycle lock"})

    variant = record_by_id.get("SEM-RED-ITEM-VARIANT-BOUNDARIES-001") or {}
    if variant.get("status") != "source-variant" or variant.get("unresolvedQuestionRefs") != [] or len(variant.get("sourceVariants") or []) != 25 or len(variant.get("sourceAssertions") or []) != 18 or len(variant.get("operations") or []) != 27 or any(row.get("sourceAssertionId") not in {item.get("assertionId") for item in variant.get("sourceAssertions") or []} for row in variant.get("sourceVariants") or []) or "no title, Red color, weapon/ammo art" not in (variant.get("operations") or [{}])[-1].get("objectRef", ""):
        failures.append({"check": "Red Item variant/authority closure"})

    expected_question_blocks = {
        "SEM-Q-046": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset in {"red-sheet-01", "red-sheet-06", "red-sheet-07"}],
        "SEM-Q-047": ["SEM-RED-ITEM-DECK-001"],
        "SEM-Q-048": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset == "direct-exploring"],
        "SEM-Q-049": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset == "red-sheet-06"],
        "SEM-Q-050": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset == "red-sheet-07"],
    }
    for question_id, blocks in expected_question_blocks.items():
        question = question_by_id.get(question_id) or {}
        if question.get("defaultProhibited") is not True or question.get("blocksRuleIds") != blocks or len(question.get("alternatives") or []) != 3:
            failures.append({"check": "Red Item ambiguity no-default alternatives/linkage", "questionId": question_id})
    expected_combined_suffixes = {
        "SEM-Q-039": ["SEM-RED-ITEM-ONE-USE-001"],
        "SEM-Q-040": ["SEM-RED-ITEM-DECK-001"],
        "SEM-Q-044": [
            *[_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset == "direct-ammo"],
            *[_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset == "direct-grenade"],
        ],
        "SEM-Q-045": [
            "SEM-RED-ITEM-IMMEDIATE-USE-001",
            *[_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_RED_ITEM_ROOT if disposition == "included-regular-red-item-face" and asset in {"direct-ammo", "direct-grenade"}],
        ],
    }
    for question_id, suffix in expected_combined_suffixes.items():
        question = question_by_id.get(question_id) or {}
        actual_blocks = question.get("blocksRuleIds") or []
        filtered = [rule_id for rule_id in actual_blocks if rule_id in set(suffix)]
        if question.get("defaultProhibited") is not True or filtered != suffix or len(question.get("alternatives") or []) != 3:
            failures.append({"check": "Red Item shared ambiguity no-default family linkage", "questionId": question_id})

    red_conflicts = {row.get("conflictId"): row for row in conflict_rows if row.get("conflictId") in {f"SC-{index:03d}" for index in range(34, 41)}}
    if set(red_conflicts) != {f"SC-{index:03d}" for index in range(34, 41)} or [red_conflicts[f"SC-{index:03d}"].get("status") for index in range(34, 41)] != ["unresolved", "unresolved", "preserved-boundary", "unresolved", "unresolved", "preserved-boundary", "preserved-boundary"] or [red_conflicts[f"SC-{index:03d}"].get("questionId") for index in (34, 35, 37, 38)] != ["SEM-Q-047", "SEM-Q-046", "SEM-Q-050", "SEM-Q-049"]:
        failures.append({"check": "Red Item source-variant authority/conflict closure"})

    if EXPECTED_RED_ITEM_RECORD_DIGESTS:
        for rule_id, expected_digest in EXPECTED_RED_ITEM_RECORD_DIGESTS.items():
            item = record_by_id.get(rule_id)
            if item is None or _digest(item) != expected_digest:
                failures.append({"check": "independently locked Red Item semantic projection", "ruleId": rule_id})

    system = next((row for row in coverage.get("systems") or [] if row.get("system") == "base source-clear regular Red Item card/component family"), {})
    expected_system_ids = [*EXPECTED_RED_ITEM_REUSABLE_RULE_IDS, *expected_rule_ids]
    not_yet = " ".join(coverage.get("notYetCovered") or [])
    if system.get("ruleIds") != expected_system_ids or "21-occurrence source-clear regular Red Item" not in not_yet or "three explicit Heavy Red occurrences" not in not_yet or "six Military Taser Red class-conflict occurrences" not in not_yet:
        failures.append({"check": "Red Item coverage/class-boundary/no-full-coverage claim"})

    return {
        "rows": faces,
        "heavy": heavy,
        "classConflicts": class_conflicts,
        "assets": assets,
        "licensed": licensed,
        "official": official,
        "actualRuleIds": actual_rule_ids,
        "expectedBacklogRules": expected_backlog_rules,
    }
