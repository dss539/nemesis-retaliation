from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

from semantic_attack_records import _find_guid, _parse_value
from semantic_red_item_records import _source_icons, _source_panels, _source_regions, _source_sentences


BASE_YELLOW_ITEM_DECK_GUID = "fe68f3"
YELLOW_ITEM_ROOT_SOURCE_ID = "SRC-YELLOW-ITEM-ROOT-DECK"
YELLOW_ITEM_SHEET_33_SOURCE_ID = "SRC-YELLOW-ITEM-SHEET-33"
YELLOW_ITEM_SHEET_33_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146.jpg"
YELLOW_ITEM_SHEET_34_SOURCE_ID = "SRC-YELLOW-ITEM-SHEET-34"
YELLOW_ITEM_SHEET_34_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145.jpg"
YELLOW_ITEM_SHARED_BACK_SOURCE_ID = "SRC-YELLOW-ITEM-SHARED-BACK"
YELLOW_ITEM_SHARED_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-142.jpg"
YELLOW_ITEM_UNIQUE_BACK_SHEET_SOURCE_ID = "SRC-YELLOW-ITEM-UNIQUE-BACK-SHEET-33"
YELLOW_ITEM_UNIQUE_BACK_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-143.jpg"
BGA_YELLOW_ITEM_SOURCE_ID = "SRC-BGA-YELLOW-ITEMS"
BGA_ITEMS_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
SELECTED_EVIDENCE_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
VISION_PROGRESS_PATH = "assets/tts-mod/extract/vision-progress.json"
LOW_CONFIDENCE_PATH = "assets/tts-mod/extract/low-confidence-review.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"

SHARED_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235441/B56EC1560F6B7FB5A61EC49490019DCB185D1CFE/"
UNIQUE_BACK_SHEET_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235323/E2B2763353C8DD3A6DD329CCEC256500AEF64B8A/"
SHEET_33_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235276/4CE4EE4D61C3E4A34A941AF1D5385A94126FEFB7/"
SHEET_34_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235380/6906B55A24F3CA2E9FD143A95E39A71307EA5AC1/"

LOCAL_CROSSED_DEVICE = "[ICON: selected source-local white horizontal device crossed by a red X with no authoritative glossary match]"
LOCAL_ACTION_RECTANGLE = "[ICON: upright light-gray rounded rectangle with white rim]"


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
    source_sheet: str | None,
    generated_cell: int | None,
    physical_class: str,
    selected_disposition: str,
    type_line: str = "ONE USE ONLY",
    upper_right: str = "",
    body_panels: list[tuple[str, str]] | None = None,
    sentence_texts: list[str] | None = None,
    icon_specs: list[tuple[str, str, str | None, str, int]] | None = None,
    effect_kind: str,
    named_identity_ref: str | None = None,
    rules_text_present: bool = True,
) -> dict:
    return {
        "assetKey": asset_key,
        "sourcePath": source_path,
        "sourceRole": source_role,
        "customDeckIds": custom_deck_ids,
        "sourceSheet": source_sheet,
        "generatedCell": generated_cell,
        "physicalClass": physical_class,
        "selectedDisposition": selected_disposition,
        "printedTitle": printed_title,
        "typeLine": type_line,
        "upperRight": upper_right,
        "printedBody": printed_body,
        "bodyPanels": body_panels or ([("effect", printed_body)] if printed_body else []),
        "sentenceTexts": sentence_texts or ([printed_body] if printed_body else []),
        "iconSpecs": icon_specs or [],
        "effectKind": effect_kind,
        "namedIdentityRef": named_identity_ref,
        "rulesTextPresent": rules_text_present,
    }


ASSET_DEFINITIONS = {
    "direct-phosphates": _asset(
        "direct-phosphates", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-021.png", "direct-regular-face",
        "PHOSPHATES", "Reinforce 1 empty Corridor.\nOR\nDiscard a [fire].",
        custom_deck_ids=["3954"], source_sheet=None, generated_cell=None, physical_class="regular-item", selected_disposition="included-regular",
        upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("reinforce-corridor-branch", "Reinforce 1 empty Corridor."), ("branch-separator", "OR"), ("discard-fire-branch", "Discard a [fire].")],
        sentence_texts=["Reinforce 1 empty Corridor.", "Discard a [fire]."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[fire]", "icon.fire", "selected-verified", 0)],
        effect_kind="reinforce-or-discard-fire", named_identity_ref="NI-0355",
    ),
    "direct-oxygen": _asset(
        "direct-oxygen", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-050.png", "direct-regular-face",
        "OXYGEN TANK", "You can use this Item for free\nimmediately after gaining it.\n\nGain 3 [oxygen].\n\nOR\n\nGain 1 [oxygenToken].",
        custom_deck_ids=["5320"], source_sheet=None, generated_cell=None, physical_class="regular-item", selected_disposition="included-regular",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON",
        body_panels=[
            ("immediate-use-timing-note", "You can use this Item for free\nimmediately after gaining it."),
            ("gain-oxygen-branch", "Gain 3 [oxygen]."),
            ("branch-separator", "OR"),
            ("gain-oxygen-token-branch", "Gain 1 [oxygenToken]."),
        ],
        sentence_texts=["You can use this Item for free\nimmediately after gaining it.", "Gain 3 [oxygen].", "Gain 1 [oxygenToken]."],
        icon_specs=[("body", "[oxygen]", "icon.oxygen", "selected-verified", 0), ("body", "[oxygenToken]", "icon.oxygenToken", "selected-verified", 1)],
        effect_kind="gain-oxygen-or-token", named_identity_ref="NI-0348",
    ),
    "direct-robot": _asset(
        "direct-robot", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-097.png", "direct-physical-class-conflict",
        "ROBOT CONTROLLER", "Use the [robot] from anywhere in the Facility.\nOR\nDiscard this Item to place corresponding\nTactical Gear tokens on empty Robot slots.",
        custom_deck_ids=["5318"], source_sheet=None, generated_cell=None,
        physical_class="source-conflicted-portrait-item-versus-licensed-heavy", selected_disposition="class-conflict-excluded",
        type_line="", upper_right="notInCombat",
        body_panels=[("remote-robot-branch", "Use the [robot] from anywhere in the Facility."), ("branch-separator", "OR"), ("robot-gear-branch", "Discard this Item to place corresponding\nTactical Gear tokens on empty Robot slots.")],
        sentence_texts=["Use the [robot] from anywhere in the Facility.", "Discard this Item to place corresponding\nTactical Gear tokens on empty Robot slots."],
        icon_specs=[("upperRight", "notInCombat", "icon.notInCombat", "canonical", 0), ("body", "[robot]", "icon.robot", "canonical", 0)],
        effect_kind="class-conflict-robot-controller", named_identity_ref=None,
    ),
    "sheet34-00": _asset(
        "sheet34-00", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-00.png", "generated-cell-regular-face",
        "DUCT TAPE", "Discard a [malfunction]\nOR\nPlace this Item and 1 another\nHeavy Item under a Heavy Item\nin your Hand slot.",
        custom_deck_ids=["34"], source_sheet="34", generated_cell=0, physical_class="regular-item", selected_disposition="included-regular",
        upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("discard-malfunction-branch", "Discard a [malfunction]"), ("branch-separator", "OR"), ("stack-heavy-items-branch", "Place this Item and 1 another\nHeavy Item under a Heavy Item\nin your Hand slot.")],
        sentence_texts=["Discard a [malfunction]", "Place this Item and 1 another\nHeavy Item under a Heavy Item\nin your Hand slot."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[malfunction]", "icon.malfunction", "selected-verified", 0)],
        effect_kind="discard-malfunction-or-stack-heavy", named_identity_ref="NI-0138",
    ),
    "sheet34-01": _asset(
        "sheet34-01", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-01.png", "generated-cell-selector-gap-variant",
        "OXYGEN TANK", "You can use this Item for free\nimmediately after gaining it.\n\nGain 3 [oxygen].\n\nOR\n\nGain 1 [oxygenToken].",
        custom_deck_ids=["34"], source_sheet="34", generated_cell=1, physical_class="regular-item", selected_disposition="yellow-selector-gap",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON", upper_right="notInCombat",
        body_panels=[
            ("immediate-use-timing-note", "You can use this Item for free\nimmediately after gaining it."),
            ("gain-oxygen-branch", "Gain 3 [oxygen]."),
            ("branch-separator", "OR"),
            ("gain-oxygen-token-branch", "Gain 1 [oxygenToken]."),
        ],
        sentence_texts=["You can use this Item for free\nimmediately after gaining it.", "Gain 3 [oxygen].", "Gain 1 [oxygenToken]."],
        icon_specs=[("upperRight", "notInCombat", "icon.notInCombat", "canonical", 0), ("body", "[oxygen]", "icon.oxygen", "canonical", 0), ("body", "[oxygenToken]", "icon.oxygenToken", "canonical", 0)],
        effect_kind="gap-oxygen-tank", named_identity_ref="NI-0348",
    ),
    "sheet34-02": _asset(
        "sheet34-02", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-02.png", "generated-cell-selector-gap-variant",
        "PHOSPHATES", "Reinforce 1 empty Corridor.\nOR\nPlace 2 [secure].",
        custom_deck_ids=["34"], source_sheet="34", generated_cell=2, physical_class="regular-item", selected_disposition="yellow-selector-gap",
        upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("reinforce-corridor-branch", "Reinforce 1 empty Corridor."), ("branch-separator", "OR"), ("place-secure-branch", "Place 2 [secure].")],
        sentence_texts=["Reinforce 1 empty Corridor.", "Place 2 [secure]."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[secure]", "icon.secure", "selected-verified", 0)],
        effect_kind="gap-phosphates-secure", named_identity_ref="NI-0355",
    ),
    "sheet34-03": _asset(
        "sheet34-03", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-145_cards/card-03.png", "generated-cell-regular-face",
        "TOOLS", "Discard a [malfunction]\nOR\nOpen or Close 1 Door.",
        custom_deck_ids=["34"], source_sheet="34", generated_cell=3, physical_class="regular-item", selected_disposition="included-regular",
        upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("discard-malfunction-branch", "Discard a [malfunction]"), ("branch-separator", "OR"), ("door-state-branch", "Open or Close 1 Door.")],
        sentence_texts=["Discard a [malfunction]", "Open or Close 1 Door."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[malfunction]", "icon.malfunction", "selected-verified", 0)],
        effect_kind="discard-malfunction-or-door", named_identity_ref="NI-0488",
    ),
    "sheet33-00": _asset(
        "sheet33-00", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-00.png", "generated-cell-cross-family-selector-gap",
        "MILITARY TASER", "1 chosen [intruder] in your Room Escapes.\nOR\n1 chosen Character discards all [ICON: upright light-gray rounded rectangle with white rim].",
        custom_deck_ids=["33", "35"], source_sheet="33", generated_cell=0, physical_class="cross-family-red-class-conflict", selected_disposition="cross-family-gap-excluded",
        type_line="ONE USE ONLY. SPECIAL WEAPON",
        body_panels=[("escape-intruder-branch", "1 chosen [intruder] in your Room Escapes."), ("branch-separator", "OR"), ("discard-local-card-glyph-branch", "1 chosen Character discards all [ICON: upright light-gray rounded rectangle with white rim].")],
        sentence_texts=["1 chosen [intruder] in your Room Escapes.", "1 chosen Character discards all [ICON: upright light-gray rounded rectangle with white rim]."],
        icon_specs=[("body", "[intruder]", "icon.intruder", "selected-verified", 0), ("body", LOCAL_ACTION_RECTANGLE, None, "selected-unresolved", 0)],
        effect_kind="cross-family-military-taser", named_identity_ref=None,
    ),
    "sheet33-01": _asset(
        "sheet33-01", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-01.png", "generated-cell-physical-class-conflict",
        "FIRE EXTINGUISHER", "Discard a [fire].\n\nOR\n\n1 chosen [intruder] in your Room Escapes.",
        custom_deck_ids=["33"], source_sheet="33", generated_cell=1,
        physical_class="source-conflicted-portrait-special-weapon-versus-licensed-heavy", selected_disposition="class-conflict-excluded",
        type_line="ONE USE ONLY. SPECIAL WEAPON",
        body_panels=[("discard-fire-branch", "Discard a [fire]."), ("branch-separator", "OR"), ("escape-intruder-branch", "1 chosen [intruder] in your Room Escapes.")],
        sentence_texts=["Discard a [fire].", "1 chosen [intruder] in your Room Escapes."],
        icon_specs=[("body", "[fire]", "icon.fire", "canonical", 0), ("body", "[intruder]", "icon.intruder", "canonical", 0)],
        effect_kind="class-conflict-fire-extinguisher", named_identity_ref=None,
    ),
    "sheet33-02": _asset(
        "sheet33-02", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-02.png", "generated-cell-selector-gap-variant",
        "ROBOT CONTROLLER", "Use the [robot] from anywhere in the Facility.\nOR\nIf [robot] is not on the board yet, place it in your Room.",
        custom_deck_ids=["33"], source_sheet="33", generated_cell=2,
        physical_class="source-conflicted-portrait-item-versus-licensed-heavy", selected_disposition="yellow-selector-gap",
        type_line="", upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("remote-robot-branch", "Use the [robot] from anywhere in the Facility."), ("branch-separator", "OR"), ("place-robot-branch", "If [robot] is not on the board yet, place it in your Room.")],
        sentence_texts=["Use the [robot] from anywhere in the Facility.", "If [robot] is not on the board yet, place it in your Room."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[robot]", "icon.robot", "selected-verified", 0), ("body", "[robot]", "icon.robot", "selected-verified", 1)],
        effect_kind="gap-robot-controller", named_identity_ref="NI-0412",
    ),
    "sheet33-03": _asset(
        "sheet33-03", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-03.png", "generated-cell-non-rules-selector-gap",
        "", "", custom_deck_ids=["33"], source_sheet="33", generated_cell=3,
        physical_class="non-rules-placeholder-cell", selected_disposition="non-rules-gap-excluded", type_line="",
        effect_kind="non-rules-placeholder", rules_text_present=False,
    ),
}


def _definition(root_sequence: int, asset_key: str, card_id: int, guid: str, custom_deck_id: str, disposition: str) -> dict:
    code = f"{card_id}-{guid.upper()}"
    regular = disposition == "included-regular"
    occurrence_id = f"TTS-YELLOW-ITEM-{code}-FACE" if regular else f"TTS-YELLOW-ITEM-CLASS-CONFLICT-{code}-FACE"
    source_id = f"SRC-YELLOW-ITEM-{code}" if regular else f"SRC-YELLOW-ITEM-CLASS-CONFLICT-{code}"
    return {
        "rootSequence": root_sequence,
        "assetKey": asset_key,
        "ttsCardId": card_id,
        "ttsCardGuid": guid,
        "customDeckId": custom_deck_id,
        "disposition": disposition,
        "regular": regular,
        "occurrenceId": occurrence_id,
        "sourceId": source_id,
        "semanticRuleId": f"SEM-YELLOW-ITEM-{code}-001" if regular else None,
    }


ROOT_PHYSICAL_DEFINITIONS = [
    _definition(1, "direct-robot", 531800, "1b4ba6", "5318", "class-conflict-excluded"),
    _definition(2, "sheet33-01", 3301, "17ccd0", "33", "class-conflict-excluded"),
    _definition(3, "sheet33-01", 3301, "c76308", "33", "class-conflict-excluded"),
    _definition(4, "sheet33-01", 3301, "e7f4f9", "33", "class-conflict-excluded"),
    _definition(5, "sheet33-01", 3301, "f2016c", "33", "class-conflict-excluded"),
    _definition(6, "sheet33-01", 3301, "afbd16", "33", "class-conflict-excluded"),
    _definition(7, "sheet34-03", 3403, "2171b1", "34", "included-regular"),
    _definition(8, "sheet34-03", 3403, "41a9c1", "34", "included-regular"),
    _definition(9, "sheet34-03", 3403, "f456c3", "34", "included-regular"),
    _definition(10, "sheet34-03", 3403, "4efd6d", "34", "included-regular"),
    _definition(11, "sheet34-03", 3403, "9d4208", "34", "included-regular"),
    _definition(12, "sheet34-03", 3403, "d2ecec", "34", "included-regular"),
    _definition(13, "direct-phosphates", 395400, "6a29b0", "3954", "included-regular"),
    _definition(14, "direct-phosphates", 395400, "0b949c", "3954", "included-regular"),
    _definition(15, "direct-phosphates", 395400, "8f66f9", "3954", "included-regular"),
    _definition(16, "direct-phosphates", 395400, "11861a", "3954", "included-regular"),
    _definition(17, "direct-phosphates", 395400, "988612", "3954", "included-regular"),
    _definition(18, "direct-oxygen", 532000, "ce55d9", "5320", "included-regular"),
    _definition(19, "direct-oxygen", 532000, "45f0f3", "5320", "included-regular"),
    _definition(20, "direct-oxygen", 532000, "28907a", "5320", "included-regular"),
    _definition(21, "direct-oxygen", 532000, "8a4908", "5320", "included-regular"),
    _definition(22, "direct-oxygen", 532000, "490933", "5320", "included-regular"),
    _definition(23, "direct-oxygen", 532000, "1ff6e7", "5320", "included-regular"),
    _definition(24, "direct-oxygen", 532000, "5db915", "5320", "included-regular"),
    _definition(25, "direct-oxygen", 532000, "ce5897", "5320", "included-regular"),
    _definition(26, "sheet34-00", 3400, "801470", "34", "included-regular"),
    _definition(27, "sheet34-00", 3400, "a29f14", "34", "included-regular"),
    _definition(28, "sheet34-00", 3400, "2284bd", "34", "included-regular"),
    _definition(29, "sheet34-00", 3400, "534b88", "34", "included-regular"),
    _definition(30, "sheet34-00", 3400, "bea081", "34", "included-regular"),
]
REGULAR_PHYSICAL_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if row["regular"]]
CLASS_CONFLICT_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if not row["regular"]]
for family_sequence, row in enumerate(REGULAR_PHYSICAL_DEFINITIONS, 1):
    row["familySequence"] = family_sequence

YELLOW_ITEM_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS]
TOOLS_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet34-03"]
PHOSPHATES_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-phosphates"]
OXYGEN_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-oxygen"]
DUCT_TAPE_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet34-00"]
LOCAL_GLYPH_RULE_IDS = [*TOOLS_RULE_IDS, *PHOSPHATES_RULE_IDS, *DUCT_TAPE_RULE_IDS]

YELLOW_ITEM_QUESTION_BLOCKS = {
    "SEM-Q-039": ["SEM-YELLOW-ITEM-ONE-USE-001"],
    "SEM-Q-040": ["SEM-YELLOW-ITEM-DECK-001"],
    "SEM-Q-044": [*OXYGEN_RULE_IDS],
    "SEM-Q-045": ["SEM-YELLOW-ITEM-IMMEDIATE-USE-001", *OXYGEN_RULE_IDS],
    "SEM-Q-051": LOCAL_GLYPH_RULE_IDS,
    "SEM-Q-052": ["SEM-YELLOW-ITEM-DECK-001"],
    "SEM-Q-053": ["SEM-YELLOW-ITEM-ONE-USE-001", *DUCT_TAPE_RULE_IDS],
    "SEM-Q-054": ["SEM-ITEM-TRADE-GAIN-001", *DUCT_TAPE_RULE_IDS],
    "SEM-Q-055": PHOSPHATES_RULE_IDS,
    "SEM-Q-056": TOOLS_RULE_IDS,
}


def _raw_yellow_deck(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    deck = _find_guid(root.get("ObjectStates"), BASE_YELLOW_ITEM_DECK_GUID)
    if not isinstance(deck, dict):
        raise AssertionError("base Yellow Item root Deck missing from raw TTS save")
    return deck, hashlib.sha256(data).hexdigest()


def _parse_bga_yellow_items(path: Path) -> list[dict]:
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
        if not deck_match or ast.literal_eval(deck_match.group(1)) != "deck-yellow":
            continue

        def literal(pattern: str, default=None):
            found = re.search(pattern, source_block, re.S)
            return ast.literal_eval(found.group(1)) if found else default

        nbr_match = re.search(r"\n    nbr: (\d+)", source_block)
        if not nbr_match:
            raise AssertionError(f"licensed Yellow Item multiplicity missing: {key}")
        rows.append({
            "key": key,
            "sourceOrder": source_index + 1,
            "deck": "deck-yellow",
            "name": literal(r"\n    name: ('(?:\\.|[^'])*')"),
            "subtitle": literal(r"\n    subtitle: ('(?:\\.|[^'])*')"),
            "heavy": bool(re.search(r"\n    heavy: true", source_block)),
            "armor": bool(re.search(r"\n    armor: true", source_block)),
            "rangedWeapon": bool(re.search(r"\n    rangedWeapon: true", source_block)),
            "meleeWeapon": bool(re.search(r"\n    meleeWeapon: true", source_block)),
            "noAmmoWeapon": bool(re.search(r"\n    noAmmoWeapon: true", source_block)),
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
        ("DuctTape", 5, False), ("FireExtinguisher", 5, True), ("OxygenTank", 8, False),
        ("Phosphates", 5, False), ("RobotController", 1, True), ("Tools", 6, False),
    ]
    if [(row["key"], row["nbr"], row["heavy"]) for row in rows] != expected:
        raise AssertionError("licensed Yellow Item rows/order/multiplicity changed")
    return rows


def _selected_text_contains_asset(selected_run: dict, asset: dict) -> bool:
    visible = selected_run.get("visibleText") or {}
    strings = []

    def collect(value) -> None:
        if isinstance(value, str):
            strings.append(value)
        elif isinstance(value, dict):
            for child in value.values():
                collect(child)
        elif isinstance(value, list):
            for child in value:
                collect(child)

    collect(visible)
    haystack = "\n".join(strings)
    return (
        visible.get("title") == asset["printedTitle"]
        and all(sentence in haystack for sentence in asset["sentenceTexts"])
        and visible.get("typeLine") == asset["typeLine"]
    )


def build_yellow_item_source_index(repo: Path) -> dict:
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

    matching_roles = [row for row in roles if row.get("role") == "yellowItemsDeck"]
    if len(matching_roles) != 1:
        raise AssertionError("Yellow Item Lua role multiplicity changed")
    role = matching_roles[0]
    expected_deck_nums = ["33", "34", "3954", "5318", "5320"]
    if role.get("guid") != BASE_YELLOW_ITEM_DECK_GUID or role.get("type") != "Deck" or role.get("gmnotes") != "yellowitemDiscard" or role.get("n_urls") != 7 or role.get("deck_nums") != expected_deck_nums:
        raise AssertionError("base Yellow Item Lua role changed")

    raw_deck, raw_save_sha = _raw_yellow_deck(repo)
    raw_deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
    expected_deck_ids = [row["ttsCardId"] for row in ROOT_PHYSICAL_DEFINITIONS]
    if raw_deck_ids != expected_deck_ids:
        raise AssertionError("base Yellow Item raw DeckIDs order changed")
    contained_value = raw_deck.get("ContainedObjects") or {}
    contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
    expected_children = [(row["ttsCardId"], row["ttsCardGuid"]) for row in ROOT_PHYSICAL_DEFINITIONS]
    if [(int(row["CardID"]), row["GUID"]) for row in contained] != expected_children:
        raise AssertionError("base Yellow Item raw contained occurrence order changed")
    root_custom = raw_deck.get("CustomDeck") or {}
    if set(root_custom) != set(expected_deck_nums):
        raise AssertionError("base Yellow Item root CustomDeck IDs changed")
    expected_custom = {
        "33": (SHEET_33_FACE_URL, UNIQUE_BACK_SHEET_URL, 2, 2, True, True, 0),
        "34": (SHEET_34_FACE_URL, SHARED_BACK_URL, 2, 2, True, False, 0),
        "3954": ("https://steamusercontent-a.akamaihd.net/ugc/11925215517038364/893293A964CAD5BA1C0BAC2151347F3DFCEB39DA/", SHARED_BACK_URL, 1, 1, True, False, 0),
        "5318": ("https://steamusercontent-a.akamaihd.net/ugc/15675662852869742422/12CD04D399C375C4CE7995ED1E7D4CB251EB3880/", SHARED_BACK_URL, 1, 1, True, False, 0),
        "5320": ("https://steamusercontent-a.akamaihd.net/ugc/12290911472281889972/157636E7D8FCB7FCD661479C09512756EE788A9C/", SHARED_BACK_URL, 1, 1, True, False, 0),
    }
    for custom_id, expected in expected_custom.items():
        custom = root_custom[custom_id]
        actual = (custom.get("FaceURL"), custom.get("BackURL"), custom.get("NumWidth"), custom.get("NumHeight"), custom.get("BackIsHidden"), custom.get("UniqueBack"), custom.get("Type"))
        if actual != expected:
            raise AssertionError(f"base Yellow Item CustomDeck tuple changed: {custom_id}")

    root_object = next(row for row in objects if row.get("guid") == BASE_YELLOW_ITEM_DECK_GUID)
    yellow_children = [row for row in objects if ["Deck", BASE_YELLOW_ITEM_DECK_GUID, ""] in (row.get("parent") or []) and row.get("gmnotes") == "yellowitem"]
    all_yellow_tagged = [row for row in objects if row.get("gmnotes") == "yellowitem"]
    if root_object.get("type") != "Deck" or root_object.get("parent") != [] or len(yellow_children) != 30 or len(all_yellow_tagged) != 30 or {(int(row["card_id"]), row["guid"]) for row in yellow_children} != set(expected_children):
        raise AssertionError("base Yellow Item object/tag/container closure changed")
    classification_by_guid = {row["guid"]: row for row in classification}
    if classification_by_guid[BASE_YELLOW_ITEM_DECK_GUID].get("verdict") != "base" or any(classification_by_guid[guid].get("verdict") != "base" for _, guid in expected_children):
        raise AssertionError("Yellow Item base classification changed")

    bga_rows = _parse_bga_yellow_items(repo / BGA_ITEMS_PATH)
    bga_table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "ITEMS_DATA")
    if bga_table.get("count") != 57 or not set(row["key"] for row in bga_rows).issubset(set(bga_table.get("keys") or [])):
        raise AssertionError("licensed Yellow Item evidence-index closure changed")
    if sum(row["nbr"] for row in bga_rows) != 30 or sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]) != 24 or sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]) != 6:
        raise AssertionError("licensed Yellow Item aggregate class/count boundary changed")

    sheet_meta = {
        "33": (YELLOW_ITEM_SHEET_33_SOURCE_ID, YELLOW_ITEM_SHEET_33_PATH, {"columns": 2, "rows": 2}),
        "34": (YELLOW_ITEM_SHEET_34_SOURCE_ID, YELLOW_ITEM_SHEET_34_PATH, {"columns": 2, "rows": 2}),
    }
    source_asset_rows = []
    source_asset_by_key = {}
    for asset_key, asset in ASSET_DEFINITIONS.items():
        source_path = asset["sourcePath"]
        source_sha = _sha(repo / source_path)
        corpus_row = corpus_by_path.get(source_path) or {}
        if corpus_row.get("sourceSha256") != source_sha:
            raise AssertionError(f"Yellow Item corpus/hash readiness drift: {asset_key}")
        if asset["rulesTextPresent"]:
            if not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"}:
                raise AssertionError(f"Yellow Item rules/readiness drift: {asset_key}")
        elif corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") != "non-rules-or-reference":
            raise AssertionError(f"Yellow Item non-rules cell drift: {asset_key}")
        selected_entry = selected_by_path.get(source_path) or {}
        selected_runs = selected_entry.get("runs") or []
        selected_run = selected_runs[0] if len(selected_runs) == 1 else None
        if corpus_row.get("extractionState") in {"draft-full", "non-rules-or-reference"}:
            if selected_run is None:
                raise AssertionError(f"Yellow Item selected source evidence missing: {asset_key}")
            if asset["rulesTextPresent"] and not _selected_text_contains_asset(selected_run, asset):
                raise AssertionError(f"Yellow Item selected title/body evidence drift: {asset_key}")
            if not asset["rulesTextPresent"] and ((selected_run.get("visibleText") or {}).get("body") or (selected_run.get("visibleText") or {}).get("title")):
                raise AssertionError(f"Yellow Item selected non-rules evidence drift: {asset_key}")
        elif selected_runs:
            raise AssertionError(f"Yellow Item canonical asset unexpectedly depends on selected overlay: {asset_key}")
        progress_row = progress_by_path.get(source_path) or {}
        vision_result_path = (progress_row.get("vision") or {}).get("resultPath")
        vision_result = json.loads((repo / vision_result_path).read_text(encoding="utf-8")) if vision_result_path else None
        if corpus_row.get("extractionState") == "verified-canonical":
            parsed = (vision_result or {}).get("parsed") or {}
            if parsed.get("title") != asset["printedTitle"]:
                raise AssertionError(f"Yellow Item canonical title evidence drift: {asset_key}")
        generated = progress_row.get("generatedFrom") or (low_by_path.get(source_path) or {}).get("provenance") or {}
        if asset["generatedCell"] is not None:
            _, expected_sheet_path, _ = sheet_meta[asset["sourceSheet"]]
            if generated.get("sourceSheetPath") != expected_sheet_path or generated.get("cellIndex") != asset["generatedCell"]:
                raise AssertionError(f"Yellow Item generated source/cell drift: {asset_key}")
        elif generated.get("sourceSheetPath") is not None or generated.get("cellIndex") is not None:
            raise AssertionError(f"Yellow Item direct/generated inversion: {asset_key}")
        panels = _source_panels(asset)
        regions = _source_regions(asset)
        sentences = _source_sentences(asset, panels)
        icons = _source_icons(asset, selected_run, vision_result, panels)
        selected_occurrences = [row["occurrenceId"] for row in ROOT_PHYSICAL_DEFINITIONS if row["assetKey"] == asset_key]
        source_id = None
        if not selected_occurrences:
            if asset["sourceSheet"] == "34":
                source_id = f"SRC-YELLOW-ITEM-VARIANT-34-CELL-{asset['generatedCell']:02d}"
            elif asset["selectedDisposition"] == "cross-family-gap-excluded":
                source_id = f"SRC-YELLOW-ITEM-CROSS-FAMILY-33-CELL-{asset['generatedCell']:02d}"
            elif asset["selectedDisposition"] == "non-rules-gap-excluded":
                source_id = f"SRC-YELLOW-ITEM-NON-RULES-33-CELL-{asset['generatedCell']:02d}"
            else:
                source_id = f"SRC-YELLOW-ITEM-VARIANT-33-CELL-{asset['generatedCell']:02d}"
        source_sheet_id = source_sheet_path = source_sheet_grid = None
        if asset["sourceSheet"]:
            source_sheet_id, source_sheet_path, source_sheet_grid = sheet_meta[asset["sourceSheet"]]
        normalized_corpus_body = (corpus_row.get("printedData") or {}).get("body")
        source_asset_row = {
            **{key: asset[key] for key in ("assetKey", "sourcePath", "sourceRole", "customDeckIds", "generatedCell", "physicalClass", "selectedDisposition", "printedTitle", "typeLine", "upperRight", "printedBody", "effectKind", "namedIdentityRef", "rulesTextPresent")},
            "sourceSheet": asset["sourceSheet"],
            "sourceId": source_id,
            "sourceSha256": source_sha,
            "sourceSheetId": source_sheet_id,
            "sourceSheetPath": source_sheet_path,
            "sourceSheetGrid": source_sheet_grid,
            "selectedByRootDeck": bool(selected_occurrences),
            "selectedPhysicalOccurrenceIds": selected_occurrences,
            "selectorGap": None if selected_occurrences else {
                "status": "explicit-no-Yellow-root-DeckID-GUID-selector",
                "reason": "The generated source-sheet cell exists, but no raw Yellow root full CardID/GUID selector selects it; cross-family and non-rules cells remain excluded.",
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
            "rulesInformationReadiness": corpus_row.get("rulesInformationReadiness"),
            "representationBoundary": {
                "normalizedCorpusBody": normalized_corpus_body,
                "semanticProjectionBody": asset["printedBody"],
                "bodyDiffers": normalized_corpus_body != asset["printedBody"],
                "selectedEvidenceConflicts": (selected_run or {}).get("conflictsWithPriorSnapshot") or [],
                "policy": "semantic projection uses exact visible sections plus source-scoped icon adjudication without rewriting the extraction record; conflicting normalized placeholders remain visible here",
            },
        }
        source_asset_rows.append(source_asset_row)
        source_asset_by_key[asset_key] = source_asset_row

    for sheet_key, (_, sheet_path_value, grid) in sheet_meta.items():
        sheet_path = repo / sheet_path_value
        with Image.open(sheet_path) as sheet_image:
            if sheet_image.size != (grid["columns"] * 591, grid["rows"] * 863):
                raise AssertionError(f"Yellow Item CustomDeck {sheet_key} source-sheet dimensions/grid changed")
            for cell in range(grid["columns"] * grid["rows"]):
                row_index, column_index = divmod(cell, grid["columns"])
                crop = sheet_image.crop((column_index * 591, row_index * 863, (column_index + 1) * 591, (row_index + 1) * 863)).convert("RGB")
                generated_asset = source_asset_by_key[f"sheet{sheet_key}-{cell:02d}"]
                with Image.open(repo / generated_asset["sourcePath"]) as generated_image:
                    if generated_image.convert("RGB").tobytes() != crop.tobytes():
                        raise AssertionError(f"Yellow Item CustomDeck {sheet_key} generated-cell pixel drift: {cell}")

    contained_by_tuple = {(int(row["CardID"]), row["GUID"]): row for row in contained}

    def build_physical(definition: dict) -> dict:
        asset = source_asset_by_key[definition["assetKey"]]
        raw_child = contained_by_tuple[(definition["ttsCardId"], definition["ttsCardGuid"])]
        custom = root_custom[definition["customDeckId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        side_role = "operative-regular-yellow-item-face" if definition["regular"] else "excluded-source-conflicted-yellow-root-face"
        batch_disposition = "included-regular-yellow-item-face" if definition["regular"] else "excluded-physical-class-conflict"
        sheet_hash = _sha(repo / asset["sourceSheetPath"]) if asset["generatedCell"] is not None else None
        unique_back = bool(custom.get("UniqueBack"))
        selector = {
            "key": "FaceURL",
            "objectType": raw_child.get("Name"),
            "fullCardId": definition["ttsCardId"],
            "guid": definition["ttsCardGuid"],
            "parentDeckGuid": BASE_YELLOW_ITEM_DECK_GUID,
            "customDeckId": definition["customDeckId"],
            "url": custom["FaceURL"],
            "backUrl": custom["BackURL"],
            "backIsHidden": custom.get("BackIsHidden"),
            "uniqueBack": unique_back,
            "backGeneratedCell": asset["generatedCell"] if unique_back else None,
            "sideRole": side_role,
            "sourceRole": asset["sourceRole"],
            "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-BackURL-parent-tuple-with-explicit-generated-cell" if asset["generatedCell"] is not None else "exact-full-CardID-GUID-direct-FaceURL-BackURL-parent-tuple",
            "generatedSpriteSheetCell": asset["generatedCell"] is not None,
            "sourceSheetPath": asset["sourceSheetPath"],
            "sourceSheetSha256": sheet_hash,
            "sourceSheetGrid": asset["sourceSheetGrid"],
            "generatedCell": asset["generatedCell"],
            "selectorGap": None,
            "cardIdModuloJoinUsed": False,
        }
        provenance_source_path = asset["sourceSheetPath"] if asset["generatedCell"] is not None else asset["sourcePath"]
        provenance_file = provenance_source_path.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]
        provenance_row = provenance_by_file.get(provenance_file) or {}
        exact_ref = next((row for row in provenance_row.get("objects") or [] if row.get("key") == "FaceURL" and row.get("guid") == definition["ttsCardGuid"] and row.get("cardId") == definition["ttsCardId"]), None)
        if exact_ref is None or exact_ref.get("parent") != [["Deck", BASE_YELLOW_ITEM_DECK_GUID, ""]] or provenance_row.get("url") != custom["FaceURL"]:
            raise AssertionError(f"Yellow Item exact provenance selector drift: {code}")
        physical_regions = [{**region, "regionId": f"YI-{code}-{region['regionId']}"} for region in asset["regions"]]
        region_map = {old: new["regionId"] for old, new in zip(("R1", "R2", "R3"), physical_regions)}
        physical_panels = [{**panel, "panelId": f"YI-{code}-{panel['panelId']}", "regionId": region_map[panel["regionId"]]} for panel in asset["panels"]]
        panel_map = {source["panelId"]: physical["panelId"] for source, physical in zip(asset["panels"], physical_panels)}
        physical_sentences = [{**sentence, "sentenceId": f"YI-{code}-S{sentence['sequence']:02d}", "regionId": region_map[sentence["regionId"]], "panelId": panel_map[sentence["panelId"]]} for sentence in asset["sentences"]]
        physical_icons = [{**icon, "occurrenceId": f"YI-{code}-I{icon['sequence']:02d}", "assetMorphologyOccurrenceId": icon["assetIconOccurrenceId"], "regionId": region_map[icon["regionId"]], "panelId": panel_map[icon["panelId"]], "mappingScope": f"exact physical root occurrence {definition['occurrenceId']} only"} for icon in asset["iconOccurrences"]]
        backlog_id = "CARD:" + asset["sourceSha256"][:16]
        backlog_row = backlog_by_id.get(backlog_id) or {}
        if backlog_row.get("sourcePath") != asset["sourcePath"] or backlog_row.get("sourceLocator") != asset["sourceSha256"]:
            raise AssertionError(f"Yellow Item backlog source tuple drift: {definition['occurrenceId']}")
        return {
            "yellowItemOccurrenceId": definition["occurrenceId"],
            "rootSequence": definition["rootSequence"],
            "familySequence": definition.get("familySequence"),
            "ttsRole": "yellowItemsDeck",
            "ttsDeckGuid": BASE_YELLOW_ITEM_DECK_GUID,
            "ttsDeckType": "Deck",
            "ttsCardId": definition["ttsCardId"],
            "ttsCardGuid": definition["ttsCardGuid"],
            "customDeckId": definition["customDeckId"],
            "sourceSelector": selector,
            "sourceId": definition["sourceId"],
            "sourcePath": asset["sourcePath"],
            "sourceSha256": asset["sourceSha256"],
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS source-bound base yellowItemsDeck root occurrence {definition['rootSequence']} / full CardID {definition['ttsCardId']} / GUID {definition['ttsCardGuid']}",
            "sourceAssetKey": definition["assetKey"],
            "physicalClass": asset["physicalClass"],
            "batchDisposition": batch_disposition,
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
            "licensedCrosswalk": {"status": "not-asserted", "reason": "licensed rows remain independent; aggregate class/copy equality is not a title, body, key, order, or multiplicity crosswalk"},
            "officialCrosswalk": {"status": "not-asserted", "reason": "no checked official occurrence identifies this exact TTS full CardID/GUID physical copy; even Duct Tape title equality supplies no copy identity"},
            "joinEvidence": {
                "identityJoin": "exact raw root physical occurrence and exact source-asset projection",
                "titleOnlyJoin": False,
                "colorOnlyJoin": False,
                "utilityOrSystemAppearanceJoin": False,
                "bodyResemblanceJoin": False,
                "folderOnlyJoin": False,
                "sourceOrderOnlyJoin": False,
                "generatedCellOnlyJoin": False,
                "cardIdModuloJoin": False,
                "licensedKeyJoin": False,
                "basis": ["sole base yellowItemsDeck Lua role and exact raw root GUID", "raw saved DeckIDs plus contained full CardID/GUID occurrence", "exact CustomDeck ID, FaceURL, BackURL, UniqueBack, parent deck, and source SHA-256", "for generated faces: exact sheet hash/grid/cell plus full selector"],
            },
        }

    regular_faces = [build_physical(row) for row in REGULAR_PHYSICAL_DEFINITIONS]
    class_conflict_faces = [build_physical(row) for row in CLASS_CONFLICT_DEFINITIONS]

    for path_value, expected_refs, expected_key in (
        (YELLOW_ITEM_SHARED_BACK_PATH, 26, "BackURL"),
        (YELLOW_ITEM_UNIQUE_BACK_SHEET_PATH, 13, "BackURL"),
        (YELLOW_ITEM_SHEET_34_PATH, 12, "FaceURL"),
        (YELLOW_ITEM_SHEET_33_PATH, 13, "FaceURL"),
    ):
        provenance_row = provenance_by_file[path_value.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]]
        if provenance_row.get("refs") != expected_refs or {row.get("key") for row in provenance_row.get("objects") or []} != {expected_key}:
            raise AssertionError(f"Yellow Item sheet/back provenance changed: {path_value}")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    official_ids = [
        "RB-P03-V01", "RB-P05-V01", "RB-P09-V01", "RB-P12-V02", "RB-P16-V02", "RB-P17-V01",
        "RB-P21-V01", "RB-P22-V01", "RB-P23-V02", "RB-P28-V02", "RB-P28-V03", "RB-P29-V01",
        "RB-P29-V03", "RB-P37-V01", "RB-P40-V02",
    ]
    if any(occurrence_id not in visual_by_id for occurrence_id in official_ids):
        raise AssertionError("Yellow Item official visual occurrence missing")
    official_counterparts = [
        {"sourceOccurrenceId": "RB-P03-V01", "kind": "family-count-and-representative-card-images", "locator": "unprinted component page 3 / Item cards row", "visibleText": "90 Item cards (30 cards of each type)", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P05-V01", "kind": "finite-marker-token-inventory", "locator": "unprinted component page 5", "visibleText": "finite Fire, Malfunction, Door, Secure, Oxygen-token, and Robot-associated component counts", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P09-V01", "kind": "setup-deck-placement", "locator": "printed page 9 / C. Remaining Components", "visibleText": "three Item decks shuffled separately face down with discard spaces", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P12-V02", "kind": "use-item-action-cost", "locator": "printed page 12 / Basic Actions List", "visibleText": "Use an Item costs 1 Action card", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P16-V02", "kind": "tactical-gear-placement", "locator": "printed page 16 / Gaining Tactical Gear", "visibleText": "gained Tactical Gear occupies a compatible empty slot", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P17-V01", "kind": "oxygen-token-effect", "locator": "printed page 17 / Oxygen Tokens", "visibleText": "using an Oxygen token gains 3 Oxygen", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P21-V01", "kind": "reinforced-corridor-state", "locator": "printed page 21", "visibleText": "Corridor front/reinforced back, Noise discard, and value-0 state", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P22-V01", "kind": "door-state-placement", "locator": "printed page 22", "visibleText": "Open, Closed, and Destroyed Door placement/state distinctions", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P23-V02", "kind": "marker-icon-key", "locator": "printed page 23", "visibleText": "Fire, Malfunction, and Secure printed name/icon associations", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P28-V02", "kind": "yellow-item-search-icon", "locator": "printed page 28 / Search example", "visibleText": "Yellow Item icon participates in one-card-per-icon Search and private bottom return", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P28-V03", "kind": "current-official-duct-tape-face", "locator": "printed page 28 / Duct Tape", "visibleText": "DUCT TAPE / ONE USE ONLY / Discard a source glyph OR Place 1 Heavy Item above another Heavy Item in your Hand slot (effectively carrying 2 Heavy Items in 1 Hand).", "exactRegularYellowRulesFace": True, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P29-V01", "kind": "heavy-item-format-boundary", "locator": "printed page 29", "visibleText": "horizontal Items are Heavy and do not fit in a Backpack", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P29-V03", "kind": "oxygen-slot-color-key", "locator": "printed page 29", "visibleText": "yellow Oxygen slots and gray Any slots", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P37-V01", "kind": "robot-and-tactical-gear-associations", "locator": "printed page 37", "visibleText": "Robot model/icon plus Robot Ammo/Oxygen slots and Activation context", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P40-V02", "kind": "icon-glossary", "locator": "printed page 40", "visibleText": "Yellow Item, Oxygen, Oxygen token, Robot, Fire, Malfunction, Secure, and related exact icon names", "exactRegularYellowRulesFace": False, "exactTtsPhysicalCrosswalk": False},
    ]

    faq_units = [unit for page in faq["pages"] for unit in page.get("units", [])]
    faq_by_id = {unit["sourceUnitId"]: unit for unit in faq_units}
    relevant_faq_ids = ["FQ-P02-U10", "FQ-P02-U18", "FQ-P03-U04", "FQ-P03-U05", "FQ-P03-U06", "FQ-P03-U07"]
    relevant_faq = [{"sourceUnitId": source_id, "applicability": faq_by_id[source_id]["applicability"], "printedText": faq_by_id[source_id]["printedText"]} for source_id in relevant_faq_ids]
    if any(row["applicability"] not in {"base-game", "base-game-additional-mode"} for row in relevant_faq):
        raise AssertionError("Yellow Item FAQ applicability changed")
    excluded_faq = [unit["sourceUnitId"] for unit in faq_units if unit.get("applicability", "").startswith("expansion") and re.search(r"Item|Oxygen|Robot|Door|Corridor|Malfunction|Fire|Secure", unit.get("printedText", ""), re.I)]

    regular_asset_keys = {row["assetKey"] for row in REGULAR_PHYSICAL_DEFINITIONS}
    selected_regular_assets = [row for row in source_asset_rows if row["assetKey"] in regular_asset_keys]
    variant_assets = [row for row in source_asset_rows if row["selectedDisposition"] == "yellow-selector-gap"]
    cross_family_gap_assets = [row for row in source_asset_rows if row["selectedDisposition"] == "cross-family-gap-excluded"]
    non_rules_gap_assets = [row for row in source_asset_rows if row["selectedDisposition"] == "non-rules-gap-excluded"]
    excluded_asset_keys = {row["assetKey"] for row in CLASS_CONFLICT_DEFINITIONS}
    excluded_assets = [row for row in source_asset_rows if row["assetKey"] in excluded_asset_keys]
    face_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in selected_regular_assets})
    variant_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in variant_assets})
    excluded_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in excluded_assets})
    cross_family_pending_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in cross_family_gap_assets if row["rulesTextPresent"]})
    overlapping_unit_ids = [
        "RULE:ACT-ITEM-001", "RULE:ACT-TRADE-001", "RULE:ACT-TACTICAL-001",
        "RULE:ITM-001", "RULE:ITM-002", "RULE:ITM-003", "RULE:ITM-004", "RULE:ITM-005", "RULE:ITM-006", "RULE:ITM-008",
        *[f"FAQ:{source_id}" for source_id in relevant_faq_ids], *[f"VIS:{source_id}" for source_id in official_ids],
    ]
    linked_unit_ids = sorted(set(face_unit_ids + variant_unit_ids + overlapping_unit_ids))
    if any(unit_id not in backlog_by_id for unit_id in linked_unit_ids + excluded_unit_ids + cross_family_pending_ids):
        raise AssertionError("Yellow Item backlog obligation ID missing")

    title_multiplicity = dict(sorted(Counter(row["printedTitle"] for row in regular_faces).items()))
    asset_multiplicity = dict(sorted(Counter(row["sourceAssetKey"] for row in regular_faces).items()))
    root_class_multiplicity = dict(sorted(Counter(row["physicalClass"] for row in [*regular_faces, *class_conflict_faces]).items()))
    regular_icons = [icon for face in regular_faces for icon in face["iconOccurrences"]]
    variant_icons = [icon for asset in variant_assets for icon in asset["iconOccurrences"]]
    cross_family_icons = [icon for asset in cross_family_gap_assets for icon in asset["iconOccurrences"]]
    class_conflict_icons = [icon for face in class_conflict_faces for icon in face["iconOccurrences"]]

    counts = {
        "rootPhysicalOccurrences": 30,
        "regularPhysicalFaceOccurrences": len(regular_faces),
        "explicitHeavyPhysicalOccurrences": 0,
        "physicalClassConflictOccurrences": len(class_conflict_faces),
        "currentLicensedHeavyAggregate": 6,
        "uniqueRegularPrintedTitles": len(title_multiplicity),
        "uniqueSelectedRegularFaceAssets": len(selected_regular_assets),
        "sourceFaceAssets": len(source_asset_rows),
        "rulesBearingSourceFaceAssets": sum(row["rulesTextPresent"] for row in source_asset_rows),
        "nonRulesSourceCells": sum(not row["rulesTextPresent"] for row in source_asset_rows),
        "generatedRegularPhysicalFaceOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] for row in regular_faces),
        "directRegularPhysicalFaceOccurrences": sum(not row["sourceSelector"]["generatedSpriteSheetCell"] for row in regular_faces),
        "generatedClassConflictPhysicalOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] for row in class_conflict_faces),
        "directClassConflictPhysicalOccurrences": sum(not row["sourceSelector"]["generatedSpriteSheetCell"] for row in class_conflict_faces),
        "sourceSheets": 2,
        "sourceSheetCells": 8,
        "selectedGeneratedCells": 3,
        "selectorGapCells": 5,
        "rulesBearingSelectorGapCells": 4,
        "sameFamilySelectorGapCells": len(variant_assets),
        "crossFamilySelectorGapCells": len(cross_family_gap_assets),
        "nonRulesSelectorGapCells": len(non_rules_gap_assets),
        "rootBackAssets": 2,
        "sharedBackPhysicalSelectors": 25,
        "uniqueBackSheetPhysicalSelectors": 5,
        "sharedBackGlobalSelectorReferences": 26,
        "uniqueBackSheetGlobalSelectorReferences": 13,
        "sheet33GlobalSelectorReferences": 13,
        "sheet34GlobalSelectorReferences": 12,
        "rootCustomDeckEntries": len(root_custom),
        "physicalRegions": sum(len(row["regions"]) for row in regular_faces),
        "operativeRegions": sum(sum(region["operative"] for region in row["regions"]) for row in regular_faces),
        "physicalPanels": sum(len(row["panels"]) for row in regular_faces),
        "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in regular_faces),
        "oneUseHeadingOccurrences": len(regular_faces),
        "specialWeaponHeadingOccurrences": sum("SPECIAL WEAPON" in row["typeLine"] for row in regular_faces),
        "branchSeparatorHeadingOccurrences": sum(sum(panel["role"] == "branch-separator" for panel in row["panels"]) for row in regular_faces),
        "useDiscardPassiveReactionHeadingOccurrences": 0,
        "printedSentenceOccurrences": sum(len(row["sentences"]) for row in regular_faces),
        "physicalFunctionalIconOccurrences": len(regular_icons),
        "physicalMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in regular_icons),
        "physicalUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in regular_icons),
        "rootPhysicalRegions": sum(len(row["regions"]) for row in [*regular_faces, *class_conflict_faces]),
        "rootOperativeRegions": sum(sum(region["operative"] for region in row["regions"]) for row in [*regular_faces, *class_conflict_faces]),
        "rootPhysicalPanels": sum(len(row["panels"]) for row in [*regular_faces, *class_conflict_faces]),
        "rootOperativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in [*regular_faces, *class_conflict_faces]),
        "rootPrintedSentenceOccurrences": sum(len(row["sentences"]) for row in [*regular_faces, *class_conflict_faces]),
        "rootFunctionalIconOccurrences": len(regular_icons) + len(class_conflict_icons),
        "rootMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in [*regular_icons, *class_conflict_icons]),
        "rootUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in [*regular_icons, *class_conflict_icons]),
        "classConflictPhysicalPanels": sum(len(row["panels"]) for row in class_conflict_faces),
        "classConflictOperativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in class_conflict_faces),
        "classConflictPrintedSentenceOccurrences": sum(len(row["sentences"]) for row in class_conflict_faces),
        "sameFamilyGapFunctionalIconOccurrences": len(variant_icons),
        "sameFamilyGapMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in variant_icons),
        "sameFamilyGapUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in variant_icons),
        "sameFamilyGapPhysicalPanels": sum(len(row["panels"]) for row in variant_assets),
        "sameFamilyGapPrintedSentenceOccurrences": sum(len(row["sentences"]) for row in variant_assets),
        "crossFamilyGapFunctionalIconOccurrences": len(cross_family_icons),
        "crossFamilyGapMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in cross_family_icons),
        "crossFamilyGapUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in cross_family_icons),
        "crossFamilyGapPhysicalPanels": sum(len(row["panels"]) for row in cross_family_gap_assets),
        "crossFamilyGapPrintedSentenceOccurrences": sum(len(row["sentences"]) for row in cross_family_gap_assets),
        "nonRulesGapPhysicalPanels": sum(len(row["panels"]) for row in non_rules_gap_assets),
        "classConflictFunctionalIconOccurrences": len(class_conflict_icons),
        "classConflictMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in class_conflict_icons),
        "classConflictUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in class_conflict_icons),
        "licensedDigitalOccurrences": len(bga_rows),
        "licensedDigitalPhysicalCopies": sum(row["nbr"] for row in bga_rows),
        "licensedRegularOccurrences": sum(not row["heavy"] and not row["armor"] for row in bga_rows),
        "licensedRegularPhysicalCopies": sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]),
        "licensedHeavyOccurrences": sum(row["heavy"] or row["armor"] for row in bga_rows),
        "licensedHeavyPhysicalCopies": sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]),
        "officialInventoryCopiesPerType": 30,
        "officialVisibleRegularFaceOccurrences": 1,
        "officialVisibleHeavySameTitleOccurrences": 0,
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
        "recordType": "semantic-yellow-item-source-index",
        "scope": "entire mechanically derived base yellowItemsDeck root: all 30 physical children retained, partitioned into 24 source-clear regular faces and six physical-class-conflict faces (five FIRE EXTINGUISHER plus one ROBOT CONTROLLER); two source sheets, five selector-gap cells, two materially different BackURL forms, official/FAQ evidence, and six licensed rows remain independent",
        "derivationPolicy": "Derive only from the sole base yellowItemsDeck Lua role and exact raw root GUID, saved DeckIDs, contained full CardID/GUID/CustomDeck/FaceURL/BackURL/UniqueBack tuples, and exact generated sheet/hash/grid/cell evidence. Never join by title, Yellow color, utility/repair/system appearance, body similarity, folder/order/cell, CardID modulo, licensed key, or multiplicity. Current licensed Heavy classification does not rewrite the six portrait TTS conflict occurrences.",
        "counts": counts,
        "rootDeckEvidence": {
            "sourceId": YELLOW_ITEM_ROOT_SOURCE_ID,
            "ttsRole": "yellowItemsDeck",
            "rootGuid": BASE_YELLOW_ITEM_DECK_GUID,
            "rootType": "Deck",
            "rootGmNotes": "yellowitemDiscard",
            "rawSavePath": RAW_SAVE_PATH,
            "rawSaveSha256": raw_save_sha,
            "luaRolePath": "assets/tts-mod/extract/v2/lua_roles.json",
            "objectsPath": "assets/tts-mod/extract/v2/objects.json",
            "savedDeckIds": raw_deck_ids,
            "fullContainedSelectors": [{"rootSequence": row["rootSequence"], "fullCardId": row["ttsCardId"], "guid": row["ttsCardGuid"], "customDeckId": row["customDeckId"], "batchDisposition": row["disposition"]} for row in ROOT_PHYSICAL_DEFINITIONS],
            "customDeckTuples": {key: {"faceUrl": value[0], "backUrl": value[1], "columns": value[2], "rows": value[3], "backIsHidden": value[4], "uniqueBack": value[5], "type": value[6]} for key, value in sorted(expected_custom.items())},
            "rootOrderIsGameplayOrder": False,
            "reason": "official setup shuffles each Item deck separately; saved sequence is provenance only",
        },
        "familyCountEvidence": {
            "official": {"count": 30, "scope": "Item cards of each type", "source": "RB-P03-V01 / rulebook_text lines 520–521"},
            "tts": {"rootChildren": 30, "sourceClearRegularIncluded": 24, "explicitHeavy": 0, "physicalClassConflictExcluded": 6, "classMultiplicity": root_class_multiplicity},
            "licensedDigital": {"deckYellowRows": len(bga_rows), "declaredCopies": 30, "regularCopies": 24, "heavyCopies": 6, "physicalIdentityCrosswalkAsserted": False},
            "reconciliation": "Official inventory and exact root each retain 30. Licensed 24/6 agrees in aggregate with 24 source-clear regular plus six current Heavy candidates, but five portrait FIRE EXTINGUISHER selectors and one portrait no-HEAVY ROBOT CONTROLLER selector remain occurrence-scoped class conflicts under SEM-Q-052; aggregate equality is not a copy crosswalk.",
            "backlog": {
                "faceUnitIds": face_unit_ids,
                "variantUnitIds": variant_unit_ids,
                "excludedClassConflictUnitIds": excluded_unit_ids,
                "crossFamilyPendingUnitIds": cross_family_pending_ids,
                "nonRulesGapPaths": [row["sourcePath"] for row in non_rules_gap_assets],
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
        "sourceSheets": [
            {"sourceId": YELLOW_ITEM_SHEET_33_SOURCE_ID, "occurrenceId": "TTS-YELLOW-ITEM-PARENT-SHEET-33", "sourcePath": YELLOW_ITEM_SHEET_33_PATH, "sourceSha256": _sha(repo / YELLOW_ITEM_SHEET_33_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS shared Red/Yellow CustomDeck 33/35 parent 2x2 face sheet", "sourceSelector": {"key": "FaceURL", "rootGuid": BASE_YELLOW_ITEM_DECK_GUID, "customDeckId": "33", "url": SHEET_33_FACE_URL, "grid": {"columns": 2, "rows": 2}, "sideRole": "parent-sheet-provenance-not-rules-face"}, "globalSelectorReferences": 13, "yellowRootSelectedCells": [1], "redRootSelectedCells": [0], "yellowSelectorGapCells": [0, 2, 3], "separateRulesFace": False},
            {"sourceId": YELLOW_ITEM_SHEET_34_SOURCE_ID, "occurrenceId": "TTS-YELLOW-ITEM-PARENT-SHEET-34", "sourcePath": YELLOW_ITEM_SHEET_34_PATH, "sourceSha256": _sha(repo / YELLOW_ITEM_SHEET_34_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS base Yellow Item CustomDeck 34 parent 2x2 face sheet", "sourceSelector": {"key": "FaceURL", "rootGuid": BASE_YELLOW_ITEM_DECK_GUID, "customDeckId": "34", "url": SHEET_34_FACE_URL, "grid": {"columns": 2, "rows": 2}, "sideRole": "parent-sheet-provenance-not-rules-face"}, "globalSelectorReferences": 12, "yellowRootSelectedCells": [0, 3], "yellowSelectorGapCells": [1, 2], "separateRulesFace": False},
        ],
        "rootBacks": [
            {"sourceId": YELLOW_ITEM_SHARED_BACK_SOURCE_ID, "occurrenceId": "TTS-YELLOW-ITEM-SHARED-BACK", "sourcePath": YELLOW_ITEM_SHARED_BACK_PATH, "sourceSha256": _sha(repo / YELLOW_ITEM_SHARED_BACK_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS base Yellow Item shared non-operative back", "sourceSelector": {"key": "BackURL", "rootGuid": BASE_YELLOW_ITEM_DECK_GUID, "url": SHARED_BACK_URL, "uniqueBack": False, "sideRole": "shared-non-operative-yellow-item-back"}, "rootPhysicalSelectors": 25, "globalSelectorReferences": 26, "visibleText": "[yellowItem] ITEM", "rulesTextPresent": False, "separateRulesFace": False},
            {"sourceId": YELLOW_ITEM_UNIQUE_BACK_SHEET_SOURCE_ID, "occurrenceId": "TTS-YELLOW-ITEM-UNIQUE-BACK-SHEET-33", "sourcePath": YELLOW_ITEM_UNIQUE_BACK_SHEET_PATH, "sourceSha256": _sha(repo / YELLOW_ITEM_UNIQUE_BACK_SHEET_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS shared 2x2 unique-back sheet used by Yellow CustomDeck 33 cell 1 and Red CustomDeck 35 cell 0", "sourceSelector": {"key": "BackURL", "rootGuid": BASE_YELLOW_ITEM_DECK_GUID, "customDeckId": "33", "url": UNIQUE_BACK_SHEET_URL, "grid": {"columns": 2, "rows": 2}, "uniqueBack": True, "rootSelectedCell": 1, "sideRole": "unique-back-sheet-provenance-not-rules-face"}, "rootPhysicalSelectors": 5, "yellowRootSelectedCells": [1], "redRootSelectedCells": [0], "selectorGapCells": [2, 3], "visibleCellRoles": [{"cell": 0, "literal": "Red Item back"}, {"cell": 1, "literal": "Yellow Item back"}, {"cell": 2, "literal": "Yellow Item back"}, {"cell": 3, "literal": "blank/non-rules"}], "globalSelectorReferences": 13, "rulesTextPresent": False, "separateRulesFace": False},
        ],
        "sourceFaceAssets": source_asset_rows,
        "faces": regular_faces,
        "physicalClassConflictFaces": class_conflict_faces,
        "licensedDigitalOccurrences": bga_rows,
        "officialVisibleCounterparts": official_counterparts,
        "officialRulebookTextOccurrences": [
            {"locator": "unprinted page 3 / lines 520–521", "text": "90 Item cards (30 cards of each type)."},
            {"locator": "printed page 9 / lines 2593–2600", "text": "Shuffle red, green, and yellow Item decks separately face down and leave discard space."},
            {"locator": "printed pages 16–17 / lines 3469–3548,3633–3638,3665–3673", "text": "Tactical Gear use/gain, finite supply, Oxygen-token effect, whole/local/component limits, and voluntary Item discard."},
            {"locator": "printed pages 21–23 / lines 4150–4157,4243–4395", "text": "Reinforced Corridor, Door, Fire, Malfunction, Secure, Closed-Door, and discard-Malfunction procedures."},
            {"locator": "printed pages 28–29 / lines 4849–5103", "text": "Search, regular Item/Backpack, One Use Only, Heavy, Duct Tape visible face, Interplay, and Trade rules."},
            {"locator": "printed page 37 / lines 5982–6041", "text": "Robot Activation, slots, Malfunction, and effect context."},
        ],
        "faqSearchClosure": {"baseApplicableOccurrences": relevant_faq, "excludedExpansionOccurrences": excluded_faq},
        "exclusions": {
            "otherColorDecks": [{"role": "greenItemsDeck", "guid": "17400d"}, {"role": "redItemsDeck", "guid": "9027ed"}],
            "heavyEquipmentStarting": {"startItemDeckRole": "startItemDeck", "startItemDeckGuid": "f71196", "rootClassConflictOccurrenceIds": [row["yellowItemOccurrenceId"] for row in class_conflict_faces]},
            "tacticalGear": "Oxygen Tactical Gear tokens, Robot slots, Fire/Malfunction/Secure/Door components, and utility/system artwork are not Yellow Item card faces.",
            "parentBackGaps": {"parentSheets": [YELLOW_ITEM_SHEET_33_PATH, YELLOW_ITEM_SHEET_34_PATH], "backs": [YELLOW_ITEM_SHARED_BACK_PATH, YELLOW_ITEM_UNIQUE_BACK_SHEET_PATH], "selectorGapCells": {"33": [0, 2, 3], "34": [1, 2]}},
            "other": "Starting/Equipment/Heavy cards outside exact root selectors, expansion/prototype decks, Tactical Gear/tokens, overlays, placeholders, duplicate references, parent sheets, backs, and non-rules cells never enter the 24 regular-face count.",
        },
        "fidelityBoundaries": {
            "rootVersusFamily": "All 30 exact root children remain indexed. Only 24 source-clear regular occurrences dispatch here; six Fire Extinguisher/Robot Controller class-conflict occurrences remain excluded from regular/Backpack effect semantics.",
            "classBoundary": "Five exact root Fire Extinguisher selectors are portrait ONE USE ONLY. SPECIAL WEAPON faces and one exact Robot Controller selector is portrait with no HEAVY line; licensed same-title rows classify all six as Heavy. No title or aggregate default is adopted under SEM-Q-052.",
            "backBoundary": "Twenty-five root children use one shared Yellow Item back. Five Fire Extinguisher children use cell 1 of a 2x2 UniqueBack sheet also used at cell 0 by six Red-root Military Tasers. Back color/cell never assigns family, class, or effect identity.",
            "glyphBoundary": "Sixteen regular physical upper-right occurrences retain explicit all-glossary no-matches under SEM-Q-051. A separate canonical Oxygen-gap or direct Robot Not In Combat match creates no position/color/title-wide alias.",
            "variantBoundary": "Five unselected sheet cells, all six licensed rows, current official Duct Tape, and every scan/current wording/icon/class difference remain independent. No selector gap is repaired from title, body, art, source cell, BGA key, or expected game logic.",
            "officialBoundary": "Official rules control count, class definitions, storage/use, Oxygen/Reinforce/Door/Malfunction procedures, FAQ Duct Tape stacking, and exact publisher occurrences only. No checked official visual identifies a TTS GUID copy or an exact Yellow back.",
        },
    }


def yellow_item_source_registry_rows(source_index: dict) -> list[dict]:
    rows = [{
        "sourceId": YELLOW_ITEM_ROOT_SOURCE_ID,
        "authority": "source-bound-component-scan",
        "version": "TTS raw base yellowItemsDeck root / GUID fe68f3",
        "path": RAW_SAVE_PATH,
        "sha256": source_index["rootDeckEvidence"]["rawSaveSha256"],
        "occurrenceId": "TTS-YELLOW-ITEM-ROOT-DECK",
        "evidenceIndexPath": "docs/rules/semantics/yellow-item-source-index.json",
        "evidenceRecord": "rootDeckEvidence",
        "provenanceIndexPath": "assets/tts-mod/extract/v2/lua_roles.json",
    }]
    for face in [*source_index["faces"], *source_index["physicalClassConflictFaces"]]:
        rows.append({"sourceId": face["sourceId"], "authority": face["sourceAuthority"], "version": face["sourceVersion"], "path": face["sourcePath"], "sha256": face["sourceSha256"], "occurrenceId": face["yellowItemOccurrenceId"], "evidenceIndexPath": face["corpusEvidencePath"], "evidenceRecord": face["sourceSha256"], "provenanceIndexPath": face["provenanceEvidencePath"]})
    for sheet in source_index["sourceSheets"]:
        rows.append({"sourceId": sheet["sourceId"], "authority": sheet["sourceAuthority"], "version": sheet["sourceVersion"], "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"], "evidenceIndexPath": VISION_PROGRESS_PATH, "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for back in source_index["rootBacks"]:
        rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for asset in source_index["sourceFaceAssets"]:
        if not asset["sourceId"]:
            continue
        rows.append({"sourceId": asset["sourceId"], "authority": "source-bound-component-scan", "version": f"TTS Yellow source-sheet selector-gap occurrence / CustomDeck {asset['sourceSheet']} / cell {asset['generatedCell']}", "path": asset["sourcePath"], "sha256": asset["sourceSha256"], "occurrenceId": f"TTS-YELLOW-ITEM-GAP-{asset['sourceSheet']}-CELL-{asset['generatedCell']:02d}", "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": asset["sourceSha256"], "provenanceIndexPath": VISION_PROGRESS_PATH})
    repo = Path(__file__).resolve().parents[1]
    rows.append({"sourceId": BGA_YELLOW_ITEM_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / ITEMS_DATA deck-yellow rows", "path": BGA_ITEMS_PATH, "sha256": _sha(repo / BGA_ITEMS_PATH), "occurrenceId": "ITEMS_DATA:deck-yellow", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "ITEMS_DATA"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None, visibility: str = "public") -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": visibility}


def build_yellow_item_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo
    records = []
    face_by_occurrence = {row["yellowItemOccurrenceId"]: row for row in source_index["faces"]}

    records.append(record(
        "SEM-YELLOW-ITEM-DECK-001", "Finite Yellow Item root and source-clear regular-family boundary", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [
            assertion("SA-YI-DECK-RB", "SRC-RULEBOOK", "unprinted page 3; printed pages 9 and 28 / RB-P03-V01, RB-P09-V01, RB-P28-V02 / lines 520–521,2593–2600,4849–4865", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "The official Yellow Item type has 30 cards. Shuffle its deck separately face down, draw by Yellow Item icons, and return unchosen Search cards privately to the Yellow deck bottom.", "docs/rules/semantics/yellow-item-source-index.json:familyCountEvidence"),
            assertion("SA-YI-DECK-TTS", YELLOW_ITEM_ROOT_SOURCE_ID, "raw root GUID fe68f3 / exact ordered DeckIDs and 30 contained full CardID/GUID selectors", ["informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "sourceVariants", "unresolvedQuestionRefs"], "The exact root contains 30 physical children: 24 source-clear regular occurrences and six portrait physical-class-conflict occurrences under SEM-Q-052.", "docs/rules/semantics/yellow-item-source-index.json:rootDeckEvidence"),
        ],
        ["term.item", "term.regular-item", "icon.yellowItem"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-YI-DECK", "tax.entity.component.card.item", "when-triggered", "once-at-setup-plus-per-source-requested-Yellow-draw/return/discard"), [participant("P-RULES", "rules-system"), participant("P-DRAWING-CHARACTER", "affected", "tax.entity.agent.character")], "must", [], [],
        [{"informationId": "I-YI-DECK", "subjectRef": "30 exact root cards, two back forms, 24 source-clear regular faces, six class-conflict faces, shuffled order, and remaining fronts", "audience": "hidden-from-all fronts/order; public deck/back/count/discard locations", "revealTrigger": "owner-private Search inspection, gain, or source-defined use", "secrecy": "no client, log, accessibility output, or spectator may expose unselected fronts/order"}], [],
        [_target("T-YI-DECK-CARD", ["tax.entity.component.card.item"], mode="random", minimum=0, maximum=1)],
        [
            operation("S01", 1, "shuffle", "must", "P-RULES", "all 30 exact Yellow-root physical children without changing their BackURL/UniqueBack or physical-class evidence", ["SA-YI-DECK-RB", "SA-YI-DECK-TTS"], repeat={"rootPhysicalCardCount": 30, "regularBatchFaceCount": 24, "explicitHeavyCount": 0, "physicalClassConflictCount": 6}),
            operation("S02", 2, "transition-zone", "must", "P-RULES", "shuffled Yellow root face down", ["SA-YI-DECK-RB"], transition={"from": "tax.scaffold.supply-pool", "to": "tax.scaffold.zone.deck"}),
            operation("S03", 3, "set-state", "must", "P-RULES", "separate empty Yellow Item discard pile", ["SA-YI-DECK-RB"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "whether a requested Yellow draw has a remaining physical card", ["SA-YI-DECK-RB", "SA-YI-DECK-TTS"], target_ref="T-YI-DECK-CARD"),
            operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-040 color-deck exhaustion/recycle and multi-draw shortage handling", ["SA-YI-DECK-RB", "SA-YI-DECK-TTS"], conditions=["a Yellow draw is requested with insufficient cards"], target_ref="T-YI-DECK-CARD"),
            operation("S06", 6, "draw-random", "if-able", "P-RULES", "one exact physical Yellow-root card into the caller's source-defined private candidate/gain zone", ["SA-YI-DECK-RB", "SA-YI-DECK-TTS"], conditions=["a physical card remains"], target_ref="T-YI-DECK-CARD"),
            operation("S07", 7, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-052 physical class/storage/effect handling only if the drawn exact occurrence is one of six conflict selectors", ["SA-YI-DECK-RB", "SA-YI-DECK-TTS"], conditions=["drawn occurrence is a Fire Extinguisher or Robot Controller class-conflict face"]),
            operation("S08", 8, "evaluate-condition", "must", "P-RULES", "unchosen Search cards return to Yellow deck bottom; Used/voluntarily discarded Items enter the separate Item discard pile", ["SA-YI-DECK-RB"]),
        ],
        {"policy": "source-limited-components", "unit": "one requested physical Yellow draw or exact lifecycle transition", "onImpossible": "SEM-Q-040 prohibits invented reshuffles/shortage assignment; SEM-Q-052 prohibits selecting class/storage/effect identity from title, Yellow color, utility art, or aggregate evidence"},
        {"kind": "persistent-finite-deck-and-discard-state"}, {"policy": "one finite 30-card root; only 24 source-clear regular occurrences dispatch here; no title/licensed-row dispatch"}, [], ["SEM-Q-040", "SEM-Q-052"], []))

    records.append(record(
        "SEM-YELLOW-ITEM-ONE-USE-001", "One Use Only lifecycle for source-clear regular Yellow Items", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-YI-ONE-USE-RB", "SRC-RULEBOOK", "printed page 29 / lines 4933–4951", ["timing", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "One Use Only Items are discarded when Used.", "docs/rulebooks/rulebook_text.txt:lines 4933–4951"), *[assertion(f"SA-YI-ONE-USE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['yellowItemOccurrenceId']} / exact printed trait", ["timing", "operations", "duration", "stacking", "unresolvedQuestionRefs"], face["typeLine"], f"docs/rules/semantics/yellow-item-source-index.json:{face['yellowItemOccurrenceId']}.typeLine") for face in source_index["faces"]]],
        ["term.item", "term.regular-item"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-YI-ONE-USE", "tax.entity.component.card.item.regular", "when-triggered", "once-when-one-exact-source-clear-regular-Yellow-Item-is-Used"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-YI-ONE-USE", "subjectRef": "used exact physical Yellow Item, effect, Duct Tape attachment alternative, discard destination, and sibling Backpack cards", "audience": "used Item public; discard face orientation source-unspecified; siblings owner-private", "revealTrigger": "SEM-Q-039", "secrecy": "discarding one copy never reveals or collapses sibling copies"}], [], [_target("T-YI-ONE-USE", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1)],
        [
            operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-039 exact One Use Only transition point", ["SA-YI-ONE-USE-RB"], target_ref="T-YI-ONE-USE"),
            operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-053 exact TTS Duct Tape self-placement versus current official effect and generic One Use discard", ["SA-YI-ONE-USE-RB"], conditions=["used exact occurrence is Duct Tape"], target_ref="T-YI-ONE-USE"),
            operation("S03", 3, "transition-zone", "must", "P-RULES", "used exact regular Yellow Item", ["SA-YI-ONE-USE-RB"], conditions=["source-defined discard point under SEM-Q-039 is reached", "for Duct Tape, SEM-Q-053 selects a disposition that discards this card"], target_ref="T-YI-ONE-USE", transition={"from": "owned Backpack or card-in-resolution/attachment zone", "to": "tax.scaffold.zone.discard-pile"}),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "discarded copy cannot be Used again absent an explicit future return; no checked Yellow rule returns or reshuffles it", ["SA-YI-ONE-USE-RB"]),
        ],
        {"policy": "ordered-complete", "unit": "one exact used regular Yellow Item", "onImpossible": "do not remove from game, return, reshuffle, destroy, attach, or discard a different copy; relative timing remains SEM-Q-039 and Duct Tape disposition remains SEM-Q-053"}, {"kind": "instantaneous-transition-ending-that-copy's-availability-or-unresolved-Duct-attachment"}, {"policy": "one physical copy per use; same-title copies remain distinct"}, [], ["SEM-Q-039", "SEM-Q-053"], []))

    immediate_faces = [face for face in source_index["faces"] if face["sourceAssetKey"] == "direct-oxygen"]
    immediate_assertions = [assertion(f"SA-YI-IMMEDIATE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['yellowItemOccurrenceId']} / printed immediate-use sentence", ["timing", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "You can use this Item for free\nimmediately after gaining it.", f"docs/rules/semantics/yellow-item-source-index.json:{face['yellowItemOccurrenceId']}.sentences") for face in immediate_faces]
    records.append(record(
        "SEM-YELLOW-ITEM-IMMEDIATE-USE-001", "Optional free immediate use of exact regular Oxygen Tank occurrences", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [*immediate_assertions, assertion("SA-YI-IMMEDIATE-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U04", ["timing", "operations", "duration", "unresolvedQuestionRefs"], "A traded Item is gained and may be used immediately when its exact text permits.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U04")],
        ["term.item", "term.regular-item"], ["tax.entity.component.card.item.regular"], ["NI-0348"],
        timing("TW-YI-IMMEDIATE", "tax.entity.component.card.item.regular", "immediately-after-gain", "once-per-gain-of-one-of-eight-exact-physical-occurrences"), [participant("P-RECIPIENT", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "may", [],
        [decision("D-YI-IMMEDIATE", "P-OWNER", "player-choice", 0, 1, True, "public-on-use", ["use this exact gained Item immediately for free", "decline and retain it in the Backpack"])],
        [{"informationId": "I-YI-IMMEDIATE", "subjectRef": "gained exact Oxygen Tank occurrence, immediate choice, branch/target, and sibling gained Items", "audience": "owner-private until use; public on use", "revealTrigger": "exercise immediate window", "secrecy": "declining does not reveal a retained card beyond source-authorized gain/Trade visibility"}], [],
        [_target("T-YI-IMMEDIATE-ITEM", ["tax.entity.component.card.item.regular"], selector="P-OWNER", mode="deterministic-exact-face-filter", minimum=1, maximum=1, visibility="owner-private-until-use")],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "gained physical occurrence is one of the eight exact direct Oxygen Tank selectors", [row["assertionId"] for row in immediate_assertions], target_ref="T-YI-IMMEDIATE-ITEM"),
            operation("S02", 2, "choose", "may", "P-OWNER", "exercise or decline this exact immediate window", [*[row["assertionId"] for row in immediate_assertions], "SA-YI-IMMEDIATE-FAQ"], decision_ref="D-YI-IMMEDIATE", target_ref="T-YI-IMMEDIATE-ITEM"),
            operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-045 order when one gain/Trade produces multiple immediate windows", [*[row["assertionId"] for row in immediate_assertions], "SA-YI-IMMEDIATE-FAQ"], conditions=["multiple immediate-use windows arise"]),
            operation("S04", 4, "invoke-process", "may", "P-RECIPIENT", "Use the exact Item with ordinary one-Action-card cost waived only for this immediate window", [row["assertionId"] for row in immediate_assertions], conditions=["owner exercises this window under SEM-Q-045"], decision_ref="D-YI-IMMEDIATE", target_ref="T-YI-IMMEDIATE-ITEM", invoke="SEM-USE-ITEM-001", notes="Printed immediate timing is not a Reaction; ordinary restrictions, branch legality, visibility, and One Use Only lifecycle still apply."),
        ],
        {"policy": "one-optional-window-per-exact-gain", "unit": "one gained exact physical occurrence", "onImpossible": "declining is legal; free permission expires after the window; SEM-Q-045 prohibits merged/automatic ordering"}, {"kind": "instantaneous-optional-followup-window"}, {"policy": "each physical copy grants at most one window for that gain"}, [], ["SEM-Q-045"], []))

    records.append(record(
        "SEM-GAIN-OXYGEN-001", "Gain a source-instructed amount of Oxygen up to 7", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-YI-OXYGEN-RB", "SRC-RULEBOOK", "printed page 17 / RB-P17-V01/RB-P17-V02 / lines 3633–3638", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "An Oxygen token gains 3 Oxygen, and a Character's Oxygen supply can never exceed 7.", "docs/rulebooks/rulebook_text.txt:lines 3633–3638")],
        ["icon.oxygen"], ["tax.entity.agent.character", "tax.value.resource.oxygen"], [],
        timing("TW-YI-OXYGEN-GAIN", "tax.value.resource.oxygen", "when-triggered", "per-source-instructed-Oxygen-gain"), [participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-YI-OXYGEN-GAIN", "subjectRef": "affected Character, prior Oxygen, requested gain, capped result, and Oxygen dial", "audience": "public", "revealTrigger": "gain resolution", "secrecy": "none"}], [], [_target("T-YI-OXYGEN-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1), _target("T-YI-OXYGEN-VALUE", ["tax.value.resource.oxygen"], minimum=1, maximum=1)],
        [operation("S01", 1, "change-value", "must", "P-RULES", "affected Character Oxygen increases by the requested amount without exceeding 7", ["SA-YI-OXYGEN-RB"], target_ref="T-YI-OXYGEN-VALUE", value_change={"amount": "min(source-requested amount, 7 minus current Oxygen)", "valueTaxonId": "tax.value.resource.oxygen"}), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "Oxygen remains within 0 through 7 and excess requested gain is not carried elsewhere", ["SA-YI-OXYGEN-RB"])],
        {"policy": "up-to-source-maximum", "unit": "one source-instructed Oxygen gain", "onImpossible": "gain only the amount that fits before 7; do not create overflow or another resource"}, {"kind": "instantaneous-resource-change"}, {"policy": "multiple gains apply independently against current Oxygen"}, [], [], []))

    records.append(record(
        "SEM-OXYGEN-TOKEN-EFFECT-001", "Oxygen Tactical Gear token effect", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-YI-OXYGEN-TOKEN-RB", "SRC-RULEBOOK", "printed pages 16–17 / RB-P16-V02, RB-P17-V01 / lines 3469–3490,3633–3638", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "When an Oxygen token is used, its Character gains 3 Oxygen; Use Any Tactical Gear resolves selected non-Ammo token effects before returning those tokens to their finite pools.", "docs/rulebooks/rulebook_text.txt:lines 3469–3490,3633–3638")],
        ["icon.oxygenToken", "icon.oxygen", "term.tactical-gear-token"], ["tax.entity.component.token.tactical-gear.oxygen", "tax.value.resource.oxygen"], [],
        timing("TW-YI-OXYGEN-TOKEN", "tax.entity.component.token.tactical-gear.oxygen", "when-triggered", "per-selected-Oxygen-token-use"), [participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-YI-OXYGEN-TOKEN", "subjectRef": "selected physical Oxygen token, source slot, affected Character, Oxygen gain, and caller-owned discard transition", "audience": "public", "revealTrigger": "token use", "secrecy": "none"}], [], [_target("T-YI-OXYGEN-TOKEN", ["tax.entity.component.token.tactical-gear.oxygen"], minimum=1, maximum=1), _target("T-YI-OXYGEN-TOKEN-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1)],
        [operation("S01", 1, "invoke-process", "must", "P-CHARACTER", "gain 3 Oxygen through the capped reusable procedure", ["SA-YI-OXYGEN-TOKEN-RB"], target_ref="T-YI-OXYGEN-TOKEN-CHARACTER", invoke="SEM-GAIN-OXYGEN-001", repeat={"requestedOxygen": 3}), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "the enclosing Use Any Tactical Gear Action returns this used non-Ammo token to its finite pool exactly once after its effect", ["SA-YI-OXYGEN-TOKEN-RB"], target_ref="T-YI-OXYGEN-TOKEN")],
        {"policy": "ordered-complete", "unit": "one physical Oxygen token use", "onImpossible": "effect gains only up to Oxygen 7; token lifecycle remains owned by the enclosing Tactical Gear use and is not duplicated here"}, {"kind": "instantaneous-tactical-gear-effect"}, {"policy": "each selected physical token resolves separately"}, [], [], []))

    records.append(record(
        "SEM-DISCARD-MALFUNCTION-001", "Discard one local Malfunction marker", "source-backed", "procedure", "official-errata", "source-composed",
        [assertion("SA-YI-DISCARD-MALFUNCTION-RB", "SRC-RULEBOOK", "printed pages 17,22,29 / lines 3537–3542,4392–4395,5079–5096", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "A local discard-Malfunction effect may remove one marker from the current Room or an Item/Robot there; using it on another Character's Item requires co-location and consent under Interplay.", "docs/rulebooks/rulebook_text.txt:lines 3537–3542,4392–4395,5079–5096"), assertion("SA-YI-DISCARD-MALFUNCTION-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U07", ["preconditions", "decisions", "targets", "operations", "partialResolution"], "Interplay applies to Item Actions when the receiving Character consents and the effect belongs to a printed Interplay class.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U07")],
        ["icon.malfunction", "term.item"], ["tax.entity.component.marker.malfunction", "tax.entity.spatial.room", "tax.entity.component.card.item", "tax.entity.agent.robot"], [],
        timing("TW-YI-DISCARD-MALFUNCTION", "tax.entity.component.marker.malfunction", "when-triggered", "per-source-instructed-discard"), [participant("P-USING-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-USING-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RECEIVER-OWNER", "conditional-consent-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must",
        [condition("C-YI-DISCARD-MALFUNCTION", "predicate", [{"predicate": "target Malfunction is on the using Character's Room, an Item in that Room, or the Robot in that Room"}], ["SA-YI-DISCARD-MALFUNCTION-RB"])],
        [decision("D-YI-DISCARD-MALFUNCTION-TARGET", "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["each source-legal local Malfunction marker"]), decision("D-YI-DISCARD-MALFUNCTION-CONSENT", "P-RECEIVER-OWNER", "consent", 0, 1, True, "public-on-response", ["allow removal from own Item", "decline"])],
        [{"informationId": "I-YI-DISCARD-MALFUNCTION", "subjectRef": "eligible local markers, selected host, consent when another Character owns that host Item, and returned marker", "audience": "public", "revealTrigger": "declaration/resolution", "secrecy": "no private Item face is exposed beyond source-authorized use/Interplay"}], [], [_target("T-YI-DISCARD-MALFUNCTION", ["tax.entity.component.marker.malfunction"], selector="P-USING-PLAYER", mode="player-choice-with-consent", minimum=1, maximum=1)],
        [operation("S01", 1, "select-target", "must", "P-USING-PLAYER", "one source-legal local Malfunction marker", ["SA-YI-DISCARD-MALFUNCTION-RB", "SA-YI-DISCARD-MALFUNCTION-FAQ"], decision_ref="D-YI-DISCARD-MALFUNCTION-TARGET", target_ref="T-YI-DISCARD-MALFUNCTION"), operation("S02", 2, "evaluate-condition", "must", "P-RULES", "another Character's Item owner consents when that Item hosts the marker", ["SA-YI-DISCARD-MALFUNCTION-RB", "SA-YI-DISCARD-MALFUNCTION-FAQ"], conditions=["selected marker is on another Character's Item"], decision_ref="D-YI-DISCARD-MALFUNCTION-CONSENT"), operation("S03", 3, "transition-zone", "must", "P-RULES", "selected Malfunction marker back to its finite supply", ["SA-YI-DISCARD-MALFUNCTION-RB"], conditions=["target is legal and any required consent is granted"], decision_ref="D-YI-DISCARD-MALFUNCTION-TARGET", target_ref="T-YI-DISCARD-MALFUNCTION", transition={"from": "selected Room/Item/Robot", "to": "tax.scaffold.supply-pool"})],
        {"policy": "all-or-nothing-selection", "unit": "one selected local Malfunction marker", "onImpossible": "without an eligible marker or required consent the caller branch is not legal; never remove another marker"}, {"kind": "instantaneous-marker-removal"}, {"policy": "one physical marker per invocation"}, [], [], []))

    records.append(record(
        "SEM-REINFORCE-CORRIDOR-001", "Reinforce one source-selected Empty Corridor", "source-backed", "procedure", "official-errata", "source-composed",
        [assertion("SA-YI-REINFORCE-RB", "SRC-RULEBOOK", "printed pages 17,21–22 / RB-P21-V01 / lines 3537–3548,4150–4157,4243–4268", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "An Empty Corridor may be Reinforced: discard its Noise marker if present, then flip it to the value-0 Reinforced side. Hibernatorium Corridors cannot be Reinforced; Closed Doors block effects across them.", "docs/rulebooks/rulebook_text.txt:lines 4150–4157,4243–4268"), assertion("SA-YI-REINFORCE-FAQ", "SRC-FAQ", "General rules / FQ-P02-U10", ["preconditions", "operations", "partialResolution"], "A Corridor cannot be Reinforced through a Closed Door.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10")],
        ["term.empty-corridor", "term.reinforced-corridor", "term.closed"], ["tax.entity.spatial.corridor", "tax.state.corridor.empty", "tax.state.corridor.reinforced", "tax.entity.spatial.door", "tax.state.closed"], [],
        timing("TW-YI-REINFORCE", "tax.state.corridor.reinforced", "when-triggered", "per-source-selected-Corridor"), [participant("P-CALLER", "target-owner-supplied-by-calling-effect"), participant("P-RULES", "rules-system")], "must",
        [condition("C-YI-REINFORCE", "all", [{"predicate": "selected Corridor is Empty"}, {"predicate": "selected Corridor is not a Hibernatorium Corridor"}, {"predicate": "no Closed Door blocks the caller's effect"}], ["SA-YI-REINFORCE-RB", "SA-YI-REINFORCE-FAQ"])], [],
        [{"informationId": "I-YI-REINFORCE", "subjectRef": "selected Corridor, Empty/Reinforced state, Noise marker, and Door path", "audience": "public", "revealTrigger": "target declaration/resolution", "secrecy": "none"}], [], [_target("T-YI-REINFORCE-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-CALLER", mode="deterministic-state-filter", minimum=1, maximum=1)],
        [operation("S01", 1, "remove-component", "if-able", "P-RULES", "Noise marker from the selected Empty Corridor", ["SA-YI-REINFORCE-RB"], conditions=["selected Corridor contains a Noise marker"], target_ref="T-YI-REINFORCE-CORRIDOR", transition={"from": "selected Corridor", "to": "tax.scaffold.supply-pool"}), operation("S02", 2, "set-state", "must", "P-RULES", "selected Corridor flips to its value-0 Reinforced side", ["SA-YI-REINFORCE-RB"], target_ref="T-YI-REINFORCE-CORRIDOR")],
        {"policy": "ordered-complete", "unit": "one source-selected legal Empty Corridor", "onImpossible": "caller must supply a legal target; no target owner, adjacency, or allocation rule is invented by this reusable procedure"}, {"kind": "persistent-until-source-defined-unreinforce"}, {"policy": "one physical Corridor side/state at a time"}, [], [], []))

    gap_assets = [row for row in source_index["sourceFaceAssets"] if row["selectorGap"] is not None]
    class_conflict_faces = source_index["physicalClassConflictFaces"]
    bga_rows = source_index["licensedDigitalOccurrences"]
    variant_assertions = []
    variant_operations = []
    variant_refs = []
    for asset in gap_assets:
        assertion_id = f"SA-YI-VARIANT-GAP-{asset['sourceSheet']}-{asset['generatedCell']:02d}"
        item = assertion(assertion_id, asset["sourceId"], f"CustomDeck {asset['sourceSheet']} / generated cell {asset['generatedCell']} / explicit Yellow-root selector gap", ["operations", "sourceVariants"], asset["printedBody"] or "Non-rules/blank generated cell.", f"docs/rules/semantics/yellow-item-source-index.json:sourceFaceAssets.{asset['assetKey']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve unselected CustomDeck {asset['sourceSheet']} cell {asset['generatedCell']} exactly; never dispatch it as a physical regular Yellow face", [assertion_id]))
        variant_refs.append({"variantId": f"SV-YI-GAP-{asset['sourceSheet']}-{asset['generatedCell']:02d}", "sourceId": asset["sourceId"], "sourceAssertionId": assertion_id, "difference": f"Generated cell prints title {asset['printedTitle']!r}, body {asset['printedBody']!r}, and literal icon evidence but has no Yellow-root full CardID/GUID selector; disposition={asset['selectedDisposition']!r}.", "resolution": "Retain independently; title, Yellow color, body, utility art, cell, folder, or CardID modulo cannot repair the gap or cross-family boundary."})
    for face in class_conflict_faces:
        assertion_id = f"SA-YI-VARIANT-CONFLICT-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}"
        item = assertion(assertion_id, face["sourceId"], f"{face['yellowItemOccurrenceId']} / exact root selector and physical-class evidence", ["operations", "sourceVariants", "unresolvedQuestionRefs"], face["printedBody"], f"docs/rules/semantics/yellow-item-source-index.json:{face['yellowItemOccurrenceId']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"retain excluded root occurrence {face['yellowItemOccurrenceId']} and never dispatch it as one of 24 source-clear regular Yellow faces", [assertion_id]))
        variant_refs.append({"variantId": f"SV-YI-CONFLICT-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", "sourceId": face["sourceId"], "sourceAssertionId": assertion_id, "difference": f"Exact TTS root child class evidence is {face['physicalClass']!r}; licensed same-title occurrence is Heavy.", "resolution": "Preserve root membership and exact scan. Class/current correspondence remains SEM-Q-052; title, body, back color, and aggregate 24/6 supply no default."})
    bga_assertion_id = "SA-YI-VARIANT-BGA"
    bga_assertion = assertion(bga_assertion_id, BGA_YELLOW_ITEM_SOURCE_ID, "ITEMS_DATA / all six deck-yellow rows in source order", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "\n".join(row["sourceBlockText"] for row in bga_rows), "docs/rules/semantics/yellow-item-source-index.json:licensedDigitalOccurrences")
    bga_assertion["textKind"] = "verbatim"
    variant_assertions.append(bga_assertion)
    for row in bga_rows:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve licensed ITEMS_DATA.{row['key']} independently: name={row['name']!r}, nbr={row['nbr']}, heavy={row['heavy']}, noIntruders={row['noIntruders']}, effectDesc={row['effectDesc']!r}", [bga_assertion_id]))
        variant_refs.append({"variantId": f"SV-YI-BGA-{row['key'].upper()}", "sourceId": BGA_YELLOW_ITEM_SOURCE_ID, "sourceAssertionId": bga_assertion_id, "difference": f"Licensed row {row['key']} has an independent title/class/multiplicity/restriction/body tuple with no TTS/official physical selector.", "resolution": "Retain below official/source-bound authority. Aggregate 30/24/6 reconciliation is not a copy, title, body, or ordinal crosswalk."})
    official_assertion_id = "SA-YI-VARIANT-OFFICIAL-DUCT"
    official_assertion = assertion(official_assertion_id, "SRC-RULEBOOK", "printed page 28 / RB-P28-V03 current Duct Tape occurrence", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "DUCT TAPE / ONE USE ONLY / Discard a source glyph. OR Place 1 Heavy Item above another Heavy Item in your Hand slot (effectively carrying 2 Heavy Items in 1 Hand).", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P28-V03")
    variant_assertions.append(official_assertion)
    variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", "preserve current official Duct Tape face and FAQ third-Item ruling independently from five TTS GUID copies", [official_assertion_id]))
    variant_refs.append({"variantId": "SV-YI-OFFICIAL-DUCT-TAPE", "sourceId": "SRC-RULEBOOK", "sourceAssertionId": official_assertion_id, "difference": "Current official face says place one Heavy Item above another and does not print TTS 'this Item ... under' wording; FAQ permits a third Item in one Hand. No publisher occurrence identifies a TTS GUID copy.", "resolution": "Official/FAQ occurrence controls only its exact current source. Preserve TTS physical copies independently under SEM-Q-053/054; never pair by title."})
    records.append(record(
        "SEM-YELLOW-ITEM-VARIANT-BOUNDARIES-001", "Yellow root, class, back, selector-gap, official, and licensed boundaries", "source-variant", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-YI-VARIANT-RB", "SRC-RULEBOOK", "unprinted page 3 and printed pages 28–29 / counts, classes, backs, Duct Tape, and current rules", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "Official inventory has 30 per Item type; regular/Heavy classes use physical format/trait rules; page 28 shows current Duct Tape but identifies no TTS GUID copy.", "docs/rules/semantics/yellow-item-source-index.json:familyCountEvidence"), *variant_assertions],
        ["term.item", "term.regular-item", "term.backpack", "term.heavy-item"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.component.card.item.heavy"], [],
        timing("TW-YI-VARIANTS", "tax.entity.component.card.item", "when-triggered", "per-source-comparison-or-canonicalization-attempt"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-YI-VARIANTS", "subjectRef": "24 regular physical faces, six class conflicts, five selector gaps, two back forms, six licensed rows, official Duct Tape, and wording/icon/class differences", "audience": "public source evidence", "revealTrigger": "source audit", "secrecy": "does not expose live shuffled order or private Backpack"}], [], [],
        [*variant_operations, operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", "affected deck/face records own SEM-Q-051–056 without turning this source ledger into a default", ["SA-YI-VARIANT-RB", *[row["assertionId"] for row in variant_assertions]]), operation(f"S{len(variant_operations)+2:02d}", len(variant_operations)+2, "evaluate-condition", "must", "P-RULES", "no title, Yellow color, utility/repair/system art, body, folder, order, generated cell, CardID modulo, licensed key, multiplicity, or expected logic establishes identity/effect equivalence", ["SA-YI-VARIANT-RB", *[row["assertionId"] for row in variant_assertions]])],
        {"policy": "per-proposed-source-merge", "unit": "one proposed Yellow/class/back/gap/licensed/official identity or effect merge", "onImpossible": "without exact source-backed correspondence, preserve independent occurrences/conflicts and no-default questions"}, {"kind": "persistent-source-audit-boundary"}, {"policy": "source variants do not dispatch, stack, replace, or identify one another from resemblance"}, [], [], variant_refs))

    def build_face(definition: dict) -> dict:
        source = face_by_occurrence[definition["occurrenceId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        scan_id = f"SA-YIF-{code}-SCAN"
        general_id = f"SA-YIF-{code}-GENERAL"
        scan = assertion(scan_id, source["sourceId"], f"{source['yellowItemOccurrenceId']} / exact selector, regions, panels, title, trait, punctuation, sentences, and icons", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/yellow-item-source-index.json:{source['yellowItemOccurrenceId']}")
        scan["textKind"] = "verbatim"
        general = assertion(general_id, "SRC-RULEBOOK", "printed pages 17,21–23,28–29 / whole-effect, Item use, Backpack, One Use, Oxygen, Reinforce, Door, Malfunction, Interplay", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "This exact source-clear regular Item stays owner-private until selected, resolves only through a legal Use/immediate window, applies official local/whole/component limits and reusable procedures, and uses the separate One Use Only lifecycle.", "docs/rules/semantics/yellow-item-source-index.json:officialRulebookTextOccurrences")
        terms = ["term.item", "term.regular-item"]
        taxa = ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.agent.character"]
        named = [source["namedIdentityRef"]] if source.get("namedIdentityRef") else []
        for icon in source["iconOccurrences"]:
            if icon.get("semanticReferenceId"):
                terms.append(icon["semanticReferenceId"])
        participants = [participant("P-USING-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-USING-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")]
        decisions = []
        targets = [_target(f"T-YIF-{code}-ITEM", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1), _target(f"T-YIF-{code}-CHARACTER", ["tax.entity.agent.character"], selector="P-USING-PLAYER", mode="player-choice-with-consent", minimum=1, maximum=1)]
        ops = []

        def add(sentence_sequence: int, op_type: str, modality: str, subject: str, obj: str, *, sources=None, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
            sequence = len(ops) + 1
            sentence = source["sentences"][sentence_sequence - 1]
            op = operation(f"S{sequence:02d}", sequence, op_type, modality, subject, obj, sources or [scan_id, general_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref or f"T-YIF-{code}-CHARACTER", transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence["sentenceId"]
            op["sourceRegionId"] = sentence["regionId"]
            op["sourcePanelId"] = sentence["panelId"]
            ops.append(op)
            return op

        unresolved = []
        kind = source["effectKind"]
        preconditions = [condition(f"C-YIF-{code}-OCCURRENCE", "predicate", [{"predicate": f"exact selected physical occurrence is {source['yellowItemOccurrenceId']}"}], [scan_id, general_id])]
        has_local_upper = any(icon.get("semanticReferenceId") is None and icon.get("cardLocationClass") == "upperRight" for icon in source["iconOccurrences"])
        if has_local_upper:
            unresolved.append("SEM-Q-051")
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-051 exact identity/scope of this selected source-local upper-right crossed glyph; licensed noIntruders and other matched faces do not assign it")

        if kind == "discard-malfunction-or-stack-heavy":
            terms.extend(["icon.malfunction", "term.heavy-item", "term.hand-slot"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.component.card.item.heavy", "tax.entity.component.slot.hand"]); unresolved.extend(["SEM-Q-053", "SEM-Q-054"])
            branch_id = f"D-YIF-{code}-BRANCH"
            stack_id = f"D-YIF-{code}-STACK"
            decisions.append(decision(branch_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["discard one source-legal local Malfunction", "resolve the printed Duct Tape Heavy-Item placement branch under SEM-Q-053/054"]))
            decisions.append(decision(stack_id, "P-USING-PLAYER", "player-choice", 2, 2, False, "public-on-placement", ["one Heavy Item in a Hand slot as anchor", "one other owned Heavy Item to combine under the source-resolved arrangement"]))
            targets.extend([_target(f"T-YIF-{code}-HEAVY-ANCHOR", ["tax.entity.component.card.item.heavy"], selector="P-USING-PLAYER", mode="player-choice", minimum=1, maximum=1), _target(f"T-YIF-{code}-HEAVY-OTHER", ["tax.entity.component.card.item.heavy"], selector="P-USING-PLAYER", mode="player-choice", minimum=1, maximum=1)])
            add(1, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=branch_id)
            add(1, "invoke-process", "must", "P-USING-CHARACTER", "discard one source-legal local Malfunction marker", conditions=["discard-Malfunction branch"], decision_ref=branch_id, invoke="SEM-DISCARD-MALFUNCTION-001")
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-053 TTS self-placement/current official stacking/One Use disposition and confirmed third-Item scope", conditions=["Heavy-Item branch"], decision_ref=stack_id, target_ref=f"T-YIF-{code}-HEAVY-ANCHOR")
            add(2, "set-state", "if-able", "P-RULES", "source-resolved Heavy-Item stacking relation in one Hand slot without collapsing any physical Item", conditions=["Heavy-Item branch", "SEM-Q-053 resolves exact arrangement and Duct Tape disposition"], decision_ref=stack_id, target_ref=f"T-YIF-{code}-HEAVY-ANCHOR", repeat={"confirmedByFaq": "a third Item may occupy the single Hand", "beyondThird": "SEM-Q-054 unresolved"})
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-054 beyond-third cardinality plus discard/loss/Malfunction/Trade/separation lifecycle for stacked physical Items", conditions=["Heavy-Item branch"], decision_ref=stack_id, target_ref=f"T-YIF-{code}-HEAVY-ANCHOR")
        elif kind == "reinforce-or-discard-fire":
            terms.extend(["term.empty-corridor", "term.reinforced-corridor", "icon.fire"]); taxa.extend(["tax.entity.spatial.corridor", "tax.state.corridor.empty", "tax.state.corridor.reinforced", "tax.entity.component.marker.fire"]); unresolved.append("SEM-Q-055")
            branch_id = f"D-YIF-{code}-BRANCH"
            corridor_id = f"D-YIF-{code}-CORRIDOR"
            decisions.append(decision(branch_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["Reinforce 1 empty Corridor", "Discard a Fire marker from the using Character's Room"]))
            decisions.append(decision(corridor_id, "P-RULES", "unresolved", 1, 1, False, "source-unspecified", ["using player selects one local/adjacent eligible Empty Corridor", "another source-defined owner/scope/tie-break"]))
            targets.extend([_target(f"T-YIF-{code}-CORRIDOR", ["tax.entity.spatial.corridor"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=1, maximum=1), _target(f"T-YIF-{code}-FIRE", ["tax.entity.component.marker.fire"], mode="deterministic-state-filter", minimum=1, maximum=1)])
            add(1, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=branch_id)
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-055 Empty Corridor target owner/locality/adjacency/Closed-Door eligibility; licensed adjacent wording supplies no identity default", conditions=["Reinforce branch"], decision_ref=corridor_id, target_ref=f"T-YIF-{code}-CORRIDOR")
            add(1, "invoke-process", "must", "P-RULES", "reinforce the one source-resolved legal Empty Corridor", conditions=["Reinforce branch", "SEM-Q-055 resolves a legal target"], decision_ref=corridor_id, target_ref=f"T-YIF-{code}-CORRIDOR", invoke="SEM-REINFORCE-CORRIDOR-001")
            add(2, "transition-zone", "must", "P-RULES", "Fire marker in the using Character's current Room back to its finite supply", conditions=["discard-Fire branch", "current Room contains Fire"], decision_ref=branch_id, target_ref=f"T-YIF-{code}-FIRE", transition={"from": "using Character's Room", "to": "tax.scaffold.supply-pool"})
        elif kind == "gain-oxygen-or-token":
            terms.extend(["icon.oxygen", "icon.oxygenToken", "term.tactical-gear-token"]); taxa.extend(["tax.value.resource.oxygen", "tax.entity.component.token.tactical-gear.oxygen"]); unresolved.extend(["SEM-Q-044", "SEM-Q-045"])
            branch_id = f"D-YIF-{code}-BRANCH"
            decisions.append(decision(branch_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["gain 3 Oxygen", "gain 1 Oxygen Tactical Gear token"]))
            add(1, "evaluate-condition", "must", "P-RULES", "printed optional immediate-use sentence is delegated to SEM-YELLOW-ITEM-IMMEDIATE-USE-001")
            add(2, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=branch_id)
            add(2, "invoke-process", "must", "P-USING-CHARACTER", "gain 3 Oxygen up to the maximum of 7", conditions=["gain-Oxygen branch"], decision_ref=branch_id, invoke="SEM-GAIN-OXYGEN-001", repeat={"requestedOxygen": 3})
            add(3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-044 whether the unresolved Interplay Gaining class permits this Oxygen-token branch on another consenting Character", conditions=["gain-token branch", "proposed affected Character differs from using Character"], decision_ref=branch_id)
            add(3, "invoke-process", "must", "P-AFFECTED-CHARACTER", "gain 1 finite Oxygen token in an owner-chosen compatible empty slot", conditions=["gain-token branch", "target is source-legal under SEM-Q-044"], decision_ref=branch_id, invoke="SEM-ITM-005", repeat={"tokenType": "oxygen", "quantity": 1})
        elif kind == "discard-malfunction-or-door":
            terms.extend(["icon.malfunction", "term.door", "term.opened", "term.closed"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.spatial.door", "tax.state.opened", "tax.state.closed"]); unresolved.append("SEM-Q-056")
            branch_id = f"D-YIF-{code}-BRANCH"
            door_id = f"D-YIF-{code}-DOOR"
            decisions.append(decision(branch_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["discard one source-legal local Malfunction", "Open or Close 1 Door"]))
            decisions.append(decision(door_id, "P-RULES", "unresolved", 1, 1, False, "source-unspecified", ["using player selects one ordinary local/accessibly reachable Door and Open/Closed state", "another source-defined target/state owner or scope"]))
            targets.append(_target(f"T-YIF-{code}-DOOR", ["tax.entity.spatial.door"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=1, maximum=1))
            add(1, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=branch_id)
            add(1, "invoke-process", "must", "P-USING-CHARACTER", "discard one source-legal local Malfunction marker", conditions=["discard-Malfunction branch"], decision_ref=branch_id, invoke="SEM-DISCARD-MALFUNCTION-001")
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-056 Door target/state owner, local/accessibility range, Closed-Door path, and ordinary Destroyed/no-slot constraints", conditions=["Door branch"], decision_ref=door_id, target_ref=f"T-YIF-{code}-DOOR")
            add(2, "invoke-process", "must", "P-RULES", "set the one source-resolved Door Open or Closed under ordinary Door constraints", conditions=["Door branch", "SEM-Q-056 resolves target/state and legality"], decision_ref=door_id, target_ref=f"T-YIF-{code}-DOOR", invoke="SEM-DOOR-001")
        else:
            raise AssertionError(f"unexpected Yellow Item effect kind: {kind}")

        unresolved = list(dict.fromkeys(unresolved))
        status = "source-backed-with-open-question" if unresolved else "source-backed"
        interpretation = "open-alternatives" if unresolved else "source-composed"
        recurrence = "once-per-exact-physical-Item-use; printed immediate timing delegates to SEM-YELLOW-ITEM-IMMEDIATE-USE-001" if kind == "gain-oxygen-or-token" else "once-per-exact-physical-Item-use"
        duration_kind = "instantaneous-one-use-effect; no Passive or Reaction heading"
        if kind == "discard-malfunction-or-stack-heavy":
            duration_kind += "; Heavy-Item stacking state persists only as resolved under SEM-Q-053/054"
        return record(
            definition["semanticRuleId"], f"Regular Yellow Item physical occurrence {code}", status, "component-effect", "official-primary", interpretation,
            [scan, general], terms, taxa, named, timing(f"TW-YIF-{code}", "tax.entity.component.card.item.regular", "when-triggered", recurrence), participants, "mixed", preconditions, decisions,
            [{"informationId": f"I-YIF-{code}", "subjectRef": "exact physical occurrence, printed title/trait/body/panels/icons, decisions, operations, and result", "audience": "owner-private before use; public selected face/decisions/results at source-defined use point", "revealTrigger": "SEM-USE-ITEM-001 under SEM-Q-039", "secrecy": "sibling Backpack faces and Yellow deck order remain hidden; Duct-stacked Heavy Items remain public as Hand-slot Items"}], [], targets, ops,
            {"policy": "all-or-nothing-selection", "unit": "one exact physical occurrence's printed effect/selected branch", "onImpossible": "generic cost/reveal/One Use lifecycle remains reusable; no glyph, class, target owner, Door/Corridor, Duct stacking/Trade, Interplay, or immediate-window default is invented"},
            {"kind": duration_kind}, {"policy": "each physical copy resolves separately; same title/body/multiplicity creates no identity or stacking key; only Duct Tape creates a source-resolved physical attachment relation"}, [], unresolved, [])

    records.extend(build_face(definition) for definition in REGULAR_PHYSICAL_DEFINITIONS)
    return records


def integrate_yellow_item_shared_records(records: list[dict], source_index: dict, assertion, operation) -> None:
    use = next(row for row in records if row["ruleId"] == "SEM-USE-ITEM-001")
    yellow_assertion_ids = []
    for face in source_index["faces"]:
        assertion_id = f"SA-YI-USE-FACE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}"
        use["sourceAssertions"].append(assertion(assertion_id, face["sourceId"], f"{face['yellowItemOccurrenceId']} / exact physical selector and face", ["preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], face["printedBody"], f"docs/rules/semantics/yellow-item-source-index.json:{face['yellowItemOccurrenceId']}"))
        yellow_assertion_ids.append(assertion_id)
    dispatch = next(op for op in use["operations"] if op.get("stepId") == "S05")
    dispatch.setdefault("dispatchRuleIds", []).extend(YELLOW_ITEM_RULE_IDS)
    dispatch["sourceAssertionIds"].extend(yellow_assertion_ids)
    dispatch["objectRef"] = "exact occurrence-specific source-clear regular Item effect"
    dispatch["notes"] = "Dispatch uses the complete family-specific exact root selector; never title, color, utility/repair/system art, body, folder, order, cell, modulo, licensed key, or multiplicity."
    lifecycle = next(op for op in use["operations"] if op.get("stepId") == "S06")
    lifecycle["operationType"] = "invoke-selected-process"
    lifecycle["objectRef"] = "family-specific One Use Only lifecycle for the selected physical Item"
    lifecycle["invokeRuleId"] = None
    lifecycle.setdefault("dispatchRuleIds", ["SEM-GREEN-ITEM-ONE-USE-001", "SEM-RED-ITEM-ONE-USE-001"])
    lifecycle["dispatchRuleIds"].append("SEM-YELLOW-ITEM-ONE-USE-001")

    trade = next(row for row in records if row["ruleId"] == "SEM-ITEM-TRADE-GAIN-001")
    immediate = next(op for op in trade["operations"] if op.get("operationType") == "invoke-selected-process")
    immediate["operationType"] = "invoke-selected-process"
    immediate["objectRef"] = "exact gained Item's family-specific immediate-use procedure"
    immediate["invokeRuleId"] = None
    immediate.setdefault("dispatchRuleIds", ["SEM-GREEN-ITEM-IMMEDIATE-USE-001", "SEM-RED-ITEM-IMMEDIATE-USE-001"])
    immediate["dispatchRuleIds"].append("SEM-YELLOW-ITEM-IMMEDIATE-USE-001")

    duct_faq = assertion("SA-YI-TRADE-DUCT-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U05", ["decisions", "operations", "partialResolution", "stacking", "unresolvedQuestionRefs"], "Duct Tape may place a third Item in one Hand, but the checked source does not define transfer/separation or later stack lifecycle.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U05")
    trade["sourceAssertions"].append(duct_faq)
    if "SEM-Q-054" not in trade["unresolvedQuestionRefs"]:
        trade["unresolvedQuestionRefs"].append("SEM-Q-054")
    transfer_index = next(index for index, op in enumerate(trade["operations"]) if op.get("operationType") == "transition-zone")
    source_ids = [trade["operations"][transfer_index]["sourceAssertionIds"][0], "SA-YI-TRADE-DUCT-FAQ"]
    trade["preconditions"].append({"conditionId": "C-YI-TRADE-DUCT-STACK", "scope": "operation-guard", "expression": {"operator": "predicate", "args": [{"predicate": "a proposed transferred Item participates in a Duct Tape stack"}]}, "sourceAssertionIds": source_ids})
    trade["operations"].insert(transfer_index, operation("TEMP", 0, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-054 transfer/separation handling when one selected Item participates in a Duct Tape Hand-slot stack", source_ids, conditions=["C-YI-TRADE-DUCT-STACK"]))
    for sequence, op in enumerate(trade["operations"], 1):
        op["sequence"] = sequence
        op["stepId"] = f"S{sequence:02d}"
    trade["partialResolution"]["onImpossible"] = "Unconsented transfers do not occur; SEM-Q-045 prohibits merged immediate windows, and SEM-Q-054 prohibits inventing transfer/separation behavior for a Duct Tape stack"
