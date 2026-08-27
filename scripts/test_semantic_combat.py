#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
DIR = REPO / "docs/rules/semantics"
VALIDATOR = REPO / "scripts/validate_semantic_pilots.py"


def run_validator(*, combat=None, pilots=None, review=None, backlog=None) -> tuple[int, dict]:
    command = ["python3", str(VALIDATOR), "--skip-reproducibility"]
    for flag, path in (
        ("--combat-source-index", combat),
        ("--pilots", pilots),
        ("--review-gates", review),
        ("--backlog", backlog),
    ):
        if path is not None:
            command.extend([flag, str(path)])
    run = subprocess.run(command, cwd=REPO, check=False, capture_output=True, text=True, timeout=300)
    return run.returncode, json.loads(run.stdout)


def mutated_file(name: str, mutator) -> tuple[tempfile.TemporaryDirectory, Path]:
    temp = tempfile.TemporaryDirectory(prefix="combat-semantic-negative-")
    path = Path(temp.name) / name
    value = json.loads((DIR / name).read_text(encoding="utf-8"))
    mutator(value)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return temp, path


def record(value: dict, rule_id: str) -> dict:
    return next(row for row in value["records"] if row["ruleId"] == rule_id)


def resequence(operations: list[dict]) -> None:
    for index, operation in enumerate(operations, 1):
        operation["stepId"] = f"S{index:02d}"
        operation["sequence"] = index


class CombatSemanticAdversarialTests(unittest.TestCase):
    def assertRejected(self, name: str, mutator, check: str, *, argument: str) -> None:
        temp, path = mutated_file(name, mutator)
        try:
            kwargs = {argument: path}
            returncode, report = run_validator(**kwargs)
        finally:
            temp.cleanup()
        self.assertNotEqual(returncode, 0)
        self.assertTrue(any(row.get("check") == check for row in report["failures"]), report)

    def test_current_combat_projection_passes(self):
        returncode, report = run_validator()
        self.assertEqual(returncode, 0, report)
        self.assertTrue(report["passed"])
        self.assertEqual(report["checks"]["combatSourceSegments"], 15)
        self.assertEqual(report["checks"]["combatVisualObligations"], 9)
        self.assertEqual(report["checks"]["combatNewRecords"], 14)
        self.assertEqual(report["checks"]["combatClosedBacklogUnits"], 11)
        self.assertEqual(report["checks"]["backlogPilotCovered"], 510)

    def test_noise_hazard_branch_collapse_is_rejected(self):
        def mutate(value):
            row = record(value, "SEM-NOISE-RESULT-001")
            branches = next(op["resultBranches"] for op in row["operations"] if op.get("resultBranches"))
            branches[-1] = {"termId": "icon.noiseDieHazard", "resultClass": "corridor-number", "corridorValue": 4}
        self.assertRejected("pilots.json", mutate, "Combat Noise/Hazard branch separation", argument="pilots")

    def test_token_bag_type_order_loss_is_rejected(self):
        def mutate(value):
            operations = record(value, "SEM-NOISE-MARKER-001")["operations"]
            operations[0], operations[1] = operations[1], operations[0]
            resequence(operations)
        self.assertRejected("pilots.json", mutate, "Combat token/bag/type/order and Blank dispatch closure", argument="pilots")

    def test_attack_class_collapse_is_rejected(self):
        def mutate(value):
            row = record(value, "SEM-OPPORTUNITY-ATTACK-001")
            next(op for op in row["operations"] if op.get("invokeRuleId") == "SEM-INT-004")["attackClass"] = "hazard-entry"
        self.assertRejected("pilots.json", mutate, "Combat normal/Opportunity/Hazard/Intruder attack-class collapse", argument="pilots")

    def test_shoot_melee_result_substitution_is_rejected(self):
        def mutate(value):
            shoot = next(op["resultBranches"] for op in record(value, "SEM-SHOOT-DIE-RESULT-001")["operations"] if op.get("resultBranches"))
            melee = next(op["resultBranches"] for op in record(value, "SEM-MELEE-SHOOT-DIE-RESULT-001")["operations"] if op.get("resultBranches"))
            shoot[-1]["standardResult"], melee[-1]["standardResult"] = melee[-1]["standardResult"], shoot[-1]["standardResult"]
        self.assertRejected("pilots.json", mutate, "Combat Shoot/Burst/Melee die-result substitution or inversion", argument="pilots")

    def test_target_owner_default_invention_is_rejected(self):
        def mutate(value):
            row = record(value, "SEM-BURST-SEQUENCE-001")
            next(item for item in row["decisions"] if item["decisionId"] == "D-BURST-HITS")["ownerRef"] = "P-RULES"
            next(item for item in row["operations"] if item.get("decisionRef") == "D-BURST-HITS")["allocationOwner"] = "P-RULES"
        self.assertRejected("pilots.json", mutate, "Combat target/owner/allocation/default invention closure", argument="pilots")

    def test_movement_attack_timing_flattening_is_rejected(self):
        def mutate(value):
            operations = record(value, "SEM-MOVEMENT-SEQUENCE-001")["operations"]
            operations[1], operations[4] = operations[4], operations[1]
            resequence(operations)
        self.assertRejected("pilots.json", mutate, "Combat movement/attack/reaction timing flattening", argument="pilots")

    def test_same_count_adult_drone_swap_is_rejected(self):
        def mutate(value):
            row = record(value, "SEM-IH-QA-C-02")
            mapping = next(op["repeat"]["tokenFaceResolutions"] for op in row["operations"] if (op.get("repeat") or {}).get("tokenFaceResolutions"))
            mapping["2+1"] = {"adultCount": 1, "droneCount": 2}
        self.assertRejected("pilots.json", mutate, "Combat same-count token/type swap closure", argument="pilots")

    def test_icon_source_visual_geometry_drift_is_rejected(self):
        def mutate(value):
            row = next(item for item in value["visualObligations"] if item["occurrenceId"] == "RB-P33-V01")
            row["visualUnit"]["bbox"][0] += 1
        self.assertRejected("combat-source-index.json", mutate, "Combat exact icon/source/visual/geometry projection", argument="combat")

    def test_finite_supply_same_total_swap_is_rejected(self):
        def mutate(value):
            value["componentCounts"]["noiseMarkers"] = 31
            value["componentCounts"]["universalMarkers"] = 29
        self.assertRejected("combat-source-index.json", mutate, "Combat finite supply/exhaustion invention closure", argument="combat")

    def test_coordinated_backlog_lowering_is_rejected(self):
        def mutate(value):
            value["units"] = [row for row in value["units"] if row["semanticUnitId"] != "VIS:RB-P25-V01"]
            value["counts"]["units"] = 599
            value["counts"]["byChannel"]["rulebook-visual-obligation"] = 79
            value["counts"]["byStatus"]["pilot-covered"] = 509
        self.assertRejected("backlog.json", mutate, "Combat coordinated backlog lowering", argument="backlog")

    def test_no_default_question_invention_is_rejected(self):
        def mutate(value):
            next(row for row in value["questions"] if row["questionId"] == "SEM-Q-098")["defaultProhibited"] = False
        self.assertRejected("review-gates.json", mutate, "Combat no-default question closure", argument="review")

    def test_blank_scope_collapse_is_rejected(self):
        def mutate(value):
            row = record(value, "SEM-IH-QA-BOTTOM-01")
            row["operations"] = row["operations"][1:]
            resequence(row["operations"])
            row["unresolvedQuestionRefs"].remove("SEM-Q-099")
        self.assertRejected("pilots.json", mutate, "Combat side-level Blank return/scope no-default closure", argument="pilots")

    def test_burst_added_effect_before_hits_is_rejected(self):
        def mutate(value):
            operations = record(value, "SEM-BURST-SEQUENCE-001")["operations"]
            additional = next(op for op in operations if op.get("invokeRuleId") == "SEM-WEAPON-DIE-RESULT-ADDITION-001")
            operations.remove(additional)
            operations.insert(4, additional)
            resequence(operations)
        self.assertRejected("pilots.json", mutate, "Combat target/owner/allocation/default invention closure", argument="pilots")

    def test_source_effect_paid_action_wrapper_reintroduction_is_rejected(self):
        def mutate(value):
            row = next(item for item in value["records"] if item["ruleId"].startswith("SEM-ACTION-") and any(op.get("invokeRuleId") == "SEM-MOVEMENT-SEQUENCE-001" for op in item["operations"]))
            next(op for op in row["operations"] if op.get("invokeRuleId") == "SEM-MOVEMENT-SEQUENCE-001")["invokeRuleId"] = "SEM-ACT-MOVE-001"
        self.assertRejected("pilots.json", mutate, "Combat source effect incorrectly invokes paid Basic Action", argument="pilots")


if __name__ == "__main__":
    unittest.main()
