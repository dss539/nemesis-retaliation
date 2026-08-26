from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path


BASE_ROBOT_DECK_GUID = "98925d"
ROBOT_MODEL_GUID = "cbf1f3"
ROBOT_STATE_TOKEN_GUID = "828c1d"
ROBOT_BACK_SOURCE_ID = "SRC-ROBOT-BACK"
ROBOT_BACK_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/game/robotDeck-155.jpg"
BGA_ROBOT_SOURCE_ID = "SRC-BGA-ROBOTS"
BGA_ROBOT_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"


def _sentence(sentence_id: str, option_id: str, exact_text: str) -> dict:
    return {"sentenceId": sentence_id, "optionId": option_id, "exactText": exact_text}


ROBOT_DEFINITIONS = {
    506400: {
        "sourceId": "SRC-ROBOT-506400",
        "ttsGuid": "cd319d",
        "objectDeckNums": ["5064"],
        "title": "SERVER ROBOT",
        "bgaKey": "ServerRobot",
        "ruleId": "SEM-ROBOT-SERVER-001",
        "sentences": [
            _sentence("RB506400-O1-S01", "O1", "Move the [robot] up to 3 times."),
            _sentence("RB506400-O2-S01", "O2", "If the [robot] is in a [computer] Room, use\nthe Room (even with a [malfunction])."),
        ],
        "officialOccurrences": [
            {
                "sourceOccurrenceId": "RB-P03-V01-ROBOT-SERVER",
                "parentOccurrenceId": "RB-P03-V01",
                "locator": "unprinted PDF page 3 / lower Robot-card row / rulebook_text lines 140–148",
                "visibleTitle": "SERVER ROBOT",
                "pixelMatch": {"renderDpi": 300, "ratioMatches": 115, "ransacInliers": 62, "inlierRatio": 0.5391, "medianReprojectionError": 0.5666, "bbox": [1063.81, 2798.88, 1268.62, 3084.55]},
            }
        ],
        "identityRefs": [],
        "variantDifference": "The licensed record normalizes line wrapping and placeholder notation; the exact scan and official visible occurrence remain independent.",
    },
    510800: {
        "sourceId": "SRC-ROBOT-510800",
        "ttsGuid": "6a5c53",
        "objectDeckNums": ["5108"],
        "title": "SECURING ROBOT",
        "bgaKey": "SecuringRobot",
        "ruleId": "SEM-ROBOT-SECURING-001",
        "sentences": [
            _sentence("RB510800-O1-S01", "O1", "Move the [robot] up to 3 times."),
            _sentence("RB510800-O2-S01", "O2", "Open or Close 1 Door\naccessible to the [robot]."),
            _sentence("RB510800-O3-S01", "O3", "Place 2 [secure] in a Room\nwith the [robot]."),
        ],
        "identityRefs": ["NI-0431"],
        "variantDifference": "The licensed occurrence corroborates all three option strings with normalized placeholders and line grouping; it remains a separate secondary occurrence.",
    },
    529300: {
        "sourceId": "SRC-ROBOT-529300",
        "ttsGuid": "5f4876",
        "objectDeckNums": ["5293"],
        "title": "EXPLORATION ROBOT",
        "bgaKey": "ExplorationRobot",
        "ruleId": "SEM-ROBOT-EXPLORATION-001",
        "sentences": [
            _sentence("RB529300-O1-S01", "O1", "Move the [robot] up to 2 times."),
            _sentence("RB529300-O2-S01", "O2", "Move the [robot] through\nan Unexplored Corridor\nand resolve an Exploration\nSequence."),
            _sentence("RB529300-O2-S02", "O2", "Do not resolve\nthe Entrance effect."),
        ],
        "identityRefs": [],
        "variantDifference": "The licensed occurrence normalizes line grouping and placeholder notation while retaining the same two alternatives; it remains secondary.",
    },
    529400: {
        "sourceId": "SRC-ROBOT-529400",
        "ttsGuid": "c5b268",
        "objectDeckNums": ["5107"],
        "title": "TECHNICAL ROBOT",
        "bgaKey": "TechnicalRobot",
        "ruleId": "SEM-ROBOT-TECHNICAL-001",
        "sentences": [
            _sentence("RB529400-O1-S01", "O1", "Move the [robot] up to 2 times."),
            _sentence("RB529400-O2-S01", "O2", "Discard a [malfunction] or a [fire]\nfrom the Room with the [robot]."),
        ],
        "officialOccurrences": [
            {
                "sourceOccurrenceId": "RB-P03-V01-ROBOT-TECHNICAL",
                "parentOccurrenceId": "RB-P03-V01",
                "locator": "unprinted PDF page 3 / lower Robot-card row / rulebook_text lines 99–111",
                "visibleTitle": "TECHNICAL ROBOT",
                "pixelMatch": {"renderDpi": 300, "ratioMatches": 134, "ransacInliers": 46, "inlierRatio": 0.3433, "medianReprojectionError": 0.5303, "bbox": [1201.81, 2750.24, 1383.27, 3024.36]},
            }
        ],
        "identityRefs": [],
        "variantDifference": "The licensed record normalizes line wrapping and placeholders; the scan and official visible occurrence remain independently traceable.",
    },
    529500: {
        "sourceId": "SRC-ROBOT-529500",
        "ttsGuid": "90c510",
        "objectDeckNums": ["5109"],
        "title": "MEDICAL ROBOT",
        "bgaKey": "MedicalRobot",
        "ruleId": "SEM-ROBOT-MEDICAL-001",
        "sentences": [
            _sentence("RB529500-O1-S01", "O1", "Move the [robot] up to 2 times."),
            _sentence("RB529500-O2-S01", "O2", "A [character] of your choice\nin a Room with the [robot]\ndiscards 1 Serious Wound\nor restores 2 [characterHealth]."),
        ],
        "identityRefs": [],
        "variantDifference": "The licensed occurrence normalizes the exact line grouping and icon placeholders; the scan remains an independent component occurrence.",
    },
    529600: {
        "sourceId": "SRC-ROBOT-529600",
        "ttsGuid": "fbe18a",
        "objectDeckNums": ["5110"],
        "title": "MILITARY ROBOT",
        "bgaKey": "MilitaryRobot",
        "ruleId": "SEM-ROBOT-MILITARY-001",
        "sentences": [
            _sentence("RB529600-O1-S01", "O1", "Move the [robot] once."),
            _sentence("RB529600-O2-S01", "O2", "Choose a Corridor adjacent\nto the [robot] and roll a Burst\ndie."),
            _sentence("RB529600-O2-S02", "O2", "Deal Hits equal to the\nresult in that Corridor."),
            _sentence("RB529600-O2-S03", "O2", "[burstDieAdditionalEffects]: Place a [malfunction] on the [robot]."),
        ],
        "identityRefs": ["NI-0300"],
        "variantDifference": "The licensed Military Robot occurrence omits the final period after its Robot placeholder; the source scan retains that punctuation and controls over the lower-authority variant.",
    },
}

ROBOT_RULE_IDS = [ROBOT_DEFINITIONS[card_id]["ruleId"] for card_id in sorted(ROBOT_DEFINITIONS)]

RULEBOOK_TEXT_OCCURRENCES = [
    {"occurrenceId": "RB-ROBOT-SETUP-01", "section": "setup", "locator": "printed page 8 / lines 2421–2426", "sourceText": "Until the Hibernatorium is discovered, the Robot cannot be Activated."},
    {"occurrenceId": "RB-ROBOT-SETUP-02", "section": "setup", "locator": "printed page 8 / lines 2446–2448", "sourceText": "Shuffle all 6 Robot cards, draw 1 without looking, place it face down on the Robot slot, and leave the rest unseen in the box."},
    {"occurrenceId": "RB-ROBOT-SETUP-03", "section": "setup", "locator": "printed page 8 / lines 2450–2455", "sourceText": "Place 1 full Ammo token and 1 Oxygen token on the slots next to the Robot card."},
    {"occurrenceId": "RB-ROBOT-SETUP-04", "section": "setup", "locator": "printed page 8 / line 2456", "sourceText": "Assemble the Robot model and place it on the Hibernatorium."},
    {"occurrenceId": "RB-ROBOT-ACTION-01", "section": "activation", "locator": "printed page 12 / lines 2876–2895 and RB-P12-V02", "sourceText": "Activate the Robot is a 1-Action-card Basic Action carrying the Not In Combat restriction."},
    {"occurrenceId": "RB-ROBOT-EFFECT-01", "section": "effect-selection", "locator": "printed page 14 / lines 3187–3198", "sourceText": "A chosen effect must be entirely resolvable; cards may provide more than one effect to choose from."},
    {"occurrenceId": "RB-ROBOT-LOCAL-01", "section": "targeting", "locator": "printed page 17 / lines 3537–3542", "sourceText": "An effect with no clearly specified target is local to the Room of the Character performing it."},
    {"occurrenceId": "RB-ROBOT-COMPONENT-LIMIT-01", "section": "finite-supply", "locator": "printed page 17 / lines 3543–3548", "sourceText": "Components are finite; where no special exhaustion rule exists, unavailable component use does nothing."},
    {"occurrenceId": "RB-ROBOT-WOUND-01", "section": "medical", "locator": "printed page 18 / lines 3797–3813", "sourceText": "The affected Character chooses which Serious Wound to discard and a player may restore fewer Health points than stated."},
    {"occurrenceId": "RB-ROBOT-MALFUNCTION-01", "section": "malfunction", "locator": "printed page 22 / lines 4383–4391", "sourceText": "A malfunctioned Robot cannot be used and has no text/icons; effects only requiring a Robot remain available; repeated Robot Malfunction placement is ignored."},
    {"occurrenceId": "RB-ROBOT-MALFUNCTION-02", "section": "malfunction-removal", "locator": "printed page 22 / lines 4392–4395", "sourceText": "Discard-Malfunction effects may remove a marker from the Character's Room or an Item/Robot there unless stated otherwise."},
    {"occurrenceId": "RB-ROBOT-SECURE-01", "section": "secure", "locator": "printed page 23 / lines 4396–4405", "sourceText": "A Room holds at most 3 Secure tokens and cannot be Secured while it contains an Intruder."},
    {"occurrenceId": "RB-ROBOT-MALFUNCTION-LIMIT-01", "section": "finite-supply", "locator": "printed page 23 / lines 4414–4468", "sourceText": "If Malfunction supply is empty, place Fire in the Room if possible; if required Fire cannot be placed because Fire supply is empty, destroy the Facility."},
    {"occurrenceId": "RB-ROBOT-INTRO-01", "section": "identity", "locator": "printed page 37 / lines 5982–5992", "sourceText": "One randomly selected face-down Robot starts in the Hibernatorium and acts only when assigned Actions by Characters."},
    {"occurrenceId": "RB-ROBOT-REVEAL-01", "section": "reveal", "locator": "printed page 37 / lines 5993–5994", "sourceText": "Reveal the Robot card when any Room is connected to the Hibernatorium for the first time; the Robot can then be Activated."},
    {"occurrenceId": "RB-ROBOT-INTRUDER-01", "section": "interaction", "locator": "printed page 37 / lines 5995–5996", "sourceText": "Intruders completely ignore the Robot in all cases."},
    {"occurrenceId": "RB-ROBOT-FAMILY-01", "section": "identity", "locator": "printed page 37 / lines 5997–6000", "sourceText": "There are 6 different Robot cards and only 1 appears in a game; each has a unique effect."},
    {"occurrenceId": "RB-ROBOT-ACTIVATE-LOCAL-01", "section": "activation", "locator": "printed page 37 / lines 6000–6004", "sourceText": "Activate locally by discarding 1 Action card while in the Room with the Robot."},
    {"occurrenceId": "RB-ROBOT-ACTIVATE-REMOTE-01", "section": "activation", "locator": "printed page 37 / lines 6005–6008", "sourceText": "Activate remotely from a Computer Room by discarding 1 additional Action card."},
    {"occurrenceId": "RB-ROBOT-DATA-01", "section": "activation", "locator": "printed page 37 / lines 6009–6012", "sourceText": "A Character with a Data token may Activate remotely without the additional card."},
    {"occurrenceId": "RB-ROBOT-MALFUNCTION-P37-01", "section": "malfunction", "locator": "printed page 37 / lines 6015–6022", "sourceText": "A Robot with Malfunction has no Action and all game effects mentioning it are unavailable; its Tactical Gear remains usable and an adjacent Character may remove the marker."},
    {"occurrenceId": "RB-ROBOT-MOVE-01", "section": "movement", "locator": "printed page 37 / lines 6023–6028", "sourceText": "Robot movement occurs only from player Actions, one neighboring Room at a time; it ignores Intruders but not Closed Doors."},
    {"occurrenceId": "RB-ROBOT-MOVE-02", "section": "movement", "locator": "printed page 37 / lines 6029–6030", "sourceText": "The Robot cannot normally traverse an Unexplored Corridor and never makes a Noise roll."},
    {"occurrenceId": "RB-ROBOT-MOVE-03", "section": "movement", "locator": "printed page 37 / lines 6031–6032", "sourceText": "Exploration Robot is the only exception: it may Explore a new Room and could make a Noise roll."},
    {"occurrenceId": "RB-ROBOT-GEAR-01", "section": "tactical-gear", "locator": "printed page 37 / lines 6033–6037", "sourceText": "The Robot has its own Tactical Gear slots and starts with 1 Ammo and 1 Oxygen token."},
    {"occurrenceId": "RB-ROBOT-GEAR-02", "section": "tactical-gear", "locator": "printed page 37 / lines 6038–6041", "sourceText": "A co-located Character using Tactical Gear may use Robot tokens and move tokens between Character and Robot slots."},
    {"occurrenceId": "RB-ROBOT-BURST-01", "section": "military", "locator": "printed page 33 / lines 5508–5537", "sourceText": "The player allocates Burst-die Hits among Intruders under type limits, loses leftovers, then resolves any additional-effects symbol; 4 and additional effects share one die face."},
]

OFFICIAL_VISUAL_OCCURRENCES = [
    {"occurrenceId": "RB-P03-V01", "aspect": "6-card family count and two exact visible Robot faces"},
    {"occurrenceId": "RB-P05-V01", "aspect": "finite 9 Fire, 14 Malfunction, 20 Secure, and 20-each Tactical Gear supplies"},
    {"occurrenceId": "RB-P05-V02", "aspect": "one Robot model"},
    {"occurrenceId": "RB-P08-V03", "aspect": "setup callouts A8 and A9 for Robot card and starting gear"},
    {"occurrenceId": "RB-P09-V01", "aspect": "setup callout A10 for Robot model"},
    {"occurrenceId": "RB-P12-V02", "aspect": "Activate Robot cost group and Not In Combat association"},
    {"occurrenceId": "RB-P37-V01", "aspect": "Robot model and Robot/Computer/Data/Ammo/Oxygen visual associations"},
    {"occurrenceId": "RB-P40-V02", "aspect": "authoritative Robot icon glossary occurrence"},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_js_literal(body: str, field: str):
    match = re.search(rf"^    {field}: ", body, re.M)
    if not match:
        raise AssertionError(f"missing Robot BGA field {field}")
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
    elif opening == "[":
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
    raise AssertionError(f"unterminated Robot BGA field {field}")


def _parse_bga_robots(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const ROBOT_CARDS_DATA = \{\n(.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError("ROBOT_CARDS_DATA block not found")
    records = {}
    for row in re.finditer(r"^  ([A-Za-z0-9]+): \{\n(.*?)^  \},$", match.group(1), re.M | re.S):
        key, body = row.groups()
        records[key] = {
            "name": _parse_js_literal(body, "name"),
            "desc": _parse_js_literal(body, "desc"),
            "color": _parse_js_literal(body, "color"),
            "sourceBlockText": row.group(0),
        }
    if set(records) != {definition["bgaKey"] for definition in ROBOT_DEFINITIONS.values()}:
        raise AssertionError("licensed Robot table identity set changed")
    return records


def _panels(card_id: int, title: str, body: str, first_sentence_end: int) -> list[dict]:
    separator_start = body.find("OR", first_sentence_end)
    if separator_start < 0:
        raise AssertionError(f"Robot panel separator missing: {card_id}")
    return [
        {"panelId": "P1", "readingOrder": 1, "role": "title", "operative": False, "exactText": title, "bodyStart": None, "bodyEnd": None},
        {"panelId": "P2", "readingOrder": 2, "role": "artwork", "operative": False, "exactText": "", "bodyStart": None, "bodyEnd": None},
        {"panelId": "P3", "readingOrder": 3, "role": "first-option-rules-plaque", "operative": True, "exactText": body[:first_sentence_end], "bodyStart": 0, "bodyEnd": first_sentence_end},
        {"panelId": "P4", "readingOrder": 4, "role": "remaining-options-rules-field", "operative": True, "exactText": body[separator_start:], "bodyStart": separator_start, "bodyEnd": len(body)},
    ]


def _icon_occurrences(card_id: int, body: str, first_sentence_end: int) -> list[dict]:
    rows = []
    for sequence, match in enumerate(re.finditer(r"\[([A-Za-z0-9]+)\]", body), 1):
        token = match.group(1)
        rows.append(
            {
                "occurrenceId": f"RBT-{card_id}-I{sequence:02d}",
                "sequence": sequence,
                "sourceToken": token,
                "semanticReferenceId": f"icon.{token}",
                "panelId": "P3" if match.start() < first_sentence_end else "P4",
                "start": match.start(),
                "end": match.end(),
                "location": body[max(0, match.start() - 18):min(len(body), match.end() + 18)].replace("\n", " "),
            }
        )
    return rows


def build_robot_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / "assets/tts-mod/extract/card-text-corpus.json").read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    provenance = json.loads((repo / "assets/tts-mod/extract/card-provenance-inventory.json").read_text(encoding="utf-8"))
    roles = json.loads((repo / "assets/tts-mod/extract/v2/lua_roles.json").read_text(encoding="utf-8"))
    objects = json.loads((repo / "assets/tts-mod/extract/v2/objects.json").read_text(encoding="utf-8"))
    classification = json.loads((repo / "assets/tts-mod/extract/v2/classification.json").read_text(encoding="utf-8"))
    secondary = json.loads((repo / "docs/rules/source-extraction/secondary-evidence-index.json").read_text(encoding="utf-8"))
    visuals = json.loads((repo / "docs/rules/source-extraction/rulebook-visual-obligations.json").read_text(encoding="utf-8"))
    faq = json.loads((repo / "docs/rules/source-extraction/faq-v1.2-source-extraction.json").read_text(encoding="utf-8"))
    backlog = json.loads((repo / "docs/rules/semantics/backlog.json").read_text(encoding="utf-8"))
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    bga = _parse_bga_robots(repo / BGA_ROBOT_PATH)

    role = next(row for row in roles if row.get("role") == "robotDeck" and row.get("guid") == BASE_ROBOT_DECK_GUID)
    expected_deck_nums = ["5064", "5108", "5293", "5294", "5295", "5296"]
    if role.get("deck_nums") != expected_deck_nums or role.get("n_urls") != 7:
        raise AssertionError("base Robot root role/deck numbers changed")
    card_ids = [int(value) * 100 for value in role["deck_nums"]]
    if card_ids != sorted(ROBOT_DEFINITIONS):
        raise AssertionError("base Robot root role does not close against definitions")
    deck_object = next(row for row in objects if row.get("guid") == BASE_ROBOT_DECK_GUID)
    if deck_object.get("parent") != [] or deck_object.get("type") != "DeckCustom":
        raise AssertionError("base Robot deck is not the root DeckCustom")

    table = next(row for row in secondary["licensedDigital"]["structuredIndex"]["tables"] if row["name"] == "ROBOT_CARDS_DATA")
    if table.get("count") != 6 or set(table.get("keys") or []) != set(bga):
        raise AssertionError("licensed Robot evidence-index closure changed")

    provenance_by_card = {}
    back_row = None
    for provenance_row in provenance:
        for obj in provenance_row.get("objects", []):
            if obj.get("key") == "BackURL" and obj.get("guid") == BASE_ROBOT_DECK_GUID:
                if back_row is not None and back_row is not provenance_row:
                    raise AssertionError("multiple root Robot BackURL provenance rows")
                back_row = provenance_row
            if obj.get("key") != "FaceURL" or obj.get("type") != "CardCustom" or not obj.get("cardId"):
                continue
            if ["DeckCustom", BASE_ROBOT_DECK_GUID, ""] not in (obj.get("parent") or []):
                continue
            card_id = int(obj["cardId"])
            if card_id in ROBOT_DEFINITIONS:
                provenance_by_card.setdefault(card_id, []).append((provenance_row, obj))
    if set(provenance_by_card) != set(ROBOT_DEFINITIONS) or any(len(rows) != 1 for rows in provenance_by_card.values()) or back_row is None:
        raise AssertionError("base Robot FaceURL/BackURL provenance closure failed")

    visual_by_id = {unit["occurrenceId"]: unit for page in visuals["pages"] for unit in page.get("visualUnits", [])}
    required_visual_ids = [row["occurrenceId"] for row in OFFICIAL_VISUAL_OCCURRENCES]
    if any(occurrence_id not in visual_by_id for occurrence_id in required_visual_ids):
        raise AssertionError("Robot official visual occurrence missing")
    faq_by_id = {unit["sourceUnitId"]: unit for page in faq["pages"] for unit in page.get("units", [])}
    if faq_by_id["FQ-P02-U17"]["applicability"] != "base-game" or any(faq_by_id[qid]["applicability"] != "expansion-neoflesh" for qid in ("FQ-P03-U15", "FQ-P03-U17")):
        raise AssertionError("Robot FAQ applicability boundary changed")

    rows = []
    for card_id in card_ids:
        definition = ROBOT_DEFINITIONS[card_id]
        provenance_row, obj = provenance_by_card[card_id][0]
        source_path = "assets/tts-mod/extract/v2-dl/tree/" + provenance_row["file"]
        source_file = repo / source_path
        source_sha = _sha(source_file)
        corpus_row = corpus_by_path.get(source_path) or {}
        if source_sha != corpus_row.get("sourceSha256") or not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"}:
            raise AssertionError(f"Robot corpus/hash readiness drift: {card_id}")
        if obj.get("guid") != definition["ttsGuid"] or int(obj.get("cardId", 0)) != card_id:
            raise AssertionError(f"Robot CardID/GUID crosswalk drift: {card_id}")
        object_row = next(row for row in objects if row.get("guid") == definition["ttsGuid"])
        if object_row.get("deck_nums") != definition["objectDeckNums"]:
            raise AssertionError(f"Robot child object deck-number drift: {card_id}")
        body = corpus_row["printedData"]["body"]
        visible_title = (corpus_row.get("printedData") or {}).get("title")
        if not visible_title:
            evidence_path = (corpus_row.get("evidence") or {}).get("resultPath")
            if not isinstance(evidence_path, str) or not evidence_path:
                raise AssertionError(f"Robot title evidence path missing: {card_id}")
            evidence = json.loads((repo / evidence_path).read_text(encoding="utf-8"))
            visible_title = (evidence.get("parsed") or {}).get("title")
        if not isinstance(visible_title, str) or visible_title != definition["title"]:
            raise AssertionError(f"Robot title projection drift: {card_id}")

        sentence_rows = []
        cursor = 0
        for sequence, sentence in enumerate(definition["sentences"], 1):
            start = body.find(sentence["exactText"], cursor)
            if start < 0:
                raise AssertionError(f"Robot sentence boundary drift: {card_id} {sentence['sentenceId']}")
            end = start + len(sentence["exactText"])
            sentence_rows.append({**sentence, "sequence": sequence, "panelId": "P3" if sequence == 1 else "P4", "start": start, "end": end})
            cursor = end
        first_sentence_end = sentence_rows[0]["end"]
        panels = _panels(card_id, visible_title, body, first_sentence_end)
        icon_rows = _icon_occurrences(card_id, body, first_sentence_end)
        bga_row = bga[definition["bgaKey"]]
        if bga_row["name"].upper() != visible_title:
            raise AssertionError(f"Robot BGA explicit crosswalk title drift: {card_id}")
        backlog_id = "CARD:" + source_sha[:16]
        backlog_row = backlog_by_id.get(backlog_id)
        if not backlog_row or backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != source_sha:
            raise AssertionError(f"Robot backlog source tuple drift: {card_id}")

        official_occurrences = []
        for occurrence in definition.get("officialOccurrences", []):
            parent = visual_by_id[occurrence["parentOccurrenceId"]]
            official_occurrences.append(
                {
                    **occurrence,
                    "sourceId": "SRC-RULEBOOK",
                    "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
                    "sourceSha256": _sha(repo / "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"),
                    "visibleText": body,
                    "parentVisualType": parent["type"],
                    "parentBbox160Dpi": parent["bbox"],
                    "variantDifference": "A deterministic feature match establishes this exact face as a scaled official page-3 occurrence. Preserve it independently even where its visible wording matches the TTS scan.",
                }
            )

        rows.append(
            {
                "robotOccurrenceId": f"TTS-ROBOT-{card_id}-FACE",
                "ttsRole": "robotDeck",
                "ttsDeckGuid": BASE_ROBOT_DECK_GUID,
                "ttsDeckType": "DeckCustom",
                "ttsRootDeckNumber": str(card_id // 100),
                "ttsCardGuid": obj["guid"],
                "ttsCardId": card_id,
                "ttsChildObjectDeckNums": object_row["deck_nums"],
                "sourceSelector": {
                    "key": "FaceURL",
                    "objectType": "CardCustom",
                    "cardId": card_id,
                    "guid": obj["guid"],
                    "parentDeckGuid": BASE_ROBOT_DECK_GUID,
                    "url": provenance_row["url"],
                    "sideRole": "operative-face",
                    "selectorStatus": "exact-composite-card-reference",
                    "singularUrlSelector": False,
                    "generatedSpriteSheetCell": False,
                    "selectorGap": None,
                },
                "sourceId": definition["sourceId"],
                "sourcePath": source_path,
                "sourceSha256": source_sha,
                "sourceAuthority": "source-bound-component-scan",
                "sourceVersion": f"TTS base Robot face / root deck {BASE_ROBOT_DECK_GUID} / CardID {card_id}",
                "corpusEvidencePath": "assets/tts-mod/extract/card-text-corpus.json",
                "provenanceEvidencePath": "assets/tts-mod/extract/card-provenance-inventory.json",
                "visionEvidencePath": "assets/tts-mod/extract/selected-card-text-evidence.json" if corpus_row["extractionState"] == "draft-full" else (corpus_row.get("evidence") or {}).get("resultPath"),
                "printedTitle": visible_title,
                "printedBody": body,
                "extractionState": corpus_row["extractionState"],
                "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
                "panels": panels,
                "sentences": sentence_rows,
                "actionOptions": [
                    {"optionId": option_id, "sequence": index, "sentenceIds": [sentence["sentenceId"] for sentence in sentence_rows if sentence["optionId"] == option_id]}
                    for index, option_id in enumerate(dict.fromkeys(sentence["optionId"] for sentence in sentence_rows), 1)
                ],
                "iconOccurrences": icon_rows,
                "cardStateRoles": {"initial": "face-down-unrevealed", "afterRevealTrigger": "face-up-revealed", "sharedBackSourceId": ROBOT_BACK_SOURCE_ID, "separateRulesFaceOnBack": False},
                "semanticRuleId": definition["ruleId"],
                "backlogUnitId": backlog_id,
                "bgaOccurrence": {
                    "sourceId": BGA_ROBOT_SOURCE_ID,
                    "sourcePath": BGA_ROBOT_PATH,
                    "sourceSha256": _sha(repo / BGA_ROBOT_PATH),
                    "sourceVersion": "licensed BGA immutable build 260622-1220 / ROBOT_CARDS_DATA",
                    "table": "ROBOT_CARDS_DATA",
                    "key": definition["bgaKey"],
                    **bga_row,
                    "variantDifference": definition["variantDifference"],
                },
                "officialOccurrences": official_occurrences,
                "joinEvidence": {
                    "identityJoin": "explicit occurrence crosswalk",
                    "titleOnlyJoin": False,
                    "basis": [
                        "root base Robot Lua role and exact root deck number",
                        "exact full CardID, child GUID, FaceURL, and parent DeckCustom GUID",
                        "closed-corpus source path and live SHA-256",
                        "ordered panel, option, sentence, and icon occurrence projection",
                        "explicit licensed ROBOT_CARDS_DATA key and exact ordered desc array",
                    ],
                },
            }
        )

    back_path = repo / ROBOT_BACK_PATH
    back_sha = _sha(back_path)
    back_corpus = corpus_by_path[ROBOT_BACK_PATH]
    back_objects = [obj for obj in back_row["objects"] if obj.get("key") == "BackURL"]
    base_back_selectors = [obj for obj in back_objects if obj.get("guid") == BASE_ROBOT_DECK_GUID or ["DeckCustom", BASE_ROBOT_DECK_GUID, ""] in (obj.get("parent") or [])]
    prototype_back_selectors = [obj for obj in back_objects if any(parent[1] in {"450d09", "905230"} for parent in obj.get("parent") or [])]
    if back_sha != back_corpus.get("sourceSha256") or back_corpus.get("rulesTextPresent") or len(base_back_selectors) != 7 or len(prototype_back_selectors) != 2:
        raise AssertionError("Robot shared-back/base/prototype reference closure drift")

    model_object = next(row for row in objects if row.get("guid") == ROBOT_MODEL_GUID)
    state_token_object = next(row for row in objects if row.get("guid") == ROBOT_STATE_TOKEN_GUID)
    lua_text = (repo / "assets/tts-mod/extract/v2/lua_script.lua").read_text(encoding="utf-8")
    for fragment in ("robot = gO('cbf1f3')", "robotDeck = gO('98925d')", "robotToken = gO('828c1d')", "robotDeck.takeObject({", "entry.hasTag('RobotCard')", "entry.flip()", "robot.setGMNotes('active')", "robotToken.setState(1)"):
        if fragment not in lua_text:
            raise AssertionError(f"Robot Lua state provenance drift: {fragment}")

    prototype_rows = []
    for guid in ("c24f3f", "d65fd6"):
        row = next(item for item in classification if item.get("guid") == guid)
        prototype_rows.append({"guid": guid, "nickname": row["nickname"], "cardId": row["card_id"], "verdict": row["verdict"], "reason": row["reason"], "parent": row["parent"], "faceUrl": next(url for key, url in row["urls"] if key == "FaceURL"), "backUrl": next(url for key, url in row["urls"] if key == "BackURL")})
    expansion_rows = []
    for guid in ("492017", "a81e7e", "37d67f"):
        row = next(item for item in classification if item.get("guid") == guid)
        expansion_rows.append({"guid": guid, "description": row["description"], "cardId": row["card_id"], "verdict": row["verdict"], "reason": row["reason"], "parent": row["parent"]})
    security_room_collisions = [row for row in classification if row.get("nickname") == "SECURITY ROBOT ROOM"]

    visual_projection = []
    for definition in OFFICIAL_VISUAL_OCCURRENCES:
        visual = visual_by_id[definition["occurrenceId"]]
        visual_projection.append({**definition, "sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf", "visualType": visual["type"], "bbox160Dpi": visual["bbox"], "obligationClass": visual["obligationClass"]})

    source_backlog_units = [row["backlogUnitId"] for row in rows] + [
        "RULE:ACT-ROBOT-001", "RULE:ACT-TACTICAL-001", "RULE:ITM-005",
        "FAQ:FQ-P02-U17",
        *[f"VIS:{occurrence_id}" for occurrence_id in required_visual_ids],
    ]
    if any(unit_id not in backlog_by_id for unit_id in source_backlog_units):
        raise AssertionError("Robot source-obligation backlog ID closure failed")

    return {
        "schemaVersion": 1,
        "recordType": "semantic-robot-source-index",
        "scope": "entire base-game Robot-card/component family; source versions, sides, runtime-state artifacts, and excluded collisions remain independent",
        "derivationPolicy": "Derive base faces only from the root robotDeck Lua role and exact full CardID/GUID/FaceURL/parent-deck tuples; close against source bytes, corpus, panels, sentences, icons, official visuals, licensed data, and backlog. Never join by title, folder, URL alone, or CardID modulo.",
        "counts": {
            "robotIdentities": len(rows),
            "ttsFaceOccurrences": len(rows),
            "directCompositeFaceSelectors": len(rows),
            "generatedSpriteSheetCells": 0,
            "selectorGaps": 0,
            "ttsSharedBackOccurrences": 1,
            "baseBackSelectorReferences": len(base_back_selectors),
            "prototypeBackSelectorReferencesExcluded": len(prototype_back_selectors),
            "canonicalCorpusFaces": sum(row["extractionState"] == "verified-canonical" for row in rows),
            "sourceBoundDraftFaces": sum(row["extractionState"] == "draft-full" for row in rows),
            "licensedDigitalOccurrences": len(bga),
            "officialVisibleComponentOccurrences": sum(len(row["officialOccurrences"]) for row in rows),
            "officialVisibleComponentIdentities": sum(bool(row["officialOccurrences"]) for row in rows),
            "physicalPanels": sum(len(row["panels"]) for row in rows),
            "operativePanels": sum(sum(panel["operative"] for panel in row["panels"]) for row in rows),
            "actionOptions": sum(len(row["actionOptions"]) for row in rows),
            "printedSentences": sum(len(row["sentences"]) for row in rows),
            "functionalIconOccurrences": sum(len(row["iconOccurrences"]) for row in rows),
            "officialVisibleFaceIconOccurrences": sum(len(row["iconOccurrences"]) for row in rows if row["officialOccurrences"]),
            "licensedPlaceholderOccurrences": sum(sum(len(re.findall(r"<([A-Z-]+)>", text)) for text in row["bgaOccurrence"]["desc"]) for row in rows),
            "rulebookTextOccurrences": len(RULEBOOK_TEXT_OCCURRENCES),
            "rulebookVisualOccurrences": len(visual_projection),
            "baseFaqOccurrences": 1,
            "excludedExpansionFaqOccurrences": 2,
            "prototypeRobotCardsExcluded": len(prototype_rows),
            "expansionRobotCardsExcluded": len(expansion_rows),
            "securityRobotRoomNameCollisionsExcluded": len(security_room_collisions),
            "backlogTuples": len(rows),
            "backlogObligationsLinked": len(source_backlog_units),
        },
        "familyCountEvidence": {
            "officialRulebook": {"sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf", "locators": ["unprinted PDF page 3 / RB-P03-V01", "printed page 37 / lines 5997–5999"], "printedCount": 6},
            "ttsRole": {"sourcePath": "assets/tts-mod/extract/v2/lua_roles.json", "role": "robotDeck", "deckGuid": BASE_ROBOT_DECK_GUID, "deckType": role["type"], "rootParent": deck_object["parent"], "nUrls": role["n_urls"], "rootDeckNumbers": role["deck_nums"], "fullCardIds": card_ids, "faceCount": len(rows), "sharedBackCount": 1},
            "closedCorpus": {"sourcePath": "assets/tts-mod/extract/card-text-corpus.json", "faceCount": len(rows), "sharedBackCount": 1, "sourcePaths": [row["sourcePath"] for row in rows]},
            "licensedDigital": {"sourcePath": BGA_ROBOT_PATH, "indexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "table": "ROBOT_CARDS_DATA", "count": len(bga), "keys": sorted(bga)},
            "backlog": {"sourcePath": "docs/rules/semantics/backlog.json", "faceTupleCount": len(rows), "faceUnitIds": [row["backlogUnitId"] for row in rows], "linkedUnitIds": source_backlog_units},
        },
        "sharedBack": {
            "sourceId": ROBOT_BACK_SOURCE_ID,
            "occurrenceId": "TTS-ROBOT-SHARED-BACK",
            "sourcePath": ROBOT_BACK_PATH,
            "sourceSha256": back_sha,
            "sourceAuthority": "source-bound-component-scan",
            "sourceVersion": f"TTS shared base Robot back / root deck {BASE_ROBOT_DECK_GUID}",
            "sourceSelector": {"key": "BackURL", "objectType": "DeckCustom", "guid": BASE_ROBOT_DECK_GUID, "url": back_row["url"], "sideRole": "shared-non-operative-back", "rootDeckSelectorCount": 1, "baseCardSelectorCount": 6, "prototypeSelectorCountExcluded": 2},
            "corpusEvidencePath": "assets/tts-mod/extract/card-text-corpus.json",
            "provenanceEvidencePath": "assets/tts-mod/extract/card-provenance-inventory.json",
            "rulesTextPresent": False,
            "sourceClassification": "generic-card-back",
            "separateRulesFace": False,
        },
        "ttsRuntimeStateProvenance": {
            "authorityBoundary": "TTS automation/provenance only; never rules authority",
            "luaPath": "assets/tts-mod/extract/v2/lua_script.lua",
            "rolesPath": "assets/tts-mod/extract/v2/lua_roles.json",
            "objectsPath": "assets/tts-mod/extract/v2/objects.json",
            "roleBindings": [
                {"role": "robot", "guid": ROBOT_MODEL_GUID, "objectType": model_object["type"], "urlRoles": [key for key, _ in model_object["urls"]]},
                {"role": "robotDeck", "guid": BASE_ROBOT_DECK_GUID, "objectType": deck_object["type"], "urlRoles": [key for key, _ in deck_object["urls"]]},
                {"role": "robotToken", "guid": ROBOT_STATE_TOKEN_GUID, "objectType": state_token_object["type"], "urlRoles": [key for key, _ in state_token_object["urls"]]},
            ],
            "setup": {"locator": "lua_script.lua:4388–4398", "operation": "take one random object from root robotDeck; move remainder away", "explorationRobotSpecialCase": "adds characterFig and noEntrance tags to the Robot model"},
            "reveal": {"locator": "lua_script.lua:2102–2124 and 13446–13460", "cardOperation": "flip the object tagged RobotCard", "modelStateTransition": {"fromGmNotes": "", "toGmNotes": "active"}, "helperTokenStateTransition": {"toStateId": 1, "semanticImageIdentity": "not inferred; extracted URLs collide with status-token assets"}},
        },
        "officialRulebookTextOccurrences": RULEBOOK_TEXT_OCCURRENCES,
        "officialVisualOccurrences": visual_projection,
        "faqBoundary": {
            "baseApplicable": [{"sourceUnitId": "FQ-P02-U17", "section": faq_by_id["FQ-P02-U17"]["section"], "applicability": faq_by_id["FQ-P02-U17"]["applicability"], "printedText": faq_by_id["FQ-P02-U17"]["printedText"]}],
            "excludedExpansion": [{"sourceUnitId": qid, "section": faq_by_id[qid]["section"], "applicability": faq_by_id[qid]["applicability"], "printedText": faq_by_id[qid]["printedText"]} for qid in ("FQ-P03-U15", "FQ-P03-U17")],
            "boundary": "Neoflesh FAQ answers do not resolve base-game Robot reveal or SEM-Q-010.",
        },
        "excludedContent": {
            "prototypeRobotCards": prototype_rows,
            "expansionRobotCards": expansion_rows,
            "securityRobotRoomNameCollisions": [{"guid": row["guid"], "type": row["type"], "cardId": row["card_id"], "verdict": row["verdict"], "reason": row["reason"]} for row in security_room_collisions],
            "folderNameBoundary": "Robot-named folders, models, Room components, placeholders, and duplicated URL references are not Robot-card identities without the exact root-deck composite selector.",
        },
        "faces": rows,
    }


def robot_source_registry_rows(robot_source_index: dict) -> list[dict]:
    rows = []
    for face in robot_source_index["faces"]:
        rows.append({"sourceId": face["sourceId"], "authority": face["sourceAuthority"], "version": face["sourceVersion"], "path": face["sourcePath"], "sha256": face["sourceSha256"], "occurrenceId": face["robotOccurrenceId"], "evidenceIndexPath": face["corpusEvidencePath"], "evidenceRecord": face["sourceSha256"], "provenanceIndexPath": face["provenanceEvidencePath"]})
    back = robot_source_index["sharedBack"]
    rows.append({"sourceId": back["sourceId"], "authority": back["sourceAuthority"], "version": back["sourceVersion"], "path": back["sourcePath"], "sha256": back["sourceSha256"], "occurrenceId": back["occurrenceId"], "evidenceIndexPath": back["corpusEvidencePath"], "evidenceRecord": back["sourceSha256"], "provenanceIndexPath": back["provenanceEvidencePath"]})
    rows.append({"sourceId": BGA_ROBOT_SOURCE_ID, "authority": "licensed-digital-secondary", "version": "licensed BGA immutable build 260622-1220 / ROBOT_CARDS_DATA", "path": BGA_ROBOT_PATH, "sha256": robot_source_index["faces"][0]["bgaOccurrence"]["sourceSha256"], "occurrenceId": "ROBOT_CARDS_DATA", "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "evidenceRecord": "ROBOT_CARDS_DATA"})
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, selector: str = "rules-system", mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None) -> dict:
    return {"targetId": target_id, "selectorRef": selector, "eligibleTaxonIds": eligible_taxa, "cardinality": {"min": minimum, "max": maximum}, "selectionMode": mode, "visibility": "public"}


def build_robot_records(repo: Path, robot_source_index: dict, record, assertion, timing, participant, condition, decision, operation, exploration_rule_ids: list[str], room_rule_ids: list[str]) -> list[dict]:
    del repo
    records = []
    face_by_card = {row["ttsCardId"]: row for row in robot_source_index["faces"]}

    records.append(record(
        "SEM-ROBOT-SETUP-001", "Robot setup and finite starting components", "source-backed", "procedure", "official-primary", "verbatim-structure",
        [assertion("SA-ROBOT-SETUP-RB", "SRC-RULEBOOK", "printed pages 3, 5, and 8 / Robot inventory and Section Setup steps 2, 8–10", ["timing", "preconditions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "Shuffle all 6 Robot cards, draw 1 without looking and place it face down on the Robot slot; leave the other 5 unseen in the box. Place 1 full Ammo and 1 Oxygen by the card and the one Robot model on the Hibernatorium.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-SETUP-02"), assertion("SA-ROBOT-BACK", ROBOT_BACK_SOURCE_ID, "TTS-ROBOT-SHARED-BACK / paired non-operative side", ["informationPolicy", "sourceVariants"], "The six base Robot faces share one generic back with no operative text; two prototype cards reference the same pixels but are excluded by container identity.", "docs/rules/semantics/robot-source-index.json:TTS-ROBOT-SHARED-BACK")],
        ["term.robot-card", "icon.robot", "icon.ammoToken", "icon.oxygenToken"], ["tax.entity.component.card.robot", "tax.entity.agent.robot", "tax.entity.component.token.tactical-gear", "tax.entity.spatial.room.hibernatorium", "tax.scaffold.zone.removed-from-game"], [],
        timing("TW-ROBOT-SETUP", "tax.entity.component.card.robot", "when-triggered", "once-during-game-setup"), [participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ROBOT-SETUP-SELECTED", "subjectRef": "selected Robot-card identity and face", "audience": "hidden-from-all", "revealTrigger": "SEM-ROBOT-REVEAL-001 only", "secrecy": "draw without looking and keep face down"}, {"informationId": "I-ROBOT-SETUP-UNSELECTED", "subjectRef": "five unselected Robot-card identities", "audience": "hidden-from-all", "revealTrigger": "never in this game", "secrecy": "leave unseen in the box"}], [], [],
        [operation("S01", 1, "shuffle", "must", "P-RULES", "all 6 Robot cards", ["SA-ROBOT-SETUP-RB"]), operation("S02", 2, "draw-random", "must", "P-RULES", "1 Robot card without inspection", ["SA-ROBOT-SETUP-RB"]), operation("S03", 3, "set-state", "must", "selected Robot card", "sem.state.robot-card.unrevealed", ["SA-ROBOT-SETUP-RB"]), operation("S04", 4, "transition-zone", "must", "P-RULES", "five unselected Robot cards unseen in box", ["SA-ROBOT-SETUP-RB"], transition={"from": "Robot-card setup set", "to": "tax.scaffold.zone.removed-from-game"}), operation("S05", 5, "place-component", "must", "P-RULES", "1 full Ammo token and 1 Oxygen token in the Robot's corresponding Tactical Gear slots", ["SA-ROBOT-SETUP-RB"], repeat={"finiteSupply": {"Ammo": 20, "Oxygen": 20}, "startingQuantity": {"Ammo": 1, "Oxygen": 1}, "ammoSide": "full"}), operation("S06", 6, "place-component", "must", "P-RULES", "the sole Robot model in the Hibernatorium", ["SA-ROBOT-SETUP-RB"], repeat={"finiteRobotModels": 1})],
        {"policy": "ordered-complete", "unit": "Robot setup step", "onImpossible": "the source assumes the listed physical components are present; no substitute component or face may be invented"}, {"kind": "persistent-game-setup"}, {"policy": "exactly one selected face, five unseen excluded faces, one model, and one starting token of each stated type"}, [], [],
        [{"variantId": "SV-ROBOT-BACK-PROTOTYPE-REFS", "sourceId": ROBOT_BACK_SOURCE_ID, "sourceAssertionId": "SA-ROBOT-BACK", "difference": "Two junk/prototype Robot cards also reference the same BackURL pixels.", "resolution": "Container/GUID/CardID provenance excludes those selectors from the six-card base family; shared pixels do not create rules-face identity."}]))

    records.append(record(
        "SEM-ROBOT-REVEAL-001", "Robot-card reveal and pre-reveal availability", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-ROBOT-REVEAL-RB", "SRC-RULEBOOK", "printed pages 8 and 37 / Hibernatorium discovery and Robot reveal", ["timing", "preconditions", "informationPolicy", "operations", "duration", "unresolvedQuestionRefs"], "The Robot cannot be Activated while the Hibernatorium is Undiscovered. When any Room is connected to it for the first time, reveal the Robot card; the Robot can then be Activated.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-REVEAL-01")],
        ["term.robot-card", "icon.robot"], ["tax.entity.component.card.robot", "tax.entity.agent.robot", "tax.entity.spatial.room.hibernatorium"], [],
        timing("TW-ROBOT-REVEAL", "tax.entity.spatial.room.hibernatorium", "when-triggered", "first-Room-connection-only"), [participant("P-RULES", "rules-system")], "must",
        [condition("C-ROBOT-REVEAL", "predicate", [{"predicate": "a Room is connected to the Hibernatorium for the first time"}], ["SA-ROBOT-REVEAL-RB"])], [],
        [{"informationId": "I-ROBOT-IDENTITY", "subjectRef": "selected Robot-card face, title, and printed effect", "audience": "hidden-from-all-before-trigger; public-after-trigger", "revealTrigger": "first Room connected to Hibernatorium", "secrecy": "no player may inspect the face before the source reveal trigger"}], [], [],
        [operation("S01", 1, "evaluate-condition", "must", "P-RULES", "Robot Activation remains unavailable before the reveal trigger", ["SA-ROBOT-REVEAL-RB"]), operation("S02", 2, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-012 applicability of non-Activation Robot-referencing effects before reveal", ["SA-ROBOT-REVEAL-RB"]), operation("S03", 3, "reveal", "must", "P-RULES", "selected Robot card", ["SA-ROBOT-REVEAL-RB"]), operation("S04", 4, "set-state", "must", "selected Robot card", "sem.state.robot-card.revealed", ["SA-ROBOT-REVEAL-RB"]), operation("S05", 5, "set-state", "if-able", "Robot", "sem.state.robot.operational", ["SA-ROBOT-REVEAL-RB"], conditions=["Robot has no Malfunction marker"])],
        {"policy": "ordered-complete", "unit": "first Hibernatorium-connection trigger", "onImpossible": "Activation remains unavailable before reveal; non-Activation effect applicability remains SEM-Q-012 without a default"}, {"kind": "unrevealed-until-first-connection-then-public"}, {"policy": "irreversible single reveal; no separate back rules face"}, [], ["SEM-Q-012"], []))

    records.append(record(
        "SEM-ACT-ROBOT-001", "Activate the Robot Basic Action", "source-backed", "action", "official-primary", "source-composed",
        [assertion("SA-ACT-ROBOT-RB", "SRC-RULEBOOK", "printed pages 12, 14, and 37 / Basic Actions, Effects, and Activating the Robot", ["timing", "preconditions", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution"], "Activate the Robot is Not In Combat and costs 1 Action card locally in the Robot's Room, or 2 remotely from a Computer Room; a Data token waives the additional remote card. Select only a fully resolvable printed Robot effect.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-ACTIVATE-LOCAL-01")],
        ["term.action", "term.robot-card", "icon.actionCard", "icon.notInCombat", "icon.computer", "term.data-token"], ["tax.process.action.basic", "tax.entity.component.card.robot", "tax.entity.agent.robot", "tax.entity.component.card.action", "tax.state.combat.not-in-combat", "tax.entity.component.token.data"], [],
        timing("TW-ACT-ROBOT", "tax.process.temporal.turn", "during", "per-selected-Activate-Robot-Action"), [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-ROBOT", "affected", "tax.entity.agent.robot"), participant("P-RULES", "rules-system")], "must",
        [condition("C-ACT-ROBOT", "all", [{"predicate": "Robot card is revealed"}, {"predicate": "Robot has no Malfunction marker"}, {"predicate": "Character is Not In Combat"}, {"predicate": "local or remote activation route is legal"}, {"predicate": "at least one printed Robot option is entirely resolvable"}], ["SA-ACT-ROBOT-RB"])],
        [decision("D-ACT-ROBOT-MODE", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["local", "remote using Data token", "remote with additional Action-card payment"]), decision("D-ACT-ROBOT-BASE-PAY", "P-PLAYER", "player-choice", 1, 1, False, "owner-private-until-discard", ["own Action cards in hand"]), decision("D-ACT-ROBOT-REMOTE-PAY", "P-PLAYER", "player-choice", 0, 1, True, "owner-private-until-discard", ["own additional Action card when remote and no Data token"])],
        [{"informationId": "I-ACT-ROBOT", "subjectRef": "activation mode, discarded payment cards, revealed Robot identity, and resolved option", "audience": "public-on-declaration/payment", "revealTrigger": "Action declaration", "secrecy": "unselected hand cards remain private"}],
        [{"costId": "COST-ACT-ROBOT-BASE", "payerRef": "P-PLAYER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-ACT-ROBOT-BASE-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}, {"costId": "COST-ACT-ROBOT-REMOTE", "payerRef": "P-PLAYER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-ACT-ROBOT-REMOTE-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [operation("S01", 1, "choose", "must", "P-PLAYER", "legal local/remote activation mode", ["SA-ACT-ROBOT-RB"], decision_ref="D-ACT-ROBOT-MODE"), operation("S02", 2, "pay-cost", "must", "P-PLAYER", "COST-ACT-ROBOT-BASE", ["SA-ACT-ROBOT-RB"], decision_ref="D-ACT-ROBOT-BASE-PAY"), operation("S03", 3, "pay-cost", "if-able", "P-PLAYER", "COST-ACT-ROBOT-REMOTE", ["SA-ACT-ROBOT-RB"], conditions=["remote mode selected", "Character has no Data token"], decision_ref="D-ACT-ROBOT-REMOTE-PAY"), operation("S04", 4, "invoke-selected-process", "must", "P-ROBOT", "exact Robot-face semantic record selected by full locked occurrence identity", ["SA-ACT-ROBOT-RB"], notes="Dispatch uses the selected face's full CardID/GUID/FaceURL tuple, never title, folder, shared back, or CardID modulo.")],
        {"policy": "all-or-nothing-selection", "unit": "Activate Robot Action and one selected printed option", "onImpossible": "the Action/option may not be selected unless payment, route, Robot availability, and the whole chosen option are resolvable"}, {"kind": "instantaneous-basic-action"}, {"policy": "repeatable only through distinct legal Actions"}, [], [], []))
    records[-1]["operations"][-1]["dispatchRuleIds"] = list(ROBOT_RULE_IDS)

    records.append(record(
        "SEM-ROBOT-MOVEMENT-001", "Robot movement procedure", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-ROBOT-MOVE-RB", "SRC-RULEBOOK", "printed page 37 / Robot Movement", ["timing", "preconditions", "decisions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Robot movement occurs only through player Actions. Each move is between neighboring Rooms, ignores Intruders, cannot pass a Closed Door, normally cannot use an Unexplored Corridor, and makes no Noise roll except for the Exploration Robot exception.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-MOVE-01")],
        ["icon.robot", "term.room", "term.corridor", "term.closed", "term.unexplored-corridor", "term.noise-roll"], ["tax.entity.agent.robot", "tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.state.closed", "tax.state.corridor.unexplored", "tax.process.sequence.noise-roll"], [],
        timing("TW-ROBOT-MOVE", "tax.entity.agent.robot", "when-triggered", "per-caller-requested-step-up-to-printed-maximum"), [participant("P-MOVE-OWNER", "source-unspecified-decision-owner"), participant("P-ROBOT", "actor", "tax.entity.agent.robot"), participant("P-RULES", "rules-system")], "must",
        [condition("C-ROBOT-MOVE-LEGAL", "all", [{"predicate": "destination is a neighboring Room"}, {"predicate": "path has no Closed Door"}, {"predicate": "path is not an Unexplored Corridor unless caller is Exploration Robot's exception"}], ["SA-ROBOT-MOVE-RB"])],
        [decision("D-ROBOT-MOVE-STEP", "P-MOVE-OWNER", "unresolved", 0, 1, True, "source-unspecified", ["stop", "one legal neighboring destination for the next movement step"])],
        [{"informationId": "I-ROBOT-MOVE", "subjectRef": "Robot origin, eligible neighboring destinations, selected step, and remaining printed movement allowance", "audience": "public", "revealTrigger": "each movement step", "secrecy": "none"}], [],
        [_target("T-ROBOT-MOVE-DEST", ["tax.entity.spatial.room"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=0, maximum=1)],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-013 Robot movement destination/route decision owner and step timing", ["SA-ROBOT-MOVE-RB"]), operation("S02", 2, "select-target", "may", "P-MOVE-OWNER", "stop or one legal neighboring Room", ["SA-ROBOT-MOVE-RB"], decision_ref="D-ROBOT-MOVE-STEP", target_ref="T-ROBOT-MOVE-DEST"), operation("S03", 3, "move-entity", "if-able", "P-ROBOT", "selected neighboring Room", ["SA-ROBOT-MOVE-RB"], conditions=["a destination rather than stop was selected"], decision_ref="D-ROBOT-MOVE-STEP", target_ref="T-ROBOT-MOVE-DEST", repeat={"maximumSteps": "caller-supplied printed value", "zeroStepsLegal": True, "reselectionTiming": "SEM-Q-013 unresolved"}), operation("S04", 4, "evaluate-condition", "must", "P-RULES", "ordinary Robot movement produces no Noise roll and no Intruder interaction", ["SA-ROBOT-MOVE-RB"])],
        {"policy": "source-conditional-steps", "unit": "one optional movement step up to caller maximum", "onImpossible": "stop is legal because the face says up to; never route through a Closed Door or ordinary Unexplored Corridor, and do not invent a destination owner/tie-break"}, {"kind": "instantaneous-caller-bounded-movement"}, {"policy": "one Room-to-neighboring-Room transition per selected step"}, [], ["SEM-Q-013"], []))

    records.append(record(
        "SEM-ACT-TACTICAL-001", "Use Any Tactical Gear Basic Action", "source-backed", "action", "official-primary", "verbatim-structure",
        [assertion("SA-ACT-GEAR-RB", "SRC-RULEBOOK", "printed pages 12 and 16 / Basic Actions and Use Any Tactical Gear Action", ["timing", "decisions", "informationPolicy", "costs", "targets", "operations", "partialResolution"], "Discard 1 Action card, choose any number of own Tactical Gear tokens, apply their effects, then discard them except Ammo moved to Weapons; any number of own tokens may also move between compatible own slots.", "docs/rulebooks/rulebook_text.txt:lines 2876–2895, 3469–3490")],
        ["term.action", "term.tactical-gear-token", "term.tactical-gear-slot", "icon.actionCard", "icon.ammoToken"], ["tax.process.action.basic", "tax.entity.component.token.tactical-gear", "tax.entity.component.slot.tactical-gear", "tax.entity.component.card.action"], [],
        timing("TW-ACT-GEAR", "tax.process.temporal.turn", "during", "per-selected-Use-Any-Tactical-Gear-Action"), [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-RULES", "rules-system")], "must", [],
        [decision("D-ACT-GEAR-PAY", "P-PLAYER", "player-choice", 1, 1, False, "owner-private-until-discard", ["own Action cards in hand"]), decision("D-ACT-GEAR-USE", "P-PLAYER", "player-choice", 0, None, True, "public-on-use", ["any subset of own Tactical Gear tokens"]), decision("D-ACT-GEAR-MOVE", "P-PLAYER", "player-choice", 0, None, True, "public-on-move", ["any legal transfers among own compatible Tactical Gear slots"])],
        [{"informationId": "I-ACT-GEAR", "subjectRef": "paid card, selected token identities/sides, effects, and slot transfers", "audience": "public-on-payment/use", "revealTrigger": "Action resolution", "secrecy": "unselected hand cards remain private"}],
        [{"costId": "COST-ACT-GEAR", "payerRef": "P-PLAYER", "resourceTermId": "icon.actionCard", "quantity": 1, "selectionDecisionRef": "D-ACT-GEAR-PAY", "transition": {"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile"}}], [],
        [operation("S01", 1, "pay-cost", "must", "P-PLAYER", "COST-ACT-GEAR", ["SA-ACT-GEAR-RB"], decision_ref="D-ACT-GEAR-PAY"), operation("S02", 2, "choose", "may", "P-PLAYER", "any subset of own Tactical Gear tokens to use", ["SA-ACT-GEAR-RB"], decision_ref="D-ACT-GEAR-USE"), operation("S03", 3, "invoke-selected-process", "if-able", "P-CHARACTER", "each selected Tactical Gear token effect", ["SA-ACT-GEAR-RB"], decision_ref="D-ACT-GEAR-USE", repeat={"scope": "each selected token"}), operation("S04", 4, "remove-component", "if-able", "P-RULES", "each used non-Ammo Tactical Gear token back to its finite pool", ["SA-ACT-GEAR-RB"], decision_ref="D-ACT-GEAR-USE"), operation("S05", 5, "move-entity", "may", "P-PLAYER", "selected legal Tactical Gear transfers among compatible own slots", ["SA-ACT-GEAR-RB"], decision_ref="D-ACT-GEAR-MOVE")],
        {"policy": "source-conditional-steps", "unit": "one selected token effect or slot transfer", "onImpossible": "only legal compatible transfers and resolvable selected token effects may be chosen; zero tokens/transfers is source-permitted"}, {"kind": "instantaneous-basic-action"}, {"policy": "each physical token occupies at most one compatible slot"}, [], [], []))

    records.append(record(
        "SEM-ROBOT-TACTICAL-GEAR-001", "Robot Tactical Gear access and transfer extension", "source-backed", "constraint", "official-primary", "source-composed",
        [assertion("SA-ROBOT-GEAR-RB", "SRC-RULEBOOK", "printed pages 16 and 37 / Robot's Tactical Gear Slots", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking"], "While a Character in the Robot's Room performs Use Any Tactical Gear, Robot tokens may also be used and tokens may move between Character and Robot compatible slots. Robot Tactical Gear remains usable while the Robot is malfunctioned.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-GEAR-02")],
        ["icon.robot", "term.tactical-gear-token", "term.tactical-gear-slot", "icon.ammoToken", "icon.oxygenToken"], ["tax.entity.agent.robot", "tax.entity.agent.character", "tax.entity.component.token.tactical-gear", "tax.entity.component.slot.tactical-gear"], [],
        timing("TW-ROBOT-GEAR", "tax.process.action.basic", "during", "per-co-located-Use-Any-Tactical-Gear-Action"), [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-ROBOT", "component-holder", "tax.entity.agent.robot"), participant("P-RULES", "rules-system")], "may",
        [condition("C-ROBOT-GEAR", "all", [{"predicate": "Character is performing SEM-ACT-TACTICAL-001"}, {"predicate": "Character and Robot occupy the same Room"}], ["SA-ROBOT-GEAR-RB"])],
        [decision("D-ROBOT-GEAR-USE", "P-PLAYER", "player-choice", 0, None, True, "public-on-use", ["any subset of Tactical Gear tokens on the Robot"]), decision("D-ROBOT-GEAR-MOVE", "P-PLAYER", "player-choice", 0, None, True, "public-on-move", ["legal compatible transfers between Character and Robot slots"])],
        [{"informationId": "I-ROBOT-GEAR", "subjectRef": "Robot token types/sides, slots, use, and transfers", "audience": "public", "revealTrigger": "continuous/use", "secrecy": "none"}], [], [],
        [operation("S01", 1, "choose", "may", "P-PLAYER", "Robot Tactical Gear tokens to include in the current Gear Action", ["SA-ROBOT-GEAR-RB"], decision_ref="D-ROBOT-GEAR-USE"), operation("S02", 2, "invoke-selected-process", "if-able", "P-CHARACTER", "each selected Robot-held Tactical Gear effect", ["SA-ROBOT-GEAR-RB"], decision_ref="D-ROBOT-GEAR-USE", repeat={"scope": "each selected token", "robotMalfunctionDoesNotBlock": True}), operation("S03", 3, "move-entity", "may", "P-PLAYER", "selected tokens between compatible Character and Robot Tactical Gear slots", ["SA-ROBOT-GEAR-RB"], decision_ref="D-ROBOT-GEAR-MOVE")],
        {"policy": "source-conditional-steps", "unit": "one selected Robot token use or transfer", "onImpossible": "incompatible or occupied target slots are unavailable; zero Robot tokens/transfers remains legal"}, {"kind": "continuous-extension-during-one-Gear-Action"}, {"policy": "one physical token per compatible slot; no duplication; malfunction does not suppress tokens"}, [], [], []))

    records.append(record(
        "SEM-ROBOT-MALFUNCTION-PLACEMENT-001", "Place a Malfunction on the Robot", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        [assertion("SA-ROBOT-MALF-PLACE-P22", "SRC-RULEBOOK", "printed pages 22–23 / Malfunction on Robot and marker limits", ["timing", "preconditions", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs"], "Place a Malfunction marker on the Robot card; repeated placement is ignored. If no Malfunction is available, place Fire in the Room if possible, and if required Fire supply is empty the Facility is destroyed.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-MALFUNCTION-01"), assertion("SA-ROBOT-MALF-PLACE-P37", "SRC-RULEBOOK", "printed page 37 / Malfunction Marker on the Robot", ["preconditions", "operations", "duration", "unresolvedQuestionRefs"], "A Robot with Malfunction has no Action and all game effects mentioning it are unavailable.", "docs/rules/semantics/robot-source-index.json:RB-ROBOT-MALFUNCTION-P37-01")],
        ["icon.robot", "icon.malfunction", "icon.fire"], ["tax.entity.agent.robot", "tax.entity.component.card.robot", "tax.entity.component.marker.malfunction", "tax.entity.component.marker.fire", "tax.scaffold.supply-pool"], [],
        timing("TW-ROBOT-MALF-PLACE", "tax.entity.agent.robot", "when-triggered", "per-effect-requesting-Robot-Malfunction-placement"), [participant("P-RULES", "rules-system"), participant("P-ROBOT", "affected", "tax.entity.agent.robot")], "must", [], [],
        [{"informationId": "I-ROBOT-MALF-PLACE", "subjectRef": "Robot marker state, finite marker pools, fallback Fire, and Facility outcome", "audience": "public", "revealTrigger": "placement resolution", "secrecy": "face identity remains governed by SEM-ROBOT-REVEAL-001"}], [], [],
        [operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-012 pre-reveal applicability when caller targets an unrevealed Robot card", ["SA-ROBOT-MALF-PLACE-P22", "SA-ROBOT-MALF-PLACE-P37"]), operation("S02", 2, "transition-zone", "if-able", "P-RULES", "1 Malfunction marker onto the Robot card", ["SA-ROBOT-MALF-PLACE-P22", "SA-ROBOT-MALF-PLACE-P37"], conditions=["Robot has no Malfunction marker", "a Malfunction marker is available"], transition={"from": "tax.scaffold.supply-pool", "to": "Robot card"}), operation("S03", 3, "set-state", "if-able", "P-ROBOT", "sem.state.robot.broken", ["SA-ROBOT-MALF-PLACE-P22", "SA-ROBOT-MALF-PLACE-P37"], conditions=["Malfunction marker was placed"]), operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-010 repeated-placement/effect-availability conflict when Robot already has Malfunction", ["SA-ROBOT-MALF-PLACE-P22", "SA-ROBOT-MALF-PLACE-P37"], conditions=["Robot already has a Malfunction marker"]), operation("S05", 5, "place-component", "if-able", "P-RULES", "1 Fire marker in the Robot's Room as finite-Malfunction fallback", ["SA-ROBOT-MALF-PLACE-P22"], conditions=["Robot has no Malfunction marker", "no Malfunction marker is available", "Fire placement is possible"]), operation("S06", 6, "invoke-process", "if-able", "P-RULES", "Facility destruction and End of the Game", ["SA-ROBOT-MALF-PLACE-P22"], conditions=["required fallback Fire cannot be placed because Fire supply is empty"], invoke="SEM-ENDGAME-001")],
        {"policy": "if-not-possible-fallback", "unit": "one requested Robot Malfunction placement", "onImpossible": "apply the explicit Fire fallback and Facility-destruction rule; repeated placement and pre-reveal applicability remain no-default questions"}, {"kind": "persistent-marker-until-source-defined-removal"}, {"policy": "at most one Robot Malfunction marker; 14 finite Malfunctions and 9 finite Fire markers globally; no destroyed-Robot state is source-defined"}, [], ["SEM-Q-010", "SEM-Q-012"], []))

    for card_id in sorted(ROBOT_DEFINITIONS):
        definition = ROBOT_DEFINITIONS[card_id]
        source = face_by_card[card_id]
        code = str(card_id)
        scan_id = f"SA-RBT-{code}-SCAN"
        general_id = f"SA-RBT-{code}-GENERAL"
        bga_id = f"SA-RBT-{code}-BGA"
        assertions = [
            assertion(scan_id, definition["sourceId"], f"{source['robotOccurrenceId']} / exact face panels and sentences", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "sourceVariants", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/robot-source-index.json:{source['robotOccurrenceId']}"),
            assertion(general_id, "SRC-RULEBOOK", "printed pages 14, 17, 22–23, 33, and 37 / effect legality and Robot procedures", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "duration", "stacking", "unresolvedQuestionRefs", "sourceVariants"], "Resolve one entirely legal printed Robot option through the official Robot movement, health, Burst, Door, marker, Room, Exploration, and finite-component rules that apply to that option.", "docs/rules/semantics/robot-source-index.json:officialRulebookTextOccurrences"),
            assertion(bga_id, BGA_ROBOT_SOURCE_ID, f"ROBOT_CARDS_DATA.{definition['bgaKey']}", ["sourceVariants"], source["bgaOccurrence"]["sourceBlockText"], f"docs/rules/semantics/robot-source-index.json:{source['robotOccurrenceId']}.bgaOccurrence"),
        ]
        assertions[0]["textKind"] = "verbatim"
        assertions[2]["textKind"] = "verbatim"
        official_assertion_ids = []
        for index, official in enumerate(source["officialOccurrences"], 1):
            assertion_id = f"SA-RBT-{code}-OFFICIAL-{index:02d}"
            item = assertion(assertion_id, "SRC-RULEBOOK", official["locator"], ["operations", "targets", "sourceVariants"], official["visibleText"], f"docs/rules/source-extraction/rulebook-visual-obligations.json:{official['parentOccurrenceId']}")
            item["textKind"] = "verbatim"
            assertions.append(item)
            official_assertion_ids.append(assertion_id)

        participants = [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "actor", "tax.entity.agent.character"), participant("P-ROBOT", "affected", "tax.entity.agent.robot"), participant("P-RULES", "rules-system")]
        decisions = [decision(f"D-RBT-{code}-OPTION", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", [f"option {row['optionId']}" for row in source["actionOptions"]])]
        information = [{"informationId": f"I-RBT-{code}", "subjectRef": "revealed exact Robot face, selected option, targets, random results, and state changes", "audience": "public", "revealTrigger": "option declaration/resolution", "secrecy": "remaining five Robot cards stay unseen and out of this game"}]
        targets = []
        terms = ["term.robot-card", "icon.robot"]
        taxa = ["tax.entity.component.card.robot", "tax.entity.agent.robot"]
        unresolved = ["SEM-Q-013"]
        ops = []

        def add(sentence_id, op_type, modality, subject, obj, *, source_ids=None, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
            sentence = next(row for row in source["sentences"] if row["sentenceId"] == sentence_id)
            step = len(ops) + 1
            op = operation(f"S{step:02d}", step, op_type, modality, subject, obj, source_ids or [scan_id, general_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref, transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence_id
            op["sourcePanelId"] = sentence["panelId"]
            op["sourceOptionId"] = sentence["optionId"]
            ops.append(op)
            return op

        option_decision_id = f"D-RBT-{code}-OPTION"
        first_sentence = source["sentences"][0]
        move_max = {506400: 3, 510800: 3, 529300: 2, 529400: 2, 529500: 2, 529600: 1}[card_id]
        add(first_sentence["sentenceId"], "invoke-process", "may" if move_max > 1 else "must", "P-ROBOT", f"move zero through {move_max} neighboring-Room steps" if move_max > 1 else "move exactly one neighboring-Room step", conditions=["movement option selected"], decision_ref=option_decision_id, invoke="SEM-ROBOT-MOVEMENT-001", repeat={"printedMaximumSteps": move_max, "zeroStepsLegal": move_max > 1})
        terms.extend(["term.room", "term.corridor", "term.closed"])
        taxa.extend(["tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.state.closed"])

        if card_id == 506400:
            sentence_id = source["sentences"][1]["sentenceId"]
            targets.append(_target("T-RBT-506400-ROOM", ["tax.entity.spatial.room"], minimum=1, maximum=1))
            add(sentence_id, "invoke-selected-process", "must", "P-PLAYER", "Room effect for the Computer Room containing the Robot, bypassing that Room's Malfunction restriction", conditions=["Room-use option selected", "Robot is in a Room with Computer"], decision_ref=option_decision_id, target_ref="T-RBT-506400-ROOM", notes="No second Basic-Action cost or generic SEM-USE-ROOM-001 invocation is adopted; actor/context ownership remains SEM-Q-018.")
            ops[-1]["dispatchRuleIds"] = list(room_rule_ids)
            terms.extend(["icon.computer", "icon.malfunction"]); taxa.extend(["tax.entity.component.marker.malfunction"]); unresolved.append("SEM-Q-018")
        elif card_id == 510800:
            door_sentence = source["sentences"][1]["sentenceId"]
            secure_sentence = source["sentences"][2]["sentenceId"]
            decisions.extend([decision("D-RBT-510800-DOOR", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["one source-eligible accessible Door"]), decision("D-RBT-510800-DOOR-STATE", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["Open", "Closed"])])
            targets.extend([_target("T-RBT-510800-DOOR", ["tax.entity.spatial.door"], selector="P-PLAYER", mode="unresolved-when-multiple", minimum=1, maximum=1), _target("T-RBT-510800-ROOM", ["tax.entity.spatial.room"], minimum=1, maximum=1)])
            add(door_sentence, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-016 meaning of a Door accessible to the Robot", conditions=["Door option selected"], decision_ref="D-RBT-510800-DOOR")
            add(door_sentence, "select-target", "must", "P-PLAYER", "one source-eligible accessible Door", conditions=["Door option selected"], decision_ref="D-RBT-510800-DOOR", target_ref="T-RBT-510800-DOOR")
            add(door_sentence, "set-state", "must", "P-RULES", "selected Door Open or Closed under ordinary Door-state constraints", conditions=["Door option selected"], decision_ref="D-RBT-510800-DOOR-STATE", target_ref="T-RBT-510800-DOOR", invoke="SEM-DOOR-001")
            add(secure_sentence, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-017 finite-supply/capacity behavior for the printed quantity 2", conditions=["Secure option selected"], decision_ref=option_decision_id)
            add(secure_sentence, "place-component", "if-able", "P-RULES", "exactly 2 Secure tokens in the Room containing the Robot", conditions=["Secure option selected", "Room contains no Intruder", "Room is not Secure-prohibited"], decision_ref=option_decision_id, target_ref="T-RBT-510800-ROOM", repeat={"requested": 2, "globalFiniteSupply": 20, "perRoomMaximum": 3, "partialPlacement": "SEM-Q-017 unresolved"})
            terms.extend(["term.door", "term.opened", "term.closed", "icon.secure"]); taxa.extend(["tax.entity.spatial.door", "tax.state.opened", "tax.state.closed", "tax.entity.component.token.secure"]); unresolved.extend(["SEM-Q-016", "SEM-Q-017"])
        elif card_id == 529300:
            move_sentence = source["sentences"][1]["sentenceId"]
            ignore_sentence = source["sentences"][2]["sentenceId"]
            targets.append(_target("T-RBT-529300-CORRIDOR", ["tax.entity.spatial.corridor"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=1, maximum=1))
            decisions.append(decision("D-RBT-529300-CORRIDOR", "P-ROBOT", "unresolved", 1, 1, False, "source-unspecified", ["one adjacent Unexplored Corridor not blocked by a Closed Door"]))
            add(move_sentence, "select-target", "must", "P-ROBOT", "one adjacent Unexplored Corridor", conditions=["Exploration option selected"], decision_ref="D-RBT-529300-CORRIDOR", target_ref="T-RBT-529300-CORRIDOR")
            add(move_sentence, "move-entity", "must", "P-ROBOT", "through selected Unexplored Corridor", conditions=["Exploration option selected"], decision_ref="D-RBT-529300-CORRIDOR", target_ref="T-RBT-529300-CORRIDOR", notes="This is the sole source exception to ordinary Robot unexplored-Corridor prohibition; Intruders are ignored and a Closed Door still blocks.")
            add(move_sentence, "draw-random", "must", "P-RULES", "top Exploration card into resolution, reshuffling eligible discard cards first if needed", conditions=["Exploration option selected"])
            add(ignore_sentence, "set-state", "must", "P-RULES", "current Exploration invocation ignores every Entrance-effect source unit", conditions=["Exploration option selected"])
            dispatch = add(move_sentence, "invoke-selected-process", "must", "P-RULES", "exact Exploration occurrence with Robot as explorer and Entrance Effects suppressed", conditions=["Exploration option selected"], notes="Occurrence dispatch preserves exact diagrams and unconditional lifecycle; it does not substitute a Character or grant Moving Cautiously Secure placement.")
            dispatch["dispatchRuleIds"] = list(exploration_rule_ids)
            add(ignore_sentence, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-014 whether/when the Exploration Robot makes a Noise roll", conditions=["Exploration option selected"])
            terms.extend(["term.unexplored-corridor", "term.exploration-card", "term.exploration-sequence", "term.noise-roll"]); taxa.extend(["tax.state.corridor.unexplored", "tax.entity.component.card.exploration", "tax.process.sequence.exploration", "tax.process.sequence.noise-roll"]); unresolved.append("SEM-Q-014")
        elif card_id == 529400:
            sentence_id = source["sentences"][1]["sentenceId"]
            participants.append(participant("P-TECHNICAL-TARGET-OWNER", "source-unspecified-decision-owner"))
            decisions.append(decision("D-RBT-529400-MARKER", "P-TECHNICAL-TARGET-OWNER", "unresolved", 1, 1, False, "source-unspecified", ["one Fire marker on the Room", "one eligible Malfunction marker under SEM-Q-019"]))
            targets.append(_target("T-RBT-529400-MARKER", ["tax.entity.component.marker.malfunction", "tax.entity.component.marker.fire"], selector="unresolved-by-source", mode="unresolved-when-multiple", minimum=1, maximum=1))
            add(sentence_id, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-019 scope of ‘from the Room with the Robot’ for a Malfunction marker", conditions=["repair option selected"], decision_ref="D-RBT-529400-MARKER")
            add(sentence_id, "remove-component", "must", "P-RULES", "selected Fire/Malfunction marker back to its finite pool", conditions=["repair option selected"], decision_ref="D-RBT-529400-MARKER", target_ref="T-RBT-529400-MARKER", notes="No destroyed-Robot state or automatic self-repair target is adopted.")
            terms.extend(["icon.malfunction", "icon.fire"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.component.marker.fire"]); unresolved.append("SEM-Q-019")
        elif card_id == 529500:
            sentence_id = source["sentences"][1]["sentenceId"]
            participants.append(participant("P-TARGET-OWNER", "affected-decision-owner", "tax.entity.agent.player"))
            decisions.extend([decision("D-RBT-529500-TARGET", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["one Character in the Room with the Robot"]), decision("D-RBT-529500-BRANCH", "P-TARGET-OWNER", "unresolved", 1, 1, False, "source-unspecified", ["discard 1 Serious Wound", "restore 0–2 Health points"]), decision("D-RBT-529500-WOUND", "P-TARGET-OWNER", "player-choice", 0, 1, True, "public-on-discard", ["one owned Serious Wound when discard branch is chosen"])])
            targets.extend([_target("T-RBT-529500-CHARACTER", ["tax.entity.agent.character"], selector="P-PLAYER", mode="player-choice", minimum=1, maximum=1), _target("T-RBT-529500-WOUND", ["tax.entity.component.card.serious-wound"], selector="P-TARGET-OWNER", mode="player-choice", minimum=0, maximum=1)])
            add(sentence_id, "select-target", "must", "P-PLAYER", "one Character in the Room with the Robot", conditions=["medical option selected"], decision_ref="D-RBT-529500-TARGET", target_ref="T-RBT-529500-CHARACTER")
            add(sentence_id, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-015 owner of the discard-versus-restore branch and reduced restoration", conditions=["medical option selected"], decision_ref="D-RBT-529500-BRANCH")
            add(sentence_id, "remove-component", "if-able", "P-RULES", "one Serious Wound selected by the affected Character's player", conditions=["discard-Wound branch selected"], decision_ref="D-RBT-529500-WOUND", target_ref="T-RBT-529500-WOUND")
            add(sentence_id, "change-value", "if-able", "P-RULES", "selected Character Health", conditions=["restore-Health branch selected"], decision_ref="D-RBT-529500-BRANCH", target_ref="T-RBT-529500-CHARACTER", value_change={"amount": "0 through +2 chosen under SEM-Q-015", "valueTaxonId": "tax.state.health.point"})
            terms.extend(["icon.character", "term.serious-wound-card", "icon.characterHealth", "term.character-health"]); taxa.extend(["tax.entity.agent.character", "tax.entity.component.card.serious-wound", "tax.state.health.point"]); unresolved.append("SEM-Q-015")
        elif card_id == 529600:
            corridor_sentence, hits_sentence, extra_sentence = [row["sentenceId"] for row in source["sentences"][1:]]
            decisions.extend([decision("D-RBT-529600-CORRIDOR", "P-PLAYER", "player-choice", 1, 1, False, "public-on-declaration", ["one legally accessible adjacent Corridor"]), decision("D-RBT-529600-HITS", "P-PLAYER", "player-choice", 0, 4, True, "public-on-allocation", ["legal Burst-Hit allocations among Intruders in selected Corridor"])])
            targets.extend([_target("T-RBT-529600-CORRIDOR", ["tax.entity.spatial.corridor"], selector="P-PLAYER", mode="player-choice", minimum=1, maximum=1), _target("T-RBT-529600-INTRUDERS", ["tax.entity.agent.intruder"], selector="P-PLAYER", mode="player-choice", minimum=0, maximum=None)])
            add(corridor_sentence, "select-target", "must", "P-PLAYER", "one adjacent Corridor not blocked by a Closed Door", conditions=["Burst-roll option selected"], decision_ref="D-RBT-529600-CORRIDOR", target_ref="T-RBT-529600-CORRIDOR")
            add(corridor_sentence, "draw-random", "must", "P-RULES", "one Burst die result; this is not a Character Burst Action and spends no Ammo", conditions=["Burst-roll option selected"], decision_ref=option_decision_id)
            add(hits_sentence, "change-value", "must", "P-PLAYER", "rolled Hits allocated among Intruders in selected Corridor under standard type limits", conditions=["Burst-roll option selected"], decision_ref="D-RBT-529600-HITS", target_ref="T-RBT-529600-INTRUDERS", value_change={"amount": "Burst die numeric result", "valueTaxonId": "tax.process.operation.hit"}, notes="At most 1 per Adult/Larva, exactly 2 per Drone, any number up to Queen maximum; leftovers are lost.")
            add(extra_sentence, "invoke-process", "if-able", "P-RULES", "place a Malfunction on the Robot after numeric Hits resolve", conditions=["Burst additional-effects symbol was rolled"], invoke="SEM-ROBOT-MALFUNCTION-PLACEMENT-001", notes="The additional-effects symbol shares the 4 face; resolve 4 Hits and then this effect.")
            terms.extend(["term.burst", "term.hit", "icon.burstDieAdditionalEffects", "icon.malfunction"]); taxa.extend(["tax.process.action.attack.burst", "tax.process.operation.hit", "tax.symbol.die-result", "tax.entity.agent.intruder", "tax.entity.component.marker.malfunction"])

        variants = [{"variantId": f"SV-RBT-{code}-BGA", "sourceId": BGA_ROBOT_SOURCE_ID, "sourceAssertionId": bga_id, "difference": source["bgaOccurrence"]["variantDifference"], "resolution": "Retain the licensed structured occurrence as secondary evidence; exact scan and applicable official general/component text control by authority without rewriting the variant."}]
        for index, (official, assertion_id) in enumerate(zip(source["officialOccurrences"], official_assertion_ids), 1):
            variants.append({"variantId": f"SV-RBT-{code}-OFFICIAL-{index:02d}", "sourceId": "SRC-RULEBOOK", "sourceAssertionId": assertion_id, "difference": official["variantDifference"], "resolution": "The official-primary visible component occurrence is retained separately and controls over the lower-authority scan where they differ; no difference is invented where pixels match."})

        result = record(
            definition["ruleId"], definition["title"].title(), "source-backed-with-open-question" if unresolved else "source-backed", "component-effect", "official-primary", "open-alternatives" if unresolved else "source-composed", assertions, terms, taxa, definition["identityRefs"],
            timing(f"TW-RBT-{code}", "tax.process.action.basic", "during", "when-this-exact-revealed-Robot-face-is-Activated"), participants, "must",
            [condition(f"C-RBT-{code}-FACE", "all", [{"predicate": f"revealed Robot occurrence identity is {source['robotOccurrenceId']}"}, {"predicate": "Robot has no Malfunction marker"}, {"predicate": "selected printed option is entirely resolvable"}], [scan_id, general_id])], decisions, information, [], targets,
            [operation("S01", 1, "choose", "must", "P-PLAYER", "one printed Robot option", [scan_id, general_id], decision_ref=option_decision_id), *[dict(op, sequence=index + 2, stepId=f"S{index + 2:02d}") for index, op in enumerate(ops)]],
            {"policy": "all-or-nothing-selection", "unit": "one printed option and each sourceSentenceId within that option", "onImpossible": "an option may not be selected unless it resolves entirely; explicit component-limit behavior and each no-default question remain source-scoped"}, {"kind": "instantaneous-Robot-option-resolution"}, {"policy": "one option per Activate Robot Action; printed up-to movement permits zero steps; no face effects stack by name"}, [], unresolved, variants)
        records.append(result)

    return records
