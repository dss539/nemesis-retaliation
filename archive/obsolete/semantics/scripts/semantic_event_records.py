from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path


BASE_EVENT_DECK_GUID = "0d3dae"
BGA_EVENT_SOURCE_ID = "SRC-BGA-EVENTS"
BGA_EVENT_PATH = "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"


def _sentence(sentence_id: str, section: str, exact_text: str) -> dict:
    return {"sentenceId": sentence_id, "section": section, "exactText": exact_text}


# This crosswalk is occurrence-first: TTS deck card ID and source bytes identify the
# component face. Display titles are retained as evidence but are never join keys.
EVENT_DEFINITIONS = {
    5609: {
        "sourceId": "SRC-EVENT-5609",
        "bgaKey": "Event_SystemFailure",
        "ruleId": "SEM-EVENT-SYSTEM-FAILURE-001",
        "sentences": [
            _sentence("EV5609-MOVE-01", "movement", "All [intruder] in each [corridorEW] move."),
            _sentence("EV5609-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5609-MAIN-01", "main", "Place a [malfunction] in each [computer] Room."),
            _sentence("EV5609-SECONDARY-01", "secondary", "Resolve each [noise] in\nUnexplored Corridors."),
        ],
        "variantDifference": "The licensed record uses named placeholders and normalized line grouping; the scan retains the printed icon tokens, capitalization, punctuation, and line breaks independently.",
    },
    5610: {
        "sourceId": "SRC-EVENT-5610",
        "bgaKey": "Event_NoWayOut",
        "ruleId": "SEM-EVENT-NO-WAY-OUT-001",
        "sentences": [
            _sentence("EV5610-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5610-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5610-MAIN-01", "main", "Place 4 Adults\nin each non-Reinforced Corridor\nadjacent to the Landing Zone."),
            _sentence("EV5610-SECONDARY-01", "secondary", "Each [character] makes a Noise roll."),
        ],
        "variantDifference": "The licensed record normalizes the scan's line wrapping and icon placeholders; both occurrences remain independently traceable.",
    },
    5611: {
        "sourceId": "SRC-EVENT-5611",
        "bgaKey": "Event_TheQueenAwakens",
        "ruleId": "SEM-EVENT-THE-QUEEN-AWAKENS-001",
        "sentences": [
            _sentence("EV5611-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5611-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5611-MAIN-01", "main", "If the Queen is alive, add all\nQueen tokens to the bag."),
            _sentence("EV5611-SECONDARY-01", "secondary", "Place a [noise] in each Unexplored\nCorridor without [noise]."),
        ],
        "variantDifference": "The licensed record normalizes line wrapping and placeholder notation while the component scan preserves the printed occurrence.",
    },
    5612: {
        "sourceId": "SRC-EVENT-5612",
        "bgaKey": "Event_ScentOfPrey",
        "ruleId": "SEM-EVENT-SCENT-OF-PREY-001",
        "sentences": [
            _sentence("EV5612-MOVE-01", "movement", "All [intruder] in each [corridorNWSE] move."),
            _sentence("EV5612-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5612-MAIN-01", "main", "Resolve each [noise] adjacent to a [character]."),
            _sentence("EV5612-SECONDARY-01", "secondary", "Each [character] makes a Noise roll."),
        ],
        "variantDifference": "The licensed structured occurrence uses BGA placeholders; the source scan and official rulebook component occurrence retain their own wording and layout.",
        "officialOccurrences": [
            {"sourceId": "SRC-RULEBOOK", "locator": "unprinted PDF page 3 / RB-P03-V01 / rulebook_text lines 481–491", "visibleTitle": "SCENT OF PREY"},
        ],
    },
    5613: {
        "sourceId": "SRC-EVENT-5613",
        "bgaKey": "Event_Panic",
        "ruleId": "SEM-EVENT-PANIC-001",
        "sentences": [
            _sentence("EV5613-MOVE-01", "movement", "All [intruder] in each [corridorEW] move."),
            _sentence("EV5613-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5613-MAIN-01", "main", "Each [character] in a Room with [intruder] or adjacent\nto a Corridor with [intruder]:\nLoses 1 [oxygenToken] or spends [ammoToken]."),
            _sentence("EV5613-SECONDARY-01", "secondary", "Resolve each [noise] in\nUnexplored Corridors."),
        ],
        "variantDifference": "The licensed record adds an article before its Intruder placeholder and normalizes grammar/line grouping; the scan wording is not rewritten.",
    },
    5614: {
        "sourceId": "SRC-EVENT-5614",
        "bgaKey": "Event_LeavingTheShell",
        "ruleId": "SEM-EVENT-LEAVING-THE-SHELL-001",
        "sentences": [
            _sentence("EV5614-MOVE-01", "movement", "No [intruder] moves."),
            _sentence("EV5614-MAIN-01", "main", "Each [character] with Larva:\nGain 1 Contamination, discard all [ICON: solid white rectangular block],\nand reshuffle your deck."),
            _sentence("EV5614-MAIN-02", "main", "Then, resolve the Eclosion Procedure."),
            _sentence("EV5614-MAIN-03", "main", "Each other [character]:\nDraw 4 [ICON: solid white rectangular block] and resolve the Infection\nProcedure."),
            _sentence("EV5614-MAIN-04", "main", "Then, discard all [ICON: solid white rectangular block]."),
            _sentence("EV5614-SECONDARY-01", "secondary", "Reshuffle the Event deck."),
        ],
        "variantDifference": "The scan's three featureless white rectangles are explicitly unresolved/no-match; the licensed record identifies all three as ACTION-CARD. That lower-authority semantic identification is preserved as an unresolved variant, not adopted as a default.",
    },
    5615: {
        "sourceId": "SRC-EVENT-5615",
        "bgaKey": "Event_BreakingIn",
        "ruleId": "SEM-EVENT-BREAKING-IN-001",
        "sentences": [
            _sentence("EV5615-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5615-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5615-MAIN-01", "main", "Remove 1 [secure] from each Room."),
            _sentence("EV5615-SECONDARY-01", "secondary", "Resolve each [noise] in\nUnexplored Corridors."),
        ],
        "variantDifference": "The scan says “Remove” while the licensed record says “Discard”; both source occurrences remain verbatim and the scan controls this component projection.",
    },
    5616: {
        "sourceId": "SRC-EVENT-HATCHING",
        "bgaKey": "Event_Hatching",
        "ruleId": "SEM-EVENT-HATCHING-001",
        "sentences": [
            _sentence("EV5616-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5616-MAIN-01", "main", "Place a Larva in the Nest - it\nimmediately Attacks if any [character] is there."),
            _sentence("EV5616-MAIN-02", "main", "Place 1 Larva in each Unexplored\nCorridor adjacent to a [character]."),
            _sentence("EV5616-SECONDARY-01", "secondary", "Resolve each [noise] in\nUnexplored Corridors."),
        ],
        "variantDifference": "The licensed record uses an en dash, contains “Attack”/“ajdacent” transcription variants, and says “Resolve a ... in each”; the scan retains “Attacks”/“adjacent”/“Resolve each” independently.",
    },
    5617: {
        "sourceId": "SRC-EVENT-5617",
        "bgaKey": "Event_EggProtection",
        "ruleId": "SEM-EVENT-EGG-PROTECTION-001",
        "sentences": [
            _sentence("EV5617-MOVE-01", "movement", "All [intruder] in each [corridorNWSE] move."),
            _sentence("EV5617-MAIN-01", "main", "Place 2 Drones in the Nest - they\nimmediately Attack if any [character] is there."),
            _sentence("EV5617-MAIN-02", "main", "Place 1 Drone in each Unexplored\nCorridor in section C."),
            _sentence("EV5617-SECONDARY-01", "secondary", "Each [character] makes a Noise roll."),
        ],
        "variantDifference": "The licensed record normalizes the hyphen to an en dash and the Section capitalization/line grouping; the component wording remains separate.",
    },
    5618: {
        "sourceId": "SRC-EVENT-5618",
        "bgaKey": "Event_LandingZoneExplodes",
        "ruleId": "SEM-EVENT-LANDING-ZONE-EXPLODES-001",
        "sentences": [
            _sentence("EV5618-MOVE-01", "movement", "All [intruder] in each [corridorEW] move."),
            _sentence("EV5618-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5618-MAIN-01", "main", "Place a [fire] and a [malfunction] in\nthe Landing Zone."),
            _sentence("EV5618-SECONDARY-01", "secondary", "Place a [noise] in each Unexplored\nCorridor without [noise]."),
        ],
        "variantDifference": "The licensed record normalizes line wrapping and named placeholders while the scan preserves exact printed layout and icon occurrences.",
    },
    5619: {
        "sourceId": "SRC-EVENT-5619",
        "bgaKey": "Event_Damage",
        "ruleId": "SEM-EVENT-DAMAGE-001",
        "sentences": [
            _sentence("EV5619-MOVE-01", "movement", "All [intruder] in each [corridorEW] move."),
            _sentence("EV5619-MAIN-01", "main", "Place a [malfunction] in each Room with a [intruder]."),
            _sentence("EV5619-SECONDARY-01", "secondary", "Each [character] in a Room\nwithout [secure] resolves [noiseDieHazard]."),
        ],
        "variantDifference": "The licensed record uses “an” before its Intruder placeholder and normalized line grouping; the scan occurrence is retained verbatim.",
    },
    5620: {
        "sourceId": "SRC-EVENT-5620",
        "bgaKey": "Event_LifeSupportFailure",
        "ruleId": "SEM-EVENT-LIFE-SUPPORT-FAILURE-001",
        "sentences": [
            _sentence("EV5620-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5620-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5620-MAIN-01", "main", "Flip all [lifeSupportActive] to [lifeSupportInactive]."),
            _sentence("EV5620-MAIN-02", "main", "Place a [malfunction]\nin each Life Support Control Room."),
            _sentence("EV5620-SECONDARY-01", "secondary", "Place a [noise] in each Unexplored\nCorridor without [noise]."),
        ],
        "variantDifference": "The licensed record combines the two main-effect sentences into one array element and uses named placeholders; the scan sentence boundary remains authoritative for partial resolution.",
    },
    5621: {
        "sourceId": "SRC-EVENT-5621",
        "bgaKey": "Event_FireBreath",
        "ruleId": "SEM-EVENT-FIRE-BREATH-001",
        "sentences": [
            _sentence("EV5621-MOVE-01", "movement", "All [intruder] in each [corridorEW] move."),
            _sentence("EV5621-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5621-MAIN-01", "main", "From each Room with a [fire],\nspread [fire] to the neighboring\nRooms in Sections with [lifeSupportActive]."),
            _sentence("EV5621-SECONDARY-01", "secondary", "Each [character] makes a Noise roll."),
        ],
        "variantDifference": "The licensed occurrence inserts “all” before neighboring Rooms and normalizes icon/line syntax; the component sentence is preserved separately.",
    },
    5622: {
        "sourceId": "SRC-EVENT-5622",
        "bgaKey": "Event_DamagingFire",
        "ruleId": "SEM-EVENT-DAMAGING-FIRE-001",
        "sentences": [
            _sentence("EV5622-MOVE-01", "movement", "All [intruder] in each [corridorNWSE] move."),
            _sentence("EV5622-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5622-MAIN-01", "main", "Place a [malfunction] in each Room with a [fire]."),
            _sentence("EV5622-MAIN-02", "main", "From each Room with a [fire],\nspread it through Corridors\nwith the lowest Noise value."),
            _sentence("EV5622-SECONDARY-01", "secondary", "Each [character] in a Room\nwithout [secure] resolves [noiseDieHazard]."),
        ],
        "variantDifference": "The licensed record changes “From” to “In” and repeats FIRE instead of the scan pronoun “it”; both occurrences remain independent.",
    },
    5623: {
        "sourceId": "SRC-EVENT-5623",
        "bgaKey": "Event_GeneratorsOverheat",
        "ruleId": "SEM-EVENT-GENERATORS-OVERHEAT-001",
        "sentences": [
            _sentence("EV5623-MOVE-01", "movement", "All [intruder] in each [corridorNWSE] move."),
            _sentence("EV5623-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5623-MAIN-01", "main", "In Sections with an [lifeSupportActive]:\nPlace a [fire] in each\nLife Support Control Room."),
            _sentence("EV5623-MAIN-02", "main", "In Sections with an [lifeSupportInactive]:\nPlace a [malfunction] in each\nLife Support Control Room."),
            _sentence("EV5623-SECONDARY-01", "secondary", "Each [character] makes a Noise roll."),
        ],
        "variantDifference": "The licensed table splits each conditional heading and placement line into separate array entries; the scan's two conditional sentence blocks remain intact.",
    },
    5624: {
        "sourceId": "SRC-EVENT-5624",
        "bgaKey": "Event_OverwhelmingEnemies",
        "ruleId": "SEM-EVENT-OVERWHELMING-ENEMIES-001",
        "sentences": [
            _sentence("EV5624-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5624-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5624-MAIN-01", "main", "Place 1 Drone in each Corridor\nwith a [noise] adjacent to a [character]."),
            _sentence("EV5624-SECONDARY-01", "secondary", "Each [character] in a Room without a [secure]\nresolves [noiseDieHazard]."),
        ],
        "variantDifference": "The licensed record normalizes line grouping and named placeholders; the source scan's occurrence and sentence boundary remain separate.",
    },
    5625: {
        "sourceId": "SRC-EVENT-5625",
        "bgaKey": "Event_ProtectServe",
        "ruleId": "SEM-EVENT-PROTECT-AND-SERVE-001",
        "sentences": [
            _sentence("EV5625-MOVE-01", "movement", "All [intruder] in each [corridorEW] move."),
            _sentence("EV5625-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5625-MAIN-01", "main", "Place 2 Drones in the Room/Corridor\nwith the Queen – they do not Attack."),
            _sentence("EV5625-MAIN-02", "main", "If there is no Queen on the map,\nadd 2 random Drone tokens to the bag."),
            _sentence("EV5625-SECONDARY-01", "secondary", "Each [character] in a Room without a [secure]\nresolves [noiseDieHazard]."),
        ],
        "variantDifference": "The licensed occurrence supplies the display title “Protect & Serve” and normalizes placeholders/line grouping; identity remains anchored to cardId 5625 and source bytes, not title alone.",
    },
    5626: {
        "sourceId": "SRC-EVENT-5626",
        "bgaKey": "Event_ReactorOverheating",
        "ruleId": "SEM-EVENT-REACTOR-OVERHEATING-001",
        "sentences": [
            _sentence("EV5626-MOVE-01", "movement", "All [intruder] in each [corridorNWSE], [corridorEW], and [corridorNESW] move."),
            _sentence("EV5626-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5626-MAIN-01", "main", "If a [malfunction] is in the Cooling System\nRoom or the Reactor Room, Activate\nthe Autodestruction Procedure."),
            _sentence("EV5626-MAIN-02", "main", "Then, place a [malfunction] in each of these Rooms."),
            _sentence("EV5626-SECONDARY-01", "secondary", "Reshuffle the Event deck."),
        ],
        "variantDifference": "The licensed first movement entry omits the verb “move”; the official rulebook component occurrence and TTS scan include it. Higher-authority/current visible evidence controls without rewriting the BGA occurrence.",
        "officialOccurrences": [
            {"sourceId": "SRC-RULEBOOK", "locator": "unprinted PDF page 3 / RB-P03-V01 / rulebook_text lines 272–286", "visibleTitle": "REACTOR OVERHEATING"},
        ],
    },
    5627: {
        "sourceId": "SRC-EVENT-5627",
        "bgaKey": "Event_RiseOfTheMachine",
        "ruleId": "SEM-EVENT-RISE-OF-THE-MACHINE-001",
        "sentences": [
            _sentence("EV5627-MOVE-01", "movement", "All [intruder] in each [corridorNWSE] move."),
            _sentence("EV5627-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5627-MAIN-01", "main", "Place a [malfunction] on the [robot]."),
            _sentence("EV5627-MAIN-02", "main", "Place a [malfunction] in a Room with the [robot]."),
            _sentence("EV5627-MAIN-03", "main", "Each [character] in that Room loses 2 [characterHealth]."),
            _sentence("EV5627-SECONDARY-01", "secondary", "Place a [noise] in each Unexplored\nCorridor without a [noise]."),
        ],
        "variantDifference": "The licensed record normalizes placeholders and line grouping; the official rulebook and scan occurrences retain exact card layout independently.",
        "officialOccurrences": [
            {"sourceId": "SRC-RULEBOOK", "locator": "printed page 14 / RB-P14-V01 / rulebook_text lines 3207–3225", "visibleTitle": "RISE OF THE MACHINE"},
        ],
    },
    5628: {
        "sourceId": "SRC-EVENT-5628",
        "bgaKey": "Event_ShortCircuit",
        "ruleId": "SEM-EVENT-SHORT-CIRCUIT-001",
        "sentences": [
            _sentence("EV5628-MOVE-01", "movement", "All [intruder] in each [corridorNESW] move."),
            _sentence("EV5628-MOVE-02", "movement", "Then, all [intruder] in every Room move."),
            _sentence("EV5628-MAIN-01", "main", "In Sections with an [lifeSupportActive]:\nPlace a [fire] in each Room with a [malfunction]."),
            _sentence("EV5628-SECONDARY-01", "secondary", "Each [character] in a Room without a [secure]\nresolves [noiseDieHazard]."),
        ],
        "variantDifference": "The licensed occurrence splits the conditional heading and placement into separate array entries; the official/TTS card sentence boundary is retained.",
        "officialOccurrences": [
            {"sourceId": "SRC-RULEBOOK", "locator": "printed page 31 / RB-P31-V01 and RB-P31-V02 / rulebook_text lines 5308–5341", "visibleTitle": "SHORT CIRCUIT"},
        ],
    },
}

EVENT_RULE_IDS = [EVENT_DEFINITIONS[card_id]["ruleId"] for card_id in sorted(EVENT_DEFINITIONS)]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_bga_events(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"const EVENT_CARDS_DATA = \{\n(.*?)\n\};", text, re.S)
    if not match:
        raise AssertionError("EVENT_CARDS_DATA block not found")
    block = match.group(1)
    records: dict[str, dict] = {}
    for row in re.finditer(r"^  (Event_[A-Za-z0-9]+): \{\n(.*?)^  \},$", block, re.M | re.S):
        key, body = row.groups()
        parsed: dict[str, object] = {}
        for field in ("name", "intrudersEffectDesc", "primaryEffectDesc", "secondaryEffectDesc"):
            field_match = re.search(rf"^    {field}: ", body, re.M)
            if not field_match:
                raise AssertionError(f"missing {field} in {key}")
            start = field_match.end()
            opening = body[start]
            if opening not in {"'", "["}:
                raise AssertionError(f"unsupported {field} literal in {key}")
            scalar_string = opening == "'"
            in_string = scalar_string
            depth = 0
            escaped = False
            end = None
            for index in range(start, len(body)):
                character = body[index]
                if in_string:
                    if escaped:
                        escaped = False
                    elif character == "\\":
                        escaped = True
                    elif character == "'" and index > start:
                        if scalar_string:
                            end = index + 1
                            break
                        in_string = False
                    continue
                if character == "'":
                    in_string = True
                    continue
                if character == "[":
                    depth += 1
                elif character == "]":
                    depth -= 1
                    if depth == 0:
                        end = index + 1
                        break
            if end is None:
                raise AssertionError(f"unterminated {field} literal in {key}")
            literal = body[start:end]
            parsed[field] = ast.literal_eval(literal)
        parsed["sourceBlockText"] = row.group(0)
        records[key] = parsed
    if len(records) != 20:
        raise AssertionError(f"expected 20 BGA Events, got {len(records)}")
    return records


def build_event_source_index(repo: Path) -> dict:
    corpus = json.loads((repo / "assets/tts-mod/extract/card-text-corpus.json").read_text(encoding="utf-8"))
    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    progress = json.loads((repo / "assets/tts-mod/extract/vision-progress.json").read_text(encoding="utf-8"))
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    provenance = json.loads((repo / "assets/tts-mod/extract/card-provenance-inventory.json").read_text(encoding="utf-8"))
    roles = json.loads((repo / "assets/tts-mod/extract/v2/lua_roles.json").read_text(encoding="utf-8"))
    backlog = json.loads((repo / "docs/rules/semantics/backlog.json").read_text(encoding="utf-8"))
    backlog_by_id = {row["semanticUnitId"]: row for row in backlog["units"]}
    secondary_index = json.loads((repo / "docs/rules/source-extraction/secondary-evidence-index.json").read_text(encoding="utf-8"))
    bga = _parse_bga_events(repo / BGA_EVENT_PATH)

    role = next(row for row in roles if row.get("role") == "eventDeck" and row.get("guid") == BASE_EVENT_DECK_GUID)
    deck_card_ids = sorted(int(value) for value in role["deck_nums"])
    if deck_card_ids != list(range(5609, 5629)) or role.get("n_urls") != 21:
        raise AssertionError("base Event TTS role/card IDs changed")

    table = next(
        row
        for row in secondary_index["licensedDigital"]["structuredIndex"]["tables"]
        if row["name"] == "EVENT_CARDS_DATA"
    )
    if table["count"] != 20 or set(table["keys"]) != set(bga):
        raise AssertionError("licensed Event index changed")

    faces: dict[int, dict] = {}
    shared_back = None
    for provenance_row in provenance:
        for obj in provenance_row.get("objects", []):
            if obj.get("key") == "BackURL" and obj.get("guid") == BASE_EVENT_DECK_GUID:
                shared_back = provenance_row
            if obj.get("key") != "FaceURL" or obj.get("gmnotes") != "event" or not obj.get("cardId"):
                continue
            if ["DeckCustom", BASE_EVENT_DECK_GUID, ""] not in obj.get("parent", []):
                continue
            card_id = int(obj["cardId"]) // 100
            if card_id not in deck_card_ids:
                continue
            source_path = "assets/tts-mod/extract/v2-dl/tree/" + provenance_row["file"]
            if card_id in faces:
                raise AssertionError(f"duplicate base Event cardId {card_id}")
            faces[card_id] = {"provenance": provenance_row, "object": obj, "sourcePath": source_path}
    if set(faces) != set(deck_card_ids) or shared_back is None:
        raise AssertionError("base Event face/back provenance closure failed")

    rows = []
    for card_id in deck_card_ids:
        definition = EVENT_DEFINITIONS[card_id]
        face = faces[card_id]
        source_path = face["sourcePath"]
        source_file = repo / source_path
        corpus_row = corpus_by_path[source_path]
        progress_row = progress_by_path[source_path]
        source_sha = _sha(source_file)
        if source_sha != corpus_row["sourceSha256"] or source_sha != progress_row["sha256"]:
            raise AssertionError(f"Event source hash drift: {card_id}")
        if not corpus_row.get("rulesTextPresent") or corpus_row.get("extractionState") not in {"verified-canonical", "draft-full"}:
            raise AssertionError(f"Event corpus readiness drift: {card_id}")
        body = corpus_row["printedData"]["body"]
        visible_title = (corpus_row.get("printedData") or {}).get("title") or (progress_row.get("semanticRead") or {}).get("title")
        if not visible_title:
            raise AssertionError(f"Event title evidence missing: {card_id}")
        progress_body = (progress_row.get("semanticRead") or {}).get("body")
        if card_id != 5614 and progress_body != body:
            raise AssertionError(f"Event transcription projection drift: {card_id}")
        cursor = 0
        sentence_rows = []
        for sequence, sentence in enumerate(definition["sentences"], 1):
            start = body.find(sentence["exactText"], cursor)
            if start < 0:
                raise AssertionError(f"Event sentence boundary drift: {card_id} {sentence['sentenceId']}")
            end = start + len(sentence["exactText"])
            sentence_rows.append({**sentence, "sequence": sequence, "start": start, "end": end})
            cursor = end
        bga_row = bga[definition["bgaKey"]]
        backlog_id = "CARD:" + source_sha[:16]
        backlog_row = backlog_by_id.get(backlog_id)
        if not backlog_row or backlog_row.get("sourcePath") != source_path or backlog_row.get("sourceLocator") != source_sha:
            raise AssertionError(f"Event backlog occurrence drift: {card_id}")
        title_evidence_path = "assets/tts-mod/extract/selected-card-text-evidence.json" if card_id == 5614 else "assets/tts-mod/extract/vision-progress.json"
        rows.append(
            {
                "eventOccurrenceId": f"TTS-EVENT-{card_id}-FACE",
                "ttsDeckGuid": BASE_EVENT_DECK_GUID,
                "ttsCardGuid": face["object"]["guid"],
                "ttsCardId": card_id,
                "ttsRole": "eventDeck",
                "ttsClassification": face["object"]["gmnotes"],
                "sourceId": definition["sourceId"],
                "sourcePath": source_path,
                "sourceSha256": source_sha,
                "sourceAuthority": "source-bound-component-scan",
                "sourceVersion": f"TTS base Event face / deck {BASE_EVENT_DECK_GUID} / cardId {card_id}",
                "corpusEvidencePath": "assets/tts-mod/extract/card-text-corpus.json",
                "provenanceEvidencePath": "assets/tts-mod/extract/card-provenance-inventory.json",
                "titleEvidencePath": title_evidence_path,
                "visibleTitle": visible_title,
                "printedBody": body,
                "extractionState": corpus_row["extractionState"],
                "rulesInformationReadiness": corpus_row["rulesInformationReadiness"],
                "sentences": sentence_rows,
                "semanticRuleId": definition["ruleId"],
                "backlogUnitId": backlog_id,
                "bgaOccurrence": {
                    "sourceId": BGA_EVENT_SOURCE_ID,
                    "sourcePath": BGA_EVENT_PATH,
                    "sourceSha256": _sha(repo / BGA_EVENT_PATH),
                    "sourceVersion": "licensed BGA immutable build 260622-1220 / EVENT_CARDS_DATA",
                    "table": "EVENT_CARDS_DATA",
                    "key": definition["bgaKey"],
                    "name": bga_row["name"],
                    "intrudersEffectDesc": bga_row["intrudersEffectDesc"],
                    "primaryEffectDesc": bga_row["primaryEffectDesc"],
                    "secondaryEffectDesc": bga_row["secondaryEffectDesc"],
                    "sourceBlockText": bga_row["sourceBlockText"],
                    "variantDifference": definition["variantDifference"],
                },
                "officialOccurrences": definition.get("officialOccurrences", []),
                "joinEvidence": {
                    "identityJoin": "explicit occurrence crosswalk",
                    "titleOnlyJoin": False,
                    "basis": [
                        "TTS base Event deck role and exact cardId",
                        "FaceURL provenance under deck 0d3dae",
                        "closed-corpus source path and live SHA-256",
                        "visible title plus ordered sentence evidence",
                        "explicit licensed EVENT_CARDS_DATA key plus ordered effect fields",
                    ],
                },
            }
        )

    shared_back_path = "assets/tts-mod/extract/v2-dl/tree/" + shared_back["file"]
    return {
        "schemaVersion": 1,
        "recordType": "semantic-event-source-index",
        "scope": "base-game Event face occurrences; source versions remain independent",
        "derivationPolicy": "Derive faces from TTS role/cardId/FaceURL provenance, close each against corpus bytes and backlog tuple, and crosswalk explicitly to the licensed table without title-only identity joins.",
        "counts": {
            "eventIdentities": 20,
            "ttsFaceOccurrences": 20,
            "ttsSharedBackOccurrencesExcluded": 1,
            "canonicalCorpusFaces": sum(row["extractionState"] == "verified-canonical" for row in rows),
            "sourceBoundDraftFaces": sum(row["extractionState"] == "draft-full" for row in rows),
            "licensedDigitalOccurrences": len(bga),
            "officialVisibleComponentOccurrences": sum(len(row["officialOccurrences"]) for row in rows),
            "backlogTuples": len(rows),
        },
        "familyCountEvidence": {
            "officialRulebook": {"sourcePath": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf", "locator": "unprinted PDF page 3 / RB-P03-V01", "printedCount": 20},
            "ttsRole": {"sourcePath": "assets/tts-mod/extract/v2/lua_roles.json", "deckGuid": BASE_EVENT_DECK_GUID, "nUrls": role["n_urls"], "faceCardIds": deck_card_ids, "faceCount": len(rows), "sharedBackCount": 1},
            "licensedDigital": {"sourcePath": BGA_EVENT_PATH, "indexPath": "docs/rules/source-extraction/secondary-evidence-index.json", "table": "EVENT_CARDS_DATA", "count": len(bga), "keys": sorted(bga)},
            "backlog": {"sourcePath": "docs/rules/semantics/backlog.json", "count": len(rows), "unitIds": [row["backlogUnitId"] for row in rows]},
        },
        "excludedSharedBack": {"sourcePath": shared_back_path, "sourceSha256": _sha(repo / shared_back_path), "reason": "shared non-operative Event back; not an Event identity/effect"},
        "events": rows,
    }


def event_source_registry_rows(event_source_index: dict) -> list[dict]:
    rows = []
    for event in event_source_index["events"]:
        rows.append(
            {
                "sourceId": event["sourceId"],
                "authority": event["sourceAuthority"],
                "version": event["sourceVersion"],
                "path": event["sourcePath"],
                "sha256": event["sourceSha256"],
                "occurrenceId": event["eventOccurrenceId"],
                "evidenceIndexPath": event["corpusEvidencePath"],
                "evidenceRecord": event["sourceSha256"],
                "provenanceIndexPath": event["provenanceEvidencePath"],
            }
        )
    rows.append(
        {
            "sourceId": BGA_EVENT_SOURCE_ID,
            "authority": "licensed-digital-secondary",
            "version": "licensed BGA immutable build 260622-1220 / EVENT_CARDS_DATA",
            "path": BGA_EVENT_PATH,
            "sha256": event_source_index["events"][0]["bgaOccurrence"]["sourceSha256"],
            "occurrenceId": "EVENT_CARDS_DATA",
            "evidenceIndexPath": "docs/rules/source-extraction/secondary-evidence-index.json",
            "evidenceRecord": "EVENT_CARDS_DATA",
        }
    )
    return rows


def _target(target_id: str, eligible_taxa: list[str], *, mode: str = "deterministic-state-filter", minimum: int = 0, maximum=None) -> dict:
    return {
        "targetId": target_id,
        "selectorRef": "rules-system",
        "eligibleTaxonIds": eligible_taxa,
        "cardinality": {"min": minimum, "max": maximum},
        "selectionMode": mode,
        "visibility": "public",
    }


def build_event_records(repo: Path, event_source_index: dict, record, assertion, timing, participant, condition, decision, operation) -> list[dict]:
    event_by_card = {row["ttsCardId"]: row for row in event_source_index["events"]}
    records = []

    # Reusable procedures exercised by multiple Event faces.
    records.append(
        record(
            "SEM-EVENT-INTRUDER-MOVEMENT-001",
            "Event-card Intruder movement",
            "source-backed",
            "procedure",
            "official-errata",
            "source-composed",
            [
                assertion("SA-EVENT-MOVE-RB", "SRC-RULEBOOK", "printed pages 15 and 30–31 / Event movement", ["preconditions", "targets", "operations", "partialResolution"], "For each printed Event movement sentence, resolve matching Intruder groups from the Facility top-left row by row toward the closest eligible Character, with source-defined route, Door, capacity, and Attack rules.", "docs/rulebooks/rulebook_text.txt:lines 3279–3287, 5125–5159, 5324–5355"),
                assertion("SA-EVENT-MOVE-FAQ", "SRC-FAQ", "General rules / FQ-P02-U12", ["preconditions", "targets", "operations"], "Q: Do Intruders move towards Characters in the Lander?\nA: No.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U12"),
            ],
            ["term.event-card", "icon.intruder", "term.corridor", "term.room"],
            ["tax.entity.component.card.event", "tax.entity.agent.intruder", "tax.entity.spatial.corridor", "tax.entity.spatial.room"],
            [],
            timing("TW-EVENT-INTRUDER-MOVE", "tax.process.temporal.phase.event", "during-event-card-resolution", "per-printed-movement-sentence"),
            [participant("P-RULES", "rules-system"), participant("P-INTRUDERS", "collection", "tax.entity.agent.intruder"), participant("P-CHARACTERS", "collection", "tax.entity.agent.character")],
            "must",
            [condition("C-CALLER-SCOPE", "predicate", [{"predicate": "caller supplies the exact printed Corridor orientation(s), every-Room scope, or no-movement instruction"}], ["SA-EVENT-MOVE-RB"])],
            [],
            [{"informationId": "I-EVENT-MOVEMENT", "subjectRef": "eligible Intruder groups, route, movement, Door/capacity result, and entry Attack", "audience": "public", "revealTrigger": "resolution", "secrecy": "none"}],
            [],
            [_target("T-EVENT-MOVING-GROUPS", ["tax.entity.agent.intruder"])],
            [
                operation("S01", 1, "select-target", "must", "P-RULES", "matching Intruder groups in caller's printed origin scope", ["SA-EVENT-MOVE-RB"], target_ref="T-EVENT-MOVING-GROUPS", notes="Resolve groups from Facility top-left row by row; do not use Event display title as a dispatcher."),
                operation("S02", 2, "evaluate-condition", "must", "P-RULES", "closest eligible on-map Character and shortest route; Characters in the Lander are not eligible", ["SA-EVENT-MOVE-RB", "SA-EVENT-MOVE-FAQ"]),
                operation("S03", 3, "move-entity", "if-able", "selected Intruder group", "one adjacent Room/Corridor on the resolved route", ["SA-EVENT-MOVE-RB"], notes="Closed Door is destroyed instead of traversal; a full Corridor uses the stated equal-route/capacity fallback."),
                operation("S04", 4, "invoke-process", "if-able", "each Intruder entering a Room with a Character", "Secure-entry/Attack resolution", ["SA-EVENT-MOVE-RB"], invoke="SEM-SECURE-ENTRY-001"),
            ],
            {"policy": "source-conditional-steps", "unit": "one printed movement sentence and one origin group", "onImpossible": "apply route/capacity waiting rules per group; do not invent a destination or move toward a Character in the Lander"},
            {"kind": "instantaneous-subprocedure"},
            {"policy": "once per caller-selected group per printed sentence"},
            [],
            [],
            [],
        )
    )

    records.append(
        record(
            "SEM-NOISE-MARKER-001",
            "Resolve one existing Noise marker",
            "source-backed",
            "procedure",
            "official-errata",
            "source-composed",
            [
                assertion("SA-NOISE-MARKER-RB", "SRC-RULEBOOK", "printed page 25 / Resolving Noise markers", ["preconditions", "operations", "partialResolution"], "Remove the Noise marker, draw an Intruder token, and resolve its back in the same Corridor using the current Intruder Help side and Corridor context.", "docs/rules/02-character-actions.md:Noise-marker constraints"),
                assertion("SA-NOISE-MARKER-FAQ", "SRC-FAQ", "General rules / FQ-P02-U08", ["preconditions", "operations", "partialResolution"], "Q: For events with “Resolve a Noise marker in each Unexplored corridor” effect – do those Corridors must have Noise markers placed?\nA: Yes. You cannot resolve a Noise marker, if it does not exist in a Corridor.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U08"),
            ],
            ["icon.noise", "term.corridor", "icon.intruder"],
            ["tax.entity.component.marker.noise", "tax.entity.spatial.corridor", "tax.entity.agent.intruder"],
            [],
            timing("TW-NOISE-MARKER", "tax.entity.spatial.corridor", "when-triggered", "per-existing-marker"),
            [participant("P-RULES", "rules-system")],
            "must",
            [condition("C-NOISE-EXISTS", "predicate", [{"predicate": "the caller Corridor currently contains a Noise marker"}], ["SA-NOISE-MARKER-RB", "SA-NOISE-MARKER-FAQ"])],
            [],
            [{"informationId": "I-NOISE-MARKER", "subjectRef": "removed marker, drawn token, token back, placed Intruders, and token lifecycle", "audience": "public", "revealTrigger": "resolution", "secrecy": "none"}],
            [],
            [],
            [
                operation("S01", 1, "remove-component", "must", "P-RULES", "the existing Noise marker in caller Corridor", ["SA-NOISE-MARKER-RB", "SA-NOISE-MARKER-FAQ"]),
                operation("S02", 2, "draw-random", "must", "P-RULES", "1 Intruder token; use its back for Corridor context", ["SA-NOISE-MARKER-RB"]),
                operation("S03", 3, "invoke-selected-process", "must", "P-RULES", "exact Corridor-context Intruder Help row selected by Queen side and token back", ["SA-NOISE-MARKER-RB"]),
            ],
            {"policy": "all-or-nothing-selection", "unit": "one existing Noise marker", "onImpossible": "without an existing marker, do nothing; never create a marker in order to resolve it"},
            {"kind": "instantaneous-procedure"},
            {"policy": "one token resolution per removed marker"},
            [],
            [],
            [],
        )
    )
    records[-1]["operations"][2]["dispatchRuleIds"] = [
        "SEM-IH-QA-C-01", "SEM-IH-QA-C-02", "SEM-IH-QA-C-03",
        "SEM-IH-QD-C-01", "SEM-IH-QD-C-02", "SEM-IH-QD-C-03",
    ]

    records.append(
        record(
            "SEM-NOISE-HAZARD-001",
            "Resolve a direct Hazard result",
            "source-backed",
            "procedure",
            "official-primary",
            "source-composed",
            [assertion("SA-NOISE-HAZARD", "SRC-RULEBOOK", "printed page 25 / Hazard result and Surprise Attacks", ["preconditions", "operations", "partialResolution"], "For a Hazard result, draw an Intruder token, use only its front type in the Character's Room, and resolve the current Queen-side Room-context Help row including entry Attack and token lifecycle.", "docs/rules/02-character-actions.md:Noise-roll procedure")],
            ["icon.noiseDieHazard", "icon.intruder", "term.room"],
            ["tax.entity.agent.intruder", "tax.entity.spatial.room"],
            [],
            timing("TW-NOISE-HAZARD", "tax.process.sequence.noise-roll", "when-triggered", "per-Hazard-result"),
            [participant("P-RULES", "rules-system"), participant("P-AFFECTED-CHARACTER", "affected", "tax.entity.agent.character")],
            "must",
            [],
            [],
            [{"informationId": "I-HAZARD", "subjectRef": "drawn token front, placed Intruder, Secure/Attack result, and token lifecycle", "audience": "public", "revealTrigger": "resolution", "secrecy": "token back is ignored for this result"}],
            [],
            [],
            [
                operation("S01", 1, "draw-random", "must", "P-RULES", "1 Intruder token; use its front only", ["SA-NOISE-HAZARD"]),
                operation("S02", 2, "invoke-selected-process", "must", "P-RULES", "exact Room-context Intruder Help row selected by Queen side and token front", ["SA-NOISE-HAZARD"]),
            ],
            {"policy": "source-limited-components", "unit": "one Hazard token result", "onImpossible": "the selected Help row controls finite placement and lifecycle; do not read the token back"},
            {"kind": "instantaneous-procedure"},
            {"policy": "one token result per Hazard"},
            [],
            [],
            [],
        )
    )
    records[-1]["operations"][1]["dispatchRuleIds"] = ["SEM-IH-QA-R-01", "SEM-IH-QA-R-02", "SEM-IH-QD-R-01", "SEM-IH-QD-R-02"]

    records.append(
        record(
            "SEM-SECURE-ENTRY-001",
            "Secure token on Intruder entry",
            "source-backed-with-open-question",
            "procedure",
            "official-errata",
            "open-alternatives",
            [
                assertion("SA-SECURE-ENTRY-RB", "SRC-RULEBOOK", "printed page 23 / Resolving Secure tokens", ["preconditions", "operations", "partialResolution", "unresolvedQuestionRefs"], "Whenever an Intruder enters a Room with at least one Character and a Secure token, discard one Secure instead of resolving that Intruder Attack.", "docs/rulebooks/rulebook_text.txt:lines 4396–4413"),
                assertion("SA-SECURE-ENTRY-FAQ", "SRC-FAQ", "General rules / FQ-P02-U13", ["preconditions", "operations"], "Q: Do Secure tokens prevent Attacks from Intruder being placed in the room?\nA: Yes.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U13"),
            ],
            ["icon.secure", "icon.intruder", "term.attack"],
            ["tax.entity.component.token.secure", "tax.entity.agent.intruder", "tax.process.attack", "tax.entity.spatial.room"],
            [],
            timing("TW-SECURE-ENTRY", "tax.process.attack", "before-attack-resolution", "per-entering-Intruder"),
            [participant("P-RULES", "rules-system"), participant("P-ENTERING-INTRUDER", "actor", "tax.entity.agent.intruder"), participant("P-TARGET", "affected", "tax.entity.agent.character")],
            "must",
            [condition("C-ENTRY", "all", [{"predicate": "Intruder enters or is placed in a Room"}, {"predicate": "Room contains at least one Character"}], ["SA-SECURE-ENTRY-RB", "SA-SECURE-ENTRY-FAQ"])],
            [],
            [{"informationId": "I-SECURE-ENTRY", "subjectRef": "entering Intruder, Secure count, prevented or resolved Attack", "audience": "public", "revealTrigger": "entry", "secrecy": "none"}],
            [],
            [],
            [
                operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "OQ-007 simultaneous multi-Intruder Secure consumption", ["SA-SECURE-ENTRY-RB"], conditions=["more than one Intruder enters simultaneously"]),
                operation("S02", 2, "remove-component", "must", "P-RULES", "1 Secure token instead of this entry Attack", ["SA-SECURE-ENTRY-RB", "SA-SECURE-ENTRY-FAQ"], conditions=["a Secure token is available for this entering Intruder"]),
                operation("S03", 3, "invoke-process", "must", "P-ENTERING-INTRUDER", "Intruder Attack", ["SA-SECURE-ENTRY-RB"], conditions=["no Secure token prevents this entry Attack"], invoke="SEM-INT-004"),
            ],
            {"policy": "replacement-effect", "unit": "one entering Intruder Attack", "onImpossible": "single-entry behavior is explicit; simultaneous multi-entry allocation remains OQ-007 with no default"},
            {"kind": "one-entry-attack"},
            {"policy": "one Secure may replace one entry Attack; simultaneous grouping unresolved"},
            [],
            ["OQ-007"],
            [],
        )
    )

    records.append(
        record(
            "SEM-FIRE-SPREAD-001",
            "Spread Fire between Rooms",
            "source-backed-with-open-question",
            "procedure",
            "official-errata",
            "open-alternatives",
            [
                assertion("SA-FIRE-SPREAD-RB", "SRC-RULEBOOK", "printed pages 22–23 / Doors and spreading Fire; Fire markers", ["preconditions", "targets", "operations", "partialResolution", "unresolvedQuestionRefs"], "Spreading Fire places Fire in neighboring Rooms according to the caller card; Closed Doors block the spread, an existing Fire is ignored, and exhausting Fire markers destroys the Facility.", "docs/rulebooks/rulebook_text.txt:lines 4284–4287, 4436–4456, 4465–4468"),
                assertion("SA-FIRE-SPREAD-FAQ", "SRC-FAQ", "General rules / FQ-P02-U09", ["preconditions", "targets", "operations"], "Q: What happens when Fire is to be spread through an Open Corridor?\nA: Nothing. Do not place the Fire marker.", "docs/rules/source-extraction/faq-v1.2-source-extraction.json:FQ-P02-U09"),
            ],
            ["icon.fire", "term.room", "term.corridor"],
            ["tax.entity.component.marker.fire", "tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.entity.spatial.door"],
            [],
            timing("TW-FIRE-SPREAD", "tax.entity.component.marker.fire", "when-triggered", "per-printed-spread-sentence"),
            [participant("P-RULES", "rules-system")],
            "must",
            [condition("C-CALLER-FIRE-SCOPE", "predicate", [{"predicate": "caller supplies exact source-Room and Corridor/destination filters from one printed sentence"}], ["SA-FIRE-SPREAD-RB"])],
            [],
            [{"informationId": "I-FIRE-SPREAD", "subjectRef": "source Rooms, paths, destination Rooms, marker supply, and Facility destruction", "audience": "public", "revealTrigger": "resolution", "secrecy": "none"}],
            [],
            [_target("T-FIRE-DESTINATIONS", ["tax.entity.spatial.room"], mode="unresolved-order")],
            [
                operation("S01", 1, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-009 source-Room snapshot versus newly placed Fire propagation", ["SA-FIRE-SPREAD-RB"]),
                operation("S02", 2, "select-target", "must", "P-RULES", "caller-eligible neighboring destination Rooms", ["SA-FIRE-SPREAD-RB", "SA-FIRE-SPREAD-FAQ"], target_ref="T-FIRE-DESTINATIONS", notes="Closed Doors block; an Open Corridor with no eligible destination places nothing."),
                operation("S03", 3, "place-component", "if-able", "P-RULES", "1 Fire marker in each resolved destination Room", ["SA-FIRE-SPREAD-RB", "SA-FIRE-SPREAD-FAQ"], target_ref="T-FIRE-DESTINATIONS", notes="Ignore destinations already containing Fire; if a required Fire marker is unavailable, Facility destruction triggers."),
                operation("S04", 4, "invoke-process", "if-able", "P-RULES", "Facility destruction and endgame", ["SA-FIRE-SPREAD-RB"], conditions=["a required Fire marker is unavailable"], invoke="SEM-ENDGAME-001"),
            ],
            {"policy": "source-conditional-steps", "unit": "one printed spread sentence", "onImpossible": "path blocking/existing Fire/exhaustion are explicit; source-set propagation remains SEM-Q-009 with no default"},
            {"kind": "instantaneous-procedure"},
            {"policy": "one Fire marker per resolved destination Room"},
            [],
            ["SEM-Q-009"],
            [],
        )
    )

    records.append(
        record(
            "SEM-INFECTION-PROCEDURE-001",
            "Infection Procedure",
            "source-backed",
            "procedure",
            "official-primary",
            "verbatim-structure",
            [assertion("SA-INFECTION-PROCEDURE", "SRC-RULEBOOK", "printed page 38 / Infection Procedure", ["timing", "operations", "informationPolicy", "partialResolution"], "Scan all Contamination cards in hand; if any reads INFECTED and no Larva is present, place one Larva; then place all Contaminations from hand on top of the discard pile.", "docs/rulebooks/rulebook_text.txt:lines 6079–6098")],
            ["term.infection-procedure", "term.contamination-card", "term.infected", "term.larva"],
            ["tax.process.procedure.infection", "tax.entity.component.card.contamination", "tax.state.infection.infected", "tax.entity.agent.intruder.larva"],
            [],
            timing("TW-INFECTION-PROCEDURE", "tax.process.procedure.infection", "when-triggered", "per-invocation"),
            [participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")],
            "must",
            [],
            [],
            [
                {"informationId": "I-INFECTION-SCAN", "subjectRef": "hidden Contamination text and scan result", "audience": "scanning-player", "revealTrigger": "scan instruction", "secrecy": "card text remains hidden from unauthorized players; disclosure after scanning is not specified"},
                {"informationId": "I-INFECTION-RESULT", "subjectRef": "Larva placement and Contamination discard count", "audience": "public", "revealTrigger": "resolution", "secrecy": "individual hidden scan text remains private"},
            ],
            [],
            [],
            [
                operation("S01", 1, "inspect-private", "must", "P-OWNER", "all Contamination cards in hand", ["SA-INFECTION-PROCEDURE"]),
                operation("S02", 2, "evaluate-condition", "must", "P-OWNER", "whether any scanned card contains INFECTED", ["SA-INFECTION-PROCEDURE"]),
                operation("S03", 3, "place-component", "if-able", "P-RULES", "1 Larva on the Character board", ["SA-INFECTION-PROCEDURE"], conditions=["at least one scanned card is Infected", "Character board has no Larva"]),
                operation("S04", 4, "transition-zone", "must", "P-OWNER", "all Contamination cards in hand", ["SA-INFECTION-PROCEDURE"], transition={"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"}),
            ],
            {"policy": "ordered-complete", "unit": "Infection Procedure step", "onImpossible": "Larva placement is skipped only when one is already present or supply is unavailable; remaining steps continue"},
            {"kind": "instantaneous-procedure"},
            {"policy": "one invocation at a time"},
            [],
            [],
            [],
        )
    )

    records.append(
        record(
            "SEM-ECLOSION-PROCEDURE-001",
            "Eclosion Procedure",
            "source-backed-with-open-question",
            "procedure",
            "official-primary",
            "open-alternatives",
            [assertion("SA-ECLOSION-PROCEDURE", "SRC-RULEBOOK", "printed page 38 / Eclosion Procedure", ["timing", "operations", "informationPolicy", "outcomes", "partialResolution", "unresolvedQuestionRefs"], "Draw four Action cards; check Contamination cards in hand without scanning; if none, discard the hand and live, otherwise die; during the game, place one Adult in the dead Character's Room and it may Attack another Character.", "docs/rulebooks/rulebook_text.txt:lines 6099–6116")],
            ["term.eclosion-procedure", "icon.actionCard", "term.contamination-card", "term.adult"],
            ["tax.process.procedure.eclosion", "tax.entity.component.card.action", "tax.entity.component.card.contamination", "tax.entity.agent.intruder.adult"],
            [],
            timing("TW-ECLOSION-PROCEDURE", "tax.process.procedure.eclosion", "when-triggered", "per-invocation"),
            [participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-OWNER", "controller", "tax.entity.agent.player"), participant("P-RULES", "rules-system")],
            "must",
            [],
            [],
            [
                {"informationId": "I-ECLOSION-HAND", "subjectRef": "drawn and pre-existing hand identities", "audience": "owner-private", "revealTrigger": "source-defined discard/outcome only", "secrecy": "Contamination cards are checked by type without scanning hidden text"},
                {"informationId": "I-ECLOSION-OUTCOME", "subjectRef": "survival/death, Adult placement, and entry Attack", "audience": "public", "revealTrigger": "resolution", "secrecy": "none"},
            ],
            [],
            [],
            [
                operation("S01", 1, "draw-random", "must", "P-OWNER", "4 Action cards", ["SA-ECLOSION-PROCEDURE"]),
                operation("S02", 2, "resolve-open-alternative", "must", "P-OWNER", "OQ-001 pre-existing-hand versus newly drawn Contamination check", ["SA-ECLOSION-PROCEDURE"]),
                operation("S03", 3, "transition-zone", "must", "P-OWNER", "all cards in hand", ["SA-ECLOSION-PROCEDURE"], conditions=["resolved check finds no Contamination"], transition={"from": "tax.scaffold.zone.hand", "to": "tax.scaffold.zone.discard-pile", "positionRef": "sem.position.deck-top"}),
                operation("S04", 4, "set-state", "must", "P-CHARACTER", "sem.state.participation.dead", ["SA-ECLOSION-PROCEDURE"], conditions=["resolved check finds any Contamination"]),
                operation("S05", 5, "place-component", "if-able", "P-RULES", "1 Adult in the dead Character's Room", ["SA-ECLOSION-PROCEDURE"], conditions=["Character dies during the game rather than End of Game"]),
                operation("S06", 6, "invoke-process", "if-able", "placed Adult", "Secure-entry/Attack resolution against another Character in that Room", ["SA-ECLOSION-PROCEDURE"], conditions=["Adult was placed", "another Character is in the Room"], invoke="SEM-SECURE-ENTRY-001"),
            ],
            {"policy": "ordered-complete", "unit": "Eclosion Procedure step", "onImpossible": "OQ-001 remains unresolved; finite Adult placement follows source limits without changing death"},
            {"kind": "instantaneous-procedure"},
            {"policy": "one invocation at a time"},
            [{"condition": "resolved Contamination check is empty", "result": "Character survives"}, {"condition": "resolved Contamination check finds a Contamination", "result": "Character dies"}],
            ["OQ-001"],
            [],
        )
    )

    def build_card(card_id: int) -> dict:
        source = event_by_card[card_id]
        definition = EVENT_DEFINITIONS[card_id]
        code = str(card_id)
        scan_assertion_id = f"SA-EVT-{code}-SCAN"
        procedure_assertion_id = f"SA-EVT-{code}-PROCEDURE"
        bga_assertion_id = f"SA-EVT-{code}-BGA"
        assertions = [
            assertion(scan_assertion_id, definition["sourceId"], f"{source['eventOccurrenceId']} / exact face", ["timing", "preconditions", "decisions", "informationPolicy", "targets", "operations", "partialResolution", "sourceVariants", "unresolvedQuestionRefs"], source["printedBody"], f"docs/rules/semantics/event-source-index.json:{source['eventOccurrenceId']}"),
            assertion(procedure_assertion_id, "SRC-RULEBOOK", "printed pages 15 and 31 / Event resolution, order, and movement", ["timing", "operations", "partialResolution", "targets"], "Resolve the printed movement, main-effect, and secondary-effect sentences in order; ignore only an impossible Event sentence and continue; Character effects use Turn order and Noise-marker effects use Facility top-left row order.", "docs/rules/01-round-and-turns.md:RT-009"),
            assertion(bga_assertion_id, BGA_EVENT_SOURCE_ID, f"EVENT_CARDS_DATA.{definition['bgaKey']}", ["sourceVariants"], source["bgaOccurrence"]["sourceBlockText"], f"docs/rules/semantics/event-source-index.json:{source['eventOccurrenceId']}.bgaOccurrence"),
        ]
        assertions[0]["textKind"] = "verbatim"
        assertions[2]["textKind"] = "verbatim"
        for index, official in enumerate(source["officialOccurrences"], 1):
            assertions.append(assertion(f"SA-EVT-{code}-OFFICIAL-{index:02d}", "SRC-RULEBOOK", official["locator"], ["operations", "sourceVariants", "targets"], f"Official rulebook visible component occurrence titled {official['visibleTitle']} corroborates the current Event occurrence and panel grouping.", "docs/rules/source-extraction/rulebook-visual-obligations.json"))

        faq_by_card = {
            5609: ("FQ-P02-U08", "Q: For events with “Resolve a Noise marker in each Unexplored corridor” effect – do those Corridors must have Noise markers placed?\nA: Yes. You cannot resolve a Noise marker, if it does not exist in a Corridor."),
            5613: ("FQ-P02-U08", "Q: For events with “Resolve a Noise marker in each Unexplored corridor” effect – do those Corridors must have Noise markers placed?\nA: Yes. You cannot resolve a Noise marker, if it does not exist in a Corridor."),
            5615: ("FQ-P02-U08", "Q: For events with “Resolve a Noise marker in each Unexplored corridor” effect – do those Corridors must have Noise markers placed?\nA: Yes. You cannot resolve a Noise marker, if it does not exist in a Corridor."),
            5616: ("FQ-P02-U08", "Q: For events with “Resolve a Noise marker in each Unexplored corridor” effect – do those Corridors must have Noise markers placed?\nA: Yes. You cannot resolve a Noise marker, if it does not exist in a Corridor."),
            5621: ("FQ-P02-U09", "Q: What happens when Fire is to be spread through an Open Corridor?\nA: Nothing. Do not place the Fire marker."),
            5622: ("FQ-P02-U09", "Q: What happens when Fire is to be spread through an Open Corridor?\nA: Nothing. Do not place the Fire marker."),
            5614: ("FQ-P02-U11", "Q: When a card tells me to reshuffle the deck, does it include the card itself?\nA: Yes. Note that it differs from reshuffling the Action deck due to drawing cards. Meaning that, if an Action card allows you to draw more cards, the cards are drawn (which may force you to reshuffle the deck) before the card itself is discarded. In turn, it is not reshuffled."),
            5626: ("FQ-P02-U11", "Q: When a card tells me to reshuffle the deck, does it include the card itself?\nA: Yes. Note that it differs from reshuffling the Action deck due to drawing cards. Meaning that, if an Action card allows you to draw more cards, the cards are drawn (which may force you to reshuffle the deck) before the card itself is discarded. In turn, it is not reshuffled."),
        }
        faq_assertion_id = None
        if card_id in faq_by_card:
            faq_id, faq_text = faq_by_card[card_id]
            faq_assertion_id = f"SA-EVT-{code}-FAQ"
            faq_assertion = assertion(faq_assertion_id, "SRC-FAQ", f"General rules / {faq_id}", ["operations", "partialResolution", "targets", "sourceVariants"], faq_text, f"docs/rules/source-extraction/faq-v1.2-source-extraction.json:{faq_id}")
            faq_assertion["textKind"] = "verbatim"
            assertions.append(faq_assertion)

        supplement_id = None
        if card_id in {5610, 5616, 5617, 5624, 5625}:
            supplement_id = f"SA-EVT-{code}-LIMITS"
            assertions.append(assertion(supplement_id, "SRC-RULEBOOK", "printed pages 21 and 30–31 / Corridor and Intruder limits", ["operations", "partialResolution", "targets", "unresolvedQuestionRefs"], "Corridors hold six Intruder-equivalents (Queen counts four); place as many requested models of a type as available and ignore excess.", "docs/rulebooks/rulebook_text.txt:lines 4141–4149, 5189–5198"))
        if card_id in {5609, 5618, 5619, 5620, 5622, 5623, 5626, 5627}:
            supplement_id = f"SA-EVT-{code}-MARKERS"
            assertions.append(assertion(supplement_id, "SRC-RULEBOOK", "printed pages 22–23 / Malfunction and Fire marker limits", ["operations", "partialResolution", "targets", "unresolvedQuestionRefs"], "A Room already holding the same marker ignores another placement; when no Malfunction marker remains, place Fire in the Room instead if possible; exhausting required Fire destroys the Facility.", "docs/rulebooks/rulebook_text.txt:lines 4368–4375, 4414–4426, 4436–4468"))
        if card_id == 5627:
            assertions.append(assertion(f"SA-EVT-{code}-ROBOT-P22", "SRC-RULEBOOK", "printed page 22 / Malfunction on a Robot", ["operations", "unresolvedQuestionRefs", "sourceVariants"], "A malfunctioned Robot has no text/icons and cannot be used, but effects that only require a Robot can still be used; another Robot Malfunction placement is ignored.", "docs/rulebooks/rulebook_text.txt:lines 4383–4391"))
            assertions.append(assertion(f"SA-EVT-{code}-ROBOT-P37", "SRC-RULEBOOK", "printed page 37 / Malfunction marker on the Robot", ["operations", "unresolvedQuestionRefs", "sourceVariants"], "A Robot with a Malfunction has no Action and all game effects mentioning the Robot are unavailable.", "docs/rulebooks/rulebook_text.txt:lines 6015–6022"))
            assertions.append(assertion(f"SA-EVT-{code}-ROBOT-REVEAL", "SRC-RULEBOOK", "printed pages 8 and 37 / unrevealed Robot", ["operations", "unresolvedQuestionRefs", "sourceVariants"], "The selected Robot card begins face down and the Robot cannot be Activated until a Room first connects to the Hibernatorium, but the checked base rules do not state a general pre-reveal policy for external Robot-referencing effects.", "docs/rulebooks/rulebook_text.txt:lines 2421–2426, 2446–2448, 5982–5996"))

        participants = [participant("P-RULES", "rules-system")]
        information = [{"informationId": f"I-EVT-{code}-PUBLIC", "subjectRef": "drawn Event identity, printed sentences, targets, and results", "audience": "public", "revealTrigger": "Event draw/resolution", "secrecy": "remaining Event-deck order stays unrevealed"}]
        terms = ["term.event-card"]
        taxa = ["tax.entity.component.card.event"]
        named = []
        targets = []
        decisions = []
        unresolved: list[str] = []
        ops = []
        sentence_by_id = {row["sentenceId"]: row for row in source["sentences"]}

        def add(sentence_id, op_type, modality, subject, obj, *, source_ids=None, conditions=None, decision_ref=None, target_ref=None, transition=None, value_change=None, invoke=None, repeat=None, notes=None):
            step = len(ops) + 1
            op = operation(f"S{step:02d}", step, op_type, modality, subject, obj, source_ids or [scan_assertion_id], conditions=conditions, decision_ref=decision_ref, target_ref=target_ref, transition=transition, value_change=value_change, invoke=invoke, repeat=repeat, notes=notes)
            op["sourceSentenceId"] = sentence_id
            op["sourceSection"] = sentence_by_id[sentence_id]["section"]
            ops.append(op)
            return op

        def add_target(target_id, eligible, *, mode="deterministic-state-filter"):
            targets.append(_target(target_id, eligible, mode=mode))
            return target_id

        def add_move(sentence_id, scope):
            target_id = add_target(f"T-{sentence_id}-GROUPS", ["tax.entity.agent.intruder"])
            add(sentence_id, "invoke-process", "must", "P-RULES", scope, source_ids=[scan_assertion_id, procedure_assertion_id], target_ref=target_id, invoke="SEM-EVENT-INTRUDER-MOVEMENT-001")
            terms.extend(["icon.intruder", "term.corridor", "term.room"])
            taxa.extend(["tax.entity.agent.intruder", "tax.entity.spatial.corridor", "tax.entity.spatial.room"])

        def add_character_noise(sentence_id):
            nonlocal participants
            if not any(row["participantId"] == "P-CHARACTERS" for row in participants):
                participants.append(participant("P-CHARACTERS", "collection", "tax.entity.agent.character"))
            target_id = add_target(f"T-{sentence_id}-CHARACTERS", ["tax.entity.agent.character"], mode="deterministic-turn-order")
            add(sentence_id, "invoke-process", "must", "each Character in Turn order", "Noise Roll", target_ref=target_id, invoke="SEM-NOISE-001", repeat={"order": "Turn order", "scope": "each matching Character"})
            terms.extend(["icon.character", "term.noise-roll"])
            taxa.extend(["tax.entity.agent.character", "tax.process.sequence.noise-roll"])

        def add_unexplored_noise_resolution(sentence_id):
            target_id = add_target(f"T-{sentence_id}-NOISE", ["tax.entity.component.marker.noise"])
            source_ids = [scan_assertion_id, procedure_assertion_id] + ([faq_assertion_id] if faq_assertion_id else [])
            add(sentence_id, "invoke-process", "if-able", "P-RULES", "each existing Noise marker in an Unexplored Corridor", source_ids=source_ids, target_ref=target_id, invoke="SEM-NOISE-MARKER-001", repeat={"order": "Facility top-left Corridor row by row", "scope": "each matching existing marker"})
            terms.extend(["icon.noise", "term.unexplored-corridor"])
            taxa.extend(["tax.entity.component.marker.noise", "tax.state.corridor.unexplored"])

        def add_hazard(sentence_id):
            if not any(row["participantId"] == "P-CHARACTERS" for row in participants):
                participants.append(participant("P-CHARACTERS", "collection", "tax.entity.agent.character"))
            target_id = add_target(f"T-{sentence_id}-CHARACTERS", ["tax.entity.agent.character"], mode="deterministic-turn-order")
            add(sentence_id, "invoke-process", "must", "each Character in a Room without a Secure token, in Turn order", "direct Hazard result", target_ref=target_id, invoke="SEM-NOISE-HAZARD-001", repeat={"order": "Turn order", "scope": "each matching Character"})
            terms.extend(["icon.character", "icon.secure", "icon.noiseDieHazard"])
            taxa.extend(["tax.entity.agent.character", "tax.entity.component.token.secure"])

        def add_noise_placement(sentence_id):
            target_id = add_target(f"T-{sentence_id}-CORRIDORS", ["tax.entity.spatial.corridor"])
            add(sentence_id, "place-component", "if-able", "P-RULES", "1 Noise marker in each Unexplored Corridor without one", target_ref=target_id, notes="This is one printed sentence; do not infer a target-level partial-resolution order.")
            terms.extend(["icon.noise", "term.unexplored-corridor"])
            taxa.extend(["tax.entity.component.marker.noise", "tax.state.corridor.unexplored"])

        if card_id == 5609:
            add_move("EV5609-MOVE-01", "Intruders in E–W Corridors")
            add_move("EV5609-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5609-COMPUTER-ROOMS", ["tax.entity.spatial.room"])
            add("EV5609-MAIN-01", "place-component", "if-able", "P-RULES", "1 Malfunction marker in each Computer Room", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, notes="Finite marker/fallback target order remains SEM-Q-008; preserve this as one printed sentence.")
            add_unexplored_noise_resolution("EV5609-SECONDARY-01")
            terms.extend(["icon.malfunction", "icon.computer"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.spatial.room"]); unresolved.append("SEM-Q-008")
        elif card_id == 5610:
            add_move("EV5610-MOVE-01", "Intruders in NE–SW Corridors")
            add_move("EV5610-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5610-CORRIDORS", ["tax.entity.spatial.corridor"], mode="unresolved-order")
            add("EV5610-MAIN-01", "place-component", "if-able", "P-RULES", "up to 4 Adults in each non-Reinforced Corridor adjacent to the Landing Zone", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, repeat={"requestedPerCorridor": 4, "corridorCapacityEquivalentLimit": 6, "finiteModelSupply": True, "allocationOrder": "SEM-Q-007 unresolved"})
            add_character_noise("EV5610-SECONDARY-01")
            terms.extend(["term.adult", "term.reinforced-corridor", "term.landing-zone"]); taxa.extend(["tax.entity.agent.intruder.adult", "tax.state.corridor.reinforced", "tax.entity.spatial.room.landing-zone"]); named.append("NI-0273"); unresolved.append("SEM-Q-007")
        elif card_id == 5611:
            add_move("EV5611-MOVE-01", "Intruders in NE–SW Corridors")
            add_move("EV5611-MOVE-02", "Intruders in every Room")
            add("EV5611-MAIN-01", "transition-zone", "if-able", "P-RULES", "all remaining Queen tokens", conditions=["Queen is alive"], transition={"from": "tax.scaffold.zone.token-pile", "to": "tax.scaffold.zone.intruder-bag"})
            add_noise_placement("EV5611-SECONDARY-01")
            terms.append("term.queen"); taxa.extend(["tax.entity.agent.intruder.queen", "tax.scaffold.zone.intruder-bag"])
        elif card_id == 5612:
            add_move("EV5612-MOVE-01", "Intruders in NW–SE Corridors")
            add_move("EV5612-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5612-NOISE", ["tax.entity.component.marker.noise"])
            add("EV5612-MAIN-01", "invoke-process", "if-able", "P-RULES", "each distinct Noise marker adjacent to at least one Character", source_ids=[scan_assertion_id, procedure_assertion_id], target_ref=target_id, invoke="SEM-NOISE-MARKER-001", repeat={"order": "Facility top-left Corridor row by row", "deduplicate": "one resolution per Noise marker even when adjacent to multiple Characters"})
            add_character_noise("EV5612-SECONDARY-01")
            terms.extend(["icon.noise", "icon.character"]); taxa.extend(["tax.entity.component.marker.noise", "tax.entity.agent.character"])
        elif card_id == 5613:
            add_move("EV5613-MOVE-01", "Intruders in E–W Corridors")
            add_move("EV5613-MOVE-02", "Intruders in every Room")
            participants.append(participant("P-AFFECTED-PLAYERS", "decision-owner", "tax.entity.agent.player"))
            target_id = add_target("T-EV5613-CHARACTERS", ["tax.entity.agent.character"], mode="deterministic-turn-order")
            decisions.append(decision("D-EV5613-RESOURCE", "P-AFFECTED-PLAYERS", "player-choice", 1, 1, False, "public-on-resolution", ["lose 1 Oxygen Tactical Gear token if available", "spend 1 Ammo Tactical Gear token if available"]))
            add("EV5613-MAIN-01", "choose", "must", "each affected Character's controlling Player in Turn order", "one available printed resource branch", decision_ref="D-EV5613-RESOURCE", target_ref=target_id, repeat={"order": "Turn order", "scope": "each matching Character"})
            add("EV5613-MAIN-01", "remove-component", "must", "each affected Character", "selected Oxygen or Ammo token", decision_ref="D-EV5613-RESOURCE", target_ref=target_id)
            add_unexplored_noise_resolution("EV5613-SECONDARY-01")
            terms.extend(["icon.character", "icon.intruder", "icon.oxygenToken", "icon.ammoToken"]); taxa.extend(["tax.entity.agent.character", "tax.entity.component.token.tactical-gear.oxygen", "tax.entity.component.token.tactical-gear.ammo"])
        elif card_id == 5614:
            add("EV5614-MOVE-01", "evaluate-condition", "must", "P-RULES", "no Intruder movement occurs")
            participants.extend([participant("P-CHARACTERS", "collection", "tax.entity.agent.character"), participant("P-AFFECTED-PLAYERS", "controllers", "tax.entity.agent.player")])
            target_larva = add_target("T-EV5614-WITH-LARVA", ["tax.entity.agent.character"], mode="deterministic-turn-order")
            target_other = add_target("T-EV5614-OTHER", ["tax.entity.agent.character"], mode="deterministic-turn-order")
            add("EV5614-MAIN-01", "draw-random", "must", "each Character with a Larva in Turn order", "gain 1 Contamination", target_ref=target_larva, repeat={"order": "Turn order"})
            add("EV5614-MAIN-01", "resolve-open-alternative", "must", "each affected Player", "SEM-Q-006 meaning of the first white-rectangle glyph and resulting discard/own-deck reshuffle", target_ref=target_larva)
            add("EV5614-MAIN-02", "invoke-process", "must", "each Character with a Larva in Turn order", "Eclosion Procedure", target_ref=target_larva, invoke="SEM-ECLOSION-PROCEDURE-001")
            add("EV5614-MAIN-03", "resolve-open-alternative", "must", "each other Character in Turn order", "SEM-Q-006 draw 4 cards denoted by the second unresolved white rectangle", target_ref=target_other)
            add("EV5614-MAIN-03", "invoke-process", "must", "each other Character in Turn order", "Infection Procedure", target_ref=target_other, invoke="SEM-INFECTION-PROCEDURE-001")
            add("EV5614-MAIN-04", "resolve-open-alternative", "must", "each other Character in Turn order", "SEM-Q-006 discard all cards denoted by the third unresolved white rectangle", target_ref=target_other)
            source_ids = [scan_assertion_id, faq_assertion_id]
            add("EV5614-SECONDARY-01", "transition-zone", "must", "P-RULES", "this Leaving the Shell Event card", source_ids=source_ids, transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.deck"})
            add("EV5614-SECONDARY-01", "shuffle", "must", "P-RULES", "Event deck including this Event card", source_ids=source_ids)
            information.extend([
                {"informationId": "I-EV5614-HANDS", "subjectRef": "cards drawn/held for Infection and Eclosion", "audience": "owner-private", "revealTrigger": "source-defined scan/discard only", "secrecy": "card identities and hidden Contamination text are not made public by this Event"},
                {"informationId": "I-EV5614-GLYPHS", "subjectRef": "three source-local white rectangle occurrences", "audience": "public", "revealTrigger": "card reveal", "secrecy": "visual occurrences are public but semantic identity remains unresolved"},
            ])
            terms.extend(["icon.intruder", "icon.character", "term.larva", "term.contamination", "term.eclosion-procedure", "term.infection-procedure"]); taxa.extend(["tax.entity.agent.intruder", "tax.entity.agent.character", "tax.entity.agent.intruder.larva", "tax.state.infection.contamination", "tax.process.procedure.eclosion", "tax.process.procedure.infection", "tax.scaffold.zone.deck"]); named.append("NI-0275"); unresolved.append("SEM-Q-006")
        elif card_id == 5615:
            add_move("EV5615-MOVE-01", "Intruders in NE–SW Corridors")
            add_move("EV5615-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5615-ROOMS", ["tax.entity.spatial.room"])
            add("EV5615-MAIN-01", "remove-component", "if-able", "P-RULES", "1 printed Secure token from each Room", target_ref=target_id, notes="Permanent always-secured status is not a Secure token; retain this as one printed sentence.")
            add_unexplored_noise_resolution("EV5615-SECONDARY-01")
            terms.append("icon.secure"); taxa.extend(["tax.entity.component.token.secure", "tax.entity.spatial.room"])
        elif card_id == 5616:
            add_move("EV5616-MOVE-01", "Intruders in NE–SW Corridors")
            add("EV5616-MAIN-01", "resolve-open-alternative", "must", "P-RULES", "OQ-009 Nest placement before discovery", conditions=["Nest is not discovered"])
            add("EV5616-MAIN-01", "place-component", "if-able", "P-RULES", "1 Larva in the discovered Nest", source_ids=[scan_assertion_id, supplement_id], conditions=["Nest is discovered"])
            add("EV5616-MAIN-01", "invoke-process", "if-able", "placed Larva", "Secure-entry/Attack resolution", conditions=["Larva was placed", "Nest contains a Character"], invoke="SEM-SECURE-ENTRY-001")
            target_id = add_target("T-EV5616-CORRIDORS", ["tax.entity.spatial.corridor"], mode="unresolved-order")
            add("EV5616-MAIN-02", "place-component", "if-able", "P-RULES", "1 Larva in each Unexplored Corridor adjacent to a Character", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, repeat={"requestedPerCorridor": 1, "finiteModelSupply": True, "allocationOrder": "SEM-Q-007 unresolved"})
            add_unexplored_noise_resolution("EV5616-SECONDARY-01")
            terms.extend(["term.larva", "term.nest", "term.unexplored-corridor", "icon.character"]); taxa.extend(["tax.entity.agent.intruder.larva", "tax.entity.spatial.room.nest", "tax.state.corridor.unexplored", "tax.entity.agent.character"]); named.append("NI-0305"); unresolved.extend(["OQ-009", "SEM-Q-007"])
        elif card_id == 5617:
            add_move("EV5617-MOVE-01", "Intruders in NW–SE Corridors")
            add("EV5617-MAIN-01", "resolve-open-alternative", "must", "P-RULES", "OQ-009 Nest placement before discovery", conditions=["Nest is not discovered"])
            add("EV5617-MAIN-01", "place-component", "if-able", "P-RULES", "up to 2 Drones in the discovered Nest", source_ids=[scan_assertion_id, supplement_id], conditions=["Nest is discovered"], repeat={"requested": 2, "finiteModelSupply": True})
            add("EV5617-MAIN-01", "invoke-process", "if-able", "each placed Drone", "Secure-entry/Attack resolution", conditions=["one or more Drones were placed", "Nest contains a Character"], invoke="SEM-SECURE-ENTRY-001", repeat={"scope": "each placed Drone", "simultaneousSecureQuestion": "OQ-007"})
            target_id = add_target("T-EV5617-CORRIDORS", ["tax.entity.spatial.corridor"], mode="unresolved-order")
            add("EV5617-MAIN-02", "place-component", "if-able", "P-RULES", "1 Drone in each Unexplored Corridor in Section C", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, repeat={"requestedPerCorridor": 1, "finiteModelSupply": True, "allocationOrder": "SEM-Q-007 unresolved"})
            add_character_noise("EV5617-SECONDARY-01")
            terms.extend(["term.drone", "term.nest", "term.unexplored-corridor", "term.section-c"]); taxa.extend(["tax.entity.agent.intruder.drone", "tax.entity.spatial.room.nest", "tax.state.corridor.unexplored", "tax.entity.spatial.section.c"]); named.append("NI-0305"); unresolved.extend(["OQ-007", "OQ-009", "SEM-Q-007"])
        elif card_id == 5618:
            add_move("EV5618-MOVE-01", "Intruders in E–W Corridors")
            add_move("EV5618-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5618-LANDING", ["tax.entity.spatial.room.landing-zone"])
            add("EV5618-MAIN-01", "place-component", "if-able", "P-RULES", "1 Fire and 1 Malfunction in the Landing Zone as one printed sentence", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, notes="Do not split this sentence into an invented partial default.")
            add_noise_placement("EV5618-SECONDARY-01")
            terms.extend(["icon.fire", "icon.malfunction", "term.landing-zone"]); taxa.extend(["tax.entity.component.marker.fire", "tax.entity.component.marker.malfunction", "tax.entity.spatial.room.landing-zone"]); named.append("NI-0273")
        elif card_id == 5619:
            add_move("EV5619-MOVE-01", "Intruders in E–W Corridors")
            target_id = add_target("T-EV5619-ROOMS", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5619-MAIN-01", "place-component", "if-able", "P-RULES", "1 Malfunction marker in each Room containing an Intruder", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, notes="Finite marker/fallback target order remains SEM-Q-008.")
            add_hazard("EV5619-SECONDARY-01")
            terms.extend(["icon.malfunction", "icon.intruder"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.agent.intruder", "tax.entity.spatial.room"]); unresolved.append("SEM-Q-008")
        elif card_id == 5620:
            add_move("EV5620-MOVE-01", "Intruders in NE–SW Corridors")
            add_move("EV5620-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5620-LIFE-SUPPORT", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5620-MAIN-01", "set-state", "must", "P-RULES", "all Active Life Support Systems become Inactive")
            add("EV5620-MAIN-02", "place-component", "if-able", "P-RULES", "1 Malfunction marker in each Life Support Control Room", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, notes="Finite marker/fallback target order remains SEM-Q-008.")
            add_noise_placement("EV5620-SECONDARY-01")
            terms.extend(["icon.lifeSupportActive", "icon.lifeSupportInactive", "icon.malfunction"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.spatial.room"]); named.extend(["NI-0278", "NI-0279", "NI-0280"]); unresolved.append("SEM-Q-008")
        elif card_id == 5621:
            add_move("EV5621-MOVE-01", "Intruders in E–W Corridors")
            add_move("EV5621-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5621-FIRE-ROOMS", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5621-MAIN-01", "invoke-process", "must", "P-RULES", "spread Fire from each Fire Room to neighboring Rooms in Active-Life-Support Sections", source_ids=[scan_assertion_id, faq_assertion_id], target_ref=target_id, invoke="SEM-FIRE-SPREAD-001")
            add_character_noise("EV5621-SECONDARY-01")
            terms.extend(["icon.fire", "icon.lifeSupportActive"]); taxa.extend(["tax.entity.component.marker.fire", "tax.entity.spatial.room"]); unresolved.append("SEM-Q-009")
        elif card_id == 5622:
            add_move("EV5622-MOVE-01", "Intruders in NW–SE Corridors")
            add_move("EV5622-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5622-MALFUNCTION-ROOMS", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5622-MAIN-01", "place-component", "if-able", "P-RULES", "1 Malfunction marker in each Room with Fire", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, notes="Finite marker/fallback target order remains SEM-Q-008.")
            fire_target = add_target("T-EV5622-FIRE-DESTINATIONS", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5622-MAIN-02", "invoke-process", "must", "P-RULES", "spread Fire from each Fire Room through its lowest-Noise-value Corridor(s)", source_ids=[scan_assertion_id, faq_assertion_id], target_ref=fire_target, invoke="SEM-FIRE-SPREAD-001")
            add_hazard("EV5622-SECONDARY-01")
            terms.extend(["icon.malfunction", "icon.fire"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.component.marker.fire", "tax.entity.spatial.room"]); unresolved.extend(["SEM-Q-008", "SEM-Q-009"])
        elif card_id == 5623:
            add_move("EV5623-MOVE-01", "Intruders in NW–SE Corridors")
            add_move("EV5623-MOVE-02", "Intruders in every Room")
            active_target = add_target("T-EV5623-ACTIVE-ROOMS", ["tax.entity.spatial.room"])
            add("EV5623-MAIN-01", "place-component", "if-able", "P-RULES", "1 Fire in each Life Support Control Room in an Active-Life-Support Section", source_ids=[scan_assertion_id, supplement_id], target_ref=active_target)
            inactive_target = add_target("T-EV5623-INACTIVE-ROOMS", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5623-MAIN-02", "place-component", "if-able", "P-RULES", "1 Malfunction in each Life Support Control Room in an Inactive-Life-Support Section", source_ids=[scan_assertion_id, supplement_id], target_ref=inactive_target, notes="Finite marker/fallback target order remains SEM-Q-008.")
            add_character_noise("EV5623-SECONDARY-01")
            terms.extend(["icon.lifeSupportActive", "icon.lifeSupportInactive", "icon.fire", "icon.malfunction"]); taxa.extend(["tax.entity.component.marker.fire", "tax.entity.component.marker.malfunction", "tax.entity.spatial.room"]); named.extend(["NI-0278", "NI-0279", "NI-0280"]); unresolved.append("SEM-Q-008")
        elif card_id == 5624:
            add_move("EV5624-MOVE-01", "Intruders in NE–SW Corridors")
            add_move("EV5624-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5624-CORRIDORS", ["tax.entity.spatial.corridor"], mode="unresolved-order")
            add("EV5624-MAIN-01", "remove-component", "if-able", "P-RULES", "Noise marker from each matching Corridor that receives a Drone", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, conditions=["a Drone can enter that Corridor"], notes="Noise is discarded because an Intruder enters; do not discard when no Drone can be placed.")
            add("EV5624-MAIN-01", "place-component", "if-able", "P-RULES", "1 Drone in each Corridor with Noise adjacent to a Character", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, repeat={"requestedPerCorridor": 1, "finiteModelSupply": True, "allocationOrder": "SEM-Q-007 unresolved"})
            add_hazard("EV5624-SECONDARY-01")
            terms.extend(["term.drone", "icon.noise", "icon.character"]); taxa.extend(["tax.entity.agent.intruder.drone", "tax.entity.component.marker.noise", "tax.entity.agent.character", "tax.entity.spatial.corridor"]); unresolved.append("SEM-Q-007")
        elif card_id == 5625:
            add_move("EV5625-MOVE-01", "Intruders in E–W Corridors")
            add_move("EV5625-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5625-QUEEN-SPACE", ["tax.entity.spatial.room", "tax.entity.spatial.corridor"])
            add("EV5625-MAIN-01", "place-component", "if-able", "P-RULES", "up to 2 Drones in the Room/Corridor with the Queen; no entry Attack", source_ids=[scan_assertion_id, supplement_id], conditions=["Queen is on the map"], target_ref=target_id, repeat={"requested": 2, "finiteModelSupply": True, "corridorCapacityEquivalentLimit": 6})
            add("EV5625-MAIN-02", "draw-random", "if-able", "P-RULES", "2 random Drone tokens from their pile into the Intruder bag", source_ids=[scan_assertion_id, supplement_id], conditions=["Queen is not on the map"], repeat={"requested": 2, "selection": "random without inspecting token backs"})
            add_hazard("EV5625-SECONDARY-01")
            information.append({"informationId": "I-EV5625-DRONE-TOKENS", "subjectRef": "backs of random Drone tokens added to the bag", "audience": "hidden-from-all-before-later-draw", "revealTrigger": "source-defined future token resolution", "secrecy": "random token backs are not inspected during this Event"})
            terms.extend(["term.drone", "term.queen"]); taxa.extend(["tax.entity.agent.intruder.drone", "tax.entity.agent.intruder.queen", "tax.scaffold.zone.intruder-bag"])
        elif card_id == 5626:
            add_move("EV5626-MOVE-01", "Intruders in NW–SE, E–W, and NE–SW Corridors")
            add_move("EV5626-MOVE-02", "Intruders in every Room")
            add("EV5626-MAIN-01", "invoke-process", "if-able", "P-RULES", "Autodestruction Procedure", conditions=["Cooling System Room or Reactor Room contains a Malfunction"], invoke="SEM-AUTODESTRUCTION-001")
            target_id = add_target("T-EV5626-ROOMS", ["tax.entity.spatial.room"], mode="unresolved-order")
            add("EV5626-MAIN-02", "place-component", "if-able", "P-RULES", "1 Malfunction marker in each of Cooling System and Reactor Rooms", source_ids=[scan_assertion_id, supplement_id], target_ref=target_id, notes="One printed sentence; finite marker/fallback target order remains SEM-Q-008.")
            source_ids = [scan_assertion_id, faq_assertion_id]
            add("EV5626-SECONDARY-01", "transition-zone", "must", "P-RULES", "this Reactor Overheating Event card", source_ids=source_ids, transition={"from": "sem.zone.card-in-resolution", "to": "tax.scaffold.zone.deck"})
            add("EV5626-SECONDARY-01", "shuffle", "must", "P-RULES", "Event deck including this Event card", source_ids=source_ids)
            terms.extend(["icon.malfunction", "term.autodestruction-procedure"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.process.procedure.autodestruction", "tax.entity.spatial.room.reactor", "tax.scaffold.zone.deck"]); named.extend(["NI-0070", "NI-0392"]); unresolved.append("SEM-Q-008")
        elif card_id == 5627:
            add_move("EV5627-MOVE-01", "Intruders in NW–SE Corridors")
            add_move("EV5627-MOVE-02", "Intruders in every Room")
            add("EV5627-MAIN-01", "resolve-open-alternative", "must", "P-RULES", "SEM-Q-010 Robot-malfunction passage conflict", source_ids=[scan_assertion_id, f"SA-EVT-{code}-ROBOT-P22", f"SA-EVT-{code}-ROBOT-P37"], conditions=["Robot already has a Malfunction"])
            add("EV5627-MAIN-01", "invoke-process", "must", "P-RULES", "source-composed Robot Malfunction placement, including pre-reveal and repeated-placement boundaries", source_ids=[scan_assertion_id, supplement_id, f"SA-EVT-{code}-ROBOT-P22", f"SA-EVT-{code}-ROBOT-P37", f"SA-EVT-{code}-ROBOT-REVEAL"], invoke="SEM-ROBOT-MALFUNCTION-PLACEMENT-001")
            target_id = add_target("T-EV5627-ROBOT-ROOM", ["tax.entity.spatial.room"])
            add("EV5627-MAIN-02", "place-component", "if-able", "P-RULES", "1 Malfunction marker in the Room containing the Robot", source_ids=[scan_assertion_id, supplement_id, f"SA-EVT-{code}-ROBOT-P22", f"SA-EVT-{code}-ROBOT-P37"], target_ref=target_id)
            char_target = add_target("T-EV5627-CHARACTERS", ["tax.entity.agent.character"], mode="deterministic-turn-order")
            add("EV5627-MAIN-03", "change-value", "if-able", "each Character in that Room in Turn order", "Character Health", target_ref=char_target, value_change={"amount": -2, "valueTaxonId": "tax.state.health.point"}, repeat={"order": "Turn order"}, notes="Characters inside the Lander are not in the Room and are not affected.")
            add_noise_placement("EV5627-SECONDARY-01")
            terms.extend(["icon.malfunction", "icon.robot", "icon.character", "icon.characterHealth"]); taxa.extend(["tax.entity.component.marker.malfunction", "tax.entity.agent.robot", "tax.entity.agent.character", "tax.state.health.point"]); unresolved.extend(["SEM-Q-010", "SEM-Q-012"])
        elif card_id == 5628:
            add_move("EV5628-MOVE-01", "Intruders in NE–SW Corridors")
            add_move("EV5628-MOVE-02", "Intruders in every Room")
            target_id = add_target("T-EV5628-ROOMS", ["tax.entity.spatial.room"])
            add("EV5628-MAIN-01", "place-component", "if-able", "P-RULES", "1 Fire in each Room with a Malfunction in Active-Life-Support Sections", target_ref=target_id)
            add_hazard("EV5628-SECONDARY-01")
            terms.extend(["icon.lifeSupportActive", "icon.fire", "icon.malfunction"]); taxa.extend(["tax.entity.component.marker.fire", "tax.entity.component.marker.malfunction", "tax.entity.spatial.room"])
        else:
            raise AssertionError(card_id)

        highest = "official-errata" if faq_assertion_id else "official-primary"
        status = "source-backed-with-open-question" if unresolved else "source-backed"
        source_variant = {
            "variantId": f"SV-EVT-{code}-BGA",
            "sourceId": BGA_EVENT_SOURCE_ID,
            "sourceAssertionId": bga_assertion_id,
            "difference": source["bgaOccurrence"]["variantDifference"],
            "resolution": "Retain the licensed-digital occurrence as secondary evidence; applicable official text and the exact visible component scan control without rewriting either source.",
        }
        result = record(
            definition["ruleId"],
            f"{source['bgaOccurrence']['name']} Event effect",
            status,
            "event",
            highest,
            "open-alternatives" if unresolved else "source-composed",
            assertions,
            terms,
            taxa,
            named,
            timing(f"TW-EVT-{code}", "tax.process.temporal.phase.event", "during-event-card-resolution", "when-this-exact-Event-occurrence-is-drawn"),
            participants,
            "must",
            [],
            decisions,
            information,
            [],
            targets,
            ops,
            {"policy": "per-sentence-continue", "unit": "sourceSentenceId / exact printed Event-card sentence", "onImpossible": "ignore exactly the impossible printed sentence and continue later sentence IDs; do not invent target-level partial resolution or a tie-break, except the explicit finite-Intruder-model rule"},
            {"kind": "instantaneous-event-effect"},
            {"policy": "one resolution per drawn source occurrence"},
            [],
            unresolved,
            [source_variant],
        )
        return result

    records.extend(build_card(card_id) for card_id in sorted(EVENT_DEFINITIONS))
    return records
