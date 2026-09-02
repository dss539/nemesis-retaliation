from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

from semantic_attack_records import _find_guid, _parse_value


BASE_RED_ITEM_DECK_GUID = "9027ed"
RED_ITEM_ROOT_SOURCE_ID = "SRC-RED-ITEM-ROOT-DECK"
RED_ITEM_RED_SHEET_SOURCE_ID = "SRC-RED-ITEM-SHEET-36"
RED_ITEM_RED_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148.jpg"
RED_ITEM_YELLOW_SHEET_SOURCE_ID = "SRC-RED-ITEM-CROSS-FAMILY-SHEET-35"
RED_ITEM_YELLOW_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146.jpg"
RED_ITEM_RED_BACK_SOURCE_ID = "SRC-RED-ITEM-BACK"
RED_ITEM_RED_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-147.jpg"
RED_ITEM_YELLOW_BACK_SOURCE_ID = "SRC-RED-ITEM-CROSS-FAMILY-YELLOW-BACK"
RED_ITEM_YELLOW_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-143.jpg"
BGA_RED_ITEM_SOURCE_ID = "SRC-BGA-RED-ITEMS"
BGA_ITEMS_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
SELECTED_EVIDENCE_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
VISION_PROGRESS_PATH = "assets/tts-mod/extract/vision-progress.json"
LOW_CONFIDENCE_PATH = "assets/tts-mod/extract/low-confidence-review.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"

RED_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235610/413F1511B1E70F81E0F7C17B3F7653DA1631AF3E/"
YELLOW_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235323/E2B2763353C8DD3A6DD329CCEC256500AEF64B8A/"
RED_SHEET_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235531/79667CFE1133A841ED788CF7FD14435143EDF3E9/"
YELLOW_SHEET_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235276/4CE4EE4D61C3E4A34A941AF1D5385A94126FEFB7/"


LOCAL_CROSSED_DEVICE = "[ICON: selected source-local red crossed-device morphology with no authoritative glossary match]"
LOCAL_REMOTE_BADGE = "[ICON: circular red white and black crossed badge]"
LOCAL_RED_TOKEN = "[ICON: red rounded rectangular tile with white upright bulb-shaped inset]"
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
        "bodyPanels": body_panels or ([('effect', printed_body)] if printed_body else []),
        "sentenceTexts": sentence_texts or ([printed_body] if printed_body else []),
        "iconSpecs": icon_specs or [],
        "effectKind": effect_kind,
        "namedIdentityRef": named_identity_ref,
        "rulesTextPresent": rules_text_present,
    }


ASSET_DEFINITIONS = {
    "direct-ammo": _asset(
        "direct-ammo", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-059.png", "direct-regular-face",
        "AMMO MAGAZINE", "You can use this Item for free\nimmediately after gaining it.\n\nGain 1 [ammoToken]",
        custom_deck_ids=["5438"], source_sheet=None, generated_cell=None, physical_class="regular-item", selected_disposition="included-regular",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON",
        body_panels=[("immediate-use-timing-note", "You can use this Item for free\nimmediately after gaining it."), ("gain-ammo-effect", "Gain 1 [ammoToken]")],
        sentence_texts=["You can use this Item for free\nimmediately after gaining it.", "Gain 1 [ammoToken]"],
        icon_specs=[("body", "[ammoToken]", "icon.ammoToken", "selected-verified", 0)],
        effect_kind="gain-ammo", named_identity_ref="NI-0007",
    ),
    "direct-exploring": _asset(
        "direct-exploring", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-112.png", "direct-regular-face",
        "EXPLORING\nDRONE", "Resolve Exploration Sequence\nfor a neighboring Room\nwithout Moving.\nDo not resolve the Entrance effect.",
        custom_deck_ids=["5307", "5308"], source_sheet=None, generated_cell=None, physical_class="regular-item", selected_disposition="included-regular",
        upper_right="notInCombat",
        body_panels=[("remote-exploration-effect", "Resolve Exploration Sequence\nfor a neighboring Room\nwithout Moving."), ("entrance-suppression", "Do not resolve the Entrance effect.")],
        sentence_texts=["Resolve Exploration Sequence\nfor a neighboring Room\nwithout Moving.", "Do not resolve the Entrance effect."],
        icon_specs=[("upperRight", "notInCombat", "icon.notInCombat", "selected-verified", 0)],
        effect_kind="remote-exploration", named_identity_ref="NI-0199",
    ),
    "direct-grenade": _asset(
        "direct-grenade", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-128.png", "direct-regular-face",
        "GRENADE", "You can use this Item for free\nimmediately after gaining it.\n\nResolve a [grenadeToken] effect in\nan adjacent Corridor.\n\nOR\n\nGain 1 [grenadeToken].",
        custom_deck_ids=["5309", "5310", "5311", "5312", "5313"], source_sheet=None, generated_cell=None, physical_class="regular-item", selected_disposition="included-regular",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON",
        body_panels=[
            ("immediate-use-and-grenade-effect-branch", "You can use this Item for free\nimmediately after gaining it.\n\nResolve a [grenadeToken] effect in\nan adjacent Corridor."),
            ("branch-separator", "OR"),
            ("gain-grenade-branch", "Gain 1 [grenadeToken]."),
        ],
        sentence_texts=["You can use this Item for free\nimmediately after gaining it.", "Resolve a [grenadeToken] effect in\nan adjacent Corridor.", "Gain 1 [grenadeToken]."],
        icon_specs=[("body", "[grenadeToken]", "icon.grenadeToken", "canonical", 0), ("body", "[grenadeToken]", "icon.grenadeToken", "canonical", 0)],
        effect_kind="grenade-effect-or-gain", named_identity_ref=None,
    ),
    "direct-heavy-remote": _asset(
        "direct-heavy-remote", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-117.png", "direct-heavy-face-excluded",
        "REMOTE DETONATOR", "Discard 1 [secure] from any Room in the same Section\nto deal [shootDieCritical] to all [intruder] in that Room.\nEach [character] there lose 3 [characterHealth].",
        custom_deck_ids=["5314", "5315", "5316"], source_sheet=None, generated_cell=None, physical_class="heavy-item", selected_disposition="excluded-heavy",
        type_line="ONE USE ONLY, HEAVY", upper_right=LOCAL_REMOTE_BADGE,
        sentence_texts=[
            "Discard 1 [secure] from any Room in the same Section",
            "to deal [shootDieCritical] to all [intruder] in that Room.",
            "Each [character] there lose 3 [characterHealth].",
        ],
        icon_specs=[
            ("upperRight", LOCAL_REMOTE_BADGE, None, "literal-unresolved", 0),
            ("body", "[secure]", "icon.secure", "selected-verified", 0),
            ("body", "[shootDieCritical]", "icon.shootDieCritical", "selected-verified", 1),
            ("body", "[intruder]", "icon.intruder", "selected-verified", 2),
            ("body", "[character]", "icon.character", "selected-verified", 3),
            ("body", "[characterHealth]", "icon.characterHealth", "selected-verified", 4),
        ],
        effect_kind="excluded-heavy-remote-detonator", named_identity_ref="NI-0406",
    ),
    "yellow-sheet-00": _asset(
        "yellow-sheet-00", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-00.png", "generated-cell-physical-class-conflict",
        "MILITARY TASER", "1 chosen [intruder] in your Room Escapes.\nOR\n1 chosen Character discards all [ICON: upright light-gray rounded rectangle with white rim].",
        custom_deck_ids=["35"], source_sheet="yellow", generated_cell=0, physical_class="source-conflicted-portrait-special-weapon-versus-current-heavy", selected_disposition="class-conflict-excluded",
        type_line="ONE USE ONLY. SPECIAL WEAPON",
        body_panels=[("escape-intruder-branch", "1 chosen [intruder] in your Room Escapes."), ("branch-separator", "OR"), ("discard-local-card-glyph-branch", "1 chosen Character discards all [ICON: upright light-gray rounded rectangle with white rim].")],
        sentence_texts=["1 chosen [intruder] in your Room Escapes.", "1 chosen Character discards all [ICON: upright light-gray rounded rectangle with white rim]."],
        icon_specs=[("body", "[intruder]", "icon.intruder", "selected-verified", 0), ("body", LOCAL_ACTION_RECTANGLE, None, "selected-unresolved", 0)],
        effect_kind="class-conflict-military-taser", named_identity_ref="NI-0301",
    ),
    "yellow-sheet-01": _asset(
        "yellow-sheet-01", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-01.png", "generated-cell-cross-family-selector-gap",
        "FIRE EXTINGUISHER", "Discard a [fire].\n\nOR\n\n1 chosen [intruder] in your Room Escapes.",
        custom_deck_ids=["35"], source_sheet="yellow", generated_cell=1, physical_class="cross-family-yellow-special-weapon", selected_disposition="cross-family-gap-excluded",
        type_line="ONE USE ONLY. SPECIAL WEAPON",
        body_panels=[("discard-fire-branch", "Discard a [fire]."), ("branch-separator", "OR"), ("escape-intruder-branch", "1 chosen [intruder] in your Room Escapes.")],
        sentence_texts=["Discard a [fire].", "1 chosen [intruder] in your Room Escapes."],
        icon_specs=[("body", "[fire]", "icon.fire", "canonical", 0), ("body", "[intruder]", "icon.intruder", "canonical", 0)],
        effect_kind="cross-family-fire-extinguisher", named_identity_ref=None,
    ),
    "yellow-sheet-02": _asset(
        "yellow-sheet-02", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-02.png", "generated-cell-cross-family-selector-gap",
        "ROBOT CONTROLLER", "Use the [robot] from anywhere in the Facility.\nOR\nIf [robot] is not on the board yet, place it in your Room.",
        custom_deck_ids=["35"], source_sheet="yellow", generated_cell=2, physical_class="cross-family-yellow-item", selected_disposition="cross-family-gap-excluded",
        type_line="", upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("remote-robot-branch", "Use the [robot] from anywhere in the Facility."), ("branch-separator", "OR"), ("place-robot-branch", "If [robot] is not on the board yet, place it in your Room.")],
        sentence_texts=["Use the [robot] from anywhere in the Facility.", "If [robot] is not on the board yet, place it in your Room."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[robot]", "icon.robot", "selected-verified", 0), ("body", "[robot]", "icon.robot", "selected-verified", 1)],
        effect_kind="cross-family-robot-controller", named_identity_ref=None,
    ),
    "yellow-sheet-03": _asset(
        "yellow-sheet-03", "assets/tts-mod/extract/v2-dl/tree/cards/game/yellowitem-146_cards/card-03.png", "generated-cell-cross-family-non-rules-gap",
        "", "", custom_deck_ids=["35"], source_sheet="yellow", generated_cell=3, physical_class="cross-family-non-rules-cell", selected_disposition="cross-family-gap-excluded",
        type_line="", effect_kind="cross-family-non-rules-cell", rules_text_present=False,
    ),
    "red-sheet-00": _asset(
        "red-sheet-00", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-00.png", "generated-cell-selector-gap-variant",
        "AMMO MAGAZINE", "You can use this Item for free\nimmediately after gaining it.\n\nGain up to 2 [ammoToken]",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=0, physical_class="regular-item", selected_disposition="red-selector-gap",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON",
        body_panels=[("immediate-use-timing-note", "You can use this Item for free\nimmediately after gaining it."), ("gain-ammo-effect", "Gain up to 2 [ammoToken]")],
        sentence_texts=["You can use this Item for free\nimmediately after gaining it.", "Gain up to 2 [ammoToken]"],
        icon_specs=[("body", "[ammoToken]", "icon.ammoToken", "selected-verified", 0)], effect_kind="gap-gain-two-ammo", named_identity_ref="NI-0007",
    ),
    "red-sheet-01": _asset(
        "red-sheet-01", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-01.png", "generated-cell-regular-face",
        "ANTI-AIRCRAFT\nCODES", "Only in [computer] Room without [malfunction].\n\nTake both Anti-Aircraft tokens\nand place them in any order.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=1, physical_class="regular-item", selected_disposition="included-regular",
        upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("room-restriction", "Only in [computer] Room without [malfunction]."), ("anti-aircraft-reorder-effect", "Take both Anti-Aircraft tokens\nand place them in any order.")],
        sentence_texts=["Only in [computer] Room without [malfunction].", "Take both Anti-Aircraft tokens\nand place them in any order."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[computer]", "icon.computer", "selected-verified", 0), ("body", "[malfunction]", "icon.malfunction", "selected-verified", 1)],
        effect_kind="reorder-anti-aircraft", named_identity_ref="NI-0009",
    ),
    "red-sheet-02": _asset(
        "red-sheet-02", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-02.png", "generated-cell-selector-gap-variant",
        "CLAYMORE\nMINE", f"Place 1 {LOCAL_RED_TOKEN} in an empty Corridor.\nWhen any number of [intruder]\nare placed in that Corridor,\nremove the {LOCAL_RED_TOKEN} and resolve\nthe token effect there.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=2, physical_class="regular-item", selected_disposition="red-selector-gap",
        upper_right=LOCAL_CROSSED_DEVICE,
        sentence_texts=[f"Place 1 {LOCAL_RED_TOKEN} in an empty Corridor.", f"When any number of [intruder]\nare placed in that Corridor,\nremove the {LOCAL_RED_TOKEN} and resolve\nthe token effect there."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", LOCAL_RED_TOKEN, None, "selected-unresolved", 1), ("body", "[intruder]", "icon.intruder", "selected-verified", 0), ("body", LOCAL_RED_TOKEN, None, "selected-unresolved", 2)],
        effect_kind="gap-claymore", named_identity_ref=None,
    ),
    "red-sheet-03": _asset(
        "red-sheet-03", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-03.png", "generated-cell-selector-gap-variant",
        "EXPLORING\nDRONE", "Resolve an Exploration Procedure\nfor a Room on the other side\nof an empty, Open Corridor.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=3, physical_class="regular-item", selected_disposition="red-selector-gap",
        upper_right=LOCAL_CROSSED_DEVICE,
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0)],
        effect_kind="gap-exploring", named_identity_ref="NI-0199",
    ),
    "red-sheet-04": _asset(
        "red-sheet-04", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-04.png", "generated-cell-regular-face",
        "FLASHBANG", "Move.\nIgnore all Opportunity Attacks\nduring that Movement.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=4, physical_class="regular-item", selected_disposition="included-regular",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON",
        body_panels=[("movement-instruction", "Move."), ("opportunity-attack-suppression", "Ignore all Opportunity Attacks\nduring that Movement.")],
        sentence_texts=["Move.", "Ignore all Opportunity Attacks\nduring that Movement."], effect_kind="flashbang-movement", named_identity_ref=None,
    ),
    "red-sheet-05": _asset(
        "red-sheet-05", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-05.png", "generated-cell-selector-gap-variant",
        "GRENADE", f"You can use this Item for free\nimmediately after gaining it.\n\nResolve a {LOCAL_RED_TOKEN} effect in\nan adjacent Corridor.\n\nOR\n\nGain 1 {LOCAL_RED_TOKEN}.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=5, physical_class="regular-item", selected_disposition="red-selector-gap",
        type_line="ONE USE ONLY,\nSPECIAL WEAPON",
        body_panels=[("immediate-use-and-local-token-branch", f"You can use this Item for free\nimmediately after gaining it.\n\nResolve a {LOCAL_RED_TOKEN} effect in\nan adjacent Corridor."), ("branch-separator", "OR"), ("gain-local-token-branch", f"Gain 1 {LOCAL_RED_TOKEN}.")],
        sentence_texts=["You can use this Item for free\nimmediately after gaining it.", f"Resolve a {LOCAL_RED_TOKEN} effect in\nan adjacent Corridor.", f"Gain 1 {LOCAL_RED_TOKEN}."],
        icon_specs=[("body", LOCAL_RED_TOKEN, None, "selected-unresolved", 0), ("body", "OR", None, "selected-unresolved", 1), ("body", LOCAL_RED_TOKEN, None, "selected-unresolved", 2)],
        effect_kind="gap-grenade-local-glyph", named_identity_ref="NI-0224",
    ),
    "red-sheet-06": _asset(
        "red-sheet-06", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-06.png", "generated-cell-regular-face",
        "PERSONAL\nLOG CODES", "Only in a [computer] Room with no [malfunction].\nCheck all Objective cards\nof a chosen Character.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=6, physical_class="regular-item", selected_disposition="included-regular",
        upper_right=LOCAL_CROSSED_DEVICE,
        body_panels=[("room-restriction", "Only in a [computer] Room with no [malfunction]."), ("objective-inspection-effect", "Check all Objective cards\nof a chosen Character.")],
        sentence_texts=["Only in a [computer] Room with no [malfunction].", "Check all Objective cards\nof a chosen Character."],
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0), ("body", "[computer]", "icon.computer", "selected-verified", 0), ("body", "[malfunction]", "icon.malfunction", "selected-verified", 1)],
        effect_kind="inspect-objectives", named_identity_ref="NI-0353",
    ),
    "red-sheet-07": _asset(
        "red-sheet-07", "assets/tts-mod/extract/v2-dl/tree/cards/game/reditem-148_cards/card-07.png", "generated-cell-regular-face",
        "PORTABLE\nBARRIER", "Place a closed Door.",
        custom_deck_ids=["36"], source_sheet="red", generated_cell=7, physical_class="regular-item", selected_disposition="included-regular",
        upper_right=LOCAL_CROSSED_DEVICE,
        icon_specs=[("upperRight", LOCAL_CROSSED_DEVICE, None, "selected-unresolved", 0)],
        effect_kind="place-closed-door", named_identity_ref="NI-0366",
    ),
}


def _definition(root_sequence: int, asset_key: str, card_id: int, guid: str, custom_deck_id: str, disposition: str) -> dict:
    code = f"{card_id}-{guid.upper()}"
    regular = disposition == "included-regular"
    if regular:
        occurrence_id = f"TTS-RED-ITEM-{code}-FACE"
        source_id = f"SRC-RED-ITEM-{code}"
    elif disposition == "excluded-heavy":
        occurrence_id = f"TTS-RED-ITEM-EXCLUDED-HEAVY-{code}-FACE"
        source_id = f"SRC-RED-ITEM-EXCLUDED-HEAVY-{code}"
    else:
        occurrence_id = f"TTS-RED-ITEM-CLASS-CONFLICT-{code}-FACE"
        source_id = f"SRC-RED-ITEM-CLASS-CONFLICT-{code}"
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
        "semanticRuleId": f"SEM-RED-ITEM-{code}-001" if regular else None,
    }


ROOT_PHYSICAL_DEFINITIONS = [
    _definition(1, "yellow-sheet-00", 3500, "37723a", "35", "class-conflict-excluded"),
    _definition(2, "yellow-sheet-00", 3500, "d1fe22", "35", "class-conflict-excluded"),
    _definition(3, "yellow-sheet-00", 3500, "173951", "35", "class-conflict-excluded"),
    _definition(4, "yellow-sheet-00", 3500, "179555", "35", "class-conflict-excluded"),
    _definition(5, "yellow-sheet-00", 3500, "2f5802", "35", "class-conflict-excluded"),
    _definition(6, "yellow-sheet-00", 3500, "fa1a60", "35", "class-conflict-excluded"),
    _definition(7, "direct-heavy-remote", 531600, "0c0643", "5316", "excluded-heavy"),
    _definition(8, "direct-heavy-remote", 531500, "810d80", "5315", "excluded-heavy"),
    _definition(9, "direct-heavy-remote", 531400, "5df671", "5314", "excluded-heavy"),
    _definition(10, "direct-ammo", 543800, "01970b", "5438", "included-regular"),
    _definition(11, "direct-ammo", 543800, "d8d841", "5438", "included-regular"),
    _definition(12, "direct-ammo", 543800, "43ac80", "5438", "included-regular"),
    _definition(13, "direct-ammo", 543800, "ea2857", "5438", "included-regular"),
    _definition(14, "direct-ammo", 543800, "af5a2d", "5438", "included-regular"),
    _definition(15, "direct-ammo", 543800, "eaf654", "5438", "included-regular"),
    _definition(16, "direct-ammo", 543800, "ee51d1", "5438", "included-regular"),
    _definition(17, "red-sheet-01", 3601, "2bc2db", "36", "included-regular"),
    _definition(18, "direct-exploring", 530700, "ed1060", "5307", "included-regular"),
    _definition(19, "direct-exploring", 530800, "301a8b", "5308", "included-regular"),
    _definition(20, "red-sheet-04", 3604, "82349f", "36", "included-regular"),
    _definition(21, "red-sheet-04", 3604, "8bfa0b", "36", "included-regular"),
    _definition(22, "red-sheet-04", 3604, "1df1c5", "36", "included-regular"),
    _definition(23, "direct-grenade", 530900, "9cda71", "5309", "included-regular"),
    _definition(24, "direct-grenade", 531000, "ebc22d", "5310", "included-regular"),
    _definition(25, "direct-grenade", 531100, "5108bc", "5311", "included-regular"),
    _definition(26, "direct-grenade", 531200, "11f04f", "5312", "included-regular"),
    _definition(27, "direct-grenade", 531300, "dc960f", "5313", "included-regular"),
    _definition(28, "red-sheet-06", 3606, "ea89da", "36", "included-regular"),
    _definition(29, "red-sheet-07", 3607, "3dad95", "36", "included-regular"),
    _definition(30, "red-sheet-07", 3607, "7afbe8", "36", "included-regular"),
]

REGULAR_PHYSICAL_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if row["regular"]]
EXCLUDED_HEAVY_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if row["disposition"] == "excluded-heavy"]
CLASS_CONFLICT_DEFINITIONS = [row for row in ROOT_PHYSICAL_DEFINITIONS if row["disposition"] == "class-conflict-excluded"]
for family_sequence, row in enumerate(REGULAR_PHYSICAL_DEFINITIONS, 1):
    row["familySequence"] = family_sequence

RED_ITEM_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS]
AMMO_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-ammo"]
EXPLORING_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-exploring"]
FLASHBANG_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "red-sheet-04"]
GRENADE_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-grenade"]
ANTI_AIRCRAFT_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "red-sheet-01"]
PERSONAL_LOG_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "red-sheet-06"]
PORTABLE_BARRIER_RULE_IDS = [row["semanticRuleId"] for row in REGULAR_PHYSICAL_DEFINITIONS if row["assetKey"] == "red-sheet-07"]
IMMEDIATE_RED_RULE_IDS = [*AMMO_RULE_IDS, *GRENADE_RULE_IDS]

RED_ITEM_QUESTION_BLOCKS = {
    "SEM-Q-039": ["SEM-RED-ITEM-ONE-USE-001"],
    "SEM-Q-040": ["SEM-RED-ITEM-DECK-001"],
    "SEM-Q-044": [*AMMO_RULE_IDS, *GRENADE_RULE_IDS],
    "SEM-Q-045": ["SEM-RED-ITEM-IMMEDIATE-USE-001", *IMMEDIATE_RED_RULE_IDS],
    "SEM-Q-046": [*ANTI_AIRCRAFT_RULE_IDS, *PERSONAL_LOG_RULE_IDS, *PORTABLE_BARRIER_RULE_IDS],
    "SEM-Q-047": ["SEM-RED-ITEM-DECK-001"],
    "SEM-Q-048": EXPLORING_RULE_IDS,
    "SEM-Q-049": PERSONAL_LOG_RULE_IDS,
    "SEM-Q-050": [*PORTABLE_BARRIER_RULE_IDS],
}


def _raw_red_deck(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    deck = _find_guid(root.get("ObjectStates"), BASE_RED_ITEM_DECK_GUID)
    if not isinstance(deck, dict):
        raise AssertionError("base Red Item root Deck missing from raw TTS save")
    return deck, hashlib.sha256(data).hexdigest()


def _parse_bga_red_items(path: Path) -> list[dict]:
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
        if not deck_match or ast.literal_eval(deck_match.group(1)) != "deck-red":
            continue

        def literal(pattern: str, default=None):
            found = re.search(pattern, source_block, re.S)
            return ast.literal_eval(found.group(1)) if found else default

        nbr_match = re.search(r"\n    nbr: (\d+)", source_block)
        if not nbr_match:
            raise AssertionError(f"licensed Red Item multiplicity missing: {key}")
        rows.append({
            "key": key,
            "sourceOrder": source_index + 1,
            "deck": "deck-red",
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
        ("Ammo", 7, False), ("AntiaircraftCodes", 1, False), ("ExploringDrone", 2, False),
        ("Flashbang", 3, False), ("Grenade", 5, False), ("MilitaryTaser", 6, True),
        ("PersonalLogCodes", 1, False), ("PortableBarrier", 2, False), ("RemoteDetonator", 3, True),
    ]
    if [(row["key"], row["nbr"], row["heavy"]) for row in rows] != expected:
        raise AssertionError("licensed Red Item rows/order/multiplicity changed")
    return rows


def _source_regions(asset: dict) -> list[dict]:
    regions = [
        {
            "regionId": "R1", "readingOrder": 1, "role": "artwork-and-interface", "operative": False,
            "rulesDataHandling": "preserve pixels as artwork/interface; exclude decoration, props, labels embedded in art, microtext, and overlays from operative rules",
        },
        {
            "regionId": "R2", "readingOrder": 2, "role": "identity-trait-and-restriction", "operative": bool(asset["rulesTextPresent"]),
            "printedTitle": asset["printedTitle"], "typeLine": asset["typeLine"], "upperRight": asset["upperRight"],
            "headingOccurrences": ([{"exactText": asset["typeLine"], "headingClass": "trait-line"}] if asset["typeLine"] else []),
            "traitKeywords": [value for value in ("ONE USE ONLY", "SPECIAL WEAPON", "HEAVY") if value in asset["typeLine"]],
            "useHeadingPresent": False, "discardHeadingPresent": False, "passiveHeadingPresent": False, "reactionHeadingPresent": False,
        },
        {
            "regionId": "R3", "readingOrder": 3, "role": "operative-effect-body", "operative": bool(asset["rulesTextPresent"]),
            "exactText": asset["printedBody"], "bodyStart": 0, "bodyEnd": len(asset["printedBody"]),
            "branchHeadingOccurrences": [{"exactText": "OR", "headingClass": "branch-separator"}] if "\nOR\n" in asset["printedBody"] else [],
        },
    ]
    return regions


def _source_panels(asset: dict) -> list[dict]:
    panels = [
        {"panelId": "P1", "readingOrder": 1, "role": "artwork-panel", "operative": False, "regionId": "R1", "exactText": None},
        {
            "panelId": "P2", "readingOrder": 2, "role": "identity-trait-restriction-panel", "operative": bool(asset["rulesTextPresent"]), "regionId": "R2",
            "exactText": "\n".join(value for value in (asset["printedTitle"], asset["typeLine"], asset["upperRight"]) if value),
        },
    ]
    for index, (role, exact_text) in enumerate(asset["bodyPanels"], 3):
        panels.append({"panelId": f"P{index}", "readingOrder": index, "role": role, "operative": bool(asset["rulesTextPresent"]), "regionId": "R3", "exactText": exact_text})
    return panels


def _source_sentences(asset: dict, panels: list[dict]) -> list[dict]:
    rows = []
    cursor = 0
    body_panels = panels[2:]
    for sequence, exact_text in enumerate(asset["sentenceTexts"], 1):
        start = asset["printedBody"].find(exact_text, cursor)
        if start < 0:
            raise AssertionError(f"Red Item sentence span missing: {asset['assetKey']}:{sequence}")
        end = start + len(exact_text)
        panel = next((row for row in body_panels if exact_text in (row.get("exactText") or "")), None)
        if panel is None:
            panel = next((row for row in body_panels if (row.get("exactText") or "") and (row.get("exactText") or "") in exact_text), body_panels[0])
        rows.append({"sentenceId": f"RI-{asset['assetKey'].upper()}-S{sequence:02d}", "sequence": sequence, "regionId": "R3", "panelId": panel["panelId"], "exactText": exact_text, "start": start, "end": end})
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
                raise AssertionError(f"Red Item icon span missing: {asset['assetKey']}:{source_token}")
            end = start + len(source_token)
            body_cursor = end
            panel = next((item for item in panels[2:] if source_token in (item.get("exactText") or "")), panels[2])
        if evidence_kind == "canonical":
            token = semantic_reference.removeprefix("icon.") if semantic_reference else None
            evidence = canonical_claims.get(token)
            if not evidence or evidence.get("verdict") != "match" or evidence.get("actual") != token:
                raise AssertionError(f"Red Item canonical icon evidence missing: {asset['assetKey']}:{token}")
            mapping_status = "canonical-sidecar-plus-independent-icon-verification"
            page40_assigned = True
            literal = evidence.get("evidence")
        elif evidence_kind == "selected-verified":
            if evidence_index >= len(verified):
                raise AssertionError(f"Red Item selected verified icon evidence missing: {asset['assetKey']}:{sequence}")
            evidence = verified[evidence_index]
            token = semantic_reference.removeprefix("icon.") if semantic_reference else None
            if evidence.get("matchDecision") != "match" or evidence.get("canonicalToken") != token:
                raise AssertionError(f"Red Item selected verified icon drift: {asset['assetKey']}:{sequence}")
            mapping_status = "selected-source-scoped-authoritative-match"
            page40_assigned = True
            literal = evidence.get("visibleDiscriminator") or evidence.get("referenceLabel")
        elif evidence_kind == "selected-unresolved":
            if evidence_index >= len(unresolved):
                raise AssertionError(f"Red Item selected unresolved icon evidence missing: {asset['assetKey']}:{sequence}")
            evidence = unresolved[evidence_index]
            if evidence.get("matchDecision") != "no-match" or evidence.get("canonicalToken") is not None or semantic_reference is not None:
                raise AssertionError(f"Red Item selected unresolved icon drift: {asset['assetKey']}:{sequence}")
            mapping_status = "selected-explicit-authoritative-no-match"
            page40_assigned = False
            literal = evidence.get("referenceLabel") or source_token
        elif evidence_kind == "literal-unresolved":
            evidence = {"matchDecision": "not-asserted", "referenceLabel": source_token, "reason": "visible local morphology retained literally; no controlled token assigned"}
            mapping_status = "visible-literal-unresolved-not-promoted"
            page40_assigned = False
            literal = source_token
        else:
            raise AssertionError(f"unknown Red Item icon evidence kind: {evidence_kind}")
        rows.append({
            "assetIconOccurrenceId": f"RI-ASSET-{asset['assetKey'].upper()}-I{sequence:02d}", "sequence": sequence,
            "regionId": "R2" if location == "upperRight" else "R3", "panelId": panel["panelId"], "cardLocationClass": location,
            "sourceToken": source_token, "start": start, "end": end, "literalAppearance": literal, "semanticReferenceId": semantic_reference,
            "mappingStatus": mapping_status, "page40TokenAssigned": page40_assigned, "mappingScope": f"exact source asset {asset['sourcePath']} occurrence only", "selectedEvidence": evidence,
        })
    expected_verified_indices = {spec[4] for spec in asset["iconSpecs"] if spec[3] == "selected-verified"}
    expected_unresolved_indices = {spec[4] for spec in asset["iconSpecs"] if spec[3] == "selected-unresolved"}
    if expected_verified_indices != set(range(len(verified))) or expected_unresolved_indices != set(range(len(unresolved))):
        raise AssertionError(f"Red Item selected icon evidence count drift: {asset['assetKey']}")
    return rows


def build_red_item_source_index(repo: Path) -> dict:
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

    matching_roles = [row for row in roles if row.get("role") == "redItemsDeck"]
    if len(matching_roles) != 1:
        raise AssertionError("Red Item Lua role multiplicity changed")
    role = matching_roles[0]
    expected_deck_nums = ["35", "36", "5307", "5308", "5309", "5310", "5311", "5312", "5313", "5314", "5315", "5316", "5438"]
    if role.get("guid") != BASE_RED_ITEM_DECK_GUID or role.get("type") != "Deck" or role.get("gmnotes") != "reditemDiscard" or role.get("n_urls") != 8 or role.get("deck_nums") != expected_deck_nums:
        raise AssertionError("base Red Item Lua role changed")

    raw_deck, raw_save_sha = _raw_red_deck(repo)
    raw_deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
    expected_deck_ids = [row["ttsCardId"] for row in ROOT_PHYSICAL_DEFINITIONS]
    if raw_deck_ids != expected_deck_ids:
        raise AssertionError("base Red Item raw DeckIDs order changed")
    contained_value = raw_deck.get("ContainedObjects") or {}
    contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
    expected_children = [(row["ttsCardId"], row["ttsCardGuid"]) for row in ROOT_PHYSICAL_DEFINITIONS]
    if [(int(row["CardID"]), row["GUID"]) for row in contained] != expected_children:
        raise AssertionError("base Red Item raw contained occurrence order changed")
    root_custom = raw_deck.get("CustomDeck") or {}
    if set(root_custom) != set(expected_deck_nums):
        raise AssertionError("base Red Item root CustomDeck IDs changed")
    expected_custom = {
        "35": (YELLOW_SHEET_FACE_URL, YELLOW_BACK_URL, 2, 2),
        "36": (RED_SHEET_FACE_URL, RED_BACK_URL, 4, 2),
        "5307": ("https://steamusercontent-a.akamaihd.net/ugc/16224918053163279520/CC9C3828CDFBF1772D56486605233B81D2067792/", RED_BACK_URL, 1, 1),
        "5308": ("https://steamusercontent-a.akamaihd.net/ugc/16224918053163279520/CC9C3828CDFBF1772D56486605233B81D2067792/", RED_BACK_URL, 1, 1),
        "5309": ("https://steamusercontent-a.akamaihd.net/ugc/17486770896024566813/D996C47118C240A1CCAA619B07FBDF117DA83DE4/", RED_BACK_URL, 1, 1),
        "5310": ("https://steamusercontent-a.akamaihd.net/ugc/17486770896024566813/D996C47118C240A1CCAA619B07FBDF117DA83DE4/", RED_BACK_URL, 1, 1),
        "5311": ("https://steamusercontent-a.akamaihd.net/ugc/17486770896024566813/D996C47118C240A1CCAA619B07FBDF117DA83DE4/", RED_BACK_URL, 1, 1),
        "5312": ("https://steamusercontent-a.akamaihd.net/ugc/17486770896024566813/D996C47118C240A1CCAA619B07FBDF117DA83DE4/", RED_BACK_URL, 1, 1),
        "5313": ("https://steamusercontent-a.akamaihd.net/ugc/17486770896024566813/D996C47118C240A1CCAA619B07FBDF117DA83DE4/", RED_BACK_URL, 1, 1),
        "5314": ("https://steamusercontent-a.akamaihd.net/ugc/16745308283630248460/E4D26ECC0E7FAECF6EC1155FEFB9F4D77E39EBC3/", RED_BACK_URL, 1, 1),
        "5315": ("https://steamusercontent-a.akamaihd.net/ugc/16745308283630248460/E4D26ECC0E7FAECF6EC1155FEFB9F4D77E39EBC3/", RED_BACK_URL, 1, 1),
        "5316": ("https://steamusercontent-a.akamaihd.net/ugc/16745308283630248460/E4D26ECC0E7FAECF6EC1155FEFB9F4D77E39EBC3/", RED_BACK_URL, 1, 1),
        "5438": ("https://steamusercontent-a.akamaihd.net/ugc/13253344914688903592/E70046DE0E4022172D30DA264346EE4452CD55D9/", RED_BACK_URL, 1, 1),
    }
    for custom_id, expected in expected_custom.items():
        custom = root_custom[custom_id]
        if (custom.get("FaceURL"), custom.get("BackURL"), custom.get("NumWidth"), custom.get("NumHeight")) != expected:
            raise AssertionError(f"base Red Item CustomDeck tuple changed: {custom_id}")

    root_object = next(row for row in objects if row.get("guid") == BASE_RED_ITEM_DECK_GUID)
    red_children = [row for row in objects if ["Deck", BASE_RED_ITEM_DECK_GUID, ""] in (row.get("parent") or []) and row.get("gmnotes") == "reditem"]
    all_red_tagged = [row for row in objects if row.get("gmnotes") == "reditem"]
    if root_object.get("type") != "Deck" or root_object.get("parent") != [] or len(red_children) != 30 or len(all_red_tagged) != 30 or {(int(row["card_id"]), row["guid"]) for row in red_children} != set(expected_children):
        raise AssertionError("base Red Item object/tag/container closure changed")
    classification_by_guid = {row["guid"]: row for row in classification}
    if classification_by_guid[BASE_RED_ITEM_DECK_GUID].get("verdict") != "base" or any(classification_by_guid[guid].get("verdict") != "base" for _, guid in expected_children):
        raise AssertionError("Red Item base classification changed")

    bga_rows = _parse_bga_red_items(repo / BGA_ITEMS_PATH)
    bga_table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "ITEMS_DATA")
    if bga_table.get("count") != 57 or not set(row["key"] for row in bga_rows).issubset(set(bga_table.get("keys") or [])):
        raise AssertionError("licensed Red Item evidence-index closure changed")
    if sum(row["nbr"] for row in bga_rows) != 30 or sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]) != 21 or sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]) != 9:
        raise AssertionError("licensed Red Item aggregate class/count boundary changed")

    sheet_meta = {
        "red": (RED_ITEM_RED_SHEET_SOURCE_ID, RED_ITEM_RED_SHEET_PATH, {"columns": 4, "rows": 2}),
        "yellow": (RED_ITEM_YELLOW_SHEET_SOURCE_ID, RED_ITEM_YELLOW_SHEET_PATH, {"columns": 2, "rows": 2}),
    }
    source_asset_rows = []
    source_asset_by_key = {}
    for asset_key, asset in ASSET_DEFINITIONS.items():
        source_path = asset["sourcePath"]
        source_sha = _sha(repo / source_path)
        corpus_row = corpus_by_path.get(source_path) or {}
        if corpus_row.get("sourceSha256") != source_sha:
            raise AssertionError(f"Red Item corpus/hash readiness drift: {asset_key}")
        if asset["rulesTextPresent"]:
            if not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"} or corpus_row.get("printedData", {}).get("body") != asset["printedBody"]:
                raise AssertionError(f"Red Item exact corpus body/readiness drift: {asset_key}")
        elif corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") != "non-rules-or-reference":
            raise AssertionError(f"Red Item cross-family non-rules cell drift: {asset_key}")
        selected_entry = selected_by_path.get(source_path) or {}
        selected_runs = selected_entry.get("runs") or []
        selected_run = selected_runs[0] if len(selected_runs) == 1 else None
        if corpus_row.get("extractionState") in {"draft-full", "non-rules-or-reference"}:
            if selected_run is None or (selected_run.get("visibleText") or {}).get("title") != asset["printedTitle"] or (selected_run.get("visibleText") or {}).get("body") != asset["printedBody"]:
                raise AssertionError(f"Red Item selected title/body evidence drift: {asset_key}")
        elif selected_runs:
            raise AssertionError(f"Red Item canonical asset unexpectedly depends on selected overlay: {asset_key}")
        progress_row = progress_by_path.get(source_path) or {}
        vision_result_path = (progress_row.get("vision") or {}).get("resultPath")
        vision_result = json.loads((repo / vision_result_path).read_text(encoding="utf-8")) if vision_result_path else None
        if corpus_row.get("extractionState") == "verified-canonical":
            parsed = (vision_result or {}).get("parsed") or {}
            if parsed.get("title") != asset["printedTitle"] or parsed.get("body") != asset["printedBody"]:
                raise AssertionError(f"Red Item canonical title/body evidence drift: {asset_key}")
        generated = progress_row.get("generatedFrom") or (low_by_path.get(source_path) or {}).get("provenance") or {}
        if asset["generatedCell"] is not None:
            _, expected_sheet_path, _ = sheet_meta[asset["sourceSheet"]]
            if generated.get("sourceSheetPath") != expected_sheet_path or generated.get("cellIndex") != asset["generatedCell"]:
                raise AssertionError(f"Red Item generated source/cell drift: {asset_key}")
        elif generated.get("sourceSheetPath") is not None or generated.get("cellIndex") is not None:
            raise AssertionError(f"Red Item direct/generated inversion: {asset_key}")
        panels = _source_panels(asset)
        regions = _source_regions(asset)
        sentences = _source_sentences(asset, panels)
        icons = _source_icons(asset, selected_run, vision_result, panels)
        selected_occurrences = [row["occurrenceId"] for row in ROOT_PHYSICAL_DEFINITIONS if row["assetKey"] == asset_key]
        source_id = None
        if asset["selectedDisposition"] == "red-selector-gap":
            source_id = f"SRC-RED-ITEM-VARIANT-36-CELL-{asset['generatedCell']:02d}"
        elif asset["selectedDisposition"] == "cross-family-gap-excluded":
            source_id = f"SRC-RED-ITEM-CROSS-FAMILY-35-CELL-{asset['generatedCell']:02d}"
        source_sheet_id = source_sheet_path = source_sheet_grid = None
        if asset["sourceSheet"]:
            source_sheet_id, source_sheet_path, source_sheet_grid = sheet_meta[asset["sourceSheet"]]
        source_asset_row = {
            **{key: asset[key] for key in ("assetKey", "sourcePath", "sourceRole", "customDeckIds", "generatedCell", "physicalClass", "selectedDisposition", "printedTitle", "typeLine", "upperRight", "printedBody", "effectKind", "namedIdentityRef", "rulesTextPresent")},
            "sourceId": source_id, "sourceSha256": source_sha, "sourceSheetId": source_sheet_id, "sourceSheetPath": source_sheet_path, "sourceSheetGrid": source_sheet_grid,
            "selectedByRootDeck": bool(selected_occurrences), "selectedPhysicalOccurrenceIds": selected_occurrences,
            "selectorGap": None if selected_occurrences else {"status": "explicit-no-root-DeckID-GUID-selector", "reason": "The generated source-sheet cell exists, but no raw Red root DeckID/contained GUID selects it. Cross-family cells remain excluded and Red cells remain independent variants.", "cardIdModuloJoinUsed": False},
            "regions": regions, "panels": panels, "sentences": sentences, "iconOccurrences": icons,
            "printedBodyDigest": _digest({"title": asset["printedTitle"], "typeLine": asset["typeLine"], "upperRight": asset["upperRight"], "body": asset["printedBody"]}),
            "panelDigest": _digest(panels), "iconDigest": _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in icons]),
            "corpusEvidencePath": CORPUS_PATH, "selectedEvidencePath": SELECTED_EVIDENCE_PATH if selected_run else None, "visionEvidencePath": vision_result_path,
            "generatedCellEvidencePath": VISION_PROGRESS_PATH, "extractionState": corpus_row["extractionState"], "rulesInformationReadiness": corpus_row.get("rulesInformationReadiness"),
        }
        source_asset_rows.append(source_asset_row)
        source_asset_by_key[asset_key] = source_asset_row

    for sheet_key, (_, sheet_path_value, grid) in sheet_meta.items():
        sheet_path = repo / sheet_path_value
        with Image.open(sheet_path) as sheet_image:
            expected_size = (grid["columns"] * 591, grid["rows"] * 863)
            if sheet_image.size != expected_size:
                raise AssertionError(f"Red Item {sheet_key} source-sheet dimensions/grid changed")
            for cell in range(grid["columns"] * grid["rows"]):
                row_index, column_index = divmod(cell, grid["columns"])
                crop = sheet_image.crop((column_index * 591, row_index * 863, (column_index + 1) * 591, (row_index + 1) * 863)).convert("RGB")
                generated_asset = source_asset_by_key[f"{sheet_key}-sheet-{cell:02d}"]
                with Image.open(repo / generated_asset["sourcePath"]) as generated_image:
                    if generated_image.convert("RGB").tobytes() != crop.tobytes():
                        raise AssertionError(f"Red Item {sheet_key} generated-cell pixel drift: {cell}")

    contained_by_tuple = {(int(row["CardID"]), row["GUID"]): row for row in contained}

    def build_physical(definition: dict) -> dict:
        asset = source_asset_by_key[definition["assetKey"]]
        raw_child = contained_by_tuple[(definition["ttsCardId"], definition["ttsCardGuid"])]
        custom = root_custom[definition["customDeckId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        if definition["regular"]:
            side_role = "operative-regular-red-item-face"
            batch_disposition = "included-regular-red-item-face"
        elif definition["disposition"] == "excluded-heavy":
            side_role = "excluded-heavy-red-root-face"
            batch_disposition = "excluded-heavy-item-face"
        else:
            side_role = "excluded-source-conflicted-military-taser-face"
            batch_disposition = "excluded-physical-class-conflict"
        sheet_hash = _sha(repo / asset["sourceSheetPath"]) if asset["generatedCell"] is not None else None
        selector = {
            "key": "FaceURL", "objectType": raw_child.get("Name"), "fullCardId": definition["ttsCardId"], "guid": definition["ttsCardGuid"],
            "parentDeckGuid": BASE_RED_ITEM_DECK_GUID, "customDeckId": definition["customDeckId"], "url": custom["FaceURL"], "backUrl": custom["BackURL"],
            "sideRole": side_role, "sourceRole": asset["sourceRole"],
            "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-BackURL-parent-tuple-with-explicit-generated-cell" if asset["generatedCell"] is not None else "exact-full-CardID-GUID-direct-FaceURL-BackURL-parent-tuple",
            "generatedSpriteSheetCell": asset["generatedCell"] is not None, "sourceSheetPath": asset["sourceSheetPath"], "sourceSheetSha256": sheet_hash,
            "sourceSheetGrid": asset["sourceSheetGrid"], "generatedCell": asset["generatedCell"], "selectorGap": None, "cardIdModuloJoinUsed": False,
        }
        provenance_source_path = asset["sourceSheetPath"] if asset["generatedCell"] is not None else asset["sourcePath"]
        provenance_file = provenance_source_path.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]
        provenance_row = provenance_by_file.get(provenance_file) or {}
        exact_ref = next((row for row in provenance_row.get("objects") or [] if row.get("key") == "FaceURL" and row.get("guid") == definition["ttsCardGuid"] and row.get("cardId") == definition["ttsCardId"]), None)
        if exact_ref is None or exact_ref.get("parent") != [["Deck", BASE_RED_ITEM_DECK_GUID, ""]] or provenance_row.get("url") != custom["FaceURL"]:
            raise AssertionError(f"Red Item exact provenance selector drift: {code}")
        physical_regions = [{**region, "regionId": f"RI-{code}-{region['regionId']}"} for region in asset["regions"]]
        region_map = {old: new["regionId"] for old, new in zip(("R1", "R2", "R3"), physical_regions)}
        physical_panels = [{**panel, "panelId": f"RI-{code}-{panel['panelId']}", "regionId": region_map[panel["regionId"]]} for panel in asset["panels"]]
        panel_map = {source["panelId"]: physical["panelId"] for source, physical in zip(asset["panels"], physical_panels)}
        physical_sentences = [{**sentence, "sentenceId": f"RI-{code}-S{sentence['sequence']:02d}", "regionId": region_map[sentence["regionId"]], "panelId": panel_map[sentence["panelId"]]} for sentence in asset["sentences"]]
        physical_icons = [{**icon, "occurrenceId": f"RI-{code}-I{icon['sequence']:02d}", "assetMorphologyOccurrenceId": icon["assetIconOccurrenceId"], "regionId": region_map[icon["regionId"]], "panelId": panel_map[icon["panelId"]], "mappingScope": f"exact physical root occurrence {definition['occurrenceId']} only"} for icon in asset["iconOccurrences"]]
        backlog_id = "CARD:" + asset["sourceSha256"][:16]
        backlog_row = backlog_by_id.get(backlog_id) or {}
        if backlog_row.get("sourcePath") != asset["sourcePath"] or backlog_row.get("sourceLocator") != asset["sourceSha256"]:
            raise AssertionError(f"Red Item backlog source tuple drift: {definition['occurrenceId']}")
        return {
            "redItemOccurrenceId": definition["occurrenceId"], "rootSequence": definition["rootSequence"], "familySequence": definition.get("familySequence"),
            "ttsRole": "redItemsDeck", "ttsDeckGuid": BASE_RED_ITEM_DECK_GUID, "ttsDeckType": "Deck", "ttsCardId": definition["ttsCardId"], "ttsCardGuid": definition["ttsCardGuid"], "customDeckId": definition["customDeckId"],
            "sourceSelector": selector, "sourceId": definition["sourceId"], "sourcePath": asset["sourcePath"], "sourceSha256": asset["sourceSha256"], "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS source-bound base redItemsDeck root occurrence {definition['rootSequence']} / full CardID {definition['ttsCardId']} / GUID {definition['ttsCardGuid']}",
            "sourceAssetKey": definition["assetKey"], "physicalClass": asset["physicalClass"], "batchDisposition": batch_disposition,
            "printedTitle": asset["printedTitle"], "typeLine": asset["typeLine"], "upperRight": asset["upperRight"], "printedBody": asset["printedBody"], "effectKind": asset["effectKind"], "namedIdentityRef": asset["namedIdentityRef"],
            "regions": physical_regions, "panels": physical_panels, "sentences": physical_sentences, "iconOccurrences": physical_icons,
            "printedBodyDigest": asset["printedBodyDigest"], "panelDigest": _digest(physical_panels), "iconDigest": _digest([{key: icon.get(key) for key in ("sequence", "cardLocationClass", "sourceToken", "semanticReferenceId", "mappingStatus")} for icon in physical_icons]),
            "semanticRuleId": definition["semanticRuleId"], "backlogUnitId": backlog_id, "corpusEvidencePath": CORPUS_PATH, "provenanceEvidencePath": PROVENANCE_PATH,
            "licensedCrosswalk": {"status": "not-asserted", "reason": "licensed rows remain independent; aggregate class/copy equality is not a title, body, key, order, or multiplicity crosswalk"},
            "officialCrosswalk": {"status": "not-asserted", "reason": "no checked official occurrence identifies this exact TTS full CardID/GUID physical copy; even Military Taser title equality supplies no copy identity"},
            "joinEvidence": {
                "identityJoin": "exact raw root physical occurrence and exact source-asset projection", "titleOnlyJoin": False, "colorOnlyJoin": False,
                "weaponOrAmmoAppearanceJoin": False, "bodyResemblanceJoin": False, "folderOnlyJoin": False, "sourceOrderOnlyJoin": False,
                "generatedCellOnlyJoin": False, "cardIdModuloJoin": False, "licensedKeyJoin": False,
                "basis": ["sole base redItemsDeck Lua role and exact raw root GUID", "raw saved DeckIDs plus contained full CardID/GUID occurrence", "exact CustomDeck ID, FaceURL, BackURL, parent deck, and source SHA-256", "for generated faces: exact sheet hash/grid/cell plus full selector"],
            },
        }

    regular_faces = [build_physical(row) for row in REGULAR_PHYSICAL_DEFINITIONS]
    excluded_heavy_faces = [build_physical(row) for row in EXCLUDED_HEAVY_DEFINITIONS]
    class_conflict_faces = [build_physical(row) for row in CLASS_CONFLICT_DEFINITIONS]

    for path_value, expected_refs, expected_key in (
        (RED_ITEM_RED_BACK_PATH, 25, "BackURL"), (RED_ITEM_YELLOW_BACK_PATH, 13, "BackURL"),
        (RED_ITEM_RED_SHEET_PATH, 8, "FaceURL"), (RED_ITEM_YELLOW_SHEET_PATH, 13, "FaceURL"),
    ):
        provenance_row = provenance_by_file[path_value.split("assets/tts-mod/extract/v2-dl/tree/", 1)[1]]
        if provenance_row.get("refs") != expected_refs or {row.get("key") for row in provenance_row.get("objects") or []} != {expected_key}:
            raise AssertionError(f"Red Item sheet/back provenance changed: {path_value}")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    official_ids = ["RB-P03-V01", "RB-P05-V01", "RB-P09-V01", "RB-P12-V02", "RB-P16-V02", "RB-P16-V03", "RB-P17-V01", "RB-P28-V02", "RB-P28-V03", "RB-P29-V01", "RB-P29-V03", "RB-P33-V03", "RB-P37-V02", "RB-P40-V02"]
    if any(occurrence_id not in visual_by_id for occurrence_id in official_ids):
        raise AssertionError("Red Item official visual occurrence missing")
    official_counterparts = [
        {"sourceOccurrenceId": "RB-P03-V01", "kind": "family-count-and-representative-card-images", "locator": "unprinted component page 3 / Item cards row", "visibleText": "90 Item cards (30 cards of each type)", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P05-V01", "kind": "finite-tactical-gear-inventory", "locator": "printed page 5 / Tactical Gear row", "visibleText": "20 Ammo and 20 Grenade tokens among 80 Tactical Gear tokens", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P09-V01", "kind": "setup-deck-placement", "locator": "printed page 9 / C. Remaining Components", "visibleText": "three Item decks shuffled separately face down with discard spaces", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P12-V02", "kind": "use-item-action-cost", "locator": "printed page 12 / Basic Actions List", "visibleText": "Use an Item costs 1 Action card", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P16-V02", "kind": "tactical-gear-placement", "locator": "printed page 16 / Gaining Tactical Gear", "visibleText": "Ammo uses red/Any compatible empty slots", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P16-V03", "kind": "ammo-token-face-key", "locator": "printed page 16 / Ammo", "visibleText": "Full and Half-full Ammo token faces", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P17-V01", "kind": "grenade-token-effect", "locator": "printed page 17 / Grenade Tokens", "visibleText": "Grenade token and its Corridor/Burst-die effect", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P28-V02", "kind": "red-item-search-icon", "locator": "printed page 28 / Search example", "visibleText": "Red Item icon maps Search to the Red deck", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P28-V03", "kind": "regular-item-anatomy", "locator": "printed page 28 / regular Item example", "visibleText": "vertical ONE USE ONLY regular Item anatomy", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P29-V01", "kind": "current-military-taser-heavy-face", "locator": "printed page 29 / Heavy Item example", "visibleText": "MILITARY TASER / ONE USE ONLY, HEAVY / materially different current effect", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P29-V03", "kind": "tactical-slot-color-key", "locator": "printed page 29 / slots", "visibleText": "red Ammo, purple Grenade, gray Any", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P33-V03", "kind": "ammo-spend-state", "locator": "printed page 33 / Spend", "visibleText": "Full to Half-full, then Half-full discard", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P37-V02", "kind": "anti-aircraft-hidden-state-key", "locator": "printed page 37 / Anti-Aircraft", "visibleText": "ACTIVE and INACTIVE token faces; hidden top-token state", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
        {"sourceOccurrenceId": "RB-P40-V02", "kind": "icon-glossary", "locator": "printed page 40", "visibleText": "Red Item, Ammo, Grenade, Computer, Malfunction and related exact icon names", "exactRegularRedRulesFace": False, "exactTtsPhysicalCrosswalk": False},
    ]

    faq_units = [unit for page in faq["pages"] for unit in page.get("units", [])]
    faq_by_id = {unit["sourceUnitId"]: unit for unit in faq_units}
    relevant_faq_ids = ["FQ-P02-U04", "FQ-P02-U10", "FQ-P03-U04", "FQ-P03-U06", "FQ-P03-U07", "FQ-P03-U08"]
    relevant_faq = [{"sourceUnitId": source_id, "applicability": faq_by_id[source_id]["applicability"], "printedText": faq_by_id[source_id]["printedText"]} for source_id in relevant_faq_ids]
    if any(row["applicability"] not in {"base-game", "base-game-additional-mode"} for row in relevant_faq):
        raise AssertionError("Red Item FAQ applicability changed")
    excluded_faq = [unit["sourceUnitId"] for unit in faq_units if unit.get("applicability", "").startswith("expansion") and re.search(r"Item|Ammo|Grenade|Anti-Aircraft|Health|Oxygen", unit.get("printedText", ""), re.I)]

    regular_asset_keys = {row["assetKey"] for row in REGULAR_PHYSICAL_DEFINITIONS}
    selected_regular_assets = [row for row in source_asset_rows if row["assetKey"] in regular_asset_keys]
    red_gap_assets = [row for row in source_asset_rows if row["selectedDisposition"] == "red-selector-gap"]
    cross_family_gap_assets = [row for row in source_asset_rows if row["selectedDisposition"] == "cross-family-gap-excluded"]
    excluded_asset_keys = {row["assetKey"] for row in [*EXCLUDED_HEAVY_DEFINITIONS, *CLASS_CONFLICT_DEFINITIONS]}
    excluded_assets = [row for row in source_asset_rows if row["assetKey"] in excluded_asset_keys]
    face_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in selected_regular_assets})
    variant_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in red_gap_assets})
    excluded_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in excluded_assets})
    cross_family_unit_ids = sorted({"CARD:" + row["sourceSha256"][:16] for row in cross_family_gap_assets if row["rulesTextPresent"]})
    cross_family_pending_ids = [unit_id for unit_id in cross_family_unit_ids if (backlog_by_id.get(unit_id) or {}).get("status") == "pending"]
    cross_family_covered_by_yellow_ids = [unit_id for unit_id in cross_family_unit_ids if (backlog_by_id.get(unit_id) or {}).get("status") == "pilot-covered"]
    overlapping_unit_ids = [
        "RULE:ACT-ITEM-001", "RULE:ACT-MOVE-001", "RULE:ACT-EXPLORE-001", "RULE:ACT-TRADE-001", "RULE:ACT-TACTICAL-001",
        "RULE:ITM-001", "RULE:ITM-002", "RULE:ITM-003", "RULE:ITM-004", "RULE:ITM-005", "RULE:ITM-006", "RULE:ITM-008",
        *[f"FAQ:{source_id}" for source_id in relevant_faq_ids], *[f"VIS:{source_id}" for source_id in official_ids],
    ]
    linked_unit_ids = sorted(set(face_unit_ids + variant_unit_ids + overlapping_unit_ids))
    if any(unit_id not in backlog_by_id for unit_id in linked_unit_ids + excluded_unit_ids + cross_family_unit_ids):
        raise AssertionError("Red Item backlog obligation ID missing")

    title_multiplicity = dict(sorted(Counter(row["printedTitle"] for row in regular_faces).items()))
    asset_multiplicity = dict(sorted(Counter(row["sourceAssetKey"] for row in regular_faces).items()))
    root_class_multiplicity = dict(sorted(Counter(row["physicalClass"] for row in [*regular_faces, *excluded_heavy_faces, *class_conflict_faces]).items()))
    regular_icons = [icon for face in regular_faces for icon in face["iconOccurrences"]]
    red_gap_icons = [icon for asset in red_gap_assets for icon in asset["iconOccurrences"]]
    cross_family_gap_icons = [icon for asset in cross_family_gap_assets for icon in asset["iconOccurrences"]]
    class_conflict_icons = [icon for face in class_conflict_faces for icon in face["iconOccurrences"]]
    heavy_icons = [icon for face in excluded_heavy_faces for icon in face["iconOccurrences"]]

    counts = {
        "rootPhysicalOccurrences": 30, "regularPhysicalFaceOccurrences": len(regular_faces), "excludedHeavyPhysicalOccurrences": len(excluded_heavy_faces),
        "physicalClassConflictOccurrences": len(class_conflict_faces), "currentOfficialLicensedHeavyAggregate": 9,
        "uniqueRegularPrintedTitles": len(title_multiplicity), "uniqueSelectedRegularFaceAssets": len(selected_regular_assets), "sourceFaceAssets": len(source_asset_rows),
        "rulesBearingSourceFaceAssets": sum(row["rulesTextPresent"] for row in source_asset_rows), "nonRulesSourceCells": sum(not row["rulesTextPresent"] for row in source_asset_rows),
        "generatedRegularPhysicalFaceOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] for row in regular_faces), "directRegularPhysicalFaceOccurrences": sum(not row["sourceSelector"]["generatedSpriteSheetCell"] for row in regular_faces),
        "generatedClassConflictPhysicalOccurrences": sum(row["sourceSelector"]["generatedSpriteSheetCell"] for row in class_conflict_faces), "directHeavyPhysicalOccurrences": sum(not row["sourceSelector"]["generatedSpriteSheetCell"] for row in excluded_heavy_faces),
        "sourceSheets": 2, "sourceSheetCells": 12, "selectedGeneratedCells": 5, "redSelectorGapCells": len(red_gap_assets), "crossFamilySelectorGapCells": len(cross_family_gap_assets),
        "rootBackAssets": 2, "redBackPhysicalSelectors": 24, "yellowBackPhysicalSelectors": 6, "redBackGlobalSelectorReferences": 25, "yellowBackGlobalSelectorReferences": 13,
        "redSheetGlobalSelectorReferences": 8, "yellowSheetGlobalSelectorReferences": 13, "rootCustomDeckEntries": len(root_custom),
        "physicalRegions": sum(len(row["regions"]) for row in regular_faces), "operativeRegions": sum(sum(region["operative"] for region in row["regions"]) for row in regular_faces),
        "physicalPanels": sum(len(row["panels"]) for row in regular_faces), "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in regular_faces),
        "oneUseHeadingOccurrences": len(regular_faces), "specialWeaponHeadingOccurrences": sum("SPECIAL WEAPON" in row["typeLine"] for row in regular_faces),
        "branchSeparatorHeadingOccurrences": sum(sum(panel["role"] == "branch-separator" for panel in row["panels"]) for row in regular_faces),
        "useDiscardPassiveReactionHeadingOccurrences": 0, "printedSentenceOccurrences": sum(len(row["sentences"]) for row in regular_faces),
        "physicalFunctionalIconOccurrences": len(regular_icons), "physicalMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in regular_icons), "physicalUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in regular_icons),
        "redSelectorGapFunctionalIconOccurrences": len(red_gap_icons), "redSelectorGapMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in red_gap_icons), "redSelectorGapUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in red_gap_icons),
        "crossFamilyGapFunctionalIconOccurrences": len(cross_family_gap_icons), "classConflictFunctionalIconOccurrences": len(class_conflict_icons), "excludedHeavyFunctionalIconOccurrences": len(heavy_icons),
        "licensedDigitalOccurrences": len(bga_rows), "licensedDigitalPhysicalCopies": sum(row["nbr"] for row in bga_rows), "licensedRegularOccurrences": sum(not row["heavy"] and not row["armor"] for row in bga_rows),
        "licensedRegularPhysicalCopies": sum(row["nbr"] for row in bga_rows if not row["heavy"] and not row["armor"]), "licensedHeavyOccurrences": sum(row["heavy"] or row["armor"] for row in bga_rows), "licensedHeavyPhysicalCopies": sum(row["nbr"] for row in bga_rows if row["heavy"] or row["armor"]),
        "officialInventoryCopiesPerType": 30, "officialVisibleRegularFaceOccurrences": 0, "officialVisibleHeavySameTitleOccurrences": 1, "officialVisibleBackOccurrences": 0, "officialFamilyVisualOccurrences": len(official_counterparts),
        "baseApplicableFaqOccurrences": len(relevant_faq), "excludedExpansionFaqOccurrences": len(excluded_faq),
        "backlogTuples": len(face_unit_ids) + len(variant_unit_ids), "backlogPhysicalFaceLinks": len(regular_faces), "backlogObligationsLinked": len(linked_unit_ids), "semanticPhysicalFaceRecords": len(regular_faces),
    }

    return {
        "schemaVersion": 1, "recordType": "semantic-red-item-source-index",
        "scope": "entire mechanically derived base redItemsDeck root: all 30 physical children retained, partitioned into 21 source-clear regular faces, three explicit Heavy REMOTE DETONATOR faces, and six MILITARY TASER physical-class-conflict faces; two source sheets, seven unselected selector-gap cells, two backs, official/FAQ evidence, and nine licensed rows remain independent",
        "derivationPolicy": "Derive only from the sole base redItemsDeck Lua role and exact raw root GUID, saved DeckIDs, contained full CardID/GUID/CustomDeck/FaceURL/BackURL tuples, and exact generated sheet/hash/grid/cell evidence. Never join by title, Red color, weapon/ammo appearance, body similarity, folder/order/cell, CardID modulo, licensed key, or multiplicity. Current official/ licensed Heavy classification does not rewrite the six portrait TTS Military Taser occurrences.",
        "counts": counts,
        "rootDeckEvidence": {
            "sourceId": RED_ITEM_ROOT_SOURCE_ID, "ttsRole": "redItemsDeck", "rootGuid": BASE_RED_ITEM_DECK_GUID, "rootType": "Deck", "rootGmNotes": "reditemDiscard",
            "rawSavePath": RAW_SAVE_PATH, "rawSaveSha256": raw_save_sha, "luaRolePath": "assets/tts-mod/extract/v2/lua_roles.json", "objectsPath": "assets/tts-mod/extract/v2/objects.json",
            "savedDeckIds": raw_deck_ids,
            "fullContainedSelectors": [{"rootSequence": row["rootSequence"], "fullCardId": row["ttsCardId"], "guid": row["ttsCardGuid"], "customDeckId": row["customDeckId"], "batchDisposition": row["disposition"]} for row in ROOT_PHYSICAL_DEFINITIONS],
            "customDeckTuples": {key: {"faceUrl": value[0], "backUrl": value[1], "columns": value[2], "rows": value[3]} for key, value in sorted(expected_custom.items())},
            "rootOrderIsGameplayOrder": False, "reason": "official setup shuffles each Item deck separately; saved sequence is provenance only",
        },
        "familyCountEvidence": {
            "official": {"count": 30, "scope": "Item cards of each type", "source": "RB-P03-V01 / rulebook_text lines 520–521"},
            "tts": {"rootChildren": 30, "sourceClearRegularIncluded": 21, "explicitHeavyExcluded": 3, "physicalClassConflictExcluded": 6, "classMultiplicity": root_class_multiplicity},
            "licensedDigital": {"deckRedRows": len(bga_rows), "declaredCopies": 30, "regularCopies": 21, "heavyCopies": 9, "physicalIdentityCrosswalkAsserted": False},
            "reconciliation": "Official inventory, the exact root, and licensed aggregate each retain 30. Licensed 21/9 agrees with 21 source-clear regular plus all nine current Heavy candidates, but the six exact TTS Military Taser occurrences remain portrait SPECIAL WEAPON variants under SEM-Q-047; aggregate equality is not a copy crosswalk.",
            "backlog": {
                "faceUnitIds": face_unit_ids, "variantUnitIds": variant_unit_ids, "excludedHeavyOrConflictUnitIds": excluded_unit_ids, "crossFamilyPendingUnitIds": cross_family_pending_ids,
                "crossFamilyCoveredByYellowUnitIds": cross_family_covered_by_yellow_ids,
                "overlappingUnitIds": sorted(overlapping_unit_ids), "linkedUnitIds": linked_unit_ids, "faceTupleCount": len(face_unit_ids), "variantTupleCount": len(variant_unit_ids),
                "physicalFaceLinkCount": len(regular_faces), "obligationCount": len(linked_unit_ids),
            },
        },
        "titleMultiplicity": title_multiplicity, "selectedAssetMultiplicity": asset_multiplicity,
        "sourceSheets": [
            {"sourceId": RED_ITEM_RED_SHEET_SOURCE_ID, "occurrenceId": "TTS-RED-ITEM-PARENT-SHEET-36", "sourcePath": RED_ITEM_RED_SHEET_PATH, "sourceSha256": _sha(repo / RED_ITEM_RED_SHEET_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS base Red Item CustomDeck 36 parent 4x2 face sheet", "sourceSelector": {"key": "FaceURL", "rootGuid": BASE_RED_ITEM_DECK_GUID, "customDeckId": "36", "url": RED_SHEET_FACE_URL, "grid": {"columns": 4, "rows": 2}, "sideRole": "parent-sheet-provenance-not-rules-face"}, "globalSelectorReferences": 8, "rootSelectedCells": [1, 4, 6, 7], "selectorGapCells": [0, 2, 3, 5], "separateRulesFace": False},
            {"sourceId": RED_ITEM_YELLOW_SHEET_SOURCE_ID, "occurrenceId": "TTS-RED-ITEM-CROSS-FAMILY-PARENT-SHEET-35", "sourcePath": RED_ITEM_YELLOW_SHEET_PATH, "sourceSha256": _sha(repo / RED_ITEM_YELLOW_SHEET_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS cross-family CustomDeck 35 parent 2x2 face sheet selected by the Red root only at cell 0", "sourceSelector": {"key": "FaceURL", "rootGuid": BASE_RED_ITEM_DECK_GUID, "customDeckId": "35", "url": YELLOW_SHEET_FACE_URL, "grid": {"columns": 2, "rows": 2}, "sideRole": "cross-family-parent-sheet-provenance-not-rules-face"}, "globalSelectorReferences": 13, "redRootSelectedCells": [0], "crossFamilySelectorGapCells": [1, 2, 3], "separateRulesFace": False},
        ],
        "rootBacks": [
            {"sourceId": RED_ITEM_RED_BACK_SOURCE_ID, "occurrenceId": "TTS-RED-ITEM-SHARED-RED-BACK", "sourcePath": RED_ITEM_RED_BACK_PATH, "sourceSha256": _sha(repo / RED_ITEM_RED_BACK_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS base Red Item shared non-operative back", "sourceSelector": {"key": "BackURL", "rootGuid": BASE_RED_ITEM_DECK_GUID, "url": RED_BACK_URL, "sideRole": "shared-non-operative-red-item-back"}, "rootPhysicalSelectors": 24, "globalSelectorReferences": 25, "visibleText": "ITEM", "rulesTextPresent": False, "separateRulesFace": False},
            {"sourceId": RED_ITEM_YELLOW_BACK_SOURCE_ID, "occurrenceId": "TTS-RED-ITEM-CROSS-FAMILY-YELLOW-BACK", "sourcePath": RED_ITEM_YELLOW_BACK_PATH, "sourceSha256": _sha(repo / RED_ITEM_YELLOW_BACK_PATH), "sourceAuthority": "source-bound-component-scan", "sourceVersion": "TTS Yellow Item back used by six Red-root Military Taser selectors", "sourceSelector": {"key": "BackURL", "rootGuid": BASE_RED_ITEM_DECK_GUID, "customDeckId": "35", "url": YELLOW_BACK_URL, "sideRole": "cross-family-non-operative-yellow-item-back"}, "rootPhysicalSelectors": 6, "rootPlusPhysicalSelectorReferences": 7, "globalSelectorReferences": 13, "visibleText": "ITEM", "rulesTextPresent": False, "separateRulesFace": False},
        ],
        "sourceFaceAssets": source_asset_rows, "faces": regular_faces, "excludedHeavyFaces": excluded_heavy_faces, "physicalClassConflictFaces": class_conflict_faces,
        "licensedDigitalOccurrences": bga_rows, "officialVisibleCounterparts": official_counterparts,
        "officialRulebookTextOccurrences": [
            {"locator": "unprinted page 3 / lines 520–521", "text": "90 Item cards (30 cards of each type)"},
            {"locator": "printed page 9 / lines 2593–2600", "text": "Shuffle red, green, and yellow Item decks separately face down and leave discard space."},
            {"locator": "printed pages 16–17 / lines 3469–3548, 3639–3650", "text": "Tactical Gear use/gain, finite supply, Ammo reload, and exact Grenade Corridor/Burst-die procedure."},
            {"locator": "printed page 17 / lines 3530–3548, 3665–3673", "text": "Whole/local/component-limit rules and voluntary discard destinations."},
            {"locator": "printed pages 28–29 / lines 4849–5103", "text": "Search, regular Item/Backpack, One Use Only, Heavy, Interplay, and Trade rules."},
            {"locator": "printed page 33 / lines 5607–5620", "text": "Full Ammo spends to Half-full; Half-full spends to discard."},
            {"locator": "printed page 37 / lines 5953–5979", "text": "Two Anti-Aircraft tokens start face down in random order; inspect/reorder is secret, claims may be lies, tokens cannot be shown, and top ACTIVE/INACTIVE controls Lander resolution."},
        ],
        "faqSearchClosure": {"baseApplicableOccurrences": relevant_faq, "excludedExpansionOccurrences": excluded_faq},
        "exclusions": {
            "otherColorDecks": [{"role": "greenItemsDeck", "guid": "17400d"}, {"role": "yellowItemsDeck", "guid": "fe68f3"}],
            "heavyEquipmentStarting": {"startItemDeckRole": "startItemDeck", "startItemDeckGuid": "f71196", "rootHeavyOccurrenceIds": [row["redItemOccurrenceId"] for row in excluded_heavy_faces], "rootClassConflictOccurrenceIds": [row["redItemOccurrenceId"] for row in class_conflict_faces]},
            "tacticalGear": "Red Ammo tokens, Grenade tokens, their pools/slots, and weapon/ammo artwork are not Red Item card faces.",
            "parentBackGaps": {"parentSheets": [RED_ITEM_RED_SHEET_PATH, RED_ITEM_YELLOW_SHEET_PATH], "backs": [RED_ITEM_RED_BACK_PATH, RED_ITEM_YELLOW_BACK_PATH], "redSelectorGapCells": [0, 2, 3, 5], "crossFamilyGapCells": [1, 2, 3]},
            "other": "Starting/Equipment/Heavy cards outside exact root selectors, expansion/prototype decks, Tactical Gear, ammo tokens, overlays, placeholders, duplicate references, parent sheets, backs, and non-rules cells never enter the 21 regular-face count.",
        },
        "fidelityBoundaries": {
            "rootVersusFamily": "All 30 exact root children remain indexed. Only 21 source-clear regular occurrences dispatch here; three explicit Heavy faces and six Military Taser class-conflict faces remain excluded from regular/Backpack effect semantics.",
            "militaryTaserBoundary": "Six exact root selectors use portrait TTS SPECIAL WEAPON bytes and a Yellow back. The official page-29 and licensed same-title occurrences are Heavy with materially different effects; title and aggregate multiplicity establish no identity or rewrite.",
            "backBoundary": "Twenty-four children use the Red back and six Military Taser children use a Yellow back. Neither back is a rules face and neither color assigns card effect semantics.",
            "glyphBoundary": "Four selected regular physical upper-right occurrences retain explicit all-glossary no-matches under SEM-Q-046. The separately matched Exploring Drone Not In Combat occurrence creates no position/color/title-wide alias.",
            "variantBoundary": "Four unselected Red-sheet cells, three cross-family Yellow-sheet cells, all nine licensed rows, and every scan/current wording difference remain independent. No selector gap is repaired from title, body, art, source cell, BGA key, or expected game logic.",
            "officialBoundary": "Official rules control count, class definitions, storage/use, Tactical Gear/Grenade/Anti-Aircraft procedures, and exact official occurrences only. No checked official visual identifies a TTS GUID copy or an exact regular Red face/back.",
        },
    }


def red_item_source_registry_rows(source_index: dict) -> list[dict]:
    rows = [{
        "sourceId": RED_ITEM_ROOT_SOURCE_ID, "authority": "source-bound-component-scan", "version": "TTS raw base redItemsDeck root / GUID 9027ed",
        "path": RAW_SAVE_PATH, "sha256": source_index["rootDeckEvidence"]["rawSaveSha256"], "occurrenceId": "TTS-RED-ITEM-ROOT-DECK",
        "evidenceIndexPath": "docs/rules/semantics/red-item-source-index.json", "evidenceRecord": "rootDeckEvidence", "provenanceIndexPath": "assets/tts-mod/extract/v2/lua_roles.json",
    }]
    for face in [*source_index["faces"], *source_index["excludedHeavyFaces"], *source_index["physicalClassConflictFaces"]]:
        rows.append({"sourceId": face["sourceId"], "authority": face["sourceAuthority"], "version": face["sourceVersion"], "path": face["sourcePath"], "sha256": face["sourceSha256"], "occurrenceId": face["redItemOccurrenceId"], "evidenceIndexPath": face["corpusEvidencePath"], "evidenceRecord": face["sourceSha256"], "provenanceIndexPath": face["provenanceEvidencePath"]})
    for sheet in source_index["sourceSheets"]:
        rows.append({"sourceId": sheet["sourceId"], "authority": sheet["sourceAuthority"], "version": sheet["sourceVersion"], "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"], "evidenceIndexPath": VISION_PROGRESS_PATH, "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for back in source_index["rootBacks"]:
        rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for asset in source_index["sourceFaceAssets"]:
        if not asset["sourceId"]:
            continue
        family = "36" if asset["sourceSheetId"] == RED_ITEM_RED_SHEET_SOURCE_ID else "35"
        rows.append({"sourceId": asset["sourceId"], "authority": "source-bound-component-scan", "version": f"TTS source-sheet selector-gap occurrence / CustomDeck {family} / cell {asset['generatedCell']}", "path": asset["sourcePath"], "sha256": asset["sourceSha256"], "occurrenceId": f"TTS-RED-ITEM-{'VARIANT' if family == '36' else 'CROSS-FAMILY'}-{family}-CELL-{asset['generatedCell']:02d}", "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": asset["sourceSha256"], "provenanceIndexPath": VISION_PROGRESS_PATH})
    repo = Path(__file__).resolve().parents[1]
    rows.append({"sourceId": BGA_RED_ITEM_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / ITEMS_DATA deck-red rows", "path": BGA_ITEMS_PATH, "sha256": _sha(repo / BGA_ITEMS_PATH), "occurrenceId": "ITEMS_DATA:deck-red", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "ITEMS_DATA"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None, visibility: str = "public") -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": visibility}


def build_red_item_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation, exploration_rule_ids: list[str]) -> list[dict]:
    del repo
    records = []
    face_by_occurrence = {row["redItemOccurrenceId"]: row for row in source_index["faces"]}

    records.append(record(
        "SEM-RED-ITEM-DECK-001", "Finite Red Item root and source-clear regular-family boundary", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [
            assertion("SA-RI-DECK-RB", "SRC-RULEBOOK", "unprinted page 3; printed pages 9 and 28 / RB-P03-V01, RB-P09-V01, RB-P28-V02 / lines 520–521,2593–2600,4849–4865", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "The official Red Item type has 30 cards. Shuffle its deck separately face down, draw by Red Item icons, and return unchosen Search cards privately to the Red deck bottom.", "docs/rules/semantics/red-item-source-index.json:familyCountEvidence"),
            assertion("SA-RI-DECK-TTS", RED_ITEM_ROOT_SOURCE_ID, "raw root GUID 9027ed / exact ordered DeckIDs and 30 contained full CardID/GUID selectors", ["informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "sourceVariants", "unresolvedQuestionRefs"], "The exact root contains 30 physical children: 21 source-clear regular occurrences, three explicit Heavy REMOTE DETONATOR occurrences, and six Military Taser source-class-conflict occurrences.", "docs/rules/semantics/red-item-source-index.json:rootDeckEvidence"),
        ],
        ["term.item", "term.regular-item", "icon.redItem"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-RI-DECK", "tax.entity.component.card.item", "when-triggered", "once-at-setup-plus-per-source-requested-Red-draw/return/discard"), [participant("P-RULES", "rules-system"), participant("P-DRAWING-CHARACTER", "affected", "tax.entity.agent.character")], "must", [], [],
        [{"informationId": "I-RI-DECK", "subjectRef": "30 exact root cards, two back families, 21 source-clear regular faces, excluded Heavy/class-conflict faces, shuffled order, and remaining fronts", "audience": "hidden-from-all fronts/order; public deck/back/count/discard locations", "revealTrigger": "owner-private Search inspection, gain, or source-defined use", "secrecy": "no client, log, accessibility output, or spectator may expose unselected fronts/order"}], [],
        [_target("T-RI-DECK-CARD", ["tax.entity.component.card.item"], mode="random", minimum=0, maximum=1)],
        [
            operation("S01", 1, "shuffle", "must", "P-RULES", "all 30 exact Red-root physical children without changing their two BackURL or physical-class evidence", ["SA-RI-DECK-RB", "SA-RI-DECK-TTS"], repeat={"rootPhysicalCardCount": 30, "regularBatchFaceCount": 21, "excludedHeavyCount": 3, "physicalClassConflictCount": 6}),
            operation("S02", 2, "transition-zone", "must", "P-RULES", "shuffled Red root face down", ["SA-RI-DECK-RB"], transition={"from": "tax.scaffold.supply-pool", "to": "tax.scaffold.zone.deck"}),
            operation("S03", 3, "set-state", "must", "P-RULES", "separate empty Red Item discard pile", ["SA-RI-DECK-RB"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "whether a requested Red draw has a remaining physical card", ["SA-RI-DECK-RB", "SA-RI-DECK-TTS"], target_ref="T-RI-DECK-CARD"),
            operation("S05", 5, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-040 color-deck exhaustion/recycle and multi-draw shortage handling", ["SA-RI-DECK-RB", "SA-RI-DECK-TTS"], conditions=["a Red draw is requested with insufficient cards"], target_ref="T-RI-DECK-CARD"),
            operation("S06", 6, "draw-random", "if-able", "P-RULES", "one exact physical Red-root card into the caller's source-defined private candidate/gain zone", ["SA-RI-DECK-RB", "SA-RI-DECK-TTS"], conditions=["a physical card remains"], target_ref="T-RI-DECK-CARD"),
            operation("S07", 7, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-047 class/storage handling only if the drawn exact occurrence is one of six Military Taser conflict selectors", ["SA-RI-DECK-RB", "SA-RI-DECK-TTS"], conditions=["drawn occurrence is a Military Taser class-conflict face"]),
            operation("S08", 8, "evaluate-condition", "must", "P-RULES", "unchosen Search cards return to Red deck bottom; Used/voluntarily discarded Items enter the separate Item discard pile", ["SA-RI-DECK-RB"]),
        ],
        {"policy": "source-limited-components", "unit": "one requested physical Red draw or exact lifecycle transition", "onImpossible": "SEM-Q-040 prohibits invented reshuffles/shortage assignment; SEM-Q-047 prohibits selecting a Military Taser storage/effect class from title or aggregate evidence"},
        {"kind": "persistent-finite-deck-and-discard-state"}, {"policy": "one finite 30-card root; only 21 source-clear regular occurrences dispatch here; no title/licensed-row dispatch"}, [], ["SEM-Q-040", "SEM-Q-047"], []))

    records.append(record(
        "SEM-RED-ITEM-ONE-USE-001", "One Use Only lifecycle for source-clear regular Red Items", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-RI-ONE-USE-RB", "SRC-RULEBOOK", "printed page 29 / lines 4933–4951", ["timing", "informationPolicy", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "One Use Only Items are discarded when Used.", "docs/rulebooks/rulebook_text.txt:lines 4933–4951"), *[assertion(f"SA-RI-ONE-USE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['redItemOccurrenceId']} / exact printed trait", ["timing", "operations", "duration", "stacking"], face["typeLine"], f"docs/rules/semantics/red-item-source-index.json:{face['redItemOccurrenceId']}.typeLine") for face in source_index["faces"]]],
        ["term.item", "term.regular-item"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-RI-ONE-USE", "tax.entity.component.card.item.regular", "when-triggered", "once-when-one-exact-source-clear-regular-Red-Item-is-Used"), [participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-RI-ONE-USE", "subjectRef": "used exact physical Red Item, effect, discard destination, and sibling Backpack cards", "audience": "used Item public; discard face orientation source-unspecified; siblings owner-private", "revealTrigger": "SEM-Q-039", "secrecy": "discarding one copy never reveals or collapses sibling copies"}], [], [_target("T-RI-ONE-USE", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1)],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-039 exact One Use Only transition point", ["SA-RI-ONE-USE-RB"], target_ref="T-RI-ONE-USE"), operation("S02", 2, "transition-zone", "must", "P-RULES", "used exact regular Red Item", ["SA-RI-ONE-USE-RB"], conditions=["source-defined discard point under SEM-Q-039 is reached"], target_ref="T-RI-ONE-USE", transition={"from": "owned Backpack or card-in-resolution zone", "to": "tax.scaffold.zone.discard-pile"}), operation("S03", 3, "evaluate-condition", "must", "P-RULES", "discarded copy cannot be Used again absent an explicit future return; no checked Red rule returns or reshuffles it", ["SA-RI-ONE-USE-RB"])],
        {"policy": "ordered-complete", "unit": "one exact used regular Red Item", "onImpossible": "do not remove from game, return, reshuffle, destroy, or discard a different copy; relative timing remains SEM-Q-039"}, {"kind": "instantaneous-transition-ending-that-copy's-availability"}, {"policy": "one physical copy per use; same-title copies remain distinct"}, [], ["SEM-Q-039"], []))

    immediate_faces = [face for face in source_index["faces"] if face["sourceAssetKey"] in {"direct-ammo", "direct-grenade"}]
    immediate_assertions = [assertion(f"SA-RI-IMMEDIATE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", face["sourceId"], f"{face['redItemOccurrenceId']} / printed immediate-use sentence", ["timing", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "You can use this Item for free\nimmediately after gaining it.", f"docs/rules/semantics/red-item-source-index.json:{face['redItemOccurrenceId']}.sentences") for face in immediate_faces]
    records.append(record(
        "SEM-RED-ITEM-IMMEDIATE-USE-001", "Optional free immediate use of exact Ammo Magazine or Grenade occurrences", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [*immediate_assertions, assertion("SA-RI-IMMEDIATE-FAQ", "SRC-FAQ", "Items and tactical gear / FQ-P03-U04", ["timing", "operations", "duration", "unresolvedQuestionRefs"], "A traded Item is gained and may be used immediately when its exact text permits.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U04")],
        ["term.item", "term.regular-item"], ["tax.entity.component.card.item.regular"], [],
        timing("TW-RI-IMMEDIATE", "tax.entity.component.card.item.regular", "immediately-after-gain", "once-per-gain-of-one-of-twelve-exact-physical-occurrences"), [participant("P-RECIPIENT", "actor", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "may", [],
        [decision("D-RI-IMMEDIATE", "P-OWNER", "player-choice", 0, 1, True, "public-on-use", ["use this exact gained Item immediately for free", "decline and retain it in the Backpack"])],
        [{"informationId": "I-RI-IMMEDIATE", "subjectRef": "gained exact occurrence, immediate choice, branch/target, and sibling gained Items", "audience": "owner-private until use; public on use", "revealTrigger": "exercise immediate window", "secrecy": "declining does not reveal a retained card beyond source-authorized gain/Trade visibility"}], [],
        [_target("T-RI-IMMEDIATE-ITEM", ["tax.entity.component.card.item.regular"], selector="P-OWNER", mode="deterministic-exact-face-filter", minimum=1, maximum=1, visibility="owner-private-until-use")],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "gained physical occurrence is one of the exact direct Ammo Magazine/Grenade selectors", [row["assertionId"] for row in immediate_assertions], target_ref="T-RI-IMMEDIATE-ITEM"), operation("S02", 2, "choose", "may", "P-OWNER", "exercise or decline this exact immediate window", [*[row["assertionId"] for row in immediate_assertions], "SA-RI-IMMEDIATE-FAQ"], decision_ref="D-RI-IMMEDIATE", target_ref="T-RI-IMMEDIATE-ITEM"), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-045 order when one gain/Trade produces multiple immediate windows", [*[row["assertionId"] for row in immediate_assertions], "SA-RI-IMMEDIATE-FAQ"], conditions=["multiple immediate-use windows arise"]), operation("S04", 4, "invoke-process", "may", "P-RECIPIENT", "Use the exact Item with ordinary one-Action-card cost waived only for this immediate window", [row["assertionId"] for row in immediate_assertions], conditions=["owner exercises this window under SEM-Q-045"], decision_ref="D-RI-IMMEDIATE", target_ref="T-RI-IMMEDIATE-ITEM", invoke="SEM-USE-ITEM-001", notes="Printed immediate timing is not a Reaction; ordinary restrictions, branch legality, visibility, and One Use Only lifecycle still apply.")],
        {"policy": "one-optional-window-per-exact-gain", "unit": "one gained exact physical occurrence", "onImpossible": "declining is legal; free permission expires after the window; SEM-Q-045 prohibits merged/automatic ordering"}, {"kind": "instantaneous-optional-followup-window"}, {"policy": "each physical copy grants at most one window for that gain"}, [], ["SEM-Q-045"], []))

    records.append(record(
        "SEM-AMMO-TOKEN-LIFECYCLE-001", "Ammo token reload and Full/Half-full spend lifecycle", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-RI-AMMO-RB", "SRC-RULEBOOK", "printed pages 16, 17, 29, and 33 / RB-P16-V03, RB-P29-V03, RB-P33-V03 / lines 3476–3490,5058–5078,5607–5620", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "Using Ammo chooses a Weapon and moves the token from a compatible Tactical Gear slot onto that Weapon; loaded Ammo cannot move between Weapons. Spending Full flips it Half-full; spending Half-full discards it.", "docs/rulebooks/rulebook_text.txt:lines 3476–3490,5607–5620")],
        ["icon.ammoToken", "term.tactical-gear-token", "term.tactical-gear-slot", "term.weapon"], ["tax.entity.component.token.tactical-gear.ammo", "tax.entity.component.slot.tactical-gear", "tax.entity.component.card.item.weapon"], [],
        timing("TW-RI-AMMO", "tax.entity.component.token.tactical-gear.ammo", "when-triggered", "per-reload-or-source-instructed-spend"), [participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "mixed",
        [condition("C-RI-AMMO-RELOAD", "all", [{"predicate": "selected Ammo is not already loaded"}, {"predicate": "selected Weapon has an eligible empty Ammo slot"}], ["SA-RI-AMMO-RB"])],
        [decision("D-RI-AMMO-WEAPON", "P-OWNER", "player-choice", 1, 1, False, "public-on-placement", ["eligible owned Weapons with an empty Ammo slot"])],
        [{"informationId": "I-RI-AMMO", "subjectRef": "Ammo physical token, Full/Half-full side, source slot, chosen Weapon, and spend result", "audience": "public", "revealTrigger": "continuous/use/spend", "secrecy": "none"}], [],
        [_target("T-RI-AMMO", ["tax.entity.component.token.tactical-gear.ammo"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-RI-AMMO-WEAPON", ["tax.entity.component.card.item.weapon"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1)],
        [operation("S01", 1, "select-target", "must", "P-OWNER", "one eligible Weapon for Reload", ["SA-RI-AMMO-RB"], conditions=["Ammo is Used to Reload"], decision_ref="D-RI-AMMO-WEAPON", target_ref="T-RI-AMMO-WEAPON"), operation("S02", 2, "transition-zone", "must", "P-RULES", "selected Ammo token onto selected Weapon Ammo slot", ["SA-RI-AMMO-RB"], conditions=["Ammo is Used to Reload"], target_ref="T-RI-AMMO", transition={"from": "compatible owned Tactical Gear slot", "to": "selected Weapon Ammo slot"}), operation("S03", 3, "evaluate-condition", "must", "P-RULES", "loaded Ammo cannot be moved or swapped between Weapons", ["SA-RI-AMMO-RB"]), operation("S04", 4, "set-state", "must", "P-RULES", "Full Ammo token becomes Half-full", ["SA-RI-AMMO-RB"], conditions=["a source spends a Full Ammo token"], target_ref="T-RI-AMMO"), operation("S05", 5, "transition-zone", "must", "P-RULES", "spent Half-full Ammo token back to the finite supply pool", ["SA-RI-AMMO-RB"], conditions=["a source spends a Half-full Ammo token"], target_ref="T-RI-AMMO", transition={"from": "Weapon Ammo slot", "to": "tax.scaffold.supply-pool"})],
        {"policy": "source-conditional-steps", "unit": "one exact Ammo reload or spend", "onImpossible": "Reload requires an eligible Weapon slot; Full and Half-full spending follow distinct deterministic transitions"}, {"kind": "persistent-two-sided-token-and-slot-state"}, {"policy": "one physical token per slot; one side at a time"}, [], [], []))

    records.append(record(
        "SEM-GRENADE-TOKEN-EFFECT-001", "Grenade token Corridor effect without Burst-Action inference", "source-backed", "procedure", "official-errata", "source-composed",
        [assertion("SA-RI-GRENADE-RB", "SRC-RULEBOOK", "printed page 17 / RB-P17-V01 / lines 3639–3650", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "Choose an adjacent Corridor, roll a Burst die, add 2, and deal that many Hits there; the special Burst face has no effect and the roll is not Bursting, so Weapon effects do not apply.", "docs/rulebooks/rulebook_text.txt:lines 3639–3650"), assertion("SA-RI-GRENADE-FAQ", "SRC-FAQ", "General rules / FQ-P02-U10", ["preconditions", "operations", "partialResolution"], "Closed Doors block throwing Grenades and other effects on objects across them.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10")],
        ["icon.grenadeToken", "term.corridor", "term.hit", "term.closed"], ["tax.entity.component.token.tactical-gear.grenade", "tax.entity.spatial.corridor", "tax.process.operation.hit", "tax.entity.spatial.door", "tax.state.closed"], [],
        timing("TW-RI-GRENADE", "tax.entity.component.token.tactical-gear.grenade", "when-triggered", "per-token-effect-or-exact-caller-that-resolves-the-token-effect"), [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must",
        [condition("C-RI-GRENADE", "all", [{"predicate": "target Corridor is adjacent to the Character's Room"}, {"predicate": "no Closed Door blocks the effect"}], ["SA-RI-GRENADE-RB", "SA-RI-GRENADE-FAQ"])],
        [decision("D-RI-GRENADE-CORRIDOR", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["source-legal adjacent Corridors not blocked by a Closed Door"]), decision("D-RI-GRENADE-HITS", "P-PLAYER", "player-choice", 0, None, False, "public-on-allocation", ["an allocation of the complete numeric Grenade Hit total among eligible Intruders in the chosen Corridor"])],
        [{"informationId": "I-RI-GRENADE", "subjectRef": "chosen Corridor, Burst-die face, modified result, Intruders, allocated Hits, and caller-owned token/Item lifecycle", "audience": "public", "revealTrigger": "declaration/roll", "secrecy": "none"}], [],
        [_target("T-RI-GRENADE-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-PLAYER", mode="player-choice", minimum=1, maximum=1), _target("T-RI-GRENADE-INTRUDERS", ["tax.entity.agent.intruder"], selector="P-PLAYER", mode="player-choice", minimum=0, maximum=None)],
        [operation("S01", 1, "select-target", "must", "P-PLAYER", "one source-legal adjacent Corridor", ["SA-RI-GRENADE-RB", "SA-RI-GRENADE-FAQ"], decision_ref="D-RI-GRENADE-CORRIDOR", target_ref="T-RI-GRENADE-CORRIDOR"), operation("S02", 2, "draw-random", "must", "P-CHARACTER", "one Burst die result as a Grenade roll only", ["SA-RI-GRENADE-RB"]), operation("S03", 3, "change-value", "must", "P-RULES", "numeric Burst result plus 2", ["SA-RI-GRENADE-RB"], conditions=["rolled face is numeric"], value_change={"amount": 2, "value": "Grenade Hit total"}), operation("S04", 4, "change-value", "must", "P-PLAYER", "deal the modified number of Hits among Intruders in the chosen Corridor", ["SA-RI-GRENADE-RB"], conditions=["rolled face is numeric"], decision_ref="D-RI-GRENADE-HITS", target_ref="T-RI-GRENADE-INTRUDERS", value_change={"amount": "Burst numeric result + 2", "valueTaxonId": "tax.process.operation.hit"}), operation("S05", 5, "evaluate-condition", "must", "P-RULES", "special Burst face has no effect; this is not a Burst Action and applies no Weapon effects", ["SA-RI-GRENADE-RB"], conditions=["rolled face is the special Burst result"])],
        {"policy": "source-conditional-steps", "unit": "one Grenade effect roll", "onImpossible": "Closed Door blocks selection; special face does nothing; caller separately owns physical token or Item discard lifecycle"}, {"kind": "instantaneous-combat-effect-not-a-Burst-Action"}, {"policy": "one die result per effect; no Weapon-effect stacking"}, [], [], []))

    records.append(record(
        "SEM-ANTI-AIRCRAFT-TOKEN-STATE-001", "Anti-Aircraft token hidden order, inspection, and Lander resolution", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-RI-AA-RB", "SRC-RULEBOOK", "printed page 37 / RB-P37-V02 / lines 5953–5979", ["timing", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "outcomes"], "Place the two Anti-Aircraft tokens face down in random order; top token is current status. Authorized Characters inspect/reorder secretly, may share or lie verbally, and cannot show tokens. When Lander/Round markers coincide, ACTIVE destroys Lander; INACTIVE lands it and removes both tokens.", "docs/rulebooks/rulebook_text.txt:lines 5953–5979")],
        ["icon.lander"], ["tax.entity.component.token", "tax.entity.component.token.lander", "tax.entity.spatial.room"], [],
        timing("TW-RI-AA", "tax.entity.component.token", "when-triggered", "setup-once-plus-per-authorized-secret-inspection/reorder-plus-one-Lander-resolution"), [participant("P-RULES", "rules-system"), participant("P-INSPECTOR", "decision-owner", "tax.entity.agent.player")], "mixed", [],
        [decision("D-RI-AA-ORDER", "P-INSPECTOR", "player-choice", 1, 1, False, "inspector-private", ["ACTIVE above INACTIVE", "INACTIVE above ACTIVE"])],
        [{"informationId": "I-RI-AA-ORDER", "subjectRef": "both Anti-Aircraft token faces and top/bottom order", "audience": "temporary-private-inspector; hidden from all others", "revealTrigger": "authorized secret check or final top-token resolution", "secrecy": "verbal claims may be shared and may be lies; token faces cannot be shown; clients/logs/accessibility/spectators expose no hidden face/order"}, {"informationId": "I-RI-AA-OUTCOME", "subjectRef": "resolved top status, Lander destruction/landing, and token removal", "audience": "public", "revealTrigger": "Lander/Round-marker coincidence", "secrecy": "bottom token need not be shown before both are removed unless the source physically requires it"}], [],
        [_target("T-RI-AA-TOKENS", ["tax.entity.component.token"], minimum=2, maximum=2)],
        [operation("S01", 1, "shuffle", "must", "P-RULES", "the exact two Anti-Aircraft tokens face down", ["SA-RI-AA-RB"], repeat={"requested": 2, "order": "random"}), operation("S02", 2, "set-state", "must", "P-RULES", "top face-down token denotes current Anti-Aircraft status", ["SA-RI-AA-RB"]), operation("S03", 3, "inspect-private", "must", "P-INSPECTOR", "both Anti-Aircraft token faces/order", ["SA-RI-AA-RB"], conditions=["an exact authorized effect invokes inspection/reorder"], target_ref="T-RI-AA-TOKENS"), operation("S04", 4, "choose", "must", "P-INSPECTOR", "one of the two exact top/bottom orders", ["SA-RI-AA-RB"], conditions=["authorized reorder is resolving"], decision_ref="D-RI-AA-ORDER", target_ref="T-RI-AA-TOKENS"), operation("S05", 5, "set-state", "must", "P-RULES", "both tokens remain face down in selected order and cannot be shown", ["SA-RI-AA-RB"], conditions=["authorized reorder is resolving"]), operation("S06", 6, "inspect-private", "must", "P-RULES", "top Anti-Aircraft token for final resolution", ["SA-RI-AA-RB"], conditions=["Round marker and Lander token occupy the same space"]), operation("S07", 7, "transition-zone", "must", "P-RULES", "Lander token removed from game", ["SA-RI-AA-RB"], conditions=["top token is ACTIVE"], transition={"from": "Round track", "to": "tax.scaffold.zone.removed-from-game"}), operation("S08", 8, "place-component", "must", "P-RULES", "Lander token on Landing Zone Room", ["SA-RI-AA-RB"], conditions=["top token is INACTIVE"]), operation("S09", 9, "transition-zone", "must", "P-RULES", "both Anti-Aircraft tokens removed from game", ["SA-RI-AA-RB"], conditions=["top token is INACTIVE"], target_ref="T-RI-AA-TOKENS", transition={"from": "Anti-Aircraft slot", "to": "tax.scaffold.zone.removed-from-game"})],
        {"policy": "ordered-complete", "unit": "one setup, authorized reorder, or final top-token resolution", "onImpossible": "finite exact tokens and hidden order are mandatory; no unauthorized reveal/show or automated strategic reordering"}, {"kind": "persistent-hidden-two-token-order-until-final-resolution"}, {"policy": "exactly two physical tokens in one order; repeated authorized checks replace order rather than stack"}, [{"condition": "top ACTIVE at resolution", "result": "Lander destroyed"}, {"condition": "top INACTIVE at resolution", "result": "Lander lands and Anti-Aircraft tokens are removed"}], [], []))

    red_gap_assets = [row for row in source_index["sourceFaceAssets"] if row["selectedDisposition"] == "red-selector-gap"]
    cross_gap_assets = [row for row in source_index["sourceFaceAssets"] if row["selectedDisposition"] == "cross-family-gap-excluded"]
    excluded_faces = [*source_index["excludedHeavyFaces"], *source_index["physicalClassConflictFaces"]]
    bga_rows = source_index["licensedDigitalOccurrences"]
    variant_assertions = []
    variant_operations = []
    variant_refs = []
    for asset in [*red_gap_assets, *cross_gap_assets]:
        family = "36" if asset["selectedDisposition"] == "red-selector-gap" else "35"
        assertion_id = f"SA-RI-VARIANT-{family}-{asset['generatedCell']:02d}"
        item = assertion(assertion_id, asset["sourceId"], f"CustomDeck {family} / generated cell {asset['generatedCell']} / explicit selector gap", ["operations", "sourceVariants"], asset["printedBody"] or "Non-rules/blank generated cell.", f"docs/rules/semantics/red-item-source-index.json:sourceFaceAssets.{asset['assetKey']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve unselected CustomDeck {family} cell {asset['generatedCell']} exactly; never dispatch it as a physical regular Red face", [assertion_id]))
        variant_refs.append({"variantId": f"SV-RI-GAP-{family}-{asset['generatedCell']:02d}", "sourceId": asset["sourceId"], "sourceAssertionId": assertion_id, "difference": f"Generated cell prints title {asset['printedTitle']!r}, body {asset['printedBody']!r}, and literal icon evidence but has no Red-root full CardID/GUID selector.", "resolution": "Retain independently; title, color, body, cell, folder, or CardID modulo cannot repair the gap or cross-family boundary."})
    for face in excluded_faces:
        assertion_id = f"SA-RI-VARIANT-EXCLUDED-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}"
        item = assertion(assertion_id, face["sourceId"], f"{face['redItemOccurrenceId']} / exact root selector and physical-class evidence", ["operations", "sourceVariants", "unresolvedQuestionRefs"], face["printedBody"], f"docs/rules/semantics/red-item-source-index.json:{face['redItemOccurrenceId']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"retain excluded root occurrence {face['redItemOccurrenceId']} and never dispatch it as one of 21 source-clear regular Red faces", [assertion_id]))
        variant_refs.append({"variantId": f"SV-RI-EXCLUDED-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}", "sourceId": face["sourceId"], "sourceAssertionId": assertion_id, "difference": f"Exact root child class is {face['physicalClass']!r} and printed body is {face['printedBody']!r}.", "resolution": "Preserve root membership. Explicit Heavy stays outside regular dispatch; Military Taser class/current correspondence remains SEM-Q-047 with no title-only default."})
    bga_assertion_id = "SA-RI-VARIANT-BGA"
    bga_assertion = assertion(bga_assertion_id, BGA_RED_ITEM_SOURCE_ID, "ITEMS_DATA / all nine deck-red rows in source order", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "\n".join(row["sourceBlockText"] for row in bga_rows), "docs/rules/semantics/red-item-source-index.json:licensedDigitalOccurrences")
    bga_assertion["textKind"] = "verbatim"
    variant_assertions.append(bga_assertion)
    for row in bga_rows:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve licensed ITEMS_DATA.{row['key']} independently: name={row['name']!r}, nbr={row['nbr']}, heavy={row['heavy']}, noIntruders={row['noIntruders']}, effectDesc={row['effectDesc']!r}", [bga_assertion_id]))
        variant_refs.append({"variantId": f"SV-RI-BGA-{row['key'].upper()}", "sourceId": BGA_RED_ITEM_SOURCE_ID, "sourceAssertionId": bga_assertion_id, "difference": f"Licensed row {row['key']} has an independent title/class/multiplicity/restriction/body tuple with no TTS/official physical selector.", "resolution": "Retain below official/source-bound authority. Aggregate 30/21/9 reconciliation is not a copy, title, body, or ordinal crosswalk."})
    records.append(record(
        "SEM-RED-ITEM-VARIANT-BOUNDARIES-001", "Red root, class, back, selector-gap, official, and licensed boundaries", "source-variant", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-RI-VARIANT-RB", "SRC-RULEBOOK", "unprinted page 3 and printed pages 28–29,37 / counts, classes, backs, and current Military Taser example", ["operations", "sourceVariants", "unresolvedQuestionRefs"], "Official inventory has 30 per Item type; regular/Heavy classes use physical format/trait rules; page 29 shows a current Heavy Military Taser occurrence but identifies no TTS GUID copy.", "docs/rules/semantics/red-item-source-index.json:familyCountEvidence"), *variant_assertions],
        ["term.item", "term.regular-item", "term.backpack"], ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.component.card.item.heavy"], [],
        timing("TW-RI-VARIANTS", "tax.entity.component.card.item", "when-triggered", "per-source-comparison-or-canonicalization-attempt"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-RI-VARIANTS", "subjectRef": "21 regular physical faces, three Heavy exclusions, six class-conflict selectors, seven selector gaps, two backs, nine licensed rows, official evidence, and wording/icon/class differences", "audience": "public source evidence", "revealTrigger": "source audit", "secrecy": "does not expose live shuffled order or private Backpack"}], [], [],
        [*variant_operations, operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", "Military Taser class/current and Portable Barrier/Barricade source differences stay independent; affected deck/face records own SEM-Q-047/050 without turning this source ledger into a default", ["SA-RI-VARIANT-RB", *[row["assertionId"] for row in variant_assertions]]), operation(f"S{len(variant_operations)+2:02d}", len(variant_operations)+2, "evaluate-condition", "must", "P-RULES", "no title, Red color, weapon/ammo art, body, folder, order, generated cell, CardID modulo, licensed key, multiplicity, or expected logic establishes identity/effect equivalence", ["SA-RI-VARIANT-RB", *[row["assertionId"] for row in variant_assertions]])],
        {"policy": "per-proposed-source-merge", "unit": "one proposed Red/Heavy/class/gap/licensed/official identity or effect merge", "onImpossible": "without exact source-backed correspondence, preserve independent occurrences/conflicts; affected records retain SEM-Q-047/050"}, {"kind": "persistent-source-audit-boundary"}, {"policy": "source variants do not dispatch, stack, replace, or identify one another from resemblance"}, [], [], variant_refs))

    def build_face(definition: dict) -> dict:
        source = face_by_occurrence[definition["occurrenceId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        scan_id = f"SA-RIF-{code}-SCAN"
        general_id = f"SA-RIF-{code}-GENERAL"
        scan = assertion(scan_id, source["sourceId"], f"{source['redItemOccurrenceId']} / exact selector, regions, panels, title, trait, punctuation, sentences, and icons", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/red-item-source-index.json:{source['redItemOccurrenceId']}")
        scan["textKind"] = "verbatim"
        general = assertion(general_id, "SRC-RULEBOOK", "printed pages 16–17,28–29,33,37 / whole-effect, Item use, Backpack, One Use Only, Tactical Gear, Combat, Anti-Aircraft", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "This exact source-clear regular Item stays owner-private until selected, resolves only through a legal Use/immediate window, applies official local/whole/component limits and reusable procedures, and uses the separate One Use Only lifecycle.", "docs/rules/semantics/red-item-source-index.json:officialRulebookTextOccurrences")
        terms = ["term.item", "term.regular-item"]
        taxa = ["tax.entity.component.card.item", "tax.entity.component.card.item.regular", "tax.entity.agent.character"]
        named = [source["namedIdentityRef"]] if source.get("namedIdentityRef") else []
        for icon in source["iconOccurrences"]:
            if icon.get("semanticReferenceId"):
                terms.append(icon["semanticReferenceId"])
        participants = [participant("P-USING-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-USING-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")]
        decisions = []
        targets = [_target(f"T-RIF-{code}-ITEM", ["tax.entity.component.card.item.regular"], minimum=1, maximum=1), _target(f"T-RIF-{code}-CHARACTER", ["tax.entity.agent.character"], selector="P-USING-PLAYER", mode="player-choice-with-consent", minimum=1, maximum=1)]
        ops = []

        def add(sentence_sequence: int, op_type: str, modality: str, subject: str, obj: str, *, sources=None, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
            sequence = len(ops) + 1
            sentence = source["sentences"][sentence_sequence - 1]
            op = operation(f"S{sequence:02d}", sequence, op_type, modality, subject, obj, sources or [scan_id, general_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref or f"T-RIF-{code}-CHARACTER", transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence["sentenceId"]
            op["sourceRegionId"] = sentence["regionId"]
            op["sourcePanelId"] = sentence["panelId"]
            ops.append(op)
            return op

        unresolved = []
        kind = source["effectKind"]
        preconditions = [condition(f"C-RIF-{code}-OCCURRENCE", "predicate", [{"predicate": f"exact selected physical occurrence is {source['redItemOccurrenceId']}"}], [scan_id, general_id])]
        matched_not_in_combat = any(icon.get("semanticReferenceId") == "icon.notInCombat" and icon.get("cardLocationClass") == "upperRight" for icon in source["iconOccurrences"])
        has_local_upper = any(icon.get("semanticReferenceId") is None and icon.get("cardLocationClass") == "upperRight" for icon in source["iconOccurrences"])
        if matched_not_in_combat:
            preconditions.append(condition(f"C-RIF-{code}-NOT-COMBAT", "predicate", [{"predicate": "using Character is Not In Combat"}], [scan_id, general_id]))
        if has_local_upper:
            unresolved.append("SEM-Q-046")
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-046 exact identity/scope of this selected source-local upper-right crossed glyph; licensed noIntruders does not assign it")

        if kind == "gain-ammo":
            terms.extend(["icon.ammoToken", "term.tactical-gear-token"]); taxa.append("tax.entity.component.token.tactical-gear.ammo"); unresolved.extend(["SEM-Q-044", "SEM-Q-045"])
            add(1, "evaluate-condition", "must", "P-RULES", "printed optional immediate-use sentence is delegated to SEM-RED-ITEM-IMMEDIATE-USE-001")
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-044 whether the unresolved Interplay Gaining class permits this Ammo gain on another consenting Character", conditions=["proposed affected Character differs from using Character"])
            add(2, "invoke-process", "must", "P-AFFECTED-CHARACTER", "gain 1 finite Ammo token in an owner-chosen compatible empty slot", conditions=["target is source-legal under SEM-Q-044"], invoke="SEM-ITM-005", repeat={"tokenType": "ammo", "quantity": 1})
        elif kind == "reorder-anti-aircraft":
            terms.extend(["icon.computer", "icon.malfunction"]); taxa.extend(["tax.entity.spatial.room", "tax.entity.component.marker.malfunction", "tax.entity.component.token"])
            preconditions.append(condition(f"C-RIF-{code}-ROOM", "all", [{"predicate": "using Character occupies a Room with Computer"}, {"predicate": "that Room has no Malfunction marker"}, {"predicate": "both Anti-Aircraft tokens remain reorderable"}], [scan_id, general_id]))
            add(2, "invoke-process", "must", "P-USING-PLAYER", "privately inspect both Anti-Aircraft tokens and place them face down in owner-chosen top/bottom order", invoke="SEM-ANTI-AIRCRAFT-TOKEN-STATE-001")
        elif kind == "remote-exploration":
            terms.extend(["term.exploration-sequence", "term.room", "term.corridor", "icon.notInCombat"]); taxa.extend(["tax.process.sequence.exploration", "tax.entity.spatial.room", "tax.entity.spatial.corridor"]); unresolved.append("SEM-Q-048")
            decision_id = f"D-RIF-{code}-ROOM"
            decisions.append(decision(decision_id, "P-RULES", "unresolved", 1, 1, False, "source-unspecified-until-declaration", ["one source-legal neighboring Undiscovered Room/slot", "another source-defined target owner/tie-break"]))
            targets.append(_target(f"T-RIF-{code}-ROOM", ["tax.entity.spatial.room"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=1, maximum=1))
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-048 neighboring Room target owner/eligibility and source-local remote Exploration context", decision_ref=decision_id, target_ref=f"T-RIF-{code}-ROOM")
            dispatch = add(1, "invoke-selected-process", "must", "P-RULES", "exact Exploration-card occurrence for the resolved neighboring target without moving the Character", conditions=["target is resolved under SEM-Q-048"], decision_ref=decision_id, target_ref=f"T-RIF-{code}-ROOM", repeat={"callerContext": "Red Item Exploring Drone", "characterMovement": False, "entranceEffectResolution": False}, notes="Exact Exploration face remains occurrence-dispatched; target, map orientation, card setup, finite components, and lifecycle remain source-bound. No title/BGA number dispatch.")
            dispatch["dispatchRuleIds"] = list(exploration_rule_ids)
            add(2, "evaluate-condition", "must", "P-RULES", "do not resolve the selected Exploration face's Entrance effect; this suppression does not invent Character Movement or post-Movement Noise")
        elif kind == "flashbang-movement":
            terms.extend(["term.move", "term.movement-sequence", "term.opportunity-attack", "term.corridor", "term.room", "term.noise-roll"]); taxa.extend(["tax.process.sequence.movement", "tax.process.attack.opportunity", "tax.entity.spatial.corridor", "tax.entity.spatial.room"]); unresolved.append("SEM-Q-002")
            decision_id = f"D-RIF-{code}-CORRIDOR"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["adjacent Corridors with a fully resolvable Movement destination and no Closed Door"]))
            targets.append(_target(f"T-RIF-{code}-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-USING-PLAYER", mode="player-choice", minimum=1, maximum=1))
            add(1, "select-target", "must", "P-USING-PLAYER", "one legal adjacent Corridor for the printed Move", decision_ref=decision_id, target_ref=f"T-RIF-{code}-CORRIDOR")
            add(2, "evaluate-condition", "must", "P-RULES", "zero Opportunity Attacks resolve during this source-defined Movement; Hazard-result Attacks outside Opportunity scope remain unaffected", decision_ref=decision_id)
            add(1, "branch", "must", "P-RULES", "Discovered destination movement or exact Exploration Sequence", decision_ref=decision_id)
            add(1, "move-entity", "must", "P-USING-CHARACTER", "selected Discovered destination Room", conditions=["destination is already Discovered"], decision_ref=decision_id, target_ref=f"T-RIF-{code}-CORRIDOR")
            add(1, "invoke-process", "must", "P-USING-CHARACTER", "Exploration Sequence for selected Unexplored destination", conditions=["selected Corridor is Unexplored"], decision_ref=decision_id, target_ref=f"T-RIF-{code}-CORRIDOR", invoke="SEM-ACT-EXPLORE-001", notes="The enclosing Use Item pays the only Action-card cost; printed Move does not instruct a second Basic-Action payment.")
            add(1, "invoke-process", "must", "P-USING-CHARACTER", "Noise Roll", conditions=["destination is already Discovered"], invoke="SEM-NOISE-001")
        elif kind == "grenade-effect-or-gain":
            terms.extend(["icon.grenadeToken", "term.corridor", "term.hit"]); taxa.extend(["tax.entity.component.token.tactical-gear.grenade", "tax.entity.spatial.corridor", "tax.process.operation.hit"]); unresolved.extend(["SEM-Q-044", "SEM-Q-045"])
            decision_id = f"D-RIF-{code}-BRANCH"
            decisions.append(decision(decision_id, "P-USING-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["resolve one Grenade token effect in an adjacent Corridor", "gain 1 Grenade token"]))
            add(1, "evaluate-condition", "must", "P-RULES", "printed optional immediate-use sentence is delegated to SEM-RED-ITEM-IMMEDIATE-USE-001")
            add(2, "choose", "must", "P-USING-PLAYER", "one printed OR branch", decision_ref=decision_id)
            add(2, "invoke-process", "must", "P-USING-CHARACTER", "Grenade token Corridor effect without consuming a separate Grenade token", conditions=["resolve-effect branch"], decision_ref=decision_id, invoke="SEM-GRENADE-TOKEN-EFFECT-001")
            add(3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-044 whether the unresolved Interplay Gaining class permits this Grenade-token gain on another consenting Character", conditions=["gain branch", "proposed affected Character differs from using Character"], decision_ref=decision_id)
            add(3, "invoke-process", "must", "P-AFFECTED-CHARACTER", "gain 1 finite Grenade token in an owner-chosen compatible empty slot", conditions=["gain branch", "target is source-legal under SEM-Q-044"], decision_ref=decision_id, invoke="SEM-ITM-005", repeat={"tokenType": "grenade", "quantity": 1})
        elif kind == "inspect-objectives":
            terms.extend(["icon.computer", "icon.malfunction", "term.objective-card"]); taxa.extend(["tax.entity.spatial.room", "tax.entity.component.marker.malfunction", "tax.entity.component.card.objective"]); unresolved.append("SEM-Q-049")
            preconditions.append(condition(f"C-RIF-{code}-ROOM", "all", [{"predicate": "using Character occupies a Room with Computer"}, {"predicate": "that Room has no Malfunction marker"}], [scan_id, general_id]))
            decision_id = f"D-RIF-{code}-CHARACTER"
            decisions.append(decision(decision_id, "P-RULES", "unresolved", 1, 1, False, "source-unspecified", ["using player selects a source-legal Character and privately checks that Character's Objective cards", "chosen Character's owner or another source-defined actor owns selection/inspection"]))
            targets.append(_target(f"T-RIF-{code}-OBJECTIVES", ["tax.entity.component.card.objective"], selector="P-RULES", mode="deterministic-state-filter", minimum=1, maximum=2, visibility="temporary-private-inspection"))
            add(2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-049 target scope, selection owner, authorized inspector, and private information boundary", decision_ref=decision_id)
            add(2, "inspect-private", "must", "resolved inspector under SEM-Q-049", "all Objective cards currently belonging to the resolved chosen Character", conditions=["SEM-Q-049 owner/scope/inspector is resolved"], decision_ref=decision_id, target_ref=f"T-RIF-{code}-OBJECTIVES", notes="No Objective is revealed publicly, moved, chosen, fulfilled, or shown merely by Check; unselected Characters' Objectives remain hidden.")
        elif kind == "place-closed-door":
            terms.extend(["term.door", "term.closed"]); taxa.extend(["tax.entity.spatial.door", "tax.entity.spatial.corridor", "tax.state.closed"]); unresolved.append("SEM-Q-050")
            decision_id = f"D-RIF-{code}-DOOR"
            decisions.append(decision(decision_id, "P-RULES", "unresolved", 1, 1, False, "source-unspecified", ["one ordinary local eligible Door slot", "one accessible Door including destroyed/no-slot under the independent licensed variant", "another source-defined target/owner"]))
            targets.append(_target(f"T-RIF-{code}-DOOR", ["tax.entity.spatial.door"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=1, maximum=1))
            add(1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-050 Door target owner/eligibility, destroyed/no-slot override, finite placement, and Portable Barrier/Barricade FAQ applicability", decision_ref=decision_id, target_ref=f"T-RIF-{code}-DOOR")
            add(1, "invoke-process", "if-able", "P-RULES", "close/place the one resolved Door under the reusable Door-state constraint", conditions=["SEM-Q-050 supplies a source-legal target and placement rule"], decision_ref=decision_id, target_ref=f"T-RIF-{code}-DOOR", invoke="SEM-DOOR-001")
            add(1, "evaluate-condition", "must", "P-RULES", "if FAQ FQ-P03-U08 is established as applicable, an opened placed Portable Barricade Door is gone; no re-close lifecycle is invented otherwise", conditions=["SEM-Q-050 resolves FAQ title/applicability"])
        else:
            raise AssertionError(f"unexpected Red Item effect kind: {kind}")

        unresolved = list(dict.fromkeys(unresolved))
        status = "source-backed-with-open-question" if unresolved else "source-backed"
        interpretation = "open-alternatives" if unresolved else "source-composed"
        recurrence = "once-per-exact-physical-Item-use; printed immediate timing delegates to SEM-RED-ITEM-IMMEDIATE-USE-001" if kind in {"gain-ammo", "grenade-effect-or-gain"} else "once-per-exact-physical-Item-use"
        info_subject = "exact physical occurrence, printed title/trait/body/panels/icons, decisions, operations, and result"
        info_audience = "owner-private before use; public selected face/decisions/results at source-defined use point"
        secrecy = "sibling Backpack faces and Red deck order remain hidden"
        if kind == "inspect-objectives":
            info_subject += "; selected Character Objective identities are temporary private information"
            info_audience = "selected face/use public; Objective identities visible only to the inspector resolved under SEM-Q-049"
            secrecy += "; Objective data never enters unauthorized clients/logs/accessibility/spectator views"
        return record(
            definition["semanticRuleId"], f"Regular Red Item physical occurrence {code}", status, "component-effect", "official-primary", interpretation,
            [scan, general], terms, taxa, named, timing(f"TW-RIF-{code}", "tax.entity.component.card.item.regular", "when-triggered", recurrence), participants, "mixed" if decisions or unresolved else "must", preconditions, decisions,
            [{"informationId": f"I-RIF-{code}", "subjectRef": info_subject, "audience": info_audience, "revealTrigger": "SEM-USE-ITEM-001 under SEM-Q-039", "secrecy": secrecy}], [], targets, ops,
            {"policy": "all-or-nothing-selection", "unit": "one exact physical occurrence's printed effect/selected branch", "onImpossible": "generic cost/reveal/One Use lifecycle remains reusable; no glyph, class, target owner, inspection, Door, Interplay, or immediate-window default is invented"},
            {"kind": "instantaneous-one-use-effect; no Passive or Reaction heading; exact Ammo/Grenade timing notes create separate immediate-use windows"},
            {"policy": "each physical copy resolves separately; same title/body/multiplicity creates no identity or stacking key"}, [], unresolved, [])

    records.extend(build_face(definition) for definition in REGULAR_PHYSICAL_DEFINITIONS)
    return records


def integrate_red_item_shared_records(records: list[dict], source_index: dict, assertion, operation) -> None:
    use = next(row for row in records if row["ruleId"] == "SEM-USE-ITEM-001")
    red_assertion_ids = []
    for face in source_index["faces"]:
        assertion_id = f"SA-RI-USE-FACE-{face['ttsCardId']}-{face['ttsCardGuid'].upper()}"
        use["sourceAssertions"].append(assertion(assertion_id, face["sourceId"], f"{face['redItemOccurrenceId']} / exact physical selector and face", ["preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], face["printedBody"], f"docs/rules/semantics/red-item-source-index.json:{face['redItemOccurrenceId']}"))
        red_assertion_ids.append(assertion_id)
    dispatch = next(op for op in use["operations"] if op.get("dispatchRuleIds"))
    dispatch["dispatchRuleIds"].extend(RED_ITEM_RULE_IDS)
    dispatch["sourceAssertionIds"].extend(red_assertion_ids)
    dispatch["objectRef"] = "exact occurrence-specific source-clear regular Item effect"
    dispatch["notes"] = "Dispatch uses the complete family-specific exact root selector; never title, color, weapon/ammo art, body, folder, order, cell, modulo, licensed key, or multiplicity."
    lifecycle = use["operations"][-1]
    lifecycle["operationType"] = "invoke-selected-process"
    lifecycle["objectRef"] = "family-specific One Use Only lifecycle for the selected physical Item"
    lifecycle["invokeRuleId"] = None
    lifecycle["dispatchRuleIds"] = ["SEM-GREEN-ITEM-ONE-USE-001", "SEM-RED-ITEM-ONE-USE-001"]

    trade = next(row for row in records if row["ruleId"] == "SEM-ITEM-TRADE-GAIN-001")
    immediate = trade["operations"][-1]
    immediate["operationType"] = "invoke-selected-process"
    immediate["objectRef"] = "exact gained Item's family-specific immediate-use procedure"
    immediate["invokeRuleId"] = None
    immediate["dispatchRuleIds"] = ["SEM-GREEN-ITEM-IMMEDIATE-USE-001", "SEM-RED-ITEM-IMMEDIATE-USE-001"]

    tactical = next(row for row in records if row["ruleId"] == "SEM-ACT-TACTICAL-001")
    faq_assertion = assertion("SA-ACT-GEAR-FAQ-SEQUENTIAL", "SRC-FAQ", "Items and tactical gear / FQ-P03-U06", ["decisions", "operations", "partialResolution", "stacking"], "Any number of Tactical Gear tokens may be used; choose and resolve tokens one by one, and may decide to use an additional token after one already resolves.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P03-U06")
    tactical["sourceAssertions"].append(faq_assertion)
    tactical["authority"]["highest"] = "official-errata"
    use_decision = next(row for row in tactical["decisions"] if row["decisionId"] == "D-ACT-GEAR-USE")
    use_decision["selectionMode"] = "player-choice-sequential"
    use_decision["options"] = ["stop", "choose one next own Tactical Gear token after observing prior token resolution"]
    token_operation = next(row for row in tactical["operations"] if row["stepId"] == "S03")
    token_operation["sourceAssertionIds"].append("SA-ACT-GEAR-FAQ-SEQUENTIAL")
    token_operation["repeat"] = {"scope": "one selected token at a time", "selectionTiming": "after each prior token resolves, owner may stop or select another"}
    tactical["partialResolution"]["onImpossible"] = "Only legal compatible transfers and resolvable next token effects may be chosen; zero tokens/transfers and stopping after any resolved token are source-permitted"
