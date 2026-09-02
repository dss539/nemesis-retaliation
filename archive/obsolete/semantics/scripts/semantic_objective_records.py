from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from PIL import Image

from semantic_action_records import _raw_root
from semantic_attack_records import _find_guid


RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
OBJECTS_PATH = "assets/tts-mod/extract/v2/objects.json"
LUA_PATH = "assets/tts-mod/extract/v2/lua_script.lua"
ROLES_PATH = "assets/tts-mod/extract/v2/lua_roles.json"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
PROGRESS_PATH = "assets/tts-mod/extract/vision-progress.json"
SELECTED_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"
BACKLOG_PATH = "docs/rules/semantics/backlog.json"
BGA_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
SECONDARY_PATH = "docs/rules/source-extraction/secondary-evidence-index.json"
OBJECTIVE_HELP_PATH = "docs/rulebooks/Nemesis_RT_Objectives_Sheet.pdf"
OBJECTIVE_HELP_EXTRACTION_PATH = "docs/rules/source-extraction/objective-help-sheet.json"
OBJECTIVE_HELP_LAYOUT_PATH = "docs/rules/source-extraction/objective-help-sheet-layout.json"
RULEBOOK_VISUAL_PATH = "docs/rules/source-extraction/rulebook-visual-obligations.json"
FAQ_PATH = "docs/rules/source-extraction/faq-v1.2-source-extraction.json"
ALIASES_PATH = "docs/rules/vocabulary/alias-registry.json"
IDENTITIES_PATH = "docs/rules/vocabulary/named-component-identities.json"

OBJECTIVE_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162.jpg"
OBJECTIVE_SHEET_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880245495/C3E2A6ADEA742B5492FF053F02EF7B24124772CD/"
MISSION_TASK_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160.jpg"
MISSION_TASK_SHEET_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880246035/7A63AECA22A453903BF427431CD1B46E65E49390/"
OBJECTIVE_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-019.png"
OBJECTIVE_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/11923947277683883/7DB96F9DC33FDF984F39FED3282BF126A8A126AE/"
MISSION_TASK_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-018.png"
MISSION_TASK_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/11923947277675696/FDDA1BE010D2F625A6710CDDB32F812CB0828258/"

OBJECTIVE_HELP_SOURCE_ID = "SRC-OBJECTIVE-HELP"
BGA_SOURCE_ID = "SRC-BGA-OBJECTIVES-MISSIONS"
ROOT_SOURCE_IDS = {
    "objectiveMissonDeck": "SRC-OBJECTIVE-MISSION-ROOT",
    "objectivePersonalDeck": "SRC-OBJECTIVE-PRIVATE-ROOT",
    "missionTaskDeck": "SRC-MISSION-TASK-ROOT",
    "objectiveCoopDeck": "SRC-OBJECTIVE-SOLO-COOP-ROOT",
    "objectiveCoopCustomDeck": "SRC-OBJECTIVE-SOLO-COOP-CUSTOM-ROOT",
}

# Exact reviewed root-member tuples. Membership, category, copy identity, and
# generated-cell selectors are never derived from title, body, folder, source
# order, a cell alone, or CardID modulo. The saved sequence remains provenance;
# all three competitive decks are shuffled during setup.
_ROOT_ROWS = [
    # category, role, root, sequence, full CardID, GUID, GMNotes minimum,
    # exact generated cell, disposition, semantic effect kind
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 1, 394402, "60a237", 2, 2, "base-competitive", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 2, 394401, "2e948e", 2, 1, "base-competitive", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 3, 394402, "659a35", 2, 2, "base-competitive", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 4, 394402, "df6765", 2, 2, "base-competitive", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 5, 394402, "6bf621", 2, 2, "base-competitive", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 6, 529900, "37829f", 2, None, "base-competitive", "only-survivor"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 7, 553000, "d711ab", 2, None, "base-competitive", "mission-task-remain-unfulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 8, 394403, "f9ad29", 7, 3, "prototype-high-count-excluded", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 9, 529900, "c600ff", 8, None, "prototype-high-count-excluded", "only-survivor"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 10, 394402, "9ddfc0", 9, 2, "prototype-high-count-excluded", "mission-task-fulfilled"),
    ("mission-objective", "objectiveMissonDeck", "fae6cf", 11, 553000, "263495", 10, None, "prototype-high-count-excluded", "mission-task-remain-unfulfilled"),
    ("private-objective", "objectivePersonalDeck", "263314", 1, 590600, "0df957", 2, None, "base-competitive", "queen-dead"),
    ("private-objective", "objectivePersonalDeck", "263314", 2, 394106, "9bfb37", 2, 6, "base-competitive", "nest-destroyed"),
    ("private-objective", "objectivePersonalDeck", "263314", 3, 529800, "e0580b", 3, None, "base-competitive", "no-character-lander-escape"),
    ("private-objective", "objectivePersonalDeck", "263314", 4, 530000, "e5ecaa", 2, None, "base-competitive", "shutdown-tts"),
    ("private-objective", "objectivePersonalDeck", "263314", 5, 394110, "affe59", 2, 10, "base-competitive", "ranking-tts"),
    ("private-objective", "objectivePersonalDeck", "263314", 6, 394111, "6ff7f8", 4, 11, "base-competitive", "ranking-tts"),
    ("private-objective", "objectivePersonalDeck", "263314", 7, 394112, "8d1916", 2, 12, "base-competitive", "numbered-character-or-only-survivor-1"),
    ("private-objective", "objectivePersonalDeck", "263314", 8, 394113, "6bec70", 2, 13, "base-competitive", "numbered-character-or-only-survivor-2"),
    ("private-objective", "objectivePersonalDeck", "263314", 9, 394114, "8e35e7", 3, 14, "base-competitive", "numbered-character-or-only-survivor-3"),
    ("private-objective", "objectivePersonalDeck", "263314", 10, 394115, "f1afb5", 4, 15, "base-competitive", "numbered-character-or-only-survivor-4"),
    ("private-objective", "objectivePersonalDeck", "263314", 11, 394120, "f4abba", 5, 20, "base-competitive", "numbered-character-or-only-survivor-5"),
    ("private-objective", "objectivePersonalDeck", "263314", 12, 530100, "6fd912", 3, None, "base-competitive", "only-surviving-data-owner"),
    ("private-objective", "objectivePersonalDeck", "263314", 13, 529700, "72e954", 3, None, "base-competitive", "escaped-contamination-aggregate-tts"),
    ("private-objective", "objectivePersonalDeck", "263314", 14, 394117, "f5d0a6", 3, 17, "base-competitive", "only-surviving-data-owner"),
    ("private-objective", "objectivePersonalDeck", "263314", 15, 394119, "79afc8", 2, 19, "base-competitive", "survive-with-egg"),
    ("private-objective", "objectivePersonalDeck", "263314", 16, 447800, "533f2a", 6, None, "prototype-corporate-excluded", "prototype-numbered-character-6"),
    ("private-objective", "objectivePersonalDeck", "263314", 17, 447900, "6ffcf3", 7, None, "prototype-corporate-excluded", "prototype-numbered-character-7"),
    ("private-objective", "objectivePersonalDeck", "263314", 18, 448000, "769b09", 8, None, "prototype-corporate-excluded", "prototype-numbered-character-8"),
    ("private-objective", "objectivePersonalDeck", "263314", 19, 448100, "946f66", 9, None, "prototype-corporate-excluded", "prototype-numbered-character-9"),
    ("private-objective", "objectivePersonalDeck", "263314", 20, 448200, "1ce110", 10, None, "prototype-corporate-excluded", "prototype-numbered-character-10"),
    ("mission-task", "missionTaskDeck", "eabc1d", 1, 557000, "22342f", 3, None, "base-competitive", "eradication-tts"),
    ("mission-task", "missionTaskDeck", "eabc1d", 2, 530400, "ca25da", 2, None, "base-competitive", "primary-samples-tts"),
    ("mission-task", "missionTaskDeck", "eabc1d", 3, 399700, "94ffe0", 2, None, "base-competitive-source-blocked", "facility-restart-blocked"),
    ("mission-task", "missionTaskDeck", "eabc1d", 4, 393801, "abfbde", 1, 1, "base-competitive", "perimeter-clearing-tts"),
    ("mission-task", "missionTaskDeck", "eabc1d", 5, 553400, "ed0104", 2, None, "base-competitive", "escort-mission"),
    ("mission-task", "missionTaskDeck", "eabc1d", 6, 581800, "a9faad", 2, None, "base-competitive", "essential-data"),
    ("mission-task", "missionTaskDeck", "eabc1d", 7, 590700, "c59ec7", 3, None, "base-competitive", "reconnaissance"),
    ("mission-task", "missionTaskDeck", "eabc1d", 8, 585900, "d6eed2", 3, None, "base-competitive", "supply-route"),
]

ROOT_DEFINITIONS = [
    {
        "category": category,
        "role": role,
        "rootGuid": root_guid,
        "rootSequence": sequence,
        "fullCardId": card_id,
        "guid": guid,
        "ttsGmNotesMinimum": minimum,
        "generatedCell": cell,
        "disposition": disposition,
        "effectKind": effect_kind,
    }
    for category, role, root_guid, sequence, card_id, guid, minimum, cell, disposition, effect_kind in _ROOT_ROWS
]

ROOTS = [
    ("objectiveMissonDeck", "fae6cf", "mission-objective"),
    ("objectivePersonalDeck", "263314", "private-objective"),
    ("missionTaskDeck", "eabc1d", "mission-task"),
]
EXCLUDED_ROOTS = [
    ("objectiveCoopDeck", "e22eaa", "official Solo/Coop root excluded from competitive conclusions"),
    ("objectiveCoopCustomDeck", "831e19", "custom/prototype Solo/Coop root excluded from competitive conclusions"),
]

OFFICIAL_EFFECT_KINDS = {
    "P1-MO-OFFICIAL-ORDER-3": "mission-task-fulfilled",
    "P1-MO-ULTERIOR-MOTIVE": "mission-task-remain-unfulfilled",
    "P1-MO-SELF-SERVING": "only-survivor",
    "P1-MT-ESCORT-MISSION": "escort-mission",
    "P1-MT-ESSENTIAL-DATA": "essential-data",
    "P1-MT-THE-SUPPLY-ROUTE": "supply-route",
    "P1-MT-PRIMARY-SAMPLES": "primary-samples-current",
    "P1-MT-RECONNAISSANCE": "reconnaissance",
    "P1-MT-PERIMETER-CLEARING": "perimeter-clearing-current",
    "P1-MT-FACILITY-RESTART": "facility-restart-current",
    "P1-MT-ERADICATION": "eradication-current",
    "P2-PO-CORPORATE-CONTRACT": "numbered-character-or-only-survivor-5",
    "P2-PO-LUXURIOUS-OFFER": "survive-carrying-nest-egg",
    "P2-PO-QUARANTINE": "no-character-lander-escape",
    "P2-PO-STATES-EVIDENCE": "only-surviving-data-owner",
    "P2-PO-SHUTDOWN": "shutdown-current",
    "P2-PO-EXPERIMENTAL-SUBJECTS": "escaped-contamination-aggregate-current",
    "P2-PO-WEVE-GOT-HISTORY": "ranking-current",
    "P2-PO-THE-GREAT-HUNT": "queen-dead",
    "P2-PO-VENI-VIDI-VICI": "nest-destroyed",
}

BGA_EFFECT_KINDS = {
    "Eradication": "eradication-current",
    "EscortMission": "escort-mission",
    "EssentialData": "essential-data",
    "FacilityRestart": "facility-restart-bga",
    "PerimeterClearing": "perimeter-clearing-current",
    "PrimarySamples": "primary-samples-current",
    "Reconnaissance": "reconnaissance",
    "TheSupplyRoute": "supply-route",
    "Objective_OfficialOrder": "mission-task-fulfilled",
    "Objective_SelfServing": "only-survivor",
    "Objective_UlteriorMotive": "mission-task-remain-unfulfilled",
    "Objective_VeniVidiVici": "nest-destroyed",
    "Objective_TheGreatHunt": "queen-dead",
    "Objective_Quarantine": "no-character-lander-escape",
    "Objective_Shutdown": "shutdown-current",
    "Objective_CrewsFavorite": "ranking-current",
    "Objective_WeveGotHistory": "ranking-current",
    "Objective_TheRightMomentToStrike": "numbered-character-or-only-survivor-1",
    "Objective_GreenerPastures": "numbered-character-or-only-survivor-2",
    "Objective_AnOldFeud": "numbered-character-or-only-survivor-3",
    "Objective_HostileTakeover": "numbered-character-or-only-survivor-4",
    "Objective_CorporateContract": "numbered-character-or-only-survivor-5",
    "Objective_ExperimentalSubjects": "escaped-contamination-aggregate-current",
    "Objective_InsiderInformation": "only-surviving-data-owner",
    "Objective_StatesEvidence": "only-surviving-data-owner",
    "Objective_LuxuriousOffer": "survive-carrying-nest-egg",
}

OBJECTIVE_REUSABLE_RULE_IDS = [
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


def _load(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).replace("’", "'").replace("“", '"').replace("”", '"').lower()
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def _code(category: str, card_id: int, guid: str) -> str:
    prefix = {"mission-objective": "MISSION", "private-objective": "PRIVATE", "mission-task": "TASK"}[category]
    return f"{prefix}-{card_id}-{guid.upper()}"


def _physical_rule_id(definition: dict) -> str | None:
    if definition["disposition"] == "base-competitive-source-blocked":
        return None
    if definition["disposition"] != "base-competitive":
        return None
    prefix = "SEM-MISSION-TASK" if definition["category"] == "mission-task" else "SEM-OBJECTIVE"
    return f"{prefix}-{_code(definition['category'], definition['fullCardId'], definition['guid'])}-001"


def _physical_source_id(definition: dict) -> str:
    return f"SRC-OBJECTIVE-{_code(definition['category'], definition['fullCardId'], definition['guid'])}"


def _physical_occurrence_id(definition: dict) -> str:
    return f"TTS-OBJECTIVE-{_code(definition['category'], definition['fullCardId'], definition['guid'])}-FACE"


def _official_rule_id(source_unit_id: str) -> str:
    prefix = "SEM-MISSION-TASK-OFFICIAL" if "-MT-" in source_unit_id else "SEM-OBJECTIVE-OFFICIAL"
    return prefix + "-" + re.sub(r"[^A-Z0-9]+", "-", source_unit_id.upper()).strip("-") + "-001"


def _bga_rule_id(key: str, asset_type: str) -> str:
    prefix = "SEM-MISSION-TASK-BGA" if asset_type == "mission" else "SEM-OBJECTIVE-BGA"
    return prefix + "-" + re.sub(r"[^A-Z0-9]+", "-", key.upper()).strip("-") + "-001"


def _source_asset_id(sheet: str, cell: int) -> str:
    return f"SRC-OBJECTIVE-ASSET-{sheet}-CELL-{cell:02d}"


def _generated_path(sheet: str, cell: int) -> str:
    if sheet == "3944":
        return f"assets/tts-mod/extract/v2-dl/tree/cards/game/objectiveMissonDeck-162_cards/card-{cell:02d}.png"
    if sheet == "3938":
        return f"assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-{cell:02d}.png"
    raise AssertionError(f"unknown Objective generated sheet {sheet}")


def _parse_bga_table(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    marker = "const MISSIONS_OBJECTIVES_DATA = {"
    start = text.find(marker)
    end = text.find("\n};\nconst ROBOT_CARDS_DATA", start)
    if start < 0 or end < 0:
        raise AssertionError("MISSIONS_OBJECTIVES_DATA block not found")
    body = text[start + len(marker):end]
    rows = []
    offset = 0
    while offset < len(body):
        while offset < len(body) and body[offset] in " \t\r\n,":
            offset += 1
        if offset >= len(body):
            break
        key_match = re.match(r"([A-Za-z0-9_]+):\s*", body[offset:])
        if not key_match:
            raise AssertionError(f"unparsed BGA objective table at offset {offset}")
        key = key_match.group(1)
        object_start = offset + key_match.end()
        if body[object_start] != "{":
            raise AssertionError(f"BGA objective {key} is not an object")
        depth = 0
        quote_char = None
        escaped = False
        object_end = None
        for index in range(object_start, len(body)):
            char = body[index]
            if quote_char:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == quote_char:
                    quote_char = None
                continue
            if char in {"'", '"'}:
                quote_char = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    object_end = index + 1
                    break
        if object_end is None:
            raise AssertionError(f"unterminated BGA objective {key}")
        source_block = body[offset:object_end]
        object_body = body[object_start + 1:object_end - 1]

        def string_field(field: str) -> str | None:
            match = re.search(rf"\b{field}:\s*(('(?:\\.|[^'])*')|(\"(?:\\.|[^\"])*\"))", object_body)
            return ast.literal_eval(match.group(1)) if match else None

        def bool_field(field: str) -> bool | None:
            match = re.search(rf"\b{field}:\s*(true|false)", object_body)
            return match.group(1) == "true" if match else None

        def array_field(field: str) -> list:
            match = re.search(rf"\b{field}:\s*", object_body)
            if not match:
                return []
            array_start = match.end()
            if object_body[array_start] != "[":
                raise AssertionError(f"BGA objective {key}.{field} is not an array")
            level = 0
            array_quote = None
            escaped_local = False
            for index in range(array_start, len(object_body)):
                char = object_body[index]
                if array_quote:
                    if escaped_local:
                        escaped_local = False
                    elif char == "\\":
                        escaped_local = True
                    elif char == array_quote:
                        array_quote = None
                    continue
                if char in {"'", '"'}:
                    array_quote = char
                elif char == "[":
                    level += 1
                elif char == "]":
                    level -= 1
                    if level == 0:
                        return ast.literal_eval(object_body[array_start:index + 1])
            raise AssertionError(f"unterminated BGA objective {key}.{field}")

        asset_type = string_field("assetType")
        desc = array_field("desc")
        effect = array_field("effectDesc")
        alternate = array_field("orEffectDesc")
        condition_lines = desc if desc else [*effect, *(["{{OR}}", *alternate] if alternate else [])]
        rows.append({
            "key": key,
            "name": string_field("name"),
            "assetType": asset_type,
            "soloCoop": bool_field("soloCoop"),
            "desc": desc,
            "effectDesc": effect,
            "orEffectDesc": alternate,
            "conditionLines": condition_lines,
            "printedCondition": "\n".join(condition_lines),
            "sourceBlockText": source_block,
        })
        offset = object_end
    return rows


def _visible(corpus_row: dict) -> tuple[dict, dict]:
    selected = corpus_row.get("selectedExtraction") or {}
    visible = selected.get("visibleText") or {}
    printed = corpus_row.get("printedData") or {}
    return selected, visible if visible else printed


def _section_text(section) -> str:
    if isinstance(section, dict):
        heading = section.get("heading") or ""
        text = section.get("text") or ""
        return "\n".join(part for part in (heading, text) if part)
    return str(section)


def _extract_choice_instruction(visible: dict) -> str | None:
    for section in visible.get("sections") or []:
        text = _section_text(section)
        if text.startswith("Remove the other Objective from the game to:"):
            return text
    body = visible.get("body") or ""
    if body.startswith("Remove the other Objective from the game to:"):
        pieces = re.split(r"\n\n+", body, maxsplit=1)
        return pieces[0]
    return None


def _visible_threshold(selected: dict, visible: dict) -> str | None:
    candidates = [str(visible.get("upperRight") or "")]
    candidates.extend(_section_text(section) for section in visible.get("sections") or [])
    candidates.extend(str(row.get("cardLocation") or "") for row in selected.get("unresolvedIconOccurrences") or [])
    for candidate in candidates:
        match = re.search(r"(?<![A-Za-z0-9])(\d+\+|ALL)(?![A-Za-z0-9])", candidate, re.I)
        if match:
            return match.group(1).upper()
    return None


def _source_icons(selected: dict, visible: dict) -> list[dict]:
    rows = []
    for icon in selected.get("verifiedIconOccurrences") or []:
        token = icon.get("canonicalToken")
        rows.append({
            "iconId": f"I{len(rows)+1:02d}",
            "location": icon.get("cardLocation") or "selected evidence location",
            "literalAppearance": icon.get("referenceLabel") or token,
            "matchDecision": icon.get("matchDecision"),
            "semanticReferenceId": f"icon.{token}" if token else None,
            "evidence": "selected-card-text-evidence",
        })
    for icon in selected.get("unresolvedIconOccurrences") or []:
        rows.append({
            "iconId": f"I{len(rows)+1:02d}",
            "location": icon.get("cardLocation") or "selected evidence location",
            "literalAppearance": icon.get("referenceLabel") or "unresolved local glyph",
            "matchDecision": icon.get("matchDecision") or "no-match",
            "semanticReferenceId": None,
            "evidence": "selected-card-text-evidence",
        })
    if not selected:
        combined = "\n".join(str(value or "") for value in (visible.get("body"), visible.get("upperRight")))
        for match in re.finditer(r"\[([^\]]+)\]", combined):
            literal = match.group(1)
            semantic = "icon." + literal if re.fullmatch(r"[A-Za-z][A-Za-z0-9]+", literal) else None
            rows.append({
                "iconId": f"I{len(rows)+1:02d}",
                "location": f"visibleText:{match.start()}-{match.end()}",
                "literalAppearance": "[" + literal + "]",
                "matchDecision": "canonical-corpus" if semantic else "literal-no-match",
                "semanticReferenceId": semantic,
                "evidence": "card-text-corpus",
            })
    return rows


def _panels(title: str, condition_text: str, footer: str, choice_instruction: str | None, threshold: str | None) -> list[dict]:
    rows = []

    def add(role: str, text: str, *, heading=None, operative=False) -> None:
        rows.append({
            "panelId": f"P{len(rows)+1:02d}",
            "readingOrder": len(rows)+1,
            "role": role,
            "heading": heading,
            "operative": operative,
            "exactText": text,
        })

    if choice_instruction:
        add("objective-choice-instruction", choice_instruction, operative=True)
    if threshold:
        add("number-of-characters-metadata", threshold, operative=True)
    add("title", title, operative=False)
    parts = re.split(r"\n\s*(AND|OR)\s*\n", condition_text)
    for part in parts:
        value = part.strip()
        if not value:
            continue
        if value in {"AND", "OR"}:
            add("condition-connector", value, heading=value, operative=True)
        else:
            add("condition", value, operative=True)
    add("footer", footer, operative=False)
    return rows


def _sentences(condition_text: str, panels: list[dict]) -> list[dict]:
    condition_panels = [row for row in panels if row["role"] == "condition"]
    rows = []
    for panel in condition_panels:
        text = panel["exactText"]
        parts = [part.strip() for part in re.split(r"(?<=[.!?])(?:\s+|\n+)", text) if part.strip()]
        if not parts and text:
            parts = [text]
        for part in parts:
            rows.append({"sentenceId": f"S{len(rows)+1:02d}", "sequence": len(rows)+1, "panelId": panel["panelId"], "exactText": part})
    return rows


def _atom(condition_id: str, predicate: str, *, timing="endgame-objective-check", subject="rules-system", target=None, historical=False) -> dict:
    return {
        "conditionId": condition_id,
        "operator": "predicate",
        "predicate": predicate,
        "evaluationWindow": timing,
        "subject": subject,
        "target": target,
        "historicalState": historical,
    }


def _condition_tree(effect_kind: str) -> dict | None:
    if effect_kind == "facility-restart-blocked" or effect_kind.startswith("prototype-numbered-character"):
        return None
    numbered = re.fullmatch(r"numbered-character-or-only-survivor-(\d+)", effect_kind)
    if numbered:
        number = int(numbered.group(1))
        return {
            "operator": "any",
            "branchTimingQuestionId": "SEM-Q-075",
            "clauses": [
                {"operator": "all", "branchId": "B01", "clauses": [
                    _atom("C01", f"Character controlled by Player/Help-card number {number} is not a Survivor", target=f"Character number {number}"),
                    _atom("C02", f"branch B01 is unavailable when the Objective owner is Player/Help-card number {number}", subject="Objective owner"),
                ]},
                {"operator": "all", "branchId": "B02", "clauses": [_atom("C03", "Objective owner's Character is the only Survivor", subject="Objective owner Character")]},
            ],
        }
    if effect_kind in {"ranking-current", "ranking-tts"}:
        first_predicate = "Objective owner and lowest-ranking Character are Survivors" if effect_kind == "ranking-tts" else "lowest-ranking Character is a Survivor"
        return {
            "operator": "any",
            "branchTimingQuestionId": "SEM-Q-075",
            "clauses": [
                {"operator": "all", "branchId": "B01", "clauses": [
                    _atom("C01", first_predicate),
                    _atom("C02", "branch B01 is unavailable when the Objective owner is the lowest-ranking Character", subject="Objective owner"),
                ]},
                {"operator": "all", "branchId": "B02", "clauses": [
                    _atom("C03", "highest-ranking Character is not a Survivor"),
                    _atom("C04", "branch B02 is unavailable when the Objective owner is the highest-ranking Character", subject="Objective owner"),
                ]},
            ],
        }
    specs = {
        "mission-task-fulfilled": ("all", [_atom("C01", "the one public selected Mission Task is Fulfilled")]),
        "mission-task-remain-unfulfilled": ("all", [_atom("C01", "the one public selected Mission Task remains UNFULFILLED", timing="continuous-or-endgame-unresolved")]),
        "only-survivor": ("all", [_atom("C01", "Objective owner's Character is the only Survivor", subject="Objective owner Character")]),
        "queen-dead": ("all", [_atom("C01", "Queen is dead")]),
        "nest-destroyed": ("all", [_atom("C01", "Nest is Destroyed")]),
        "no-character-lander-escape": ("all", [_atom("C01", "no Character, including the Objective owner, Escaped from the Facility using the Lander")]),
        "shutdown-current": ("all", [_atom("C01", "all Life Support tokens are inactive or removed from the game"), _atom("C02", "Objective owner has a Data token from the Server Room in Section B", subject="Objective owner Character")]),
        "shutdown-tts": ("all", [_atom("C01", "Objective owner has a Data token from the Server Room in Section B", subject="Objective owner Character"), _atom("C02", "all Life Support tokens are inactive or removed from the game")]),
        "only-surviving-data-owner": ("all", [_atom("C01", "Objective owner is a Survivor", subject="Objective owner Character"), _atom("C02", "Objective owner has a Data token from the Server Room in Section B", subject="Objective owner Character"), _atom("C03", "no other Survivor has a Data token from the Server Room in Section B")]),
        "escaped-contamination-aggregate-current": ("all", [_atom("C01", "all Characters who Escaped have at least 3 Contaminations in total among their complete decks, regardless of death during final Eclosion", target="Escaped Character cohort")]),
        "escaped-contamination-aggregate-tts": ("all", [_atom("C01", "all Characters who Escaped have at least 3 Contamination cards in total among them, no matter if they Survive", target="Escaped Character cohort")]),
        "survive-with-egg": ("all", [_atom("C01", "Objective owner is a Survivor while carrying an Egg", subject="Objective owner Character")]),
        "survive-carrying-nest-egg": ("all", [_atom("C01", "Objective owner is a Survivor carrying an Egg from the Nest in Section C", subject="Objective owner Character")]),
        "escort-mission": ("all", [_atom("C01", "Robot reached the Reactor in Section C at least once during the game and the public checkbox was marked", timing="when-Robot-first-reaches-Reactor", target="Robot", historical=True), _atom("C02", "at least 1 Character with a Data token from the Server Room in Section B Escaped from the Facility", target="Escaped Character cohort")]),
        "essential-data": ("all", [_atom("C01", "at least 1 Character with a Data token from the Server Room in Section B Escaped using the Lander in Section A", target="Escaped Character cohort"), _atom("C02", "there are no Unexplored Corridors in Section A, including the A/B border; each existing one is connected with two Rooms")]),
        "supply-route": ("all", [_atom("C01", "a continuous path of Reinforced Corridors connects the Landing Zone in Section A to Life Support Control C, ignoring Closed Doors and Intruders"), _atom("C02", "Facility is not Destroyed")]),
        "primary-samples-current": ("all", [_atom("C01", "Characters who Escaped carried at least 2 Eggs in total among them at Escape, regardless of whether they Survive after Escaping", target="Escaped Character cohort", historical=True)]),
        "primary-samples-tts": ("all", [_atom("C01", "at least 2 Eggs were taken out of the Facility using the Lander or Escape Shuttle", target="escaped cargo", historical=True)]),
        "reconnaissance": ("all", [_atom("C01", "Undiscovered Room pools for types A, B, and C are empty"), _atom("C02", "Hibernatorium is connected by a Corridor to at least 1 Room")]),
        "perimeter-clearing-current": ("all", [_atom("C01", "Reactor in Section C is shut down by using the Room"), _atom("C02", "all 3 A-type Rooms are Discovered")]),
        "perimeter-clearing-tts": ("all", [_atom("C01", "Reactor is shut down"), _atom("C02", "all Section A Rooms are Explored")]),
        "facility-restart-current": ("all", [_atom("C01", "Hibernatorium is active by using Life Support Control C"), _atom("C02", "Reactor in Section C is shut down by using the Room; Autodestruction token has been removed from the game")]),
        "facility-restart-bga": ("all", [_atom("C01", "Hibernatorium is active by using Life Support C"), _atom("C02", "Reactor in Section C is shut down by using the Room")]),
        "eradication-current": ("all", [_atom("C01", "Queen is dead"), _atom("C02", "Facility is not Destroyed")]),
        "eradication-tts": ("all", [_atom("C01", "Queen was killed"), _atom("C02", "Facility cannot be Destroyed")]),
    }
    if effect_kind not in specs:
        raise AssertionError(f"unmapped Objective semantic effect kind {effect_kind}")
    operator, clauses = specs[effect_kind]
    tree = {"operator": operator, "clauses": clauses}
    if effect_kind == "mission-task-remain-unfulfilled":
        tree["continuousTimingQuestionId"] = "SEM-Q-076"
    return tree


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


def _effect_questions(effect_kind: str) -> list[str]:
    rows = []
    if effect_kind == "mission-task-remain-unfulfilled":
        rows.append("SEM-Q-076")
    if effect_kind in {"ranking-current", "ranking-tts"} or effect_kind.startswith("numbered-character-or-only-survivor-"):
        rows.append("SEM-Q-075")
    return rows


def _term_taxa(effect_kind: str, category: str) -> tuple[list[str], list[str]]:
    terms = ["term.mission-task" if category == "mission-task" else "term.objective"]
    taxa = ["tax.entity.information.mission-task" if category == "mission-task" else "tax.entity.information.objective"]
    if category == "mission-objective":
        terms.append("term.mission-objective")
        taxa.append("tax.entity.information.objective.mission")
    elif category == "private-objective":
        terms.append("term.private-objective")
        taxa.append("tax.entity.information.objective.private")
    if "survivor" in effect_kind or effect_kind.startswith("ranking") or effect_kind.startswith("numbered-character"):
        terms.append("term.survivor")
        taxa.append("tax.state.participation.survivor")
    if "escape" in effect_kind or effect_kind in {"primary-samples-current", "primary-samples-tts", "escaped-contamination-aggregate-current", "escaped-contamination-aggregate-tts", "escort-mission", "essential-data"}:
        terms.append("term.escape")
        taxa.append("tax.state.participation.escaped")
    if "data" in effect_kind or effect_kind in {"shutdown-current", "shutdown-tts", "escort-mission"}:
        terms.append("term.data-token")
        taxa.append("tax.entity.component.token.data")
    if "egg" in effect_kind or effect_kind.startswith("primary-samples"):
        terms.append("term.egg-token")
        taxa.append("tax.entity.component.token.egg")
    if "queen" in effect_kind or effect_kind.startswith("eradication"):
        terms.append("term.queen")
        taxa.append("tax.entity.agent.intruder.queen")
    if "nest" in effect_kind:
        terms.append("term.nest")
        taxa.append("tax.entity.spatial.room.nest")
    if category != "mission-task":
        terms.extend(["term.objective-card", "term.fulfilled"])
        taxa.extend(["tax.entity.component.card.objective", "tax.state.objective.fulfilled"])
    else:
        terms.extend(["term.mission-task-card", "term.fulfilled"])
        taxa.extend(["tax.entity.component.card.mission-task", "tax.state.objective.fulfilled"])
    return sorted(set(terms)), sorted(set(taxa))


def _source_asset_anatomy(corpus_row: dict, effect_kind: str | None) -> dict:
    selected, visible = _visible(corpus_row)
    title = str(visible.get("title") or "")
    body = str(visible.get("body") or "")
    footer = str(visible.get("footer") or visible.get("lowerCenter") or "")
    choice = _extract_choice_instruction(visible)
    threshold = _visible_threshold(selected, visible)
    panels = _panels(title, body, footer, choice, threshold)
    icons = _source_icons(selected, visible)
    tree = _condition_tree(effect_kind) if effect_kind else None
    return {
        "printedTitle": title,
        "printedCondition": body,
        "printedFooter": footer,
        "printedTypeLine": str(visible.get("typeLine") or ""),
        "objectiveChoiceInstruction": choice,
        "visiblePrintedPlayerCount": threshold,
        "sourceSections": visible.get("sections") or [],
        "panels": panels,
        "sentences": _sentences(body, panels),
        "iconOccurrences": icons,
        "checkboxPanels": [panel["panelId"] for panel in panels if "mark the box" in panel["exactText"].lower()] or ([next((row["panelId"] for row in panels if row["role"] == "condition"), "P00")] if any("mark the box" in (row.get("location") or "").lower() or "empty rounded square" in (row.get("literalAppearance") or "").lower() for row in icons) else []),
        "conditionTree": tree,
        "conditionConnectorCounts": {"AND": sum(panel.get("heading") == "AND" for panel in panels), "OR": sum(panel.get("heading") == "OR" for panel in panels)},
        "selectedEvidenceUsed": bool(selected),
        "selectedEvidenceRunIdentity": selected.get("runIdentity"),
        "selectedVisibleText": visible if selected else None,
        "sourcePrintedData": corpus_row.get("printedData") or {},
        "representationBoundary": {
            "selectedPixelEvidenceControls": bool(selected),
            "conflictsWithPriorSnapshot": selected.get("conflictsWithPriorSnapshot") or [],
            "policy": "Selected source-bound visible text and icon comparisons control this literal TTS occurrence. Prior corpus text, official Help text, and licensed data remain independent and never fill, rewrite, or identify this face by title/body similarity.",
        },
    }


def _official_icons(unit: dict) -> list[dict]:
    rows = []
    for source in unit.get("functionalIconOccurrences") or []:
        location = source.get("location") or ""
        semantic = None
        if "top instruction" in location and "after “draw”" in location:
            semantic = "icon.actionCard"
        elif "above the title" in location and "printed" in location:
            semantic = "icon.numberOfCharacters"
        elif "ESCORT-MISSION-I03" in source.get("occurrenceId", ""):
            semantic = "icon.robot"
        elif "using the" in location:
            semantic = "icon.lander"
        elif "after “The”" in location or "after “All”" in location or "after “No”" in location or "after the printed 1" in location or "ranking" in location:
            semantic = "icon.character"
        elif "must be" in location and "SHUTDOWN" in unit.get("sourceUnitId", ""):
            semantic = "icon.lifeSupportInactive"
        elif "must be" in location and "FACILITY-RESTART" in unit.get("sourceUnitId", ""):
            semantic = "icon.hibernatoriumActive"
        rows.append({
            "iconId": source.get("occurrenceId"),
            "location": location,
            "literalAppearance": source.get("literalAppearance"),
            "matchDecision": "official-source-scoped-semantic-projection" if semantic else "literal-source-local",
            "semanticReferenceId": semantic,
            "evidence": "objective-help-sheet visible pixels",
        })
    for source in unit.get("directlyVisibleIconOccurrences") or []:
        rows.append({"iconId": source.get("occurrenceId"), "location": source.get("location"), "literalAppearance": source.get("literalAppearance"), "matchDecision": "literal-partial-visible", "semanticReferenceId": None, "evidence": "objective-help-sheet visible pixels"})
    for source in unit.get("partiallyVisibleIconOccurrences") or []:
        rows.append({"iconId": source.get("occurrenceId"), "location": source.get("location"), "literalAppearance": source.get("literalAppearance"), "matchDecision": "partially-visible-no-semantic-promotion", "semanticReferenceId": None, "evidence": "objective-help-sheet visible pixels"})
    return rows


def _official_occurrence(unit: dict) -> dict:
    source_unit_id = unit["sourceUnitId"]
    visible = unit.get("visibility") != "partially-occluded"
    effect_kind = OFFICIAL_EFFECT_KINDS.get(source_unit_id)
    title = unit.get("printedTitle")
    condition_text = unit.get("printedCondition")
    footer = unit.get("printedFooter")
    threshold = (unit.get("countThreshold") or {}).get("printedText")
    choice = unit.get("topInstruction")
    panels = _panels(title or "", condition_text or "", footer or "", choice, threshold) if visible and (title or condition_text) else []
    semantic_rule_id = _official_rule_id(source_unit_id) if effect_kind else None
    if source_unit_id.startswith("P1-GT-") or source_unit_id.startswith("P2-GT-"):
        heading = unit.get("heading")
        semantic_rule_id = {
            "FULFILLED": "SEM-OBJECTIVE-FULFILLMENT-001",
            "SURVIVOR": "SEM-OBJECTIVE-SURVIVOR-001",
            "ESCAPE": "SEM-OBJECTIVE-ESCAPE-001",
            "DATA TOKEN": "SEM-DATA-TOKEN-001",
            "FACILITY DESTRUCTION": "SEM-FACILITY-DESTRUCTION-001",
            "QUEEN IS DEAD": "SEM-QUEEN-DEATH-001",
            "NEST IS DESTROYED": "SEM-NEST-DESTROYED-001",
        }[heading]
    if source_unit_id == "P2-NOTE-RANKING-CHOICE":
        semantic_rule_id = "SEM-OBJECTIVE-FULFILLMENT-001"
    return {
        "sourceUnitId": source_unit_id,
        "category": unit.get("category"),
        "visibility": "partially-occluded" if unit.get("visibility") == "partially-occluded" else "fully-visible",
        "printedTitle": title,
        "printedCondition": condition_text,
        "printedDefinition": unit.get("printedDefinition"),
        "printedText": unit.get("printedText"),
        "printedFooter": footer,
        "objectiveChoiceInstruction": choice,
        "playerCountMetadata": {"visiblePrintedThreshold": threshold, "semanticMinimumPlayers": int(threshold[:-1]) if isinstance(threshold, str) and threshold.endswith("+") else None},
        "panels": panels,
        "sentences": _sentences(condition_text or "", panels) if panels else [],
        "iconOccurrences": _official_icons(unit),
        "checkboxPanels": [panel["panelId"] for panel in panels if "mark the box" in panel["exactText"].lower()],
        "conditionConnectorCounts": {"AND": sum(panel.get("heading") == "AND" for panel in panels), "OR": sum(panel.get("heading") == "OR" for panel in panels)},
        "conditionTree": _condition_tree(effect_kind) if effect_kind else None,
        "effectKind": effect_kind,
        "semanticRuleId": semantic_rule_id,
        "boundaryRuleId": "SEM-OBJECTIVE-VARIANT-BOUNDARIES-001" if unit.get("visibility") == "partially-occluded" else None,
        "associatedNotes": unit.get("associatedNotes") or [],
        "sharedExplanatoryNoteSourceUnitId": unit.get("sharedExplanatoryNoteSourceUnitId"),
        "directlyVisibleTextFragments": unit.get("directlyVisibleTextFragments") or [],
        "materialOccludedSpans": unit.get("materialOccludedSpans") or [],
        "occludedTextLayerMetadata": unit.get("pdfTextLayerMetadata"),
        "visualEvidence": unit.get("visualEvidence"),
        "occludedMetadataPromotedToVisibleEvidence": False,
        "backlogUnitId": "OBJ:" + source_unit_id,
    }


def build_objective_source_index(repo: Path) -> dict:
    corpus = _load(repo / CORPUS_PATH)
    progress = _load(repo / PROGRESS_PATH)
    provenance = _load(repo / PROVENANCE_PATH)
    backlog = _load(repo / BACKLOG_PATH)
    objective_help = _load(repo / OBJECTIVE_HELP_EXTRACTION_PATH)
    objective_layout = _load(repo / OBJECTIVE_HELP_LAYOUT_PATH)
    roles = _load(repo / ROLES_PATH)
    aliases = _load(repo / ALIASES_PATH)
    identities = _load(repo / IDENTITIES_PATH)
    secondary = _load(repo / SECONDARY_PATH)
    faq = _load(repo / FAQ_PATH)
    rulebook_visual = _load(repo / RULEBOOK_VISUAL_PATH)
    if not all(isinstance(value, (dict, list)) for value in (corpus, progress, provenance, backlog, objective_help, objective_layout, roles, aliases, identities, secondary, faq, rulebook_visual)):
        raise AssertionError("Objective evidence container shape changed")
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    provenance_by_url = {row["url"]: row for row in provenance}
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    raw, raw_sha = _raw_root(repo)

    role_by_name = {row["role"]: row for row in roles}
    root_evidence = []
    raw_children_by_root = {}
    raw_roots_by_guid = {}
    for role, root_guid, category in ROOTS:
        role_row = role_by_name.get(role) or {}
        if role_row.get("guid") != root_guid:
            raise AssertionError(f"Objective Lua role drift: {role}")
        root = _find_guid(raw.get("ObjectStates"), root_guid)
        if not isinstance(root, dict):
            raise AssertionError(f"Objective raw root missing: {root_guid}")
        contained_value = root.get("ContainedObjects") or {}
        contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
        definitions = [row for row in ROOT_DEFINITIONS if row["rootGuid"] == root_guid]
        expected = [(row["fullCardId"], row["guid"]) for row in definitions]
        actual = [(int(row["CardID"]), row["GUID"]) for row in contained]
        deck_ids = [int(value) for value in (root.get("DeckIDs") or {}).values()]
        if actual != expected or deck_ids != [row[0] for row in expected]:
            raise AssertionError(f"Objective raw root member/order drift: {root_guid}")
        raw_children_by_root[root_guid] = contained
        raw_roots_by_guid[root_guid] = root
        root_evidence.append({
            "sourceId": ROOT_SOURCE_IDS[role],
            "role": role,
            "category": category,
            "rootGuid": root_guid,
            "rootType": root.get("Name"),
            "gmNotes": root.get("GMNotes"),
            "savedDeckIds": deck_ids,
            "rootCustomDeckIds": list(root.get("CustomDeck") or {}),
            "fullContainedSelectors": [
                {"rootSequence": row["rootSequence"], "fullCardId": row["fullCardId"], "guid": row["guid"], "disposition": row["disposition"], "ttsGmNotesMinimum": row["ttsGmNotesMinimum"], "generatedCell": row["generatedCell"]}
                for row in definitions
            ],
            "savedOrderIsGameplayOrder": False,
            "setupShuffleRequired": True,
        })

    excluded_roots = []
    for role, root_guid, boundary in EXCLUDED_ROOTS:
        role_row = role_by_name.get(role) or {}
        root = _find_guid(raw.get("ObjectStates"), root_guid)
        if role_row.get("guid") != root_guid or not isinstance(root, dict):
            raise AssertionError(f"Objective excluded root drift: {role}")
        contained_value = root.get("ContainedObjects") or {}
        contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
        excluded_roots.append({
            "sourceId": ROOT_SOURCE_IDS[role],
            "role": role,
            "rootGuid": root_guid,
            "rootType": root.get("Name"),
            "physicalOccurrences": len(contained),
            "savedDeckIds": [int(value) for value in (root.get("DeckIDs") or {}).values()],
            "fullContainedSelectors": [
                {
                    "rootSequence": index,
                    "fullCardId": int(child["CardID"]),
                    "guid": child["GUID"],
                    "childCustomDeckIds": list(child.get("CustomDeck") or {}),
                    "faceUrl": next(iter((child.get("CustomDeck") or {}).values())).get("FaceURL"),
                    "backUrl": next(iter((child.get("CustomDeck") or {}).values())).get("BackURL"),
                }
                for index, child in enumerate(contained, 1)
            ],
            "boundary": boundary,
            "includedInCompetitiveConclusions": False,
        })

    source_assets = []
    base_generated_cells = {
        "3944": {row["generatedCell"] for row in ROOT_DEFINITIONS if row["disposition"].startswith("base-competitive") and row["generatedCell"] is not None and row["rootGuid"] in {"fae6cf", "263314"}},
        "3938": {row["generatedCell"] for row in ROOT_DEFINITIONS if row["disposition"].startswith("base-competitive") and row["generatedCell"] is not None and row["rootGuid"] == "eabc1d"},
    }
    prototype_generated_cells = {
        "3944": {row["generatedCell"] for row in ROOT_DEFINITIONS if "prototype" in row["disposition"] and row["generatedCell"] is not None},
        "3938": {3, 5},
    }
    for sheet, cell_count, sheet_path, grid in (
        ("3944", 21, OBJECTIVE_SHEET_PATH, {"columns": 7, "rows": 3, "cellWidth": 827, "cellHeight": 1111}),
        ("3938", 10, MISSION_TASK_SHEET_PATH, {"columns": 5, "rows": 2, "cellWidth": 1136, "cellHeight": 1525}),
    ):
        for cell in range(cell_count):
            source_path = _generated_path(sheet, cell)
            corpus_row = corpus_by_path.get(source_path)
            progress_row = progress_by_path.get(source_path)
            if not corpus_row or not corpus_row.get("rulesTextPresent") or (progress_row or {}).get("generatedFrom") != {"sourceSheetPath": sheet_path, "cellIndex": cell}:
                raise AssertionError(f"Objective generated asset evidence drift: {source_path}")
            definitions = [row for row in ROOT_DEFINITIONS if row["generatedCell"] == cell and ((sheet == "3944" and row["rootGuid"] in {"fae6cf", "263314"}) or (sheet == "3938" and row["rootGuid"] == "eabc1d"))]
            base_definitions = [row for row in definitions if row["disposition"].startswith("base-competitive")]
            effect_kind = base_definitions[0]["effectKind"] if base_definitions else (definitions[0]["effectKind"] if definitions else None)
            anatomy = _source_asset_anatomy(corpus_row, effect_kind if effect_kind != "facility-restart-blocked" else None)
            source_assets.append({
                "assetId": f"OBJECTIVE-ASSET-{len(source_assets)+1:03d}",
                "sourceId": _source_asset_id(sheet, cell),
                "sourcePath": source_path,
                "sourceSha256": corpus_row["sourceSha256"],
                "sourceRole": "generated-cell-selected-base-face" if cell in base_generated_cells[sheet] else ("generated-cell-prototype-root-exclusion" if cell in prototype_generated_cells[sheet] else "generated-cell-base-selector-gap-variant"),
                "sourceSheetId": "SRC-OBJECTIVE-PARENT-SHEET" if sheet == "3944" else "SRC-MISSION-TASK-PARENT-SHEET",
                "sourceSheetPath": sheet_path,
                "sourceSheetSha256": _sha(repo / sheet_path),
                "sourceSheetGrid": grid,
                "customDeckId": sheet,
                "generatedCell": cell,
                "selectedBasePhysicalOccurrenceIds": [_physical_occurrence_id(row) for row in base_definitions],
                "selectedPrototypePhysicalOccurrenceIds": [_physical_occurrence_id(row) for row in definitions if "prototype" in row["disposition"]],
                "baseSelectorGap": None if base_definitions else {"status": "explicit-no-base-competitive-root-full-CardID-GUID-selector", "cardIdModuloJoinUsed": False},
                "backlogUnitId": "CARD:" + corpus_row["sourceSha256"][:16],
                "corpusExtractionState": corpus_row.get("extractionState"),
                "effectKind": effect_kind,
                **anatomy,
            })

    direct_definitions_by_url = {}
    for definition in ROOT_DEFINITIONS:
        if definition["generatedCell"] is not None:
            continue
        child = raw_children_by_root[definition["rootGuid"]][definition["rootSequence"] - 1]
        custom = child.get("CustomDeck") or {}
        if len(custom) != 1:
            raise AssertionError(f"Objective direct child selector count drift: {definition['guid']}")
        face_url = next(iter(custom.values())).get("FaceURL")
        direct_definitions_by_url.setdefault(face_url, []).append(definition)
    for face_url, definitions in sorted(direct_definitions_by_url.items(), key=lambda item: min(row["rootSequence"] for row in item[1])):
        provenance_row = provenance_by_url.get(face_url) or {}
        file_name = provenance_row.get("file")
        if not file_name:
            raise AssertionError(f"Objective direct FaceURL provenance missing: {face_url}")
        source_path = "assets/tts-mod/extract/v2-dl/tree/" + file_name
        corpus_row = corpus_by_path.get(source_path)
        if not corpus_row or not corpus_row.get("rulesTextPresent"):
            raise AssertionError(f"Objective direct rules-bearing corpus row missing: {source_path}")
        base_definitions = [row for row in definitions if row["disposition"].startswith("base-competitive")]
        effect_kind = base_definitions[0]["effectKind"] if base_definitions else definitions[0]["effectKind"]
        anatomy = _source_asset_anatomy(corpus_row, effect_kind if effect_kind != "facility-restart-blocked" and not effect_kind.startswith("prototype-") else None)
        source_assets.append({
            "assetId": f"OBJECTIVE-ASSET-{len(source_assets)+1:03d}",
            "sourceId": f"SRC-OBJECTIVE-DIRECT-ASSET-{corpus_row['sourceSha256'][:16].upper()}",
            "sourcePath": source_path,
            "sourceSha256": corpus_row["sourceSha256"],
            "sourceRole": "direct-selected-base-face" if base_definitions else "direct-prototype-root-exclusion",
            "sourceSheetId": None,
            "sourceSheetPath": None,
            "sourceSheetSha256": None,
            "sourceSheetGrid": None,
            "customDeckId": None,
            "generatedCell": None,
            "selectedBasePhysicalOccurrenceIds": [_physical_occurrence_id(row) for row in base_definitions],
            "selectedPrototypePhysicalOccurrenceIds": [_physical_occurrence_id(row) for row in definitions if "prototype" in row["disposition"]],
            "baseSelectorGap": None,
            "backlogUnitId": "CARD:" + corpus_row["sourceSha256"][:16],
            "corpusExtractionState": corpus_row.get("extractionState"),
            "effectKind": effect_kind,
            "provenanceReferenceCount": provenance_row.get("refs"),
            **anatomy,
        })
    if len(source_assets) != 50 or len({row["sourcePath"] for row in source_assets}) != 50:
        raise AssertionError("Objective exact 50 source-face asset closure changed")
    asset_by_path = {row["sourcePath"]: row for row in source_assets}

    # Verify every generated crop against exact parent bytes and exact grid/cell.
    for sheet_path, grid, paths in (
        (OBJECTIVE_SHEET_PATH, {"columns": 7, "rows": 3, "cellWidth": 827, "cellHeight": 1111}, [_generated_path("3944", cell) for cell in range(21)]),
        (MISSION_TASK_SHEET_PATH, {"columns": 5, "rows": 2, "cellWidth": 1136, "cellHeight": 1525}, [_generated_path("3938", cell) for cell in range(10)]),
    ):
        with Image.open(repo / sheet_path) as sheet_image:
            if sheet_image.size != (grid["columns"] * grid["cellWidth"], grid["rows"] * grid["cellHeight"]):
                raise AssertionError(f"Objective parent sheet dimensions drift: {sheet_path}")
            for cell, source_path in enumerate(paths):
                row_index, column_index = divmod(cell, grid["columns"])
                crop = sheet_image.crop((column_index * grid["cellWidth"], row_index * grid["cellHeight"], (column_index + 1) * grid["cellWidth"], (row_index + 1) * grid["cellHeight"])).convert("RGB")
                with Image.open(repo / source_path) as generated:
                    if generated.convert("RGB").tobytes() != crop.tobytes():
                        raise AssertionError(f"Objective generated crop pixel drift: {source_path}")

    physical_faces = []
    excluded_physical = []
    category_copy_counts = Counter()
    for definition in ROOT_DEFINITIONS:
        child = raw_children_by_root[definition["rootGuid"]][definition["rootSequence"] - 1]
        custom = child.get("CustomDeck") or {}
        child_custom_id = next(iter(custom))
        selector = custom[child_custom_id]
        root_custom_matches = [
            custom_id for custom_id, custom_value in (raw_roots_by_guid[definition["rootGuid"]].get("CustomDeck") or {}).items()
            if custom_value.get("FaceURL") == selector.get("FaceURL")
        ]
        if len(root_custom_matches) != 1:
            raise AssertionError(f"Objective exact root CustomDeck selector is ambiguous: {definition['guid']}")
        root_custom_id = root_custom_matches[0]
        if definition["generatedCell"] is not None:
            sheet = "3938" if definition["rootGuid"] == "eabc1d" else "3944"
            source_path = _generated_path(sheet, definition["generatedCell"])
        else:
            source_path = "assets/tts-mod/extract/v2-dl/tree/" + provenance_by_url[selector["FaceURL"]]["file"]
        asset = asset_by_path[source_path]
        category_copy_counts[definition["category"]] += 1
        copy_id = f"BASE-{definition['category'].upper()}-DECK-COPY-{category_copy_counts[definition['category']]:02d}"
        source_id = _physical_source_id(definition)
        face = {
            **definition,
            "copyId": copy_id,
            "deckId": {"mission-objective": "BASE-MISSION-OBJECTIVE-DECK", "private-objective": "BASE-PRIVATE-OBJECTIVE-DECK", "mission-task": "BASE-MISSION-TASK-DECK"}[definition["category"]],
            "sourceId": source_id,
            "occurrenceId": _physical_occurrence_id(definition),
            "semanticRuleId": _physical_rule_id(definition),
            "sourcePath": source_path,
            "sourceSha256": asset["sourceSha256"],
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS source-bound {definition['category']} physical occurrence / root {definition['rootGuid']} / full CardID {definition['fullCardId']} / GUID {definition['guid']}",
            "sourceSelector": {
                "key": "FaceURL",
                "objectType": child.get("Name"),
                "fullCardId": definition["fullCardId"],
                "guid": definition["guid"],
                "parentDeckGuid": definition["rootGuid"],
                "rootCustomDeckId": root_custom_id,
                "childCustomDeckId": child_custom_id,
                "url": selector.get("FaceURL"),
                "backUrl": selector.get("BackURL"),
                "grid": {"columns": selector.get("NumWidth"), "rows": selector.get("NumHeight")},
                "generatedSpriteSheetCell": definition["generatedCell"] is not None,
                "sourceSheetPath": asset["sourceSheetPath"],
                "sourceSheetSha256": asset["sourceSheetSha256"],
                "sourceSheetGrid": asset["sourceSheetGrid"],
                "generatedCell": definition["generatedCell"],
                "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-BackURL-container-tuple-with-reviewed-sheet-hash-grid-cell" if definition["generatedCell"] is not None else "exact-full-CardID-GUID-direct-FaceURL-BackURL-container-tuple",
                "cardIdModuloJoinUsed": False,
            },
            "playerCountMetadata": {
                "ttsGmNotesMinimum": definition["ttsGmNotesMinimum"],
                "visiblePrintedThreshold": asset["visiblePrintedPlayerCount"],
                "luaFilteringEvidence": "assets/tts-mod/extract/v2/lua_script.lua:lines 4516–4531",
                "includedForStandardPlayerCounts": [count for count in range(2, 6) if definition["ttsGmNotesMinimum"] <= count] if definition["disposition"].startswith("base-competitive") else [],
                "technicalMetadataIsPrintedAlias": False,
            },
            "backlogUnitId": asset["backlogUnitId"],
            "printedTitle": asset["printedTitle"],
            "printedCondition": asset["printedCondition"],
            "printedFooter": asset["printedFooter"],
            "printedTypeLine": asset["printedTypeLine"],
            "objectiveChoiceInstruction": asset["objectiveChoiceInstruction"],
            "panels": [{**panel, "panelId": f"{copy_id}-{panel['panelId']}"} for panel in asset["panels"]],
            "sentences": [{**sentence, "sentenceId": f"{copy_id}-{sentence['sentenceId']}", "panelId": f"{copy_id}-{sentence['panelId']}"} for sentence in asset["sentences"]],
            "iconOccurrences": [{**icon, "iconId": f"{copy_id}-{icon['iconId']}"} for icon in asset["iconOccurrences"]],
            "checkboxPanels": [f"{copy_id}-{panel_id}" for panel_id in asset["checkboxPanels"]],
            "conditionConnectorCounts": asset["conditionConnectorCounts"],
            "conditionTree": _condition_tree(definition["effectKind"]) if definition["disposition"].startswith("base-competitive") else None,
            "selectedEvidenceUsed": asset["selectedEvidenceUsed"],
            "selectedEvidenceRunIdentity": asset["selectedEvidenceRunIdentity"],
            "representationBoundary": asset["representationBoundary"],
            "identityJoinEvidence": {
                "identityJoin": "exact raw root physical occurrence and exact source-asset projection",
                "titleOnlyJoin": False,
                "bodySimilarityJoin": False,
                "categoryLabelOnlyJoin": False,
                "privatePersonalGlobalAliasJoin": False,
                "folderOnlyJoin": False,
                "sourceOrderOnlyJoin": False,
                "sourceSheetOnlyJoin": False,
                "generatedCellOnlyJoin": False,
                "cardIdModuloJoin": False,
                "licensedKeyJoin": False,
                "officialHelpTitleJoin": False,
            },
        }
        if definition["disposition"].startswith("base-competitive"):
            physical_faces.append(face)
        else:
            excluded_physical.append(face)
    if len(physical_faces) != 30 or len(excluded_physical) != 9:
        raise AssertionError("Objective physical base/prototype partition drift")

    official_occurrences = [_official_occurrence(unit) for unit in objective_help["units"]]
    if len(official_occurrences) != 45:
        raise AssertionError("Objective Help occurrence closure drift")

    bga_sha = _sha(repo / BGA_PATH)
    bga_rows = _parse_bga_table(repo / BGA_PATH)
    if len(bga_rows) != 38:
        raise AssertionError("Objective licensed table count drift")
    for row in bga_rows:
        row.update({"sourceId": BGA_SOURCE_ID, "sourcePath": BGA_PATH, "sourceSha256": bga_sha, "authority": "licensed-digital-secondary", "assertedTtsPhysicalIdentityLinks": [], "assertedOfficialOccurrenceIdentityLinks": []})
        competitive = row["assetType"] in {"shared", "private"} or (row["assetType"] == "mission" and row["soloCoop"] is False)
        row["competitiveDisposition"] = "base-competitive-licensed-occurrence" if competitive else "solo-coop-excluded"
        row["effectKind"] = BGA_EFFECT_KINDS.get(row["key"]) if competitive else None
        row["semanticRuleId"] = _bga_rule_id(row["key"], row["assetType"]) if competitive else None
        row["conditionTree"] = _condition_tree(row["effectKind"]) if row["effectKind"] else None
        row["playerCountMetadata"] = {"present": False, "semanticMinimumPlayers": None}
        if competitive and not row["effectKind"]:
            raise AssertionError(f"unmapped competitive BGA Objective row: {row['key']}")

    # Alias scope is exact. PERSONAL OBJECTIVE may project to Private Objective
    # only for listed tuples; neither the misspelled Lua role nor Corporate/
    # prototype footers create a global family alias.
    personal_alias = next(row for row in aliases["aliases"] if row["aliasId"] == "AL-003")
    personal_alias_paths = {row["sourcePath"] for row in personal_alias["sourceTuples"]}
    for face in physical_faces:
        footer = face["printedFooter"]
        face["privatePersonalAliasProjection"] = {
            "aliasId": "AL-003" if footer == "PERSONAL OBJECTIVE" and face["sourcePath"] in personal_alias_paths else None,
            "sourceFooter": footer,
            "semanticCategory": face["category"],
            "globalAliasUsed": False,
        }
        if footer == "PERSONAL OBJECTIVE" and face["sourcePath"] not in personal_alias_paths:
            raise AssertionError(f"Objective PERSONAL alias tuple missing: {face['sourcePath']}")

    identity_by_key = {row["normalizedExactStringKey"]: row["identityObservationId"] for row in identities["records"]}
    for collection in (physical_faces, excluded_physical):
        for face in collection:
            face["namedIdentityRef"] = identity_by_key.get(_normalize(face["printedTitle"]))
    for row in official_occurrences:
        row["namedIdentityRef"] = identity_by_key.get(_normalize(row["printedTitle"] or "")) if row["printedTitle"] else None
    for row in bga_rows:
        row["namedIdentityRef"] = identity_by_key.get(_normalize(row["name"] or "")) if row["name"] else None

    sheet_provenance = {row["url"]: row for row in provenance if row.get("url") in {OBJECTIVE_SHEET_URL, MISSION_TASK_SHEET_URL}}
    back_provenance = {row["url"]: row for row in provenance if row.get("url") in {OBJECTIVE_BACK_URL, MISSION_TASK_BACK_URL}}
    if sheet_provenance[OBJECTIVE_SHEET_URL]["refs"] != 19 or sheet_provenance[MISSION_TASK_SHEET_URL]["refs"] != 4 or back_provenance[OBJECTIVE_BACK_URL]["refs"] != 33 or back_provenance[MISSION_TASK_BACK_URL]["refs"] != 11:
        raise AssertionError("Objective parent-sheet/back reference closure drift")

    source_sheets = [
        {"sourceId": "SRC-OBJECTIVE-PARENT-SHEET", "occurrenceId": "TTS-OBJECTIVE-PARENT-SHEET-3944", "sourcePath": OBJECTIVE_SHEET_PATH, "sourceSha256": _sha(repo / OBJECTIVE_SHEET_PATH), "customDeckId": "3944", "url": OBJECTIVE_SHEET_URL, "grid": {"columns": 7, "rows": 3, "cellWidth": 827, "cellHeight": 1111}, "baseSelectedCells": sorted(base_generated_cells["3944"]), "baseSelectorGapCells": sorted(set(range(21)) - base_generated_cells["3944"]), "prototypeRootSelectedCells": sorted(prototype_generated_cells["3944"]), "globalReferenceCount": 19, "parentSheetNotRulesFace": True},
        {"sourceId": "SRC-MISSION-TASK-PARENT-SHEET", "occurrenceId": "TTS-MISSION-TASK-PARENT-SHEET-3938", "sourcePath": MISSION_TASK_SHEET_PATH, "sourceSha256": _sha(repo / MISSION_TASK_SHEET_PATH), "customDeckId": "3938", "url": MISSION_TASK_SHEET_URL, "grid": {"columns": 5, "rows": 2, "cellWidth": 1136, "cellHeight": 1525}, "baseSelectedCells": [1], "baseSelectorGapCells": [0, 2, 3, 4, 5, 6, 7, 8, 9], "prototypeRootSelectedCells": [3, 5], "globalReferenceCount": 4, "parentSheetNotRulesFace": True},
    ]
    shared_backs = [
        {"sourceId": "SRC-OBJECTIVE-SHARED-BACK", "occurrenceId": "TTS-OBJECTIVE-SHARED-BACK", "sourcePath": OBJECTIVE_BACK_PATH, "sourceSha256": _sha(repo / OBJECTIVE_BACK_PATH), "url": OBJECTIVE_BACK_URL, "basePhysicalSelectorReferences": 22, "allCompetitiveRootSelectorReferences": 31, "globalReferenceCount": 33, "sharedByCategories": ["mission-objective", "private-objective"], "rulesFaceCounted": False},
        {"sourceId": "SRC-MISSION-TASK-SHARED-BACK", "occurrenceId": "TTS-MISSION-TASK-SHARED-BACK", "sourcePath": MISSION_TASK_BACK_PATH, "sourceSha256": _sha(repo / MISSION_TASK_BACK_PATH), "url": MISSION_TASK_BACK_URL, "basePhysicalSelectorReferences": 8, "allCompetitiveRootSelectorReferences": 8, "globalReferenceCount": 11, "sharedByCategories": ["mission-task"], "rulesFaceCounted": False},
    ]

    # Official/FAQ/visual source obligations remain independent. FAQ v1.2 has
    # no Objective/Mission-specific base ruling; this is an explicit zero, not
    # an omitted search.
    faq_hits = [unit["sourceUnitId"] for page in faq["pages"] for unit in page.get("units", []) if re.search(r"objective|mission task", json.dumps(unit, ensure_ascii=False), re.I)]
    if faq_hits:
        raise AssertionError("Objective FAQ v1.2 zero-hit boundary changed")
    visual_ids = {unit["occurrenceId"] for page in rulebook_visual["pages"] for unit in page.get("visualUnits", [])}
    relevant_visual_ids = ["RB-P03-V01", "RB-P11-V01", "RB-P13-V02", "RB-P39-V01"]
    if not set(relevant_visual_ids).issubset(visual_ids):
        raise AssertionError("Objective rulebook visual boundary changed")

    source_asset_backlog_ids = [row["backlogUnitId"] for row in source_assets]
    if any(unit_id not in backlog_by_id for unit_id in source_asset_backlog_ids):
        raise AssertionError("Objective exact card backlog tuple missing")
    help_backlog_ids = [row["backlogUnitId"] for row in official_occurrences]
    if any(unit_id not in backlog_by_id for unit_id in help_backlog_ids):
        raise AssertionError("Objective exact Help backlog tuple missing")
    overlap_ids = ["RULE:RT-010", "RULE:INT-009", "RULE:INT-011", *["VIS:" + value for value in relevant_visual_ids]]
    linked_backlog_ids = sorted(set([*source_asset_backlog_ids, *help_backlog_ids, *[unit_id for unit_id in overlap_ids if unit_id in backlog_by_id]]))

    title_multiplicity = {
        category: dict(sorted(Counter(row["printedTitle"] for row in physical_faces if row["category"] == category).items()))
        for category in ("mission-objective", "private-objective", "mission-task")
    }
    base_by_category = Counter(row["category"] for row in physical_faces)
    official_by_category = Counter(row["category"] for row in official_occurrences)
    visible_official_cards = [row for row in official_occurrences if row["category"] in {"mission-objective", "private-objective", "mission-task"} and row["visibility"] == "fully-visible"]
    occluded_official_cards = [row for row in official_occurrences if row["visibility"] == "partially-occluded"]
    competitive_bga = [row for row in bga_rows if row["competitiveDisposition"] == "base-competitive-licensed-occurrence"]
    counts = {
        "officialObjectiveCards": 22,
        "officialMissionObjectiveCards": 7,
        "officialPrivateObjectiveCards": 15,
        "officialMissionTaskCards": 8,
        "officialSoloCoopObjectiveCards": 12,
        "ttsMissionObjectiveRootOccurrences": 11,
        "ttsPrivateObjectiveRootOccurrences": 20,
        "ttsMissionTaskRootOccurrences": 8,
        "baseCompetitivePhysicalOccurrences": len(physical_faces),
        "baseMissionObjectivePhysicalOccurrences": base_by_category["mission-objective"],
        "basePrivateObjectivePhysicalOccurrences": base_by_category["private-objective"],
        "baseMissionTaskPhysicalOccurrences": base_by_category["mission-task"],
        "sourceClearPhysicalOccurrences": sum(row["semanticRuleId"] is not None for row in physical_faces),
        "sourceBlockedPhysicalOccurrences": sum(row["semanticRuleId"] is None for row in physical_faces),
        "generatedPhysicalOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] for row in physical_faces),
        "directPhysicalOccurrences": sum(not row["sourceSelector"]["generatedSpriteSheetCell"] for row in physical_faces),
        "prototypeHighCountPhysicalExclusions": len(excluded_physical),
        "prototypeMissionObjectivePhysicalExclusions": sum(row["category"] == "mission-objective" for row in excluded_physical),
        "prototypeCorporatePrivatePhysicalExclusions": sum(row["category"] == "private-objective" for row in excluded_physical),
        "soloCoopTtsRootOccurrencesExcluded": sum(row["physicalOccurrences"] for row in excluded_roots),
        "soloCoopRootDecksExcluded": len(excluded_roots),
        "sourceFaceAssets": len(source_assets),
        "baseSelectedSourceFaceAssets": sum(bool(row["selectedBasePhysicalOccurrenceIds"]) for row in source_assets),
        "baseSelectorGapSourceFaceAssets": sum(row["baseSelectorGap"] is not None for row in source_assets),
        "prototypeOnlyDirectSourceFaceAssets": sum(row["sourceRole"] == "direct-prototype-root-exclusion" for row in source_assets),
        "sourceSheets": len(source_sheets),
        "sourceSheetCells": 31,
        "baseSelectedGeneratedCells": sum(len(row["baseSelectedCells"]) for row in source_sheets),
        "baseSelectorGapCells": sum(len(row["baseSelectorGapCells"]) for row in source_sheets),
        "sharedBacks": len(shared_backs),
        "objectiveBackGlobalReferences": 33,
        "missionTaskBackGlobalReferences": 11,
        "physicalPanels": sum(len(row["panels"]) for row in physical_faces),
        "printedSentenceOccurrences": sum(len(row["sentences"]) for row in physical_faces),
        "functionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in physical_faces),
        "matchedIconOccurrences": sum(sum(icon["semanticReferenceId"] is not None for icon in row["iconOccurrences"]) for row in physical_faces),
        "literalNoMatchIconOccurrences": sum(sum(icon["semanticReferenceId"] is None for icon in row["iconOccurrences"]) for row in physical_faces),
        "checkboxPhysicalOccurrences": sum(bool(row["checkboxPanels"]) for row in physical_faces),
        "officialHelpUnits": len(official_occurrences),
        "officialHelpFullyVisibleUnits": sum(row["visibility"] == "fully-visible" for row in official_occurrences),
        "officialHelpOccludedUnits": len(occluded_official_cards),
        "officialHelpCardUnits": sum(official_by_category[value] for value in ("mission-objective", "private-objective", "mission-task")),
        "officialHelpVisibleCardUnits": len(visible_official_cards),
        "officialHelpVisibleFunctionalIcons": objective_help["counts"]["functionalIconOccurrences"],
        "officialHelpPartiallyVisibleIcons": objective_help["counts"]["partiallyVisibleIconOccurrences"],
        "officialVisibleSemanticRecords": sum(row["effectKind"] is not None for row in official_occurrences),
        "officialOccludedEffectRecordsProhibited": len(occluded_official_cards),
        "licensedRows": len(bga_rows),
        "licensedCompetitiveRows": len(competitive_bga),
        "licensedCompetitiveMissionTasks": sum(row["assetType"] == "mission" for row in competitive_bga),
        "licensedCompetitiveObjectives": sum(row["assetType"] in {"shared", "private"} for row in competitive_bga),
        "licensedSoloCoopRowsExcluded": sum(row["competitiveDisposition"] == "solo-coop-excluded" for row in bga_rows),
        "assertedPhysicalToLicensedIdentityLinks": 0,
        "assertedPhysicalToOfficialIdentityLinks": 0,
        "faqObjectiveSpecificOccurrences": 0,
        "rulebookVisualOccurrences": len(relevant_visual_ids),
        "cardBacklogTuples": len(source_asset_backlog_ids),
        "objectiveHelpBacklogUnits": len(help_backlog_ids),
        "overlappingBacklogObligationsLinked": len(linked_backlog_ids),
        "semanticPhysicalFaceRecords": sum(row["semanticRuleId"] is not None for row in physical_faces),
        "semanticOfficialVisibleFaceRecords": sum(row["effectKind"] is not None for row in official_occurrences),
        "semanticLicensedCompetitiveRecords": len(competitive_bga),
    }
    return {
        "schemaVersion": 1,
        "recordType": "semantic-objective-mission-source-index",
        "scope": "entire base-competitive Mission Objective, Private Objective, and Mission Task family at exact physical/source-occurrence boundaries; Solo/Coop roots, Corporate/high-count prototypes, parent sheets, backs, selector gaps, occluded official spans, placeholders, and duplicate references remain explicit exclusions or boundaries",
        "derivationPolicy": "Derive TTS physical membership only from exact Lua roles, root GUIDs, raw full CardID/GUID/CustomDeck/FaceURL/BackURL/container tuples, GMNotes player-count metadata, and reviewed sheet/hash/grid/cell selectors. Never join by display title, normalized wording, category/footer label, body similarity, folder/order/cell, source sheet, CardID modulo, licensed key, official Help position, or multiplicity.",
        "counts": counts,
        "titleMultiplicity": title_multiplicity,
        "rootDeckEvidence": root_evidence,
        "physicalFaces": physical_faces,
        "excludedPhysicalOccurrences": excluded_physical,
        "sourceFaceAssets": source_assets,
        "sourceSheets": source_sheets,
        "sharedBacks": shared_backs,
        "officialHelpOccurrences": official_occurrences,
        "licensedDigitalOccurrences": bga_rows,
        "excludedSoloCoopRoots": excluded_roots,
        "crossSourceIdentityBoundary": {
            "physicalToOfficial": "No official Help occurrence identifies a TTS root GUID, full CardID/GUID copy, generated cell, or direct URL. Visible current wording controls only its exact publisher occurrence; occluded bodies stay occluded.",
            "physicalToLicensed": "All 38 licensed rows remain independent. The 26 competitive rows and 12 Solo/Coop rows are never paired to a TTS copy by title, wording, key, order, player count, or multiplicity.",
            "privatePersonalAlias": "AL-003 projects PERSONAL OBJECTIVE to Private Objective only for its exact listed TTS footer tuples; it is not global and never applies to Corporate prototype footers, Lua role names, BGA keys, or other files.",
            "missionObjectiveTask": "Mission Objective and Mission Task remain separate categories/decks. A Mission Objective condition may inspect the one public Mission Task; that reference never identifies the two card objects.",
        },
        "familyCountEvidence": {
            "official": {"objectiveCards": 22, "missionObjectives": 7, "privateObjectives": 15, "missionTasks": 8, "soloCoopObjectives": 12, "source": "rulebook component list and Objective Help Sheet"},
            "tts": {"competitiveRootChildren": {"missionObjective": 11, "privateObjective": 20, "missionTask": 8}, "baseAfterExplicitCompetitiveBoundary": {"missionObjective": 7, "privateObjective": 15, "missionTask": 8}, "rawSaveSha256": raw_sha},
            "licensed": {"rows": 38, "competitiveRows": 26, "soloCoopRows": 12, "identityLinksToTts": 0},
            "officialHelp": {"units": 45, "fullyVisible": 35, "physicallyOccluded": 10, "visibleFunctionalIcons": 50, "partiallyVisibleIcons": 5},
            "backlog": {"cardUnitIds": source_asset_backlog_ids, "helpUnitIds": help_backlog_ids, "linkedUnitIds": linked_backlog_ids},
        },
        "excludedContent": {
            "soloCoop": excluded_roots,
            "prototypePhysicalOccurrences": [row["occurrenceId"] for row in excluded_physical],
            "parentSheets": "Two source sheets are provenance containers, not extra rules faces.",
            "backs": "The shared Objective and Mission Task BackURLs are hidden-information sides, not operative faces.",
            "selectorGaps": "Eighteen generated cells lack a base-competitive full selector; prototype bag/root selectors remain exclusions rather than repairs.",
            "officialOcclusion": "Ten official Help units retain only visible fragments and explicit metadata boundaries; BGA/TTS text never fills them.",
            "duplicateReferences": "Root, child, crop, corpus, Help, visual, licensed, and backlog references are evidence links, never extra physical cards.",
        },
    }


def objective_source_registry_rows(source_index: dict) -> list[dict]:
    rows = []
    raw_sha = source_index["familyCountEvidence"]["tts"]["rawSaveSha256"]
    for root in [*source_index["rootDeckEvidence"], *source_index["excludedSoloCoopRoots"]]:
        rows.append({
            "sourceId": root["sourceId"], "authority": "source-bound-component-scan",
            "version": f"TTS structured root / {root['role']} / {root['rootGuid']}",
            "path": RAW_SAVE_PATH, "sha256": raw_sha, "occurrenceId": f"TTS-OBJECTIVE-ROOT-{root['rootGuid'].upper()}",
            "evidenceIndexPath": OBJECTS_PATH, "evidenceRecord": root["rootGuid"], "provenanceIndexPath": LUA_PATH,
        })
    for sheet in source_index["sourceSheets"]:
        rows.append({"sourceId": sheet["sourceId"], "authority": "source-bound-component-scan", "version": f"TTS Objective/Mission parent sheet / CustomDeck {sheet['customDeckId']}", "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": PROGRESS_PATH})
    for back in source_index["sharedBacks"]:
        rows.append({"sourceId": back["sourceId"], "authority": "source-bound-component-scan", "version": "TTS hidden Objective/Mission shared back", "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for asset in source_index["sourceFaceAssets"]:
        if asset["selectedBasePhysicalOccurrenceIds"]:
            continue
        rows.append({"sourceId": asset["sourceId"], "authority": "source-bound-component-scan", "version": f"TTS Objective/Mission source asset boundary / {asset['sourceRole']}", "path": asset["sourcePath"], "sha256": asset["sourceSha256"], "occurrenceId": f"TTS-OBJECTIVE-SOURCE-ASSET-{asset['assetId']}", "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": asset["sourceSha256"], "provenanceIndexPath": PROGRESS_PATH if asset["generatedCell"] is not None else PROVENANCE_PATH})
    for face in [*source_index["physicalFaces"], *source_index["excludedPhysicalOccurrences"]]:
        rows.append({"sourceId": face["sourceId"], "authority": "source-bound-component-scan", "version": face["sourceVersion"], "path": face["sourcePath"], "sha256": face["sourceSha256"], "occurrenceId": face["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": face["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    bga = source_index["licensedDigitalOccurrences"][0]
    rows.append({"sourceId": BGA_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / MISSIONS_OBJECTIVES_DATA", "path": BGA_PATH, "sha256": bga["sourceSha256"], "occurrenceId": "MISSIONS_OBJECTIVES_DATA", "evidenceIndexPath": SECONDARY_PATH, "evidenceRecord": "MISSIONS_OBJECTIVES_DATA"})
    # SRC-OBJECTIVE-HELP is already contributed by Queen Health semantics; the
    # exact same source tuple is intentionally reused rather than duplicated.
    return rows


def _record_information(category: str, source_kind: str, occurrence_label: str) -> list[dict]:
    if category == "mission-task":
        return [{"informationId": "I-MISSION-TASK", "subjectRef": occurrence_label, "audience": "public", "revealTrigger": "setup face-up placement", "secrecy": "none; selected Mission Task identity and printed state are public"}]
    return [{"informationId": "I-OBJECTIVE-IDENTITY", "subjectRef": occurrence_label, "audience": "Objective owner only until source-defined endgame reveal; exact source publication evidence remains public corpus material", "revealTrigger": "chosen Objective endgame reveal only", "secrecy": "other players, spectators, logs, accessibility output, notifications, and unauthorized clients must not receive the live identity; discussion and lying do not authorize showing"}]


def _build_face_record(source: dict, source_kind: str, record, assertion, timing, participant, operation) -> dict:
    category = source["category"]
    effect_kind = source["effectKind"]
    rule_id = source["semanticRuleId"]
    source_id = source["sourceId"] if source_kind != "official" else OBJECTIVE_HELP_SOURCE_ID
    authority = {"physical": "source-bound-component-scan", "official": "official-component-reference", "licensed": "licensed-digital-secondary"}[source_kind]
    condition_text = source["printedCondition"]
    source_path = source["sourcePath"] if source_kind != "official" else OBJECTIVE_HELP_PATH
    source_sha = source["sourceSha256"] if source_kind != "official" else None
    locator = source.get("occurrenceId") or source.get("sourceUnitId") or source.get("key")
    tree = source["conditionTree"]
    terms, taxa = _term_taxa(effect_kind, category)
    named = [source["namedIdentityRef"]] if source.get("namedIdentityRef") else []
    evidence_record = {
        "physical": f"{CORPUS_PATH}:{source.get('sourceSha256')}",
        "official": f"{OBJECTIVE_HELP_EXTRACTION_PATH}:{source.get('sourceUnitId')}",
        "licensed": f"{BGA_PATH}:MISSIONS_OBJECTIVES_DATA:{source.get('key')}",
    }[source_kind]
    source_assertion = assertion(f"SA-{re.sub(r'[^A-Z0-9]+', '-', rule_id.upper()).strip('-')}-FACE", source_id, locator, ["applicability", "timing", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "outcomes", "unresolvedQuestionRefs", "sourceVariants"], condition_text, evidence_record)
    source_assertion["textKind"] = "verbatim"
    if source_sha:
        source_assertion["sourceSha256"] = source_sha
        source_assertion["sourcePath"] = source_path
    generic_assertion = assertion(f"SA-{re.sub(r'[^A-Z0-9]+', '-', rule_id.upper()).strip('-')}-FULFILL", "SRC-RULEBOOK", "printed pages 7 and 39 / Objective fulfillment and endgame", ["timing", "operations", "outcomes"], "An Objective is Fulfilled when all its conditions are met at the end of the game; it does not matter who or what fulfilled them. Still-alive Characters reveal and check chosen Objectives after Infection and Eclosion.", "docs/rulebooks/rulebook_text.txt:lines 786–790,6251–6273")
    assertions = [source_assertion, generic_assertion]
    atoms = _tree_atoms(tree)
    ops = []
    for index, atom in enumerate(atoms, 1):
        if atom.get("historicalState") and "checkbox" in atom["predicate"]:
            ops.append(operation(f"S{index:02d}", index, "set-state", "must", "rules-system", atom["predicate"], [source_assertion["assertionId"]], transition={"from": "unmarked public Mission Task checkbox", "to": "marked public Mission Task checkbox"}, notes="Resolve immediately at the first qualifying Robot/Reactor occurrence; the mark persists to endgame."))
        else:
            ops.append(operation(f"S{index:02d}", index, "evaluate-condition", "must", atom.get("subject") or "rules-system", atom["predicate"], [source_assertion["assertionId"], generic_assertion["assertionId"]], notes=f"Evaluate at {atom['evaluationWindow']}; source condition {atom['conditionId']}."))
        ops[-1]["sourceConditionId"] = atom["conditionId"]
        if source.get("panels"):
            condition_panels = [panel["panelId"] for panel in source["panels"] if panel["role"] == "condition"]
            if condition_panels:
                ops[-1]["sourcePanelIds"] = condition_panels
    if tree.get("operator") == "any":
        sequence = len(ops) + 1
        ops.append(operation(f"S{sequence:02d}", sequence, "resolve-open-alternative", "must", "Objective owner", "SEM-Q-075 OR-branch commitment/availability timing", [source_assertion["assertionId"], generic_assertion["assertionId"]], notes="No branch owner/timing/default is invented; preserve both printed branches and unavailable clauses."))
    if effect_kind == "mission-task-remain-unfulfilled":
        sequence = len(ops) + 1
        ops.append(operation(f"S{sequence:02d}", sequence, "resolve-open-alternative", "must", "rules-system", "SEM-Q-076 meaning of remain UNFULFILLED", [source_assertion["assertionId"], generic_assertion["assertionId"]], notes="Do not collapse continuous historical non-fulfillment into an endgame-only snapshot or vice versa."))
    sequence = len(ops) + 1
    ops.append(operation(f"S{sequence:02d}", sequence, "set-state", "must", "rules-system", f"this exact {category} occurrence is Fulfilled iff its exact grouped condition tree is satisfied", [source_assertion["assertionId"], generic_assertion["assertionId"]], transition={"from": "source occurrence condition result unevaluated", "to": "tax.state.objective.fulfilled"}, notes="If the exact grouped tree is not satisfied, retain this exact occurrence as Unfulfilled; never share state by title/body."))
    participants = [participant("P-RULES", "rules-system")]
    if category != "mission-task":
        participants.extend([participant("P-OBJECTIVE-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-OWNER-CHARACTER", "affected", "tax.entity.agent.character")])
    questions = _effect_questions(effect_kind)
    status = "source-backed-with-open-question" if questions else ("source-variant" if source_kind == "licensed" else "source-backed")
    semantic = record(
        rule_id,
        f"{source.get('printedTitle') or source.get('name') or locator} — {source_kind} occurrence {locator}",
        status,
        "component-effect",
        "official-primary",
        "open-alternatives" if questions else "verbatim-structure",
        assertions,
        terms,
        taxa,
        named,
        timing(f"TW-{re.sub(r'[^A-Z0-9]+', '-', rule_id.upper()).strip('-')}", "tax.process.procedure.endgame", "during", "once-per-exact-source-occurrence-if-selected"),
        participants,
        "must",
        [],
        [],
        _record_information(category, source_kind, locator),
        [],
        [],
        ops,
        {"policy": "source-conditional-steps", "unit": "exact source occurrence condition tree", "onImpossible": "no side effect is partially awarded; historical checkbox state remains independent; unresolved branch/continuous timing receives no default"},
        {"kind": "historical-checkbox-plus-endgame-snapshot" if any(atom.get("historicalState") for atom in atoms) else "endgame-check"},
        {"policy": "one fulfillment result per exact selected occurrence; repeated same-title physical copies remain separate"},
        [{"condition": "exact grouped condition tree satisfied at the source-defined check", "result": "this occurrence is Fulfilled"}, {"condition": "one or more mandatory clauses fail", "result": "this occurrence is Unfulfilled"}],
        questions,
        [],
    )
    minimum = None
    if source_kind == "physical":
        minimum = source["playerCountMetadata"]["ttsGmNotesMinimum"]
    elif source_kind == "official":
        minimum = source["playerCountMetadata"]["semanticMinimumPlayers"]
    semantic["applicability"]["playerCount"] = {"min": minimum, "max": 5, "source": "TTS GMNotes/Lua technical filter" if source_kind == "physical" else "visible Number of Characters metadata"} if minimum else None
    return semantic


def build_objective_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo, condition
    records = []
    physical_rule_ids = [row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"]]
    official_rule_ids = [row["semanticRuleId"] for row in source_index["officialHelpOccurrences"] if row["effectKind"]]
    licensed_rule_ids = [row["semanticRuleId"] for row in source_index["licensedDigitalOccurrences"] if row["competitiveDisposition"] == "base-competitive-licensed-occurrence"]
    objective_dispatch_ids = [
        *[row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"] and row["category"] != "mission-task"],
        *[row["semanticRuleId"] for row in source_index["officialHelpOccurrences"] if row["effectKind"] and row["category"] != "mission-task"],
        *[row["semanticRuleId"] for row in source_index["licensedDigitalOccurrences"] if row["semanticRuleId"] and row["assetType"] in {"shared", "private"}],
    ]
    mission_dispatch_ids = [
        *[row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"] and row["category"] == "mission-task"],
        *[row["semanticRuleId"] for row in source_index["officialHelpOccurrences"] if row["effectKind"] and row["category"] == "mission-task"],
        *[row["semanticRuleId"] for row in source_index["licensedDigitalOccurrences"] if row["semanticRuleId"] and row["assetType"] == "mission"],
    ]

    records.append(record(
        "SEM-OBJECTIVE-SETUP-001", "Set up competitive Objective decks and one Mission Task", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-OBJECTIVE-SETUP-RB", "SRC-RULEBOOK", "printed pages 3 and 10 / lines 530–536,2631–2657", ["applicability", "timing", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "outcomes"], "The base game has 7 Mission Objectives, 15 Private Objectives, and 8 Mission Tasks. Remove cards above the Character count, shuffle each deck separately, deal one Private and one Mission Objective to each player face down, box the rest unseen, reveal one random Mission Task, and box the rest.", "docs/rulebooks/rulebook_text.txt:lines 530–536,2631–2657"), assertion("SA-OBJECTIVE-SETUP-TTS", "SRC-OBJECTIVE-MISSION-ROOT", "exact three competitive root tuples and Lua setupPhase02", ["applicability", "operations", "partialResolution", "sourceVariants"], "The TTS roots contain 11 Mission, 20 Personal, and 8 Mission Task children; exact GMNotes/Lua filtering retains the 7 + 15 + 8 base-competitive family and excludes nine high-count/prototype children.", "docs/rules/semantics/objective-mission-source-index.json:rootDeckEvidence")],
        ["term.mission-objective", "term.mission-task-card", "term.objective-card", "term.private-objective"], ["tax.entity.component.card.mission-task", "tax.entity.component.card.objective", "tax.entity.information.objective.mission", "tax.entity.information.objective.private", "tax.scaffold.supply-pool", "tax.scaffold.zone.deck"], [],
        timing("TW-OBJECTIVE-SETUP", "tax.entity.component.card.objective", "when-triggered", "once-during-base-standard-setup"), [participant("P-RULES", "rules-system"), participant("P-PLAYERS", "collection", "tax.entity.agent.player")], "must", [], [],
        [{"informationId": "I-OBJECTIVE-SETUP-DECKS", "subjectRef": "eligible Objective identities/order and boxed remainders", "audience": "hidden from all except each dealt card's owner", "revealTrigger": "source-defined endgame reveal for chosen Objectives only", "secrecy": "shuffle order, undealt cards, other players' cards, and boxed remainders are not exposed in logs, accessibility output, notifications, unauthorized client state, or spectator state"}, {"informationId": "I-MISSION-TASK-SETUP", "subjectRef": "selected Mission Task identity and face", "audience": "public", "revealTrigger": "setup placement face up", "secrecy": "none"}], [], [],
        [operation("S01", 1, "remove-component", "must", "P-RULES", "every card in each exact deck whose source-defined Number of Characters minimum exceeds current Character count", ["SA-OBJECTIVE-SETUP-RB", "SA-OBJECTIVE-SETUP-TTS"]), operation("S02", 2, "shuffle", "must", "P-RULES", "eligible Private Objective, Mission Objective, and Mission Task decks separately", ["SA-OBJECTIVE-SETUP-RB", "SA-OBJECTIVE-SETUP-TTS"]), operation("S03", 3, "draw-random", "must", "P-RULES", "1 Private Objective and 1 Mission Objective face down to each player", ["SA-OBJECTIVE-SETUP-RB"], repeat={"physicalPools": {"missionObjective": 7, "privateObjective": 15}, "eligibleTtsCountsByPlayers": {"2": {"missionObjective": 7, "privateObjective": 7}, "3": {"missionObjective": 7, "privateObjective": 12}, "4": {"missionObjective": 7, "privateObjective": 14}, "5": {"missionObjective": 7, "privateObjective": 15}}}), operation("S04", 4, "transition-zone", "must", "P-RULES", "all undealt Objective cards unseen", ["SA-OBJECTIVE-SETUP-RB"], transition={"from": "tax.scaffold.zone.deck", "to": "tax.scaffold.supply-pool"}, notes="Return these cards to the box unseen."), operation("S05", 5, "draw-random", "must", "P-RULES", "1 eligible Mission Task face up on the bottom Round-track tile", ["SA-OBJECTIVE-SETUP-RB"], repeat={"physicalPool": 8, "eligibleTtsCountsByPlayers": {"2": 5, "3": 8, "4": 8, "5": 8}}), operation("S06", 6, "transition-zone", "must", "P-RULES", "all unselected Mission Tasks back to the box", ["SA-OBJECTIVE-SETUP-RB"], transition={"from": "tax.scaffold.zone.deck", "to": "tax.scaffold.supply-pool"})],
        {"policy": "ordered-complete", "unit": "three exact finite decks", "onImpossible": "the locked base pools supply all required deals for standard 2–5 players; no title substitution, discard recycling, reshuffle from boxed cards, Solo/Coop card, prototype, parent sheet, back, gap, or placeholder is permitted"}, {"kind": "persistent-setup-state"}, {"policy": "one shuffled eligible deck per category; one Objective pair per player; one public Mission Task"}, [], [], []))

    records.append(record(
        "SEM-OBJECTIVE-SECRECY-001", "Objective ownership, secrecy, discussion, inspection, and reveal", "source-backed", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-OBJECTIVE-SECRECY-RB", "SRC-RULEBOOK", "printed page 10 / lines 2643–2655 and printed page 39 / lines 6267–6273", ["timing", "informationPolicy", "operations", "duration", "stacking", "outcomes"], "Deal both Objectives face down. Do not show Objective cards to other players at any point; reveal only the chosen Objective at the End of the Game. Objectives may be discussed and lied about.", "docs/rulebooks/rulebook_text.txt:lines 2643–2655,6267–6273"), assertion("SA-OBJECTIVE-SECRECY-CHOICE", "SRC-RULEBOOK", "printed page 13 / lines 3076–3094", ["informationPolicy", "operations", "duration"], "Remove one Objective without showing it; keep the other.", "docs/rulebooks/rulebook_text.txt:lines 3076–3094")],
        ["term.mission-objective", "term.objective-card", "term.private-objective"], ["tax.entity.component.card.objective", "tax.entity.information.objective.mission", "tax.entity.information.objective.private"], [],
        timing("TW-OBJECTIVE-SECRECY", "tax.entity.component.card.objective", "when-triggered", "continuous-from-deal-through-source-defined-reveal"), [participant("P-OWNER", "authorized-viewer", "tax.entity.agent.player"), participant("P-OTHER-PLAYERS", "unauthorized-viewers", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-OBJECTIVE-LIVE", "subjectRef": "both dealt Objective identities, retained choice, and removed identity", "audience": "owner-private", "revealTrigger": "only chosen Objective at the End of the Game while owner remains eligible to reveal", "secrecy": "voluntary showing is forbidden; discussion and lying convey claims, not card pixels/identity authority"}, {"informationId": "I-OBJECTIVE-REMOVED", "subjectRef": "removed Objective identity", "audience": "owner-private; hidden from all other players permanently absent another explicit source", "revealTrigger": "none in checked base sources", "secrecy": "removed-from-game must not imply a public discard or log entry"}, {"informationId": "I-OBJECTIVE-INSPECTION", "subjectRef": "source-authorized temporary inspection", "audience": "only the exact source-named inspector", "revealTrigger": "inspection instruction only", "secrecy": "inspection does not authorize showing, public reveal, logs, accessibility announcements, spectators, or unrelated serialized clients; Personal Log Codes owner/range remains SEM-Q-049"}], [], [],
        [operation("S01", 1, "set-state", "must", "P-RULES", "each dealt Objective identity owner-private", ["SA-OBJECTIVE-SECRECY-RB"]), operation("S02", 2, "prohibit", "must", "P-OWNER", "showing either Objective card to another player during the game", ["SA-OBJECTIVE-SECRECY-RB"]), operation("S03", 3, "permit", "may", "P-OWNER", "discussing or lying about Objective information without showing the card", ["SA-OBJECTIVE-SECRECY-RB"]), operation("S04", 4, "transition-zone", "must", "P-OWNER", "removed Objective with identity still private", ["SA-OBJECTIVE-SECRECY-CHOICE"], transition={"from": "owner-private Objective pair", "to": "tax.scaffold.zone.removed-from-game"}, notes="The zone transition does not make the removed identity public."), operation("S05", 5, "inspect-private", "if-able", "source-named inspector", "only Objective identities granted by an exact inspection effect", ["SA-OBJECTIVE-SECRECY-RB"], conditions=["an explicit source grants inspection"], notes="Inspection cannot inherit public reveal or a broader viewer/range; SEM-Q-049 remains for Personal Log Codes."), operation("S06", 6, "reveal", "must", "surviving eligible Objective owner", "chosen Objective only", ["SA-OBJECTIVE-SECRECY-RB"], conditions=["endgame Objective reveal step reached"])],
        {"policy": "per-selected-component", "unit": "one Objective identity", "onImpossible": "no unauthorized reveal, inference, default, or full-state exposure is permitted"}, {"kind": "deal-until-endgame-reveal-or-permanent-hidden-removal"}, {"policy": "each physical identity has one owner; discussion does not change visibility"}, [], [], []))

    records.append(record(
        "SEM-OBJECTIVE-FULFILLMENT-001", "Objective and Mission Task fulfillment check", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-OBJECTIVE-FULFILLED-HELP", OBJECTIVE_HELP_SOURCE_ID, "P1-GT-01 and P2-GT-01", ["timing", "operations", "outcomes", "partialResolution"], "An Objective is fulfilled when all of its conditions are met at the end of the game. It is not important which player fulfilled them or whether an Event/non-player effect did so.", "docs/rules/source-extraction/objective-help-sheet.json:P1-GT-01/P2-GT-01"), assertion("SA-OBJECTIVE-ENDGAME-RB", "SRC-RULEBOOK", "printed page 39 / lines 6251–6293", ["timing", "operations", "outcomes", "unresolvedQuestionRefs"], "After Infection and Eclosion, each still-alive Character reveals and checks the chosen Objective; a fulfilled chosen Objective is required to win.", "docs/rulebooks/rulebook_text.txt:lines 6251–6293")],
        ["term.fulfilled", "term.mission-task", "term.objective", "term.survivor"], ["tax.entity.information.mission-task", "tax.entity.information.objective", "tax.state.objective.fulfilled", "tax.state.participation.survivor"], [],
        timing("TW-OBJECTIVE-FULFILLMENT", "tax.process.procedure.endgame", "during", "once-per-chosen-exact-objective-and-referenced-task"), [participant("P-RULES", "rules-system"), participant("P-OWNER", "affected", "tax.entity.agent.player")], "must", [], [],
        [{"informationId": "I-FULFILLMENT-INPUTS", "subjectRef": "public game state, public Mission Task, chosen Objective after reveal, and source-defined historical marks/snapshots", "audience": "public at endgame except removed/unchosen Objective identity", "revealTrigger": "chosen Objective reveal and check", "secrecy": "condition evaluation must not reveal removed Objectives, dead owners' unrevealed cards, deck order, or unauthorized temporary inspection data"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "every exact condition atom at its source-defined endgame or historical window", ["SA-OBJECTIVE-FULFILLED-HELP", "SA-OBJECTIVE-ENDGAME-RB"]), operation("S02", 2, "resolve-open-alternative", "must", "P-OWNER", "SEM-Q-075 source-unspecified commitment/timing for printed OR branches and unavailable options", ["SA-OBJECTIVE-FULFILLED-HELP", "SA-OBJECTIVE-ENDGAME-RB"], conditions=["chosen Objective contains OR branches"]), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-076 continuous versus endgame meaning of remain UNFULFILLED", ["SA-OBJECTIVE-FULFILLED-HELP", "SA-OBJECTIVE-ENDGAME-RB"], conditions=["chosen Mission Objective says Mission Task must remain UNFULFILLED"]), operation("S04", 4, "set-state", "must", "P-RULES", "chosen Objective Fulfilled only if all source-grouped mandatory conditions/selected legal branch are satisfied", ["SA-OBJECTIVE-FULFILLED-HELP", "SA-OBJECTIVE-ENDGAME-RB"]), operation("S05", 5, "evaluate-condition", "must", "P-RULES", "who or what caused a condition does not alter fulfillment", ["SA-OBJECTIVE-FULFILLED-HELP"])],
        {"policy": "source-conditional-steps", "unit": "one exact Objective/Mission Task occurrence", "onImpossible": "a failed atom fails its mandatory group; no partial victory; OR/continuous timing remains no-default"}, {"kind": "endgame-snapshot-with-explicit-historical-exceptions"}, {"policy": "one result per exact occurrence; same titles/bodies never share state"}, [{"condition": "owner remains alive and chosen exact Objective is Fulfilled", "result": "owner wins"}], ["SEM-Q-075", "SEM-Q-076", "SEM-Q-078"], []))

    records.append(record(
        "SEM-OBJECTIVE-SURVIVOR-001", "Objective Survivor status", "source-backed", "constraint", "official-component-reference", "verbatim-structure",
        [assertion("SA-OBJECTIVE-SURVIVOR-HELP", OBJECTIVE_HELP_SOURCE_ID, "P1-GT-02 and P2-GT-02", ["timing", "operations", "outcomes", "duration"], "A Survivor is a Character who has not died during the game or final Eclosion. At Round 14, Characters who have not Escaped or Hibernated die.", "docs/rules/source-extraction/objective-help-sheet.json:P1-GT-02/P2-GT-02")],
        ["term.survivor"], ["tax.state.participation.survivor", "tax.state.participation.escaped", "tax.state.participation.hibernated"], [],
        timing("TW-OBJECTIVE-SURVIVOR", "tax.process.procedure.endgame", "during", "once-per-Character-after-final-Eclosion"), [participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [], [{"informationId": "I-SURVIVOR", "subjectRef": "death, Escape/Hibernation, final Eclosion, and resulting Survivor status", "audience": "public", "revealTrigger": "continuous/endgame", "secrecy": "none"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "Character has not died during play or final Eclosion", ["SA-OBJECTIVE-SURVIVOR-HELP"]), operation("S02", 2, "set-state", "must", "P-RULES", "non-Escaped/non-Hibernated Character dead when Round 14 ends", ["SA-OBJECTIVE-SURVIVOR-HELP"], conditions=["Round 14 ended"]), operation("S03", 3, "set-state", "if-able", "P-RULES", "tax.state.participation.survivor", ["SA-OBJECTIVE-SURVIVOR-HELP"], conditions=["Character remains alive after final Eclosion"])],
        {"policy": "per-selected-component", "unit": "one Character", "onImpossible": "not applicable"}, {"kind": "endgame-derived-status"}, {"policy": "one Survivor/not-Survivor result per Character"}, [], [], []))

    records.append(record(
        "SEM-OBJECTIVE-ESCAPE-001", "Objective Escape status", "source-backed", "constraint", "official-component-reference", "verbatim-structure",
        [assertion("SA-OBJECTIVE-ESCAPE-HELP", OBJECTIVE_HELP_SOURCE_ID, "P1-GT-03 and P2-GT-03", ["timing", "operations", "outcomes", "duration"], "Characters who leave using the Lander or Escape Shuttle count as Escaped even if final Infection/Eclosion kills them; Hibernated Characters do not Escape.", "docs/rules/source-extraction/objective-help-sheet.json:P1-GT-03/P2-GT-03")],
        ["term.escape", "term.escape-shuttle", "term.hibernate"], ["tax.process.procedure.escape", "tax.process.procedure.hibernate", "tax.state.participation.escaped", "tax.state.participation.hibernated"], [],
        timing("TW-OBJECTIVE-ESCAPE", "tax.process.procedure.escape", "when-triggered", "once-per-successful-Lander-or-Escape-Shuttle-departure"), [participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [], [{"informationId": "I-ESCAPE", "subjectRef": "Escape method/time and persistent Escaped status", "audience": "public", "revealTrigger": "departure", "secrecy": "none"}], [], [],
        [operation("S01", 1, "set-state", "must", "P-RULES", "tax.state.participation.escaped", ["SA-OBJECTIVE-ESCAPE-HELP"], conditions=["Character leaves via Lander or Escape Shuttle"]), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "final Infection/Eclosion death does not erase Escaped status", ["SA-OBJECTIVE-ESCAPE-HELP"]), operation("S03", 3, "prohibit", "must", "P-RULES", "treating Hibernation as Escape", ["SA-OBJECTIVE-ESCAPE-HELP"])],
        {"policy": "per-selected-component", "unit": "one Character departure", "onImpossible": "not applicable"}, {"kind": "persistent-historical-status"}, {"policy": "Escape and Hibernation remain distinct"}, [], [], []))

    records.append(record(
        "SEM-FACILITY-DESTRUCTION-001", "Facility destruction and Objective consequences", "source-backed", "procedure", "official-component-reference", "source-composed",
        [assertion("SA-FACILITY-DESTRUCTION-HELP", OBJECTIVE_HELP_SOURCE_ID, "P1-GT-05 and P2-GT-05", ["timing", "operations", "outcomes", "duration"], "Facility destruction kills all non-Escaped and Hibernated Characters and all Intruders, and destroys the Nest. It results from Autodestruction or an unavailable required Fire marker.", "docs/rules/source-extraction/objective-help-sheet.json:P1-GT-05/P2-GT-05")],
        ["term.facility", "term.nest", "term.survivor"], ["tax.entity.spatial.facility", "tax.entity.spatial.room.nest", "tax.state.participation.escaped", "tax.state.participation.hibernated"], [],
        timing("TW-FACILITY-DESTRUCTION", "tax.entity.spatial.facility", "when-triggered", "once-per-game"), [participant("P-RULES", "rules-system"), participant("P-CHARACTERS", "collection", "tax.entity.agent.character")], "must", [], [], [{"informationId": "I-FACILITY-DESTRUCTION", "subjectRef": "Facility, Character, Intruder, Queen, and Nest states", "audience": "public", "revealTrigger": "destruction", "secrecy": "Objective identities remain governed separately"}], [], [],
        [operation("S01", 1, "set-state", "must", "P-RULES", "Facility Destroyed", ["SA-FACILITY-DESTRUCTION-HELP"]), operation("S02", 2, "set-state", "must", "each non-Escaped Character including each Hibernated Character", "sem.state.participation.dead", ["SA-FACILITY-DESTRUCTION-HELP"]), operation("S03", 3, "remove-component", "must", "P-RULES", "all Intruders including Queen", ["SA-FACILITY-DESTRUCTION-HELP"]), operation("S04", 4, "set-state", "must", "P-RULES", "sem.state.room.nest-destroyed", ["SA-FACILITY-DESTRUCTION-HELP"]), operation("S05", 5, "invoke-process", "must", "P-RULES", "End of the Game", ["SA-FACILITY-DESTRUCTION-HELP"], invoke="SEM-ENDGAME-001")],
        {"policy": "ordered-complete", "unit": "one irreversible destruction trigger", "onImpossible": "not applicable"}, {"kind": "irreversible-game-state"}, {"policy": "Facility can be destroyed only once"}, [{"condition": "Facility Destroyed", "result": "Queen and Nest destruction predicates are true; only previously Escaped Characters avoid this death cause"}], [], []))

    records.append(record(
        "SEM-OBJECTIVE-FACE-CHECK-001", "Dispatch a chosen competitive Objective by exact source occurrence", "source-backed-with-open-question", "dispatcher", "official-primary", "open-alternatives",
        [assertion("SA-OBJECTIVE-DISPATCH-RB", "SRC-RULEBOOK", "printed page 39 / lines 6267–6293", ["timing", "operations", "outcomes", "unresolvedQuestionRefs"], "Each still-alive Character reveals and checks their chosen exact Objective after any required late choice.", "docs/rulebooks/rulebook_text.txt:lines 6267–6293")],
        ["term.mission-objective", "term.objective", "term.private-objective"], ["tax.entity.component.card.objective", "tax.entity.information.objective.mission", "tax.entity.information.objective.private"], [],
        timing("TW-OBJECTIVE-DISPATCH", "tax.process.procedure.endgame", "during", "once-per-surviving-owner"), [participant("P-OWNER", "affected", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [], [{"informationId": "I-OBJECTIVE-DISPATCH", "subjectRef": "chosen exact Objective occurrence and result", "audience": "public after reveal", "revealTrigger": "endgame", "secrecy": "removed Objective and other source variants remain hidden/not selected"}], [], [],
        [operation("S01", 1, "invoke-selected-process", "must", "P-RULES", "exact occurrence-specific chosen Objective semantic record", ["SA-OBJECTIVE-DISPATCH-RB"], notes="Dispatch uses the exact live physical/source occurrence identity; no title, wording, category, sheet, cell, modulo, Help layout, or licensed key join."), operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-078 reveal/check order among surviving Characters", ["SA-OBJECTIVE-DISPATCH-RB"], notes="Do not invent simultaneous or turn-order reveal where the source names no order.")],
        {"policy": "source-conditional-steps", "unit": "one chosen Objective", "onImpossible": "blocked/occluded/unmapped source occurrences cannot be filled from another source"}, {"kind": "instantaneous-endgame-dispatch"}, {"policy": "one exact rule target per chosen Objective"}, [], ["SEM-Q-078"], []))
    records[-1]["operations"][0]["dispatchRuleIds"] = objective_dispatch_ids

    records.append(record(
        "SEM-MISSION-TASK-CHECK-001", "Dispatch the one public Mission Task by exact source occurrence", "source-backed", "dispatcher", "official-primary", "verbatim-structure",
        [assertion("SA-MISSION-TASK-DISPATCH-RB", "SRC-RULEBOOK", "printed page 39 / lines 6277–6290", ["timing", "operations", "outcomes"], "The one Mission Task is public and never changes; a chosen Mission Objective may require it to be fulfilled.", "docs/rulebooks/rulebook_text.txt:lines 6277–6290")],
        ["term.mission-objective", "term.mission-task", "term.mission-task-card"], ["tax.entity.component.card.mission-task", "tax.entity.information.mission-task", "tax.entity.information.objective.mission"], [],
        timing("TW-MISSION-TASK-DISPATCH", "tax.process.procedure.endgame", "during", "once-per-requested-check-of-selected-task"), [participant("P-RULES", "rules-system")], "must", [], [], [{"informationId": "I-MISSION-TASK-DISPATCH", "subjectRef": "selected exact Mission Task occurrence and public fulfillment result", "audience": "public", "revealTrigger": "continuous/check", "secrecy": "none"}], [], [],
        [operation("S01", 1, "invoke-selected-process", "must", "P-RULES", "exact selected Mission Task semantic record", ["SA-MISSION-TASK-DISPATCH-RB"], notes="Dispatch uses exact source occurrence identity; the blocked TTS FACILITY RESTART face has no semantic target and cannot borrow current official or BGA text.")],
        {"policy": "source-conditional-steps", "unit": "one selected Mission Task", "onImpossible": "source-blocked exact occurrence remains blocked; no variant substitution"}, {"kind": "instantaneous-endgame-dispatch"}, {"policy": "one selected public Mission Task for base competitive play"}, [], [], []))
    records[-1]["operations"][0]["dispatchRuleIds"] = mission_dispatch_ids

    records.append(record(
        "SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", "Objective/Mission physical and source-variant boundaries", "source-backed", "constraint", "official-primary", "source-composed",
        [assertion("SA-OBJECTIVE-VARIANT-RB", "SRC-RULEBOOK", "printed pages 3, 10, 39, and 40", ["applicability", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "sourceVariants"], "Base competitive inventory is 7 Mission Objectives, 15 Private Objectives, and 8 Mission Tasks; Solo/Coop replaces standard Objectives and is outside this family.", "docs/rulebooks/rulebook_text.txt:lines 530–536,2631–2657,6274–6293,6412–6427"), assertion("SA-OBJECTIVE-VARIANT-TTS", "SRC-OBJECTIVE-MISSION-ROOT", "exact raw roots/sheets/backs/exclusions", ["applicability", "operations", "partialResolution", "sourceVariants"], "Exact TTS roots preserve 30 base physical copies, nine high-count/prototype exclusions, two parent sheets, two backs, eighteen base selector gaps, and 38 separately excluded Solo/Coop selectors.", "docs/rules/semantics/objective-mission-source-index.json"), assertion("SA-OBJECTIVE-VARIANT-HELP", OBJECTIVE_HELP_SOURCE_ID, "all 45 units", ["informationPolicy", "operations", "partialResolution", "sourceVariants"], "Objective Help has 45 units: 35 fully visible and 10 physically occluded. Occluded text-layer metadata is not visible face evidence.", "docs/rules/source-extraction/objective-help-sheet.json"), assertion("SA-OBJECTIVE-VARIANT-BGA", BGA_SOURCE_ID, "all 38 MISSIONS_OBJECTIVES_DATA rows", ["applicability", "operations", "partialResolution", "sourceVariants"], "Licensed data has 26 competitive and 12 Solo/Coop rows with no physical TTS or official-copy crosswalk.", "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js:MISSIONS_OBJECTIVES_DATA")],
        ["term.mission-objective", "term.mission-task-card", "term.objective-card", "term.private-objective", "term.solo-coop-objective-card"], ["tax.entity.component.card.mission-task", "tax.entity.component.card.objective", "tax.entity.component.card.objective.solo-coop"], [],
        timing("TW-OBJECTIVE-VARIANTS", "tax.entity.component.card.objective", "when-triggered", "per-source/identity audit"), [participant("P-RULES", "rules-system")], "must", [], [], [{"informationId": "I-OBJECTIVE-VARIANTS", "subjectRef": "root/deck/copy/source/sheet/cell/back/visibility/authority/alias/variant provenance", "audience": "public corpus evidence", "revealTrigger": "continuous audit", "secrecy": "does not reveal live shuffled order, dealt identities, removed identity, or owner-private cards"}], [], [],
        [operation("S01", 1, "preserve-identity", "must", "P-RULES", "all 30 base physical copies and nine prototype/high-count root exclusions as distinct full tuples", ["SA-OBJECTIVE-VARIANT-RB", "SA-OBJECTIVE-VARIANT-TTS"]), operation("S02", 2, "preserve-identity", "must", "P-RULES", "all 50 source face assets, two parent sheets, two backs, and eighteen base selector gaps without turning containers/sides/gaps into base faces", ["SA-OBJECTIVE-VARIANT-TTS"]), operation("S03", 3, "preserve-identity", "must", "P-RULES", "all 45 official Help units with exact 35-visible/10-occluded boundary", ["SA-OBJECTIVE-VARIANT-HELP"]), operation("S04", 4, "prohibit", "must", "P-RULES", "promotion of physically occluded official text-layer metadata or BGA/TTS wording into visible official face evidence", ["SA-OBJECTIVE-VARIANT-HELP", "SA-OBJECTIVE-VARIANT-BGA"]), operation("S05", 5, "preserve-identity", "must", "P-RULES", "all 38 licensed rows independently, with 12 Solo/Coop exclusions and zero asserted physical joins", ["SA-OBJECTIVE-VARIANT-BGA"]), operation("S06", 6, "prohibit", "must", "P-RULES", "title/body/category/footer/folder/order/sheet/cell/modulo/alias/threshold/multiplicity identity joins", ["SA-OBJECTIVE-VARIANT-TTS", "SA-OBJECTIVE-VARIANT-HELP", "SA-OBJECTIVE-VARIANT-BGA"]), operation("S07", 7, "prohibit", "must", "P-RULES", "global Private/Personal aliasing, Mission Objective/Mission Task flattening, or Solo/Coop leakage", ["SA-OBJECTIVE-VARIANT-RB", "SA-OBJECTIVE-VARIANT-TTS"])],
        {"policy": "per-selected-component", "unit": "one exact physical/source/side/cell occurrence", "onImpossible": "retain blocker or exclusion; never repair from another variant"}, {"kind": "persistent-audit-boundary"}, {"policy": "duplicate labels/bodies may coexist but never collapse copy or state identity"}, [], [], []))

    for face in source_index["physicalFaces"]:
        if not face["semanticRuleId"]:
            continue
        records.append(_build_face_record(face, "physical", record, assertion, timing, participant, operation))
    for source in source_index["officialHelpOccurrences"]:
        if not source["effectKind"]:
            continue
        source = {**source, "sourceId": OBJECTIVE_HELP_SOURCE_ID, "sourcePath": OBJECTIVE_HELP_PATH, "sourceSha256": _sha(Path(__file__).resolve().parents[1] / OBJECTIVE_HELP_PATH), "occurrenceId": source["sourceUnitId"]}
        records.append(_build_face_record(source, "official", record, assertion, timing, participant, operation))
    for source in source_index["licensedDigitalOccurrences"]:
        if source["competitiveDisposition"] != "base-competitive-licensed-occurrence":
            continue
        category = "mission-task" if source["assetType"] == "mission" else ("mission-objective" if source["assetType"] == "shared" else "private-objective")
        panels = _panels(source["name"] or "", source["printedCondition"], source["assetType"].upper(), None, None)
        normalized = {
            **source,
            "category": category,
            "printedTitle": source["name"],
            "printedFooter": source["assetType"],
            "occurrenceId": "BGA-MISSIONS-OBJECTIVES-" + source["key"],
            "panels": panels,
            "sentences": _sentences(source["printedCondition"], panels),
            "iconOccurrences": [],
            "checkboxPanels": [],
            "conditionConnectorCounts": {"AND": source["conditionLines"].count("{{AND}}"), "OR": int(bool(source["orEffectDesc"]))},
        }
        records.append(_build_face_record(normalized, "licensed", record, assertion, timing, participant, operation))

    expected_ids = set([*OBJECTIVE_REUSABLE_RULE_IDS, *physical_rule_ids, *official_rule_ids, *licensed_rule_ids])
    if {row["ruleId"] for row in records} != expected_ids:
        raise AssertionError("Objective semantic record ID closure changed")
    return records


def integrate_objective_shared_records(records: list[dict], source_index: dict, assertion, decision, operation) -> None:
    by_id = {row["ruleId"]: row for row in records}
    choice = by_id["SEM-RT-010"]
    choice_assertion = assertion("SA-RT010-HELP", OBJECTIVE_HELP_SOURCE_ID, "visible top instruction on 20 fully visible card occurrences", ["informationPolicy", "operations", "sourceVariants"], "Remove the other Objective from the game to: Progress the Objective Choice track once and draw [source-local Action-card glyph] accordingly.", "docs/rules/source-extraction/objective-help-sheet.json")
    choice_assertion["textKind"] = "verbatim"
    choice["sourceAssertions"].append(choice_assertion)
    choice["informationPolicy"] = [
        {"informationId": "I-OBJECTIVE-PAIR", "subjectRef": "both dealt Objective identities, selection, retained identity, and removed identity", "audience": "owner-private", "revealTrigger": "chosen Objective at source-defined endgame reveal only", "secrecy": "removed Objective is never shown; retained Objective stays hidden; discussion/lying is permitted but showing is forbidden; no logs/accessibility/spectator/client leakage"},
        {"informationId": "I-OBJECTIVE-TRACK", "subjectRef": "Objective Choice track movement and Action-card draw count", "audience": "public counts/state; drawn Action-card identities owner-private", "revealTrigger": "choice resolution", "secrecy": "Objective identity is not inferred from track movement or reward"},
    ]
    choice["operations"][1]["objectRef"] = "selected removed Objective"
    choice["operations"][1]["transition"] = {"from": "owner-private Objective pair", "to": "tax.scaffold.zone.removed-from-game"}
    choice["operations"][1]["notes"] = "The zone transition does not make the removed identity public."
    choice["operations"][2]["objectRef"] = "other Objective retained as chosen and owner-private"
    choice["operations"][3]["objectRef"] = "Objective Choice track marker down by one position if possible"
    choice["operations"][4] = operation("S05", 5, "invoke-process", "must", "P-CHOOSING-PLAYER", "draw Action cards according to the post-move Objective Choice marker: first choice 3; second/third 2; fourth/fifth 1", ["SA-RT010-1", "SA-RT010-HELP"], invoke="SEM-ACTION-CARD-DRAW-001", repeat={"drawCountByChoiceOrdinal": {"1": 3, "2": 2, "3": 2, "4": 1, "5": 1}, "markerReadTiming": "after moving marker down by one if possible"})
    choice["partialResolution"] = {"policy": "all-or-nothing-selection", "unit": "Objective choice procedure", "onImpossible": "may be initiated only in its legal Turn window while two Objectives remain; ordinary choice uses exact post-move 3/2/2/1/1 reward and never reveals either identity"}

    endgame = by_id["SEM-ENDGAME-001"]
    endgame["sourceAssertions"].append(assertion("SA-END-OBJECTIVE-SECRECY", "SRC-RULEBOOK", "printed pages 10, 13, and 39 / Objective setup, choice, reveal", ["decisions", "informationPolicy", "operations", "outcomes", "unresolvedQuestionRefs"], "Unchosen Objectives are removed without showing; late choosers choose before other players reveal; each still-alive Character then reveals/checks the chosen Objective.", "docs/rulebooks/rulebook_text.txt:lines 2643–2655,3076–3094,6267–6273"))
    endgame["decisions"][0] = decision("D-LATE-OBJECTIVE-REMOVE", "P-PLAYERS", "player-choice", 1, 1, False, "owner-private", ["one of that Player's two exact Objective cards to remove; the other is retained"])
    endgame["informationPolicy"] = [
        {"informationId": "I-OBJECTIVES", "subjectRef": "unselected/chosen/removed Objective identities", "audience": "owner-private until chosen reveal; removed identity stays owner-private", "revealTrigger": "chosen Objective endgame reveal only", "secrecy": "all late choices complete before another Objective is revealed; dead Characters have no source-defined reveal"},
        {"informationId": "I-END-RESULT", "subjectRef": "survival, revealed chosen Objectives, fulfillment, and winners", "audience": "public", "revealTrigger": "ordered endgame resolution", "secrecy": "no removed/boxed/dead-owner Objective identity leakage"},
    ]
    # Preserve the independently locked Infection/Eclosion S01–S04 sequence.
    endgame["operations"] = [
        *endgame["operations"][:4],
        operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-077 complete late-choice procedure, track/reward handling, and ordering among multiple late choosers", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"]),
        operation("S06", 6, "choose", "if-able", "each still-alive Player lacking chosen Objective", "one exact Objective to remove privately", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"], decision_ref="D-LATE-OBJECTIVE-REMOVE"),
        operation("S07", 7, "transition-zone", "if-able", "late-choosing Player", "selected removed Objective", ["SA-END-OBJECTIVE-SECRECY"], transition={"from": "owner-private Objective pair", "to": "tax.scaffold.zone.removed-from-game"}, notes="The removed identity remains owner-private."),
        operation("S08", 8, "set-state", "if-able", "late-choosing Player", "other Objective retained as chosen and owner-private", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"]),
        operation("S09", 9, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-078 reveal/check order among still-alive Characters after every late choice is complete", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"]),
        operation("S10", 10, "reveal", "must", "each still-alive Character", "chosen Objective only", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"]),
        operation("S11", 11, "invoke-process", "must", "P-RULES", "exact chosen Objective occurrence check", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"], invoke="SEM-OBJECTIVE-FACE-CHECK-001"),
        operation("S12", 12, "set-state", "if-able", "Character with fulfilled chosen Objective", "sem.state.outcome.winner", ["SA-END-1", "SA-END-OBJECTIVE-SECRECY"]),
    ]
    endgame["partialResolution"] = {"policy": "ordered-complete", "unit": "endgame sequence step", "onImpossible": "source-specific; OQ-001 remains explicit for Eclosion; SEM-Q-077/078 retain late-choice and reveal ordering without exposing removed/dead-owner Objectives or inventing track rewards"}
    endgame["unresolvedQuestionRefs"] = ["OQ-001", "SEM-Q-077", "SEM-Q-078"]




def build_objective_question_rows() -> list[dict]:
    def row(qid: str, title: str, decision_class: str, evidence: list[str], alternatives: list[tuple[str, str]], blocks: list[str]) -> dict:
        return {"questionId": qid, "title": title, "decisionClass": decision_class, "blocksRuleIds": sorted(set(blocks)), "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": evidence, "alternatives": [{"alternativeId": f"{qid}-{chr(65+index)}", "description": description, "support": support} for index, (description, support) in enumerate(alternatives)]}

    return [
        row("SEM-Q-075", "Objective OR-branch commitment, timing, and unavailable-option handling", "official-clarification-preferred", ["docs/rules/source-extraction/objective-help-sheet.json:P2-NOTE-RANKING-CHOICE", "docs/rulebooks/rulebook_text.txt:lines 3076–3094,6267–6293", "docs/rules/semantics/objective-mission-source-index.json"], [("The Objective owner commits to one currently available branch when choosing the Objective; only that branch may fulfill it.", "the Help note says the owner cannot choose an unavailable option, suggesting a branch choice, but gives no timing"), ("The Objective owner chooses one available branch only when revealing/checking at endgame.", "the branch affects only the endgame predicate and no earlier commitment procedure is printed"), ("No commitment is required; the Objective is fulfilled if any branch that is not barred for that owner is true at endgame.", "ordinary OR can be a logical alternative, while the Help note may only remove impossible branches")], ["SEM-OBJECTIVE-FULFILLMENT-001", "SEM-Q-PLACEHOLDER"]),
        row("SEM-Q-076", "Ulterior Motive ‘remain UNFULFILLED’ continuous history versus endgame snapshot", "official-clarification-preferred", ["docs/rules/source-extraction/objective-help-sheet.json:P1-MO-ULTERIOR-MOTIVE", "docs/rulebooks/rulebook_text.txt:lines 786–790,6277–6290", "docs/rules/semantics/objective-mission-source-index.json"], [("The selected Mission Task must never become fulfilled at any point after setup; an earlier fulfilled state fails Ulterior Motive even if conditions later cease.", "the word remain suggests a continuous historical constraint"), ("Only the ordinary endgame fulfillment snapshot matters; the selected Mission Task must be Unfulfilled when checked.", "FULFILLED is defined by conditions at the end of the game"), ("Use another source-defined historical window, such as from Objective choice rather than setup.", "the source does not state when the remain constraint begins")], ["SEM-OBJECTIVE-FULFILLMENT-001"]),
        row("SEM-Q-077", "Late endgame Objective choice procedure, Objective Choice track reward, and chooser order", "official-clarification-preferred", ["docs/rulebooks/rulebook_text.txt:lines 3076–3094,6267–6273", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P13-V02", "docs/rules/semantics/objective-mission-source-index.json"], [("Late choice performs only the private remove/retain steps; it does not move the track or draw Action cards, and multiple late choosers use a source-defined but currently unstated order.", "endgame says simply choose now; Action-card rewards have no stated use after Infection/Eclosion"), ("Late choice invokes the complete ordinary choice procedure, including post-move track reward, before reveals.", "‘simply do so now’ may refer back to the full Choosing an Objective procedure"), ("All late choosers choose simultaneously/private, with a source-defined aggregate track/reward treatment.", "all must choose before other Objectives reveal, but no chooser order is printed")], ["SEM-ENDGAME-001"]),
        row("SEM-Q-078", "Endgame chosen-Objective reveal and check order among surviving Characters", "source-ambiguity-owner-decision-after-source-search", ["docs/rulebooks/rulebook_text.txt:lines 6251–6273", "docs/rules/semantics/objective-mission-source-index.json"], [("Reveal and check in current Turn order after all late choices finish.", "many cohort procedures use Turn order, but this Objective step does not state it"), ("Reveal all chosen Objectives simultaneously, then check all conditions.", "the prose addresses each Character without an explicit sequence"), ("Each surviving owner chooses when to reveal/check, subject to all late choices completing first.", "physical play may permit voluntary ordering, but no owner is named")], ["SEM-ENDGAME-001", "SEM-OBJECTIVE-FACE-CHECK-001", "SEM-OBJECTIVE-FULFILLMENT-001"]),
    ]


def finalize_objective_question_blocks(records: list[dict], questions: list[dict]) -> None:
    record_by_id = {row["ruleId"]: row for row in records}
    question_by_id = {row["questionId"]: row for row in questions}
    for qid in OBJECTIVE_QUESTION_IDS:
        actual = sorted(rule_id for rule_id, semantic in record_by_id.items() if qid in semantic.get("unresolvedQuestionRefs", []))
        question_by_id[qid]["blocksRuleIds"] = actual
        if not actual:
            raise AssertionError(f"Objective question has no blocked semantic record: {qid}")


def build_objective_conflicts(source_index: dict) -> list[dict]:
    physical_ids = [row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"]]
    official_ids = [row["semanticRuleId"] for row in source_index["officialHelpOccurrences"] if row["effectKind"]]
    licensed_ids = [row["semanticRuleId"] for row in source_index["licensedDigitalOccurrences"] if row["semanticRuleId"]]
    return [
        {"conflictId": "SC-059", "title": "Official 7/15/8 inventory versus TTS 11/20/8 competitive roots", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-SETUP-001", "SEM-OBJECTIVE-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-OBJECTIVE-MISSION-ROOT", "SRC-OBJECTIVE-PRIVATE-ROOT", "SRC-MISSION-TASK-ROOT"], "difference": "Official base inventory is 7 Mission Objectives, 15 Private Objectives, and 8 Mission Tasks. TTS roots contain 11, 20, and 8 children; exact GMNotes/Lua filtering leaves 7 + 15 + 8 and excludes four high-count Mission plus five Corporate prototype Private children.", "resolution": "Preserve all 39 root children and exact exclusions. Never lower the official inventory, promote high-count prototypes, or identify copies by title/order."},
        {"conflictId": "SC-060", "title": "Shared Objective sheet contains multiple categories and unselected/prototype variants", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", *physical_ids], "evidenceRefs": ["SRC-OBJECTIVE-PARENT-SHEET", "docs/rules/semantics/objective-mission-source-index.json"], "difference": "The 7×3 sheet contains Mission and Personal faces; only exact full selectors choose twelve base cells, while nine cells are base selector gaps and one gap is selected only by a high-count prototype root child.", "resolution": "Keep sheet/hash/grid/cell and each exact selector. Category/footer/title/cell/modulo never supplies membership or identity."},
        {"conflictId": "SC-061", "title": "PERSONAL OBJECTIVE versus Private Objective is exact-source scoped", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", *[row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"] and row["category"] == "private-objective"]], "evidenceRefs": ["docs/rules/vocabulary/alias-registry.json:AL-003", "SRC-OBJECTIVE-PRIVATE-ROOT"], "difference": "Selected TTS source tuples print PERSONAL OBJECTIVE while the current official category is Private Objective; Corporate prototypes print another footer and the Lua role name is technical/misspelled.", "resolution": "Apply AL-003 only to its exact listed tuples. No global Personal/Private, role-name, footer, or category alias is created."},
        {"conflictId": "SC-062", "title": "Current and TTS Mission Task wording/panel variants", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", *[row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"] and row["category"] == "mission-task"], *[row["semanticRuleId"] for row in source_index["officialHelpOccurrences"] if row["effectKind"] and row["category"] == "mission-task"]], "evidenceRefs": ["SRC-OBJECTIVE-HELP", "SRC-MISSION-TASK-ROOT"], "difference": "Eradication, Primary Samples, Perimeter Clearing, and other TTS faces differ in killed/dead, cannot/NOT, cargo cohort, Room wording, thresholds, and checkbox/panel detail from current visible Help occurrences.", "resolution": "Official visible wording controls only exact publisher occurrences; every TTS physical occurrence remains verbatim. No title/body counterpart join is asserted."},
        {"conflictId": "SC-063", "title": "TTS FACILITY RESTART exact source blocker versus complete current/licensed variants", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", _official_rule_id("P1-MT-FACILITY-RESTART"), _bga_rule_id("FacilityRestart", "mission")], "evidenceRefs": ["docs/rules/source-extraction/card-gap-adjudications.json", "SRC-OBJECTIVE-HELP", BGA_SOURCE_ID], "difference": "The exact TTS physical face visibly ends one condition at ‘Systems must be’ with no recoverable following mark. Current official and licensed Facility Restart records are materially different complete occurrences.", "resolution": "Retain the one card backlog unit source-blocked. Neither current official nor BGA wording fills the physical TTS face."},
        {"conflictId": "SC-064", "title": "Private Objective current/TTS/licensed text and title variants", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", *[row["semanticRuleId"] for row in source_index["physicalFaces"] if row["semanticRuleId"] and row["category"] == "private-objective"], *[row["semanticRuleId"] for row in source_index["officialHelpOccurrences"] if row["effectKind"] and row["category"] == "private-objective"], *[row["semanticRuleId"] for row in source_index["licensedDigitalOccurrences"] if row["semanticRuleId"] and row["assetType"] == "private"]], "evidenceRefs": ["SRC-OBJECTIVE-HELP", "SRC-OBJECTIVE-PRIVATE-ROOT", BGA_SOURCE_ID], "difference": "TTS and current/licensed occurrences differ for Favourites/Crew’s Favorite/We’ve Got History, Veni, Great Hunt, Quarantine, Shutdown, Experimental Subjects, Insider/State’s Evidence, Luxurious Offer, and numbered targets; duplicate wording/titles also occur under distinct keys/copies.", "resolution": "Preserve all exact occurrences and authority. Matching title/body/function never identifies a physical copy or authorizes text replacement."},
        {"conflictId": "SC-065", "title": "Player-count metadata conflicts across TTS and current visible occurrences", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-SETUP-001", "SEM-OBJECTIVE-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-OBJECTIVE-HELP", "SRC-OBJECTIVE-PRIVATE-ROOT", "SRC-MISSION-TASK-ROOT", "assets/tts-mod/extract/selected-card-text-evidence.json"], "difference": "Exact TTS metadata/visible variants include Perimeter Clearing 1+, An Old Feud 3+, and Hostile Takeover 4+, while current Help shows 2+, 2+, and 3+. Licensed rows omit player-count metadata.", "resolution": "Keep applicability source-scoped. No title correspondence, licensed omission, or GMNotes technical value silently overwrites another occurrence."},
        {"conflictId": "SC-066", "title": "Ten official Help card occurrences are physically occluded", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-OBJECTIVE-HELP", "docs/rules/source-extraction/objective-help-sheet-layout.json"], "difference": "Four Official Order copies and six Private Objective occurrences have physically occluded title/count/body/icon/footer spans. Searchable PDF text-layer metadata exists for some but is not visible face evidence.", "resolution": "Index each occurrence and visible fragment independently. Do not create effect records from hidden metadata or fill them with TTS/BGA rows."},
        {"conflictId": "SC-067", "title": "Ulterior Motive ‘remain UNFULFILLED’ timing", "status": "unresolved", "questionId": "SEM-Q-076", "affectedRuleIds": [], "evidenceRefs": ["SRC-OBJECTIVE-HELP", "SRC-RULEBOOK", BGA_SOURCE_ID], "difference": "Ulterior Motive says the Mission Task must remain UNFULFILLED, while the general definition evaluates fulfillment when conditions are met at the end of the game.", "resolution": "No default; SEM-Q-076 retains continuous, endgame-snapshot, and later-window readings."},
        {"conflictId": "SC-068", "title": "Objective OR-branch choice and late endgame choice/reveal ordering", "status": "unresolved", "questionId": "SEM-Q-075", "affectedRuleIds": ["SEM-OBJECTIVE-FULFILLMENT-001", "SEM-ENDGAME-001", "SEM-OBJECTIVE-FACE-CHECK-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-OBJECTIVE-HELP"], "difference": "Cards and the Help note bar owner-specific branches but do not state branch commitment timing; endgame allows a late Objective choice before reveals without specifying full track/reward handling, chooser order, or reveal/check order.", "resolution": "No default; SEM-Q-075, SEM-Q-077, and SEM-Q-078 preserve the separate choices/order questions."},
        {"conflictId": "SC-069", "title": "Licensed competitive/Solo-Coop rows and TTS Solo/Coop roots remain outside standard copy identity", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-OBJECTIVE-VARIANT-BOUNDARIES-001", *licensed_ids], "evidenceRefs": [BGA_SOURCE_ID, "SRC-OBJECTIVE-SOLO-COOP-ROOT", "SRC-OBJECTIVE-SOLO-COOP-CUSTOM-ROOT", "SRC-RULEBOOK"], "difference": "BGA stores 26 competitive and 12 Solo/Coop rows. TTS separately stores 12 official-style and 26 custom Solo/Coop selectors; official inventory says 12 Solo/Coop cards and standard rules do not use them.", "resolution": "Retain all counts without forcing equality or a copy crosswalk. Solo/Coop and custom roots are indexed exclusions from base-competitive conclusions."},
    ]


def finalize_objective_conflict_blocks(records: list[dict], conflicts: list[dict]) -> None:
    by_question = {}
    for record in records:
        for question in record.get("unresolvedQuestionRefs") or []:
            by_question.setdefault(question, []).append(record["ruleId"])
    for conflict in conflicts:
        if conflict["conflictId"] == "SC-067":
            conflict["affectedRuleIds"] = sorted(by_question.get("SEM-Q-076", []))
        elif conflict["conflictId"] == "SC-068":
            conflict["affectedRuleIds"] = sorted(set([*by_question.get("SEM-Q-075", []), *by_question.get("SEM-Q-077", []), *by_question.get("SEM-Q-078", [])]))
