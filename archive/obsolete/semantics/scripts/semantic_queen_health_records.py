from __future__ import annotations

import ast
from collections import Counter
import hashlib
import json
import re
from pathlib import Path

from semantic_attack_records import _find_guid, _parse_value


BASE_QUEEN_HEALTH_DECK_GUID = "9acd7f"
QUEEN_HEALTH_BACK_SOURCE_ID = "SRC-QUEEN-HEALTH-BACK"
QUEEN_HEALTH_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-017.png"
BGA_QUEEN_HEALTH_SOURCE_ID = "SRC-BGA-QUEEN-HEALTH"
BGA_QUEEN_HEALTH_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
OBJECTIVE_HELP_SOURCE_ID = "SRC-OBJECTIVE-HELP"
OBJECTIVE_HELP_PATH = "docs/rulebooks/Nemesis_RT_Objectives_Sheet.pdf"
RAW_SAVE_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
SELECTED_EVIDENCE_PATH = "assets/tts-mod/extract/selected-card-text-evidence.json"
CORPUS_PATH = "assets/tts-mod/extract/card-text-corpus.json"
PROVENANCE_PATH = "assets/tts-mod/extract/card-provenance-inventory.json"


def _definition(
    sequence: int,
    card_id: int,
    guid: str,
    custom_deck_id: str,
    source_path: str,
    *,
    discard_count: int,
    body: str,
    effect_kind: str,
    bga_candidate_keys: list[str],
    bga_match_status: str = "exact-functional-tuple-candidate",
    official_refs: list[str] | None = None,
) -> dict:
    code = f"{card_id}-{guid.upper()}"
    return {
        "ttsSavedSequence": sequence,
        "ttsCardId": card_id,
        "ttsCardGuid": guid,
        "customDeckId": custom_deck_id,
        "sourcePath": source_path,
        "sourceId": f"SRC-QUEEN-HEALTH-{code}",
        "occurrenceId": f"TTS-QUEEN-HEALTH-{code}-FACE",
        "semanticRuleId": f"SEM-QUEEN-HEALTH-{code}-001",
        "discardCount": discard_count,
        "body": body,
        "effectKind": effect_kind,
        "bgaCandidateKeys": bga_candidate_keys,
        "bgaMatchStatus": bga_match_status,
        "officialCounterpartRefs": official_refs or [],
    }


QUEEN_HEALTH_DEFINITIONS = [
    _definition(
        1,
        424300,
        "615e22",
        "4243",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-039.png",
        discard_count=0,
        body="0\nadditional cards.\n\nIf the card was drawn by a [character]:\n\nRepel the Queen.",
        effect_kind="repel",
        bga_candidate_keys=["QueenHealthCard1"],
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL"],
    ),
    _definition(
        2,
        424500,
        "0dd25f",
        "4245",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-040.png",
        discard_count=0,
        body="0\nadditional cards.\n\nIf the card was drawn by a [character].\n\nPlace the Queen back in the pool.",
        effect_kind="return-pool",
        bga_candidate_keys=["QueenHealthCard3"],
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL"],
    ),
    _definition(
        3,
        503700,
        "e4ab1c",
        "5037",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-013.png",
        discard_count=0,
        body="0\nadditional cards.\n\nIf the card was drawn by a [character].\n\nActivate the Queen.",
        effect_kind="activate",
        bga_candidate_keys=["QueenHealthCard2"],
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL"],
    ),
    _definition(
        4,
        504100,
        "717b23",
        "5041",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-084.png",
        discard_count=1,
        body="1\nadditional cards.\n\nIf the card was drawn by a [character].\n\nRepel the Queen.",
        effect_kind="repel",
        bga_candidate_keys=["QueenHealthCard4", "QueenHealthCard5"],
        bga_match_status="duplicate-functional-tuple-candidate-set",
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL", "RB-P35-V02-QH-FACE-DISCARD-1-REPEL"],
    ),
    _definition(
        5,
        504200,
        "ca5827",
        "5042",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-084.png",
        discard_count=1,
        body="1\nadditional cards.\n\nIf the card was drawn by a [character].\n\nRepel the Queen.",
        effect_kind="repel",
        bga_candidate_keys=["QueenHealthCard4", "QueenHealthCard5"],
        bga_match_status="duplicate-functional-tuple-candidate-set",
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL", "RB-P35-V02-QH-FACE-DISCARD-1-REPEL"],
    ),
    _definition(
        6,
        504000,
        "919263",
        "5040",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-126.png",
        discard_count=1,
        body="1\nadditional cards.\n\nIf the card was drawn by a [character].\n\nAdd all Queen tokens to the bag.",
        effect_kind="add-queen-tokens",
        bga_candidate_keys=["QueenHealthCard6"],
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL"],
    ),
    _definition(
        7,
        503900,
        "b42831",
        "5039",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-164.png",
        discard_count=1,
        body="1\nadditional cards.\n\nIf the card was drawn by a [character].\n\nEach [character] in the Room with the Queen\nDraws 2 [actionCard].",
        effect_kind="draw-action-cards",
        bga_candidate_keys=["QueenHealthCard7"],
        official_refs=["RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL"],
    ),
    _definition(
        8,
        503800,
        "64ae0a",
        "5038",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-165.png",
        discard_count=2,
        body="2\nadditional cards.\n\nIf the card was drawn by a [character].\n\nEach [character] in the Room with the Queen\nMakes a Noise roll.",
        effect_kind="noise-rolls",
        bga_candidate_keys=["QueenHealthCard9"],
    ),
    _definition(
        9,
        424100,
        "a10f34",
        "4241",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-038.png",
        discard_count=2,
        body="2\nadditional cards.\n\nIf the card was drawn by a [character].\n\nRepel the Queen.",
        effect_kind="repel",
        bga_candidate_keys=["QueenHealthCard8"],
    ),
    _definition(
        10,
        458100,
        "6ba0a2",
        "4581",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-041.png",
        discard_count=3,
        body="3\nadditional cards.\n\nIf the card was drawn by a [character]:\n\nPlace a [malfunction] in the Queen's Room.\nOR\nUnreinforce Queen's Corridor.",
        effect_kind="malfunction-or-unreinforce",
        bga_candidate_keys=["QueenHealthCard12"],
        bga_match_status="material-source-variant-conflict",
    ),
    _definition(
        11,
        429200,
        "48a2ae",
        "4292",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-045.png",
        discard_count=3,
        body="3\nadditional cards.\n\nIf the card was drawn by a [character].\n\nActivate the Queen.",
        effect_kind="activate",
        bga_candidate_keys=["QueenHealthCard10", "QueenHealthCard11"],
        bga_match_status="duplicate-functional-tuple-candidate-set",
    ),
    _definition(
        12,
        429200,
        "0fbf8d",
        "4292",
        "assets/tts-mod/extract/v2-dl/tree/cards/game/queenHealthDeck-045.png",
        discard_count=3,
        body="3\nadditional cards.\n\nIf the card was drawn by a [character].\n\nActivate the Queen.",
        effect_kind="activate",
        bga_candidate_keys=["QueenHealthCard10", "QueenHealthCard11"],
        bga_match_status="duplicate-functional-tuple-candidate-set",
    ),
]

QUEEN_HEALTH_RULE_IDS = [row["semanticRuleId"] for row in QUEEN_HEALTH_DEFINITIONS]
QUEEN_HEALTH_QUESTION_BLOCKS = {
    "SEM-Q-025": ["SEM-ACT-SHOOT-001", "SEM-ACT-BURST-001", "SEM-QUEEN-HIT-001", "SEM-QUEEN-HEALTH-RESOLUTION-001"],
    "SEM-Q-026": ["SEM-QUEEN-HEALTH-RESOLUTION-001", *QUEEN_HEALTH_RULE_IDS],
    "SEM-Q-027": ["SEM-QUEEN-HEALTH-RESOLUTION-001", "SEM-QUEEN-DEATH-001", *QUEEN_HEALTH_RULE_IDS],
    "SEM-Q-028": ["SEM-QUEEN-HEALTH-458100-6BA0A2-001"],
    "SEM-Q-029": ["SEM-ACT-SHOOT-001", "SEM-QUEEN-HIT-001"],
}

LOCAL_DISPLAY_MORPHOLOGY = {
    0: "Large near-square octagonal outline made from separated horizontal, vertical, and diagonal glowing green segments, with gaps at the middle of both sides, containing a tall narrow white 0-like glyph in a dark translucent green interior.",
    1: "Large near-square octagonal outline made from separated horizontal, vertical, and diagonal glowing green segments, with side gaps, containing a white 1 with angled upper-left flag, straight stem, broad basal foot, and gray shadow in a dark translucent green interior.",
    2: "Large near-square octagonal outline made from separated horizontal, vertical, and diagonal glowing green segments, with side gaps, containing a white 2 with curved top, descending diagonal middle, horizontal basal stroke, and gray shadow in a dark translucent green interior.",
    3: "Large near-square octagonal outline made from separated horizontal, vertical, and diagonal glowing green segments, with gaps at the middle of both sides, containing a large white 3 in a dark translucent green interior.",
}

OFFICIAL_VISIBLE_COUNTERPARTS = [
    {
        "sourceOccurrenceId": "RB-P03-V01-QH-FACE-DISCARD-0-PARTIAL",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "partial-face",
        "locator": "unprinted PDF page 3 / bottom-right Queen Health spread / rear upper-left face",
        "visibleText": "Discard\n0",
        "completeness": "same-family face; remaining operative text physically occluded",
        "candidateDiscardCount": 0,
    },
    {
        "sourceOccurrenceId": "RB-P03-V01-QH-FACE-DISCARD-1-PARTIAL",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "partial-face",
        "locator": "unprinted PDF page 3 / bottom-right Queen Health spread / rear upper-right face",
        "visibleText": "Discard\n1",
        "completeness": "same-family face; remaining operative text physically occluded",
        "candidateDiscardCount": 1,
    },
    {
        "sourceOccurrenceId": "RB-P03-V01-QH-BACK",
        "parentOccurrenceId": "RB-P03-V01",
        "kind": "shared-back",
        "locator": "unprinted PDF page 3 / bottom-right Queen Health spread / front card back",
        "visibleText": "QUEEN HEALTH\nPRIMEBLOOD",
        "completeness": "visible family back; non-operative",
        "candidateDiscardCount": None,
    },
    {
        "sourceOccurrenceId": "RB-P35-V02-QH-FACE-DISCARD-1-REPEL",
        "parentOccurrenceId": "RB-P35-V02",
        "kind": "face",
        "locator": "printed page 35 / Queen Health card anatomy example",
        "visibleText": "Discard\n1\nadditional card.\nRepel the Queen.",
        "completeness": "official visible current component occurrence; panel structure and exposed wording control only this occurrence",
        "candidateDiscardCount": 1,
    },
    {
        "sourceOccurrenceId": "RB-P35-V02-QH-BACK",
        "parentOccurrenceId": "RB-P35-V02",
        "kind": "shared-back",
        "locator": "printed page 35 / Queen Health card anatomy example",
        "visibleText": "QUEEN HEALTH\nPRIMEBLOOD",
        "completeness": "visible family back; non-operative",
        "candidateDiscardCount": None,
    },
]

OFFICIAL_RULEBOOK_TEXT_OCCURRENCES = [
    {"occurrenceId": "RB-QH-INVENTORY", "section": "inventory", "locator": "unprinted PDF page 3 / rulebook_text line 524", "sourceText": "12 Queen Health cards."},
    {"occurrenceId": "RB-QH-SETUP-01", "section": "setup", "locator": "printed page 10 / lines 2583–2587", "sourceText": "Shuffle all Queen Health cards and place them numbers-side down; place a Universal marker on 0 of the Queen's Hits track."},
    {"occurrenceId": "RB-QH-BURST-01", "section": "burst", "locator": "printed page 33 / lines 5514–5529", "sourceText": "A Character may apply any number of Burst Hits to the Queen up to her Hits track maximum; leftover Hits are lost."},
    {"occurrenceId": "RB-QH-SHOOT-01", "section": "shoot", "locator": "printed page 33 / lines 5576–5605", "sourceText": "Shoot deals 1 Hit before the Shoot roll; Larvae and the Queen use different Health resolution."},
    {"occurrenceId": "RB-QH-MELEE-01", "section": "melee", "locator": "printed page 34 / lines 5628–5669", "sourceText": "Melee deals 1 Hit before its Shoot-die roll; the Queen's Health resolves differently."},
    {"occurrenceId": "RB-QH-HITS-01", "section": "queen-health", "locator": "printed page 35 / lines 5791–5800", "sourceText": "For each Hit dealt to the Queen, advance the Universal marker on the Queen's Hits track by 1 instead of placing markers near the model."},
    {"occurrenceId": "RB-QH-THRESHOLD-01", "section": "queen-health", "locator": "printed page 35 / lines 5747–5754", "sourceText": "Whenever the marker reaches the final space, ignore any further Hits in that Action and draw the top Queen Health card."},
    {"occurrenceId": "RB-QH-RESOLVE-01", "section": "queen-health", "locator": "printed page 35 / lines 5754–5760", "sourceText": "Discard the shown number of additional cards without revealing them, then resolve the bottom effect even if the Queen dies from the additional discards."},
    {"occurrenceId": "RB-QH-RESOLVE-02", "section": "queen-health", "locator": "printed page 35 / lines 5761–5763", "sourceText": "Discard the drawn card and reset the Universal marker to 0."},
    {"occurrenceId": "RB-QH-DEATH-01", "section": "queen-death", "locator": "printed page 35 / lines 5764–5772", "sourceText": "When the last Queen Health card is discarded, remove the Queen model, ignore future Queen placements, and flip the Intruder Help sheet."},
    {"occurrenceId": "RB-QH-ACTIVATION-01", "section": "queen-activation", "locator": "printed page 35 / lines 5773–5786", "sourceText": "The Queen Attacks a Character in her Room if possible, otherwise moves once toward the closest Character using the stated tie-breaks."},
    {"occurrenceId": "RB-QH-REPEL-01", "section": "repel", "locator": "printed page 31 / lines 5273–5292", "sourceText": "A Character Repelling an Intruder from the same Room chooses the exit Corridor; other Repel destinations use lowest ID and preserve Door/entry consequences."},
    {"occurrenceId": "RB-QH-ACTION-DRAW-01", "section": "action-deck", "locator": "printed page 16 / lines 3435–3438", "sourceText": "When an Action deck has no card to draw, shuffle that Character's discard pile into a new deck and continue drawing."},
    {"occurrenceId": "RB-QH-CHARACTER-ORDER-01", "section": "effect-order", "locator": "printed page 14 / lines 3294–3299", "sourceText": "All effects mentioning Characters resolve in Turn order."},
    {"occurrenceId": "RB-QH-MALFUNCTION-01", "section": "malfunction", "locator": "printed page 22 / lines 4368–4375, 4414–4426", "sourceText": "A Room holds at most one Malfunction; repeated placement is ignored; if the supply is empty place Fire in the Room instead if possible."},
    {"occurrenceId": "RB-QH-REINFORCE-01", "section": "reinforced-corridor", "locator": "printed page 21 / lines 4150–4157", "sourceText": "Reinforcing an empty Corridor discards Noise and flips the Corridor to its value-0 side."},
    {"occurrenceId": "RB-QH-FACILITY-DEATH-01", "section": "facility-destruction", "locator": "printed pages 7 and 38 / INT-010", "sourceText": "Facility destruction kills all Intruders, including the Queen."},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw_queen_health_deck(repo: Path) -> tuple[dict, str]:
    path = repo / RAW_SAVE_PATH
    data = path.read_bytes()
    root: dict = {}
    offset = 4
    while offset < len(data):
        parsed, offset = _parse_value(data, offset, len(data))
        if parsed is not None:
            root[parsed[0]] = parsed[1]
    deck = _find_guid(root.get("ObjectStates"), BASE_QUEEN_HEALTH_DECK_GUID)
    if not isinstance(deck, dict):
        raise AssertionError("base Queen Health root Deck missing from raw TTS save")
    return deck, _sha(path)


def _parse_bga_queen_health(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const QUEEN_CARDS_DATA = \{\n(.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError("QUEEN_CARDS_DATA block not found")
    records = {}
    for row in re.finditer(r"^  (QueenHealthCard\d+): \{ discard: (\d+), effectDesc: ('(?:\\.|[^'])*') \},$", match.group(1), re.M):
        key, discard, effect = row.groups()
        records[key] = {
            "key": key,
            "structuredOrdinal": int(key.removeprefix("QueenHealthCard")),
            "discard": int(discard),
            "effectDesc": ast.literal_eval(effect),
            "sourceBlockText": row.group(0),
            "structuredOrdinalIsNotPrintedCardNumberOrDeckOrder": True,
        }
    expected_keys = {f"QueenHealthCard{index}" for index in range(1, 13)}
    if set(records) != expected_keys:
        raise AssertionError("licensed Queen Health table identity set changed")
    return records


def _source_sentences(definition: dict) -> list[dict]:
    count = definition["discardCount"]
    conditional = "If the card was drawn by a [character]:" if definition["effectKind"] in {"repel"} and definition["sourcePath"].endswith("-039.png") or definition["effectKind"] == "malfunction-or-unreinforce" else "If the card was drawn by a [character]."
    effects = {
        "repel": ["Repel the Queen."],
        "return-pool": ["Place the Queen back in the pool."],
        "activate": ["Activate the Queen."],
        "add-queen-tokens": ["Add all Queen tokens to the bag."],
        "draw-action-cards": ["Each [character] in the Room with the Queen\nDraws 2 [actionCard]."],
        "noise-rolls": ["Each [character] in the Room with the Queen\nMakes a Noise roll."],
        "malfunction-or-unreinforce": ["Place a [malfunction] in the Queen's Room.", "Unreinforce Queen's Corridor."],
    }[definition["effectKind"]]
    code = f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"
    specs = [(f"QH-{code}-S01", "P1", f"{count}\nadditional cards."), (f"QH-{code}-S02", "P2", conditional)]
    specs.extend((f"QH-{code}-S{index + 3:02d}", "P2", text) for index, text in enumerate(effects))
    body = definition["body"]
    rows = []
    cursor = 0
    for sequence, (sentence_id, panel_id, exact_text) in enumerate(specs, 1):
        start = body.find(exact_text, cursor)
        if start < 0:
            raise AssertionError(f"Queen Health source sentence missing: {sentence_id}")
        end = start + len(exact_text)
        rows.append({"sentenceId": sentence_id, "sequence": sequence, "panelId": panel_id, "exactText": exact_text, "start": start, "end": end})
        cursor = end
    return rows


def _panels(definition: dict) -> list[dict]:
    body = definition["body"]
    split = body.find("\n\n")
    if split < 0:
        raise AssertionError("Queen Health panel split missing")
    upper = body[:split]
    lower = body[split + 2:]
    return [
        {
            "panelId": "P1",
            "readingOrder": 1,
            "role": "discard-count-and-artwork-panel",
            "operative": True,
            "heading": "Discard",
            "exactText": f"Discard\n{upper}",
            "bodyStart": 0,
            "bodyEnd": split,
        },
        {
            "panelId": "P2",
            "readingOrder": 2,
            "role": "conditional-special-effect-panel",
            "operative": True,
            "heading": "",
            "exactText": lower,
            "bodyStart": split + 2,
            "bodyEnd": len(body),
        },
    ]


def _physical_code(definition: dict) -> str:
    return f"{definition['ttsCardId']}-{definition['ttsCardGuid'].upper()}"


def build_queen_health_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / CORPUS_PATH).read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    selected = json.loads((repo / SELECTED_EVIDENCE_PATH).read_text(encoding="utf-8"))
    selected_by_path = {row["sourcePath"]: row for row in selected["entries"]}
    progress = json.loads((repo / "assets/tts-mod/extract/vision-progress.json").read_text(encoding="utf-8"))
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    provenance = json.loads((repo / PROVENANCE_PATH).read_text(encoding="utf-8"))
    provenance_by_file = {row["file"]: row for row in provenance}
    roles = json.loads((repo / "assets/tts-mod/extract/v2/lua_roles.json").read_text(encoding="utf-8"))
    objects = json.loads((repo / "assets/tts-mod/extract/v2/objects.json").read_text(encoding="utf-8"))
    classification = json.loads((repo / "assets/tts-mod/extract/v2/classification.json").read_text(encoding="utf-8"))
    secondary = json.loads((repo / "docs/rules/source-extraction/secondary-evidence-index.json").read_text(encoding="utf-8"))
    visuals = json.loads((repo / "docs/rules/source-extraction/rulebook-visual-obligations.json").read_text(encoding="utf-8"))
    faq = json.loads((repo / "docs/rules/source-extraction/faq-v1.2-source-extraction.json").read_text(encoding="utf-8"))
    objective_help = json.loads((repo / "docs/rules/source-extraction/objective-help-sheet.json").read_text(encoding="utf-8"))
    backlog = json.loads((repo / "docs/rules/semantics/backlog.json").read_text(encoding="utf-8"))
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    bga = _parse_bga_queen_health(repo / BGA_QUEEN_HEALTH_PATH)

    role = next(row for row in roles if row.get("role") == "queenHealthDeck" and row.get("guid") == BASE_QUEEN_HEALTH_DECK_GUID)
    expected_deck_numbers = ["4241", "4243", "4245", "4292", "4581", "5037", "5038", "5039", "5040", "5041", "5042"]
    if role.get("type") != "Deck" or role.get("n_urls") != 11 or role.get("deck_nums") != expected_deck_numbers:
        raise AssertionError("base Queen Health root Lua role changed")
    expansion_names = {"99e2ce": "Neoflesh", "3b65b3": "Sangrevores", "6963a5": "Carnomorph"}
    excluded_roles = [row for row in roles if row.get("role") == "queenHealthDeck" and row.get("guid") != BASE_QUEEN_HEALTH_DECK_GUID]
    if {row["guid"] for row in excluded_roles} != set(expansion_names):
        raise AssertionError("Queen Health expansion-role boundary changed")
    classification_by_guid = {row["guid"]: row for row in classification}
    if any(classification_by_guid[guid].get("verdict") != "expansion" for guid in expansion_names):
        raise AssertionError("Queen Health expansion classification changed")

    raw_deck, raw_save_sha = _raw_queen_health_deck(repo)
    deck_ids = [int(value) for value in (raw_deck.get("DeckIDs") or {}).values()]
    expected_deck_ids = [row["ttsCardId"] for row in QUEEN_HEALTH_DEFINITIONS]
    if deck_ids != expected_deck_ids:
        raise AssertionError("base Queen Health raw DeckIDs order changed")
    contained_value = raw_deck.get("ContainedObjects") or {}
    contained = list(contained_value.values()) if isinstance(contained_value, dict) else list(contained_value)
    expected_children = [(row["ttsCardId"], row["ttsCardGuid"]) for row in QUEEN_HEALTH_DEFINITIONS]
    actual_children = [(int(row["CardID"]), row["GUID"]) for row in contained]
    if actual_children != expected_children:
        raise AssertionError("base Queen Health raw contained occurrence order changed")
    root_custom = raw_deck.get("CustomDeck") or {}
    if set(root_custom) != set(expected_deck_numbers):
        raise AssertionError("base Queen Health raw CustomDeck IDs changed")

    root_object = next(row for row in objects if row.get("guid") == BASE_QUEEN_HEALTH_DECK_GUID)
    child_objects = [row for row in objects if ["Deck", BASE_QUEEN_HEALTH_DECK_GUID, ""] in (row.get("parent") or [])]
    child_by_tuple = {(int(row["card_id"]), row["guid"]): row for row in child_objects if row.get("card_id")}
    if root_object.get("type") != "Deck" or root_object.get("parent") != [] or set(child_by_tuple) != set(expected_children) or len(child_objects) != 12:
        raise AssertionError("base Queen Health object/container closure changed")

    bga_table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "QUEEN_CARDS_DATA")
    if bga_table.get("count") != 12 or set(bga_table.get("keys") or []) != set(bga):
        raise AssertionError("licensed Queen Health evidence-index closure changed")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    if any(occurrence_id not in visual_by_id for occurrence_id in ("RB-P03-V01", "RB-P35-V01", "RB-P35-V02", "RB-P35-V03")):
        raise AssertionError("Queen Health official visual occurrence missing")
    faq_by_id = {unit["sourceUnitId"]: unit for page in faq["pages"] for unit in page.get("units", [])}
    if faq_by_id["FQ-P02-U03"].get("applicability") != "base-game":
        raise AssertionError("Queen Health FAQ applicability boundary changed")
    objective_by_id = {unit["sourceUnitId"]: unit for unit in objective_help["units"]}
    objective_ids = ["P1-GT-06", "P2-GT-06"]
    if any(objective_by_id[unit_id].get("heading") != "QUEEN IS DEAD" for unit_id in objective_ids):
        raise AssertionError("Queen-death Objective Help occurrence changed")

    asset_multiplicity = Counter(row["sourcePath"] for row in QUEEN_HEALTH_DEFINITIONS)
    face_rows = []
    for definition, raw_child in zip(QUEEN_HEALTH_DEFINITIONS, contained):
        code = _physical_code(definition)
        source_path = definition["sourcePath"]
        corpus_row = corpus_by_path.get(source_path) or {}
        source_sha = _sha(repo / source_path)
        if source_sha != corpus_row.get("sourceSha256") or not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"}:
            raise AssertionError(f"Queen Health corpus/hash readiness drift: {code}")
        printed = corpus_row.get("printedData") or {}
        if printed.get("body") != definition["body"]:
            raise AssertionError(f"Queen Health body drift: {code}")
        progress_row = progress_by_path.get(source_path) or {}
        if definition["ttsCardId"] == 424300:
            visible = progress_row.get("semanticRead") or {}
            if visible.get("title") != "Discard" or visible.get("body") != definition["body"]:
                raise AssertionError("canonical Queen Health face evidence drift")
            selected_run = None
            local_status = "canonical-preselected-local-morphology-no-global-alias"
            verified_tokens = list((progress_row.get("vision", {}).get("iconVerification") or {}).get("claimed") or [])
            if verified_tokens != ["character"]:
                raise AssertionError("canonical Queen Health Character icon evidence drift")
            verified_rows = [{"canonicalToken": "character", "matchDecision": "match", "referenceLabel": "Character", "evidenceSource": progress_row.get("vision", {}).get("resultPath")}]
            unresolved_rows = []
        else:
            selected_entry = selected_by_path.get(source_path) or {}
            runs = selected_entry.get("runs") or []
            if len(runs) != 1:
                raise AssertionError(f"Queen Health selected-evidence run count changed: {source_path}")
            selected_run = runs[-1]
            visible = selected_run.get("visibleText") or {}
            if visible.get("title") != "Discard" or visible.get("body") != definition["body"]:
                raise AssertionError(f"Queen Health selected title/body drift: {code}")
            unresolved_rows = selected_run.get("unresolvedIconOccurrences") or []
            verified_rows = selected_run.get("verifiedIconOccurrences") or []
            if len(unresolved_rows) != 1 or unresolved_rows[0].get("matchDecision") != "no-match":
                raise AssertionError(f"Queen Health local display no-match drift: {code}")
            local_status = "selected-explicit-authoritative-no-match"

        provenance_row = provenance_by_file[source_path.removeprefix("assets/tts-mod/extract/v2-dl/tree/")]
        expected_refs = 3 if asset_multiplicity[source_path] == 2 else 2
        if provenance_row.get("refs") != expected_refs:
            raise AssertionError(f"Queen Health FaceURL reference count drift: {source_path}")
        child_ref = next((row for row in provenance_row.get("objects") or [] if row.get("guid") == definition["ttsCardGuid"] and row.get("cardId") == definition["ttsCardId"]), None)
        if child_ref is None or child_ref.get("key") != "FaceURL" or child_ref.get("parent") != [["Deck", BASE_QUEEN_HEALTH_DECK_GUID, ""]]:
            raise AssertionError(f"Queen Health exact provenance selector drift: {code}")
        custom = root_custom[definition["customDeckId"]]
        if custom.get("FaceURL") != provenance_row.get("url") or custom.get("BackURL") != "https://steamusercontent-a.akamaihd.net/ugc/11923313303559415/089CF664C3CC0F028CCC63FB2B9C15C4B063F3A9/" or custom.get("NumWidth") != 1 or custom.get("NumHeight") != 1:
            raise AssertionError(f"Queen Health CustomDeck URL/shape drift: {code}")
        if raw_child.get("GUID") != definition["ttsCardGuid"] or int(raw_child.get("CardID")) != definition["ttsCardId"]:
            raise AssertionError(f"Queen Health raw full CardID/GUID drift: {code}")

        panels = _panels(definition)
        sentences = _source_sentences(definition)
        icon_rows = [
            {
                "occurrenceId": f"QH-{code}-I01",
                "assetMorphologyOccurrenceId": f"QH-ASSET-{source_sha[:16]}-DISPLAY",
                "sequence": 1,
                "panelId": "P1",
                "sourceToken": f"LOCAL-DISCARD-DISPLAY-{definition['discardCount']}",
                "literalAppearance": LOCAL_DISPLAY_MORPHOLOGY[definition["discardCount"]],
                "printedNumericValue": definition["discardCount"],
                "semanticReferenceId": None,
                "mappingStatus": local_status,
                "page40TokenAssigned": False,
                "mappingScope": f"exact Queen Health source occurrence {definition['occurrenceId']} only",
                "resolutionBoundary": "The visible numeral remains source-local morphology. Its numeric value is read from this card occurrence and composed with the official page-35 instruction; it is not a Shoot/Burst/Health/damage icon alias.",
                "selectedEvidence": unresolved_rows[0] if unresolved_rows else None,
            }
        ]
        token_matches = list(re.finditer(r"\[(character|actionCard|malfunction)\]", definition["body"]))
        verified_tokens = [row.get("canonicalToken") for row in verified_rows]
        if verified_tokens != [match.group(1) for match in token_matches]:
            raise AssertionError(f"Queen Health matched inline icon projection drift: {code}")
        for index, (match, evidence) in enumerate(zip(token_matches, verified_rows), 2):
            icon_rows.append({
                "occurrenceId": f"QH-{code}-I{index:02d}",
                "assetMorphologyOccurrenceId": f"QH-ASSET-{source_sha[:16]}-INLINE-{index - 1:02d}",
                "sequence": index,
                "panelId": "P2",
                "sourceToken": match.group(1),
                "start": match.start(),
                "end": match.end(),
                "literalAppearance": evidence.get("visibleDiscriminator") or evidence.get("referenceLabel") or match.group(1),
                "semanticReferenceId": f"icon.{match.group(1)}",
                "mappingStatus": "authoritative-page40-exact-occurrence-match",
                "page40TokenAssigned": True,
                "mappingScope": f"exact Queen Health source occurrence {definition['occurrenceId']} only",
                "resolutionBoundary": "Only the exact occurrence-specific authoritative comparison is used; no color, position, title, or surrounding-text alias is created.",
                "selectedEvidence": evidence,
            })

        backlog_id = "CARD:" + source_sha[:16]
        backlog_row = backlog_by_id.get(backlog_id) or {}
        if backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != source_sha:
            raise AssertionError(f"Queen Health backlog source tuple drift: {code}")
        bga_candidates = [bga[key] for key in definition["bgaCandidateKeys"]]
        face_rows.append({
            "queenHealthOccurrenceId": definition["occurrenceId"],
            "ttsRole": "queenHealthDeck",
            "ttsDeckGuid": BASE_QUEEN_HEALTH_DECK_GUID,
            "ttsDeckType": "Deck",
            "ttsSavedSequence": definition["ttsSavedSequence"],
            "rulesDeckOrderSourceBacked": False,
            "ttsCardGuid": definition["ttsCardGuid"],
            "ttsCardId": definition["ttsCardId"],
            "customDeckId": definition["customDeckId"],
            "sourceSelector": {
                "key": "FaceURL",
                "objectType": "CardCustom",
                "fullCardId": definition["ttsCardId"],
                "guid": definition["ttsCardGuid"],
                "parentDeckGuid": BASE_QUEEN_HEALTH_DECK_GUID,
                "customDeckId": definition["customDeckId"],
                "url": custom["FaceURL"],
                "backUrl": custom["BackURL"],
                "sideRole": "operative-number-and-effect-face",
                "sourceRole": "direct-composite-face",
                "selectorStatus": "exact-full-CardID-GUID-CustomDeck-FaceURL-parent-tuple",
                "generatedSpriteSheetCell": False,
                "selectorGap": None,
                "cardIdModuloJoinUsed": False,
            },
            "sourceId": definition["sourceId"],
            "sourcePath": source_path,
            "sourceSha256": source_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS base Queen Health physical occurrence / root deck {BASE_QUEEN_HEALTH_DECK_GUID} / saved sequence {definition['ttsSavedSequence']} / full CardID {definition['ttsCardId']} / GUID {definition['ttsCardGuid']}",
            "corpusEvidencePath": CORPUS_PATH,
            "selectedEvidencePath": SELECTED_EVIDENCE_PATH if selected_run else progress_row.get("vision", {}).get("resultPath"),
            "provenanceEvidencePath": PROVENANCE_PATH,
            "extractionState": corpus_row["extractionState"],
            "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
            "printedHeading": "Discard",
            "printedDiscardCount": definition["discardCount"],
            "printedBody": definition["body"],
            "panels": panels,
            "sentences": sentences,
            "iconOccurrences": icon_rows,
            "cardStateRoles": {
                "setup": "numbers-side down; operative face hidden and shared back visible",
                "drawn": "operative face revealed publicly in resolution",
                "additionalDiscards": "discarded without revealing",
                "sharedBackSourceId": QUEEN_HEALTH_BACK_SOURCE_ID,
                "separateRulesFaceOnBack": False,
            },
            "sharedFaceAsset": {
                "sourceSha256": source_sha,
                "physicalOccurrenceCount": asset_multiplicity[source_path],
                "physicalOccurrenceIds": [row["occurrenceId"] for row in QUEEN_HEALTH_DEFINITIONS if row["sourcePath"] == source_path],
                "assetIdentityDoesNotCollapsePhysicalCopies": True,
            },
            "semanticRuleId": definition["semanticRuleId"],
            "backlogUnitId": backlog_id,
            "bgaVariantCandidates": {
                "sourceId": BGA_QUEEN_HEALTH_SOURCE_ID,
                "sourcePath": BGA_QUEEN_HEALTH_PATH,
                "sourceSha256": _sha(repo / BGA_QUEEN_HEALTH_PATH),
                "sourceVersion": "licensed BGA immutable build 260622-1220 / QUEEN_CARDS_DATA",
                "table": "QUEEN_CARDS_DATA",
                "matchStatus": definition["bgaMatchStatus"],
                "candidateKeys": definition["bgaCandidateKeys"],
                "candidates": bga_candidates,
                "oneToOneCopyAssignmentAsserted": len(definition["bgaCandidateKeys"]) == 1,
                "boundary": "Candidate projection uses exact discard/effect tuples and family multiplicity only; BGA key suffixes are not printed card numbers or TTS deck order, and duplicate candidate copies are not arbitrarily paired.",
            },
            "officialCounterpartRefs": definition["officialCounterpartRefs"],
            "joinEvidence": {
                "identityJoin": "exact physical occurrence and source-asset projection",
                "titleOnlyJoin": False,
                "folderOnlyJoin": False,
                "cardIdModuloJoin": False,
                "bgaOrdinalJoin": False,
                "basis": [
                    "first/base queenHealthDeck Lua role and exact root GUID",
                    "raw saved DeckIDs sequence plus contained full CardID/GUID occurrence",
                    "exact CustomDeck ID, FaceURL, shared BackURL, and parent deck tuple",
                    "closed-corpus path/live SHA-256 and exact selected/canonical text evidence",
                    "ordered two-panel body, source sentences, local number display, and occurrence-scoped icon comparisons",
                    "licensed rows retained independently with candidate-set boundaries rather than title or ordinal pairing",
                ],
            },
        })

    back_provenance = provenance_by_file[QUEEN_HEALTH_BACK_PATH.removeprefix("assets/tts-mod/extract/v2-dl/tree/")]
    back_corpus = corpus_by_path[QUEEN_HEALTH_BACK_PATH]
    back_sha = _sha(repo / QUEEN_HEALTH_BACK_PATH)
    if back_provenance.get("refs") != 13 or back_sha != back_corpus.get("sourceSha256") or back_corpus.get("rulesTextPresent") or (back_corpus.get("printedData") or {}).get("title") != "QUEEN HEALTH":
        raise AssertionError("Queen Health shared-back boundary changed")

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

    face_backlog_ids = list(dict.fromkeys(row["backlogUnitId"] for row in face_rows))
    linked_backlog_ids = [
        *face_backlog_ids,
        "RULE:ACT-SHOOT-001",
        "RULE:ACT-BURST-001",
        "RULE:INT-001",
        "RULE:INT-003",
        "RULE:INT-007",
        "RULE:INT-010",
        "RULE:INT-011",
        "RULE:RT-011",
        "FAQ:FQ-P02-U03",
        "VIS:RB-P03-V01",
        "VIS:RB-P35-V01",
        "VIS:RB-P35-V02",
        "VIS:RB-P35-V03",
        "OBJ:P1-GT-06",
        "OBJ:P2-GT-06",
    ]
    if len(face_backlog_ids) != 10 or any(unit_id not in backlog_by_id for unit_id in linked_backlog_ids):
        raise AssertionError("Queen Health source-obligation backlog closure failed")

    number_counts = Counter(row["printedDiscardCount"] for row in face_rows)
    icon_ref_counts = Counter(icon.get("semanticReferenceId") or "source-local-number-display" for row in face_rows for icon in row["iconOccurrences"])
    unique_asset_icon_count = sum(len(next(row for row in face_rows if row["sourcePath"] == path)["iconOccurrences"]) for path in asset_multiplicity)
    return {
        "schemaVersion": 1,
        "recordType": "semantic-queen-health-source-index",
        "scope": "entire mechanically derived base Queen Health card/component family; twelve physical occurrences, ten face assets, shared back, official visuals, licensed rows, and source variants remain independent",
        "derivationPolicy": "Derive physical cards only from the first/base queenHealthDeck Lua role and exact raw root Deck GUID, saved DeckIDs order, contained full CardID/GUID/CustomDeck/FaceURL/BackURL tuples. Close each occurrence against live bytes, corpus/selected evidence, panels, sentences, local symbols, official rule/FAQ/visual evidence, licensed rows, and backlog. Never join by Discard heading, display number alone, filename/folder, CardID modulo, BGA ordinal, or effect resemblance.",
        "counts": {
            "physicalFaceOccurrences": len(face_rows),
            "uniqueFaceAssets": len(asset_multiplicity),
            "uniqueFullCardIds": len({row["ttsCardId"] for row in face_rows}),
            "uniqueCardGuids": len({row["ttsCardGuid"] for row in face_rows}),
            "rootCustomDeckEntries": len(root_custom),
            "rootUniqueFaceUrls": len({value["FaceURL"] for value in root_custom.values()}),
            "directFaceOccurrences": len(face_rows),
            "generatedFaceOccurrences": 0,
            "sourceSheets": 0,
            "selectorGaps": 0,
            "sharedBackOccurrences": 1,
            "sharedBackSelectorReferences": back_provenance["refs"],
            "canonicalCorpusAssets": sum(next(row for row in face_rows if row["sourcePath"] == path)["extractionState"] == "verified-canonical" for path in asset_multiplicity),
            "sourceBoundDraftAssets": sum(next(row for row in face_rows if row["sourcePath"] == path)["extractionState"] == "draft-full" for path in asset_multiplicity),
            "physicalPanels": sum(len(row["panels"]) for row in face_rows),
            "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in face_rows),
            "printedSentences": sum(len(row["sentences"]) for row in face_rows),
            "localNumberDisplayOccurrences": icon_ref_counts["source-local-number-display"],
            "page40MatchedIconOccurrences": sum(count for key, count in icon_ref_counts.items() if key != "source-local-number-display"),
            "functionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in face_rows),
            "uniqueAssetFunctionalIconOccurrences": unique_asset_icon_count,
            "selectedEvidenceNoMatchAssetOccurrences": 9,
            "canonicalLocalUnregisteredAssetOccurrences": 1,
            "characterIconOccurrences": icon_ref_counts["icon.character"],
            "actionCardIconOccurrences": icon_ref_counts["icon.actionCard"],
            "malfunctionIconOccurrences": icon_ref_counts["icon.malfunction"],
            "queenIconOccurrences": 0,
            "damageIconOccurrences": 0,
            "burstIconOccurrences": 0,
            "healthIconOccurrences": 0,
            "licensedDigitalOccurrences": len(bga),
            "licensedPlaceholderOccurrences": sum(len(re.findall(r"<[A-Z-]+>", row["effectDesc"])) for row in bga.values()),
            "licensedCandidateLinks": sum(len((row["bgaVariantCandidates"] or {}).get("candidateKeys") or []) for row in face_rows),
            "officialVisibleFaceOccurrences": sum(row["kind"] in {"face", "partial-face"} for row in official_projection),
            "officialVisibleBackOccurrences": sum(row["kind"] == "shared-back" for row in official_projection),
            "officialQueenHitsTrackSpaces": 6,
            "officialTrackTerminalLocalSymbolOccurrences": 2,
            "officialRulebookTextOccurrences": len(OFFICIAL_RULEBOOK_TEXT_OCCURRENCES),
            "officialRulebookVisualObligations": 4,
            "faqOccurrences": 1,
            "objectiveHelpOccurrences": 2,
            "excludedExpansionQueenHealthDecks": len(excluded_roles),
            "excludedPrototypeFaces": 0,
            "excludedPlaceholderFaces": 0,
            "excludedParentSheets": 0,
            "excludedBaseAttackOccurrencesWithQueenApplicability": 20,
            "backlogTuples": len(face_backlog_ids),
            "backlogPhysicalFaceLinks": len(face_rows),
            "backlogObligationsLinked": len(linked_backlog_ids),
        },
        "discardNumberMultiplicity": {str(key): number_counts[key] for key in sorted(number_counts)},
        "familyCountEvidence": {
            "officialRulebook": {"sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf", "locator": "unprinted PDF page 3 / RB-P03-V01 / rulebook_text line 524", "printedPhysicalCount": 12},
            "rawTtsDeck": {"sourcePath": RAW_SAVE_PATH, "sourceSha256": raw_save_sha, "rolePath": "assets/tts-mod/extract/v2/lua_roles.json", "role": "queenHealthDeck", "deckGuid": BASE_QUEEN_HEALTH_DECK_GUID, "deckIdsInSavedOrder": deck_ids, "savedOrderIsGameplayDeckOrder": False, "setupRequiresShuffle": True, "physicalFaceCount": len(face_rows), "uniqueFaceAssetCount": len(asset_multiplicity)},
            "closedCorpus": {"sourcePath": CORPUS_PATH, "physicalOccurrenceCount": len(face_rows), "uniqueFaceAssetCount": len(asset_multiplicity), "sourcePaths": list(asset_multiplicity)},
            "licensedDigital": {"sourcePath": BGA_QUEEN_HEALTH_PATH, "indexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "table": "QUEEN_CARDS_DATA", "structuredVariantCount": len(bga), "keysInSourceOrder": list(bga), "keySuffixIsNotPrintedCardNumberOrDeckOrder": True},
            "backlog": {"sourcePath": "docs/rules/semantics/backlog.json", "faceTupleCount": len(face_backlog_ids), "physicalFaceLinkCount": len(face_rows), "faceUnitIds": face_backlog_ids, "linkedUnitIds": linked_backlog_ids},
        },
        "queenHitsTrack": {
            "sourceOccurrenceId": "RB-P35-V01-QH-HITS-TRACK",
            "parentOccurrenceId": "RB-P35-V01",
            "spacesInPrintedOrder": [
                {"sequence": 1, "printedValue": 0, "role": "reset/setup"},
                {"sequence": 2, "printedValue": 1, "role": "accumulated-Hit"},
                {"sequence": 3, "printedValue": 2, "role": "accumulated-Hit"},
                {"sequence": 4, "printedValue": 3, "role": "accumulated-Hit"},
                {"sequence": 5, "printedValue": 4, "role": "accumulated-Hit"},
                {"sequence": 6, "printedValue": None, "role": "final-space-local-symbol", "literalAppearance": "small pale queen-head/blob-plus-style local terminal glyph; the visual census conservatively describes it as skull-like", "semanticReferenceId": None, "page40TokenAssigned": False},
            ],
            "cardAreaSlots": 1,
            "cardFaceTracks": 0,
            "cardFaceSlots": 0,
        },
        "officialLocalSymbols": [
            {"occurrenceId": "RB-P35-V01-QH-TERMINAL", "parentOccurrenceId": "RB-P35-V01", "location": "terminal Queen's Hits track space", "literalAppearance": "small pale queen-head/blob-plus-style local glyph; existing census says skull-like", "semanticReferenceId": None, "page40TokenAssigned": False},
            {"occurrenceId": "RB-P35-V03-QH-INLINE", "parentOccurrenceId": "RB-P35-V03", "location": "inline parenthetical next to final-space trigger prose", "literalAppearance": "small pale queen-head/blob-plus-style local glyph associated visually with the track terminal", "semanticReferenceId": None, "page40TokenAssigned": False},
        ],
        "sharedBack": {
            "sourceId": QUEEN_HEALTH_BACK_SOURCE_ID,
            "occurrenceId": "TTS-QUEEN-HEALTH-SHARED-BACK",
            "sourcePath": QUEEN_HEALTH_BACK_PATH,
            "sourceSha256": back_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS shared base Queen Health back / root deck {BASE_QUEEN_HEALTH_DECK_GUID}",
            "sourceSelector": {"key": "BackURL", "objectType": "Deck", "guid": BASE_QUEEN_HEALTH_DECK_GUID, "url": next(iter(root_custom.values()))["BackURL"], "sideRole": "shared-non-operative-back", "rootDeckSelectorCount": 1, "baseCardSelectorCount": 12, "referenceCount": back_provenance["refs"]},
            "printedTitle": "QUEEN HEALTH",
            "printedVisibleText": "PRIMEBLOOD",
            "rulesTextPresent": False,
            "separateRulesFace": False,
            "numberedBack": False,
        },
        "officialRulebookTextOccurrences": OFFICIAL_RULEBOOK_TEXT_OCCURRENCES,
        "officialVisibleCounterparts": official_projection,
        "faqOccurrences": [{"sourceUnitId": "FQ-P02-U03", "section": faq_by_id["FQ-P02-U03"]["section"], "applicability": faq_by_id["FQ-P02-U03"]["applicability"], "printedText": faq_by_id["FQ-P02-U03"]["printedText"]}],
        "objectiveHelpOccurrences": [{"sourceUnitId": unit_id, "heading": objective_by_id[unit_id]["heading"], "printedDefinition": objective_by_id[unit_id]["printedDefinition"], "visibility": objective_by_id[unit_id].get("visibility")} for unit_id in objective_ids],
        "licensedDigitalOccurrences": [bga[key] for key in bga],
        "excludedContent": {
            "expansionQueenHealthDecks": [{"expansion": expansion_names[row["guid"]], "role": row["role"], "guid": row["guid"], "type": row["type"], "deckNums": row["deck_nums"], "scope": "expansion; excluded from base conclusions"} for row in excluded_roles],
            "prototypePlaceholderParentSheetBoundary": "The base root deck has twelve direct CardCustom children, zero generated cells, zero source sheets, zero selector gaps, and no separately selected prototype or placeholder face.",
            "sharedBackBoundary": "One generic BackURL is referenced by the root deck and all twelve physical cards; it is not a thirteenth rules face and it carries no per-card number.",
            "duplicateFaceBoundary": "Two physical cards share queenHealthDeck-084.png under distinct CardID/GUID tuples; two more share queenHealthDeck-045.png and CardID 429200 under distinct GUIDs. Shared bytes do not collapse copies.",
            "attackAndNonHealthCollisions": [
                {"kind": "base Intruder Attack family", "count": 20, "boundary": "Queen applicability badges or Queen Attack resolution do not make an Intruder Attack card a Queen Health card."},
                {"kind": "The Queen Awakens Event", "count": 1, "boundary": "Event title collision; separate Event deck occurrence."},
                {"kind": "Intruder Help Queen Alive/Dead faces", "count": 2, "boundary": "reference-sheet state faces, not Queen Health cards."},
                {"kind": "Queen model/tokens/objective labels", "boundary": "agents, tokens, and game-term occurrences are supporting evidence, not deck faces."},
            ],
            "licensedOrdinalBoundary": "QueenHealthCard1..12 are licensed structured keys. Their suffixes are retained but are not promoted to printed titles, physical card numbers, TTS saved order, or a one-to-one duplicate-copy assignment.",
            "duplicateReferenceBoundary": "Root-deck, child-card, corpus, selected-evidence, official-visible, backlog, and licensed records are provenance links rather than extra physical Queen Health occurrences.",
        },
        "faces": face_rows,
    }


def queen_health_source_registry_rows(queen_source_index: dict) -> list[dict]:
    rows = []
    for face in queen_source_index["faces"]:
        rows.append({
            "sourceId": face["sourceId"],
            "authority": face["sourceAuthority"],
            "version": face["sourceVersion"],
            "path": face["sourcePath"],
            "sha256": face["sourceSha256"],
            "occurrenceId": face["queenHealthOccurrenceId"],
            "evidenceIndexPath": face["corpusEvidencePath"],
            "evidenceRecord": face["sourceSha256"],
            "provenanceIndexPath": face["provenanceEvidencePath"],
        })
    back = queen_source_index["sharedBack"]
    rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": CORPUS_PATH, "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": PROVENANCE_PATH})
    rows.append({"sourceId": BGA_QUEEN_HEALTH_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / QUEEN_CARDS_DATA", "path": BGA_QUEEN_HEALTH_PATH, "sha256": queen_source_index["faces"][0]["bgaVariantCandidates"]["sourceSha256"], "occurrenceId": "QUEEN_CARDS_DATA", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "QUEEN_CARDS_DATA"})
    rows.append({"sourceId": OBJECTIVE_HELP_SOURCE_ID, "authority": "official-component-reference", "version": "base Objective Help Sheet", "path": OBJECTIVE_HELP_PATH, "sha256": hashlib.sha256((Path(__file__).resolve().parents[1] / OBJECTIVE_HELP_PATH).read_bytes()).hexdigest(), "occurrenceId": "OBJECTIVE-HELP-SHEET", "evidenceIndexPath": "docs/rules/source-extraction/objective-help-sheet.json", "evidenceRecord": "docs/rules/source-extraction/objective-help-sheet.json"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None) -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": "public"}


def build_queen_health_records(repo: Path, queen_source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo
    records = []
    face_by_occurrence = {row["queenHealthOccurrenceId"]: row for row in queen_source_index["faces"]}

    records.append(record(
        "SEM-ACTION-CARD-DRAW-001", "Draw Action cards with deck renewal", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-ACTION-DRAW-RB", "SRC-RULEBOOK", "printed page 16 / lines 3435–3438", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "Whenever there are no more cards in your Action deck to be drawn and you need to draw another one, first reshuffle your discard pile into a new Action deck and continue drawing.", "docs/rulebooks/rulebook_text.txt:lines 3435–3438")],
        ["icon.actionCard"], ["tax.entity.component.card.action", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-ACTION-DRAW", "tax.entity.component.card.action", "when-triggered", "per-source-requested-card"), [participant("P-DRAWING-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-OWNER", "decision-owner", "tax.entity.agent.player"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ACTION-DRAW", "subjectRef": "drawn Action-card identities and remaining deck order", "audience": "owner-private card identities; public draw count", "revealTrigger": "draw to owner", "secrecy": "other players do not inspect drawn card identities or deck order"}], [],
        [_target("T-ACTION-DRAW-CHARACTER", ["tax.entity.agent.character"], minimum=1, maximum=1)],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "whether the next requested Action card exists in the Character's deck", ["SA-ACTION-DRAW-RB"], target_ref="T-ACTION-DRAW-CHARACTER"), operation("S02", 2, "shuffle", "if-able", "P-OWNER", "that Character's complete Action discard pile into a new Action deck", ["SA-ACTION-DRAW-RB"], conditions=["Action deck is empty and another card is requested"], target_ref="T-ACTION-DRAW-CHARACTER"), operation("S03", 3, "draw-random", "if-able", "P-OWNER", "1 top Action card into that Character's hand", ["SA-ACTION-DRAW-RB"], target_ref="T-ACTION-DRAW-CHARACTER", repeat={"callerRequestedCount": "source-instructed", "renewBeforeEachOtherwiseImpossibleDraw": True})],
        {"policy": "source-limited-components", "unit": "one requested Action card", "onImpossible": "renew from that Character's discard pile before an otherwise impossible draw; if both deck and discard are empty, that requested card cannot be drawn"}, {"kind": "instantaneous-private-card-draw"}, {"policy": "each successful draw moves one physical card into one owner-private hand"}, [], [], []))

    records.append(record(
        "SEM-ROOM-MALFUNCTION-PLACEMENT-001", "Place a Malfunction marker in a Room", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-ROOM-MALFUNCTION-RB", "SRC-RULEBOOK", "printed page 22 / lines 4368–4375, 4414–4426, 4465–4469", ["preconditions", "targets", "operations", "partialResolution", "duration", "stacking", "outcomes"], "A Room may contain one Malfunction. Repeated placement is ignored. If no Malfunction is available, place Fire in the Room if possible; unavailable Fire destroys the Facility.", "docs/rulebooks/rulebook_text.txt:lines 4368–4375, 4414–4426, 4465–4469")],
        ["icon.fire", "icon.malfunction", "term.room"], ["tax.entity.component.marker.fire", "tax.entity.component.marker.malfunction", "tax.entity.spatial.room", "tax.scaffold.supply-pool"], [],
        timing("TW-ROOM-MALFUNCTION", "tax.entity.component.marker.malfunction", "when-triggered", "per-requested-placement"), [participant("P-RULES", "rules-system"), participant("P-ROOM", "affected", "tax.entity.spatial.room")], "must", [], [],
        [{"informationId": "I-ROOM-MALFUNCTION", "subjectRef": "Room marker state, finite pools, fallback, and Facility outcome", "audience": "public", "revealTrigger": "placement resolution", "secrecy": "none"}], [],
        [_target("T-MALFUNCTION-ROOM", ["tax.entity.spatial.room"], minimum=1, maximum=1)],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "whether target Room already has a Malfunction", ["SA-ROOM-MALFUNCTION-RB"], target_ref="T-MALFUNCTION-ROOM"), operation("S02", 2, "place-component", "if-able", "P-RULES", "1 finite Malfunction marker in the target Room", ["SA-ROOM-MALFUNCTION-RB"], conditions=["Room has no Malfunction", "Malfunction marker available"], target_ref="T-MALFUNCTION-ROOM"), operation("S03", 3, "place-component", "if-able", "P-RULES", "1 finite Fire marker in the target Room", ["SA-ROOM-MALFUNCTION-RB"], conditions=["Room has no Malfunction", "no Malfunction marker available", "Room has no Fire", "Fire marker available"], target_ref="T-MALFUNCTION-ROOM"), operation("S04", 4, "invoke-process", "if-able", "P-RULES", "Facility destruction when fallback Fire cannot be placed because the Fire supply is empty", ["SA-ROOM-MALFUNCTION-RB"], conditions=["a Fire fallback is required", "no Fire marker is available"], invoke="SEM-AUTODESTRUCTION-001")],
        {"policy": "if-not-possible-fallback", "unit": "one requested Room Malfunction", "onImpossible": "ignore a repeat on an already malfunctioned Room; otherwise use the explicit Fire fallback and Facility-destruction consequence"}, {"kind": "persistent-marker-until-source-defined-removal"}, {"policy": "at most one Malfunction and one Fire marker per Room; 14 Malfunctions and 9 Fire markers are globally finite"}, [{"condition": "required fallback Fire unavailable", "result": "Facility is destroyed"}], [], []))

    records.append(record(
        "SEM-INTRUDER-REPEL-001", "Repel an Intruder", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-REPEL-RB", "SRC-RULEBOOK", "printed page 31 / lines 5273–5292", ["timing", "participants", "decisions", "targets", "operations", "partialResolution", "duration", "stacking"], "A Character Repelling an Intruder from the same Room chooses the exit Corridor. Otherwise the Intruder moves away through the lowest-ID destination; Closed Doors are destroyed without traversal, occupied-Room entry attacks, and an Unexplored-edge exit does not move.", "docs/rules/03-intruders-and-survival.md:INT-003")],
        ["term.corridor", "term.repel", "term.room"], ["tax.entity.agent.intruder", "tax.entity.spatial.corridor", "tax.entity.spatial.room", "tax.process.operation.repel"], [],
        timing("TW-REPEL", "tax.process.operation.repel", "when-triggered", "once-per-repel-instruction"), [participant("P-SOURCE-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-INTRUDER", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must", [],
        [decision("D-REPEL-EXIT", "P-SOURCE-CHARACTER", "player-choice", 1, 1, False, "public", ["legal exit Corridors when the Intruder and source Character share a Room"])],
        [{"informationId": "I-REPEL", "subjectRef": "source, Intruder, legal destinations, Door and destination outcome", "audience": "public", "revealTrigger": "resolution", "secrecy": "none"}], [],
        [_target("T-REPEL-INTRUDER", ["tax.entity.agent.intruder"], minimum=1, maximum=1), _target("T-REPEL-DESTINATION", ["tax.entity.spatial.corridor", "tax.entity.spatial.room"], selector="P-SOURCE-CHARACTER", mode="player-choice", minimum=0, maximum=1)],
        [operation("S01", 1, "branch", "must", "P-RULES", "same-Room Character source versus farther source", ["SA-REPEL-RB"], target_ref="T-REPEL-INTRUDER"), operation("S02", 2, "choose", "must", "P-SOURCE-CHARACTER", "one legal exit Corridor", ["SA-REPEL-RB"], conditions=["source Character and Intruder share a Room"], decision_ref="D-REPEL-EXIT", target_ref="T-REPEL-DESTINATION"), operation("S03", 3, "select-target", "must", "P-RULES", "lowest-ID farther-away legal destination", ["SA-REPEL-RB"], conditions=["source is farther than an adjacent Corridor"], target_ref="T-REPEL-DESTINATION"), operation("S04", 4, "move-entity", "if-able", "P-INTRUDER", "one Repel step away from the source", ["SA-REPEL-RB"], conditions=["destination is not beyond an Unexplored Corridor", "no Closed Door blocks traversal"], target_ref="T-REPEL-INTRUDER"), operation("S05", 5, "remove-component", "if-able", "P-INTRUDER", "Closed Door attempted during Repel", ["SA-REPEL-RB"], conditions=["Repel path has a Closed Door"], notes="Destroy the Door and do not traverse it in this Repel step."), operation("S06", 6, "invoke-process", "if-able", "P-INTRUDER", "entry Attack against the first Character in Turn order", ["SA-REPEL-RB"], conditions=["Repelled Intruder entered a Room with Characters"], invoke="SEM-INT-004")],
        {"policy": "source-conditional-steps", "unit": "one Repel movement attempt", "onImpossible": "an Unexplored-edge exit leaves the Intruder in place; a Closed Door is destroyed without traversal; otherwise complete the move and immediate entry consequence"}, {"kind": "instantaneous-movement"}, {"policy": "one source-defined movement attempt per Repel instruction"}, [], [], []))

    records.append(record(
        "SEM-QUEEN-ACTIVATION-001", "Queen Activation", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-QUEEN-ACTIVATION-RB", "SRC-RULEBOOK", "printed page 35 / lines 5773–5786", ["timing", "preconditions", "participants", "targets", "operations", "partialResolution", "duration", "stacking"], "When the Queen Activates she Attacks a Character in her Room if possible, otherwise moves once toward the closest Character; ties prefer an activating Character and then Turn order.", "docs/rulebooks/rulebook_text.txt:lines 5773–5786")],
        ["term.attack", "term.queen", "term.room"], ["tax.entity.agent.intruder.queen", "tax.entity.agent.character", "tax.entity.spatial.room", "tax.process.attack"], [],
        timing("TW-QUEEN-ACTIVATION", "tax.state.activation", "when-triggered", "once-per-Activation"), [participant("P-QUEEN", "actor", "tax.entity.agent.intruder.queen"), participant("P-ACTIVATING-CHARACTER", "trigger-owner", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-QUEEN-ACTIVATION", "subjectRef": "Queen location, Characters, activating Character, target, movement/Attack", "audience": "public", "revealTrigger": "continuous/resolution", "secrecy": "none"}], [],
        [_target("T-QUEEN-ACTIVATION-CHARACTER", ["tax.entity.agent.character"], mode="deterministic-turn-order", minimum=0, maximum=1)],
        [operation("S01", 1, "select-target", "must", "P-RULES", "Character in the Queen's Room, preferring the activating Character when applicable and then Turn order", ["SA-QUEEN-ACTIVATION-RB"], target_ref="T-QUEEN-ACTIVATION-CHARACTER"), operation("S02", 2, "invoke-process", "if-able", "P-QUEEN", "one Intruder Attack", ["SA-QUEEN-ACTIVATION-RB"], conditions=["eligible Character is in the Queen's Room"], target_ref="T-QUEEN-ACTIVATION-CHARACTER", invoke="SEM-INT-004"), operation("S03", 3, "select-target", "if-able", "P-RULES", "closest Character using activating-Character then Turn-order ties", ["SA-QUEEN-ACTIVATION-RB"], conditions=["no Character is in the Queen's Room"], target_ref="T-QUEEN-ACTIVATION-CHARACTER"), operation("S04", 4, "move-entity", "if-able", "P-QUEEN", "one ordinary Intruder movement step toward the selected Character", ["SA-QUEEN-ACTIVATION-RB"], conditions=["no Character is in the Queen's Room", "an eligible Character exists"], target_ref="T-QUEEN-ACTIVATION-CHARACTER")],
        {"policy": "source-conditional-steps", "unit": "one Queen Activation", "onImpossible": "Attack if a Character shares the Room; otherwise move once if a Character and legal movement exist; absent Queen/no target yields no invented placement"}, {"kind": "instantaneous-activation"}, {"policy": "one Attack-or-move branch per Activation"}, [], [], []))

    records.append(record(
        "SEM-QUEEN-HEALTH-SETUP-001", "Set up the Queen Health deck and Hits track", "source-backed", "procedure", "official-primary", "source-composed",
        [assertion("SA-QH-SETUP-RB", "SRC-RULEBOOK", "unprinted page 3 and printed page 10 / lines 2583–2587", ["timing", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "The base game has 12 Queen Health cards. Shuffle all, place them numbers-side down on Section C, and place a Universal marker on 0 of the Queen's Hits track.", "docs/rules/semantics/queen-health-source-index.json:familyCountEvidence")],
        ["term.queen-health-card", "term.universal-marker"], ["tax.entity.component.card.queen-health", "tax.entity.component.marker.universal", "tax.scaffold.supply-pool", "tax.scaffold.zone.deck"], [],
        timing("TW-QH-SETUP", "tax.entity.component.card.queen-health", "when-triggered", "once-during-base-setup"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-QH-SETUP", "subjectRef": "twelve card identities/order, operative fronts, shared back, and Hits marker", "audience": "hidden-from-all card identities/order; public shared back/count/marker", "revealTrigger": "individual card draw", "secrecy": "numbers and effects remain face down; setup does not inspect deck order"}], [], [],
        [operation("S01", 1, "shuffle", "must", "P-RULES", "all 12 exact base Queen Health physical occurrences", ["SA-QH-SETUP-RB"], repeat={"physicalCardCount": 12}), operation("S02", 2, "transition-zone", "must", "P-RULES", "all shuffled Queen Health cards numbers-side down", ["SA-QH-SETUP-RB"], transition={"from": "tax.scaffold.supply-pool", "to": "tax.scaffold.zone.deck"}), operation("S03", 3, "change-value", "must", "P-RULES", "Queen's Hits Universal marker", ["SA-QH-SETUP-RB"], value_change={"amount": 0, "value": "Queen's Hits track position"})],
        {"policy": "ordered-complete", "unit": "Queen Health deck/track setup", "onImpossible": "setup requires the complete finite 12-card family and one Universal marker; do not substitute backs, source sheets, expansion cards, or placeholders"}, {"kind": "persistent-setup-state"}, {"policy": "one shuffled finite deck and one Hits marker"}, [], [], []))

    records.append(record(
        "SEM-QUEEN-HIT-001", "Apply Hits and lethal results to the Queen", "source-backed-with-open-question", "procedure", "official-errata", "open-alternatives",
        [assertion("SA-QUEEN-HIT-RB", "SRC-RULEBOOK", "printed pages 33–35 / lines 5514–5529, 5576–5605, 5747–5800", ["timing", "preconditions", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Each Hit advances the Queen's Hits marker by 1. At the final space, further Hits in that Action are ignored and a Queen Health card resolves; the marker later resets to 0.", "docs/rulebooks/rulebook_text.txt:lines 5514–5529, 5576–5605, 5747–5800"), assertion("SA-QUEEN-HIT-FAQ", "SRC-FAQ", "General rules / FQ-P02-U03", ["timing", "preconditions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Shooting at the Queen works as for Adults, but resolve the top Queen Health card instead of removing the model; with 2 Hits, a roll of 2 or fewer or skull resolves the card.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U03")],
        ["term.hit", "term.queen", "term.queen-health-card", "term.universal-marker"], ["tax.entity.agent.intruder.queen", "tax.entity.component.card.queen-health", "tax.entity.component.marker.universal", "tax.process.operation.hit"], [],
        timing("TW-QUEEN-HIT", "tax.process.operation.hit", "when-triggered", "per-Hit-or-source-defined-lethal-result"), [participant("P-QUEEN", "affected", "tax.entity.agent.intruder.queen"), participant("P-ACTION-SOURCE", "trigger-owner"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-QUEEN-HIT", "subjectRef": "Queen location, Hits marker, assigned Hits, die/lethal result, suppression, and Health-card trigger", "audience": "public", "revealTrigger": "continuous/resolution", "secrecy": "remaining Queen Health order/effects remain hidden"}], [],
        [_target("T-QUEEN-HIT", ["tax.entity.agent.intruder.queen"], minimum=1, maximum=1)],
        [operation("S01", 1, "change-value", "must", "P-RULES", "Queen's Hits marker +1 for each accepted Hit, carrying between Actions until a trigger resets it", ["SA-QUEEN-HIT-RB"], target_ref="T-QUEEN-HIT", value_change={"amount": "+1 per accepted Hit up to the final space", "value": "Queen's Hits track position"}, repeat={"sourceAssignedHits": "one at a time", "sameActionOverflow": "ignored after trigger", "crossActionCarry": True}), operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-025 exact threshold timing relative to remaining Shoot/Burst/weapon operations", ["SA-QUEEN-HIT-RB", "SA-QUEEN-HIT-FAQ"], conditions=["marker reached final space or source produced a lethal Shoot result"], target_ref="T-QUEEN-HIT"), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-029 exact source-scoped meaning of the unmapped final/inline local glyph versus FAQ skull", ["SA-QUEEN-HIT-RB", "SA-QUEEN-HIT-FAQ"], conditions=["trigger depends on the official local terminal/critical morphology"], target_ref="T-QUEEN-HIT"), operation("S04", 4, "set-state", "must", "P-RULES", "ignore all later Hits dealt to the Queen in this same Action", ["SA-QUEEN-HIT-RB"], conditions=["Queen Health trigger occurred"], target_ref="T-QUEEN-HIT", notes="This suppression does not erase Hits carried from earlier Actions and creates no overflow carry after reset."), operation("S05", 5, "invoke-process", "must", "P-RULES", "one Queen Health card resolution", ["SA-QUEEN-HIT-RB", "SA-QUEEN-HIT-FAQ"], conditions=["marker reached final space or an applicable lethal Shoot result occurred under SEM-Q-029"], target_ref="T-QUEEN-HIT", invoke="SEM-QUEEN-HEALTH-RESOLUTION-001")],
        {"policy": "source-conditional-steps", "unit": "one accepted Queen Hit or source-defined lethal result", "onImpossible": "never carry same-Action overflow, never draw more than one card from one threshold trigger, and adopt no timing/glyph default prohibited by SEM-Q-025/029"}, {"kind": "persistent-track-until-card-resolution-reset"}, {"policy": "Hits carry across Actions until one trigger; further same-Action Hits after that trigger are ignored; no overflow carries through reset"}, [], ["SEM-Q-025", "SEM-Q-029"], []))

    records.append(record(
        "SEM-ACT-SHOOT-001", "Shoot, including Queen Health resolution", "source-backed-with-open-question", "action", "official-errata", "open-alternatives",
        [assertion("SA-SHOOT-RB", "SRC-RULEBOOK", "printed pages 12 and 33 / lines 2883, 5576–5605", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Choose a working loaded Ranged Weapon and an Intruder in the same Room, deal 1 Hit, roll the Shoot die, resolve its result, and apply Weapon modifiers.", "docs/rules/02-character-actions.md:ACT-SHOOT-001"), assertion("SA-SHOOT-QUEEN-FAQ", "SRC-FAQ", "General rules / FQ-P02-U03", ["timing", "preconditions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Shooting the Queen follows Adult shooting, except a lethal result resolves the top Queen Health card instead of removing the Queen.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U03")],
        ["icon.actionCard", "icon.shootDieAmmoLoss", "icon.shootDieCritical", "term.hit", "term.queen", "term.shoot"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.agent.intruder.queen", "tax.entity.component.card.action", "tax.process.action.attack.shoot", "tax.process.operation.hit"], [],
        timing("TW-SHOOT", "tax.process.action.attack.shoot", "during", "once-per-selected-Shoot-Action"), [participant("P-SHOOTER", "actor", "tax.entity.agent.character"), participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-TARGET", "affected", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must",
        [condition("C-SHOOT", "all", [{"predicate": "selected Ranged Weapon is working, in Hand, and has at least 1 Ammo token"}, {"predicate": "target Intruder is in the shooting Character's Room"}], ["SA-SHOOT-RB"])],
        [decision("D-SHOOT-WEAPON", "P-PLAYER", "player-choice", 1, 1, False, "public", ["eligible Ranged Weapons in Hand"]), decision("D-SHOOT-TARGET", "P-PLAYER", "player-choice", 1, 1, False, "public", ["eligible Intruders in the Character's Room"])],
        [{"informationId": "I-SHOOT", "subjectRef": "selected Weapon/target, Hit count, die result, Queen track/card trigger, Ammo and modifiers", "audience": "public", "revealTrigger": "selection/roll/resolution", "secrecy": "Queen Health deck order remains hidden until a card is drawn"}],
        [{"costId": "COST-SHOOT-ACTION", "payerRef": "P-SHOOTER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": None, "destination": "discard pile"}],
        [_target("T-SHOOT-INTRUDER", ["tax.entity.agent.intruder"], selector="P-PLAYER", mode="player-choice", minimum=1, maximum=1)],
        [operation("S01", 1, "choose", "must", "P-PLAYER", "eligible Ranged Weapon", ["SA-SHOOT-RB"], decision_ref="D-SHOOT-WEAPON"), operation("S02", 2, "select-target", "must", "P-PLAYER", "one Intruder in the shooter's Room", ["SA-SHOOT-RB"], decision_ref="D-SHOOT-TARGET", target_ref="T-SHOOT-INTRUDER"), operation("S03", 3, "pay-cost", "must", "P-SHOOTER", "COST-SHOOT-ACTION", ["SA-SHOOT-RB"]), operation("S04", 4, "invoke-process", "must", "P-SHOOTER", "the initial Shoot Hit through Queen Hits when the target is the Queen", ["SA-SHOOT-RB", "SA-SHOOT-QUEEN-FAQ"], conditions=["target is Queen"], target_ref="T-SHOOT-INTRUDER", invoke="SEM-QUEEN-HIT-001"), operation("S05", 5, "place-component", "must", "P-SHOOTER", "1 Universal Hit marker next to a non-Queen Intruder", ["SA-SHOOT-RB"], conditions=["target is not Queen"], target_ref="T-SHOOT-INTRUDER"), operation("S06", 6, "draw-random", "must", "P-RULES", "one Shoot-die result", ["SA-SHOOT-RB"]), operation("S07", 7, "branch", "must", "P-RULES", "Critical, numeric 2–5, or Ammo-loss result", ["SA-SHOOT-RB"], target_ref="T-SHOOT-INTRUDER"), operation("S08", 8, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-025/029 Queen lethal-result timing versus an initial-Hit threshold already reached", ["SA-SHOOT-RB", "SA-SHOOT-QUEEN-FAQ"], conditions=["target is Queen", "roll is numeric at or below current Hits or skull/Critical"], target_ref="T-SHOOT-INTRUDER"), operation("S09", 9, "invoke-process", "must", "P-RULES", "Queen lethal Shoot result through Queen Hits", ["SA-SHOOT-QUEEN-FAQ"], conditions=["target is Queen", "applicable lethal result occurred under SEM-Q-025/029", "initial Hit did not already consume the one Health-card trigger for this Action"], target_ref="T-SHOOT-INTRUDER", invoke="SEM-QUEEN-HIT-001"), operation("S10", 10, "transition-zone", "if-able", "P-SHOOTER", "one Ammo use from the selected Weapon", ["SA-SHOOT-RB"], conditions=["Ammo-loss result"], transition={"from": "tax.entity.component.token.tactical-gear.ammo", "to": "tax.scaffold.supply-pool"}), operation("S11", 11, "evaluate-condition", "must", "P-RULES", "non-Queen death on Critical or numeric result at/below current Hits", ["SA-SHOOT-RB"], conditions=["target is not Queen"], target_ref="T-SHOOT-INTRUDER"), operation("S12", 12, "evaluate-condition", "must", "P-RULES", "all selected Weapon modifiers in addition to standard result unless text says instead", ["SA-SHOOT-RB"], target_ref="T-SHOOT-INTRUDER")],
        {"policy": "ordered-complete", "unit": "one Shoot Action", "onImpossible": "selection must be legal before payment; preserve initial-Hit then roll order and no-default Queen threshold/critical ordering under SEM-Q-025/029"}, {"kind": "instantaneous-basic-action"}, {"policy": "one target and one die result per Shoot Action; Weapon text may add or replace only as printed"}, [], ["SEM-Q-025", "SEM-Q-029"], []))

    records.append(record(
        "SEM-ACT-BURST-001", "Burst, including Queen Hit allocation", "source-backed-with-open-question", "action", "official-errata", "open-alternatives",
        [assertion("SA-BURST-RB", "SRC-RULEBOOK", "printed pages 12 and 33 / lines 2885, 5490–5537", ["timing", "preconditions", "participants", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Choose a working loaded Ranged Weapon and adjacent Corridor, spend Ammo, roll Burst, allocate Hits with type limits, resolve them, lose leftovers, then resolve the additional-effects symbol.", "docs/rules/02-character-actions.md:ACT-BURST-001"), assertion("SA-BURST-DOOR-FAQ", "SRC-FAQ", "General rules / FQ-P02-U10", ["preconditions", "targets", "operations"], "Closed Doors prevent Bursting through them.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U10")],
        ["icon.actionCard", "icon.ammoToken", "icon.burstDieAdditionalEffects", "term.burst", "term.corridor", "term.hit", "term.queen"], ["tax.entity.agent.character", "tax.entity.agent.intruder", "tax.entity.agent.intruder.queen", "tax.entity.component.card.action", "tax.entity.component.token.tactical-gear.ammo", "tax.entity.spatial.corridor", "tax.process.action.attack.burst", "tax.process.operation.hit"], [],
        timing("TW-BURST", "tax.process.action.attack.burst", "during", "once-per-selected-Burst-Action"), [participant("P-BURSTER", "actor", "tax.entity.agent.character"), participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-INTRUDERS", "affected-collection", "tax.entity.agent.intruder"), participant("P-RULES", "rules-system")], "must",
        [condition("C-BURST", "all", [{"predicate": "selected Ranged Weapon is working, in Hand, and has at least 1 Ammo token"}, {"predicate": "target Corridor is adjacent and no Closed Door blocks Bursting"}], ["SA-BURST-RB", "SA-BURST-DOOR-FAQ"])],
        [decision("D-BURST-WEAPON", "P-PLAYER", "player-choice", 1, 1, False, "public", ["eligible Ranged Weapons in Hand"]), decision("D-BURST-CORRIDOR", "P-PLAYER", "player-choice", 1, 1, False, "public", ["eligible adjacent Corridors"]), decision("D-BURST-HITS", "P-PLAYER", "player-choice", 0, None, True, "public", ["legal Hit allocations among Intruders in the chosen Corridor"])],
        [{"informationId": "I-BURST", "subjectRef": "selected Weapon/Corridor, die result, Hit allocation, Queen track/card trigger, leftovers, and additional effects", "audience": "public", "revealTrigger": "selection/roll/resolution", "secrecy": "Queen Health deck order remains hidden until a card is drawn"}],
        [{"costId": "COST-BURST-ACTION", "payerRef": "P-BURSTER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": None, "destination": "discard pile"}, {"costId": "COST-BURST-AMMO", "payerRef": "P-BURSTER", "resourceTermId": "icon.ammoToken", "quantity": 1, "selectionDecisionRef": None, "destination": "spent/half-used according to token state"}],
        [_target("T-BURST-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-PLAYER", mode="player-choice", minimum=1, maximum=1), _target("T-BURST-INTRUDERS", ["tax.entity.agent.intruder"], selector="P-PLAYER", mode="player-choice")],
        [operation("S01", 1, "choose", "must", "P-PLAYER", "eligible Ranged Weapon", ["SA-BURST-RB"], decision_ref="D-BURST-WEAPON"), operation("S02", 2, "select-target", "must", "P-PLAYER", "one eligible adjacent Corridor", ["SA-BURST-RB", "SA-BURST-DOOR-FAQ"], decision_ref="D-BURST-CORRIDOR", target_ref="T-BURST-CORRIDOR"), operation("S03", 3, "pay-cost", "must", "P-BURSTER", "COST-BURST-ACTION", ["SA-BURST-RB"]), operation("S04", 4, "pay-cost", "must", "P-BURSTER", "COST-BURST-AMMO", ["SA-BURST-RB"]), operation("S05", 5, "draw-random", "must", "P-RULES", "one Burst-die result", ["SA-BURST-RB"]), operation("S06", 6, "choose", "must", "P-PLAYER", "legal Hit allocation: at most 1 per Adult/Larva, exactly 2 per Drone, any number to Queen only up to her track maximum", ["SA-BURST-RB"], decision_ref="D-BURST-HITS", target_ref="T-BURST-INTRUDERS"), operation("S07", 7, "evaluate-condition", "must", "P-RULES", "non-Queen deaths from allocated legal Hit groups", ["SA-BURST-RB"], target_ref="T-BURST-INTRUDERS"), operation("S08", 8, "invoke-process", "if-able", "P-BURSTER", "each allocated Queen Hit through Queen Hits", ["SA-BURST-RB"], conditions=["one or more Burst Hits allocated to Queen"], target_ref="T-BURST-INTRUDERS", invoke="SEM-QUEEN-HIT-001", repeat={"oneAtATime": True, "stopAfterThreshold": True, "sameActionOverflow": "lost"}), operation("S09", 9, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-025 threshold card timing relative to remaining Burst and additional-effect operations", ["SA-BURST-RB"], conditions=["Queen threshold reached during allocated Hits"], target_ref="T-BURST-INTRUDERS"), operation("S10", 10, "evaluate-condition", "must", "P-RULES", "all unallocated or post-threshold leftover Hits are lost", ["SA-BURST-RB"]), operation("S11", 11, "evaluate-condition", "if-able", "P-RULES", "applicable Weapon/Action effects for the Burst additional-effects symbol after normal Hit resolution", ["SA-BURST-RB"], conditions=["additional-effects symbol rolled"] )],
        {"policy": "ordered-complete", "unit": "one Burst Action and one player-owned Hit allocation", "onImpossible": "selection/payment must be legal; each type limit is exact; leftovers and same-Action Queen overflow are lost; adopt no SEM-Q-025 timing default"}, {"kind": "instantaneous-basic-action"}, {"policy": "one Corridor/die/allocation per Burst Action; special additional effects coexist with the printed numeric result"}, [], ["SEM-Q-025"], []))

    resolution_rulebook_assertion = assertion("SA-QH-RESOLUTION-RB", "SRC-RULEBOOK", "printed page 35 / lines 5747–5763 and RB-P35-V01/V02/V03", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Draw/reveal the top Queen Health card, discard its shown number of additional cards without revealing them, resolve its bottom effect even if those discards kill the Queen, then discard the drawn card and reset Hits to 0.", "docs/rules/semantics/queen-health-source-index.json:officialRulebookTextOccurrences")
    resolution_component_assertions = []
    resolution_component_ids = []
    for definition in QUEEN_HEALTH_DEFINITIONS:
        code = _physical_code(definition)
        assertion_id = f"SA-QH-RESOLUTION-FACE-{code}"
        item = assertion(assertion_id, definition["sourceId"], f"{definition['occurrenceId']} / exact physical count and conditional bottom panel", ["informationPolicy", "operations", "partialResolution", "sourceVariants", "unresolvedQuestionRefs"], definition["body"], f"docs/rules/semantics/queen-health-source-index.json:{definition['occurrenceId']}")
        item["textKind"] = "verbatim"
        resolution_component_ids.append(assertion_id)
        resolution_component_assertions.append(item)
    resolution_all_ids = ["SA-QH-RESOLUTION-RB", *resolution_component_ids]

    records.append(record(
        "SEM-QUEEN-HEALTH-RESOLUTION-001", "Resolve one Queen Health card", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [resolution_rulebook_assertion, *resolution_component_assertions],
        ["term.hit", "term.queen", "term.queen-health-card", "term.universal-marker"], ["tax.entity.agent.intruder.queen", "tax.entity.component.card.queen-health", "tax.entity.component.marker.universal", "tax.scaffold.zone.deck", "tax.scaffold.zone.discard-pile"], [],
        timing("TW-QH-RESOLUTION", "tax.entity.component.card.queen-health", "when-triggered", "once-per-Queen-Health-trigger"), [participant("P-DRAWING-SOURCE", "trigger-owner"), participant("P-QUEEN", "affected", "tax.entity.agent.intruder.queen"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-QH-DRAWN", "subjectRef": "drawn physical occurrence, number, bottom effect, and result", "audience": "public after draw", "revealTrigger": "top-card draw", "secrecy": "remaining deck order and fronts stay hidden"}, {"informationId": "I-QH-ADDITIONAL", "subjectRef": "identities/numbers/effects of additionally discarded cards", "audience": "hidden-from-all", "revealTrigger": "none from this discard instruction", "secrecy": "discard exactly the requested available cards without revealing them; do not expose identities in logs or derived state"}], [],
        [_target("T-QH-DRAWN-CARD", ["tax.entity.component.card.queen-health"], mode="random", minimum=0, maximum=1), _target("T-QH-QUEEN", ["tax.entity.agent.intruder.queen"], minimum=0, maximum=1)],
        [operation("S01", 1, "draw-random", "if-able", "P-RULES", "top physical Queen Health occurrence into sem.zone.card-in-resolution", resolution_all_ids, target_ref="T-QH-DRAWN-CARD"), operation("S02", 2, "reveal", "must", "P-RULES", "drawn occurrence's exact two-panel face and source-local number display", resolution_all_ids, conditions=["a top card was drawn"], target_ref="T-QH-DRAWN-CARD"), operation("S03", 3, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-027 whether drawing the final deck card creates Queen death before any discard", ["SA-QH-RESOLUTION-RB"], conditions=["draw left no card in the deck"], target_ref="T-QH-DRAWN-CARD"), operation("S04", 4, "transition-zone", "if-able", "P-RULES", "the source-local displayed number of additional Queen Health cards without revealing them", resolution_all_ids, conditions=["a card was drawn"], transition={"from": "tax.scaffold.zone.deck", "to": "tax.scaffold.zone.discard-pile"}, repeat={"requested": "drawn occurrence printedDiscardCount", "reveal": False, "positionWithinDeck": "source does not add a non-top selector", "stopWhenDeckEmpty": True}), operation("S05", 5, "invoke-process", "if-able", "P-RULES", "Queen death immediately when an additional discard removes the last card", ["SA-QH-RESOLUTION-RB"], conditions=["last Queen Health card was discarded during additional discards"], invoke="SEM-QUEEN-DEATH-001"), operation("S06", 6, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-026 exact attribution of 'drawn by a Character' for the bottom-panel condition", resolution_component_ids, conditions=["a card was drawn"], target_ref="T-QH-DRAWN-CARD"), operation("S07", 7, "invoke-selected-process", "must", "P-RULES", "exact physical occurrence's conditional bottom-panel rule", resolution_all_ids, conditions=["a card was drawn", "bottom condition applicability is evaluated without inventing a SEM-Q-026 default"], target_ref="T-QH-DRAWN-CARD"), operation("S08", 8, "transition-zone", "must", "P-RULES", "drawn Queen Health occurrence after its bottom panel completes", ["SA-QH-RESOLUTION-RB"], conditions=["drawn card remains in resolution"], target_ref="T-QH-DRAWN-CARD", transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.discard-pile"}), operation("S09", 9, "invoke-process", "if-able", "P-RULES", "Queen death when discarding the drawn card removes the last remaining Queen Health card", ["SA-QH-RESOLUTION-RB"], conditions=["drawn card discard is the last Queen Health card under SEM-Q-027"], invoke="SEM-QUEEN-DEATH-001"), operation("S10", 10, "change-value", "must", "P-RULES", "Queen's Hits Universal marker reset to 0 with no overflow carry", ["SA-QH-RESOLUTION-RB"], value_change={"amount": "set exactly 0", "value": "Queen's Hits track position", "overflowCarry": False})],
        {"policy": "source-limited-components", "unit": "one drawn physical occurrence plus each requested hidden additional discard", "onImpossible": "discard every requested card that exists, trigger death at the source-defined boundary, always continue to the drawn card's bottom effect, never reshuffle, and adopt no SEM-Q-025/026/027 default"}, {"kind": "instantaneous-card-resolution-with-final-reset"}, {"policy": "one exact physical face dispatch per trigger; deck is finite and never reshuffled; number/effect/title similarities do not merge copies"}, [], ["SEM-Q-025", "SEM-Q-026", "SEM-Q-027"], []))
    records[-1]["operations"][6]["dispatchRuleIds"] = list(QUEEN_HEALTH_RULE_IDS)

    records.append(record(
        "SEM-QUEEN-DEATH-001", "Queen death and post-death state", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-QUEEN-DEATH-RB", "SRC-RULEBOOK", "printed pages 7 and 35 / lines 817–820, 5764–5772", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "outcomes", "unresolvedQuestionRefs"], "The Queen dies when the last Queen Health card is discarded or the Facility is destroyed; remove her model, ignore future Queen placements, and flip Intruder Help to Queen Dead.", "docs/rulebooks/rulebook_text.txt:lines 817–820, 5764–5772"), assertion("SA-QUEEN-DEATH-OBJ", OBJECTIVE_HELP_SOURCE_ID, "P1-GT-06 and P2-GT-06", ["preconditions", "operations", "outcomes", "unresolvedQuestionRefs"], "The Queen is considered dead when the Facility is Destroyed or when the Queen Health deck is empty.", "docs/rules/source-extraction/objective-help-sheet.json:P1-GT-06/P2-GT-06")],
        ["term.queen", "term.queen-health-card"], ["tax.entity.agent.intruder.queen", "tax.entity.component.card.queen-health"], [],
        timing("TW-QUEEN-DEATH", "tax.entity.agent.intruder.queen", "when-triggered", "once-per-game"), [participant("P-QUEEN", "affected", "tax.entity.agent.intruder.queen"), participant("P-RULES", "rules-system")], "must",
        [condition("C-QUEEN-DEATH", "any", [{"predicate": "last Queen Health card was discarded"}, {"predicate": "Queen Health deck is empty under SEM-Q-027"}, {"predicate": "Facility was destroyed"}], ["SA-QUEEN-DEATH-RB", "SA-QUEEN-DEATH-OBJ"])], [],
        [{"informationId": "I-QUEEN-DEATH", "subjectRef": "Queen alive/dead state, model absence, empty deck, ignored placement, and Help-sheet side", "audience": "public", "revealTrigger": "death trigger", "secrecy": "previously discarded unrevealed card identities remain hidden"}], [],
        [_target("T-QUEEN-DEATH", ["tax.entity.agent.intruder.queen"], minimum=0, maximum=1)],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-027 exact empty-deck versus last-discard trigger boundary", ["SA-QUEEN-DEATH-RB", "SA-QUEEN-DEATH-OBJ"], conditions=["death depends on drawing versus discarding the final card"], target_ref="T-QUEEN-DEATH"), operation("S02", 2, "set-state", "must", "P-RULES", "Queen considered dead", ["SA-QUEEN-DEATH-RB", "SA-QUEEN-DEATH-OBJ"], target_ref="T-QUEEN-DEATH"), operation("S03", 3, "remove-component", "if-able", "P-RULES", "Queen model from the game rather than back to the Intruder pool", ["SA-QUEEN-DEATH-RB"], target_ref="T-QUEEN-DEATH"), operation("S04", 4, "set-state", "must", "P-RULES", "all later effects that would place the Queen in the Facility are ignored", ["SA-QUEEN-DEATH-RB"]), operation("S05", 5, "set-state", "must", "P-RULES", "Intruder Help sheet to The Queen Is Dead side", ["SA-QUEEN-DEATH-RB"])],
        {"policy": "ordered-complete", "unit": "one Queen-death transition", "onImpossible": "model absence does not prevent setting the persistent dead/placement-ignore/Help-side state; SEM-Q-027 remains no-default"}, {"kind": "persistent-irrevocable-until-game-end"}, {"policy": "Queen death occurs at most once; Facility destruction independently satisfies the death state"}, [{"condition": "Queen-death trigger resolves", "result": "Queen remains dead, model absent, future placements ignored, Queen-Dead Help rules active"}], ["SEM-Q-027"], []))

    def build_face(definition: dict) -> dict:
        source = face_by_occurrence[definition["occurrenceId"]]
        code = _physical_code(definition)
        scan_id = f"SA-QHF-{code}-SCAN"
        generic_id = f"SA-QHF-{code}-GENERAL"
        bga_id = f"SA-QHF-{code}-BGA"
        bga_text = "\n".join(row["sourceBlockText"] for row in source["bgaVariantCandidates"]["candidates"])
        assertions = [
            assertion(scan_id, definition["sourceId"], f"{definition['occurrenceId']} / exact panels, count display, punctuation, sentences, and icon occurrences", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "sourceVariants", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/queen-health-source-index.json:{definition['occurrenceId']}"),
            assertion(generic_id, "SRC-RULEBOOK", "printed page 35 / Queen Health card resolution", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "The generic Queen Health procedure owns draw/reveal, hidden additional discards, Queen death checks, drawn-card discard, and reset; this occurrence owns only its exact count declaration, conditional applicability, and bottom effect.", "docs/rules/semantics/queen-health-source-index.json:officialRulebookTextOccurrences"),
            assertion(bga_id, BGA_QUEEN_HEALTH_SOURCE_ID, "QUEEN_CARDS_DATA candidate rows: " + ", ".join(definition["bgaCandidateKeys"]), ["sourceVariants"], bga_text, f"docs/rules/semantics/queen-health-source-index.json:{definition['occurrenceId']}.bgaVariantCandidates"),
        ]
        assertions[0]["textKind"] = "verbatim"
        assertions[2]["textKind"] = "verbatim"
        official_assertion_ids = []
        official_by_id = {row["sourceOccurrenceId"]: row for row in queen_source_index["officialVisibleCounterparts"]}
        for index, counterpart_ref in enumerate(definition["officialCounterpartRefs"], 1):
            counterpart = official_by_id[counterpart_ref]
            assertion_id = f"SA-QHF-{code}-OFFICIAL-{index:02d}"
            item = assertion(assertion_id, "SRC-RULEBOOK", counterpart["locator"], ["sourceVariants"], counterpart["visibleText"], f"docs/rules/semantics/queen-health-source-index.json:{counterpart_ref}")
            item["textKind"] = "verbatim"
            assertions.append(item)
            official_assertion_ids.append(assertion_id)

        target_id = f"T-QHF-{code}-QUEEN"
        targets = [_target(target_id, ["tax.entity.agent.intruder.queen"], minimum=0, maximum=1)]
        participants = [participant("P-DRAWING-SOURCE", "trigger-owner"), participant("P-DRAWING-CHARACTER", "conditional-actor", "tax.entity.agent.character"), participant("P-QUEEN", "affected", "tax.entity.agent.intruder.queen"), participant("P-RULES", "rules-system")]
        decisions = []
        if definition["effectKind"] == "malfunction-or-unreinforce":
            participants.append(participant("P-BRANCH-OWNER", "source-unspecified-decision-owner"))
            decisions.append(decision(f"D-QHF-{code}-BRANCH", "P-BRANCH-OWNER", "unresolved", 1, 1, False, "public", ["Place a Malfunction in the Queen's Room", "Unreinforce Queen's Corridor", "source-defined location dispatch if OR is not a free choice"]))
        information = [{"informationId": f"I-QHF-{code}", "subjectRef": "exact physical occurrence, source-local number, conditional attribution, Queen/location/Characters, effect and outcome", "audience": "public only after generic reveal", "revealTrigger": "SEM-QUEEN-HEALTH-RESOLUTION-001 draws this exact occurrence", "secrecy": "this face remains hidden before draw; sibling copies and deck order remain unrevealed"}]
        terms = ["icon.character", "term.queen", "term.queen-health-card"]
        taxa = ["tax.entity.agent.character", "tax.entity.agent.intruder.queen", "tax.entity.component.card.queen-health"]
        for icon in source["iconOccurrences"]:
            if icon.get("semanticReferenceId"):
                terms.append(icon["semanticReferenceId"])
        sentence_by_id = {row["sentenceId"]: row for row in source["sentences"]}
        sentence_ids = [row["sentenceId"] for row in source["sentences"]]
        ops = []

        def add(sentence_id: str, op_type: str, modality: str, subject: str, obj: str, *, sources=None, conditions=None, decision_ref=None, target_ref=target_id, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
            sentence = sentence_by_id[sentence_id]
            step = len(ops) + 1
            op = operation(f"S{step:02d}", step, op_type, modality, subject, obj, sources or [scan_id, generic_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref, transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence_id
            op["sourcePanelId"] = sentence["panelId"]
            ops.append(op)
            return op

        add(sentence_ids[0], "change-value", "must", "P-RULES", f"generic resolver additional-discard request = {definition['discardCount']}", value_change={"amount": definition["discardCount"], "value": "additional Queen Health cards requested"}, notes="The segmented display remains a source-local no-alias morphology; only this exact visible numeric value is projected.")
        add(sentence_ids[1], "resolve-open-alternative", "must", "P-RULES", "SEM-Q-026 exact meaning of 'drawn by a Character' for this conditional panel", conditions=["this exact occurrence was revealed"])
        common_guard = ["bottom panel applies under the unresolved SEM-Q-026 attribution"]
        effect_kind = definition["effectKind"]
        effect_sentence = sentence_ids[2]
        if effect_kind == "repel":
            terms.extend(["term.repel", "term.corridor"]); taxa.extend(["tax.process.operation.repel", "tax.entity.spatial.corridor"])
            add(effect_sentence, "invoke-process", "must", "P-DRAWING-CHARACTER", "Repel the Queen through the reusable Repel procedure", conditions=common_guard, invoke="SEM-INTRUDER-REPEL-001")
        elif effect_kind == "return-pool":
            add(effect_sentence, "transition-zone", "must", "P-RULES", "Queen model back to the Intruder pool", conditions=common_guard, transition={"from": "tax.entity.spatial.location", "to": "tax.scaffold.supply-pool"}, notes="If Queen death already removed the model, this physical transition is unavailable; the bottom sentence is still evaluated as required by the generic procedure.")
        elif effect_kind == "activate":
            add(effect_sentence, "invoke-process", "must", "P-RULES", "Queen Activation with the drawing Character retained as activating Character when SEM-Q-026 supports that attribution", conditions=common_guard, invoke="SEM-QUEEN-ACTIVATION-001")
        elif effect_kind == "add-queen-tokens":
            add(effect_sentence, "transition-zone", "if-able", "P-RULES", "all currently available Queen tokens from their type pile into the Intruder bag", conditions=common_guard, transition={"from": "tax.scaffold.zone.token-pile", "to": "tax.scaffold.zone.intruder-bag"}, repeat={"scope": "every available Queen token in the Queen token pile", "finiteSupply": True}, notes="Do not duplicate Queen tokens already in the bag or invent tokens outside the source-defined pile lifecycle.")
        elif effect_kind == "draw-action-cards":
            terms.append("icon.actionCard"); taxa.append("tax.entity.component.card.action")
            targets.append(_target(f"T-QHF-{code}-CHARACTERS", ["tax.entity.agent.character"], mode="deterministic-turn-order"))
            add(effect_sentence, "invoke-process", "must", "each Character in the Queen's Room in Turn order", "draw 2 Action cards through the reusable draw/renewal procedure", conditions=common_guard, target_ref=f"T-QHF-{code}-CHARACTERS", invoke="SEM-ACTION-CARD-DRAW-001", repeat={"perCharacter": 2, "order": "Turn order", "finishEachCharacterBeforeNext": True})
        elif effect_kind == "noise-rolls":
            terms.append("term.noise-roll"); taxa.append("tax.process.sequence.noise-roll")
            targets.append(_target(f"T-QHF-{code}-CHARACTERS", ["tax.entity.agent.character"], mode="deterministic-turn-order"))
            add(effect_sentence, "invoke-process", "must", "each Character in the Queen's Room in Turn order", "one complete Noise roll, including each immediate entry Attack before the next Character", conditions=common_guard, target_ref=f"T-QHF-{code}-CHARACTERS", invoke="SEM-NOISE-001", repeat={"perCharacter": 1, "order": "Turn order", "completeImmediateConsequencesBeforeNext": True})
        elif effect_kind == "malfunction-or-unreinforce":
            terms.extend(["icon.malfunction", "term.reinforced-corridor"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.spatial.room", "tax.state.corridor.reinforced"])
            branch_decision = f"D-QHF-{code}-BRANCH"
            add(effect_sentence, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-028 branch ownership versus Queen-location dispatch and target eligibility", conditions=common_guard, decision_ref=branch_decision)
            add(effect_sentence, "invoke-process", "if-able", "P-RULES", "place a Malfunction in the Queen's Room through the reusable finite/fallback procedure", conditions=[*common_guard, "Malfunction branch is selected or source-defined for Queen in a Room under SEM-Q-028"], decision_ref=branch_decision, invoke="SEM-ROOM-MALFUNCTION-PLACEMENT-001")
            add(sentence_ids[3], "change-value", "if-able", "P-RULES", "Queen's reinforced Corridor back from its value-0 side without inventing an original printed value", conditions=[*common_guard, "Unreinforce branch is selected or source-defined for Queen in a Corridor under SEM-Q-028", "Queen's Corridor is reinforced"], decision_ref=branch_decision, value_change={"amount": "remove reinforced state", "value": "tax.state.corridor.reinforced"}, notes="The card says Unreinforce but the checked rules define only Reinforce; do not invent which nonzero face/value appears.")
        else:
            raise AssertionError(effect_kind)

        unresolved = ["SEM-Q-026", "SEM-Q-027"] + (["SEM-Q-028"] if effect_kind == "malfunction-or-unreinforce" else [])
        variants = [{"variantId": f"SV-QHF-{code}-BGA", "sourceId": BGA_QUEEN_HEALTH_SOURCE_ID, "sourceAssertionId": bga_id, "difference": f"Licensed candidate set {definition['bgaCandidateKeys']} is retained independently with status {definition['bgaMatchStatus']}; it omits the scan's shared Character condition and may differ in wording/effect.", "resolution": "Use the exact TTS physical occurrence for this scan-side record. Preserve all licensed keys independently; never pair duplicate copies by BGA ordinal or flatten a material conflict."}]
        for index, (counterpart_ref, assertion_id) in enumerate(zip(definition["officialCounterpartRefs"], official_assertion_ids), 1):
            counterpart = official_by_id[counterpart_ref]
            variants.append({"variantId": f"SV-QHF-{code}-OFFICIAL-{index:02d}", "sourceId": "SRC-RULEBOOK", "sourceAssertionId": assertion_id, "difference": f"Official occurrence {counterpart_ref} is {counterpart['completeness']} and visibly reads {counterpart['visibleText']!r}; it does not identify this physical copy by GUID/CardID.", "resolution": "Official-visible wording/structure controls only its exact current occurrence. Retain this TTS copy independently, including pluralization, condition punctuation, and duplicate-copy provenance."})

        result = record(
            definition["semanticRuleId"], f"Queen Health physical occurrence {code}", "source-backed-with-open-question", "component-effect", "official-primary", "open-alternatives",
            assertions, terms, taxa, [], timing(f"TW-QHF-{code}", "tax.entity.component.card.queen-health", "during", "when-this-exact-occurrence-is-dispatched-by-SEM-QUEEN-HEALTH-RESOLUTION-001"), participants, "must",
            [condition(f"C-QHF-{code}", "all", [{"predicate": f"drawn physical occurrence is {definition['occurrenceId']}"}, {"predicate": "generic resolver has already revealed this face and processed its additional discards"}], [scan_id, generic_id])],
            decisions, information, [], targets, ops,
            {"policy": "source-conditional-steps", "unit": "one exact physical Queen Health occurrence's count declaration and bottom panel", "onImpossible": "generic draw/discard/reset remains outside this face; bottom condition/branch/death ordering keeps SEM-Q-026/027/028 no-default; finite invoked procedures retain their own boundaries"}, {"kind": "instantaneous-dispatched-component-effect"}, {"policy": "one dispatch per drawn physical occurrence; identical bytes/headings/numbers do not merge copies or stack effects"}, [], unresolved, variants)
        return result

    records.extend(build_face(definition) for definition in QUEEN_HEALTH_DEFINITIONS)
    return records
