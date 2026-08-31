#!/usr/bin/env python3
"""Candidate-5 completeness CLI prewrite matrix (review evidence only)."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

WORKSPACE = Path("/home/smithers/projects/nemesis-c5-r02")
OUT = WORKSPACE / "review-output/c5-r02"
ROOT = OUT / "candidate-snapshot"
SCRIPT = ROOT / "scripts/build_correctness_audit_prompt.py"
AUDIT = ROOT / "docs/qa/implementation-readiness/correctness-audit"
PACKETS = AUDIT / "packets"
PROMPTS = PACKETS / "prompts"
PACKET = PACKETS / "c5-r02-matrix-packet.json"
OUTPUT = PROMPTS / "c5-r02-matrix-output.txt"
OUTPUT_REL = OUTPUT.relative_to(ROOT).as_posix()
DETAILS = OUT / "completeness-cli-matrix-details.jsonl"
RESULTS = OUT / "completeness-cli-matrix-results.json"
CANDIDATE_HEAD = "d78e91e9f0d29eab7e9d838d4fc043ba73518cec"
SENTINEL = b"c5-r02 sentinel: must remain byte-identical\n\x00\xff"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_property_names(value: Any) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(str(key) for key in properties)
        for child in value.values():
            names.update(schema_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(schema_property_names(child))
    return names


def load_candidate_module():
    spec = importlib.util.spec_from_file_location("candidate_prompt_builder", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate prompt builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_packet() -> dict[str, Any]:
    source_path = "docs/rulebooks/c5-r02-probe.pdf"
    source_sha = "a" * 64
    unit_id = "C5-R02-PROBE"
    return {
        "schemaVersion": 1,
        "recordType": "stage-1-source-only-audit-packet",
        "packetId": "c5-r02-probe",
        "sealedAtUtc": "2026-08-31T00:00:00Z",
        "sealedAtGitHead": CANDIDATE_HEAD,
        "auditUnitIds": [unit_id],
        "scope": "base-competitive-stage1",
        "authorityOrder": ["official-rulebook"],
        "sourceDocuments": [
            {
                "sourcePath": source_path,
                "sourceSha256": source_sha,
                "authority": "official-rulebook",
                "version": "probe",
                "role": "primary-rule-text",
            }
        ],
        "evidence": [
            {
                "evidenceId": "E-C5-R02",
                "auditUnitIds": [unit_id],
                "sourcePath": source_path,
                "sourceSha256": source_sha,
                "locator": "probe locator",
                "evidenceKind": "official-text",
                "exactText": "benign probe text",
                "visualEvidencePath": None,
                "visualEvidenceSha256": None,
                "pdfPageIndex": None,
                "renderDpi": None,
            }
        ],
        "searchCoverage": {
            "searchedSourcePaths": [
                {"sourcePath": source_path, "sourceSha256": source_sha}
            ],
            "searchTerms": ["benign probe term"],
            "neighboringSectionsChecked": ["benign neighboring section"],
            "faqUnitIdsChecked": [],
            "componentChannelsChecked": ["official text"],
            "exclusions": [{"scope": "expansions", "reason": "out of scope"}],
        },
        "sourceOnlyAttestation": True,
        "forbiddenDownstreamSourcesIncluded": [],
    }


def payload_for(token: str, placement: str) -> dict[str, Any]:
    payload = base_packet()
    if placement == "key-root":
        payload[token] = "benign"
    elif placement == "key-nested":
        payload["searchCoverage"]["exclusions"][0][token] = "benign"
    elif placement == "value-root":
        payload["packetId"] = token
    elif placement == "value-nested":
        payload["searchCoverage"]["searchTerms"] = [f"prefix [{token}] suffix"]
    else:
        raise ValueError(placement)
    return payload


def schema_errors(validator: Draft202012Validator, payload: dict[str, Any]) -> list[str]:
    return sorted(error.message for error in validator.iter_errors(payload))


def stat_record(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = path.stat()
    return {
        "inode": value.st_ino,
        "mode": value.st_mode,
        "mtimeNs": value.st_mtime_ns,
        "size": value.st_size,
        "sha256": sha256_path(path),
    }


def run_cli(payload: dict[str, Any], output_state: str) -> dict[str, Any]:
    PACKETS.mkdir(parents=True, exist_ok=True)
    PACKET.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if OUTPUT.exists():
        OUTPUT.unlink()
    if output_state == "sentinel":
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(SENTINEL)
    elif output_state != "absent":
        raise ValueError(output_state)
    before = stat_record(OUTPUT)
    command = [
        sys.executable,
        str(SCRIPT),
        "--mode",
        "completeness",
        "--packet",
        str(PACKET),
        "--output",
        OUTPUT_REL,
    ]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
        check=False,
    )
    after = stat_record(OUTPUT)
    output_bytes = OUTPUT.read_bytes() if OUTPUT.is_file() else None
    stderr = completed.stderr.decode("utf-8", errors="replace")
    stdout = completed.stdout.decode("utf-8", errors="replace")
    return {
        "command": command,
        "exitCode": completed.returncode,
        "stdout": stdout,
        "stderrTail": "\n".join(stderr.splitlines()[-8:]),
        "before": before,
        "after": after,
        "outputContainsPacketBytes": output_bytes is not None
        and PACKET.read_bytes().rstrip(b"\n") in output_bytes,
        "outputSha256": None if output_bytes is None else sha256_bytes(output_bytes),
    }


def detail_write(handle, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    handle.flush()


def main() -> int:
    module = load_candidate_module()
    actual_paths, actual_ids = module.source_only_forbidden_inventory()
    actual_paths = set(actual_paths)
    actual_ids = set(actual_ids)

    manifest = load_json(AUDIT / "manifest.json")
    expected_paths = set(module.SOURCE_ONLY_FIXED_PATH_TOKENS)
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
                if not str(path).startswith(tuple(module.ALLOWED_SOURCE_PATH_PREFIXES))
            )
    for unit in manifest.get("units", []):
        if not isinstance(unit, dict):
            continue
        for field in ("downstreamPath", "extractionPath"):
            path = unit.get(field)
            if isinstance(path, str) and not path.startswith(
                tuple(module.ALLOWED_SOURCE_PATH_PREFIXES)
            ):
                expected_paths.add(path)

    comparison_schema = load_json(AUDIT / "comparison.schema.json")
    result_schema = load_json(AUDIT / "audit-result.schema.json")
    source_schema = load_json(AUDIT / "source-packet.schema.json")
    completeness_schema = load_json(AUDIT / "packet-completeness-review.schema.json")
    comparison_properties = schema_property_names(comparison_schema)
    result_properties = schema_property_names(result_schema)
    source_properties = schema_property_names(source_schema)
    completeness_properties = schema_property_names(completeness_schema)
    post_reveal_before_payload_allowlists = (
        set(module.SOURCE_ONLY_FIXED_IDENTIFIERS)
        | comparison_properties
        | result_properties
    ) - set(module.SOURCE_ONLY_SHARED_IDENTIFIERS)
    expected_ids = (
        post_reveal_before_payload_allowlists
        - source_properties
        - completeness_properties
    )
    removed_by_source_schema = sorted(
        post_reveal_before_payload_allowlists & source_properties
    )
    removed_by_completeness_schema = sorted(
        (post_reveal_before_payload_allowlists - source_properties)
        & completeness_properties
    )
    all_removed_post_reveal = sorted(
        post_reveal_before_payload_allowlists - actual_ids
    )

    source_validator = Draft202012Validator(source_schema)
    benign = base_packet()
    benign_schema_errors = schema_errors(source_validator, benign)
    if benign_schema_errors:
        raise RuntimeError(f"base packet is not schema-valid: {benign_schema_errors}")

    DETAILS.parent.mkdir(parents=True, exist_ok=True)
    if DETAILS.exists():
        DETAILS.unlink()
    rejection_total = 0
    rejection_failures: list[dict[str, Any]] = []
    rejection_exit_codes: Counter[int] = Counter()
    rejection_counts: defaultdict[str, int] = defaultdict(int)
    rejection_schema_valid_counts: Counter[bool] = Counter()
    placements = ("key-root", "key-nested", "value-root", "value-nested")
    output_states = ("absent", "sentinel")

    with DETAILS.open("w", encoding="utf-8") as details:
        for token_kind, tokens in (
            ("path", sorted(actual_paths)),
            ("identifier", sorted(actual_ids)),
        ):
            for token in tokens:
                for placement in placements:
                    payload = payload_for(token, placement)
                    validation_errors = schema_errors(source_validator, payload)
                    for output_state in output_states:
                        result = run_cli(payload, output_state)
                        rejection_total += 1
                        rejection_exit_codes[result["exitCode"]] += 1
                        rejection_schema_valid_counts[not validation_errors] += 1
                        before = result["before"]
                        after = result["after"]
                        preserved = (
                            after is None
                            if output_state == "absent"
                            else before == after
                        )
                        diagnostic = result["stderrTail"]
                        rejected = result["exitCode"] != 0
                        diagnosed = token in diagnostic and f"forbidden {token_kind}" in diagnostic
                        passed = rejected and preserved and diagnosed
                        rejection_counts[
                            f"{token_kind}/{placement}/{output_state}"
                        ] += int(passed)
                        record = {
                            "matrix": "derived-forbidden-rejection",
                            "tokenKind": token_kind,
                            "token": token,
                            "placement": placement,
                            "outputState": output_state,
                            "sourcePacketSchemaValid": not validation_errors,
                            "sourcePacketSchemaErrors": validation_errors,
                            "rejected": rejected,
                            "diagnosedExactTokenAndKind": diagnosed,
                            "outputPreserved": preserved,
                            "passed": passed,
                            **result,
                        }
                        detail_write(details, record)
                        if not passed:
                            rejection_failures.append(record)

        bypass_total = 0
        bypass_records: list[dict[str, Any]] = []
        for token in all_removed_post_reveal:
            for placement in placements:
                payload = payload_for(token, placement)
                validation_errors = schema_errors(source_validator, payload)
                for output_state in output_states:
                    result = run_cli(payload, output_state)
                    bypass_total += 1
                    before = result["before"]
                    after = result["after"]
                    wrote = (
                        after is not None
                        if output_state == "absent"
                        else before != after
                    )
                    accepted_and_wrote = (
                        result["exitCode"] == 0
                        and wrote
                        and result["outputContainsPacketBytes"]
                    )
                    record = {
                        "matrix": "allowlist-bypass",
                        "tokenKind": "post-reveal-identifier-removed-by-allowlist",
                        "token": token,
                        "placement": placement,
                        "outputState": output_state,
                        "sourcePacketSchemaValid": not validation_errors,
                        "sourcePacketSchemaErrors": validation_errors,
                        "cliAccepted": result["exitCode"] == 0,
                        "outputCreatedOrChanged": wrote,
                        "acceptedAndWrote": accepted_and_wrote,
                        **result,
                    }
                    detail_write(details, record)
                    bypass_records.append(record)

        benign_result = run_cli(benign, "absent")
        benign_record = {
            "matrix": "benign-positive-control",
            "sourcePacketSchemaValid": True,
            "cliAccepted": benign_result["exitCode"] == 0,
            "outputCreated": benign_result["after"] is not None,
            "outputContainsPacketBytes": benign_result["outputContainsPacketBytes"],
            **benign_result,
        }
        detail_write(details, benign_record)

    bypass_summary: list[dict[str, Any]] = []
    for token in all_removed_post_reveal:
        rows = [row for row in bypass_records if row["token"] == token]
        bypass_summary.append(
            {
                "token": token,
                "removedBySourceSchemaAllowlist": token in removed_by_source_schema,
                "removedByCompletenessSchemaAllowlist": token
                in removed_by_completeness_schema,
                "caseCount": len(rows),
                "acceptedAndWroteCount": sum(
                    1 for row in rows if row["acceptedAndWrote"]
                ),
                "schemaValidStringValueCaseCount": sum(
                    1
                    for row in rows
                    if row["placement"].startswith("value-")
                    and row["sourcePacketSchemaValid"]
                ),
                "invalidExtraKeyCaseCount": sum(
                    1
                    for row in rows
                    if row["placement"].startswith("key-")
                    and not row["sourcePacketSchemaValid"]
                ),
                "exitCodes": dict(
                    sorted(Counter(row["exitCode"] for row in rows).items())
                ),
            }
        )

    summary = {
        "schemaVersion": 1,
        "recordType": "candidate-5-completeness-cli-matrix",
        "candidateHead": CANDIDATE_HEAD,
        "candidateScript": str(SCRIPT),
        "candidateScriptSha256": sha256_path(SCRIPT),
        "pythonExecutable": sys.executable,
        "realCliCommandTemplate": [
            sys.executable,
            str(SCRIPT),
            "--mode",
            "completeness",
            "--packet",
            str(PACKET),
            "--output",
            OUTPUT_REL,
        ],
        "inventory": {
            "actualForbiddenPathCount": len(actual_paths),
            "actualForbiddenIdentifierCount": len(actual_ids),
            "expectedForbiddenPathCount": len(expected_paths),
            "expectedForbiddenIdentifierCount": len(expected_ids),
            "pathsExactlyDerived": actual_paths == expected_paths,
            "identifiersExactlyDerivedByCandidateFormula": actual_ids == expected_ids,
            "missingPaths": sorted(expected_paths - actual_paths),
            "extraPaths": sorted(actual_paths - expected_paths),
            "missingIdentifiers": sorted(expected_ids - actual_ids),
            "extraIdentifiers": sorted(actual_ids - expected_ids),
            "forbiddenPaths": sorted(actual_paths),
            "forbiddenIdentifiers": sorted(actual_ids),
            "postRevealBeforePayloadSchemaAllowlists": sorted(
                post_reveal_before_payload_allowlists
            ),
            "postRevealRemovedBySourceSchema": removed_by_source_schema,
            "postRevealRemovedByCompletenessSchema": removed_by_completeness_schema,
            "allPostRevealRemovedFromForbiddenInventory": all_removed_post_reveal,
        },
        "derivedForbiddenRealCliMatrix": {
            "placements": list(placements),
            "outputStates": list(output_states),
            "caseCount": rejection_total,
            "passedCount": rejection_total - len(rejection_failures),
            "failedCount": len(rejection_failures),
            "exitCodes": dict(sorted(rejection_exit_codes.items())),
            "schemaValidCaseCounts": {
                str(key).lower(): value
                for key, value in sorted(rejection_schema_valid_counts.items())
            },
            "passedCountsByCell": dict(sorted(rejection_counts.items())),
            "failures": rejection_failures,
            "absentOutputPreservationVerified": all(
                row["outputPreserved"]
                for row in rejection_failures
                if row["outputState"] == "absent"
            )
            if rejection_failures
            else True,
            "sentinelOutputPreservationVerified": all(
                row["outputPreserved"]
                for row in rejection_failures
                if row["outputState"] == "sentinel"
            )
            if rejection_failures
            else True,
        },
        "allowlistBypassRealCliMatrix": {
            "caseCount": bypass_total,
            "acceptedAndWroteCount": sum(
                1 for row in bypass_records if row["acceptedAndWrote"]
            ),
            "tokens": bypass_summary,
        },
        "benignPositiveControl": benign_record,
        "detailsPath": str(DETAILS),
    }
    RESULTS.write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # Remove ephemeral packet/prompt after all evidence has been serialized.
    if PACKET.exists():
        PACKET.unlink()
    if OUTPUT.exists():
        OUTPUT.unlink()
    print(json.dumps({
        "results": str(RESULTS),
        "details": str(DETAILS),
        "derivedCases": rejection_total,
        "derivedFailures": len(rejection_failures),
        "bypassCases": bypass_total,
        "bypassAcceptedAndWrote": sum(
            1 for row in bypass_records if row["acceptedAndWrote"]
        ),
        "removedPostRevealIdentifiers": all_removed_post_reveal,
        "benignExit": benign_result["exitCode"],
    }, sort_keys=True))
    return 0 if not rejection_failures and benign_result["exitCode"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
