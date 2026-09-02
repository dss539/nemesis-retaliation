from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from PIL import Image


PINNED_OBJECTIVE_SOURCE_INDEX_HASH = "f9000de68c79a786c2d4ea33f6f3f65fb45fe0350b79ca241346e62c2b9070d9"
EXPECTED_COUNTS_DIGEST = "76532bd7b0475db0ccea0e27034591083893eb5b149ec1ed9773d4f9abaa34b4"
EXPECTED_PHYSICAL_PROJECTION_DIGEST = "caeed72fb2f824f56ac5f214970e67aa84d2ee66b93d7b03142209a2391946f7"
EXPECTED_EXCLUDED_PHYSICAL_PROJECTION_DIGEST = "dc6a94ceadb3667a6155eab774c7e63950219c1613c455bad80ffd138a8cae4f"
EXPECTED_ASSET_PROJECTION_DIGEST = "5328131914846c7201e642724ca4f56d84f14a02d08a20135e504cb7481691b2"
EXPECTED_ROOT_PROJECTION_DIGEST = "818984a87621e8637b19020ea2c08a4162ca69a0fc505e23b0573530d2f8ee5e"
EXPECTED_SHEET_BACK_PROJECTION_DIGEST = "c9c571a35b69284e1a4a69acc9938c667d3026dbbc4705bfb7ee8b0add483931"
EXPECTED_OFFICIAL_PROJECTION_DIGEST = "f2e1cebbcdf3abece19c67436f2696c4c971ce9899da394c408677e05e703c2f"
EXPECTED_LICENSED_PROJECTION_DIGEST = "c6e1fcde362f21276084c88812ab4c8d51b49e447178129d989d1da456e05c39"
EXPECTED_RECORD_ID_DIGEST = "03f1194754afe1d6153da716364ab7c113e489d69fcd4db7eb59c57a27086a3c"
EXPECTED_RECORD_PROJECTION_DIGEST = "6042fba7e64cbf7ffb17dbec26848d44464ef113354fad5a8e30be306e5a6338"
EXPECTED_QUESTION_PROJECTION_DIGEST = "31ca5b8c016549864f05ced4f6da4d2d9bce1cb4f730de25cfa814c03ec2968e"
EXPECTED_CONFLICT_PROJECTION_DIGEST = "e113b495085c89f8723e41a290c0e08b7954cb6a4104da75ed00f1109eb71576"
EXPECTED_LINKED_BACKLOG_ID_DIGEST = "dfa79ab6dd5f909a921438794c6d054c912bbe203c196a845483f8238394a407"

OBJECTIVE_REUSABLE_IDS = [
    "SEM-OBJECTIVE-SETUP-001",
    "SEM-OBJECTIVE-SECRECY-001",
    "SEM-OBJECTIVE-FULFILLMENT-001",
    "SEM-OBJECTIVE-SURVIVOR-001",
    "SEM-OBJECTIVE-ESCAPE-001",
    "SEM-FACILITY-DESTRUCTION-001",
    "SEM-OBJECTIVE-FACE-CHECK-001",
    "SEM-MISSION-TASK-CHECK-001",
    "SEM-OBJECTIVE-VARIANT-BOUNDARIES-001",
]
OBJECTIVE_QUESTION_IDS = ["SEM-Q-075", "SEM-Q-076", "SEM-Q-077", "SEM-Q-078"]
OBJECTIVE_CONFLICT_IDS = [f"SC-{number:03d}" for number in range(59, 70)]

EXPECTED_HEADLINE_COUNTS = {
    "officialObjectiveCards": 22,
    "officialMissionObjectiveCards": 7,
    "officialPrivateObjectiveCards": 15,
    "officialMissionTaskCards": 8,
    "officialSoloCoopObjectiveCards": 12,
    "baseCompetitivePhysicalOccurrences": 30,
    "baseMissionObjectivePhysicalOccurrences": 7,
    "basePrivateObjectivePhysicalOccurrences": 15,
    "baseMissionTaskPhysicalOccurrences": 8,
    "sourceClearPhysicalOccurrences": 29,
    "sourceBlockedPhysicalOccurrences": 1,
    "generatedPhysicalOccurrences": 16,
    "directPhysicalOccurrences": 14,
    "prototypeHighCountPhysicalExclusions": 9,
    "soloCoopTtsRootOccurrencesExcluded": 38,
    "sourceFaceAssets": 50,
    "baseSelectedSourceFaceAssets": 27,
    "baseSelectorGapSourceFaceAssets": 18,
    "sourceSheets": 2,
    "sourceSheetCells": 31,
    "baseSelectedGeneratedCells": 13,
    "baseSelectorGapCells": 18,
    "sharedBacks": 2,
    "officialHelpUnits": 45,
    "officialHelpFullyVisibleUnits": 35,
    "officialHelpOccludedUnits": 10,
    "officialHelpVisibleCardUnits": 20,
    "officialHelpVisibleFunctionalIcons": 50,
    "officialHelpPartiallyVisibleIcons": 5,
    "licensedRows": 38,
    "licensedCompetitiveRows": 26,
    "licensedSoloCoopRowsExcluded": 12,
    "semanticPhysicalFaceRecords": 29,
    "semanticOfficialVisibleFaceRecords": 20,
    "semanticLicensedCompetitiveRecords": 26,
    "cardBacklogTuples": 50,
    "objectiveHelpBacklogUnits": 45,
    "overlappingBacklogObligationsLinked": 102,
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def _physical_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "category", "role", "rootGuid", "rootSequence", "fullCardId", "guid", "ttsGmNotesMinimum",
        "generatedCell", "disposition", "effectKind", "copyId", "deckId", "sourceId", "occurrenceId",
        "semanticRuleId", "sourcePath", "sourceSha256", "sourceSelector", "playerCountMetadata", "backlogUnitId",
        "printedTitle", "printedCondition", "printedFooter", "printedTypeLine", "objectiveChoiceInstruction",
        "panels", "sentences", "iconOccurrences", "checkboxPanels", "conditionConnectorCounts", "conditionTree",
        "representationBoundary", "identityJoinEvidence", "privatePersonalAliasProjection", "namedIdentityRef",
    ]}


def _asset_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "assetId", "sourceId", "sourcePath", "sourceSha256", "sourceRole", "sourceSheetId", "sourceSheetPath",
        "sourceSheetSha256", "sourceSheetGrid", "customDeckId", "generatedCell", "selectedBasePhysicalOccurrenceIds",
        "selectedPrototypePhysicalOccurrenceIds", "baseSelectorGap", "backlogUnitId", "corpusExtractionState", "effectKind",
        "printedTitle", "printedCondition", "printedFooter", "printedTypeLine", "objectiveChoiceInstruction",
        "visiblePrintedPlayerCount", "sourceSections", "panels", "sentences", "iconOccurrences", "checkboxPanels",
        "conditionTree", "conditionConnectorCounts", "representationBoundary",
    ]}


def _official_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "sourceUnitId", "category", "visibility", "printedTitle", "printedCondition", "printedDefinition", "printedText",
        "printedFooter", "objectiveChoiceInstruction", "playerCountMetadata", "panels", "sentences", "iconOccurrences",
        "checkboxPanels", "conditionConnectorCounts", "conditionTree", "effectKind", "semanticRuleId", "boundaryRuleId",
        "associatedNotes", "sharedExplanatoryNoteSourceUnitId", "directlyVisibleTextFragments", "materialOccludedSpans",
        "occludedTextLayerMetadata", "visualEvidence", "occludedMetadataPromotedToVisibleEvidence", "backlogUnitId",
        "namedIdentityRef",
    ]}


def _licensed_projection(row: dict) -> dict:
    return {key: row.get(key) for key in [
        "key", "name", "assetType", "soloCoop", "desc", "effectDesc", "orEffectDesc", "conditionLines",
        "printedCondition", "sourceBlockText", "competitiveDisposition", "effectKind", "semanticRuleId", "conditionTree",
        "playerCountMetadata", "assertedTtsPhysicalIdentityLinks", "assertedOfficialOccurrenceIdentityLinks", "namedIdentityRef",
    ]}


def _tree_atoms(tree: dict | None) -> list[dict]:
    if not tree:
        return []
    rows = []
    for clause in tree.get("clauses") or []:
        if clause.get("operator") == "predicate":
            rows.append(clause)
        else:
            rows.extend(_tree_atoms(clause))
    return rows


def validate_objective_family(
    repo: Path,
    source_path: Path,
    source: dict,
    source_by_id: dict[str, dict],
    backlog_by_id: dict[str, dict],
    record_by_id: dict[str, dict],
    question_by_id: dict[str, dict],
    conflict_rows: list[dict],
    coverage: dict,
    failures: list[dict],
) -> dict:
    faces = source.get("physicalFaces") or []
    excluded = source.get("excludedPhysicalOccurrences") or []
    assets = source.get("sourceFaceAssets") or []
    roots = source.get("rootDeckEvidence") or []
    sheets = source.get("sourceSheets") or []
    backs = source.get("sharedBacks") or []
    official = source.get("officialHelpOccurrences") or []
    licensed = source.get("licensedDigitalOccurrences") or []
    solo_roots = source.get("excludedSoloCoopRoots") or []

    if _sha(source_path) != PINNED_OBJECTIVE_SOURCE_INDEX_HASH:
        failures.append({"check": "pinned Objective/Mission source index"})
    if _digest(source.get("counts")) != EXPECTED_COUNTS_DIGEST:
        failures.append({"check": "Objective/Mission exact family counts"})
    if any((source.get("counts") or {}).get(key) != value for key, value in EXPECTED_HEADLINE_COUNTS.items()):
        failures.append({"check": "Objective/Mission official/physical/source/licensed reconciliation"})

    occurrence_ids = [row.get("occurrenceId") for row in faces]
    copy_ids = [row.get("copyId") for row in faces]
    clear_rule_ids = [row.get("semanticRuleId") for row in faces if row.get("semanticRuleId")]
    if len(faces) != 30 or len(set(occurrence_ids)) != 30 or len(set(copy_ids)) != 30 or len(clear_rule_ids) != 29 or len(set(clear_rule_ids)) != 29:
        failures.append({"check": "Objective/Mission dropped/duplicated physical copy closure"})
    expected_partition = Counter({"mission-objective": 7, "private-objective": 15, "mission-task": 8})
    if Counter(row.get("category") for row in faces) != expected_partition:
        failures.append({"check": "Objective/Mission exact category/deck/copy partition"})
    if Counter(row.get("printedTitle") for row in faces if row.get("category") == "mission-objective") != Counter({"OFFICIAL ORDER": 5, "SELF-SERVING": 1, "ULTERIOR MOTIVE": 1}):
        failures.append({"check": "Objective repeated OFFICIAL ORDER/title multiplicity closure"})
    if len({row.get("printedTitle") for row in faces if row.get("category") == "private-objective"}) != 15 or len({row.get("printedTitle") for row in faces if row.get("category") == "mission-task"}) != 8:
        failures.append({"check": "Objective/Task title/category collapse prohibited"})
    if _digest([_physical_projection(row) for row in faces]) != EXPECTED_PHYSICAL_PROJECTION_DIGEST:
        failures.append({"check": "Objective/Mission exact physical tuple/panel/text/icon/condition projection"})
    if len(excluded) != 9 or _digest([_physical_projection(row) for row in excluded]) != EXPECTED_EXCLUDED_PHYSICAL_PROJECTION_DIGEST:
        failures.append({"check": "Objective prototype/high-count exact physical exclusion closure"})

    facility = next((row for row in faces if row.get("sourcePath", "").endswith("missionTaskDeck-023.png")), {})
    if facility.get("semanticRuleId") is not None or facility.get("disposition") != "base-competitive-source-blocked" or facility.get("printedCondition", "").count("[illegible]") != 1:
        failures.append({"check": "Objective FACILITY RESTART source-blocker/no-substitution lock"})

    if len(assets) != 50 or len({row.get("sourcePath") for row in assets}) != 50 or _digest([_asset_projection(row) for row in assets]) != EXPECTED_ASSET_PROJECTION_DIGEST:
        failures.append({"check": "Objective/Mission exact 50 source-face asset closure"})
    if sum(row.get("baseSelectorGap") is not None for row in assets) != 18 or sum(bool(row.get("selectedBasePhysicalOccurrenceIds")) for row in assets) != 27:
        failures.append({"check": "Objective/Mission selected/gap/prototype asset partition"})
    for asset in assets:
        path = repo / str(asset.get("sourcePath") or "")
        if not path.is_file() or _sha(path) != asset.get("sourceSha256"):
            failures.append({"check": "Objective/Mission live source asset hash", "assetId": asset.get("assetId")})
        if asset.get("baseSelectorGap") and (asset["baseSelectorGap"].get("cardIdModuloJoinUsed") is not False or asset.get("selectedBasePhysicalOccurrenceIds")):
            failures.append({"check": "Objective/Mission selector-gap/no-modulo closure", "assetId": asset.get("assetId")})

    if _digest(roots) != EXPECTED_ROOT_PROJECTION_DIGEST or len(roots) != 3:
        failures.append({"check": "Objective/Mission exact root/member tuple projection"})
    if len(solo_roots) != 2 or [row.get("physicalOccurrences") for row in solo_roots] != [12, 26] or any(row.get("includedInCompetitiveConclusions") is not False for row in solo_roots):
        failures.append({"check": "Objective Solo/Coop exact-root exclusion closure"})
    if _digest({"sheets": sheets, "backs": backs}) != EXPECTED_SHEET_BACK_PROJECTION_DIGEST:
        failures.append({"check": "Objective sheet/grid/cell/back role closure"})
    if len(sheets) != 2 or sum(len(row.get("baseSelectedCells") or []) for row in sheets) != 13 or sum(len(row.get("baseSelectorGapCells") or []) for row in sheets) != 18:
        failures.append({"check": "Objective sheet/cell/base-selector partition"})
    if len(backs) != 2 or [row.get("globalReferenceCount") for row in backs] != [33, 11] or any(row.get("rulesFaceCounted") is not False for row in backs):
        failures.append({"check": "Objective shared-back non-operative/reference closure"})

    # Recheck every generated crop independently against exact parent pixels.
    for sheet in sheets:
        grid = sheet["grid"]
        with Image.open(repo / sheet["sourcePath"]) as parent:
            cells = grid["columns"] * grid["rows"]
            for cell in range(cells):
                path = repo / next(row["sourcePath"] for row in assets if row.get("customDeckId") == sheet["customDeckId"] and row.get("generatedCell") == cell)
                row_index, column_index = divmod(cell, grid["columns"])
                crop = parent.crop((column_index * grid["cellWidth"], row_index * grid["cellHeight"], (column_index + 1) * grid["cellWidth"], (row_index + 1) * grid["cellHeight"])).convert("RGB")
                with Image.open(path) as generated:
                    if generated.convert("RGB").tobytes() != crop.tobytes():
                        failures.append({"check": "Objective generated sheet/hash/grid/cell pixel lock", "customDeckId": sheet["customDeckId"], "cell": cell})

    for face in [*faces, *excluded]:
        selector = face.get("sourceSelector") or {}
        join = face.get("identityJoinEvidence") or {}
        if (
            selector.get("fullCardId") != face.get("fullCardId")
            or selector.get("guid") != face.get("guid")
            or selector.get("parentDeckGuid") != face.get("rootGuid")
            or selector.get("url") == selector.get("backUrl")
            or selector.get("cardIdModuloJoinUsed") is not False
            or join.get("identityJoin") != "exact raw root physical occurrence and exact source-asset projection"
            or any(join.get(key) is not False for key in (
                "titleOnlyJoin", "bodySimilarityJoin", "categoryLabelOnlyJoin", "privatePersonalGlobalAliasJoin",
                "folderOnlyJoin", "sourceOrderOnlyJoin", "sourceSheetOnlyJoin", "generatedCellOnlyJoin",
                "cardIdModuloJoin", "licensedKeyJoin", "officialHelpTitleJoin",
            ))
        ):
            failures.append({"check": "Objective title/body/category/alias/folder/order/sheet/cell/modulo join prohibited", "occurrenceId": face.get("occurrenceId")})
        if selector.get("url") == selector.get("backUrl"):
            failures.append({"check": "Objective selector/back inversion", "occurrenceId": face.get("occurrenceId")})
        if selector.get("generatedSpriteSheetCell") and (selector.get("sourceSheetPath") is None or selector.get("generatedCell") is None):
            failures.append({"check": "Objective exact generated selector closure", "occurrenceId": face.get("occurrenceId")})
        registry = source_by_id.get(face.get("sourceId")) or {}
        if (registry.get("path"), registry.get("sha256"), registry.get("occurrenceId"), registry.get("authority")) != (face.get("sourcePath"), face.get("sourceSha256"), face.get("occurrenceId"), "source-bound-component-scan"):
            failures.append({"check": "Objective source-registry exact physical tuple", "occurrenceId": face.get("occurrenceId")})
        panel_ids = [row.get("panelId") for row in face.get("panels") or []]
        if [row.get("readingOrder") for row in face.get("panels") or []] != list(range(1, len(panel_ids) + 1)) or len(panel_ids) != len(set(panel_ids)) or any(row.get("panelId") not in panel_ids for row in face.get("sentences") or []):
            failures.append({"check": "Objective panel/body/punctuation/order closure", "occurrenceId": face.get("occurrenceId")})
        alias = face.get("privatePersonalAliasProjection") or {}
        if face.get("category") == "private-objective" and face.get("printedFooter") == "PERSONAL OBJECTIVE" and (alias.get("aliasId") != "AL-003" or alias.get("globalAliasUsed") is not False):
            failures.append({"check": "Objective Private/Personal exact-source alias closure", "occurrenceId": face.get("occurrenceId")})

    if len(official) != 45 or _digest([_official_projection(row) for row in official]) != EXPECTED_OFFICIAL_PROJECTION_DIGEST:
        failures.append({"check": "Objective exact official Help visible/occluded projection"})
    if Counter(row.get("visibility") for row in official) != Counter({"fully-visible": 35, "partially-occluded": 10}):
        failures.append({"check": "Objective Help exact 35-visible/10-occluded partition"})
    occluded = [row for row in official if row.get("visibility") == "partially-occluded"]
    if len(occluded) != 10 or any(row.get("semanticRuleId") is not None or row.get("boundaryRuleId") != "SEM-OBJECTIVE-VARIANT-BOUNDARIES-001" or row.get("occludedMetadataPromotedToVisibleEvidence") is not False for row in occluded):
        failures.append({"check": "Objective occluded-text non-promotion lock"})
    visible_cards = [row for row in official if row.get("category") in {"mission-objective", "private-objective", "mission-task"} and row.get("visibility") == "fully-visible"]
    if len(visible_cards) != 20 or sum(len(row.get("iconOccurrences") or []) for row in official) != 55:
        failures.append({"check": "Objective official visible card/icon occurrence closure"})
    if sum(sum(icon.get("semanticReferenceId") == "icon.numberOfCharacters" for icon in row.get("iconOccurrences") or []) for row in visible_cards) != 20:
        failures.append({"check": "Objective official Number-of-Characters metadata projection"})
    escort_official = next((row for row in official if row.get("sourceUnitId") == "P1-MT-ESCORT-MISSION"), {})
    if not escort_official.get("checkboxPanels") or [icon.get("semanticReferenceId") for icon in escort_official.get("iconOccurrences") or []] != ["icon.numberOfCharacters", None, "icon.robot", "icon.character"]:
        failures.append({"check": "Objective checkbox/Robot/Character/icon order lock"})

    if len(licensed) != 38 or _digest([_licensed_projection(row) for row in licensed]) != EXPECTED_LICENSED_PROJECTION_DIGEST:
        failures.append({"check": "Objective exact independent licensed row/variant closure"})
    if Counter(row.get("competitiveDisposition") for row in licensed) != Counter({"base-competitive-licensed-occurrence": 26, "solo-coop-excluded": 12}) or any(row.get("assertedTtsPhysicalIdentityLinks") or row.get("assertedOfficialOccurrenceIdentityLinks") for row in licensed):
        failures.append({"check": "Objective licensed competitive/Solo-Coop/no-crosswalk closure"})
    bga_registry = source_by_id.get("SRC-BGA-OBJECTIVES-MISSIONS") or {}
    if bga_registry.get("occurrenceId") != "MISSIONS_OBJECTIVES_DATA" or bga_registry.get("authority") != "licensed-digital-secondary":
        failures.append({"check": "Objective licensed source-registry closure"})

    expected_record_ids = sorted(set(["SEM-RT-010", *OBJECTIVE_REUSABLE_IDS, *clear_rule_ids, *[row["semanticRuleId"] for row in official if row.get("effectKind")], *[row["semanticRuleId"] for row in licensed if row.get("semanticRuleId")]]))
    if len(expected_record_ids) != 85 or _digest(expected_record_ids) != EXPECTED_RECORD_ID_DIGEST:
        failures.append({"check": "Objective independently locked semantic rule-ID set"})
    if any(rule_id not in record_by_id for rule_id in expected_record_ids):
        failures.append({"check": "Objective semantic record closure"})
    if _digest([record_by_id.get(rule_id) for rule_id in expected_record_ids]) != EXPECTED_RECORD_PROJECTION_DIGEST:
        failures.append({"check": "Objective independently locked ordered semantic atoms"})

    for face in faces:
        if not face.get("semanticRuleId"):
            continue
        semantic = record_by_id.get(face["semanticRuleId"]) or {}
        exact = next((row for row in semantic.get("sourceAssertions") or [] if row.get("sourceId") == face.get("sourceId")), {})
        if (exact.get("sourceText"), exact.get("sourceSha256"), exact.get("textKind")) != (face.get("printedCondition"), face.get("sourceSha256"), "verbatim"):
            failures.append({"check": "Objective exact face/body/punctuation semantic assertion", "ruleId": face.get("semanticRuleId")})
        operation_condition_ids = [row.get("sourceConditionId") for row in semantic.get("operations") or [] if row.get("sourceConditionId")]
        expected_condition_ids = [row.get("conditionId") for row in _tree_atoms(face.get("conditionTree"))]
        if operation_condition_ids != expected_condition_ids:
            failures.append({"check": "Objective semantic condition/AND-OR/order projection", "ruleId": face.get("semanticRuleId")})

    objective_dispatch = record_by_id.get("SEM-OBJECTIVE-FACE-CHECK-001") or {}
    mission_dispatch = record_by_id.get("SEM-MISSION-TASK-CHECK-001") or {}
    actual_objective_dispatch = next((row.get("dispatchRuleIds") for row in objective_dispatch.get("operations") or [] if row.get("dispatchRuleIds")), None)
    actual_mission_dispatch = next((row.get("dispatchRuleIds") for row in mission_dispatch.get("operations") or [] if row.get("dispatchRuleIds")), None)
    expected_objective_dispatch = [row["semanticRuleId"] for row in faces if row.get("semanticRuleId") and row.get("category") != "mission-task"] + [row["semanticRuleId"] for row in official if row.get("effectKind") and row.get("category") != "mission-task"] + [row["semanticRuleId"] for row in licensed if row.get("semanticRuleId") and row.get("assetType") in {"shared", "private"}]
    expected_mission_dispatch = [row["semanticRuleId"] for row in faces if row.get("semanticRuleId") and row.get("category") == "mission-task"] + [row["semanticRuleId"] for row in official if row.get("effectKind") and row.get("category") == "mission-task"] + [row["semanticRuleId"] for row in licensed if row.get("semanticRuleId") and row.get("assetType") == "mission"]
    if actual_objective_dispatch != expected_objective_dispatch or actual_mission_dispatch != expected_mission_dispatch:
        failures.append({"check": "Objective/Task exact occurrence dispatcher/no-leakage lock"})

    secrecy = record_by_id.get("SEM-OBJECTIVE-SECRECY-001") or {}
    secrecy_text = json.dumps(secrecy, ensure_ascii=False)
    if not all(fragment in secrecy_text for fragment in ("owner-private", "showing", "discussion", "lying", "logs", "accessibility", "spectators", "removed Objective")) or any(row.get("audience") == "public" for row in secrecy.get("informationPolicy") or [] if row.get("informationId") != "I-END-RESULT"):
        failures.append({"check": "Objective private identity/removal/inspection/no-exposure lock"})
    choice = record_by_id.get("SEM-RT-010") or {}
    if [row.get("operationType") for row in choice.get("operations") or []] != ["choose", "transition-zone", "set-state", "change-value", "invoke-process"] or (choice.get("operations") or [{}])[-1].get("repeat", {}).get("drawCountByChoiceOrdinal") != {"1": 3, "2": 2, "3": 2, "4": 1, "5": 1} or (choice.get("operations") or [{}])[-1].get("repeat", {}).get("markerReadTiming") != "after moving marker down by one if possible":
        failures.append({"check": "Objective Choice post-move track/draw/lifecycle lock"})
    setup = record_by_id.get("SEM-OBJECTIVE-SETUP-001") or {}
    setup_text = json.dumps(setup, ensure_ascii=False)
    if not all(fragment in setup_text for fragment in ("7 + 15 + 8", '"2": {"missionObjective": 7, "privateObjective": 7}', "one public Mission Task")):
        failures.append({"check": "Objective finite setup/deck-exhaustion lock"})
    endgame = record_by_id.get("SEM-ENDGAME-001") or {}
    if endgame.get("unresolvedQuestionRefs") != ["OQ-001", "SEM-Q-077", "SEM-Q-078"] or [row.get("operationType") for row in (endgame.get("operations") or [])[4:]] != ["resolve-open-alternative", "choose", "transition-zone", "set-state", "resolve-open-alternative", "reveal", "invoke-process", "set-state"]:
        failures.append({"check": "Objective late-choice/reveal/endgame lifecycle lock"})

    objective_questions = [question_by_id.get(qid) or {} for qid in OBJECTIVE_QUESTION_IDS]
    if _digest(objective_questions) != EXPECTED_QUESTION_PROJECTION_DIGEST:
        failures.append({"check": "Objective ambiguity owner/timing/default projection"})
    for question in objective_questions:
        qid = question.get("questionId")
        actual_blocks = sorted(rule_id for rule_id, semantic in record_by_id.items() if qid in (semantic.get("unresolvedQuestionRefs") or []))
        if question.get("defaultProhibited") is not True or sorted(question.get("blocksRuleIds") or []) != actual_blocks or not actual_blocks:
            failures.append({"check": "Objective ambiguity owner/timing/default linkage", "questionId": qid})

    objective_conflicts = [row for row in conflict_rows if row.get("conflictId") in OBJECTIVE_CONFLICT_IDS]
    if _digest(objective_conflicts) != EXPECTED_CONFLICT_PROJECTION_DIGEST or [row.get("conflictId") for row in objective_conflicts] != OBJECTIVE_CONFLICT_IDS or Counter(row.get("status") for row in objective_conflicts) != Counter({"preserved-boundary": 9, "unresolved": 2}):
        failures.append({"check": "Objective exact conflict/variant/authority register closure"})

    expected_backlog_rules = {}
    for asset in assets:
        unit_id = asset["backlogUnitId"]
        if unit_id == "CARD:eaa728ca02c48c33":
            continue
        rules = [row["semanticRuleId"] for row in faces if row.get("semanticRuleId") and row.get("sourcePath") == asset.get("sourcePath")]
        expected_backlog_rules[unit_id] = rules or ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001"]
    for occurrence in official:
        rules = []
        if occurrence.get("semanticRuleId"):
            rules.append(occurrence["semanticRuleId"])
        if occurrence.get("boundaryRuleId"):
            rules.append(occurrence["boundaryRuleId"])
        if occurrence.get("sourceUnitId") == "P2-NOTE-RANKING-CHOICE":
            rules.extend(["SEM-OBJECTIVE-FULFILLMENT-001", "SEM-OBJECTIVE-OFFICIAL-P2-PO-WEVE-GOT-HISTORY-001"])
        expected_backlog_rules[occurrence["backlogUnitId"]] = list(dict.fromkeys(rules))
    for unit_id, rules in expected_backlog_rules.items():
        backlog = backlog_by_id.get(unit_id) or {}
        if backlog.get("pilotRuleIds") != rules or backlog.get("status") != "pilot-covered":
            failures.append({"check": "Objective exact card/Help backlog tuple projection", "semanticUnitId": unit_id})
    blocker = backlog_by_id.get("CARD:eaa728ca02c48c33") or {}
    if blocker.get("status") != "source-blocked" or blocker.get("pilotRuleIds"):
        failures.append({"check": "Objective exact inherited source blocker backlog lock"})
    linked_ids = source.get("familyCountEvidence", {}).get("backlog", {}).get("linkedUnitIds") or []
    if len(linked_ids) != 102 or _digest(linked_ids) != EXPECTED_LINKED_BACKLOG_ID_DIGEST:
        failures.append({"check": "Objective exact overlapping backlog-obligation closure"})
    if any((backlog_by_id.get(unit_id) or {}).get("status") not in {"pilot-covered", "source-blocked"} for unit_id in linked_ids):
        failures.append({"check": "Objective linked backlog status boundary"})

    expected_coverage_ids = [
        "SEM-RT-010",
        *OBJECTIVE_REUSABLE_IDS,
        *sorted(rule_id for rule_id in expected_record_ids if rule_id != "SEM-RT-010" and rule_id not in OBJECTIVE_REUSABLE_IDS),
    ]
    family_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "base competitive Objective and Mission Task family"), {})
    if family_system.get("ruleIds") != expected_coverage_ids or "fullBaseSemanticCoverageClaimed" in family_system:
        failures.append({"check": "Objective family coverage/no-full-coverage boundary"})
    not_yet = " ".join(coverage.get("notYetCovered") or [])
    if not all(fragment in not_yet for fragment in ("FACILITY RESTART", "physically occluded", "Solo/Coop", "not full" if False else "remaining")):
        failures.append({"check": "Objective exclusions/source-blocker coverage boundary"})

    return {
        "faces": faces,
        "excluded": excluded,
        "assets": assets,
        "roots": roots,
        "sheets": sheets,
        "backs": backs,
        "official": official,
        "licensed": licensed,
        "soloRoots": solo_roots,
        "physicalRuleIds": clear_rule_ids,
        "officialRuleIds": [row["semanticRuleId"] for row in official if row.get("effectKind")],
        "licensedRuleIds": [row["semanticRuleId"] for row in licensed if row.get("semanticRuleId")],
        "expectedRecordIds": expected_record_ids,
        "expectedBacklogRules": expected_backlog_rules,
        "linkedBacklogIds": linked_ids,
    }
