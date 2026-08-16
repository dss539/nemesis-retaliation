#!/usr/bin/env python3
"""Read-only deterministic validator for sol-max-worker-06."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
from typing import Any

from PIL import Image

REPO = Path("/home/smithers/nemesis-retaliation").resolve()
WORKER = (REPO / "assets/tts-mod/extract/vision-workers/sol-max-worker-06").resolve()
ASSIGNMENT = WORKER / "assignment.json"
SESSION_ID = "20260815_224527_5f5db3"
EXPECTED_IDS = ["W06-001", "W06-002", "W06-003", "W06-004"]
REQUIRED_RESULT_FIELDS = [
    "assetId",
    "sourcePath",
    "sourceSha256",
    "sourceMetadata",
    "runtimeProvenance",
    "orientation",
    "blindPixelObservations",
    "visibleText",
    "iconMorphology",
    "evidenceConsulted",
    "proposedClassification",
    "readConfidence",
    "classificationConfidence",
    "uncertainties",
    "promotionDecision",
    "decisionReasons",
    "validationPerformed",
    "rawResultPath",
]


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_tuple_digest(assets: list[dict[str, Any]]) -> str:
    tuples = [(a["assetId"], a["sourcePath"], a["sourceSha256"]) for a in assets]
    return sha_bytes(json.dumps(tuples, separators=(",", ":")).encode())


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_tool_calls(raw: str | None) -> list[dict[str, Any]]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except Exception:
        return []
    return parsed if isinstance(parsed, list) else [parsed]


def tool_name_args(call: dict[str, Any]) -> tuple[str | None, dict[str, Any]]:
    fn = call.get("function", {}) if isinstance(call, dict) else {}
    name = fn.get("name") or call.get("name")
    args: Any = fn.get("arguments", call.get("arguments", {}))
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {}
    return name, args if isinstance(args, dict) else {}


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    assignment_bytes = ASSIGNMENT.read_bytes()
    assignment = json.loads(assignment_bytes)
    assets = assignment["assets"]
    assigned_ids = [a["assetId"] for a in assets]
    assignment_sha = sha_bytes(assignment_bytes)
    tuple_digest = canonical_tuple_digest(assets)
    checks["assignment"] = {
        "path": str(ASSIGNMENT.relative_to(REPO)),
        "sha256": assignment_sha,
        "orderedTupleDigest": tuple_digest,
        "assignedIds": assigned_ids,
        "assignedCount": len(assets),
    }
    if assigned_ids != EXPECTED_IDS:
        errors.append(f"assignment IDs/order differ: {assigned_ids!r}")
    if len(assets) != 4:
        errors.append(f"assignment count is {len(assets)}, expected 4")

    baseline = load_json(WORKER / "batches/baseline.json")
    checks["assignment"]["baselineSha256"] = baseline["assignmentSha256"]
    checks["assignment"]["baselineOrderedTupleDigest"] = baseline["orderedTupleDigest"]
    checks["assignment"]["drift"] = {
        "fileHashChanged": assignment_sha != baseline["assignmentSha256"],
        "orderedTuplesChanged": tuple_digest != baseline["orderedTupleDigest"],
    }
    if tuple_digest != baseline["orderedTupleDigest"]:
        errors.append("ordered assignment tuple digest changed")

    raw_paths = sorted((WORKER / "raw").glob("W06-*.json"))
    result_paths = sorted((WORKER / "results").glob("W06-*.json"))
    raw_ids = [p.stem for p in raw_paths]
    result_ids = [p.stem for p in result_paths]
    checks["artifactSets"] = {
        "rawIds": raw_ids,
        "resultIds": result_ids,
        "rawCount": len(raw_paths),
        "resultCount": len(result_paths),
        "duplicateRawIds": sorted({x for x in raw_ids if raw_ids.count(x) > 1}),
        "duplicateResultIds": sorted({x for x in result_ids if result_ids.count(x) > 1}),
    }
    if raw_ids != EXPECTED_IDS:
        errors.append(f"raw artifact IDs differ: {raw_ids!r}")
    if result_ids != EXPECTED_IDS:
        errors.append(f"result artifact IDs differ: {result_ids!r}")

    runtime_path = WORKER / "metadata/runtime.json"
    runtime_bytes = runtime_path.read_bytes()
    runtime = json.loads(runtime_bytes)
    runtime_sha = sha_bytes(runtime_bytes)
    checks["runtime"] = {
        "sha256": runtime_sha,
        "sealed": runtime.get("sealed"),
        "verificationState": runtime.get("actualRuntime", {}).get("verificationState"),
        "nativeImageRouteState": runtime.get("nativeImageRoute", {}).get("state"),
        "provider": runtime.get("actualRuntime", {}).get("provider"),
        "model": runtime.get("actualRuntime", {}).get("model"),
        "reasoningEffort": runtime.get("actualRuntime", {}).get("reasoningEffort"),
        "sessionId": runtime.get("session", {}).get("sessionId"),
        "forbiddenRoutes": runtime.get("forbiddenRoutes"),
    }
    expected_runtime = ("openai-codex", "gpt-5.6-sol", "max", "20260815_224527_5f5db3")
    observed_runtime = (
        checks["runtime"]["provider"],
        checks["runtime"]["model"],
        checks["runtime"]["reasoningEffort"],
        checks["runtime"]["sessionId"],
    )
    if observed_runtime != expected_runtime:
        errors.append(f"runtime mismatch: {observed_runtime!r}")
    if runtime.get("sealed") is not True or checks["runtime"]["nativeImageRouteState"] != "exercisedVerified":
        errors.append("runtime/native route is not sealed and exercisedVerified")
    if any(runtime.get("forbiddenRoutes", {}).get(k) for k in (
        "auxiliaryVisionUsed", "qwenUsed", "ocrCanonicalEvidenceUsed", "modelDowngradeUsed",
        "sharedProviderConfigurationModified",
    )):
        errors.append("a forbidden runtime route/configuration flag is true")

    asset_checks: list[dict[str, Any]] = []
    total_submitted = 0
    total_returned = 0
    decisions: list[str] = []
    expected_next = {
        "W06-001": ("W06-002", assets[1]["sourcePath"]),
        "W06-002": ("W06-003", assets[2]["sourcePath"]),
        "W06-003": ("W06-004", assets[3]["sourcePath"]),
        "W06-004": (None, None),
    }
    for asset in assets:
        aid = asset["assetId"]
        source = REPO / asset["sourcePath"]
        raw_path = WORKER / "raw" / f"{aid}.json"
        result_path = WORKER / "results" / f"{aid}.json"
        entry: dict[str, Any] = {"assetId": aid}
        try:
            source_bytes = source.read_bytes()
            live_sha = sha_bytes(source_bytes)
            with Image.open(source) as im:
                im.verify()
            with Image.open(source) as im:
                live_meta = {
                    "width": im.width,
                    "height": im.height,
                    "format": im.format,
                    "mode": im.mode,
                    "frames": getattr(im, "n_frames", 1),
                    "bytes": len(source_bytes),
                    "decode": True,
                }
            entry["sourceLive"] = {"sha256": live_sha, **live_meta}
        except Exception as exc:
            errors.append(f"{aid} source decode/probe failed: {exc}")
            asset_checks.append(entry)
            continue
        if live_sha != asset["sourceSha256"]:
            errors.append(f"{aid} live source hash differs from assignment")

        try:
            raw = load_json(raw_path)
            result = load_json(result_path)
        except Exception as exc:
            errors.append(f"{aid} raw/result parse failed: {exc}")
            asset_checks.append(entry)
            continue

        missing = [f for f in REQUIRED_RESULT_FIELDS if f not in result]
        if missing:
            errors.append(f"{aid} result missing fields: {missing}")
        for label, obj in (("raw", raw), ("result", result)):
            if obj.get("assetId") != aid:
                errors.append(f"{aid} {label} assetId mismatch")
            if obj.get("sourcePath") != asset["sourcePath"]:
                errors.append(f"{aid} {label} sourcePath mismatch")
            if obj.get("sourceSha256") != asset["sourceSha256"]:
                errors.append(f"{aid} {label} sourceSha256 mismatch")

        expected_meta = live_meta
        if result.get("sourceMetadata") != expected_meta:
            errors.append(f"{aid} result sourceMetadata mismatch: {result.get('sourceMetadata')!r}")
        att = raw.get("attachment", {})
        submitted = att.get("submittedCount", 0)
        returned = att.get("returnedCount", 0)
        total_submitted += submitted
        total_returned += returned
        if submitted != 1 or returned != 1 or att.get("submittedAssetIds") != [aid] or att.get("returnedAssetIds") != [aid]:
            errors.append(f"{aid} attachment ID/count reconciliation failed")
        rp = result.get("runtimeProvenance", {})
        if rp.get("normalizedRecordSha256") != runtime_sha:
            errors.append(f"{aid} runtime provenance hash mismatch")
        if (rp.get("provider"), rp.get("model"), rp.get("reasoningEffort"), rp.get("sessionId")) != expected_runtime:
            errors.append(f"{aid} runtime provenance core mismatch")
        if rp.get("nativeImageRouteState") != "exercisedVerified" or any(rp.get(k) for k in (
            "auxiliaryVisionUsed", "qwenUsed", "ocrCanonicalEvidenceUsed", "modelDowngradeUsed",
        )):
            errors.append(f"{aid} invalid per-result route provenance")
        if result.get("orientation", {}).get("observed") != "upright":
            errors.append(f"{aid} final orientation is not upright")
        if result.get("rawResultPath") != str(raw_path.relative_to(REPO)):
            errors.append(f"{aid} rawResultPath mismatch")
        expected_id, expected_path = expected_next[aid]
        if (result.get("nextPendingAssetId"), result.get("nextPendingSourcePath")) != (expected_id, expected_path):
            errors.append(f"{aid} next pending tuple mismatch")
        decision = result.get("promotionDecision")
        decisions.append(decision)
        entry.update({
            "rawParsed": True,
            "resultParsed": True,
            "requiredFieldsPresent": not missing,
            "submittedCount": submitted,
            "returnedCount": returned,
            "orientation": result.get("orientation", {}).get("observed"),
            "promotionDecision": decision,
            "selectorGatePassed": result.get("validationPerformed", {}).get("exactGeneratedCellSelectorPassed"),
            "pairedSideGatePassed": result.get("validationPerformed", {}).get("uniquePairedSidePassed"),
            "candidateSidecarCreated": result.get("validationPerformed", {}).get("candidateSidecarCreated"),
        })
        asset_checks.append(entry)

    checks["assets"] = asset_checks
    checks["reconciliation"] = {
        "assignedCount": len(assets),
        "processedCount": len(result_paths),
        "submittedCount": total_submitted,
        "returnedCount": total_returned,
        "decisions": {
            "promotable": sum(d == "promote" for d in decisions),
            "deferred": sum(d == "defer" for d in decisions),
            "nonCardComplete": sum(d == "nonCardComplete" for d in decisions),
        },
        "nextPendingAssetId": None,
        "nextPendingSourcePath": None,
    }
    if total_submitted != 4 or total_returned != 4:
        errors.append(f"aggregate submitted/returned mismatch: {total_submitted}/{total_returned}")
    if decisions != ["defer"] * 4:
        errors.append(f"unexpected decisions: {decisions!r}")

    candidate_files = sorted(str(p.relative_to(WORKER)) for p in WORKER.rglob("*") if p.is_file() and "candidate" in p.name.lower())
    checks["candidateSidecars"] = {"count": len(candidate_files), "paths": candidate_files}
    if candidate_files:
        errors.append(f"candidate files exist: {candidate_files!r}")

    parse_failures: list[dict[str, str]] = []
    parsed_json_count = 0
    for path in sorted(WORKER.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
            parsed_json_count += 1
        except Exception as exc:
            parse_failures.append({"path": str(path.relative_to(WORKER)), "error": str(exc)})
    checks["workerJsonParse"] = {"parsedCount": parsed_json_count, "failures": parse_failures}
    if parse_failures:
        errors.append(f"worker JSON parse failures: {parse_failures!r}")

    git_cmds = {
        "status": ["git", "status", "--porcelain=v1", "-z"],
        "unstagedDiff": ["git", "diff", "--binary", "--no-ext-diff"],
        "stagedDiff": ["git", "diff", "--cached", "--binary", "--no-ext-diff"],
    }
    git_now: dict[str, Any] = {}
    for key, cmd in git_cmds.items():
        out = subprocess.run(cmd, cwd=REPO, stdout=subprocess.PIPE, check=True).stdout
        git_now[key] = {"sha256": sha_bytes(out), "bytes": len(out)}
    git_base = baseline["gitBaseline"]
    git_comparison = {
        "statusUnchanged": git_now["status"]["sha256"] == git_base["porcelainSha256"],
        "unstagedDiffUnchanged": git_now["unstagedDiff"]["sha256"] == git_base["unstagedDiffSha256"],
        "stagedDiffUnchanged": git_now["stagedDiff"]["sha256"] == git_base["stagedDiffSha256"],
    }
    checks["gitState"] = {"baseline": git_base, "final": git_now, "comparison": git_comparison}
    if not all(git_comparison.values()):
        warnings.append("repository Git fingerprints changed during worker run; session mutation-target audit determines worker write scope")

    db = sqlite3.connect("file:/home/smithers/.hermes/state.db?mode=ro", uri=True)
    rows = db.execute(
        "select id, role, tool_name, tool_calls, content from messages where session_id=? order by id",
        (SESSION_ID,),
    ).fetchall()
    mutation_targets: list[dict[str, Any]] = []
    vision_calls: list[dict[str, Any]] = []
    terminal_write_flags: list[dict[str, Any]] = []
    for message_id, role, tool_result_name, raw_calls, content in rows:
        for call in parse_tool_calls(raw_calls):
            name, args = tool_name_args(call)
            if name in ("write_file", "patch"):
                target = args.get("path")
                resolved = Path(target).resolve() if target else None
                in_worker = bool(resolved and (resolved == WORKER or WORKER in resolved.parents))
                mutation_targets.append({
                    "messageId": message_id,
                    "tool": name,
                    "path": target,
                    "resolvedPath": str(resolved) if resolved else None,
                    "withinWorkerRoot": in_worker,
                })
            elif name == "vision_analyze":
                vision_calls.append({
                    "messageId": message_id,
                    "imageUrl": args.get("image_url"),
                    "stableIdMentioned": next((aid for aid in EXPECTED_IDS if aid in str(args.get("question", ""))), None),
                })
            elif name == "terminal":
                command = str(args.get("command", ""))
                patterns = [">", " tee ", "rm ", "mv ", "cp ", "touch ", "mkdir ", ".write_text", ".write_bytes", "open(.*,'w"]
                hits = [p for p in patterns if p in command]
                if hits:
                    terminal_write_flags.append({"messageId": message_id, "patterns": hits, "commandSha256": sha_bytes(command.encode())})
    native_tool_results = [
        {"messageId": mid, "nativeAttachmentConfirmed": "Image loaded into your context" in (content or "")}
        for mid, role, tool_name, raw_calls, content in rows
        if role == "tool" and tool_name == "vision_analyze"
    ]
    expected_abs_paths = [str((REPO / a["sourcePath"]).resolve()) for a in assets]
    observed_vision_paths = [v["imageUrl"] for v in vision_calls]
    checks["sessionWriteScopeAudit"] = {
        "sessionId": SESSION_ID,
        "mutationTargetCount": len(mutation_targets),
        "mutationTargets": mutation_targets,
        "allMutationTargetsWithinWorkerRoot": all(x["withinWorkerRoot"] for x in mutation_targets),
        "terminalWritePatternFlags": terminal_write_flags,
    }
    checks["nativeVisionCallAudit"] = {
        "callCount": len(vision_calls),
        "calls": vision_calls,
        "exactOrderedSourcePaths": observed_vision_paths == expected_abs_paths,
        "nativeToolResultCount": len(native_tool_results),
        "nativeToolResults": native_tool_results,
        "allNativeAttachmentConfirmed": all(x["nativeAttachmentConfirmed"] for x in native_tool_results),
    }
    if not mutation_targets or not all(x["withinWorkerRoot"] for x in mutation_targets):
        errors.append("session mutation-target audit found a missing/out-of-scope write target")
    if terminal_write_flags:
        errors.append(f"terminal commands have potential write patterns: {terminal_write_flags!r}")
    if len(vision_calls) != 4 or observed_vision_paths != expected_abs_paths:
        errors.append("native vision call count/order/path audit failed")
    if len(native_tool_results) != 4 or not all(x["nativeAttachmentConfirmed"] for x in native_tool_results):
        errors.append("native attachment tool-result audit failed")

    checks["workerFileInventory"] = sorted(
        str(p.relative_to(WORKER)) for p in WORKER.rglob("*") if p.is_file()
    )
    output = {
        "schemaVersion": 1,
        "workerId": "sol-max-worker-06",
        "validationStage": os.environ.get("W06_VALIDATION_STAGE", "core"),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
        "overallPassed": not errors,
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
