#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from semantic_facility_validation import validate_facility_family

REPO = Path(__file__).resolve().parents[1]
DIR = REPO / "docs/rules/semantics"


def load(name: str):
    return json.loads((DIR / name).read_text(encoding="utf-8"))


class FacilityAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.source = load("facility-source-index.json")
        pilots = load("pilots.json")
        review = load("review-gates.json")
        coverage = load("coverage.json")
        backlog = load("backlog.json")
        contradictions = load("contradictions.json")
        self.records = {row["ruleId"]: row for row in pilots["records"]}
        self.questions = {row["questionId"]: row for row in review["questions"]}
        self.conflicts = contradictions["conflicts"]
        self.coverage = coverage
        self.backlog = {row["semanticUnitId"]: row for row in backlog["units"]}

    def run_mutation(self, mutate_source=None, mutate_records=None):
        source = copy.deepcopy(self.source)
        records = copy.deepcopy(self.records)
        if mutate_source:
            mutate_source(source)
        if mutate_records:
            mutate_records(records)
        failures = []
        with tempfile.NamedTemporaryFile(prefix="facility-index-", suffix=".json") as handle:
            # The validator intentionally checks the pinned live source path, not
            # this temporary payload. The payload is supplied as the parsed index.
            result = validate_facility_family(
                REPO, DIR / "facility-source-index.json", source, records,
                copy.deepcopy(self.questions), copy.deepcopy(self.conflicts), copy.deepcopy(self.coverage),
                copy.deepcopy(self.backlog), failures,
            )
        self.assertIsInstance(result, dict)
        return {row["check"] for row in failures}

    def test_component_drop_and_same_count_component_swap_rejected(self):
        def drop(source):
            source["componentInventory"].pop()
        self.assertIn("Facility exact component inventory projection", self.run_mutation(drop))

        def same_count_swap(source):
            rows = source["componentInventory"]
            rows[6], rows[7] = rows[7], rows[6]  # Scanner and Intruder bag are both count 1.
        self.assertIn("Facility exact component inventory projection", self.run_mutation(same_count_swap))

    def test_section_slot_swap_and_orientation_inversion_rejected(self):
        def section_swap(source):
            source["roomSlots"][0]["section"] = "B"
        self.assertIn("Facility independent pinned Room-slot geometry", self.run_mutation(section_swap))

        def orientation_inversion(source):
            source["roomSlots"][0]["edgeDirections"] = ["NW", "W", "SW", "SE", "E", "NE"]
        self.assertIn("Facility independent pinned Room-slot geometry", self.run_mutation(orientation_inversion))

    def test_room_corridor_edge_collapse_rejected(self):
        def collapse(source):
            source["topologyProjection"]["edgeAdjacency"].pop()
        self.assertIn("Facility independent paired Corridor-gap geometry", self.run_mutation(collapse))

        def corridor_collapse(source):
            source["topologyProjection"]["edgeAdjacency"][0]["isGameplayCorridor"] = True
        self.assertIn("Facility gap/Corridor state separation", self.run_mutation(corridor_collapse))

    def test_door_slot_state_collapse_rejected(self):
        def mutate(records):
            door = records["SEM-DOOR-001"]
            operation = next(row for row in door["operations"] if row["stepId"] == "S04")
            operation["objectRef"] = "Closed Door blocks movement/effects"
        self.assertIn("Facility Door/slot/state boundary projection", self.run_mutation(mutate_records=mutate))

    def test_front_back_and_token_face_swaps_rejected(self):
        def front_back(records):
            operation = records["SEM-ROOM-TILE-STATE-001"]["operations"][1]
            operation["objectRef"] = "face-up Room tile/back is discovered before placement"
        self.assertIn("Facility setup/state boundary projection", self.run_mutation(mutate_records=front_back))

        def token_face(records):
            operation = records["SEM-ROUND-TRACK-SETUP-001"]["operations"][5]
            operation["objectRef"] = operation["objectRef"].replace("face down", "face up")
        self.assertIn("Facility exact Round-track token-face/setup projection", self.run_mutation(mutate_records=token_face))

    def test_marker_swap_finite_supply_and_setup_lifecycle_rejected(self):
        def marker_default(records):
            operation = records["SEM-MAP-MARKER-PLACEMENT-001"]["operations"][5]
            operation["objectRef"] = "marker supply is unlimited and unnamed markers are accepted"
        self.assertIn("Facility finite marker supply/default projection", self.run_mutation(mutate_records=marker_default))

        def setup_lifecycle(records):
            operation = records["SEM-ROUND-TRACK-SETUP-001"]["operations"][0]
            operation["objectRef"] = "Round marker advances during later Cleanup"
        self.assertIn("Facility exact Round-track token-face/setup projection", self.run_mutation(mutate_records=setup_lifecycle))

    def test_source_visual_authority_and_tts_drift_rejected(self):
        def visual_text(source):
            source["visualObligations"][0]["visualUnit"]["description"] = "text-only inventory"
        self.assertIn("Facility exact source/visual projection", self.run_mutation(visual_text))

        def authority(source):
            source["sourceDocuments"]["SRC-RULEBOOK"]["authority"] = "project-interpretation"
        self.assertIn("Facility source document authority projection", self.run_mutation(authority))

        def tts_hash(source):
            source["ttsProvenance"]["roles"]["sha256"] = "0" * 64
        self.assertIn("Facility TTS source tuple", self.run_mutation(tts_hash))

    def test_backlog_lowering_and_default_link_rejected(self):
        def lower(source):
            source["closedPendingBacklogUnitIds"] = source["closedPendingBacklogUnitIds"][:-1]
        self.assertIn("Facility exact backlog link projection", self.run_mutation(lower))

        def invent(source):
            source["backlogRuleLinks"]["RULE:FND-005"] = ["SEM-FACILITY-TOPOLOGY-001", "SEM-FACILITY-CORRIDOR-SETUP-001"]
        self.assertIn("Facility exact backlog link projection", self.run_mutation(invent))


if __name__ == "__main__":
    unittest.main()
