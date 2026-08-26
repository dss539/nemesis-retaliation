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
LUA_PATH = "assets/tts-mod/extract/v2/lua_script.lua"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
PROGRESS_PATH = "assets/tts-mod/extract/vision-progress.json"
SELECTED_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"
BACKLOG_PATH = "docs/rules/semantics/backlog.json"
BGA_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
RULEBOOK_VISUAL_PATH = "docs/rules/source-extraction/rulebook-visual-obligations.json"
FAQ_PATH = "docs/rules/source-extraction/faq-v1.2-source-extraction.json"

SHARED_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/action/back.jpg"
SHARED_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/10207952820401286363/045849F3D9E78090494EBF29460723DFD3BF642F/"
SHEET_5674_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045.jpg"
SHEET_5674_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880241742/F6B1605A2ED018B39F0BE82DD120FBFC08C5EF65/"
SHEET_5675_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/action-154.jpg"
SHEET_5675_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880240500/27D0366F2E56321E3F0B9AFD749D346CFE98D400/"

CHARACTER_CODES = {
    "Combat Engineer": "CE",
    "Heavy Gun Operator": "HGO",
    "Medical Support": "MS",
    "Contractor": "CON",
    "Officer": "OFF",
    "Recon": "REC",
}

# These exact kit/deck roots are mechanical TTS provenance. Contractor's final
# base deck is the union of its five-card kit root and the five-card Shared
# Contractor root; the official rulebook independently says to ignore the two
# printed Contractor labels in the base game.
DECK_ROOTS = [
    ("Combat Engineer", "CE", "284e9d", "d7e854", "character-kit"),
    ("Heavy Gun Operator", "HGO", "6219a2", "c8f207", "character-kit"),
    ("Medical Support", "MS", "79d6b1", "1edb6c", "character-kit"),
    ("Contractor", "CON", "47658d", "18a2ab", "character-kit"),
    ("Contractor", "CON", None, "6855bb", "shared-contractor"),
    ("Officer", "OFF", "6031da", "8b2d1b", "character-kit"),
    ("Recon", "REC", "8a007f", "a8e6a4", "character-kit"),
]

# Character, root deck, segment, root-local saved sequence, full CardID, GUID,
# exact selected source asset, exact generated cell (if any), semantic effect
# kind. This is an explicit reviewed selector crosswalk; no title, folder, cell,
# source order alone, or CardID modulo computation supplies identity.
_PHYSICAL_ROWS = [
    ("Combat Engineer", "d7e854", "character-kit", 1, 592400, "164b84", "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-031.png", None, "demolition"),
    ("Combat Engineer", "d7e854", "character-kit", 2, 567424, "b5ee2b", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-24.png", 24, "fast-repairs"),
    ("Combat Engineer", "d7e854", "character-kit", 3, 567428, "84096b", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-28.png", 28, "secure-no-cost"),
    ("Combat Engineer", "d7e854", "character-kit", 4, 567426, "e4355b", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-26.png", 26, "rest"),
    ("Combat Engineer", "d7e854", "character-kit", 5, 567427, "20f4e2", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-27.png", 27, "search"),
    ("Combat Engineer", "d7e854", "character-kit", 6, 568800, "4907b2", "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-010.png", None, "explosives"),
    ("Combat Engineer", "d7e854", "character-kit", 7, 569000, "1892a7", "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-034.png", None, "tactical-retreat"),
    ("Combat Engineer", "d7e854", "character-kit", 8, 569100, "750970", "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-020.png", None, "pyrotechnics"),
    ("Combat Engineer", "d7e854", "character-kit", 9, 569300, "28d06b", "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-027.png", None, "computer-skills"),
    ("Combat Engineer", "d7e854", "character-kit", 10, 569400, "774d62", "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-017.png", None, "chain-command-reaction"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 1, 592400, "b36ef3", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-030.png", None, "demolition"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 2, 567414, "320528", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-14.png", 14, "fast-reload"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 3, 567416, "12b5c5", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-16.png", 16, "repairs"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 4, 567417, "650559", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-17.png", 17, "rest"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 5, 567418, "32b36f", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-18.png", 18, "search"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 6, 570300, "461dc0", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-003.png", None, "secure"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 7, 570500, "f97ad0", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-035.png", None, "continuous-fire"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 8, 570600, "03260a", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-002.png", None, "forcing-fire"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 9, 570800, "f30901", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-005.png", None, "breakthrough"),
    ("Heavy Gun Operator", "c8f207", "character-kit", 10, 570700, "ae6bc0", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-018.png", None, "chain-command-reaction"),
    ("Medical Support", "1edb6c", "character-kit", 1, 570400, "d17c81", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-023.jpg", None, "field-surgery"),
    ("Medical Support", "1edb6c", "character-kit", 2, 569400, "962ad8", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-050.jpg", None, "chain-command-reaction"),
    ("Medical Support", "1edb6c", "character-kit", 3, 569500, "7654b2", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-039.jpg", None, "secure"),
    ("Medical Support", "1edb6c", "character-kit", 4, 569600, "1864bb", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-047.jpg", None, "search"),
    ("Medical Support", "1edb6c", "character-kit", 5, 569700, "49120b", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-022.jpg", None, "rest-medical"),
    ("Medical Support", "1edb6c", "character-kit", 6, 569800, "1688a1", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-048.jpg", None, "repairs-accessible"),
    ("Medical Support", "1edb6c", "character-kit", 7, 569900, "cd0684", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-040.jpg", None, "hippocratic-oath"),
    ("Medical Support", "1edb6c", "character-kit", 8, 570000, "3e472f", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-028.jpg", None, "first-aid"),
    ("Medical Support", "1edb6c", "character-kit", 9, 570200, "176bdb", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-049.jpg", None, "demolition"),
    ("Medical Support", "1edb6c", "character-kit", 10, 570300, "239acd", "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-033.jpg", None, "combat-drugs"),
    ("Contractor", "18a2ab", "character-kit", 1, 567514, "35d06d", "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-003.png", 14, "weak-spots"),
    ("Contractor", "18a2ab", "character-kit", 2, 571000, "b27c01", "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-004.jpg", None, "computer-skills"),
    ("Contractor", "18a2ab", "character-kit", 3, 570600, "d30470", "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-026.jpg", None, "duck-and-cover"),
    ("Contractor", "18a2ab", "character-kit", 4, 570700, "e2ef18", "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-029.jpg", None, "move-quietly"),
    ("Contractor", "18a2ab", "character-kit", 5, 570800, "8c77fb", "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-053.png", None, "always-prepared"),
    ("Officer", "8b2d1b", "character-kit", 1, 567436, "56d897", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-36.png", 36, "rest"),
    ("Officer", "8b2d1b", "character-kit", 2, 567600, "ecd451", "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-009.png", None, "secure"),
    ("Officer", "8b2d1b", "character-kit", 3, 567800, "961585", "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-014.png", None, "fire-at-will"),
    ("Officer", "8b2d1b", "character-kit", 4, 567900, "96dbdb", "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-037.png", None, "officer-channel"),
    ("Officer", "8b2d1b", "character-kit", 5, 568000, "5a4763", "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-015.png", None, "stay-calm-reaction"),
    ("Officer", "8b2d1b", "character-kit", 6, 567435, "017d60", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-35.png", 35, "repairs"),
    ("Officer", "8b2d1b", "character-kit", 7, 567437, "7909aa", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-37.png", 37, "search"),
    ("Officer", "8b2d1b", "character-kit", 8, 567433, "5d3e97", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-33.png", 33, "lets-go"),
    ("Officer", "8b2d1b", "character-kit", 9, 567700, "1325b4", "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-016.png", None, "chain-command"),
    ("Officer", "8b2d1b", "character-kit", 10, 592400, "bbd2b9", "assets/tts-mod/extract/v2-dl/tree/cards/character/officer-001.png", None, "demolition"),
    ("Recon", "a8e6a4", "character-kit", 1, 592400, "8af78a", "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-051.png", None, "demolition"),
    ("Recon", "a8e6a4", "character-kit", 2, 567403, "83078c", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-03.png", 3, "repairs"),
    ("Recon", "a8e6a4", "character-kit", 3, 567406, "59dea3", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-06.png", 6, "search"),
    ("Recon", "a8e6a4", "character-kit", 4, 567404, "62092f", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-04.png", 4, "rest"),
    ("Recon", "a8e6a4", "character-kit", 5, 568600, "662fa5", "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-006.png", None, "sprint"),
    ("Recon", "a8e6a4", "character-kit", 6, 568700, "d711d5", "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-036.png", None, "shoot-first"),
    ("Recon", "a8e6a4", "character-kit", 7, 568900, "443817", "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-007.png", None, "secure"),
    ("Recon", "a8e6a4", "character-kit", 8, 569000, "06bd33", "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-019.png", None, "chain-command-reaction"),
    ("Recon", "a8e6a4", "character-kit", 9, 599300, "83c5b5", "assets/tts-mod/extract/v2-dl/tree/cards/character/recon-043.png", None, "scouting"),
    ("Recon", "a8e6a4", "character-kit", 10, 567409, "bb47f4", "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-09.png", 9, "taking-aim"),
    ("Contractor", "6855bb", "shared-contractor", 1, 567513, "f809a3", "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-002.png", 13, "basic-secure"),
    ("Contractor", "6855bb", "shared-contractor", 2, 567512, "a8c697", "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-001.png", 12, "search"),
    ("Contractor", "6855bb", "shared-contractor", 3, 567511, "46e6c0", "assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png", 11, "rest"),
    ("Contractor", "6855bb", "shared-contractor", 4, 571000, "ad29b5", "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-135.png", None, "demolition"),
    ("Contractor", "6855bb", "shared-contractor", 5, 567510, "10707c", "assets/tts-mod/extract/v2-dl/tree/cards/game/action/repairs.png", 10, "repairs"),
]

EXISTING_SOURCE_IDS_BY_PATH = {
    "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-026.jpg": "SRC-CARD-DUCK",
    "assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png": "SRC-CARD-REST",
    "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-022.jpg": "SRC-CARD-REST-MEDICAL",
    "assets/tts-mod/extract/v2-dl/tree/cards/character/medical-support-047.jpg": "SRC-CARD-SEARCH-MEDICAL",
}


def _code(character: str, card_id: int, guid: str) -> str:
    return f"{CHARACTER_CODES[character]}-{card_id}-{guid.upper()}"


def _rule_id(character: str, card_id: int, guid: str) -> str:
    return f"SEM-ACTION-{_code(character, card_id, guid)}-001"


def _reaction_rule_id(character: str, card_id: int, guid: str) -> str:
    return f"SEM-ACTION-REACTION-{_code(character, card_id, guid)}-001"


def _source_id(character: str, card_id: int, guid: str, path: str) -> str:
    return EXISTING_SOURCE_IDS_BY_PATH.get(path, f"SRC-ACTION-{_code(character, card_id, guid)}")


def _definition(row: tuple) -> dict:
    character, deck_guid, segment, sequence, card_id, guid, source_path, cell, effect_kind = row
    return {
        "character": character,
        "characterCode": CHARACTER_CODES[character],
        "deckGuid": deck_guid,
        "deckSegment": segment,
        "rootSequence": sequence,
        "ttsCardId": card_id,
        "ttsCardGuid": guid,
        "sourcePath": source_path,
        "generatedCell": cell,
        "effectKind": effect_kind,
        "semanticRuleId": _rule_id(character, card_id, guid),
        "reactionRuleId": _reaction_rule_id(character, card_id, guid) if effect_kind in {"chain-command-reaction", "stay-calm-reaction"} else ("SEM-REACTION-DUCK-001" if effect_kind == "duck-and-cover" else None),
        "sourceId": _source_id(character, card_id, guid, source_path),
        "occurrenceId": f"TTS-ACTION-{_code(character, card_id, guid)}-FACE",
        "copyId": None,
        "characterDeckId": f"BASE-ACTION-DECK-{CHARACTER_CODES[character]}",
    }


PHYSICAL_DEFINITIONS = [_definition(row) for row in _PHYSICAL_ROWS]
for character in CHARACTER_CODES:
    character_rows = [row for row in PHYSICAL_DEFINITIONS if row["character"] == character]
    character_rows.sort(key=lambda row: (row["deckSegment"] == "shared-contractor", row["rootSequence"]))
    for index, row in enumerate(character_rows, 1):
        row["copyId"] = f"{row['characterDeckId']}-COPY-{index:02d}"

ACTION_RULE_IDS = [
    row["semanticRuleId"]
    for _, _, _, deck_guid, _ in DECK_ROOTS
    for row in sorted((item for item in PHYSICAL_DEFINITIONS if item["deckGuid"] == deck_guid), key=lambda item: item["rootSequence"])
]
ACTION_REACTION_RULE_IDS = [row["reactionRuleId"] for row in PHYSICAL_DEFINITIONS if row["reactionRuleId"]]
ACTION_REACTION_DISPATCH_RULE_IDS = ["SEM-REACTION-DUCK-001", *[row for row in ACTION_REACTION_RULE_IDS if row != "SEM-REACTION-DUCK-001"]]
ACTION_REUSABLE_RULE_IDS = [
    "SEM-ACTION-DECK-SETUP-001",
    "SEM-ACTION-CARD-PLAY-001",
    "SEM-ACTION-CARD-PAYMENT-001",
    "SEM-ACTION-CARD-REACTION-001",
    "SEM-ACTION-CARD-COMMAND-001",
    "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001",
]


def _rules_for(*effect_kinds: str) -> list[str]:
    return [row["semanticRuleId"] for row in PHYSICAL_DEFINITIONS if row["effectKind"] in set(effect_kinds)]


# Exact selected generated occurrences whose upper-right morphology lacks an
# approved source-scoped denotation. These are deliberately not inferred from
# the licensed noIntruders boolean.
NIC_UNRESOLVED_RULE_IDS = [
    _rule_id("Combat Engineer", 567424, "b5ee2b"),
    _rule_id("Combat Engineer", 567428, "84096b"),
    _rule_id("Combat Engineer", 567427, "20f4e2"),
    _rule_id("Heavy Gun Operator", 567416, "12b5c5"),
    _rule_id("Heavy Gun Operator", 567418, "32b36f"),
    _rule_id("Officer", 567437, "7909aa"),
    _rule_id("Officer", 567433, "5d3e97"),
    _rule_id("Recon", 567406, "59dea3"),
]
SEARCH_LOCAL_RULE_IDS = [
    row["semanticRuleId"] for row in PHYSICAL_DEFINITIONS
    if row["effectKind"] == "search" and row["character"] != "Medical Support"
]
CHAIN_REACTION_RULE_IDS = [
    row["reactionRuleId"] for row in PHYSICAL_DEFINITIONS
    if row["effectKind"] == "chain-command-reaction"
]

ACTION_QUESTION_BLOCKS = {
    "SEM-Q-057": NIC_UNRESOLVED_RULE_IDS,
    "SEM-Q-058": SEARCH_LOCAL_RULE_IDS,
    "SEM-Q-059": ["SEM-ACTION-CARD-COMMAND-001", *_rules_for("chain-command", "chain-command-reaction", "fire-at-will", "officer-channel", "stay-calm-reaction")],
    "SEM-Q-060": ["SEM-ACTION-CARD-REACTION-001", "SEM-REACTION-DUCK-001", *[row for row in ACTION_REACTION_RULE_IDS if row != "SEM-REACTION-DUCK-001"]],
    "SEM-Q-061": ["SEM-ACTION-CARD-PLAY-001", *_rules_for("tactical-retreat", "breakthrough", "shoot-first", "always-prepared", "field-surgery", "hippocratic-oath", "weak-spots", "lets-go")],
    "SEM-Q-062": _rules_for("continuous-fire"),
    "SEM-Q-063": _rules_for("always-prepared"),
    "SEM-Q-064": _rules_for("always-prepared"),
    "SEM-Q-065": _rules_for("field-surgery", "first-aid", "combat-drugs"),
    "SEM-Q-066": _rules_for("weak-spots", "hippocratic-oath"),
    "SEM-Q-067": _rules_for("officer-channel"),
    "SEM-Q-068": _rules_for("stay-calm-reaction"),
    "SEM-Q-069": _rules_for("lets-go"),
    "SEM-Q-070": _rules_for("taking-aim"),
    "SEM-Q-071": _rules_for("explosives"),
    "SEM-Q-072": ["SEM-ACTION-CARD-DRAW-001", "SEM-RT-012", *_rules_for("combat-drugs", "stay-calm-reaction")],
    "SEM-Q-073": _rules_for("tactical-retreat", "breakthrough", "shoot-first", "duck-and-cover", "lets-go"),
    "SEM-Q-074": [
        row["reactionRuleId"] for row in PHYSICAL_DEFINITIONS
        if row["effectKind"] == "chain-command-reaction" and row["character"] != "Medical Support"
    ],
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _load(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def _raw_root(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    return root, hashlib.sha256(data).hexdigest()


def _parse_js_literal(body: str, field: str):
    match = re.search(rf"^    {field}:\s*", body, re.M)
    if not match:
        raise AssertionError(f"missing Action BGA field {field}")
    start = match.end()
    opening = body[start]
    if opening == "'":
        escaped = False
        for index in range(start + 1, len(body)):
            char = body[index]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == "'":
                return ast.literal_eval(body[start:index + 1])
    if opening == "[":
        depth = 0
        in_string = False
        escaped = False
        for index in range(start, len(body)):
            char = body[index]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == "'":
                    in_string = False
                continue
            if char == "'":
                in_string = True
            elif char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    return ast.literal_eval(body[start:index + 1])
    raise AssertionError(f"unterminated Action BGA field {field}")


def _parse_bga_actions(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const ACTION_CARDS_DATA = \{\n(.*?)\n\};\nconst EVENT_CARDS_DATA", text, re.S)
    if not match:
        raise AssertionError("ACTION_CARDS_DATA block not found")
    records = {}
    for row in re.finditer(r"^  ([A-Za-z0-9_]+): \{\n(.*?)^  \},$", match.group(1), re.M | re.S):
        key, body = row.groups()
        character_match = re.search(r"^    character: (\d+),$", body, re.M)
        no_intruders_match = re.search(r"^    noIntruders: (true|false),$", body, re.M)
        command_match = re.search(r"^    command: (true|false),$", body, re.M)
        if not character_match or not no_intruders_match or not command_match:
            raise AssertionError(f"Action BGA scalar fields missing: {key}")
        records[key] = {
            "key": key,
            "character": int(character_match.group(1)),
            "name": _parse_js_literal(body, "name"),
            "effectDesc": _parse_js_literal(body, "effectDesc"),
            "reactionDesc": _parse_js_literal(body, "reactionDesc"),
            "noIntruders": no_intruders_match.group(1) == "true",
            "command": command_match.group(1) == "true",
            "sourceBlockText": row.group(0),
        }
    if len(records) != 60:
        raise AssertionError("licensed Action table count changed")
    expected_prefixes = {
        "CombatEngineer": 10,
        "ContractorConsultant": 10,
        "HeavyGunOperator": 10,
        "MedicalSupport": 10,
        "Officer": 10,
        "Recon": 10,
    }
    prefixes = Counter(key.split("_", 1)[0] for key in records)
    if dict(prefixes) != expected_prefixes:
        raise AssertionError("licensed Action Character partition changed")
    return records


def _compose_printed_body(printed: dict) -> str:
    body = printed.get("body")
    if isinstance(body, str) and body:
        return body
    for first, separator, second in (
        ("firstEffect", "divider", "secondEffect"),
        ("firstInstruction", "separator", "secondInstruction"),
        ("effect1", "separator", "effect2"),
    ):
        if isinstance(printed.get(first), str):
            pieces = [printed[first]]
            if isinstance(printed.get(separator), str):
                pieces.append(printed[separator])
            if isinstance(printed.get(second), str):
                pieces.append(printed[second])
            return "\n".join(piece for piece in pieces if piece)
    candidates = []
    for key, value in printed.items():
        if isinstance(value, str) and re.search(r"effect|instruction|reaction", key, re.I):
            candidates.append(value)
    return "\n".join(value for value in candidates if value)


def _title_from_canonical(corpus_row: dict) -> str:
    canonical = (corpus_row.get("identity") or {}).get("canonicalPath")
    if not canonical:
        return ""
    return Path(canonical).stem.replace("-", " ").upper()


def _split_reaction(body: str, visible: dict) -> tuple[str, str | None]:
    reaction = visible.get("reaction")
    sections = visible.get("sections") or []
    if not reaction:
        for section in sections:
            text = section.get("text", "") if isinstance(section, dict) else str(section)
            if text.startswith("REACTION\n"):
                reaction = text.split("\n", 1)[1]
                break
    if not reaction and "REACTION\n" in body:
        body, reaction = body.split("REACTION\n", 1)
        body = body.rstrip()
    elif reaction and body.endswith("REACTION\n" + reaction):
        body = body[: -(len(reaction) + len("REACTION\n"))].rstrip()
    return body, reaction


def _split_branches(body: str) -> list[str]:
    parts = re.split(r"\n\s*OR\s*\n|\s+OR\s+(?=[A-ZIf])", body)
    return [part.strip() for part in parts if part.strip()]


def _split_sentences(text: str) -> list[str]:
    normalized = text.strip()
    if not normalized:
        return []
    pieces = re.split(r"(?<=[.!?])(?:\s+|\n+)", normalized)
    return [piece.strip() for piece in pieces if piece.strip()]


def _semantic_token(token: str) -> str | None:
    normalized = token.strip()
    aliases = {"action-card": "actionCard", "oxygenToken": "oxygenToken"}
    normalized = aliases.get(normalized, normalized)
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9]+", normalized):
        return "icon." + normalized
    return None


def _icon_rows(corpus_row: dict, main_body: str, reaction: str | None, upper_right) -> list[dict]:
    selected = corpus_row.get("selectedExtraction") or {}
    rows = []
    if selected:
        for index, icon in enumerate(selected.get("verifiedIconOccurrences") or [], 1):
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
                "literalAppearance": icon.get("referenceLabel") or icon.get("literalAppearance") or "unresolved local glyph",
                "matchDecision": icon.get("matchDecision") or "no-match",
                "semanticReferenceId": None,
                "evidence": "selected-card-text-evidence",
            })
        return rows
    combined = "\n".join(value for value in (main_body, reaction or "") if value)
    for match in re.finditer(r"\[([^\]]+)\]", combined):
        literal = match.group(1)
        semantic = None if literal.startswith(("ICON:", "LOCAL_", "unresolved:")) else _semantic_token(literal)
        rows.append({
            "iconId": f"I{len(rows)+1:02d}",
            "location": f"rulesText:{match.start()}-{match.end()}",
            "literalAppearance": "[" + literal + "]",
            "matchDecision": "canonical-corpus" if semantic else "literal-no-match",
            "semanticReferenceId": semantic,
            "evidence": "verified canonical sidecar/corpus",
        })
    if upper_right not in (None, "") and not any("upper" in row["location"].lower() for row in rows):
        semantic = "icon.notInCombat" if upper_right in {"notInCombat", "[notInCombat]"} else None
        rows.insert(0, {
            "iconId": "I00",
            "location": "upper-right",
            "literalAppearance": upper_right,
            "matchDecision": "canonical-corpus" if semantic else "literal-no-match",
            "semanticReferenceId": semantic,
            "evidence": "verified canonical sidecar/corpus",
        })
        for index, row in enumerate(rows, 1):
            row["iconId"] = f"I{index:02d}"
    return rows


def _preferred_asset(corpus_row: dict, character: str | None, selected_occurrences: list[str], generated_cell: int | None) -> dict:
    printed = corpus_row.get("printedData") or {}
    selected = corpus_row.get("selectedExtraction") or {}
    visible = selected.get("visibleText") or {}
    title = visible.get("title") or printed.get("title") or _title_from_canonical(corpus_row)
    body = visible.get("body") or _compose_printed_body(printed)
    if not isinstance(title, str):
        title = ""
    if not isinstance(body, str):
        body = ""
    body, reaction = _split_reaction(body, visible)
    footer = visible.get("footer")
    if footer in (None, ""):
        footer = visible.get("lowerCenter") or printed.get("footer") or (character.upper() if character else "")
    if selected:
        upper_right = visible.get("upperRight") if "upperRight" in visible else printed.get("upperRight")
    else:
        upper_right = printed.get("upperRight")
    verified_nic = any(icon.get("canonicalToken") == "notInCombat" for icon in selected.get("verifiedIconOccurrences") or [])
    unresolved_upper = [
        icon for icon in selected.get("unresolvedIconOccurrences") or []
        if "upper" in (icon.get("cardLocation") or "").lower() or "corner" in (icon.get("cardLocation") or "").lower()
    ]
    if verified_nic:
        not_in_combat = {"status": "source-resolved", "semanticReferenceId": "icon.notInCombat", "literalAppearance": upper_right}
    elif unresolved_upper:
        not_in_combat = {"status": "literal-unresolved", "semanticReferenceId": None, "literalAppearance": upper_right or unresolved_upper[0].get("referenceLabel")}
    elif selected and upper_right not in (None, ""):
        not_in_combat = {"status": "literal-unresolved", "semanticReferenceId": None, "literalAppearance": upper_right}
    elif not selected and printed.get("upperRight") == "notInCombat":
        not_in_combat = {"status": "source-resolved", "semanticReferenceId": "icon.notInCombat", "literalAppearance": "notInCombat"}
    else:
        not_in_combat = {"status": "absent", "semanticReferenceId": None, "literalAppearance": upper_right}

    branches = _split_branches(body)
    panels = []
    reading = 1
    if not_in_combat["status"] != "absent":
        panels.append({"panelId": f"P{reading}", "readingOrder": reading, "role": "upper-right-restriction", "heading": None, "operative": True, "exactText": str(not_in_combat["literalAppearance"] or "")})
        reading += 1
    panels.append({"panelId": f"P{reading}", "readingOrder": reading, "role": "title", "heading": None, "operative": False, "exactText": title})
    reading += 1
    for index, branch in enumerate(branches, 1):
        if index > 1:
            panels.append({"panelId": f"P{reading}", "readingOrder": reading, "role": "branch-separator-heading", "heading": "OR", "operative": False, "exactText": "OR"})
            reading += 1
        heading = "COMMAND" if re.search(r"(?:^|\n)COMMAND(?:\n|$)", branch) else None
        effect_text = re.sub(r"(?:^|\n)COMMAND\n", "", branch, count=1).strip() if heading else branch
        panels.append({"panelId": f"P{reading}", "readingOrder": reading, "role": "command-effect" if heading else "action-effect", "heading": heading, "operative": True, "exactText": effect_text})
        reading += 1
    if reaction:
        panels.append({"panelId": f"P{reading}", "readingOrder": reading, "role": "reaction-effect", "heading": "REACTION", "operative": True, "exactText": reaction})
        reading += 1
    panels.append({"panelId": f"P{reading}", "readingOrder": reading, "role": "character-footer", "heading": None, "operative": False, "exactText": footer or ""})

    sentences = []
    for panel in panels:
        if panel["role"] not in {"action-effect", "command-effect", "reaction-effect"}:
            continue
        for text in _split_sentences(panel["exactText"]):
            sentences.append({"sentenceId": f"S{len(sentences)+1:02d}", "sequence": len(sentences)+1, "panelId": panel["panelId"], "exactText": text})
    icons = _icon_rows(corpus_row, body, reaction, upper_right)
    corpus_projection = {key: printed.get(key) for key in ("title", "body", "footer", "upperRight")}
    selected_projection = {key: visible.get(key) for key in ("title", "body", "footer", "upperRight")}
    differences = {
        key: {"corpusProjection": corpus_projection[key], "selectedPixelEvidence": selected_projection[key]}
        for key in corpus_projection
        if selected and corpus_projection[key] != selected_projection[key]
    }
    return {
        "printedTitle": title,
        "printedBody": body,
        "printedFooter": footer or "",
        "upperRight": upper_right,
        "reactionText": reaction,
        "branches": branches,
        "panels": panels,
        "sentences": sentences,
        "iconOccurrences": icons,
        "notInCombat": not_in_combat,
        "selectedEvidenceUsed": bool(selected),
        "selectedEvidenceRunIdentity": selected.get("runIdentity"),
        "sourcePrintedData": printed,
        "selectedVisibleText": visible if selected else None,
        "representationBoundary": {
            "differences": differences,
            "policy": "Selected source-bound pixel evidence controls literal transcription where present; stale corpus/canonical projections remain independently visible and are never silently rewritten.",
        },
        "selectedPhysicalOccurrenceIds": selected_occurrences,
        "selectedByPhysicalRoot": bool(selected_occurrences),
        "generatedCell": generated_cell,
    }


def _cost_clauses(effect_kind: str) -> list[dict]:
    specs = {
        "repairs": [("icon.actionCard", 1, "discard one Action card before discarding a Malfunction")],
        "repairs-accessible": [("icon.actionCard", 1, "discard one Action card before discarding a Malfunction")],
        "basic-secure": [("icon.actionCard", 1, "one Action card for either selected branch")],
        "secure": [("icon.actionCard", 1, "one Action card for the Reinforce branch only")],
        "explosives": [("icon.grenadeToken", 1, "Grenade token for the new-Corridor branch")],
        "tactical-retreat": [("icon.actionCard", 1, "additional Action card"), ("icon.ammoToken", 1, "Ammo from a Weapon")],
        "pyrotechnics": [("icon.grenadeToken", 1, "Grenade token for the critical-result branch")],
        "continuous-fire": [("icon.actionCard", None, "any number of Action cards, one per Hit")],
        "forcing-fire": [("icon.ammoToken", 1, "Ammo from the selected Ranged Weapon")],
        "field-surgery": [("icon.actionCard", 1, "Action card before Wound discard"), ("icon.medpackToken", 1, "Medpack token or target gains Contamination")],
        "combat-drugs": [("icon.medpackToken", 1, "Medpack token")],
        "duck-and-cover": [("icon.actionCard", 1, "additional Action card")],
        "always-prepared": [("icon.actionCard", 1, "Action card for the draw-two-Items branch")],
        "sprint": [("icon.oxygen", 1, "optional Oxygen loss for the second Move")],
    }
    return [
        {"resourceTermId": resource, "quantity": quantity, "scope": scope}
        for resource, quantity, scope in specs.get(effect_kind, [])
    ]


def build_action_source_index(repo: Path) -> dict:
    corpus = _load(repo / CORPUS_PATH)
    progress = _load(repo / PROGRESS_PATH)
    objects = _load(repo / OBJECTS_PATH)
    provenance = _load(repo / PROVENANCE_PATH)
    backlog = _load(repo / BACKLOG_PATH)
    rulebook_visual = _load(repo / RULEBOOK_VISUAL_PATH)
    faq = _load(repo / FAQ_PATH)
    if not isinstance(corpus, dict) or not isinstance(progress, dict) or not isinstance(objects, list) or not isinstance(provenance, list) or not isinstance(backlog, dict) or not isinstance(rulebook_visual, dict) or not isinstance(faq, dict):
        raise AssertionError("Action evidence container shape changed")
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    provenance_by_file = {row["file"]: row for row in provenance}
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    raw, raw_sha = _raw_root(repo)

    definition_by_path: dict[str, list[dict]] = {}
    for definition in PHYSICAL_DEFINITIONS:
        definition_by_path.setdefault(definition["sourcePath"], []).append(definition)

    sheet_5674_paths = [f"assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-{cell:02d}.png" for cell in range(45)]
    sheet_5675_paths = [
        "assets/tts-mod/extract/v2-dl/tree/cards/game/action/repairs.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/action/rest.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-001.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-002.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/action/action-003.png",
    ]
    direct_paths = sorted({row["sourcePath"] for row in PHYSICAL_DEFINITIONS if row["generatedCell"] is None})
    all_asset_paths = [*sheet_5674_paths, *sheet_5675_paths, *direct_paths]
    if len(set(all_asset_paths)) != 89:
        raise AssertionError("Action source-face asset closure changed")

    source_assets = []
    for source_path in all_asset_paths:
        corpus_row = corpus_by_path.get(source_path)
        if not corpus_row or not corpus_row.get("rulesTextPresent"):
            raise AssertionError(f"Action rules-bearing corpus row missing: {source_path}")
        selected_definitions = definition_by_path.get(source_path, [])
        character = selected_definitions[0]["character"] if selected_definitions else None
        generated = (progress_by_path.get(source_path) or {}).get("generatedFrom")
        generated_cell = generated.get("cellIndex") if isinstance(generated, dict) else None
        preferred = _preferred_asset(corpus_row, character, [row["occurrenceId"] for row in selected_definitions], generated_cell)
        selected = bool(selected_definitions)
        if source_path in sheet_5674_paths:
            source_role = "generated-cell-selected-face" if selected else "generated-cell-selector-gap-variant"
            sheet_id = "SRC-ACTION-SHEET-5674"
            sheet_path = SHEET_5674_PATH
            custom_deck_id = "5674"
        elif source_path in sheet_5675_paths:
            source_role = "generated-cell-selected-face"
            sheet_id = "SRC-ACTION-SHEET-5675"
            sheet_path = SHEET_5675_PATH
            custom_deck_id = "5675"
        else:
            source_role = "direct-selected-face"
            sheet_id = None
            sheet_path = None
            custom_deck_id = None
        gap_source_id = f"SRC-ACTION-SHEET-5674-CELL-{generated_cell:02d}" if source_role == "generated-cell-selector-gap-variant" else None
        source_assets.append({
            "assetId": f"ACTION-ASSET-{len(source_assets)+1:03d}",
            "sourceId": gap_source_id,
            "sourcePath": source_path,
            "sourceSha256": corpus_row["sourceSha256"],
            "sourceRole": source_role,
            "sourceSheetId": sheet_id,
            "sourceSheetPath": sheet_path,
            "sourceSheetGrid": {"columns": 9, "rows": 5, "cellWidth": 1052, "cellHeight": 1433} if sheet_id else None,
            "customDeckId": custom_deck_id,
            "selectorGap": None if selected else {
                "status": "explicit-no-selected-base-root-full-CardID-GUID-selector",
                "reason": "The source-clear generated base-Character Action face exists in the exact 9x5 sheet/corpus, but none of the six base Character roots or Shared Contractor root selects this cell. It remains a source variant, not a physical copy.",
                "cardIdModuloJoinUsed": False,
            },
            "backlogUnitId": "CARD:" + corpus_row["sourceSha256"][:16],
            "corpusExtractionState": corpus_row.get("extractionState"),
            **preferred,
        })

    asset_by_path = {row["sourcePath"]: row for row in source_assets}
    if len(asset_by_path) != len(source_assets):
        raise AssertionError("Action source asset paths are not unique")

    # Pixel-lock both full sheets and every retained base cell. The second sheet
    # retains only cells 10–14 because cells 0–9 and 15–44 belong to expansion
    # Characters; those forty cells are counted but not promoted into base data.
    for sheet_path, cell_paths, cell_indices in (
        (SHEET_5674_PATH, sheet_5674_paths, list(range(45))),
        (SHEET_5675_PATH, sheet_5675_paths, list(range(10, 15))),
    ):
        with Image.open(repo / sheet_path) as sheet:
            if sheet.size != (9468, 7165):
                raise AssertionError(f"Action 9x5 sheet dimensions changed: {sheet_path}")
            for source_path, cell in zip(cell_paths, cell_indices):
                row_index, column_index = divmod(cell, 9)
                crop = sheet.crop((column_index * 1052, row_index * 1433, (column_index + 1) * 1052, (row_index + 1) * 1433)).convert("RGB")
                with Image.open(repo / source_path) as generated_image:
                    if generated_image.convert("RGB").tobytes() != crop.tobytes():
                        raise AssertionError(f"Action generated-cell pixel drift: {source_path}")

    root_evidence = []
    physical_faces = []
    roots_by_guid = {row[3]: row for row in DECK_ROOTS}
    definitions_by_root: dict[str, list[dict]] = {}
    for definition in PHYSICAL_DEFINITIONS:
        definitions_by_root.setdefault(definition["deckGuid"], []).append(definition)
    for character, code, bag_guid, deck_guid, segment in DECK_ROOTS:
        raw_deck = _find_guid(raw.get("ObjectStates"), deck_guid)
        if not isinstance(raw_deck, dict):
            raise AssertionError(f"Action root missing from raw TTS save: {deck_guid}")
        definitions = sorted(definitions_by_root[deck_guid], key=lambda row: row["rootSequence"])
        contained_value = raw_deck.get("ContainedObjects") or {}
        contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
        expected = [(row["ttsCardId"], row["ttsCardGuid"]) for row in definitions]
        actual = [(int(row["CardID"]), row["GUID"]) for row in contained]
        deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
        if actual != expected or deck_ids != [row[0] for row in expected]:
            raise AssertionError(f"Action raw root member/order drift: {deck_guid}")
        tags = raw_deck.get("Tags") or {}
        if "ActionDeck" not in (list(tags.values()) if isinstance(tags, dict) else list(tags)) or raw_deck.get("GMNotes") != "actionDiscard":
            raise AssertionError(f"Action root tag/GMNotes drift: {deck_guid}")
        custom = raw_deck.get("CustomDeck") or {}
        root_evidence.append({
            "sourceId": f"SRC-ACTION-DECK-{code}{'-SHARED' if segment == 'shared-contractor' else ''}",
            "character": character,
            "characterCode": code,
            "characterDeckId": f"BASE-ACTION-DECK-{code}",
            "deckSegment": segment,
            "bagGuid": bag_guid,
            "deckGuid": deck_guid,
            "rootType": raw_deck.get("Name"),
            "gmNotes": raw_deck.get("GMNotes"),
            "tags": list(tags.values()) if isinstance(tags, dict) else list(tags),
            "savedDeckIds": deck_ids,
            "customDeckIds": list(custom),
            "fullContainedSelectors": [
                {"rootSequence": row["rootSequence"], "fullCardId": row["ttsCardId"], "guid": row["ttsCardGuid"], "copyId": row["copyId"], "occurrenceId": row["occurrenceId"]}
                for row in definitions
            ],
        })
        contained_by_tuple = {(int(row["CardID"]), row["GUID"]): row for row in contained}
        for definition in definitions:
            raw_child = contained_by_tuple[(definition["ttsCardId"], definition["ttsCardGuid"])]
            child_custom = raw_child.get("CustomDeck") or {}
            if len(child_custom) != 1:
                raise AssertionError(f"Action child CustomDeck selector count changed: {definition['occurrenceId']}")
            custom_deck_id = next(iter(child_custom))
            root_custom = custom.get(custom_deck_id)
            if not isinstance(root_custom, dict) or root_custom != child_custom[custom_deck_id]:
                raise AssertionError(f"Action root/child CustomDeck projection drift: {definition['occurrenceId']}")
            asset = asset_by_path[definition["sourcePath"]]
            generated = definition["generatedCell"] is not None
            expected_sheet_url = SHEET_5674_URL if custom_deck_id == "5674" else SHEET_5675_URL if custom_deck_id == "5675" else None
            if generated:
                if root_custom.get("FaceURL") != expected_sheet_url or root_custom.get("NumWidth") != 9 or root_custom.get("NumHeight") != 5:
                    raise AssertionError(f"Action generated selector grid drift: {definition['occurrenceId']}")
                progress_generated = (progress_by_path[definition["sourcePath"]].get("generatedFrom") or {})
                expected_sheet_path = SHEET_5674_PATH if custom_deck_id == "5674" else SHEET_5675_PATH
                if progress_generated != {"sourceSheetPath": expected_sheet_path, "cellIndex": definition["generatedCell"]}:
                    raise AssertionError(f"Action exact full selector/cell evidence drift: {definition['occurrenceId']}")
            else:
                file_name = definition["sourcePath"].split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]
                provenance_row = provenance_by_file.get(file_name) or {}
                exact_ref = next((row for row in provenance_row.get("objects") or [] if row.get("key") == "FaceURL" and row.get("guid") == definition["ttsCardGuid"] and int(row.get("cardId") or 0) == definition["ttsCardId"]), None)
                if not exact_ref or provenance_row.get("url") != root_custom.get("FaceURL"):
                    raise AssertionError(f"Action direct FaceURL provenance drift: {definition['occurrenceId']}")
            if root_custom.get("BackURL") != SHARED_BACK_URL:
                raise AssertionError(f"Action BackURL drift: {definition['occurrenceId']}")
            source_id = definition["sourceId"]
            face = {
                **definition,
                "ttsBagGuid": bag_guid,
                "ttsDeckType": raw_deck.get("Name"),
                "customDeckId": custom_deck_id,
                "sourceSelector": {
                    "key": "FaceURL",
                    "objectType": raw_child.get("Name"),
                    "fullCardId": definition["ttsCardId"],
                    "guid": definition["ttsCardGuid"],
                    "parentDeckGuid": deck_guid,
                    "customDeckId": custom_deck_id,
                    "url": root_custom.get("FaceURL"),
                    "backUrl": root_custom.get("BackURL"),
                    "sideRole": "operative-base-Action-face",
                    "sourceRole": asset["sourceRole"],
                    "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-BackURL-container-tuple-with-reviewed-generated-cell" if generated else "exact-full-CardID-GUID-direct-FaceURL-BackURL-container-tuple",
                    "generatedSpriteSheetCell": generated,
                    "sourceSheetPath": asset["sourceSheetPath"],
                    "sourceSheetSha256": _sha(repo / asset["sourceSheetPath"]) if generated else None,
                    "sourceSheetGrid": asset["sourceSheetGrid"],
                    "generatedCell": definition["generatedCell"],
                    "selectorGap": None,
                    "cardIdModuloJoinUsed": False,
                },
                "sourcePath": definition["sourcePath"],
                "sourceSha256": asset["sourceSha256"],
                "sourceAuthority": "source-bound-component-scan",
                "sourceVersion": f"TTS source-bound base Action physical occurrence / Character {character} / root {deck_guid} / full CardID {definition['ttsCardId']} / GUID {definition['ttsCardGuid']}",
                "backlogUnitId": asset["backlogUnitId"],
                "playActionCardBasicActionCost": 0,
                "printedCostClauses": _cost_clauses(definition["effectKind"]),
                "printedTitle": asset["printedTitle"],
                "printedBody": asset["printedBody"],
                "printedFooter": asset["printedFooter"],
                "upperRight": asset["upperRight"],
                "notInCombat": asset["notInCombat"],
                "reactionText": asset["reactionText"],
                "panels": [{**panel, "panelId": f"{definition['copyId']}-{panel['panelId']}"} for panel in asset["panels"]],
                "sentences": [{**sentence, "sentenceId": f"{definition['copyId']}-{sentence['sentenceId']}", "panelId": f"{definition['copyId']}-{sentence['panelId']}"} for sentence in asset["sentences"]],
                "iconOccurrences": [{**icon, "iconId": f"{definition['copyId']}-{icon['iconId']}"} for icon in asset["iconOccurrences"]],
                "selectedEvidenceUsed": asset["selectedEvidenceUsed"],
                "selectedEvidenceRunIdentity": asset["selectedEvidenceRunIdentity"],
                "sourcePrintedData": asset["sourcePrintedData"],
                "selectedVisibleText": asset["selectedVisibleText"],
                "representationBoundary": asset["representationBoundary"],
                "identityJoinEvidence": {
                    "characterNameOnlyJoin": False,
                    "titleOnlyJoin": False,
                    "bodySimilarityJoin": False,
                    "folderOnlyJoin": False,
                    "sourceSheetOnlyJoin": False,
                    "generatedCellOnlyJoin": False,
                    "cardIdModuloJoin": False,
                    "licensedKeyJoin": False,
                    "basis": [
                        "exact Character kit/container ancestry and root ActionDeck tag",
                        "exact raw full CardID/GUID/CustomDeck/FaceURL/BackURL/root tuple",
                        "for generated cards: explicit reviewed sheet hash/grid/cell crosswalk",
                        "live source bytes and selected/canonical evidence closure",
                    ],
                },
            }
            physical_faces.append(face)

    # Final Character deck membership is a set because setup shuffles it; the
    # root-local saved order remains provenance only.
    character_decks = []
    for character, code in CHARACTER_CODES.items():
        faces = [row for row in physical_faces if row["character"] == character]
        if len(faces) != 10:
            raise AssertionError(f"Action final Character deck count changed: {character}")
        character_decks.append({
            "characterDeckId": f"BASE-ACTION-DECK-{code}",
            "character": character,
            "physicalCopies": sorted([row["copyId"] for row in faces]),
            "physicalOccurrenceIds": sorted([row["occurrenceId"] for row in faces]),
            "rootDeckGuids": [row[3] for row in DECK_ROOTS if row[0] == character],
            "membershipOrderSourceBacked": False,
            "setupShuffleRequired": True,
        })

    bga = _parse_bga_actions(repo / BGA_PATH)
    bga_sha = _sha(repo / BGA_PATH)
    licensed = [
        {**bga[key], "sourceId": "SRC-BGA-ACTION-CARDS", "sourcePath": BGA_PATH, "sourceSha256": bga_sha, "authority": "licensed-digital-secondary", "assertedTtsPhysicalIdentityLinks": []}
        for key in sorted(bga)
    ]

    faq_by_id = {unit["sourceUnitId"]: unit for page in faq["pages"] for unit in page.get("units", [])}
    faq_ids = ["FQ-P02-U10", "FQ-P02-U11", "FQ-P02-U14", "FQ-P02-U15", "FQ-P02-U16", "FQ-P03-U01", "FQ-P03-U02", "FQ-P03-U07"]
    faq_occurrences = [
        {"sourceUnitId": qid, "section": faq_by_id[qid]["section"], "applicability": faq_by_id[qid]["applicability"], "printedText": faq_by_id[qid]["printedText"]}
        for qid in faq_ids
    ]
    if any(row["applicability"] != "base-game" for row in faq_occurrences):
        raise AssertionError("Action FAQ applicability changed")

    visual_unit_ids = {unit["occurrenceId"] for page in rulebook_visual["pages"] for unit in page.get("visualUnits", [])}
    if not {"RB-P03-V01", "RB-P11-V01", "RB-P12-V02", "RB-P13-V01", "RB-P28-V02", "RB-P36-V01", "RB-P40-V02"}.issubset(visual_unit_ids):
        raise AssertionError("Action official visual-obligation boundary changed")
    official_faces = [
        {"occurrenceId": "RB-P03-V01-ACTION-WEAK-SPOT", "kind": "current-visible-face", "title": "Weak spot", "visibleText": "Deal 1 Hit to an [official Intruder glyph]. Then, Shoot or Melee Attack it.", "visualUnitId": "RB-P03-V01", "assertedTtsGuid": None},
        {"occurrenceId": "RB-P13-V01-ACTION-DUCK", "kind": "current-visible-face-and-anatomy", "title": "Duck and cover", "visibleText": "Discard 1 [Action-card glyph] to Move. During that Movement, Prevent 1 Intruder Attack. Reaction panel shown independently.", "visualUnitId": "RB-P13-V01", "assertedTtsGuid": None},
        {"occurrenceId": "RB-P13-ACTION-SPRINT", "kind": "current-visible-face", "title": "Sprint", "visibleText": "Move. Then, you may spend 1 [inline source glyph] to Move again.", "visualUnitId": "RB-P13-V01-page-context", "assertedTtsGuid": None, "visibilityBoundary": "Text extraction omits the inline glyph identity; do not infer it from the TTS or licensed occurrence."},
        {"occurrenceId": "RB-P28-V02-ACTION-SEARCH", "kind": "current-visible-face", "title": "SEARCH", "visibleText": "For each Item Icon in your Room draw 1 Item of the corresponding type. You may keep 1 of them and discard the rest.", "visualUnitId": "RB-P28-V02", "assertedTtsGuid": None},
    ]
    official_backs = [
        {"occurrenceId": "RB-P03-V01-ACTION-BACK", "kind": "visible-family-back", "visualUnitId": "RB-P03-V01"},
        {"occurrenceId": "RB-P36-V01-ACTION-BACK", "kind": "visible-common-back-behind-Contamination", "visualUnitId": "RB-P36-V01"},
    ]

    action_deck_guids = {row[3] for row in DECK_ROOTS}
    excluded_roots = []
    for obj in objects:
        if obj.get("type") not in {"Deck", "DeckCustom"} or obj.get("gmnotes") != "actionDiscard" or obj.get("guid") in action_deck_guids:
            continue
        raw_obj = _find_guid(raw.get("ObjectStates"), obj.get("guid")) or {}
        tags = raw_obj.get("Tags") or {}
        if "ActionDeck" not in (list(tags.values()) if isinstance(tags, dict) else list(tags)):
            continue
        parent_bag = next((parent for parent in reversed(obj.get("parent") or []) if parent[0] == "Bag"), None)
        excluded_roots.append({"deckGuid": obj["guid"], "characterBag": parent_bag, "physicalChildren": len((raw_obj.get("DeckIDs") or {}).values()), "scope": "expansion Character Action root; excluded from base conclusions"})
    excluded_roots.sort(key=lambda row: (str(row["characterBag"]), row["deckGuid"]))
    if len(excluded_roots) != 22:
        raise AssertionError("expansion Action root boundary changed")

    back_provenance = provenance_by_file["cards/game/action/back.jpg"]
    sheet_5674_provenance = provenance_by_file["cards/character/heavy-gun-operator-045.jpg"]
    sheet_5675_provenance = provenance_by_file["cards/game/action-154.jpg"]
    if back_provenance.get("refs") != 273 or sheet_5674_provenance.get("refs") != 20 or sheet_5675_provenance.get("refs") != 21:
        raise AssertionError("Action back/sheet global provenance references changed")

    selected_asset_rows = [row for row in source_assets if row["selectedByPhysicalRoot"]]
    gap_asset_rows = [row for row in source_assets if row["selectorGap"]]
    face_unit_ids = sorted({row["backlogUnitId"] for row in source_assets})
    rule_visual_ids = ["RULE:RT-002", "RULE:RT-003", "RULE:RT-006", "RULE:RT-012", "RULE:RT-013", "RULE:ACT-MOVE-002", "RULE:ACT-MELEE-001", "RULE:ACT-CARD-001", "RULE:ACT-CARD-002", "RULE:ACT-SECURE-001", "RULE:ACT-ROOM-001", "VIS:RB-P03-V01", "VIS:RB-P11-V01", "VIS:RB-P12-V02", "VIS:RB-P13-V01", "VIS:RB-P28-V02", "VIS:RB-P36-V01", "VIS:RB-P40-V02", *["FAQ:" + qid for qid in faq_ids]]
    linked_backlog_ids = sorted(set(face_unit_ids + [unit_id for unit_id in rule_visual_ids if unit_id in backlog_by_id]))
    if any(unit_id not in backlog_by_id for unit_id in face_unit_ids):
        raise AssertionError("Action exact card backlog tuple missing")

    title_counts = Counter(row["printedTitle"] for row in physical_faces)
    per_character = {character: sum(row["character"] == character for row in physical_faces) for character in CHARACTER_CODES}
    counts = {
        "officialActionCardTotal": 60,
        "officialCharacters": 6,
        "officialCardsPerCharacter": 10,
        "rootDecks": 7,
        "characterKitRootDecks": 6,
        "sharedContractorRootDecks": 1,
        "characterKitPhysicalOccurrences": 55,
        "sharedContractorPhysicalOccurrences": 5,
        "physicalFaceOccurrences": len(physical_faces),
        "perCharacterPhysicalOccurrences": per_character,
        "uniquePhysicalCopyIds": len({row["copyId"] for row in physical_faces}),
        "uniqueSelectedFaceAssets": len({row["sourceSha256"] for row in physical_faces}),
        "uniquePrintedTitles": len(title_counts),
        "directPhysicalFaceOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] is False for row in physical_faces),
        "generatedPhysicalFaceOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] is True for row in physical_faces),
        "sourceFaceAssets": len(source_assets),
        "selectedSourceFaceAssets": len(selected_asset_rows),
        "selectorGapSourceFaceAssets": len(gap_asset_rows),
        "sourceSheets": 2,
        "sourceSheetCells": 90,
        "selectedGeneratedCells": 21,
        "baseSelectorGapCells": 29,
        "excludedExpansionSheetCells": 40,
        "rootCustomDeckEntries": sum(len(row["customDeckIds"]) for row in root_evidence),
        "sharedBackOccurrences": 1,
        "sharedBackPhysicalSelectors": 60,
        "sharedBackGlobalSelectorReferences": back_provenance["refs"],
        "sheet5674GlobalSelectorReferences": sheet_5674_provenance["refs"],
        "sheet5675GlobalSelectorReferences": sheet_5675_provenance["refs"],
        "physicalRegions": sum(len(row["panels"]) for row in physical_faces),
        "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in physical_faces),
        "branchSeparatorHeadingOccurrences": sum(sum(panel["role"] == "branch-separator-heading" for panel in row["panels"]) for row in physical_faces),
        "commandHeadingOccurrences": sum(sum(panel.get("heading") == "COMMAND" for panel in row["panels"]) for row in physical_faces),
        "reactionHeadingOccurrences": sum(sum(panel.get("heading") == "REACTION" for panel in row["panels"]) for row in physical_faces),
        "printedSentenceOccurrences": sum(len(row["sentences"]) for row in physical_faces),
        "functionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in physical_faces),
        "matchedIconOccurrences": sum(sum(icon["semanticReferenceId"] is not None for icon in row["iconOccurrences"]) for row in physical_faces),
        "unresolvedLocalGlyphOccurrences": sum(sum(icon["semanticReferenceId"] is None for icon in row["iconOccurrences"]) for row in physical_faces),
        "sourceResolvedNotInCombatOccurrences": sum(row["notInCombat"]["status"] == "source-resolved" for row in physical_faces),
        "literalUnresolvedUpperRightOccurrences": sum(row["notInCombat"]["status"] == "literal-unresolved" for row in physical_faces),
        "absentUpperRightOccurrences": sum(row["notInCombat"]["status"] == "absent" for row in physical_faces),
        "zeroPlayActionCostOccurrences": sum(row["playActionCardBasicActionCost"] == 0 for row in physical_faces),
        "printedAdditionalCostClauses": sum(len(row["printedCostClauses"]) for row in physical_faces),
        "licensedDigitalOccurrences": len(licensed),
        "licensedReactionOccurrences": sum(bool(row["reactionDesc"]) for row in licensed),
        "licensedCommandTrueOccurrences": sum(row["command"] for row in licensed),
        "licensedNoIntrudersTrueOccurrences": sum(row["noIntruders"] for row in licensed),
        "assertedPhysicalToLicensedIdentityLinks": 0,
        "officialVisibleFaceOccurrences": len(official_faces),
        "officialVisibleBackOccurrences": len(official_backs),
        "baseApplicableFaqOccurrences": len(faq_occurrences),
        "excludedExpansionActionRoots": len(excluded_roots),
        "backlogTuples": len(face_unit_ids),
        "backlogPhysicalFaceLinks": len(physical_faces),
        "backlogObligationsLinked": len(linked_backlog_ids),
        "semanticPhysicalFaceRecords": len(ACTION_RULE_IDS),
        "semanticReactionPanelRecords": len(ACTION_REACTION_DISPATCH_RULE_IDS),
    }
    return {
        "schemaVersion": 1,
        "recordType": "semantic-action-source-index",
        "scope": "entire mechanically derived 60-card base Action family across the six base Characters; all physical copies, seven root segments, two sheets, twenty-nine base selector-gap variants, shared back, current official occurrences, FAQ rulings, and sixty licensed rows remain independent",
        "derivationPolicy": "Derive physical membership only from exact base Character kit/container ancestry, ActionDeck tags, root deck GUIDs, raw full CardID/GUID/CustomDeck/FaceURL/BackURL tuples, and reviewed generated sheet/hash/grid/cell evidence. Never join by title, Character name alone, body similarity, folder/order/cell, source sheet, CardID modulo, licensed key, or aggregate multiplicity.",
        "counts": counts,
        "titleMultiplicity": dict(sorted(title_counts.items())),
        "rootDeckEvidence": root_evidence,
        "characterDecks": character_decks,
        "sourceFaceAssets": source_assets,
        "faces": physical_faces,
        "sourceSheets": [
            {"sourceId": "SRC-ACTION-SHEET-5674", "occurrenceId": "TTS-ACTION-PARENT-SHEET-5674", "sourcePath": SHEET_5674_PATH, "sourceSha256": _sha(repo / SHEET_5674_PATH), "customDeckId": "5674", "url": SHEET_5674_URL, "grid": {"columns": 9, "rows": 5, "cellWidth": 1052, "cellHeight": 1433}, "selectedCells": sorted(row["generatedCell"] for row in physical_faces if row["customDeckId"] == "5674"), "selectorGapCells": sorted(row["generatedCell"] for row in gap_asset_rows), "expansionCellsExcluded": [], "globalReferenceCount": sheet_5674_provenance["refs"], "parentSheetNotRulesFace": True},
            {"sourceId": "SRC-ACTION-SHEET-5675", "occurrenceId": "TTS-ACTION-PARENT-SHEET-5675", "sourcePath": SHEET_5675_PATH, "sourceSha256": _sha(repo / SHEET_5675_PATH), "customDeckId": "5675", "url": SHEET_5675_URL, "grid": {"columns": 9, "rows": 5, "cellWidth": 1052, "cellHeight": 1433}, "selectedCells": [10, 11, 12, 13, 14], "selectorGapCells": [], "expansionCellsExcluded": [*range(0, 10), *range(15, 45)], "globalReferenceCount": sheet_5675_provenance["refs"], "parentSheetNotRulesFace": True},
        ],
        "sharedBack": {"sourceId": "SRC-ACTION-SHARED-BACK", "occurrenceId": "TTS-ACTION-SHARED-BACK", "sourcePath": SHARED_BACK_PATH, "sourceSha256": _sha(repo / SHARED_BACK_PATH), "url": SHARED_BACK_URL, "physicalSelectorReferences": 60, "globalReferenceCount": back_provenance["refs"], "rulesFaceCounted": False},
        "contractorCompositionEvidence": {
            "officialRulebook": "The Contractor has 5 cards marked Contractor and 5 marked Contractor: Consultant; ignore the distinction in the base game.",
            "ttsKitRootGuid": "18a2ab",
            "ttsSharedRootGuid": "6855bb",
            "luaEvidence": ["assets/tts-mod/extract/v2/lua_script.lua:lines 4951–4979", "assets/tts-mod/extract/v2/lua_script.lua:lines 12995–12997"],
            "finalPhysicalCopies": 10,
            "orderingPolicy": "membership only; both roots are shuffled together and no source-backed final deck order is asserted",
        },
        "licensedDigitalOccurrences": licensed,
        "crossSourceIdentityBoundary": {
            "licensed": "All sixty ACTION_CARDS_DATA rows remain independent licensed occurrences. No title/Character/body/order/multiplicity join to any TTS GUID copy is asserted.",
            "official": "Current official visible examples control only their exact publisher occurrences and general procedures; none identifies a TTS root GUID or physical copy.",
            "selectedVersusCorpus": "Selected pixel evidence and stale corpus/canonical projections remain separately recorded on each affected source asset.",
        },
        "officialVisibleOccurrences": {"faces": official_faces, "backs": official_backs, "anatomyVisualUnit": "RB-P13-V01"},
        "faqOccurrences": faq_occurrences,
        "familyCountEvidence": {
            "official": {"total": 60, "perCharacter": 10, "characters": 6, "source": "rulebook component list and setup"},
            "tts": {"rootSegments": 7, "physicalFaces": 60, "perCharacter": per_character, "rawSaveSha256": raw_sha},
            "licensed": {"rows": 60, "perCharacterPrefix": {prefix: sum(row["key"].startswith(prefix + "_") for row in licensed) for prefix in ("CombatEngineer", "ContractorConsultant", "HeavyGunOperator", "MedicalSupport", "Officer", "Recon")}, "identityLinksToTts": 0},
            "backlog": {"faceUnitIds": face_unit_ids, "linkedUnitIds": linked_backlog_ids, "faceTupleCount": len(face_unit_ids)},
        },
        "excludedContent": {
            "expansionCharacterActionRoots": excluded_roots,
            "characterDraftDeck": {"guid": "2abdf6", "boundary": "Character-selection cards, not Action rules faces."},
            "contaminationDeck": {"guid": "7e89ea", "boundary": "Separate Contamination family despite common Action back and action-like GMNotes."},
            "startingItems": {"luaRole": "startItemDeck", "guid": "f71196", "boundary": "Character/Starting Items are not Action cards."},
            "parentSheetBoundary": "Both 9x5 parent sheets are provenance, never extra rules faces.",
            "backBoundary": "The shared BackURL is a hidden-information side, not a sixty-first Action face.",
            "selectorGapBoundary": "Twenty-nine source-clear base-Character cells on CustomDeck 5674 have no selected base-root selector and remain variants, not physical copies.",
            "crossCharacterBoundary": "A cell or direct asset printed for one Character never enters another Character deck without that exact root's full selector.",
            "expansionSheetBoundary": "CustomDeck 5675 cells 0–9 and 15–44 are expansion Character cells and remain outside base semantics.",
            "duplicateReferenceBoundary": "Root, child, crop, corpus, selected evidence, official, licensed, and backlog references are evidence links rather than extra physical cards.",
        },
    }


def action_source_registry_rows(source_index: dict) -> list[dict]:
    rows = []
    raw_sha = source_index["familyCountEvidence"]["tts"]["rawSaveSha256"]
    for root in source_index["rootDeckEvidence"]:
        rows.append({
            "sourceId": root["sourceId"], "authority": "source-bound-component-scan",
            "version": f"TTS base Action root segment / {root['character']} / deck {root['deckGuid']}",
            "path": RAW_SAVE_PATH, "sha256": raw_sha, "occurrenceId": f"TTS-ACTION-ROOT-{root['deckGuid'].upper()}",
            "evidenceIndexPath": OBJECTS_PATH, "evidenceRecord": root["deckGuid"], "provenanceIndexPath": LUA_PATH,
        })
    for sheet in source_index["sourceSheets"]:
        rows.append({
            "sourceId": sheet["sourceId"], "authority": "source-bound-component-scan",
            "version": f"TTS base/expansion Action 9x5 parent sheet / CustomDeck {sheet['customDeckId']}",
            "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"],
            "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH,
        })
    back = source_index["sharedBack"]
    rows.append({
        "sourceId": back["sourceId"], "authority": "source-bound-component-scan", "version": "TTS shared Action/Contamination card back",
        "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"],
        "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH,
    })
    for asset in source_index["sourceFaceAssets"]:
        if not asset.get("sourceId"):
            continue
        rows.append({
            "sourceId": asset["sourceId"], "authority": "source-bound-component-scan",
            "version": f"TTS base Action unselected generated source variant / CustomDeck 5674 / cell {asset['generatedCell']}",
            "path": asset["sourcePath"], "sha256": asset["sourceSha256"], "occurrenceId": f"TTS-ACTION-VARIANT-5674-CELL-{asset['generatedCell']:02d}",
            "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": asset["sourceSha256"], "provenanceIndexPath": PROGRESS_PATH,
        })
    existing_versions = {
        "SRC-CARD-DUCK": "Contractor: Consultant Duck and Cover face",
        "SRC-CARD-REST": "project-owner-reviewed canonical Rest face",
        "SRC-CARD-REST-MEDICAL": "Medical Support Rest source variant",
        "SRC-CARD-SEARCH-MEDICAL": "Medical Support Search face",
    }
    for face in source_index["faces"]:
        rows.append({
            "sourceId": face["sourceId"], "authority": "source-bound-component-scan",
            "version": existing_versions.get(face["sourceId"], face["sourceVersion"]),
            "path": face["sourcePath"], "sha256": face["sourceSha256"], "occurrenceId": face["occurrenceId"],
            "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": face["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH,
        })
    bga = source_index["licensedDigitalOccurrences"][0]
    rows.append({
        "sourceId": "SRC-BGA-ACTION-CARDS", "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / ACTION_CARDS_DATA",
        "path": BGA_PATH, "sha256": bga["sourceSha256"], "occurrenceId": "ACTION_CARDS_DATA",
        "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "ACTION_CARDS_DATA",
    })
    unique = {}
    for row in rows:
        unique[row["sourceId"]] = row
    return [unique[source_id] for source_id in sorted(unique)]


def _target(target_id: str, eligible: list[str], *, selector: str = "P-OWNER", mode: str = "player-choice", minimum: int = 1, maximum=1, visibility: str = "public") -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": visibility}


def _build_face_effect(face: dict, assertion_id: str, decision, condition, operation) -> tuple[list[str], list[str], list[dict], list[dict], list[dict], list[dict], list[dict], list[dict], list[str]]:
    kind = face["effectKind"]
    code = _code(face["character"], face["ttsCardId"], face["ttsCardGuid"])
    terms = ["icon.actionCard", "term.action"]
    taxa = ["tax.entity.component.card.action", "tax.process.action"]
    preconditions = []
    decisions = []
    costs = []
    targets = []
    ops = []
    outcomes = []
    unresolved = [qid for qid, rule_ids in ACTION_QUESTION_BLOCKS.items() if face["semanticRuleId"] in rule_ids]

    def add(op_type: str, modality: str, subject: str, obj: str, *, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None, panel_ids=None):
        op = operation(f"S{len(ops)+1:02d}", len(ops)+1, op_type, modality, subject, obj, [assertion_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref, transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
        op["sourcePanelIds"] = panel_ids or [panel["panelId"] for panel in face["panels"] if panel["operative"]]
        ops.append(op)
        return op

    branches = [panel for panel in face["panels"] if panel["role"] in {"action-effect", "command-effect"}]
    branch_decision = None
    if len(branches) > 1:
        branch_decision = f"D-{code}-BRANCH"
        decisions.append(decision(branch_decision, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", [panel["exactText"] for panel in branches]))
        add("choose", "must", "P-OWNER", "one exact printed OR branch", decision_ref=branch_decision, panel_ids=[panel["panelId"] for panel in branches])

    if face["notInCombat"]["status"] == "source-resolved":
        terms.append("icon.notInCombat"); taxa.append("tax.state.combat.not-in-combat")
        preconditions.append(condition(f"C-{code}-NIC", "predicate", [{"predicate": "acting Character is Not In Combat"}], [assertion_id]))
    elif face["notInCombat"]["status"] == "literal-unresolved":
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-057 exact source-local upper-right restriction denotation", notes="No Not In Combat default is imported from licensed noIntruders, corner position, color, crossed-gun appearance, or sibling cards.")

    def pay(resource: str, quantity: int, label: str, *, guard: str | None = None):
        terms.append(resource)
        did = f"D-{code}-COST-{len(costs)+1:02d}"
        decisions.append(decision(did, "P-OWNER", "player-choice", quantity, quantity, False, "owner-private-until-payment", [f"exact owned {resource} resource(s) satisfying {label}"]))
        cid = f"COST-{code}-{len(costs)+1:02d}"
        costs.append({"costId": cid, "payerRef": "P-OWNER", "resourceTermId": resource, "quantity": quantity, "selectionDecisionRef": did, "transition": {"from": "owner supply/hand/attached slot", "to": "source-defined discard/spent destination"}})
        add("pay-cost", "must", "P-OWNER", cid, conditions=[guard] if guard else None, decision_ref=did)
        return cid

    def choose_target(suffix: str, eligible: list[str], label: str, *, consent=False, guard=None, mode=None):
        did = f"D-{code}-{suffix}"
        decisions.append(decision(did, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", [label]))
        tid = f"T-{code}-{suffix}"
        targets.append(_target(tid, eligible, mode=mode or ("player-choice-with-consent" if consent else "player-choice")))
        add("select-target", "must", "P-OWNER", label, conditions=[guard] if guard else None, decision_ref=did, target_ref=tid)
        return did, tid

    b1 = "printed branch 1 selected" if branch_decision else None
    b2 = "printed branch 2 selected" if branch_decision else None

    if kind == "demolition":
        terms.append("icon.malfunction"); taxa.extend(["tax.entity.spatial.door", "tax.entity.component.marker.malfunction"])
        _, door = choose_target("DOOR", ["tax.entity.spatial.door"], "one accessible Door", guard=b1)
        add("set-state", "must", "P-RULES", "selected Door becomes Destroyed", conditions=[b1] if b1 else None, target_ref=door)
        add("place-component", "must", "P-RULES", "one Malfunction marker in acting Character's Room", conditions=[b2] if b2 else None)
    elif kind in {"fast-repairs", "repairs", "repairs-accessible"}:
        terms.append("icon.malfunction"); taxa.extend(["tax.entity.spatial.door", "tax.entity.component.marker.malfunction"])
        if kind != "fast-repairs": pay("icon.actionCard", 1, "printed Malfunction-discard branch", guard=b1)
        _, malfunction = choose_target("MALFUNCTION", ["tax.entity.component.marker.malfunction"], "one source-legal local Malfunction marker", guard=b1)
        add("remove-component", "must", "P-RULES", "selected Malfunction marker", conditions=[b1] if b1 else None, target_ref=malfunction)
        _, door = choose_target("DOOR", ["tax.entity.spatial.door"], "one accessible Door" if kind == "repairs-accessible" else "one local Door", guard=b2)
        state_decision = f"D-{code}-DOOR-STATE"
        decisions.append(decision(state_decision, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Open", "Closed"]))
        add("set-state", "must", "P-RULES", "selected Door Open or Closed subject to Door constraints", conditions=[b2] if b2 else None, decision_ref=state_decision, target_ref=door)
    elif kind in {"secure", "secure-no-cost", "basic-secure"}:
        terms.extend(["icon.secure"]); taxa.extend(["tax.entity.component.token.secure", "tax.entity.spatial.corridor"])
        if kind == "basic-secure": pay("icon.actionCard", 1, "either selected branch")
        add("place-component", "must", "P-RULES", "2 Secure tokens in acting Character's Room", conditions=[b1] if b1 else None, repeat={"quantity": 2, "finiteSupplyAndRoomCapacity": True})
        if kind == "secure": pay("icon.actionCard", 1, "Reinforce branch", guard=b2)
        _, corridor = choose_target("CORRIDOR", ["tax.entity.spatial.corridor"], "one empty adjacent Corridor leading to a Room with a Character or Robot", guard=b2)
        add("set-state", "must", "P-RULES", "selected Corridor Reinforced", conditions=[b2] if b2 else None, target_ref=corridor)
    elif kind in {"rest", "rest-medical"}:
        add("invoke-process", "must", "P-ACTOR", "exact Rest variant over the Infection Procedure", invoke="SEM-ACT-REST-001", notes="The exact physical face remains selected by full occurrence identity; the reusable procedure owns scan and destination precedence.")
    elif kind == "search":
        if face["semanticRuleId"] in SEARCH_LOCAL_RULE_IDS:
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-058 exact source-local Search octagon denotation and corresponding Item-deck mapping")
            add("invoke-process", "if-able", "P-ACTOR", "official Search procedure only after the local source mapping is established", conditions=["SEM-Q-058 establishes the source-local Item Icon mapping"], invoke="SEM-ACT-SEARCH-001")
        else:
            add("invoke-process", "must", "P-ACTOR", "official Search procedure", invoke="SEM-ACT-SEARCH-001")
    elif kind == "explosives":
        terms.extend(["icon.grenadeToken", "icon.yellowItem"]); taxa.extend(["tax.entity.component.token.tactical-gear.grenade", "tax.entity.spatial.corridor", "tax.entity.spatial.room"])
        pay("icon.grenadeToken", 1, "new-Corridor branch", guard=b1)
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-071 legal endpoint, orientation, component supply, and placement procedure", conditions=[b1])
        add("place-component", "if-able", "P-RULES", "one new Corridor between acting Room and another Explored Room", conditions=[b1, "SEM-Q-071 establishes a legal placement"])
        add("place-component", "if-able", "P-RULES", "one Grenade Tactical Gear token gained by acting Character", conditions=[b2, "acting Room has a Yellow Item Icon"], repeat={"quantity": 1, "finiteSupply": True})
    elif kind == "tactical-retreat":
        terms.extend(["icon.ammoToken", "icon.character", "icon.intruder"]); taxa.extend(["tax.entity.component.token.tactical-gear.ammo", "tax.entity.spatial.corridor", "tax.entity.agent.character"])
        pay("icon.actionCard", 1, "printed additional Action-card payment")
        pay("icon.ammoToken", 1, "Ammo from one selected Weapon")
        _, corridor = choose_target("CORRIDOR", ["tax.entity.spatial.corridor"], "one empty adjacent Corridor")
        _, companion = choose_target("COMPANION", ["tax.entity.agent.character"], "zero or one consenting co-located other Character", consent=True)
        add("invoke-process", "must", "P-ACTOR", "Movement through selected empty Corridor with only printed card costs", target_ref=corridor, invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False, "companionTargetRef": companion, "companionNoiseRoll": False, "preventedAttackScope": "Opportunity Attacks under FAQ FQ-P02-U16"}, notes="SEM-Q-073 retains interrupt and continuation boundaries; Hazard-result Attacks are not prevented.")
    elif kind == "pyrotechnics":
        terms.extend(["icon.fire", "icon.grenadeToken", "icon.shootDieCritical", "icon.intruder"]); taxa.extend(["tax.entity.component.marker.fire", "tax.entity.component.token.tactical-gear.grenade", "tax.entity.spatial.corridor", "tax.entity.agent.intruder"])
        add("remove-component", "must", "P-RULES", "one Fire marker in acting Character's Room", conditions=[b1])
        pay("icon.grenadeToken", 1, "critical-result branch", guard=b2)
        _, corridor = choose_target("CORRIDOR", ["tax.entity.spatial.corridor"], "one adjacent Corridor", guard=b2)
        add("invoke-process", "must", "P-RULES", "Shoot-die Critical result against every Intruder in selected Corridor", conditions=[b2], target_ref=corridor, repeat={"scope": "all Intruders in target Corridor", "completeEachTargetBeforeNext": True})
    elif kind == "computer-skills":
        terms.append("icon.computer"); taxa.extend(["tax.entity.spatial.room", "tax.entity.spatial.door", "tax.process.action.use-room"])
        preconditions.append(condition(f"C-{code}-COMPUTER", "predicate", [{"predicate": "acting Character is in a Computer Room"}], [assertion_id]))
        add("invoke-process", "must", "P-ACTOR", "current Room effect without a second Basic-Action card cost", conditions=[b1], invoke="SEM-USE-ROOM-001", repeat={"includeBasicActionCardCost": False})
        _, door = choose_target("DOOR", ["tax.entity.spatial.door"], "one Door in the Facility", guard=b2)
        state_decision = f"D-{code}-DOOR-STATE"; decisions.append(decision(state_decision, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Open", "Closed"]))
        add("set-state", "must", "P-RULES", "selected Door Open or Closed subject to Door constraints", conditions=[b2], decision_ref=state_decision, target_ref=door)
    elif kind in {"chain-command", "chain-command-reaction"}:
        terms.extend(["icon.lander", "term.command"]); taxa.extend(["tax.entity.component.token.lander", "tax.entity.agent.character"])
        add("move-entity", "must", "P-OWNER", "Lander token one space in either direction on Round track", conditions=[b1])
        add("invoke-process", "must", "P-OWNER", "exact printed lower-Rank Move/Shoot/Burst Command", conditions=[b2], invoke="SEM-ACTION-CARD-COMMAND-001", repeat={"sourceRange": "owner's Room or neighboring Room", "sourceChoicesOwnedBy": "effect owner"})
    elif kind == "fast-reload":
        terms.append("icon.ammoToken"); taxa.extend(["tax.entity.component.card.item.weapon", "tax.entity.component.token.tactical-gear.ammo"])
        _, weapon = choose_target("WEAPON", ["tax.entity.component.card.item.weapon"], "one owned Weapon")
        order_decision = f"D-{code}-ORDER"; decisions.append(decision(order_decision, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Reload then Shoot/Burst", "Shoot/Burst then Reload"]))
        attack_decision = f"D-{code}-ATTACK"; decisions.append(decision(attack_decision, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Shoot", "Burst"]))
        add("choose", "must", "P-OWNER", "printed two-operation order", decision_ref=order_decision, target_ref=weapon)
        add("invoke-process", "must", "P-ACTOR", "Reload selected Weapon at the owner-selected position", decision_ref=order_decision, target_ref=weapon, invoke="SEM-AMMO-TOKEN-LIFECYCLE-001", repeat={"position": "first or second as selected"})
        add("invoke-selected-process", "must", "P-ACTOR", "Shoot or Burst with selected Weapon at the remaining position", decision_ref=attack_decision, target_ref=weapon, repeat={"includeBasicActionCardCost": False, "position": "first or second as selected"})
    elif kind == "continuous-fire":
        terms.append("icon.ammoToken"); taxa.extend(["tax.entity.component.card.item.weapon.ranged", "tax.entity.spatial.corridor"])
        preconditions.append(condition(f"C-{code}-BF", "predicate", [{"predicate": "BF Gun has at least one Ammo token"}], [assertion_id]))
        _, corridor = choose_target("CORRIDOR", ["tax.entity.spatial.corridor"], "one adjacent Corridor")
        subset = f"D-{code}-CARDS"; decisions.append(decision(subset, "P-OWNER", "player-choice", 0, None, True, "owner-private-until-payment", ["any subset of owned Action cards"]));
        add("transition-zone", "may", "P-OWNER", "selected Action cards as one Hit each", decision_ref=subset, transition={"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}, repeat={"oneHitPerSelectedCard": True})
        add("place-component", "must", "P-OWNER", "one Hit in selected Corridor per discarded Action card", target_ref=corridor, repeat={"quantityFromDecisionRef": subset, "allocation": "SEM-Q-062"})
        burst = f"D-{code}-BURST"; decisions.append(decision(burst, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "Burst with BF Gun"]))
        add("invoke-process", "may", "P-ACTOR", "Burst with BF Gun", decision_ref=burst, invoke="SEM-ACT-BURST-001", repeat={"includeBasicActionCardCost": False})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-062 zero-card legality, Hit allocation, and optional Burst boundary")
    elif kind == "forcing-fire":
        terms.extend(["icon.ammoToken", "icon.intruder"]); taxa.extend(["tax.entity.component.card.item.weapon.ranged", "tax.entity.agent.intruder"])
        _, weapon = choose_target("WEAPON", ["tax.entity.component.card.item.weapon.ranged"], "one source-legal owned Ranged Weapon")
        pay("icon.ammoToken", 1, "Ammo from selected Ranged Weapon")
        add("invoke-process", "must", "P-ACTOR", "Repel all Intruders from acting Character's Room", target_ref=weapon, invoke="SEM-INTRUDER-REPEL-001", repeat={"scope": "all Intruders in Room"})
    elif kind == "breakthrough":
        terms.extend(["icon.ammoToken", "icon.intruder"]); taxa.extend(["tax.entity.component.card.item.weapon.ranged", "tax.entity.spatial.corridor"])
        _, weapon = choose_target("WEAPON", ["tax.entity.component.card.item.weapon.ranged"], "one loaded Weapon")
        _, corridor = choose_target("CORRIDOR", ["tax.entity.spatial.corridor"], "one legal adjacent Burst Corridor")
        add("invoke-process", "must", "P-ACTOR", "Burst with selected Weapon at selected Corridor", target_ref=corridor, invoke="SEM-ACT-BURST-001", repeat={"includeBasicActionCardCost": False, "weaponTargetRef": weapon})
        move_decision = f"D-{code}-MOVE"; decisions.append(decision(move_decision, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "Move through Bursted Corridor"]))
        add("invoke-process", "may", "P-ACTOR", "Movement through the Bursted Corridor with printed Attack prevention", decision_ref=move_decision, target_ref=corridor, invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False, "preventedAttackScope": "Opportunity Attacks under FAQ"}, notes="SEM-Q-073 retains exact interrupt/continuation boundaries.")
    elif kind == "field-surgery":
        terms.extend(["icon.medpackToken"]); taxa.extend(["tax.entity.agent.character", "tax.entity.component.card.serious-wound", "tax.entity.component.token.tactical-gear.medpack"])
        pay("icon.actionCard", 1, "printed Wound-discard branch cost")
        _, target = choose_target("CHARACTER", ["tax.entity.agent.character"], "acting Character or one consenting Character in the same Room", consent=True)
        add("invoke-process", "must", "target Character's owner", "discard one owner-selected Serious Wound", target_ref=target, invoke="SEM-SERIOUS-WOUND-DISCARD-001")
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-065 Medpack-payment versus target-Contamination owner/order", target_ref=target)
    elif kind == "hippocratic-oath":
        terms.extend(["icon.character", "icon.intruder"]); taxa.extend(["tax.entity.agent.character", "tax.entity.agent.intruder"])
        preconditions.append(condition(f"C-{code}-WOUNDED-OTHER", "predicate", [{"predicate": "another Character with at least one Serious Wound is in acting Character's Room"}], [assertion_id]))
        _, intruder = choose_target("INTRUDER", ["tax.entity.agent.intruder"], "one Intruder in acting Character's Room")
        add("place-component", "must", "P-RULES", "2 Hits on selected Intruder", target_ref=intruder, repeat={"quantity": 2})
        attack = f"D-{code}-ATTACK"; decisions.append(decision(attack, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Shoot", "Melee Attack"]))
        add("invoke-selected-process", "must", "P-ACTOR", "Shoot or Melee Attack the same selected Intruder", decision_ref=attack, target_ref=intruder, notes="SEM-Q-066 retains legality/continuation if the setup Hits change target eligibility.")
    elif kind == "first-aid":
        terms.extend(["icon.characterHealth", "icon.greenItem", "icon.medpackToken"]); taxa.extend(["tax.entity.agent.character", "tax.state.health.point", "tax.entity.component.token.tactical-gear.medpack"])
        _, target = choose_target("CHARACTER", ["tax.entity.agent.character"], "acting Character or one consenting co-located Character", consent=True, guard=b1)
        add("invoke-process", "must", "P-ACTOR", "restore 1 Character Health", conditions=[b1], target_ref=target, invoke="SEM-RESTORE-HEALTH-001", repeat={"sourceMaximum": 1})
        add("place-component", "must", "P-RULES", "one Medpack Tactical Gear token gained by acting Character", conditions=[b2, "acting Room has a Green Item Icon"], repeat={"quantity": 1, "finiteSupply": True})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-065 target consent and branch ownership boundary")
    elif kind == "combat-drugs":
        terms.extend(["icon.medpackToken", "icon.character"]); taxa.extend(["tax.entity.agent.character", "tax.entity.component.token.tactical-gear.medpack"])
        pay("icon.medpackToken", 1, "printed cost")
        _, target = choose_target("CHARACTER", ["tax.entity.agent.character"], "one consenting Character in acting Character's Room", consent=True)
        add("invoke-process", "must", "target Character", "draw Action cards until that Character has 3 Action cards in hand", target_ref=target, invoke="SEM-ACTION-CARD-DRAW-001", repeat={"targetHandCount": 3, "finishEachDrawBeforeNext": True})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-065 consent/target and SEM-Q-072 finite draw-shortage boundaries", target_ref=target)
    elif kind == "weak-spots":
        terms.append("icon.intruder"); taxa.append("tax.entity.agent.intruder")
        _, intruder = choose_target("INTRUDER", ["tax.entity.agent.intruder"], "one Intruder in acting Character's Room")
        add("place-component", "must", "P-RULES", "1 Hit on selected Intruder", target_ref=intruder)
        attack = f"D-{code}-ATTACK"; decisions.append(decision(attack, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Shoot", "Melee Attack"]))
        add("invoke-selected-process", "must", "P-ACTOR", "Shoot or Melee Attack the same selected Intruder", decision_ref=attack, target_ref=intruder, notes="SEM-Q-066 retains legality/continuation if the setup Hit changes target eligibility.")
    elif kind == "duck-and-cover":
        pay("icon.actionCard", 1, "printed additional card")
        add("invoke-process", "must", "P-ACTOR", "Move with prevention of exactly one Opportunity Attack", invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False, "preventedOpportunityAttacks": 1}, notes="FAQ FQ-P02-U16 excludes Hazard-result Attacks; SEM-Q-073 retains selection and interrupt order.")
    elif kind == "move-quietly":
        taxa.extend(["tax.entity.spatial.room", "tax.entity.spatial.corridor"])
        _, room = choose_target("ROOM", ["tax.entity.spatial.room"], "one adjacent Discovered Room")
        add("invoke-process", "must", "P-ACTOR", "Move to selected Discovered Room without a Noise roll", target_ref=room, invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False, "postMovementNoiseRoll": False})
    elif kind == "always-prepared":
        taxa.extend(["tax.entity.spatial.room", "tax.entity.component.card.item", "tax.entity.agent.intruder"])
        add("invoke-process", "must", "P-ACTOR", "Use current Room without a second Basic-Action card cost", conditions=[b1], invoke="SEM-USE-ROOM-001", repeat={"includeBasicActionCardCost": False})
        add("resolve-attacks", "must", "all Intruders in acting Character's Room", "acting Character", conditions=[b1], repeat={"orderAndContinuation": "SEM-Q-063"})
        pay("icon.actionCard", 1, "draw-two-Items branch", guard=b2)
        deck_choice = f"D-{code}-ITEM-DECK"; decisions.append(decision(deck_choice, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one Item deck"]));
        add("choose", "must", "P-OWNER", "one Item deck", conditions=[b2], decision_ref=deck_choice)
        add("draw-random", "must", "P-OWNER", "2 Items from selected deck", conditions=[b2], decision_ref=deck_choice, repeat={"quantity": 2, "shortage": "SEM-Q-064"})
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-064 optional keep cardinality, privacy, destination, and deck-shortage procedure", conditions=[b2])
    elif kind == "fire-at-will":
        terms.extend(["icon.lander", "term.command"]); taxa.extend(["tax.entity.component.token.lander", "tax.entity.agent.character", "tax.entity.spatial.room", "tax.entity.spatial.corridor"])
        add("move-entity", "must", "P-OWNER", "Lander token one space in either direction on Round track", conditions=[b1])
        _, room = choose_target("ROOM", ["tax.entity.spatial.room"], "Officer's Room or one neighboring Room", guard=b2)
        add("invoke-selected-process", "must", "each Character in selected Room in Turn order", "Burst at a Corridor selected separately by Officer; each Bursting Character chooses their Weapon", conditions=[b2], target_ref=room, repeat={"order": "Turn order", "corridorOwner": "Officer", "differentCorridorPerCharacter": True, "weaponOwner": "each Bursting Character", "includeBasicActionCardCost": "SEM-Q-059"})
    elif kind == "officer-channel":
        terms.extend(["icon.lander", "term.command"]); taxa.append("tax.entity.component.token.lander")
        add("move-entity", "must", "P-OWNER", "Lander token one space in either direction on Round track", conditions=[b1])
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-067 nested Command card selection, reveal, Reaction, cost, discard, and Facility-Room substitution", conditions=[b2])
    elif kind == "stay-calm-reaction":
        terms.extend(["icon.lander", "term.command"]); taxa.extend(["tax.entity.component.token.lander", "tax.entity.agent.character", "tax.entity.spatial.room"])
        add("move-entity", "must", "P-OWNER", "Lander token one space in either direction on Round track", conditions=[b1])
        _, room = choose_target("ROOM", ["tax.entity.spatial.room"], "Officer's Room or one neighboring Room", guard=b2)
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-068 source-local upright card/tile glyph identity", conditions=[b2], target_ref=room)
        add("invoke-process", "if-able", "each Character in selected Room in Turn order", "draw one source-defined card only after SEM-Q-068 resolves the glyph", conditions=[b2, "SEM-Q-068 establishes Action card"], target_ref=room, invoke="SEM-ACTION-CARD-DRAW-001", repeat={"perCharacter": 1, "order": "Turn order", "shortage": "SEM-Q-072"})
    elif kind == "lets-go":
        terms.append("icon.lander"); taxa.extend(["tax.entity.component.token.lander", "tax.entity.agent.character", "tax.entity.spatial.room"])
        add("move-entity", "must", "P-OWNER", "Lander token one space in either direction on Round track", conditions=[b1])
        _, companion = choose_target("COMPANION", ["tax.entity.agent.character"], "one other Character moved with the Officer under SEM-Q-069", guard=b2)
        add("invoke-process", "must", "P-ACTOR", "one Movement with selected companion; only Officer makes Noise roll", conditions=[b2], target_ref=companion, invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False, "companionNoiseRoll": False, "consentAndAttackWindows": "SEM-Q-069/SEM-Q-073"})
    elif kind == "sprint":
        terms.append("icon.oxygen"); taxa.append("tax.value.resource.oxygen")
        add("invoke-process", "must", "P-ACTOR", "Move", invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False})
        second = f"D-{code}-SECOND-MOVE"; decisions.append(decision(second, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "lose 1 Oxygen and Move again"]))
        add("change-value", "may", "P-ACTOR", "Oxygen -1", decision_ref=second, value_change={"amount": -1, "valueTaxonId": "tax.value.resource.oxygen"})
        add("invoke-process", "may", "P-ACTOR", "second Move", decision_ref=second, invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False})
    elif kind == "shoot-first":
        add("invoke-process", "must", "P-ACTOR", "Movement through one empty Corridor", invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False})
        attack = f"D-{code}-ATTACK"; decisions.append(decision(attack, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["decline", "Shoot during Movement", "Burst during Movement"]))
        add("invoke-selected-process", "may", "P-ACTOR", "Shoot or Burst at an owner-selected printed Movement window, including before Movement or immediately before an Intruder Attack", decision_ref=attack, notes="FAQ FQ-P02-U15 includes Intruders appearing from the Movement Noise roll; SEM-Q-073 retains interrupt/continuation order.")
    elif kind == "scouting":
        add("invoke-process", "must", "P-ACTOR", "Move Cautiously to a Discovered Room without paying the Basic Action card cost", conditions=[b1], invoke="SEM-ACT-MOVE-001", repeat={"includeBasicActionCardCost": False, "cautious": True})
        add("invoke-process", "must", "P-ACTOR", "Move through an Unexplored Corridor and resolve Exploration", conditions=[b2], invoke="SEM-ACT-EXPLORE-001", repeat={"includeBasicActionCardCost": False})
        add("invoke-process", "must", "P-ACTOR", "Search in the newly explored Room", conditions=[b2], invoke="SEM-ACT-SEARCH-001")
    elif kind == "taking-aim":
        attack = f"D-{code}-ATTACK"; decisions.append(decision(attack, "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Shoot", "Burst"]))
        add("invoke-selected-process", "must", "P-ACTOR", "Shoot or Burst without a second Basic-Action card cost", decision_ref=attack)
        reroll = f"D-{code}-REROLL"; decisions.append(decision(reroll, "P-OWNER", "player-choice", 0, 1, True, "public-on-declaration", ["accept first result", "reroll first result under SEM-Q-070"]))
        add("resolve-open-alternative", "may", "P-RULES", "SEM-Q-070 reroll scope and whether the second result must be accepted", decision_ref=reroll)
    else:
        raise AssertionError(f"unexpected Action effect kind: {kind}")

    if face["semanticRuleId"] in ACTION_QUESTION_BLOCKS["SEM-Q-061"]:
        add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-061 remaining actor-bound operations and final lifecycle after death/escape during resolution")

    unresolved = list(dict.fromkeys(unresolved))
    return terms, taxa, preconditions, decisions, costs, targets, ops, outcomes, unresolved


def build_action_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo
    records = []
    faces = source_index["faces"]
    face_by_rule = {row["semanticRuleId"]: row for row in faces}

    # Setup owns the exact six 10-card memberships, hidden deck zones, shuffle,
    # and initial five-card draw. Saved TTS sequence is provenance only.
    setup = record(
        "SEM-ACTION-DECK-SETUP-001", "Per-Character Action deck setup and initial hand", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-ACTION-SETUP-RB", "SRC-RULEBOOK", "printed page 8 / setup step 6 and Beginning of Game", ["preconditions", "informationPolicy", "operations", "partialResolution", "duration", "stacking"], "Take all Action cards for your Character, shuffle them face down beside the Character board with a discard space, then each player draws 5 Action cards. Contractor's five-plus-five printed distinction is ignored in the base game.", "docs/rulebooks/rulebook_text.txt:lines 2684–2690, 2741–2744")],
        ["icon.actionCard"], ["tax.entity.component.card.action", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile", "tax.scaffold.zone.hand"], [],
        timing("TW-ACTION-SETUP", "tax.entity.component.card.action", "when-triggered", "once-per-Character-at-setup"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ACTION-SETUP", "subjectRef": "exact ten-card deck membership, shuffled order, and five-card initial hand", "audience": "membership public by Character; order and hand identities owner-private", "revealTrigger": "source-defined card play/payment/Reaction", "secrecy": "other players receive only observable hand/deck/discard counts and public discards"}], [], [],
        [operation("S01", 1, "transition-zone", "must", "P-RULES", "each exact physical Action copy into its source-locked Character deck", ["SA-ACTION-SETUP-RB"], transition={"from": "game component supply", "to": "tax.scaffold.zone.deck"}, repeat={"characterDeckMembership": {deck["characterDeckId"]: deck["physicalOccurrenceIds"] for deck in source_index["characterDecks"]}, "noTitleOrCharacterNameOnlyJoin": True}), operation("S02", 2, "shuffle", "must", "P-RULES", "each six Character Action decks face down independently", ["SA-ACTION-SETUP-RB"], repeat={"perCharacter": 1}), operation("S03", 3, "invoke-process", "must", "each Character", "draw 5 Action cards", ["SA-ACTION-SETUP-RB"], invoke="SEM-ACTION-CARD-DRAW-001", repeat={"perCharacter": 5, "finishEachDrawBeforeNext": True})],
        {"policy": "ordered-complete", "unit": "one Character's exact deck setup and initial draw", "onImpossible": "use exact finite deck membership; no substitute, title merge, or expansion card is introduced"}, {"kind": "setup-and-persistent-zones"}, {"policy": "one independently shuffled 10-card Action deck and discard pile per Character"}, [], [], [])
    records.append(setup)

    play = record(
        "SEM-ACTION-CARD-PLAY-001", "Play an exact Action card occurrence", "source-backed-with-open-question", "dispatcher", "official-errata", "open-alternatives",
        [assertion("SA-ACTION-PLAY-RB", "SRC-RULEBOOK", "printed pages 12–14 / Basic Actions, Playing Action cards, Effects", ["preconditions", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Play an Action card costs 0 Action cards. Reveal the chosen card from hand, resolve one entirely resolvable printed effect, then place the card on top of the discard pile.", "docs/rulebooks/rulebook_text.txt:lines 2871–2875, 3161–3198"), assertion("SA-ACTION-PLAY-FAQ", "SRC-FAQ", "FQ-P02-U11", ["operations", "partialResolution"], "When a played Action card draws cards, complete those draws and any required Action-deck reshuffle before discarding the played card; it is not included in that reshuffle.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U11")],
        ["icon.actionCard", "term.action"], ["tax.entity.component.card.action", "tax.process.action", "tax.scaffold.zone.hand", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-ACTION-PLAY", "tax.process.temporal.turn", "during", "per-selected-Play-an-Action-card Basic Action"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-ACTOR", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed",
        [condition("C-ACTION-PLAY-LEGAL", "all", [{"predicate": "exact selected Action card is in this Character owner's hand"}, {"predicate": "one printed main effect is entirely resolvable"}, {"predicate": "any source-resolved Not In Combat restriction is satisfied"}], ["SA-ACTION-PLAY-RB"])],
        [decision("D-ACTION-PLAY-CARD", "P-OWNER", "player-choice", 1, 1, False, "owner-private-until-reveal", ["any exact owned physical Action-card occurrence satisfying C-ACTION-PLAY-LEGAL"])],
        [{"informationId": "I-ACTION-HAND", "subjectRef": "unselected Action/Contamination identities and order", "audience": "owner-private; other players may observe only total hand count", "revealTrigger": "never by selecting another card", "secrecy": "common backs must not disclose card family/title"}, {"informationId": "I-ACTION-PLAYED", "subjectRef": "selected face, declared branch/targets/costs, and results", "audience": "public", "revealTrigger": "play-card operation", "secrecy": "none after reveal"}],
        [{"costId": "COST-ACTION-PLAY", "payerRef": "P-OWNER", "resourceTermId": "icon.actionCard", "quantity": 0, "selectionDecisionRef": None, "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.hand"}}],
        [_target("T-ACTION-PLAY-CARD", ["tax.entity.component.card.action"], mode="deterministic-exact-face-filter", visibility="owner-private")],
        [operation("S01", 1, "play-card", "must", "P-OWNER", "selected exact Action-card occurrence", ["SA-ACTION-PLAY-RB"], decision_ref="D-ACTION-PLAY-CARD", target_ref="T-ACTION-PLAY-CARD", transition={"from": "tax.scaffold.zone.hand", "to": "sem.zone.card-in-resolution"}), operation("S02", 2, "invoke-selected-process", "must", "P-ACTOR", "exact occurrence-keyed main-effect semantic record", ["SA-ACTION-PLAY-RB"], decision_ref="D-ACTION-PLAY-CARD", target_ref="T-ACTION-PLAY-CARD", notes="Dispatch never uses title, Character name alone, body similarity, folder, sheet, cell, modulo, or licensed key."), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-061 remaining actor-bound operations after death/escape during resolution", ["SA-ACTION-PLAY-RB"]), operation("S04", 4, "transition-zone", "must", "P-RULES", "played Action card if it remains in resolution after its exact effect", ["SA-ACTION-PLAY-RB", "SA-ACTION-PLAY-FAQ"], transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"}, notes="Draws/renewal caused by this card finish before this transition, so the played card is not shuffled.")],
        {"policy": "all-or-nothing-selection", "unit": "one selected printed main effect on one exact physical occurrence", "onImpossible": "the card/effect cannot be selected; SEM-Q-061 retains only death/escape interruption continuation, never a legality default"}, {"kind": "instantaneous-Basic-Action-with-card-in-resolution"}, {"policy": "one selected exact copy per play; same titles in other decks remain separate"}, [], ["SEM-Q-061"], [])
    play["operations"][1]["dispatchRuleIds"] = list(ACTION_RULE_IDS)
    records.append(play)

    payment = record(
        "SEM-ACTION-CARD-PAYMENT-001", "Discard Action cards as costs without resolving effects", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-ACTION-PAY-RB", "SRC-RULEBOOK", "printed page 12 / Cost in Action cards", ["preconditions", "decisions", "informationPolicy", "costs", "operations", "partialResolution", "duration", "stacking"], "Pay an Action cost by discarding the required number of Action cards from hand face up to the discard pile; cards discarded as Basic-Action cost or by another effect do not resolve their printed effects.", "docs/rulebooks/rulebook_text.txt:lines 2921–2938")],
        ["icon.actionCard"], ["tax.entity.component.card.action", "tax.scaffold.zone.hand", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-ACTION-PAY", "tax.process.action", "when-triggered", "per-source-defined Action-card payment"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [],
        [decision("D-ACTION-PAY-CARDS", "P-OWNER", "player-choice", 0, None, True, "owner-private-until-payment", ["exact required number of owned Action cards; invocation supplies quantity"])],
        [{"informationId": "I-ACTION-PAY", "subjectRef": "selected paid card identities", "audience": "public after face-up discard", "revealTrigger": "payment", "secrecy": "unselected hand identities remain private"}], [], [],
        [operation("S01", 1, "transition-zone", "must", "P-OWNER", "exact selected payment cards face up without printed effects", ["SA-ACTION-PAY-RB"], decision_ref="D-ACTION-PAY-CARDS", transition={"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"}, repeat={"quantity": "source invocation's exact Action-card cost", "resolvePrintedEffects": False})],
        {"policy": "all-or-nothing-selection", "unit": "complete required Action-card payment", "onImpossible": "the enclosing Action/effect is illegal if its required payment cannot be made"}, {"kind": "immediate-payment-before-enclosing-effect"}, {"policy": "each exact card moves once and contributes no printed effect"}, [], [], [])
    records.append(payment)

    reaction = record(
        "SEM-ACTION-CARD-REACTION-001", "Play an exact Reaction panel", "source-backed-with-open-question", "dispatcher", "official-primary", "open-alternatives",
        [assertion("SA-ACTION-REACTION-RB", "SRC-RULEBOOK", "printed pages 13–14 / Reactions", ["preconditions", "decisions", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "When a Reaction condition is met, its owner may place the card in front of them, resolve the Reaction, then put it on top of the discard pile. A Reaction is not an Action; a player who Passed may still react.", "docs/rulebooks/rulebook_text.txt:lines 3067–3075, 3180–3186")],
        ["icon.actionCard", "term.reaction"], ["tax.entity.component.card.action", "tax.process.card-effect.reaction", "tax.scaffold.zone.hand", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-ACTION-REACTION", "tax.process.card-effect.reaction", "when-triggered", "per-met exact Reaction condition"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-ACTOR", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "may", [],
        [decision("D-ACTION-REACTION", "P-OWNER", "player-choice", 0, 1, True, "owner-private-until-play", ["decline", "play one exact eligible Reaction occurrence"])],
        [{"informationId": "I-ACTION-REACTION", "subjectRef": "eligible Reaction identities", "audience": "owner-private until one is played; played face/effect/result public", "revealTrigger": "play", "secrecy": "unplayed hand and Reaction availability are not disclosed"}], [], [_target("T-ACTION-REACTION", ["tax.entity.component.card.action"], mode="deterministic-exact-face-filter", visibility="owner-private")],
        [operation("S01", 1, "play-card", "may", "P-OWNER", "one exact eligible Reaction card", ["SA-ACTION-REACTION-RB"], decision_ref="D-ACTION-REACTION", target_ref="T-ACTION-REACTION", transition={"from": "tax.scaffold.zone.hand", "to": "sem.zone.card-in-resolution"}), operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-060 priority/ordering/stacking when multiple Reaction windows are simultaneously legal", ["SA-ACTION-REACTION-RB"], conditions=["a Reaction was played"]), operation("S03", 3, "invoke-selected-process", "must", "P-ACTOR", "exact occurrence-keyed Reaction effect", ["SA-ACTION-REACTION-RB"], conditions=["a Reaction was played"], target_ref="T-ACTION-REACTION"), operation("S04", 4, "transition-zone", "must", "P-RULES", "played Reaction card", ["SA-ACTION-REACTION-RB"], conditions=["a Reaction was played"], transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"})],
        {"policy": "replacement-effect", "unit": "one exact pending trigger and one exact Reaction copy", "onImpossible": "decline is legal; no priority, simultaneous ordering, or stack default is invented under SEM-Q-060"}, {"kind": "one pending source-defined trigger"}, {"policy": "each physical copy may be played once per time it is in hand; no title collapse"}, [], ["SEM-Q-060"], [])
    reaction["operations"][2]["dispatchRuleIds"] = list(ACTION_REACTION_DISPATCH_RULE_IDS)
    records.append(reaction)

    command = record(
        "SEM-ACTION-CARD-COMMAND-001", "Orders and Commands using another Character", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [assertion("SA-ACTION-COMMAND-RB", "SRC-RULEBOOK", "printed page 13 / Orders and Commands", ["preconditions", "decisions", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "The effect owner chooses the target of an ordered Action; passed Characters may be ordered. An order may never result in an Intruder Opportunity Attack. The effect owner chooses the Corridor when making another Character Burst.", "docs/rulebooks/rulebook_text.txt:lines 3095–3105"), assertion("SA-ACTION-COMMAND-DOOR", "SRC-FAQ", "FQ-P02-U10", ["preconditions", "operations"], "A Closed Door blocks commanding another Character through it.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10")],
        ["term.command", "term.reaction"], ["tax.entity.agent.character", "tax.process.action"], [],
        timing("TW-ACTION-COMMAND", "tax.process.action", "when-triggered", "per-printed Command branch"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-COMMANDER", "actor", "tax.entity.agent.character"), participant("P-ORDERED", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed",
        [condition("C-ACTION-COMMAND-LEGAL", "all", [{"predicate": "printed target range/rank condition is satisfied"}, {"predicate": "no Closed Door blocks the effect"}, {"predicate": "ordered Action would not cause an Opportunity Attack"}, {"predicate": "ordered Action is otherwise entirely resolvable"}], ["SA-ACTION-COMMAND-RB", "SA-ACTION-COMMAND-DOOR"])],
        [decision("D-ACTION-COMMAND-TARGET", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["one printed-range/rank eligible Character, including one who Passed"]), decision("D-ACTION-COMMAND-ACTION", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["Move", "Shoot", "Burst as permitted by the exact Command"])],
        [{"informationId": "I-ACTION-COMMAND", "subjectRef": "ordered Character, Action, targets, choices, payments/resources, and results", "audience": "public", "revealTrigger": "Command declaration", "secrecy": "ordered Character's unselected hand/Items remain private except source-required choices"}], [],
        [_target("T-ACTION-COMMAND-CHARACTER", ["tax.entity.agent.character"], mode="player-choice")],
        [operation("S01", 1, "select-target", "must", "P-OWNER", "one eligible ordered Character", ["SA-ACTION-COMMAND-RB"], decision_ref="D-ACTION-COMMAND-TARGET", target_ref="T-ACTION-COMMAND-CHARACTER"), operation("S02", 2, "choose", "must", "P-OWNER", "one exact printed ordered Action and all source-assigned targets", ["SA-ACTION-COMMAND-RB"], decision_ref="D-ACTION-COMMAND-ACTION", target_ref="T-ACTION-COMMAND-CHARACTER"), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-059 normal Action-card payment, non-card resources, weapon ownership, legality, and remaining choices", ["SA-ACTION-COMMAND-RB"]), operation("S04", 4, "invoke-selected-process", "if-able", "P-ORDERED", "ordered Move, Shoot, or Burst after SEM-Q-059 resolves its cost/resource contract", ["SA-ACTION-COMMAND-RB"], conditions=["C-ACTION-COMMAND-LEGAL", "SEM-Q-059 establishes required payment/resource handling"], decision_ref="D-ACTION-COMMAND-ACTION", target_ref="T-ACTION-COMMAND-CHARACTER")],
        {"policy": "all-or-nothing-selection", "unit": "one exact ordered Action", "onImpossible": "an Opportunity-Attack-producing or otherwise incomplete order is prohibited; payment/resource defaults remain prohibited by SEM-Q-059"}, {"kind": "one nested ordered Action"}, {"policy": "each exact Command branch resolves independently; Command headings do not merge card identities"}, [], ["SEM-Q-059"], [])
    records.append(command)

    variant = record(
        "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001", "Base Action physical/source-variant boundaries", "source-backed", "constraint", "official-primary", "source-composed",
        [assertion("SA-ACTION-VARIANT-RB", "SRC-RULEBOOK", "component list, setup, and visible examples", ["operations", "partialResolution", "duration", "stacking", "sourceVariants"], "The base game has 60 Action cards, 10 per Character; Contractor's five-plus-five printed labels are ignored in the base game.", "docs/rulebooks/rulebook_text.txt:lines 528–529, 2684–2690"), assertion("SA-ACTION-VARIANT-SHEET", "SRC-ACTION-SHEET-5674", "full 9x5 sheet and exact cell ledger", ["operations", "sourceVariants"], "The first Action sheet retains 16 selected physical cells and 29 base-Character selector-gap source variants.", "docs/rules/semantics/action-source-index.json"), assertion("SA-ACTION-VARIANT-BGA", "SRC-BGA-ACTION-CARDS", "ACTION_CARDS_DATA", ["operations", "sourceVariants"], "Sixty licensed Character/card rows remain independent lower-authority occurrences with no asserted TTS-copy identity links.", "docs/rules/source-extraction/secondary-evidence-index.json:ACTION_CARDS_DATA")],
        ["icon.actionCard"], ["tax.entity.component.card.action"], [],
        timing("TW-ACTION-VARIANTS", "tax.entity.component.card.action", "when-triggered", "per-source/identity comparison"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ACTION-VARIANTS", "subjectRef": "physical copy, root/deck membership, selected/gap cell, official occurrence, licensed occurrence, and representation provenance", "audience": "public corpus evidence", "revealTrigger": "continuous audit", "secrecy": "does not reveal live shuffled order or player hands"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "exact 60 physical occurrence IDs partition 10×6 and remain distinct", ["SA-ACTION-VARIANT-RB"]), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "29 base selector gaps and 40 expansion cells remain outside physical base membership", ["SA-ACTION-VARIANT-SHEET"]), operation("S03", 3, "evaluate-condition", "must", "P-RULES", "zero TTS-to-licensed copy identity links unless future independent evidence supplies one", ["SA-ACTION-VARIANT-BGA"])],
        {"policy": "per-proposed-source-merge", "unit": "one exact source occurrence/copy/variant assertion", "onImpossible": "retain independent records; never force title, Character, body, folder, sheet, cell, modulo, or multiplicity identity"}, {"kind": "persistent-evidence-boundary"}, {"policy": "not a game-effect stack; each source occurrence remains independent"}, [], [],
        [{"variantId": "SV-ACTION-SELECTOR-GAPS", "sourceId": "SRC-ACTION-SHEET-5674", "sourceAssertionId": "SA-ACTION-VARIANT-SHEET", "difference": "Twenty-nine source-clear base-Character cells are not selected by any exact base physical root.", "resolution": "Preserve as selector-gap variants, not physical deck copies or substitutes."}, {"variantId": "SV-ACTION-LICENSED", "sourceId": "SRC-BGA-ACTION-CARDS", "sourceAssertionId": "SA-ACTION-VARIANT-BGA", "difference": "Licensed names, wording, Reaction, Command, and noIntruders fields are independent from TTS physical selectors.", "resolution": "Retain all sixty rows without a one-to-one physical pairing."}])
    records.append(variant)

    # One main-effect record per exact physical occurrence.
    for face in faces:
        scan_id = f"SA-ACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}-SCAN"
        source_text = face["printedBody"] + (("\n\nREACTION\n" + face["reactionText"]) if face.get("reactionText") else "")
        assertions = [assertion(scan_id, face["sourceId"], face["occurrenceId"], ["preconditions", "timing", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "outcomes", "unresolvedQuestionRefs"], source_text, face["sourcePath"])]
        if face["effectKind"] == "fire-at-will":
            assertions.append(assertion(f"SA-ACTION-{face['characterCode']}-FIRE-FAQ", "SRC-FAQ", "FQ-P02-U14", ["decisions", "targets", "operations", "partialResolution"], "Officer chooses their Room or a neighboring Room and each Character Bursts in Turn order; Officer chooses each Corridor and each Character chooses their Weapon.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U14"))
        elif face["effectKind"] == "shoot-first":
            assertions.append(assertion(f"SA-ACTION-{face['characterCode']}-SHOOT-FIRST-FAQ", "SRC-FAQ", "FQ-P02-U15", ["timing", "operations"], "Shoot First may Shoot/Burst at Intruders that appear from the Movement Noise roll.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U15"))
        elif face["effectKind"] == "duck-and-cover":
            assertions.append(assertion(f"SA-ACTION-{face['characterCode']}-DUCK-FAQ", "SRC-FAQ", "FQ-P02-U16", ["operations", "partialResolution"], "Attack prevention during Movement applies only to Opportunity Attacks, not Hazard-result Attacks.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U16"))
        terms, taxa, preconditions, decisions, costs, targets, ops, outcomes, unresolved = _build_face_effect(face, scan_id, decision, condition, operation)
        highest = "official-errata" if len(assertions) > 1 else "source-bound-component-scan"
        result = record(
            face["semanticRuleId"], f"{face['character']} — {face['printedTitle']} physical Action occurrence {face['copyId']}", "source-backed-with-open-question" if unresolved else "source-backed", "component-effect", highest, "open-alternatives" if unresolved else "verbatim-structure",
            assertions, terms, taxa, [], timing(f"TW-ACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}", "tax.process.action.basic", "when-action-card-played", "per-exact-physical-occurrence"),
            [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-ACTOR", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed", [condition(f"C-ACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}-EXACT", "all", [{"predicate": f"dispatcher selected exact occurrence {face['occurrenceId']}"}, {"predicate": "one printed main effect/branch is entirely resolvable"}], [scan_id]), *preconditions], decisions,
            [{"informationId": f"I-ACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}", "subjectRef": "exact physical face, selected branch/costs/targets, operations, and results", "audience": "owner-private in hand; public after generic Action-card play reveals it", "revealTrigger": "SEM-ACTION-CARD-PLAY-001", "secrecy": "other hand identities and deck order remain hidden"}], costs, targets, ops,
            {"policy": "all-or-nothing-selection", "unit": "one exact physical occurrence's selected printed main effect branch", "onImpossible": "generic play lifecycle remains in SEM-ACTION-CARD-PLAY-001; unresolved glyph, owner, Command, Reaction, continuation, and draw questions receive no default"}, {"kind": "instantaneous-main-effect; Reaction panel is independently dispatched if present"}, {"policy": "each physical copy resolves separately; repeated/shared titles never collapse deck membership or semantic occurrence"}, outcomes, unresolved, [])
        for source_assertion in result["sourceAssertions"]:
            if source_assertion["assertionId"] == scan_id:
                source_assertion["textKind"] = "verbatim"
        records.append(result)

    # Reaction-effect records are distinct timing occurrences from main effects.
    for face in faces:
        reaction_rule = face.get("reactionRuleId")
        if not reaction_rule or reaction_rule == "SEM-REACTION-DUCK-001":
            continue
        scan_id = f"SA-ACTION-REACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}-SCAN"
        source_text = face.get("reactionText") or ""
        if not source_text:
            raise AssertionError(f"Action Reaction text missing: {face['occurrenceId']}")
        questions = ["SEM-Q-060"]
        if face["effectKind"] == "chain-command-reaction" and face["character"] != "Medical Support":
            questions.append("SEM-Q-074")
        if face["effectKind"] == "stay-calm-reaction":
            precondition_text = "an Intruder Attack would resolve against any Character in the Reaction owner's Room"
            effect_object = "ignore exactly that pending Intruder Attack"
            operation_type = "end-process"
        elif face["character"] == "Medical Support":
            precondition_text = "a Command card is played on the Reaction owner"
            effect_object = "ignore the Command's effect on the Reaction owner"
            operation_type = "end-process"
        else:
            precondition_text = "a higher-Rank Character plays a Command on the Reaction owner"
            effect_object = "cancel the Command effect on the Reaction owner while retaining SEM-Q-074 payment boundary"
            operation_type = "end-process"
        ops = [operation("S01", 1, operation_type, "must", "P-OWNER", effect_object, [scan_id]), operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-060 simultaneous Reaction ordering/priority", [scan_id])]
        if "SEM-Q-074" in questions:
            ops.append(operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-074 exact meaning/timing of the Command actor still paying the Action's cost", [scan_id]))
        result = record(
            reaction_rule, f"{face['character']} — {face['printedTitle']} Reaction occurrence", "source-backed-with-open-question", "reaction", "source-bound-component-scan", "open-alternatives",
            [assertion(scan_id, face["sourceId"], face["occurrenceId"] + " / REACTION", ["preconditions", "timing", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], source_text, face["sourcePath"])], ["term.reaction", "term.command"] if "Command" in source_text else ["term.reaction"], ["tax.process.card-effect.reaction", "tax.entity.agent.character"], [],
            timing(f"TW-ACTION-REACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}", "tax.process.card-effect.reaction", "when-triggered", "per-exact-pending-trigger"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-ACTOR", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must",
            [condition(f"C-ACTION-REACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}", "predicate", [{"predicate": precondition_text}], [scan_id])], [],
            [{"informationId": f"I-ACTION-REACTION-{_code(face['character'], face['ttsCardId'], face['ttsCardGuid'])}", "subjectRef": "pending trigger, exact Reaction face, and replacement/cancellation result", "audience": "public after generic Reaction play", "revealTrigger": "SEM-ACTION-CARD-REACTION-001", "secrecy": "other hand identities remain private"}], [], [], ops,
            {"policy": "replacement-effect", "unit": "one exact pending Attack/Command trigger", "onImpossible": "generic Reaction lifecycle owns play/discard; no simultaneous priority or cost default is invented"}, {"kind": "one-pending-trigger"}, {"policy": "one exact physical Reaction panel; same titles remain distinct"}, [], questions, [])
        result["sourceAssertions"][0]["textKind"] = "verbatim"
        records.append(result)

    return records


def integrate_action_shared_records(records: list[dict], assertion, operation) -> None:
    by_id = {row["ruleId"]: row for row in records}

    # Exact occurrence dispatchers now own card movement. Reusable effects own
    # only effect semantics so Search/Rest/Reaction do not double-discard.
    search = by_id["SEM-ACT-SEARCH-001"]
    search["operations"] = [op for op in search["operations"] if not (op.get("transition") or {}).get("from") == "tax.scaffold.zone.hand" or "played Search" not in op.get("objectRef", "")]
    search["sourceAssertions"] = [row for row in search["sourceAssertions"] if row["assertionId"] != "SA-SEARCH-3"]
    for index, op in enumerate(search["operations"], 1):
        op["sequence"] = index; op["stepId"] = f"S{index:02d}"

    rest = by_id["SEM-ACT-REST-001"]
    rest["operations"] = [op for op in rest["operations"] if "played Rest Action card" not in op.get("objectRef", "")]
    rest["sourceAssertions"] = [row for row in rest["sourceAssertions"] if row["assertionId"] != "SA-REST-3"]
    for index, op in enumerate(rest["operations"], 1):
        op["sequence"] = index; op["stepId"] = f"S{index:02d}"

    duck = by_id["SEM-REACTION-DUCK-001"]
    duck["decisions"] = []
    duck["preconditions"] = [row for row in duck["preconditions"] if row["conditionId"] == "C-DUCK"]
    duck["operations"] = [op for op in duck["operations"] if op["operationType"] not in {"play-card", "transition-zone"}]
    for op in duck["operations"]:
        op["conditionRefs"] = []
        op["decisionRef"] = None
    duck["operations"].append(operation("S99", 99, "resolve-open-alternative", "must", "P-OWNER", "SEM-Q-060 simultaneous Reaction ordering/priority", ["SA-DUCK-1"]))
    for index, op in enumerate(duck["operations"], 1):
        op["sequence"] = index; op["stepId"] = f"S{index:02d}"
    duck["unresolvedQuestionRefs"] = ["SEM-Q-001", "SEM-Q-060"]

    draw = by_id["SEM-ACTION-CARD-DRAW-001"]
    draw["sourceAssertions"].append(assertion("SA-ACTION-DRAW-FAQ", "SRC-FAQ", "FQ-P02-U11", ["operations", "partialResolution", "unresolvedQuestionRefs"], "If a played Action card causes draws, draw and renew the deck before discarding that resolving card, so it is not shuffled.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U11"))
    draw["operations"].append(operation("S99", 99, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-072 requested draw when both Action deck and discard pile cannot supply another card", ["SA-ACTION-DRAW-RB", "SA-ACTION-DRAW-FAQ"]))
    for index, op in enumerate(draw["operations"], 1):
        op["sequence"] = index; op["stepId"] = f"S{index:02d}"
    draw["unresolvedQuestionRefs"] = ["SEM-Q-072"]
    draw["status"] = "source-backed-with-open-question"
    draw["authority"]["highest"] = "official-errata"
    draw["authority"]["interpretation"] = "open-alternatives"

    cleanup = by_id["SEM-RT-012"]
    cleanup_draw = next(op for op in cleanup["operations"] if op["stepId"] == "S02")
    cleanup_draw["operationType"] = "invoke-process"
    cleanup_draw["objectRef"] = "refill each eligible Character's hand to 5 through exact Action draw/renewal"
    cleanup_draw["invokeRuleId"] = "SEM-ACTION-CARD-DRAW-001"
    cleanup_draw["repeat"] = {"targetHandCount": 5, "perCharacter": True, "finishEachCharacterBeforeNext": True}
    cleanup["unresolvedQuestionRefs"] = list(dict.fromkeys([*cleanup["unresolvedQuestionRefs"], "SEM-Q-072"]))


def build_action_question_rows() -> list[dict]:
    def row(qid: str, title: str, decision_class: str, evidence: list[str], alternatives: list[tuple[str, str]], blocks: list[str]) -> dict:
        return {"questionId": qid, "title": title, "decisionClass": decision_class, "blocksRuleIds": blocks, "plannedRuleIds": [], "defaultProhibited": True, "sourceEvidenceRefs": evidence, "alternatives": [{"alternativeId": f"{qid}-{chr(65+index)}", "description": description, "support": support} for index, (description, support) in enumerate(alternatives)]}
    index_ref = ["docs/rules/semantics/action-source-index.json"]
    return [
        row("SEM-Q-057", "Selected Action upper-right crossed-glyph denotations and scope", "source-ambiguity-owner-decision-after-source-search", [*index_ref, "assets/tts-mod/extract/selected-card-text-evidence.json"], [("Treat only independently matched/canonical occurrences as Not In Combat; keep eight selected local morphologies undispatched.", "selected comparisons are unresolved/no-match and no approved source-scoped alias exists"), ("Map one or more exact local occurrences to Not In Combat after a reviewed page-40/source-scoped artwork match.", "licensed noIntruders and expected tactics are leads, not source identity"), ("Establish another exact source-local restriction for individual occurrences.", "position/color/crossed-gun appearance cannot establish a global alias")], ACTION_QUESTION_BLOCKS["SEM-Q-057"]),
        row("SEM-Q-058", "Selected Search octagon identity and corresponding Item-deck mapping", "source-ambiguity-owner-decision-after-source-search", [*index_ref, "assets/tts-mod/extract/selected-card-text-evidence.json", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P28-V02"], [("Apply the official Search Item-Icon procedure to these exact TTS occurrences after establishing that each local octagon denotes the printed Room Item Icons collectively.", "official Search is a strong procedure counterpart but does not identify each TTS cell glyph"), ("Keep the local octagons literal and do not dispatch Item decks until an exact source-scoped match exists.", "selected evidence records explicit no-matches"), ("Map individual octagons to another source-defined icon/deck relation.", "title/body similarity and licensed text cannot create identity")], ACTION_QUESTION_BLOCKS["SEM-Q-058"]),
        row("SEM-Q-059", "Command nested-Action costs, resources, legality, and remaining choices", "official-clarification-preferred", [*index_ref, "docs/rulebooks/rulebook_text.txt:lines 3095–3105", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10"], [("Ordered Move/Shoot/Burst pays no normal Action-card Basic-Action cost, but the ordered Character supplies source-required Weapon/Ammo and the effect owner makes source-assigned choices.", "cards already resolve as effects and often say the owner makes choices; payment exception is not explicit"), ("Apply the complete normal Action cost/resource procedure to the ordered Character or effect owner.", "rulebook calls the nested operation an Action but does not name payer"), ("Use another source-defined split of Action-card payment, equipment/resources, target/weapon choices, and legality.", "Fire At Will assigns Corridor and Weapon owners specially, proving one global guess is unsafe")], ACTION_QUESTION_BLOCKS["SEM-Q-059"]),
        row("SEM-Q-060", "Reaction priority, simultaneous windows, replacement order, and stacking", "official-clarification-preferred", [*index_ref, "docs/rulebooks/rulebook_text.txt:lines 3067–3075,3180–3186"], [("Trigger owner chooses whether/which eligible Reaction to resolve, one complete Reaction at a time, with a source-defined priority among different owners.", "optional play is clear; priority/order is absent"), ("Use turn order for simultaneously eligible Reaction owners and re-evaluate after each replacement/cancellation.", "turn order is the common tie-break but not stated for Reactions"), ("Allow another source-defined interrupt/stack procedure.", "no checked source defines a stack, priority pass, or conflicting prevention order")], ACTION_QUESTION_BLOCKS["SEM-Q-060"]),
        row("SEM-Q-061", "Action-card continuation and discard after acting Character death/escape", "official-clarification-preferred", [*index_ref, "docs/rulebooks/rulebook_text.txt:lines 3161–3198,3750–3763"], [("Stop later actor-bound operations when the Character no longer participates, but always discard the resolving Action card.", "death ends participation while play rule still says discard after resolution"), ("Finish every already-selected card operation despite death/escape, then discard.", "effect was legal and selected before the interruption"), ("Use another source-defined per-operation interruption boundary.", "nested Attacks/Movement/Commands can remove the actor and no general continuation rule is printed")], ACTION_QUESTION_BLOCKS["SEM-Q-061"]),
        row("SEM-Q-062", "Continuous Fire zero-card legality, Hit allocation, and optional Burst", "official-clarification-preferred", index_ref, [("Any number includes zero; owner allocates one Hit per discarded card in one adjacent Corridor, then independently may Burst.", "literal any-number/may reading; zero-card legality may trivialize the effect"), ("At least one Action card must be discarded and all Hit targets/stacking must be declared for whole-effect legality.", "effect purpose suggests a positive payment but source says no minimum"), ("Use another source-defined allocation/order among multiple Intruders and the optional Burst.", "source gives no allocation or death/order procedure")], ACTION_QUESTION_BLOCKS["SEM-Q-062"]),
        row("SEM-Q-063", "Always Prepared multi-Intruder Attack order and continuation", "official-clarification-preferred", index_ref, [("Resolve attacking Intruders largest-first and continue to the next only while the actor remains participating.", "Intruder Phase supplies an order but this is a card effect"), ("Resolve all Intruders in another source-defined order even after intermediate death.", "card says all Attack; no interruption clause"), ("Apply turn/map/physical ordering with explicit death/escape continuation.", "checked sources do not assign it")], ACTION_QUESTION_BLOCKS["SEM-Q-063"]),
        row("SEM-Q-064", "Always Prepared Item draw privacy, optional keep, destination, and shortage", "official-clarification-preferred", index_ref, [("Privately inspect two, keep zero or one, and put every unkept card in that Item deck's discard pile.", "card says may keep 1 and discard the other, but zero-choice grammar is incomplete"), ("Keeping exactly one is required if two are drawn; discard the other publicly.", "the singular other supports exact-one"), ("Use official Search bottom/private procedure or another source-defined shortage/destination rule.", "this card is not labeled Search and cannot inherit by body similarity")], ACTION_QUESTION_BLOCKS["SEM-Q-064"]),
        row("SEM-Q-065", "Medical Action target consent and Field Surgery payment/choice ownership", "official-clarification-preferred", [*index_ref, "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U07"], [("Action owner chooses target/branch and pays; receiving Character consents and owns Serious Wound selection.", "Interplay requires consent and affected owner normally chooses Wound"), ("Receiving Character owns branch/payment consequence as well as Wound selection.", "card says that Character gains Contamination but does not assign the Medpack-or-Contamination choice"), ("Use another source-defined split for First Aid, Field Surgery, and Combat Drugs.", "FAQ broadens Interplay but does not fully assign nested choices")], ACTION_QUESTION_BLOCKS["SEM-Q-065"]),
        row("SEM-Q-066", "Weak Spots/Hippocratic Oath setup Hits before required attack", "official-clarification-preferred", index_ref, [("Card is legal only if the same target remains legal for the required Shoot/Melee after setup Hits.", "whole effect must resolve entirely"), ("Deal setup Hits, then skip an impossible required attack if the target is removed or otherwise ineligible.", "later eligibility can change only during resolution"), ("Use another source-defined target/death continuation boundary.", "no example covers Larva/Queen or target removal between clauses")], ACTION_QUESTION_BLOCKS["SEM-Q-066"]),
        row("SEM-Q-067", "Officer Channel nested Command card lifecycle and Room substitution", "official-clarification-preferred", index_ref, [("Choose another Command card from hand, reveal it, open its Reaction window, resolve it with any Facility Room substituted, then discard both cards in nested order.", "natural play-card reading; no nested lifecycle is printed"), ("Resolve only another Command effect without playing/discarding its physical card or opening Reactions.", "effect may reference card text as an option rather than a second play"), ("Use another source-defined card source, cost, Room, Reaction, and discard order.", "licensed wording does not settle physical lifecycle")], ACTION_QUESTION_BLOCKS["SEM-Q-067"]),
        row("SEM-Q-068", "Stay Calm local draw-glyph identity", "source-ambiguity-owner-decision-after-source-search", [*index_ref, "assets/tts-mod/extract/selected-card-text-evidence.json", "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js:ACTION_CARDS_DATA.Officer_StayCalm"], [("The source-local upright card/tile denotes Action card, following the licensed row.", "licensed occurrence is a strong lead but lower authority"), ("Keep the glyph literal and do not draw until exact source-scoped evidence resolves it.", "selected comparison is an explicit no-match"), ("Assign another source-local component meaning.", "shape and expected tactics cannot establish identity")], ACTION_QUESTION_BLOCKS["SEM-Q-068"]),
        row("SEM-Q-069", "Let's Go companion owner, consent, Movement, and Noise/Attack scope", "official-clarification-preferred", index_ref, [("Officer chooses one consenting co-located Character; both move through one legal Corridor, only Officer rolls Noise, and each resolves source-defined opportunity consequences.", "co-movement effects elsewhere state consent, but this face omits it"), ("Officer may move another Character without consent and owns route/target choices.", "literal card gives no consent"), ("Use another source-defined companion, range, attack, and interruption procedure.", "card gives only the Noise exception")], ACTION_QUESTION_BLOCKS["SEM-Q-069"]),
        row("SEM-Q-070", "Taking Aim reroll scope and second-result acceptance", "official-clarification-preferred", index_ref, [("Reroll exactly the first Shoot/Burst die result and must accept the second result.", "licensed row states acceptance; TTS face only says can reroll"), ("Reroll the first result and retain a choice between first and second.", "ordinary language does not say replace/accept"), ("Apply reroll to another source-defined die/result set, including additional Weapon dice.", "no general reroll rule was found")], ACTION_QUESTION_BLOCKS["SEM-Q-070"]),
        row("SEM-Q-071", "Explosives new-Corridor endpoint, geometry, orientation, and finite supply", "official-clarification-preferred", index_ref, [("Effect owner chooses another Explored Room and a source-legal pair of free edges; place an available Corridor with Door orientation under ordinary rules.", "natural owner/local/geometry composition; chooser/edges are not printed"), ("Use a random/deterministic physical placement among legal endpoints/components.", "Corridor components are random/finite in other procedures but not here"), ("The branch is illegal unless another source-defined direct connection placement is fully available.", "whole-effect legality is clear but exact geometry is absent")], ACTION_QUESTION_BLOCKS["SEM-Q-071"]),
        row("SEM-Q-072", "Action draw shortage and multi-recipient ordering", "official-clarification-preferred", [*index_ref, "docs/rulebooks/rulebook_text.txt:lines 3401–3403,3434–3438", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U11"], [("Draw sequentially; renew from discard when needed; stop without substitution when deck and discard are empty, using source order among recipients.", "finite physical deck implies shortfall but source never says stop/order"), ("A draw-to-count effect is illegal unless the complete requested count can be supplied.", "whole-effect rule may precheck draws"), ("Use another source-defined shortage/allocation procedure among multiple Characters.", "Cleanup, Combat Drugs, and Stay Calm have different recipient shapes")], ACTION_QUESTION_BLOCKS["SEM-Q-072"]),
        row("SEM-Q-073", "Movement-card interrupt, prevention, companion, and continuation windows", "official-clarification-preferred", [*index_ref, "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U15/FQ-P02-U16"], [("Resolve printed card costs, then Movement in normal order; prevention covers only selected Opportunity Attacks; pause at printed Shoot/Burst windows and resume if actor remains participating.", "FAQ settles Hazard scope and Shoot First availability but not all ordering"), ("Choose/predeclare prevention and optional attacks at another point, with source-specific continuation after death/escape.", "cards phrase windows differently"), ("Use another source-defined sequence for companions and nested Movement effects.", "no unified interrupt stack or continuation rule is printed")], ACTION_QUESTION_BLOCKS["SEM-Q-073"]),
        row("SEM-Q-074", "Chain of Command Reaction cancellation cost meaning and timing", "official-clarification-preferred", index_ref, [("Cancel after the Command card and all printed additional Action-card costs are paid; return no resource and discard the Command normally.", "TTS says the Character must still pay the Action's cost"), ("Only the zero-cost Play-an-Action-card cost is retained; nested Action resources/additional printed costs are not spent.", "Action card itself costs zero and Command payment is unresolved"), ("Use another source-defined cancellation/payment/refund boundary.", "different Chain variants say cancel versus ignore and no general cancellation rule applies")], ACTION_QUESTION_BLOCKS["SEM-Q-074"]),
    ]


def build_action_conflicts() -> list[dict]:
    return [
        {"conflictId": "SC-049", "title": "Seven TTS roots versus six final Character Action decks", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-ACTION-DECK-SETUP-001", "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-ACTION-DECK-CON", "SRC-ACTION-DECK-CON-SHARED", "docs/rules/semantics/action-source-index.json"], "difference": "Five Contractor kit cards and five Shared Contractor cards occupy two TTS roots, while the official base rules require one shuffled ten-card Contractor deck and ignore the printed distinction.", "resolution": "Compose exact membership only for Contractor setup; preserve both root segments and every physical selector."},
        {"conflictId": "SC-050", "title": "Action sheet selected cells, base selector gaps, and expansion cells", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-ACTION-SHEET-5674", "SRC-ACTION-SHEET-5675", "docs/rules/semantics/action-source-index.json"], "difference": "CustomDeck 5674 has 16 selected base physical cells plus 29 base-Character selector gaps; CustomDeck 5675 selects base cells 10–14 while forty other cells are expansion Characters.", "resolution": "Retain sheet/hash/grid/cell evidence; gaps and expansion cells never become base physical copies."},
        {"conflictId": "SC-051", "title": "Selected Action crossed upper-right glyphs versus licensed noIntruders", "status": "unresolved", "questionId": "SEM-Q-057", "affectedRuleIds": [*ACTION_QUESTION_BLOCKS["SEM-Q-057"], "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-BGA-ACTION-CARDS", "assets/tts-mod/extract/selected-card-text-evidence.json", "docs/rules/semantics/action-source-index.json"], "difference": "Eight selected generated occurrences retain unresolved/no-match crossed morphologies while licensed rows expose booleans; aggregate true counts and exact occurrence representations are not a source identity crosswalk.", "resolution": "No Not In Combat default; retain exact literal art and independent licensed flags."},
        {"conflictId": "SC-052", "title": "Selected Search octagons versus current official Item Icons", "status": "unresolved", "questionId": "SEM-Q-058", "affectedRuleIds": [*ACTION_QUESTION_BLOCKS["SEM-Q-058"], "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-BGA-ACTION-CARDS", "assets/tts-mod/extract/selected-card-text-evidence.json"], "difference": "Five selected TTS Search faces show local solid octagons with no exact approved glossary match; the current official Search occurrence and licensed rows say Item Icon(s) and corresponding type.", "resolution": "Official procedure remains independent; no title/body-based mapping to TTS local glyphs."},
        {"conflictId": "SC-053", "title": "Selected pixel evidence versus stale Action corpus projections", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-ACTION-CARD-VARIANT-BOUNDARIES-001", *ACTION_RULE_IDS], "evidenceRefs": ["assets/tts-mod/extract/card-text-corpus.json", "assets/tts-mod/extract/selected-card-text-evidence.json", "docs/rules/semantics/action-source-index.json"], "difference": "Twenty-six selected physical faces have one or more title/body/footer/upper-right representation differences from earlier corpus printedData, including Combat Drugs Medpack and several Lander/Reaction reads.", "resolution": "Selected source-bound pixel evidence controls the semantic projection; both representations remain recorded without rewriting extraction history."},
        {"conflictId": "SC-054", "title": "Sixty physical TTS copies versus sixty licensed Action rows", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-ACTION-CARD-VARIANT-BOUNDARIES-001", *ACTION_RULE_IDS], "evidenceRefs": ["SRC-BGA-ACTION-CARDS", "docs/rules/semantics/action-source-index.json"], "difference": "Counts partition 10×6 in both sources, but no licensed key identifies a TTS deck GUID/full CardID/GUID/cell copy and wording/layout fields differ.", "resolution": "Retain sixty plus sixty independent occurrences with zero asserted physical identity links."},
        {"conflictId": "SC-055", "title": "Sprint TTS/corpus/current-official wording and resource representation", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": [_rule_id("Recon", 568600, "662fa5"), "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-BGA-ACTION-CARDS", "docs/rules/semantics/action-source-index.json"], "difference": "Selected TTS says lose 1 Oxygen, an earlier corpus projection emitted Oxygen token, and current official/licensed wording says spend 1 Oxygen; no official visual occurrence identifies the TTS GUID.", "resolution": "Encode exact selected TTS occurrence and preserve current official/licensed occurrences independently."},
        {"conflictId": "SC-056", "title": "Stay Calm local draw glyph versus licensed Action-card placeholder", "status": "unresolved", "questionId": "SEM-Q-068", "affectedRuleIds": ACTION_QUESTION_BLOCKS["SEM-Q-068"], "evidenceRefs": ["SRC-BGA-ACTION-CARDS", "assets/tts-mod/extract/selected-card-text-evidence.json", "docs/rules/semantics/action-source-index.json"], "difference": "Selected source evidence leaves the upright card/tile glyph unresolved while licensed Stay Calm says each Character draws one Action card.", "resolution": "No draw target default; unaffected Lander/Room/Reaction clauses remain encoded."},
        {"conflictId": "SC-057", "title": "Weak Spots TTS plural versus current official/licensed Weak Spot", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": [_rule_id("Contractor", 567514, "35d06d"), "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001"], "evidenceRefs": ["SRC-RULEBOOK", "SRC-BGA-ACTION-CARDS", "SRC-ACTION-SHEET-5675"], "difference": "The selected TTS face is WEAK SPOTS and says chosen Intruder in your Room; current official visible/licensed occurrences are Weak spot/Weak Spot with their own punctuation/wording.", "resolution": "Current official controls only its exact publisher occurrence; no title normalization or GUID substitution."},
        {"conflictId": "SC-058", "title": "Printed Command headings versus licensed command flags", "status": "preserved-boundary", "questionId": None, "affectedRuleIds": ["SEM-ACTION-CARD-COMMAND-001", "SEM-ACTION-CARD-VARIANT-BOUNDARIES-001", *_rules_for("chain-command", "chain-command-reaction", "fire-at-will", "officer-channel", "stay-calm-reaction")], "evidenceRefs": ["SRC-BGA-ACTION-CARDS", "docs/rules/semantics/action-source-index.json"], "difference": "Eight TTS physical main panels visibly carry COMMAND headings, while seven licensed rows set command=true because Officer's Channel references playing another Command rather than being flagged as one.", "resolution": "Preserve panel headings and licensed booleans as different source fields; never flatten one into the other."},
    ]
