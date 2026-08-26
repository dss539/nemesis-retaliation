from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

from semantic_attack_records import _find_guid, _parse_value


BASE_GREEN_ITEM_DECK_GUID = "17400d"
GREEN_ITEM_ROOT_SOURCE_ID = "SRC-GREEN-ITEM-ROOT-DECK"
GREEN_ITEM_SHEET_SOURCE_ID = "SRC-GREEN-ITEM-SHEET"
GREEN_ITEM_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181.jpg"
GREEN_ITEM_BACK_SOURCE_ID = "SRC-GREEN-ITEM-BACK"
GREEN_ITEM_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-152.jpg"
BGA_GREEN_ITEM_SOURCE_ID = "SRC-BGA-GREEN-ITEMS"
BGA_ITEMS_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
SELECTED_EVIDENCE_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
VISION_PROGRESS_PATH = "assets/tts-mod/extract/vision-progress.json"
LOW_CONFIDENCE_PATH = "assets/tts-mod/extract/low-confidence-review.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"

SHARED_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235748/220899EB4989F76566E84DE9851C764359F18ECC/"
SHEET_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235671/C061484313FA1C3B1731583743DAE5115DBD4068/"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _asset(
    asset_key: str,
    source_path: str,
    source_role: str,
    printed_title: str,
    printed_body: str,
    *,
    custom_deck_ids: list[str],
    generated_cell: int | None,
    physical_class: str,
    selected_regular: bool,
    type_line: str = "ONE USE ONLY",
    upper_right: str = "",
    body_panels: list[tuple[str, str]] | None = None,
    sentence_texts: list[str] | None = None,
    icon_specs: list[tuple[str, str, str | None, str, int]] | None = None,
    effect_kind: str,
    named_identity_ref: str | None = None,
) -> dict:
    return {
        "assetKey": asset_key,
        "sourcePath": source_path,
        "sourceRole": source_role,
        "customDeckIds": custom_deck_ids,
        "generatedCell": generated_cell,
        "physicalClass": physical_class,
        "selectedRegular": selected_regular,
        "printedTitle": printed_title,
        "typeLine": type_line,
        "upperRight": upper_right,
        "printedBody": printed_body,
        "bodyPanels": body_panels or [("effect", printed_body)],
        "sentenceTexts": sentence_texts or [printed_body],
        "iconSpecs": icon_specs or [],
        "effectKind": effect_kind,
        "namedIdentityRef": named_identity_ref,
    }


ASSET_DEFINITIONS = {
    "direct-5365": _asset(
        "direct-5365",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-140.png",
        "direct-regular-face",
        "EMERGENCY LIFE\nSUPPORT CODES",
        "Only in [computer] Room without [malfunction]:\nFlip an [lifeSupportActive] / [lifeSupportInactive]\nin any Section.",
        custom_deck_ids=["5365"], generated_cell=None, physical_class="regular-item", selected_regular=True,
        upper_right="notInCombat",
        icon_specs=[
            ("upperRight", "notInCombat", "icon.notInCombat", "canonical", 0),
            ("body", "[computer]", "icon.computer", "canonical", 0),
            ("body", "[malfunction]", "icon.malfunction", "canonical", 0),
            ("body", "[lifeSupportActive]", "icon.lifeSupportActive", "canonical", 0),
            ("body", "[lifeSupportInactive]", "icon.lifeSupportInactive", "canonical", 0),
        ],
        effect_kind="flip-life-support", named_identity_ref="NI-0142",
    ),
    "direct-5366": _asset(
        "direct-5366",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-115.png",
        "direct-regular-face",
        "CAFFEINE PILLS",
        "Draw 3 [actionCard].",
        custom_deck_ids=["5366"], generated_cell=None, physical_class="regular-item", selected_regular=True,
        upper_right="notInCombat",
        icon_specs=[
            ("upperRight", "notInCombat", "icon.notInCombat", "selected-verified", 0),
            ("body", "[actionCard]", "icon.actionCard", "selected-verified", 1),
        ],
        effect_kind="draw-three-action-cards", named_identity_ref="NI-0036",
    ),
    "direct-5367": _asset(
        "direct-5367",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-120.png",
        "direct-regular-face",
        "MEDKIT",
        "You can use this Item for free\nimmediately after gaining it.\n\nRestore 2 [characterHealth].\n\nOR\n\nGain 1 [medpackToken].",
        custom_deck_ids=["5367"], generated_cell=None, physical_class="regular-item", selected_regular=True,
        upper_right="notInCombat",
        body_panels=[
            ("immediate-use-timing-note", "You can use this Item for free\nimmediately after gaining it."),
            ("restore-health-branch", "Restore 2 [characterHealth]."),
            ("gain-medpack-branch", "Gain 1 [medpackToken]."),
        ],
        sentence_texts=[
            "You can use this Item for free\nimmediately after gaining it.",
            "Restore 2 [characterHealth].",
            "Gain 1 [medpackToken].",
        ],
        icon_specs=[
            ("upperRight", "notInCombat", "icon.notInCombat", "selected-verified", 0),
            ("body", "[characterHealth]", "icon.characterHealth", "selected-verified", 1),
            ("body", "[medpackToken]", "icon.medpackToken", "selected-verified", 2),
        ],
        effect_kind="restore-or-gain-medpack", named_identity_ref="NI-0298",
    ),
    "direct-heavy-medkit": _asset(
        "direct-heavy-medkit",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-035.png",
        "direct-heavy-face-excluded",
        "MEDKIT",
        "Discard 1 Serious Wound and/or restore 3 [characterHealth].",
        custom_deck_ids=["4159", "4160", "4161"], generated_cell=None, physical_class="heavy-item", selected_regular=False,
        upper_right="notInCombat",
        icon_specs=[
            ("upperRight", "notInCombat", "icon.notInCombat", "canonical", 0),
            ("body", "[characterHealth]", "icon.characterHealth", "canonical", 0),
        ],
        effect_kind="excluded-heavy-medkit", named_identity_ref="NI-0298",
    ),
    "direct-heavy-oxygen": _asset(
        "direct-heavy-oxygen",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-029.png",
        "direct-heavy-face-excluded",
        "HEAVY OXYGEN TANK",
        "Gain 7 [oxygen].",
        custom_deck_ids=["4001"], generated_cell=None, physical_class="heavy-item", selected_regular=False,
        type_line="ONE USE ONLY, SPECIAL WEAPON",
        upper_right="[ICON: red X over white horizontal device]",
        icon_specs=[
            ("upperRight", "[ICON: red X over white horizontal device]", None, "selected-unresolved", 0),
            ("body", "[oxygen]", "icon.oxygen", "selected-verified", 0),
        ],
        effect_kind="excluded-heavy-oxygen", named_identity_ref="NI-0236",
    ),
    "sheet-00": _asset(
        "sheet-00",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-00.png",
        "generated-cell-regular-face",
        "ADRENALINE\nINJECTION",
        "Draw 1 [ICON: solid blank white rectangle].\nYou may perform any number\nof Actions in this single Turn.\nPass as the last Action.",
        custom_deck_ids=["37"], generated_cell=0, physical_class="regular-item", selected_regular=True,
        sentence_texts=[
            "Draw 1 [ICON: solid blank white rectangle].",
            "You may perform any number\nof Actions in this single Turn.",
            "Pass as the last Action.",
        ],
        icon_specs=[("body", "[ICON: solid blank white rectangle]", None, "selected-unresolved", 0)],
        effect_kind="adrenaline-action-window", named_identity_ref="NI-0002",
    ),
    "sheet-01": _asset(
        "sheet-01",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-01.png",
        "generated-cell-regular-face",
        "ANTISEPTIC",
        "Remove 1 Contamination\ncard from your hand\nwithout scanning it.",
        custom_deck_ids=["37"], generated_cell=1, physical_class="regular-item", selected_regular=True,
        upper_right="notInCombat",
        icon_specs=[("upperRight", "notInCombat", "icon.notInCombat", "canonical", 0)],
        effect_kind="remove-unscanned-contamination", named_identity_ref="NI-0011",
    ),
    "sheet-02": _asset(
        "sheet-02",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-02.png",
        "generated-cell-selector-gap-variant",
        "CAFFEINE PILLS",
        "Draw 3 [ICON: solid blank white rectangle], reveal them,\nand resolve the Infection\nProcedure.",
        custom_deck_ids=["37"], generated_cell=2, physical_class="regular-item", selected_regular=False,
        upper_right="[ICON: red X over white horizontal device]",
        icon_specs=[
            ("upperRight", "[ICON: red X over white horizontal device]", None, "selected-unresolved", 0),
            ("body", "[ICON: solid blank white rectangle]", None, "selected-unresolved", 1),
        ],
        effect_kind="selector-gap-caffeine", named_identity_ref="NI-0036",
    ),
    "sheet-03": _asset(
        "sheet-03",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-03.png",
        "generated-cell-regular-face",
        "CONTAMINATION\nCODES",
        "Only in a [computer] Room without [malfunction].\nChoose any Room in the Facility\nand place a closed Door in\neach adjacent Corridor.",
        custom_deck_ids=["37"], generated_cell=3, physical_class="regular-item", selected_regular=True,
        upper_right="notInCombat",
        sentence_texts=[
            "Only in a [computer] Room without [malfunction].",
            "Choose any Room in the Facility\nand place a closed Door in\neach adjacent Corridor.",
        ],
        icon_specs=[
            ("upperRight", "notInCombat", "icon.notInCombat", "canonical", 0),
            ("body", "[computer]", "icon.computer", "canonical", 0),
            ("body", "[malfunction]", "icon.malfunction", "canonical", 0),
        ],
        effect_kind="place-closed-doors", named_identity_ref=None,
    ),
    "sheet-04": _asset(
        "sheet-04",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-04.png",
        "generated-cell-selector-gap-variant",
        "EMERGENCY LIFE SUPPORT CODES",
        "Only in [computer] Room without [malfunction].\nFlip all [ICON: white three-lobed horizontal cluster with cyan center and an outlined upright rounded rectangle].\nFlip 1 [ICON: white three-lobed horizontal cluster with gray center and a pale outlined upright rounded rectangle].",
        custom_deck_ids=["37"], generated_cell=4, physical_class="regular-item", selected_regular=False,
        upper_right="[ICON: narrow white segmented horizontal mark overlaid by a large red diagonal X]",
        sentence_texts=[
            "Only in [computer] Room without [malfunction].",
            "Flip all [ICON: white three-lobed horizontal cluster with cyan center and an outlined upright rounded rectangle].",
            "Flip 1 [ICON: white three-lobed horizontal cluster with gray center and a pale outlined upright rounded rectangle].",
        ],
        icon_specs=[
            ("upperRight", "[ICON: narrow white segmented horizontal mark overlaid by a large red diagonal X]", None, "selected-unresolved", 0),
            ("body", "[computer]", "icon.computer", "selected-verified", 0),
            ("body", "[malfunction]", "icon.malfunction", "selected-verified", 1),
            ("body", "[ICON: white three-lobed horizontal cluster with cyan center and an outlined upright rounded rectangle]", None, "selected-unresolved", 1),
            ("body", "[ICON: white three-lobed horizontal cluster with gray center and a pale outlined upright rounded rectangle]", None, "selected-unresolved", 2),
        ],
        effect_kind="selector-gap-life-support", named_identity_ref="NI-0142",
    ),
    "sheet-05": _asset(
        "sheet-05",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-05.png",
        "generated-cell-regular-face",
        "MEDICAL\nSTAPLER",
        "Discard 1 Serious Wound.\n\nOR\n\nRestore 2 [characterHealth].",
        custom_deck_ids=["37"], generated_cell=5, physical_class="regular-item", selected_regular=True,
        body_panels=[
            ("discard-wound-branch", "Discard 1 Serious Wound."),
            ("restore-health-branch", "Restore 2 [characterHealth]."),
        ],
        sentence_texts=["Discard 1 Serious Wound.", "Restore 2 [characterHealth]."],
        icon_specs=[("body", "[characterHealth]", "icon.characterHealth", "canonical", 0)],
        effect_kind="discard-wound-or-restore", named_identity_ref=None,
    ),
    "sheet-06": _asset(
        "sheet-06",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-06.png",
        "generated-cell-selector-gap-variant",
        "MEDKIT",
        "Discard 1 Serious Wound.\nOR\nMove your [characterHealth] marker\nback to the first space\nof the Injured Health section.",
        custom_deck_ids=["37"], generated_cell=6, physical_class="regular-item", selected_regular=False,
        upper_right="[ICON: jagged white horizontal segmented mark overlaid by a large red diagonal X]",
        body_panels=[
            ("discard-wound-branch", "Discard 1 Serious Wound."),
            ("move-health-marker-branch", "Move your [characterHealth] marker\nback to the first space\nof the Injured Health section."),
        ],
        sentence_texts=[
            "Discard 1 Serious Wound.",
            "Move your [characterHealth] marker\nback to the first space\nof the Injured Health section.",
        ],
        icon_specs=[
            ("upperRight", "[ICON: jagged white horizontal segmented mark overlaid by a large red diagonal X]", None, "selected-unresolved", 0),
            ("body", "[characterHealth]", "icon.characterHealth", "selected-verified", 0),
        ],
        effect_kind="selector-gap-medkit", named_identity_ref="NI-0298",
    ),
    "sheet-07": _asset(
        "sheet-07",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-07.png",
        "generated-cell-regular-face",
        "STIMULANTS",
        "Restore 2 [characterHealth].\nOR\nDraw 2 [ICON: blank upright white rounded rectangle with a dark outline].",
        custom_deck_ids=["37"], generated_cell=7, physical_class="regular-item", selected_regular=True,
        upper_right="[ICON: white horizontally layered jagged-ended mark overlaid by a red X]",
        body_panels=[
            ("restore-health-branch", "Restore 2 [characterHealth]."),
            ("draw-local-glyph-branch", "Draw 2 [ICON: blank upright white rounded rectangle with a dark outline]."),
        ],
        sentence_texts=[
            "Restore 2 [characterHealth].",
            "Draw 2 [ICON: blank upright white rounded rectangle with a dark outline].",
        ],
        icon_specs=[
            ("upperRight", "[ICON: white horizontally layered jagged-ended mark overlaid by a red X]", None, "selected-unresolved", 0),
            ("body", "[characterHealth]", "icon.characterHealth", "selected-verified", 0),
            ("body", "[ICON: blank upright white rounded rectangle with a dark outline]", None, "selected-unresolved", 1),
        ],
        effect_kind="restore-or-local-draw", named_identity_ref="NI-0454",
    ),
    "sheet-08": _asset(
        "sheet-08",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/greenitem-181_cards/card-08.png",
        "generated-cell-selector-gap-variant",
        "SYNTHETIC FOOD",
        "Draw 2 [ICON: blank upright white rounded rectangle with a dark outline].",
        custom_deck_ids=["37"], generated_cell=8, physical_class="regular-item", selected_regular=False,
        upper_right="[ICON: white horizontally segmented mark overlaid by a large red X]",
        icon_specs=[
            ("upperRight", "[ICON: white horizontally segmented mark overlaid by a large red X]", None, "selected-unresolved", 0),
            ("body", "[ICON: blank upright white rounded rectangle with a dark outline]", None, "selected-unresolved", 1),
        ],
        effect_kind="selector-gap-synthetic-food", named_identity_ref="NI-0466",
    ),
}


def _definition(root_sequence: int, asset_key: str, card_id: int, guid: str, custom_deck_id: str, *, regular: bool) -> dict:
    code = f"{card_id}-{guid.upper()}"
    return {
        "rootSequence": root_sequence,
        "assetKey": asset_key,
        "ttsCardId": card_id,
        "ttsCardGuid": guid,
        "customDeckId": custom_deck_id,
        "regular": regular,
        "occurrenceId": f"TTS-GREEN-ITEM-{code}-FACE" if regular else f"TTS-GREEN-ITEM-EXCLUDED-HEAVY-{code}-FACE",
        "sourceId": f"SRC-GREEN-ITEM-{code}" if regular else f"SRC-GREEN-ITEM-EXCLUDED-HEAVY-{code}",
        "semanticRuleId": f"SEM-GREEN-ITEM-{code}-001" if regular else None,
    }


ROOT_PHYSICAL_DEFINITIONS = [
    _definition(1, "direct-5365", 536500, "dc077a", "5365", regular=True),
    _definition(2, "direct-5366", 536600, "d4829e", "5366", regular=True),
    _definition(3, "direct-5366", 536600, "f2503b", "5366", regular=True),
    _definition(4, "direct-5366", 536600, "4995a3", "5366", regular=True),
    _definition(5, "direct-5367", 536700, "96f194", "5367", regular=True),
    _definition(6, "direct-5367", 536700, "63664d", "5367", regular=True),
    _definition(7, "direct-5367", 536700, "a35eff", "5367", regular=True),
    _definition(8, "direct-5367", 536700, "7aba7a", "5367", regular=True),
    _definition(9, "direct-heavy-medkit", 415900, "9bd717", "4159", regular=False),
    _definition(10, "direct-heavy-medkit", 415900, "339846", "4159", regular=False),
    _definition(11, "direct-heavy-medkit", 416000, "c8e79c", "4160", regular=False),
    _definition(12, "direct-heavy-medkit", 416100, "61a77c", "4161", regular=False),
    _definition(13, "direct-heavy-oxygen", 400100, "4ff8a4", "4001", regular=False),
    _definition(14, "direct-heavy-oxygen", 400100, "4b18b1", "4001", regular=False),
    _definition(15, "direct-heavy-oxygen", 400100, "1ceccd", "4001", regular=False),
    _definition(16, "sheet-00", 3700, "eabba4", "37", regular=True),
    _definition(17, "sheet-00", 3700, "7e1c40", "37", regular=True),
    _definition(18, "sheet-00", 3700, "cefcf6", "37", regular=True),
    _definition(19, "sheet-01", 3701, "2e0877", "37", regular=True),
    _definition(20, "sheet-01", 3701, "2f0205", "37", regular=True),
    _definition(21, "sheet-01", 3701, "e2e7d7", "37", regular=True),
    _definition(22, "sheet-03", 3703, "c1bef4", "37", regular=True),
    _definition(23, "sheet-05", 3705, "824be4", "37", regular=True),
    _definition(24, "sheet-05", 3705, "b9c9df", "37", regular=True),
    _definition(25, "sheet-05", 3705, "6f0675", "37", regular=True),
    _definition(26, "sheet-05", 3705, "271ced", "37", regular=True),
    _definition(27, "sheet-05", 3705, "1a13ab", "37", regular=True),
    _definition(28, "sheet-07", 3707, "79581a", "37", regular=True),
    _definition(29, "sheet-07", 3707, "64df0b", "37", regular=True),
    _definition(30, "sheet-07", 3707, "30f2f8", "37", regular=True),
]

REGULAR_PHYSICAL_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if row["regular"]]
EXCLUDED_HEAVY_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if not row["regular"]]
for family_sequence, row in enumerate(REGULAR_PHYSICAL_DEFINITIONS, 1):
    row["familySequence"] = family_sequence

GREEN_ITEM_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS]
MEDKIT_IMMEDIATE_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-5367"]
ADRENALINE_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet-00"]
STIMULANTS_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet-07"]
CONTAMINATION_CODES_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet-03"]
RESTORE_GREEN_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] in {"direct-5367", "sheet-05", "sheet-07"}]

GREEN_ITEM_QUESTION_BLOCKS = {
    "SEM-Q-039": ["SEM-USE-ITEM-001", "SEM-GREEN-ITEM-ONE-USE-001"],
    "SEM-Q-040": ["SEM-GREEN-ITEM-DECK-001", "SEM-ACT-SEARCH-001"],
    "SEM-Q-041": [*ADRENALINE_RULE_IDS, *STIMULANTS_RULE_IDS],
    "SEM-Q-042": CONTAMINATION_CODES_RULE_IDS,
    "SEM-Q-043": ["SEM-RESTORE-HEALTH-001", *RESTORE_GREEN_RULE_IDS],
    "SEM-Q-044": ["SEM-ITEM-INTERPLAY-001", *MEDKIT_IMMEDIATE_RULE_IDS],
    "SEM-Q-045": ["SEM-ITEM-TRADE-GAIN-001", "SEM-GREEN-ITEM-IMMEDIATE-USE-001", *MEDKIT_IMMEDIATE_RULE_IDS],
}


def _raw_green_deck(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    deck = _find_guid(root.get("ObjectStates"), BASE_GREEN_ITEM_DECK_GUID)
    if not isinstance(deck, dict):
        raise AssertionError("base Green Item root Deck missing from raw TTS save")
    return deck, hashlib.sha256(data).hexdigest()


def _parse_bga_green_items(path: Path) -> list[dict]:
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
        deck_match = re.search(r"\n    deck: ('(?:\\.|[^'])*')", source_block)
        if not deck_match or ast.literal_eval(deck_match.group(1)) != "deck-green":
            continue

        def literal(pattern: str, default=None):
            found = re.search(pattern, source_block, re.S)
            return ast.literal_eval(found.group(1)) if found else default

        nbr_match = re.search(r"\n    nbr: (\d+)", source_block)
        if not nbr_match:
            raise AssertionError(f"licensed Green Item multiplicity missing: {key}")
        rows.append({
            "key": key,
            "sourceOrder": source_index + 1,
            "deck": "deck-green",
            "name": literal(r"\n    name: ('(?:\\.|[^'])*')"),
            "subtitle": literal(r"\n    subtitle: ('(?:\\.|[^'])*')"),
            "heavy": bool(re.search(r"\n    heavy: true", source_block)),
            "armor": bool(re.search(r"\n    armor: true", source_block)),
            "nbr": int(nbr_match.group(1)),
            "noIntruders": bool(re.search(r"\n    noIntruders: true", source_block)),
            "oneUse": bool(re.search(r"\n    oneUse: true", source_block)),
            "slots": literal(r"\n    slots: (\[(?:.|\n)*?\])\s*,\n    effectDesc", []),
            "effectDesc": literal(r"\n    effectDesc: (\[(?:.|\n)*?\])\s*,\n    traits", []),
            "traits": literal(r"\n    traits: ('(?:\\.|[^'])*')"),
            "sourceBlockText": source_block,
            "identityCrosswalkStatus": "independent licensed occurrence; no TTS/official physical identity join asserted",
        })
    expected = [
        ("AdrenalineInjection", 3, False),
        ("Antiseptic", 3, False),
        ("CaffeinePills", 3, False),
        ("EmergencyLifeSupportCodes", 1, False),
        ("HeavyOxygenTank", 3, True),
        ("MedicalStapler", 5, False),
        ("Medkit", 4, True),
        ("Medpack", 4, False),
        ("Stimulants", 3, False),
        ("TerminationCodes", 1, False),
    ]
    if [(row["key"], row["nbr"], row["heavy"]) for row in rows] != expected:
        raise AssertionError("licensed Green Item rows/order/multiplicity changed")
    return rows


def _source_regions(asset: dict) -> list[dict]:
    return [
        {
            "regionId": "R1",
            "readingOrder": 1,
            "role": "artwork-and-interface",
            "operative": False,
            "rulesDataHandling": "preserve pixels as card anatomy/artwork; exclude decorative machinery, medical objects, rails, backgrounds, microtext, and overlays from rules text",
        },
        {
            "regionId": "R2",
            "readingOrder": 2,
            "role": "identity-trait-and-restriction",
            "operative": True,
            "printedTitle": asset["printedTitle"],
            "typeLine": asset["typeLine"],
            "upperRight": asset["upperRight"],
            "headingOccurrences": [{"exactText": asset["typeLine"], "headingClass": "trait-line"}],
            "useHeadingPresent": False,
            "discardHeadingPresent": False,
            "passiveHeadingPresent": False,
            "reactionHeadingPresent": False,
        },
        {
            "regionId": "R3",
            "readingOrder": 3,
            "role": "operative-effect-body",
            "operative": True,
            "exactText": asset["printedBody"],
            "bodyStart": 0,
            "bodyEnd": len(asset["printedBody"]),
        },
    ]


def _source_panels(asset: dict) -> list[dict]:
    panels = [
        {"panelId": "P1", "readingOrder": 1, "role": "artwork-panel", "operative": False, "regionId": "R1", "exactText": None},
        {
            "panelId": "P2",
            "readingOrder": 2,
            "role": "identity-trait-restriction-panel",
            "operative": True,
            "regionId": "R2",
            "exactText": "\n".join(value for value in (asset["printedTitle"], asset["typeLine"], asset["upperRight"]) if value),
        },
    ]
    for index, (role, exact_text) in enumerate(asset["bodyPanels"], 3):
        panels.append({
            "panelId": f"P{index}",
            "readingOrder": index,
            "role": role,
            "operative": True,
            "regionId": "R3",
            "exactText": exact_text,
            "branchSeparatorBefore": "OR" if index > 3 and "\nOR\n" in asset["printedBody"] else None,
        })
    return panels


def _source_sentences(asset: dict, panels: list[dict]) -> list[dict]:
    rows = []
    cursor = 0
    body_panels = panels[2:]
    for sequence, exact_text in enumerate(asset["sentenceTexts"], 1):
        start = asset["printedBody"].find(exact_text, cursor)
        if start < 0:
            raise AssertionError(f"Green Item sentence span missing: {asset['assetKey']}:{sequence}")
        end = start + len(exact_text)
        panel = next((row for row in body_panels if exact_text in (row.get("exactText") or "")), None)
        if panel is None:
            panel = next((row for row in body_panels if (row.get("exactText") or "") in exact_text), body_panels[0])
        rows.append({
            "sentenceId": f"GI-{asset['assetKey'].upper()}-S{sequence:02d}",
            "sequence": sequence,
            "regionId": "R3",
            "panelId": panel["panelId"],
            "exactText": exact_text,
            "start": start,
            "end": end,
        })
        cursor = end
    return rows


def _source_icons(asset: dict, selected_run: dict | None, vision_result: dict | None, panels: list[dict]) -> list[dict]:
    selected_run = selected_run or {}
    vision_result = vision_result or {}
    verified = list(selected_run.get("verifiedIconOccurrences") or [])
    unresolved = list(selected_run.get("unresolvedIconOccurrences") or [])
    canonical_claims = {row.get("claimed"): row for row in (((vision_result.get("iconVerification") or {}).get("parsed") or {}).get("claims") or [])}
    rows = []
    body_cursor = 0
    for sequence, (location, source_token, semantic_reference, evidence_kind, evidence_index) in enumerate(asset["iconSpecs"], 1):
        if location == "upperRight":
            start, end = 0, len(asset["upperRight"])
            panel = panels[1]
        else:
            start = asset["printedBody"].find(source_token, body_cursor)
            if start < 0:
                raise AssertionError(f"Green Item icon span missing: {asset['assetKey']}:{source_token}")
            end = start + len(source_token)
            body_cursor = end
            panel = next((item for item in panels[2:] if source_token in (item.get("exactText") or "")), panels[2])
        if evidence_kind == "canonical":
            token = semantic_reference.removeprefix("icon.") if semantic_reference else None
            evidence = canonical_claims.get(token)
            if not evidence or evidence.get("verdict") != "match" or evidence.get("actual") != token:
                raise AssertionError(f"Green Item canonical icon evidence missing: {asset['assetKey']}:{token}")
            mapping_status = "canonical-sidecar-plus-independent-icon-verification"
            page40_assigned = True
            literal = evidence.get("evidence")
        elif evidence_kind == "selected-verified":
            if evidence_index >= len(verified):
                raise AssertionError(f"Green Item selected verified icon evidence missing: {asset['assetKey']}:{sequence}")
            evidence = verified[evidence_index]
            token = semantic_reference.removeprefix("icon.") if semantic_reference else None
            if evidence.get("matchDecision") != "match" or evidence.get("canonicalToken") != token:
                raise AssertionError(f"Green Item selected verified icon drift: {asset['assetKey']}:{sequence}")
            mapping_status = "selected-source-scoped-authoritative-match"
            page40_assigned = True
            literal = evidence.get("visibleDiscriminator") or evidence.get("referenceLabel")
        elif evidence_kind == "selected-unresolved":
            if evidence_index >= len(unresolved):
                raise AssertionError(f"Green Item selected unresolved icon evidence missing: {asset['assetKey']}:{sequence}")
            evidence = unresolved[evidence_index]
            if evidence.get("matchDecision") != "no-match" or evidence.get("canonicalToken") is not None or semantic_reference is not None:
                raise AssertionError(f"Green Item selected unresolved icon drift: {asset['assetKey']}:{sequence}")
            mapping_status = "selected-explicit-authoritative-no-match"
            page40_assigned = False
            literal = evidence.get("referenceLabel") or source_token
        else:
            raise AssertionError(f"unknown Green Item icon evidence kind: {evidence_kind}")
        rows.append({
            "assetIconOccurrenceId": f"GI-ASSET-{asset['assetKey'].upper()}-I{sequence:02d}",
            "sequence": sequence,
            "regionId": "R2" if location == "upperRight" else "R3",
            "panelId": panel["panelId"],
            "cardLocationClass": location,
            "sourceToken": source_token,
            "start": start,
            "end": end,
            "literalAppearance": literal,
            "semanticReferenceId": semantic_reference,
            "mappingStatus": mapping_status,
            "page40TokenAssigned": page40_assigned,
            "mappingScope": f"exact source asset {asset['sourcePath']} occurrence only",
            "selectedEvidence": evidence,
        })
    expected_verified_indices = {spec[4] for spec in asset["iconSpecs"] if spec[3] == "selected-verified"}
    expected_unresolved_indices = {spec[4] for spec in asset["iconSpecs"] if spec[3] == "selected-unresolved"}
    if expected_verified_indices != set(range(len(verified))) or expected_unresolved_indices != set(range(len(unresolved))):
        raise AssertionError(f"Green Item selected icon evidence count drift: {asset['assetKey']}")
    return rows


def build_green_item_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / CORPUS_PATH).read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    selected = json.loads((repo / SELECTED_EVIDENCE_PATH).read_text(encoding="utf-8"))
    selected_by_path = {row["sourcePath"]: row for row in selected["entries"]}
    progress = json.loads((repo / VISION_PROGRESS_PATH).read_text(encoding="utf-8"))
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    low = json.loads((repo / LOW_CONFIDENCE_PATH).read_text(encoding="utf-8"))
    low_by_path = {row["sourcePath"]: row for row in low["entries"]}
    provenance = json.loads((repo / PROVENANCE_PATH).read_text(encoding="utf-8"))
    provenance_by_file = {row["file"]: row for row in provenance}
    roles = json.loads((repo / "assets/tts-mod/extract/v2/lua_roles.json").read_text(encoding="utf-8"))
    objects = json.loads((repo / "assets/tts-mod/extract/v2/objects.json").read_text(encoding="utf-8"))
    classification = json.loads((repo / "assets/tts-mod/extract/v2/classification.json").read_text(encoding="utf-8"))
    secondary = json.loads((repo / "docs/rules/source-extraction/secondary-evidence-index.json").read_text(encoding="utf-8"))
    visuals = json.loads((repo / "docs/rules/source-extraction/rulebook-visual-obligations.json").read_text(encoding="utf-8"))
    faq = json.loads((repo / "docs/rules/source-extraction/faq-v1.2-source-extraction.json").read_text(encoding="utf-8"))
    backlog = json.loads((repo / "docs/rules/semantics/backlog.json").read_text(encoding="utf-8"))
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}

    matching_roles = [row for row in roles if row.get("role") == "greenItemsDeck"]
    if len(matching_roles) != 1:
        raise AssertionError("Green Item Lua role multiplicity changed")
    role = matching_roles[0]
    expected_deck_nums = ["37", "4001", "4159", "4160", "4161", "5365", "5366", "5367"]
    if role.get("guid") != BASE_GREEN_ITEM_DECK_GUID or role.get("type") != "Deck" or role.get("gmnotes") != "greenitemDiscard" or role.get("n_urls") != 7 or role.get("deck_nums") != expected_deck_nums:
        raise AssertionError("base Green Item Lua role changed")

    raw_deck, raw_save_sha = _raw_green_deck(repo)
    raw_deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
    expected_deck_ids = [row["ttsCardId"] for row in ROOT_PHYSICAL_DEFINITIONS]
    if raw_deck_ids != expected_deck_ids:
        raise AssertionError("base Green Item raw DeckIDs order changed")
    contained_value = raw_deck.get("ContainedObjects") or {}
    contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
    expected_children = [(row["ttsCardId"], row["ttsCardGuid"]) for row in ROOT_PHYSICAL_DEFINITIONS]
    actual_children = [(int(row["CardID"]), row["GUID"]) for row in contained]
    if actual_children != expected_children:
        raise AssertionError("base Green Item raw contained occurrence order changed")
    root_custom = raw_deck.get("CustomDeck") or {}
    if set(root_custom) != set(expected_deck_nums):
        raise AssertionError("base Green Item root CustomDeck IDs changed")
    expected_custom = {
        "5365": ("https://steamusercontent-a.akamaihd.net/ugc/18382559417803082430/AF76204C25941F3983000186E7FDB49829A439D9/", SHARED_BACK_URL, 1, 1),
        "5366": ("https://steamusercontent-a.akamaihd.net/ugc/16626696722124461178/E6AEC973279E33B07B582A15C1C7B109CA7F9D83/", SHARED_BACK_URL, 1, 1),
        "5367": ("https://steamusercontent-a.akamaihd.net/ugc/16879121740466996812/12DF8EC9C9991AC9A6C556177FB7A422C4D7BB60/", SHARED_BACK_URL, 1, 1),
        "4159": ("https://steamusercontent-a.akamaihd.net/ugc/11926683858157864/F88CBC6F0EB59AC169BD77C9F570F485A54698AA/", SHARED_BACK_URL, 1, 1),
        "4160": ("https://steamusercontent-a.akamaihd.net/ugc/11926683858157864/F88CBC6F0EB59AC169BD77C9F570F485A54698AA/", SHARED_BACK_URL, 1, 1),
        "4161": ("https://steamusercontent-a.akamaihd.net/ugc/11926683858157864/F88CBC6F0EB59AC169BD77C9F570F485A54698AA/", SHARED_BACK_URL, 1, 1),
        "4001": ("https://steamusercontent-a.akamaihd.net/ugc/11925215517194819/8B57837741BBDED9848E21878E83C94B0C4FFD62/", SHARED_BACK_URL, 1, 1),
        "37": (SHEET_FACE_URL, SHARED_BACK_URL, 3, 3),
    }
    for custom_id, expected in expected_custom.items():
        custom = root_custom[custom_id]
        if (custom.get("FaceURL"), custom.get("BackURL"), custom.get("NumWidth"), custom.get("NumHeight")) != expected:
            raise AssertionError(f"base Green Item CustomDeck tuple changed: {custom_id}")

    root_object = next(row for row in objects if row.get("guid") == BASE_GREEN_ITEM_DECK_GUID)
    green_children = [row for row in objects if ["Deck", BASE_GREEN_ITEM_DECK_GUID, ""] in (row.get("parent") or []) and row.get("gmnotes") == "greenitem"]
    all_green_tagged = [row for row in objects if row.get("gmnotes") == "greenitem"]
    child_by_tuple = {(int(row["card_id"]), row["guid"]): row for row in green_children}
    if root_object.get("type") != "Deck" or root_object.get("parent") != [] or len(green_children) != 30 or len(all_green_tagged) != 30 or set(child_by_tuple) != set(expected_children):
        raise AssertionError("base Green Item object/tag/container closure changed")
    classification_by_guid = {row["guid"]: row for row in classification}
    if classification_by_guid[BASE_GREEN_ITEM_DECK_GUID].get("verdict") != "base" or any(classification_by_guid[guid].get("verdict") != "base" for _, guid in expected_children):
        raise AssertionError("Green Item base classification changed")

    bga_rows = _parse_bga_green_items(repo / BGA_ITEMS_PATH)
    bga_table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "ITEMS_DATA")
    if bga_table.get("count") != 57 or not set(row["key"] for row in bga_rows).issubset(set(bga_table.get("keys") or [])):
        raise AssertionError("licensed Green Item evidence-index closure changed")
    if sum(row["nbr"] for row in bga_rows) != 30 or sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]) != 23 or sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]) != 7:
        raise AssertionError("licensed Green Item aggregate class/count boundary changed")

    source_asset_rows = []
    source_asset_by_key = {}
    for asset_key, asset in ASSET_DEFINITIONS.items():
        source_path = asset["sourcePath"]
        source_sha = _sha(repo / source_path)
        corpus_row = corpus_by_path.get(source_path) or {}
        if corpus_row.get("sourceSha256") != source_sha or not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"}:
            raise AssertionError(f"Green Item corpus/hash readiness drift: {asset_key}")
        if corpus_row.get("printedData", {}).get("body") != asset["printedBody"]:
            raise AssertionError(f"Green Item exact corpus body drift: {asset_key}")
        selected_entry = selected_by_path.get(source_path) or {}
        selected_runs = selected_entry.get("runs") or []
        selected_run = selected_runs[0] if len(selected_runs) == 1 else None
        if corpus_row.get("extractionState") == "draft-full":
            if selected_run is None or (selected_run.get("visibleText") or {}).get("title") != asset["printedTitle"] or (selected_run.get("visibleText") or {}).get("body") != asset["printedBody"]:
                raise AssertionError(f"Green Item selected title/body evidence drift: {asset_key}")
        elif selected_runs:
            raise AssertionError(f"Green Item canonical asset unexpectedly depends on selected overlay: {asset_key}")
        progress_row = progress_by_path.get(source_path) or {}
        vision_result_path = (progress_row.get("vision") or {}).get("resultPath")
        vision_result = json.loads((repo / vision_result_path).read_text(encoding="utf-8")) if vision_result_path else None
        if corpus_row.get("extractionState") == "verified-canonical":
            parsed = (vision_result or {}).get("parsed") or {}
            if parsed.get("title") != asset["printedTitle"] or parsed.get("body") != asset["printedBody"]:
                raise AssertionError(f"Green Item canonical title/body evidence drift: {asset_key}")
        generated = progress_row.get("generatedFrom") or (low_by_path.get(source_path) or {}).get("provenance") or {}
        if asset["generatedCell"] is not None:
            if generated.get("sourceSheetPath") != GREEN_ITEM_SHEET_PATH or generated.get("cellIndex") != asset["generatedCell"]:
                raise AssertionError(f"Green Item generated source/cell drift: {asset_key}")
        elif generated.get("sourceSheetPath") is not None or generated.get("cellIndex") is not None:
            raise AssertionError(f"Green Item direct/generated inversion: {asset_key}")
        panels = _source_panels(asset)
        regions = _source_regions(asset)
        sentences = _source_sentences(asset, panels)
        icons = _source_icons(asset, selected_run, vision_result, panels)
        selected_occurrences = [row["occurrenceId"] for row in ROOT_PHYSICAL_DEFINITIONS if row["assetKey"] == asset_key]
        gap_source_id = f"SRC-GREEN-ITEM-VARIANT-37-CELL-{asset['generatedCell']:02d}" if asset["sourceRole"] == "generated-cell-selector-gap-variant" else None
        source_asset_row = {
            **{key: asset[key] for key in ("assetKey", "sourcePath", "sourceRole", "customDeckIds", "generatedCell", "physicalClass", "selectedRegular", "printedTitle", "typeLine", "upperRight", "printedBody", "effectKind", "namedIdentityRef")},
            "sourceId": gap_source_id,
            "sourceSha256": source_sha,
            "sourceSheetId": GREEN_ITEM_SHEET_SOURCE_ID if asset["generatedCell"] is not None else None,
            "sourceSheetPath": GREEN_ITEM_SHEET_PATH if asset["generatedCell"] is not None else None,
            "sourceSheetGrid": {"columns": 3, "rows": 3} if asset["generatedCell"] is not None else None,
            "selectedByRootDeck": bool(selected_occurrences),
            "selectedPhysicalOccurrenceIds": selected_occurrences,
            "selectorGap": None if selected_occurrences else {
                "status": "explicit-no-root-DeckID-GUID-selector",
                "reason": "The generated cell exists in the exact 3x3 source sheet and closed corpus, but no raw root DeckID/contained GUID selects it; it remains a source variant rather than a physical root-deck face.",
                "cardIdModuloJoinUsed": False,
            },
            "regions": regions,
            "panels": panels,
            "sentences": sentences,
            "iconOccurrences": icons,
            "printedBodyDigest": _digest({"title": asset["printedTitle"], "typeLine": asset["typeLine"], "upperRight": asset["upperRight"], "body": asset["printedBody"]}),
            "panelDigest": _digest(panels),
            "iconDigest": _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in icons]),
            "corpusEvidencePath": CORPUS_PATH,
            "selectedEvidencePath": SELECTED_EVIDENCE_PATH if selected_run else None,
            "visionEvidencePath": vision_result_path,
            "generatedCellEvidencePath": VISION_PROGRESS_PATH,
            "extractionState": corpus_row["extractionState"],
            "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
        }
        source_asset_rows.append(source_asset_row)
        source_asset_by_key[asset_key] = source_asset_row

    sheet_path = repo / GREEN_ITEM_SHEET_PATH
    with Image.open(sheet_path) as sheet_image:
        if sheet_image.size != (1773, 2589) or sheet_image.width % 3 or sheet_image.height % 3:
            raise AssertionError("Green Item source-sheet dimensions/grid changed")
        for cell in range(9):
            row_index, column_index = divmod(cell, 3)
            crop = sheet_image.crop((column_index * 591, row_index * 863, (column_index + 1) * 591, (row_index + 1) * 863)).convert("RGB")
            generated_asset = source_asset_by_key[f"sheet-{cell:02d}"]
            with Image.open(repo / generated_asset["sourcePath"]) as generated_image:
                if generated_image.convert("RGB").tobytes() != crop.tobytes():
                    raise AssertionError(f"Green Item generated-cell pixel drift: {cell}")

    contained_by_tuple = {(int(row["CardID"]), row["GUID"]): row for row in contained}

    def build_physical(definition: dict) -> dict:
        asset = source_asset_by_key[definition["assetKey"]]
        raw_child = contained_by_tuple[(definition["ttsCardId"], definition["ttsCardGuid"])]
        custom = root_custom[definition["customDeckId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        selector = {
            "key": "FaceURL",
            "objectType": raw_child.get("Name"),
            "fullCardId": definition["ttsCardId"],
            "guid": definition["ttsCardGuid"],
            "parentDeckGuid": BASE_GREEN_ITEM_DECK_GUID,
            "customDeckId": definition["customDeckId"],
            "url": custom["FaceURL"],
            "backUrl": custom["BackURL"],
            "sideRole": "operative-regular-green-item-face" if definition["regular"] else "excluded-heavy-item-face",
            "sourceRole": asset["sourceRole"],
            "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-BackURL-parent-tuple-with-explicit-generated-cell" if asset["generatedCell"] is not None else "exact-full-CardID-GUID-direct-FaceURL-BackURL-parent-tuple",
            "generatedSpriteSheetCell": asset["generatedCell"] is not None,
            "sourceSheetPath": asset["sourceSheetPath"],
            "sourceSheetSha256": _sha(sheet_path) if asset["generatedCell"] is not None else None,
            "sourceSheetGrid": asset["sourceSheetGrid"],
            "generatedCell": asset["generatedCell"],
            "selectorGap": None,
            "cardIdModuloJoinUsed": False,
        }
        provenance_source_path = GREEN_ITEM_SHEET_PATH if asset["generatedCell"] is not None else asset["sourcePath"]
        provenance_file = provenance_source_path.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]
        provenance_row = provenance_by_file.get(provenance_file) or {}
        exact_ref = next((row for row in provenance_row.get("objects") or [] if row.get("key") == "FaceURL" and row.get("guid") == definition["ttsCardGuid"] and row.get("cardId") == definition["ttsCardId"]), None)
        if exact_ref is None or exact_ref.get("parent") != [["Deck", BASE_GREEN_ITEM_DECK_GUID, ""]] or provenance_row.get("url") != custom["FaceURL"]:
            raise AssertionError(f"Green Item exact provenance selector drift: {code}")
        physical_regions = [{**region, "regionId": f"GI-{code}-{region['regionId']}"} for region in asset["regions"]]
        region_map = {old: new["regionId"] for old, new in zip(("R1", "R2", "R3"), physical_regions)}
        physical_panels = [
            {**panel, "panelId": f"GI-{code}-{panel['panelId']}", "regionId": region_map[panel["regionId"]]}
            for panel in asset["panels"]
        ]
        panel_map = {source["panelId"]: physical["panelId"] for source, physical in zip(asset["panels"], physical_panels)}
        physical_sentences = [
            {**sentence, "sentenceId": f"GI-{code}-S{sentence['sequence']:02d}", "regionId": region_map[sentence["regionId"]], "panelId": panel_map[sentence["panelId"]]}
            for sentence in asset["sentences"]
        ]
        physical_icons = [
            {
                **icon,
                "occurrenceId": f"GI-{code}-I{icon['sequence']:02d}",
                "assetMorphologyOccurrenceId": icon["assetIconOccurrenceId"],
                "regionId": region_map[icon["regionId"]],
                "panelId": panel_map[icon["panelId"]],
                "mappingScope": f"exact physical root occurrence {definition['occurrenceId']} only",
            }
            for icon in asset["iconOccurrences"]
        ]
        backlog_id = "CARD:" + asset["sourceSha256"][:16]
        backlog_row = backlog_by_id.get(backlog_id) or {}
        if backlog_row.get("sourcePath") != asset["sourcePath"] or backlog_row.get("sourceLocator") != asset["sourceSha256"]:
            raise AssertionError(f"Green Item backlog source tuple drift: {definition['occurrenceId']}")
        row = {
            "greenItemOccurrenceId": definition["occurrenceId"],
            "rootSequence": definition["rootSequence"],
            "familySequence": definition.get("familySequence"),
            "ttsRole": "greenItemsDeck",
            "ttsDeckGuid": BASE_GREEN_ITEM_DECK_GUID,
            "ttsDeckType": "Deck",
            "ttsCardId": definition["ttsCardId"],
            "ttsCardGuid": definition["ttsCardGuid"],
            "customDeckId": definition["customDeckId"],
            "sourceSelector": selector,
            "sourceId": definition["sourceId"],
            "sourcePath": asset["sourcePath"],
            "sourceSha256": asset["sourceSha256"],
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS source-bound base greenItemsDeck root occurrence {definition['rootSequence']} / full CardID {definition['ttsCardId']} / GUID {definition['ttsCardGuid']}",
            "sourceAssetKey": definition["assetKey"],
            "physicalClass": asset["physicalClass"],
            "batchDisposition": "included-regular-green-item-face" if definition["regular"] else "excluded-heavy-item-face",
            "printedTitle": asset["printedTitle"],
            "typeLine": asset["typeLine"],
            "upperRight": asset["upperRight"],
            "printedBody": asset["printedBody"],
            "effectKind": asset["effectKind"],
            "namedIdentityRef": asset["namedIdentityRef"],
            "regions": physical_regions,
            "panels": physical_panels,
            "sentences": physical_sentences,
            "iconOccurrences": physical_icons,
            "printedBodyDigest": asset["printedBodyDigest"],
            "panelDigest": _digest(physical_panels),
            "iconDigest": _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in physical_icons]),
            "semanticRuleId": definition["semanticRuleId"],
            "backlogUnitId": backlog_id,
            "corpusEvidencePath": CORPUS_PATH,
            "provenanceEvidencePath": PROVENANCE_PATH,
            "licensedCrosswalk": {"status": "not-asserted", "reason": "licensed rows remain independent; no title, color, body, order, multiplicity, or key establishes physical copy identity"},
            "officialCrosswalk": {"status": "not-asserted", "reason": "no checked official visible component occurrence identifies this TTS CardID/GUID copy"},
            "joinEvidence": {
                "identityJoin": "exact raw root physical occurrence and exact source-asset projection",
                "titleOnlyJoin": False,
                "colorOnlyJoin": False,
                "bodyResemblanceJoin": False,
                "folderOnlyJoin": False,
                "sourceOrderOnlyJoin": False,
                "generatedCellOnlyJoin": False,
                "cardIdModuloJoin": False,
                "licensedKeyJoin": False,
                "basis": [
                    "sole base greenItemsDeck Lua role and exact raw root GUID",
                    "raw saved DeckIDs sequence plus contained full CardID/GUID occurrence",
                    "exact CustomDeck ID, FaceURL, BackURL, parent deck, and source SHA-256",
                    "for generated faces: exact 3x3 sheet hash/grid/cell plus full selector",
                ],
            },
        }
        return row

    regular_faces = [build_physical(row) for row in REGULAR_PHYSICAL_DEFINITIONS]
    excluded_heavy_faces = [build_physical(row) for row in EXCLUDED_HEAVY_DEFINITIONS]

    back_path = repo / GREEN_ITEM_BACK_PATH
    back_provenance = provenance_by_file[GREEN_ITEM_BACK_PATH.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]]
    if back_provenance.get("refs") != 31 or {row.get("key") for row in back_provenance.get("objects") or []} != {"BackURL"}:
        raise AssertionError("Green Item shared-back provenance changed")
    sheet_provenance = provenance_by_file[GREEN_ITEM_SHEET_PATH.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]]
    if sheet_provenance.get("refs") != 16 or {row.get("key") for row in sheet_provenance.get("objects") or []} != {"FaceURL"}:
        raise AssertionError("Green Item parent-sheet provenance changed")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    official_ids = ["RB-P03-V01", "RB-P09-V01", "RB-P12-V02", "RB-P28-V02", "RB-P28-V03", "RB-P29-V01", "RB-P40-V02"]
    if any(occurrence_id not in visual_by_id for occurrence_id in official_ids):
        raise AssertionError("Green Item official visual occurrence missing")
    official_counterparts = [
        {"sourceOccurrenceId": "RB-P03-V01", "kind": "family-count-and-representative-card-images", "locator": "unprinted component page 3 / Item cards row", "visibleText": "90 Item cards (30 cards of each type)", "exactGreenRulesFace": False},
        {"sourceOccurrenceId": "RB-P09-V01", "kind": "setup-deck-placement", "locator": "printed page 9 / C. Remaining Components", "visibleText": "3 Item decks (red, green, yellow), each shuffled separately face down with discard-pile space", "exactGreenRulesFace": False},
        {"sourceOccurrenceId": "RB-P12-V02", "kind": "use-item-action-cost", "locator": "printed page 12 / Basic Actions List", "visibleText": "Use an Item is grouped under Costing 1 Action card", "exactGreenRulesFace": False},
        {"sourceOccurrenceId": "RB-P28-V02", "kind": "green-item-search-icon", "locator": "printed page 28 / Search example", "visibleText": "Green Item icon participates in one-card-per-icon Search and private bottom return", "exactGreenRulesFace": False},
        {"sourceOccurrenceId": "RB-P28-V03", "kind": "regular-item-anatomy-example", "locator": "printed page 28 / Duct Tape example", "visibleText": "Vertical ONE USE ONLY regular Item anatomy and branch grouping", "exactGreenRulesFace": False},
        {"sourceOccurrenceId": "RB-P29-V01", "kind": "heavy-item-exclusion-boundary", "locator": "printed page 29 / Heavy Item example", "visibleText": "All horizontal Items are Heavy and do not fit in a Backpack", "exactGreenRulesFace": False},
        {"sourceOccurrenceId": "RB-P40-V02", "kind": "green-item-icon-glossary", "locator": "printed page 40 / MAP-RELATED ICONS", "visibleText": "Red, Yellow, Green Item — An Item of a specific type", "exactGreenRulesFace": False},
    ]

    faq_units = [unit for page in faq["pages"] for unit in page.get("units", [])]
    faq_by_id = {unit["sourceUnitId"]: unit for unit in faq_units}
    relevant_faq_ids = ["FQ-P02-U04", "FQ-P03-U04", "FQ-P03-U07"]
    relevant_faq = [
        {"sourceUnitId": source_id, "applicability": faq_by_id[source_id]["applicability"], "printedText": faq_by_id[source_id]["printedText"]}
        for source_id in relevant_faq_ids
    ]
    if any(row["applicability"] not in {"base-game", "base-game-additional-mode"} for row in relevant_faq):
        raise AssertionError("Green Item FAQ applicability changed")
    excluded_faq = [unit["sourceUnitId"] for unit in faq_units if unit.get("applicability", "").startswith("expansion") and re.search(r"Item|Health|Oxygen", unit.get("printedText", ""), re.I)]

    selected_asset_keys = {row["assetKey"] for row in REGULAR_PHYSICAL_DEFINITIONS}
    selected_asset_rows = [row for row in source_asset_rows if row["assetKey"] in selected_asset_keys]
    gap_asset_rows = [row for row in source_asset_rows if row["sourceRole"] == "generated-cell-selector-gap-variant"]
    heavy_asset_rows = [row for row in source_asset_rows if row["physicalClass"] == "heavy-item"]
    face_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in selected_asset_rows})
    variant_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in gap_asset_rows})
    excluded_heavy_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in heavy_asset_rows})
    overlapping_unit_ids = [
        "RULE:ACT-ITEM-001", "RULE:ACT-TRADE-001",
        "RULE:ITM-001", "RULE:ITM-002", "RULE:ITM-003", "RULE:ITM-004", "RULE:ITM-006", "RULE:ITM-008",
        "FAQ:FQ-P02-U04", "FAQ:FQ-P03-U04", "FAQ:FQ-P03-U07",
        "VIS:RB-P03-V01", "VIS:RB-P09-V01", "VIS:RB-P12-V02", "VIS:RB-P28-V02", "VIS:RB-P28-V03", "VIS:RB-P29-V01", "VIS:RB-P40-V02",
    ]
    linked_unit_ids = sorted(set(face_unit_ids + variant_unit_ids + overlapping_unit_ids))
    if any(unit_id not in backlog_by_id for unit_id in linked_unit_ids + excluded_heavy_unit_ids):
        raise AssertionError("Green Item backlog obligation ID missing")

    title_multiplicity = dict(sorted(Counter(row["printedTitle"] for row in regular_faces).items()))
    asset_multiplicity = dict(sorted(Counter(row["sourceAssetKey"] for row in regular_faces).items()))
    root_class_multiplicity = dict(sorted(Counter(row["physicalClass"] for row in regular_faces + excluded_heavy_faces).items()))
    regular_icons = [icon for face in regular_faces for icon in face["iconOccurrences"]]
    gap_icons = [icon for asset in gap_asset_rows for icon in asset["iconOccurrences"]]

    counts = {
        "rootPhysicalOccurrences": 30,
        "physicalFaceOccurrences": len(regular_faces),
        "excludedHeavyPhysicalOccurrences": len(excluded_heavy_faces),
        "uniquePrintedTitles": len(title_multiplicity),
        "uniqueSelectedFaceAssets": len(selected_asset_rows),
        "sourceFaceAssets": len(source_asset_rows),
        "generatedPhysicalFaceOccurrences": sum((row["sourceSelector"] or {}).get("generatedSpriteSheetCell") is True for row in regular_faces),
        "directPhysicalFaceOccurrences": sum((row["sourceSelector"] or {}).get("generatedSpriteSheetCell") is False for row in regular_faces),
        "sourceSheets": 1,
        "sourceSheetCells": 9,
        "selectedGeneratedCells": sum(row["generatedCell"] is not None for row in selected_asset_rows),
        "selectorGapCells": len(gap_asset_rows),
        "sharedBackOccurrences": 1,
        "sharedBackSelectorReferences": 31,
        "sourceSheetSelectorReferences": 16,
        "rootCustomDeckEntries": len(root_custom),
        "physicalRegions": sum(len(row["regions"]) for row in regular_faces),
        "operativeRegions": sum(sum(region["operative"] for region in row["regions"]) for row in regular_faces),
        "physicalPanels": sum(len(row["panels"]) for row in regular_faces),
        "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in regular_faces),
        "oneUseHeadingOccurrences": len(regular_faces),
        "useDiscardPassiveReactionHeadingOccurrences": 0,
        "printedSentenceOccurrences": sum(len(row["sentences"]) for row in regular_faces),
        "physicalFunctionalIconOccurrences": len(regular_icons),
        "physicalMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in regular_icons),
        "physicalUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in regular_icons),
        "selectorGapFunctionalIconOccurrences": len(gap_icons),
        "selectorGapMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in gap_icons),
        "selectorGapUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in gap_icons),
        "licensedDigitalOccurrences": len(bga_rows),
        "licensedDigitalPhysicalCopies": sum(row["nbr"] for row in bga_rows),
        "licensedRegularOccurrences": sum(not row["heavy"] and not row["armor"] for row in bga_rows),
        "licensedRegularPhysicalCopies": sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]),
        "licensedHeavyOccurrences": sum(row["heavy"] or row["armor"] for row in bga_rows),
        "licensedHeavyPhysicalCopies": sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]),
        "officialInventoryCopiesPerType": 30,
        "officialVisibleFaceOccurrences": 0,
        "officialVisibleBackOccurrences": 0,
        "officialFamilyVisualOccurrences": len(official_counterparts),
        "baseApplicableFaqOccurrences": len(relevant_faq),
        "excludedExpansionFaqOccurrences": len(excluded_faq),
        "backlogTuples": len(face_unit_ids) + len(variant_unit_ids),
        "backlogPhysicalFaceLinks": len(regular_faces),
        "backlogObligationsLinked": len(linked_unit_ids),
        "semanticPhysicalFaceRecords": len(regular_faces),
    }

    return {
        "schemaVersion": 1,
        "recordType": "semantic-green-item-source-index",
        "scope": "entire mechanically derived base regular Green Item card family: 23 physical Backpack-card occurrences selected from a 30-child greenItemsDeck root after retaining seven Heavy occurrences as explicit exclusions; four generated selector-gap variants, one parent sheet, one shared back, official family evidence, and ten licensed rows remain independent",
        "derivationPolicy": "Derive the root only from the sole base greenItemsDeck Lua role and exact raw root GUID, saved DeckIDs order, contained full CardID/GUID/CustomDeck/FaceURL/BackURL tuples, and for generated faces exact source-sheet hash/grid/cell evidence. Apply the official physical-class rule to exclude all horizontal Heavy Items from this bounded regular Green family. Never join by title, item color alone, body similarity, folder, source order, generated-cell position alone, CardID modulo, licensed key, or multiplicity.",
        "counts": counts,
        "rootDeckEvidence": {
            "sourceId": GREEN_ITEM_ROOT_SOURCE_ID,
            "ttsRole": "greenItemsDeck",
            "rootGuid": BASE_GREEN_ITEM_DECK_GUID,
            "rootType": "Deck",
            "rootGmNotes": "greenitemDiscard",
            "rawSavePath": RAW_SAVE_PATH,
            "rawSaveSha256": raw_save_sha,
            "luaRolePath": "assets/tts-mod/extract/v2/lua_roles.json",
            "objectsPath": "assets/tts-mod/extract/v2/objects.json",
            "savedDeckIds": raw_deck_ids,
            "fullContainedSelectors": [{"rootSequence": row["rootSequence"], "fullCardId": row["ttsCardId"], "guid": row["ttsCardGuid"], "customDeckId": row["customDeckId"], "batchDisposition": "included-regular" if row["regular"] else "excluded-heavy"} for row in ROOT_PHYSICAL_DEFINITIONS],
            "customDeckTuples": {key: {"faceUrl": value[0], "backUrl": value[1], "columns": value[2], "rows": value[3]} for key, value in sorted(expected_custom.items())},
            "rootOrderIsGameplayOrder": False,
            "reason": "official setup shuffles each Item deck separately; saved sequence is provenance only",
        },
        "familyCountEvidence": {
            "official": {"count": 30, "scope": "Item cards of each type", "source": "RB-P03-V01 / rulebook_text lines 520–521"},
            "tts": {"rootChildren": 30, "regularIncluded": 23, "heavyExcluded": 7, "classMultiplicity": root_class_multiplicity},
            "licensedDigital": {"deckGreenRows": len(bga_rows), "declaredCopies": sum(row["nbr"] for row in bga_rows), "regularCopies": sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]), "heavyCopies": sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]), "physicalIdentityCrosswalkAsserted": False},
            "reconciliation": "All channels preserve the 30-card color-deck aggregate. This bounded batch includes the independently matching 23 regular/Backpack occurrences and retains the seven Heavy occurrences outside Green regular face semantics; aggregate equality is not a copy crosswalk.",
            "backlog": {
                "faceUnitIds": face_unit_ids,
                "variantUnitIds": variant_unit_ids,
                "excludedHeavyUnitIds": excluded_heavy_unit_ids,
                "overlappingUnitIds": sorted(overlapping_unit_ids),
                "linkedUnitIds": linked_unit_ids,
                "faceTupleCount": len(face_unit_ids),
                "variantTupleCount": len(variant_unit_ids),
                "physicalFaceLinkCount": len(regular_faces),
                "obligationCount": len(linked_unit_ids),
            },
        },
        "titleMultiplicity": title_multiplicity,
        "selectedAssetMultiplicity": asset_multiplicity,
        "sourceSheet": {
            "sourceId": GREEN_ITEM_SHEET_SOURCE_ID,
            "occurrenceId": "TTS-GREEN-ITEM-PARENT-SHEET-37",
            "sourcePath": GREEN_ITEM_SHEET_PATH,
            "sourceSha256": _sha(sheet_path),
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": "TTS base Green Item CustomDeck 37 parent 3x3 face sheet",
            "sourceSelector": {"key": "FaceURL", "rootGuid": BASE_GREEN_ITEM_DECK_GUID, "customDeckId": "37", "url": SHEET_FACE_URL, "grid": {"columns": 3, "rows": 3}, "sideRole": "parent-sheet-provenance-not-rules-face"},
            "selectorReferences": 16,
            "selectedCells": [0, 1, 3, 5, 7],
            "selectorGapCells": [2, 4, 6, 8],
            "separateRulesFace": False,
        },
        "sharedBack": {
            "sourceId": GREEN_ITEM_BACK_SOURCE_ID,
            "occurrenceId": "TTS-GREEN-ITEM-SHARED-BACK",
            "sourcePath": GREEN_ITEM_BACK_PATH,
            "sourceSha256": _sha(back_path),
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": "TTS base Green Item shared non-operative back",
            "sourceSelector": {"key": "BackURL", "rootGuid": BASE_GREEN_ITEM_DECK_GUID, "url": SHARED_BACK_URL, "sideRole": "shared-non-operative-green-item-back"},
            "selectorReferences": 31,
            "visibleText": "ITEM",
            "visibleGreenItemBadge": True,
            "rulesTextPresent": False,
            "separateRulesFace": False,
        },
        "sourceFaceAssets": source_asset_rows,
        "faces": regular_faces,
        "excludedHeavyFaces": excluded_heavy_faces,
        "licensedDigitalOccurrences": bga_rows,
        "officialVisibleCounterparts": official_counterparts,
        "officialRulebookTextOccurrences": [
            {"locator": "unprinted page 3 / lines 520–521", "text": "90 Item cards (30 cards of each type)"},
            {"locator": "printed page 9 / lines 2593–2600", "text": "Take the 3 Item decks (red, green, yellow), shuffle each separately, place face down, and leave discard-pile space."},
            {"locator": "printed page 17 / lines 3530–3548", "text": "Whole-effect, local-effect, and finite-component Golden Rules."},
            {"locator": "printed page 17 / lines 3665–3673", "text": "Characters may discard any number of Items at any point; Items go to the Items discard pile."},
            {"locator": "printed page 28 / lines 4849–4923", "text": "Search draws by Item icon, returns unchosen cards to respective deck bottoms privately, defines regular Item use and unlimited secret Backpack storage."},
            {"locator": "printed page 29 / lines 4933–4951", "text": "One Use Only Items are discarded when Used; horizontal Items are Heavy and held in Hands."},
            {"locator": "printed page 29 / lines 5079–5103", "text": "Interplay and Trade consent, co-location, reveal, and exchange rules."},
        ],
        "faqSearchClosure": {"baseApplicableOccurrences": relevant_faq, "excludedExpansionOccurrences": excluded_faq},
        "exclusions": {
            "redYellowDecks": [{"role": "redItemsDeck", "guid": "9027ed"}, {"role": "yellowItemsDeck", "guid": "fe68f3"}],
            "heavyEquipmentStarting": {"startItemDeckRole": "startItemDeck", "startItemDeckGuid": "f71196", "rootGreenHeavyOccurrenceIds": [row["greenItemOccurrenceId"] for row in excluded_heavy_faces]},
            "tacticalGear": "Green Medpack tokens, slots, and green-colored Tactical Gear art are not Green Item card faces.",
            "parentBackGaps": {"parentSheet": GREEN_ITEM_SHEET_PATH, "sharedBack": GREEN_ITEM_BACK_PATH, "selectorGapCells": [2, 4, 6, 8]},
            "other": "Expansion/prototype decks, placeholders, duplicate root/child/corpus/provenance references, generated parent sheets, backs, and non-rules overlays never enter the 23-face count.",
        },
        "fidelityBoundaries": {
            "rootVersusFamily": "The exact root has 30 color-deck children. Physical layout independently classifies seven as Heavy, so they remain root evidence but are excluded from the bounded regular Green/Backpack face family.",
            "titleBoundary": "Two Heavy MEDKIT/Medkit sources and one regular TTS MEDKIT source are not joined by title. Licensed Medkit and Medpack remain separate rows with no TTS copy crosswalk.",
            "glyphBoundary": "Nine functional glyph occurrences on selected physical faces retain explicit selected no-match evidence; licensed ACTION-CARD and noIntruders fields do not assign those source-local glyphs.",
            "variantBoundary": "Four unselected generated cells and all ten licensed rows remain independent source variants; no selector gap is repaired from title, body, source cell, BGA key, or expected game logic.",
            "officialBoundary": "No checked official visual identifies an exact Green face or TTS GUID. Official rules control count, class, storage, use, discard, privacy, Search, Interplay, and Trade only at their exact scopes.",
        },
    }


def green_item_source_registry_rows(source_index: dict) -> list[dict]:
    rows = [{
        "sourceId": GREEN_ITEM_ROOT_SOURCE_ID,
        "authority": "source-bound-component-scan",
        "version": "TTS raw base greenItemsDeck root / GUID 17400d",
        "path": RAW_SAVE_PATH,
        "sha256": source_index["rootDeckEvidence"]["rawSaveSha256"],
        "occurrenceId": "TTS-GREEN-ITEM-ROOT-DECK",
        "evidenceIndexPath": "docs/rules/semantics/green-item-source-index.json",
        "evidenceRecord": "rootDeckEvidence",
        "provenanceIndexPath": "assets/tts-mod/extract/v2/lua_roles.json",
    }]
    for face in [*source_index["faces"], *source_index["excludedHeavyFaces"]]:
        rows.append({
            "sourceId": face["sourceId"],
            "authority": face["sourceAuthority"],
            "version": face["sourceVersion"],
            "path": face["sourcePath"],
            "sha256": face["sourceSha256"],
            "occurrenceId": face["greenItemOccurrenceId"],
            "evidenceIndexPath": face["corpusEvidencePath"],
            "evidenceRecord": face["sourceSha256"],
            "provenanceIndexPath": face["provenanceEvidencePath"],
        })
    sheet = source_index["sourceSheet"]
    rows.append({"sourceId": sheet["sourceId"], "authority": sheet["sourceAuthority"], "version": sheet["sourceVersion"], "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"], "evidenceIndexPath": VISION_PROGRESS_PATH, "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    back = source_index["sharedBack"]
    rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for asset in source_index["sourceFaceAssets"]:
        if not asset["sourceId"]:
            continue
        rows.append({"sourceId": asset["sourceId"], "authority": "source-bound-component-scan", "version": f"TTS base Green Item unselected generated source variant / CustomDeck 37 / cell {asset['generatedCell']}", "path": asset["sourcePath"], "sha256": asset["sourceSha256"], "occurrenceId": f"TTS-GREEN-ITEM-VARIANT-37-CELL-{asset['generatedCell']:02d}", "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": asset["sourceSha256"], "provenanceIndexPath": VISION_PROGRESS_PATH})
    rows.append({"sourceId": BGA_GREEN_ITEM_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / ITEMS_DATA deck-green rows", "path": BGA_ITEMS_PATH, "sha256": _sha(Path(__file__).resolve().parents[1] / BGA_ITEMS_PATH), "occurrenceId": "ITEMS_DATA:deck-green", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "ITEMS_DATA"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None, visibility: str = "public") -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": visibility}


def build_green_item_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo
    records = []
    face_by_occurrence = {row["greenItemOccurrenceId"]: row for row in source_index["faces"]}
    all_face_source_ids = [row["sourceId"] for row in source_index["faces"]]

    records.append(record(
        "SEM-GREEN-ITEM-DECK-001", "Finite Green Item color deck and regular-family boundary", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [
            assertion("SA-GI-DECK-RB", "SRC-RULEBOOK", "unprinted page 3; printed page 9 and page 28 / RB-P03-V01, RB-P09-V01, RB-P28-V02 / lines 520–521, 2593–2600, 4849–4865", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "The official Green Item type has 30 cards. Shuffle its deck separately face down, leave a discard pile, draw by Green Item icons, and return unchosen Search cards privately to the Green deck bottom.", "docs/rules/semantics/green-item-source-index.json:familyCountEvidence"),
            assertion("SA-GI-DECK-TTS", GREEN_ITEM_ROOT_SOURCE_ID, "raw root GUID 17400d / exact ordered DeckIDs and 30 contained full CardID/GUID selectors", ["informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "sourceVariants"], "The exact source-bound root contains 30 physical children: 23 regular Green Item occurrences in this batch and seven horizontal Heavy occurrences retained as explicit exclusions.", "docs/rules/semantics/green-item-source-index.json:rootDeckEvidence"),
        ],
        ["term.item", "term.regular-item", "icon.greenItem"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-GI-DECK", "tax.entity.component.card.item.regular", "when-triggered", "once-at-setup-plus-per-source-requested-Green-draw/return/discard"), [participant("P-RULES", "rules-system"), participant("P-DRAWING-CHARACTER", "affected", "tax.entity.agent.character")], "must", [], [],
        [{"informationId": "I-GI-DECK", "subjectRef": "30 root physical cards, 23 regular faces, seven Heavy exclusions, shuffled order, and remaining fronts", "audience": "hidden-from-all fronts/order; public deck/back/count/discard locations", "revealTrigger": "owner-private Search inspection, gain, or source-defined use", "secrecy": "no client, log, accessibility output, or spectator may expose unselected fronts/order"}], [],
        [_target("T-GI-DECK-CARD", ["tax.entity.component.card.item"], mode="random", minimum=0, maximum=1)],
        [
            operation("S01", 1, "shuffle", "must", "P-RULES", "all 30 exact root Green color-deck children, including seven Heavy components outside this batch's face semantics", ["SA-GI-DECK-RB", "SA-GI-DECK-TTS"], repeat={"rootPhysicalCardCount": 30, "regularBatchFaceCount": 23, "excludedHeavyCount": 7}),
            operation("S02", 2, "transition-zone", "must", "P-RULES", "shuffled Green color deck face down", ["SA-GI-DECK-RB"], transition={"from": "tax.scaffold.supply-pool", "to": "tax.scaffold.zone.deck"}),
            operation("S03", 3, "set-state", "must", "P-RULES", "separate empty Green Item discard pile", ["SA-GI-DECK-RB"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "whether a requested Green draw has a remaining physical card", ["SA-GI-DECK-RB", "SA-GI-DECK-TTS"], target_ref="T-GI-DECK-CARD"),
            operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-040 empty-deck/recycle and multi-draw shortage handling", ["SA-GI-DECK-RB", "SA-GI-DECK-TTS"], conditions=["a Green draw is requested with insufficient cards"], target_ref="T-GI-DECK-CARD"),
            operation("S06", 6, "draw-random", "if-able", "P-RULES", "one exact physical Green root card into the caller's source-defined private candidate/gain zone", ["SA-GI-DECK-RB", "SA-GI-DECK-TTS"], conditions=["a physical card remains"], target_ref="T-GI-DECK-CARD"),
            operation("S07", 7, "evaluate-condition", "must", "P-RULES", "unchosen Search cards return to Green deck bottom; Used/voluntarily discarded Items enter the separate Item discard pile; no checked rule silently equates those destinations", ["SA-GI-DECK-RB"]),
        ],
        {"policy": "source-limited-components", "unit": "one requested physical Green draw or one exact lifecycle transition", "onImpossible": "SEM-Q-040 prohibits inventing a discard reshuffle, return rule, partial multi-draw assignment, or exhaustion policy"}, {"kind": "persistent-finite-deck-and-discard-state"}, {"policy": "one finite 30-card color deck; 23 regular occurrences dispatch only after exact physical selection/use; no title or licensed-row dispatch"}, [], ["SEM-Q-040"], []))

    records.append(record(
        "SEM-REGULAR-ITEM-BACKPACK-001", "Regular Item gain, Backpack capacity, and secrecy", "source-backed", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-GI-BACKPACK-RB", "SRC-RULEBOOK", "printed page 28 / lines 4882–4923", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "Regular vertical Items enter the numbered Backpack, which has no capacity limit. Backpack Items are secret and should not be revealed to other players until used.", "docs/rulebooks/rulebook_text.txt:lines 4882–4923")],
        ["term.item", "term.regular-item", "term.backpack"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.component.storage.backpack", "tax.scaffold.zone.backpack"], [],
        timing("TW-GI-BACKPACK", "tax.entity.component.card.item.regular", "when-triggered", "per-regular-Item-gain/use/transfer"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-GI-BACKPACK", "subjectRef": "exact regular Item identities and arrangement in the Backpack", "audience": "owner-private", "revealTrigger": "selected Item is used or another source explicitly authorizes reveal", "secrecy": "capacity is public/unlimited; unselected identities remain hidden from other players, logs, clients, accessibility output, and spectators"}], [],
        [_target("T-GI-BACKPACK-ITEM", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1, visibility="owner-private")],
        [
            operation("S01", 1, "transition-zone", "must", "P-RULES", "gained regular Item", ["SA-GI-BACKPACK-RB"], target_ref="T-GI-BACKPACK-ITEM", transition={"from": "caller gain/candidate zone", "to": "tax.scaffold.zone.backpack"}),
            operation("S02", 2, "set-state", "must", "P-RULES", "Backpack capacity remains unlimited regardless of regular Item count", ["SA-GI-BACKPACK-RB"]),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "only the exact Item selected for use/source-authorized reveal becomes visible; sibling Backpack Items remain owner-private", ["SA-GI-BACKPACK-RB"]),
        ],
        {"policy": "ordered-complete", "unit": "one gained regular Item", "onImpossible": "Backpack capacity never blocks a regular Item gain; Heavy/Armor placement is outside this record"}, {"kind": "persistent-owner-private-storage"}, {"policy": "unlimited distinct physical regular Items; matching titles/effects do not collapse copies"}, [], [], []))

    records.append(record(
        "SEM-USE-ITEM-001", "Use one regular Item", "source-backed-with-open-question", "action", "official-primary", "open-alternatives",
        [
            assertion("SA-GI-USE-RB", "SRC-RULEBOOK", "printed pages 12, 17, 28–29 / RB-P12-V02 / lines 2889, 3530–3548, 4882–4951", ["timing", "preconditions", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Use an Item costs 1 Action card. Select a regular Item, reveal it when used, resolve its entire legal effect, and apply its printed trait/timing; One Use Only Items are discarded when Used.", "docs/rules/02-character-actions.md:ACT-ITEM-001"),
            *[
                assertion(f"SA-GI-USE-FACE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['greenItemOccurrenceId']} / exact physical selector and face", ["preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], face["printedBody"], f"docs/rules/semantics/green-item-source-index.json:{face['greenItemOccurrenceId']}")
                for face in source_index["faces"]
            ],
        ],
        ["term.item", "term.regular-item", "term.backpack", "term.action", "icon.actionCard"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.component.storage.backpack", "tax.process.action.basic", "tax.entity.component.card.action"], [],
        timing("TW-GI-USE", "tax.process.temporal.turn", "during", "per-selected-Use-Item-Action-or-exact-free-immediate-window"), [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-USING-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed",
        [condition("C-GI-USE", "all", [{"predicate": "selected component is an exact owned regular Item in the Backpack"}, {"predicate": "selected exact face's restrictions and one complete effect/branch are resolvable"}], ["SA-GI-USE-RB"])],
        [decision("D-GI-USE-ITEM", "P-PLAYER", "player-choice", 1, 1, False, "owner-private-until-declaration", ["each exact physical regular Item in the acting Character's Backpack"]), decision("D-GI-USE-PAYMENT", "P-PLAYER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one Action card in own hand unless the exact immediate-free window applies"])],
        [{"informationId": "I-GI-USE", "subjectRef": "selected exact Item, paid Action card, selected effect/branch, affected Character, and result", "audience": "selected Item/result public on use; payment public on discard; sibling Backpack/hand identities remain owner-private", "revealTrigger": "source-defined use ordering under SEM-Q-039", "secrecy": "do not reveal unselected Backpack or hand cards"}],
        [{"costId": "COST-GI-USE", "payerRef": "P-PLAYER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-GI-USE-PAYMENT", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}],
        [_target("T-GI-USE-ITEM", ["tax.entity.component.card.item.regular"], selector="P-PLAYER", mode="player-choice", minimum=1, maximum=1, visibility="owner-private-until-declaration"), _target("T-GI-USE-CHARACTER", ["tax.entity.agent.character"], selector="P-PLAYER", mode="player-choice-with-consent", minimum=1, maximum=1)],
        [
            operation("S01", 1, "select-target", "must", "P-PLAYER", "one exact owned regular Item", ["SA-GI-USE-RB"], decision_ref="D-GI-USE-ITEM", target_ref="T-GI-USE-ITEM"),
            operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-039 exact declaration/reveal/payment/effect/One Use Only discard order", ["SA-GI-USE-RB"], target_ref="T-GI-USE-ITEM"),
            operation("S03", 3, "pay-cost", "must", "P-PLAYER", "COST-GI-USE", ["SA-GI-USE-RB"], conditions=["ordinary Use an Item Action rather than the exact immediate-free window", "payment point is reached under SEM-Q-039"], decision_ref="D-GI-USE-PAYMENT"),
            operation("S04", 4, "reveal", "must", "P-PLAYER", "selected exact Item only", ["SA-GI-USE-RB"], conditions=["reveal point is reached under SEM-Q-039"], target_ref="T-GI-USE-ITEM"),
            operation("S05", 5, "invoke-selected-process", "must", "P-USING-CHARACTER", "exact occurrence-specific regular Green Item effect", ["SA-GI-USE-RB", *[f"SA-GI-USE-FACE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}" for face in source_index["faces"]]], conditions=["cost/reveal prerequisites selected under SEM-Q-039 are complete"], target_ref="T-GI-USE-ITEM", notes="Dispatch uses full root CardID/GUID/CustomDeck/FaceURL/BackURL/generated-cell selector, never title, color, body, folder, cell alone, modulo, licensed key, or multiplicity."),
            operation("S06", 6, "invoke-process", "must", "P-RULES", "One Use Only lifecycle for the selected physical Item", ["SA-GI-USE-RB"], target_ref="T-GI-USE-ITEM", invoke="SEM-GREEN-ITEM-ONE-USE-001"),
        ],
        {"policy": "all-or-nothing-selection", "unit": "one exact regular Item use and one entirely resolvable selected branch", "onImpossible": "the Action/window cannot be initiated without a complete legal branch; SEM-Q-039 prohibits inventing payment, reveal, effect, or discard order"}, {"kind": "instantaneous-action-or-source-defined-immediate-window"}, {"policy": "one selected physical Item per invocation; multiple Items require separate use/immediate windows"}, [], ["SEM-Q-039"], []))
    records[-1]["operations"][4]["dispatchRuleIds"] = list(GREEN_ITEM_RULE_IDS)

    records.append(record(
        "SEM-GREEN-ITEM-ONE-USE-001", "One Use Only Green Item lifecycle", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-GI-ONE-USE-RB", "SRC-RULEBOOK", "printed page 29 / lines 4933–4951", ["timing", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "One Use Only Items are discarded when Used.", "docs/rulebooks/rulebook_text.txt:lines 4933–4951"), *[assertion(f"SA-GI-ONE-USE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['greenItemOccurrenceId']} / printed trait line", ["timing", "operations", "duration", "stacking"], face["typeLine"], f"docs/rules/semantics/green-item-source-index.json:{face['greenItemOccurrenceId']}.typeLine") for face in source_index["faces"]]],
        ["term.item", "term.regular-item"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-GI-ONE-USE", "tax.entity.component.card.item.regular", "when-triggered", "once-when-this-exact-physical-Item-is-Used"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-GI-ONE-USE", "subjectRef": "used exact physical Item face, effect, discard destination, and sibling Backpack cards", "audience": "used Item public; discard-pile face orientation source-unspecified; sibling Backpack cards owner-private", "revealTrigger": "SEM-Q-039", "secrecy": "discarding one copy never reveals or collapses sibling copies"}], [],
        [_target("T-GI-ONE-USE", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-039 whether the exact One Use Only transition occurs at declaration, before effect, after effect, or another source-defined point", ["SA-GI-ONE-USE-RB"], target_ref="T-GI-ONE-USE"),
            operation("S02", 2, "transition-zone", "must", "P-RULES", "used exact physical One Use Only Item", ["SA-GI-ONE-USE-RB"], conditions=["the source-defined discard point under SEM-Q-039 is reached"], target_ref="T-GI-ONE-USE", transition={"from": "owned Backpack or card-in-resolution zone", "to": "tax.scaffold.zone.discard-pile"}),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "the discarded physical copy cannot be Used again unless an explicit future source returns it; no checked Green rule returns or reshuffles it", ["SA-GI-ONE-USE-RB"]),
        ],
        {"policy": "ordered-complete", "unit": "one exact used physical Item", "onImpossible": "do not remove from game, return to deck/bottom, reshuffle, destroy, or discard a different copy; exact relative timing remains SEM-Q-039"}, {"kind": "instantaneous-transition-ending-that-copy's-availability"}, {"policy": "one physical copy discarded per completed use; same-title copies remain distinct"}, [], ["SEM-Q-039"], []))

    records.append(record(
        "SEM-ITEM-VOLUNTARY-DISCARD-001", "Voluntarily discard owned Items", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-GI-VOLUNTARY-DISCARD-RB", "SRC-RULEBOOK", "printed page 17 / lines 3665–3673", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "A Character may discard any number of their Items at any point; Items enter the Items discard pile. Discarding this way does not Use the Item or resolve its effect.", "docs/rulebooks/rulebook_text.txt:lines 3665–3673")],
        ["term.item"], ["tax.entity.component.card.item", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-GI-VOLUNTARY-DISCARD", "tax.entity.component.card.item", "when-triggered", "any-point-per-owner-choice"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "may", [],
        [decision("D-GI-VOLUNTARY-DISCARD", "P-OWNER", "player-choice", 0, None, True, "owner-private-until-discard", ["any subset of exact physical Items owned by the Character"])],
        [{"informationId": "I-GI-VOLUNTARY-DISCARD", "subjectRef": "selected Item faces and unselected owned Items", "audience": "selected cards public on physical discard; unselected Backpack Items remain owner-private", "revealTrigger": "discard", "secrecy": "zero selection is legal; no unselected card is revealed"}], [],
        [_target("T-GI-VOLUNTARY-DISCARD", ["tax.entity.component.card.item"], selector="P-OWNER", mode="player-choice", minimum=0, maximum=None, visibility="owner-private-until-discard")],
        [operation("S01", 1, "choose", "may", "P-OWNER", "any subset of owned physical Items", ["SA-GI-VOLUNTARY-DISCARD-RB"], decision_ref="D-GI-VOLUNTARY-DISCARD", target_ref="T-GI-VOLUNTARY-DISCARD"), operation("S02", 2, "transition-zone", "if-able", "P-RULES", "each selected physical Item independently", ["SA-GI-VOLUNTARY-DISCARD-RB"], decision_ref="D-GI-VOLUNTARY-DISCARD", target_ref="T-GI-VOLUNTARY-DISCARD", transition={"from": "class-appropriate owned storage", "to": "tax.scaffold.zone.discard-pile"}), operation("S03", 3, "evaluate-condition", "must", "P-RULES", "no selected Item effect resolves because voluntary discard is not Use an Item", ["SA-GI-VOLUNTARY-DISCARD-RB"])],
        {"policy": "per-selected-component", "unit": "one owner-selected exact physical Item", "onImpossible": "zero selection is legal; do not discard an unselected copy or resolve its printed effect"}, {"kind": "instantaneous-owner-choice"}, {"policy": "each selected physical copy transitions independently"}, [], [], []))

    records.append(record(
        "SEM-ITEM-TRADE-GAIN-001", "Trade Items and treat each received Item as gained", "source-backed-with-open-question", "action", "official-errata", "open-alternatives",
        [assertion("SA-GI-TRADE-RB", "SRC-RULEBOOK", "printed pages 12 and 29 / RB-P12-V02 / lines 2893, 5097–5103", ["timing", "preconditions", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Trade costs 1 Action card and is Not In Combat. Co-located Characters may reveal and exchange Items/Tactical Gear with mutual consent; multi-party and gifts are allowed if the active Character agrees.", "docs/rules/02-character-actions.md:ACT-TRADE-001"), assertion("SA-GI-TRADE-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U04", ["timing", "operations", "duration", "unresolvedQuestionRefs"], "A traded Item is gained and may be used immediately when its exact text permits.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U04")],
        ["term.trade", "term.item", "term.regular-item", "icon.actionCard", "icon.notInCombat"], ["tax.process.action.trade", "tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.component.card.action", "tax.scaffold.zone.backpack"], [],
        timing("TW-GI-TRADE", "tax.process.temporal.turn", "during", "per-selected-Trade-Action-plus-per-received-Item"), [participant("P-ACTIVE-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-ACTIVE-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-PARTICIPANTS", "collection", "tax.entity.agent.character"), participant("P-RECIPIENTS", "collection", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "may",
        [condition("C-GI-TRADE", "all", [{"predicate": "active Character is Not In Combat"}, {"predicate": "each participant is in the active Character's Room"}, {"predicate": "every transfer has all required consent and the active Character agrees to any multi-party exchange"}], ["SA-GI-TRADE-RB"])],
        [decision("D-GI-TRADE-PAY", "P-ACTIVE-PLAYER", "player-choice", 1, 1, False, "owner-private-until-discard", ["one own Action card"]), decision("D-GI-TRADE-TRANSFERS", "P-PARTICIPANTS", "mutual-consent", 0, None, True, "public-on-reveal", ["any consented Item/Tactical Gear transfers, exchanges, or gifts involving the active Character"]), decision("D-GI-TRADE-IMMEDIATE", "P-RECIPIENTS", "player-choice", 0, None, True, "public-on-use", ["decline or exercise each exact gained Item's printed immediate-use permission"])],
        [{"informationId": "I-GI-TRADE", "subjectRef": "offered/accepted Items, transfers, recipient storage, and immediate-use decisions", "audience": "revealed transferred components public among participants/table; unoffered Backpack contents remain owner-private", "revealTrigger": "consented reveal/exchange", "secrecy": "Trade never authorizes inspecting unoffered Backpack contents"}],
        [{"costId": "COST-GI-TRADE", "payerRef": "P-ACTIVE-PLAYER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-GI-TRADE-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}],
        [_target("T-GI-TRADE-ITEMS", ["tax.entity.component.card.item"], selector="P-PARTICIPANTS", mode="mutual-consent", minimum=0, maximum=None), _target("T-GI-TRADE-RECIPIENTS", ["tax.entity.agent.character"], selector="P-PARTICIPANTS", mode="mutual-consent", minimum=0, maximum=None)],
        [
            operation("S01", 1, "pay-cost", "must", "P-ACTIVE-PLAYER", "COST-GI-TRADE", ["SA-GI-TRADE-RB"], decision_ref="D-GI-TRADE-PAY"),
            operation("S02", 2, "choose", "may", "P-PARTICIPANTS", "consented transfers/exchanges/gifts", ["SA-GI-TRADE-RB"], decision_ref="D-GI-TRADE-TRANSFERS", target_ref="T-GI-TRADE-ITEMS"),
            operation("S03", 3, "transition-zone", "if-able", "P-RULES", "each transferred exact Item to recipient class-appropriate storage", ["SA-GI-TRADE-RB", "SA-GI-TRADE-FAQ"], decision_ref="D-GI-TRADE-TRANSFERS", target_ref="T-GI-TRADE-RECIPIENTS", transition={"from": "previous owner class-appropriate storage", "to": "recipient class-appropriate storage"}, repeat={"scope": "each consented transfer; a gift need not receive a return component"}),
            operation("S04", 4, "set-state", "must", "P-RULES", "each received Item is gained by its recipient", ["SA-GI-TRADE-FAQ"]),
            operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-045 ordering of multiple gained immediate-use windows and effects", ["SA-GI-TRADE-FAQ"], conditions=["more than one gained Item supplies an immediate-use window"]),
            operation("S06", 6, "invoke-process", "may", "each recipient", "exact gained Item immediate-use procedure", ["SA-GI-TRADE-FAQ"], conditions=["the gained exact face grants immediate use", "recipient elects that window under SEM-Q-045"], decision_ref="D-GI-TRADE-IMMEDIATE", invoke="SEM-GREEN-ITEM-IMMEDIATE-USE-001", repeat={"scope": "each source-ordered immediate-use window under SEM-Q-045"}),
        ],
        {"policy": "mutual-consent-per-transfer", "unit": "one exact transferred component and recipient", "onImpossible": "unconsented transfers do not occur; SEM-Q-045 prohibits inventing simultaneous-gain ordering or merging multiple immediate windows"}, {"kind": "instantaneous-action-plus-source-defined-immediate-followups"}, {"policy": "each physical Item remains distinct through transfer/gain/use"}, [], ["SEM-Q-045"], []))

    records.append(record(
        "SEM-ITEM-INTERPLAY-001", "Use eligible Item effects on a consenting co-located Character", "source-backed-with-open-question", "constraint", "official-errata", "open-alternatives",
        [assertion("SA-GI-INTERPLAY-RB", "SRC-RULEBOOK", "printed page 29 / lines 5079–5096", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "An Item may be used on another Character in the same Room with that Character's consent only for the four printed Interplay effect classes; visible text identifies restoring Health and discarding Serious Wounds, while two inline glyph objects require exact visual identity.", "docs/rulebooks/rulebook_text.txt:lines 5079–5096"), assertion("SA-GI-INTERPLAY-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U07", ["timing", "preconditions", "decisions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Interplay applies to all forms of Actions, including Item cards, when the receiver allows it and the effect is one of the four rulebook classes; non-Action effects cannot target another Character this way.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U07")],
        ["term.item", "term.character-health", "term.serious-wound-card"], ["tax.entity.component.card.item", "tax.entity.agent.character", "tax.state.health.point", "tax.entity.component.card.serious-wound"], [],
        timing("TW-GI-INTERPLAY", "tax.process.action", "when-triggered", "per-Item-Action-targeting-another-Character"), [participant("P-USING-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-USING-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RECEIVING-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RECEIVER-OWNER", "consent-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "may",
        [condition("C-GI-INTERPLAY", "all", [{"predicate": "the Item use/effect is an Action"}, {"predicate": "receiving Character occupies the using Character's Room"}, {"predicate": "receiving Character allows the Item to be used on them"}, {"predicate": "selected effect is source-clear restoring Health or discarding a Serious Wound, or another class resolved under SEM-Q-044"}], ["SA-GI-INTERPLAY-RB", "SA-GI-INTERPLAY-FAQ"])],
        [decision("D-GI-INTERPLAY-TARGET", "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["using Character", "one other co-located Character who consents"]), decision("D-GI-INTERPLAY-CONSENT", "P-RECEIVER-OWNER", "consent", 0, 1, True, "public-on-response", ["allow", "decline"])],
        [{"informationId": "I-GI-INTERPLAY", "subjectRef": "selected Item/effect, proposed recipient, consent, amount/branch, and result", "audience": "public on declaration/consent/use", "revealTrigger": "Item use", "secrecy": "unselected Backpack contents remain private"}], [],
        [_target("T-GI-INTERPLAY-CHARACTER", ["tax.entity.agent.character"], selector="P-USING-PLAYER", mode="player-choice-with-consent", minimum=1, maximum=1)],
        [
            operation("S01", 1, "select-target", "may", "P-USING-PLAYER", "using Character or one consenting co-located receiving Character", ["SA-GI-INTERPLAY-RB", "SA-GI-INTERPLAY-FAQ"], decision_ref="D-GI-INTERPLAY-TARGET", target_ref="T-GI-INTERPLAY-CHARACTER"),
            operation("S02", 2, "evaluate-condition", "must", "P-RULES", "receiver consent and source-clear Interplay class", ["SA-GI-INTERPLAY-RB", "SA-GI-INTERPLAY-FAQ"], decision_ref="D-GI-INTERPLAY-CONSENT", target_ref="T-GI-INTERPLAY-CHARACTER"),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-044 identity/scope of the visually lost Interplay inline glyph after 'Gaining' and whether the MEDKIT Medpack-token branch qualifies", ["SA-GI-INTERPLAY-RB", "SA-GI-INTERPLAY-FAQ"], conditions=["proposed other-Character effect is neither source-clear Health restoration nor Serious Wound discard"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "all other Item effects require Trade before the recipient uses the Item themselves", ["SA-GI-INTERPLAY-RB", "SA-GI-INTERPLAY-FAQ"]),
        ],
        {"policy": "consent-and-effect-class-gated", "unit": "one Item Action and one receiving Character", "onImpossible": "without co-location, consent, and a source-clear/SEM-Q-044-qualified effect class, target only the using Character or Trade first"}, {"kind": "per-Item-Action-targeting-constraint"}, {"policy": "one affected Character per Item use unless exact face text says otherwise"}, [], ["SEM-Q-044"], []))

    records.append(record(
        "SEM-RESTORE-HEALTH-001", "Restore up to a source-instructed amount of Character Health", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [assertion("SA-GI-RESTORE-RB", "SRC-RULEBOOK", "printed page 18 / lines 3750–3756, 3811–3823", ["timing", "decisions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Move the affected Character's Health marker left to restore Health. A player may always choose to restore fewer Health points than the source-instructed amount.", "docs/rulebooks/rulebook_text.txt:lines 3750–3756,3811–3823"), assertion("SA-GI-RESTORE-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U07", ["decisions", "targets", "operations", "unresolvedQuestionRefs"], "A consenting co-located Character may receive an Item Action's Health restoration through Interplay.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U07")],
        ["term.character-health", "term.health-point", "icon.characterHealth"], ["tax.entity.agent.character", "tax.state.health", "tax.state.health.point"], [],
        timing("TW-GI-RESTORE", "tax.state.health", "when-triggered", "per-source-instructed-restoration"), [participant("P-USING-PLAYER", "controller", "tax.entity.agent.player"), participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-AFFECTED-OWNER", "possible-decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "may", [],
        [decision("D-GI-RESTORE-AMOUNT", "P-RULES", "unresolved", 0, None, True, "public-on-declaration", ["using player chooses 0..printed amount", "affected Character's owner chooses 0..printed amount", "another source-defined owner chooses fewer restoration"])],
        [{"informationId": "I-GI-RESTORE", "subjectRef": "source maximum, chosen lesser amount, affected Character, Health marker, and Armor", "audience": "public", "revealTrigger": "declaration/resolution", "secrecy": "none"}], [],
        [_target("T-GI-RESTORE-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1), _target("T-GI-RESTORE-HEALTH", ["tax.state.health"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-043 restoration-amount owner when the Item user and receiving Character differ", ["SA-GI-RESTORE-RB", "SA-GI-RESTORE-FAQ"], decision_ref="D-GI-RESTORE-AMOUNT", target_ref="T-GI-RESTORE-CHARACTER"),
            operation("S02", 2, "change-value", "may", "P-RULES", "affected Character Health marker left by the selected 0..source-instructed amount", ["SA-GI-RESTORE-RB", "SA-GI-RESTORE-FAQ"], conditions=["amount owner/selection is resolved under SEM-Q-043"], decision_ref="D-GI-RESTORE-AMOUNT", target_ref="T-GI-RESTORE-HEALTH", value_change={"amount": "player-chosen-zero-to-source-maximum", "value": "Health damage restored"}),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "restoration does not move beyond maximum Health or recreate Armor; source-specific Item branch remains one effect", ["SA-GI-RESTORE-RB"]),
        ],
        {"policy": "up-to-source-maximum", "unit": "one affected Character and source-instructed maximum", "onImpossible": "zero/fewer restoration is legal; do not choose an owner for cross-Character Interplay until SEM-Q-043 is resolved"}, {"kind": "instantaneous-health-restoration"}, {"policy": "separate Item uses restore independently; no persistent stacking state"}, [], ["SEM-Q-043"], []))

    immediate_assertions = [assertion(f"SA-GI-IMMEDIATE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['greenItemOccurrenceId']} / immediate-use timing panel", ["timing", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "You can use this Item for free\nimmediately after gaining it.", f"docs/rules/semantics/green-item-source-index.json:{face['greenItemOccurrenceId']}.panels") for face in source_index["faces"] if face["sourceAssetKey"] == "direct-5367"]
    records.append(record(
        "SEM-GREEN-ITEM-IMMEDIATE-USE-001", "Optional free immediate use of the exact regular MEDKIT face", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [*immediate_assertions, assertion("SA-GI-IMMEDIATE-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U04", ["timing", "operations", "duration", "unresolvedQuestionRefs"], "A traded Item is gained and may be used immediately when its text permits.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U04")],
        ["term.item", "term.regular-item"], ["tax.entity.component.card.item.regular"], ["NI-0298"],
        timing("TW-GI-IMMEDIATE", "tax.entity.component.card.item.regular", "immediately-after-gain", "once-per-gain-of-one-of-four-exact-physical-occurrences"), [participant("P-RECIPIENT", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "may", [],
        [decision("D-GI-IMMEDIATE", "P-OWNER", "player-choice", 0, 1, True, "public-on-use", ["use this exact gained Item immediately for free", "decline and retain it in the Backpack"])],
        [{"informationId": "I-GI-IMMEDIATE", "subjectRef": "gained exact MEDKIT occurrence, immediate-use choice, selected branch/target, and sibling gained Items", "audience": "owner-private until use; public on use", "revealTrigger": "exercise immediate window", "secrecy": "declining does not reveal the retained card beyond source-authorized Trade/gain visibility"}], [],
        [_target("T-GI-IMMEDIATE-ITEM", ["tax.entity.component.card.item.regular"], selector="P-OWNER", mode="deterministic-exact-face-filter", minimum=1, maximum=1, visibility="owner-private-until-use")],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "gained physical occurrence is one of the four exact direct-5367 MEDKIT selectors", [row["assertionId"] for row in immediate_assertions], target_ref="T-GI-IMMEDIATE-ITEM"),
            operation("S02", 2, "choose", "may", "P-OWNER", "exercise or decline this exact immediate window", [*([row["assertionId"] for row in immediate_assertions]), "SA-GI-IMMEDIATE-FAQ"], decision_ref="D-GI-IMMEDIATE", target_ref="T-GI-IMMEDIATE-ITEM"),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-045 ordering when multiple Items are gained with immediate-use permissions", [*([row["assertionId"] for row in immediate_assertions]), "SA-GI-IMMEDIATE-FAQ"], conditions=["multiple immediate-use windows arise from one gain/Trade resolution"]),
            operation("S04", 4, "invoke-process", "may", "P-RECIPIENT", "Use the exact Item with its ordinary one-Action-card cost waived only for this immediate window", [row["assertionId"] for row in immediate_assertions], conditions=["owner exercises this Item's window under SEM-Q-045"], decision_ref="D-GI-IMMEDIATE", target_ref="T-GI-IMMEDIATE-ITEM", invoke="SEM-USE-ITEM-001", notes="This is a printed immediate timing note, not a Reaction heading; all ordinary restrictions, branch legality, visibility, and One Use Only lifecycle still apply."),
        ],
        {"policy": "one-optional-window-per-exact-gain", "unit": "one gained exact direct-5367 physical occurrence", "onImpossible": "declining is legal; the free permission expires after the immediate window; SEM-Q-045 prohibits merging or auto-ordering multiple windows"}, {"kind": "instantaneous-optional-followup-window"}, {"policy": "each gained physical copy grants at most one window for that gain; later use costs normally"}, [], ["SEM-Q-045"], []))

    gap_assets = [row for row in source_index["sourceFaceAssets"] if row["sourceRole"] == "generated-cell-selector-gap-variant"]
    bga_rows = source_index["licensedDigitalOccurrences"]
    excluded_faces = source_index["excludedHeavyFaces"]
    variant_assertions = []
    variant_operations = []
    variant_refs = []
    for asset in gap_assets:
        assertion_id = f"SA-GI-VARIANT-GAP-{asset['generatedCell']:02d}"
        item = assertion(assertion_id, asset["sourceId"], f"CustomDeck 37 / generated cell {asset['generatedCell']} / explicit selector gap", ["operations", "sourceVariants"], asset["printedBody"], f"docs/rules/semantics/green-item-source-index.json:sourceFaceAssets.{asset['assetKey']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve unselected cell {asset['generatedCell']} {asset['printedTitle']!r} exactly; never dispatch it as a root physical Green face", [assertion_id]))
        variant_refs.append({"variantId": f"SV-GI-GAP-{asset['generatedCell']:02d}", "sourceId": asset["sourceId"], "sourceAssertionId": assertion_id, "difference": f"Generated cell {asset['generatedCell']} prints title {asset['printedTitle']!r}, body {asset['printedBody']!r}, and exact local glyph evidence but has no root full CardID/GUID selector.", "resolution": "Retain as an independent selector-gap source variant; title, body, cell, color, and CardID modulo cannot repair the gap."})
    for face in excluded_faces:
        assertion_id = f"SA-GI-VARIANT-HEAVY-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}"
        item = assertion(assertion_id, face["sourceId"], f"{face['greenItemOccurrenceId']} / exact root selector and horizontal Heavy class", ["operations", "sourceVariants"], face["printedBody"], f"docs/rules/semantics/green-item-source-index.json:{face['greenItemOccurrenceId']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"retain excluded Heavy root occurrence {face['greenItemOccurrenceId']} and never dispatch it as a regular Green/Backpack face", [assertion_id]))
        variant_refs.append({"variantId": f"SV-GI-HEAVY-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", "sourceId": face["sourceId"], "sourceAssertionId": assertion_id, "difference": f"This exact root child is a horizontal Heavy Item ({face['printedTitle']!r}), not one of the 23 regular Green Item faces in this batch.", "resolution": "Preserve exact root membership and exclude from regular Green/Backpack effect dispatch; do not erase it or reinterpret it from color."})
    bga_assertion_id = "SA-GI-VARIANT-BGA"
    bga_assertion = assertion(bga_assertion_id, BGA_GREEN_ITEM_SOURCE_ID, "ITEMS_DATA / all ten deck-green rows in source order", ["operations", "sourceVariants"], "\n".join(row["sourceBlockText"] for row in bga_rows), "docs/rules/semantics/green-item-source-index.json:licensedDigitalOccurrences")
    bga_assertion["textKind"] = "verbatim"
    variant_assertions.append(bga_assertion)
    for row in bga_rows:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve licensed ITEMS_DATA.{row['key']} independently: name={row['name']!r}, nbr={row['nbr']}, heavy={row['heavy']}, noIntruders={row['noIntruders']}, effectDesc={row['effectDesc']!r}", [bga_assertion_id]))
        variant_refs.append({"variantId": f"SV-GI-BGA-{row['key'].upper()}", "sourceId": BGA_GREEN_ITEM_SOURCE_ID, "sourceAssertionId": bga_assertion_id, "difference": f"Licensed row {row['key']} has its own exact title/class/multiplicity/restriction/body tuple; no TTS/official physical identity selector exists.", "resolution": "Retain independently below official/source-bound authority. Aggregate 30/23/7 reconciliation is not a copy, title, body, or ordinal crosswalk."})
    records.append(record(
        "SEM-GREEN-ITEM-VARIANT-BOUNDARIES-001", "Green Item root, selector-gap, Heavy, and licensed variant boundaries", "source-variant", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-GI-VARIANT-RB", "SRC-RULEBOOK", "unprinted page 3 and printed pages 28–29 / physical count, Regular, Backpack, and Heavy classes", ["operations", "sourceVariants"], "The official inventory supplies 30 cards per Item type; vertical non-Armor Items are regular/Backpack Items, while horizontal Items are Heavy and do not fit in a Backpack.", "docs/rules/semantics/green-item-source-index.json:familyCountEvidence"), *variant_assertions],
        ["term.item", "term.regular-item", "term.backpack"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.component.card.item.heavy"], [],
        timing("TW-GI-VARIANTS", "tax.entity.component.card.item", "when-triggered", "per-source-comparison-or-canonicalization-attempt"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-GI-VARIANTS", "subjectRef": "23 regular physical faces, seven Heavy exclusions, four selector gaps, ten licensed rows, official family/count/rules evidence, and all wording/icon/class differences", "audience": "public source evidence", "revealTrigger": "source audit", "secrecy": "does not expose a live shuffled deck order or private Backpack"}], [], [],
        [*variant_operations, operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", "no title, color, body, folder, source order, generated-cell position, CardID modulo, licensed key, copy multiplicity, or expected game logic establishes source identity or effect equivalence", ["SA-GI-VARIANT-RB", *[row["assertionId"] for row in variant_assertions]])],
        {"policy": "per-proposed-source-merge", "unit": "one proposed Green/Heavy/gap/licensed identity or effect merge", "onImpossible": "without an exact source-backed correspondence, preserve independent occurrences and conflicts rather than selecting a default"}, {"kind": "persistent-source-audit-boundary"}, {"policy": "source variants do not dispatch, stack, replace, or identify one another from resemblance"}, [], [], variant_refs))

    def build_face(definition: dict) -> dict:
        source = face_by_occurrence[definition["occurrenceId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        scan_id = f"SA-GIF-{code}-SCAN"
        general_id = f"SA-GIF-{code}-GENERAL"
        scan = assertion(scan_id, source["sourceId"], f"{source['greenItemOccurrenceId']} / exact selector, regions, panels, title, trait, punctuation, sentences, and icons", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/green-item-source-index.json:{source['greenItemOccurrenceId']}")
        scan["textKind"] = "verbatim"
        general = assertion(general_id, "SRC-RULEBOOK", "printed pages 17–18 and 28–29 / whole-effect, Item use, Backpack, One Use Only, Health, Interplay", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "This exact physical regular Item is owner-private in the Backpack until selected, resolves only through a legal Use/immediate window, follows official Health/Interplay/component limits, and uses the separate One Use Only lifecycle.", "docs/rules/semantics/green-item-source-index.json:officialRulebookTextOccurrences")
        terms = ["term.item", "term.regular-item"]
        taxa = ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.agent.character"]
        named = [source["namedIdentityRef"]] if source.get("namedIdentityRef") else []
        for icon in source["iconOccurrences"]:
            if icon.get("semanticReferenceId"):
                terms.append(icon["semanticReferenceId"])
        participants = [participant("P-USING-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-USING-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")]
        decisions = []
        targets = [_target(f"T-GIF-{code}-ITEM", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1), _target(f"T-GIF-{code}-CHARACTER", ["tax.entity.agent.character"], selector="P-USING-PLAYER", mode="player-choice-with-consent", minimum=1, maximum=1)]
        ops = []

        def add(sentence_sequence: int, op_type: str, modality: str, subject: str, obj: str, *, sources=None, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
            sequence = len(ops) + 1
            sentence = source["sentences"][sentence_sequence - 1]
            op = operation(f"S{sequence:02d}", sequence, op_type, modality, subject, obj, sources or [scan_id, general_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref or f"T-GIF-{code}-CHARACTER", transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence["sentenceId"]
            op["sourceRegionId"] = sentence["regionId"]
            op["sourcePanelId"] = sentence["panelId"]
            ops.append(op)
            return op

        unresolved = []
        kind = source["effectKind"]
        matched_not_in_combat = any(icon.get("semanticReferenceId") == "icon.notInCombat" and icon.get("cardLocationClass") == "upperRight" for icon in source["iconOccurrences"])
        preconditions = [condition(f"C-GIF-{code}-OCCURRENCE", "predicate", [{"predicate": f"exact selected physical occurrence is {source['greenItemOccurrenceId']}"}], [scan_id, general_id])]
        if matched_not_in_combat:
            preconditions.append(condition(f"C-GIF-{code}-NOT-COMBAT", "predicate", [{"predicate": "using Character is Not In Combat"}], [scan_id, general_id]))
        if kind == "flip-life-support":
            terms.extend(["term.section", "icon.computer", "icon.malfunction", "icon.lifeSupportActive", "icon.lifeSupportInactive", "icon.notInCombat"])
            taxa.extend(["tax.entity.spatial.section", "tax.entity.spatial.room", "tax.entity.component.marker.malfunction"])
            decision_id = f"D-GIF-{code}-SECTION"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["Section A", "Section B", "Section C"]))
            targets.append(_target(f"T-GIF-{code}-SECTION", ["tax.entity.spatial.section"], selector="P-USING-PLAYER", mode="player-choice", minimum=1, maximum=1))
            preconditions.append(condition(f"C-GIF-{code}-ROOM", "all", [{"predicate": "using Character occupies a Room with Computer"}, {"predicate": "that Room has no Malfunction marker"}], [scan_id, general_id]))
            add(1, "select-target", "must", "P-USING-PLAYER", "one Section", decision_ref=decision_id, target_ref=f"T-GIF-{code}-SECTION")
            add(1, "set-state", "must", "P-RULES", "selected Section Life Support flips Active to Inactive or Inactive to Active", decision_ref=decision_id, target_ref=f"T-GIF-{code}-SECTION")
        elif kind == "draw-three-action-cards":
            terms.append("icon.actionCard"); taxa.append("tax.entity.component.card.action")
            add(1, "invoke-process", "must", "P-AFFECTED-CHARACTER", "draw 3 Action cards through the reusable private draw/renewal procedure", invoke="SEM-ACTION-CARD-DRAW-001", repeat={"requestedCards": 3, "completeEachDrawBeforeNext": True})
        elif kind == "restore-or-gain-medpack":
            terms.extend(["term.character-health", "icon.characterHealth", "icon.medpackToken", "icon.notInCombat"]); taxa.extend(["tax.state.health.point", "tax.entity.component.token.tactical-gear.medpack"]); unresolved.extend(["SEM-Q-043", "SEM-Q-044", "SEM-Q-045"])
            decision_id = f"D-GIF-{code}-BRANCH"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["restore up to 2 Character Health", "gain 1 Medpack Tactical Gear token"]))
            add(2, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=decision_id)
            add(2, "invoke-process", "must", "P-AFFECTED-CHARACTER", "restore up to 2 Character Health under SEM-Q-043", conditions=["restore branch"], decision_ref=decision_id, invoke="SEM-RESTORE-HEALTH-001", repeat={"sourceMaximum": 2})
            add(3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-044 whether the visually incomplete Interplay 'Gaining' class permits this Medpack-token branch to target another Character", conditions=["gain Medpack branch", "proposed affected Character differs from using Character"], decision_ref=decision_id)
            add(3, "invoke-process", "must", "P-AFFECTED-CHARACTER", "gain 1 finite Medpack token in a compatible empty slot", conditions=["gain Medpack branch", "target is source-legal under SEM-Q-044"], decision_ref=decision_id, invoke="SEM-ITM-005", repeat={"tokenType": "medpack", "quantity": 1})
        elif kind == "adrenaline-action-window":
            terms.extend(["term.action", "term.turn", "term.pass"]); taxa.extend(["tax.process.action", "tax.process.temporal.turn", "tax.process.action.pass"]); unresolved.append("SEM-Q-041")
            decision_id = f"D-GIF-{code}-ACTIONS"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice-sequential", 0, None, True, "public-on-declaration", ["each next fully legal Action", "stop selecting further non-Pass Actions and Pass"]))
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-041 identity and operation of the source-local solid blank white rectangle after 'Draw 1'")
            add(1, "invoke-process", "if-able", "P-AFFECTED-CHARACTER", "one source-defined card draw only if the local glyph identity is independently established under SEM-Q-041", conditions=["SEM-Q-041 establishes an exact draw target"], invoke="SEM-ACTION-CARD-DRAW-001", notes="Licensed ACTION-CARD is a lower-authority occurrence and is not promoted into the literal no-match glyph.")
            add(2, "set-state", "may", "P-RULES", "this Turn permits a player-chosen sequential number of additional fully legal Actions", decision_ref=decision_id, repeat={"minimum": 0, "maximum": None, "selectionTiming": "one Action at a time"})
            add(2, "invoke-selected-process", "may", "P-USING-CHARACTER", "each next owner-selected fully legal Action", decision_ref=decision_id, repeat={"until": "owner stops or Pass is selected", "noActionsAfterPass": True})
            add(3, "invoke-process", "must", "P-USING-CHARACTER", "Pass as the last Action of this Turn", invoke="SEM-RT-007")
        elif kind == "remove-unscanned-contamination":
            terms.extend(["term.contamination-card", "icon.notInCombat"]); taxa.append("tax.entity.component.card.contamination")
            decision_id = f"D-GIF-{code}-CONTAMINATION"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "owner-private-until-removal", ["each exact Contamination card in the using Character's hand without scanning hidden INFECTED text"]))
            targets.append(_target(f"T-GIF-{code}-CONTAMINATION", ["tax.entity.component.card.contamination"], selector="P-USING-PLAYER", mode="player-choice-without-scan", minimum=1, maximum=1, visibility="owner-private-until-removal"))
            add(1, "select-target", "must", "P-USING-PLAYER", "one exact Contamination card in own hand without scanning", decision_ref=decision_id, target_ref=f"T-GIF-{code}-CONTAMINATION")
            add(1, "transition-zone", "must", "P-RULES", "selected Contamination card without inspecting hidden INFECTED text", decision_ref=decision_id, target_ref=f"T-GIF-{code}-CONTAMINATION", transition={"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.removed-from-game"})
        elif kind == "place-closed-doors":
            terms.extend(["term.room", "term.door", "term.closed", "icon.computer", "icon.malfunction", "icon.notInCombat"]); taxa.extend(["tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.entity.spatial.door", "tax.state.closed", "tax.entity.component.marker.malfunction"]); unresolved.append("SEM-Q-042")
            decision_id = f"D-GIF-{code}-ROOM"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["any Room in the Facility"]))
            targets.append(_target(f"T-GIF-{code}-ROOM", ["tax.entity.spatial.room"], selector="P-USING-PLAYER", mode="player-choice", minimum=1, maximum=1))
            preconditions.append(condition(f"C-GIF-{code}-ROOM", "all", [{"predicate": "using Character occupies a Room with Computer"}, {"predicate": "that Room has no Malfunction marker"}], [scan_id, general_id]))
            add(2, "select-target", "must", "P-USING-PLAYER", "any Room in the Facility", decision_ref=decision_id, target_ref=f"T-GIF-{code}-ROOM")
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-042 finite Door allocation/order and whether exact TTS 'place a closed Door' overrides no-slot/existing/Destroyed Door constraints", decision_ref=decision_id, target_ref=f"T-GIF-{code}-ROOM")
            add(2, "place-component", "if-able", "P-RULES", "one Closed Door at each source-eligible adjacent Corridor under SEM-Q-042", conditions=["target/placement remains legal under official Door rules and SEM-Q-042"], decision_ref=decision_id, target_ref=f"T-GIF-{code}-ROOM", repeat={"scope": "each adjacent Corridor", "allocationOrder": "source-unspecified", "finiteSupply": True})
        elif kind == "discard-wound-or-restore":
            terms.extend(["term.serious-wound-card", "term.character-health", "icon.characterHealth"]); taxa.extend(["tax.entity.component.card.serious-wound", "tax.state.health.point"]); unresolved.append("SEM-Q-043")
            decision_id = f"D-GIF-{code}-BRANCH"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["discard 1 Serious Wound", "restore up to 2 Character Health"]))
            add(1, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=decision_id)
            add(1, "invoke-process", "must", "P-AFFECTED-CHARACTER", "discard one owner-selected Serious Wound through the reusable discard/slide procedure", conditions=["discard Wound branch"], decision_ref=decision_id, invoke="SEM-SERIOUS-WOUND-DISCARD-001")
            add(2, "invoke-process", "must", "P-AFFECTED-CHARACTER", "restore up to 2 Character Health under SEM-Q-043", conditions=["restore branch"], decision_ref=decision_id, invoke="SEM-RESTORE-HEALTH-001", repeat={"sourceMaximum": 2})
        elif kind == "restore-or-local-draw":
            terms.extend(["term.character-health", "icon.characterHealth"]); taxa.append("tax.state.health.point"); unresolved.extend(["SEM-Q-041", "SEM-Q-043"])
            decision_id = f"D-GIF-{code}-BRANCH"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["restore up to 2 Character Health", "resolve the source-local Draw 2 glyph branch under SEM-Q-041"]))
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-041 identity/scope of the source-local crossed upper-right device and whether it imposes a use restriction")
            add(1, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=decision_id)
            add(1, "invoke-process", "must", "P-AFFECTED-CHARACTER", "restore up to 2 Character Health under SEM-Q-043", conditions=["restore branch", "source-local use restriction under SEM-Q-041 is satisfied"], decision_ref=decision_id, invoke="SEM-RESTORE-HEALTH-001", repeat={"sourceMaximum": 2})
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-041 identity and operation of the blank rounded rectangle after 'Draw 2'", conditions=["draw branch"], decision_ref=decision_id)
            add(2, "invoke-process", "if-able", "P-AFFECTED-CHARACTER", "draw 2 source-defined cards only if the local glyph identity is independently established", conditions=["draw branch", "SEM-Q-041 establishes an exact draw target", "source-local use restriction under SEM-Q-041 is satisfied"], decision_ref=decision_id, invoke="SEM-ACTION-CARD-DRAW-001", repeat={"requestedCards": 2}, notes="Licensed ACTION-CARD and noIntruders are lower-authority structured variants and do not assign either literal TTS glyph.")
        else:
            raise AssertionError(f"unexpected Green Item effect kind: {kind}")

        unresolved = list(dict.fromkeys(unresolved))
        status = "source-backed-with-open-question" if unresolved else "source-backed"
        interpretation = "open-alternatives" if unresolved else "source-composed"
        recurrence = "once-per-exact-physical-Item-use; printed immediate timing is delegated to SEM-GREEN-ITEM-IMMEDIATE-USE-001" if kind == "restore-or-gain-medpack" else "once-per-exact-physical-Item-use"
        return record(
            definition["semanticRuleId"], f"Regular Green Item physical occurrence {code}", status, "component-effect", "official-primary", interpretation,
            [scan, general], terms, taxa, named, timing(f"TW-GIF-{code}", "tax.entity.component.card.item.regular", "when-triggered", recurrence), participants, "mixed" if decisions or unresolved else "must", preconditions, decisions,
            [{"informationId": f"I-GIF-{code}", "subjectRef": "exact physical occurrence, printed title/trait/body/panels/icons, using/affected Character, decisions, operations, and result", "audience": "owner-private before use; public selected face/decisions/results at source-defined use point", "revealTrigger": "SEM-USE-ITEM-001 under SEM-Q-039", "secrecy": "sibling Backpack faces and Green deck order remain hidden"}], [], targets, ops,
            {"policy": "all-or-nothing-selection", "unit": "one exact physical occurrence's printed effect/selected branch", "onImpossible": "generic cost/reveal/One Use lifecycle remains in reusable records; no unresolved glyph, owner, Door, Interplay, or multi-window default is invented"}, {"kind": "instantaneous-one-use-effect; no Passive or Reaction heading; exact MEDKIT timing note creates a separate immediate-use window"}, {"policy": "each physical copy resolves separately; same title/body/multiplicity creates no identity or stacking key"}, [], unresolved, [])

    records.extend(build_face(definition) for definition in REGULAR_PHYSICAL_DEFINITIONS)
    return records


def integrate_green_item_search_record(records: list[dict], operation) -> None:
    search = next(row for row in records if row["ruleId"] == "SEM-ACT-SEARCH-001")
    if "SEM-Q-040" not in search["unresolvedQuestionRefs"]:
        search["unresolvedQuestionRefs"].append("SEM-Q-040")
    search["status"] = "source-backed-with-open-question"
    search["authority"]["interpretation"] = "open-alternatives"
    draw_index = next(index for index, op in enumerate(search["operations"]) if op["operationType"] == "draw-random")
    source_ids = search["operations"][draw_index]["sourceAssertionIds"]
    exhaustion_condition_id = "C-SEARCH-GREEN-EXHAUSTION"
    search["preconditions"].append({"conditionId": exhaustion_condition_id, "scope": "operation-guard", "expression": {"operator": "predicate", "args": [{"predicate": "one or more corresponding Item decks lack a required physical card"}]}, "sourceAssertionIds": source_ids})
    search["operations"].insert(draw_index, operation("TEMP", 0, "resolve-open-alternative", "must", "P-SEARCHER", "SEM-Q-040 source-deck exhaustion/recycle and multi-icon shortage handling before each required draw", source_ids, conditions=[exhaustion_condition_id]))
    for sequence, op in enumerate(search["operations"], 1):
        op["sequence"] = sequence
        op["stepId"] = f"S{sequence:02d}"
    search["partialResolution"]["onImpossible"] = "Action/card effect may be selected only if fully resolvable; SEM-Q-040 prohibits inventing an Item discard reshuffle, partial shortage assignment, or exhausted-deck return policy"
