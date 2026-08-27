from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


RULEBOOK_TEXT_PATH = "docs/rulebooks/rulebook_text.txt"
VISUAL_PATH = "docs/rules/source-extraction/rulebook-visual-obligations.json"
RAW_TTS_PATH = "assets/tts-mod/extract/nemesis_script_mod.bin"
TTS_ROLES_PATH = "assets/tts-mod/extract/v2/lua_roles.json"
TTS_OBJECTS_PATH = "assets/tts-mod/extract/v2/objects.json"
TTS_LUA_PATH = "assets/tts-mod/extract/v2/lua_script.lua"
TTS_MANIFEST_PATH = "assets/tts-mod/extract/v2-dl/tree/manifest.json"

PINNED_FACILITY_SOURCE_INDEX_HASH = "806d05a72e2c4e1bd77375f43a5041a65a25d1981cbc810e14cec0bb68951be6"
PINNED_TTS_HASHES = {
    RAW_TTS_PATH: "8592c12556630d20c2443a2bd26059ddd8c38d64d91a695c2cfe3542914d1c68",
    TTS_ROLES_PATH: "9f45b811a7ac2375681ac173043db12da2eeaaa359cd2c2b5c0d14db5721c49a",
    TTS_OBJECTS_PATH: "107f917269c73746affce85ef871d983e7d033c32bad3e1e524c3fafd1f220c2",
    TTS_LUA_PATH: "0bcc12026d4e35d26dc5b168b826f861acf82bb486c8a79ea801867af1aface5",
    TTS_MANIFEST_PATH: "8bc6d3add705eae4453d77e0b1ce14b788c4435322214af790eb18251b2145a1",
}

FACILITY_VISUAL_IDS = [
    "RB-P04-V01", "RB-P08-V01", "RB-P08-V02", "RB-P09-V02", "RB-P10-V01",
    "RB-P11-V02", "RB-P12-V01", "RB-P14-V03", "RB-P15-V01", "RB-P15-V02",
    "RB-P16-V01", "RB-P19-V01", "RB-P19-V02", "RB-P20-V01", "RB-P20-V02",
    "RB-P20-V03", "RB-P21-V02", "RB-P22-V02", "RB-P23-V01",
]
FACILITY_PENDING_BACKLOG_IDS = ["RULE:FND-005", *[f"VIS:{x}" for x in FACILITY_VISUAL_IDS]]
FACILITY_RULE_IDS = [
    "SEM-FACILITY-COMPONENT-INVENTORY-001", "SEM-FACILITY-TOPOLOGY-001",
    "SEM-FACILITY-ROOM-SETUP-001", "SEM-FACILITY-CORRIDOR-SETUP-001",
    "SEM-ROUND-TRACK-SETUP-001", "SEM-CHARACTER-BOARD-SETUP-001",
    "SEM-MAP-MARKER-PLACEMENT-001", "SEM-ROOM-TILE-STATE-001",
    "SEM-FACILITY-VISUAL-ASSOCIATIONS-001",
]
FACILITY_QUESTION_IDS = [f"SEM-Q-{x:03d}" for x in range(106, 111)]
SOURCE_SEGMENTS = [
    ("RB-FACILITY-SETUP-ROOM-CORRIDOR", 2399, 2406, "initial Landing Zone Corridor and Room-stack setup"),
    ("RB-FACILITY-SETUP-SECTIONS", 2413, 2444, "Section border, fixed-space, track, system, and Robot setup"),
    ("RB-FACILITY-SETUP-CORRIDOR-SUPPLY", 2461, 2476, "Anti-Aircraft, Eggs, Landing Zone supplies, and hidden Corridor supply"),
    ("RB-FACILITY-MAP-STRUCTURE", 3884, 3951, "three-section Facility, named spaces, and Facility boundary"),
    ("RB-FACILITY-NEST", 3988, 4005, "Nest border-piece space, Eggs, Universal marker, and Fire"),
    ("RB-FACILITY-ROOMS", 4007, 4040, "Room classes, Room anatomy, and printed restrictions"),
    ("RB-FACILITY-CORRIDORS", 4150, 4194, "Reinforced, Empty, Unexplored, Corridor anatomy, and adjacency"),
    ("RB-FACILITY-DOORS", 4243, 4287, "Door slots, orientation, adjacency, blocking, and states"),
    ("RB-FACILITY-MARKERS", 4368, 4470, "Room/Corridor marker surfaces, finite marker limits, and state effects"),
    ("RB-FACILITY-EXPLORATION-PLACEMENT", 4494, 4535, "source-clear Room/Corridor/marker placement and orientation"),
    ("RB-FACILITY-EXPLORATION-DISCOVERY", 4571, 4585, "Exploration trigger, empty slot, map orientation, and Undiscovered state"),
    ("RB-FACILITY-CHARACTER-SETUP", 2630, 2746, "Character-board initial slots, starting placement, and beginning state"),
]
ROOM_SLOT_BOXES = [
    ("A-R01", "A", (230, 104, 72, 65)), ("A-R02", "A", (349, 104, 72, 65)),
    ("A-R03", "A", (290, 207, 71, 65)), ("A-R04", "A", (348, 308, 73, 68)),
    ("A-R05", "A", (290, 413, 71, 64)), ("A-R06", "A", (230, 516, 72, 64)),
    ("A-R07", "A", (349, 515, 72, 65)), ("B-R01", "B", (408, 207, 73, 64)),
    ("B-R02", "B", (528, 207, 72, 64)), ("B-R03", "B", (468, 310, 72, 64)),
    ("B-R04", "B", (408, 413, 73, 64)), ("B-R05", "B", (528, 413, 72, 64)),
    ("B-R06", "B", (468, 515, 71, 65)), ("C-R01", "C", (587, 104, 71, 64)),
    ("C-R02", "C", (706, 104, 71, 64)), ("C-R03", "C", (646, 207, 72, 65)),
    ("C-R04", "C", (587, 310, 71, 64)), ("C-R05", "C", (705, 310, 72, 64)),
    ("C-R06", "C", (646, 413, 71, 64)), ("C-R07", "C", (587, 516, 72, 63)),
    ("C-R08", "C", (706, 516, 71, 63)),
]
EDGE_DIRECTIONS = ["NE", "E", "SE", "SW", "W", "NW"]
INVERSE = {"NE": "SW", "E": "W", "SE": "NW", "SW": "NE", "W": "E", "NW": "SE"}
EXPECTED_TTS_ROLES = {
    "hiddenRoom": ("3d73e4", "Custom_Model", "HIBERNATORIUM", "18", 3),
    "hibUnexplored": ("3817bc", "Custom_Token", "", "-", 2),
    "boarderTile": ("006497", "Custom_Token", "", "-", 2),
    "landingZone": ("8e0bfa", "Custom_Model", "", "14", 3),
    "roomIABag": ("4b5bf1", "Custom_Model_Bag", "", "-", 3),
    "roomIBBag": ("40de95", "Custom_Model_Bag", "", "-", 3),
    "roomICBag": ("94cb25", "Custom_Model_Bag", "", "-", 3),
    "roomIIBag": ("e548bf", "Custom_Model_Bag", "", "-", 3),
    "corridorBag": ("527c41", "Custom_Model_Bag", "", "-", 3),
    "doorBag": ("435a9a", "Custom_Model_Bag", "Doors", "-", 3),
    "roundTile": ("dfc0e5", "Custom_Model", "", "-", 2),
    "autoDestructionToken": ("d24061", "Custom_Tile", "", "-", 2),
    "turnMarker": ("513438", "go_game_piece_white", "turnMarker", "-", 0),
}
EXPECTED_COMPONENT_INVENTORY = [
    {"label": "Round track border pieces", "count": 3}, {"label": "Section border pieces", "count": 3},
    {"label": "Room tiles", "count": 23, "breakdown": {"A": 3, "B": 3, "C": 4, "?": 13}},
    {"label": "Corridor tiles", "count": 40, "breakdown": {"1": 10, "2": 10, "3": 10, "4": 10}},
    {"label": "Character boards", "count": 5}, {"label": "Character Tiles", "count": 6},
    {"label": "Scanner", "count": 1}, {"label": "Intruder bag", "count": 1},
    {"label": "numbered Backpack card holders", "count": 5}, {"label": "Room Help sheet", "count": 1},
    {"label": "Objective Help sheet", "count": 1}, {"label": "colored plastic rings", "count": 6},
    {"label": "Intruder Help sheet", "count": 1}, {"label": "six-sided Burst dice", "count": 2},
    {"label": "eight-sided Shoot dice", "count": 2}, {"label": "ten-sided Noise dice", "count": 2},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fail(failures: list[dict], check: str, **extra) -> None:
    failures.append({"check": check, **extra})


def _line_segment(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def _visuals(data: dict) -> list[dict]:
    wanted = set(FACILITY_VISUAL_IDS)
    return [
        {"occurrenceId": unit["occurrenceId"], "pdfPageIndex": page["pdfPageIndex"], "visiblePrintedPageNumber": page["visiblePrintedPageNumber"], "pageRole": page["pageRole"], "renderEvidence": page["renderEvidence"], "visualUnit": unit}
        for page in data["pages"]
        for unit in page.get("visualUnits", [])
        if unit.get("occurrenceId") in wanted
    ]


def _expected_slots() -> list[dict]:
    rows = []
    for slot_id, section, (x, y, width, height) in ROOM_SLOT_BOXES:
        cx = round(x + (width - 1) / 2, 3)
        cy = round(y + (height - 1) / 2, 3)
        rows.append({
            "slotId": slot_id, "slotKind": "variable-room-slot", "section": section,
            "allowedRoomTypes": [section, "?"], "shape": "regular-pointy-top-hexagon",
            "edgeDirections": EDGE_DIRECTIONS, "sourceLocalBbox": [x, y, width, height],
            "fullPageBbox": [x + 165, y + 1080, x + width + 165, y + height + 1080],
            "sourceLocalCenter": [cx, cy], "fullPageCenter": [round(cx + 165, 3), round(cy + 1080, 3)],
            "reservedCorridorSpaceOnAllEdges": True,
        })
    return rows


def _expected_gaps(slots: list[dict]) -> list[dict]:
    by_id = {row["slotId"]: row for row in slots}
    result = []
    ids = sorted(by_id)
    for index, a_id in enumerate(ids):
        a = by_id[a_id]
        for b_id in ids[index + 1 :]:
            b = by_id[b_id]
            dx = b["sourceLocalCenter"][0] - a["sourceLocalCenter"][0]
            dy = b["sourceLocalCenter"][1] - a["sourceLocalCenter"][1]
            distance = math.hypot(dx, dy)
            if not 117.0 <= distance <= 120.0:
                continue
            if abs(dy) <= 1.0:
                direction = "E" if dx > 0 else "W"
            elif dx > 0 and dy > 0:
                direction = "SE"
            elif dx < 0 and dy > 0:
                direction = "SW"
            elif dx > 0:
                direction = "NE"
            else:
                direction = "NW"
            result.append({
                "gapId": f"CORRIDOR-GAP-{len(result) + 1:03d}", "roomSlotA": a_id, "roomSlotB": b_id,
                "edgeFromA": direction, "edgeFromB": INVERSE[direction],
                "centerDistancePixels": round(distance, 3),
                "reservedGapState": "empty-unoccupied-until-Corridor-placement", "isGameplayCorridor": False,
            })
    return result


def _expected_backlog_links() -> dict[str, list[str]]:
    return {
        "RULE:FND-005": ["SEM-FACILITY-TOPOLOGY-001"],
        "VIS:RB-P04-V01": ["SEM-FACILITY-COMPONENT-INVENTORY-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P08-V01": ["SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P08-V02": ["SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P09-V02": ["SEM-MAP-MARKER-PLACEMENT-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P10-V01": ["SEM-CHARACTER-BOARD-SETUP-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P11-V02": ["SEM-CHARACTER-BOARD-SETUP-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P12-V01": ["SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P14-V03": ["SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P15-V01": ["SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P15-V02": ["SEM-ROUND-TRACK-SETUP-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P16-V01": ["SEM-CHARACTER-BOARD-SETUP-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P19-V01": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P19-V02": ["SEM-ROUND-TRACK-SETUP-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P20-V01": ["SEM-ROOM-TILE-STATE-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P20-V02": ["SEM-ROOM-TILE-STATE-001", "SEM-ROOM-STATIC-PROHIBITIONS", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P20-V03": ["SEM-NEST-DESTROYED-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P21-V02": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-CORRIDOR-SETUP-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P22-V02": ["SEM-DOOR-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
        "VIS:RB-P23-V01": ["SEM-MAP-MARKER-PLACEMENT-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
    }


def validate_facility_family(repo: Path, facility_source_path: Path, source: dict, record_by_id: dict[str, dict], question_by_id: dict[str, dict], conflict_rows: list[dict], coverage: dict, backlog_by_id: dict[str, dict], failures: list[dict]) -> dict:
    if _sha(facility_source_path) != PINNED_FACILITY_SOURCE_INDEX_HASH:
        _fail(failures, "pinned Facility source index")

    expected_counts = {
        "sourceSegments": 12, "visualObligations": 19, "componentInventoryRows": 16,
        "regularRoomSlots": 21, "fixedMapSpaces": 2, "roomEdgeDirections": 6,
        "roomEdgeEndpoints": 126, "pairedConnectorGaps": 43, "ttsFacilityRoles": 13,
        "closedPendingBacklogUnits": 20,
    }
    if source.get("counts") != expected_counts:
        _fail(failures, "Facility declared source projection counts", expected=expected_counts, actual=source.get("counts"))

    for source_id, document in (source.get("sourceDocuments") or {}).items():
        path = repo / str(document.get("path") or "")
        if not path.is_file() or _sha(path) != document.get("sha256"):
            _fail(failures, "Facility live source document hash", sourceId=source_id)
    expected_source_authorities = {"SRC-RULEBOOK": "official-primary", "SRC-FND-005": "project-interpretation", "SRC-VISUAL-CENSUS": "official-primary-visual-census"}
    if {key: (source.get("sourceDocuments", {}).get(key) or {}).get("authority") for key in expected_source_authorities} != expected_source_authorities:
        _fail(failures, "Facility source document authority projection")
    if source.get("sourceDocuments", {}).get("SRC-VISUAL-CENSUS", {}).get("sha256") != _sha(repo / VISUAL_PATH):
        _fail(failures, "Facility visual-census source tuple")

    lines = (repo / RULEBOOK_TEXT_PATH).read_text(encoding="utf-8").splitlines()
    expected_segments = [
        {"sourceUnitId": source_id, "printedLineStart": start, "printedLineEnd": end, "role": role, "checkedExtractionText": _line_segment(lines, start, end)}
        for source_id, start, end, role in SOURCE_SEGMENTS
    ]
    if source.get("sourceSegments") != expected_segments:
        _fail(failures, "Facility exact official procedure line projection")

    visual_data = json.loads((repo / VISUAL_PATH).read_text(encoding="utf-8"))
    expected_visuals = _visuals(visual_data)
    actual_visuals = source.get("visualObligations") or []
    if actual_visuals != expected_visuals or [row.get("occurrenceId") for row in actual_visuals] != FACILITY_VISUAL_IDS:
        _fail(failures, "Facility exact source/visual projection")
    for row in actual_visuals:
        unit = row.get("visualUnit") or {}
        bbox = unit.get("bbox") or []
        dims = row.get("renderEvidence", {}).get("dimensions") or []
        if len(bbox) != 4 or len(dims) != 2 or not (0 <= bbox[0] < bbox[2] <= dims[0] and 0 <= bbox[1] < bbox[3] <= dims[1]) or unit.get("obligationClass") != "normative-visual-obligation" and row.get("occurrenceId") not in {"RB-P22-V02", "RB-P23-V01"}:
            _fail(failures, "Facility visual bbox/authority closure", occurrenceId=row.get("occurrenceId"))

    if source.get("componentInventory") != EXPECTED_COMPONENT_INVENTORY:
        _fail(failures, "Facility exact component inventory projection")

    expected_slots = _expected_slots()
    actual_slots = source.get("roomSlots") or []
    if actual_slots != expected_slots:
        _fail(failures, "Facility independent pinned Room-slot geometry")
    if len({row.get("slotId") for row in actual_slots}) != 21 or {row.get("section") for row in actual_slots} != {"A", "B", "C"}:
        _fail(failures, "Facility Room-slot identity/section partition")
    for row in actual_slots:
        if row.get("shape") != "regular-pointy-top-hexagon" or row.get("edgeDirections") != EDGE_DIRECTIONS or row.get("reservedCorridorSpaceOnAllEdges") is not True:
            _fail(failures, "Facility six-edge geometry invariant", slotId=row.get("slotId"))

    topology = source.get("topologyProjection") or {}
    render = topology.get("renderEvidence") or {}
    expected_render = {
        "sourceVisualObligation": "RB-P19-V01", "pdfPageIndex": 19, "visiblePrintedPageNumber": 19,
        "dpi": 160, "fullPageDimensions": [1361, 1834], "sourceLocalCropOrigin": [165, 1080],
        "sourceLocalCropDimensions": [970, 645], "renderedPageImageSha256": "13ccec5174fa7ce56ceae4b2f2e8afa2b75b70bc528c9a732cd0d53c5d50a44c",
    }
    if render != expected_render or topology.get("sectionColors") != {"A": "green", "B": "blue", "C": "red"} or topology.get("roomEdgeDirections") != EDGE_DIRECTIONS:
        _fail(failures, "Facility rendered source/section/orientation projection")
    expected_gaps = _expected_gaps(expected_slots)
    if topology.get("edgeAdjacency") != expected_gaps:
        _fail(failures, "Facility independent paired Corridor-gap geometry")
    if any(row.get("isGameplayCorridor") is not False or row.get("reservedGapState") != "empty-unoccupied-until-Corridor-placement" for row in topology.get("edgeAdjacency") or []):
        _fail(failures, "Facility gap/Corridor state separation")
    if topology.get("corridorGapProjection", {}).get("notAnOccupiedCorridor") is not True or topology.get("corridorEndpointPolicy", "").find("outside-border placement is prohibited") < 0:
        _fail(failures, "Facility reserved-gap and boundary policy")

    expected_fixed = [
        ("A-LANDING-ZONE", "A", "14", "Section A border-piece named space", False, "source-defined starting named Room space"),
        ("B-HIBERNATORIUM", "B", "18", "Section B border-piece named space", False, "Undiscovered and Inactive; covered by Undiscovered Hibernatorium tile"),
    ]
    fixed = source.get("fixedMapSpaces") or []
    actual_fixed = [(row.get("spaceId"), row.get("section"), row.get("roomHelpNumber"), row.get("surface"), row.get("regularRoomTile"), row.get("initialState")) for row in fixed]
    if actual_fixed != expected_fixed or any("not flattened" not in row.get("geometryBoundary", "") for row in fixed) or any("not assigned" not in row.get("adjacentSlotCrosswalk", "") for row in fixed) or (fixed[1].get("suppressedStates") if len(fixed) > 1 else None) != ["Noise markers cannot be placed on connected Corridors", "Robot cannot be Activated"]:
        _fail(failures, "Facility fixed named-space boundary")

    for path, expected_hash in PINNED_TTS_HASHES.items():
        if _sha(repo / path) != expected_hash:
            _fail(failures, "Facility pinned TTS provenance hash", path=path)
    tts = source.get("ttsProvenance") or {}
    for key, path in (("rawSave", RAW_TTS_PATH), ("roles", TTS_ROLES_PATH), ("objects", TTS_OBJECTS_PATH), ("lua", TTS_LUA_PATH), ("manifest", TTS_MANIFEST_PATH)):
        if (tts.get(key) or {}).get("path") != path or (tts.get(key) or {}).get("sha256") != PINNED_TTS_HASHES[path]:
            _fail(failures, "Facility TTS source tuple", key=key)
    role_objects = tts.get("roleObjects") or []
    if [row.get("role") for row in role_objects] != list(EXPECTED_TTS_ROLES):
        _fail(failures, "Facility TTS role ordering")
    for row in role_objects:
        role = row.get("role")
        expected = EXPECTED_TTS_ROLES.get(role)
        role_tuple = row.get("roleTuple") or {}
        if expected and (role_tuple.get("guid"), role_tuple.get("type"), role_tuple.get("nickname"), role_tuple.get("gmnotes"), role_tuple.get("n_urls")) != expected:
            _fail(failures, "Facility TTS role identity tuple", role=role)
    if "provenance only" not in tts.get("authorityBoundary", "") or "official rulebook" not in tts.get("authorityBoundary", ""):
        _fail(failures, "Facility TTS authority boundary")

    expected_operation_types = {
        "SEM-FACILITY-COMPONENT-INVENTORY-001": ["evaluate-condition"] * 4,
        "SEM-FACILITY-TOPOLOGY-001": ["set-state", "evaluate-condition", "set-state", "evaluate-condition", "evaluate-condition", "resolve-open-alternative"],
        "SEM-FACILITY-ROOM-SETUP-001": ["evaluate-condition", "shuffle", "place-component", "set-state", "evaluate-condition", "evaluate-condition", "resolve-open-alternative"],
        "SEM-FACILITY-CORRIDOR-SETUP-001": ["shuffle", "draw-random", "place-component", "resolve-open-alternative", "set-state", "evaluate-condition"],
        "SEM-ROUND-TRACK-SETUP-001": ["place-component", "place-component", "place-component", "place-component", "place-component", "shuffle", "place-component", "place-component", "resolve-open-alternative"],
        "SEM-CHARACTER-BOARD-SETUP-001": ["place-component", "place-component", "set-state", "place-component", "place-component", "shuffle", "place-component", "evaluate-condition"],
        "SEM-MAP-MARKER-PLACEMENT-001": ["place-component", "place-component", "place-component", "place-component", "evaluate-condition", "evaluate-condition"],
        "SEM-ROOM-TILE-STATE-001": ["evaluate-condition", "set-state", "evaluate-condition", "set-state", "evaluate-condition"],
        "SEM-FACILITY-VISUAL-ASSOCIATIONS-001": ["evaluate-condition"] * 19,
    }
    for rule_id, expected_types in expected_operation_types.items():
        record = record_by_id.get(rule_id) or {}
        if [row.get("operationType") for row in record.get("operations") or []] != expected_types:
            _fail(failures, "Facility operation order/state projection", ruleId=rule_id)
        if not record.get("implementationBoundary", "").startswith("implementation-neutral"):
            _fail(failures, "Facility implementation boundary", ruleId=rule_id)
    expected_state_fragments = {
        "SEM-FACILITY-COMPONENT-INVENTORY-001": ["23 physical Room tiles", "40 physical Corridor tiles"],
        "SEM-FACILITY-TOPOLOGY-001": ["Sections A, B, and C", "regular pointy-top six-edge boundary", "not itself a gameplay Corridor"],
        "SEM-FACILITY-ROOM-SETUP-001": ["four back-type stacks A, B, C, and ?", "Undiscovered Hibernatorium tile", "Noise markers cannot be placed on connected Corridors", "Robot cannot be Activated", "Section Room type is placed only"],
        "SEM-FACILITY-CORRIDOR-SETUP-001": ["all 40 Corridor tiles", "three have been drawn", "non-zero side visible", "one-ended"],
        "SEM-ROUND-TRACK-SETUP-001": ["first Round-track slot", "Round-track slot 10", "above the Round track", "top-most Objective Choice", "Inactive side up", "face down", "five Egg tokens", "four full Ammo"],
        "SEM-CHARACTER-BOARD-SETUP-001": ["left-most Health-track slot", "maximum value 7", "matching colored ring", "above the Character board", "face down", "full-side-up Ammo token"],
        "SEM-MAP-MARKER-PLACEMENT-001": ["Noise marker only in a Corridor", "Fire marker only in a Room", "Secure token only in a Room", "Malfunction marker on a source-eligible component", "printed Room Item/Computer/Other icons"],
        "SEM-ROOM-TILE-STATE-001": ["separate front regions", "face-down Room tile/back", "A/B/C Section type and ? random type", "printed no-Secure/no-Malfunction"],
    }
    for rule_id, fragments in expected_state_fragments.items():
        text = json.dumps(record_by_id.get(rule_id) or {}, ensure_ascii=False)
        if any(fragment not in text for fragment in fragments):
            _fail(failures, "Facility setup/state boundary projection", ruleId=rule_id)
    door = record_by_id.get("SEM-DOOR-001") or {}
    door_text = json.dumps(door, ensure_ascii=False)
    if "preserves adjacency" not in door_text or "Noise markers may still be placed/discarded" not in door_text or not all(value in door_text for value in ("tax.state.opened", "tax.state.closed", "tax.state.destroyed")):
        _fail(failures, "Facility Door/slot/state boundary projection")
    track_operations = (record_by_id.get("SEM-ROUND-TRACK-SETUP-001") or {}).get("operations") or []
    if len(track_operations) != 9 or "first Round-track slot" not in track_operations[0].get("objectRef", "") or "face down" not in track_operations[5].get("objectRef", "") or "Anti-Aircraft" not in track_operations[5].get("objectRef", ""):
        _fail(failures, "Facility exact Round-track token-face/setup projection")
    marker_operations = (record_by_id.get("SEM-MAP-MARKER-PLACEMENT-001") or {}).get("operations") or []
    if len(marker_operations) != 6 or "marker supply is finite" not in marker_operations[5].get("objectRef", "") or "no unlisted" not in marker_operations[5].get("objectRef", ""):
        _fail(failures, "Facility finite marker supply/default projection")
    if "SEM-Q-106" not in (record_by_id.get("SEM-FACILITY-TOPOLOGY-001") or {}).get("unresolvedQuestionRefs", []) or "SEM-Q-110" not in (record_by_id.get("SEM-MAP-MARKER-PLACEMENT-001") or {}).get("unresolvedQuestionRefs", []):
        _fail(failures, "Facility no-default record linkage")
    room_setup = record_by_id.get("SEM-FACILITY-ROOM-SETUP-001") or {}
    if (room_setup.get("operations") or [{}])[0].get("operationType") == "sort":
        _fail(failures, "Facility unsupported sort operation collapse")
    marker = record_by_id.get("SEM-MAP-MARKER-PLACEMENT-001") or {}
    if marker.get("status") != "source-backed-with-open-question" or marker.get("authority", {}).get("interpretation") != "open-alternatives":
        _fail(failures, "Facility marker ambiguity status")
    visual_record = record_by_id.get("SEM-FACILITY-VISUAL-ASSOCIATIONS-001") or {}
    expected_assertions = [f"SA-FACILITY-{x}" for x in FACILITY_VISUAL_IDS]
    if [row.get("assertionId") for row in visual_record.get("sourceAssertions") or []] != expected_assertions:
        _fail(failures, "Facility visual assertion identity/order")
    if any("source-local" not in (row.get("notes") or "") for row in visual_record.get("operations") or []):
        _fail(failures, "Facility visual no-alias projection")

    if set(question_by_id) < set(FACILITY_QUESTION_IDS):
        _fail(failures, "Facility question IDs", missing=sorted(set(FACILITY_QUESTION_IDS) - set(question_by_id)))
    for question_id in FACILITY_QUESTION_IDS:
        question = question_by_id.get(question_id) or {}
        if question.get("defaultProhibited") is not True or len(question.get("alternatives") or []) != 3 or not question.get("sourceEvidenceRefs"):
            _fail(failures, "Facility no-default question shape", questionId=question_id)
    expected_conflicts = {"SC-083": "resolved-by-authority", "SC-084": "resolved-by-authority", "SC-085": "preserved-boundary", "SC-086": "unresolved", "SC-087": "unresolved", "SC-088": "unresolved"}
    actual_conflicts = {row.get("conflictId"): row for row in conflict_rows if row.get("conflictId") in expected_conflicts}
    if set(actual_conflicts) != set(expected_conflicts) or any(actual_conflicts[key].get("status") != value for key, value in expected_conflicts.items()):
        _fail(failures, "Facility conflict status closure")
    if actual_conflicts.get("SC-086", {}).get("questionId") != "SEM-Q-107" or actual_conflicts.get("SC-087", {}).get("questionId") != "SEM-Q-109" or actual_conflicts.get("SC-088", {}).get("questionId") != "SEM-Q-110":
        _fail(failures, "Facility conflict/question linkage")

    links = _expected_backlog_links()
    if source.get("closedPendingBacklogUnitIds") != FACILITY_PENDING_BACKLOG_IDS or source.get("backlogRuleLinks") != links:
        _fail(failures, "Facility exact backlog link projection")
    for unit_id, rule_ids in links.items():
        row = backlog_by_id.get(unit_id) or {}
        if row.get("status") != "pilot-covered" or row.get("pilotRuleIds") != rule_ids:
            _fail(failures, "Facility backlog status/link closure", semanticUnitId=unit_id)
    facility_system = next((row for row in coverage.get("systems") or [] if row.get("system") == "base Facility/map topology and setup-state"), {})
    if facility_system.get("ruleIds") != FACILITY_RULE_IDS or coverage.get("counts", {}).get("fullBaseSemanticCoverageClaimed") is not False:
        _fail(failures, "Facility coverage system projection")

    return {
        "sourceSegments": len(source.get("sourceSegments") or []),
        "visualObligations": len(source.get("visualObligations") or []),
        "regularRoomSlots": len(source.get("roomSlots") or []),
        "pairedConnectorGaps": len((source.get("topologyProjection") or {}).get("edgeAdjacency") or []),
        "newSemanticRecords": len(FACILITY_RULE_IDS),
        "newNoDefaultQuestions": len(FACILITY_QUESTION_IDS),
        "newConflicts": len(expected_conflicts),
        "closedBacklogUnits": len(FACILITY_PENDING_BACKLOG_IDS),
    }
