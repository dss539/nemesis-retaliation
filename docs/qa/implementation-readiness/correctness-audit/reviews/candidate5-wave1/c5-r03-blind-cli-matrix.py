#!/usr/bin/env python3
"""Candidate-5 blind canonical CLI boundary matrix (external probe)."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

REPO = Path("/home/smithers/projects/nemesis-c5-r03/repos/nemesis-retaliation")
AUDIT_DIR = REPO / "docs/qa/implementation-readiness/correctness-audit"
SCRIPT = REPO / "scripts/build_correctness_audit_prompt.py"
CANDIDATE_HEAD = "d78e91e9f0d29eab7e9d838d4fc043ba73518cec"
SENTINEL = b"c5-r03-sentinel\x00\xff\nDO-NOT-CHANGE\n"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_prompt_module():
    spec = importlib.util.spec_from_file_location("candidate5_prompt", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load prompt module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def schema_properties(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            found.update(str(key) for key in properties)
        for child in value.values():
            found.update(schema_properties(child))
    elif isinstance(value, list):
        for child in value:
            found.update(schema_properties(child))
    return found


def token_payload(token: str, representation: str, depth: str) -> dict[str, Any]:
    leaf: dict[str, Any]
    if representation == "key":
        leaf = {token: "safe"}
    else:
        leaf = {"value": f"fixture {token} fixture"}
    if depth == "flat":
        return leaf
    return {"outer": [{"inner": leaf}]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.time()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    module = load_prompt_module()
    forbidden_paths, forbidden_ids = module.source_only_forbidden_inventory()

    manifest = json.loads((AUDIT_DIR / "manifest.json").read_text(encoding="utf-8"))
    expected_paths = set(module.SOURCE_ONLY_FIXED_PATH_TOKENS)
    for section in ("frozenSemanticHashes", "frozenConciseRuleHashes", "selectionInputHashes"):
        mapping = manifest.get(section, {})
        if isinstance(mapping, dict):
            expected_paths.update(
                str(path)
                for path in mapping
                if not str(path).startswith(module.ALLOWED_SOURCE_PATH_PREFIXES)
            )
    for unit in manifest.get("units", []):
        if not isinstance(unit, dict):
            continue
        for field in ("downstreamPath", "extractionPath"):
            path = unit.get(field)
            if isinstance(path, str) and not path.startswith(module.ALLOWED_SOURCE_PATH_PREFIXES):
                expected_paths.add(path)

    downstream_properties = set(module.SOURCE_ONLY_FIXED_IDENTIFIERS)
    source_properties: set[str] = set()
    for name in ("comparison.schema.json", "audit-result.schema.json"):
        downstream_properties.update(
            schema_properties(json.loads((AUDIT_DIR / name).read_text(encoding="utf-8")))
        )
    for name in ("source-packet.schema.json", "packet-completeness-review.schema.json"):
        source_properties.update(
            schema_properties(json.loads((AUDIT_DIR / name).read_text(encoding="utf-8")))
        )
    expected_ids = (
        downstream_properties
        - set(module.SOURCE_ONLY_SHARED_IDENTIFIERS)
        - source_properties
    )
    allowed_shared = downstream_properties & (
        set(module.SOURCE_ONLY_SHARED_IDENTIFIERS) | source_properties
    )

    packets_root = AUDIT_DIR / "packets"
    prompts_root = packets_root / "prompts"
    packets_existed = packets_root.exists()
    prompts_existed = prompts_root.exists()
    input_root = packets_root / f".c5-r03-cli-input-{os.getpid()}"
    output_root = prompts_root / f".c5-r03-cli-output-{os.getpid()}"
    packet_path = input_root / "packet.json"
    review_path = input_root / "completeness.json"
    output_path = output_root / "prompt.txt"
    output_rel = output_path.relative_to(REPO).as_posix()
    rows: list[dict[str, Any]] = []

    def write_payloads(packet: dict[str, Any], review: dict[str, Any]) -> None:
        input_root.mkdir(parents=True, exist_ok=True)
        packet_path.write_text(json.dumps(packet, ensure_ascii=False) + "\n", encoding="utf-8")
        review_path.write_text(json.dumps(review, ensure_ascii=False) + "\n", encoding="utf-8")

    def invoke(
        packet: dict[str, Any],
        review: dict[str, Any],
        initial: str,
        expectation: str,
        metadata: dict[str, Any],
        custom_output: Path | None = None,
    ) -> dict[str, Any]:
        write_payloads(packet, review)
        target = custom_output or output_path
        target_rel = target.relative_to(REPO).as_posix()
        if target.exists():
            target.unlink()
        if initial == "sentinel":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(SENTINEL)
        before_exists = target.exists()
        before = target.read_bytes() if before_exists else None
        command = [
            sys.executable,
            str(SCRIPT),
            "--mode",
            "blind",
            "--packet",
            str(packet_path),
            "--completeness",
            str(review_path),
            "--output",
            target_rel,
        ]
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            command,
            cwd=REPO,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        after_exists = target.exists()
        after = target.read_bytes() if after_exists else None
        preserved = before_exists == after_exists and before == after
        if expectation == "reject":
            passed = completed.returncode != 0 and preserved
        elif expectation == "allow":
            passed = completed.returncode == 0 and after_exists and after != SENTINEL
        elif expectation == "leak-should-reject":
            passed = completed.returncode != 0 and preserved
        else:
            raise ValueError(expectation)
        row = {
            **metadata,
            "initialOutput": initial,
            "expectation": expectation,
            "exit": completed.returncode,
            "stdout": completed.stdout.decode("utf-8", errors="replace")[-500:],
            "stderr": completed.stderr.decode("utf-8", errors="replace")[-1000:],
            "beforeExists": before_exists,
            "afterExists": after_exists,
            "beforeSha256": digest(before) if before is not None else None,
            "afterSha256": digest(after) if after is not None else None,
            "bytesPreserved": preserved,
            "passed": passed,
            "command": command,
        }
        rows.append(row)
        return row

    cleanup_error: str | None = None
    try:
        # Ordering control: a rejected payload must not even create the output parent.
        no_mkdir_output = prompts_root / f".c5-r03-no-mkdir-{os.getpid()}" / "deep" / "prompt.txt"
        no_mkdir_parent = no_mkdir_output.parent
        row = invoke(
            {"outer": [{"value": "docs/rules/semantics/pilots.json"}]},
            {"safe": "safe"},
            "absent",
            "reject",
            {"category": "write-order", "control": "absent-parent"},
            custom_output=no_mkdir_output,
        )
        row["parentAbsentAfter"] = not no_mkdir_parent.exists()
        row["passed"] = row["passed"] and row["parentAbsentAfter"]
        print("write-order control complete", flush=True)

        # Exhaust every forbidden inventory member through both blind payloads,
        # as a key and value, flat and nested, with absent and sentinel outputs.
        for token_type, tokens in (
            ("path", sorted(forbidden_paths)),
            ("identifier", sorted(forbidden_ids)),
        ):
            for location in ("packet", "completeness"):
                for token in tokens:
                    for representation in ("key", "value"):
                        for depth in ("flat", "nested"):
                            payload = token_payload(token, representation, depth)
                            packet = payload if location == "packet" else {"safe": "safe"}
                            review = payload if location == "completeness" else {"safe": "safe"}
                            for initial in ("absent", "sentinel"):
                                invoke(
                                    packet,
                                    review,
                                    initial,
                                    "reject",
                                    {
                                        "category": "exact-forbidden-matrix",
                                        "tokenType": token_type,
                                        "token": token,
                                        "location": location,
                                        "representation": representation,
                                        "depth": depth,
                                    },
                                )
            print(f"exact matrix complete for {token_type}", flush=True)

        # Every justified shared identifier must remain usable in either payload,
        # as a key/value and through nested traversal.
        for location in ("packet", "completeness"):
            for identifier in sorted(allowed_shared):
                for representation in ("key", "value"):
                    for depth in ("flat", "nested"):
                        payload = token_payload(identifier, representation, depth)
                        packet = payload if location == "packet" else {"safe": "safe"}
                        review = payload if location == "completeness" else {"safe": "safe"}
                        invoke(
                            packet,
                            review,
                            "absent",
                            "allow",
                            {
                                "category": "shared-allowed",
                                "identifier": identifier,
                                "location": location,
                                "representation": representation,
                                "depth": depth,
                            },
                        )
        print("shared allowed matrix complete", flush=True)

        # An allowed shared key must not suppress recursive forbidden checks.
        representative_id = "rootCauseId"
        representative_path = "docs/rules/semantics/pilots.json"
        for location in ("packet", "completeness"):
            for shared in sorted(allowed_shared):
                contaminations = {
                    "identifier-key": {shared: {representative_id: "RC-1"}},
                    "identifier-value": {shared: {"value": f"fixture {representative_id} fixture"}},
                    "path-key": {shared: {representative_path: "leak"}},
                    "path-value": {shared: {"value": f"fixture {representative_path} fixture"}},
                }
                for contamination, payload in contaminations.items():
                    packet = payload if location == "packet" else {"safe": "safe"}
                    review = payload if location == "completeness" else {"safe": "safe"}
                    invoke(
                        packet,
                        review,
                        "sentinel",
                        "reject",
                        {
                            "category": "shared-recursion-contamination",
                            "sharedIdentifier": shared,
                            "contamination": contamination,
                            "location": location,
                        },
                    )
        print("shared recursion contamination matrix complete", flush=True)

        # Adversarial post-reveal variants: visible exact identifiers delimited
        # inside member names, and dot-relative spellings of forbidden paths.
        for location in ("packet", "completeness"):
            for identifier in sorted(forbidden_ids):
                payload = {"outer": [{"path": {f"leak:{identifier}:field": "post-reveal"}}]}
                packet = payload if location == "packet" else {"safe": "safe"}
                review = payload if location == "completeness" else {"safe": "safe"}
                for initial in ("absent", "sentinel"):
                    invoke(
                        packet,
                        review,
                        initial,
                        "leak-should-reject",
                        {
                            "category": "adversarial-identifier-key-wrapper",
                            "identifier": identifier,
                            "location": location,
                            "depth": "nested-under-shared-path",
                            "renderedKey": f"leak:{identifier}:field",
                        },
                    )
            for path_token in sorted(forbidden_paths):
                payload = {"outer": [{"path": {"value": f"inspect ./{path_token}"}}]}
                packet = payload if location == "packet" else {"safe": "safe"}
                review = payload if location == "completeness" else {"safe": "safe"}
                for initial in ("absent", "sentinel"):
                    invoke(
                        packet,
                        review,
                        initial,
                        "leak-should-reject",
                        {
                            "category": "adversarial-dot-relative-path-value",
                            "path": path_token,
                            "location": location,
                            "depth": "nested-under-shared-path",
                            "renderedValue": f"inspect ./{path_token}",
                        },
                    )
        print("adversarial leakage matrix complete", flush=True)
    finally:
        for candidate in (input_root, output_root, prompts_root / f".c5-r03-no-mkdir-{os.getpid()}"):
            if candidate.exists():
                shutil.rmtree(candidate)
        try:
            if not prompts_existed and prompts_root.exists():
                prompts_root.rmdir()
            if not packets_existed and packets_root.exists():
                packets_root.rmdir()
        except OSError as exc:
            cleanup_error = str(exc)

    by_category: dict[str, dict[str, Any]] = {}
    for row in rows:
        bucket = by_category.setdefault(
            row["category"],
            {"count": 0, "passed": 0, "failed": 0, "exitCounts": {}},
        )
        bucket["count"] += 1
        bucket["passed" if row["passed"] else "failed"] += 1
        exit_key = str(row["exit"])
        bucket["exitCounts"][exit_key] = bucket["exitCounts"].get(exit_key, 0) + 1

    exact_rows = [row for row in rows if row["category"] == "exact-forbidden-matrix"]
    shared_rows = [row for row in rows if row["category"] == "shared-allowed"]
    contamination_rows = [
        row for row in rows if row["category"] == "shared-recursion-contamination"
    ]
    adversarial_rows = [row for row in rows if row["category"].startswith("adversarial-")]
    unexpected_exact = [row for row in exact_rows if not row["passed"]]
    unexpected_shared = [row for row in shared_rows if not row["passed"]]
    unexpected_contamination = [row for row in contamination_rows if not row["passed"]]
    admitted_leaks = [row for row in adversarial_rows if row["exit"] == 0]

    evidence = {
        "schemaVersion": 1,
        "recordType": "candidate5-blind-cli-boundary-matrix-evidence",
        "candidateHead": CANDIDATE_HEAD,
        "specialty": "blind-cli-boundary",
        "repo": str(REPO),
        "commandTemplate": [
            "python3",
            "scripts/build_correctness_audit_prompt.py",
            "--mode",
            "blind",
            "--packet",
            "<packet-under-audit-packets>",
            "--completeness",
            "<review-under-audit-packets>",
            "--output",
            "<canonical-path-under-audit-packets-prompts>",
        ],
        "inventory": {
            "forbiddenPathCount": len(forbidden_paths),
            "forbiddenIdentifierCount": len(forbidden_ids),
            "allowedSharedIdentifierCount": len(allowed_shared),
            "forbiddenPaths": sorted(forbidden_paths),
            "forbiddenIdentifiers": sorted(forbidden_ids),
            "allowedSharedIdentifiers": sorted(allowed_shared),
            "expectedPathsExact": forbidden_paths == expected_paths,
            "expectedIdentifiersExact": forbidden_ids == expected_ids,
        },
        "summary": {
            "rowCount": len(rows),
            "byCategory": by_category,
            "exactForbiddenFailures": len(unexpected_exact),
            "sharedAllowedFailures": len(unexpected_shared),
            "sharedRecursionFailures": len(unexpected_contamination),
            "adversarialLeakAdmissions": len(admitted_leaks),
            "sentinelSha256": digest(SENTINEL),
            "sentinelPreservedRejectedCount": sum(
                1
                for row in rows
                if row["initialOutput"] == "sentinel"
                and row["exit"] != 0
                and row["bytesPreserved"]
            ),
            "absentPreservedRejectedCount": sum(
                1
                for row in rows
                if row["initialOutput"] == "absent"
                and row["exit"] != 0
                and not row["afterExists"]
            ),
            "cleanupError": cleanup_error,
            "durationSeconds": round(time.time() - started, 3),
        },
        "unexpectedExactRows": unexpected_exact,
        "unexpectedSharedRows": unexpected_shared,
        "unexpectedContaminationRows": unexpected_contamination,
        "admittedLeakRows": admitted_leaks,
        "rows": rows,
    }
    args.output.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(evidence["summary"], indent=2, sort_keys=True), flush=True)
    return 0 if not (unexpected_exact or unexpected_shared or unexpected_contamination or cleanup_error) else 2


if __name__ == "__main__":
    raise SystemExit(main())
