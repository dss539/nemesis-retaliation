#!/usr/bin/env python3
"""Evaluate the preregistered Stage 1 decision thresholds."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import validate_correctness_audit as validation

ROOT = validation.ROOT
AUDIT_DIR = validation.AUDIT_DIR
FINAL_STATUSES = {"accepted", "material-error", "critical-error", "source-blocked"}


def rank(unit_id: str) -> str:
    return hashlib.sha256(f"nemesis-stage1-lane-d-match-v1|{unit_id}".encode()).hexdigest()


def result_map(progress: dict[str, Any]) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for row in progress["units"]:
        if row["status"] in FINAL_STATUSES:
            result = validation.strict_load(ROOT / row["resultPath"])
            comparison = validation.strict_load(ROOT / row["comparisonPath"])
            result["__comparison"] = comparison["comparison"]
            results[row["auditUnitId"]] = result
    return results


def comparison_map(progress: dict[str, Any]) -> dict[str, dict[str, Any]]:
    comparisons: dict[str, dict[str, Any]] = {}
    for row in progress["units"]:
        if row["status"] in FINAL_STATUSES | {"compared"}:
            comparisons[row["auditUnitId"]] = validation.strict_load(ROOT / row["comparisonPath"])
    return comparisons


def pure_match(result: dict[str, Any]) -> bool:
    rows = result["__comparison"]["discrepancies"]
    return bool(rows) and all(row["classification"] == "match" and row["severity"] == "none" for row in rows)


def verification_covers(result: dict[str, Any]) -> bool:
    expected = {row["discrepancyId"] for row in result["__comparison"]["discrepancies"]}
    reviewed: set[str] = set()
    for review in result["verificationReviews"]:
        reviewed.update(review["reviewedDiscrepancyIds"])
    return expected.issubset(reviewed)


def valid_classification_severity(row: dict[str, Any]) -> bool:
    classification = row.get("classification")
    severity = row.get("severity")
    if classification == "match":
        return severity == "none"
    if classification in {
        "downstream-omission",
        "downstream-overstatement",
        "source-ambiguity-lost",
        "source-conflict-flattened",
        "transcription-or-packet-gap",
    }:
        return severity in {"minor", "material", "critical", "blocked"}
    if classification in {"authority-inversion", "hidden-default"}:
        return severity == "critical"
    if classification in {"source-ambiguity-preserved", "source-conflict-preserved"}:
        return severity == "none"
    if classification == "presentation-only":
        return severity in {"none", "minor"}
    return False


def select_match_review_sample(
    manifest: dict[str, Any], comparisons: dict[str, dict[str, Any]]
) -> list[str]:
    units = {row["auditUnitId"]: row for row in manifest["units"]}
    clean = [
        uid
        for uid, comparison in comparisons.items()
        if bool(comparison["comparison"]["discrepancies"])
        and all(
            row["classification"] == "match" and row["severity"] == "none"
            for row in comparison["comparison"]["discrepancies"]
        )
    ]
    chosen: list[str] = []
    sample_plan = manifest["passThreshold"]["deterministicCleanMatchReviewSample"]
    for unit_class, count in sample_plan["perUnitClass"].items():
        pool = [uid for uid in clean if units[uid]["unitClass"] == unit_class]
        chosen.extend(sorted(pool, key=lambda uid: (rank(uid), uid))[:count])
    for family in sorted(validation.EXPECTED_FAMILIES):
        pool = [uid for uid in clean if units[uid].get("family") == family]
        quota = sample_plan["perComponentFamily"]
        chosen.extend(sorted(pool, key=lambda uid: (rank(uid), uid))[:quota])
    return chosen


def evaluate_records(
    manifest: dict[str, Any],
    progress: dict[str, Any],
    results: dict[str, dict[str, Any]],
    comparisons: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    units = {row["auditUnitId"]: row for row in manifest["units"]}
    if comparisons is None:
        comparisons = {
            unit_id: {"comparison": result["__comparison"]}
            for unit_id, result in results.items()
        }
    match_sample = select_match_review_sample(manifest, comparisons)
    unfinished = [row["auditUnitId"] for row in progress["units"] if row["status"] not in FINAL_STATUSES]
    if unfinished:
        comparisons_complete = all(
            row["status"] not in {"pending-blind-derivation", "blind-derived"}
            for row in progress["units"]
        )
        partial_source_blocked = sorted(
            unit_id
            for unit_id, result in results.items()
            if result.get("status") == "source-blocked"
            or any(
                row.get("severity") == "blocked"
                for row in result.get("__comparison", {}).get("discrepancies", [])
                if isinstance(row, dict)
            )
        )
        partial_affected_families = sorted(
            {
                result.get("family")
                for result in results.values()
                if isinstance(result.get("family"), str)
                and any(
                    row.get("severity") in {"material", "critical", "blocked"}
                    or row.get("authorityOverride") is True
                    or row.get("hiddenDefault") is True
                    for row in result.get("__comparison", {}).get("discrepancies", [])
                    if isinstance(row, dict)
                )
            }
        )
        decision = {
            "schemaVersion": 1,
            "recordType": "stage-1-correctness-audit-decision",
            "decision": "incomplete",
            "decisionReady": False,
            "unfinishedUnitIds": unfinished,
            "sourceBlockedUnitIds": partial_source_blocked,
            "affectedFamilyEscalationCandidates": partial_affected_families,
            "claimScope": (
                "No correctness or rewrite-readiness conclusion is authorized while any unit is unfinished. "
                "The audit covers 140 units only and does not establish correctness of the approximately "
                "199 unaudited primary component-effect units."
            ),
        }
        if comparisons_complete:
            decision["deterministicMatchReviewSampleUnitIds"] = match_sample
        return decision

    critical_units: set[str] = set()
    authority_units: set[str] = set()
    hidden_default_units: set[str] = set()
    material_component_units: set[str] = set()
    unresolved_core_material_units: set[str] = set()
    source_blocked_units: set[str] = set()
    invalid_classification_units: set[str] = set()
    root_units: dict[str, set[str]] = defaultdict(set)
    root_families: dict[str, set[str]] = defaultdict(set)

    for unit_id, result in results.items():
        unit = units[unit_id]
        if result["status"] == "critical-error":
            critical_units.add(unit_id)
        if result["status"] == "material-error":
            if unit["unitClass"] == "sampled-component-effect":
                material_component_units.add(unit_id)
            else:
                unresolved_core_material_units.add(unit_id)
        if result["status"] == "source-blocked":
            source_blocked_units.add(unit_id)
        for row in result["__comparison"]["discrepancies"]:
            if not valid_classification_severity(row):
                invalid_classification_units.add(unit_id)
            if row["severity"] == "critical":
                critical_units.add(unit_id)
            elif row["severity"] == "material":
                if unit["unitClass"] == "sampled-component-effect":
                    material_component_units.add(unit_id)
                else:
                    unresolved_core_material_units.add(unit_id)
            elif row["severity"] == "blocked":
                source_blocked_units.add(unit_id)
            if row["authorityOverride"]:
                authority_units.add(unit_id)
            if row["hiddenDefault"]:
                hidden_default_units.add(unit_id)
            if row["severity"] in {"material", "critical"} and row["rootCauseId"]:
                root = row["rootCauseId"]
                root_units[root].add(unit_id)
                root_families[root].add(result["family"])

    recurring = sorted(
        root
        for root in root_units
        if len(root_units[root]) >= 3 or len(root_families[root]) >= 2
    )
    unverified_match_sample = sorted(
        uid for uid in match_sample if not verification_covers(results[uid])
    )
    expected_match_sample = manifest["passThreshold"]["deterministicCleanMatchReviewSample"]["total"]
    failures = {
        "criticalErrors": sorted(critical_units),
        "inventedAuthorityOverrides": sorted(authority_units),
        "hiddenDefaults": sorted(hidden_default_units),
        "recurringDefectPatterns": recurring,
        "unresolvedCoreMaterialErrors": sorted(unresolved_core_material_units),
        "componentMaterialErrorsOverLimit": sorted(material_component_units)
        if len(material_component_units)
        > manifest["passThreshold"]["maximumIsolatedMaterialErrorsInComponentSample"]
        else [],
        "sourceBlockedUnits": sorted(source_blocked_units),
        "invalidClassificationSeverityUnits": sorted(invalid_classification_units),
        "deterministicMatchSampleSizeMismatch": []
        if len(match_sample) == expected_match_sample
        else [{"expected": expected_match_sample, "actual": len(match_sample)}],
        "unverifiedDeterministicMatchSample": unverified_match_sample,
    }
    passed = not any(failures.values())
    decision = "pass-audited-units-only" if passed else "fail-or-escalate"
    full_escalation = bool(
        critical_units
        or authority_units
        or hidden_default_units
        or recurring
        or invalid_classification_units
        or len(material_component_units)
        > manifest["passThreshold"]["maximumIsolatedMaterialErrorsInComponentSample"]
    )
    recurring_units = {
        uid
        for root in recurring
        for uid in root_units[root]
    }
    affected_families = sorted(
        {
            results[uid]["family"]
            for uid in (
                critical_units
                | material_component_units
                | unresolved_core_material_units
                | source_blocked_units
                | authority_units
                | hidden_default_units
                | recurring_units
            )
        }
    )
    return {
        "schemaVersion": 1,
        "recordType": "stage-1-correctness-audit-decision",
        "decision": decision,
        "decisionReady": True,
        "unfinishedUnitIds": [],
        "thresholdsSatisfied": passed,
        "failures": failures,
        "observedCounts": {
            "criticalErrorUnits": len(critical_units),
            "authorityOverrideUnits": len(authority_units),
            "hiddenDefaultUnits": len(hidden_default_units),
            "recurringDefectPatterns": len(recurring),
            "unresolvedCoreMaterialErrorUnits": len(unresolved_core_material_units),
            "componentMaterialErrorUnits": len(material_component_units),
            "sourceBlockedUnits": len(source_blocked_units),
            "invalidClassificationSeverityUnits": len(invalid_classification_units),
            "deterministicMatchReviewSample": len(match_sample),
            "unverifiedMatchSampleUnits": len(unverified_match_sample),
        },
        "deterministicMatchReviewSampleUnitIds": match_sample,
        "affectedFamilyEscalationCandidates": affected_families,
        "fullAuditEscalationRequired": full_escalation,
        "claimScope": (
            "Any pass applies only to the 140 audited units in the base-competitive Stage 1 population. "
            "It is not an error-rate estimate and does not establish correctness of the approximately "
            "199 unaudited primary component-effect units in the current ~255-unit planning inventory."
        ),
        "sourceBlockedUnitIds": sorted(source_blocked_units),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="docs/qa/implementation-readiness/correctness-audit/reports/decision.json",
    )
    args = parser.parse_args()
    structural = validation.validate(require_lock=validation.LOCK_PATH.is_file())
    if not structural["passed"]:
        raise SystemExit("structural validation failed; decision not evaluated")
    manifest = validation.strict_load(validation.MANIFEST_PATH)
    progress = validation.strict_load(validation.PROGRESS_PATH)
    comparisons = comparison_map(progress)
    decision = evaluate_records(manifest, progress, result_map(progress), comparisons)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(decision, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))
    return 0 if decision["decision"] == "pass-audited-units-only" else 2


if __name__ == "__main__":
    raise SystemExit(main())
