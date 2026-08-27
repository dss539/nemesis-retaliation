from __future__ import annotations

import hashlib
import json
from pathlib import Path

from semantic_combat_records import (
    COMBAT_DEPENDENCY_VISUAL_IDS,
    COMBAT_FAQ_IDS,
    COMBAT_NEW_RULE_IDS,
    COMBAT_PENDING_BACKLOG_IDS,
    COMBAT_QUESTION_IDS,
    COMBAT_REPLACED_RULE_IDS,
    COMBAT_VISUAL_IDS,
    FAQ_PATH,
    HELP_PATH,
    LUA_PATH,
    MANIFEST_PATH,
    OBJECTS_PATH,
    ROLES_PATH,
    SOURCE_SEGMENTS,
    VISUAL_PATH,
)


PINNED_COMBAT_SOURCE_INDEX_HASH = "1497b6ddcddf10672c02f25524f168494be3be26772717103f889f2c8c188173"
EXPECTED_COUNTS_DIGEST = "26d1b80d2c27d290c5554f4275174a38295617ab02554c379980f0178ca5491c"
EXPECTED_SOURCE_SEGMENT_DIGEST = "4225ec96135a28c1900522ecd713daff871e526085185fc7cc2cb9fe69b7958c"
EXPECTED_VISUAL_PROJECTION_DIGEST = "58ee8f34f31bb00b6f9f7afbab769d5fd9965f9645c57cac67bd6c9705663893"
EXPECTED_FAQ_PROJECTION_DIGEST = "6ce2d98742d0a6872916d823248162dddf70caf28eae9efcbf424978646bbfe5"
EXPECTED_HELP_PROJECTION_DIGEST = "03f1c08de3d21e2a284d55644a71192a764f9cf8259485f3571a03924455bd58"
EXPECTED_DICE_PROJECTION_DIGEST = "3dbb7b0afe7f38c20b14c02b5db07e4fb69675cad0db7eba0259cec27bd98084"
EXPECTED_CLASS_PROJECTION_DIGEST = "cfcd003c1187f484cb0d83928f9cf2babc50b61dfc214a1d4ff0f3386cc4e3bd"
EXPECTED_RECORD_PROJECTION_DIGEST = "004f7c669603a3b5786ae9a1525a90aaf14401fe60b0dbc0b0126cf1f23db2cb"
EXPECTED_QUESTION_PROJECTION_DIGEST = "22ae39a5b3141222060fcabadc3d950afffe8075951422c972740d42dd833f61"
EXPECTED_CONFLICT_PROJECTION_DIGEST = "9dfd271e4c55cb61ba591d13388741b841fb3578951d73b50f78669e79076454"
EXPECTED_BACKLOG_PROJECTION_DIGEST = "bc21396810544046e10852fa837dece518e55a211a6b49d2bf7819d999881a91"

COMBAT_PINNED_RULE_IDS = sorted(set([
    *COMBAT_NEW_RULE_IDS,
    *COMBAT_REPLACED_RULE_IDS,
    "SEM-IH-QA-C-02",
    "SEM-IH-QD-C-02",
    "SEM-IH-QA-BOTTOM-01",
    "SEM-IH-QD-BOTTOM-01",
    "SEM-REACTION-DUCK-001",
    "SEM-ROOM-10",
    "SEM-RT-011",
]))

EXPECTED_TOKEN_BACK_RESULTS = {
    "2": {"adultCount": 2, "droneCount": 0},
    "3": {"adultCount": 3, "droneCount": 0},
    "4": {"adultCount": 4, "droneCount": 0},
    "1+1": {"adultCount": 1, "droneCount": 1},
    "2+1": {"adultCount": 2, "droneCount": 1},
    "3+1": {"adultCount": 3, "droneCount": 1},
}

EXPECTED_NOISE_RESULTS = [
    {"termId": "icon.noiseDie1", "resultClass": "corridor-number", "corridorValue": 1},
    {"termId": "icon.noiseDie2", "resultClass": "corridor-number", "corridorValue": 2},
    {"termId": "icon.noiseDie3", "resultClass": "corridor-number", "corridorValue": 3},
    {"termId": "icon.noiseDie4", "resultClass": "corridor-number", "corridorValue": 4},
    {"termId": "icon.noiseDieHazard", "resultClass": "hazard", "corridorValue": None},
]

EXPECTED_SHOOT_RESULTS = [
    {"termId": "icon.shootDieCritical", "standardResult": "critical-kill"},
    *[
        {"termId": f"icon.shootDie{value}", "standardResult": "kill-if-result-at-or-below-current-Hits", "value": value}
        for value in (2, 3, 4, 5)
    ],
    {"termId": "icon.shootDieAmmoLoss", "standardResult": "spend-one-Ammo-use"},
]

EXPECTED_MELEE_RESULTS = [
    {"termId": "icon.shootDieCritical", "standardResult": "critical-kill"},
    *[
        {"termId": f"icon.shootDie{value}", "standardResult": "kill-if-result-at-or-below-current-Hits", "value": value}
        for value in (2, 3, 4, 5)
    ],
    {"termId": "icon.shootDieAmmoLoss", "standardResult": "ineffective-no-effect-no-Ammo-spend"},
]

EXPECTED_BURST_RESULTS = [
    {"termId": f"icon.burstDie{value}", "hits": value, "additionalEffects": value == 4}
    for value in (1, 2, 3, 4)
]

EXPECTED_MARKER_DISPATCH = [
    "SEM-IH-QA-C-01", "SEM-IH-QA-C-02", "SEM-IH-QA-C-03", "SEM-IH-QA-BOTTOM-01",
    "SEM-IH-QD-C-01", "SEM-IH-QD-C-02", "SEM-IH-QD-C-03", "SEM-IH-QD-BOTTOM-01",
]
EXPECTED_HAZARD_DISPATCH = [
    "SEM-IH-QA-R-01", "SEM-IH-QA-R-02", "SEM-IH-QA-BOTTOM-01",
    "SEM-IH-QD-R-01", "SEM-IH-QD-R-02", "SEM-IH-QD-BOTTOM-01",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def _fail(failures: list[dict], check: str, **extra) -> None:
    failures.append({"check": check, **extra})


def _find_visuals(data: dict, wanted: set[str]) -> list[dict]:
    rows = []
    for page in data.get("pages") or []:
        for unit in page.get("visualUnits") or []:
            if unit.get("occurrenceId") in wanted:
                rows.append({
                    "occurrenceId": unit["occurrenceId"],
                    "pdfPageIndex": page["pdfPageIndex"],
                    "visiblePrintedPageNumber": page["visiblePrintedPageNumber"],
                    "pageRole": page["pageRole"],
                    "renderEvidence": page["renderEvidence"],
                    "visualUnit": unit,
                })
    return rows


def _find_faq(data: dict, wanted: set[str]) -> list[dict]:
    return [
        unit
        for page in data.get("pages") or []
        for unit in page.get("units") or []
        if unit.get("sourceUnitId") in wanted
    ]


def _record_projection(record_by_id: dict[str, dict]) -> list[dict | None]:
    return [record_by_id.get(rule_id) for rule_id in COMBAT_PINNED_RULE_IDS]


def _question_projection(question_by_id: dict[str, dict]) -> list[dict | None]:
    return [question_by_id.get(question_id) for question_id in COMBAT_QUESTION_IDS]


def _conflict_projection(conflict_rows: list[dict]) -> list[dict | None]:
    by_id = {row.get("conflictId"): row for row in conflict_rows}
    return [by_id.get("SC-081"), by_id.get("SC-082")]


def _backlog_projection(backlog_by_id: dict[str, dict]) -> list[dict | None]:
    return [backlog_by_id.get(unit_id) for unit_id in COMBAT_PENDING_BACKLOG_IDS]


def validate_combat_family(
    repo: Path,
    combat_source_path: Path,
    source: dict,
    record_by_id: dict[str, dict],
    question_by_id: dict[str, dict],
    conflict_rows: list[dict],
    coverage: dict,
    backlog: dict,
    backlog_by_id: dict[str, dict],
    failures: list[dict],
) -> dict:
    if _sha(combat_source_path) != PINNED_COMBAT_SOURCE_INDEX_HASH:
        _fail(failures, "pinned Combat source index")
    if _digest(source.get("counts")) != EXPECTED_COUNTS_DIGEST:
        _fail(failures, "Combat exact source counts")

    expected_counts = {
        "sourceSegments": 15,
        "closedPendingBacklogUnits": 11,
        "visualObligationsClosed": 9,
        "dependencyVisualObligations": 2,
        "faqUnits": 11,
        "intruderHelpSides": 2,
        "intruderHelpCorridorRows": 6,
        "intruderHelpRoomRows": 4,
        "intruderHelpSideLevelBlankRows": 2,
        "diceKinds": 3,
        "officialDistinctDieResultTerms": 16,
        "attackClasses": 9,
        "movementClasses": 6,
        "newSemanticRecords": 14,
        "replacedSemanticRecords": 10,
        "newNoDefaultQuestions": 9,
    }
    if source.get("counts") != expected_counts:
        _fail(failures, "Combat declared source projection counts", expected=expected_counts, actual=source.get("counts"))

    # Re-read every pinned source tuple and line segment rather than trusting the
    # generated projection or coordinated changes to its declared counts.
    for document in (source.get("sourceDocuments") or {}).values():
        path = repo / str(document.get("path") or "")
        if not path.is_file() or _sha(path) != document.get("sha256"):
            _fail(failures, "Combat live source document hash", path=document.get("path"))
    rulebook_lines = (repo / "docs/rulebooks/rulebook_text.txt").read_text(encoding="utf-8").splitlines()
    expected_segments = [
        {
            "sourceUnitId": source_id,
            "printedLineStart": start,
            "printedLineEnd": end,
            "role": role,
            "checkedExtractionText": "\n".join(rulebook_lines[start - 1 : end]),
        }
        for source_id, start, end, role in SOURCE_SEGMENTS
    ]
    if source.get("sourceSegments") != expected_segments or _digest(source.get("sourceSegments")) != EXPECTED_SOURCE_SEGMENT_DIGEST:
        _fail(failures, "Combat exact official procedure line projection")

    visual_data = json.loads((repo / VISUAL_PATH).read_text(encoding="utf-8"))
    expected_visuals = _find_visuals(visual_data, set(COMBAT_VISUAL_IDS + COMBAT_DEPENDENCY_VISUAL_IDS))
    source_visuals = source.get("visualObligations") or []
    if source_visuals != expected_visuals or set(row.get("occurrenceId") for row in source_visuals) != set(COMBAT_VISUAL_IDS + COMBAT_DEPENDENCY_VISUAL_IDS) or _digest(source_visuals) != EXPECTED_VISUAL_PROJECTION_DIGEST:
        _fail(failures, "Combat exact icon/source/visual/geometry projection")
    for row in source_visuals:
        visual = row.get("visualUnit") or {}
        bbox = visual.get("bbox") or []
        dimensions = (row.get("renderEvidence") or {}).get("dimensions") or []
        if len(bbox) != 4 or len(dimensions) != 2 or not (0 <= bbox[0] < bbox[2] <= dimensions[0] and 0 <= bbox[1] < bbox[3] <= dimensions[1]) or visual.get("obligationClass") != "normative-visual-obligation":
            _fail(failures, "Combat visual bbox/authority closure", occurrenceId=row.get("occurrenceId"))

    faq_data = json.loads((repo / FAQ_PATH).read_text(encoding="utf-8"))
    expected_faq = _find_faq(faq_data, set(COMBAT_FAQ_IDS))
    if source.get("faqUnits") != expected_faq or [row.get("sourceUnitId") for row in expected_faq] != COMBAT_FAQ_IDS or _digest(expected_faq) != EXPECTED_FAQ_PROJECTION_DIGEST:
        _fail(failures, "Combat exact FAQ authority/applicability projection")
    if any(row.get("applicability") != "base-game" for row in expected_faq):
        _fail(failures, "Combat expansion FAQ exclusion")

    help_data = json.loads((repo / HELP_PATH).read_text(encoding="utf-8"))
    expected_help_sides = [
        {"sideId": side["sideId"], "sourcePath": side["sourcePath"], "sourceSha256": side["sourceSha256"], "columns": side["columns"], "bottomRow": side["bottomRow"]}
        for side in help_data["sides"]
    ]
    help_projection = source.get("intruderHelp") or {}
    if help_projection.get("sides") != expected_help_sides or _digest(help_projection) != EXPECTED_HELP_PROJECTION_DIGEST:
        _fail(failures, "Combat exact Intruder Help token/front/back/panel projection")
    for key in ("queenAliveVisualEvidence", "queenDeadVisualEvidence"):
        evidence = help_projection.get(key) or {}
        p5 = evidence.get("blankPanelRelation") or {}
        if p5.get("panelId") != "P5" or "beneath" not in (p5.get("location") or "") and "bottom" not in (p5.get("location") or ""):
            _fail(failures, "Combat side-level Blank panel geometry", side=key)

    # Dice roles/assets are exact secondary tuples, but their runtime labels do
    # not become official semantics. Current official result terms stay closed.
    roles = json.loads((repo / ROLES_PATH).read_text(encoding="utf-8"))
    objects = json.loads((repo / OBJECTS_PATH).read_text(encoding="utf-8"))
    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    role_by_name = {row.get("role"): row for row in roles}
    object_by_guid = {row.get("guid"): row for row in objects}
    manifest_by_url = {row.get("url"): row for row in manifest}
    expected_role_tuples = [("shootRollDice", "d8282d", "Shoot", 2, 8), ("burstRollDice", "9cd65f", "Burst", 2, 6), ("noiseRollDice", "effa9f", "Noise", 2, 10)]
    for role_name, guid, die_kind, count, sides in expected_role_tuples:
        projected = next((row for row in source.get("dice") or [] if row.get("ttsRole") == role_name), {})
        role = role_by_name.get(role_name) or {}
        obj = object_by_guid.get(guid) or {}
        image_url = dict(obj.get("urls") or []).get("ImageURL")
        manifest_row = manifest_by_url.get(image_url) or {}
        live_path = repo / ("assets/tts-mod/extract/v2-dl/tree/" + str(manifest_row.get("file") or ""))
        if (role.get("guid"), role.get("type"), projected.get("ttsGuid"), projected.get("dieKind"), projected.get("physicalCount"), projected.get("sides")) != (guid, "Custom_Dice", guid, die_kind, count, sides) or not live_path.is_file() or _sha(live_path) != projected.get("ttsImageSha256"):
            _fail(failures, "Combat exact die role/asset/count/sides tuple", role=role_name)
    runtime = source.get("runtimeNoiseBoundaries") or {}
    current = runtime.get("currentRetaliationResultBranch") or {}
    excluded = runtime.get("excludedUnboundLegacyBranches") or {}
    lua_lines = (repo / LUA_PATH).read_text(encoding="utf-8").splitlines()
    if current.get("text") != "\n".join(lua_lines[5897:5915]) or excluded.get("text") != "\n".join(lua_lines[5838:5871]) or current.get("allowedLabels") != ["Noise in corridor 1", "Noise in corridor 2", "Noise in corridor 3", "Noise in corridor 4", "Hazard !!"] or excluded.get("excludedLabels") != ["Silence unless Slimed", "!!! DANGER !!!", "Mars Surface"] or runtime.get("noOfficialFaceMultiplicityProjection") is not True or _digest({"dice": source.get("dice"), "runtime": runtime}) != EXPECTED_DICE_PROJECTION_DIGEST:
        _fail(failures, "Combat official Noise versus Silence/Danger/runtime boundary")

    if _digest({"attackClasses": source.get("attackClasses"), "movementClasses": source.get("movementClasses")}) != EXPECTED_CLASS_PROJECTION_DIGEST:
        _fail(failures, "Combat attack/movement class projection")
    if [row.get("attackClass") for row in source.get("attackClasses") or []] != ["character-shoot", "character-burst", "character-melee", "opportunity", "intruder-phase", "noise-entry", "hazard-entry", "other-entry", "melee-response"]:
        _fail(failures, "Combat normal/Opportunity/Hazard/Intruder attack-class separation")
    if [row.get("movementClass") for row in source.get("movementClasses") or []] != ["basic-normal", "basic-cautious", "source-effect", "intruder-movement", "robot-movement", "repel"]:
        _fail(failures, "Combat normal/cautious/effect/Intruder/Robot/Repel movement separation")

    if any(record_by_id.get(rule_id) is None for rule_id in COMBAT_NEW_RULE_IDS + COMBAT_REPLACED_RULE_IDS):
        _fail(failures, "Combat exact reusable record closure")

    # Noise/Hazard/spawn dispatch and immediate order.
    noise = record_by_id.get("SEM-NOISE-001") or {}
    noise_result = record_by_id.get("SEM-NOISE-RESULT-001") or {}
    numeric = record_by_id.get("SEM-NOISE-NUMERIC-CORRIDOR-001") or {}
    marker = record_by_id.get("SEM-NOISE-MARKER-001") or {}
    hazard = record_by_id.get("SEM-NOISE-HAZARD-001") or {}
    result_branch = next((row for row in noise_result.get("operations") or [] if row.get("resultBranches")), {})
    if result_branch.get("resultBranches") != EXPECTED_NOISE_RESULTS or [op.get("invokeRuleId") for op in noise.get("operations") or [] if op.get("invokeRuleId")] != ["SEM-NOISE-RESULT-001"] or [op.get("invokeRuleId") for op in noise_result.get("operations") or [] if op.get("invokeRuleId")] != ["SEM-NOISE-DEADLY-MODE-001", "SEM-NOISE-NUMERIC-CORRIDOR-001", "SEM-NOISE-HAZARD-001"] or not any(op.get("operationType") == "prohibit" and all(word in op.get("objectRef", "") for word in ("Silence", "Danger", "marker-limit")) for op in noise_result.get("operations") or []):
        _fail(failures, "Combat Noise/Hazard branch separation")
    numeric_types = [op.get("operationType") for op in numeric.get("operations") or []]
    numeric_invokes = [op.get("invokeRuleId") for op in numeric.get("operations") or [] if op.get("invokeRuleId")]
    numeric_entry = next((op for op in numeric.get("operations") or [] if op.get("invokeRuleId") == "SEM-SECURE-ENTRY-001"), {})
    if numeric_types != ["branch", "select-target", "move-entity", "invoke-process", "invoke-process", "place-component", "evaluate-condition"] or numeric_invokes != ["SEM-SECURE-ENTRY-001", "SEM-NOISE-MARKER-001"] or numeric_entry.get("attackClass") != "noise-entry" or "marker-limit Hazard" not in (numeric.get("partialResolution") or {}).get("onImpossible", ""):
        _fail(failures, "Combat numeric Corridor branch/order/immediate-entry closure")
    marker_dispatch = next((op.get("dispatchRuleIds") for op in marker.get("operations") or [] if op.get("dispatchRuleIds")), None)
    hazard_dispatch = next((op.get("dispatchRuleIds") for op in hazard.get("operations") or [] if op.get("dispatchRuleIds")), None)
    if marker_dispatch != EXPECTED_MARKER_DISPATCH or hazard_dispatch != EXPECTED_HAZARD_DISPATCH or [op.get("operationType") for op in marker.get("operations") or []] != ["remove-component", "resolve-open-alternative", "draw-random", "invoke-selected-process"] or [op.get("operationType") for op in hazard.get("operations") or []] != ["resolve-open-alternative", "draw-random", "invoke-selected-process", "prohibit"]:
        _fail(failures, "Combat token/bag/type/order and Blank dispatch closure")

    for rule_id in ("SEM-IH-QA-C-02", "SEM-IH-QD-C-02"):
        row = record_by_id.get(rule_id) or {}
        placement = next((op for op in row.get("operations") or [] if op.get("operationType") == "place-component"), {})
        repeat = placement.get("repeat") or {}
        if repeat.get("tokenFaceResolutions") != EXPECTED_TOKEN_BACK_RESULTS or repeat.get("allocationOrder") != "SEM-Q-105 source-unspecified under scarcity/capacity" or "SEM-Q-105" not in row.get("unresolvedQuestionRefs", []):
            _fail(failures, "Combat same-count token/type swap closure", ruleId=rule_id)
    for rule_id in ("SEM-IH-QA-BOTTOM-01", "SEM-IH-QD-BOTTOM-01"):
        row = record_by_id.get(rule_id) or {}
        ops = row.get("operations") or []
        if "SEM-Q-099" not in row.get("unresolvedQuestionRefs", []) or [op.get("operationType") for op in ops] != ["resolve-open-alternative", "draw-random", "transition-zone"] or (ops[-1].get("transition") or {}).get("to") != "tax.scaffold.zone.intruder-bag" or "all-token-draw-contexts" not in json.dumps(row.get("preconditions") or []):
            _fail(failures, "Combat side-level Blank return/scope no-default closure", ruleId=rule_id)

    # Distinct Attack classes, target rules, and prevention windows.
    movement = record_by_id.get("SEM-MOVEMENT-SEQUENCE-001") or {}
    opportunity = record_by_id.get("SEM-OPPORTUNITY-ATTACK-001") or {}
    phase = record_by_id.get("SEM-RT-008") or {}
    secure = record_by_id.get("SEM-SECURE-ENTRY-001") or {}
    melee = record_by_id.get("SEM-MELEE-SEQUENCE-001") or {}
    duck = record_by_id.get("SEM-REACTION-DUCK-001") or {}
    class_atoms = {
        "movement": next((op.get("attackClass") for op in movement.get("operations") or [] if op.get("invokeRuleId") == "SEM-OPPORTUNITY-ATTACK-001"), None),
        "opportunity": next((op.get("attackClass") for op in opportunity.get("operations") or [] if op.get("invokeRuleId") == "SEM-INT-004"), None),
        "phase": next((op.get("attackClass") for op in phase.get("operations") or [] if op.get("invokeRuleId") == "SEM-INT-004"), None),
        "secure": next((op.get("attackClass") for op in secure.get("operations") or [] if op.get("invokeRuleId") == "SEM-INT-004"), None),
        "melee": next((op.get("attackClass") for op in melee.get("operations") or [] if op.get("invokeRuleId") == "SEM-INT-004"), None),
        "duck": next((op.get("attackClass") for op in duck.get("operations") or [] if op.get("invokeRuleId") == "SEM-INT-004"), None),
    }
    expected_class_atoms = {"movement": "opportunity", "opportunity": "opportunity", "phase": "intruder-phase", "secure": "caller-preserved-entry-class", "melee": "melee-response", "duck": "reaction-redirected-preserve-original-class"}
    if class_atoms != expected_class_atoms:
        _fail(failures, "Combat normal/Opportunity/Hazard/Intruder attack-class collapse", actual=class_atoms)
    attack = record_by_id.get("SEM-INT-004") or {}
    attack_ops = attack.get("operations") or []
    if [op.get("operationType") for op in attack_ops] != ["branch", "select-target", "resolve-open-alternative", "end-process", "branch", "resolve-open-alternative", "draw-random", "invoke-selected-process", "transition-zone", "invoke-process", "move-entity", "remove-component"] or next((op.get("attackClassTargetRules") for op in attack_ops if op.get("attackClassTargetRules")), None) is None or "SEM-Q-060" not in attack.get("unresolvedQuestionRefs", []) or "SEM-Q-101" not in attack.get("unresolvedQuestionRefs", []):
        _fail(failures, "Combat Intruder target/prevention/Larva/card branch closure")

    # Die-result substitutions/inversions and exact player-owned allocation.
    shoot_die = record_by_id.get("SEM-SHOOT-DIE-RESULT-001") or {}
    melee_die = record_by_id.get("SEM-MELEE-SHOOT-DIE-RESULT-001") or {}
    burst_die = record_by_id.get("SEM-BURST-DIE-RESULT-001") or {}
    shoot_map = next((op.get("resultBranches") for op in shoot_die.get("operations") or [] if op.get("resultBranches")), None)
    melee_map = next((op.get("resultBranches") for op in melee_die.get("operations") or [] if op.get("resultBranches")), None)
    burst_map = next((op.get("resultBranches") for op in burst_die.get("operations") or [] if op.get("resultBranches")), None)
    if shoot_map != EXPECTED_SHOOT_RESULTS or melee_map != EXPECTED_MELEE_RESULTS or burst_map != EXPECTED_BURST_RESULTS or next((op.get("coLocatedTermIds") for op in burst_die.get("operations") or [] if op.get("coLocatedTermIds")), None) != ["icon.burstDie4", "icon.burstDieAdditionalEffects"]:
        _fail(failures, "Combat Shoot/Burst/Melee die-result substitution or inversion")
    shoot_sequence = record_by_id.get("SEM-SHOOT-SEQUENCE-001") or {}
    burst_sequence = record_by_id.get("SEM-BURST-SEQUENCE-001") or {}
    burst_decision = next((row for row in burst_sequence.get("decisions") or [] if row.get("decisionId") == "D-BURST-HITS"), {})
    burst_allocation = next((op for op in burst_sequence.get("operations") or [] if op.get("decisionRef") == "D-BURST-HITS"), {})
    burst_hit_index = next((index for index, op in enumerate(burst_sequence.get("operations") or []) if op.get("invokeRuleId") == "SEM-INTRUDER-HIT-RESOLUTION-001"), None)
    burst_extra_index = next((index for index, op in enumerate(burst_sequence.get("operations") or []) if op.get("invokeRuleId") == "SEM-WEAPON-DIE-RESULT-ADDITION-001"), None)
    if burst_decision.get("ownerRef") != "P-OWNER" or burst_decision.get("selectionMode") != "player-choice" or burst_decision.get("cardinality") != {"min": 0, "max": None} or burst_allocation.get("allocationOwner") != "P-OWNER" or burst_allocation.get("attackClass") != "character-burst" or burst_hit_index is None or burst_extra_index is None or burst_hit_index >= burst_extra_index or any(op.get("invokeRuleId") == "SEM-WEAPON-DIE-RESULT-ADDITION-001" for op in burst_die.get("operations") or []) or not any("Character, Robot, and non-Intruder targets are ineligible" in op.get("objectRef", "") for op in shoot_sequence.get("operations") or []) or not any("Character, Robot, and non-Intruder targets are ineligible" in op.get("objectRef", "") for op in melee.get("operations") or []):
        _fail(failures, "Combat target/owner/allocation/default invention closure")

    # Paid Basic Actions versus reusable sequences and Movement/Attack timing.
    wrapper_to_sequence = {
        "SEM-ACT-MOVE-001": "SEM-MOVEMENT-SEQUENCE-001",
        "SEM-ACT-MOVE-CAUTIOUSLY-001": "SEM-MOVEMENT-SEQUENCE-001",
        "SEM-ACT-SHOOT-001": "SEM-SHOOT-SEQUENCE-001",
        "SEM-ACT-BURST-001": "SEM-BURST-SEQUENCE-001",
        "SEM-ACT-MELEE-001": "SEM-MELEE-SEQUENCE-001",
    }
    for wrapper_id, sequence_id in wrapper_to_sequence.items():
        wrapper = record_by_id.get(wrapper_id) or {}
        ops = wrapper.get("operations") or []
        if [op.get("operationType") for op in ops] != ["pay-cost", "invoke-process"] or ops[-1].get("invokeRuleId") != sequence_id:
            _fail(failures, "Combat Basic-Action payment versus reusable sequence boundary", ruleId=wrapper_id)
    for sequence_id in set(wrapper_to_sequence.values()):
        if any(op.get("operationType") == "pay-cost" for op in (record_by_id.get(sequence_id) or {}).get("operations") or []):
            _fail(failures, "Combat reusable sequence contains invented Basic-Action payment", ruleId=sequence_id)
    movement_types = [op.get("operationType") for op in movement.get("operations") or []]
    if movement_types != ["select-target", "invoke-process", "resolve-open-alternative", "branch", "move-entity", "place-component", "invoke-process", "invoke-process"] or next((op.get("movementTiming") for op in movement.get("operations") or [] if op.get("invokeRuleId") == "SEM-OPPORTUNITY-ATTACK-001"), None) != "after-direction-before-destination":
        _fail(failures, "Combat movement/attack/reaction timing flattening")
    for row in record_by_id.values():
        if row.get("ruleId") in wrapper_to_sequence:
            continue
        for op in row.get("operations") or []:
            if op.get("invokeRuleId") in wrapper_to_sequence:
                _fail(failures, "Combat source effect incorrectly invokes paid Basic Action", ruleId=row.get("ruleId"), stepId=op.get("stepId"))

    # Finite supply/exhaustion policy must not manufacture a rule.
    expected_components = {
        "burstDice": 2,
        "shootDice": 2,
        "noiseDice": 2,
        "intruderTokens": {"total": 40, "Blank": 1, "Queen": 9, "Drone": 8, "Adult": 16, "Larva": 6},
        "intruderModels": {"Queen": 1, "Drone": 8, "Adult": 36, "Larva": 6},
        "noiseMarkers": 30,
        "universalMarkers": 30,
        "secureTokens": 20,
    }
    supply = record_by_id.get("SEM-COMBAT-COMPONENT-LIMITS-001") or {}
    if source.get("componentCounts") != expected_components or [op.get("operationType") for op in supply.get("operations") or []] != ["evaluate-condition", "place-component", "evaluate-condition", "prohibit"] or not any(all(word in op.get("objectRef", "") for word in ("die exhaustion", "bag refill", "type substitution")) for op in supply.get("operations") or []):
        _fail(failures, "Combat finite supply/exhaustion invention closure")

    # Exact questions/conflicts and pinned semantic atoms.
    for question_id in COMBAT_QUESTION_IDS:
        question = question_by_id.get(question_id) or {}
        if question.get("defaultProhibited") is not True or len(question.get("alternatives") or []) != 3 or not question.get("blocksRuleIds") or any(rule_id not in record_by_id for rule_id in question.get("blocksRuleIds") or []):
            _fail(failures, "Combat no-default question closure", questionId=question_id)
    if _digest(_question_projection(question_by_id)) != EXPECTED_QUESTION_PROJECTION_DIGEST:
        _fail(failures, "pinned Combat no-default question projection")
    combat_conflicts = _conflict_projection(conflict_rows)
    if [row.get("conflictId") if row else None for row in combat_conflicts] != ["SC-081", "SC-082"] or (combat_conflicts[0] or {}).get("status") != "resolved-by-authority" or (combat_conflicts[1] or {}).get("status") != "unresolved" or _digest(combat_conflicts) != EXPECTED_CONFLICT_PROJECTION_DIGEST:
        _fail(failures, "pinned Combat visual/runtime/Blank conflict projection")
    if _digest(_record_projection(record_by_id)) != EXPECTED_RECORD_PROJECTION_DIGEST:
        _fail(failures, "pinned Combat ordered semantic atom projection")

    core_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "core Combat, Intruder Attack, base Attack cards, Secure entry, and Character Health"), {})
    movement_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "movement/base Exploration cards"), {})
    noise_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "Doors and Noise"), {})
    if not set(COMBAT_NEW_RULE_IDS).issubset(set(core_system.get("ruleIds") or []) | set(movement_system.get("ruleIds") or []) | set(noise_system.get("ruleIds") or [])) or coverage.get("counts", {}).get("fullBaseSemanticCoverageClaimed") is not False:
        _fail(failures, "Combat partial coverage system projection")

    # The 600-unit ledger and inherited blocker are independently coordinated.
    if source.get("closedPendingBacklogUnitIds") != COMBAT_PENDING_BACKLOG_IDS:
        _fail(failures, "Combat exact pending backlog ID closure")
    backlog_rows = _backlog_projection(backlog_by_id)
    if any(row is None or row.get("status") != "pilot-covered" or not row.get("pilotRuleIds") for row in backlog_rows) or _digest(backlog_rows) != EXPECTED_BACKLOG_PROJECTION_DIGEST:
        _fail(failures, "Combat exact backlog status/link projection")
    if backlog.get("counts") != {
        "units": 600,
        "byChannel": {"card-reference-source-tuple": 350, "interpreted-rule-record": 54, "intruder-help-instruction": 18, "objective-help-unit": 45, "official-faq-unit": 28, "room-help-entry": 25, "rulebook-visual-obligation": 80},
        "byStatus": {"pending": 69, "pilot-covered": 530, "source-blocked": 1},
    }:
        _fail(failures, "Combat coordinated backlog lowering")
    blocked = [row for row in backlog.get("units") or [] if row.get("status") == "source-blocked"]
    if len(blocked) != 1 or blocked[0].get("semanticUnitId") != "CARD:eaa728ca02c48c33":
        _fail(failures, "Combat inherited blocker preservation")

    return {
        "sourceSegments": len(source.get("sourceSegments") or []),
        "visualObligations": len([row for row in source.get("visualObligations") or [] if row.get("occurrenceId") in COMBAT_VISUAL_IDS]),
        "dependencyVisualObligations": len([row for row in source.get("visualObligations") or [] if row.get("occurrenceId") in COMBAT_DEPENDENCY_VISUAL_IDS]),
        "faqUnits": len(source.get("faqUnits") or []),
        "diceKinds": len(source.get("dice") or []),
        "attackClasses": len(source.get("attackClasses") or []),
        "movementClasses": len(source.get("movementClasses") or []),
        "newRecords": len(COMBAT_NEW_RULE_IDS),
        "replacedRecords": len(COMBAT_REPLACED_RULE_IDS),
        "newQuestions": len(COMBAT_QUESTION_IDS),
        "newConflicts": len(combat_conflicts),
        "closedBacklogUnits": len(COMBAT_PENDING_BACKLOG_IDS),
    }
