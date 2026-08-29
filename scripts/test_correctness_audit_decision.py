#!/usr/bin/env python3
"""Focused threshold tests for the Stage 1 decision evaluator."""

from __future__ import annotations

import copy
import unittest

import evaluate_correctness_audit as target
import validate_correctness_audit as validation

MANIFEST = validation.strict_load(validation.MANIFEST_PATH)
PROGRESS = validation.strict_load(validation.PROGRESS_PATH)


def family(unit: dict) -> str:
    if unit["unitClass"] == "sampled-component-effect":
        return unit["family"]
    return "concise-rule" if unit["unitClass"] == "concise-rule-record" else "faq"


def clean_fixture() -> tuple[dict, dict]:
    progress = copy.deepcopy(PROGRESS)
    results = {}
    for index, unit in enumerate(MANIFEST["units"]):
        uid = unit["auditUnitId"]
        did = f"D-{index:03d}"
        row = progress["units"][index]
        row["status"] = "accepted"
        results[uid] = {
            "status": "accepted",
            "family": family(unit),
            "comparison": {"discrepancies": [{
                "discrepancyId": did,
                "classification": "match",
                "severity": "none",
                "rootCauseId": None,
                "authorityOverride": False,
                "hiddenDefault": False,
            }]},
            "verificationReviews": [{"reviewedDiscrepancyIds": [did]}],
            "resolution": {"status": "not-required"},
        }
    return progress, results


class DecisionTests(unittest.TestCase):
    def test_incomplete_is_not_ready(self) -> None:
        decision = target.evaluate_records(MANIFEST, PROGRESS, {})
        self.assertEqual(decision["decision"], "incomplete")
        self.assertFalse(decision["decisionReady"])

    def test_clean_fixture_passes_audited_units_only(self) -> None:
        progress, results = clean_fixture()
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["decision"], "pass-audited-units-only")
        self.assertEqual(decision["observedCounts"]["deterministicMatchReviewSample"], 23)
        self.assertIn("140 audited units", decision["claimScope"])
        self.assertIn("199 unaudited", decision["claimScope"])

    def test_critical_forces_full_escalation(self) -> None:
        progress, results = clean_fixture()
        uid = MANIFEST["units"][0]["auditUnitId"]
        results[uid]["status"] = "critical-error"
        results[uid]["comparison"]["discrepancies"][0].update({"classification": "downstream-omission", "severity": "critical", "rootCauseId": "RC-X"})
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["decision"], "fail-or-escalate")
        self.assertTrue(decision["fullAuditEscalationRequired"])

    def test_three_component_material_errors_exceed_limit(self) -> None:
        progress, results = clean_fixture()
        units = [row for row in MANIFEST["units"] if row["unitClass"] == "sampled-component-effect"][:3]
        for index, unit in enumerate(units):
            uid = unit["auditUnitId"]
            results[uid]["status"] = "material-error"
            results[uid]["comparison"]["discrepancies"][0].update({"classification": "downstream-omission", "severity": "material", "rootCauseId": f"RC-{index}"})
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(len(decision["failures"]["componentMaterialErrorsOverLimit"]), 3)

    def test_recurring_root_across_two_families_fails(self) -> None:
        progress, results = clean_fixture()
        units = [row for row in MANIFEST["units"] if row["unitClass"] == "sampled-component-effect"]
        first = units[0]
        second = next(row for row in units if row["family"] != first["family"])
        for unit in (first, second):
            uid = unit["auditUnitId"]
            results[uid]["status"] = "material-error"
            results[uid]["comparison"]["discrepancies"][0].update({"classification": "downstream-omission", "severity": "material", "rootCauseId": "RC-SHARED"})
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["recurringDefectPatterns"], ["RC-SHARED"])

    def test_unverified_match_sample_fails(self) -> None:
        progress, results = clean_fixture()
        sample = target.select_match_review_sample(MANIFEST, results)
        results[sample[0]]["verificationReviews"] = []
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["unverifiedDeterministicMatchSample"], [sample[0]])

    def test_nonmatch_none_severity_cannot_pass_direct_evaluator(self) -> None:
        progress, results = clean_fixture()
        uid = MANIFEST["units"][0]["auditUnitId"]
        results[uid]["comparison"]["discrepancies"][0]["classification"] = "downstream-omission"
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["invalidClassificationSeverityUnits"], [uid])
        self.assertEqual(decision["decision"], "fail-or-escalate")

    def test_empty_repair_proof_remains_unresolved(self) -> None:
        progress, results = clean_fixture()
        uid = MANIFEST["units"][0]["auditUnitId"]
        results[uid]["status"] = "material-error"
        results[uid]["comparison"]["discrepancies"][0].update({
            "classification": "downstream-omission",
            "severity": "material",
            "rootCauseId": "RC-REPAIR",
        })
        results[uid]["resolution"] = {
            "status": "repaired-verified",
            "repairPaths": [],
            "verificationEvidenceRefs": [],
        }
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["unresolvedCoreMaterialErrors"], [uid])


if __name__ == "__main__":
    unittest.main(verbosity=2)
