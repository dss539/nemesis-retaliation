from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

from semantic_attack_records import _find_guid, _parse_value


RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
OBJECTS_PATH = "assets/tts-mod/extract/v2/objects.json"
ROLES_PATH = "assets/tts-mod/extract/v2/lua_roles.json"
CLASSIFICATION_PATH = "assets/tts-mod/extract/v2/classification.json"
MANIFEST_PATH = "assets/tts-mod/extract/v2-dl/tree/manifest.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
SELECTED_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
PROGRESS_PATH = "assets/tts-mod/extract/vision-progress.json"
BACKLOG_PATH = "docs/rules/semantics/backlog.json"
BGA_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
FAQ_PATH = "docs/rules/source-extraction/faq-v1.2-source-extraction.json"
VISUAL_PATH = "docs/rules/source-extraction/rulebook-visual-obligations.json"

SUPPORT_ROOT_GUID = "f71196"
SUPPORT_ROOT_SOURCE_ID = "SRC-EQUIPMENT-SUPPORT-ROOT"
SUPPORT_SHEET_SOURCE_ID = "SRC-EQUIPMENT-SUPPORT-SHEET-29"
SUPPORT_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144.jpg"
SUPPORT_BACK_SOURCE_ID = "SRC-EQUIPMENT-SUPPORT-BACK"
SUPPORT_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-141.jpg"
SUPPORT_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880234833/1F244555560EF449E0BC92001FF09CE6301DC220/"
SUPPORT_SHEET_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880234762/3C863FACB5D0B6A80CB5191FD0B36EE0EB4A537C/"
BGA_EQUIPMENT_SOURCE_ID = "SRC-BGA-EQUIPMENT-ITEMS"

CHARACTER_BAGS = {
    "Combat Engineer": "284e9d",
    "Heavy Gun Operator": "6219a2",
    "Medical Support": "79d6b1",
    "Contractor": "47658d",
    "Officer": "6031da",
    "Recon": "8a007f",
}
CHARACTER_CODES = {
    "Combat Engineer": "CE",
    "Heavy Gun Operator": "HGO",
    "Medical Support": "MS",
    "Contractor": "CON",
    "Officer": "OFF",
    "Recon": "REC",
}


# Physical membership is locked to the raw Support Equipment root. The two
# generated selections are explicit full-CardID-to-cell crosswalks, not a
# CardID-modulo computation or title/body join.
_SUPPORT_ROWS = [
    (1, 556600, "a0daef", "5566", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-131.png", None, "ranged-weapon", "gatling-second-burst"),
    (2, 507800, "f56191", "5078", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-118.jpg", None, "ranged-weapon", "assault-shotgun-prevent"),
    (3, 508200, "a0f5b7", "5082", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-074.jpg", None, "melee-weapon", "entrenching-tool"),
    (4, 502900, "4ecb1e", "5029", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-163.png", None, "heavy-item", "security-system-control"),
    (5, 507200, "2f41b8", "5072", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-136.jpg", None, "ranged-weapon", "submachine-gun"),
    (6, 507600, "1281c5", "5076", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-114.jpg", None, "ranged-weapon", "plasma-gun"),
    (7, 507300, "a9fab3", "5073", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-083.jpg", None, "heavy-item", "rpg-launcher"),
    (8, 507400, "badad6", "5074", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-088.jpg", None, "heavy-item", "supporting-robot-controller"),
    (9, 507500, "33c9e4", "5075", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-134.jpg", None, "heavy-item", "portable-device"),
    (10, 507700, "4e708d", "5077", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-073.jpg", None, "ranged-weapon", "hand-cannon"),
    (11, 507100, "875c54", "5071", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-098.jpg", None, "melee-weapon", "tactical-hatchet"),
    (12, 410200, "98ad4c", "4102", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-030.png", None, "heavy-item", "combat-motion-tracker"),
    (13, 493400, "85096e", "4934", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-171.jpg", None, "heavy-item", "engineering-equipment"),
    (14, 2917, "dffd35", "29", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-17.png", 17, "ranged-weapon", "sonic-gun"),
    (15, 424900, "8ae645", "4249", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-044.png", None, "armor-item", "autoloader-belt"),
    (16, 508300, "fd46ec", "5083", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-055.jpg", None, "ranged-weapon", "flamethrower"),
    (17, 410400, "a242e6", "4104", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-033.png", None, "ranged-weapon", "grenade-launcher"),
    (18, 507000, "1f3ca2", "5070", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-108.jpg", None, "armor-item", "utility-vest"),
    (19, 507900, "df46d6", "5079", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-046.jpg", None, "melee-weapon", "bayonet"),
    (20, 466100, "4912a1", "4661", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-005.png", None, "armor-item", "tactical-armor"),
    (21, 424800, "881635", "4248", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-042.png", None, "armor-item", "heavy-armor"),
    (22, 508100, "785b03", "5081", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-085.jpg", None, "ranged-weapon", "drum-mag-rifle"),
    (23, 2910, "d29216", "29", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-10.png", 10, "heavy-item", "motion-tracker"),
    (24, 508000, "0f51f3", "5080", "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-067.jpg", None, "armor-item", "biohazard-armor"),
]


_CHARACTER_ROWS = [
    ("Combat Engineer", "2059a7", 431200, "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-021.png", "ranged-weapon", "automatic-shotgun-prototype", "prototype-current-authority-conflict-excluded"),
    ("Heavy Gun Operator", "427c1a", 524700, "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-025.png", "ranged-weapon", "bf-gun-prototype", "prototype-current-authority-conflict-excluded"),
    ("Medical Support", "219bff", 545000, "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-024.jpg", "ranged-weapon", "carbine", "source-clear-tts-character-kit-variant"),
    ("Contractor", "bac443", 545000, "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-052.jpg", "ranged-weapon", "handgun", "source-clear-tts-character-kit-variant"),
    ("Contractor", "21bd03", 591300, "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-042.png", "armor-item", "bulletproof-vest", "source-clear-tts-character-kit-variant"),
    ("Officer", "039116", 581900, "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-041.png", "ranged-weapon", "sawed-off-shotgun", "source-clear-tts-character-kit-variant"),
    ("Recon", "81d699", 556600, "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-032.png", "ranged-weapon", "assault-rifle", "source-clear-tts-character-kit-variant"),
]


CANONICAL_TEXT_OVERRIDES = {
    "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-134.jpg": {"title": "PORTABLE DEVICE"},
    "assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-10.png": {"title": "MOTION TRACKER", "typeLine": ""},
    "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-021.png": {"title": "AUTOMATIC SHOTGUN", "typeLine": "RANGED WEAPON, RIFLE"},
    "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-052.jpg": {"title": "HANDGUN"},
    "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-042.png": {"title": "BULLETPROOF VEST"},
}


EQUIPMENT_REUSABLE_RULE_IDS = [
    "SEM-CHARACTER-ITEM-SETUP-001",
    "SEM-SUPPORT-EQUIPMENT-DRAFT-001",
    "SEM-HEAVY-ITEM-HAND-CAPACITY-001",
    "SEM-ARMOR-ITEM-LIFECYCLE-001",
    "SEM-EQUIPMENT-FULLY-LOADED-001",
    "SEM-HEAVY-ITEM-USE-001",
    "SEM-HEAVY-ITEM-ONE-USE-001",
    "SEM-ITEM-PASSIVE-EFFECT-001",
    "SEM-ITEM-LOSS-ATTACHED-GEAR-001",
    "SEM-WEAPON-MALFUNCTION-LIFECYCLE-001",
    "SEM-WEAPON-DIE-RESULT-ADDITION-001",
    "SEM-GRENADE-LAUNCHER-MALFUNCTION-001",
    "SEM-EQUIPMENT-OCCURRENCE-DISPATCH-001",
    "SEM-EQUIPMENT-VARIANT-BOUNDARIES-001",
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _load_raw(repo: Path) -> tuple[dict, str]:
    data = (repo / RAW_SAVE_PATH).read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    return root, hashlib.sha256(data).hexdigest()


def _list_values(value) -> list:
    if isinstance(value, dict):
        return list(value.values())
    return list(value or [])


def _parse_bga_items(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const ITEMS_DATA = \{\n(.*?)\n\};\nconst MISSIONS_OBJECTIVES_DATA", text, re.S)
    if not match:
        raise AssertionError("ITEMS_DATA block missing")
    block = match.group(1)
    starts = list(re.finditer(r"^  ([A-Za-z][A-Za-z0-9]*): \{", block, re.M))
    rows = []
    for source_index, start_match in enumerate(starts):
        key = start_match.group(1)
        start = start_match.start()
        end = starts[source_index + 1].start() if source_index + 1 < len(starts) else len(block)
        source_block = block[start:end].rstrip("\n")

        def literal(pattern: str, default=None):
            found = re.search(pattern, source_block, re.S)
            return ast.literal_eval(found.group(1)) if found else default

        number = re.search(r"\n    nbr: (\d+)", source_block)
        rows.append({
            "key": key,
            "sourceOrder": source_index + 1,
            "deck": literal(r"\n    deck: ('(?:\\.|[^'])*')"),
            "name": literal(r"\n    name: ('(?:\\.|[^'])*')"),
            "subtitle": literal(r"\n    subtitle: ('(?:\\.|[^'])*')"),
            "heavy": bool(re.search(r"\n    heavy: true", source_block)),
            "armor": bool(re.search(r"\n    armor: true", source_block)),
            "rangedWeapon": bool(re.search(r"\n    rangedWeapon: true", source_block)),
            "meleeWeapon": bool(re.search(r"\n    meleeWeapon: true", source_block)),
            "noAmmoWeapon": bool(re.search(r"\n    noAmmoWeapon: true", source_block)),
            "nbr": int(number.group(1)) if number else None,
            "noIntruders": bool(re.search(r"\n    noIntruders: true", source_block)),
            "oneUse": bool(re.search(r"\n    oneUse: true", source_block)),
            "slots": literal(r"\n    slots: (\[(?:.|\n)*?\])\s*,\n    effectDesc", []),
            "effectDesc": literal(r"\n    effectDesc: (\[(?:.|\n)*?\])\s*,\n    traits", []),
            "traits": literal(r"\n    traits: ('(?:\\.|[^'])*')"),
            "sourceBlockText": source_block,
            "identityCrosswalkStatus": "independent licensed occurrence; no TTS or official physical identity join asserted",
        })
    return rows


def _selected_run(selected_entry: dict | None) -> dict | None:
    runs = (selected_entry or {}).get("runs") or []
    return runs[0] if len(runs) == 1 else None


def _source_text(path: str, corpus_row: dict, selected_entry: dict | None) -> dict:
    printed = corpus_row.get("printedData") or {}
    selected = _selected_run(selected_entry)
    visible = (selected or {}).get("visibleText") or {}
    identity = corpus_row.get("identity") or {}
    override = CANONICAL_TEXT_OVERRIDES.get(path) or {}
    title = override.get("title", visible.get("title") or printed.get("title") or (identity.get("titleFromCanonicalSlug") or "").upper())
    type_line = override.get("typeLine", visible.get("typeLine") if visible.get("typeLine") is not None else printed.get("typeLine") or "")
    body = printed.get("body")
    if body is None:
        body = visible.get("body") or ""
    upper_right = printed.get("upperRight")
    if upper_right is None:
        upper_right = visible.get("upperRight") or ""
    lower_center = printed.get("lowerCenter")
    if lower_center is None:
        lower_center = visible.get("lowerCenter") or ""
    return {
        "printedTitle": title,
        "typeLine": type_line,
        "printedBody": body,
        "upperRight": upper_right,
        "lowerCenter": lower_center,
        "selectedVisibleText": visible or None,
        "selectedEvidenceRunIdentity": (selected or {}).get("runIdentity"),
        "representationBoundary": {
            "corpusPrintedData": printed,
            "selectedVisibleText": visible or None,
            "canonicalIdentity": identity or None,
            "selectedAndCorpusNeverSilentlyFlattened": True,
        },
    }


def _body_panels(text: dict, prefix: str) -> list[dict]:
    body = text["printedBody"]
    panels = [
        {
            "panelId": f"{prefix}-P1",
            "readingOrder": 1,
            "role": "identity-and-trait-panel",
            "operative": True,
            "exactText": "\n".join(value for value in (text["printedTitle"], text["typeLine"], text["upperRight"]) if value),
            "headings": [value for value in (text["printedTitle"], text["typeLine"]) if value],
        },
        {
            "panelId": f"{prefix}-P2",
            "readingOrder": 2,
            "role": "artwork-panel",
            "operative": False,
            "exactText": "",
        },
    ]
    pieces = [piece for piece in re.split(r"\n(?:OR|AND/OR)\n", body) if piece]
    if not pieces:
        pieces = [""]
    cursor = 0
    for index, piece in enumerate(pieces, 3):
        start = body.find(piece, cursor)
        end = start + len(piece)
        cursor = end
        role = "passive-effect-panel" if piece.startswith(("Whenever", "If you are")) else "operative-effect-panel"
        panels.append({
            "panelId": f"{prefix}-P{index}",
            "readingOrder": index,
            "role": role,
            "operative": bool(piece),
            "exactText": piece,
            "bodyStart": start,
            "bodyEnd": end,
            "branchSeparatorBefore": "OR" if index > 3 else None,
        })
    panels.append({
        "panelId": f"{prefix}-P{len(panels)+1}",
        "readingOrder": len(panels) + 1,
        "role": "track-and-slot-region",
        "operative": False,
        "exactText": text["lowerCenter"],
    })
    return panels


def _sentences(text: dict, panels: list[dict], prefix: str) -> list[dict]:
    body = text["printedBody"]
    if not body:
        return []
    spans = []
    start = 0
    for match in re.finditer(r"\n(?:OR|AND/OR)\n|(?<=[.!?])\n", body):
        end = match.start()
        if end > start:
            spans.append((start, end))
        start = match.end()
    if start < len(body):
        spans.append((start, len(body)))
    rows = []
    operative_panels = [row for row in panels if row.get("operative") and row.get("bodyStart") is not None]
    for sequence, (start, end) in enumerate(spans, 1):
        exact = body[start:end]
        panel = next((row for row in operative_panels if row["bodyStart"] <= start and row["bodyEnd"] >= end), operative_panels[0])
        rows.append({
            "sentenceId": f"{prefix}-S{sequence:02d}",
            "sequence": sequence,
            "panelId": panel["panelId"],
            "exactText": exact,
            "start": start,
            "end": end,
        })
    return rows


def _icons(text: dict, selected_entry: dict | None, panels: list[dict], prefix: str) -> list[dict]:
    selected = _selected_run(selected_entry) or {}
    selected_verified = list(selected.get("verifiedIconOccurrences") or [])
    selected_unresolved = list(selected.get("unresolvedIconOccurrences") or [])
    body = text["printedBody"]
    tokens = []
    for location, value in (("upperRight", text["upperRight"]), ("body", body)):
        if not value:
            continue
        if location != "body" and not value.startswith("["):
            found = [value] if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", value) else []
        else:
            found = re.findall(r"\[([^\]]+)\]", value)
        cursor = 0
        for token in found:
            rendered = f"[{token}]" if location == "body" or value.startswith("[") else token
            start = value.find(rendered, cursor)
            if start < 0:
                start = value.find(token, cursor)
                rendered = token
            end = start + len(rendered)
            cursor = end
            semantic = None if token.startswith(("ICON:", "LOCAL_ICON:")) else f"icon.{token}"
            tokens.append((location, token, semantic, start, end))
    rows = []
    body_panels = [row for row in panels if row.get("bodyStart") is not None]
    verified_cursor = 0
    unresolved_cursor = 0
    for sequence, (location, token, semantic, start, end) in enumerate(tokens, 1):
        if location == "body":
            panel = next((row for row in body_panels if row["bodyStart"] <= start and row["bodyEnd"] >= end), body_panels[0])
        elif location == "upperRight":
            panel = panels[0]
        else:
            panel = panels[-1]
        selected_evidence = None
        if semantic and verified_cursor < len(selected_verified):
            candidate = selected_verified[verified_cursor]
            if candidate.get("canonicalToken") == semantic.removeprefix("icon."):
                selected_evidence = candidate
                verified_cursor += 1
        if semantic is None and unresolved_cursor < len(selected_unresolved):
            selected_evidence = selected_unresolved[unresolved_cursor]
            unresolved_cursor += 1
        rows.append({
            "occurrenceId": f"{prefix}-I{sequence:02d}",
            "sequence": sequence,
            "panelId": panel["panelId"],
            "cardLocationClass": location,
            "sourceToken": token,
            "start": start,
            "end": end,
            "semanticReferenceId": semantic,
            "mappingStatus": "source-scoped-corpus-token" if semantic else "literal-source-local-no-match",
            "mappingScope": f"exact source occurrence {prefix} only",
            "selectedEvidence": selected_evidence,
        })
    return rows


def _slot_evidence(text: dict, gmnotes: str, licensed_candidates: list[dict]) -> dict:
    lower = text.get("lowerCenter") or ""
    resolved = []
    for token in re.findall(r"(?:^|\[)(ammoSlot|grenadeSlot|oxygenSlot|medpackSlot|anySlot)(?:\]|$)", lower):
        resolved.append({"semanticReferenceId": f"icon.{token}", "basis": "tracked human-reviewed/corpus lower-center source occurrence"})
    return {
        "sourceResolvedSlotOccurrences": resolved,
        "sourceResolvedSlotCount": len(resolved),
        "ttsGmNotesLiteral": gmnotes,
        "ttsGmNotesRole": "corroboration-only; never authority over printed pixels",
        "licensedCandidates": [{"key": row["key"], "slots": row["slots"], "identityCrosswalkAsserted": False} for row in licensed_candidates],
        "unresolvedWhenPixelsNotMatched": not bool(resolved) and bool(gmnotes or any(row["slots"] for row in licensed_candidates)),
        "colorTitleArtOrientationInferenceUsed": False,
    }


def _support_rule_id(card_id: int, guid: str) -> str:
    return f"SEM-SUPPORT-EQUIPMENT-{card_id}-{guid.upper()}-001"


def _character_rule_id(character: str, card_id: int, guid: str) -> str:
    return f"SEM-CHARACTER-ITEM-{CHARACTER_CODES[character]}-{card_id}-{guid.upper()}-001"


def build_equipment_source_index(repo: Path, green_source: dict, red_source: dict, yellow_source: dict) -> dict:
    raw, raw_sha = _load_raw(repo)
    roles = json.loads((repo / ROLES_PATH).read_text(encoding="utf-8"))
    objects = json.loads((repo / OBJECTS_PATH).read_text(encoding="utf-8"))
    classification = json.loads((repo / CLASSIFICATION_PATH).read_text(encoding="utf-8"))
    manifest = json.loads((repo / MANIFEST_PATH).read_text(encoding="utf-8"))
    provenance = json.loads((repo / PROVENANCE_PATH).read_text(encoding="utf-8"))
    corpus = json.loads((repo / CORPUS_PATH).read_text(encoding="utf-8"))
    selected = json.loads((repo / SELECTED_PATH).read_text(encoding="utf-8"))
    progress = json.loads((repo / PROGRESS_PATH).read_text(encoding="utf-8"))
    backlog = json.loads((repo / BACKLOG_PATH).read_text(encoding="utf-8"))
    faq = json.loads((repo / FAQ_PATH).read_text(encoding="utf-8"))
    visuals = json.loads((repo / VISUAL_PATH).read_text(encoding="utf-8"))

    url_to_path = {row["url"]: "assets/tts-mod/extract/v2-dl/tree/" + row["file"] for row in manifest}
    provenance_by_url = {row["url"]: row for row in provenance}
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    selected_by_path = {row["sourcePath"]: row for row in selected["entries"]}
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    classification_by_guid = {row["guid"]: row for row in classification}

    bga_all = _parse_bga_items(repo / BGA_PATH)
    relevant_decks = {"item-support", "item-recon", "item-combat-engineer", "item-heavy-gun", "item-contractor", "item-medical", "item-officer"}
    relevant_keys = {"HeavyOxygenTank", "Medkit", "RemoteDetonator", "MilitaryTaser", "FireExtinguisher", "RobotController"}
    licensed = [row for row in bga_all if row["deck"] in relevant_decks or row["key"] in relevant_keys]
    if len(bga_all) != 57 or len(licensed) != 37:
        raise AssertionError("licensed Equipment/Starting/Heavy row boundary changed")
    licensed_by_normalized_title: dict[str, list[dict]] = {}
    for row in licensed:
        key = re.sub(r"[^a-z0-9]", "", (row.get("name") or "").lower())
        licensed_by_normalized_title.setdefault(key, []).append(row)

    support_role = [row for row in roles if row.get("role") == "startItemDeck"]
    if len(support_role) != 1 or support_role[0].get("guid") != SUPPORT_ROOT_GUID or support_role[0].get("type") != "DeckCustom" or support_role[0].get("contained") != 1:
        raise AssertionError("Support Equipment Lua root role changed")
    root = _find_guid(raw.get("ObjectStates"), SUPPORT_ROOT_GUID)
    if not isinstance(root, dict) or root.get("Name") != "DeckCustom":
        raise AssertionError("Support Equipment raw root missing")
    contained = _list_values(root.get("ContainedObjects"))
    root_custom = root.get("CustomDeck") or {}
    expected_children = [(row[1], row[2]) for row in _SUPPORT_ROWS]
    actual_children = [(int(row["CardID"]), row["GUID"]) for row in contained]
    deck_ids = [int(value) for value in _list_values(root.get("DeckIDs"))]
    if actual_children != expected_children or deck_ids != [row[0] for row in expected_children] or len(root_custom) != 23:
        raise AssertionError("Support Equipment exact root members/order changed")
    if classification_by_guid[SUPPORT_ROOT_GUID].get("verdict") != "base" or any(classification_by_guid[guid].get("verdict") != "base" for _, guid in expected_children):
        raise AssertionError("Support Equipment base classification changed")

    root_by_tuple = {(int(row["CardID"]), row["GUID"]): row for row in contained}
    support_faces = []
    selected_support_paths = set()
    for sequence, card_id, guid, custom_id, source_path, cell, physical_class, effect_kind in _SUPPORT_ROWS:
        child = root_by_tuple[(card_id, guid)]
        custom = root_custom[custom_id]
        parent_path = url_to_path.get(custom.get("FaceURL"))
        expected_parent = SUPPORT_SHEET_PATH if cell is not None else source_path
        if parent_path != expected_parent or custom.get("BackURL") != SUPPORT_BACK_URL:
            raise AssertionError(f"Support Equipment FaceURL/BackURL path drift: {card_id}-{guid}")
        if cell is not None:
            generated = (progress_by_path.get(source_path) or {}).get("generatedFrom") or {}
            if generated != {"sourceSheetPath": SUPPORT_SHEET_PATH, "cellIndex": cell} or custom.get("NumWidth") != 6 or custom.get("NumHeight") != 3 or custom.get("FaceURL") != SUPPORT_SHEET_URL:
                raise AssertionError(f"Support Equipment explicit generated-cell selector drift: {card_id}-{guid}")
        else:
            generated = (progress_by_path.get(source_path) or {}).get("generatedFrom") or {}
            if generated.get("sourceSheetPath") is not None or generated.get("cellIndex") is not None:
                raise AssertionError(f"Support Equipment direct/generated inversion: {card_id}-{guid}")
        corpus_row = corpus_by_path.get(source_path) or {}
        corpus_ready = (
            corpus_row.get("sourceSha256") == _sha(repo / source_path)
            and (
                (corpus_row.get("rulesTextPresent") and corpus_row.get("extractionState") in {"verified-canonical", "draft-full"})
                or (
                    effect_kind == "utility-vest"
                    and corpus_row.get("extractionState") == "non-rules-or-reference"
                    and (corpus_row.get("printedData") or {}).get("body") == ""
                )
            )
        )
        if not corpus_ready:
            raise AssertionError(f"Support Equipment closed-corpus readiness drift: {source_path}")
        text = _source_text(source_path, corpus_row, selected_by_path.get(source_path))
        code = f"SUP-{card_id}-{guid.upper()}"
        panels = _body_panels(text, code)
        sentences = _sentences(text, panels, code)
        icons = _icons(text, selected_by_path.get(source_path), panels, code)
        title_key = re.sub(r"[^a-z0-9]", "", text["printedTitle"].lower())
        bga_candidates = licensed_by_normalized_title.get(title_key, [])
        backlog_id = "CARD:" + corpus_row["sourceSha256"][:16] if corpus_row.get("rulesTextPresent") else None
        backlog_row = backlog_by_id.get(backlog_id) or {}
        if backlog_id and (backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != corpus_row["sourceSha256"]):
            raise AssertionError(f"Support Equipment exact backlog tuple missing: {source_path}")
        occurrence_id = f"TTS-SUPPORT-EQUIPMENT-{card_id}-{guid.upper()}-FACE"
        source_id = f"SRC-EQUIPMENT-SUPPORT-{card_id}-{guid.upper()}"
        support_faces.append({
            "supportEquipmentOccurrenceId": occurrence_id,
            "copyId": f"BASE-SUPPORT-EQUIPMENT-COPY-{sequence:02d}",
            "rootSequence": sequence,
            "ttsRole": "startItemDeck",
            "ttsRootGuid": SUPPORT_ROOT_GUID,
            "ttsRootType": root.get("Name"),
            "ttsCardId": card_id,
            "ttsCardGuid": guid,
            "customDeckId": custom_id,
            "ttsObjectDescription": child.get("Description") or "",
            "ttsGmNotes": child.get("GMNotes") or "",
            "sourceId": source_id,
            "sourcePath": source_path,
            "sourceSha256": corpus_row["sourceSha256"],
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS source-bound base Support Equipment root occurrence {sequence} / full CardID {card_id} / GUID {guid}",
            "sourceSelector": {
                "key": "FaceURL",
                "objectType": child.get("Name"),
                "fullCardId": card_id,
                "guid": guid,
                "parentDeckGuid": SUPPORT_ROOT_GUID,
                "customDeckId": custom_id,
                "url": custom.get("FaceURL"),
                "backUrl": custom.get("BackURL"),
                "sideRole": "operative-support-equipment-face",
                "generatedSpriteSheetCell": cell is not None,
                "sourceSheetPath": SUPPORT_SHEET_PATH if cell is not None else None,
                "sourceSheetSha256": _sha(repo / SUPPORT_SHEET_PATH) if cell is not None else None,
                "sourceSheetGrid": {"columns": 6, "rows": 3, "cellWidth": 591, "cellHeight": 863} if cell is not None else None,
                "generatedCell": cell,
                "selectorGap": None,
                "cardIdModuloJoinUsed": False,
            },
            "physicalClass": physical_class,
            "itemSourceClass": "support-equipment",
            "effectKind": effect_kind,
            "semanticRuleId": _support_rule_id(card_id, guid),
            **text,
            "panels": panels,
            "sentences": sentences,
            "iconOccurrences": icons,
            "dedicatedTrackOccurrences": [],
            "tacticalGearSlotEvidence": _slot_evidence(text, child.get("GMNotes") or "", bga_candidates),
            "backlogUnitId": backlog_id,
            "licensedVariantCandidates": [{**row, "assertedTtsPhysicalIdentityLinks": []} for row in bga_candidates],
            "officialPhysicalCrosswalk": {"status": "not-asserted", "reason": "current official visible examples do not identify this TTS full CardID/GUID physical copy"},
            "identityJoinEvidence": {
                "identityJoin": "exact raw root physical occurrence and exact source-asset projection",
                "titleOnlyJoin": False,
                "bodySimilarityJoin": False,
                "colorOnlyJoin": False,
                "orientationOnlyJoin": False,
                "gmNotesOnlyJoin": False,
                "folderOnlyJoin": False,
                "sourceOrderOnlyJoin": False,
                "sourceSheetOnlyJoin": False,
                "generatedCellOnlyJoin": False,
                "cardIdModuloJoin": False,
                "licensedKeyJoin": False,
                "officialTitleJoin": False,
                "basis": [
                    "sole base startItemDeck Lua role and exact raw root GUID",
                    "raw saved full CardID/GUID occurrence and parent container",
                    "exact CustomDeck ID, FaceURL, BackURL, source path, and SHA-256",
                    "for two generated faces only: explicit full CardID-to-sheet/hash/grid/cell crosswalk",
                ],
            },
            "printedBodyDigest": _digest({"title": text["printedTitle"], "typeLine": text["typeLine"], "upperRight": text["upperRight"], "body": text["printedBody"]}),
            "panelDigest": _digest(panels),
            "iconDigest": _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in icons]),
        })
        selected_support_paths.add(source_path)

    # The parent 6x3 sheet is a source asset, never a rules face. All sixteen
    # unselected cells remain source variants with their own exact corpus tuples.
    support_assets = []
    generated_paths = []
    for cell in range(18):
        path = f"assets/tts-mod/extract/v2-dl/tree/cards/game/startItemDeck-144_cards/card-{cell:02d}.png"
        generated_paths.append(path)
        row = corpus_by_path.get(path) or {}
        if not row.get("rulesTextPresent") or row.get("sourceSha256") != _sha(repo / path):
            raise AssertionError(f"Support Equipment generated cell corpus drift: {cell}")
        text = _source_text(path, row, selected_by_path.get(path))
        selected_faces = [face for face in support_faces if face["sourcePath"] == path]
        source_id = None if selected_faces else f"SRC-EQUIPMENT-SUPPORT-GAP-29-CELL-{cell:02d}"
        panels = _body_panels(text, f"SUP-ASSET-29-{cell:02d}")
        icons = _icons(text, selected_by_path.get(path), panels, f"SUP-ASSET-29-{cell:02d}")
        support_assets.append({
            "assetId": f"SUPPORT-ASSET-SHEET-29-CELL-{cell:02d}",
            "sourceId": source_id,
            "sourcePath": path,
            "sourceSha256": row["sourceSha256"],
            "sourceRole": "generated-selected-support-face" if selected_faces else "generated-selector-gap-variant",
            "sourceSheetId": SUPPORT_SHEET_SOURCE_ID,
            "sourceSheetPath": SUPPORT_SHEET_PATH,
            "sourceSheetSha256": _sha(repo / SUPPORT_SHEET_PATH),
            "sourceSheetGrid": {"columns": 6, "rows": 3, "cellWidth": 591, "cellHeight": 863},
            "customDeckId": "29",
            "generatedCell": cell,
            "selectedPhysicalOccurrenceIds": [face["supportEquipmentOccurrenceId"] for face in selected_faces],
            "selectorGap": None if selected_faces else {"status": "explicit-no-root-full-CardID-GUID-selector", "cardIdModuloJoinUsed": False},
            "backlogUnitId": "CARD:" + row["sourceSha256"][:16] if row.get("rulesTextPresent") else None,
            **text,
            "panels": panels,
            "sentences": _sentences(text, panels, f"SUP-ASSET-29-{cell:02d}"),
            "iconOccurrences": icons,
        })
    for face in support_faces:
        if face["sourceSelector"]["generatedSpriteSheetCell"]:
            continue
        row = corpus_by_path[face["sourcePath"]]
        support_assets.append({
            "assetId": f"SUPPORT-ASSET-DIRECT-{face['rootSequence']:02d}",
            "sourceId": None,
            "sourcePath": face["sourcePath"],
            "sourceSha256": face["sourceSha256"],
            "sourceRole": "direct-selected-support-face",
            "sourceSheetId": None,
            "sourceSheetPath": None,
            "sourceSheetSha256": None,
            "sourceSheetGrid": None,
            "customDeckId": face["customDeckId"],
            "generatedCell": None,
            "selectedPhysicalOccurrenceIds": [face["supportEquipmentOccurrenceId"]],
            "selectorGap": None,
            "backlogUnitId": "CARD:" + row["sourceSha256"][:16] if row.get("rulesTextPresent") else None,
            **{key: face[key] for key in ("printedTitle", "typeLine", "printedBody", "upperRight", "lowerCenter", "selectedVisibleText", "selectedEvidenceRunIdentity", "representationBoundary", "panels", "sentences", "iconOccurrences")},
        })
    support_assets.sort(key=lambda row: (row["sourceSheetPath"] is None, row["generatedCell"] if row["generatedCell"] is not None else row["assetId"]))

    with Image.open(repo / SUPPORT_SHEET_PATH) as parent:
        if parent.size != (3546, 2589):
            raise AssertionError("Support Equipment 6x3 parent sheet dimensions changed")
        for cell, path in enumerate(generated_paths):
            row_index, column_index = divmod(cell, 6)
            crop = parent.crop((column_index * 591, row_index * 863, (column_index + 1) * 591, (row_index + 1) * 863)).convert("RGB")
            with Image.open(repo / path) as generated:
                if generated.convert("RGB").tobytes() != crop.tobytes():
                    raise AssertionError(f"Support Equipment generated-cell pixel drift: {cell}")

    # Exact TTS kit membership is source-local provenance. Two explicitly
    # audited prototype/current-authority conflicts remain indexed exclusions;
    # the other five readable TTS faces receive source-variant semantics without
    # claiming that their kit ownership is the complete current official roster.
    character_faces = []
    character_backs: dict[str, dict] = {}
    for character, guid, card_id, source_path, physical_class, effect_kind, disposition in _CHARACTER_ROWS:
        raw_face = _find_guid(raw.get("ObjectStates"), guid)
        if not isinstance(raw_face, dict):
            raise AssertionError(f"Character Item raw face missing: {guid}")
        parent = next((row for row in objects if row.get("guid") == guid), {})
        expected_parent = ["Bag", CHARACTER_BAGS[character], character]
        if expected_parent not in (parent.get("parent") or []) or classification_by_guid[guid].get("verdict") != "base":
            raise AssertionError(f"Character Item kit ancestry/base classification changed: {guid}")
        custom = raw_face.get("CustomDeck") or {}
        if len(custom) != 1:
            raise AssertionError(f"Character Item CustomDeck selector changed: {guid}")
        custom_id, custom_row = next(iter(custom.items()))
        if url_to_path.get(custom_row.get("FaceURL")) != source_path:
            raise AssertionError(f"Character Item FaceURL path drift: {guid}")
        back_path = url_to_path.get(custom_row.get("BackURL"))
        if not back_path:
            raise AssertionError(f"Character Item BackURL path missing: {guid}")
        corpus_row = corpus_by_path.get(source_path) or {}
        if not corpus_row.get("rulesTextPresent") or corpus_row.get("sourceSha256") != _sha(repo / source_path):
            raise AssertionError(f"Character Item corpus/hash drift: {guid}")
        text = _source_text(source_path, corpus_row, selected_by_path.get(source_path))
        code = f"CHAR-{CHARACTER_CODES[character]}-{card_id}-{guid.upper()}"
        panels = _body_panels(text, code)
        icons = _icons(text, selected_by_path.get(source_path), panels, code)
        title_key = re.sub(r"[^a-z0-9]", "", text["printedTitle"].lower())
        bga_candidates = licensed_by_normalized_title.get(title_key, [])
        semantic_rule_id = _character_rule_id(character, card_id, guid) if disposition == "source-clear-tts-character-kit-variant" else None
        backlog_id = "CARD:" + corpus_row["sourceSha256"][:16]
        if (backlog_by_id.get(backlog_id) or {}).get("sourcePath") != source_path:
            raise AssertionError(f"Character Item exact backlog tuple missing: {guid}")
        occurrence_id = f"TTS-CHARACTER-ITEM-{CHARACTER_CODES[character]}-{card_id}-{guid.upper()}-FACE"
        source_id = f"SRC-EQUIPMENT-CHARACTER-{CHARACTER_CODES[character]}-{card_id}-{guid.upper()}"
        character_faces.append({
            "characterItemOccurrenceId": occurrence_id,
            "copyId": f"TTS-CHARACTER-ITEM-{CHARACTER_CODES[character]}-COPY-{sum(row[0] == character for row in _CHARACTER_ROWS[:_CHARACTER_ROWS.index((character, guid, card_id, source_path, physical_class, effect_kind, disposition)) + 1]):02d}",
            "ttsCharacterKitOwner": character,
            "ttsCharacterBagGuid": CHARACTER_BAGS[character],
            "ttsCardId": card_id,
            "ttsCardGuid": guid,
            "customDeckId": custom_id,
            "ttsObjectDescription": raw_face.get("Description") or "",
            "ttsGmNotes": raw_face.get("GMNotes") or "",
            "sourceId": source_id,
            "sourcePath": source_path,
            "sourceSha256": corpus_row["sourceSha256"],
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS source-bound Character kit occurrence / {character} bag {CHARACTER_BAGS[character]} / full CardID {card_id} / GUID {guid}",
            "sourceSelector": {
                "key": "FaceURL",
                "objectType": raw_face.get("Name"),
                "fullCardId": card_id,
                "guid": guid,
                "parentBagGuid": CHARACTER_BAGS[character],
                "customDeckId": custom_id,
                "url": custom_row.get("FaceURL"),
                "backUrl": custom_row.get("BackURL"),
                "sideRole": "operative-character-item-face",
                "generatedSpriteSheetCell": False,
                "selectorGap": None,
                "cardIdModuloJoinUsed": False,
            },
            "backPath": back_path,
            "physicalClass": physical_class,
            "itemSourceClass": "character-item",
            "effectKind": effect_kind,
            "batchDisposition": disposition,
            "semanticRuleId": semantic_rule_id,
            **text,
            "panels": panels,
            "sentences": _sentences(text, panels, code),
            "iconOccurrences": icons,
            "dedicatedTrackOccurrences": [],
            "tacticalGearSlotEvidence": _slot_evidence(text, raw_face.get("GMNotes") or "", bga_candidates),
            "backlogUnitId": backlog_id,
            "licensedVariantCandidates": [{**row, "assertedTtsPhysicalIdentityLinks": []} for row in bga_candidates],
            "currentOfficialOwnership": {"status": "resolved-conflict" if guid == "2059a7" else "prototype-excluded" if guid == "427c1a" else "not-established-by-checked-current-official-visible-inventory", "assertedCurrentOwner": "Heavy Gun Operator" if guid == "2059a7" else None},
            "identityJoinEvidence": {
                "identityJoin": "exact raw Character-kit physical occurrence and exact source-asset projection",
                "titleOnlyJoin": False,
                "bodySimilarityJoin": False,
                "characterNameOnlyJoin": False,
                "backLabelOnlyJoin": False,
                "folderOnlyJoin": False,
                "cardIdModuloJoin": False,
                "licensedKeyJoin": False,
                "officialTitleJoin": False,
                "basis": ["exact Character bag GUID/container ancestry", "exact full CardID/GUID/CustomDeck/FaceURL/BackURL tuple", "live source bytes and source-side provenance"],
            },
            "printedBodyDigest": _digest({"title": text["printedTitle"], "typeLine": text["typeLine"], "upperRight": text["upperRight"], "body": text["printedBody"]}),
        })
        if back_path != SUPPORT_BACK_PATH:
            back = character_backs.setdefault(back_path, {
                "sourceId": f"SRC-EQUIPMENT-CHARACTER-BACK-{len(character_backs)+1:02d}",
                "sourcePath": back_path,
                "sourceSha256": _sha(repo / back_path),
                "url": custom_row.get("BackURL"),
                "faceOccurrenceIds": [],
                "globalReferenceCount": (provenance_by_url.get(custom_row.get("BackURL")) or {}).get("refs"),
                "rulesFaceCounted": False,
                "sideRole": "character-item-non-operative-back",
            })
            back["faceOccurrenceIds"].append(occurrence_id)

    # Exact color-root Heavy faces are promoted out of their prior regular-family
    # exclusion sets. Class-conflict faces remain indexed and non-dispatchable.
    color_heavy_faces = []
    for family, rows in (("green", green_source.get("excludedHeavyFaces") or []), ("red", red_source.get("excludedHeavyFaces") or [])):
        for family_sequence, row in enumerate(rows, 1):
            occurrence_id = row[f"{family}ItemOccurrenceId"]
            code = f"{family.upper()}-{row['ttsCardId']}-{row['ttsCardGuid'].upper()}"
            color_heavy_faces.append({
                **row,
                "equipmentOccurrenceId": occurrence_id,
                "copyId": f"BASE-{family.upper()}-ROOT-HEAVY-COPY-{family_sequence:02d}",
                "sourceFamily": f"{family}-item-root-heavy",
                "itemSourceClass": f"{family}-item-root",
                "semanticRuleId": f"SEM-HEAVY-{code}-001",
                "priorBatchDisposition": row.get("batchDisposition"),
                "batchDisposition": "included-source-clear-heavy-item-face",
            })
    class_conflicts = [
        *[{**row, "conflictFamily": "red-military-taser", "semanticDispatchProhibited": True, "questionId": "SEM-Q-047"} for row in red_source.get("physicalClassConflictFaces") or []],
        *[{**row, "conflictFamily": "yellow-fire-extinguisher-or-robot-controller", "semanticDispatchProhibited": True, "questionId": "SEM-Q-052"} for row in yellow_source.get("physicalClassConflictFaces") or []],
    ]

    official_visible = [
        {
            "officialOccurrenceId": "RB-P03-V01-CHARACTER-AUTOMATIC-SHOTGUN",
            "sourceId": "SRC-RULEBOOK",
            "visualUnitId": "RB-P03-V01",
            "itemSourceClass": "character-item",
            "printedOwner": "HEAVY GUN OPERATOR",
            "printedTitle": "AUTOMATIC SHOTGUN",
            "typeLine": "RANGED WEAPON, HEAVY",
            "printedBody": "Shoot: Before Shooting, deal 1 Hit more.\n[shootDieCritical]: Spend [ammoToken] if able.",
            "physicalClass": "ranged-weapon",
            "tacticalGearSlots": [{"slotType": "ammo", "count": 1, "status": "official-visible-component occurrence"}],
            "semanticRuleId": "SEM-CHARACTER-ITEM-OFFICIAL-AUTOMATIC-SHOTGUN-001",
            "authority": "official-primary",
            "ttsPhysicalCrosswalkAsserted": False,
            "evidenceRefs": ["docs/qa/card-source-audits/automatic-shotgun-source-fidelity.md", "docs/rulebooks/rulebook_text.txt:lines 149–156"],
            "backlogUnitId": "VIS:RB-P03-V01",
        },
        {
            "officialOccurrenceId": "RB-P03-V01-SUPPORT-TACTICAL-HATCHET",
            "sourceId": "SRC-RULEBOOK",
            "visualUnitId": "RB-P03-V01",
            "itemSourceClass": "support-equipment",
            "printedOwner": None,
            "printedTitle": "TACTICAL HATCHET",
            "typeLine": "MELEE WEAPON, HEAVY",
            "printedBody": "Melee Attack: Deal [LOCAL_ICON: official isolated result glyph] instead of rolling the Shoot die, and place a [malfunction] on this Weapon.",
            "physicalClass": "melee-weapon",
            "tacticalGearSlots": [],
            "semanticRuleId": "SEM-SUPPORT-OFFICIAL-TACTICAL-HATCHET-001",
            "authority": "official-primary",
            "ttsPhysicalCrosswalkAsserted": False,
            "evidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 157–162"],
            "backlogUnitId": "VIS:RB-P03-V01",
        },
        {
            "officialOccurrenceId": "RB-P03-V01-CHARACTER-SONIC-GUN",
            "sourceId": "SRC-RULEBOOK",
            "visualUnitId": "RB-P03-V01",
            "itemSourceClass": "character-item",
            "printedOwner": "RECON",
            "printedTitle": "SONIC GUN",
            "typeLine": "RANGED WEAPON, REQUIRES NO AMMO, HEAVY",
            "printedBody": "Burst: Treat [burstDie3] and [burstDie4] as [burstDie2].\n[burstDieAdditionalEffects], [shootDieAmmoLoss]: Place a [malfunction] in your Room.",
            "physicalClass": "ranged-weapon",
            "tacticalGearSlots": [],
            "semanticRuleId": "SEM-CHARACTER-ITEM-OFFICIAL-SONIC-GUN-001",
            "authority": "official-primary",
            "ttsPhysicalCrosswalkAsserted": False,
            "evidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 172–187"],
            "backlogUnitId": "VIS:RB-P03-V01",
        },
        {
            "officialOccurrenceId": "RB-P29-V01-MILITARY-TASER",
            "sourceId": "SRC-RULEBOOK",
            "visualUnitId": "RB-P29-V01",
            "itemSourceClass": "color-item-heavy-current-occurrence",
            "printedOwner": None,
            "printedTitle": "MILITARY TASER",
            "typeLine": "ONE USE ONLY, HEAVY",
            "printedBody": "Repel 1 [intruder] from the Room.\nOR\nA [character] of your choice discards all [actionCard].",
            "physicalClass": "heavy-item",
            "tacticalGearSlots": [],
            "semanticRuleId": "SEM-HEAVY-OFFICIAL-MILITARY-TASER-001",
            "authority": "official-primary",
            "ttsPhysicalCrosswalkAsserted": False,
            "evidenceRefs": ["docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P29-V01", "docs/rulebooks/rulebook_text.txt:lines 5014–5023"],
            "backlogUnitId": "VIS:RB-P29-V01",
        },
        {
            "officialOccurrenceId": "RB-P29-V02-HEAVY-ARMOR",
            "sourceId": "SRC-RULEBOOK",
            "visualUnitId": "RB-P29-V02",
            "itemSourceClass": "support-equipment",
            "printedOwner": None,
            "printedTitle": "HEAVY ARMOR",
            "typeLine": "ARMOR",
            "printedBody": "Whenever you would gain a Serious Wound, you may lose 2 [characterHealth] instead.",
            "physicalClass": "armor-item",
            "tacticalGearSlots": [{"slotType": "medpack", "count": 1, "status": "official-visible color/type key and attached slot"}],
            "dedicatedTrackOccurrence": {"track": "Character Health track Heavily Injured section", "spacesVisible": 3, "cardPlacedOnTrack": True},
            "semanticRuleId": "SEM-SUPPORT-OFFICIAL-HEAVY-ARMOR-001",
            "authority": "official-primary",
            "ttsPhysicalCrosswalkAsserted": False,
            "evidenceRefs": ["docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P29-V02"],
            "backlogUnitId": "VIS:RB-P29-V02",
        },
        {
            "officialOccurrenceId": "RB-P29-V04-GRENADE-LAUNCHER",
            "sourceId": "SRC-RULEBOOK",
            "visualUnitId": "RB-P29-V04",
            "itemSourceClass": "support-equipment",
            "printedOwner": None,
            "printedTitle": "GRENADE LAUNCHER",
            "typeLine": "RANGED WEAPON, HEAVY",
            "printedBody": "Burst: You may use any number of [grenadeToken] from this Weapon before or instead of a normal Burst.",
            "physicalClass": "ranged-weapon",
            "tacticalGearSlots": [{"slotType": "ammo", "count": 1, "status": "official-visible arrow/caption"}, {"slotType": "grenade", "count": 2, "status": "official-visible arrow/caption"}],
            "semanticRuleId": "SEM-SUPPORT-OFFICIAL-GRENADE-LAUNCHER-001",
            "authority": "official-primary",
            "ttsPhysicalCrosswalkAsserted": False,
            "evidenceRefs": ["docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P29-V04", "docs/rulebooks/rulebook_text.txt:lines 5104–5113"],
            "backlogUnitId": "VIS:RB-P29-V04",
        },
    ]

    faq_by_id = {row["sourceUnitId"]: row for page in faq["pages"] for row in page.get("units", [])}
    faq_ids = ["FQ-P02-U21", "FQ-P03-U01", "FQ-P03-U02", "FQ-P03-U03", "FQ-P03-U04", "FQ-P03-U05", "FQ-P03-U06", "FQ-P03-U07"]
    faq_occurrences = [{"sourceUnitId": qid, "section": faq_by_id[qid]["section"], "applicability": faq_by_id[qid]["applicability"], "printedText": faq_by_id[qid]["printedText"], "visualOccurrences": faq_by_id[qid].get("visualOccurrences") or []} for qid in faq_ids]
    if any(row["applicability"] != "base-game" for row in faq_occurrences):
        raise AssertionError("Equipment FAQ base applicability changed")

    visual_by_id = {row["occurrenceId"]: row for page in visuals["pages"] for row in page.get("visualUnits", [])}
    visual_ids = ["RB-P03-V01", "RB-P05-V01", "RB-P12-V02", "RB-P16-V02", "RB-P16-V03", "RB-P17-V01", "RB-P18-V01", "RB-P29-V01", "RB-P29-V02", "RB-P29-V03", "RB-P29-V04", "RB-P33-V03", "RB-P40-V02"]
    official_visual_occurrences = [{"occurrenceId": occurrence_id, "type": visual_by_id[occurrence_id]["type"], "bbox": visual_by_id[occurrence_id]["bbox"]} for occurrence_id in visual_ids]

    support_back_provenance = provenance_by_url[SUPPORT_BACK_URL]
    support_sheet_provenance = provenance_by_url[SUPPORT_SHEET_URL]
    if support_back_provenance.get("refs") != 72 or support_sheet_provenance.get("refs") != 3:
        raise AssertionError("Support Equipment shared-back/sheet provenance reference counts changed")
    shared_backs = [
        {
            "sourceId": SUPPORT_BACK_SOURCE_ID,
            "occurrenceId": "TTS-EQUIPMENT-SUPPORT-SHARED-BACK",
            "sourcePath": SUPPORT_BACK_PATH,
            "sourceSha256": _sha(repo / SUPPORT_BACK_PATH),
            "url": SUPPORT_BACK_URL,
            "supportRootPhysicalSelectorReferences": 24,
            "characterKitPhysicalSelectorReferences": 2,
            "batchPhysicalSelectorReferences": 26,
            "globalReferenceCount": 72,
            "rulesFaceCounted": False,
            "sideRole": "generic-support-or-character-item-non-operative-back",
        },
        *sorted(character_backs.values(), key=lambda row: row["sourcePath"]),
    ]

    selected_face_assets = {row["sourcePath"] for row in support_faces}
    support_gap_assets = [row for row in support_assets if row["selectorGap"]]
    linked_backlog_ids = set()
    for asset in support_assets:
        if asset["backlogUnitId"]:
            linked_backlog_ids.add(asset["backlogUnitId"])
    for face in character_faces:
        linked_backlog_ids.add(face["backlogUnitId"])
    for face in color_heavy_faces:
        linked_backlog_ids.add(face["backlogUnitId"])
    for face in class_conflicts:
        linked_backlog_ids.add(face["backlogUnitId"])
    linked_backlog_ids.update({"RULE:ITM-001", "RULE:ITM-002", "RULE:ITM-003", "RULE:ITM-004", "RULE:ITM-005", "RULE:ACT-ITEM-001", "RULE:ACT-TRADE-001", "RULE:ACT-SHOOT-001", "RULE:ACT-BURST-001", "RULE:ACT-MELEE-001", "RULE:INT-006", *["FAQ:" + qid for qid in faq_ids], *["VIS:" + occurrence_id for occurrence_id in visual_ids]})
    linked_backlog_ids = sorted(unit_id for unit_id in linked_backlog_ids if unit_id in backlog_by_id)

    title_multiplicity = Counter(face["printedTitle"] for face in support_faces)
    counts = {
        "officialCharacterItemCards": 7,
        "officialSupportEquipmentCards": 24,
        "supportRootPhysicalOccurrences": len(support_faces),
        "supportRootDirectPhysicalOccurrences": sum(face["sourceSelector"]["generatedSpriteSheetCell"] is False for face in support_faces),
        "supportRootGeneratedPhysicalOccurrences": sum(face["sourceSelector"]["generatedSpriteSheetCell"] is True for face in support_faces),
        "supportRootUniquePrintedTitles": len(title_multiplicity),
        "supportRootHeavyPhysicalOccurrences": sum(face["physicalClass"] != "armor-item" for face in support_faces),
        "supportRootArmorPhysicalOccurrences": sum(face["physicalClass"] == "armor-item" for face in support_faces),
        "supportRootWeaponPhysicalOccurrences": sum(face["physicalClass"] in {"ranged-weapon", "melee-weapon"} for face in support_faces),
        "supportRootRangedWeaponPhysicalOccurrences": sum(face["physicalClass"] == "ranged-weapon" for face in support_faces),
        "supportRootMeleeWeaponPhysicalOccurrences": sum(face["physicalClass"] == "melee-weapon" for face in support_faces),
        "supportSourceFaceAssets": len(support_assets),
        "supportSelectedSourceFaceAssets": len(selected_face_assets),
        "supportSelectorGapSourceFaceAssets": len(support_gap_assets),
        "supportParentSheets": 1,
        "supportParentSheetCells": 18,
        "supportSelectedGeneratedCells": 2,
        "supportSharedBacks": 1,
        "supportSharedBackGlobalReferences": 72,
        "characterKitPhysicalOccurrences": len(character_faces),
        "characterKitSourceClearVariantOccurrences": sum(face["semanticRuleId"] is not None for face in character_faces),
        "characterKitPrototypeExclusions": sum(face["semanticRuleId"] is None for face in character_faces),
        "characterKitDistinctBackAssets": len(shared_backs),
        "contractorCharacterItemOccurrences": sum(face["ttsCharacterKitOwner"] == "Contractor" for face in character_faces),
        "greenRootHeavyPhysicalOccurrences": len(green_source.get("excludedHeavyFaces") or []),
        "redRootExplicitHeavyPhysicalOccurrences": len(red_source.get("excludedHeavyFaces") or []),
        "redRootClassConflictPhysicalOccurrences": len(red_source.get("physicalClassConflictFaces") or []),
        "yellowRootClassConflictPhysicalOccurrences": len(yellow_source.get("physicalClassConflictFaces") or []),
        "colorRootHeavySemanticOccurrences": len(color_heavy_faces),
        "classConflictSemanticExclusions": len(class_conflicts),
        "officialVisibleCurrentFaceOccurrences": len(official_visible),
        "officialVisibleCurrentCharacterItemOccurrences": sum(row["itemSourceClass"] == "character-item" for row in official_visible),
        "officialVisibleCurrentSupportOccurrences": sum(row["itemSourceClass"] == "support-equipment" for row in official_visible),
        "officialVisibleCurrentOtherHeavyOccurrences": sum(row["itemSourceClass"] == "color-item-heavy-current-occurrence" for row in official_visible),
        "officialResolvedTacticalGearSlotOccurrences": sum(sum(slot["count"] for slot in row.get("tacticalGearSlots") or []) for row in official_visible),
        "ttsSourceResolvedTacticalGearSlotOccurrences": sum(face["tacticalGearSlotEvidence"]["sourceResolvedSlotCount"] for face in [*support_faces, *character_faces]),
        "ttsSlotEvidenceUnresolvedOccurrences": sum(face["tacticalGearSlotEvidence"]["unresolvedWhenPixelsNotMatched"] for face in [*support_faces, *character_faces]),
        "dedicatedPrintedCardTrackOccurrences": sum(len(face["dedicatedTrackOccurrences"]) for face in [*support_faces, *character_faces]),
        "officialCharacterHealthTrackOccurrences": sum(bool(row.get("dedicatedTrackOccurrence")) for row in official_visible),
        "supportPhysicalPanels": sum(len(face["panels"]) for face in support_faces),
        "supportPrintedSentences": sum(len(face["sentences"]) for face in support_faces),
        "supportFunctionalIconOccurrences": sum(len(face["iconOccurrences"]) for face in support_faces),
        "supportMatchedIconOccurrences": sum(sum(icon["semanticReferenceId"] is not None for icon in face["iconOccurrences"]) for face in support_faces),
        "supportLiteralNoMatchIconOccurrences": sum(sum(icon["semanticReferenceId"] is None for icon in face["iconOccurrences"]) for face in support_faces),
        "characterPhysicalPanels": sum(len(face["panels"]) for face in character_faces),
        "characterPrintedSentences": sum(len(face["sentences"]) for face in character_faces),
        "characterFunctionalIconOccurrences": sum(len(face["iconOccurrences"]) for face in character_faces),
        "licensedRelevantRows": len(licensed),
        "licensedSupportRows": sum(row["deck"] == "item-support" for row in licensed),
        "licensedCharacterRows": sum((row["deck"] or "").startswith("item-") and row["deck"] != "item-support" for row in licensed),
        "licensedColorHeavyOrConflictRows": sum(row["key"] in relevant_keys for row in licensed),
        "licensedDeclaredRelevantCopies": sum(row["nbr"] for row in licensed),
        "baseApplicableFaqOccurrences": len(faq_occurrences),
        "officialRulebookVisualOccurrences": len(official_visual_occurrences),
        "semanticTtsPhysicalFaceRecords": len(support_faces) + sum(face["semanticRuleId"] is not None for face in character_faces) + len(color_heavy_faces),
        "semanticOfficialFaceRecords": len(official_visible),
        "backlogSourceFaceTuples": len({unit_id for unit_id in linked_backlog_ids if unit_id.startswith("CARD:")}),
        "backlogObligationsLinked": len(linked_backlog_ids),
    }

    return {
        "schemaVersion": 1,
        "recordType": "semantic-heavy-equipment-starting-item-source-index",
        "scope": "entire source-clear base Heavy Item, Support Equipment, Weapon, Armor, and Character Item ecosystem at the current source boundary: exact 24-card Support root, seven Character-kit TTS occurrences with two audited prototype exclusions, ten source-clear color-root Heavy occurrences, twelve unresolved Red/Yellow class conflicts retained without semantic dispatch, six current official-visible occurrences, shared backs, parent-sheet variants, FAQ rulings, and thirty-seven independent licensed rows",
        "derivationPolicy": "Derive physical roots and kit members only from global Lua role/GUIDs, exact raw full CardID/GUID/CustomDeck/FaceURL/BackURL/container ancestry, live source hashes, generated sheet/hash/grid/cell selectors, and tracked source/corpus evidence. Never join or classify from title, body resemblance, color, orientation, GMNotes, folder/order/cell, CardID modulo, licensed key/class, aggregate multiplicity, or expected tactics alone. GMNotes and licensed slots remain corroboration/independent variants unless exact printed pixels or an applicable official visible occurrence resolve the proposition.",
        "counts": counts,
        "supportTitleMultiplicity": dict(sorted(title_multiplicity.items())),
        "supportRootEvidence": {
            "sourceId": SUPPORT_ROOT_SOURCE_ID,
            "ttsRole": "startItemDeck",
            "rootGuid": SUPPORT_ROOT_GUID,
            "rootType": root.get("Name"),
            "rawSaveSha256": raw_sha,
            "savedDeckIds": deck_ids,
            "customDeckIds": list(root_custom),
            "fullContainedSelectors": [{"rootSequence": face["rootSequence"], "fullCardId": face["ttsCardId"], "guid": face["ttsCardGuid"], "copyId": face["copyId"], "occurrenceId": face["supportEquipmentOccurrenceId"]} for face in support_faces],
            "setupShuffleRequired": True,
            "savedOrderIsGameplayOrder": False,
        },
        "supportEquipmentFaces": support_faces,
        "supportSourceFaceAssets": support_assets,
        "supportSourceSheet": {
            "sourceId": SUPPORT_SHEET_SOURCE_ID,
            "occurrenceId": "TTS-EQUIPMENT-SUPPORT-PARENT-SHEET-29",
            "sourcePath": SUPPORT_SHEET_PATH,
            "sourceSha256": _sha(repo / SUPPORT_SHEET_PATH),
            "url": SUPPORT_SHEET_URL,
            "customDeckId": "29",
            "grid": {"columns": 6, "rows": 3, "cellWidth": 591, "cellHeight": 863},
            "selectedCells": [10, 17],
            "selectorGapCells": [cell for cell in range(18) if cell not in {10, 17}],
            "globalReferenceCount": 3,
            "parentSheetNotRulesFace": True,
            "cardIdModuloJoinUsed": False,
        },
        "sharedBacks": shared_backs,
        "characterItemTtsFaces": character_faces,
        "colorRootHeavyFaces": color_heavy_faces,
        "physicalClassConflictExclusions": class_conflicts,
        "officialVisibleOccurrences": official_visible,
        "licensedDigitalOccurrences": licensed,
        "faqOccurrences": faq_occurrences,
        "officialRulebookVisualOccurrences": official_visual_occurrences,
        "familyCountEvidence": {
            "official": {"characterItemCards": 7, "supportEquipmentCards": 24, "source": "RB-P03-V01 and setup"},
            "tts": {"supportRootPhysicalOccurrences": 24, "characterKitPhysicalOccurrences": 7, "greenRootHeavy": 7, "redRootExplicitHeavy": 3, "redClassConflicts": 6, "yellowClassConflicts": 6, "rawSaveSha256": raw_sha},
            "licensed": {"supportRows": 24, "characterRows": 7, "colorHeavyOrConflictRows": 6, "assertedPhysicalIdentityLinks": 0},
            "reconciliation": "Official and licensed aggregates reconcile 24 Support Equipment and 7 Character Items, while exact TTS physical ownership/version conflicts remain independent. Green 7 Heavy and Red 3 explicit Heavy enter this batch; six Red and six Yellow class conflicts remain non-dispatchable. Aggregate equality never supplies a copy crosswalk.",
            "backlog": {"linkedUnitIds": linked_backlog_ids, "sourceFaceUnitIds": [unit_id for unit_id in linked_backlog_ids if unit_id.startswith("CARD:")]},
        },
        "fidelityBoundaries": {
            "startingRoster": "Only current official-visible Character Item occurrences establish current owner/text. TTS kit ancestry and licensed deck labels remain source-local variants; BF Gun and the misnested TTS Automatic Shotgun are explicit prototype/current-authority exclusions.",
            "slots": "Exact official slot arrows/captions and tracked source-resolved slot tokens may be semantic. TTS GMNotes letters, colors, title, art, orientation, and BGA slots are never promoted alone.",
            "tracks": "No TTS face in this batch asserts a dedicated health/ammo/durability track. Official Heavy Armor shows placement on the three-space Heavily Injured Health section; Ammo state remains token/slot state, not an invented card durability track.",
            "backs": "Each BackURL is a non-operative side. Generic support and Character labels do not create extra faces or repair current owner identity.",
            "classConflicts": "Six Red Military Taser and six Yellow Fire Extinguisher/Robot Controller root occurrences remain exact class/source conflicts and do not dispatch as Heavy/Equipment faces.",
            "variants": "Direct and sheet same-title faces, official occurrences, licensed rows, and TTS kit/root copies remain independent. No title/body/cell/modulo/aggregate join is used.",
        },
    }


def equipment_source_registry_rows(source_index: dict) -> list[dict]:
    rows = [{
        "sourceId": SUPPORT_ROOT_SOURCE_ID,
        "authority": "source-bound-component-scan",
        "version": "TTS raw base Support Equipment root / startItemDeck / GUID f71196",
        "path": RAW_SAVE_PATH,
        "sha256": source_index["supportRootEvidence"]["rawSaveSha256"],
        "occurrenceId": "TTS-EQUIPMENT-SUPPORT-ROOT",
        "evidenceIndexPath": "docs/rules/semantics/equipment-source-index.json",
        "evidenceRecord": "supportRootEvidence",
        "provenanceIndexPath": ROLES_PATH,
    }]
    for face in source_index["supportEquipmentFaces"]:
        rows.append({
            "sourceId": face["sourceId"],
            "authority": "source-bound-component-scan",
            "version": face["sourceVersion"],
            "path": face["sourcePath"],
            "sha256": face["sourceSha256"],
            "occurrenceId": face["supportEquipmentOccurrenceId"],
            "evidenceIndexPath": CORPUS_PATH,
            "evidenceRecord": face["sourceSha256"],
            "provenanceIndexPath": PROVENANCE_PATH,
        })
    for asset in source_index["supportSourceFaceAssets"]:
        if not asset.get("sourceId"):
            continue
        rows.append({
            "sourceId": asset["sourceId"],
            "authority": "source-bound-component-scan",
            "version": f"TTS Support Equipment parent-sheet selector-gap variant / CustomDeck 29 / cell {asset['generatedCell']}",
            "path": asset["sourcePath"],
            "sha256": asset["sourceSha256"],
            "occurrenceId": f"TTS-EQUIPMENT-SUPPORT-GAP-29-CELL-{asset['generatedCell']:02d}",
            "evidenceIndexPath": CORPUS_PATH,
            "evidenceRecord": asset["sourceSha256"],
            "provenanceIndexPath": PROGRESS_PATH,
        })
    sheet = source_index["supportSourceSheet"]
    rows.append({
        "sourceId": sheet["sourceId"],
        "authority": "source-bound-component-scan",
        "version": "TTS Support Equipment 6x3 parent sheet / CustomDeck 29",
        "path": sheet["sourcePath"],
        "sha256": sheet["sourceSha256"],
        "occurrenceId": sheet["occurrenceId"],
        "evidenceIndexPath": PROGRESS_PATH,
        "evidenceRecord": sheet["sourceSha256"],
        "provenanceIndexPath": PROVENANCE_PATH,
    })
    for face in source_index["characterItemTtsFaces"]:
        rows.append({
            "sourceId": face["sourceId"],
            "authority": "source-bound-component-scan",
            "version": face["sourceVersion"],
            "path": face["sourcePath"],
            "sha256": face["sourceSha256"],
            "occurrenceId": face["characterItemOccurrenceId"],
            "evidenceIndexPath": CORPUS_PATH,
            "evidenceRecord": face["sourceSha256"],
            "provenanceIndexPath": PROVENANCE_PATH,
        })
    for back in source_index["sharedBacks"]:
        rows.append({
            "sourceId": back["sourceId"],
            "authority": "source-bound-component-scan",
            "version": "TTS Equipment/Character Item non-operative BackURL occurrence",
            "path": back["sourcePath"],
            "sha256": back["sourceSha256"],
            "occurrenceId": back.get("occurrenceId") or f"TTS-{back['sourceId'].removeprefix('SRC-')}",
            "evidenceIndexPath": CORPUS_PATH,
            "evidenceRecord": back["sourceSha256"],
            "provenanceIndexPath": PROVENANCE_PATH,
        })
    rows.append({
        "sourceId": BGA_EQUIPMENT_SOURCE_ID,
        "authority": "licensed-digital-secondary",
        "version": "licensed BGA immutable build 260622-1220 / thirty-seven relevant ITEMS_DATA rows",
        "path": BGA_PATH,
        "sha256": _sha(Path(__file__).resolve().parents[1] / BGA_PATH),
        "occurrenceId": "ITEMS_DATA:equipment-heavy-character",
        "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json",
        "evidenceRecord": "ITEMS_DATA",
    })
    unique = {row["sourceId"]: row for row in rows}
    return [unique[source_id] for source_id in sorted(unique)]
