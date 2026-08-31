#!/usr/bin/env python3
"""Independent candidate-5 source-only inventory and closure probe."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path("/home/smithers/projects/nemesis-c5-r01/repos/nemesis-retaliation")
OUTPUT = Path("/home/smithers/projects/nemesis-c5-r01/review-output")
AUDIT_REL = Path("docs/qa/implementation-readiness/correctness-audit")
AUDIT = REPO / AUDIT_REL
PROMPT_SCRIPT = REPO / "scripts/build_correctness_audit_prompt.py"
RESULT = OUTPUT / "source-only-inventory-probe-results.json"
PROBE_ROOT = OUTPUT / "source-only-probe-root"
PRIOR_PROBE_ROOT = OUTPUT / "source-only-prior-probe-root"

EXPECTED_HEAD = "d78e91e9f0d29eab7e9d838d4fc043ba73518cec"
PRIOR_HEAD = "9af725a59b20d8d70a13487f0e588d7306ee16e6"
ALLOWED_SOURCE_PREFIXES = (
    "docs/rulebooks/",
    "docs/rules/source-extraction/",
    "assets/tts-mod/extract/",
)
FIXED_PATHS = {
    "docs/rules/00-foundations.md",
    "docs/rules/01-round-and-turns.md",
    "docs/rules/02-character-actions.md",
    "docs/rules/03-intruders-and-survival.md",
    "docs/rules/04-items-and-equipment.md",
    "docs/rules/semantics/",
    "docs/rules/ontology/",
    "docs/rules/vocabulary/",
    "docs/rules/implementation-readiness.md",
    "docs/design/",
    "archive/design/",
    "index.html",
    "js/",
    "css/",
}
FIXED_IDENTIFIERS = {
    "downstreamPath",
    "extractionPath",
    "revealedArtifacts",
    "semanticRecordIds",
    "questionIds",
    "conflictIds",
    "discrepancies",
    "blindDerivationRef",
    "comparisonRef",
    "verificationReviews",
    "repairPaths",
    "physicalClass",
    "batchDisposition",
    "equipmentStratum",
}
EXPLICIT_SHARED_IDENTIFIERS = {
    "schemaVersion",
    "recordType",
    "auditUnitId",
    "sealedAtUtc",
    "sealedAtGitHead",
    "reviewer",
    "reviewId",
    "kind",
    "reviewerId",
    "provider",
    "requestedModel",
    "responseModel",
    "requestedReasoning",
    "requestMode",
    "promptPath",
    "promptSha256",
    "responsePath",
    "responseSha256",
    "thinkingRetained",
    "path",
    "sha256",
    "role",
    "evidenceRefs",
}
SCHEMA_NAMES = (
    "comparison.schema.json",
    "audit-result.schema.json",
    "source-packet.schema.json",
    "packet-completeness-review.schema.json",
)


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def independent_schema_properties(value: Any) -> set[str]:
    """Collect every JSON Schema properties member without candidate helpers."""
    found: set[str] = set()
    pending = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, dict):
            properties = current.get("properties")
            if isinstance(properties, dict):
                found.update(properties.keys())
            pending.extend(current.values())
        elif isinstance(current, list):
            pending.extend(current)
    return found


def discover_manifest_path_values(value: Any, parent_key: str = "") -> set[str]:
    """Inventory repository-like values below path/hash/target fields."""
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if isinstance(child, str) and (
                "path" in lowered
                or "target" in lowered
                or lowered.endswith("hashes")
            ) and "/" in child:
                found.add(child)
            elif isinstance(child, dict) and lowered.endswith("hashes"):
                found.update(str(item) for item in child if "/" in str(item))
            found.update(discover_manifest_path_values(child, key))
    elif isinstance(value, list):
        for child in value:
            found.update(discover_manifest_path_values(child, parent_key))
    return found


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_cli(root: Path, args: list[str]) -> dict[str, Any]:
    command = [sys.executable, "scripts/build_correctness_audit_prompt.py", *args]
    completed = subprocess.run(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": command,
        "returnCode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, capture_output=True, check=True
    ).stdout.strip()
    if head != EXPECTED_HEAD:
        raise SystemExit(f"wrong HEAD: {head}")

    spec = importlib.util.spec_from_file_location("candidate_prompt", PROMPT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import candidate prompt builder")
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)

    manifest = load_json(AUDIT / "manifest.json")
    schemas = {name: load_json(AUDIT / name) for name in SCHEMA_NAMES}
    props = {name: independent_schema_properties(value) for name, value in schemas.items()}

    expected_paths = set(FIXED_PATHS)
    for section in (
        "frozenSemanticHashes",
        "frozenConciseRuleHashes",
        "selectionInputHashes",
    ):
        mapping = manifest.get(section, {})
        if isinstance(mapping, dict):
            expected_paths.update(
                str(path)
                for path in mapping
                if not str(path).startswith(ALLOWED_SOURCE_PREFIXES)
            )
    non_source_unit_paths: set[str] = set()
    for unit in manifest.get("units", []):
        if not isinstance(unit, dict):
            continue
        for field in ("downstreamPath", "extractionPath", "sourcePath"):
            path = unit.get(field)
            if isinstance(path, str) and not path.startswith(ALLOWED_SOURCE_PREFIXES):
                expected_paths.add(path)
                non_source_unit_paths.add(path)

    discovered_manifest_paths = discover_manifest_path_values(manifest)
    discovered_non_source_manifest_paths = {
        path
        for path in discovered_manifest_paths
        if not path.startswith(ALLOWED_SOURCE_PREFIXES)
    }

    raw_post_ids = (
        set(FIXED_IDENTIFIERS)
        | props["comparison.schema.json"]
        | props["audit-result.schema.json"]
    )
    after_explicit = raw_post_ids - EXPLICIT_SHARED_IDENTIFIERS
    source_packet_overlap = after_explicit & props["source-packet.schema.json"]
    completeness_overlap = after_explicit & props["packet-completeness-review.schema.json"]
    expected_ids = (
        after_explicit
        - props["source-packet.schema.json"]
        - props["packet-completeness-review.schema.json"]
    )

    actual_paths, actual_ids = candidate.source_only_forbidden_inventory()
    actual_paths = set(actual_paths)
    actual_ids = set(actual_ids)

    inventory = {
        "pathCount": len(actual_paths),
        "identifierCount": len(actual_ids),
        "paths": sorted(actual_paths),
        "identifiers": sorted(actual_ids),
        "expectedPathCount": len(expected_paths),
        "expectedIdentifierCount": len(expected_ids),
        "missingPaths": sorted(expected_paths - actual_paths),
        "unexpectedPaths": sorted(actual_paths - expected_paths),
        "missingIdentifiers": sorted(expected_ids - actual_ids),
        "unexpectedIdentifiers": sorted(actual_ids - expected_ids),
        "nonSourceUnitPaths": sorted(non_source_unit_paths),
        "discoveredNonSourceManifestPathsNotForbidden": sorted(
            discovered_non_source_manifest_paths - actual_paths
        ),
        "schemaPropertyCounts": {name: len(value) for name, value in props.items()},
        "sourcePacketSchemaAllowlist": sorted(props["source-packet.schema.json"]),
        "completenessSchemaAllowlist": sorted(
            props["packet-completeness-review.schema.json"]
        ),
        "sourcePacketPostRevealOverlapRemoved": sorted(source_packet_overlap),
        "completenessPostRevealOverlapRemoved": sorted(completeness_overlap),
        "explicitSharedAllowlist": sorted(EXPLICIT_SHARED_IDENTIFIERS),
        "candidateSchemaTraversalMatchesIndependent": {
            name: set(candidate.schema_property_names(schemas[name])) == props[name]
            for name in SCHEMA_NAMES
        },
    }

    id_rows: list[dict[str, Any]] = []
    for identifier in sorted(actual_ids):
        exact_key = candidate.source_only_payload_failures(
            {"level1": [{"level2": {identifier: "benign"}}]}
        )
        exact_value = candidate.source_only_payload_failures(
            {"level1": [{"level2": f"before:{identifier}:after"}]}
        )
        wrapped_key_name = f"before:{identifier}:after"
        wrapped_key = candidate.source_only_payload_failures(
            {"level1": [{"level2": {wrapped_key_name: "benign"}}]}
        )
        embedded_value = candidate.source_only_payload_failures(
            {"level1": [{"level2": f"beforeX{identifier}Yafter"}]}
        )
        id_rows.append(
            {
                "identifier": identifier,
                "exactNestedKeyRejected": bool(exact_key),
                "boundaryNestedValueRejected": bool(exact_value),
                "boundaryWrappedNestedKeyRejected": bool(wrapped_key),
                "alphanumericEmbeddedValueAccepted": not bool(embedded_value),
                "exactKeyFailures": exact_key,
                "wrappedKeyFailures": wrapped_key,
            }
        )

    path_rows: list[dict[str, Any]] = []
    for path_token in sorted(actual_paths):
        exact_key = candidate.source_only_payload_failures(
            {"level1": [{"level2": {path_token: "benign"}}]}
        )
        boundary_value = candidate.source_only_payload_failures(
            {"level1": [{"level2": f"before:{path_token}after"}]}
        )
        wrapped_key = candidate.source_only_payload_failures(
            {"level1": [{"level2": {f"before:{path_token}:after": "benign"}}]}
        )
        left_embedded_value = candidate.source_only_payload_failures(
            {"level1": [{"level2": f"X{path_token}"}]}
        )
        path_rows.append(
            {
                "path": path_token,
                "exactNestedKeyRejected": bool(exact_key),
                "boundaryNestedValueRejected": bool(boundary_value),
                "boundaryWrappedNestedKeyRejected": bool(wrapped_key),
                "alphanumericLeftEmbeddedValueAccepted": not bool(left_embedded_value),
            }
        )

    shared_rows: list[dict[str, Any]] = []
    for schema_name, allowed in (
        ("source-packet.schema.json", props["source-packet.schema.json"]),
        (
            "packet-completeness-review.schema.json",
            props["packet-completeness-review.schema.json"],
        ),
    ):
        for identifier in sorted(allowed):
            key_failures = candidate.source_only_payload_failures(
                {"level1": [{identifier: "benign"}]}
            )
            value_failures = candidate.source_only_payload_failures(
                {"level1": [f"before:{identifier}:after"]}
            )
            shared_rows.append(
                {
                    "schema": schema_name,
                    "identifier": identifier,
                    "exactNestedKeyAccepted": not bool(key_failures),
                    "boundaryNestedValueAccepted": not bool(value_failures),
                    "keyFailures": key_failures,
                    "valueFailures": value_failures,
                }
            )

    if PROBE_ROOT.exists():
        shutil.rmtree(PROBE_ROOT)
    (PROBE_ROOT / "scripts").mkdir(parents=True)
    shutil.copy2(PROMPT_SCRIPT, PROBE_ROOT / "scripts/build_correctness_audit_prompt.py")
    mirror_audit = PROBE_ROOT / AUDIT_REL
    (mirror_audit / "prompts").mkdir(parents=True)
    (mirror_audit / "packets").mkdir(parents=True)
    for name in SCHEMA_NAMES + ("manifest.json",):
        shutil.copy2(AUDIT / name, mirror_audit / name)
    for name in (
        "packet-completeness-instructions.txt",
        "blind-derivation-instructions.txt",
    ):
        shutil.copy2(AUDIT / "prompts" / name, mirror_audit / "prompts" / name)

    wrapped_keys = {f"before:{identifier}:after": "benign" for identifier in sorted(actual_ids)}
    benign_packet = mirror_audit / "packets/benign-packet.json"
    boundary_packet = mirror_audit / "packets/boundary-key-packet.json"
    boundary_review = mirror_audit / "packets/boundary-key-review.json"
    exact_packet = mirror_audit / "packets/exact-key-packet.json"
    exact_review = mirror_audit / "packets/exact-key-review.json"
    value_packet = mirror_audit / "packets/exact-value-packet.json"
    write_json(benign_packet, {"benign": "value"})
    write_json(boundary_packet, {"outer": [{"inner": wrapped_keys}]})
    write_json(boundary_review, {"outer": [[{"inner": wrapped_keys}]]})
    write_json(exact_packet, {"outer": [{"inner": {"rootCauseId": "benign"}}]})
    write_json(exact_review, {"outer": [[{"inner": {"rootCauseId": "benign"}}]]})
    write_json(value_packet, {"outer": [{"inner": "before:rootCauseId:after"}]})

    cli_cases: dict[str, Any] = {}
    cli_cases["completenessBoundaryWrappedKeys"] = run_cli(
        PROBE_ROOT,
        [
            "--mode", "completeness",
            "--packet", str(boundary_packet.relative_to(PROBE_ROOT)),
            "--output", str((mirror_audit / "packets/prompts/boundary-completeness.txt").relative_to(PROBE_ROOT)),
        ],
    )
    cli_cases["blindBoundaryWrappedKeys"] = run_cli(
        PROBE_ROOT,
        [
            "--mode", "blind",
            "--packet", str(benign_packet.relative_to(PROBE_ROOT)),
            "--completeness", str(boundary_review.relative_to(PROBE_ROOT)),
            "--output", str((mirror_audit / "packets/prompts/boundary-blind.txt").relative_to(PROBE_ROOT)),
        ],
    )

    exact_absent = mirror_audit / "packets/prompts/exact-absent.txt"
    cli_cases["completenessExactKeyAbsentOutput"] = run_cli(
        PROBE_ROOT,
        [
            "--mode", "completeness",
            "--packet", str(exact_packet.relative_to(PROBE_ROOT)),
            "--output", str(exact_absent.relative_to(PROBE_ROOT)),
        ],
    )
    cli_cases["completenessExactKeyAbsentOutput"]["outputAbsentAfter"] = not exact_absent.exists()

    sentinel_path = mirror_audit / "packets/prompts/exact-sentinel.txt"
    sentinel = b"SENTINEL-UNCHANGED\n"
    sentinel_path.write_bytes(sentinel)
    cli_cases["completenessExactKeySentinelOutput"] = run_cli(
        PROBE_ROOT,
        [
            "--mode", "completeness",
            "--packet", str(exact_packet.relative_to(PROBE_ROOT)),
            "--output", str(sentinel_path.relative_to(PROBE_ROOT)),
        ],
    )
    cli_cases["completenessExactKeySentinelOutput"]["sentinelUnchanged"] = sentinel_path.read_bytes() == sentinel

    value_sentinel_path = mirror_audit / "packets/prompts/value-sentinel.txt"
    value_sentinel_path.write_bytes(sentinel)
    cli_cases["completenessBoundaryValueSentinelOutput"] = run_cli(
        PROBE_ROOT,
        [
            "--mode", "completeness",
            "--packet", str(value_packet.relative_to(PROBE_ROOT)),
            "--output", str(value_sentinel_path.relative_to(PROBE_ROOT)),
        ],
    )
    cli_cases["completenessBoundaryValueSentinelOutput"]["sentinelUnchanged"] = value_sentinel_path.read_bytes() == sentinel

    blind_sentinel_path = mirror_audit / "packets/prompts/blind-exact-sentinel.txt"
    blind_sentinel_path.write_bytes(sentinel)
    cli_cases["blindExactCompletenessKeySentinelOutput"] = run_cli(
        PROBE_ROOT,
        [
            "--mode", "blind",
            "--packet", str(benign_packet.relative_to(PROBE_ROOT)),
            "--completeness", str(exact_review.relative_to(PROBE_ROOT)),
            "--output", str(blind_sentinel_path.relative_to(PROBE_ROOT)),
        ],
    )
    cli_cases["blindExactCompletenessKeySentinelOutput"]["sentinelUnchanged"] = blind_sentinel_path.read_bytes() == sentinel

    boundary_completeness_output = mirror_audit / "packets/prompts/boundary-completeness.txt"
    boundary_blind_output = mirror_audit / "packets/prompts/boundary-blind.txt"
    for case_name, output_path in (
        ("completenessBoundaryWrappedKeys", boundary_completeness_output),
        ("blindBoundaryWrappedKeys", boundary_blind_output),
    ):
        output_text = output_path.read_text(encoding="utf-8") if output_path.is_file() else ""
        cli_cases[case_name]["outputExists"] = output_path.is_file()
        cli_cases[case_name]["allBoundaryWrappedIdentifiersEmitted"] = all(
            f"before:{identifier}:after" in output_text for identifier in actual_ids
        )
        cli_cases[case_name]["emittedIdentifierCount"] = sum(
            f"before:{identifier}:after" in output_text for identifier in actual_ids
        )
        if output_path.is_file():
            cli_cases[case_name]["outputSha256"] = sha256_path(output_path)

    if PRIOR_PROBE_ROOT.exists():
        shutil.rmtree(PRIOR_PROBE_ROOT)
    (PRIOR_PROBE_ROOT / "scripts").mkdir(parents=True)
    prior_script = subprocess.run(
        [
            "git",
            "show",
            f"{PRIOR_HEAD}:scripts/build_correctness_audit_prompt.py",
        ],
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout
    (PRIOR_PROBE_ROOT / "scripts/build_correctness_audit_prompt.py").write_bytes(
        prior_script
    )
    prior_audit = PRIOR_PROBE_ROOT / AUDIT_REL
    (prior_audit / "prompts").mkdir(parents=True)
    (prior_audit / "packets").mkdir(parents=True)
    for name in SCHEMA_NAMES + ("manifest.json",):
        shutil.copy2(AUDIT / name, prior_audit / name)
    for name in (
        "packet-completeness-instructions.txt",
        "blind-derivation-instructions.txt",
    ):
        shutil.copy2(AUDIT / "prompts" / name, prior_audit / "prompts" / name)
    prior_benign_packet = prior_audit / "packets/benign-packet.json"
    prior_exact_packet = prior_audit / "packets/exact-key-packet.json"
    prior_exact_review = prior_audit / "packets/exact-key-review.json"
    write_json(prior_benign_packet, {"benign": "value"})
    write_json(prior_exact_packet, {"outer": [{"inner": {"rootCauseId": "benign"}}]})
    write_json(prior_exact_review, {"outer": [[{"inner": {"rootCauseId": "benign"}}]]})
    prior_cli_cases: dict[str, Any] = {}
    prior_completeness_output = prior_audit / "packets/prompts/prior-exact-completeness.txt"
    prior_blind_output = prior_audit / "packets/prompts/prior-exact-blind.txt"
    prior_cli_cases["completenessExactKey"] = run_cli(
        PRIOR_PROBE_ROOT,
        [
            "--mode", "completeness",
            "--packet", str(prior_exact_packet.relative_to(PRIOR_PROBE_ROOT)),
            "--output", str(prior_completeness_output.relative_to(PRIOR_PROBE_ROOT)),
        ],
    )
    prior_cli_cases["blindExactCompletenessKey"] = run_cli(
        PRIOR_PROBE_ROOT,
        [
            "--mode", "blind",
            "--packet", str(prior_benign_packet.relative_to(PRIOR_PROBE_ROOT)),
            "--completeness", str(prior_exact_review.relative_to(PRIOR_PROBE_ROOT)),
            "--output", str(prior_blind_output.relative_to(PRIOR_PROBE_ROOT)),
        ],
    )
    for case_name, output_path in (
        ("completenessExactKey", prior_completeness_output),
        ("blindExactCompletenessKey", prior_blind_output),
    ):
        output_text = output_path.read_text(encoding="utf-8") if output_path.is_file() else ""
        prior_cli_cases[case_name]["outputExists"] = output_path.is_file()
        prior_cli_cases[case_name]["exactIdentifierEmitted"] = "rootCauseId" in output_text
        if output_path.is_file():
            prior_cli_cases[case_name]["outputSha256"] = sha256_path(output_path)

    bypass_ids = [
        row["identifier"]
        for row in id_rows
        if not row["boundaryWrappedNestedKeyRejected"]
        and row["boundaryNestedValueRejected"]
    ]
    controls = {
        "inventoryExactlyMatchesIndependentDerivation": (
            actual_paths == expected_paths and actual_ids == expected_ids
        ),
        "allExactIdentifiersRejectedAsNestedKeys": all(
            row["exactNestedKeyRejected"] for row in id_rows
        ),
        "allIdentifiersRejectedAtValueTokenBoundaries": all(
            row["boundaryNestedValueRejected"] for row in id_rows
        ),
        "allBoundaryWrappedIdentifierKeysRejected": all(
            row["boundaryWrappedNestedKeyRejected"] for row in id_rows
        ),
        "allAlphanumericEmbeddedIdentifierValuesAccepted": all(
            row["alphanumericEmbeddedValueAccepted"] for row in id_rows
        ),
        "allPathsRejectedAsNestedKeys": all(
            row["exactNestedKeyRejected"] for row in path_rows
        ),
        "allPathsRejectedAtValueTokenBoundaries": all(
            row["boundaryNestedValueRejected"] for row in path_rows
        ),
        "allBoundaryWrappedPathKeysRejected": all(
            row["boundaryWrappedNestedKeyRejected"] for row in path_rows
        ),
        "bothSharedSchemaAllowlistsAccepted": all(
            row["exactNestedKeyAccepted"] and row["boundaryNestedValueAccepted"]
            for row in shared_rows
        ),
        "completenessCliEmittedAllBoundaryWrappedIdentifiers": (
            cli_cases["completenessBoundaryWrappedKeys"]["returnCode"] == 0
            and cli_cases["completenessBoundaryWrappedKeys"]["allBoundaryWrappedIdentifiersEmitted"]
        ),
        "blindCliEmittedAllBoundaryWrappedIdentifiers": (
            cli_cases["blindBoundaryWrappedKeys"]["returnCode"] == 0
            and cli_cases["blindBoundaryWrappedKeys"]["allBoundaryWrappedIdentifiersEmitted"]
        ),
        "exactKeyCliControlsRejectedBeforeWrite": (
            cli_cases["completenessExactKeyAbsentOutput"]["returnCode"] != 0
            and cli_cases["completenessExactKeyAbsentOutput"]["outputAbsentAfter"]
            and cli_cases["completenessExactKeySentinelOutput"]["returnCode"] != 0
            and cli_cases["completenessExactKeySentinelOutput"]["sentinelUnchanged"]
            and cli_cases["blindExactCompletenessKeySentinelOutput"]["returnCode"] != 0
            and cli_cases["blindExactCompletenessKeySentinelOutput"]["sentinelUnchanged"]
        ),
        "boundaryValueCliControlRejectedBeforeWrite": (
            cli_cases["completenessBoundaryValueSentinelOutput"]["returnCode"] != 0
            and cli_cases["completenessBoundaryValueSentinelOutput"]["sentinelUnchanged"]
        ),
        "priorCandidateReproducesS7C4001BothModes": all(
            case["returnCode"] == 0
            and case["outputExists"]
            and case["exactIdentifierEmitted"]
            for case in prior_cli_cases.values()
        ),
    }

    result = {
        "candidateHead": head,
        "candidatePromptScript": str(PROMPT_SCRIPT),
        "candidatePromptScriptSha256": sha256_path(PROMPT_SCRIPT),
        "probeScript": str(Path(__file__).resolve()),
        "inventory": inventory,
        "controls": controls,
        "boundaryWrappedIdentifierKeyBypasses": bypass_ids,
        "boundaryWrappedIdentifierKeyBypassCount": len(bypass_ids),
        "identifierMatrix": id_rows,
        "pathMatrix": path_rows,
        "sharedSchemaAllowlistMatrix": shared_rows,
        "cliCases": cli_cases,
        "priorCandidate": {
            "head": PRIOR_HEAD,
            "promptScriptSha256": hashlib.sha256(prior_script).hexdigest(),
            "cliCases": prior_cli_cases,
            "probeRoot": str(PRIOR_PROBE_ROOT),
        },
        "probeRoot": str(PROBE_ROOT),
    }
    write_json(RESULT, result)
    print(json.dumps({
        "result": str(RESULT),
        "pathCount": len(actual_paths),
        "identifierCount": len(actual_ids),
        "inventoryMatch": controls["inventoryExactlyMatchesIndependentDerivation"],
        "boundaryWrappedIdentifierKeyBypassCount": len(bypass_ids),
        "completenessCliBypass": controls["completenessCliEmittedAllBoundaryWrappedIdentifiers"],
        "blindCliBypass": controls["blindCliEmittedAllBoundaryWrappedIdentifiers"],
        "exactKeyControls": controls["exactKeyCliControlsRejectedBeforeWrite"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
