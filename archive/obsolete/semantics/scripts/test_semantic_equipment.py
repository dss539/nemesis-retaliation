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
EQUIPMENT = DIR / "equipment-source-index.json"


def run_validator(equipment_path: Path = EQUIPMENT, review_path: Path | None = None) -> tuple[int, dict]:
    command = [
        "python3", str(VALIDATOR), "--skip-reproducibility",
        "--equipment-source-index", str(equipment_path),
    ]
    if review_path is not None:
        command.extend(["--review-gates", str(review_path)])
    run = subprocess.run(command, cwd=REPO, check=False, capture_output=True, text=True, timeout=300)
    return run.returncode, json.loads(run.stdout)


def mutated_index(mutator) -> tuple[tempfile.TemporaryDirectory, Path]:
    temp = tempfile.TemporaryDirectory(prefix="equipment-negative-")
    path = Path(temp.name) / "equipment-source-index.json"
    value = json.loads(EQUIPMENT.read_text(encoding="utf-8"))
    mutator(value)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return temp, path


class EquipmentSemanticAdversarialTests(unittest.TestCase):
    def assertRejected(self, mutator, check: str):
        temp, path = mutated_index(mutator)
        try:
            returncode, report = run_validator(path)
        finally:
            temp.cleanup()
        self.assertNotEqual(returncode, 0)
        self.assertTrue(any(row.get("check") == check for row in report["failures"]), report)

    def test_current_equipment_projection_passes(self):
        returncode, report = run_validator()
        self.assertEqual(returncode, 0, report)
        self.assertTrue(report["passed"])
        self.assertEqual(report["checks"]["equipmentTtsPhysicalFaceRecords"], 39)
        self.assertEqual(report["checks"]["equipmentOfficialFaceRecords"], 6)
        self.assertEqual(report["checks"]["equipmentClassConflictExclusions"], 12)
        self.assertEqual(report["checks"]["equipmentBacklogSourceFaceTuples"], 52)

    def test_dropped_support_copy_is_rejected(self):
        self.assertRejected(lambda value: value["supportEquipmentFaces"].pop(), "Support Equipment physical occurrence cardinality/order")

    def test_duplicated_support_copy_is_rejected(self):
        def mutate(value):
            value["supportEquipmentFaces"].append(copy.deepcopy(value["supportEquipmentFaces"][0]))
        self.assertRejected(mutate, "Support Equipment physical occurrence cardinality/order")

    def test_balanced_physical_class_swap_is_rejected(self):
        def mutate(value):
            rows = value["supportEquipmentFaces"]
            first = next(row for row in rows if row["ttsCardGuid"] == "dffd35")
            second = next(row for row in rows if row["ttsCardGuid"] == "8ae645")
            first["physicalClass"], second["physicalClass"] = second["physicalClass"], first["physicalClass"]
        self.assertRejected(mutate, "Support exact physical class projection")

    def test_character_kit_owner_swap_is_rejected(self):
        def mutate(value):
            row = next(row for row in value["characterItemTtsFaces"] if row["ttsCardGuid"] == "21bd03")
            row["ttsCharacterKitOwner"] = "Officer"
        self.assertRejected(mutate, "Character exact kit ancestry")

    def test_generated_sheet_cell_swap_is_rejected(self):
        def mutate(value):
            row = next(row for row in value["supportEquipmentFaces"] if row["ttsCardGuid"] == "dffd35")
            row["sourceSelector"]["generatedCell"] = 10
        self.assertRejected(mutate, "Support generated sheet/hash/grid/cell selector")

    def test_body_punctuation_drift_is_rejected(self):
        def mutate(value):
            row = next(row for row in value["supportEquipmentFaces"] if row["ttsCardGuid"] == "a0f5b7")
            row["printedBody"] += "."
        self.assertRejected(mutate, "Support exact body/punctuation projection")

    def test_class_conflict_promotion_is_rejected(self):
        def mutate(value):
            value["physicalClassConflictExclusions"][0]["semanticDispatchProhibited"] = False
        self.assertRejected(mutate, "Equipment class-conflict exclusion closure")

    def test_default_prohibited_question_drift_is_rejected(self):
        temp = tempfile.TemporaryDirectory(prefix="equipment-question-negative-")
        path = Path(temp.name) / "review-gates.json"
        value = json.loads((DIR / "review-gates.json").read_text(encoding="utf-8"))
        next(row for row in value["questions"] if row["questionId"] == "SEM-Q-083")["defaultProhibited"] = False
        path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            returncode, report = run_validator(review_path=path)
        finally:
            temp.cleanup()
        self.assertNotEqual(returncode, 0)
        self.assertTrue(any(row.get("check") == "Equipment no-default question closure" for row in report["failures"]), report)


if __name__ == "__main__":
    unittest.main()
