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
            "__comparison": {"discrepancies": [{
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
        results[uid]["__comparison"]["discrepancies"][0].update({"classification": "downstream-omission", "severity": "critical", "rootCauseId": "RC-X"})
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["decision"], "fail-or-escalate")
        self.assertTrue(decision["fullAuditEscalationRequired"])

    def test_three_component_material_errors_exceed_limit(self) -> None:
        progress, results = clean_fixture()
        units = [row for row in MANIFEST["units"] if row["unitClass"] == "sampled-component-effect"][:3]
        for index, unit in enumerate(units):
            uid = unit["auditUnitId"]
            results[uid]["status"] = "material-error"
            results[uid]["__comparison"]["discrepancies"][0].update({"classification": "downstream-omission", "severity": "material", "rootCauseId": f"RC-{index}"})
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
            results[uid]["__comparison"]["discrepancies"][0].update({"classification": "downstream-omission", "severity": "material", "rootCauseId": "RC-SHARED"})
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["recurringDefectPatterns"], ["RC-SHARED"])

    def test_unverified_match_sample_fails(self) -> None:
        progress, results = clean_fixture()
        comparisons = {
            unit_id: {"comparison": result["__comparison"]}
            for unit_id, result in results.items()
        }
        sample = target.select_match_review_sample(MANIFEST, comparisons)
        results[sample[0]]["verificationReviews"] = []
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["unverifiedDeterministicMatchSample"], [sample[0]])

    def test_missing_clean_family_sample_cannot_pass_with_22(self) -> None:
        progress, results = clean_fixture()
        family = sorted(validation.EXPECTED_FAMILIES)[0]
        for result in results.values():
            if result["family"] != family:
                continue
            discrepancy = result["__comparison"]["discrepancies"][0]
            discrepancy["classification"] = "presentation-only"
            discrepancy["severity"] = "none"
            result["verificationReviews"] = [{
                "reviewedDiscrepancyIds": [discrepancy["discrepancyId"]],
            }]
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertFalse(decision["thresholdsSatisfied"])
        self.assertEqual(
            decision["failures"]["deterministicMatchSampleSizeMismatch"],
            [{"expected": 23, "actual": 22}],
        )

    def test_all_compared_publishes_match_sample_before_adjudication(self) -> None:
        progress, results = clean_fixture()
        for row in progress["units"]:
            row["status"] = "compared"
        comparisons = {
            unit_id: {"comparison": result["__comparison"]}
            for unit_id, result in results.items()
        }
        decision = target.evaluate_records(MANIFEST, progress, {}, comparisons)
        self.assertEqual(decision["decision"], "incomplete")
        self.assertEqual(len(decision["deterministicMatchReviewSampleUnitIds"]), 23)

    def test_nonmatch_none_severity_cannot_pass_direct_evaluator(self) -> None:
        progress, results = clean_fixture()
        uid = MANIFEST["units"][0]["auditUnitId"]
        results[uid]["__comparison"]["discrepancies"][0]["classification"] = "downstream-omission"
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["invalidClassificationSeverityUnits"], [uid])
        self.assertEqual(decision["decision"], "fail-or-escalate")

    def test_core_material_error_cannot_be_repaired_inside_frozen_version(self) -> None:
        progress, results = clean_fixture()
        uid = MANIFEST["units"][0]["auditUnitId"]
        results[uid]["status"] = "material-error"
        results[uid]["__comparison"]["discrepancies"][0].update({
            "classification": "downstream-omission",
            "severity": "material",
            "rootCauseId": "RC-REPAIR",
        })
        results[uid]["resolution"] = {
            "status": "repaired-verified",
            "repairPaths": ["docs/rules/00-foundations.md"],
            "verificationEvidenceRefs": ["VR1"],
        }
        decision = target.evaluate_records(MANIFEST, progress, results)
        self.assertEqual(decision["failures"]["unresolvedCoreMaterialErrors"], [uid])


if __name__ == "__main__":
    unittest.main(verbosity=2)
