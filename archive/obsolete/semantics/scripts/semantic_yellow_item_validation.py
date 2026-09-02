from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re


PINNED_YELLOW_ITEM_SOURCE_INDEX_HASH = "7e49fdee1d324b2ff2384828c2ed82d941686f976d39043ff03f9aa920bde43b"

EXPECTED_YELLOW_ITEM_COUNTS = {
    "rootPhysicalOccurrences": 30,
    "regularPhysicalFaceOccurrences": 24,
    "explicitHeavyPhysicalOccurrences": 0,
    "physicalClassConflictOccurrences": 6,
    "currentLicensedHeavyAggregate": 6,
    "uniqueRegularPrintedTitles": 4,
    "uniqueSelectedRegularFaceAssets": 4,
    "sourceFaceAssets": 11,
    "rulesBearingSourceFaceAssets": 10,
    "nonRulesSourceCells": 1,
    "generatedRegularPhysicalFaceOccurrences": 11,
    "directRegularPhysicalFaceOccurrences": 13,
    "generatedClassConflictPhysicalOccurrences": 5,
    "directClassConflictPhysicalOccurrences": 1,
    "sourceSheets": 2,
    "sourceSheetCells": 8,
    "selectedGeneratedCells": 3,
    "selectorGapCells": 5,
    "rulesBearingSelectorGapCells": 4,
    "sameFamilySelectorGapCells": 3,
    "crossFamilySelectorGapCells": 1,
    "nonRulesSelectorGapCells": 1,
    "rootBackAssets": 2,
    "sharedBackPhysicalSelectors": 25,
    "uniqueBackSheetPhysicalSelectors": 5,
    "sharedBackGlobalSelectorReferences": 26,
    "uniqueBackSheetGlobalSelectorReferences": 13,
    "sheet33GlobalSelectorReferences": 13,
    "sheet34GlobalSelectorReferences": 12,
    "rootCustomDeckEntries": 5,
    "physicalRegions": 72,
    "operativeRegions": 48,
    "physicalPanels": 128,
    "operativePanels": 104,
    "oneUseHeadingOccurrences": 24,
    "specialWeaponHeadingOccurrences": 8,
    "branchSeparatorHeadingOccurrences": 24,
    "useDiscardPassiveReactionHeadingOccurrences": 0,
    "printedSentenceOccurrences": 56,
    "physicalFunctionalIconOccurrences": 48,
    "physicalMatchedIconOccurrences": 32,
    "physicalUnresolvedLocalGlyphOccurrences": 16,
    "rootPhysicalRegions": 90,
    "rootOperativeRegions": 60,
    "rootPhysicalPanels": 158,
    "rootOperativePanels": 128,
    "rootPrintedSentenceOccurrences": 68,
    "rootFunctionalIconOccurrences": 60,
    "rootMatchedIconOccurrences": 44,
    "rootUnresolvedLocalGlyphOccurrences": 16,
    "classConflictPhysicalPanels": 30,
    "classConflictOperativePanels": 24,
    "classConflictPrintedSentenceOccurrences": 12,
    "sameFamilyGapFunctionalIconOccurrences": 8,
    "sameFamilyGapMatchedIconOccurrences": 6,
    "sameFamilyGapUnresolvedLocalGlyphOccurrences": 2,
    "sameFamilyGapPhysicalPanels": 16,
    "sameFamilyGapPrintedSentenceOccurrences": 7,
    "crossFamilyGapFunctionalIconOccurrences": 2,
    "crossFamilyGapMatchedIconOccurrences": 1,
    "crossFamilyGapUnresolvedLocalGlyphOccurrences": 1,
    "crossFamilyGapPhysicalPanels": 5,
    "crossFamilyGapPrintedSentenceOccurrences": 2,
    "nonRulesGapPhysicalPanels": 2,
    "classConflictFunctionalIconOccurrences": 12,
    "classConflictMatchedIconOccurrences": 12,
    "classConflictUnresolvedLocalGlyphOccurrences": 0,
    "licensedDigitalOccurrences": 6,
    "licensedDigitalPhysicalCopies": 30,
    "licensedRegularOccurrences": 4,
    "licensedRegularPhysicalCopies": 24,
    "licensedHeavyOccurrences": 2,
    "licensedHeavyPhysicalCopies": 6,
    "officialInventoryCopiesPerType": 30,
    "officialVisibleRegularFaceOccurrences": 1,
    "officialVisibleHeavySameTitleOccurrences": 0,
    "officialVisibleBackOccurrences": 0,
    "officialFamilyVisualOccurrences": 15,
    "baseApplicableFaqOccurrences": 6,
    "excludedExpansionFaqOccurrences": 9,
    "backlogTuples": 7,
    "backlogPhysicalFaceLinks": 24,
    "backlogObligationsLinked": 38,
    "semanticPhysicalFaceRecords": 24,
}

# root sequence, full CardID, GUID, CustomDeck ID, source asset, disposition
EXPECTED_YELLOW_ITEM_ROOT = [
    (1, 531800, "1b4ba6", "5318", "direct-robot", "excluded-physical-class-conflict"),
    (2, 3301, "17ccd0", "33", "sheet33-01", "excluded-physical-class-conflict"),
    (3, 3301, "c76308", "33", "sheet33-01", "excluded-physical-class-conflict"),
    (4, 3301, "e7f4f9", "33", "sheet33-01", "excluded-physical-class-conflict"),
    (5, 3301, "f2016c", "33", "sheet33-01", "excluded-physical-class-conflict"),
    (6, 3301, "afbd16", "33", "sheet33-01", "excluded-physical-class-conflict"),
    (7, 3403, "2171b1", "34", "sheet34-03", "included-regular-yellow-item-face"),
    (8, 3403, "41a9c1", "34", "sheet34-03", "included-regular-yellow-item-face"),
    (9, 3403, "f456c3", "34", "sheet34-03", "included-regular-yellow-item-face"),
    (10, 3403, "4efd6d", "34", "sheet34-03", "included-regular-yellow-item-face"),
    (11, 3403, "9d4208", "34", "sheet34-03", "included-regular-yellow-item-face"),
    (12, 3403, "d2ecec", "34", "sheet34-03", "included-regular-yellow-item-face"),
    (13, 395400, "6a29b0", "3954", "direct-phosphates", "included-regular-yellow-item-face"),
    (14, 395400, "0b949c", "3954", "direct-phosphates", "included-regular-yellow-item-face"),
    (15, 395400, "8f66f9", "3954", "direct-phosphates", "included-regular-yellow-item-face"),
    (16, 395400, "11861a", "3954", "direct-phosphates", "included-regular-yellow-item-face"),
    (17, 395400, "988612", "3954", "direct-phosphates", "included-regular-yellow-item-face"),
    (18, 532000, "ce55d9", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (19, 532000, "45f0f3", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (20, 532000, "28907a", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (21, 532000, "8a4908", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (22, 532000, "490933", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (23, 532000, "1ff6e7", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (24, 532000, "5db915", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (25, 532000, "ce5897", "5320", "direct-oxygen", "included-regular-yellow-item-face"),
    (26, 3400, "801470", "34", "sheet34-00", "included-regular-yellow-item-face"),
    (27, 3400, "a29f14", "34", "sheet34-00", "included-regular-yellow-item-face"),
    (28, 3400, "2284bd", "34", "sheet34-00", "included-regular-yellow-item-face"),
    (29, 3400, "534b88", "34", "sheet34-00", "included-regular-yellow-item-face"),
    (30, 3400, "bea081", "34", "sheet34-00", "included-regular-yellow-item-face"),
]

# path, sha, title, source role, cell, physical class, disposition,
# panel count, sentence count, ordered semantic icon refs, composite text digest
EXPECTED_YELLOW_ITEM_ASSETS = {
    "direct-phosphates": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-021.png", "2bf928289b335e659782c1a988d882b2a2ad2ffe98c2693c09d7ced40f5b23f9", "PHOSPHATES", "direct-regular-face", None, "regular-item", "included-regular", 5, 2, (None, "icon.fire"), "a19458260f2393885a7eb5381f8886edd0330f7b2e2d4b5253df7294d664d8b4"),
    "direct-oxygen": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-050.png", "1b05382453304c010a438486105a4e49a4a4f0ed6f8a86576bbd446014fc1e01", "OXYGEN TANK", "direct-regular-face", None, "regular-item", "included-regular", 6, 3, ("icon.oxygen", "icon.oxygenToken"), "12f7ec59c3da6cd128aa3a1121a9328fb36172ebcae6d8acbf7c96b8f7217899"),
    "direct-robot": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-097.png", "6ee5fca639bdfe5d1ac17877ecbb5fd6bf4dc19d1e17786200123fad17b8a6ff", "ROBOT CONTROLLER", "direct-physical-class-conflict", None, "source-conflicted-portrait-item-versus-licensed-heavy", "class-conflict-excluded", 5, 2, ("icon.notInCombat", "icon.robot"), "0fd9387cbb62a4f5b3c60b9c1c7269e843c8d05e919de60e299173a7956fdc2f"),
    "sheet34-00": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-00.png", "2a1f1d0a0fd3b20522cb04489d624d35a69e5e240ec4c3e768bd705271f442f2", "DUCT TAPE", "generated-cell-regular-face", 0, "regular-item", "included-regular", 5, 2, (None, "icon.malfunction"), "d52bf68e0a6e4c321aa8cc8c34f2862e679065d983856df4f120716d2bcca7bd"),
    "sheet34-01": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-01.png", "d8743d650f3ef84d2473128298e8a870b947279d6ac77ed80905a64f25464bfd", "OXYGEN TANK", "generated-cell-selector-gap-variant", 1, "regular-item", "yellow-selector-gap", 6, 3, ("icon.notInCombat", "icon.oxygen", "icon.oxygenToken"), "a72954a8a68b44532e8d46f327fe793f19ace7cff35b989ef4e8a295296004c1"),
    "sheet34-02": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-02.png", "287cc86522b32aac0bb0e06fcab5f3c2db09012893c323e589afe79925cff4a3", "PHOSPHATES", "generated-cell-selector-gap-variant", 2, "regular-item", "yellow-selector-gap", 5, 2, (None, "icon.secure"), "89270c0c8ac95d5b7f030090f05af5e5c22cf034ecf3762971e265ec7c1782e4"),
    "sheet34-03": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-03.png", "7bf955ec7367f7242814ff9bd7c669b8c4e8b5b316bb6b281f59b6f2f3594253", "TOOLS", "generated-cell-regular-face", 3, "regular-item", "included-regular", 5, 2, (None, "icon.malfunction"), "7db780884839c9a4b54ddd08ee3a7538712c0c93f426e3ecd28d9a1fb76c6189"),
    "sheet33-00": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-00.png", "41183eb8c34b083a45ccebaab4428902aaba2e8b2d1cceb168f2f2d99880fa0d", "MILITARY TASER", "generated-cell-cross-family-selector-gap", 0, "cross-family-red-class-conflict", "cross-family-gap-excluded", 5, 2, ("icon.intruder", None), "cdc24ff4f065ad649e9d7d266a33b0dfe2cc62d9e4c5e2cffe986c4a9e553cf2"),
    "sheet33-01": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-01.png", "326e23792c922ed04dd2d52ebf272c83d4cf8840cfc752b1b7d8cce136a50bea", "FIRE EXTINGUISHER", "generated-cell-physical-class-conflict", 1, "source-conflicted-portrait-special-weapon-versus-licensed-heavy", "class-conflict-excluded", 5, 2, ("icon.fire", "icon.intruder"), "f7fed2bc2b55c6b21bb7bacd8257c4c53fb9d8010c2a1b4a265431822e0b2765"),
    "sheet33-02": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-02.png", "6dc2643df6e90da076d79f330df888f4264607d560d367df8a89f57256eaadac", "ROBOT CONTROLLER", "generated-cell-selector-gap-variant", 2, "source-conflicted-portrait-item-versus-licensed-heavy", "yellow-selector-gap", 5, 2, (None, "icon.robot", "icon.robot"), "002d38c4df5b672223a65d4f83b78ccc1307d3bc3929a36565b4cdc6601ce411"),
    "sheet33-03": ("assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-03.png", "77223a77d61181cd144bd508dfcbfe91e135e093395d15e8b9957ce51669d8c4", "", "generated-cell-non-rules-selector-gap", 3, "non-rules-placeholder-cell", "non-rules-gap-excluded", 2, 0, (), "ba2aff362390241ac3f717eaf5641f75aade976372881087589497041efd1cc2"),
}

EXPECTED_YELLOW_ITEM_REUSABLE_RULE_IDS = [
    "SEM-YELLOW-ITEM-DECK-001", "SEM-YELLOW-ITEM-ONE-USE-001", "SEM-YELLOW-ITEM-IMMEDIATE-USE-001",
    "SEM-GAIN-OXYGEN-001", "SEM-OXYGEN-TOKEN-EFFECT-001", "SEM-DISCARD-MALFUNCTION-001",
    "SEM-REINFORCE-CORRIDOR-001", "SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001",
]

EXPECTED_YELLOW_ITEM_RECORD_DIGESTS: dict[str, str] = {
    "SEM-DISCARD-MALFUNCTION-001": "a2fa3e42fe7840d306d2136513da7e1ff67be44fa02b4cee0bd19ead4c24fb0d",
    "SEM-GAIN-OXYGEN-001": "1aeed66ceef256849e8e5ca3e6fe64887354350287c4afbe1f1f49f1689d2ce7",
    "SEM-ITEM-TRADE-GAIN-001": "0ca46870c3dff50cf649d74724bd41087382bb80955eda32a0bb08d92f5eff9a",
    "SEM-OXYGEN-TOKEN-EFFECT-001": "b3fba8c31096e1a12108d340c007b429c6e262fe2f28a68960b29b421c513676",
    "SEM-REINFORCE-CORRIDOR-001": "3ab842aa01a28b4f6d7cbd1c28f49934ff0c7dd6f792fe42cac194d4fa2e8b61",
    "SEM-USE-ITEM-001": "34b9b0c38b32a6c77cbb30f9c2c3649318e115a3de654c4a29214fb39e77ff14",
    "SEM-YELLOW-ITEM-3400-2284BD-001": "afd73e98ec742c358725bae2e4793e71e8954f9bb8d592ba7c8163eb16fdd0cd",
    "SEM-YELLOW-ITEM-3400-534B88-001": "6b95fa099a7480bcd060aa661d93bf5a074d9f489caf4813f604dc53a09dd9fd",
    "SEM-YELLOW-ITEM-3400-801470-001": "c3ca425bda531f5f464da8c8ec4e1aeb79a2f3ffed15338c2da71aa359002fea",
    "SEM-YELLOW-ITEM-3400-A29F14-001": "fd06d31446b5c7b55697a8877c2728ad83b093d209fe934877075cbf65f62d91",
    "SEM-YELLOW-ITEM-3400-BEA081-001": "9f067a2a7d7bca59e7225bb881c9f7085ddf2344432e73afcfc95b524d2bd79d",
    "SEM-YELLOW-ITEM-3403-2171B1-001": "aef55378dfecc9d051c289b25974f230160ae7b7f42156936e52fffbae75e64c",
    "SEM-YELLOW-ITEM-3403-41A9C1-001": "22182c4a89d058600f3d5a24aaad02cf617582440986ff6bda9b79a823f9e2b6",
    "SEM-YELLOW-ITEM-3403-4EFD6D-001": "1d74554f0c084f19284702325aa7d770c7a2eb046d3eb12d5420a7549064feab",
    "SEM-YELLOW-ITEM-3403-9D4208-001": "c9cd9543d4e5e9bac4f01b061f08ba84c94a209d324a139d208fd2d46866b9b7",
    "SEM-YELLOW-ITEM-3403-D2ECEC-001": "d0a91dc4c64b8d2010513b3c71d113ae2f7ac8f8737c2815eeaf95136f730445",
    "SEM-YELLOW-ITEM-3403-F456C3-001": "213f802355e9e341ebb4a9425f1c4a60b5251af107dc683b4ffb590e0232aba0",
    "SEM-YELLOW-ITEM-395400-0B949C-001": "95c94ef8ede8e402c37367ba8027eca54d4432213c8edb4c6ff8ee4fc7553f2b",
    "SEM-YELLOW-ITEM-395400-11861A-001": "25d592649a43d04af8dc62aaad9d7b97df6566dad182968e2cf1e94d55dcc105",
    "SEM-YELLOW-ITEM-395400-6A29B0-001": "6f9243dcdc645bf323673cbfc147fd9fda0d1d77445c3abb37e3381c1df4ea2d",
    "SEM-YELLOW-ITEM-395400-8F66F9-001": "ba6f5bf9e08c308e1e8710a1c5036e49b04ef2bc75a855790b8f5eace8df60a8",
    "SEM-YELLOW-ITEM-395400-988612-001": "ce5748f68ff08c32edc45773884b19fe522a5837ae5177a8617120f56d8a3551",
    "SEM-YELLOW-ITEM-532000-1FF6E7-001": "3871a7434942b30051b5674d9eda69de48264e3dba13401a79237ef4d9f1c591",
    "SEM-YELLOW-ITEM-532000-28907A-001": "ec23e465dd0e6372f1ae85147723ce244040a75113e255d9a3fbdb68b9ee0d04",
    "SEM-YELLOW-ITEM-532000-45F0F3-001": "7f7558d94babcd498d1e23387cb352f1f57a4c78af2904195856b2e868b08cad",
    "SEM-YELLOW-ITEM-532000-490933-001": "4579f9bd5bdaaf6210ce45af765b677312ed8c6d853a107ae76aa3b4da3a1df5",
    "SEM-YELLOW-ITEM-532000-5DB915-001": "6c83a8dac7608c2ae6368628ee48650c8d97152c85a0bba69826a0ff018a3556",
    "SEM-YELLOW-ITEM-532000-8A4908-001": "97f0fe1124e5edd3212eddbf23575261792196ab05bda7cf057602a42e2352dd",
    "SEM-YELLOW-ITEM-532000-CE55D9-001": "4e1697c2d13581fbc93834c7719af4c4fd2e51141449d1164efe7b8a4e499853",
    "SEM-YELLOW-ITEM-532000-CE5897-001": "6c0736e3ba60bbd6173920a1ee532a06a9231d63952bb3a3f1c1cbcd1ac24940",
    "SEM-YELLOW-ITEM-DECK-001": "cefd3d7b548785c2b78d796ccc8bfd0e9f4ed927b3f49b079b796b01f6af4200",
    "SEM-YELLOW-ITEM-IMMEDIATE-USE-001": "53bb76496da2d4119ce755e0cd2b866f483ba4fcbfc345bba10bc40ad7a77e46",
    "SEM-YELLOW-ITEM-ONE-USE-001": "1ac24c6bf25e8c1fb0dd49604338fbee325ad3b7ed5c2e634e9b6ff00eba6e83",
    "SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001": "3c38d5cda66879a69e12f885b735e669fb05ca4113ea5bd67423ff04244bc80f",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _code(card_id: int, guid: str) -> str:
    return f"{card_id}-{guid.upper()}"


def _rule_id(card_id: int, guid: str) -> str:
    return f"SEM-YELLOW-ITEM-{_code(card_id, guid)}-001"


def _regular(disposition: str) -> bool:
    return disposition == "included-regular-yellow-item-face"


def _occurrence(card_id: int, guid: str, disposition: str) -> str:
    code = _code(card_id, guid)
    return f"TTS-YELLOW-ITEM-{code}-FACE" if _regular(disposition) else f"TTS-YELLOW-ITEM-CLASS-CONFLICT-{code}-FACE"


def _source_id(card_id: int, guid: str, disposition: str) -> str:
    code = _code(card_id, guid)
    return f"SRC-YELLOW-ITEM-{code}" if _regular(disposition) else f"SRC-YELLOW-ITEM-CLASS-CONFLICT-{code}"


def _contains_in_order(values: list[str], expected: list[str]) -> bool:
    selected = [value for value in values if value in set(expected)]
    return selected == expected


def validate_yellow_item_family(
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
    class_conflicts = source.get("physicalClassConflictFaces") or []
    assets = source.get("sourceFaceAssets") or []
    assets_by_key = {row.get("assetKey"): row for row in assets}
    physical_by_sequence = {row.get("rootSequence"): row for row in [*faces, *class_conflicts]}

    if _sha(source_path) != PINNED_YELLOW_ITEM_SOURCE_INDEX_HASH:
        failures.append({"check": "pinned Yellow Item source index"})
    if source.get("counts") != EXPECTED_YELLOW_ITEM_COUNTS or len(physical_by_sequence) != 30 or sorted(physical_by_sequence) != list(range(1, 31)):
        failures.append({"check": "Yellow Item source-index exact physical/root/class occurrence count"})
    if set(assets_by_key) != set(EXPECTED_YELLOW_ITEM_ASSETS) or len(assets_by_key) != len(assets):
        failures.append({"check": "Yellow Item exact source-face asset/variant closure"})

    role_rows = [row for row in roles if row.get("role") == "yellowItemsDeck"]
    root_object = next((row for row in objects if row.get("guid") == "fe68f3"), {})
    child_objects = [row for row in objects if ["Deck", "fe68f3", ""] in (row.get("parent") or []) and row.get("gmnotes") == "yellowitem"]
    expected_children = {(card_id, guid) for _, card_id, guid, _, _, _ in EXPECTED_YELLOW_ITEM_ROOT}
    if (
        len(role_rows) != 1 or role_rows[0].get("guid") != "fe68f3" or role_rows[0].get("type") != "Deck"
        or role_rows[0].get("gmnotes") != "yellowitemDiscard" or role_rows[0].get("n_urls") != 7
        or role_rows[0].get("deck_nums") != ["33", "34", "3954", "5318", "5320"]
        or root_object.get("type") != "Deck" or root_object.get("parent") != [] or len(child_objects) != 30
        or {(int(row["card_id"]), row["guid"]) for row in child_objects} != expected_children
    ):
        failures.append({"check": "Yellow Item root Lua role/deck/tag/container closure"})

    root = source.get("rootDeckEvidence") or {}
    expected_saved_ids = [row[1] for row in EXPECTED_YELLOW_ITEM_ROOT]
    expected_selectors = [
        {"rootSequence": sequence, "fullCardId": card_id, "guid": guid, "customDeckId": custom_id,
         "batchDisposition": "included-regular" if _regular(disposition) else "class-conflict-excluded"}
        for sequence, card_id, guid, custom_id, _, disposition in EXPECTED_YELLOW_ITEM_ROOT
    ]
    custom = root.get("customDeckTuples") or {}
    if (
        root.get("sourceId") != "SRC-YELLOW-ITEM-ROOT-DECK" or root.get("ttsRole") != "yellowItemsDeck"
        or root.get("rootGuid") != "fe68f3" or root.get("rawSavePath") != "assets/tts-mod/extract/nemesis_script_mod.bin"
        or root.get("rawSaveSha256") != "8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68"
        or root.get("savedDeckIds") != expected_saved_ids or root.get("fullContainedSelectors") != expected_selectors
        or root.get("rootOrderIsGameplayOrder") is not False or sorted(custom) != ["33", "34", "3954", "5318", "5320"]
        or custom.get("33", {}).get("uniqueBack") is not True or custom.get("34", {}).get("uniqueBack") is not False
    ):
        failures.append({"check": "Yellow Item exact raw DeckIDs/full-selector/UniqueBack/saved-order lock"})

    expected_titles = {"DUCT TAPE": 5, "OXYGEN TANK": 8, "PHOSPHATES": 5, "TOOLS": 6}
    if source.get("titleMultiplicity") != expected_titles:
        failures.append({"check": "Yellow Item repeated-title/copy multiplicity no-collapse lock"})

    for asset_key, expected in EXPECTED_YELLOW_ITEM_ASSETS.items():
        path, source_sha, title, source_role, cell, physical_class, selected_disposition, panel_count, sentence_count, icon_refs, text_digest = expected
        asset = assets_by_key.get(asset_key) or {}
        actual = (asset.get("sourcePath"), asset.get("sourceSha256"), asset.get("printedTitle"), asset.get("sourceRole"), asset.get("generatedCell"), asset.get("physicalClass"), asset.get("selectedDisposition"))
        if actual != expected[:7] or not (repo / path).is_file() or _sha(repo / path) != source_sha:
            failures.append({"check": "Yellow Item independently locked source-face asset tuple", "assetKey": asset_key})
        recomputed_text = _digest({"title": asset.get("printedTitle"), "typeLine": asset.get("typeLine"), "upperRight": asset.get("upperRight"), "body": asset.get("printedBody")})
        if asset.get("printedBodyDigest") != text_digest or recomputed_text != text_digest:
            failures.append({"check": "Yellow Item exact title/body/punctuation/order lock", "assetKey": asset_key})
        regions = asset.get("regions") or []
        panels = asset.get("panels") or []
        sentences = asset.get("sentences") or []
        icons = asset.get("iconOccurrences") or []
        if [row.get("regionId") for row in regions] != ["R1", "R2", "R3"] or [row.get("role") for row in regions] != ["artwork-and-interface", "identity-trait-and-restriction", "operative-effect-body"]:
            failures.append({"check": "Yellow Item exact source region/anatomy roles/order", "assetKey": asset_key})
        if len(panels) != panel_count or [row.get("readingOrder") for row in panels] != list(range(1, panel_count + 1)) or asset.get("panelDigest") != _digest(panels):
            failures.append({"check": "Yellow Item exact source panel roles/order/region linkage", "assetKey": asset_key})
        if len(sentences) != sentence_count or [row.get("sequence") for row in sentences] != list(range(1, sentence_count + 1)):
            failures.append({"check": "Yellow Item exact printed sentence occurrence count/order", "assetKey": asset_key})
        body = asset.get("printedBody") or ""
        cursor = 0
        for sentence in sentences:
            start, end = sentence.get("start"), sentence.get("end")
            if not isinstance(start, int) or not isinstance(end, int) or start < cursor or body[start:end] != sentence.get("exactText") or sentence.get("panelId") not in {row.get("panelId") for row in panels}:
                failures.append({"check": "Yellow Item exact sentence span/punctuation/panel lock", "assetKey": asset_key, "sentenceId": sentence.get("sentenceId")})
            cursor = end if isinstance(end, int) else cursor
        if tuple(row.get("semanticReferenceId") for row in icons) != icon_refs or [row.get("sequence") for row in icons] != list(range(1, len(icons) + 1)) or asset.get("iconDigest") != _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in icons]):
            failures.append({"check": "Yellow Item exact source-local icon occurrence projection", "assetKey": asset_key})
        selected = selected_disposition in {"included-regular", "class-conflict-excluded"}
        gap = asset.get("selectorGap")
        if asset.get("selectedByRootDeck") is not selected or (not selected and (not isinstance(gap, dict) or gap.get("status") != "explicit-no-Yellow-root-DeckID-GUID-selector" or gap.get("cardIdModuloJoinUsed") is not False)) or (selected and gap is not None):
            failures.append({"check": "Yellow Item generated selector/selector-gap closure", "assetKey": asset_key})
        representation = asset.get("representationBoundary") or {}
        if representation.get("semanticProjectionBody") != asset.get("printedBody") or not representation.get("policy") or not isinstance(representation.get("bodyDiffers"), bool):
            failures.append({"check": "Yellow Item extraction/semantic representation boundary", "assetKey": asset_key})

    expected_backlog_rules: dict[str, list[str]] = {}
    regular_sequence = 0
    for sequence, card_id, guid, custom_id, asset_key, disposition in EXPECTED_YELLOW_ITEM_ROOT:
        row = physical_by_sequence.get(sequence) or {}
        asset = assets_by_key[asset_key]
        regular = _regular(disposition)
        if regular:
            regular_sequence += 1
        expected_tuple = (sequence, regular_sequence if regular else None, card_id, guid, custom_id, asset_key, disposition, _rule_id(card_id, guid) if regular else None)
        actual_tuple = (row.get("rootSequence"), row.get("familySequence"), row.get("ttsCardId"), row.get("ttsCardGuid"), row.get("customDeckId"), row.get("sourceAssetKey"), row.get("batchDisposition"), row.get("semanticRuleId"))
        occurrence_id = _occurrence(card_id, guid, disposition)
        if actual_tuple != expected_tuple or row.get("yellowItemOccurrenceId") != occurrence_id:
            failures.append({"check": "independently locked Yellow Item physical occurrence crosswalk", "occurrenceId": occurrence_id})
        selector = row.get("sourceSelector") or {}
        expected_back = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235323/E2B2763353C8DD3A6DD329CCEC256500AEF64B8A/" if custom_id == "33" else "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235441/B56EC1560F6B7FB5A61EC49490019DCB185D1CFE/"
        expected_unique = custom_id == "33"
        if (
            row.get("sourceId") != _source_id(card_id, guid, disposition) or row.get("sourcePath") != asset.get("sourcePath") or row.get("sourceSha256") != asset.get("sourceSha256")
            or selector.get("key") != "FaceURL" or selector.get("fullCardId") != card_id or selector.get("guid") != guid or selector.get("parentDeckGuid") != "fe68f3"
            or selector.get("customDeckId") != custom_id or selector.get("backUrl") != expected_back or selector.get("uniqueBack") is not expected_unique
            or selector.get("backGeneratedCell") != (1 if expected_unique else None) or selector.get("selectorGap") is not None or selector.get("cardIdModuloJoinUsed") is not False
        ):
            failures.append({"check": "Yellow Item exact CardID/GUID/FaceURL/BackURL/UniqueBack selector projection", "occurrenceId": occurrence_id})
        expected_cell = EXPECTED_YELLOW_ITEM_ASSETS[asset_key][4]
        if expected_cell is not None:
            expected_sheet = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146.jpg" if custom_id == "33" else "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145.jpg"
            expected_sha = "d71c7a4ad3490071787104e2cec054d4fc4f00ac7d15232c45b570aefe57d591" if custom_id == "33" else "8d6c105dfe16c9b2c747b9d40f2f9ba9a9ebbfa582c5aa9db2d01956b4aebb76"
            if selector.get("generatedSpriteSheetCell") is not True or selector.get("sourceSheetPath") != expected_sheet or selector.get("sourceSheetSha256") != expected_sha or selector.get("sourceSheetGrid") != {"columns": 2, "rows": 2} or selector.get("generatedCell") != expected_cell:
                failures.append({"check": "Yellow Item generated sheet/hash/grid/cell selector projection", "occurrenceId": occurrence_id})
        elif selector.get("generatedSpriteSheetCell") is not False or selector.get("sourceSheetPath") is not None or selector.get("generatedCell") is not None:
            failures.append({"check": "Yellow Item direct/generated face selector inversion", "occurrenceId": occurrence_id})
        physical_text_digest = _digest({"title": row.get("printedTitle"), "typeLine": row.get("typeLine"), "upperRight": row.get("upperRight"), "body": row.get("printedBody")})
        if (
            physical_text_digest != EXPECTED_YELLOW_ITEM_ASSETS[asset_key][10]
            or row.get("printedBodyDigest") != physical_text_digest
            or len(row.get("panels") or []) != EXPECTED_YELLOW_ITEM_ASSETS[asset_key][7]
            or row.get("panelDigest") != _digest(row.get("panels") or [])
            or len(row.get("sentences") or []) != EXPECTED_YELLOW_ITEM_ASSETS[asset_key][8]
            or tuple(icon.get("semanticReferenceId") for icon in row.get("iconOccurrences") or []) != EXPECTED_YELLOW_ITEM_ASSETS[asset_key][9]
            or row.get("iconDigest") != _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in row.get("iconOccurrences") or []])
        ):
            failures.append({"check": "Yellow Item exact physical panel/body/icon projection", "occurrenceId": occurrence_id})
        join = row.get("joinEvidence") or {}
        if join.get("identityJoin") != "exact raw root physical occurrence and exact source-asset projection" or any(join.get(key) is not False for key in ("titleOnlyJoin", "colorOnlyJoin", "utilityOrSystemAppearanceJoin", "bodyResemblanceJoin", "folderOnlyJoin", "sourceOrderOnlyJoin", "generatedCellOnlyJoin", "cardIdModuloJoin", "licensedKeyJoin")):
            failures.append({"check": "Yellow Item title/color/utility-system/body/folder/order/cell/modulo/licensed join prohibited", "occurrenceId": occurrence_id})
        registry = source_by_id.get(_source_id(card_id, guid, disposition)) or {}
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId"), registry.get("evidenceRecord")) != (asset.get("sourcePath"), asset.get("sourceSha256"), occurrence_id, asset.get("sourceSha256")):
            failures.append({"check": "Yellow Item source-registry exact physical tuple", "occurrenceId": occurrence_id})
        backlog_id = "CARD:" + asset["sourceSha256"][:16]
        if row.get("backlogUnitId") != backlog_id:
            failures.append({"check": "Yellow Item exact backlog tuple projection", "occurrenceId": occurrence_id})
        if regular:
            expected_backlog_rules.setdefault(backlog_id, []).append(_rule_id(card_id, guid))
        elif (
            row.get("semanticRuleId") is not None
            or (
                (backlog_by_id.get(backlog_id) or {}).get("status") != "pending"
                and "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001" not in (backlog_by_id.get(backlog_id) or {}).get("pilotRuleIds", [])
            )
        ):
            failures.append({"check": "Yellow Item regular/class-conflict leakage", "occurrenceId": occurrence_id})

    for asset_key in ("sheet34-01", "sheet34-02", "sheet33-02"):
        asset = assets_by_key[asset_key]
        expected_backlog_rules["CARD:" + asset["sourceSha256"][:16]] = ["SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001"]
    for backlog_id, rule_ids in expected_backlog_rules.items():
        backlog = backlog_by_id.get(backlog_id) or {}
        asset = next(item for item in assets if "CARD:" + item["sourceSha256"][:16] == backlog_id)
        if backlog.get("sourcePath") != asset.get("sourcePath") or backlog.get("sourceLocator") != asset.get("sourceSha256") or backlog.get("pilotRuleIds") != rule_ids or backlog.get("status") != "pilot-covered":
            failures.append({"check": "Yellow Item exact backlog tuple projection", "backlogUnitId": backlog_id})
    if (backlog_by_id.get("CARD:41183eb8c34b083a") or {}).get("status") != "pilot-covered" or "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001" not in (backlog_by_id.get("CARD:41183eb8c34b083a") or {}).get("pilotRuleIds", []):
        failures.append({"check": "Yellow Item cross-family Military Taser backlog boundary"})
    if (source.get("familyCountEvidence", {}).get("backlog") or {}).get("crossFamilyPendingUnitIds") != [] or (source.get("familyCountEvidence", {}).get("backlog") or {}).get("crossFamilyCoveredByEquipmentUnitIds") != ["CARD:41183eb8c34b083a"]:
        failures.append({"check": "Yellow Item equipment cross-family status projection"})

    sheets = source.get("sourceSheets") or []
    backs = source.get("rootBacks") or []
    expected_sheets = [
        ("SRC-YELLOW-ITEM-SHEET-33", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146.jpg", "d71c7a4ad3490071787104e2cec054d4fc4f00ac7d15232c45b570aefe57d591", 13, [1], [0, 2, 3]),
        ("SRC-YELLOW-ITEM-SHEET-34", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145.jpg", "8d6c105dfe16c9b2c747b9d40f2f9ba9a9ebbfa582c5aa9db2d01956b4aebb76", 12, [0, 3], [1, 2]),
    ]
    actual_sheets = [(row.get("sourceId"), row.get("sourcePath"), row.get("sourceSha256"), row.get("globalSelectorReferences"), row.get("yellowRootSelectedCells"), row.get("yellowSelectorGapCells")) for row in sheets]
    expected_backs = [
        ("SRC-YELLOW-ITEM-SHARED-BACK", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-142.jpg", "4e52af04a73a751da9415936bcd8a3144e4be7b88994498a8e51b2f3dab5c66d", 25, 26, False),
        ("SRC-YELLOW-ITEM-UNIQUE-BACK-SHEET-33", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-143.jpg", "4a4be058786fcf3e2195ef66a4052ebbf721946ed5d4b4bb3b624f3c4d5fbf6a", 5, 13, True),
    ]
    actual_backs = [(row.get("sourceId"), row.get("sourcePath"), row.get("sourceSha256"), row.get("rootPhysicalSelectors"), row.get("globalSelectorReferences"), (row.get("sourceSelector") or {}).get("uniqueBack")) for row in backs]
    if actual_sheets != expected_sheets or actual_backs != expected_backs or any(row.get("separateRulesFace") is not False for row in [*sheets, *backs]) or (backs[1].get("sourceSelector") or {}).get("rootSelectedCell") != 1 or backs[1].get("visibleCellRoles") != [{"cell": 0, "literal": "Red Item back"}, {"cell": 1, "literal": "Yellow Item back"}, {"cell": 2, "literal": "Yellow Item back"}, {"cell": 3, "literal": "blank/non-rules"}]:
        failures.append({"check": "Yellow Item parent-sheet/shared-back/UniqueBack/selector-gap closure"})
    for row in [*sheets, *backs]:
        registry = source_by_id.get(row.get("sourceId")) or {}
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId")) != (row.get("sourcePath"), row.get("sourceSha256"), row.get("occurrenceId")):
            failures.append({"check": "Yellow Item source-registry sheet/back closure", "sourceId": row.get("sourceId")})

    licensed = source.get("licensedDigitalOccurrences") or []
    expected_bga = [("DuctTape", 5, False), ("FireExtinguisher", 5, True), ("OxygenTank", 8, False), ("Phosphates", 5, False), ("RobotController", 1, True), ("Tools", 6, False)]
    items_table = next((row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row.get("name") == "ITEMS_DATA"), {})
    if [(row.get("key"), row.get("nbr"), row.get("heavy")) for row in licensed] != expected_bga or items_table.get("count") != 57 or any(row.get("sourceBlockText") not in bga_text or row.get("identityCrosswalkStatus") != "independent licensed occurrence; no TTS/official physical identity join asserted" for row in licensed) or sum(row.get("nbr", 0) for row in licensed) != 30 or sum(row.get("nbr", 0) for row in licensed if not row.get("heavy") and not row.get("armor")) != 24 or sum(row.get("nbr", 0) for row in licensed if row.get("heavy") or row.get("armor")) != 6:
        failures.append({"check": "Yellow Item licensed independent rows/30-24-6/no-crosswalk closure"})

    official = source.get("officialVisibleCounterparts") or []
    expected_official_ids = ["RB-P03-V01", "RB-P05-V01", "RB-P09-V01", "RB-P12-V02", "RB-P16-V02", "RB-P17-V01", "RB-P21-V01", "RB-P22-V01", "RB-P23-V02", "RB-P28-V02", "RB-P28-V03", "RB-P29-V01", "RB-P29-V03", "RB-P37-V01", "RB-P40-V02"]
    faq = source.get("faqSearchClosure") or {}
    if [row.get("sourceOccurrenceId") for row in official] != expected_official_ids or sum(row.get("exactRegularYellowRulesFace") is True for row in official) != 1 or next((row for row in official if row.get("sourceOccurrenceId") == "RB-P28-V03"), {}).get("exactTtsPhysicalCrosswalk") is not False or [row.get("sourceUnitId") for row in faq.get("baseApplicableOccurrences") or []] != ["FQ-P02-U10", "FQ-P02-U18", "FQ-P03-U04", "FQ-P03-U05", "FQ-P03-U06", "FQ-P03-U07"] or len(faq.get("excludedExpansionOccurrences") or []) != 9:
        failures.append({"check": "Yellow Item official/FAQ authority and occurrence closure"})

    backlog_ledger = (source.get("familyCountEvidence", {}).get("backlog") or {})
    linked_ids = backlog_ledger.get("linkedUnitIds") or []
    if backlog_ledger.get("faceTupleCount") != 4 or backlog_ledger.get("variantTupleCount") != 3 or backlog_ledger.get("physicalFaceLinkCount") != 24 or backlog_ledger.get("obligationCount") != 38 or len(linked_ids) != 38 or any((backlog_by_id.get(unit_id) or {}).get("status") != "pilot-covered" for unit_id in linked_ids):
        failures.append({"check": "Yellow Item exact overlapping backlog-obligation closure"})

    expected_rule_ids = [_rule_id(card_id, guid) for _, card_id, guid, _, _, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition)]
    actual_rule_ids = {rule_id for rule_id in record_by_id if re.fullmatch(r"SEM-YELLOW-ITEM-\d+-[A-Z0-9]+-001", rule_id)}
    if actual_rule_ids != set(expected_rule_ids):
        failures.append({"check": "Yellow Item semantic physical face-record closure", "missing": sorted(set(expected_rule_ids) - actual_rule_ids), "extra": sorted(actual_rule_ids - set(expected_rule_ids))})

    expected_questions_by_asset = {
        "sheet34-03": ["SEM-Q-051", "SEM-Q-056"],
        "direct-phosphates": ["SEM-Q-051", "SEM-Q-055"],
        "direct-oxygen": ["SEM-Q-044", "SEM-Q-045"],
        "sheet34-00": ["SEM-Q-051", "SEM-Q-053", "SEM-Q-054"],
    }
    for sequence, card_id, guid, _, asset_key, disposition in EXPECTED_YELLOW_ITEM_ROOT:
        if not _regular(disposition):
            continue
        occurrence_id = _occurrence(card_id, guid, disposition)
        source_face = physical_by_sequence.get(sequence) or {}
        rule = record_by_id.get(_rule_id(card_id, guid)) or {}
        assertions = {row.get("assertionId"): row for row in rule.get("sourceAssertions") or []}
        scan = assertions.get(f"SA-YIF-{_code(card_id, guid)}-SCAN") or {}
        if (scan.get("sourceId"), scan.get("sourceSha256"), scan.get("sourceText"), scan.get("textKind")) != (_source_id(card_id, guid, disposition), EXPECTED_YELLOW_ITEM_ASSETS[asset_key][1], source_face.get("printedBody"), "verbatim") or rule.get("authority", {}).get("highest") != "official-primary" or rule.get("sourceVariants") != []:
            failures.append({"check": "Yellow Item face exact scan/general/authority/no-title-variant projection", "occurrenceId": occurrence_id})
        expected_questions = expected_questions_by_asset[asset_key]
        if rule.get("unresolvedQuestionRefs") != expected_questions or rule.get("status") != "source-backed-with-open-question":
            failures.append({"check": "Yellow Item face exact optionality/owner/no-default question projection", "occurrenceId": occurrence_id})
        sentence_ids = {row.get("sentenceId") for row in source_face.get("sentences") or []}
        panel_ids = {row.get("panelId") for row in source_face.get("panels") or []}
        region_ids = {row.get("regionId") for row in source_face.get("regions") or []}
        operations = rule.get("operations") or []
        if not operations or any(op.get("sourceSentenceId") not in sentence_ids or op.get("sourcePanelId") not in panel_ids or op.get("sourceRegionId") not in region_ids for op in operations):
            failures.append({"check": "Yellow Item face operation-to-sentence/panel/region closure", "occurrenceId": occurrence_id})
        if "same title/body/multiplicity creates no identity or stacking key" not in rule.get("stacking", {}).get("policy", ""):
            failures.append({"check": "Yellow Item physical-copy/no-title stacking lock", "occurrenceId": occurrence_id})
        if asset_key in {"sheet34-03", "direct-phosphates", "sheet34-00"}:
            inferred = {"icon.notInCombat", "icon.computer", "term.robot-card"}
            if inferred.intersection(rule.get("termRefs", [])) or "SEM-Q-051" not in rule.get("unresolvedQuestionRefs", []) or not any(op.get("operationType") == "resolve-open-alternative" and "SEM-Q-051" in op.get("objectRef", "") for op in operations):
                failures.append({"check": "Yellow Item local glyph no-default/no-system inference lock", "occurrenceId": occurrence_id})

    use = record_by_id.get("SEM-USE-ITEM-001") or {}
    use_ops = use.get("operations") or []
    use_dispatch = next((op.get("dispatchRuleIds") for op in use_ops if op.get("stepId") == "S05"), None)
    lifecycle_dispatch = next((op.get("dispatchRuleIds") for op in use_ops if op.get("stepId") == "S06"), None)
    if not use_dispatch or use_dispatch[-24:] != expected_rule_ids or lifecycle_dispatch != ["SEM-GREEN-ITEM-ONE-USE-001", "SEM-RED-ITEM-ONE-USE-001", "SEM-YELLOW-ITEM-ONE-USE-001"] or [op.get("operationType") for op in use_ops] != ["select-target", "resolve-open-alternative", "pay-cost", "reveal", "invoke-selected-process", "invoke-selected-process"] or use.get("unresolvedQuestionRefs") != ["SEM-Q-039"]:
        failures.append({"check": "Yellow Item shared Use/payment/reveal/dispatch/lifecycle lock"})
    trade = record_by_id.get("SEM-ITEM-TRADE-GAIN-001") or {}
    trade_dispatch = next((op.get("dispatchRuleIds") for op in trade.get("operations") or [] if op.get("dispatchRuleIds")), None)
    if trade_dispatch != ["SEM-GREEN-ITEM-IMMEDIATE-USE-001", "SEM-RED-ITEM-IMMEDIATE-USE-001", "SEM-YELLOW-ITEM-IMMEDIATE-USE-001"] or trade.get("unresolvedQuestionRefs") != ["SEM-Q-045", "SEM-Q-054"] or not any(condition.get("conditionId") == "C-YI-TRADE-DUCT-STACK" for condition in trade.get("preconditions") or []) or not any(op.get("operationType") == "resolve-open-alternative" and "SEM-Q-054" in op.get("objectRef", "") for op in trade.get("operations") or []):
        failures.append({"check": "Yellow Item Trade/immediate/Duct-stack no-default integration lock"})

    deck = record_by_id.get("SEM-YELLOW-ITEM-DECK-001") or {}
    deck_ops = deck.get("operations") or []
    one_use = record_by_id.get("SEM-YELLOW-ITEM-ONE-USE-001") or {}
    immediate = record_by_id.get("SEM-YELLOW-ITEM-IMMEDIATE-USE-001") or {}
    oxygen_gain = record_by_id.get("SEM-GAIN-OXYGEN-001") or {}
    oxygen_token = record_by_id.get("SEM-OXYGEN-TOKEN-EFFECT-001") or {}
    malfunction = record_by_id.get("SEM-DISCARD-MALFUNCTION-001") or {}
    reinforce = record_by_id.get("SEM-REINFORCE-CORRIDOR-001") or {}
    if [op.get("operationType") for op in deck_ops] != ["shuffle", "transition-zone", "set-state", "evaluate-condition", "resolve-open-alternative", "draw-random", "resolve-open-alternative", "evaluate-condition"] or (deck_ops[0].get("repeat") or {}) != {"rootPhysicalCardCount": 30, "regularBatchFaceCount": 24, "explicitHeavyCount": 0, "physicalClassConflictCount": 6} or deck.get("unresolvedQuestionRefs") != ["SEM-Q-040", "SEM-Q-052"] or any(op.get("operationType") == "shuffle" and "discard" in op.get("objectRef", "").lower() for op in deck_ops[1:]):
        failures.append({"check": "Yellow Item lifecycle/class/reshuffle lock"})
    if [op.get("operationType") for op in one_use.get("operations") or []] != ["resolve-open-alternative", "resolve-open-alternative", "transition-zone", "evaluate-condition"] or (one_use.get("operations") or [{}, {}, {}])[2].get("transition", {}).get("to") != "tax.scaffold.zone.discard-pile" or one_use.get("unresolvedQuestionRefs") != ["SEM-Q-039", "SEM-Q-053"]:
        failures.append({"check": "Yellow Item One Use/Duct disposition/discard/no-return order lock"})
    if (immediate.get("decisions") or [{}])[0].get("cardinality") != {"min": 0, "max": 1} or (immediate.get("decisions") or [{}])[0].get("declineAllowed") is not True or immediate.get("unresolvedQuestionRefs") != ["SEM-Q-045"]:
        failures.append({"check": "Yellow Item immediate optionality/multi-window lock"})
    if [op.get("operationType") for op in oxygen_gain.get("operations") or []] != ["change-value", "evaluate-condition"] or "without exceeding 7" not in json.dumps(oxygen_gain) or oxygen_gain.get("partialResolution", {}).get("policy") != "up-to-source-maximum":
        failures.append({"check": "Yellow Item Oxygen gain/cap/no-overflow lock"})
    if [op.get("operationType") for op in oxygen_token.get("operations") or []] != ["invoke-process", "evaluate-condition"] or (oxygen_token.get("operations") or [{}])[0].get("invokeRuleId") != "SEM-GAIN-OXYGEN-001" or "exactly once" not in json.dumps(oxygen_token):
        failures.append({"check": "Yellow Item Oxygen token effect/caller-lifecycle lock"})
    if [op.get("operationType") for op in malfunction.get("operations") or []] != ["select-target", "evaluate-condition", "transition-zone"] or (malfunction.get("decisions") or [{}, {}])[1].get("selectionMode") != "consent" or (malfunction.get("operations") or [{}, {}, {}])[2].get("transition", {}).get("to") != "tax.scaffold.supply-pool":
        failures.append({"check": "Yellow Item Malfunction local target/consent/finite-return lock"})
    if [op.get("operationType") for op in reinforce.get("operations") or []] != ["remove-component", "set-state"] or "value-0 Reinforced side" not in json.dumps(reinforce) or "Hibernatorium" not in json.dumps(reinforce) or "Closed Door" not in json.dumps(reinforce):
        failures.append({"check": "Yellow Item Reinforce Noise/order/Hibernatorium/Door lock"})

    variant = record_by_id.get("SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001") or {}
    if variant.get("status") != "source-variant" or variant.get("unresolvedQuestionRefs") != [] or len(variant.get("sourceVariants") or []) != 18 or len(variant.get("sourceAssertions") or []) != 14 or len(variant.get("operations") or []) != 20 or any(row.get("sourceAssertionId") not in {item.get("assertionId") for item in variant.get("sourceAssertions") or []} for row in variant.get("sourceVariants") or []) or "no title, Yellow color, utility/repair/system art" not in (variant.get("operations") or [{}])[-1].get("objectRef", ""):
        failures.append({"check": "Yellow Item variant/authority closure"})

    for question_id, blocks in {key: value for key, value in {
        "SEM-Q-051": [rule_id for rule_id in expected_rule_ids if any(token in rule_id for token in [])],
        "SEM-Q-052": ["SEM-YELLOW-ITEM-DECK-001"],
        "SEM-Q-053": ["SEM-YELLOW-ITEM-ONE-USE-001", *[_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset == "sheet34-00"]],
        "SEM-Q-054": ["SEM-ITEM-TRADE-GAIN-001", *[_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset == "sheet34-00"]],
        "SEM-Q-055": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset == "direct-phosphates"],
        "SEM-Q-056": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset == "sheet34-03"],
    }.items() if key != "SEM-Q-051"}.items():
        question = question_by_id.get(question_id) or {}
        if question.get("defaultProhibited") is not True or question.get("blocksRuleIds") != blocks or len(question.get("alternatives") or []) != 3:
            failures.append({"check": "Yellow Item ambiguity no-default alternatives/linkage", "questionId": question_id})
    local_blocks = [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset in {"sheet34-03", "direct-phosphates", "sheet34-00"}]
    local_question = question_by_id.get("SEM-Q-051") or {}
    if local_question.get("defaultProhibited") is not True or local_question.get("blocksRuleIds") != local_blocks or len(local_question.get("alternatives") or []) != 3:
        failures.append({"check": "Yellow Item ambiguity no-default alternatives/linkage", "questionId": "SEM-Q-051"})
    for question_id, expected in {
        "SEM-Q-039": ["SEM-YELLOW-ITEM-ONE-USE-001"],
        "SEM-Q-040": ["SEM-YELLOW-ITEM-DECK-001"],
        "SEM-Q-044": [_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset == "direct-oxygen"],
        "SEM-Q-045": ["SEM-YELLOW-ITEM-IMMEDIATE-USE-001", *[_rule_id(card_id, guid) for _, card_id, guid, _, asset, disposition in EXPECTED_YELLOW_ITEM_ROOT if _regular(disposition) and asset == "direct-oxygen"]],
    }.items():
        question = question_by_id.get(question_id) or {}
        if question.get("defaultProhibited") is not True or not _contains_in_order(question.get("blocksRuleIds") or [], expected) or len(question.get("alternatives") or []) != 3:
            failures.append({"check": "Yellow Item shared ambiguity no-default family linkage", "questionId": question_id})

    yellow_conflicts = {row.get("conflictId"): row for row in conflict_rows if row.get("conflictId") in {f"SC-{index:03d}" for index in range(41, 49)}}
    expected_statuses = ["unresolved", "unresolved", "preserved-boundary", "unresolved", "unresolved", "unresolved", "unresolved", "preserved-boundary"]
    if set(yellow_conflicts) != {f"SC-{index:03d}" for index in range(41, 49)} or [yellow_conflicts[f"SC-{index:03d}"].get("status") for index in range(41, 49)] != expected_statuses or [yellow_conflicts[f"SC-{index:03d}"].get("questionId") for index in (41, 42, 44, 45, 46, 47)] != ["SEM-Q-052", "SEM-Q-051", "SEM-Q-053", "SEM-Q-054", "SEM-Q-055", "SEM-Q-056"]:
        failures.append({"check": "Yellow Item source-variant authority/conflict closure"})

    if EXPECTED_YELLOW_ITEM_RECORD_DIGESTS:
        for rule_id, expected_digest in EXPECTED_YELLOW_ITEM_RECORD_DIGESTS.items():
            item = record_by_id.get(rule_id)
            if item is None or _digest(item) != expected_digest:
                failures.append({"check": "independently locked Yellow Item semantic projection", "ruleId": rule_id})

    system = next((row for row in coverage.get("systems") or [] if row.get("system") == "base source-clear regular Yellow Item card/component family"), {})
    expected_system_ids = [*EXPECTED_YELLOW_ITEM_REUSABLE_RULE_IDS, *expected_rule_ids]
    not_yet = " ".join(coverage.get("notYetCovered") or [])
    if system.get("ruleIds") != expected_system_ids or "24-occurrence source-clear regular Yellow Item" not in not_yet or "six Fire Extinguisher/Robot Controller Yellow class-conflict occurrences" in not_yet:
        failures.append({"check": "Yellow Item coverage/class-boundary/no-full-coverage claim"})

    return {
        "rows": faces,
        "classConflicts": class_conflicts,
        "assets": assets,
        "licensed": licensed,
        "official": official,
        "actualRuleIds": actual_rule_ids,
        "expectedBacklogRules": expected_backlog_rules,
    }
