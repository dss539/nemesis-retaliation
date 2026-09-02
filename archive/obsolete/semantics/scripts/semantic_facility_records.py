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

FACILITY_VISUAL_IDS = [
    "RB-P04-V01",
    "RB-P08-V01",
    "RB-P08-V02",
    "RB-P09-V02",
    "RB-P10-V01",
    "RB-P11-V02",
    "RB-P12-V01",
    "RB-P14-V03",
    "RB-P15-V01",
    "RB-P15-V02",
    "RB-P16-V01",
    "RB-P19-V01",
    "RB-P19-V02",
    "RB-P20-V01",
    "RB-P20-V02",
    "RB-P20-V03",
    "RB-P21-V02",
    "RB-P22-V02",
    "RB-P23-V01",
]

FACILITY_PENDING_BACKLOG_IDS = [
    "RULE:FND-005",
    *[f"VIS:{value}" for value in FACILITY_VISUAL_IDS],
]

FACILITY_QUESTION_IDS = [f"SEM-Q-{value:03d}" for value in range(106, 111)]
FACILITY_RULE_IDS = [
    "SEM-FACILITY-COMPONENT-INVENTORY-001",
    "SEM-FACILITY-TOPOLOGY-001",
    "SEM-FACILITY-ROOM-SETUP-001",
    "SEM-FACILITY-CORRIDOR-SETUP-001",
    "SEM-ROUND-TRACK-SETUP-001",
    "SEM-CHARACTER-BOARD-SETUP-001",
    "SEM-MAP-MARKER-PLACEMENT-001",
    "SEM-ROOM-TILE-STATE-001",
    "SEM-FACILITY-VISUAL-ASSOCIATIONS-001",
]

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

# Coordinates are measured from the p.19 visual-obligation crop [165,1080,1135,1725]
# at 160 DPI. They are source-local evidence coordinates, not world-engine positions.
_ROOM_SLOT_BOXES = [
    ("A-R01", "A", (230, 104, 72, 65)),
    ("A-R02", "A", (349, 104, 72, 65)),
    ("A-R03", "A", (290, 207, 71, 65)),
    ("A-R04", "A", (348, 308, 73, 68)),
    ("A-R05", "A", (290, 413, 71, 64)),
    ("A-R06", "A", (230, 516, 72, 64)),
    ("A-R07", "A", (349, 515, 72, 65)),
    ("B-R01", "B", (408, 207, 73, 64)),
    ("B-R02", "B", (528, 207, 72, 64)),
    ("B-R03", "B", (468, 310, 72, 64)),
    ("B-R04", "B", (408, 413, 73, 64)),
    ("B-R05", "B", (528, 413, 72, 64)),
    ("B-R06", "B", (468, 515, 71, 65)),
    ("C-R01", "C", (587, 104, 71, 64)),
    ("C-R02", "C", (706, 104, 71, 64)),
    ("C-R03", "C", (646, 207, 72, 65)),
    ("C-R04", "C", (587, 310, 71, 64)),
    ("C-R05", "C", (705, 310, 72, 64)),
    ("C-R06", "C", (646, 413, 71, 64)),
    ("C-R07", "C", (587, 516, 72, 63)),
    ("C-R08", "C", (706, 516, 71, 63)),
]

EDGE_DIRECTIONS = ["NE", "E", "SE", "SW", "W", "NW"]
INVERSE_DIRECTION = {"NE": "SW", "E": "W", "SE": "NW", "SW": "NE", "W": "E", "NW": "SE"}

TTS_FACILITY_ROLE_NAMES = [
    "hiddenRoom",
    "hibUnexplored",
    "boarderTile",
    "landingZone",
    "roomIABag",
    "roomIBBag",
    "roomICBag",
    "roomIIBag",
    "corridorBag",
    "doorBag",
    "roundTile",
    "autoDestructionToken",
    "turnMarker",
]

COMPONENT_INVENTORY_ROWS = [
    {"label": "Round track border pieces", "count": 3},
    {"label": "Section border pieces", "count": 3},
    {"label": "Room tiles", "count": 23, "breakdown": {"A": 3, "B": 3, "C": 4, "?": 13}},
    {"label": "Corridor tiles", "count": 40, "breakdown": {"1": 10, "2": 10, "3": 10, "4": 10}},
    {"label": "Character boards", "count": 5},
    {"label": "Character Tiles", "count": 6},
    {"label": "Scanner", "count": 1},
    {"label": "Intruder bag", "count": 1},
    {"label": "numbered Backpack card holders", "count": 5},
    {"label": "Room Help sheet", "count": 1},
    {"label": "Objective Help sheet", "count": 1},
    {"label": "colored plastic rings", "count": 6},
    {"label": "Intruder Help sheet", "count": 1},
    {"label": "six-sided Burst dice", "count": 2},
    {"label": "eight-sided Shoot dice", "count": 2},
    {"label": "ten-sided Noise dice", "count": 2},
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _line_segment(lines: list[str], start: int, end: int) -> str:
    return "\n".join(lines[start - 1 : end])


def _visual_projection(visual_data: dict, wanted: set[str]) -> list[dict]:
    rows = []
    for page in visual_data["pages"]:
        for unit in page.get("visualUnits", []):
            if unit.get("occurrenceId") in wanted:
                rows.append(
                    {
                        "occurrenceId": unit["occurrenceId"],
                        "pdfPageIndex": page["pdfPageIndex"],
                        "visiblePrintedPageNumber": page["visiblePrintedPageNumber"],
                        "pageRole": page["pageRole"],
                        "renderEvidence": page["renderEvidence"],
                        "visualUnit": unit,
                    }
                )
    return rows


def _direction(dx: float, dy: float) -> str:
    if abs(dy) <= 1.0:
        return "E" if dx > 0 else "W"
    if dx > 0 and dy > 0:
        return "SE"
    if dx < 0 and dy > 0:
        return "SW"
    if dx > 0 and dy < 0:
        return "NE"
    if dx < 0 and dy < 0:
        return "NW"
    raise AssertionError((dx, dy))


def _room_slots() -> list[dict]:
    slots = []
    for slot_id, section, (x, y, width, height) in _ROOM_SLOT_BOXES:
        cx = round(x + (width - 1) / 2, 3)
        cy = round(y + (height - 1) / 2, 3)
        slots.append(
            {
                "slotId": slot_id,
                "slotKind": "variable-room-slot",
                "section": section,
                "allowedRoomTypes": [section, "?"],
                "shape": "regular-pointy-top-hexagon",
                "edgeDirections": EDGE_DIRECTIONS,
                "sourceLocalBbox": [x, y, width, height],
                "fullPageBbox": [x + 165, y + 1080, x + width + 165, y + height + 1080],
                "sourceLocalCenter": [cx, cy],
                "fullPageCenter": [round(cx + 165, 3), round(cy + 1080, 3)],
                "reservedCorridorSpaceOnAllEdges": True,
            }
        )
    return slots


def _edge_adjacency(slots: list[dict]) -> list[dict]:
    by_id = {row["slotId"]: row for row in slots}
    pairs = []
    ordered_ids = sorted(by_id)
    for index, left_id in enumerate(ordered_ids):
        left = by_id[left_id]
        for right_id in ordered_ids[index + 1 :]:
            right = by_id[right_id]
            dx = right["sourceLocalCenter"][0] - left["sourceLocalCenter"][0]
            dy = right["sourceLocalCenter"][1] - left["sourceLocalCenter"][1]
            distance = math.hypot(dx, dy)
            if not 117.0 <= distance <= 120.0:
                continue
            direction = _direction(dx, dy)
            pairs.append(
                {
                    "gapId": f"CORRIDOR-GAP-{len(pairs) + 1:03d}",
                    "roomSlotA": left_id,
                    "roomSlotB": right_id,
                    "edgeFromA": direction,
                    "edgeFromB": INVERSE_DIRECTION[direction],
                    "centerDistancePixels": round(distance, 3),
                    "reservedGapState": "empty-unoccupied-until-Corridor-placement",
                    "isGameplayCorridor": False,
                }
            )
    return pairs


def _tts_projection(repo: Path) -> dict:
    roles = json.loads((repo / TTS_ROLES_PATH).read_text(encoding="utf-8"))
    objects = json.loads((repo / TTS_OBJECTS_PATH).read_text(encoding="utf-8"))
    role_by_name = {row.get("role"): row for row in roles}
    object_by_guid = {row.get("guid"): row for row in objects}
    rows = []
    for role_name in TTS_FACILITY_ROLE_NAMES:
        role = role_by_name.get(role_name)
        if not role:
            raise AssertionError(f"missing TTS Facility role {role_name}")
        obj = object_by_guid.get(role["guid"])
        if not obj:
            raise AssertionError(f"missing TTS Facility object {role['guid']}")
        rows.append(
            {
                "role": role_name,
                "roleTuple": {key: role.get(key) for key in ("guid", "type", "nickname", "gmnotes", "n_urls", "deck_nums", "contained")},
                "objectTuple": {
                    "guid": obj.get("guid"),
                    "type": obj.get("type"),
                    "nickname": obj.get("nickname"),
                    "gmnotes": obj.get("gmnotes"),
                    "parent": obj.get("parent"),
                    "transform": obj.get("transform"),
                },
            }
        )
    return {
        "rawSave": {"path": RAW_TTS_PATH, "sha256": _sha(repo / RAW_TTS_PATH), "sourceRole": "secondary-evidence-only"},
        "roles": {"path": TTS_ROLES_PATH, "sha256": _sha(repo / TTS_ROLES_PATH), "sourceRole": "secondary-role-provenance"},
        "objects": {"path": TTS_OBJECTS_PATH, "sha256": _sha(repo / TTS_OBJECTS_PATH), "sourceRole": "secondary-object-provenance"},
        "lua": {"path": TTS_LUA_PATH, "sha256": _sha(repo / TTS_LUA_PATH), "sourceRole": "secondary-runtime-evidence-only"},
        "manifest": {"path": TTS_MANIFEST_PATH, "sha256": _sha(repo / TTS_MANIFEST_PATH), "sourceRole": "secondary-asset-provenance"},
        "roleObjects": rows,
        "authorityBoundary": "TTS roles, objects, transforms, and runtime variables preserve component provenance only; they do not override official rulebook text or rendered geometry.",
    }


def build_facility_source_index(repo: Path) -> dict:
    rulebook_lines = (repo / RULEBOOK_TEXT_PATH).read_text(encoding="utf-8").splitlines()
    visual_data = json.loads((repo / VISUAL_PATH).read_text(encoding="utf-8"))
    slots = _room_slots()
    gaps = _edge_adjacency(slots)
    visual_rows = _visual_projection(visual_data, set(FACILITY_VISUAL_IDS))
    source_documents = {
        "SRC-RULEBOOK": {
            "path": "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf",
            "sha256": _sha(repo / "docs/rulebooks/Nemesis_RT_Rulebook_official.pdf"),
            "authority": "official-primary",
        },
        "SRC-FND-005": {
            "path": "docs/rules/00-foundations.md",
            "sha256": _sha(repo / "docs/rules/00-foundations.md"),
            "authority": "project-interpretation",
        },
        "SRC-VISUAL-CENSUS": {
            "path": VISUAL_PATH,
            "sha256": _sha(repo / VISUAL_PATH),
            "authority": "official-primary-visual-census",
        },
    }
    source_segments = [
        {
            "sourceUnitId": source_id,
            "printedLineStart": start,
            "printedLineEnd": end,
            "role": role,
            "checkedExtractionText": _line_segment(rulebook_lines, start, end),
        }
        for source_id, start, end, role in SOURCE_SEGMENTS
    ]
    fixed_spaces = [
        {
            "spaceId": "A-LANDING-ZONE",
            "spaceKind": "fixed-named-room-space",
            "section": "A",
            "roomHelpNumber": "14",
            "sourceTerm": "Landing Zone",
            "surface": "Section A border-piece named space",
            "regularRoomTile": False,
            "initialState": "source-defined starting named Room space",
            "geometryBoundary": "special border-piece geometry; not flattened into a regular variable hex slot",
            "adjacentSlotCrosswalk": "not assigned where the rendered special-space boundary does not provide an unambiguous regular-slot pair",
        },
        {
            "spaceId": "B-HIBERNATORIUM",
            "spaceKind": "fixed-named-room-space",
            "section": "B",
            "roomHelpNumber": "18",
            "sourceTerm": "Hibernatorium",
            "surface": "Section B border-piece named space",
            "regularRoomTile": False,
            "initialState": "Undiscovered and Inactive; covered by Undiscovered Hibernatorium tile",
            "suppressedStates": ["Noise markers cannot be placed on connected Corridors", "Robot cannot be Activated"],
            "geometryBoundary": "special border-piece geometry; not flattened into a regular variable hex slot",
            "adjacentSlotCrosswalk": "not assigned where the rendered special-space boundary does not provide an unambiguous regular-slot pair",
        },
    ]
    return {
        "schemaVersion": 1,
        "recordType": "semantic-facility-map-source-index",
        "scope": "base Facility/map topology and source-clear setup-state only; no implementation coordinates or full lifecycle engine semantics",
        "authorityPolicy": "Official rulebook/FAQ/component references control rules. The rendered p.19 visual census controls source-local geometry and visual associations. FND-005 is the project-confirmed six-sided geometry invariant. TTS is provenance/evidence only.",
        "sourceDocuments": source_documents,
        "sourceSegments": source_segments,
        "visualObligations": visual_rows,
        "componentInventory": COMPONENT_INVENTORY_ROWS,
        "roomSlots": slots,
        "fixedMapSpaces": fixed_spaces,
        "topologyProjection": {
            "renderEvidence": {
                "sourceVisualObligation": "RB-P19-V01",
                "pdfPageIndex": 19,
                "visiblePrintedPageNumber": 19,
                "dpi": 160,
                "fullPageDimensions": [1361, 1834],
                "sourceLocalCropOrigin": [165, 1080],
                "sourceLocalCropDimensions": [970, 645],
                "renderedPageImageSha256": next(row["renderEvidence"]["imageSha256"] for row in visual_rows if row["occurrenceId"] == "RB-P19-V01"),
            },
            "sectionColors": {"A": "green", "B": "blue", "C": "red"},
            "regularRoomSlotShape": "regular-pointy-top-hexagon",
            "roomEdgeDirections": EDGE_DIRECTIONS,
            "centerStepProjection": {"horizontalPixels": 119.0, "diagonalPixels": "approximately 119.0", "rowStepPixels": 103.0},
            "corridorGapProjection": {"purpose": "reserved space beyond every Room edge", "horizontalMeasuredRoomWidthPixels": "71–73", "horizontalCenterStepPixels": 119.0, "derivedMinimumGapPixels": 46.0, "notAnOccupiedCorridor": True},
            "edgeAdjacency": gaps,
            "corridorEndpointPolicy": "Each paired gap has two immediate Room-edge endpoints. Unpaired outer edges remain reserved only where a source-defined Corridor can be placed; outside-border placement is prohibited. This index does not invent a source-local endpoint assignment for special border-piece spaces.",
            "proximityBoundary": "A measured neighbouring slot pair is a physical connector gap, not gameplay adjacency until a legal Corridor occupies it; a Corridor never spans an intervening Room.",
        },
        "ttsProvenance": _tts_projection(repo),
        "closedPendingBacklogUnitIds": FACILITY_PENDING_BACKLOG_IDS,
        "backlogRuleLinks": {
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
        },
        "counts": {
            "sourceSegments": len(source_segments),
            "visualObligations": len(visual_rows),
            "componentInventoryRows": len(COMPONENT_INVENTORY_ROWS),
            "regularRoomSlots": len(slots),
            "fixedMapSpaces": len(fixed_spaces),
            "roomEdgeDirections": len(EDGE_DIRECTIONS),
            "roomEdgeEndpoints": len(slots) * len(EDGE_DIRECTIONS),
            "pairedConnectorGaps": len(gaps),
            "ttsFacilityRoles": len(TTS_FACILITY_ROLE_NAMES),
            "closedPendingBacklogUnits": len(FACILITY_PENDING_BACKLOG_IDS),
        },
    }


def facility_source_registry_rows(source_index: dict) -> list[dict]:
    rows = []
    for source_id, key, version in (
        ("SRC-TTS-FACILITY-RAW", "rawSave", "Workshop 3256296893 extracted raw save"),
        ("SRC-TTS-FACILITY-ROLES", "roles", "Workshop 3256296893 extracted Lua role projection"),
        ("SRC-TTS-FACILITY-OBJECTS", "objects", "Workshop 3256296893 extracted object projection"),
        ("SRC-TTS-FACILITY-LUA", "lua", "Workshop 3256296893 extracted Lua runtime evidence"),
        ("SRC-TTS-FACILITY-MANIFEST", "manifest", "Workshop 3256296893 downloaded asset manifest"),
    ):
        evidence = source_index["ttsProvenance"][key]
        rows.append(
            {
                "sourceId": source_id,
                "authority": "source-bound-component-scan",
                "version": version,
                "path": evidence["path"],
                "sha256": evidence["sha256"],
                "evidenceIndexPath": "docs/rules/semantics/facility-source-index.json",
                "occurrenceId": f"facility-{key}",
                "evidenceRecord": f"docs/rules/semantics/facility-source-index.json:ttsProvenance.{key}",
            }
        )
    return rows


def _visual_assertions(source_index: dict, assertion) -> list[dict]:
    rows = []
    for row in source_index["visualObligations"]:
        item = assertion(
            f"SA-FACILITY-{row['occurrenceId']}",
            "SRC-RULEBOOK",
            f"printed page {row['visiblePrintedPageNumber']} / {row['occurrenceId']} / {row['visualUnit'].get('type')}",
            ["operations", "informationPolicy", "sourceVariants"],
            row["visualUnit"].get("description") or row["visualUnit"].get("classification"),
            f"docs/rules/source-extraction/rulebook-visual-obligations.json:{row['occurrenceId']}",
        )
        rows.append(item)
    return rows


def build_facility_records(repo, source_index, record, assertion, timing, participant, condition, decision, operation):
    records = []
    rb = "docs/rulebooks/rulebook_text.txt"
    visual = "docs/rules/source-extraction/rulebook-visual-obligations.json"

    inventory_assertions = [
        assertion("SA-FACILITY-INVENTORY-RB", "SRC-RULEBOOK", "printed page 4 / main component inventory; extracted lines 965–988 and 2152–2185", ["operations", "informationPolicy"], "The base inventory includes 3 Round track border pieces, 3 Section border pieces, 23 Room tiles (3 A, 3 B, 4 C, 13 ?), and 40 Corridor tiles (10 each of 1, 2, 3, and 4), with the numbered marker/token/component quantities retained source-locally.", f"{rb}:lines 965–988,2152–2185"),
        assertion("SA-FACILITY-INVENTORY-VIS", "SRC-RULEBOOK", "printed page 4 / RB-P04-V01 / illustrated main component inventory", ["operations", "informationPolicy"], "Each inventory quantity is bound to its pictured component; Room and Corridor parenthetical subtype counts remain attached to their own rows.", f"{visual}:RB-P04-V01"),
    ]
    records.append(record(
        "SEM-FACILITY-COMPONENT-INVENTORY-001", "Facility and map component inventory", "source-backed", "constraint", "official-primary", "verbatim-structure",
        inventory_assertions,
        ["term.facility", "term.map", "term.section", "term.room", "term.corridor", "term.round-marker", "term.universal-marker", "term.hibernatorium", "term.nest", "term.landing-zone", "term.door", "term.tactical-gear-token"],
        ["tax.entity.spatial.facility", "tax.entity.spatial.map", "tax.entity.spatial.section", "tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.entity.component.token.round", "tax.entity.component.marker.universal", "tax.entity.spatial.room.hibernatorium", "tax.entity.spatial.room.nest", "tax.entity.spatial.room.landing-zone", "tax.entity.spatial.door", "tax.entity.component.token.tactical-gear", "tax.scaffold.supply-pool"],
        [], timing("TW-FACILITY-INVENTORY", "tax.entity.spatial.facility", "when-triggered", "once-per-base-game-setup"),
        [participant("P-RULES", "rules-system"), participant("P-SETUP", "setup-procedure")], "must", [], [],
        [{"informationId": "I-FACILITY-INVENTORY", "subjectRef": "finite map components, subtype quantities, and separate fixed named spaces", "audience": "public", "revealTrigger": "setup", "secrecy": "no inventory quantity or map-space identity is hidden"}], [], [],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "exact base component inventory rows and quantities", ["SA-FACILITY-INVENTORY-RB", "SA-FACILITY-INVENTORY-VIS"]),
            operation("S02", 2, "evaluate-condition", "must", "P-RULES", "23 physical Room tiles partitioned 3 A, 3 B, 4 C, and 13 ?", ["SA-FACILITY-INVENTORY-RB", "SA-FACILITY-INVENTORY-VIS"]),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "40 physical Corridor tiles partitioned into ten each of values 1, 2, 3, and 4", ["SA-FACILITY-INVENTORY-RB", "SA-FACILITY-INVENTORY-VIS"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "finite Section/Round border pieces and map marker/token pools remain distinct components", ["SA-FACILITY-INVENTORY-RB"]),
        ],
        {"policy": "source-limited-components", "unit": "one named inventory row and subtype breakdown", "onImpossible": "No setup replacement, proxy, or shortage fallback is supplied by these source rows; SEM-Q-109 prohibits invention."},
        {"kind": "finite-physical-inventory"}, {"policy": "counts do not identify semantic copies or merge map surfaces"}, [], [], []
    ))

    topology_assertions = [
        assertion("SA-FACILITY-TOPOLOGY-RB", "SRC-RULEBOOK", "printed pages 19–21 / extracted lines 3915–3951,4007–4014,4171–4194", ["preconditions", "operations", "informationPolicy", "duration"], "The Facility is divided into Sections A, B, and C. Rooms belong to one Section and are connected by adjacent Corridors; Characters occupy Rooms and Intruders may occupy Rooms or Corridors. Section border and Round track pieces form the Facility boundary.", f"{rb}:lines 3915–3951,4007–4014,4171–4194"),
        assertion("SA-FACILITY-TOPOLOGY-FND", "SRC-FND-005", "FND-005 / Room geometry and Corridor spacing", ["operations", "preconditions", "informationPolicy", "unresolvedQuestionRefs"], "Every Room and empty Room slot uses a regular pointy-top hexagon with six named directions; all six edges retain reserved Corridor spacing; a Corridor connects only immediately adjacent Room edges and visual proximity alone is not gameplay adjacency.", "docs/rules/00-foundations.md:FND-005"),
        assertion("SA-FACILITY-TOPOLOGY-VIS", "SRC-RULEBOOK", "printed page 19 / RB-P19-V01 / facility-section-slot-boundary diagram", ["operations", "informationPolicy"], "The rendered map diagram supplies the green A, blue B, and red C section boundaries, 21 regular variable Room-slot contours, the Facility boundary, and separate border-piece named-space geometry.", f"{visual}:RB-P19-V01"),
        assertion("SA-FACILITY-TOPOLOGY-CORRIDOR-VIS", "SRC-RULEBOOK", "printed page 21 / RB-P21-V02 / unexplored Corridor topology example", ["operations", "informationPolicy"], "The illustrated example distinguishes one-ended Unexplored Corridors from the surrounding Room/Corridor topology.", f"{visual}:RB-P21-V02"),
    ]
    records.append(record(
        "SEM-FACILITY-TOPOLOGY-001", "Facility sections, Room-slot geometry, and Corridor gaps", "source-backed-with-open-question", "constraint", "official-primary", "open-alternatives",
        topology_assertions,
        ["term.facility", "term.map", "term.section", "term.section-a", "term.section-b", "term.section-c", "term.room", "term.corridor", "term.empty-corridor", "term.unexplored-corridor", "term.discovered", "term.undiscovered", "term.hibernatorium", "term.landing-zone", "icon.intruder"],
        ["tax.entity.spatial.facility", "tax.entity.spatial.map", "tax.entity.spatial.section", "tax.entity.spatial.section.a", "tax.entity.spatial.section.b", "tax.entity.spatial.section.c", "tax.entity.spatial.room", "tax.entity.spatial.room-slot", "tax.entity.spatial.corridor", "tax.state.corridor.empty", "tax.state.corridor.unexplored", "tax.state.discovery.discovered", "tax.state.discovery.undiscovered", "tax.entity.spatial.room.hibernatorium", "tax.entity.spatial.room.landing-zone", "tax.entity.agent.intruder"],
        [], timing("TW-FACILITY-TOPOLOGY", "tax.entity.spatial.facility", "when-triggered", "per-map-state-check"),
        [participant("P-RULES", "rules-system"), participant("P-FACILITY", "map-state", "tax.entity.spatial.facility")], "must",
        [condition("C-FACILITY-BOUNDARY", "all", [{"predicate": "destination is inside the official Facility boundary"}, {"predicate": "Room/Corridor occupies a source-defined slot or reserved connector gap"}], ["SA-FACILITY-TOPOLOGY-RB", "SA-FACILITY-TOPOLOGY-VIS"])], [],
        [{"informationId": "I-FACILITY-TOPOLOGY", "subjectRef": "section membership, six-sided Room-slot boundary, reserved Corridor gaps, special named spaces, and actual Corridor occupancy", "audience": "public", "revealTrigger": "setup/placement/continuous", "secrecy": "source geometry and current map state are public; no unexplored Room face is exposed before source-defined discovery"}], [], [],
        [
            operation("S01", 1, "set-state", "must", "P-RULES", "Facility divided into exactly Sections A, B, and C", ["SA-FACILITY-TOPOLOGY-RB", "SA-FACILITY-TOPOLOGY-VIS"]),
            operation("S02", 2, "evaluate-condition", "must", "P-RULES", "each regular variable Room slot belongs to exactly one rendered section color and permits its Section type or ? Room type", ["SA-FACILITY-TOPOLOGY-RB", "SA-FACILITY-TOPOLOGY-VIS"]),
            operation("S03", 3, "set-state", "must", "P-RULES", "each regular Room slot has a regular pointy-top six-edge boundary and reserved spacing on NE/E/SE/SW/W/NW", ["SA-FACILITY-TOPOLOGY-FND", "SA-FACILITY-TOPOLOGY-VIS"]),
            operation("S04", 4, "evaluate-condition", "must", "P-RULES", "paired connector gap joins only the two immediately adjacent Room-edge endpoints and is not itself a gameplay Corridor until a Corridor is placed", ["SA-FACILITY-TOPOLOGY-FND", "SA-FACILITY-TOPOLOGY-VIS"]),
            operation("S05", 5, "evaluate-condition", "must", "P-RULES", "Room/Corridor placement outside the Facility border is illegal", ["SA-FACILITY-TOPOLOGY-RB", "SA-FACILITY-TOPOLOGY-VIS"]),
            operation("S06", 6, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-106 section-piece orientation and fixed-space edge crosswalk", ["SA-FACILITY-TOPOLOGY-RB", "SA-FACILITY-TOPOLOGY-VIS", "SA-FACILITY-TOPOLOGY-FND"]),
        ],
        {"policy": "per-effect-check", "unit": "map slot, edge, or connector-gap state", "onImpossible": "Reject off-board, unconnected, intervening-slot, or geometry-collapsing representations; SEM-Q-106/107 retain source-unspecified physical orientation/crosswalk alternatives."},
        {"kind": "persistent-map-geometry"}, {"policy": "Room-slot geometry and actual Corridor occupancy remain distinct"}, [], ["SEM-Q-106", "SEM-Q-107"], []
    ))

    room_assertions = [
        assertion("SA-FACILITY-ROOM-SETUP-RB", "SRC-RULEBOOK", "printed page 8 / lines 2404–2426 and page 20 / lines 4011–4014", ["operations", "preconditions", "informationPolicy", "duration"], "Sort Room tiles by backs into A, B, C, and ? stacks, shuffle each stack, and keep them face down. Section Rooms belong to their associated Section; ? Rooms are random and may appear in any Section. The Undiscovered Hibernatorium tile covers the fixed Hibernatorium space until discovery; while it is covered, Noise markers cannot be placed on connected Corridors and the Robot cannot be Activated.", f"{rb}:lines 2404–2426,4011–4014"),
        assertion("SA-FACILITY-ROOM-SETUP-VIS", "SRC-RULEBOOK", "printed page 20 / RB-P20-V01 / Room-tile front/back anatomy", ["operations", "informationPolicy"], "Room front/back anatomy binds Name, Effect, Item Icons, Computer Icon, Room Type/ID, Other Icons, and the face-down Section-letter back to distinct physical regions.", f"{visual}:RB-P20-V01"),
    ]
    records.append(record(
        "SEM-FACILITY-ROOM-SETUP-001", "Room-tile stacks, fixed spaces, and discovery state", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        room_assertions,
        ["term.room", "term.section", "term.section-a", "term.section-b", "term.section-c", "term.discovered", "term.undiscovered", "term.hibernatorium", "term.landing-zone"],
        ["tax.entity.spatial.room", "tax.entity.spatial.section", "tax.entity.spatial.section.a", "tax.entity.spatial.section.b", "tax.entity.spatial.section.c", "tax.state.discovery.discovered", "tax.state.discovery.undiscovered", "tax.entity.spatial.room.hibernatorium", "tax.entity.spatial.room.landing-zone", "tax.scaffold.supply-pool"],
        [], timing("TW-ROOM-SETUP", "tax.entity.spatial.room", "when-triggered", "per-physical-Room-stack-or-placement"),
        [participant("P-SETUP", "setup-procedure"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-ROOM-SETUP", "subjectRef": "Room stack type, face-down/face-up state, Room ID, and fixed-space cover state", "audience": "public-after-placement-except-unrevealed-Room-face", "revealTrigger": "Room draw/placement/discovery", "secrecy": "Unselected stack faces remain hidden; a placed Room is face up when source-directed"}], [], [],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-SETUP", "23 physical Room tiles are sorted into four back-type stacks A, B, C, and ?", ["SA-FACILITY-ROOM-SETUP-RB"]),
            operation("S02", 2, "shuffle", "must", "P-SETUP", "each Room stack separately and keep it face down", ["SA-FACILITY-ROOM-SETUP-RB"]),
            operation("S03", 3, "place-component", "must", "P-SETUP", "Undiscovered Hibernatorium tile on the fixed Hibernatorium space", ["SA-FACILITY-ROOM-SETUP-RB"]),
            operation("S04", 4, "set-state", "must", "P-RULES", "Hibernatorium is Undiscovered and cannot be Used until its source-defined discovery trigger; Noise markers cannot be placed on connected Corridors and the Robot cannot be Activated while covered", ["SA-FACILITY-ROOM-SETUP-RB"]),
            operation("S05", 5, "evaluate-condition", "must", "P-RULES", "Section Room type is placed only in its matching Section; ? Room may appear in any Section", ["SA-FACILITY-ROOM-SETUP-RB"]),
            operation("S06", 6, "evaluate-condition", "must", "P-RULES", "face-up placed Room exposes its source-defined front anatomy and ID; an unplaced/covered Room remains face down", ["SA-FACILITY-ROOM-SETUP-RB", "SA-FACILITY-ROOM-SETUP-VIS"]),
            operation("S07", 7, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-109 setup shortage/replacement and physical stack atomicity", ["SA-FACILITY-ROOM-SETUP-RB"]),
        ],
        {"policy": "ordered-complete", "unit": "Room stack or fixed-space setup step", "onImpossible": "No substitute Room, stack, face, or shortage fallback is source-defined; SEM-Q-109 prohibits invention."},
        {"kind": "setup-and-discovery-state"}, {"policy": "one physical tile remains one occurrence; fixed named spaces are not converted into random tile copies"}, [], ["SEM-Q-106", "SEM-Q-109"], []
    ))

    corridor_assertions = [
        assertion("SA-FACILITY-CORRIDOR-SETUP-RB", "SRC-RULEBOOK", "printed page 8 / lines 2399–2403 and 2472–2476", ["operations", "preconditions", "informationPolicy", "duration"], "Draw three random Corridor tiles one by one and connect them to the Landing Zone face up with non-zero values; if a tile has a Door slot, orient that slot toward the Landing Zone entrance. Shuffle the remaining Corridor tiles into an insert and avoid seeing fronts before drawing.", f"{rb}:lines 2399–2403,2472–2476"),
        assertion("SA-FACILITY-CORRIDOR-MAP-RB", "SRC-RULEBOOK", "printed pages 21–22 / lines 4180–4194,4244–4252", ["operations", "preconditions", "informationPolicy"], "A Corridor has source-defined values and a Door slot where present; each Corridor connected to a Room is adjacent to that Room regardless of Doors or Intruders, and newly placed Corridors with Door slots orient that slot toward the Room just placed.", f"{rb}:lines 4180–4194,4244–4252"),
        assertion("SA-FACILITY-CORRIDOR-VIS", "SRC-RULEBOOK", "printed page 21 / RB-P21-V02 / unexplored Corridor topology example", ["operations", "informationPolicy"], "The visual example binds Unexplored Corridor status to a Corridor connected with only one Room, not to a generic empty gap or a collapsed Room edge.", f"{visual}:RB-P21-V02"),
    ]
    records.append(record(
        "SEM-FACILITY-CORRIDOR-SETUP-001", "Corridor supply, initial Landing Zone links, and endpoint state", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        corridor_assertions,
        ["term.corridor", "term.empty-corridor", "term.unexplored-corridor", "term.room", "term.landing-zone", "term.door", "term.discovered", "term.undiscovered"],
        ["tax.entity.spatial.corridor", "tax.state.corridor.empty", "tax.state.corridor.unexplored", "tax.entity.spatial.room", "tax.entity.spatial.room.landing-zone", "tax.entity.spatial.door", "tax.state.discovery.discovered", "tax.state.discovery.undiscovered", "tax.scaffold.supply-pool"],
        [], timing("TW-CORRIDOR-SETUP", "tax.entity.spatial.corridor", "when-triggered", "per-physical-Corridor-placement"),
        [participant("P-SETUP", "setup-procedure"), participant("P-RULES", "rules-system")], "must", [],
        [decision("D-CORRIDOR-DOOR-ORIENTATION", "P-RULES", "unresolved", 1, 1, False, "source-unspecified", ["Door slot toward the selected Landing Zone entrance", "another source-defined initial entrance/orientation rule"])],
        [{"informationId": "I-CORRIDOR-SETUP", "subjectRef": "Corridor face, non-zero value, Door slot orientation, endpoint occupancy, and one-ended Unexplored state", "audience": "public-after-draw", "revealTrigger": "draw/placement", "secrecy": "Corridor fronts remain hidden in the insert before draw; placed Corridor state is public"}], [], [],
        [
            operation("S01", 1, "shuffle", "must", "P-SETUP", "all 40 Corridor tiles into the Corridor insert", ["SA-FACILITY-CORRIDOR-SETUP-RB"]),
            operation("S02", 2, "draw-random", "must", "P-SETUP", "one Corridor tile at a time until three have been drawn", ["SA-FACILITY-CORRIDOR-SETUP-RB"], repeat={"quantity": 3, "order": "one-by-one", "frontHiddenBeforeDraw": True}),
            operation("S03", 3, "place-component", "must", "P-SETUP", "each drawn Corridor face up with its non-zero side visible, connected to the Landing Zone", ["SA-FACILITY-CORRIDOR-SETUP-RB"]),
            operation("S04", 4, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-108 Door-slot orientation and initial Landing Zone entrance assignment", ["SA-FACILITY-CORRIDOR-SETUP-RB", "SA-FACILITY-CORRIDOR-MAP-RB"], decision_ref="D-CORRIDOR-DOOR-ORIENTATION"),
            operation("S05", 5, "set-state", "must", "P-RULES", "Corridor connected to exactly one Room is Unexplored; a Corridor with no Intruders is Empty even if it has a Noise marker", ["SA-FACILITY-CORRIDOR-MAP-RB", "SA-FACILITY-CORRIDOR-VIS"]),
            operation("S06", 6, "evaluate-condition", "must", "P-RULES", "actual Corridor occupancy is distinct from a reserved empty connector gap and from Room adjacency by proximity alone", ["SA-FACILITY-CORRIDOR-MAP-RB"]),
        ],
        {"policy": "ordered-complete", "unit": "one Corridor draw or placement", "onImpossible": "Do not place outside the Facility or invent an endpoint/entrance assignment; SEM-Q-107/108 retain source-unspecified crosswalk/orientation alternatives."},
        {"kind": "finite-corridor-supply-and-map-state"}, {"policy": "one physical Corridor occupies one source-defined gap; face state and Door state remain separate"}, [], ["SEM-Q-107", "SEM-Q-108"], []
    ))

    track_assertions = [
        assertion("SA-FACILITY-TRACK-SETUP-RB", "SRC-RULEBOOK", "printed page 8 / lines 2428–2471", ["operations", "preconditions", "informationPolicy", "duration"], "Place the Round marker on Round 1, Lander on Round 10, Autodestruction above the Round track, Universal marker on the top Objective Choice space, systems/Anti-Aircraft/Eggs in their Section-border slots, and the four initial Tactical Gear groups beside the Landing Zone.", f"{rb}:lines 2428–2471"),
        assertion("SA-FACILITY-TRACK-VIS", "SRC-RULEBOOK", "printed page 15 / RB-P15-V02 / Round-track token-resolution key", ["operations", "informationPolicy"], "The visual key binds Autodestruction and Lander token glyphs and the green/red Anti-Aircraft faces to the Round-track collision outcomes; this record models setup/track state only, not full Lander escape or movement.", f"{visual}:RB-P15-V02"),
        assertion("SA-FACILITY-LIFE-SUPPORT-VIS", "SRC-RULEBOOK", "printed page 19 / RB-P19-V02 / Life Support state/icon definition", ["operations", "informationPolicy"], "Active and Inactive Life Support words are tied to distinct paired printed glyphs.", f"{visual}:RB-P19-V02"),
    ]
    records.append(record(
        "SEM-ROUND-TRACK-SETUP-001", "Round track, Section-border, and fixed-system setup state", "source-backed-with-open-question", "procedure", "official-primary", "open-alternatives",
        track_assertions,
        ["term.round-marker", "term.universal-marker", "term.hibernatorium", "term.nest", "term.landing-zone", "term.section", "term.section-a", "term.section-b", "term.section-c", "icon.lander", "icon.autodestruction", "icon.lifeSupportActive", "icon.lifeSupportInactive", "icon.hibernatoriumActive", "icon.hibernatoriumInactive", "icon.ammoToken", "icon.oxygenToken"],
        ["tax.entity.component.token.round", "tax.entity.component.marker.universal", "tax.entity.spatial.room.hibernatorium", "tax.entity.spatial.room.nest", "tax.entity.spatial.room.landing-zone", "tax.entity.spatial.section", "tax.entity.spatial.section.a", "tax.entity.spatial.section.b", "tax.entity.spatial.section.c", "tax.entity.component.token.lander", "tax.entity.component.token.autodestruction", "tax.entity.component.token.anti-aircraft", "tax.entity.component.token.egg", "tax.entity.component.token.tactical-gear.ammo", "tax.entity.component.token.tactical-gear.oxygen"],
        [], timing("TW-ROUND-TRACK-SETUP", "tax.entity.component.token.round", "when-triggered", "once-per-game-setup"),
        [participant("P-SETUP", "setup-procedure"), participant("P-RULES", "rules-system")], "must", [], [],
        [{"informationId": "I-TRACK-SETUP", "subjectRef": "Round marker, Lander, Autodestruction, Universal, Life Support, Hibernatorium, Anti-Aircraft, Eggs, and Landing Zone supply states", "audience": "public", "revealTrigger": "setup", "secrecy": "Anti-Aircraft token identities remain face down; all other listed setup states are public"}], [], [],
        [
            operation("S01", 1, "place-component", "must", "P-SETUP", "Round marker on first Round-track slot", ["SA-FACILITY-TRACK-SETUP-RB"]),
            operation("S02", 2, "place-component", "must", "P-SETUP", "Lander token on Round-track slot 10", ["SA-FACILITY-TRACK-SETUP-RB", "SA-FACILITY-TRACK-VIS"]),
            operation("S03", 3, "place-component", "must", "P-SETUP", "Autodestruction token on its corresponding slot above the Round track", ["SA-FACILITY-TRACK-SETUP-RB", "SA-FACILITY-TRACK-VIS"]),
            operation("S04", 4, "place-component", "must", "P-SETUP", "Universal marker on the top-most Objective Choice space", ["SA-FACILITY-TRACK-SETUP-RB"]),
            operation("S05", 5, "place-component", "must", "P-SETUP", "three Life Support tokens and Hibernatorium token Inactive side up on their Section-border slots", ["SA-FACILITY-TRACK-SETUP-RB", "SA-FACILITY-LIFE-SUPPORT-VIS"]),
            operation("S06", 6, "shuffle", "must", "P-SETUP", "both Anti-Aircraft tokens face down, one atop the other, in Section B's Anti-Aircraft slot", ["SA-FACILITY-TRACK-SETUP-RB", "SA-FACILITY-TRACK-VIS"]),
            operation("S07", 7, "place-component", "must", "P-SETUP", "five Egg tokens in the Eggs space on the Section C border piece", ["SA-FACILITY-TRACK-SETUP-RB"]),
            operation("S08", 8, "place-component", "must", "P-SETUP", "four full Ammo, four Grenade, four Oxygen, and four Medpack tokens on corresponding slots next to the Landing Zone", ["SA-FACILITY-TRACK-SETUP-RB"]),
            operation("S09", 9, "resolve-open-alternative", "must", "P-RULES", "SEM-Q-106 section-border orientation and simultaneous fixed-system placement boundary", ["SA-FACILITY-TRACK-SETUP-RB"], conditions=["physical border-piece orientation or simultaneous placement affects the initial state"]),
        ],
        {"policy": "ordered-complete", "unit": "one source-numbered setup placement", "onImpossible": "No replacement token, alternate slot, or shortage fallback is defined; SEM-Q-106/109 prohibit invention. Anti-Aircraft face identity remains hidden."},
        {"kind": "initial-public-track-and-border-state"}, {"policy": "one physical token/component per listed slot or finite supply instruction"}, [], ["SEM-Q-106", "SEM-Q-109"], []
    ))

    character_assertions = [
        assertion("SA-FACILITY-CHARACTER-SETUP-RB", "SRC-RULEBOOK", "printed pages 10–11 / lines 2665–2701,2741–2746", ["operations", "preconditions", "informationPolicy", "duration"], "Each player places the matching Character tile in a Character board, puts a Universal marker in the left-most Health slot, sets Oxygen to 7, puts the color-matched miniature in the Landing Zone, places their numbered Backpack holder above the board, shuffles their Action deck to the left with discard space to the right, and places the Character Item in the class-defined slot; Contractor starts with two Character Items.", f"{rb}:lines 2665–2701,2741–2746"),
        assertion("SA-FACILITY-CHARACTER-ASSEMBLY-VIS", "SRC-RULEBOOK", "printed page 11 / RB-P11-V02 / Character-board assembly diagram", ["operations", "informationPolicy"], "Arrow direction binds the Oxygen counter/pin assembly and other pins to their Character-board apertures.", f"{visual}:RB-P11-V02"),
        assertion("SA-FACILITY-CHARACTER-ANATOMY-VIS", "SRC-RULEBOOK", "printed page 16 / RB-P16-V01 / Character-board anatomy diagram", ["operations", "informationPolicy"], "The anatomy diagram binds Health, Tactical Belt, Hand slots, Oxygen area, Basic Actions, discard area, and lateral item spaces to separate board regions.", f"{visual}:RB-P16-V01"),
        assertion("SA-FACILITY-AMMO-SETUP-VIS", "SRC-RULEBOOK", "printed page 10 / RB-P10-V01 / full Ammo token face association", ["operations", "informationPolicy"], "Character Setup step 7 binds the red full-magazine face to the Ammo token placed on each starting Ammo slot.", f"{visual}:RB-P10-V01"),
    ]
    records.append(record(
        "SEM-CHARACTER-BOARD-SETUP-001", "Character-board slots and initial player-area state", "source-backed", "procedure", "official-primary", "verbatim-structure",
        character_assertions,
        ["term.character-health", "term.backpack", "term.tactical-gear-token", "term.heavy-item", "term.landing-zone", "icon.actionCard", "icon.ammoToken", "icon.oxygenToken"],
        ["tax.scaffold.zone.character-board", "tax.scaffold.zone.backpack", "tax.entity.component.token.tactical-gear", "tax.entity.component.card.item.heavy", "tax.entity.spatial.room.landing-zone", "tax.entity.component.card.action", "tax.entity.component.token.tactical-gear.ammo", "tax.entity.component.token.tactical-gear.oxygen", "tax.entity.component.slot.hand", "tax.entity.component.card.item.armor", "tax.state.health", "tax.value.resource.oxygen"],
        [], timing("TW-CHARACTER-BOARD-SETUP", "tax.scaffold.zone.character-board", "when-triggered", "once-per-Character-setup"),
        [participant("P-PLAYER", "decision-owner", "tax.entity.agent.player"), participant("P-CHARACTER", "affected", "tax.entity.agent.character"), participant("P-SETUP", "setup-procedure")], "must", [], [],
        [{"informationId": "I-CHARACTER-BOARD-SETUP", "subjectRef": "board/tile, Health/Oxygen initial state, public Landing Zone model, deck/discard positions, and class-defined starting-item slots", "audience": "public-except-shuffled-hand-and-deck-identities", "revealTrigger": "setup/placement", "secrecy": "Action deck order, hand identities, and unrevealed Objective identities remain owner-private under their own source procedures"}], [], [],
        [
            operation("S01", 1, "place-component", "must", "P-PLAYER", "one matching Character tile in one Character board", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-CHARACTER-ANATOMY-VIS"]),
            operation("S02", 2, "place-component", "must", "P-SETUP", "one Universal marker in the left-most Health-track slot", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-CHARACTER-ANATOMY-VIS"]),
            operation("S03", 3, "set-state", "must", "P-SETUP", "Character Oxygen counter at maximum value 7", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-CHARACTER-ASSEMBLY-VIS"]),
            operation("S04", 4, "place-component", "must", "P-SETUP", "chosen Character miniature in its matching colored ring and in the Landing Zone", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-CHARACTER-ANATOMY-VIS"]),
            operation("S05", 5, "place-component", "must", "P-SETUP", "numbered Backpack holder above the Character board", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-CHARACTER-ANATOMY-VIS"]),
            operation("S06", 6, "shuffle", "must", "P-SETUP", "all Action cards for the Character face down to the left of the board, leaving discard space to the right", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-CHARACTER-ANATOMY-VIS"]),
            operation("S07", 7, "place-component", "must", "P-SETUP", "Character Item in Hand slot if Heavy or Heavily Injured Health section if Armor; fill every starting Ammo slot with one full-side-up Ammo token", ["SA-FACILITY-CHARACTER-SETUP-RB", "SA-FACILITY-AMMO-SETUP-VIS"]),
            operation("S08", 8, "evaluate-condition", "must", "P-SETUP", "Contractor starts with two Character Items; other Character setup uses its one Character Item", ["SA-FACILITY-CHARACTER-SETUP-RB"]),
        ],
        {"policy": "ordered-complete", "unit": "one Character setup instruction", "onImpossible": "No alternate board slot, ring, starting location, item-class placement, or Ammo-face fallback is supplied by the source."},
        {"kind": "initial-character-board-state"}, {"policy": "one physical board/tile/holder/miniature assignment per Character; starting slots do not merge with later lifecycle"}, [], [], []
    ))

    marker_assertions = [
        assertion("SA-FACILITY-MARKERS-RB", "SRC-RULEBOOK", "printed page 23 / lines 4427–4468", ["preconditions", "operations", "partialResolution", "duration", "stacking"], "Noise markers are placed in Corridors; Fire markers and Secure tokens are placed in Rooms; Malfunction markers may be placed on Rooms, Heavy Items, and Robot cards. Room Fire and Malfunction markers have one-per-Room limits, repeated placement is ignored, and finite marker-limit fallback is source-defined.", f"{rb}:lines 4427–4468"),
        assertion("SA-FACILITY-MARKERS-VIS", "SRC-RULEBOOK", "printed page 23 / RB-P23-V01 / Room marker/token placement example", ["operations", "informationPolicy"], "The worked Room example distinguishes Character model/ring, Secure tokens, Fire marker, and printed Room Item metadata as separate coexisting physical elements.", f"{visual}:RB-P23-V01"),
        assertion("SA-FACILITY-NOISE-ICON-VIS", "SRC-RULEBOOK", "printed page 9 / RB-P09-V02 / Noise marker inline icon association", ["operations", "informationPolicy"], "The component-list Noise marker name is bound to its yellow triangular/radiating icon occurrence.", f"{visual}:RB-P09-V02"),
    ]
    records.append(record(
        "SEM-MAP-MARKER-PLACEMENT-001", "Map marker surfaces, printed Room icons, and finite marker state", "source-backed-with-open-question", "constraint", "official-primary", "open-alternatives",
        marker_assertions,
        ["term.room", "term.corridor", "icon.noise", "icon.fire", "icon.malfunction", "icon.secure", "term.universal-marker"],
        ["tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.entity.component.marker.noise", "tax.entity.component.marker.fire", "tax.entity.component.marker.malfunction", "tax.entity.component.token.secure", "tax.entity.component.marker.universal", "tax.scaffold.supply-pool"],
        [], timing("TW-MAP-MARKERS", "tax.entity.spatial.facility", "when-triggered", "per-marker-placement-or-discard"),
        [participant("P-RULES", "rules-system"), participant("P-EFFECT", "effect-owner")], "must", [], [],
        [{"informationId": "I-MAP-MARKERS", "subjectRef": "marker/token kind, map surface, host component, count, and printed-versus-runtime distinction", "audience": "public", "revealTrigger": "placement/continuous", "secrecy": "markers and their hosts are public; no source-defined hidden marker face is invented"}], [], [],
        [
            operation("S01", 1, "place-component", "if-able", "P-RULES", "Noise marker only in a Corridor", ["SA-FACILITY-MARKERS-RB", "SA-FACILITY-NOISE-ICON-VIS"]),
            operation("S02", 2, "place-component", "if-able", "P-RULES", "Fire marker only in a Room and at most one Fire marker per Room", ["SA-FACILITY-MARKERS-RB", "SA-FACILITY-MARKERS-VIS"]),
            operation("S03", 3, "place-component", "if-able", "P-RULES", "Secure token only in a Room, subject to Room-specific Secure restrictions and existing generic Secure limits", ["SA-FACILITY-MARKERS-RB", "SA-FACILITY-MARKERS-VIS"]),
            operation("S04", 4, "place-component", "if-able", "P-RULES", "Malfunction marker on a source-eligible component; at most one on a Room and repeated Room placement is ignored", ["SA-FACILITY-MARKERS-RB"]),
            operation("S05", 5, "evaluate-condition", "must", "P-RULES", "printed Room Item/Computer/Other icons are tile metadata, not runtime marker tokens", ["SA-FACILITY-MARKERS-RB", "SA-FACILITY-MARKERS-VIS"]),
            operation("S06", 6, "evaluate-condition", "must", "P-RULES", "marker supply is finite and no unlisted Room-marker, Exploration-marker, or Suppression-marker component is invented", ["SA-FACILITY-MARKERS-RB"]),
        ],
        {"policy": "source-limited-components", "unit": "one marker placement", "onImpossible": "Apply source-defined one-per-host/Room restrictions and finite marker rules; do not substitute an unnamed marker or silently move a marker to another surface."},
        {"kind": "persistent-public-marker-state"}, {"policy": "runtime markers and printed tile icons never stack as one semantic component"}, [], ["SEM-Q-110"], []
    ))

    tile_assertions = [
        assertion("SA-FACILITY-ROOM-TILE-RB", "SRC-RULEBOOK", "printed page 20 / lines 4007–4040", ["operations", "preconditions", "informationPolicy", "duration"], "Rooms are Section Rooms A/B/C, which always appear in their associated Section, or random ? Rooms, which may appear in any Section. The Room tile front has Name, Effect, Item Icons, Computer Icon, Type/ID, and Other Icons; printed restrictions govern Secure/Malfunction eligibility.", f"{rb}:lines 4007–4040"),
        assertion("SA-FACILITY-ROOM-TILE-VIS", "SRC-RULEBOOK", "printed page 20 / RB-P20-V01 / Room-tile front/back anatomy", ["operations", "informationPolicy"], "The front/back diagram binds the Room front anatomy and Section-letter back to separate physical sides/regions.", f"{visual}:RB-P20-V01"),
        assertion("SA-FACILITY-ROOM-RESTRICTION-VIS", "SRC-RULEBOOK", "printed page 20 / RB-P20-V02 / Room restriction glyph definitions", ["operations", "informationPolicy"], "The Room restriction glyphs are distinct printed Other Icons and remain separate from runtime Secure/Malfunction markers.", f"{visual}:RB-P20-V02"),
        assertion("SA-FACILITY-NEST-FIRE-VIS", "SRC-RULEBOOK", "printed page 20 / RB-P20-V03 / Nest/Fire icon association", ["operations", "informationPolicy"], "The Nest and Fire icon occurrence is bound to the named Room/map-state context; it is not a generic Fire marker alias for every Room icon.", f"{visual}:RB-P20-V03"),
    ]
    records.append(record(
        "SEM-ROOM-TILE-STATE-001", "Room-tile face/back, discovery, and printed restriction state", "source-backed", "constraint", "official-primary", "source-composed",
        tile_assertions,
        ["term.room", "term.section", "term.discovered", "term.undiscovered", "term.nest", "icon.fire", "icon.secure", "icon.malfunction"],
        ["tax.entity.spatial.room", "tax.entity.spatial.section", "tax.state.discovery.discovered", "tax.state.discovery.undiscovered", "tax.entity.spatial.room.nest", "tax.entity.component.marker.fire", "tax.entity.component.token.secure", "tax.entity.component.marker.malfunction", "tax.entity.information.component-definition.room"],
        [], timing("TW-ROOM-TILE-STATE", "tax.entity.spatial.room", "when-triggered", "per-Room-tile-state"),
        [participant("P-RULES", "rules-system"), participant("P-ROOM", "map-state", "tax.entity.spatial.room")], "must", [], [],
        [{"informationId": "I-ROOM-TILE-STATE", "subjectRef": "Room face/back, Name/Effect/icons/Type/ID, discovery state, and printed restriction glyphs", "audience": "public-after-discovery", "revealTrigger": "Room placement/discovery", "secrecy": "face-down Room identity remains hidden until source-defined placement/discovery"}], [], [],
        [
            operation("S01", 1, "evaluate-condition", "must", "P-RULES", "face-up Room exposes Name, Effect, Item Icons, Computer Icon, Type/ID, and Other Icons as separate front regions", ["SA-FACILITY-ROOM-TILE-RB", "SA-FACILITY-ROOM-TILE-VIS"]),
            operation("S02", 2, "set-state", "must", "P-RULES", "face-down Room tile/back is Undiscovered or unrevealed until its source-defined placement/discovery", ["SA-FACILITY-ROOM-TILE-RB", "SA-FACILITY-ROOM-TILE-VIS"]),
            operation("S03", 3, "evaluate-condition", "must", "P-RULES", "A/B/C Section type and ? random type remain distinct; Room ID remains source-local tie-break metadata", ["SA-FACILITY-ROOM-TILE-RB"]),
            operation("S04", 4, "set-state", "must", "P-RULES", "printed no-Secure/no-Malfunction Room restrictions remain persistent tile properties and do not become removable runtime markers", ["SA-FACILITY-ROOM-RESTRICTION-VIS"]),
            operation("S05", 5, "evaluate-condition", "must", "P-RULES", "Nest/Fire printed icon association remains source-scoped to the Nest Room/map-state", ["SA-FACILITY-NEST-FIRE-VIS"]),
        ],
        {"policy": "per-effect-check", "unit": "one Room tile side or printed feature", "onImpossible": "Do not reveal a face-down tile early, convert a printed icon into a runtime token, or merge fixed named spaces with random Room-tile identities."},
        {"kind": "room-definition-and-discovery-state"}, {"policy": "front/back and printed/runtime states remain separate"}, [], [], []
    ))

    visual_assertions = _visual_assertions(source_index, assertion)
    visual_ops = []
    visual_descriptions = {
        "RB-P04-V01": "exact illustrated component inventory rows and subtype counts",
        "RB-P08-V01": "full versus half-full Ammo token faces as two distinct faces of one token family",
        "RB-P08-V02": "Primebloods/Intruders terminology and its exact inline creature glyph occurrence",
        "RB-P09-V02": "Noise marker name and exact inline glyph association",
        "RB-P10-V01": "starting full Ammo face and full-side-up placement association",
        "RB-P11-V02": "Character-board pin/counter assembly arrows and apertures",
        "RB-P12-V01": "icon-keyed Round summary associations without adding unrelated phase rules",
        "RB-P14-V03": "Intruder and Fire icon associations without adding unrelated phase rules",
        "RB-P15-V01": "token-face-to-outcome-row associations as a visual reference projection",
        "RB-P15-V02": "Round-track token and Anti-Aircraft face/outcome associations for setup/track state",
        "RB-P16-V01": "Character-board slot and anatomy boundaries",
        "RB-P19-V01": "three-section color boundary, 21 regular slot contours, and fixed-space geometry boundary",
        "RB-P19-V02": "Active/Inactive Life Support glyph pairing",
        "RB-P20-V01": "Room front/back anatomy and type/ID placement",
        "RB-P20-V02": "Room restriction glyph definitions as printed tile metadata",
        "RB-P20-V03": "Nest/Fire icon association as source-local Room/map state",
        "RB-P21-V02": "one-ended Unexplored Corridor topology example",
        "RB-P22-V02": "Door-blocking worked map labels and intervening topology",
        "RB-P23-V01": "coexisting Room markers/tokens versus printed Room metadata",
    }
    for index, row in enumerate(source_index["visualObligations"], 1):
        occurrence = row["occurrenceId"]
        visual_ops.append(operation(f"S{index:02d}", index, "evaluate-condition", "must", "P-RULES", visual_descriptions[occurrence], [f"SA-FACILITY-{occurrence}"], notes="source-local visual projection only; it does not create a global icon, geometry, component, or terminology alias."))
    records.append(record(
        "SEM-FACILITY-VISUAL-ASSOCIATIONS-001", "Facility/setup visual associations without text or geometry flattening", "source-backed", "constraint", "official-primary", "verbatim-structure",
        visual_assertions,
        ["term.facility", "term.map", "term.room", "term.corridor", "term.door", "term.section", "term.round-marker", "term.universal-marker", "term.tactical-gear-token", "term.hibernatorium", "term.landing-zone", "term.nest", "icon.fire", "icon.malfunction", "icon.noise", "icon.secure", "icon.intruder", "icon.lander", "icon.autodestruction", "icon.lifeSupportActive", "icon.lifeSupportInactive", "icon.ammoToken", "icon.oxygenToken"],
        ["tax.entity.spatial.facility", "tax.entity.spatial.map", "tax.entity.spatial.room", "tax.entity.spatial.corridor", "tax.entity.spatial.door", "tax.entity.spatial.section", "tax.entity.component.token.round", "tax.entity.component.marker.universal", "tax.entity.component.token.tactical-gear", "tax.entity.spatial.room.hibernatorium", "tax.entity.spatial.room.landing-zone", "tax.entity.spatial.room.nest", "tax.entity.component.marker.fire", "tax.entity.component.marker.malfunction", "tax.entity.component.marker.noise", "tax.entity.component.token.secure", "tax.entity.agent.intruder", "tax.entity.component.token.lander", "tax.entity.component.token.autodestruction"],
        [], timing("TW-FACILITY-VISUAL", "tax.entity.spatial.map", "when-triggered", "once-per-exact-visual-occurrence"),
        [participant("P-RULES", "rules-system"), participant("P-SOURCE-AUDIT", "source-audit")], "must", [], [],
        [{"informationId": "I-FACILITY-VISUAL", "subjectRef": "exact source visual, labels, icon/face association, geometry, orientation, arrows, section color, and overlay relation", "audience": "public-source-evidence", "revealTrigger": "source audit", "secrecy": "visual associations do not expose hidden runtime component identities or create gameplay aliases"}], [], [], visual_ops,
        {"policy": "per-effect-check", "unit": "one exact rulebook visual obligation", "onImpossible": "Preserve the visual obligation as source evidence and do not substitute nearby text, color, shape, title, or implementation behavior."},
        {"kind": "source-visual-association-projection"}, {"policy": "visual geometry/text/icon/face associations are independent projections"}, [], [], []
    ))
    return records


def build_facility_question_rows() -> list[dict]:
    return [
        {
            "questionId": "SEM-Q-106",
            "title": "Section-border orientation and fixed Landing Zone/Hibernatorium edge crosswalk",
            "decisionClass": "source-ambiguity-owner-decision-after-source-search",
            "blocksRuleIds": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-ROOM-SETUP-001", "SEM-ROUND-TRACK-SETUP-001"],
            "plannedRuleIds": [],
            "defaultProhibited": True,
            "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 2417–2444", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01", "docs/rules/semantics/facility-source-index.json:topologyProjection"],
            "alternatives": [
                {"alternativeId": "SEM-Q-106-A", "description": "The single illustrated Section-border arrangement is the required physical orientation and fixes the special-space edge crosswalk.", "support": "setup says connect and place the border pieces; the p.19 diagram shows one exact arrangement but does not state whether rotation is legal"},
                {"alternativeId": "SEM-Q-106-B", "description": "The pieces may be physically rotated or equivalently arranged while preserving Section A/B/C identities and all slot geometry.", "support": "the prose does not expressly prohibit rotation; no alternate arrangement is illustrated"},
                {"alternativeId": "SEM-Q-106-C", "description": "A separate source-defined physical orientation/crosswalk applies to the fixed Landing Zone/Hibernatorium spaces.", "support": "the rendered special border-piece spaces are not regular variable hex slots and their exact edge pairing is not textually assigned"},
            ],
        },
        {
            "questionId": "SEM-Q-107",
            "title": "Special-space Corridor endpoints and fixed-space connector assignment",
            "decisionClass": "source-ambiguity-owner-decision-after-source-search",
            "blocksRuleIds": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-CORRIDOR-SETUP-001"],
            "plannedRuleIds": [],
            "defaultProhibited": True,
            "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 2399–2403,3915–3921", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01/RB-P21-V02", "docs/rules/semantics/facility-source-index.json:fixedMapSpaces"],
            "alternatives": [
                {"alternativeId": "SEM-Q-107-A", "description": "Only the measured paired regular-slot gaps are legal Corridor connectors; fixed named spaces use their own source-defined border-piece entrances.", "support": "the visual separates special border-piece geometry from regular Room contours"},
                {"alternativeId": "SEM-Q-107-B", "description": "One or more fixed-space edges are also regular Corridor endpoints and must be crosswalked to named variable slots.", "support": "Hibernatorium/Landing Zone are Rooms in source prose and can be connected by Corridors, but the exact rendered edge pairing is not assigned"},
                {"alternativeId": "SEM-Q-107-C", "description": "Another source-defined special-space connector topology applies.", "support": "no complete labeled endpoint map is present in the checked text"},
            ],
        },
        {
            "questionId": "SEM-Q-108",
            "title": "Initial Landing Zone entrance selection for Corridor Door-slot orientation",
            "decisionClass": "source-ambiguity-owner-decision-after-source-search",
            "blocksRuleIds": ["SEM-FACILITY-CORRIDOR-SETUP-001"],
            "plannedRuleIds": [],
            "defaultProhibited": True,
            "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 2399–2403,4244–4252", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01", "docs/rules/semantics/facility-source-index.json:topologyProjection"],
            "alternatives": [
                {"alternativeId": "SEM-Q-108-A", "description": "Each initial Corridor with a Door slot is oriented toward the one source-defined Landing Zone entrance used by the physical map.", "support": "the setup instruction uses singular “an entrance to the Landing Zone” but does not name a selector"},
                {"alternativeId": "SEM-Q-108-B", "description": "The setup actor chooses among multiple legal Landing Zone entrances independently for each drawn Corridor.", "support": "the prose says connect three Corridors one by one but does not state an entrance choice or order"},
                {"alternativeId": "SEM-Q-108-C", "description": "A deterministic physical edge/order rule assigns each Door-slot Corridor entrance.", "support": "a digital implementation would need a tie-break, but no source tie-break is stated"},
            ],
        },
        {
            "questionId": "SEM-Q-109",
            "title": "Setup component shortage, replacement, and simultaneous placement atomicity",
            "decisionClass": "official-clarification-preferred",
            "blocksRuleIds": ["SEM-FACILITY-COMPONENT-INVENTORY-001", "SEM-FACILITY-ROOM-SETUP-001", "SEM-FACILITY-CORRIDOR-SETUP-001", "SEM-ROUND-TRACK-SETUP-001"],
            "plannedRuleIds": [],
            "defaultProhibited": True,
            "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 2399–2476", "docs/rulebooks/rulebook_text.txt:lines 2659–2746", "docs/rulebooks/rulebook_text.txt:lines 3530–3548", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P04-V01"],
            "alternatives": [
                {"alternativeId": "SEM-Q-109-A", "description": "Setup cannot begin or the affected setup step is invalid when a required physical component is unavailable.", "support": "setup uses exact imperative quantities and supplies no replacement"},
                {"alternativeId": "SEM-Q-109-B", "description": "Use the generic finite-component rule and place/add only available components, leaving excess requests unresolved.", "support": "the general component-limit rule covers gameplay effects but does not expressly extend to setup"},
                {"alternativeId": "SEM-Q-109-C", "description": "Apply another source-defined shortage, proxy, replacement, or atomic-group rule.", "support": "no checked setup passage states one"},
            ],
        },
        {
            "questionId": "SEM-Q-110",
            "title": "Unnamed Room-marker, Exploration-marker, or Suppression-marker component identity",
            "decisionClass": "source-ambiguity-owner-decision-after-source-search",
            "blocksRuleIds": ["SEM-MAP-MARKER-PLACEMENT-001"],
            "plannedRuleIds": [],
            "defaultProhibited": True,
            "sourceEvidenceRefs": ["docs/rulebooks/rulebook_text.txt:lines 4427–4468", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P23-V01", "docs/rules/semantics/facility-source-index.json:componentInventory"],
            "alternatives": [
                {"alternativeId": "SEM-Q-110-A", "description": "No separate generic Room-marker, Exploration-marker, or Suppression-marker component exists; use only the named Fire, Malfunction, Noise, Secure, Universal, and source-defined cover/token components.", "support": "the checked inventory and map-marker section name specific components but no generic Room-marker family"},
                {"alternativeId": "SEM-Q-110-B", "description": "A source-local unnamed marker is a distinct physical component whose identity/face and placement surface remain to be recovered.", "support": "visual examples can show pieces whose extracted labels are absent; no exact component crosswalk is currently established"},
                {"alternativeId": "SEM-Q-110-C", "description": "One of the named marker/token families is intended as the generic Room/Exploration/Suppression marker in a source-specific context.", "support": "contextual use may be suggested by diagrams but no global alias is authoritative"},
            ],
        },
    ]


def build_facility_conflicts() -> list[dict]:
    return [
        {
            "conflictId": "SC-083",
            "title": "Twenty-three physical Room tiles versus twenty-five Room Help entries",
            "status": "resolved-by-authority",
            "questionId": None,
            "affectedRuleIds": ["SEM-FACILITY-COMPONENT-INVENTORY-001", "SEM-FACILITY-ROOM-SETUP-001", "SEM-ROOM-TILE-STATE-001"],
            "evidenceRefs": ["SRC-RULEBOOK", "SRC-ROOM-HELP", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P04-V01", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01"],
            "difference": "The main component inventory gives 23 Room tiles, while the Room Help sheet has 25 numbered effects and includes Landing Zone and Hibernatorium fixed-space entries in addition to the 23 tile-backed effects.",
            "resolution": "Keep 23 physical tiles and the two fixed named spaces separate. Room Help numbering is an effect/reference inventory, not a 25-tile physical count.",
        },
        {
            "conflictId": "SC-084",
            "title": "Official three-section map prose versus source-local rendered section geometry",
            "status": "resolved-by-authority",
            "questionId": None,
            "affectedRuleIds": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-VISUAL-ASSOCIATIONS-001"],
            "evidenceRefs": ["SRC-RULEBOOK", "SRC-FND-005", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01"],
            "difference": "The official prose names three Sections A/B/C, while the rendered diagram carries exact colored boundaries, special border-piece spaces, and 21 regular variable contours that plain text cannot preserve.",
            "resolution": "Use the official three-section proposition and the independently pinned rendered geometry together; do not replace the geometry with a text-only rectangular or four-section map.",
        },
        {
            "conflictId": "SC-085",
            "title": "Room-edge proximity versus legal Corridor adjacency",
            "status": "preserved-boundary",
            "questionId": None,
            "affectedRuleIds": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-CORRIDOR-SETUP-001", "SEM-DOOR-001"],
            "evidenceRefs": ["SRC-RULEBOOK", "SRC-FND-005", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P21-V02"],
            "difference": "The visual projection identifies reserved edge gaps and one-ended Corridor topology, while source rules make actual Room movement/connection depend on a placed legal Corridor and preserve adjacency through a Door.",
            "resolution": "Retain paired edge gaps, Corridor endpoints, actual Corridor occupancy, and Door blocking as separate states. Proximity never creates a gameplay connection.",
        },
        {
            "conflictId": "SC-086",
            "title": "Fixed Landing Zone/Hibernatorium border geometry lacks a complete text-labeled endpoint crosswalk",
            "status": "unresolved",
            "questionId": "SEM-Q-107",
            "affectedRuleIds": ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-CORRIDOR-SETUP-001"],
            "evidenceRefs": ["SRC-RULEBOOK", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P19-V01", "docs/rules/semantics/facility-source-index.json:fixedMapSpaces"],
            "difference": "The rendered diagram visibly separates fixed border-piece named spaces from regular hex contours, but the checked prose does not assign every special-space edge to a named regular Corridor endpoint.",
            "resolution": "No default. Preserve the special-space geometry and leave the exact endpoint crosswalk under SEM-Q-107.",
        },
        {
            "conflictId": "SC-087",
            "title": "Setup imperative quantities versus generic finite-component fallback",
            "status": "unresolved",
            "questionId": "SEM-Q-109",
            "affectedRuleIds": ["SEM-FACILITY-COMPONENT-INVENTORY-001", "SEM-FACILITY-ROOM-SETUP-001", "SEM-FACILITY-CORRIDOR-SETUP-001", "SEM-ROUND-TRACK-SETUP-001"],
            "evidenceRefs": ["SRC-RULEBOOK", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P04-V01"],
            "difference": "Setup directs exact quantities and positions, while the generic Component Limits rule says unavailable components do nothing for effects; no source explicitly extends that fallback to setup or defines replacement/atomicity.",
            "resolution": "No default. Do not substitute, duplicate, proxy, or partially resolve a setup component request until SEM-Q-109 is answered.",
        },
        {
            "conflictId": "SC-088",
            "title": "Named map markers versus possible unnamed visual overlay components",
            "status": "unresolved",
            "questionId": "SEM-Q-110",
            "affectedRuleIds": ["SEM-MAP-MARKER-PLACEMENT-001", "SEM-ROOM-TILE-STATE-001"],
            "evidenceRefs": ["SRC-RULEBOOK", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P23-V01", "docs/rules/source-extraction/rulebook-visual-obligations.json:RB-P20-V02", "docs/rules/semantics/facility-source-index.json:componentInventory"],
            "difference": "The checked map-marker text names Noise, Fire, Malfunction, Secure, and Universal components, while the bounded task vocabulary also uses Room-marker/Exploration/Suppression language and visual examples do not create a verified separate physical component identity.",
            "resolution": "No generic alias or hidden component is invented. Keep printed Room icons, named runtime markers, Hibernatorium cover, and Universal marker distinct under SEM-Q-110.",
        },
    ]
