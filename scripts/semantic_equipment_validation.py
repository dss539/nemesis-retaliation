from __future__ import annotations

import hashlib
import json
from pathlib import Path

from semantic_attack_records import _find_guid, _parse_value


RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
ROLES_PATH = "assets/tts-mod/extract/v2/lua_roles.json"
OBJECTS_PATH = "assets/tts-mod/extract/v2/objects.json"
CLASSIFICATION_PATH = "assets/tts-mod/extract/v2/classification.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"
MANIFEST_PATH = "assets/tts-mod/extract/v2-dl/tree/manifest.json"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"

EXPECTED_SUPPORT_CHILDREN = [
    (556600, "a0daef"), (507800, "f56191"), (508200, "a0f5b7"), (502900, "4ecb1e"),
    (507200, "2f41b8"), (507600, "1281c5"), (507300, "a9fab3"), (507400, "badad6"),
    (507500, "33c9e4"), (507700, "4e708d"), (507100, "875c54"), (410200, "98ad4c"),
    (493400, "85096e"), (2917, "dffd35"), (424900, "8ae645"), (508300, "fd46ec"),
    (410400, "a242e6"), (507000, "1f3ca2"), (507900, "df46d6"), (466100, "4912a1"),
    (424800, "881635"), (508100, "785b03"), (2910, "d29216"), (508000, "0f51f3"),
]
EXPECTED_CHARACTER_TUPLES = [
    ("Combat Engineer", "2059a7", 431200),
    ("Heavy Gun Operator", "427c1a", 524700),
    ("Medical Support", "219bff", 545000),
    ("Contractor", "bac443", 545000),
    ("Contractor", "21bd03", 591300),
    ("Officer", "039116", 581900),
    ("Recon", "81d699", 556600),
]
EXPECTED_SUPPORT_CLASSES = {
    "a0daef": "ranged-weapon", "f56191": "ranged-weapon", "a0f5b7": "melee-weapon", "4ecb1e": "heavy-item",
    "2f41b8": "ranged-weapon", "1281c5": "ranged-weapon", "a9fab3": "heavy-item", "badad6": "heavy-item",
    "33c9e4": "heavy-item", "4e708d": "ranged-weapon", "875c54": "melee-weapon", "98ad4c": "heavy-item",
    "85096e": "heavy-item", "dffd35": "ranged-weapon", "8ae645": "armor-item", "fd46ec": "ranged-weapon",
    "a242e6": "ranged-weapon", "1f3ca2": "armor-item", "df46d6": "melee-weapon", "4912a1": "armor-item",
    "881635": "armor-item", "785b03": "ranged-weapon", "d29216": "heavy-item", "0f51f3": "armor-item",
}
EXPECTED_CHARACTER_CLASSES = {
    "2059a7": "ranged-weapon", "427c1a": "ranged-weapon", "219bff": "ranged-weapon",
    "bac443": "ranged-weapon", "21bd03": "armor-item", "039116": "ranged-weapon", "81d699": "ranged-weapon",
}
EXPECTED_GENERATED_CELLS = {"dffd35": 17, "d29216": 10}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_raw(path: Path) -> dict:
    data = path.read_bytes()
    root = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    return root


def _fail(failures: list[dict], check: str, **extra) -> None:
    failures.append({"check": check, **extra})


def validate_equipment_family(
    repo: Path,
    equipment_source_path: Path,
    equipment_sources: dict,
    source_by_id: dict,
    backlog_rows_by_id: dict,
    record_by_id: dict,
    question_by_id: dict,
    conflict_rows: list[dict],
    coverage: dict,
    failures: list[dict],
) -> dict:
    idx = equipment_sources
    counts = idx.get("counts") or {}
    expected_counts = {
        "officialCharacterItemCards": 7, "officialSupportEquipmentCards": 24,
        "supportRootPhysicalOccurrences": 24, "supportRootDirectPhysicalOccurrences": 22,
        "supportRootGeneratedPhysicalOccurrences": 2, "supportRootUniquePrintedTitles": 24,
        "supportRootHeavyPhysicalOccurrences": 19, "supportRootArmorPhysicalOccurrences": 5,
        "supportRootWeaponPhysicalOccurrences": 12, "supportRootRangedWeaponPhysicalOccurrences": 9,
        "supportRootMeleeWeaponPhysicalOccurrences": 3, "supportSourceFaceAssets": 40,
        "supportSelectedSourceFaceAssets": 24, "supportSelectorGapSourceFaceAssets": 16,
        "supportParentSheets": 1, "supportParentSheetCells": 18, "supportSelectedGeneratedCells": 2,
        "supportSharedBacks": 1, "supportSharedBackGlobalReferences": 72,
        "characterKitPhysicalOccurrences": 7, "characterKitSourceClearVariantOccurrences": 5,
        "characterKitPrototypeExclusions": 2, "characterKitDistinctBackAssets": 6,
        "contractorCharacterItemOccurrences": 2, "greenRootHeavyPhysicalOccurrences": 7,
        "redRootExplicitHeavyPhysicalOccurrences": 3, "redRootClassConflictPhysicalOccurrences": 6,
        "yellowRootClassConflictPhysicalOccurrences": 6, "colorRootHeavySemanticOccurrences": 10,
        "classConflictSemanticExclusions": 12, "officialVisibleCurrentFaceOccurrences": 6,
        "officialVisibleCurrentCharacterItemOccurrences": 2, "officialVisibleCurrentSupportOccurrences": 3,
        "officialVisibleCurrentOtherHeavyOccurrences": 1, "officialResolvedTacticalGearSlotOccurrences": 5,
        "ttsSourceResolvedTacticalGearSlotOccurrences": 5, "ttsSlotEvidenceUnresolvedOccurrences": 12,
        "dedicatedPrintedCardTrackOccurrences": 0, "officialCharacterHealthTrackOccurrences": 1,
        "supportPhysicalPanels": 99, "supportPrintedSentences": 33, "supportFunctionalIconOccurrences": 52,
        "supportMatchedIconOccurrences": 48, "supportLiteralNoMatchIconOccurrences": 4,
        "characterPhysicalPanels": 28, "characterPrintedSentences": 8, "characterFunctionalIconOccurrences": 10,
        "licensedRelevantRows": 37, "licensedSupportRows": 24, "licensedCharacterRows": 7,
        "licensedColorHeavyOrConflictRows": 6, "licensedDeclaredRelevantCopies": 53,
        "baseApplicableFaqOccurrences": 8, "officialRulebookVisualOccurrences": 13,
        "semanticTtsPhysicalFaceRecords": 39, "semanticOfficialFaceRecords": 6,
        "backlogSourceFaceTuples": 52, "backlogObligationsLinked": 84,
    }
    if counts != expected_counts:
        _fail(failures, "Equipment declared counts", expected=expected_counts, actual=counts)
    if _sha(equipment_source_path) != "de37dfbe7434de48c565995ca98a87a02dcd243d92c5eeada473dea8bf153a11":
        _fail(failures, "pinned Equipment source index")

    roles = json.loads((repo / ROLES_PATH).read_text(encoding="utf-8"))
    support_roles = [row for row in roles if row.get("role") == "startItemDeck"]
    if len(support_roles) != 1 or support_roles[0].get("guid") != "f71196" or support_roles[0].get("type") != "DeckCustom" or support_roles[0].get("contained") != 1:
        _fail(failures, "Support Equipment Lua role closure")
    raw = _load_raw(repo / RAW_SAVE_PATH)
    root = _find_guid(raw.get("ObjectStates"), "f71196")
    if not isinstance(root, dict) or root.get("Name") != "DeckCustom":
        _fail(failures, "Support Equipment raw root closure")
    root_data = root if isinstance(root, dict) else {}
    contained = root_data.get("ContainedObjects") or []
    if isinstance(contained, dict):
        contained = list(contained.values())
    actual_children = [(int(row.get("CardID")), row.get("GUID")) for row in contained]
    if actual_children != EXPECTED_SUPPORT_CHILDREN:
        _fail(failures, "Support Equipment exact raw children/order", actual=actual_children, expected=EXPECTED_SUPPORT_CHILDREN)
    deck_ids = root_data.get("DeckIDs") or {}
    if [int(deck_ids[str(index)]) for index in range(len(EXPECTED_SUPPORT_CHILDREN))] != [row[0] for row in EXPECTED_SUPPORT_CHILDREN]:
        _fail(failures, "Support Equipment root DeckIDs")
    if len(root_data.get("CustomDeck") or {}) != 23:
        _fail(failures, "Support Equipment CustomDeck count")

    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    url_to_path = {row["url"]: "assets/tts-mod/extract/v2-dl/tree/" + row["file"] for row in manifest}
    objects = json.loads((repo / OBJECTS_PATH).read_text(encoding="utf-8"))
    classifications = {row.get("guid"): row for row in json.loads((repo / CLASSIFICATION_PATH).read_text(encoding="utf-8"))}
    provenance = json.loads((repo / PROVENANCE_PATH).read_text(encoding="utf-8"))
    provenance_by_url = {row.get("url"): row for row in provenance}
    corpus = json.loads((repo / CORPUS_PATH).read_text(encoding="utf-8"))
    corpus_by_path = {row.get("sourcePath"): row for row in corpus.get("records") or []}

    support_faces = idx.get("supportEquipmentFaces") or []
    if len(support_faces) != 24 or [row.get("rootSequence") for row in support_faces] != list(range(1, 25)):
        _fail(failures, "Support Equipment physical occurrence cardinality/order")
    if len({row.get("supportEquipmentOccurrenceId") for row in support_faces}) != 24 or len({row.get("copyId") for row in support_faces}) != 24:
        _fail(failures, "Support Equipment copy identity uniqueness")
    raw_by_guid = {row.get("GUID"): row for row in contained}
    support_by_guid = {row.get("ttsCardGuid"): row for row in support_faces}
    for card_id, guid in EXPECTED_SUPPORT_CHILDREN:
        face = support_by_guid.get(guid) or {}
        raw_face = raw_by_guid.get(guid) or {}
        if face.get("ttsCardId") != card_id or face.get("ttsRootGuid") != "f71196" or face.get("sourceSelector", {}).get("fullCardId") != card_id or face.get("sourceSelector", {}).get("guid") != guid:
            _fail(failures, "Support exact CardID/GUID projection", guid=guid)
        if face.get("physicalClass") != EXPECTED_SUPPORT_CLASSES.get(guid) or face.get("itemSourceClass") != "support-equipment":
            _fail(failures, "Support exact physical class projection", guid=guid)
        if face.get("sourcePath") and (not (repo / face["sourcePath"]).is_file() or _sha(repo / face["sourcePath"]) != face.get("sourceSha256")):
            _fail(failures, "Support live face path/hash", guid=guid)
        custom = (raw_face.get("CustomDeck") or {})
        selector_custom_id = face.get("customDeckId")
        if selector_custom_id not in custom and str(selector_custom_id) not in custom:
            # The child carries a parent deck reference; the root deck table is
            # the authoritative URL selector for CardCustom occurrences.
            root_custom = root_data.get("CustomDeck") or {}
            custom_row = root_custom.get(str(selector_custom_id)) or root_custom.get(selector_custom_id)
        else:
            custom_row = custom.get(selector_custom_id) or custom.get(str(selector_custom_id))
        if not custom_row:
            custom_row = (root_data.get("CustomDeck") or {}).get(str(selector_custom_id))
        if custom_row and face.get("sourceSelector", {}).get("url") != custom_row.get("FaceURL"):
            _fail(failures, "Support FaceURL selector projection", guid=guid)
        if face.get("sourceSelector", {}).get("backUrl") != custom_row.get("BackURL") if custom_row else False:
            _fail(failures, "Support BackURL selector projection", guid=guid)
        if face.get("sourceSelector", {}).get("cardIdModuloJoinUsed") is not False or face.get("sourceSelector", {}).get("selectorGap") is not None:
            _fail(failures, "Support prohibited modulo/gap join flags", guid=guid)
        expected_cell = EXPECTED_GENERATED_CELLS.get(guid)
        selector = face.get("sourceSelector", {})
        if expected_cell is None:
            if selector.get("generatedSpriteSheetCell") is not False or selector.get("generatedCell") is not None:
                _fail(failures, "Support direct/generated selector inversion", guid=guid)
        elif selector.get("generatedSpriteSheetCell") is not True or selector.get("generatedCell") != expected_cell or selector.get("sourceSheetPath") != "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144.jpg" or selector.get("sourceSheetGrid") != {"columns": 6, "rows": 3, "cellWidth": 591, "cellHeight": 863}:
            _fail(failures, "Support generated sheet/hash/grid/cell selector", guid=guid)
        corpus_row = corpus_by_path.get(face.get("sourcePath")) or {}
        if (corpus_row.get("printedData") or {}).get("body") != face.get("printedBody"):
            _fail(failures, "Support exact body/punctuation projection", guid=guid)
        expected_title = (corpus_row.get("printedData") or {}).get("title") or (corpus_row.get("identity") or {}).get("titleFromCanonicalSlug")
        if expected_title and face.get("printedTitle") != expected_title.upper():
            _fail(failures, "Support exact title projection", guid=guid)
        if face.get("ttsGmNotes") != raw_face.get("GMNotes", ""):
            _fail(failures, "Support GMNotes provenance", guid=guid)
        if face.get("ttsObjectDescription") != raw_face.get("Description", ""):
            _fail(failures, "Support TTS object-description provenance", guid=guid)
        if face.get("sourceId") not in source_by_id:
            _fail(failures, "Support source registry face", guid=guid)

    assets = idx.get("supportSourceFaceAssets") or []
    if len(assets) != 40 or sum(bool(row.get("selectorGap")) for row in assets) != 16 or sum(row.get("sourceRole") == "generated-selected-support-face" for row in assets) != 2:
        _fail(failures, "Support source asset/gap partition")
    sheet = idx.get("supportSourceSheet") or {}
    if sheet.get("selectedCells") != [10, 17] or sheet.get("selectorGapCells") != [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16] or sheet.get("parentSheetNotRulesFace") is not True:
        _fail(failures, "Support sheet selected/gap closure")
    if sheet.get("sourcePath") and _sha(repo / sheet["sourcePath"]) != sheet.get("sourceSha256"):
        _fail(failures, "Support parent sheet hash")
    for asset in assets:
        if asset.get("sourcePath") and (repo / asset["sourcePath"]).is_file() and _sha(repo / asset["sourcePath"]) != asset.get("sourceSha256"):
            _fail(failures, "Support source asset hash", assetId=asset.get("assetId"))
        if asset.get("selectorGap") and asset.get("sourceId") in source_by_id:
            registry = source_by_id[asset["sourceId"]]
            if registry.get("path") != asset.get("sourcePath") or registry.get("sha256") != asset.get("sourceSha256"):
                _fail(failures, "Support gap source registry tuple", assetId=asset.get("assetId"))

    character_faces = idx.get("characterItemTtsFaces") or []
    actual_character_tuples = [(row.get("ttsCharacterKitOwner"), row.get("ttsCardGuid"), row.get("ttsCardId")) for row in character_faces]
    if actual_character_tuples != EXPECTED_CHARACTER_TUPLES:
        _fail(failures, "Character kit occurrence tuple closure", actual=actual_character_tuples, expected=EXPECTED_CHARACTER_TUPLES)
    if sum(row.get("semanticRuleId") is not None for row in character_faces) != 5 or sum(row.get("semanticRuleId") is None for row in character_faces) != 2:
        _fail(failures, "Character prototype/source-clear partition")
    bag_guids = {"Combat Engineer": "284e9d", "Heavy Gun Operator": "6219a2", "Medical Support": "79d6b1", "Contractor": "47658d", "Officer": "6031da", "Recon": "8a007f"}
    for row in character_faces:
        guid = row.get("ttsCardGuid")
        owner = row.get("ttsCharacterKitOwner")
        obj = next((item for item in objects if item.get("guid") == guid), {})
        if ["Bag", bag_guids.get(owner), owner] not in (obj.get("parent") or []):
            _fail(failures, "Character exact kit ancestry", guid=guid)
        if classifications.get(guid, {}).get("verdict") != "base":
            _fail(failures, "Character base classification", guid=guid)
        if row.get("sourcePath") and _sha(repo / row["sourcePath"]) != row.get("sourceSha256"):
            _fail(failures, "Character live face hash", guid=guid)
        if row.get("physicalClass") != EXPECTED_CHARACTER_CLASSES.get(guid) or row.get("itemSourceClass") != "character-item":
            _fail(failures, "Character exact physical class projection", guid=guid)
        corpus_row = corpus_by_path.get(row.get("sourcePath")) or {}
        if (corpus_row.get("printedData") or {}).get("body") != row.get("printedBody"):
            _fail(failures, "Character exact body/punctuation projection", guid=guid)
        expected_title = (corpus_row.get("printedData") or {}).get("title") or (corpus_row.get("identity") or {}).get("titleFromCanonicalSlug")
        if expected_title and row.get("printedTitle") != expected_title.upper():
            _fail(failures, "Character exact title projection", guid=guid)
        if row.get("sourceSelector", {}).get("cardIdModuloJoinUsed") is not False:
            _fail(failures, "Character prohibited modulo join", guid=guid)
        raw_character_face = _find_guid(raw.get("ObjectStates"), guid) or {}
        if row.get("ttsObjectDescription") != raw_character_face.get("Description", ""):
            _fail(failures, "Character TTS object-description provenance", guid=guid)
        if row.get("semanticRuleId") and row.get("semanticRuleId") not in record_by_id:
            _fail(failures, "Character semantic dispatch record", guid=guid)

    conflicts = idx.get("physicalClassConflictExclusions") or []
    if len(conflicts) != 12 or any(row.get("semanticDispatchProhibited") is not True or not row.get("questionId") for row in conflicts):
        _fail(failures, "Equipment class-conflict exclusion closure")
    dispatch_payload = json.dumps({key: value for key, value in record_by_id.items() if "VARIANT-BOUNDARIES" not in key}, ensure_ascii=False)
    if any((row.get("redItemOccurrenceId") or row.get("yellowItemOccurrenceId")) in dispatch_payload for row in conflicts):
        _fail(failures, "Class-conflict occurrence leaked into semantic dispatch")
    color_heavy = idx.get("colorRootHeavyFaces") or []
    if len(color_heavy) != 10 or any(row.get("batchDisposition") != "included-source-clear-heavy-item-face" for row in color_heavy):
        _fail(failures, "Color Heavy inclusion closure")
    if any(row.get("semanticRuleId") not in record_by_id for row in color_heavy):
        _fail(failures, "Color Heavy semantic dispatch records")

    for row in idx.get("sharedBacks") or []:
        if row.get("rulesFaceCounted") is not False or row.get("sourcePath") and _sha(repo / row["sourcePath"]) != row.get("sourceSha256"):
            _fail(failures, "Equipment back non-operative/hash closure", sourceId=row.get("sourceId"))
    official = idx.get("officialVisibleOccurrences") or []
    if len(official) != 6 or sum(row.get("itemSourceClass") == "character-item" for row in official) != 2 or sum(row.get("itemSourceClass") == "support-equipment" for row in official) != 3:
        _fail(failures, "Official Equipment visible occurrence partition")
    if any(row.get("ttsPhysicalCrosswalkAsserted") is not False for row in official):
        _fail(failures, "Official-to-TTS crosswalk boundary")
    for row in official:
        if row.get("semanticRuleId") not in record_by_id:
            _fail(failures, "Official Equipment semantic record", occurrenceId=row.get("officialOccurrenceId"))

    expected_reusable = {"SEM-CHARACTER-ITEM-SETUP-001", "SEM-SUPPORT-EQUIPMENT-DRAFT-001", "SEM-HEAVY-ITEM-HAND-CAPACITY-001", "SEM-ARMOR-ITEM-LIFECYCLE-001", "SEM-EQUIPMENT-FULLY-LOADED-001", "SEM-HEAVY-ITEM-USE-001", "SEM-HEAVY-ITEM-ONE-USE-001", "SEM-ITEM-PASSIVE-EFFECT-001", "SEM-ITEM-LOSS-ATTACHED-GEAR-001", "SEM-WEAPON-MALFUNCTION-LIFECYCLE-001", "SEM-WEAPON-DIE-RESULT-ADDITION-001", "SEM-GRENADE-LAUNCHER-MALFUNCTION-001", "SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001", "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001"}
    expected_face_rules = {row.get("semanticRuleId") for row in support_faces} | {row.get("semanticRuleId") for row in character_faces if row.get("semanticRuleId")} | {row.get("semanticRuleId") for row in color_heavy}
    expected_official_rules = {row.get("semanticRuleId") for row in official}
    if not expected_reusable.issubset(record_by_id) or not expected_face_rules.issubset(record_by_id) or not expected_official_rules.issubset(record_by_id):
        _fail(failures, "Equipment semantic record family closure")
    for number in range(79, 97):
        qid = f"SEM-Q-{number:03d}"
        row = question_by_id.get(qid) or {}
        if row.get("defaultProhibited") is not True or len(row.get("alternatives") or []) < 3:
            _fail(failures, "Equipment no-default question closure", questionId=qid)
    if not {f"SC-{number:03d}" for number in range(70, 81)}.issubset({row.get("conflictId") for row in conflict_rows}):
        _fail(failures, "Equipment conflict closure")
    equipment_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "base Heavy, Support Equipment, Weapon, Armor, and Character Starting Item family"), {})
    if set(equipment_system.get("ruleIds") or []) != expected_reusable | expected_face_rules | expected_official_rules:
        _fail(failures, "Equipment coverage system closure")
    if any(fragment in " ".join(coverage.get("notYetCovered") or []) for fragment in ("seven Heavy Green occurrences", "three explicit Heavy Red occurrences", "source-clear Heavy/Equipment/Weapon/Armor/Starting Item occurrences")):
        _fail(failures, "Equipment stale not-yet-covered claim")

    linked = set(idx.get("familyCountEvidence", {}).get("backlog", {}).get("linkedUnitIds") or [])
    if len(linked) != 84 or any((backlog_rows_by_id.get(unit_id) or {}).get("status") != "pilot-covered" for unit_id in linked if unit_id.startswith(("RULE:", "FAQ:", "VIS:"))):
        _fail(failures, "Equipment linked backlog obligations")

    return {
        "supportFaces": support_faces,
        "supportAssets": assets,
        "characterFaces": character_faces,
        "colorHeavy": color_heavy,
        "conflicts": conflicts,
        "official": official,
        "reusableRuleIds": sorted(expected_reusable),
        "faceRuleIds": sorted(expected_face_rules),
        "officialRuleIds": sorted(expected_official_rules),
        "allRuleIds": sorted(expected_reusable | expected_face_rules | expected_official_rules),
        "linkedBacklogIds": sorted(linked),
    }
