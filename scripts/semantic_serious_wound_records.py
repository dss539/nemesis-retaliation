from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

from semantic_attack_records import _find_guid, _parse_value


BASE_SERIOUS_WOUND_DECK_GUID = "b75145"
SERIOUS_WOUND_SHEET_SOURCE_ID = "SRC-SERIOUS-WOUND-SHEET"
SERIOUS_WOUND_SHEET_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149.jpg"
SERIOUS_WOUND_BACK_SOURCE_ID = "SRC-SERIOUS-WOUND-BACK"
SERIOUS_WOUND_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-150.jpg"
BGA_SERIOUS_WOUND_SOURCE_ID = "SRC-BGA-SERIOUS-WOUNDS"
BGA_SERIOUS_WOUND_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
SELECTED_EVIDENCE_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"
LOW_CONFIDENCE_PATH = "assets/tts-mod/extract/low-confidence-review.json"

SHEET_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235807/1DB17B19A519421BD8DFDC89E444B21B5B0FCF7A/"
DIRECT_KNEE_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/11925215518148184/DE1A63A0FD1024119A73413C91C4EEE443C312A0/"
DIRECT_LEG_FACE_URL = "https://steamusercontent-a.akamaihd.net/ugc/15957550840588894905/B7208353D2AC1D8159507B7B1E1630B2F2B36242/"
SHARED_BACK_URL = "https://steamusercontent-a.akamaihd.net/ugc/2468613527880235898/A32D91672CA7CCBA01C44C27791836D0E634CE2A/"


def _asset(
    key: str,
    path: str,
    title: str,
    body: str,
    sentences: list[str],
    icon_specs: list[tuple[str, str | None]],
    effect_kind: str,
    *,
    source_role: str,
    custom_deck_id: str,
    generated_cell: int | None,
    literal_heading_class: str = "literal-anatomy-region-heading",
) -> dict:
    return {
        "assetKey": key,
        "sourcePath": path,
        "printedTitle": title,
        "printedBody": body,
        "sentenceTexts": sentences,
        "iconSpecs": icon_specs,
        "effectKind": effect_kind,
        "sourceRole": source_role,
        "customDeckId": custom_deck_id,
        "generatedCell": generated_cell,
        "literalHeadingClass": literal_heading_class,
    }


ASSET_DEFINITIONS = {
    "sheet-00": _asset(
        "sheet-00",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-00.png",
        "EYES",
        "+1 to all your Shoot values.",
        ["+1 to all your Shoot values."],
        [],
        "shoot-value-modifier",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=0,
    ),
    "sheet-01": _asset(
        "sheet-01",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-01.png",
        "LUNGS",
        "Whenever you Pass:\nlose 1 [oxygen] (even in Section\nwith [lifeSupportActive]).\nIf you already have 0 [oxygen],\nlose 2 [ICON: thick white horizontal stepped zigzag line with sharp central peak] instead.",
        [
            "Whenever you Pass:",
            "lose 1 [oxygen] (even in Section\nwith [lifeSupportActive]).",
            "If you already have 0 [oxygen],\nlose 2 [ICON: thick white horizontal stepped zigzag line with sharp central peak] instead.",
        ],
        [
            ("[oxygen]", "icon.oxygen"),
            ("[lifeSupportActive]", "icon.lifeSupportActive"),
            ("[oxygen]", "icon.oxygen"),
            ("[ICON: thick white horizontal stepped zigzag line with sharp central peak]", None),
        ],
        "pass-oxygen-or-local-glyph",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=1,
    ),
    "sheet-02": _asset(
        "sheet-02",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-02.png",
        "HAND",
        "“Use Item” Action costs\nyou 1 [actionCard] more.",
        ["“Use Item” Action costs\nyou 1 [actionCard] more."],
        [("[actionCard]", "icon.actionCard")],
        "use-item-cost-modifier",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=2,
    ),
    "sheet-03": _asset(
        "sheet-03",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-03.png",
        "ARM",
        "You have only 1 Hand slot. If you\nhave Items in both Hand slots,\nyou must instantly discard\nthe Item from one of them.",
        [
            "You have only 1 Hand slot.",
            "If you\nhave Items in both Hand slots,\nyou must instantly discard\nthe Item from one of them.",
        ],
        [],
        "hand-slot-restriction",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=3,
    ),
    "sheet-04": _asset(
        "sheet-04",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-04.png",
        "LEG",
        "Using the “Make a Move” Action\nfrom a Room with an [intruder]\nor through a Corridor\nwith an [intruder] costs you 1 [actionCard] more.",
        ["Using the “Make a Move” Action\nfrom a Room with an [intruder]\nor through a Corridor\nwith an [intruder] costs you 1 [actionCard] more."],
        [("[intruder]", "icon.intruder"), ("[intruder]", "icon.intruder"), ("[actionCard]", "icon.actionCard")],
        "unselected-leg-cost-variant",
        source_role="generated-cell-selector-gap-variant",
        custom_deck_id="38",
        generated_cell=4,
    ),
    "sheet-05": _asset(
        "sheet-05",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-05.png",
        "BODY",
        "Your Hand Size is 1 lower.",
        ["Your Hand Size is 1 lower."],
        [],
        "hand-size-modifier",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=5,
    ),
    "sheet-06": _asset(
        "sheet-06",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-06.png",
        "KNEE",
        "Using “Make a Move”\nor “Make a Move with [secure]”\nas your first Action in a Round\ncosts you 1 [actionCard] more.",
        ["Using “Make a Move”\nor “Make a Move with [secure]”\nas your first Action in a Round\ncosts you 1 [actionCard] more."],
        [("[secure]", "icon.secure"), ("[actionCard]", "icon.actionCard")],
        "unselected-knee-cost-variant",
        source_role="generated-cell-selector-gap-variant",
        custom_deck_id="38",
        generated_cell=6,
    ),
    "sheet-07": _asset(
        "sheet-07",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-07.png",
        "GUTS",
        "Whenever you Pass:\nget 1 Contamination card.",
        ["Whenever you Pass:", "get 1 Contamination card."],
        [],
        "pass-contamination",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=7,
        literal_heading_class="literal-condition-or-anatomy-heading-unresolved",
    ),
    "sheet-08": _asset(
        "sheet-08",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-149_cards/card-08.png",
        "BLEEDING",
        "Whenever you Pass:\nlose 1 [characterHealth].",
        ["Whenever you Pass:", "lose 1 [characterHealth]."],
        [("[characterHealth]", "icon.characterHealth")],
        "pass-health-loss",
        source_role="generated-cell-face",
        custom_deck_id="38",
        generated_cell=8,
        literal_heading_class="literal-condition-heading",
    ),
    "direct-4048": _asset(
        "direct-4048",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-028.png",
        "KNEE",
        "“Make a Move with [ICON: two overlapping white angular lobes with lower tab and upper notch]”\ncosts you 1 [actionCard] more.",
        ["“Make a Move with [ICON: two overlapping white angular lobes with lower tab and upper notch]”\ncosts you 1 [actionCard] more."],
        [("[ICON: two overlapping white angular lobes with lower tab and upper notch]", None), ("[actionCard]", "icon.actionCard")],
        "local-action-cost-modifier",
        source_role="direct-face",
        custom_deck_id="4048",
        generated_cell=None,
    ),
    "direct-5439": _asset(
        "direct-5439",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/seriouswound-104.png",
        "LEG",
        "Using the “Make a Move” Action\nfrom a Room with an [intruder]\ncosts you 1 [actionCard] more.",
        ["Using the “Make a Move” Action\nfrom a Room with an [intruder]\ncosts you 1 [actionCard] more."],
        [("[intruder]", "icon.intruder"), ("[actionCard]", "icon.actionCard")],
        "move-cost-modifier",
        source_role="direct-face",
        custom_deck_id="5439",
        generated_cell=None,
    ),
}


PHYSICAL_GROUPS = [
    (3800, "sheet-00", ["ee102c", "c85059", "213ca0"]),
    (3807, "sheet-07", ["89f2f0", "4d4710", "655132"]),
    (3808, "sheet-08", ["55f79e", "68a1cf", "928c60"]),
    (3801, "sheet-01", ["6466b5", "17ccb1", "5444e8"]),
    (3805, "sheet-05", ["351aa8", "6175a8", "74c9b5"]),
    (404800, "direct-4048", ["fd77b5", "1642c4", "a0a4f8"]),
    (3802, "sheet-02", ["ad7826", "2202b4", "06be60"]),
    (543900, "direct-5439", ["03d258", "864d90", "dbca72"]),
    (3803, "sheet-03", ["aa0b48", "235eb5", "6564cb"]),
]


def _physical_definition(sequence: int, card_id: int, asset_key: str, guid: str) -> dict:
    code = f"{card_id}-{guid.upper()}"
    return {
        "sequence": sequence,
        "ttsCardId": card_id,
        "ttsCardGuid": guid,
        "assetKey": asset_key,
        "occurrenceId": f"TTS-SERIOUS-WOUND-{code}-FACE",
        "sourceId": f"SRC-SERIOUS-WOUND-{code}",
        "semanticRuleId": f"SEM-SERIOUS-WOUND-{code}-001",
    }


PHYSICAL_DEFINITIONS = []
_sequence = 1
for _card_id, _asset_key, _guids in PHYSICAL_GROUPS:
    for _guid in _guids:
        PHYSICAL_DEFINITIONS.append(_physical_definition(_sequence, _card_id, _asset_key, _guid))
        _sequence += 1

SERIOUS_WOUND_RULE_IDS = [row["semanticRuleId"] for row in PHYSICAL_DEFINITIONS]
SERIOUS_WOUND_PASS_RULE_IDS = [
    row["semanticRuleId"]
    for row in PHYSICAL_DEFINITIONS
    if ASSET_DEFINITIONS[row["assetKey"]]["effectKind"] in {"pass-oxygen-or-local-glyph", "pass-contamination", "pass-health-loss"}
]
SERIOUS_WOUND_QUESTION_BLOCKS = {
    "SEM-Q-030": ["SEM-SERIOUS-WOUND-GAIN-001"],
    "SEM-Q-031": ["SEM-SERIOUS-WOUND-GAIN-001"],
    "SEM-Q-032": ["SEM-SERIOUS-WOUND-GAIN-001"],
    "SEM-Q-033": [row["semanticRuleId"] for row in PHYSICAL_DEFINITIONS if row["assetKey"] == "direct-4048"],
    "SEM-Q-034": [row["semanticRuleId"] for row in PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet-01"],
    "SEM-Q-035": [row["semanticRuleId"] for row in PHYSICAL_DEFINITIONS if row["assetKey"] == "sheet-05"],
    "SEM-Q-036": ["SEM-SERIOUS-WOUND-GAIN-001", *SERIOUS_WOUND_RULE_IDS],
    "SEM-Q-037": SERIOUS_WOUND_PASS_RULE_IDS,
    "SEM-Q-038": ["SEM-SERIOUS-WOUND-GAIN-001"],
}


OFFICIAL_VISIBLE_COUNTERPARTS = [
    {
        "sourceOccurrenceId": "RB-P03-V01-SW-EYES",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "face",
        "printedTitle": "EYES",
        "visibleText": "+1 to all your Shoot results.",
        "completeness": "complete-visible-face",
        "locator": "unprinted PDF page 3 / SMALL CARDS / Serious Wound spread / front-left face",
        "physicalCopyCorrespondence": "not established",
    },
    {
        "sourceOccurrenceId": "RB-P03-V01-SW-ARM-PARTIAL",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "partial-face",
        "printedTitle": "ARM",
        "visibleText": "you must immediately\nItems from one of them.",
        "completeness": "partially-overlapped-visible-fragment",
        "locator": "unprinted PDF page 3 / SMALL CARDS / Serious Wound spread / center face",
        "physicalCopyCorrespondence": "not established",
    },
    {
        "sourceOccurrenceId": "RB-P03-V01-SW-BACK",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "shared-back",
        "printedTitle": "SERIOUS WOUND",
        "visibleText": "SERIOUS WOUND",
        "completeness": "representative-visible-back",
        "locator": "unprinted PDF page 3 / SMALL CARDS / Serious Wound spread",
        "physicalCopyCorrespondence": "shared back only",
    },
    {
        "sourceOccurrenceId": "RB-P18-V03-SW-EYES",
        "parentOccurrenceId": "RB-P18-V03",
        "kind": "face",
        "printedTitle": "EYES",
        "visibleText": "+1 to all your Shoot results.",
        "completeness": "complete-visible-face",
        "locator": "printed page 18 / Serious Wound placement diagram",
        "physicalCopyCorrespondence": "not established",
    },
    {
        "sourceOccurrenceId": "RB-P18-V03-SW-BACK",
        "parentOccurrenceId": "RB-P18-V03",
        "kind": "shared-back",
        "printedTitle": "SERIOUS WOUND",
        "visibleText": "SERIOUS WOUND",
        "completeness": "representative-visible-back",
        "locator": "printed page 18 / Serious Wound placement diagram",
        "physicalCopyCorrespondence": "shared back only",
    },
]

OFFICIAL_RULEBOOK_TEXT_OCCURRENCES = [
    {"occurrenceId": "RB-SW-INVENTORY-01", "section": "component-inventory", "locator": "unprinted page 3 / RB-P03-V01", "sourceText": "The base game contains 27 Serious Wound cards."},
    {"occurrenceId": "RB-SW-SETUP-01", "section": "setup", "locator": "printed page 9 / lines 2594–2600 / RB-P09-V01", "sourceText": "Shuffle the Serious Wound deck separately, place it face down, and leave space for its discard pile."},
    {"occurrenceId": "RB-SW-EFFECT-01", "section": "effect-and-health", "locator": "printed page 18 / lines 3784–3789", "sourceText": "Serious Wounds introduce major negative effects and reduce current and maximum usable Health; a Health marker may never move to a covered slot."},
    {"occurrenceId": "RB-SW-GAIN-01", "section": "random-draw-placement", "locator": "printed page 18 / lines 3790–3793", "sourceText": "Draw a random Serious Wound and place it in the leftmost Health Section without one; exact duplicates are possible and their effects do not stack."},
    {"occurrenceId": "RB-SW-DISPLACE-01", "section": "health-displacement", "locator": "printed page 18 / lines 3794–3796", "sourceText": "If the Health marker is in the section receiving the Wound, move it to the first empty slot in the next Section; this may discard Armor."},
    {"occurrenceId": "RB-SW-DISCARD-01", "section": "discard", "locator": "printed page 18 / lines 3797–3804", "sourceText": "When discarding one of multiple Serious Wounds, the affected Character may choose which; slide the rest left, and do not move Health merely because a Wound was discarded."},
    {"occurrenceId": "RB-SW-COMPONENT-LIMIT-01", "section": "finite-supply", "locator": "printed page 17 / lines 3538–3548", "sourceText": "Components are limited to the supplied physical quantity; when a component is unavailable, that part of an effect does nothing unless a specific fallback is stated."},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw_serious_wound_deck(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    deck = _find_guid(root.get("ObjectStates"), BASE_SERIOUS_WOUND_DECK_GUID)
    if not isinstance(deck, dict):
        raise AssertionError("base Serious Wound root Deck missing from raw TTS save")
    return deck, _sha(path)


def _parse_bga_serious_wounds(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const SERIOUS_WOUNDS_DATA = \{\n(.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError("SERIOUS_WOUNDS_DATA block not found")
    block = match.group(1)
    starts = list(re.finditer(r"^  ([A-Za-z]+): ", block, re.M))
    records: dict[str, dict] = {}
    for index, row in enumerate(starts):
        key = row.group(1)
        start = row.start()
        end = starts[index + 1].start() if index + 1 < len(starts) else len(block)
        source_block = block[start:end].rstrip("\n")
        name_match = re.search(r"name: ('(?:\\.|[^'])*')", source_block)
        effect_match = re.search(r"effectDesc: (\[(?:.|\n)*?\])(?:,| \})", source_block)
        if not name_match or not effect_match:
            raise AssertionError(f"licensed Serious Wound row parse failed: {key}")
        records[key] = {
            "key": key,
            "name": ast.literal_eval(name_match.group(1)),
            "effectDesc": ast.literal_eval(effect_match.group(1)),
            "sourceBlockText": source_block,
            "sourceOrder": index + 1,
            "identityCrosswalkStatus": "independent licensed occurrence; no TTS/official identity join asserted",
        }
    expected = ["Bleeding", "Leg", "Arm", "Eyes", "Guts", "Body", "Hand", "Knee", "Lungs"]
    if list(records) != expected:
        raise AssertionError("licensed Serious Wound table identity/order changed")
    return records


def _source_regions(asset: dict, selected_run: dict) -> list[dict]:
    visible = selected_run.get("visibleText") or {}
    other = visible.get("otherMaterialText") or []
    illegible = visible.get("illegibleSpans") or []
    return [
        {
            "regionId": "R1",
            "readingOrder": 1,
            "role": "artwork-and-diagnostic-interface",
            "operative": False,
            "printedText": other,
            "illegibleMicrotext": illegible,
            "rulesDataHandling": "preserve as source layout/artwork evidence; exclude from operative rules text and functional-icon counts",
        },
        {
            "regionId": "R2",
            "readingOrder": 2,
            "role": "printed-heading",
            "operative": False,
            "exactText": asset["printedTitle"],
            "literalHeadingClass": asset["literalHeadingClass"],
            "semanticBodyPartOrTraitInferred": False,
        },
        {
            "regionId": "R3",
            "readingOrder": 3,
            "role": "operative-effect",
            "operative": True,
            "exactText": asset["printedBody"],
            "bodyStart": 0,
            "bodyEnd": len(asset["printedBody"]),
        },
    ]


def _source_sentences(asset: dict) -> list[dict]:
    rows = []
    cursor = 0
    for sequence, exact_text in enumerate(asset["sentenceTexts"], 1):
        start = asset["printedBody"].find(exact_text, cursor)
        if start < 0:
            raise AssertionError(f"Serious Wound sentence span missing: {asset['assetKey']}:{sequence}")
        end = start + len(exact_text)
        rows.append({
            "sentenceId": f"SW-{asset['assetKey'].upper()}-S{sequence:02d}",
            "sequence": sequence,
            "regionId": "R3",
            "exactText": exact_text,
            "start": start,
            "end": end,
        })
        cursor = end
    return rows


def _source_panels(asset: dict) -> list[dict]:
    return [
        {"panelId": "P1", "readingOrder": 1, "role": "printed-title-panel", "operative": False, "exactText": asset["printedTitle"], "regionId": "R2"},
        {"panelId": "P2", "readingOrder": 2, "role": "operative-effect-panel", "operative": True, "exactText": asset["printedBody"], "regionId": "R3"},
    ]


def _source_icons(asset: dict, selected_run: dict) -> list[dict]:
    body = asset["printedBody"]
    verified = list(selected_run.get("verifiedIconOccurrences") or [])
    unresolved = list(selected_run.get("unresolvedIconOccurrences") or [])
    verified_cursor = 0
    unresolved_cursor = 0
    body_cursor = 0
    rows = []
    for sequence, (source_token, semantic_reference) in enumerate(asset["iconSpecs"], 1):
        start = body.find(source_token, body_cursor)
        if start < 0:
            raise AssertionError(f"Serious Wound icon span missing: {asset['assetKey']}:{source_token}")
        end = start + len(source_token)
        body_cursor = end
        if semantic_reference is None:
            if unresolved_cursor >= len(unresolved):
                raise AssertionError(f"Serious Wound unresolved icon evidence missing: {asset['assetKey']}")
            evidence = unresolved[unresolved_cursor]
            unresolved_cursor += 1
            if evidence.get("matchDecision") != "no-match" or evidence.get("canonicalToken") is not None:
                raise AssertionError(f"Serious Wound unresolved icon evidence drift: {asset['assetKey']}")
            mapping_status = "selected-explicit-authoritative-no-match"
            page40_assigned = False
            literal_appearance = evidence.get("referenceLabel") or source_token
        else:
            if verified_cursor >= len(verified):
                raise AssertionError(f"Serious Wound matched icon evidence missing: {asset['assetKey']}")
            evidence = verified[verified_cursor]
            verified_cursor += 1
            expected_token = semantic_reference.removeprefix("icon.")
            if evidence.get("matchDecision") != "match" or evidence.get("canonicalToken") != expected_token:
                raise AssertionError(f"Serious Wound matched icon evidence drift: {asset['assetKey']}:{source_token}")
            mapping_status = "authoritative-page40-exact-occurrence-match"
            page40_assigned = True
            literal_appearance = evidence.get("visibleDiscriminator") or evidence.get("referenceLabel") or source_token
        rows.append({
            "assetIconOccurrenceId": f"SW-ASSET-{asset['assetKey'].upper()}-I{sequence:02d}",
            "sequence": sequence,
            "regionId": "R3",
            "sourceToken": source_token,
            "start": start,
            "end": end,
            "literalAppearance": literal_appearance,
            "semanticReferenceId": semantic_reference,
            "mappingStatus": mapping_status,
            "page40TokenAssigned": page40_assigned,
            "mappingScope": f"exact source asset {asset['sourcePath']} occurrence only",
            "selectedEvidence": evidence,
        })
    if verified_cursor != len(verified) or unresolved_cursor != len(unresolved):
        raise AssertionError(f"Serious Wound selected icon count drift: {asset['assetKey']}")
    return rows


def build_serious_wound_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / CORPUS_PATH).read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    selected = json.loads((repo / SELECTED_EVIDENCE_PATH).read_text(encoding="utf-8"))
    selected_by_path = {row["sourcePath"]: row for row in selected["entries"]}
    low_confidence = json.loads((repo / LOW_CONFIDENCE_PATH).read_text(encoding="utf-8"))
    low_by_path = {row["sourcePath"]: row for row in low_confidence["entries"]}
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
    bga = _parse_bga_serious_wounds(repo / BGA_SERIOUS_WOUND_PATH)

    matching_roles = [row for row in roles if row.get("role") == "seriouswoundDeck"]
    if len(matching_roles) != 1:
        raise AssertionError("Serious Wound Lua role multiplicity changed")
    role = matching_roles[0]
    if role.get("guid") != BASE_SERIOUS_WOUND_DECK_GUID or role.get("type") != "Deck" or role.get("n_urls") != 4 or role.get("deck_nums") != ["38", "4048", "5439"]:
        raise AssertionError("base Serious Wound Lua role changed")

    raw_deck, raw_save_sha = _raw_serious_wound_deck(repo)
    raw_deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
    expected_deck_ids = [row["ttsCardId"] for row in PHYSICAL_DEFINITIONS]
    if raw_deck_ids != expected_deck_ids:
        raise AssertionError("base Serious Wound raw DeckIDs order changed")
    contained_value = raw_deck.get("ContainedObjects") or {}
    contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
    expected_children = [(row["ttsCardId"], row["ttsCardGuid"]) for row in PHYSICAL_DEFINITIONS]
    actual_children = [(int(row["CardID"]), row["GUID"]) for row in contained]
    if actual_children != expected_children:
        raise AssertionError("base Serious Wound raw contained occurrence order changed")
    root_custom = raw_deck.get("CustomDeck") or {}
    if set(root_custom) != {"38", "4048", "5439"}:
        raise AssertionError("base Serious Wound root CustomDeck IDs changed")
    expected_custom = {
        "38": (SHEET_FACE_URL, SHARED_BACK_URL, 3, 3),
        "4048": (DIRECT_KNEE_FACE_URL, SHARED_BACK_URL, 1, 1),
        "5439": (DIRECT_LEG_FACE_URL, SHARED_BACK_URL, 1, 1),
    }
    for key, expected in expected_custom.items():
        row = root_custom[key]
        if (row.get("FaceURL"), row.get("BackURL"), row.get("NumWidth"), row.get("NumHeight")) != expected:
            raise AssertionError(f"base Serious Wound CustomDeck tuple changed: {key}")

    root_object = next(row for row in objects if row.get("guid") == BASE_SERIOUS_WOUND_DECK_GUID)
    wound_children = [row for row in objects if ["Deck", BASE_SERIOUS_WOUND_DECK_GUID, ""] in (row.get("parent") or []) and row.get("gmnotes") == "wound"]
    all_wound_tagged = [row for row in objects if row.get("gmnotes") == "wound"]
    child_by_tuple = {(int(row["card_id"]), row["guid"]): row for row in wound_children}
    if root_object.get("type") != "Deck" or root_object.get("parent") != [] or len(wound_children) != 27 or len(all_wound_tagged) != 27 or set(child_by_tuple) != set(expected_children):
        raise AssertionError("base Serious Wound object/tag/container closure changed")

    bga_table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "SERIOUS_WOUNDS_DATA")
    if bga_table.get("count") != 9 or list(bga_table.get("keys") or []) != list(bga):
        raise AssertionError("licensed Serious Wound evidence-index closure changed")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    visual_ids = ["RB-P03-V01", "RB-P09-V01", "RB-P17-V03", "RB-P18-V01", "RB-P18-V02", "RB-P18-V03", "RB-P40-V02"]
    if any(occurrence_id not in visual_by_id for occurrence_id in visual_ids):
        raise AssertionError("Serious Wound official visual occurrence missing")
    faq_units = [unit for page in faq["pages"] for unit in page.get("units", [])]
    base_faq_hits = [unit for unit in faq_units if unit.get("applicability") in {"base-game", "base-game-additional-mode"} and re.search(r"serious wound", unit.get("printedText", ""), re.I)]
    if base_faq_hits:
        raise AssertionError("new base-applicable Serious Wound FAQ occurrence requires review")
    excluded_faq_hits = [unit for unit in faq_units if unit.get("applicability", "").startswith("expansion") and re.search(r"health|wound", unit.get("printedText", ""), re.I)]

    source_asset_rows = []
    source_asset_by_key = {}
    selected_asset_keys = {row["assetKey"] for row in PHYSICAL_DEFINITIONS}
    for asset_key, asset in ASSET_DEFINITIONS.items():
        source_path = asset["sourcePath"]
        source_sha = _sha(repo / source_path)
        corpus_row = corpus_by_path.get(source_path) or {}
        if source_sha != corpus_row.get("sourceSha256") or not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") != "draft-full":
            raise AssertionError(f"Serious Wound corpus/hash readiness drift: {asset_key}")
        selected_entry = selected_by_path.get(source_path) or {}
        runs = selected_entry.get("runs") or []
        if len(runs) != 1:
            raise AssertionError(f"Serious Wound selected-evidence run count changed: {asset_key}")
        selected_run = runs[0]
        visible = selected_run.get("visibleText") or {}
        if visible.get("title") != asset["printedTitle"] or visible.get("body") != asset["printedBody"]:
            raise AssertionError(f"Serious Wound exact selected title/body drift: {asset_key}")
        low_row = low_by_path.get(source_path) or {}
        provenance_value = low_row.get("provenance") or {}
        if asset["generatedCell"] is not None:
            if provenance_value.get("sourceSheetPath") != SERIOUS_WOUND_SHEET_PATH or provenance_value.get("cellIndex") != asset["generatedCell"]:
                raise AssertionError(f"Serious Wound generated source/cell drift: {asset_key}")
        elif provenance_value.get("sourceSheetPath") is not None or provenance_value.get("cellIndex") is not None:
            raise AssertionError(f"Serious Wound direct/generated inversion: {asset_key}")
        regions = _source_regions(asset, selected_run)
        panels = _source_panels(asset)
        sentences = _source_sentences(asset)
        for sentence in sentences:
            sentence["panelId"] = "P2"
        icons = _source_icons(asset, selected_run)
        for icon in icons:
            icon["panelId"] = "P2"
        selected_physical = [row["occurrenceId"] for row in PHYSICAL_DEFINITIONS if row["assetKey"] == asset_key]
        gap_source_id = f"SRC-SERIOUS-WOUND-VARIANT-38-CELL-{asset['generatedCell']:02d}" if asset["sourceRole"] == "generated-cell-selector-gap-variant" else None
        row = {
            "assetKey": asset_key,
            "sourceId": gap_source_id,
            "sourcePath": source_path,
            "sourceSha256": source_sha,
            "sourceRole": asset["sourceRole"],
            "customDeckId": asset["customDeckId"],
            "sourceSheetId": SERIOUS_WOUND_SHEET_SOURCE_ID if asset["generatedCell"] is not None else None,
            "sourceSheetPath": SERIOUS_WOUND_SHEET_PATH if asset["generatedCell"] is not None else None,
            "sourceSheetGrid": {"columns": 3, "rows": 3} if asset["generatedCell"] is not None else None,
            "generatedCell": asset["generatedCell"],
            "selectedByRootDeck": asset_key in selected_asset_keys,
            "selectedPhysicalOccurrenceIds": selected_physical,
            "selectorGap": None if selected_physical else {
                "status": "explicit-no-root-DeckID-GUID-selector",
                "reason": "The generated cell exists in the 3x3 source sheet and closed corpus, but no raw base-root DeckID/contained GUID selects it. It remains a source variant, not a physical deck face.",
                "cardIdModuloJoinUsed": False,
            },
            "printedTitle": asset["printedTitle"],
            "printedBody": asset["printedBody"],
            "literalHeadingClass": asset["literalHeadingClass"],
            "semanticBodyPartTraitOrSeverityInferred": False,
            "regions": regions,
            "panels": panels,
            "sentences": sentences,
            "iconOccurrences": icons,
            "effectKind": asset["effectKind"],
            "corpusEvidencePath": CORPUS_PATH,
            "selectedEvidencePath": SELECTED_EVIDENCE_PATH,
            "generatedCellEvidencePath": LOW_CONFIDENCE_PATH,
            "extractionState": corpus_row["extractionState"],
            "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
            "artworkInterfaceBoundary": low_row.get("artworkOnlyEvidence") or {
                "classification": "artwork/interface outside printed heading and operative body",
                "rulesDataHandling": "preserve source pixels and selected evidence; exclude diagnostic labels, microtext, callouts, anatomy art, and scan overlays from rules data",
            },
        }
        source_asset_rows.append(row)
        source_asset_by_key[asset_key] = row

    sheet_path = repo / SERIOUS_WOUND_SHEET_PATH
    with Image.open(sheet_path) as sheet:
        if sheet.size != (1773, 2589) or sheet.width % 3 or sheet.height % 3:
            raise AssertionError("Serious Wound source-sheet dimensions/grid changed")
        for cell in range(9):
            row, column = divmod(cell, 3)
            crop = sheet.crop((column * 591, row * 863, (column + 1) * 591, (row + 1) * 863)).convert("RGB")
            generated = source_asset_by_key[f"sheet-{cell:02d}"]
            with Image.open(repo / generated["sourcePath"]) as generated_image:
                if generated_image.convert("RGB").tobytes() != crop.tobytes():
                    raise AssertionError(f"Serious Wound generated-cell pixel drift: {cell}")

    face_rows = []
    contained_by_tuple = {(int(row["CardID"]), row["GUID"]): row for row in contained}
    for definition in PHYSICAL_DEFINITIONS:
        asset = source_asset_by_key[definition["assetKey"]]
        source_path = asset["sourcePath"]
        source_sha = asset["sourceSha256"]
        raw_child = contained_by_tuple[(definition["ttsCardId"], definition["ttsCardGuid"])]
        custom = root_custom[ASSET_DEFINITIONS[definition["assetKey"]]["customDeckId"]]
        selector = {
            "key": "FaceURL",
            "objectType": raw_child.get("Name"),
            "fullCardId": definition["ttsCardId"],
            "guid": definition["ttsCardGuid"],
            "parentDeckGuid": BASE_SERIOUS_WOUND_DECK_GUID,
            "customDeckId": ASSET_DEFINITIONS[definition["assetKey"]]["customDeckId"],
            "url": custom["FaceURL"],
            "backUrl": custom["BackURL"],
            "sideRole": "operative-serious-wound-face",
            "sourceRole": ASSET_DEFINITIONS[definition["assetKey"]]["sourceRole"],
            "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-BackURL-parent-tuple-with-explicit-generated-cell" if asset["generatedCell"] is not None else "exact-full-CardID-GUID-direct-FaceURL-BackURL-parent-tuple",
            "generatedSpriteSheetCell": asset["generatedCell"] is not None,
            "sourceSheetPath": asset["sourceSheetPath"],
            "sourceSheetSha256": _sha(sheet_path) if asset["generatedCell"] is not None else None,
            "sourceSheetGrid": asset["sourceSheetGrid"],
            "generatedCell": asset["generatedCell"],
            "selectorGap": None,
            "cardIdModuloJoinUsed": False,
        }
        physical_icons = []
        for icon in asset["iconOccurrences"]:
            physical_icons.append({
                **icon,
                "occurrenceId": f"SW-{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}-I{icon['sequence']:02d}",
                "assetMorphologyOccurrenceId": icon["assetIconOccurrenceId"],
                "mappingScope": f"exact physical Serious Wound occurrence {definition['occurrenceId']} only",
            })
        physical_regions = [
            {**region, "regionId": f"SW-{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}-{region['regionId']}"}
            for region in asset["regions"]
        ]
        physical_panels = [
            {
                **panel,
                "panelId": f"SW-{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}-{panel['panelId']}",
                "regionId": physical_regions[1]["regionId"] if panel["role"] == "printed-title-panel" else physical_regions[2]["regionId"],
            }
            for panel in asset["panels"]
        ]
        physical_sentences = [
            {**sentence, "sentenceId": f"SW-{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}-S{sentence['sequence']:02d}", "regionId": physical_regions[2]["regionId"], "panelId": physical_panels[1]["panelId"]}
            for sentence in asset["sentences"]
        ]
        for icon in physical_icons:
            icon["panelId"] = physical_panels[1]["panelId"]
        backlog_id = "CARD:" + source_sha[:16]
        backlog_row = backlog_by_id.get(backlog_id) or {}
        if backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != source_sha:
            raise AssertionError(f"Serious Wound backlog source tuple drift: {definition['occurrenceId']}")
        face_rows.append({
            "seriousWoundOccurrenceId": definition["occurrenceId"],
            "ttsRole": "seriouswoundDeck",
            "ttsDeckGuid": BASE_SERIOUS_WOUND_DECK_GUID,
            "ttsDeckType": "Deck",
            "ttsSavedSequence": definition["sequence"],
            "rulesDeckOrderSourceBacked": False,
            "ttsCardGuid": definition["ttsCardGuid"],
            "ttsCardId": definition["ttsCardId"],
            "customDeckId": ASSET_DEFINITIONS[definition["assetKey"]]["customDeckId"],
            "sourceSelector": selector,
            "sourceId": definition["sourceId"],
            "sourcePath": source_path,
            "sourceSha256": source_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS base Serious Wound physical occurrence / root deck {BASE_SERIOUS_WOUND_DECK_GUID} / saved sequence {definition['sequence']} / full CardID {definition['ttsCardId']} / GUID {definition['ttsCardGuid']}",
            "corpusEvidencePath": CORPUS_PATH,
            "selectedEvidencePath": SELECTED_EVIDENCE_PATH,
            "provenanceEvidencePath": PROVENANCE_PATH,
            "printedTitle": asset["printedTitle"],
            "printedBody": asset["printedBody"],
            "literalHeadingClass": asset["literalHeadingClass"],
            "semanticBodyPartTraitOrSeverityInferred": False,
            "regions": physical_regions,
            "panels": physical_panels,
            "sentences": physical_sentences,
            "iconOccurrences": physical_icons,
            "effectKind": asset["effectKind"],
            "sharedFaceAsset": {
                "sourceSha256": source_sha,
                "physicalOccurrenceCount": 3,
                "physicalOccurrenceIds": [row["occurrenceId"] for row in PHYSICAL_DEFINITIONS if row["assetKey"] == definition["assetKey"]],
                "assetIdentityDoesNotCollapsePhysicalCopies": True,
                "stackingEquivalenceBasis": "exact selected FaceURL/source SHA-256 only; printed title is not a join key",
            },
            "semanticRuleId": definition["semanticRuleId"],
            "backlogUnitId": backlog_id,
            "licensedCrosswalk": {
                "status": "not-asserted",
                "reason": "SERIOUS_WOUNDS_DATA rows remain independent licensed occurrences; display title, body resemblance, folder, sequence, and CardID modulo are prohibited identity joins.",
            },
            "officialCrosswalk": {
                "status": "not-asserted",
                "reason": "Official visible EYES/ARM/back occurrences control only their exact publisher occurrence/version and do not identify a TTS physical GUID/CardID copy.",
            },
            "joinEvidence": {
                "identityJoin": "exact physical occurrence and source-asset projection",
                "titleOnlyJoin": False,
                "bodyResemblanceJoin": False,
                "folderOnlyJoin": False,
                "sequenceOnlyJoin": False,
                "cardIdModuloJoin": False,
                "licensedKeyJoin": False,
                "basis": [
                    "sole base seriouswoundDeck Lua role and exact root GUID",
                    "raw saved DeckIDs sequence plus contained full CardID/GUID occurrence",
                    "exact CustomDeck ID, FaceURL, BackURL, parent deck, and source SHA-256",
                    "for generated faces: exact 3x3 sheet hash/grid/cell and selected cell evidence",
                    "exact heading, ordered body, region, sentence, punctuation, and occurrence-scoped icon evidence",
                ],
            },
        })

    sheet_provenance = provenance_by_file[SERIOUS_WOUND_SHEET_PATH.removeprefix("assets/tts-mod/extract/v2-dl/tree/")]
    back_provenance = provenance_by_file[SERIOUS_WOUND_BACK_PATH.removeprefix("assets/tts-mod/extract/v2-dl/tree/")]
    direct_knee_provenance = provenance_by_file[ASSET_DEFINITIONS["direct-4048"]["sourcePath"].removeprefix("assets/tts-mod/extract/v2-dl/tree/")]
    direct_leg_provenance = provenance_by_file[ASSET_DEFINITIONS["direct-5439"]["sourcePath"].removeprefix("assets/tts-mod/extract/v2-dl/tree/")]
    back_corpus = corpus_by_path[SERIOUS_WOUND_BACK_PATH]
    back_sha = _sha(repo / SERIOUS_WOUND_BACK_PATH)
    if sheet_provenance.get("refs") != 22 or back_provenance.get("refs") != 28 or direct_knee_provenance.get("refs") != 4 or direct_leg_provenance.get("refs") != 4:
        raise AssertionError("Serious Wound FaceURL/BackURL provenance multiplicity changed")
    if back_sha != back_corpus.get("sourceSha256") or back_corpus.get("rulesTextPresent") or (back_corpus.get("printedData") or {}).get("title") != "SERIOUS\nWOUND":
        raise AssertionError("Serious Wound shared-back boundary changed")

    official_projection = []
    for counterpart in OFFICIAL_VISIBLE_COUNTERPARTS:
        parent = visual_by_id[counterpart["parentOccurrenceId"]]
        official_projection.append({
            **counterpart,
            "sourceId": "SRC-RULEBOOK",
            "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
            "sourceSha256": _sha(repo / "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"),
            "parentVisualType": parent["type"],
            "parentBbox160Dpi": parent["bbox"],
            "sourceScopedOnly": True,
        })

    face_backlog_ids = ["CARD:" + source_asset_by_key[key]["sourceSha256"][:16] for key in ASSET_DEFINITIONS]
    linked_backlog_ids = [
        *face_backlog_ids,
        "RULE:ACT-MOVE-001",
        "RULE:ACT-CARD-001",
        "RULE:INT-006",
        "RULE:INT-008",
        "RULE:RT-007",
        "RULE:RT-012",
        "ROOM:03",
        "ROOM:16",
        "VIS:RB-P03-V01",
        "VIS:RB-P09-V01",
        "VIS:RB-P17-V03",
        "VIS:RB-P18-V01",
        "VIS:RB-P18-V02",
        "VIS:RB-P18-V03",
        "VIS:RB-P40-V02",
    ]
    if len(face_backlog_ids) != 11 or len(set(face_backlog_ids)) != 11 or any(unit_id not in backlog_by_id for unit_id in linked_backlog_ids):
        raise AssertionError("Serious Wound source-obligation backlog closure failed")

    classification_by_guid = {row["guid"]: row for row in classification}
    augmented = classification_by_guid.get("94ae47") or {}
    if augmented.get("verdict") != "expansion" or augmented.get("description") != "AUGMENTED BODY":
        raise AssertionError("Serious Wound expansion/wound-like exclusion drift")

    title_counts = Counter(row["printedTitle"] for row in face_rows)
    physical_icon_counts = Counter(icon.get("semanticReferenceId") or "source-local-no-match" for row in face_rows for icon in row["iconOccurrences"])
    selected_asset_rows = [row for row in source_asset_rows if row["selectedByRootDeck"]]
    all_asset_icons = [icon for row in source_asset_rows for icon in row["iconOccurrences"]]
    return {
        "schemaVersion": 1,
        "recordType": "semantic-serious-wound-source-index",
        "scope": "entire mechanically derived base Serious Wound card/component family; 27 physical occurrences, repeated copies, generated/direct faces, two selector-gap source variants, one parent sheet, shared back, official visible occurrences, licensed rows, and conflicts remain independent",
        "derivationPolicy": "Derive physical cards only from the sole base seriouswoundDeck Lua role and exact raw root Deck GUID, saved DeckIDs order, contained full CardID/GUID/CustomDeck/FaceURL/BackURL tuples, and for generated faces the exact source-sheet hash/grid/cell evidence. Never join by display title, body resemblance, folder, saved sequence alone, CardID modulo, or licensed key. Preserve unselected cells, official occurrences, and licensed rows independently.",
        "counts": {
            "physicalFaceOccurrences": len(face_rows),
            "uniquePrintedTitles": len(title_counts),
            "uniqueSelectedFaceAssets": len({row["sourceSha256"] for row in face_rows}),
            "sourceFaceAssets": len(source_asset_rows),
            "generatedPhysicalFaceOccurrences": sum((row["sourceSelector"] or {}).get("generatedSpriteSheetCell") is True for row in face_rows),
            "directPhysicalFaceOccurrences": sum((row["sourceSelector"] or {}).get("generatedSpriteSheetCell") is False for row in face_rows),
            "sourceSheets": 1,
            "sourceSheetCells": 9,
            "selectedGeneratedCells": sum(row["selectedByRootDeck"] and row["generatedCell"] is not None for row in source_asset_rows),
            "selectorGapCells": sum(not row["selectedByRootDeck"] for row in source_asset_rows),
            "sharedBackOccurrences": 1,
            "sharedBackSelectorReferences": back_provenance["refs"],
            "sourceSheetSelectorReferences": sheet_provenance["refs"],
            "rootCustomDeckEntries": len(root_custom),
            "physicalRegions": sum(len(row["regions"]) for row in face_rows),
            "operativeRegions": sum(sum(region["operative"] for region in row["regions"]) for row in face_rows),
            "physicalPanels": sum(len(row["panels"]) for row in face_rows),
            "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in face_rows),
            "headingRegionOccurrences": len(face_rows),
            "artworkInterfaceRegionOccurrences": len(face_rows),
            "sourceAssetRegions": sum(len(row["regions"]) for row in source_asset_rows),
            "sourceAssetPanels": sum(len(row["panels"]) for row in source_asset_rows),
            "printedSentenceOccurrences": sum(len(row["sentences"]) for row in face_rows),
            "sourceAssetSentenceOccurrences": sum(len(row["sentences"]) for row in source_asset_rows),
            "physicalFunctionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in face_rows),
            "physicalMatchedIconOccurrences": sum(count for key, count in physical_icon_counts.items() if key != "source-local-no-match"),
            "physicalUnresolvedLocalGlyphOccurrences": physical_icon_counts["source-local-no-match"],
            "selectedAssetFunctionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in selected_asset_rows),
            "allSourceAssetFunctionalIconOccurrences": len(all_asset_icons),
            "allSourceAssetMatchedIconOccurrences": sum(icon["semanticReferenceId"] is not None for icon in all_asset_icons),
            "allSourceAssetUnresolvedLocalGlyphOccurrences": sum(icon["semanticReferenceId"] is None for icon in all_asset_icons),
            "literalAnatomyOrRegionHeadingOccurrences": sum(row["literalHeadingClass"] != "literal-condition-heading" for row in face_rows),
            "literalConditionHeadingOccurrences": sum(row["literalHeadingClass"] == "literal-condition-heading" for row in face_rows),
            "licensedDigitalOccurrences": len(bga),
            "licensedPlaceholderOccurrences": sum(len(re.findall(r"<[A-Z-]+>", "\n".join(row["effectDesc"]))) for row in bga.values()),
            "licensedPhysicalIdentityLinks": 0,
            "officialVisibleFaceOccurrences": sum(row["kind"] in {"face", "partial-face"} for row in official_projection),
            "officialVisibleBackOccurrences": sum(row["kind"] == "shared-back" for row in official_projection),
            "officialRulebookTextOccurrences": len(OFFICIAL_RULEBOOK_TEXT_OCCURRENCES),
            "officialRulebookVisualObligations": len(visual_ids),
            "baseApplicableFaqOccurrences": 0,
            "excludedExpansionFaqOccurrences": len(excluded_faq_hits),
            "excludedExpansionSeriousWoundDecks": 0,
            "excludedWoundLikeExpansionComponents": 1,
            "excludedParentSheetsFromFaceCount": 1,
            "excludedBacksFromFaceCount": 1,
            "excludedNonRulesOverlayClasses": 4,
            "backlogTuples": len(face_backlog_ids),
            "backlogPhysicalFaceLinks": len(face_rows),
            "backlogObligationsLinked": len(linked_backlog_ids),
            "semanticPhysicalFaceRecords": len(SERIOUS_WOUND_RULE_IDS),
        },
        "titleMultiplicity": {key: title_counts[key] for key in sorted(title_counts)},
        "familyCountEvidence": {
            "officialRulebook": {"sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf", "locator": "unprinted PDF page 3 / RB-P03-V01", "printedPhysicalCount": 27},
            "rawTtsDeck": {"sourcePath": RAW_SAVE_PATH, "sourceSha256": raw_save_sha, "rolePath": "assets/tts-mod/extract/v2/lua_roles.json", "role": "seriouswoundDeck", "deckGuid": BASE_SERIOUS_WOUND_DECK_GUID, "deckIdsInSavedOrder": raw_deck_ids, "savedOrderIsGameplayDeckOrder": False, "setupRequiresShuffle": True, "physicalFaceCount": len(face_rows)},
            "closedCorpus": {"sourcePath": CORPUS_PATH, "physicalOccurrenceCount": len(face_rows), "selectedFaceAssetCount": len(selected_asset_rows), "sourceFaceAssetCount": len(source_asset_rows), "sourcePaths": [row["sourcePath"] for row in source_asset_rows]},
            "licensedDigital": {"sourcePath": BGA_SERIOUS_WOUND_PATH, "indexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "table": "SERIOUS_WOUNDS_DATA", "structuredVariantCount": len(bga), "keysInSourceOrder": list(bga), "physicalIdentityCrosswalkAsserted": False},
            "backlog": {"sourcePath": "docs/rules/semantics/backlog.json", "faceTupleCount": len(face_backlog_ids), "physicalFaceLinkCount": len(face_rows), "faceUnitIds": face_backlog_ids, "linkedUnitIds": linked_backlog_ids},
        },
        "sourceSheet": {
            "sourceId": SERIOUS_WOUND_SHEET_SOURCE_ID,
            "occurrenceId": "TTS-SERIOUS-WOUND-PARENT-SHEET-38",
            "sourcePath": SERIOUS_WOUND_SHEET_PATH,
            "sourceSha256": _sha(sheet_path),
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS base Serious Wound 3x3 parent source sheet / root deck {BASE_SERIOUS_WOUND_DECK_GUID} / CustomDeck 38",
            "sourceSelector": {"key": "FaceURL", "objectType": "Deck", "guid": BASE_SERIOUS_WOUND_DECK_GUID, "customDeckId": "38", "url": SHEET_FACE_URL, "grid": {"columns": 3, "rows": 3}, "cellOrder": "row-major-top-left-zero-based", "referenceCount": sheet_provenance["refs"]},
            "rulesFaceCounted": False,
            "cells": [{"cell": row["generatedCell"], "sourcePath": row["sourcePath"], "sourceSha256": row["sourceSha256"], "selectedByRootDeck": row["selectedByRootDeck"], "selectorGap": row["selectorGap"]} for row in source_asset_rows if row["generatedCell"] is not None],
        },
        "sharedBack": {
            "sourceId": SERIOUS_WOUND_BACK_SOURCE_ID,
            "occurrenceId": "TTS-SERIOUS-WOUND-SHARED-BACK",
            "sourcePath": SERIOUS_WOUND_BACK_PATH,
            "sourceSha256": back_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS shared base Serious Wound back / root deck {BASE_SERIOUS_WOUND_DECK_GUID}",
            "sourceSelector": {"key": "BackURL", "objectType": "Deck", "guid": BASE_SERIOUS_WOUND_DECK_GUID, "url": SHARED_BACK_URL, "sideRole": "shared-non-operative-back", "rootDeckSelectorCount": 1, "baseCardSelectorCount": 27, "referenceCount": back_provenance["refs"]},
            "printedTitle": "SERIOUS\nWOUND",
            "rulesTextPresent": False,
            "separateRulesFace": False,
        },
        "sourceFaceAssets": source_asset_rows,
        "officialRulebookTextOccurrences": OFFICIAL_RULEBOOK_TEXT_OCCURRENCES,
        "officialVisibleCounterparts": official_projection,
        "faqSearchClosure": {
            "sourceId": "SRC-FAQ",
            "baseApplicableOccurrences": [],
            "excludedExpansionOccurrences": [{"sourceUnitId": row["sourceUnitId"], "section": row.get("section"), "applicability": row.get("applicability"), "printedText": row.get("printedText")} for row in excluded_faq_hits],
            "boundary": "FAQ v1.2 contains no base-applicable Serious Wound ruling; expansion Health/Wound material is retained but excluded from base conclusions.",
        },
        "licensedDigitalOccurrences": [bga[key] for key in bga],
        "crossSourceIdentityBoundary": {
            "licensed": "All nine SERIOUS_WOUNDS_DATA rows remain independent licensed occurrences. No display-title/body/folder/sequence/modulo join to a TTS physical copy is asserted.",
            "official": "Two complete official EYES occurrences, one partial ARM occurrence, and two visible backs control only their exact publisher occurrences/versions; none identifies one of the three TTS GUID copies.",
            "selectorGaps": "Generated cells 4 and 6 remain exact source-sheet variants with explicit selector gaps; matching titles or effect resemblance do not connect them to direct root-deck LEG/KNEE copies.",
        },
        "excludedContent": {
            "expansionSeriousWoundDecks": [],
            "expansionWoundLikeComponents": [{"guid": "94ae47", "description": "AUGMENTED BODY", "nickname": "Flip serious wound to disable their effect", "verdict": "expansion", "boundary": "Convict expansion Item/card effect referencing Serious Wounds; not a Serious Wound deck face."}],
            "parentSheetBoundary": "The 3x3 parent sheet is provenance, not a twenty-eighth rules face; its nine generated cells are source assets, of which only seven cells have exact root-deck selectors.",
            "selectorGapBoundary": "Sheet cells 4 (LEG) and 6 (KNEE) have no root DeckID/GUID selector and are retained as source variants, not substituted for the six direct physical LEG/KNEE occurrences.",
            "sharedBackBoundary": "One shared BackURL is referenced by the root and all 27 cards; it is not a twenty-eighth rules face.",
            "overlayBoundary": "Radiographic anatomy art, TEMP./39.0/TISSUE DAMAGE labels, green nodes, colored callouts, faint microtext, and scan overlays are source layout/artwork rather than operative rules text.",
            "placeholderPrototypeBoundary": "No additional wound-tagged root child, placeholder, prototype, expansion deck, or card-like overlay enters the 27 physical occurrence set.",
            "duplicateReferenceBoundary": "Root, child, sheet, generated crop, corpus, selected evidence, official, licensed, and backlog references are evidence links rather than extra physical cards.",
        },
        "faces": face_rows,
    }


def serious_wound_source_registry_rows(source_index: dict) -> list[dict]:
    rows = []
    for face in source_index["faces"]:
        rows.append({
            "sourceId": face["sourceId"],
            "authority": face["sourceAuthority"],
            "version": face["sourceVersion"],
            "path": face["sourcePath"],
            "sha256": face["sourceSha256"],
            "occurrenceId": face["seriousWoundOccurrenceId"],
            "evidenceIndexPath": face["corpusEvidencePath"],
            "evidenceRecord": face["sourceSha256"],
            "provenanceIndexPath": face["provenanceEvidencePath"],
        })
    sheet = source_index["sourceSheet"]
    rows.append({"sourceId": sheet["sourceId"], "authority": sheet["sourceAuthority"], "version": sheet["sourceVersion"], "path": sheet["sourcePath"], "sha256": sheet["sourceSha256"], "occurrenceId": sheet["occurrenceId"], "evidenceIndexPath": LOW_CONFIDENCE_PATH, "evidenceRecord": sheet["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    back = source_index["sharedBack"]
    rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    for asset in source_index["sourceFaceAssets"]:
        if not asset["sourceId"]:
            continue
        rows.append({"sourceId": asset["sourceId"], "authority": "source-bound-component-scan", "version": f"TTS base Serious Wound unselected generated source variant / CustomDeck 38 / cell {asset['generatedCell']}", "path": asset["sourcePath"], "sha256": asset["sourceSha256"], "occurrenceId": f"TTS-SERIOUS-WOUND-VARIANT-38-CELL-{asset['generatedCell']:02d}", "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": asset["sourceSha256"], "provenanceIndexPath": LOW_CONFIDENCE_PATH})
    rows.append({"sourceId": BGA_SERIOUS_WOUND_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / SERIOUS_WOUNDS_DATA", "path": BGA_SERIOUS_WOUND_PATH, "sha256": _sha(Path(__file__).resolve().parents[1] / BGA_SERIOUS_WOUND_PATH), "occurrenceId": "SERIOUS_WOUNDS_DATA", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "SERIOUS_WOUNDS_DATA"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None, visibility: str = "public") -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": visibility}


def build_serious_wound_records(repo: Path, source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo
    records = []
    face_by_occurrence = {row["seriousWoundOccurrenceId"]: row for row in source_index["faces"]}
    all_source_ids = [row["sourceId"] for row in source_index["faces"]]

    records.append(record(
        "SEM-SERIOUS-WOUND-SETUP-001", "Set up the finite Serious Wound deck", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-SW-SETUP-RB", "SRC-RULEBOOK", "unprinted page 3 and printed page 9 / RB-P03-V01/RB-P09-V01 / lines 2594–2600", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "The base game has 27 Serious Wound cards. Shuffle the deck separately, place it face down, and leave a separate Serious Wound discard pile.", "docs/rules/semantics/serious-wound-source-index.json:familyCountEvidence")],
        ["term.serious-wound-card"], ["tax.entity.component.card.serious-wound", "tax.scaffold.supply-pool", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-SW-SETUP", "tax.entity.component.card.serious-wound", "when-triggered", "once-during-base-setup"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-SW-SETUP", "subjectRef": "27 exact physical card identities, shuffled order, operative fronts, shared back, and empty discard pile", "audience": "hidden-from-all fronts/order; public shared back/count/deck/discard locations", "revealTrigger": "source-defined Wound gain and placement", "secrecy": "setup does not inspect fronts or order"}], [], [],
        [operation("S01", 1, "shuffle", "must", "P-RULES", "all 27 exact base Serious Wound physical occurrences", ["SA-SW-SETUP-RB"], repeat={"physicalCardCount": 27}), operation("S02", 2, "transition-zone", "must", "P-RULES", "all shuffled Serious Wound cards face down", ["SA-SW-SETUP-RB"], transition={"from": "tax.scaffold.supply-pool", "to": "tax.scaffold.zone.deck"}), operation("S03", 3, "set-state", "must", "P-RULES", "separate empty Serious Wound discard pile available for discarded cards", ["SA-SW-SETUP-RB"])],
        {"policy": "ordered-complete", "unit": "Serious Wound setup", "onImpossible": "setup requires all 27 exact physical cards; do not substitute the parent sheet, shared back, selector-gap cells, licensed rows, official examples, expansion references, or overlays"}, {"kind": "persistent-setup-state"}, {"policy": "one shuffled finite 27-card deck and one separate discard pile; no setup-derived gameplay order"}, [], [], []))

    gain_component_assertions = []
    gain_component_ids = []
    for definition in PHYSICAL_DEFINITIONS:
        source = face_by_occurrence[definition["occurrenceId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        assertion_id = f"SA-SW-GAIN-FACE-{code}"
        item = assertion(assertion_id, definition["sourceId"], f"{definition['occurrenceId']} / exact physical selector, face, and effect", ["informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], source["printedBody"], f"docs/rules/semantics/serious-wound-source-index.json:{definition['occurrenceId']}")
        item["textKind"] = "verbatim"
        gain_component_assertions.append(item)
        gain_component_ids.append(assertion_id)
    gain_rulebook = assertion("SA-SW-GAIN-RB", "SRC-RULEBOOK", "printed pages 3, 9, 17, and 18 / RB-P18-V01/V03 / lines 3784–3804", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "outcomes", "unresolvedQuestionRefs"], "Draw one random finite Serious Wound; place it over all three slots of the leftmost Health Section without a Wound; displace a marker already in that Section to the first empty slot of the next Section; duplicates may exist but exact duplicate effects do not stack.", "docs/rules/semantics/serious-wound-source-index.json:officialRulebookTextOccurrences")
    gain_all_ids = ["SA-SW-GAIN-RB", *gain_component_ids]
    records.append(record(
        "SEM-SERIOUS-WOUND-GAIN-001", "Gain and place a random Serious Wound", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [gain_rulebook, *gain_component_assertions],
        ["term.serious-wound-card", "term.character-health", "term.health-point"], ["tax.entity.agent.character", "tax.entity.component.card.serious-wound", "tax.state.health", "tax.state.health.point", "tax.scaffold.zone.deck"], [],
        timing("TW-SW-GAIN", "tax.entity.component.card.serious-wound", "when-triggered", "once-per-source-requested-Wound-unless-a-source-explicitly-groups-multiple"), [participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must",
        [condition("C-SW-GAIN-DECK", "predicate", [{"predicate": "at least one physical Serious Wound remains in the face-down deck"}], ["SA-SW-GAIN-RB"]), condition("C-SW-GAIN-SECTION", "predicate", [{"predicate": "the affected Character has a Health Section without a Serious Wound under SEM-Q-031"}], ["SA-SW-GAIN-RB"])], [],
        [{"informationId": "I-SW-DECK", "subjectRef": "remaining Serious Wound fronts and order", "audience": "hidden-from-all", "revealTrigger": "SEM-Q-030 source-defined draw/placement reveal boundary", "secrecy": "do not expose unselected fronts/order in logs, accessibility output, clients, or spectators"}, {"informationId": "I-SW-DRAWN", "subjectRef": "drawn physical occurrence, heading, body, icons, destination Section, displacement, and active effect", "audience": "source-unspecified until SEM-Q-030; public placement is visually supported", "revealTrigger": "SEM-Q-030", "secrecy": "no face-up default is adopted from digital convenience"}], [],
        [_target("T-SW-GAIN-CARD", ["tax.entity.component.card.serious-wound"], mode="random", minimum=0, maximum=1), _target("T-SW-GAIN-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1), _target("T-SW-GAIN-HEALTH", ["tax.state.health"], minimum=0, maximum=1)],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "finite deck availability; discard pile is not reshuffled or returned", ["SA-SW-GAIN-RB"], target_ref="T-SW-GAIN-CARD", notes="Setup creates a separate discard pile; no checked Serious Wound rule returns or reshuffles it. An empty finite deck makes the requested component unavailable."),
            operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-031 whether a card is drawn and where it goes when all three Health Sections already contain Wounds", ["SA-SW-GAIN-RB"], conditions=["no Health Section lacks a Serious Wound"], target_ref="T-SW-GAIN-CHARACTER"),
            operation("S03", 3, "draw-random", "if-able", "P-RULES", "top random physical Serious Wound into resolution", gain_all_ids, conditions=["C-SW-GAIN-DECK", "C-SW-GAIN-SECTION"], target_ref="T-SW-GAIN-CARD"),
            operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-030 exact face-up/reveal timing for the drawn and placed Wound", ["SA-SW-GAIN-RB"], conditions=["a physical Wound was drawn"], target_ref="T-SW-GAIN-CARD"),
            operation("S05", 5, "select-target", "must", "P-RULES", "leftmost Health Section without a Serious Wound", ["SA-SW-GAIN-RB"], conditions=["a physical Wound was drawn"], target_ref="T-SW-GAIN-HEALTH"),
            operation("S06", 6, "place-component", "must", "P-RULES", "drawn Wound over all three slots of the selected Health Section", gain_all_ids, conditions=["a physical Wound was drawn"], target_ref="T-SW-GAIN-HEALTH"),
            operation("S07", 7, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-032 next-Section/death handling when the Health marker occupies the Heavily Injured Section receiving the Wound", ["SA-SW-GAIN-RB"], conditions=["Health marker is in the selected Heavily Injured Section"], target_ref="T-SW-GAIN-CHARACTER"),
            operation("S08", 8, "change-value", "if-able", "P-RULES", "Health marker to the first empty slot of the next Health Section, resolving Armor loss", ["SA-SW-GAIN-RB"], conditions=["Health marker is in the selected Healthy or Injured Section"], target_ref="T-SW-GAIN-CHARACTER", value_change={"amount": "advance-to-first-empty-slot-of-next-Health-Section", "value": "Character Health track position"}),
            operation("S09", 9, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-036 exact activation point for immediate and persistent printed effects relative to placement, displacement, Armor loss, and death", gain_all_ids, conditions=["a physical Wound was placed"], target_ref="T-SW-GAIN-CARD"),
            operation("S10", 10, "invoke-selected-process", "must", "P-RULES", "exact physical occurrence-specific Serious Wound effect", gain_all_ids, conditions=["a physical Wound was placed", "effect activation is reached under SEM-Q-036"], target_ref="T-SW-GAIN-CARD"),
            operation("S11", 11, "invoke-process", "must", "P-RULES", "exact-asset duplicate non-stacking constraint", ["SA-SW-GAIN-RB"], conditions=["a physical Wound was placed"], target_ref="T-SW-GAIN-CARD", invoke="SEM-SERIOUS-WOUND-STACKING-001"),
            operation("S12", 12, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-038 assignment/order/shortfall boundaries when a source requests multiple Serious Wounds without a complete order", ["SA-SW-GAIN-RB"], conditions=["caller requests multiple Wounds in one unresolved instruction"], target_ref="T-SW-GAIN-CHARACTER"),
        ],
        {"policy": "source-limited-components", "unit": "one source-requested random physical Wound and one leftmost eligible Health Section", "onImpossible": "never reshuffle the discard pile; unavailable deck components do nothing; no-full-slot, Heavily-Injured displacement, reveal, activation, and multi-Wound defaults remain prohibited by SEM-Q-030/031/032/036/038"}, {"kind": "persistent-card-placement-plus-triggered-effect"}, {"policy": "each successful gain places one exact physical card; exact-asset duplicate effects do not stack; different assets/titles/variants are never merged"}, [{"condition": "placed Wound covers a Health Section", "result": "covered slots are unusable for current and maximum Health until that Wound is discarded"}], ["SEM-Q-030", "SEM-Q-031", "SEM-Q-032", "SEM-Q-036", "SEM-Q-038"], []))
    records[-1]["operations"][9]["dispatchRuleIds"] = list(SERIOUS_WOUND_RULE_IDS)

    records.append(record(
        "SEM-SERIOUS-WOUND-DISCARD-001", "Discard one owned Serious Wound", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-SW-DISCARD-RB", "SRC-RULEBOOK", "printed page 18 / lines 3797–3804", ["timing", "participants", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "outcomes"], "When an effect discards a Serious Wound, the affected Character may choose which physical Wound if more than one exists; move it to the Serious Wound discard pile, slide remaining Wounds left, and do not move the Health marker merely because of the discard.", "docs/rules/semantics/serious-wound-source-index.json:officialRulebookTextOccurrences")],
        ["term.serious-wound-card", "term.character-health"], ["tax.entity.agent.character", "tax.entity.component.card.serious-wound", "tax.state.health", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-SW-DISCARD", "tax.entity.component.card.serious-wound", "when-triggered", "once-per-source-instructed-discard"), [participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [],
        [decision("D-SW-DISCARD", "P-OWNER", "player-choice", 1, 1, False, "public-on-declaration", ["each exact physical Serious Wound currently owned by the affected Character"])],
        [{"informationId": "I-SW-DISCARD", "subjectRef": "eligible physical Wounds, selected card, remaining order, Health marker, and ending effect", "audience": "public", "revealTrigger": "selection/discard", "secrecy": "remaining deck fronts/order stay hidden"}], [],
        [_target("T-SW-DISCARD-CARD", ["tax.entity.component.card.serious-wound"], selector="P-OWNER", mode="player-choice", minimum=1, maximum=1), _target("T-SW-DISCARD-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1)],
        [operation("S01", 1, "select-target", "must", "P-OWNER", "one exact owned Serious Wound", ["SA-SW-DISCARD-RB"], decision_ref="D-SW-DISCARD", target_ref="T-SW-DISCARD-CARD"), operation("S02", 2, "transition-zone", "must", "P-RULES", "selected physical Serious Wound", ["SA-SW-DISCARD-RB"], decision_ref="D-SW-DISCARD", target_ref="T-SW-DISCARD-CARD", transition={"from": "affected Character Health Section", "to": "tax.scaffold.zone.discard-pile"}), operation("S03", 3, "set-state", "must", "P-RULES", "remaining Serious Wounds slide to the leftmost occupied Health Sections without changing their relative order", ["SA-SW-DISCARD-RB"], target_ref="T-SW-DISCARD-CHARACTER"), operation("S04", 4, "evaluate-condition", "must", "P-RULES", "Health marker does not move merely because the Wound was discarded", ["SA-SW-DISCARD-RB"], target_ref="T-SW-DISCARD-CHARACTER"), operation("S05", 5, "set-state", "must", "P-RULES", "discarded occurrence's printed effect ends; an exact-asset duplicate effect remains active if another matching physical copy is still owned", ["SA-SW-DISCARD-RB"], target_ref="T-SW-DISCARD-CARD")],
        {"policy": "all-or-nothing-selection", "unit": "one source-instructed physical Wound discard", "onImpossible": "the enclosing effect supplies its own legality/partial-resolution rule; this procedure never removes from game, returns to deck, reshuffles, changes Health, or chooses for the owner"}, {"kind": "instantaneous-discard-and-persistent-effect-removal"}, {"policy": "one selected physical copy per discard instruction; remaining exact duplicates preserve one non-stacking active effect"}, [], [], []))

    records.append(record(
        "SEM-SERIOUS-WOUND-STACKING-001", "Exact duplicate Serious Wound effects do not stack", "source-backed", "constraint", "official-primary", "verbatim-structure",
        [assertion("SA-SW-STACK-RB", "SRC-RULEBOOK", "printed page 18 / lines 3790–3793", ["timing", "preconditions", "operations", "partialResolution", "duration", "stacking"], "A Character may have two exactly the same Serious Wounds; do not stack their effects.", "docs/rules/semantics/serious-wound-source-index.json:officialRulebookTextOccurrences")],
        ["term.serious-wound-card"], ["tax.entity.component.card.serious-wound"], [],
        timing("TW-SW-STACK", "tax.entity.component.card.serious-wound", "when-triggered", "continuous-while-one-or-more-exact-selected-face-assets-are-owned"), [participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-SW-STACK", "subjectRef": "exact physical Wound copies, selected FaceURL/source hash, and active effect multiplicity", "audience": "public", "revealTrigger": "placement/discard", "secrecy": "deck order/fronts stay hidden"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "whether owned Wounds share the exact selected FaceURL and source SHA-256", ["SA-SW-STACK-RB"]), operation("S02", 2, "set-state", "must", "P-RULES", "at most one active printed effect for all owned physical copies of that exact selected face asset", ["SA-SW-STACK-RB"]), operation("S03", 3, "evaluate-condition", "must", "P-RULES", "matching title, body resemblance, source-sheet cell, folder, licensed key, or artwork does not establish stacking equivalence", ["SA-SW-STACK-RB"])],
        {"policy": "per-effect-check", "unit": "one candidate duplicate effect", "onImpossible": "without exact selected-face-asset equivalence, preserve separate effects/source variants and do not infer sameAs or a stacking key"}, {"kind": "persistent-while-matching-Wounds-remain"}, {"policy": "zero copies means inactive; one or more exact-asset copies means one active effect; physical copies remain separate components"}, [], [], []))

    gap_assets = [row for row in source_index["sourceFaceAssets"] if not row["selectedByRootDeck"]]
    bga_rows = source_index["licensedDigitalOccurrences"]
    official_faces = [row for row in source_index["officialVisibleCounterparts"] if row["kind"] in {"face", "partial-face"}]
    variant_assertions = []
    variant_operations = []
    variant_refs = []
    for index, asset in enumerate(gap_assets, 1):
        assertion_id = f"SA-SW-VARIANT-GAP-{asset['generatedCell']:02d}"
        item = assertion(assertion_id, asset["sourceId"], f"CustomDeck 38 / generated cell {asset['generatedCell']} / explicit selector gap", ["operations", "sourceVariants"], asset["printedBody"], f"docs/rules/semantics/serious-wound-source-index.json:sourceFaceAssets.{asset['assetKey']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve unselected generated cell {asset['generatedCell']} {asset['printedTitle']!r} body exactly; do not dispatch it as a physical root-deck card", [assertion_id]))
        variant_refs.append({"variantId": f"SV-SW-GAP-{asset['generatedCell']:02d}", "sourceId": asset["sourceId"], "sourceAssertionId": assertion_id, "difference": f"Generated cell {asset['generatedCell']} visibly prints {asset['printedTitle']!r} and {asset['printedBody']!r} but has no root DeckID/GUID selector.", "resolution": "Preserve as an independent source variant with an explicit selector gap; do not connect it to a direct physical card by title, body resemblance, cell number, or CardID modulo."})
    bga_assertion_id = "SA-SW-VARIANT-BGA"
    bga_text = "\n".join(row["sourceBlockText"] for row in bga_rows)
    bga_assertion = assertion(bga_assertion_id, BGA_SERIOUS_WOUND_SOURCE_ID, "SERIOUS_WOUNDS_DATA / all nine rows in source order", ["operations", "sourceVariants"], bga_text, "docs/rules/semantics/serious-wound-source-index.json:licensedDigitalOccurrences")
    bga_assertion["textKind"] = "verbatim"
    variant_assertions.append(bga_assertion)
    for row in bga_rows:
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve licensed row SERIOUS_WOUNDS_DATA.{row['key']} independently: {row['effectDesc']!r}", [bga_assertion_id]))
        variant_refs.append({"variantId": f"SV-SW-BGA-{row['key'].upper()}", "sourceId": BGA_SERIOUS_WOUND_SOURCE_ID, "sourceAssertionId": bga_assertion_id, "difference": f"Licensed row {row['key']} prints name {row['name']!r} and effectDesc {row['effectDesc']!r}; no TTS physical identity crosswalk is source-backed.", "resolution": "Retain the licensed structured occurrence independently and below official/source-bound component authority; do not join it by display title or effect resemblance."})
    official_assertion_ids = []
    for index, counterpart in enumerate(official_faces, 1):
        assertion_id = f"SA-SW-VARIANT-OFFICIAL-{index:02d}"
        item = assertion(assertion_id, "SRC-RULEBOOK", counterpart["locator"], ["operations", "sourceVariants"], counterpart["visibleText"], f"docs/rules/semantics/serious-wound-source-index.json:{counterpart['sourceOccurrenceId']}")
        item["textKind"] = "verbatim"
        variant_assertions.append(item)
        official_assertion_ids.append(assertion_id)
        variant_operations.append(operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", f"preserve official occurrence {counterpart['sourceOccurrenceId']} ({counterpart['completeness']}): {counterpart['visibleText']!r}", [assertion_id]))
        variant_refs.append({"variantId": f"SV-SW-OFFICIAL-{index:02d}", "sourceId": "SRC-RULEBOOK", "sourceAssertionId": assertion_id, "difference": f"Official occurrence {counterpart['sourceOccurrenceId']} visibly provides {counterpart['visibleText']!r} with completeness {counterpart['completeness']}; no TTS GUID/CardID copy is identified.", "resolution": "Official wording controls only this exact publisher occurrence/version; preserve all TTS physical copies, generated selector gaps, and licensed rows independently."})
    records.append(record(
        "SEM-SERIOUS-WOUND-VARIANT-BOUNDARIES-001", "Serious Wound cross-source variant boundaries", "source-variant", "constraint", "official-primary", "verbatim-structure",
        variant_assertions,
        ["term.serious-wound-card"], ["tax.entity.component.card.serious-wound"], [],
        timing("TW-SW-VARIANTS", "tax.entity.component.card.serious-wound", "when-triggered", "per-source-comparison-or-canonicalization-attempt"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-SW-VARIANTS", "subjectRef": "two selector-gap scans, nine licensed rows, three official visible face occurrences, 27 physical TTS occurrences, and all wording differences", "audience": "public source evidence", "revealTrigger": "source audit", "secrecy": "does not reveal live shuffled deck order"}], [], [],
        [*variant_operations, operation(f"S{len(variant_operations)+1:02d}", len(variant_operations)+1, "evaluate-condition", "must", "P-RULES", "no display-title, body-resemblance, folder, saved-sequence, CardID-modulo, source-cell, or licensed-key identity join is asserted across variants", [row["assertionId"] for row in variant_assertions])],
        {"policy": "per-effect-check", "unit": "one proposed cross-source identity/effect merge", "onImpossible": "without an exact source-backed selector/correspondence, keep occurrences independent and preserve the conflict rather than selecting a default"}, {"kind": "persistent-source-audit-boundary"}, {"policy": "source variants do not stack, dispatch, or replace one another merely because labels/effects resemble"}, [], [], variant_refs))

    def build_face(definition: dict) -> dict:
        source = face_by_occurrence[definition["occurrenceId"]]
        code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
        scan_id = f"SA-SWF-{code}-SCAN"
        general_id = f"SA-SWF-{code}-GENERAL"
        assertions = [
            assertion(scan_id, definition["sourceId"], f"{definition['occurrenceId']} / exact selector, regions, heading, punctuation, sentences, and icons", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/serious-wound-source-index.json:{definition['occurrenceId']}"),
            assertion(general_id, "SRC-RULEBOOK", "printed page 18 / Serious Wounds and duplicate/discard rules", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "This exact physical occurrence is placed and activated only through the reusable Serious Wound gain procedure, remains persistent while owned, does not stack with exact selected-face-asset duplicates, and ends when this physical card is discarded.", "docs/rules/semantics/serious-wound-source-index.json:officialRulebookTextOccurrences"),
        ]
        assertions[0]["textKind"] = "verbatim"
        target_card = f"T-SWF-{code}-CARD"
        target_character = f"T-SWF-{code}-CHARACTER"
        targets = [_target(target_card, ["tax.entity.component.card.serious-wound"], minimum=1, maximum=1), _target(target_character, ["tax.entity.agent.character"], minimum=1, maximum=1)]
        participants = [participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")]
        decisions = []
        terms = ["term.serious-wound-card"]
        taxa = ["tax.entity.component.card.serious-wound", "tax.entity.agent.character"]
        for icon in source["iconOccurrences"]:
            if icon.get("semanticReferenceId"):
                terms.append(icon["semanticReferenceId"])
        ops = []

        def add(op_type: str, modality: str, subject: str, obj: str, *, sources=None, conditions=None, decision_ref=None, target_ref=target_character, transition=None, value_change=None, invoke=None, repeat=None, notes=None, sentence_sequence=1):
            step = len(ops) + 1
            op = operation(f"S{step:02d}", step, op_type, modality, subject, obj, sources or [scan_id, general_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref, transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = source["sentences"][sentence_sequence - 1]["sentenceId"]
            op["sourceRegionId"] = source["regions"][2]["regionId"]
            op["sourcePanelId"] = source["panels"][1]["panelId"]
            ops.append(op)
            return op

        kind = source["effectKind"]
        unresolved = ["SEM-Q-036"]
        recurrence = "continuous-while-this-physical-Wound-is-owned"
        if kind == "shoot-value-modifier":
            terms.append("term.shoot"); taxa.append("tax.process.action.attack.shoot")
            add("change-value", "must", "P-RULES", "all Shoot values of the affected Character +1 while this exact selected face asset is active", value_change={"amount": 1, "value": "source-printed Shoot values"})
        elif kind == "pass-contamination":
            terms.extend(["term.pass", "term.contamination-card"]); taxa.extend(["tax.process.action.pass", "tax.entity.component.card.contamination"]); unresolved.append("SEM-Q-037"); recurrence = "whenever-the-affected-Character-Passes-under-SEM-Q-037"
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-037 exact Pass-trigger order", sentence_sequence=1)
            add("invoke-process", "must", "P-AFFECTED-CHARACTER", "gain 1 Contamination card", conditions=["Pass trigger is reached under SEM-Q-037"], invoke="SEM-CONTAMINATION-GAIN-001", sentence_sequence=2)
        elif kind == "pass-health-loss":
            terms.extend(["term.pass", "term.character-health", "icon.characterHealth"]); taxa.extend(["tax.process.action.pass", "tax.state.health.point"]); unresolved.append("SEM-Q-037"); recurrence = "whenever-the-affected-Character-Passes-under-SEM-Q-037"
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-037 exact Pass-trigger order", sentence_sequence=1)
            add("invoke-process", "must", "P-AFFECTED-CHARACTER", "lose 1 Character Health through SEM-INT-006", conditions=["Pass trigger is reached under SEM-Q-037"], invoke="SEM-INT-006", repeat={"healthLoss": 1}, sentence_sequence=2)
        elif kind == "pass-oxygen-or-local-glyph":
            terms.extend(["term.pass", "icon.oxygen", "icon.lifeSupportActive"]); taxa.extend(["tax.process.action.pass", "tax.value.resource.oxygen"]); unresolved.extend(["SEM-Q-034", "SEM-Q-037"]); recurrence = "whenever-the-affected-Character-Passes-under-SEM-Q-037"
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-037 exact Pass-trigger order", sentence_sequence=1)
            add("change-value", "must", "P-RULES", "affected Character Oxygen -1 even in a Section with Active Life Support", conditions=["Pass trigger reached under SEM-Q-037", "affected Character had at least 1 Oxygen before this effect"], value_change={"amount": -1, "valueTaxonId": "tax.value.resource.oxygen"}, sentence_sequence=2)
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-034 identity and operation denoted by the source-local standalone stepped-zigzag glyph", conditions=["affected Character already had 0 Oxygen before this effect"], sentence_sequence=3, notes="Licensed <HP> is a lower-authority source variant and is not promoted into the literal TTS glyph.")
        elif kind == "use-item-cost-modifier":
            terms.extend(["term.item", "term.action", "icon.actionCard"]); taxa.extend(["tax.entity.component.card.item", "tax.process.action", "tax.entity.component.card.action"])
            add("change-value", "must", "P-RULES", "affected Character Use Item Action cost +1 Action card", value_change={"amount": 1, "value": "Use Item Action-card cost"})
        elif kind == "hand-slot-restriction":
            terms.extend(["term.item", "term.hand-slot"]); taxa.extend(["tax.entity.component.card.item", "tax.entity.component.slot.hand"])
            participants.append(participant("P-ITEM", "discard-candidate", "tax.entity.component.card.item"))
            decision_id = f"D-SWF-{code}-ITEM"
            decisions.append(decision(decision_id, "P-OWNER", "player-choice", 1, 1, False, "public-on-discard", ["one Item in either occupied Hand slot when both are occupied at activation"]))
            targets.append(_target(f"T-SWF-{code}-ITEM", ["tax.entity.component.card.item"], selector="P-OWNER", mode="player-choice", minimum=0, maximum=1))
            add("set-state", "must", "P-RULES", "affected Character has only 1 usable Hand slot", sentence_sequence=1)
            add("choose", "must", "P-OWNER", "one Item from one occupied Hand slot", conditions=["both Hand slots contain Items when the effect activates under SEM-Q-036"], decision_ref=decision_id, target_ref=f"T-SWF-{code}-ITEM", sentence_sequence=2)
            add("transition-zone", "must", "P-RULES", "selected Item to its discard destination", conditions=["both Hand slots contain Items when the effect activates under SEM-Q-036"], decision_ref=decision_id, target_ref=f"T-SWF-{code}-ITEM", transition={"from": "selected Hand slot", "to": "tax.scaffold.zone.discard-pile"}, sentence_sequence=2)
        elif kind == "hand-size-modifier":
            unresolved.append("SEM-Q-035")
            add("change-value", "must", "P-RULES", "source-local Hand Size -1", value_change={"amount": -1, "value": "source-local Hand Size"})
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-035 whether Hand Size changes only Cleanup refill, imposes a cap/discard, or has another scope")
        elif kind == "move-cost-modifier":
            terms.extend(["term.move", "icon.intruder", "icon.actionCard"]); taxa.extend(["tax.process.action.move", "tax.entity.agent.intruder", "tax.entity.component.card.action"])
            add("change-value", "must", "P-RULES", "Make a Move Action cost +1 Action card when starting in a Room with an Intruder", conditions=["affected Character begins Make a Move in a Room with an Intruder"], value_change={"amount": 1, "value": "Make a Move Action-card cost"})
        elif kind == "local-action-cost-modifier":
            terms.append("icon.actionCard"); taxa.append("tax.entity.component.card.action"); unresolved.append("SEM-Q-033")
            add("resolve-open-alternative", "must", "P-RULES", "SEM-Q-033 identity/scope of the local two-overlapping-angular-lobes glyph inside the quoted Action name")
            add("change-value", "if-able", "P-RULES", "the exact quoted local-glyph Action cost +1 Action card", conditions=["the source-local glyph identity and applicable Action are established under SEM-Q-033"], value_change={"amount": 1, "value": "source-local quoted Action-card cost"})
        else:
            raise AssertionError(f"unexpected selected Serious Wound effect kind: {kind}")

        unresolved = list(dict.fromkeys(unresolved))
        return record(
            definition["semanticRuleId"], f"Serious Wound physical occurrence {code}", "source-backed-with-open-question", "component-effect", "official-primary", "open-alternatives",
            assertions, terms, taxa, [], timing(f"TW-SWF-{code}", "tax.entity.component.card.serious-wound", "when-triggered", recurrence), participants, "must",
            [condition(f"C-SWF-{code}", "all", [{"predicate": f"active physical Serious Wound occurrence is {definition['occurrenceId']}"}, {"predicate": "this exact selected face asset is not already contributing its one non-stacking effect through another owned copy"}], [scan_id, general_id])],
            decisions,
            [{"informationId": f"I-SWF-{code}", "subjectRef": "exact physical occurrence, printed heading/body/icons, affected Character, active effect, and duplicate status", "audience": "public after source-defined placement reveal", "revealTrigger": "SEM-SERIOUS-WOUND-GAIN-001 under SEM-Q-030", "secrecy": "sibling fronts and deck order remain hidden"}], [], targets, ops,
            {"policy": "source-conditional-steps", "unit": "one exact physical Serious Wound occurrence's printed effect", "onImpossible": "generic draw/placement/discard/slide remains in reusable procedures; local glyph, Hand Size, Pass order, and activation timing retain explicit no-default gates"}, {"kind": "persistent-while-this-physical-card-is-owned; triggered clauses recur only at their printed timing"}, {"policy": "one active effect per exact selected FaceURL/source SHA-256; three physical copies remain distinct but their duplicate effects do not stack"}, [], unresolved, [])

    records.extend(build_face(definition) for definition in PHYSICAL_DEFINITIONS)
    return records
