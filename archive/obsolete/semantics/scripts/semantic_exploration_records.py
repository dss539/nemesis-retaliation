from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path


BASE_EXPLORATION_DECK_GUID = "63add2"
BGA_EXPLORATION_SOURCE_ID = "SRC-BGA-EXPLORATION"
BGA_EXPLORATION_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
EXPLORATION_BACK_SOURCE_ID = "SRC-EXPLORATION-BACK"
EXPLORATION_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/exploration-092.jpg"
SLOT_LABELS = {
    0: "upper-left",
    1: "upper-right",
    2: "right",
    3: "lower-right",
    4: "lower-left",
    5: "left",
}


def _sentence(sentence_id: str, section: str, exact_text: str) -> dict:
    return {"sentenceId": sentence_id, "section": section, "exactText": exact_text}


def _diagram(corridors: list[int], noise: list[int], room_icons: list[str], exact_text: str) -> dict:
    return {
        "corridorSlots": corridors,
        "noiseSlots": noise,
        "roomIcons": room_icons,
        "exactText": exact_text,
    }


# The crosswalk is occurrence-first. TTS deck/card identity, exact source bytes,
# literal six-slot diagrams, and ordered effect fields identify each occurrence.
# The faces have no printed titles, so display names are never identity keys.
EXPLORATION_DEFINITIONS = {
    5629: {
        "sourceId": "SRC-EXPLORATION-5629",
        "bgaKey": "ExplorationCard9",
        "ruleId": "SEM-EXPLORATION-5629-001",
        "roomType": "ABC",
        "diagram": _diagram([1, 2, 3], [2], [], "[character]\n[noise]"),
        "sentences": [
            _sentence("EX5629-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5629-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5629-ENTRANCE-01", "entrance", "Resolve\n[noiseDieHazard]"),
        ],
    },
    5630: {
        "sourceId": "SRC-EXPLORATION-5630",
        "bgaKey": "ExplorationCard10",
        "ruleId": "SEM-EXPLORATION-5630-001",
        "roomType": "ABC",
        "diagram": _diagram([0, 2, 3], [0, 3], [], "[noise]\n[character]\n[noise]"),
        "sentences": [
            _sentence("EX5630-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5630-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5630-ENTRANCE-01", "entrance", "Entrance Effect:\nPlace 2 Adults in the Corridor\nyou have just passed through."),
            _sentence("EX5630-ENTRANCE-02", "entrance", "Then, make a Noise roll."),
        ],
        "adultCount": 2,
    },
    5631: {
        "sourceId": "SRC-EXPLORATION-5631",
        "bgaKey": "ExplorationCard11",
        "ruleId": "SEM-EXPLORATION-5631-001",
        "roomType": "ABC",
        "diagram": _diagram([2, 5], [2], [], "[character]\n[noise]"),
        "sentences": [
            _sentence("EX5631-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5631-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5631-ENTRANCE-01", "entrance", "Entrance Effect:\nPlace 3 Adults in the Corridor\nyou have just passed through."),
            _sentence("EX5631-ENTRANCE-02", "entrance", "Then, make a Noise roll."),
        ],
        "adultCount": 3,
    },
    5632: {
        "sourceId": "SRC-EXPLORATION-5632",
        "bgaKey": "ExplorationCard5",
        "ruleId": "SEM-EXPLORATION-5632-001",
        "roomType": "ABC",
        "diagram": _diagram([1, 2], [2], ["malfunction"], "[character] [malfunction]\n[noise]"),
        "sentences": [
            _sentence("EX5632-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5632-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5632-ENTRANCE-01", "entrance", "Close all doors around this room."),
            _sentence("EX5632-ENTRANCE-02", "entrance", "Make a Noise roll."),
        ],
        "closeDoors": True,
    },
    5633: {
        "sourceId": "SRC-EXPLORATION-5633",
        "bgaKey": "ExplorationCard4",
        "ruleId": "SEM-EXPLORATION-5633-001",
        "roomType": "ABC",
        "diagram": _diagram([1, 2, 3], [1], ["malfunction"], "[character] [malfunction]\n[noise]"),
        "sentences": [
            _sentence("EX5633-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5633-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5633-ENTRANCE-01", "entrance", "Make a Noise roll."),
        ],
    },
    5634: {
        "sourceId": "SRC-EXPLORATION-5634",
        "bgaKey": "ExplorationCard6",
        "ruleId": "SEM-EXPLORATION-5634-001",
        "roomType": "ABC",
        "diagram": _diagram([1, 3], [3], ["fire"], "[character] [fire]\n[noise]"),
        "sentences": [
            _sentence("EX5634-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5634-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5634-ENTRANCE-01", "entrance", "Make a Noise roll."),
        ],
        "officialOccurrences": [
            {
                "occurrenceId": "RB-P26-V01",
                "locator": "printed page 26 / RB-P26-V01 / worked example panels 1–2",
                "visibleText": "Place a Room of the A, B, or C type depending on the Section the Room is being placed in. Reminder: Place 1 [source glyph] if you are Moving Cautiously. Entrance Effect: Make a Noise roll.",
            },
            {
                "occurrenceId": "RB-P27-V01",
                "locator": "printed page 27 / RB-P27-V01 / worked example panels 3–4",
                "visibleText": "The same illustrated Exploration face continues through Character movement, Entrance-effect Noise, and discard.",
            },
        ],
    },
    5635: {
        "sourceId": "SRC-EXPLORATION-5635",
        "bgaKey": "ExplorationCard12",
        "ruleId": "SEM-EXPLORATION-5635-001",
        "roomType": "ABC",
        "diagram": _diagram([1, 2, 4], [1], [], "[character]\n[noise]"),
        "sentences": [
            _sentence("EX5635-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5635-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5635-ENTRANCE-01", "entrance", "Place 4 Adults in the Corridor\nyou have just passed through."),
            _sentence("EX5635-ENTRANCE-02", "entrance", "Then, make a Noise roll as normal."),
        ],
        "adultCount": 4,
    },
    5636: {
        "sourceId": "SRC-EXPLORATION-5636",
        "bgaKey": "ExplorationCard7",
        "ruleId": "SEM-EXPLORATION-5636-001",
        "roomType": "ABC",
        "diagram": _diagram([2, 3], [], ["fire"], "[character] [fire]"),
        "sentences": [
            _sentence("EX5636-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5636-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5636-ENTRANCE-01", "entrance", "Close all doors around this room."),
            _sentence("EX5636-ENTRANCE-02", "entrance", "Make a Noise roll."),
        ],
        "closeDoors": True,
    },
    5637: {
        "sourceId": "SRC-EXPLORATION-5637",
        "bgaKey": "ExplorationCard3",
        "ruleId": "SEM-EXPLORATION-5637-001",
        "roomType": "?",
        "diagram": _diagram([1, 3, 4], [1], [], "[character]\n[noise]"),
        "sentences": [
            _sentence("EX5637-PLACEMENT-01", "placement", "Place a “?” Room tile."),
            _sentence("EX5637-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5637-ENTRANCE-01", "entrance", "Resolve\n[noiseDieHazard]"),
            _sentence("EX5637-LIFECYCLE-01", "lifecycle", "Remove this card from the game."),
        ],
        "removeFromGame": True,
    },
    5638: {
        "sourceId": "SRC-EXPLORATION-5638",
        "bgaKey": "ExplorationCard2",
        "ruleId": "SEM-EXPLORATION-5638-001",
        "roomType": "?",
        "diagram": _diagram([0, 1, 3], [1], ["malfunction", "fire"], "[character] [malfunction] [fire]\n[noise]"),
        "sentences": [
            _sentence("EX5638-PLACEMENT-01", "placement", "Place a “?” Room tile."),
            _sentence("EX5638-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5638-ENTRANCE-01", "entrance", "Close all doors around this room."),
            _sentence("EX5638-ENTRANCE-02", "entrance", "Make a Noise roll."),
            _sentence("EX5638-LIFECYCLE-01", "lifecycle", "Remove this card from the game."),
        ],
        "closeDoors": True,
        "removeFromGame": True,
    },
    5639: {
        "sourceId": "SRC-EXPLORATION-5639",
        "bgaKey": "ExplorationCard1",
        "ruleId": "SEM-EXPLORATION-5639-001",
        "roomType": "?",
        "diagram": _diagram([0, 1, 3, 4], [0, 1, 3, 4], ["malfunction"], "[noise] [noise]\n[character] [malfunction]\n[noise] [noise]"),
        "sentences": [
            _sentence("EX5639-PLACEMENT-01", "placement", "Place a “?” Room tile."),
            _sentence("EX5639-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5639-ENTRANCE-01", "entrance", "Entrance Effect:\nClose all Doors around this Room."),
            _sentence("EX5639-LIFECYCLE-01", "lifecycle", "Remove this card from the game."),
        ],
        "closeDoors": True,
        "removeFromGame": True,
        "officialOccurrences": [
            {
                "occurrenceId": "RB-P24-V01",
                "locator": "printed page 24 / RB-P24-V01 / Exploration-card anatomy diagram",
                "visibleText": "Place a Room of the ? type. Reminder: Place 1 [source glyph] if you are Moving Cautiously. Entrance Effect: Close all Doors around this Room. Remove this card from the game.",
            },
        ],
    },
    5640: {
        "sourceId": "SRC-EXPLORATION-5640",
        "bgaKey": "ExplorationCard8",
        "ruleId": "SEM-EXPLORATION-5640-001",
        "roomType": "ABC",
        "diagram": _diagram([2, 5], [], [], "[character]"),
        "sentences": [
            _sentence("EX5640-PLACEMENT-01", "placement", "Place A/B/C Room\ndepending on your Section."),
            _sentence("EX5640-REMINDER-01", "reminder", "Reminder:\nPlace 1 [secure] if you are Moving with [secure]."),
            _sentence("EX5640-ENTRANCE-01", "entrance", "Entrance Effect:\nClose all Doors around this Room."),
            _sentence("EX5640-ENTRANCE-02", "entrance", "Resolve [noiseDieHazard]."),
        ],
        "closeDoors": True,
    },
}

EXPLORATION_RULE_IDS = [EXPLORATION_DEFINITIONS[card_id]["ruleId"] for card_id in sorted(EXPLORATION_DEFINITIONS)]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_bga_exploration(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const EXPLORATION_CARDS_DATA = \{\n(.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError("EXPLORATION_CARDS_DATA block not found")
    block = match.group(1)
    records: dict[str, dict] = {}
    for row in re.finditer(r"^  (ExplorationCard\d+): \{\n(.*?)^  \},$", block, re.M | re.S):
        key, body = row.groups()
        parsed: dict[str, object] = {}
        field_types = {
            "number": "int",
            "type": "literal",
            "corridors": "literal",
            "corridorsWithNoise": "literal",
            "otherTokens": "literal",
            "effectDesc": "literal",
            "closeDoor": "bool",
            "noiseRoll": "bool",
            "hazard": "bool",
            "intrudersToAdd": "int",
            "removeFromGame": "bool",
        }
        for field, kind in field_types.items():
            field_match = re.search(rf"^    {field}: (.*),$", body, re.M)
            if not field_match:
                raise AssertionError(f"missing {field} in {key}")
            literal = field_match.group(1)
            if kind == "bool":
                if literal not in {"true", "false"}:
                    raise AssertionError(f"invalid boolean {field} in {key}")
                parsed[field] = literal == "true"
            elif kind == "int":
                parsed[field] = int(literal)
            else:
                parsed[field] = ast.literal_eval(literal)
        parsed["sourceBlockText"] = row.group(0)
        records[key] = parsed
    if len(records) != 12:
        raise AssertionError(f"expected 12 BGA Exploration records, got {len(records)}")
    return records


def _icon_occurrences(card_id: int, definition: dict) -> list[dict]:
    occurrences = []
    sequence = 1

    def add(region: str, reference: str, location: str) -> None:
        nonlocal sequence
        occurrences.append(
            {
                "occurrenceId": f"TTS-EXPLORATION-{card_id}-ICON-{sequence:02d}",
                "sequence": sequence,
                "region": region,
                "printedToken": f"[{reference}]",
                "semanticReferenceId": f"icon.{reference}",
                "sourceLocation": location,
            }
        )
        sequence += 1

    add("diagram-room", "character", "center of depicted Room")
    for icon in definition["diagram"]["roomIcons"]:
        add("diagram-room", icon, f"depicted {icon} occurrence in new Room")
    for slot in definition["diagram"]["noiseSlots"]:
        add("diagram-corridor", "noise", f"source-local {SLOT_LABELS[slot]} Corridor slot")
    add("reminder", "secure", "component to place in the reminder sentence")
    add("reminder", "secure", "source-local icon after “Moving with” in the reminder sentence")
    for sentence in definition["sentences"]:
        if "[noiseDieHazard]" in sentence["exactText"]:
            add("entrance", "noiseDieHazard", sentence["sentenceId"])
    return occurrences


def build_exploration_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / "assets/tts-mod/extract/card-text-corpus.json").read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    progress = json.loads((repo / "assets/tts-mod/extract/vision-progress.json").read_text(encoding="utf-8"))
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    provenance = json.loads((repo / "assets/tts-mod/extract/card-provenance-inventory.json").read_text(encoding="utf-8"))
    roles = json.loads((repo / "assets/tts-mod/extract/v2/lua_roles.json").read_text(encoding="utf-8"))
    objects = json.loads((repo / "assets/tts-mod/extract/v2/objects.json").read_text(encoding="utf-8"))
    backlog = json.loads((repo / "docs/rules/semantics/backlog.json").read_text(encoding="utf-8"))
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    secondary_index = json.loads((repo / "docs/rules/source-extraction/secondary-evidence-index.json").read_text(encoding="utf-8"))
    visual_index = json.loads((repo / "docs/rules/source-extraction/rulebook-visual-obligations.json").read_text(encoding="utf-8"))
    faq_index = json.loads((repo / "docs/rules/source-extraction/faq-v1.2-source-extraction.json").read_text(encoding="utf-8"))
    bga = _parse_bga_exploration(repo / BGA_EXPLORATION_PATH)

    role = next(row for row in roles if row.get("role") == "explorationDeck" and row.get("guid") == BASE_EXPLORATION_DECK_GUID)
    deck_card_ids = sorted(int(value) for value in role["deck_nums"])
    if deck_card_ids != list(range(5629, 5641)) or role.get("n_urls") != 13:
        raise AssertionError("base Exploration TTS role/card IDs changed")
    deck_object = next(row for row in objects if row.get("guid") == BASE_EXPLORATION_DECK_GUID)
    if deck_object.get("parent") != []:
        raise AssertionError("base Exploration deck is no longer a root base-game object")

    excluded_roles = []
    for excluded_role, excluded_guid, scope in (
        ("xyrianExplorationDeck", "6b2b69", "Xyrian expansion"),
        ("explorationDeck", "a24dc8", "Neoflesh expansion"),
        ("explorationDeck", "dd1eda", "Sangrevores expansion"),
        ("explorationDeck", "2e8e9d", "Carnomorph expansion"),
    ):
        excluded = next(row for row in roles if row.get("role") == excluded_role and row.get("guid") == excluded_guid)
        excluded_roles.append(
            {
                "role": excluded_role,
                "guid": excluded_guid,
                "scope": scope,
                "cardIds": sorted(int(value) for value in excluded.get("deck_nums") or []),
                "reason": "expansion material excluded from the base-game semantic batch",
            }
        )

    table = next(
        row
        for row in secondary_index["licensedDigital"]["structuredIndex"]["tables"]
        if row["name"] == "EXPLORATION_CARDS_DATA"
    )
    if table["count"] != 12 or set(table["keys"]) != set(bga):
        raise AssertionError("licensed Exploration index changed")

    visual_by_id = {
        row["occurrenceId"]: row
        for page in visual_index["pages"]
        for row in page.get("visualUnits", [])
    }
    required_visuals = {"RB-P24-V01", "RB-P26-V01", "RB-P27-V01"}
    if not required_visuals.issubset(visual_by_id):
        raise AssertionError("official Exploration visual occurrence changed")
    faq_by_id = {
        row["sourceUnitId"]: row
        for page in faq_index["pages"]
        for row in page.get("units", [])
    }
    if not {"FQ-P02-U06", "FQ-P02-U07"}.issubset(faq_by_id):
        raise AssertionError("Exploration FAQ occurrence changed")

    faces: dict[int, dict] = {}
    shared_back = None
    back_card_selectors = []
    for provenance_row in provenance:
        for obj in provenance_row.get("objects", []):
            if obj.get("key") == "BackURL" and obj.get("guid") == BASE_EXPLORATION_DECK_GUID:
                shared_back = {"provenance": provenance_row, "object": obj}
            if obj.get("key") == "BackURL" and obj.get("gmnotes") == "exploration" and ["Deck", BASE_EXPLORATION_DECK_GUID, ""] in obj.get("parent", []):
                back_card_selectors.append(obj)
            if obj.get("key") != "FaceURL" or obj.get("gmnotes") != "exploration" or not obj.get("cardId"):
                continue
            if ["Deck", BASE_EXPLORATION_DECK_GUID, ""] not in obj.get("parent", []):
                continue
            card_id = int(obj["cardId"]) // 100
            if card_id not in deck_card_ids:
                continue
            source_path = "assets/tts-mod/extract/v2-dl/tree/" + provenance_row["file"]
            if card_id in faces:
                raise AssertionError(f"duplicate base Exploration cardId {card_id}")
            faces[card_id] = {"provenance": provenance_row, "object": obj, "sourcePath": source_path}
    if set(faces) != set(deck_card_ids) or shared_back is None or len(back_card_selectors) != 12:
        raise AssertionError("base Exploration face/back provenance closure failed")

    rows = []
    for card_id in deck_card_ids:
        definition = EXPLORATION_DEFINITIONS[card_id]
        face = faces[card_id]
        source_path = face["sourcePath"]
        source_file = repo / source_path
        corpus_row = corpus_by_path[source_path]
        progress_row = progress_by_path[source_path]
        source_sha = _sha(source_file)
        if source_sha != corpus_row["sourceSha256"] or source_sha != progress_row["sha256"]:
            raise AssertionError(f"Exploration source hash drift: {card_id}")
        if not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") != "draft-full":
            raise AssertionError(f"Exploration corpus readiness drift: {card_id}")
        if (corpus_row.get("printedData") or {}).get("title") != "":
            raise AssertionError(f"invented Exploration printed title: {card_id}")
        body = corpus_row["printedData"]["body"]
        if (progress_row.get("semanticRead") or {}).get("body") != body:
            raise AssertionError(f"Exploration transcription projection drift: {card_id}")

        unit_rows = []
        cursor = 0
        placement = definition["sentences"][0]
        placement_start = body.find(placement["exactText"], cursor)
        placement_end = placement_start + len(placement["exactText"])
        if placement_start < 0:
            raise AssertionError(f"Exploration placement sentence drift: {card_id}")
        unit_rows.append({**placement, "unitId": placement["sentenceId"], "unitKind": "printed-sentence", "sequence": 1, "start": placement_start, "end": placement_end})
        cursor = placement_end

        diagram = definition["diagram"]
        diagram_start = body.find(diagram["exactText"], cursor)
        diagram_end = diagram_start + len(diagram["exactText"])
        if diagram_start < 0:
            raise AssertionError(f"Exploration diagram text drift: {card_id}")
        diagram_unit_id = f"EX{card_id}-DIAGRAM-01"
        unit_rows.append(
            {
                "unitId": diagram_unit_id,
                "unitKind": "source-local-diagram",
                "section": "diagram",
                "sequence": 2,
                "start": diagram_start,
                "end": diagram_end,
                "exactText": diagram["exactText"],
                "roomType": definition["roomType"],
                "corridorSlots": [
                    {"slotIndex": slot, "slotLabel": SLOT_LABELS[slot]}
                    for slot in diagram["corridorSlots"]
                ],
                "noiseSlots": [
                    {"slotIndex": slot, "slotLabel": SLOT_LABELS[slot]}
                    for slot in diagram["noiseSlots"]
                ],
                "roomIcons": ["character", *diagram["roomIcons"]],
                "resolutionOrder": "source-unspecified; SEM-Q-011",
            }
        )
        cursor = diagram_end

        for sentence in definition["sentences"][1:]:
            start = body.find(sentence["exactText"], cursor)
            if start < 0:
                raise AssertionError(f"Exploration sentence boundary drift: {card_id} {sentence['sentenceId']}")
            end = start + len(sentence["exactText"])
            unit_rows.append({**sentence, "unitId": sentence["sentenceId"], "unitKind": "printed-sentence", "sequence": len(unit_rows) + 1, "start": start, "end": end})
            cursor = end
        if not definition.get("removeFromGame"):
            unit_rows.append(
                {
                    "unitId": f"EX{card_id}-PROCEDURE-DISCARD",
                    "unitKind": "official-procedure-lifecycle",
                    "section": "lifecycle",
                    "sequence": len(unit_rows) + 1,
                    "start": None,
                    "end": None,
                    "exactText": "Discard the Exploration card – Unless it was already removed as a part of the Entrance Effect.",
                    "sourceId": "SRC-RULEBOOK",
                    "locator": "printed page 24 / Exploration Sequence step 7",
                }
            )

        bga_row = bga[definition["bgaKey"]]
        if bga_row["type"] != definition["roomType"] or bga_row["corridors"] != diagram["corridorSlots"] or bga_row["corridorsWithNoise"] != diagram["noiseSlots"] or bga_row["otherTokens"] != diagram["roomIcons"]:
            raise AssertionError(f"Exploration licensed/source diagram crosswalk drift: {card_id}")
        if bga_row["intrudersToAdd"] != definition.get("adultCount", 0) or bga_row["closeDoor"] != definition.get("closeDoors", False) or bga_row["removeFromGame"] != definition.get("removeFromGame", False):
            raise AssertionError(f"Exploration licensed/source effect crosswalk drift: {card_id}")

        backlog_id = "CARD:" + source_sha[:16]
        backlog_row = backlog_by_id.get(backlog_id)
        if not backlog_row or backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != source_sha:
            raise AssertionError(f"Exploration backlog occurrence drift: {card_id}")
        official_occurrences = []
        for occurrence in definition.get("officialOccurrences", []):
            visual = visual_by_id[occurrence["occurrenceId"]]
            official_occurrences.append(
                {
                    **occurrence,
                    "sourceId": "SRC-RULEBOOK",
                    "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
                    "visualType": visual["type"],
                    "obligationClass": visual["obligationClass"],
                    "variantDifference": "The current official visible occurrence uses full current Room-placement and Moving Cautiously wording; the untitled TTS face preserves abbreviated prototype wording and two source-local Secure glyph occurrences.",
                }
            )

        rows.append(
            {
                "explorationOccurrenceId": f"TTS-EXPLORATION-{card_id}-FACE",
                "ttsDeckGuid": BASE_EXPLORATION_DECK_GUID,
                "ttsCardGuid": face["object"]["guid"],
                "ttsCardId": card_id,
                "ttsRole": "explorationDeck",
                "ttsClassification": face["object"]["gmnotes"],
                "sourceSelector": {
                    "key": "FaceURL",
                    "objectType": "CardCustom",
                    "cardId": face["object"]["cardId"],
                    "guid": face["object"]["guid"],
                    "parentDeckGuid": BASE_EXPLORATION_DECK_GUID,
                    "url": face["provenance"]["url"],
                    "selectorStatus": "exact",
                    "selectorGap": None,
                    "generatedSpriteSheetCell": False,
                },
                "sourceId": definition["sourceId"],
                "sourcePath": source_path,
                "sourceSha256": source_sha,
                "sourceAuthority": "source-bound-component-scan",
                "sourceVersion": f"TTS base Exploration face / deck {BASE_EXPLORATION_DECK_GUID} / cardId {card_id}",
                "corpusEvidencePath": "assets/tts-mod/extract/card-text-corpus.json",
                "provenanceEvidencePath": "assets/tts-mod/extract/card-provenance-inventory.json",
                "visionEvidencePath": "assets/tts-mod/extract/vision-progress.json",
                "printedTitle": "",
                "identityLabel": f"untitled TTS Exploration occurrence {card_id}",
                "printedBody": body,
                "extractionState": corpus_row["extractionState"],
                "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
                "sourceUnits": unit_rows,
                "iconOccurrences": _icon_occurrences(card_id, definition),
                "semanticRuleId": definition["ruleId"],
                "backlogUnitId": backlog_id,
                "bgaOccurrence": {
                    "sourceId": BGA_EXPLORATION_SOURCE_ID,
                    "sourcePath": BGA_EXPLORATION_PATH,
                    "sourceSha256": _sha(repo / BGA_EXPLORATION_PATH),
                    "sourceVersion": "licensed BGA immutable build 260622-1220 / EXPLORATION_CARDS_DATA",
                    "table": "EXPLORATION_CARDS_DATA",
                    "key": definition["bgaKey"],
                    **bga_row,
                    "variantDifference": "The licensed occurrence supplies a numbered structured identity and normalized room/diagram/effect fields but no printed title or full reminder wording. It remains secondary and does not rewrite the exact untitled scan.",
                },
                "officialOccurrences": official_occurrences,
                "faqOccurrences": [
                    {
                        "sourceId": "SRC-FAQ",
                        "sourceUnitId": faq_id,
                        "printedText": faq_by_id[faq_id]["printedText"],
                    }
                    for faq_id in (
                        (["FQ-P02-U06"] if definition.get("closeDoors") else [])
                        + (["FQ-P02-U07"] if definition.get("removeFromGame") else [])
                    )
                ],
                "joinEvidence": {
                    "identityJoin": "explicit occurrence crosswalk",
                    "titleOnlyJoin": False,
                    "basis": [
                        "root base Exploration TTS role and exact cardId",
                        "exact CardCustom FaceURL GUID and parent deck GUID",
                        "closed-corpus source path and live SHA-256",
                        "literal six-slot Corridor/Noise/Room-icon diagram",
                        "ordered printed placement/reminder/Entrance/lifecycle units",
                        "explicit licensed EXPLORATION_CARDS_DATA key and exact structured fields",
                    ],
                },
            }
        )

    back_file = repo / EXPLORATION_BACK_PATH
    back_corpus = corpus_by_path[EXPLORATION_BACK_PATH]
    back_sha = _sha(back_file)
    if back_sha != back_corpus["sourceSha256"] or back_corpus.get("rulesTextPresent"):
        raise AssertionError("Exploration shared back corpus drift")

    return {
        "schemaVersion": 1,
        "recordType": "semantic-exploration-source-index",
        "scope": "entire base-game Exploration-card family; source versions and untitled occurrences remain independent",
        "derivationPolicy": "Derive base faces from the root TTS role, exact CardID/GUID/FaceURL provenance, closed-corpus bytes, literal diagrams, and ordered source units; crosswalk explicitly to licensed and official visible occurrences without title, folder, display-name, or modulo joins.",
        "counts": {
            "explorationIdentities": len(rows),
            "ttsFaceOccurrences": len(rows),
            "ttsSharedBackOccurrences": 1,
            "directFaceSelectors": sum(not row["sourceSelector"]["generatedSpriteSheetCell"] for row in rows),
            "generatedSpriteSheetCells": sum(row["sourceSelector"]["generatedSpriteSheetCell"] for row in rows),
            "selectorGaps": sum(row["sourceSelector"]["selectorGap"] is not None for row in rows),
            "untitledFaces": sum(row["printedTitle"] == "" for row in rows),
            "sourceBoundDraftFaces": sum(row["extractionState"] == "draft-full" for row in rows),
            "licensedDigitalOccurrences": len(bga),
            "officialVisibleComponentOccurrences": sum(len(row["officialOccurrences"]) for row in rows),
            "officialVisibleComponentIdentities": sum(bool(row["officialOccurrences"]) for row in rows),
            "faqOccurrences": sum(len(row["faqOccurrences"]) for row in rows),
            "printedSentences": sum(sum(unit["unitKind"] == "printed-sentence" for unit in row["sourceUnits"]) for row in rows),
            "sourceLocalDiagrams": sum(sum(unit["unitKind"] == "source-local-diagram" for unit in row["sourceUnits"]) for row in rows),
            "functionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in rows),
            "backlogTuples": len(rows),
        },
        "familyCountEvidence": {
            "officialRulebook": {
                "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
                "locator": "unprinted PDF page 3 / component list / rulebook_text line 535",
                "printedCount": 12,
            },
            "ttsRole": {
                "sourcePath": "assets/tts-mod/extract/v2/lua_roles.json",
                "deckGuid": BASE_EXPLORATION_DECK_GUID,
                "rootParent": deck_object["parent"],
                "nUrls": role["n_urls"],
                "faceCardIds": deck_card_ids,
                "faceCount": len(rows),
                "sharedBackCount": 1,
            },
            "closedCorpus": {
                "sourcePath": "assets/tts-mod/extract/card-text-corpus.json",
                "faceCount": len(rows),
                "generatedSpriteSheetCells": 0,
                "sourcePaths": [row["sourcePath"] for row in rows],
            },
            "licensedDigital": {
                "sourcePath": BGA_EXPLORATION_PATH,
                "indexPath": "docs/rules/source-extraction/secondary-evidence-index.json",
                "table": "EXPLORATION_CARDS_DATA",
                "count": len(bga),
                "keys": sorted(bga),
            },
            "officialVisuals": {
                "sourcePath": "docs/rules/source-extraction/rulebook-visual-obligations.json",
                "occurrenceIds": sorted(required_visuals),
                "occurrenceCount": len(required_visuals),
                "componentIdentityCount": 2,
            },
            "backlog": {
                "sourcePath": "docs/rules/semantics/backlog.json",
                "count": len(rows),
                "unitIds": [row["backlogUnitId"] for row in rows],
            },
        },
        "excludedExpansionRoles": excluded_roles,
        "sharedBack": {
            "sourceId": EXPLORATION_BACK_SOURCE_ID,
            "occurrenceId": "TTS-EXPLORATION-SHARED-BACK",
            "sourcePath": EXPLORATION_BACK_PATH,
            "sourceSha256": back_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS shared base Exploration back / deck {BASE_EXPLORATION_DECK_GUID}",
            "sourceSelector": {
                "key": "BackURL",
                "objectType": "Deck",
                "guid": BASE_EXPLORATION_DECK_GUID,
                "url": shared_back["provenance"]["url"],
                "deckSelectorCount": 1,
                "cardSelectorCount": len(back_card_selectors),
            },
            "corpusEvidencePath": "assets/tts-mod/extract/card-text-corpus.json",
            "provenanceEvidencePath": "assets/tts-mod/extract/card-provenance-inventory.json",
            "rulesTextPresent": False,
            "printedBackLabel": "EXPLORATION\nPRIMEBLOOD",
            "role": "paired non-operative shared card back",
        },
        "faces": rows,
    }


def exploration_source_registry_rows(exploration_source_index: dict) -> list[dict]:
    rows = []
    for face in exploration_source_index["faces"]:
        rows.append(
            {
                "sourceId": face["sourceId"],
                "authority": face["sourceAuthority"],
                "version": face["sourceVersion"],
                "path": face["sourcePath"],
                "sha256": face["sourceSha256"],
                "occurrenceId": face["explorationOccurrenceId"],
                "evidenceIndexPath": face["corpusEvidencePath"],
                "evidenceRecord": face["sourceSha256"],
                "provenanceIndexPath": face["provenanceEvidencePath"],
            }
        )
    back = exploration_source_index["sharedBack"]
    rows.append(
        {
            "sourceId": back["sourceId"],
            "authority": back["sourceAuthority"],
            "version": back["sourceVersion"],
            "path": back["sourcePath"],
            "sha256": back["sourceSha256"],
            "occurrenceId": back["occurrenceId"],
            "evidenceIndexPath": back["corpusEvidencePath"],
            "evidenceRecord": back["sourceSha256"],
            "provenanceIndexPath": back["provenanceEvidencePath"],
        }
    )
    rows.append(
        {
            "sourceId": BGA_EXPLORATION_SOURCE_ID,
            "authority": "licensed-digital-secondary",
            "version": "licensed BGA immutable build 260622-1220 / EXPLORATION_CARDS_DATA",
            "path": BGA_EXPLORATION_PATH,
            "sha256": exploration_source_index["faces"][0]["bgaOccurrence"]["sourceSha256"],
            "occurrenceId": "EXPLORATION_CARDS_DATA",
            "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json",
            "evidenceRecord": "EXPLORATION_CARDS_DATA",
        }
    )
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None) -> dict:
    return {
        "targetId": target_id,
        "selectorRef": "rules-system" if not mode.startswith("unresolved") else "unresolved-by-source",
        "eligibleTaxonIds": eligible_taxa,
        "cardinality": {"min": minimum, "max": maximum},
        "selectionMode": mode,
        "visibility": "public",
    }


def build_exploration_records(repo: Path, exploration_source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    del repo, decision
    face_by_card = {row["ttsCardId"]: row for row in exploration_source_index["faces"]}
    records = []

    for card_id in sorted(EXPLORATION_DEFINITIONS):
        definition = EXPLORATION_DEFINITIONS[card_id]
        source = face_by_card[card_id]
        code = str(card_id)
        scan_assertion_id = f"SA-EXP-{code}-SCAN"
        procedure_assertion_id = f"SA-EXP-{code}-PROCEDURE"
        bga_assertion_id = f"SA-EXP-{code}-BGA"
        assertions = [
            assertion(
                scan_assertion_id,
                definition["sourceId"],
                f"{source['explorationOccurrenceId']} / exact untitled face",
                ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "sourceVariants", "unresolvedQuestionRefs"],
                source["printedBody"],
                f"docs/rules/semantics/exploration-source-index.json:{source['explorationOccurrenceId']}",
            ),
            assertion(
                procedure_assertion_id,
                "SRC-RULEBOOK",
                "printed pages 17 and 24–27 / component limits, Exploration Sequence, and worked example",
                ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "unresolvedQuestionRefs", "sourceVariants"],
                "Orient and resolve the exact Exploration occurrence: place the required random Room, random Corridors and depicted markers, move the explorer and add Secure if Moving Cautiously, resolve Entrance Effects, then discard unless removed. Invalid Corridors and their Noise are omitted; generic components are finite.",
                "docs/rulebooks/rulebook_text.txt:lines 3538–3548, 4470–4585, 4712–4776",
            ),
            assertion(
                bga_assertion_id,
                BGA_EXPLORATION_SOURCE_ID,
                f"EXPLORATION_CARDS_DATA.{definition['bgaKey']}",
                ["sourceVariants"],
                source["bgaOccurrence"]["sourceBlockText"],
                f"docs/rules/semantics/exploration-source-index.json:{source['explorationOccurrenceId']}.bgaOccurrence",
            ),
        ]
        assertions[0]["textKind"] = "verbatim"
        assertions[2]["textKind"] = "verbatim"

        faq_assertion_ids = {}
        for faq in source["faqOccurrences"]:
            faq_id = faq["sourceUnitId"]
            assertion_id = f"SA-EXP-{code}-FAQ-{faq_id.rsplit('-', 1)[-1]}"
            faq_assertion = assertion(
                assertion_id,
                "SRC-FAQ",
                f"General rules / {faq_id}",
                ["targets", "operations", "partialResolution", "sourceVariants"],
                faq["printedText"],
                f"docs/rules/source-extraction/faq-v1.2-source-extraction.json:{faq_id}",
            )
            faq_assertion["textKind"] = "verbatim"
            assertions.append(faq_assertion)
            faq_assertion_ids[faq_id] = assertion_id

        official_assertion_ids = []
        for index, official in enumerate(source["officialOccurrences"], 1):
            assertion_id = f"SA-EXP-{code}-OFFICIAL-{index:02d}"
            assertions.append(
                assertion(
                    assertion_id,
                    "SRC-RULEBOOK",
                    official["locator"],
                    ["operations", "targets", "sourceVariants"],
                    official["visibleText"],
                    f"docs/rules/source-extraction/rulebook-visual-obligations.json:{official['occurrenceId']}",
                )
            )
            official_assertion_ids.append(assertion_id)

        marker_assertion_id = None
        diagram = definition["diagram"]
        if diagram["roomIcons"]:
            marker_assertion_id = f"SA-EXP-{code}-MARKERS"
            assertions.append(
                assertion(
                    marker_assertion_id,
                    "SRC-RULEBOOK",
                    "printed pages 22–24 / Malfunction, Fire, and Exploration marker limits",
                    ["operations", "partialResolution", "targets"],
                    "A Room holds at most one Malfunction and one Fire. If Malfunction supply is empty, place Fire in the Room if possible; if required Fire supply is empty, the Facility is destroyed.",
                    "docs/rulebooks/rulebook_text.txt:lines 4368–4375, 4414–4426, 4436–4468",
                )
            )

        adult_assertion_id = None
        if definition.get("adultCount"):
            adult_assertion_id = f"SA-EXP-{code}-ADULT-LIMITS"
            assertions.append(
                assertion(
                    adult_assertion_id,
                    "SRC-RULEBOOK",
                    "printed pages 21, 25, and 30 / Corridor Noise, capacity, and finite Intruder models",
                    ["operations", "partialResolution", "targets"],
                    "Discard Noise when an Intruder enters its Corridor; place as many requested Adults as model supply and the six-equivalent Corridor capacity allow, then ignore excess.",
                    "docs/rulebooks/rulebook_text.txt:lines 4141–4149, 4222–4239, 5190–5198",
                )
            )

        participants = [
            participant("P-RULES", "rules-system"),
            participant("P-EXPLORER", "actor", "tax.entity.agent.character"),
        ]
        information = [
            {
                "informationId": f"I-EXP-{code}-PUBLIC",
                "subjectRef": "drawn untitled Exploration occurrence, full diagram, source units, target slots, and resolution",
                "audience": "public",
                "revealTrigger": "draw and resolution",
                "secrecy": "remaining Exploration-deck order stays unrevealed",
            }
        ]
        terms = [
            "term.exploration-card",
            "term.exploration-sequence",
            "term.room",
            "term.corridor",
            "term.moving-cautiously",
            "icon.character",
            "icon.secure",
        ]
        taxa = [
            "tax.entity.component.card.exploration",
            "tax.process.sequence.exploration",
            "tax.entity.spatial.room",
            "tax.entity.spatial.room-slot",
            "tax.entity.spatial.corridor",
            "tax.process.action.move-cautiously",
            "tax.entity.component.token.secure",
        ]
        targets = [
            _target(f"T-EXP-{code}-ROOM-SLOT", ["tax.entity.spatial.room-slot"], minimum=1, maximum=1),
            _target(f"T-EXP-{code}-NEW-ROOM", ["tax.entity.spatial.room"], minimum=0, maximum=1),
            _target(f"T-EXP-{code}-DIAGRAM-SLOTS", ["tax.entity.spatial.corridor"], mode="unresolved-order", minimum=0, maximum=len(diagram["corridorSlots"])),
        ]
        if definition.get("closeDoors"):
            targets.append(_target(f"T-EXP-{code}-DOORS", ["tax.entity.spatial.door"]))
            terms.extend(["term.door", "term.closed"])
            taxa.extend(["tax.entity.spatial.door", "tax.state.closed"])
        if definition.get("adultCount"):
            targets.append(_target(f"T-EXP-{code}-ENTRANCE-CORRIDOR", ["tax.entity.spatial.corridor"], minimum=1, maximum=1))
            terms.extend(["term.adult", "icon.noise"])
            taxa.extend(["tax.entity.agent.intruder.adult", "tax.entity.component.marker.noise"])
        if diagram["noiseSlots"]:
            terms.append("icon.noise")
            taxa.append("tax.entity.component.marker.noise")
        if "malfunction" in diagram["roomIcons"]:
            terms.append("icon.malfunction")
            taxa.append("tax.entity.component.marker.malfunction")
        if "fire" in diagram["roomIcons"]:
            terms.append("icon.fire")
            taxa.append("tax.entity.component.marker.fire")
        if any("[noiseDieHazard]" in sentence["exactText"] for sentence in definition["sentences"]):
            terms.append("icon.noiseDieHazard")
        if any("Noise roll" in sentence["exactText"] for sentence in definition["sentences"]):
            terms.append("term.noise-roll")
            taxa.append("tax.process.sequence.noise-roll")

        source_unit_by_section = {}
        for unit in source["sourceUnits"]:
            source_unit_by_section.setdefault(unit["section"], []).append(unit)
        placement_unit = source_unit_by_section["placement"][0]["unitId"]
        diagram_unit = source_unit_by_section["diagram"][0]["unitId"]
        reminder_unit = source_unit_by_section["reminder"][0]["unitId"]
        entrance_units = [unit["unitId"] for unit in source_unit_by_section.get("entrance", [])]
        lifecycle_unit = source_unit_by_section["lifecycle"][0]["unitId"]

        ops = []

        def add(unit_id, unit_kind, op_type, modality, subject, obj, *, source_ids=None, conditions=None, target_ref=None, transition=None, invoke=None, repeat=None, notes=None):
            step = len(ops) + 1
            op = operation(
                f"S{step:02d}",
                step,
                op_type,
                modality,
                subject,
                obj,
                source_ids or [scan_assertion_id, procedure_assertion_id],
                conditions=conditions,
                target_ref=target_ref,
                transition=transition,
                invoke=invoke,
                repeat=repeat,
                notes=notes,
            )
            op["sourceUnitId"] = unit_id
            op["sourceUnitKind"] = unit_kind
            ops.append(op)
            return op

        room_object = (
            "one random A/B/C Room matching the destination Section; use one random ? Room if that type is exhausted"
            if definition["roomType"] == "ABC"
            else "one random ? Room"
        )
        add(
            placement_unit,
            "printed-sentence",
            "place-component",
            "if-able",
            "P-RULES",
            room_object,
            target_ref=f"T-EXP-{code}-ROOM-SLOT",
            repeat={"randomWithoutInspection": True, "finiteSupply": True, "requiredRoomType": definition["roomType"]},
            notes="If neither the required Room type nor its source-defined ? fallback is available, dependent setup/movement operations have no placed Room target.",
        )
        add(
            diagram_unit,
            "source-local-diagram",
            "place-component",
            "if-able",
            "P-RULES",
            "one random Corridor in each eligible source-local diagram slot",
            conditions=["new Room was placed"],
            target_ref=f"T-EXP-{code}-DIAGRAM-SLOTS",
            repeat={
                "sourceLocalSlots": [SLOT_LABELS[slot] for slot in diagram["corridorSlots"]],
                "slotIndices": diagram["corridorSlots"],
                "randomWithoutInspection": True,
                "assignmentOrder": "SEM-Q-011 unresolved",
                "finiteSupply": True,
                "omitSlotWhen": ["outside Facility border", "would connect to an already placed Room"],
            },
            notes="No title, folder name, BGA number, or CardID modulo selects a slot. The source does not assign random draws or scarce Corridors among multiple eligible slots.",
        )
        marker_sources = [scan_assertion_id, procedure_assertion_id] + ([marker_assertion_id] if marker_assertion_id else [])
        if diagram["roomIcons"]:
            add(
                diagram_unit,
                "source-local-diagram",
                "place-component",
                "if-able",
                "P-RULES",
                "all source-depicted markers in the new Room",
                source_ids=marker_sources,
                conditions=["new Room was placed"],
                target_ref=f"T-EXP-{code}-NEW-ROOM",
                repeat={
                    "roomMarkerOccurrences": diagram["roomIcons"],
                    "sourceOrder": "unordered within this source-local diagram unit",
                    "finiteSupply": True,
                },
            )
        if diagram["noiseSlots"]:
            add(
                diagram_unit,
                "source-local-diagram",
                "place-component",
                "if-able",
                "P-RULES",
                "source-depicted Noise markers in placed diagram Corridors",
                source_ids=[scan_assertion_id, procedure_assertion_id],
                conditions=["new Room was placed"],
                target_ref=f"T-EXP-{code}-DIAGRAM-SLOTS",
                repeat={
                    "noiseSlotIndices": diagram["noiseSlots"],
                    "noiseSlotLabels": [SLOT_LABELS[slot] for slot in diagram["noiseSlots"]],
                    "noiseRequiresPlacedCorridor": True,
                    "existingNoiseIsNotDuplicated": True,
                    "finiteSupply": True,
                    "multiSlotAllocationOrder": "SEM-Q-011 unresolved",
                },
            )
        if "malfunction" in diagram["roomIcons"]:
            add(
                diagram_unit,
                "source-local-diagram",
                "place-component",
                "if-able",
                "P-RULES",
                "1 Fire in the new Room as the Malfunction-supply fallback",
                source_ids=[scan_assertion_id, marker_assertion_id],
                conditions=["depicted Malfunction is required", "no Malfunction marker is available", "Fire placement is possible"],
                target_ref=f"T-EXP-{code}-NEW-ROOM",
            )
        if "fire" in diagram["roomIcons"] or "malfunction" in diagram["roomIcons"]:
            add(
                diagram_unit,
                "source-local-diagram",
                "invoke-process",
                "if-able",
                "P-RULES",
                "Facility destruction and endgame",
                source_ids=[scan_assertion_id, marker_assertion_id],
                conditions=["a required direct or Malfunction-fallback Fire marker cannot be placed because Fire supply is empty"],
                invoke="SEM-ENDGAME-001",
            )

        add(
            reminder_unit,
            "printed-sentence",
            "move-entity",
            "if-able",
            "P-EXPLORER",
            "newly placed Room",
            conditions=["new Room was placed", "caller uses standard Movement-based Exploration rather than explicitly exploring without Moving"],
            target_ref=f"T-EXP-{code}-NEW-ROOM",
        )
        add(
            reminder_unit,
            "printed-sentence",
            "place-component",
            "if-able",
            "P-RULES",
            "1 Secure token in the new Room",
            conditions=["explorer was Moving Cautiously", "new Room was placed", "Secure token is available"],
            target_ref=f"T-EXP-{code}-NEW-ROOM",
            notes="The exact TTS reminder preserves two source-local Secure glyph occurrences; current official wording says Moving Cautiously.",
        )

        for unit_id in entrance_units:
            sentence = next(unit for unit in source["sourceUnits"] if unit["unitId"] == unit_id)
            text = sentence["exactText"]
            entrance_guard = ["caller does not explicitly ignore Entrance Effects"]
            if "Close all" in text or "Close all doors" in text:
                source_ids = [scan_assertion_id, procedure_assertion_id, faq_assertion_ids["FQ-P02-U06"]]
                add(
                    unit_id,
                    "printed-sentence",
                    "invoke-process",
                    "must",
                    "P-RULES",
                    "close only Door slots touching the new Room; never Hibernatorium Doors through Exploration",
                    source_ids=source_ids,
                    conditions=entrance_guard,
                    target_ref=f"T-EXP-{code}-DOORS",
                    invoke="SEM-DOOR-001",
                    repeat={"scope": "all touching closable Door slots", "finiteDoorSupply": True, "allocationOrder": "SEM-Q-011 unresolved when supply is insufficient"},
                )
            elif "Adults" in text:
                source_ids = [scan_assertion_id, adult_assertion_id]
                add(
                    unit_id,
                    "printed-sentence",
                    "remove-component",
                    "if-able",
                    "P-RULES",
                    "existing Noise marker in the Corridor just passed through",
                    source_ids=source_ids,
                    conditions=[*entrance_guard, "the passed-through Corridor contains Noise"],
                    target_ref=f"T-EXP-{code}-ENTRANCE-CORRIDOR",
                )
                add(
                    unit_id,
                    "printed-sentence",
                    "place-component",
                    "if-able",
                    "P-RULES",
                    f"up to {definition['adultCount']} Adults in the Corridor just passed through",
                    source_ids=source_ids,
                    conditions=entrance_guard,
                    target_ref=f"T-EXP-{code}-ENTRANCE-CORRIDOR",
                    repeat={
                        "requested": definition["adultCount"],
                        "finiteModelSupply": True,
                        "corridorCapacityEquivalentLimit": 6,
                        "placeAsManyAsPossible": True,
                        "entryAttack": False,
                    },
                )
            elif "Noise roll" in text:
                add(
                    unit_id,
                    "printed-sentence",
                    "invoke-process",
                    "must",
                    "P-EXPLORER",
                    "one Entrance-effect Noise Roll",
                    conditions=entrance_guard,
                    invoke="SEM-NOISE-001",
                    notes="This printed Entrance roll is distinct evidence from the unresolved universal post-Movement accounting in SEM-Q-002.",
                )
            elif "[noiseDieHazard]" in text:
                add(
                    unit_id,
                    "printed-sentence",
                    "invoke-process",
                    "must",
                    "P-EXPLORER",
                    "one direct Hazard result",
                    conditions=entrance_guard,
                    invoke="SEM-NOISE-HAZARD-001",
                )
            else:
                raise AssertionError(f"unhandled Exploration Entrance sentence: {card_id} {text}")

        if definition.get("removeFromGame"):
            add(
                lifecycle_unit,
                "printed-sentence",
                "transition-zone",
                "must",
                "P-RULES",
                f"untitled Exploration occurrence {card_id}",
                source_ids=[scan_assertion_id, faq_assertion_ids["FQ-P02-U07"]],
                transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.removed-from-game"},
                notes="FAQ v1.2 places this lifecycle sentence outside the Entrance Effect; it still resolves when Entrance Effects are ignored.",
            )
        else:
            add(
                lifecycle_unit,
                "official-procedure-lifecycle",
                "transition-zone",
                "must",
                "P-RULES",
                f"untitled Exploration occurrence {card_id}",
                source_ids=[procedure_assertion_id],
                transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"},
            )

        variants = [
            {
                "variantId": f"SV-EXP-{code}-BGA",
                "sourceId": BGA_EXPLORATION_SOURCE_ID,
                "sourceAssertionId": bga_assertion_id,
                "difference": source["bgaOccurrence"]["variantDifference"],
                "resolution": "Retain the licensed structured occurrence as secondary evidence; exact TTS wording and applicable official/FAQ text remain independent and control by authority.",
            }
        ]
        for index, (official, assertion_id) in enumerate(zip(source["officialOccurrences"], official_assertion_ids), 1):
            variants.append(
                {
                    "variantId": f"SV-EXP-{code}-OFFICIAL-{index:02d}",
                    "sourceId": "SRC-RULEBOOK",
                    "sourceAssertionId": assertion_id,
                    "difference": official["variantDifference"],
                    "resolution": "The official-primary visible occurrence controls the matching current wording/visual procedure without rewriting the lower-authority TTS occurrence.",
                }
            )

        result = record(
            definition["ruleId"],
            f"Untitled Exploration occurrence {card_id}",
            "source-backed-with-open-question",
            "component-effect",
            "official-errata" if source["faqOccurrences"] else "official-primary",
            "open-alternatives",
            assertions,
            terms,
            taxa,
            [],
            timing(f"TW-EXP-{code}", "tax.process.sequence.exploration", "during", "when-this-exact-untitled-Exploration-occurrence-is-drawn"),
            participants,
            "must",
            [condition(f"C-EXP-{code}-OCCURRENCE", "predicate", [{"predicate": f"drawn occurrence identity is {source['explorationOccurrenceId']}"}], [scan_assertion_id])],
            [],
            information,
            [],
            targets,
            ops,
            {
                "policy": "source-conditional-steps",
                "unit": "sourceUnitId, one source-local diagram slot/occurrence, or one lifecycle transition",
                "onImpossible": "omit only source-defined invalid Corridors and dependent Noise; apply explicit finite-component fallbacks. Random/finite multi-slot assignment remains SEM-Q-011 with no default; lifecycle removal remains outside ignored Entrance Effects.",
            },
            {"kind": "instantaneous-exploration-occurrence-resolution"},
            {"policy": "one resolution per drawn source occurrence; removed occurrences do not enter the discard/reshuffle cycle"},
            [],
            ["SEM-Q-011"],
            variants,
        )
        records.append(result)

    return records
