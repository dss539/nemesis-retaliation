from __future__ import annotations

import hashlib
import json
from pathlib import Path


RULEBOOK_PATH = "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"
RULEBOOK_TEXT_PATH = "docs/rulebooks/rulebook_text.txt"
FAQ_PATH = "docs/rules/source-extraction/faq-v1.2-source-extraction.json"
VISUAL_PATH = "docs/rules/source-extraction/rulebook-visual-obligations.json"
HELP_PATH = "docs/rules/source-extraction/intruder-help-sheet.json"
HELP_QA_VISION_PATH = "assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-33-20260821T172305Z-p465856-36ac0c/results/W33-020.json"
HELP_QD_VISION_PATH = "assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-33-20260821T172305Z-p465856-36ac0c/results/W33-021.json"
ROLES_PATH = "assets/tts-mod/extract/v2/lua_roles.json"
OBJECTS_PATH = "assets/tts-mod/extract/v2/objects.json"
MANIFEST_PATH = "assets/tts-mod/extract/v2-dl/tree/manifest.json"
LUA_PATH = "assets/tts-mod/extract/v2/lua_script.lua"

COMBAT_VISUAL_IDS = [
    "RB-P24-V02",
    "RB-P25-V01",
    "RB-P25-V02",
    "RB-P30-V01",
    "RB-P30-V02",
    "RB-P33-V01",
    "RB-P33-V02",
    "RB-P34-V01",
    "RB-P40-V01",
]

# The two already-covered visuals are retained as dependencies without being
# re-closed by this batch: Corridor anatomy supplies the Deadly/0 relationship,
# and the glossary supplies exact controlled die/icon denotations.
COMBAT_DEPENDENCY_VISUAL_IDS = ["RB-P21-V01", "RB-P40-V02"]

COMBAT_PENDING_BACKLOG_IDS = [
    "RULE:INT-002",
    "RULE:INT-005",
    *[f"VIS:{value}" for value in COMBAT_VISUAL_IDS],
]

COMBAT_FAQ_IDS = [
    "FQ-P02-U03",
    "FQ-P02-U10",
    "FQ-P02-U11",
    "FQ-P02-U13",
    "FQ-P02-U14",
    "FQ-P02-U15",
    "FQ-P02-U16",
    "FQ-P02-U19",
    "FQ-P02-U21",
    "FQ-P03-U01",
    "FQ-P03-U02",
]

SOURCE_SEGMENTS = [
    ("RB-COMPONENT-DICE", 965, 983, "physical dice and component counts"),
    ("RB-COMPONENT-TOKENS-MODELS", 2152, 2185, "finite marker, token, and model counts"),
    ("RB-BASIC-ACTIONS", 2865, 2905, "Basic Action costs and Not In Combat boundary"),
    ("RB-INTRUDER-PHASE-ATTACKS", 3313, 3324, "Intruder Phase attack cohort ordering"),
    ("RB-COMPONENT-LIMITS", 3543, 3548, "generic finite-component fallback"),
    ("RB-MOVEMENT", 4541, 4576, "Movement Sequence and Opportunity Attacks"),
    ("RB-NOISE", 4655, 4710, "Noise marker, Noise roll, Hazard, and immediate entry attack"),
    ("RB-INTRUDER-MOVEMENT-TARGETS", 5125, 5159, "Intruder movement and target priorities"),
    ("RB-INTRUDER-TYPES-BAG-LIMIT", 5164, 5198, "type order, bag lifecycle, capacity, and model limits"),
    ("RB-INTRUDER-ATTACK", 5393, 5430, "standard/Larva Attacks, prevention, and entry target"),
    ("RB-BURST", 5490, 5537, "Burst die, allocation, resolution, and additional result"),
    ("RB-WEAPON-RESULTS", 5542, 5553, "Weapon modifiers and additional die results"),
    ("RB-SHOOT", 5560, 5620, "Shoot procedure, die results, Ammo, and Character target prohibition"),
    ("RB-MELEE", 5628, 5687, "Melee, response prevention, type Health, and Corridor Hit markers"),
    ("RB-DEADLY-MODE", 6401, 6411, "dual Noise values, Secure 0, and tie-break value"),
]

COMBAT_NEW_RULE_IDS = [
    "SEM-ACT-MOVE-CAUTIOUSLY-001",
    "SEM-ACT-MELEE-001",
    "SEM-BURST-DIE-RESULT-001",
    "SEM-BURST-SEQUENCE-001",
    "SEM-COMBAT-COMPONENT-LIMITS-001",
    "SEM-INTRUDER-HIT-RESOLUTION-001",
    "SEM-MELEE-SEQUENCE-001",
    "SEM-MELEE-SHOOT-DIE-RESULT-001",
    "SEM-MOVEMENT-SEQUENCE-001",
    "SEM-NOISE-DEADLY-MODE-001",
    "SEM-NOISE-RESULT-001",
    "SEM-OPPORTUNITY-ATTACK-001",
    "SEM-SHOOT-DIE-RESULT-001",
    "SEM-SHOOT-SEQUENCE-001",
]

COMBAT_REPLACED_RULE_IDS = [
    "SEM-ACT-BURST-001",
    "SEM-ACT-MOVE-001",
    "SEM-ACT-SHOOT-001",
    "SEM-INT-004",
    "SEM-NOISE-001",
    "SEM-NOISE-HAZARD-001",
    "SEM-NOISE-MARKER-001",
    "SEM-NOISE-NUMERIC-CORRIDOR-001",
    "SEM-RT-008",
    "SEM-SECURE-ENTRY-001",
]

COMBAT_QUESTION_IDS = [f"SEM-Q-{value:03d}" for value in range(97, 106)]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _line_segment(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def _visual_projection(visual_data: dict, wanted: set[str]) -> list[dict]:
    rows = []
    for page in visual_data["pages"]:
        for unit in page.get("visualUnits", []):
            if unit.get("occurrenceId") not in wanted:
                continue
            rows.append(
                {
                    "occurrenceId": unit["occurrenceId"],
                    "pdfPageIndex": page["pdfPageIndex"],
                    "visiblePrintedPageNumber": page["visiblePrintedPageNumber"],
                    "pageRole": page["pageRole"],
                    "renderEvidence": page["renderEvidence"],
                    "visualUnit": unit,
                }
            )
    return rows


def _faq_projection(faq_data: dict, wanted: set[str]) -> list[dict]:
    rows = []
    for page in faq_data["pages"]:
        for unit in page.get("units", []):
            if unit.get("sourceUnitId") in wanted:
                rows.append(unit)
    return rows


def _help_visual_projection(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "sourcePath": data["sourcePath"],
        "sourceSha256": data["sourceSha256"],
        "panelStructure": data["panelStructure"],
        "visibleSections": data["visibleText"]["sections"],
        "blankPanelRelation": next(row for row in data["panelStructure"] if row["panelId"] == "P5"),
    }


def build_combat_source_index(repo: Path) -> dict:
    rulebook_text_path = repo / RULEBOOK_TEXT_PATH
    rulebook_lines = rulebook_text_path.read_text(encoding="utf-8").splitlines()
    visual_data = json.loads((repo / VISUAL_PATH).read_text(encoding="utf-8"))
    faq_data = json.loads((repo / FAQ_PATH).read_text(encoding="utf-8"))
    help_data = json.loads((repo / HELP_PATH).read_text(encoding="utf-8"))
    roles = json.loads((repo / ROLES_PATH).read_text(encoding="utf-8"))
    objects = json.loads((repo / OBJECTS_PATH).read_text(encoding="utf-8"))
    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    manifest_by_url = {row["url"]: row for row in manifest}

    source_segments = [
        {
            "sourceUnitId": source_id,
            "printedLineStart": start,
            "printedLineEnd": end,
            "role": role,
            "checkedExtractionText": _line_segment(rulebook_lines, start, end),
        }
        for source_id, start, end, role in SOURCE_SEGMENTS
    ]

    all_visual_ids = set(COMBAT_VISUAL_IDS + COMBAT_DEPENDENCY_VISUAL_IDS)
    visual_rows = _visual_projection(visual_data, all_visual_ids)
    faq_rows = _faq_projection(faq_data, set(COMBAT_FAQ_IDS))

    dice_roles = {
        row["role"]: row
        for row in roles
        if row.get("role") in {"shootRollDice", "burstRollDice", "noiseRollDice"}
    }
    objects_by_guid = {row.get("guid"): row for row in objects}
    dice = []
    official_dice = {
        "shootRollDice": {"dieKind": "Shoot", "physicalCount": 2, "sides": 8, "officialResultTermIds": [f"icon.shootDie{value}" for value in (2, 3, 4, 5)] + ["icon.shootDieAmmoLoss", "icon.shootDieCritical"]},
        "burstRollDice": {"dieKind": "Burst", "physicalCount": 2, "sides": 6, "officialResultTermIds": [f"icon.burstDie{value}" for value in (1, 2, 3, 4)] + ["icon.burstDieAdditionalEffects"]},
        "noiseRollDice": {"dieKind": "Noise", "physicalCount": 2, "sides": 10, "officialResultTermIds": [f"icon.noiseDie{value}" for value in (1, 2, 3, 4)] + ["icon.noiseDieHazard"]},
    }
    for role_name in ("shootRollDice", "burstRollDice", "noiseRollDice"):
        role = dice_roles[role_name]
        obj = objects_by_guid[role["guid"]]
        image_url = dict(obj["urls"])["ImageURL"]
        manifest_row = manifest_by_url[image_url]
        local_path = "assets/tts-mod/extract/v2-dl/tree/" + manifest_row["file"]
        dice.append(
            {
                **official_dice[role_name],
                "ttsRole": role_name,
                "ttsGuid": role["guid"],
                "ttsType": role["type"],
                "ttsImageUrl": image_url,
                "ttsImagePath": local_path,
                "ttsImageSha256": _sha(repo / local_path),
                "authorityBoundary": "TTS role/texture/runtime evidence is secondary provenance; official result names and procedures control",
            }
        )

    lua_lines = (repo / LUA_PATH).read_text(encoding="utf-8").splitlines()
    runtime_boundaries = {
        "currentRetaliationResultBranch": {
            "diceBranch": "yellow",
            "lineStart": 5898,
            "lineEnd": 5915,
            "text": _line_segment(lua_lines, 5898, 5915),
            "allowedLabels": ["Noise in corridor 1", "Noise in corridor 2", "Noise in corridor 3", "Noise in corridor 4", "Hazard !!"],
        },
        "excludedUnboundLegacyBranches": {
            "diceBranches": ["black", "orange"],
            "lineStart": 5839,
            "lineEnd": 5871,
            "text": _line_segment(lua_lines, 5839, 5871),
            "excludedLabels": ["Silence unless Slimed", "!!! DANGER !!!", "Mars Surface"],
            "boundary": "These branches are not the exact Lua role-bound Retaliation noiseRollDice result set and cannot create official base-game Noise outcomes.",
        },
        "noOfficialFaceMultiplicityProjection": True,
    }

    help_sides = []
    for side in help_data["sides"]:
        help_sides.append(
            {
                "sideId": side["sideId"],
                "sourcePath": side["sourcePath"],
                "sourceSha256": side["sourceSha256"],
                "columns": side["columns"],
                "bottomRow": side["bottomRow"],
            }
        )

    component_counts = {
        "burstDice": 2,
        "shootDice": 2,
        "noiseDice": 2,
        "intruderTokens": {"total": 40, "Blank": 1, "Queen": 9, "Drone": 8, "Adult": 16, "Larva": 6},
        "intruderModels": {"Queen": 1, "Drone": 8, "Adult": 36, "Larva": 6},
        "noiseMarkers": 30,
        "universalMarkers": 30,
        "secureTokens": 20,
    }

    attack_classes = [
        {"attackClass": "character-shoot", "actor": "Character", "target": "one Intruder in the same Room", "procedureRuleId": "SEM-SHOOT-SEQUENCE-001"},
        {"attackClass": "character-burst", "actor": "Character", "target": "Intruders in one adjacent Corridor", "procedureRuleId": "SEM-BURST-SEQUENCE-001"},
        {"attackClass": "character-melee", "actor": "Character", "target": "one Intruder in the same Room", "procedureRuleId": "SEM-MELEE-SEQUENCE-001"},
        {"attackClass": "opportunity", "actor": "Intruder", "target": "moving Character", "procedureRuleId": "SEM-OPPORTUNITY-ATTACK-001"},
        {"attackClass": "intruder-phase", "actor": "Intruder", "target": "first eligible Character in Turn order", "procedureRuleId": "SEM-INT-004"},
        {"attackClass": "noise-entry", "actor": "entering Intruder", "target": "Noise-rolling Character", "procedureRuleId": "SEM-SECURE-ENTRY-001"},
        {"attackClass": "hazard-entry", "actor": "Hazard-placed Intruder", "target": "affected Character or source-defined entry target", "procedureRuleId": "SEM-SECURE-ENTRY-001"},
        {"attackClass": "other-entry", "actor": "entering/placed Intruder", "target": "source Character if possible, otherwise first in Turn order", "procedureRuleId": "SEM-SECURE-ENTRY-001"},
        {"attackClass": "melee-response", "actor": "surviving Melee target", "target": "Melee attacker", "procedureRuleId": "SEM-INT-004"},
    ]

    movement_classes = [
        {"movementClass": "basic-normal", "costRuleId": "SEM-ACT-MOVE-001", "sequenceRuleId": "SEM-MOVEMENT-SEQUENCE-001"},
        {"movementClass": "basic-cautious", "costRuleId": "SEM-ACT-MOVE-CAUTIOUSLY-001", "sequenceRuleId": "SEM-MOVEMENT-SEQUENCE-001"},
        {"movementClass": "source-effect", "costRuleId": None, "sequenceRuleId": "SEM-MOVEMENT-SEQUENCE-001"},
        {"movementClass": "intruder-movement", "costRuleId": None, "sequenceRuleId": None},
        {"movementClass": "robot-movement", "costRuleId": None, "sequenceRuleId": None},
        {"movementClass": "repel", "costRuleId": None, "sequenceRuleId": None},
    ]

    counts = {
        "sourceSegments": len(source_segments),
        "closedPendingBacklogUnits": len(COMBAT_PENDING_BACKLOG_IDS),
        "visualObligationsClosed": len(COMBAT_VISUAL_IDS),
        "dependencyVisualObligations": len(COMBAT_DEPENDENCY_VISUAL_IDS),
        "faqUnits": len(faq_rows),
        "intruderHelpSides": len(help_sides),
        "intruderHelpCorridorRows": sum(len(next(col for col in side["columns"] if col["columnId"] == "corridor")["rows"]) for side in help_sides),
        "intruderHelpRoomRows": sum(len(next(col for col in side["columns"] if col["columnId"] == "room")["rows"]) for side in help_sides),
        "intruderHelpSideLevelBlankRows": len(help_sides),
        "diceKinds": len(dice),
        "officialDistinctDieResultTerms": sum(len(row["officialResultTermIds"]) for row in dice),
        "attackClasses": len(attack_classes),
        "movementClasses": len(movement_classes),
        "newSemanticRecords": len(COMBAT_NEW_RULE_IDS),
        "replacedSemanticRecords": len(COMBAT_REPLACED_RULE_IDS),
        "newNoDefaultQuestions": len(COMBAT_QUESTION_IDS),
    }

    return {
        "schemaVersion": 1,
        "recordType": "semantic-combat-source-projection",
        "scope": "base-game core Combat, Character/Intruder Attacks, Noise/Hazard spawning, Movement/Opportunity timing, and exact adjacent visual obligations",
        "authorityBoundary": "Official FAQ v1.2 controls exact propositions, then official rulebook/rendered visuals, then source-bound Intruder Help evidence. TTS runtime branches remain secondary provenance and never override official results.",
        "counts": counts,
        "sourceDocuments": {
            "rulebook": {"path": RULEBOOK_PATH, "sha256": _sha(repo / RULEBOOK_PATH)},
            "rulebookTextAid": {"path": RULEBOOK_TEXT_PATH, "sha256": _sha(rulebook_text_path)},
            "faqExtraction": {"path": FAQ_PATH, "sha256": _sha(repo / FAQ_PATH)},
            "visualCensus": {"path": VISUAL_PATH, "sha256": _sha(repo / VISUAL_PATH)},
            "intruderHelpExtraction": {"path": HELP_PATH, "sha256": _sha(repo / HELP_PATH)},
            "ttsLua": {"path": LUA_PATH, "sha256": _sha(repo / LUA_PATH), "authority": "secondary-runtime-provenance-only"},
        },
        "sourceSegments": source_segments,
        "visualObligations": visual_rows,
        "faqUnits": faq_rows,
        "intruderHelp": {
            "sides": help_sides,
            "queenAliveVisualEvidence": _help_visual_projection(repo / HELP_QA_VISION_PATH),
            "queenDeadVisualEvidence": _help_visual_projection(repo / HELP_QD_VISION_PATH),
            "blankScopeBoundary": "Each Blank row is a separate side-level P5 panel below the three P2/P3/P4 context columns. Bag Development applicability is independently official; Corridor/Room applicability remains SEM-Q-099 with no default.",
        },
        "dice": dice,
        "runtimeNoiseBoundaries": runtime_boundaries,
        "componentCounts": component_counts,
        "attackClasses": attack_classes,
        "movementClasses": movement_classes,
        "closedPendingBacklogUnitIds": COMBAT_PENDING_BACKLOG_IDS,
        "newSemanticRuleIds": COMBAT_NEW_RULE_IDS,
        "replacedSemanticRuleIds": COMBAT_REPLACED_RULE_IDS,
        "newQuestionIds": COMBAT_QUESTION_IDS,
        "fullBaseSemanticCoverageClaimed": False,
    }


def _target(target_id: str, taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None) -> dict:
    return {
        "targetId": target_id,
        "selectorRef": selector,
        "eligibleTaxonIds": taxa,
        "cardinality": {"min": minimum, "max": maximum},
        "selectionMode": mode,
        "visibility": "public",
    }


def _set_operation_class(operation_row: dict, **values) -> dict:
    operation_row.update(values)
    return operation_row


def build_combat_records(record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    records: list[dict] = []

    records.append(record(
        "SEM-COMBAT-COMPONENT-LIMITS-001", "Combat, die, Noise, Intruder-token, and model component limits", "source-backed", "constraint", "official-primary", "source-composed",
        [
            assertion("SA-COMBAT-SUPPLY-RB", "SRC-RULEBOOK", "printed pages 4, 6, 17, and 30 / lines 965–983, 2152–2185, 3543–3548, 5189–5198", ["preconditions", "informationPolicy", "operations", "partialResolution", "duration", "stacking"], "The box has 2 six-sided Burst dice, 2 eight-sided Shoot dice, 2 ten-sided Noise dice, 40 typed Intruder tokens, 30 Noise markers, 30 Universal markers, 20 Secure tokens, 36 Adults, 8 Drones, 1 Queen, and 6 Larvae. Intruder-model excess is ignored after placing as many as available; other components with no special shortage rule do nothing when unavailable.", "docs/rulebooks/rulebook_text.txt:lines 965–983,2152–2185,3543–3548,5189–5198"),
        ],
        ["icon.noise", "icon.secure", "term.adult", "term.drone", "term.larva", "term.queen"],
        ["tax.entity.agent.intruder", "tax.entity.component", "tax.entity.component.marker.noise", "tax.entity.component.token.secure", "tax.scaffold.supply-pool"], [],
        timing("TW-COMBAT-SUPPLY", "tax.entity.component", "when-triggered", "per-component-use-or-placement-request"),
        [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-COMBAT-SUPPLY", "subjectRef": "public physical dice, token, marker, and model types/counts plus current availability", "audience": "public", "revealTrigger": "continuous/use", "secrecy": "Intruder token pile order and bag contents beyond public draw/add/remove events remain source-governed"}], [], [],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "exact inventory: 2 Burst d6, 2 Shoot d8, 2 Noise d10; 40 typed Intruder tokens; 30 Noise markers; 30 Universal markers; 20 Secure tokens; 36 Adults, 8 Drones, 1 Queen, 6 Larvae", ["SA-COMBAT-SUPPLY-RB"]),
            operation("S02", 2, "place-component", "if-able", "P-RULES", "as many requested Intruder models of each exact type as are available, subject to destination capacity", ["SA-COMBAT-SUPPLY-RB"]),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "an unavailable other finite component with no special shortage rule causes that component use to do nothing", ["SA-COMBAT-SUPPLY-RB"]),
            operation("S04", 4, "prohibit", "must", "P-RULES", "invented die consumption, die exhaustion, component cloning, token reshuffle, bag refill, or type substitution", ["SA-COMBAT-SUPPLY-RB"]),
        ],
        {"policy": "source-limited-components", "unit": "one requested exact-type component/model", "onImpossible": "apply only the source-stated Intruder-model partial placement or the generic unavailable-component no-op; never substitute another type or invent replenishment"},
        {"kind": "persistent-physical-supply-constraint"}, {"policy": "counts are per physical component type; dice rolls do not consume dice"}, [], [], [],
    ))

    records.append(record(
        "SEM-NOISE-DEADLY-MODE-001", "Standard and Deadly-mode Corridor Noise values", "source-backed", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-NOISE-DEADLY-RB", "SRC-RULEBOOK", "printed pages 21 and 40 / RB-P21-V01, RB-P40-V01 / lines 4178–4189, 6401–6411", ["preconditions", "informationPolicy", "operations", "partialResolution", "duration", "stacking"], "A standard Corridor uses its large Noise value. In Deadly Mode, a Corridor is treated as having both its large standard and smaller Deadly value for any effect; a Reinforced Corridor still has only 0, and tie-breaks use only the standard value.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P21-V01/RB-P40-V01")],
        ["term.corridor", "term.deadly-mode"], ["tax.entity.spatial.corridor", "tax.rule.mode.deadly"], [],
        timing("TW-NOISE-DEADLY", "tax.rule.mode.deadly", "when-triggered", "per-Corridor-value-or-tie-check"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-NOISE-DEADLY", "subjectRef": "Corridor face, standard/secondary Noise values, Reinforced 0, active mode, and tie-break value", "audience": "public", "revealTrigger": "Corridor reveal/continuous", "secrecy": "unrevealed Corridor faces remain hidden"}], [], [_target("T-NOISE-DEADLY-CORRIDOR", ["tax.entity.spatial.corridor"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "only the large standard Noise value in base-standard mode", ["SA-NOISE-DEADLY-RB"], target_ref="T-NOISE-DEADLY-CORRIDOR"),
            operation("S02", 2, "evaluate-condition", "must", "P-RULES", "both large standard and smaller Deadly Noise values for every effect in Deadly Mode", ["SA-NOISE-DEADLY-RB"], target_ref="T-NOISE-DEADLY-CORRIDOR"),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "Reinforced Corridor has only one Noise value of 0 in either mode", ["SA-NOISE-DEADLY-RB"], target_ref="T-NOISE-DEADLY-CORRIDOR"),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "standard large value alone for any tie-break", ["SA-NOISE-DEADLY-RB"], target_ref="T-NOISE-DEADLY-CORRIDOR"),
        ],
        {"policy": "per-effect-check", "unit": "one Corridor value comparison", "onImpossible": "do not promote the smaller Deadly value outside Deadly Mode or give a Reinforced Corridor a second value"},
        {"kind": "persistent-mode-conditional-value-rule"}, {"policy": "standard and Deadly values coexist only as stated; they are not added together"}, [], [], [],
    ))

    noise_result = record(
        "SEM-NOISE-RESULT-001", "Official Noise die result dispatch", "source-backed-with-open-question", "dispatcher", "official-primary", "open-alternatives",
        [assertion("SA-NOISE-RESULT-RB", "SRC-RULEBOOK", "printed pages 25 and 40 / RB-P25-V01, RB-P40-V02 / lines 4670–4701, 6351–6353", ["preconditions", "informationPolicy", "operations", "partialResolution", "unresolvedQuestionRefs"], "The current official Noise result set is exactly numbered 1, 2, 3, 4 and Hazard. A number resolves each adjacent Corridor having that value; Hazard draws an Intruder token for Room-context resolution using its front only.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P25-V01")],
        ["icon.noiseDie1", "icon.noiseDie2", "icon.noiseDie3", "icon.noiseDie4", "icon.noiseDieHazard", "term.noise-roll"],
        ["tax.entity.spatial.corridor", "tax.process.sequence.noise-roll"], [],
        timing("TW-NOISE-RESULT", "tax.process.sequence.noise-roll", "when-triggered", "per-rolled-Noise-result"),
        [participant("P-ROLLER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-NOISE-RESULT", "subjectRef": "exact rolled official face, active mode values, matching Corridors, Hazard token/result", "audience": "public", "revealTrigger": "roll/resolution", "secrecy": "none"}], [], [],
        [
            operation("S01", 1, "branch", "must", "P-RULES", "exact official result: 1, 2, 3, 4, or Hazard", ["SA-NOISE-RESULT-RB"]),
            operation("S02", 2, "invoke-process", "if-able", "P-RULES", "standard/Deadly-mode value matching for adjacent Corridors", ["SA-NOISE-RESULT-RB"], conditions=["rolled result is 1, 2, 3, or 4"], invoke="SEM-NOISE-DEADLY-MODE-001"),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-097 order among multiple matching adjacent Corridors", ["SA-NOISE-RESULT-RB"], conditions=["more than one adjacent Corridor matches"]),
            operation("S04", 4, "invoke-process", "if-able", "P-RULES", "one complete matching-Corridor branch before the next", ["SA-NOISE-RESULT-RB"], conditions=["rolled result is 1, 2, 3, or 4"], invoke="SEM-NOISE-NUMERIC-CORRIDOR-001", repeat={"scope": "each matching adjacent Corridor", "order": "SEM-Q-097 source-unspecified", "completeImmediateConsequencesBeforeNext": True}),
            operation("S05", 5, "invoke-process", "must", "P-RULES", "one direct Hazard result in the affected Character's Room", ["SA-NOISE-RESULT-RB"], conditions=["rolled result is Hazard"], invoke="SEM-NOISE-HAZARD-001"),
            operation("S06", 6, "prohibit", "must", "P-RULES", "Silence, Danger, marker-limit-as-Hazard, or another nonofficial branch substituted for this closed Retaliation result set", ["SA-NOISE-RESULT-RB"]),
        ],
        {"policy": "source-conditional-steps", "unit": "one exact Noise face and then one matching Corridor at a time", "onImpossible": "no matching numeric Corridor does nothing; SEM-Q-097 preserves unspecified multi-Corridor order without changing each complete branch"},
        {"kind": "instantaneous-result-dispatch"}, {"policy": "one official result per Noise roll; no branch substitution"}, [], ["SEM-Q-097"], [],
    )
    noise_result["operations"][0]["resultBranches"] = [
        {"termId": f"icon.noiseDie{value}", "resultClass": "corridor-number", "corridorValue": value} for value in (1, 2, 3, 4)
    ] + [{"termId": "icon.noiseDieHazard", "resultClass": "hazard", "corridorValue": None}]
    records.append(noise_result)

    records.append(record(
        "SEM-MOVEMENT-SEQUENCE-001", "Reusable Character Movement Sequence", "source-backed-with-open-question", "sequence", "official-errata", "open-alternatives",
        [
            assertion("SA-MOVEMENT-SEQUENCE-RB", "SRC-RULEBOOK", "printed pages 24–25 / RB-P24-V02 / lines 4541–4576, 4702–4710", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Every Character Movement goes Room to Room: choose or receive an adjacent Corridor, resolve up to three Opportunity Attacks before relocation, then move to a Discovered Room and make Noise or resolve Exploration through an Unexplored Corridor. Cautious Movement places Secure after relocation and before Noise/Entrance resolution.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P24-V02"),
            assertion("SA-MOVEMENT-SEQUENCE-FAQ", "SRC-FAQ", "Action cards / FQ-P02-U16", ["preconditions", "operations", "partialResolution"], "Cards preventing an Intruder Attack during Movement apply only to Opportunity Attacks, not a Hazard-result Attack.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U16"),
        ],
        ["icon.secure", "term.corridor", "term.move", "term.movement-sequence", "term.moving-cautiously", "term.noise-roll", "term.opportunity-attack"],
        ["tax.entity.agent.character", "tax.entity.spatial.corridor", "tax.entity.spatial.room", "tax.process.action.move-cautiously", "tax.process.attack.opportunity", "tax.process.sequence.exploration", "tax.process.sequence.movement", "tax.process.sequence.noise-roll"], [],
        timing("TW-MOVEMENT-SEQUENCE", "tax.process.sequence.movement", "when-triggered", "per-source-authorized-Character-Movement"),
        [participant("P-MOVER", "actor", "tax.entity.agent.character"), participant("P-MOVER-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must",
        [condition("C-MOVEMENT", "all", [{"predicate": "caller authorizes Character Movement"}, {"predicate": "selected/fixed Corridor is adjacent unless Secret Passage source explicitly omits Choose Direction"}, {"predicate": "Closed Door does not block the path"}], ["SA-MOVEMENT-SEQUENCE-RB"])],
        [decision("D-MOVEMENT-CORRIDOR", "P-MOVER-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one legal adjacent Corridor when the caller did not already fix it"])],
        [{"informationId": "I-MOVEMENT", "subjectRef": "movement class, origin, selected/fixed Corridor, Opportunity attackers/preventions, destination, Secure placement, Noise/Exploration result", "audience": "public", "revealTrigger": "declaration/resolution", "secrecy": "none"}], [],
        [_target("T-MOVEMENT-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-MOVER-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-MOVEMENT-DESTINATION", ["tax.entity.spatial.room", "tax.entity.spatial.room-slot"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "select-target", "if-able", "P-MOVER-OWNER", "one legal adjacent Corridor", ["SA-MOVEMENT-SEQUENCE-RB"], conditions=["caller did not already fix the Corridor or Secret Passage destination"], decision_ref="D-MOVEMENT-CORRIDOR", target_ref="T-MOVEMENT-CORRIDOR"),
            _set_operation_class(operation("S02", 2, "invoke-process", "must", "P-MOVER", "Opportunity Attack cohort before relocation", ["SA-MOVEMENT-SEQUENCE-RB", "SA-MOVEMENT-SEQUENCE-FAQ"], target_ref="T-MOVEMENT-CORRIDOR", invoke="SEM-OPPORTUNITY-ATTACK-001"), attackClass="opportunity", movementTiming="after-direction-before-destination"),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-100 remaining Opportunity Attacks and Movement after mover death/escape/other participation loss", ["SA-MOVEMENT-SEQUENCE-RB"], conditions=["mover ceases participating before destination resolution"]),
            operation("S04", 4, "branch", "must", "P-RULES", "Discovered-Room destination or Unexplored-Corridor Exploration", ["SA-MOVEMENT-SEQUENCE-RB"]),
            operation("S05", 5, "move-entity", "must", "P-MOVER", "selected already Discovered destination Room", ["SA-MOVEMENT-SEQUENCE-RB"], conditions=["Discovered-Room branch", "mover remains eligible under SEM-Q-100"], target_ref="T-MOVEMENT-DESTINATION"),
            operation("S06", 6, "place-component", "if-able", "P-RULES", "1 Secure token in the destination Room", ["SA-MOVEMENT-SEQUENCE-RB"], conditions=["Movement is Cautious", "Discovered-Room branch", "mover reached destination", "Secure token available"], target_ref="T-MOVEMENT-DESTINATION"),
            operation("S07", 7, "invoke-process", "must", "P-MOVER", "post-Movement Noise Roll", ["SA-MOVEMENT-SEQUENCE-RB", "SA-MOVEMENT-SEQUENCE-FAQ"], conditions=["Discovered-Room branch", "mover reached destination", "caller source does not explicitly suppress Noise"], invoke="SEM-NOISE-001"),
            operation("S08", 8, "invoke-process", "must", "P-MOVER", "Exploration Sequence", ["SA-MOVEMENT-SEQUENCE-RB"], conditions=["Unexplored-Corridor branch", "mover remains eligible under SEM-Q-100"], invoke="SEM-ACT-EXPLORE-001"),
        ],
        {"policy": "ordered-complete", "unit": "one source-authorized Character Movement", "onImpossible": "Opportunity Attacks complete before relocation; exact caller suppressions apply only where printed; SEM-Q-100 carries death/escape interruption without a continuation default"},
        {"kind": "instantaneous-movement-sequence"}, {"policy": "one selected/fixed Corridor and one destination branch per Movement"}, [], ["SEM-Q-003", "SEM-Q-100"], [],
    ))

    records.append(record(
        "SEM-ACT-MOVE-CAUTIOUSLY-001", "Make a Move Cautiously Basic Action", "source-backed-with-open-question", "action", "official-primary", "open-alternatives",
        [assertion("SA-CAUTIOUS-ACTION-RB", "SRC-RULEBOOK", "printed pages 12 and 24 / RB-P12-V02, RB-P24-V02 / lines 2896–2905, 4541–4566", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Make a Move Cautiously costs 2 Action cards, is Not In Combat, uses the Movement Sequence, and places one Secure token in the destination after movement before the destination Noise/Entrance effect.", "docs/rules/02-character-actions.md:ACT-MOVE-002")],
        ["icon.actionCard", "icon.notInCombat", "icon.secure", "term.corridor", "term.moving-cautiously"],
        ["tax.entity.agent.character", "tax.entity.component.card.action", "tax.entity.spatial.corridor", "tax.process.action.move-cautiously", "tax.process.sequence.movement"], [],
        timing("TW-CAUTIOUS-ACTION", "tax.process.action.move-cautiously", "during", "per-selected-Basic-Action"),
        [participant("P-CAUTIOUS", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player")], "must",
        [condition("C-CAUTIOUS-ACTION", "all", [{"predicate": "Character is Not In Combat"}, {"predicate": "at least one fully resolvable legal Movement exists"}], ["SA-CAUTIOUS-ACTION-RB"])],
        [decision("D-CAUTIOUS-PAY", "P-OWNER", "player-choice", 2, 2, False, "owner-private-until-discard", ["two own Action cards in hand"])],
        [{"informationId": "I-CAUTIOUS-ACTION", "subjectRef": "declared Basic Action, paid cards, and Movement result", "audience": "public", "revealTrigger": "declaration/payment", "secrecy": "unselected hand remains owner-private"}],
        [{"costId": "COST-CAUTIOUS-ACTION", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 2, "selectionDecisionRef": "D-CAUTIOUS-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [
            operation("S01", 1, "pay-cost", "must", "P-OWNER", "COST-CAUTIOUS-ACTION", ["SA-CAUTIOUS-ACTION-RB"], decision_ref="D-CAUTIOUS-PAY"),
            _set_operation_class(operation("S02", 2, "invoke-process", "must", "P-CAUTIOUS", "one Cautious Character Movement Sequence", ["SA-CAUTIOUS-ACTION-RB"], invoke="SEM-MOVEMENT-SEQUENCE-001"), movementClass="basic-cautious", cautious=True, includeBasicActionCardCost=False),
        ],
        {"policy": "all-or-nothing-selection", "unit": "one paid Cautious Basic Action", "onImpossible": "Action may be selected only when the Movement is fully resolvable; finite Secure unavailability follows component limits and does not become Hazard"},
        {"kind": "instantaneous-basic-action"}, {"policy": "repeatable only as another paid Action"}, [], ["SEM-Q-003", "SEM-Q-100"], [],
    ))

    records.append(record(
        "SEM-OPPORTUNITY-ATTACK-001", "Opportunity Attack cohort during Character Movement", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-OPPORTUNITY-RB", "SRC-RULEBOOK", "printed page 24 / RB-P24-V02 / lines 4541–4558", ["timing", "preconditions", "participants", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Before destination resolution, each Intruder in the Character's origin Room and/or selected Corridor may Attack the moving Character, largest first, with no more than three Attacks.", "docs/rules/03-intruders-and-survival.md:INT-005"),
            assertion("SA-OPPORTUNITY-FAQ", "SRC-FAQ", "Action cards / FQ-P02-U16", ["preconditions", "operations", "partialResolution"], "Movement-limited prevention applies only to Opportunity Attacks and does not prevent a later Hazard-result Attack.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U16"),
        ],
        ["term.attack", "term.opportunity-attack"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.process.attack.opportunity", "tax.process.sequence.movement"], [],
        timing("TW-OPPORTUNITY", "tax.process.attack.opportunity", "during", "once-per-Movement-before-relocation"),
        [participant("P-MOVER", "affected", "tax.entity.agent.character"), participant("P-INTRUDERS", "collection", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-OPPORTUNITY", "subjectRef": "origin/selected Corridor, qualifying Intruders, size order, attack count, prevention use, target participation", "audience": "public", "revealTrigger": "Movement resolution", "secrecy": "none"}], [],
        [_target("T-OPPORTUNITY-INTRUDERS", ["tax.entity.agent.intruder"], mode="unresolved-order"), _target("T-OPPORTUNITY-MOVER", ["tax.entity.agent.character"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "select-target", "must", "P-RULES", "all Intruders in the origin Room and selected Corridor", ["SA-OPPORTUNITY-RB"], target_ref="T-OPPORTUNITY-INTRUDERS"),
            operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-003 equal-largest selection/order when the three-Attack maximum excludes a qualifier", ["SA-OPPORTUNITY-RB"], conditions=["more than three qualifying Intruders or equal-largest ordering can alter outcomes"]),
            _set_operation_class(operation("S03", 3, "invoke-process", "if-able", "each selected Intruder", "one complete Intruder Attack against the moving Character", ["SA-OPPORTUNITY-RB", "SA-OPPORTUNITY-FAQ"], target_ref="T-OPPORTUNITY-MOVER", invoke="SEM-INT-004", repeat={"order": "Queen > Drone > Adult > Larva; equal-size boundary SEM-Q-003", "max": 3, "completeAttackBeforeNext": True, "movementLimitedPreventionApplies": True}), attackClass="opportunity", targetSelection="fixed-moving-Character"),
            operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-100 continuation of remaining Attacks and Movement after target death/escape/participation loss", ["SA-OPPORTUNITY-RB"], conditions=["moving Character ceases participating during cohort"]),
        ],
        {"policy": "ordered-complete", "unit": "one Opportunity Attack at a time within a maximum-three cohort", "onImpossible": "SEM-Q-003 prohibits an equal-size selection/tie-break default; SEM-Q-100 prohibits a death/escape continuation default; FAQ prevention scope remains only Opportunity"},
        {"kind": "pre-relocation-attack-cohort"}, {"policy": "maximum three Attacks, not three Intruders of each location/type"}, [], ["SEM-Q-003", "SEM-Q-060", "SEM-Q-100"], [],
    ))

    records.append(record(
        "SEM-INTRUDER-HIT-RESOLUTION-001", "Resolve source-applied Hits by Intruder type and location", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-INTRUDER-HITS-RB", "SRC-RULEBOOK", "printed pages 33–35 / lines 5514–5530, 5542–5547, 5583–5605, 5628–5687", ["preconditions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Corridor Adults/Larvae die from one allocated Hit and Drones require exactly two; Room Adults/Drones retain Hit markers for a Shoot-die test; a Room Larva dies from one Hit regardless of the die; Queen Hits advance her track up to its maximum and delegate Queen Health timing.", "docs/rules/02-character-actions.md:ACT-SHOOT-001/ACT-BURST-001/ACT-MELEE-001")],
        ["term.adult", "term.drone", "term.hit", "term.larva", "term.queen"],
        ["tax.entity.agent.intruder", "tax.entity.agent.intruder.adult", "tax.entity.agent.intruder.drone", "tax.entity.agent.intruder.larva", "tax.entity.agent.intruder.queen", "tax.entity.spatial.corridor", "tax.entity.spatial.room", "tax.process.operation.hit"], [],
        timing("TW-INTRUDER-HITS", "tax.process.operation.hit", "when-triggered", "per-source-applied-Hit-group"), [participant("P-SOURCE", "actor", "tax.entity.agent.character"), participant("P-TARGET", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-INTRUDER-HITS", "subjectRef": "source attack class, Intruder type/location, assigned Hit count, existing markers, death/Queen-track result", "audience": "public", "revealTrigger": "Hit application/resolution", "secrecy": "Queen Health deck order remains hidden"}], [],
        [_target("T-INTRUDER-HIT", ["tax.entity.agent.intruder"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "branch", "must", "P-RULES", "Corridor Adult/Larva/Drone, Room Larva, Room Adult/Drone, or Queen", ["SA-INTRUDER-HITS-RB"], target_ref="T-INTRUDER-HIT"),
            operation("S02", 2, "remove-component", "must", "P-RULES", "Corridor Adult or Larva assigned 1 Hit, or Corridor Drone assigned exactly 2 Hits", ["SA-INTRUDER-HITS-RB"], conditions=["target is in a Corridor and exact type threshold is met"], target_ref="T-INTRUDER-HIT"),
            operation("S03", 3, "remove-component", "must", "P-RULES", "Room Larva assigned 1 Hit regardless of later Shoot-die result", ["SA-INTRUDER-HITS-RB"], conditions=["target is a Larva in a Room"], target_ref="T-INTRUDER-HIT"),
            operation("S04", 4, "place-component", "must", "P-RULES", "one Universal Hit marker per source-applied Hit next to a Room Adult/Drone", ["SA-INTRUDER-HITS-RB"], conditions=["target is Adult or Drone in a Room"], target_ref="T-INTRUDER-HIT"),
            operation("S05", 5, "invoke-process", "must", "P-SOURCE", "each source-applied Queen Hit through the Queen Hits track", ["SA-INTRUDER-HITS-RB"], conditions=["target is Queen"], target_ref="T-INTRUDER-HIT", invoke="SEM-QUEEN-HIT-001", repeat={"oneAtATime": True, "upToTrackMaximum": True, "overflowInSameAction": "lost"}),
            operation("S06", 6, "prohibit", "must", "P-RULES", "left-over Hit markers on Intruders in Corridors or carrying Room Hit markers into a Corridor", ["SA-INTRUDER-HITS-RB"]),
            operation("S07", 7, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-103 remaining Shoot/Melee die and added-effect operations after the initial Hit removes a Larva", ["SA-INTRUDER-HITS-RB"], conditions=["initial Room Hit kills Larva before the caller's roll step"]),
            operation("S08", 8, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-104 Burst multi-target/Queen resolution and interruption order", ["SA-INTRUDER-HITS-RB"], conditions=["one Burst allocation affects multiple Intruders or includes Queen Hits"]),
        ],
        {"policy": "source-conditional-steps", "unit": "one target's source-assigned Hit group", "onImpossible": "apply exact type/location thresholds; SEM-Q-103/104 preserve continuation and multi-target order without inventing a default"},
        {"kind": "instantaneous-hit-resolution"}, {"policy": "Corridor Hits never persist; Room Adult/Drone markers accumulate only as source-defined"}, [], ["SEM-Q-025", "SEM-Q-103", "SEM-Q-104"], [],
    ))

    shoot_die = record(
        "SEM-SHOOT-DIE-RESULT-001", "Shoot die result during Shoot", "source-backed-with-open-question", "dispatcher", "official-errata", "open-alternatives",
        [
            assertion("SA-SHOOT-DIE-RB", "SRC-RULEBOOK", "printed page 33 / RB-P33-V01 / lines 5583–5605", ["preconditions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Shoot Critical kills; numeric 2–5 kills when the result is at or below current Hits; the Ammo-loss face spends one Ammo use. Larvae and Queen use their special Health rules.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P33-V01"),
            assertion("SA-SHOOT-DIE-FAQ", "SRC-FAQ", "Items and Tactical Gear / FQ-P02-U21", ["operations", "partialResolution", "unresolvedQuestionRefs"], "Weapon result effects are additional to the standard result unless the exact instruction says instead; Ammo loss still spends Ammo.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U21"),
        ],
        ["icon.shootDie2", "icon.shootDie3", "icon.shootDie4", "icon.shootDie5", "icon.shootDieAmmoLoss", "icon.shootDieCritical", "term.shoot"],
        ["tax.entity.agent.intruder", "tax.process.action.attack.shoot"], [],
        timing("TW-SHOOT-DIE", "tax.process.action.attack.shoot", "when-triggered", "per-Shoot-roll"), [participant("P-SHOOTER", "actor", "tax.entity.agent.character"), participant("P-TARGET", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-SHOOT-DIE", "subjectRef": "exact Shoot face, target type/current Hits, standard outcome, Ammo state, exact added/replacement effect", "audience": "public", "revealTrigger": "roll/resolution", "secrecy": "none"}], [], [_target("T-SHOOT-DIE-TARGET", ["tax.entity.agent.intruder"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "draw-random", "must", "P-RULES", "one Shoot-die face", ["SA-SHOOT-DIE-RB"]),
            operation("S02", 2, "branch", "must", "P-RULES", "Critical, numeric 2/3/4/5, or Ammo-loss", ["SA-SHOOT-DIE-RB"], target_ref="T-SHOOT-DIE-TARGET"),
            operation("S03", 3, "remove-component", "if-able", "P-RULES", "non-Queen/non-Larva target on Critical or qualifying numeric result", ["SA-SHOOT-DIE-RB"], conditions=["target uses Adult/Drone Room Health", "Critical OR numeric result is at or below current Hits"], target_ref="T-SHOOT-DIE-TARGET"),
            operation("S04", 4, "invoke-process", "must", "P-SHOOTER", "one Ammo spend through Full/Half-full lifecycle", ["SA-SHOOT-DIE-RB", "SA-SHOOT-DIE-FAQ"], conditions=["Ammo-loss face"], invoke="SEM-AMMO-TOKEN-LIFECYCLE-001"),
            operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-025/029 Queen lethal-result and interrupt relation", ["SA-SHOOT-DIE-RB"], conditions=["target is Queen and result would be lethal under a retained alternative"]),
            operation("S06", 6, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-103 whether this roll/result continues after the initial Hit already killed a Larva", ["SA-SHOOT-DIE-RB"], conditions=["target was a Larva removed by initial Hit"]),
            operation("S07", 7, "invoke-process", "must", "P-RULES", "standard result plus exact Weapon die-result instruction unless it says instead", ["SA-SHOOT-DIE-FAQ"], invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001"),
        ],
        {"policy": "source-conditional-steps", "unit": "one exact Shoot face", "onImpossible": "never substitute Melee's ineffective result for Shoot Ammo loss or invert additional/\"instead\"; Queen/Larva continuation remains no-default"},
        {"kind": "one-Shoot-result"}, {"policy": "one standard result plus each exact applicable added effect"}, [], ["SEM-Q-025", "SEM-Q-029", "SEM-Q-088", "SEM-Q-103"], [],
    )
    shoot_die["operations"][1]["resultBranches"] = [
        {"termId": "icon.shootDieCritical", "standardResult": "critical-kill"},
        *[{"termId": f"icon.shootDie{value}", "standardResult": "kill-if-result-at-or-below-current-Hits", "value": value} for value in (2, 3, 4, 5)],
        {"termId": "icon.shootDieAmmoLoss", "standardResult": "spend-one-Ammo-use"},
    ]
    records.append(shoot_die)

    melee_die = record(
        "SEM-MELEE-SHOOT-DIE-RESULT-001", "Shoot die result during Melee", "source-backed-with-open-question", "dispatcher", "official-primary", "open-alternatives",
        [assertion("SA-MELEE-DIE-RB", "SRC-RULEBOOK", "printed page 34 / RB-P34-V01 / lines 5643–5669", ["preconditions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Melee uses the Shoot die, but its repeated-bar/Ammo face is an Ineffective attack and spends no Ammo. Critical kills; numeric 2–5 kills at or below Hits; Larva and Queen use special Health.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P34-V01")],
        ["icon.shootDie2", "icon.shootDie3", "icon.shootDie4", "icon.shootDie5", "icon.shootDieAmmoLoss", "icon.shootDieCritical", "term.melee-attack"],
        ["tax.entity.agent.intruder", "tax.process.action.attack.melee"], [],
        timing("TW-MELEE-DIE", "tax.process.action.attack.melee", "when-triggered", "per-Melee-roll"), [participant("P-MELEE", "actor", "tax.entity.agent.character"), participant("P-TARGET", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-MELEE-DIE", "subjectRef": "exact Shoot face in Melee context, target type/current Hits, lethal/ineffective result", "audience": "public", "revealTrigger": "roll/resolution", "secrecy": "none"}], [], [_target("T-MELEE-DIE-TARGET", ["tax.entity.agent.intruder"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "draw-random", "must", "P-RULES", "one Shoot-die face in Melee context", ["SA-MELEE-DIE-RB"]),
            operation("S02", 2, "branch", "must", "P-RULES", "Critical, numeric 2/3/4/5, or Ineffective repeated-bar face", ["SA-MELEE-DIE-RB"], target_ref="T-MELEE-DIE-TARGET"),
            operation("S03", 3, "remove-component", "if-able", "P-RULES", "non-Queen/non-Larva target on Critical or qualifying numeric result", ["SA-MELEE-DIE-RB"], conditions=["target uses Adult/Drone Room Health", "Critical OR numeric result is at or below current Hits"], target_ref="T-MELEE-DIE-TARGET"),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "Ineffective repeated-bar face does nothing and spends no Ammo in Melee", ["SA-MELEE-DIE-RB"]),
            operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-025/029 Queen result/interrupt relation in Melee", ["SA-MELEE-DIE-RB"], conditions=["target is Queen"]),
            operation("S06", 6, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-103 whether the roll continues after initial Hit killed a Larva", ["SA-MELEE-DIE-RB"], conditions=["target was a Larva removed by initial Hit"]),
        ],
        {"policy": "source-conditional-steps", "unit": "one exact Shoot face in Melee context", "onImpossible": "never substitute Shoot Ammo spending for Melee Ineffective or resolve a response after a dead target; Queen/Larva continuation remains no-default"},
        {"kind": "one-Melee-result"}, {"policy": "one context-specific standard result"}, [], ["SEM-Q-025", "SEM-Q-029", "SEM-Q-103"], [],
    )
    melee_die["operations"][1]["resultBranches"] = [
        {"termId": "icon.shootDieCritical", "standardResult": "critical-kill"},
        *[{"termId": f"icon.shootDie{value}", "standardResult": "kill-if-result-at-or-below-current-Hits", "value": value} for value in (2, 3, 4, 5)],
        {"termId": "icon.shootDieAmmoLoss", "standardResult": "ineffective-no-effect-no-Ammo-spend"},
    ]
    records.append(melee_die)

    burst_die = record(
        "SEM-BURST-DIE-RESULT-001", "Burst die Hit count and additional-effects face", "source-backed-with-open-question", "dispatcher", "official-errata", "open-alternatives",
        [
            assertion("SA-BURST-DIE-RB", "SRC-RULEBOOK", "printed page 33 / RB-P33-V02 / lines 5508–5537", ["preconditions", "informationPolicy", "operations", "partialResolution", "unresolvedQuestionRefs"], "Burst faces produce exactly 1, 2, 3, or 4 Hits. The additional-effects symbol shares the 4 face, so that face produces both 4 Hits and each applicable additional Weapon/Action effect.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P33-V02"),
            assertion("SA-BURST-DIE-FAQ", "SRC-FAQ", "Items and Tactical Gear / FQ-P02-U21", ["operations", "partialResolution", "unresolvedQuestionRefs"], "A specific Weapon die-result effect is additional unless the exact instruction says instead.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U21"),
        ],
        ["icon.burstDie1", "icon.burstDie2", "icon.burstDie3", "icon.burstDie4", "icon.burstDieAdditionalEffects", "term.burst", "term.hit"],
        ["tax.process.action.attack.burst", "tax.process.operation.hit"], [],
        timing("TW-BURST-DIE", "tax.process.action.attack.burst", "when-triggered", "per-Burst-roll"), [participant("P-BURSTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-BURST-DIE", "subjectRef": "exact Burst face, Hit total, co-located additional symbol, exact added/replacement effect", "audience": "public", "revealTrigger": "roll/resolution", "secrecy": "none"}], [], [],
        [
            operation("S01", 1, "draw-random", "must", "P-RULES", "one Burst-die face", ["SA-BURST-DIE-RB"]),
            operation("S02", 2, "branch", "must", "P-RULES", "exact Hit value 1, 2, 3, or 4", ["SA-BURST-DIE-RB"]),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "the additional-effects symbol coexists with 4 Hits on the same face", ["SA-BURST-DIE-RB"], conditions=["4/additional-effects face"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "retain the additional-effects trigger for caller resolution only after normal Hit allocation/resolution; preserve 4 Hits unless the exact instruction says instead", ["SA-BURST-DIE-RB", "SA-BURST-DIE-FAQ"], conditions=["additional-effects symbol present"]),
        ],
        {"policy": "ordered-complete", "unit": "one exact Burst face", "onImpossible": "never replace 4 Hits with the symbol, invent a symbol on 1/2/3, or invert additional versus instead; wider order remains SEM-Q-088"},
        {"kind": "one-Burst-result"}, {"policy": "one Hit total; symbol co-occurs only with 4"}, [], ["SEM-Q-088"], [],
    )
    burst_die["operations"][1]["resultBranches"] = [
        {"termId": f"icon.burstDie{value}", "hits": value, "additionalEffects": value == 4} for value in (1, 2, 3, 4)
    ]
    burst_die["operations"][2]["coLocatedTermIds"] = ["icon.burstDie4", "icon.burstDieAdditionalEffects"]
    records.append(burst_die)

    records.append(record(
        "SEM-SHOOT-SEQUENCE-001", "Reusable Shoot sequence without Basic-Action payment", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-SHOOT-SEQUENCE-RB", "SRC-RULEBOOK", "printed pages 33–35 / RB-P33-V01 / lines 5560–5605, 5672–5687, 5747–5763", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Choose one working loaded Ranged Weapon and one Intruder in the Character's Room; deal one Hit, roll Shoot, resolve type-specific Health, then exact Weapon modifiers.", "docs/rules/02-character-actions.md:ACT-SHOOT-001"),
            assertion("SA-SHOOT-SEQUENCE-FAQ", "SRC-FAQ", "General rules FQ-P02-U03; Items/Tactical Gear FQ-P02-U21", ["preconditions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Queen shooting follows Adult shooting except lethal resolution uses Queen Health; Weapon die effects are additional unless they say instead.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U03/FQ-P02-U21"),
        ],
        ["icon.shootDieAmmoLoss", "icon.shootDieCritical", "term.hit", "term.queen", "term.ranged-weapon", "term.shoot"],
        ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.component.card.item.weapon.ranged", "tax.process.action.attack.shoot", "tax.process.operation.hit"], [],
        timing("TW-SHOOT-SEQUENCE", "tax.process.action.attack.shoot", "when-triggered", "per-source-authorized-Shoot"),
        [participant("P-SHOOTER", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-TARGET", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must",
        [condition("C-SHOOT-SEQUENCE", "all", [{"predicate": "selected Weapon is a working Ranged Weapon in Hand"}, {"predicate": "selected Weapon has at least one Ammo token unless an exact source removes that requirement"}, {"predicate": "target is an Intruder in the shooter's Room"}], ["SA-SHOOT-SEQUENCE-RB", "SA-SHOOT-SEQUENCE-FAQ"])],
        [decision("D-SHOOT-WEAPON", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one eligible Ranged Weapon"]), decision("D-SHOOT-TARGET", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one eligible co-located Intruder"])],
        [{"informationId": "I-SHOOT-SEQUENCE", "subjectRef": "authorizing source, Weapon, target, initial Hit, die result, type Health, Ammo, Queen trigger, modifiers", "audience": "public", "revealTrigger": "selection/roll/resolution", "secrecy": "Queen Health deck order remains hidden"}], [],
        [_target("T-SHOOT-WEAPON", ["tax.entity.component.card.item.weapon.ranged"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-SHOOT-TARGET", ["tax.entity.agent.intruder"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1)],
        [
            operation("S01", 1, "select-target", "must", "P-OWNER", "one eligible Ranged Weapon", ["SA-SHOOT-SEQUENCE-RB"], decision_ref="D-SHOOT-WEAPON", target_ref="T-SHOOT-WEAPON"),
            operation("S02", 2, "select-target", "must", "P-OWNER", "one Intruder in the shooter's Room; Character, Robot, and non-Intruder targets are ineligible", ["SA-SHOOT-SEQUENCE-RB"], decision_ref="D-SHOOT-TARGET", target_ref="T-SHOOT-TARGET"),
            _set_operation_class(operation("S03", 3, "invoke-process", "must", "P-SHOOTER", "one initial Shoot Hit through type/location Health", ["SA-SHOOT-SEQUENCE-RB", "SA-SHOOT-SEQUENCE-FAQ"], target_ref="T-SHOOT-TARGET", invoke="SEM-INTRUDER-HIT-RESOLUTION-001"), attackClass="character-shoot", hitSource="initial-before-roll"),
            operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-103 roll/added-effect continuation after initial Hit kills a Room Larva", ["SA-SHOOT-SEQUENCE-RB"], conditions=["initial Hit removed a Larva"]),
            operation("S05", 5, "invoke-process", "must", "P-SHOOTER", "context-specific Shoot die result", ["SA-SHOOT-SEQUENCE-RB", "SA-SHOOT-SEQUENCE-FAQ"], conditions=["target/result continuation remains legal under SEM-Q-103"], target_ref="T-SHOOT-TARGET", invoke="SEM-SHOOT-DIE-RESULT-001"),
        ],
        {"policy": "ordered-complete", "unit": "one source-authorized Shoot sequence", "onImpossible": "Weapon/target must be legal; initial Hit precedes the roll; Q025/029/088/103 preserve Queen, added-effect, and dead-Larva continuation without defaults"},
        {"kind": "instantaneous-Shoot-sequence"}, {"policy": "one Weapon, one target, one initial Hit, one die result per invocation unless exact source modifies"}, [], ["SEM-Q-025", "SEM-Q-029", "SEM-Q-088", "SEM-Q-103"], [],
    ))

    records.append(record(
        "SEM-BURST-SEQUENCE-001", "Reusable Burst sequence without Basic-Action payment", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-BURST-SEQUENCE-RB", "SRC-RULEBOOK", "printed page 33 / RB-P33-V02 / lines 5490–5537", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Choose a working loaded Ranged Weapon and adjacent unblocked Corridor, spend one Ammo use, roll Burst, allocate the exact Hit total: at most one per Adult/Larva, exactly two per Drone, any number to Queen up to her track maximum; lose leftovers and resolve the shared 4/additional face.", "docs/rules/02-character-actions.md:ACT-BURST-001"),
            assertion("SA-BURST-SEQUENCE-FAQ", "SRC-FAQ", "General rules FQ-P02-U10; Items/Tactical Gear FQ-P02-U21", ["preconditions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Closed Doors block Burst; exact Weapon die effects are additional unless they say instead.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10/FQ-P02-U21"),
        ],
        ["icon.ammoToken", "icon.burstDieAdditionalEffects", "term.burst", "term.corridor", "term.hit", "term.queen", "term.ranged-weapon"],
        ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.component.card.item.weapon.ranged", "tax.entity.component.token.tactical-gear.ammo", "tax.entity.spatial.corridor", "tax.process.action.attack.burst", "tax.process.operation.hit"], [],
        timing("TW-BURST-SEQUENCE", "tax.process.action.attack.burst", "when-triggered", "per-source-authorized-Burst"),
        [participant("P-BURSTER", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-INTRUDERS", "affected-collection", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must",
        [condition("C-BURST-SEQUENCE", "all", [{"predicate": "selected Weapon is a working loaded Ranged Weapon in Hand"}, {"predicate": "selected Corridor is adjacent and no Closed Door blocks Burst"}], ["SA-BURST-SEQUENCE-RB", "SA-BURST-SEQUENCE-FAQ"])],
        [decision("D-BURST-WEAPON", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one eligible Ranged Weapon"]), decision("D-BURST-CORRIDOR", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one eligible adjacent Corridor"]), decision("D-BURST-HITS", "P-OWNER", "player-choice", 0, None, True, "public-on-allocation", ["legal per-Intruder Hit groups totaling no more than the rolled Hits; any remainder is lost"])],
        [{"informationId": "I-BURST-SEQUENCE", "subjectRef": "authorizing source, Weapon, Corridor, Ammo state, die face/Hit pool, public owner allocation, deaths/Queen track, leftovers, additional effects", "audience": "public", "revealTrigger": "selection/spend/roll/allocation", "secrecy": "Queen Health deck order remains hidden"}], [],
        [_target("T-BURST-WEAPON", ["tax.entity.component.card.item.weapon.ranged"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-BURST-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-BURST-INTRUDERS", ["tax.entity.agent.intruder"], selector="P-OWNER", mode="player-choice")],
        [
            operation("S01", 1, "select-target", "must", "P-OWNER", "one eligible Ranged Weapon", ["SA-BURST-SEQUENCE-RB"], decision_ref="D-BURST-WEAPON", target_ref="T-BURST-WEAPON"),
            operation("S02", 2, "select-target", "must", "P-OWNER", "one eligible adjacent Corridor", ["SA-BURST-SEQUENCE-RB", "SA-BURST-SEQUENCE-FAQ"], decision_ref="D-BURST-CORRIDOR", target_ref="T-BURST-CORRIDOR"),
            operation("S03", 3, "invoke-process", "must", "P-BURSTER", "one Ammo spend through Full/Half-full lifecycle before the roll", ["SA-BURST-SEQUENCE-RB"], invoke="SEM-AMMO-TOKEN-LIFECYCLE-001"),
            operation("S04", 4, "invoke-process", "must", "P-BURSTER", "exact Burst die Hit pool and co-located additional-effects result", ["SA-BURST-SEQUENCE-RB", "SA-BURST-SEQUENCE-FAQ"], invoke="SEM-BURST-DIE-RESULT-001"),
            _set_operation_class(operation("S05", 5, "choose", "must", "P-OWNER", "public legal allocation: max 1 per Adult/Larva, exactly 2 per Drone, any number to Queen up to track maximum; leftovers lost", ["SA-BURST-SEQUENCE-RB"], decision_ref="D-BURST-HITS", target_ref="T-BURST-INTRUDERS"), attackClass="character-burst", allocationOwner="P-OWNER"),
            operation("S06", 6, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-104 target-group resolution order, simultaneity, Queen interrupt, death, and continuation", ["SA-BURST-SEQUENCE-RB"], conditions=["allocation affects multiple Intruders or includes Queen"]),
            operation("S07", 7, "invoke-process", "must", "P-BURSTER", "each exact allocated target Hit group through type/location Health", ["SA-BURST-SEQUENCE-RB"], target_ref="T-BURST-INTRUDERS", invoke="SEM-INTRUDER-HIT-RESOLUTION-001", repeat={"order": "SEM-Q-104 source-unspecified", "perAllocatedTargetGroup": True}),
            operation("S08", 8, "evaluate-condition", "must", "P-RULES", "all unallocated, ineligible, and post-Queen-threshold Hits are lost", ["SA-BURST-SEQUENCE-RB"]),
            operation("S09", 9, "invoke-process", "if-able", "P-RULES", "exact Weapon/Action additional-effect instruction after normal Hit resolution; standard result remains unless the instruction says instead", ["SA-BURST-SEQUENCE-RB", "SA-BURST-SEQUENCE-FAQ"], conditions=["Burst die additional-effects symbol present"], invoke="SEM-WEAPON-DIE-RESULT-ADDITION-001"),
        ],
        {"policy": "ordered-complete", "unit": "one source-authorized Burst and owner allocation", "onImpossible": "exact type cardinalities and Closed-Door block apply; no target/order/default is invented under Q025/Q088/Q104"},
        {"kind": "instantaneous-Burst-sequence"}, {"policy": "one Weapon/Corridor/die pool/allocation per invocation; 4 and additional symbol coexist"}, [], ["SEM-Q-025", "SEM-Q-088", "SEM-Q-104"], [],
    ))

    records.append(record(
        "SEM-MELEE-SEQUENCE-001", "Reusable Melee sequence without Basic-Action payment", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-MELEE-SEQUENCE-RB", "SRC-RULEBOOK", "printed page 34 / RB-P34-V01 / lines 5628–5687", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Gain one Contamination, choose one co-located Intruder, deal one Hit, roll the Shoot die using Melee outcomes, then if the target survives choose a Weapon to malfunction and Prevent the response or resolve its Intruder Attack. A second Weapon Malfunction destroys it.", "docs/rules/02-character-actions.md:ACT-MELEE-001")],
        ["icon.malfunction", "term.contamination-card", "term.hit", "term.melee-attack", "term.weapon"],
        ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.component.card.item.weapon", "tax.entity.component.marker.malfunction", "tax.process.action.attack.melee", "tax.process.operation.hit"], [],
        timing("TW-MELEE-SEQUENCE", "tax.process.action.attack.melee", "when-triggered", "per-source-authorized-Melee"),
        [participant("P-MELEE", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-TARGET", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must",
        [condition("C-MELEE-SEQUENCE", "predicate", [{"predicate": "at least one Intruder is in the Character's Room and the complete source-authorized sequence is legal"}], ["SA-MELEE-SEQUENCE-RB"])],
        [decision("D-MELEE-TARGET", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one co-located Intruder"]), decision("D-MELEE-RESPONSE", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["place Malfunction on one owned Weapon to Prevent", "decline prevention and resolve the target Intruder Attack"]), decision("D-MELEE-WEAPON", "P-OWNER", "player-choice", 1, 1, False, "public-on-placement", ["one owned Weapon when prevention branch selected"])],
        [{"informationId": "I-MELEE-SEQUENCE", "subjectRef": "Contamination gain, target, initial Hit, die result, survival, prevention branch/Weapon, response Attack", "audience": "public", "revealTrigger": "resolution/declaration", "secrecy": "drawn Contamination identity follows its deck/hand visibility after entering discard"}], [],
        [_target("T-MELEE-TARGET", ["tax.entity.agent.intruder"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-MELEE-WEAPON", ["tax.entity.component.card.item.weapon"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1)],
        [
            operation("S01", 1, "invoke-process", "must", "P-MELEE", "gain exactly 1 Contamination into the Character's discard pile", ["SA-MELEE-SEQUENCE-RB"], invoke="SEM-CONTAMINATION-GAIN-001"),
            operation("S02", 2, "select-target", "must", "P-OWNER", "one Intruder in the same Room; Character, Robot, and non-Intruder targets are ineligible", ["SA-MELEE-SEQUENCE-RB"], decision_ref="D-MELEE-TARGET", target_ref="T-MELEE-TARGET"),
            _set_operation_class(operation("S03", 3, "invoke-process", "must", "P-MELEE", "one initial Melee Hit through type/location Health", ["SA-MELEE-SEQUENCE-RB"], target_ref="T-MELEE-TARGET", invoke="SEM-INTRUDER-HIT-RESOLUTION-001"), attackClass="character-melee", hitSource="initial-before-roll"),
            operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-103 roll continuation after initial Hit kills a Larva", ["SA-MELEE-SEQUENCE-RB"], conditions=["initial Hit removed a Larva"]),
            operation("S05", 5, "invoke-process", "must", "P-MELEE", "Shoot die with Melee-specific outcomes", ["SA-MELEE-SEQUENCE-RB"], conditions=["target/result continuation remains legal under SEM-Q-103"], target_ref="T-MELEE-TARGET", invoke="SEM-MELEE-SHOOT-DIE-RESULT-001"),
            operation("S06", 6, "choose", "must", "P-OWNER", "Prevent with one owned Weapon Malfunction or resolve response", ["SA-MELEE-SEQUENCE-RB"], conditions=["target survived"], decision_ref="D-MELEE-RESPONSE"),
            operation("S07", 7, "select-target", "must", "P-OWNER", "one owned Weapon to receive Malfunction", ["SA-MELEE-SEQUENCE-RB"], conditions=["prevention branch selected"], decision_ref="D-MELEE-WEAPON", target_ref="T-MELEE-WEAPON"),
            operation("S08", 8, "invoke-process", "must", "P-OWNER", "Weapon Malfunction/destruction lifecycle; this replaces the pending response Attack", ["SA-MELEE-SEQUENCE-RB"], conditions=["prevention branch selected"], target_ref="T-MELEE-WEAPON", invoke="SEM-WEAPON-MALFUNCTION-LIFECYCLE-001"),
            _set_operation_class(operation("S09", 9, "invoke-process", "must", "P-TARGET", "one Intruder Attack against the Melee Character", ["SA-MELEE-SEQUENCE-RB"], conditions=["target survived", "prevention branch declined"], target_ref="T-MELEE-TARGET", invoke="SEM-INT-004"), attackClass="melee-response", targetSelection="fixed-Melee-attacker"),
        ],
        {"policy": "ordered-complete", "unit": "one source-authorized Melee sequence", "onImpossible": "Contamination precedes target selection; initial Hit precedes roll; response occurs only for a surviving target and is replaced only by the chosen Weapon Malfunction branch"},
        {"kind": "instantaneous-Melee-sequence"}, {"policy": "one target, one die, one response-or-prevention branch"}, [], ["SEM-Q-025", "SEM-Q-029", "SEM-Q-060", "SEM-Q-089", "SEM-Q-103"], [],
    ))

    records.append(record(
        "SEM-ACT-MELEE-001", "Melee Attack Basic Action", "source-backed-with-open-question", "action", "official-primary", "open-alternatives",
        [assertion("SA-MELEE-ACTION-RB", "SRC-RULEBOOK", "printed pages 12 and 34 / lines 2887, 2935–2938, 5628–5687", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "operations", "partialResolution", "unresolvedQuestionRefs"], "Melee Attack costs 1 Action card paid before resolving the printed Melee sequence; a Weapon is not required to select the Basic Action.", "docs/rules/02-character-actions.md:ACT-MELEE-001")],
        ["icon.actionCard", "term.melee-attack"], ["tax.entity.agent.character", "tax.entity.component.card.action", "tax.process.action.attack.melee"], [],
        timing("TW-MELEE-ACTION", "tax.process.action.attack.melee", "during", "per-selected-Basic-Action"), [participant("P-MELEE", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player")], "must",
        [condition("C-MELEE-ACTION", "predicate", [{"predicate": "at least one complete legal Melee sequence exists"}], ["SA-MELEE-ACTION-RB"])],
        [decision("D-MELEE-PAY", "P-OWNER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one own Action card in hand"])],
        [{"informationId": "I-MELEE-ACTION", "subjectRef": "declared Melee Basic Action, paid card, and invoked sequence", "audience": "public", "revealTrigger": "declaration/payment", "secrecy": "unselected hand remains owner-private"}],
        [{"costId": "COST-MELEE-ACTION", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-MELEE-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [operation("S01", 1, "pay-cost", "must", "P-OWNER", "COST-MELEE-ACTION", ["SA-MELEE-ACTION-RB"], decision_ref="D-MELEE-PAY"), _set_operation_class(operation("S02", 2, "invoke-process", "must", "P-MELEE", "one Melee sequence without another Basic-Action payment", ["SA-MELEE-ACTION-RB"], invoke="SEM-MELEE-SEQUENCE-001"), attackClass="character-melee", invocationClass="paid-basic-action")],
        {"policy": "all-or-nothing-selection", "unit": "one paid Melee Basic Action", "onImpossible": "pay before sequence; no nested Basic-Action payment; affected continuation/Queen/response questions remain explicit"},
        {"kind": "instantaneous-basic-action"}, {"policy": "repeatable only as another paid Action"}, [], ["SEM-Q-025", "SEM-Q-029", "SEM-Q-060", "SEM-Q-089", "SEM-Q-103"], [],
    ))

    return records


def _build_replacement_records(record, assertion, timing, participant, condition, decision, operation, attack_rule_ids: list[str]) -> dict[str, dict]:
    replacements: list[dict] = []

    replacements.append(record(
        "SEM-ACT-MOVE-001", "Make a Move Basic Action", "source-backed-with-open-question", "action", "official-primary", "open-alternatives",
        [assertion("SA-MOVE-ACTION-RB", "SRC-RULEBOOK", "printed pages 12 and 24 / lines 2876–2878, 2935–2938, 4541–4576", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "operations", "partialResolution", "unresolvedQuestionRefs"], "Make a Move costs 1 Action card paid before resolving one legal Character Movement Sequence.", "docs/rules/02-character-actions.md:ACT-MOVE-001")],
        ["icon.actionCard", "term.move", "term.movement-sequence"], ["tax.entity.agent.character", "tax.entity.component.card.action", "tax.process.action.move", "tax.process.sequence.movement"], [],
        timing("TW-MOVE-ACTION", "tax.process.action.move", "during", "per-selected-Basic-Action"), [participant("P-MOVER", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player")], "must",
        [condition("C-MOVE-ACTION", "predicate", [{"predicate": "at least one complete legal Movement Sequence exists"}], ["SA-MOVE-ACTION-RB"])],
        [decision("D-MOVE-PAY", "P-OWNER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one own Action card in hand"])],
        [{"informationId": "I-MOVE-ACTION", "subjectRef": "declared Basic Action, paid card, and Movement result", "audience": "public", "revealTrigger": "declaration/payment", "secrecy": "unselected hand remains owner-private"}],
        [{"costId": "COST-MOVE-ACTION", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-MOVE-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [operation("S01", 1, "pay-cost", "must", "P-OWNER", "COST-MOVE-ACTION", ["SA-MOVE-ACTION-RB"], decision_ref="D-MOVE-PAY"), _set_operation_class(operation("S02", 2, "invoke-process", "must", "P-MOVER", "one normal Character Movement Sequence", ["SA-MOVE-ACTION-RB"], invoke="SEM-MOVEMENT-SEQUENCE-001"), movementClass="basic-normal", includeBasicActionCardCost=False)],
        {"policy": "all-or-nothing-selection", "unit": "one paid Move Basic Action", "onImpossible": "pay before sequence; no nested Basic-Action payment; Opportunity/death ordering questions remain explicit"},
        {"kind": "instantaneous-basic-action"}, {"policy": "repeatable only as another paid Action"}, [], ["SEM-Q-003", "SEM-Q-100"], [],
    ))

    replacements.append(record(
        "SEM-ACT-SHOOT-001", "Shoot Basic Action", "source-backed-with-open-question", "action", "official-errata", "open-alternatives",
        [
            assertion("SA-SHOOT-ACTION-RB", "SRC-RULEBOOK", "printed pages 12 and 33 / lines 2883, 2935–2938, 5560–5605", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "operations", "partialResolution", "unresolvedQuestionRefs"], "Shoot costs 1 Action card paid before one legal Shoot sequence.", "docs/rules/02-character-actions.md:ACT-SHOOT-001"),
            assertion("SA-SHOOT-ACTION-FAQ", "SRC-FAQ", "General rules / FQ-P02-U03", ["operations", "partialResolution", "unresolvedQuestionRefs"], "Queen shooting resolves Queen Health instead of removing the miniature.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U03"),
        ],
        ["icon.actionCard", "term.shoot"], ["tax.entity.agent.character", "tax.entity.component.card.action", "tax.process.action.attack.shoot"], [],
        timing("TW-SHOOT-ACTION", "tax.process.action.attack.shoot", "during", "per-selected-Basic-Action"), [participant("P-SHOOTER", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player")], "must",
        [condition("C-SHOOT-ACTION", "predicate", [{"predicate": "at least one complete legal Shoot sequence exists"}], ["SA-SHOOT-ACTION-RB"])],
        [decision("D-SHOOT-PAY", "P-OWNER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one own Action card in hand"])],
        [{"informationId": "I-SHOOT-ACTION", "subjectRef": "declared Shoot Basic Action, paid card, and invoked sequence", "audience": "public", "revealTrigger": "declaration/payment", "secrecy": "unselected hand remains owner-private"}],
        [{"costId": "COST-SHOOT-ACTION", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-SHOOT-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [operation("S01", 1, "pay-cost", "must", "P-OWNER", "COST-SHOOT-ACTION", ["SA-SHOOT-ACTION-RB"], decision_ref="D-SHOOT-PAY"), _set_operation_class(operation("S02", 2, "invoke-process", "must", "P-SHOOTER", "one Shoot sequence without another Basic-Action payment", ["SA-SHOOT-ACTION-RB", "SA-SHOOT-ACTION-FAQ"], invoke="SEM-SHOOT-SEQUENCE-001"), attackClass="character-shoot", invocationClass="paid-basic-action")],
        {"policy": "all-or-nothing-selection", "unit": "one paid Shoot Basic Action", "onImpossible": "pay before sequence; no nested payment; Queen/Weapon/Larva timing questions remain no-default"},
        {"kind": "instantaneous-basic-action"}, {"policy": "repeatable only as another paid Action"}, [], ["SEM-Q-025", "SEM-Q-029", "SEM-Q-088", "SEM-Q-103"], [],
    ))

    replacements.append(record(
        "SEM-ACT-BURST-001", "Burst Basic Action", "source-backed-with-open-question", "action", "official-errata", "open-alternatives",
        [
            assertion("SA-BURST-ACTION-RB", "SRC-RULEBOOK", "printed pages 12 and 33 / lines 2885, 2935–2938, 5490–5537", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "operations", "partialResolution", "unresolvedQuestionRefs"], "Burst costs 1 Action card paid before one legal Burst sequence.", "docs/rules/02-character-actions.md:ACT-BURST-001"),
            assertion("SA-BURST-ACTION-FAQ", "SRC-FAQ", "General rules / FQ-P02-U10", ["preconditions", "operations"], "A Closed Door blocks Burst through it.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10"),
        ],
        ["icon.actionCard", "term.burst"], ["tax.entity.agent.character", "tax.entity.component.card.action", "tax.process.action.attack.burst"], [],
        timing("TW-BURST-ACTION", "tax.process.action.attack.burst", "during", "per-selected-Basic-Action"), [participant("P-BURSTER", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player")], "must",
        [condition("C-BURST-ACTION", "predicate", [{"predicate": "at least one complete legal Burst sequence exists"}], ["SA-BURST-ACTION-RB", "SA-BURST-ACTION-FAQ"])],
        [decision("D-BURST-PAY", "P-OWNER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one own Action card in hand"])],
        [{"informationId": "I-BURST-ACTION", "subjectRef": "declared Burst Basic Action, paid card, and invoked sequence", "audience": "public", "revealTrigger": "declaration/payment", "secrecy": "unselected hand remains owner-private"}],
        [{"costId": "COST-BURST-ACTION", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-BURST-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [operation("S01", 1, "pay-cost", "must", "P-OWNER", "COST-BURST-ACTION", ["SA-BURST-ACTION-RB"], decision_ref="D-BURST-PAY"), _set_operation_class(operation("S02", 2, "invoke-process", "must", "P-BURSTER", "one Burst sequence without another Basic-Action payment", ["SA-BURST-ACTION-RB", "SA-BURST-ACTION-FAQ"], invoke="SEM-BURST-SEQUENCE-001"), attackClass="character-burst", invocationClass="paid-basic-action")],
        {"policy": "all-or-nothing-selection", "unit": "one paid Burst Basic Action", "onImpossible": "pay before sequence; no nested payment; exact allocation/Queen/additional-effect questions remain no-default"},
        {"kind": "instantaneous-basic-action"}, {"policy": "repeatable only as another paid Action"}, [], ["SEM-Q-025", "SEM-Q-088", "SEM-Q-104"], [],
    ))

    replacements.append(record(
        "SEM-NOISE-001", "Noise Roll", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-NOISE", "SRC-RULEBOOK", "printed page 25 / RB-P25-V01 / lines 4669–4705", ["timing", "participants", "informationPolicy", "operations", "partialResolution", "unresolvedQuestionRefs"], "Roll one Noise die and dispatch exactly its official 1/2/3/4/Hazard result. A Noise roll is mandatory after each Character Movement unless an exact special effect suppresses it.", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P25-V01")],
        ["icon.noiseDie1", "icon.noiseDie2", "icon.noiseDie3", "icon.noiseDie4", "icon.noiseDieHazard", "term.noise-roll"], ["tax.entity.agent.character", "tax.process.sequence.noise-roll"], [],
        timing("TW-NOISE", "tax.process.sequence.noise-roll", "when-triggered", "per-required-Noise-roll"), [participant("P-ROLLER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-NOISE", "subjectRef": "rolled official face and complete public result", "audience": "public", "revealTrigger": "roll", "secrecy": "none"}], [], [],
        [operation("S01", 1, "draw-random", "must", "P-ROLLER", "one Noise-die face", ["SA-NOISE"]), operation("S02", 2, "invoke-process", "must", "P-RULES", "exact official Noise result", ["SA-NOISE"], invoke="SEM-NOISE-RESULT-001")],
        {"policy": "ordered-complete", "unit": "one Noise roll/result", "onImpossible": "no matching number does nothing; downstream bag/order questions remain explicit; no Silence/Danger/marker-limit substitution"},
        {"kind": "instantaneous-procedure"}, {"policy": "one die result per roll"}, [], ["SEM-Q-097", "SEM-Q-098", "SEM-Q-099", "SEM-Q-105"], [],
    ))

    replacements.append(record(
        "SEM-NOISE-NUMERIC-CORRIDOR-001", "Resolve one matching Corridor for a numeric Noise result", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-NOISE-CORRIDOR", "SRC-RULEBOOK", "printed page 25 / RB-P25-V01, RB-P25-V02 / lines 4677–4692, 4707–4710", ["preconditions", "participants", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "For one adjacent matching-value Corridor: if it contains Intruder(s), its largest enters and immediately Attacks; otherwise if it has Noise, resolve that marker; otherwise place one Noise marker. Complete this Corridor before another.", "docs/rules/02-character-actions.md:Noise-roll procedure")],
        ["icon.intruder", "icon.noise", "term.attack", "term.corridor", "term.noise-roll"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.component.marker.noise", "tax.entity.spatial.corridor", "tax.process.sequence.noise-roll"], [],
        timing("TW-NOISE-CORRIDOR", "tax.process.sequence.noise-roll", "when-triggered", "per-matching-adjacent-Corridor"), [participant("P-ROLLER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must",
        [condition("C-NOISE-CORRIDOR", "predicate", [{"predicate": "the caller Corridor is adjacent and matches the rolled official numeric result under the active standard/Deadly value rule"}], ["SA-NOISE-CORRIDOR"])], [],
        [{"informationId": "I-NOISE-CORRIDOR", "subjectRef": "Corridor state at its turn, largest Intruder/move/entry Attack OR marker draw/spawn OR marker placement/no-op", "audience": "public", "revealTrigger": "resolution", "secrecy": "none"}], [],
        [_target("T-NOISE-CORRIDOR", ["tax.entity.spatial.corridor"], minimum=1, maximum=1), _target("T-NOISE-CORRIDOR-INTRUDER", ["tax.entity.agent.intruder"], mode="deterministic-state-filter", minimum=0, maximum=1)],
        [
            operation("S01", 1, "branch", "must", "P-RULES", "Intruder-present, else existing-Noise, else empty/no-Noise", ["SA-NOISE-CORRIDOR"], target_ref="T-NOISE-CORRIDOR"),
            operation("S02", 2, "select-target", "must", "P-RULES", "largest Intruder: Queen > Drone > Adult > Larva", ["SA-NOISE-CORRIDOR"], conditions=["Intruder-present branch"], target_ref="T-NOISE-CORRIDOR-INTRUDER"),
            operation("S03", 3, "move-entity", "must", "largest selected Intruder", "rolling Character's Room", ["SA-NOISE-CORRIDOR"], conditions=["Intruder-present branch"], target_ref="T-NOISE-CORRIDOR-INTRUDER"),
            _set_operation_class(operation("S04", 4, "invoke-process", "must", "moved Intruder", "immediate Secure/entry Attack before this Corridor completes", ["SA-NOISE-CORRIDOR"], conditions=["Intruder-present branch"], target_ref="T-NOISE-CORRIDOR-INTRUDER", invoke="SEM-SECURE-ENTRY-001"), attackClass="noise-entry", entryCause="numeric-Noise-Corridor-result", targetSelection="fixed-Noise-rolling-Character"),
            operation("S05", 5, "invoke-process", "must", "P-RULES", "the one existing Noise marker", ["SA-NOISE-CORRIDOR"], conditions=["no Intruder and existing-Noise branch"], target_ref="T-NOISE-CORRIDOR", invoke="SEM-NOISE-MARKER-001"),
            operation("S06", 6, "place-component", "if-able", "P-RULES", "one Noise marker in the matching Corridor", ["SA-NOISE-CORRIDOR"], conditions=["no Intruder and no existing Noise", "Noise marker is available"], target_ref="T-NOISE-CORRIDOR"),
            operation("S07", 7, "evaluate-condition", "must", "P-RULES", "unavailable Noise marker does nothing; it does not become Hazard or resolve a marker", ["SA-NOISE-CORRIDOR"], conditions=["no Intruder and no existing Noise", "no Noise marker available"]),
        ],
        {"policy": "source-conditional-steps", "unit": "one matching Corridor's mutually exclusive branch", "onImpossible": "complete immediate entry consequences before returning; no marker-limit Hazard; inter-Corridor order remains SEM-Q-097"},
        {"kind": "instantaneous-subprocedure"}, {"policy": "once per matching Corridor per numeric Noise result"}, [], ["SEM-Q-097", "SEM-Q-100"], [],
    ))

    marker_dispatch = ["SEM-IH-QA-C-01", "SEM-IH-QA-C-02", "SEM-IH-QA-C-03", "SEM-IH-QA-BOTTOM-01", "SEM-IH-QD-C-01", "SEM-IH-QD-C-02", "SEM-IH-QD-C-03", "SEM-IH-QD-BOTTOM-01"]
    noise_marker = record(
        "SEM-NOISE-MARKER-001", "Resolve one existing Noise marker in a Corridor", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-NOISE-MARKER-RB", "SRC-RULEBOOK", "printed pages 25 and 30 / RB-P25-V02, RB-P30-V01 / lines 4655–4668, 5182–5198", ["preconditions", "informationPolicy", "operations", "partialResolution", "unresolvedQuestionRefs"], "Remove the existing marker, draw one Intruder token, resolve its back in that same Corridor against the current Help side, then apply exact token/model lifecycle. Blank always returns to the bag.", "docs/rules/03-intruders-and-survival.md:INT-002"),
            assertion("SA-NOISE-MARKER-FAQ", "SRC-FAQ", "General rules / FQ-P02-U08", ["preconditions", "operations", "partialResolution"], "A Noise marker can be resolved only if it already exists; never create one to satisfy the instruction.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U08"),
        ],
        ["icon.intruder", "icon.noise", "term.corridor"], ["tax.entity.agent.intruder", "tax.entity.component.marker.noise", "tax.entity.spatial.corridor", "tax.scaffold.zone.intruder-bag"], [],
        timing("TW-NOISE-MARKER", "tax.entity.component.marker.noise", "when-triggered", "per-existing-marker"), [participant("P-RULES", "rules-system")], "must",
        [condition("C-NOISE-MARKER", "predicate", [{"predicate": "caller Corridor currently contains one Noise marker"}], ["SA-NOISE-MARKER-RB", "SA-NOISE-MARKER-FAQ"])], [],
        [{"informationId": "I-NOISE-MARKER", "subjectRef": "removed marker, bag availability, drawn token/back, Queen side, exact Corridor row, Adult/Drone counts, capacity/supply, token destination", "audience": "public", "revealTrigger": "removal/draw/resolution", "secrecy": "unrevealed bag contents and token-pile order remain hidden"}], [], [_target("T-NOISE-MARKER-CORRIDOR", ["tax.entity.spatial.corridor"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "remove-component", "must", "P-RULES", "the existing Noise marker", ["SA-NOISE-MARKER-RB", "SA-NOISE-MARKER-FAQ"], target_ref="T-NOISE-MARKER-CORRIDOR"),
            operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-098 required token draw when Intruder bag is empty", ["SA-NOISE-MARKER-RB"], conditions=["Intruder bag has no token"]),
            operation("S03", 3, "draw-random", "must", "P-RULES", "one Intruder token from the bag; inspect the back for Corridor context", ["SA-NOISE-MARKER-RB"], conditions=["Intruder bag contains at least one token"]),
            operation("S04", 4, "invoke-selected-process", "must", "P-RULES", "exact Queen-side Corridor row or side-level Blank row selected by the drawn back", ["SA-NOISE-MARKER-RB"], conditions=["token was drawn"]),
        ],
        {"policy": "ordered-complete", "unit": "one existing marker and one token draw/dispatch", "onImpossible": "marker removal precedes draw; Q098 leaves empty-bag continuation no-default; Q099/105 affect only Blank/mixed-type subclauses"},
        {"kind": "instantaneous-procedure"}, {"policy": "one token result per removed marker; token lifecycle belongs to exact Help row"}, [], ["SEM-Q-098", "SEM-Q-099", "SEM-Q-105"], [],
    )
    noise_marker["operations"][3]["dispatchRuleIds"] = marker_dispatch
    replacements.append(noise_marker)

    hazard_dispatch = ["SEM-IH-QA-R-01", "SEM-IH-QA-R-02", "SEM-IH-QA-BOTTOM-01", "SEM-IH-QD-R-01", "SEM-IH-QD-R-02", "SEM-IH-QD-BOTTOM-01"]
    hazard = record(
        "SEM-NOISE-HAZARD-001", "Resolve one direct Hazard result", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-NOISE-HAZARD-RB", "SRC-RULEBOOK", "printed pages 25 and 30 / RB-P25-V01, RB-P25-V02, RB-P30-V01 / lines 4693–4710, 5182–5198", ["preconditions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Draw one Intruder token, ignore its back completely, and resolve only its front in the affected Character's Room under the current Help side. Any newly placed Intruder immediately attempts an entry Attack; discard/return/remove the token exactly as stated.", "docs/rules/03-intruders-and-survival.md:INT-002"),
            assertion("SA-NOISE-HAZARD-FAQ", "SRC-FAQ", "Action cards / FQ-P02-U16; General rules / FQ-P02-U13", ["preconditions", "operations", "partialResolution"], "Movement-limited prevention does not prevent a Hazard Attack; Secure tokens do prevent Attacks from Hazard-placed Intruders.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U13/FQ-P02-U16"),
        ],
        ["icon.intruder", "icon.noiseDieHazard", "term.room"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.spatial.room", "tax.scaffold.zone.intruder-bag"], [],
        timing("TW-NOISE-HAZARD", "tax.process.sequence.noise-roll", "when-triggered", "per-Hazard-result"), [participant("P-AFFECTED", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-NOISE-HAZARD", "subjectRef": "bag availability, drawn front only, ignored back, Queen side, Room/Blank row, placed type, Secure/general prevention, immediate Attack, token destination", "audience": "public", "revealTrigger": "draw/resolution", "secrecy": "token back is not an input and unrevealed bag contents remain hidden"}], [], [_target("T-HAZARD-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-098 required token draw when Intruder bag is empty", ["SA-NOISE-HAZARD-RB"], conditions=["Intruder bag has no token"]),
            operation("S02", 2, "draw-random", "must", "P-RULES", "one Intruder token from the bag; inspect only its front", ["SA-NOISE-HAZARD-RB"], conditions=["Intruder bag contains at least one token"]),
            _set_operation_class(operation("S03", 3, "invoke-selected-process", "must", "P-RULES", "exact Queen-side Room row or side-level Blank row selected by token front", ["SA-NOISE-HAZARD-RB", "SA-NOISE-HAZARD-FAQ"], conditions=["token was drawn"], target_ref="T-HAZARD-CHARACTER"), attackClass="hazard-entry", movementLimitedPreventionApplies=False, secureEntryReplacementApplies=True),
            operation("S04", 4, "prohibit", "must", "P-RULES", "reading the token back, using back quantity/color, or applying a Movement-only Opportunity prevention to the Hazard Attack", ["SA-NOISE-HAZARD-RB", "SA-NOISE-HAZARD-FAQ"]),
        ],
        {"policy": "ordered-complete", "unit": "one Hazard token front and exact Help dispatch", "onImpossible": "Q098 leaves empty-bag behavior no-default; Q099 leaves only side-level Blank add-Adults scope open; unaffected type placement/entry Attack continues"},
        {"kind": "instantaneous-procedure"}, {"policy": "one front-only token result per Hazard"}, [], ["SEM-Q-098", "SEM-Q-099"], [],
    )
    hazard["operations"][2]["dispatchRuleIds"] = hazard_dispatch
    replacements.append(hazard)

    attack = record(
        "SEM-INT-004", "Intruder Attack with exact trigger class, target, prevention, and card/Larva branch", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-ATTACK-RB", "SRC-RULEBOOK", "printed pages 15, 24–25, 30, 32, and 34 / RB-P30-V02, RB-P32-V01 / lines 3313–3324, 4551–4558, 4707–4710, 5143–5159, 5393–5430, 5661–5667", ["timing", "preconditions", "participants", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "An Intruder Attack retains its source trigger/target. Before a standard draw, a prevention ignores the entire Attack and draws no card. Non-Larvae draw one exact Attack card, resolve the matching type panel, then discard unless the card moved itself. Larva instead gives Contamination then moves to the Character board or is discarded.", "docs/rules/03-intruders-and-survival.md:INT-004"),
            assertion("SA-ATTACK-FAQ", "SRC-FAQ", "Action cards FQ-P02-U16; Rooms FQ-P02-U19", ["preconditions", "operations", "partialResolution", "unresolvedQuestionRefs"], "Movement-limited prevention is Opportunity-only; otherwise exact effects that Prevent Intruder Attacks can prevent source-defined Attacks such as Technical Corridor Entrance.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U16/FQ-P02-U19"),
        ],
        ["term.attack", "term.contamination-card", "term.intruder-attack-card", "term.larva", "term.turn-order"],
        ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.agent.intruder.larva", "tax.entity.component.card.contamination", "tax.entity.component.card.intruder-attack", "tax.process.attack", "tax.value.turn-order"], [],
        timing("TW-INTRUDER-ATTACK", "tax.process.attack", "when-triggered", "per-attacking-Intruder-and-source-trigger"), [participant("P-INTRUDER", "actor", "tax.entity.agent.intruder"), participant("P-TARGET", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-INTRUDER-ATTACK", "subjectRef": "attack class/cause, attacker, fixed/selected target, available prevention/replacement, Larva/card branch, deck availability, exact occurrence/panel, outcomes", "audience": "public", "revealTrigger": "trigger/prevention/draw/resolution", "secrecy": "unrevealed Attack deck order remains hidden"}], [],
        [_target("T-INTRUDER-ATTACK-TARGET", ["tax.entity.agent.character"], mode="deterministic-turn-order", minimum=0, maximum=1)],
        [
            operation("S01", 1, "branch", "must", "P-RULES", "caller-fixed target versus entry target: player-effect source Character if possible, otherwise first in Turn order", ["SA-ATTACK-RB"], target_ref="T-INTRUDER-ATTACK-TARGET"),
            operation("S02", 2, "select-target", "if-able", "P-RULES", "one eligible Character under the exact caller/entry target rule", ["SA-ATTACK-RB"], target_ref="T-INTRUDER-ATTACK-TARGET"),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-060 simultaneous Reaction/prevention/replacement priority and stacking before any Attack-card draw", ["SA-ATTACK-RB", "SA-ATTACK-FAQ"], conditions=["more than one source-legal pre-resolution effect is available"]),
            operation("S04", 4, "end-process", "must", "P-RULES", "the entire pending Intruder Attack with no card draw or additional effects", ["SA-ATTACK-RB", "SA-ATTACK-FAQ"], conditions=["an exact source-legal effect Prevented the Attack"]),
            operation("S05", 5, "branch", "must", "P-RULES", "Larva Attack or standard non-Larva Attack", ["SA-ATTACK-RB"], conditions=["Attack not prevented"]),
            operation("S06", 6, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-101 required standard Attack draw when the finite Attack deck is empty and no instruction reshuffled it", ["SA-ATTACK-RB"], conditions=["non-Larva attacker", "Attack deck empty"]),
            operation("S07", 7, "draw-random", "must", "P-RULES", "one physical Intruder Attack occurrence into resolution", ["SA-ATTACK-RB"], conditions=["non-Larva attacker", "Attack deck contains a card"]),
            operation("S08", 8, "invoke-selected-process", "must", "P-INTRUDER", "exact occurrence-specific panel selected by exact attacker-type badge association", ["SA-ATTACK-RB"], conditions=["non-Larva attacker", "card was drawn"], notes="Dispatch remains full CardID/GUID/CustomDeck/FaceURL/generated-cell keyed; never title, folder, cell alone, type expectation, or modulo."),
            operation("S09", 9, "transition-zone", "if-able", "P-RULES", "resolved Attack card still in resolution", ["SA-ATTACK-RB"], conditions=["non-Larva attacker", "card remains in sem.zone.card-in-resolution"], transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"}),
            operation("S10", 10, "invoke-process", "must", "P-RULES", "gain exactly 1 Contamination into target discard pile", ["SA-ATTACK-RB"], conditions=["Larva attacker"], target_ref="T-INTRUDER-ATTACK-TARGET", invoke="SEM-CONTAMINATION-GAIN-001"),
            operation("S11", 11, "move-entity", "if-able", "attacking Larva", "target Character board", ["SA-ATTACK-RB"], conditions=["Larva attacker", "target board has no Larva"], target_ref="T-INTRUDER-ATTACK-TARGET"),
            operation("S12", 12, "remove-component", "if-able", "P-RULES", "attacking Larva back to Intruder pool", ["SA-ATTACK-RB"], conditions=["Larva attacker", "target board already has a Larva"], target_ref="T-INTRUDER-ATTACK-TARGET"),
        ],
        {"policy": "source-conditional-steps", "unit": "one exact-class Intruder Attack", "onImpossible": "no eligible target means no target is invented; prevention ends before draw; Q101 leaves empty Attack deck no-default; caller attack class/target is never flattened"},
        {"kind": "instantaneous-Intruder-Attack"}, {"policy": "one attacker, one target, one prevention window, then one Larva or card branch"}, [], ["SEM-Q-060", "SEM-Q-101"], [],
    )
    attack["operations"][0]["attackClassTargetRules"] = {
        "opportunity": "fixed moving Character",
        "intruder-phase": "caller cohort target: first in Turn order, then next after death/leave",
        "noise-entry": "fixed Noise-rolling Character",
        "hazard-entry": "player-effect source Character if possible, otherwise first in Turn order",
        "other-entry": "player-effect source Character if possible, otherwise first in Turn order",
        "melee-response": "fixed Melee attacker",
        "effect-requested": "exact caller-provided target rule",
    }
    attack["operations"][7]["dispatchRuleIds"] = list(attack_rule_ids)
    replacements.append(attack)

    replacements.append(record(
        "SEM-SECURE-ENTRY-001", "Immediate Intruder entry Attack and Secure replacement", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [
            assertion("SA-ENTRY-SECURE-RB", "SRC-RULEBOOK", "printed pages 23, 25, 30, and 32 / lines 4406–4413, 4707–4710, 5139–5146, 5424–5430", ["timing", "preconditions", "participants", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Whenever an Intruder is placed/moved into a Room containing a Character, it immediately tries to Attack. One Secure token is discarded instead of that entry Attack and this discard cannot be prevented; Secure never protects from an Intruder already in the Room.", "docs/rules/03-intruders-and-survival.md:INT-004"),
            assertion("SA-ENTRY-SECURE-FAQ", "SRC-FAQ", "General rules / FQ-P02-U13", ["preconditions", "operations", "partialResolution"], "Secure tokens prevent Attacks from Intruders being placed in the Room.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U13"),
        ],
        ["icon.intruder", "icon.secure", "term.attack"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.component.token.secure", "tax.entity.spatial.room", "tax.process.attack"], [],
        timing("TW-ENTRY-SECURE", "tax.process.attack", "before-attack-resolution", "per-entering-Intruder-before-enclosing-effect-continues"), [participant("P-ENTERING", "actor", "tax.entity.agent.intruder"), participant("P-TARGET", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must",
        [condition("C-ENTRY-SECURE", "all", [{"predicate": "one Intruder was newly placed or moved into a Room"}, {"predicate": "at least one Character is in that Room"}], ["SA-ENTRY-SECURE-RB", "SA-ENTRY-SECURE-FAQ"])], [],
        [{"informationId": "I-ENTRY-SECURE", "subjectRef": "entry cause/class, entering Intruder, target rule, public Secure count/status, prevented/resolved Attack, enclosing-effect pause", "audience": "public", "revealTrigger": "entry", "secrecy": "none"}], [], [_target("T-ENTRY-TARGET", ["tax.entity.agent.character"], mode="deterministic-turn-order", minimum=0, maximum=1)],
        [
            operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "OQ-007 simultaneous multi-Intruder entry and scarce Secure allocation", ["SA-ENTRY-SECURE-RB"], conditions=["more than one Intruder enters simultaneously"]),
            operation("S02", 2, "remove-component", "must", "P-RULES", "exactly 1 Secure token instead of this entering Intruder's Attack; discard cannot be prevented", ["SA-ENTRY-SECURE-RB", "SA-ENTRY-SECURE-FAQ"], conditions=["a Secure token applies to this entry Attack"]),
            _set_operation_class(operation("S03", 3, "invoke-process", "must", "P-ENTERING", "one immediate Intruder Attack before the enclosing effect resumes", ["SA-ENTRY-SECURE-RB", "SA-ENTRY-SECURE-FAQ"], conditions=["no Secure token replaced this entry Attack"], target_ref="T-ENTRY-TARGET", invoke="SEM-INT-004"), attackClass="caller-preserved-entry-class", targetSelection="player-effect source Character if possible, otherwise first in Turn order"),
            operation("S04", 4, "prohibit", "must", "P-RULES", "using Secure against an Intruder already in the Room or preventing the Secure discard itself", ["SA-ENTRY-SECURE-RB"]),
        ],
        {"policy": "replacement-effect", "unit": "one entering Intruder's immediate Attack", "onImpossible": "single-entry behavior is exact; OQ-007 retains true simultaneous allocation/grouping without a default; enclosing resolution waits for each resolved entry consequence"},
        {"kind": "immediate-entry-attack-window"}, {"policy": "one Secure replaces one entry Attack under the singular rule; simultaneous grouping unresolved"}, [], ["OQ-007", "SEM-Q-060"], [],
    ))

    replacements.append(record(
        "SEM-RT-008", "Intruder Phase: Burning then ordered Intruder Attack cohorts", "source-backed-with-open-question", "sequence", "official-primary", "open-alternatives",
        [assertion("SA-RT008-1", "SRC-RULEBOOK", "printed pages 14–15 / lines 3300–3324", ["timing", "participants", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Resolve Intruders Burning, then each Intruder in each Room with a Character Attacks. Rooms go top-left row by row; larger Intruders attack first; all initially target the first Character in Turn order, switching only after that Character dies or leaves.", "docs/rules/01-round-and-turns.md:RT-008")],
        ["icon.fire", "term.attack", "term.hit", "term.intruder-phase", "term.turn-order"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.component.marker.fire", "tax.process.attack", "tax.process.operation.hit", "tax.process.temporal.phase.intruder", "tax.value.turn-order"], [],
        timing("TW-INTRUDER-PHASE", "tax.process.temporal.phase.intruder", "during", "once-per-round"), [participant("P-RULES", "rules-system"), participant("P-INTRUDERS", "collection", "tax.entity.agent.intruder"), participant("P-CHARACTERS", "collection", "tax.entity.agent.character")], "must", [], [],
        [{"informationId": "I-INTRUDER-PHASE", "subjectRef": "Room order, Intruder types/order, fixed/current target, each public Attack/card/outcome", "audience": "public", "revealTrigger": "continuous/resolution", "secrecy": "unrevealed Attack deck order hidden"}], [], [_target("T-PHASE-TARGET", ["tax.entity.agent.character"], mode="deterministic-turn-order", minimum=0, maximum=1)],
        [
            operation("S01", 1, "change-value", "if-able", "each Intruder in a Room with Fire", "1 Hit", ["SA-RT008-1"], value_change={"amount": 1, "valueTaxonId": "tax.process.operation.hit"}, repeat={"scope": "each matching Intruder", "noDie": True, "cannotKillExceptLarva": True}),
            operation("S02", 2, "remove-component", "if-able", "P-RULES", "1 Egg if Fire is in the Nest", ["SA-RT008-1"]),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-102 order among equal-size Intruders when card draw/effect identity can change later resolution", ["SA-RT008-1"], conditions=["a Room has multiple equal-size Intruders"]),
            _set_operation_class(operation("S04", 4, "invoke-process", "if-able", "each not-yet-attacked Intruder in a Room with a Character", "one complete Intruder Attack", ["SA-RT008-1"], target_ref="T-PHASE-TARGET", invoke="SEM-INT-004", repeat={"roomOrder": "Facility top-left row by row", "intruderOrder": "Queen > Drone > Adult > Larva; equal-size SEM-Q-102", "targetOrder": "first in Turn order until death/leave, then next", "completeAttackBeforeNext": True}), attackClass="intruder-phase", targetSelection="cohort Turn-order rule"),
        ],
        {"policy": "ordered-complete", "unit": "Burning step then one Room/Intruder Attack at a time", "onImpossible": "skip absent targets; Q102 prohibits equal-size ordering invention; generic Attack owns prevention/deck questions"},
        {"kind": "phase"}, {"policy": "once per Round; each eligible Intruder attacks at most once in this step"}, [], ["SEM-Q-102"], [],
    ))

    return {row["ruleId"]: row for row in replacements}


def integrate_combat_shared_records(records: list[dict], record, assertion, timing, participant, condition, decision, operation, attack_rule_ids: list[str]) -> None:
    replacements = _build_replacement_records(record, assertion, timing, participant, condition, decision, operation, attack_rule_ids)
    by_id = {row["ruleId"]: row for row in records}
    missing = sorted(set(replacements) - set(by_id))
    if missing:
        raise AssertionError(f"combat replacement target missing: {missing}")
    for index, row in enumerate(records):
        if row["ruleId"] in replacements:
            records[index] = replacements[row["ruleId"]]

    # Source effects invoke reusable procedures, never paid Basic-Action wrappers.
    procedure_by_action = {
        "SEM-ACT-MOVE-001": ("SEM-MOVEMENT-SEQUENCE-001", "movementClass", "source-effect"),
        "SEM-ACT-SHOOT-001": ("SEM-SHOOT-SEQUENCE-001", "attackClass", "character-shoot"),
        "SEM-ACT-BURST-001": ("SEM-BURST-SEQUENCE-001", "attackClass", "character-burst"),
        "SEM-ACT-MELEE-001": ("SEM-MELEE-SEQUENCE-001", "attackClass", "character-melee"),
    }
    wrapper_ids = set(procedure_by_action)
    for row in records:
        if row["ruleId"] in wrapper_ids:
            continue
        for op in row.get("operations") or []:
            target = procedure_by_action.get(op.get("invokeRuleId"))
            if not target:
                continue
            op["invokeRuleId"] = target[0]
            op[target[1]] = target[2]
            op["invocationClass"] = "source-effect-no-Basic-Action-payment"
            repeat = op.get("repeat")
            if isinstance(repeat, dict):
                repeat.pop("includeBasicActionCardCost", None)

    by_id = {row["ruleId"]: row for row in records}
    duck = by_id["SEM-REACTION-DUCK-001"]
    redirected = next(op for op in duck["operations"] if op["operationType"] == "invoke-process")
    redirected["invokeRuleId"] = "SEM-INT-004"
    redirected["targetRef"] = "T-OTHER-CHARACTER"
    redirected["attackClass"] = "reaction-redirected-preserve-original-class"
    redirected["targetSelection"] = "SEM-Q-001 unresolved when multiple"
    for question_id in ("SEM-Q-001", "SEM-Q-060"):
        if question_id not in duck["unresolvedQuestionRefs"]:
            duck["unresolvedQuestionRefs"].append(question_id)
    duck["status"] = "source-backed-with-open-question"

    bag = by_id["SEM-RT-011"]
    if "SEM-Q-098" not in bag["unresolvedQuestionRefs"]:
        bag["unresolvedQuestionRefs"].append("SEM-Q-098")
    bag["status"] = "source-backed-with-open-question"
    bag["authority"]["interpretation"] = "open-alternatives"
    bag["operations"].insert(0, operation("S00", 0, "resolve-open-alternative", "must", "rules-system", "SEM-Q-098 Bag Development token draw when Intruder bag is empty", ["SA-BAG-DEV"]))
    for index, op in enumerate(bag["operations"], 1):
        op["stepId"] = f"S{index:02d}"
        op["sequence"] = index
    bag["partialResolution"]["onImpossible"] = "finite token/model additions follow exact Help/component rules; SEM-Q-098 prohibits an empty-bag refill, skip, or termination default"

    # Exact caller attack classes and immediate ordering for Help Room rows.
    for occurrence_id in ("QA-R-01", "QA-R-02", "QD-R-01", "QD-R-02"):
        help_record = by_id[f"SEM-IH-{occurrence_id}"]
        for op in help_record["operations"]:
            if op.get("invokeRuleId") == "SEM-SECURE-ENTRY-001":
                op["attackClass"] = "hazard-entry-or-other-entry-from-caller"
                op["entryCause"] = "caller-preserved Room-context token draw"
                op["immediateBeforeTokenLifecycle"] = True

    for occurrence_id in ("QA-C-01", "QA-R-01"):
        help_record = by_id[f"SEM-IH-{occurrence_id}"]
        activate = next(op for op in help_record["operations"] if op["operationType"] == "invoke-process")
        activate["invokeRuleId"] = "SEM-QUEEN-ACTIVATION-001"

    room10 = by_id["SEM-ROOM-10"]
    room10_dispatch = next(op for op in room10["operations"] if op.get("dispatchRuleIds"))
    room10_dispatch["dispatchRuleIds"] = [
        "SEM-IH-QA-R-01", "SEM-IH-QA-R-02", "SEM-IH-QA-BOTTOM-01",
        "SEM-IH-QD-R-01", "SEM-IH-QD-R-02", "SEM-IH-QD-BOTTOM-01",
    ]
    room10_dispatch["notes"] = "Remove the selected marker, draw the token, use its front only, and dispatch by current Queen side plus token front; SEM-Q-098/099 retain empty-bag and side-level Blank scope without inventing pile order."
    room10["unresolvedQuestionRefs"] = list(dict.fromkeys([*room10["unresolvedQuestionRefs"], "SEM-Q-098", "SEM-Q-099"]))
    room10["status"] = "source-backed-with-open-question"
    room10["authority"]["interpretation"] = "open-alternatives"


def build_combat_question_rows() -> list[dict]:
    return [
        {"questionId": "SEM-Q-097", "title": "Order among multiple matching Corridors in one numeric Noise result", "decisionClass": "source-ambiguity-owner-decision-after-source-search", "blocksRuleIds": ["SEM-NOISE-001", "SEM-NOISE-RESULT-001", "SEM-NOISE-NUMERIC-CORRIDOR-001"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 4677–4692", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P25-V01"], "alternatives": [{"alternativeId": "SEM-Q-097-A", "description": "The affected player chooses which matching adjacent Corridor resolves next.", "support": "physical choice is possible, but the source names no owner"}, {"alternativeId": "SEM-Q-097-B", "description": "Apply Facility top-left row order used for Event effects mentioning Noise markers.", "support": "page 14 supplies that order for Event effects, not explicitly for one Character Noise roll"}, {"alternativeId": "SEM-Q-097-C", "description": "Use another source-defined spatial/physical order.", "support": "no checked rule supplies one"}]},
        {"questionId": "SEM-Q-098", "title": "Required Intruder-token draw when the Intruder bag is empty", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-NOISE-001", "SEM-NOISE-MARKER-001", "SEM-NOISE-HAZARD-001", "SEM-ROOM-10", "SEM-RT-011"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 3385–3397,4655–4701,5182–5188", "docs/rules/source-extraction/intruder-help-sheet.json"], "alternatives": [{"alternativeId": "SEM-Q-098-A", "description": "The required draw/effect does nothing and enclosing resolution continues.", "support": "generic component-limit no-op may apply, but the bag draw itself has no explicit shortage rule"}, {"alternativeId": "SEM-Q-098-B", "description": "Return/rebuild tokens from one or more piles before drawing.", "support": "no checked source authorizes this refill"}, {"alternativeId": "SEM-Q-098-C", "description": "Use another source-defined empty-bag termination or partial procedure.", "support": "not stated"}]},
        {"questionId": "SEM-Q-099", "title": "Side-level Blank Help row applicability in Corridor and Room token draws", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-IH-QA-BOTTOM-01", "SEM-IH-QD-BOTTOM-01", "SEM-NOISE-MARKER-001", "SEM-NOISE-HAZARD-001", "SEM-ROOM-10"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rules/source-extraction/intruder-help-sheet.json:queen-alive/queen-dead.bottomRow", HELP_QA_VISION_PATH, HELP_QD_VISION_PATH, "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P15-V01/RB-P25-V02"], "alternatives": [{"alternativeId": "SEM-Q-099-A", "description": "The separate side-level P5 Blank row applies to every Corridor, Room, and Bag Development draw: add Adults and return Blank.", "support": "P5 is outside all three columns, but no printed scope label says all contexts"}, {"alternativeId": "SEM-Q-099-B", "description": "Its add-Adults instruction applies only to Bag Development; Corridor/Room draws only return Blank under the rulebook note.", "support": "the instruction itself changes the bag and page 15 reproduces it as Bag Development"}, {"alternativeId": "SEM-Q-099-C", "description": "Use another source-defined context split while always returning Blank to the bag.", "support": "return is explicit; add-Adults scope is not"}]},
        {"questionId": "SEM-Q-100", "title": "Opportunity cohort and Movement continuation after mover death/escape/participation loss", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-ACT-MOVE-001", "SEM-ACT-MOVE-CAUTIOUSLY-001", "SEM-MOVEMENT-SEQUENCE-001", "SEM-NOISE-NUMERIC-CORRIDOR-001", "SEM-OPPORTUNITY-ATTACK-001"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 4541–4576,3750–3763", "docs/rules/open-questions.md:OQ-004"], "alternatives": [{"alternativeId": "SEM-Q-100-A", "description": "Stop remaining Opportunity Attacks and cancel destination/Noise once the mover no longer participates.", "support": "dead/escaped Characters no longer take part, but no Movement interrupt states this"}, {"alternativeId": "SEM-Q-100-B", "description": "Complete the selected maximum-three Opportunity cohort, then cancel or complete the destination under another source rule.", "support": "Movement step says resolve the cohort before destination"}, {"alternativeId": "SEM-Q-100-C", "description": "Use another per-Attack interruption and Movement continuation procedure.", "support": "not stated"}]},
        {"questionId": "SEM-Q-101", "title": "Standard Intruder Attack draw when the finite Attack deck is empty", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-INT-004"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 5398–5406", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U11", "docs/rules/semantics/attack-source-index.json"], "alternatives": [{"alternativeId": "SEM-Q-101-A", "description": "No card/effect resolves and the Attack ends.", "support": "deck is only reshuffled when instructed; empty draw behavior is not stated"}, {"alternativeId": "SEM-Q-101-B", "description": "Reshuffle the Attack discard despite the explicit only-when-instructed rule.", "support": "would permit a draw but conflicts with the checked rule absent an instruction"}, {"alternativeId": "SEM-Q-101-C", "description": "Use another source-defined empty-deck Attack procedure.", "support": "not stated"}]},
        {"questionId": "SEM-Q-102", "title": "Order among equal-size Intruders in an Intruder Phase Room cohort", "decisionClass": "source-ambiguity-owner-decision-after-source-search", "blocksRuleIds": ["SEM-RT-008"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 3313–3324", "docs/rules/semantics/attack-source-index.json"], "alternatives": [{"alternativeId": "SEM-Q-102-A", "description": "A player chooses which equal-size physical Intruder attacks next.", "support": "physical selection is possible, but no owner is named"}, {"alternativeId": "SEM-Q-102-B", "description": "Use a deterministic miniature/position/order tie-break.", "support": "same Room has no source-defined spatial ordering"}, {"alternativeId": "SEM-Q-102-C", "description": "Treat equal-size order as source-unspecified and resolve through another physical procedure.", "support": "Attack card effects can move an attacker or change later targeting, so order cannot be assumed irrelevant"}]},
        {"questionId": "SEM-Q-103", "title": "Shoot/Melee roll and added-effect continuation after the initial Hit kills a Room Larva", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-ACT-SHOOT-001", "SEM-SHOOT-SEQUENCE-001", "SEM-SHOOT-DIE-RESULT-001", "SEM-ACT-MELEE-001", "SEM-MELEE-SEQUENCE-001", "SEM-MELEE-SHOOT-DIE-RESULT-001", "SEM-INTRUDER-HIT-RESOLUTION-001"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 5576–5605,5628–5675", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U21"], "alternatives": [{"alternativeId": "SEM-Q-103-A", "description": "Remove the Larva after the initial Hit, then still roll and resolve any source-legal Weapon/Action result effects.", "support": "the printed sequence lists the roll after Deal 1 Hit without a stop clause"}, {"alternativeId": "SEM-Q-103-B", "description": "The attack sequence ends when the initial Hit removes its only target; do not roll or resolve target-bound added effects.", "support": "the roll checks whether the target dies, but it is already dead"}, {"alternativeId": "SEM-Q-103-C", "description": "Roll only for a defined subset of non-target effects under another continuation rule.", "support": "no checked source defines the split"}]},
        {"questionId": "SEM-Q-104", "title": "Burst multi-target Hit resolution order, Queen interrupt, and continuation", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-ACT-BURST-001", "SEM-BURST-SEQUENCE-001", "SEM-INTRUDER-HIT-RESOLUTION-001"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 5514–5537,5747–5763", "docs/rules/open-questions.md:SEM-Q-025"], "alternatives": [{"alternativeId": "SEM-Q-104-A", "description": "The allocating player orders each target group; fully resolve each, including Queen Health, before the next.", "support": "allocation is player-owned, but resolution order is not assigned"}, {"alternativeId": "SEM-Q-104-B", "description": "Resolve all non-Queen deaths and Queen track movement simultaneously, then resolve one Queen trigger.", "support": "Apply Hits precedes Resolve Hits, but no simultaneous procedure is printed"}, {"alternativeId": "SEM-Q-104-C", "description": "Use another source-defined type/spatial order and death/interruption continuation.", "support": "not stated; Q025 independently retains Queen trigger timing"}]},
        {"questionId": "SEM-Q-105", "title": "Adult/Drone allocation under mixed token-back counts, Corridor capacity, and finite model supply", "decisionClass": "official-clarification-preferred", "blocksRuleIds": ["SEM-IH-QA-C-02", "SEM-IH-QD-C-02", "SEM-NOISE-MARKER-001"], "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": ["docs/rules/source-extraction/intruder-help-sheet.json:QA-C-02/QD-C-02", HELP_QA_VISION_PATH, HELP_QD_VISION_PATH, "docs/rulebooks/rulebook_text.txt:lines 5189–5198"], "alternatives": [{"alternativeId": "SEM-Q-105-A", "description": "Place the white Adult quantity first, then the red Drone addend until capacity/supply stops placement.", "support": "visual number order/color may suggest this, but no operation order is printed"}, {"alternativeId": "SEM-Q-105-B", "description": "Place the red Drone addend first, then Adults.", "support": "Drones are the distinguished red quantity, but no priority is stated"}, {"alternativeId": "SEM-Q-105-C", "description": "Use another simultaneous/player/random allocation while preserving exact requested counts.", "support": "general model limit says place as many as possible but gives no mixed-type scarcity/capacity tie-break"}]},
    ]


def finalize_combat_question_blocks(records: list[dict], question_rows: list[dict]) -> None:
    by_id = {row["ruleId"]: row for row in records}
    question_by_id = {row["questionId"]: row for row in question_rows}
    for question_id in COMBAT_QUESTION_IDS:
        question = question_by_id[question_id]
        for rule_id in question["blocksRuleIds"]:
            row = by_id.get(rule_id)
            if row is None:
                raise AssertionError(f"combat question target missing: {question_id} -> {rule_id}")
            if question_id not in row["unresolvedQuestionRefs"]:
                row["unresolvedQuestionRefs"].append(question_id)
            row["unresolvedQuestionRefs"] = list(dict.fromkeys(row["unresolvedQuestionRefs"]))
            row["status"] = "source-backed-with-open-question"
            row["authority"]["interpretation"] = "open-alternatives"

    # Existing cross-cutting questions now explicitly cover the reusable core.
    existing_extensions = {
        "SEM-Q-003": ["SEM-MOVEMENT-SEQUENCE-001", "SEM-OPPORTUNITY-ATTACK-001"],
        "SEM-Q-025": ["SEM-SHOOT-SEQUENCE-001", "SEM-BURST-SEQUENCE-001", "SEM-MELEE-SEQUENCE-001", "SEM-SHOOT-DIE-RESULT-001", "SEM-MELEE-SHOOT-DIE-RESULT-001", "SEM-INTRUDER-HIT-RESOLUTION-001"],
        "SEM-Q-029": ["SEM-SHOOT-SEQUENCE-001", "SEM-MELEE-SEQUENCE-001", "SEM-SHOOT-DIE-RESULT-001", "SEM-MELEE-SHOOT-DIE-RESULT-001"],
        "SEM-Q-060": ["SEM-INT-004", "SEM-OPPORTUNITY-ATTACK-001", "SEM-MELEE-SEQUENCE-001", "SEM-SECURE-ENTRY-001"],
        "SEM-Q-088": ["SEM-SHOOT-SEQUENCE-001", "SEM-BURST-SEQUENCE-001", "SEM-SHOOT-DIE-RESULT-001", "SEM-BURST-DIE-RESULT-001"],
        "SEM-Q-089": ["SEM-MELEE-SEQUENCE-001"],
    }
    for question_id, rule_ids in existing_extensions.items():
        question = question_by_id[question_id]
        question["blocksRuleIds"] = list(dict.fromkeys([*question["blocksRuleIds"], *rule_ids]))
        for rule_id in rule_ids:
            row = by_id[rule_id]
            if question_id not in row["unresolvedQuestionRefs"]:
                row["unresolvedQuestionRefs"].append(question_id)
                row["status"] = "source-backed-with-open-question"
                row["authority"]["interpretation"] = "open-alternatives"


def build_combat_conflicts() -> list[dict]:
    return [
        {"conflictId": "SC-081", "title": "Current Retaliation Noise results versus unbound legacy TTS Silence/Danger branches", "status": "resolved-by-authority", "questionId": None, "affectedRuleIds": ["SEM-NOISE-001", "SEM-NOISE-RESULT-001"], "evidenceRefs": ["SRC-RULEBOOK", LUA_PATH, "docs/rules/semantics/combat-source-index.json"], "difference": "Official page 25/page 40 and the exact Retaliation noiseRollDice role use only 1/2/3/4/Hazard. The preserved TTS Lua also contains separate black/orange branches saying Silence unless Slimed, DANGER, and Mars Surface; those branches are not the role-bound Retaliation result set.", "resolution": "Official-primary closed result vocabulary controls. Preserve the stale/unbound runtime branches as secondary provenance only; never add Silence, Danger, Mars Surface, or marker-limit Hazard to current base semantics."},
        {"conflictId": "SC-082", "title": "Intruder Help Blank row is visually side-level but its Corridor/Room applicability is unstated", "status": "unresolved", "questionId": "SEM-Q-099", "affectedRuleIds": ["SEM-IH-QA-BOTTOM-01", "SEM-IH-QD-BOTTOM-01", "SEM-NOISE-MARKER-001", "SEM-NOISE-HAZARD-001"], "evidenceRefs": ["docs/rules/source-extraction/intruder-help-sheet.json", HELP_QA_VISION_PATH, HELP_QD_VISION_PATH, "SRC-RULEBOOK"], "difference": "Each component side places Blank in a separate lower P5 panel outside Corridor/Room/Bag columns. Page 15 explicitly reproduces the add-Adults result for Bag Development; page 25 says Blank always returns to the bag but does not textually assign the add-Adults clause to Corridor/Room draws.", "resolution": "No default. Bag Development add-Adults and universal return-to-bag remain source-clear; Corridor/Room add-Adults applicability remains SEM-Q-099."},
    ]
