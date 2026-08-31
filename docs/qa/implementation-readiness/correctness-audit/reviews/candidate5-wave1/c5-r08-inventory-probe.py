#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

REPO = Path("/home/smithers/projects/nemesis-c5-r08/repos/nemesis-retaliation")
MODULE_PATH = REPO / "scripts/build_correctness_audit_prompt.py"
spec = importlib.util.spec_from_file_location("candidate_prompt", MODULE_PATH)
assert spec and spec.loader
prompt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt)


def load(name: str):
    return json.loads((prompt.AUDIT_DIR / name).read_text(encoding="utf-8"))


def schema_names(value) -> set[str]:
    result: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            result.update(str(key) for key in properties)
        for child in value.values():
            result.update(schema_names(child))
    elif isinstance(value, list):
        for child in value:
            result.update(schema_names(child))
    return result


manifest = load("manifest.json")
actual_paths, actual_ids = prompt.source_only_forbidden_inventory()
manifest_section_paths: dict[str, set[str]] = {}
for section in (
    "frozenSemanticHashes",
    "frozenConciseRuleHashes",
    "selectionInputHashes",
):
    mapping = manifest.get(section, {})
    manifest_section_paths[section] = {
        str(path)
        for path in mapping
        if not str(path).startswith(prompt.ALLOWED_SOURCE_PATH_PREFIXES)
    }
unit_paths_by_field: dict[str, set[str]] = {}
for field in ("downstreamPath", "extractionPath"):
    unit_paths_by_field[field] = {
        row[field]
        for row in manifest.get("units", [])
        if isinstance(row, dict)
        and isinstance(row.get(field), str)
        and not row[field].startswith(prompt.ALLOWED_SOURCE_PATH_PREFIXES)
    }
expected_paths = set(prompt.SOURCE_ONLY_FIXED_PATH_TOKENS)
for values in manifest_section_paths.values():
    expected_paths.update(values)
for values in unit_paths_by_field.values():
    expected_paths.update(values)

comparison_names = schema_names(load("comparison.schema.json"))
audit_result_names = schema_names(load("audit-result.schema.json"))
source_packet_names = schema_names(load("source-packet.schema.json"))
completeness_names = schema_names(load("packet-completeness-review.schema.json"))
raw_closed_ids = (
    set(prompt.SOURCE_ONLY_FIXED_IDENTIFIERS)
    | comparison_names
    | audit_result_names
)
source_allowed_ids = source_packet_names | completeness_names
candidate4_inventory_ids = raw_closed_ids - set(prompt.SOURCE_ONLY_SHARED_IDENTIFIERS)
expected_ids = candidate4_inventory_ids - source_allowed_ids

path_matrix = []
for token in sorted(actual_paths):
    value_failures = prompt.source_only_payload_failures(
        {"value": f"fixture {token} fixture"}
    )
    key_failures = prompt.source_only_payload_failures({token: "fixture"})
    path_matrix.append(
        {
            "token": token,
            "valueDetected": any(
                row.endswith(f"contains forbidden path {token}")
                for row in value_failures
            ),
            "keyDetected": any(
                row.endswith(f"contains forbidden path key {token}")
                for row in key_failures
            ),
            "valueFailureCount": len(value_failures),
            "keyFailureCount": len(key_failures),
        }
    )

id_matrix = []
for token in sorted(actual_ids):
    value_failures = prompt.source_only_payload_failures(
        {"value": f"fixture {token} fixture"}
    )
    key_failures = prompt.source_only_payload_failures({token: "fixture"})
    id_matrix.append(
        {
            "token": token,
            "valueDetected": any(
                row.endswith(f"contains forbidden identifier {token}")
                for row in value_failures
            ),
            "keyDetected": any(
                row.endswith(f"contains forbidden identifier key {token}")
                for row in key_failures
            ),
            "valueFailureCount": len(value_failures),
            "keyFailureCount": len(key_failures),
        }
    )

removed_for_source_payload = sorted(candidate4_inventory_ids & source_allowed_ids)
removed_matrix = []
for token in removed_for_source_payload:
    key_failures = prompt.source_only_payload_failures({token: "fixture"})
    value_failures = prompt.source_only_payload_failures(
        {"value": f"fixture {token} fixture"}
    )
    removed_matrix.append(
        {
            "token": token,
            "keyAllowed": not key_failures,
            "valueAllowed": not value_failures,
            "keyFailures": key_failures,
            "valueFailures": value_failures,
        }
    )

result = {
    "candidateHead": "d78e91e9f0d29eab7e9d838d4fc043ba73518cec",
    "paths": {
        "actualCount": len(actual_paths),
        "expectedIndependentCount": len(expected_paths),
        "fixedCount": len(prompt.SOURCE_ONLY_FIXED_PATH_TOKENS),
        "manifestSectionUniqueCounts": {
            key: len(value) for key, value in manifest_section_paths.items()
        },
        "unitFieldUniqueCounts": {
            key: len(value) for key, value in unit_paths_by_field.items()
        },
        "missingFromActual": sorted(expected_paths - actual_paths),
        "unexpectedInActual": sorted(actual_paths - expected_paths),
        "allKeysDetected": all(row["keyDetected"] for row in path_matrix),
        "allValuesDetected": all(row["valueDetected"] for row in path_matrix),
        "keyDetectedCount": sum(row["keyDetected"] for row in path_matrix),
        "valueDetectedCount": sum(row["valueDetected"] for row in path_matrix),
        "matrix": path_matrix,
    },
    "identifiers": {
        "actualCount": len(actual_ids),
        "expectedIndependentCount": len(expected_ids),
        "fixedCount": len(prompt.SOURCE_ONLY_FIXED_IDENTIFIERS),
        "comparisonSchemaPropertyCount": len(comparison_names),
        "auditResultSchemaPropertyCount": len(audit_result_names),
        "rawClosedUnionCount": len(raw_closed_ids),
        "candidate4AfterSharedAllowlistCount": len(candidate4_inventory_ids),
        "removedBecauseSourcePacketOrCompletenessCount": len(removed_for_source_payload),
        "removedBecauseSourcePacketOrCompleteness": removed_for_source_payload,
        "missingFromActual": sorted(expected_ids - actual_ids),
        "unexpectedInActual": sorted(actual_ids - expected_ids),
        "allKeysDetected": all(row["keyDetected"] for row in id_matrix),
        "allValuesDetected": all(row["valueDetected"] for row in id_matrix),
        "keyDetectedCount": sum(row["keyDetected"] for row in id_matrix),
        "valueDetectedCount": sum(row["valueDetected"] for row in id_matrix),
        "matrix": id_matrix,
        "removedSourcePayloadFieldsAllowed": all(
            row["keyAllowed"] and row["valueAllowed"] for row in removed_matrix
        ),
        "removedMatrix": removed_matrix,
    },
    "overallPass": (
        actual_paths == expected_paths
        and actual_ids == expected_ids
        and all(row["keyDetected"] and row["valueDetected"] for row in path_matrix)
        and all(row["keyDetected"] and row["valueDetected"] for row in id_matrix)
        and all(row["keyAllowed"] and row["valueAllowed"] for row in removed_matrix)
    ),
}
print(json.dumps(result, indent=2, sort_keys=True))
