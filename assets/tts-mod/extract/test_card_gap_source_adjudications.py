#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_card_text_corpus as corpus

REPO = Path(__file__).resolve().parents[3]
REVIEW = REPO / "docs/rules/source-extraction/card-gap-adjudications.json"


class CardGapSourceAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.review = json.loads(REVIEW.read_text())
        cls.payload = corpus.build_payload()
        cls.rows = {row["sourcePath"]: row for row in cls.payload["records"]}
        cls.entries = {row["assetId"]: row for row in cls.review["entries"]}

    def test_review_closes_all_thirteen_source_tuples(self):
        self.assertEqual(self.review["schemaVersion"], 1)
        self.assertEqual(self.review["counts"], {
            "records": 13,
            "rulesTextComplete": 9,
            "explicitOperativeSourceBlockers": 1,
            "classifiedNonRules": 3,
            "recoveredOperativeCorrections": 1,
            "materialUnreadableVisibleRulesSpans": 1,
        })
        self.assertEqual(list(self.entries), [f"G{index:02d}" for index in range(1, 14)])
        for entry in self.review["entries"]:
            with self.subTest(assetId=entry["assetId"]):
                source = REPO / entry["sourcePath"]
                self.assertTrue(source.is_file())
                self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), entry["sourceSha256"])
                self.assertIn(entry["sourcePath"], self.rows)
                self.assertEqual(self.rows[entry["sourcePath"]]["extractionState"], entry["expectedExtractionState"])
                self.assertEqual(
                    self.rows[entry["sourcePath"]]["evidence"]["sourceExtractionReview"]["evidencePath"],
                    "docs/rules/source-extraction/card-gap-adjudications.json",
                )

    def test_nine_rules_complete_records_exclude_nonrules_markers(self):
        for asset_id in ("G01", "G03", "G04", "G05", "G07", "G08", "G09", "G10", "G11"):
            path = self.entries[asset_id]["sourcePath"]
            row = self.rows[path]
            with self.subTest(assetId=asset_id):
                self.assertEqual(row["extractionState"], "draft-full")
                self.assertNotIn("[illegible]", json.dumps(row["printedData"], ensure_ascii=False))
                self.assertNotIn("[clipped]", json.dumps(row["printedData"], ensure_ascii=False))
                self.assertEqual(row["printedData"].get("illegibleSpans", []), [])
                self.assertEqual(row["printedData"].get("clippedSpans", []), [])

    def test_facility_restart_remains_smallest_honest_source_blocker(self):
        path = self.entries["G02"]["sourcePath"]
        row = self.rows[path]
        self.assertEqual(row["extractionState"], "draft-partial")
        self.assertIn("Systems must be [illegible]", row["printedData"]["body"])
        self.assertIn("no recoverable mark after", row["evidence"]["sourceExtractionReview"]["finding"])
        self.assertIn("[illegible]", row["selectedExtraction"]["visibleText"]["body"])

    def test_submachine_gun_recovers_colon_without_rewriting_selected_raw_overlay(self):
        path = self.entries["G11"]["sourcePath"]
        row = self.rows[path]
        self.assertEqual(row["extractionState"], "draft-full")
        self.assertIn("[shootDie2]: treat this result", row["printedData"]["body"])
        self.assertNotIn("[illegible]", row["printedData"]["body"])
        self.assertIn("[shootDie2][illegible] treat", row["selectedExtraction"]["visibleText"]["body"])
        self.assertEqual(row["evidence"]["sourceExtractionReview"]["disposition"], "rules-text-complete-punctuation-recovered")

    def test_three_blank_or_back_sources_are_classified_nonrules(self):
        expected = {
            "G06": "generic-card-back",
            "G12": "near-uniform-black-placeholder",
            "G13": "near-uniform-black-placeholder",
        }
        for asset_id, classification in expected.items():
            path = self.entries[asset_id]["sourcePath"]
            row = self.rows[path]
            with self.subTest(assetId=asset_id):
                self.assertEqual(row["extractionState"], "non-rules-or-reference")
                self.assertEqual(row["rulesInformationReadiness"], "not-rules-bearing-or-reference")
                self.assertFalse(row["rulesTextPresent"])
                self.assertEqual(row["evidence"]["sourceComponentClassification"]["classification"], classification)
                self.assertFalse(row["evidence"]["sourceComponentClassification"]["rulesBearing"])

    def test_selected_worker_evidence_remains_unmodified_history(self):
        for asset_id in ("G01", "G03", "G04", "G05", "G07", "G08", "G09", "G10", "G11"):
            path = self.entries[asset_id]["sourcePath"]
            selected = self.rows[path]["selectedExtraction"]["visibleText"]
            with self.subTest(assetId=asset_id):
                self.assertIn("[illegible]", json.dumps(selected, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
