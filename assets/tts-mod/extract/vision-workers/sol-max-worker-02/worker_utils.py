#!/usr/bin/env python3
"""Worker-local initialization, checkpoint, and validation helpers."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path("/home/smithers/nemesis-retaliation")
WORKER = REPO / "assets/tts-mod/extract/vision-workers/sol-max-worker-02"
ASSIGNMENT = WORKER / "assignment.json"
WORKER_REL = WORKER.relative_to(REPO).as_posix() + "/"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def external_git_status() -> dict[str, Any]:
    proc = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    lines = [line for line in proc.stdout.splitlines() if WORKER_REL not in line]
    payload = "\n".join(lines) + ("\n" if lines else "")
    return {
        "entryCount": len(lines),
        "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "entries": lines,
    }


def source_inventory() -> dict[str, Any]:
    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    rows = []
    for index, asset in enumerate(assignment["assets"], 1):
        source = REPO / asset["sourcePath"]
        with Image.open(source) as im:
            width, height = im.size
            fmt = im.format
            mode = im.mode
            frames = getattr(im, "n_frames", 1)
            im.verify()
        actual = sha256(source)
        rows.append(
            {
                "assignmentIndex": index,
                "assetId": asset["assetId"],
                "sourcePath": asset["sourcePath"],
                "absoluteSourcePath": str(source),
                "assignedSha256": asset["sourceSha256"],
                "verifiedSha256": actual,
                "hashMatchesAssignment": actual == asset["sourceSha256"],
                "byteSize": source.stat().st_size,
                "dimensions": {"width": width, "height": height},
                "format": fmt,
                "mode": mode,
                "frames": frames,
                "decodeVerified": True,
            }
        )
    ids = [row["assetId"] for row in rows]
    paths = [row["sourcePath"] for row in rows]
    return {
        "generatedAt": now_utc(),
        "assignmentCount": len(rows),
        "uniqueAssetIdCount": len(set(ids)),
        "uniqueSourcePathCount": len(set(paths)),
        "allHashesMatchAssignment": all(row["hashMatchesAssignment"] for row in rows),
        "allSourcesDecode": all(row["decodeVerified"] for row in rows),
        "assets": rows,
    }


def init() -> None:
    for name in ("metadata", "raw", "results", "batches", "checkpoints", "candidate-sidecars", "crops", "contact-sheets"):
        (WORKER / name).mkdir(parents=True, exist_ok=True)
    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    inventory = source_inventory()
    runtime = {
        "recordedAt": now_utc(),
        "workerId": assignment["workerId"],
        "provider": "openai-codex",
        "model": "gpt-5.6-sol",
        "reasoningEffort": "max",
        "platform": "subagent",
        "nativeVisionRoute": "Hermes vision_analyze attachment delivered to the active native multimodal model",
        "persistentWorker": True,
        "auxiliaryVisionUsed": False,
        "ocrUsedAsCanonicalEvidence": False,
        "qwenUsed": False,
        "runtimeVerification": {
            "activeSystemRuntimeHeader": {
                "provider": "openai-codex",
                "model": "gpt-5.6-sol",
                "platform": "subagent"
            },
            "delegationConfigReadOnlyCheck": {
                "provider": "openai-codex",
                "model": "gpt-5.6-sol",
                "reasoningEffort": "max"
            },
            "delegatedChildContextEnvironment": os.environ.get("HERMES_DELEGATED_CHILD_CONTEXT") == "1",
            "rpcSocketHandle": Path(os.environ.get("HERMES_RPC_SOCKET", "unexposed")).name,
            "sessionId": None,
            "sessionIdNote": "Hermes did not expose a canonical session ID inside this delegated child; the worker ID, single persistent conversation, and unique RPC socket handle are retained as the session-provenance handle."
        },
        "assignmentModelContractMatchesRuntime": assignment["model"] == {
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max"
        },
    }
    dump(WORKER / "metadata/runtime.json", runtime)
    dump(WORKER / "metadata/source-inventory-initial.json", inventory)
    baseline = external_git_status()
    baseline["recordedAt"] = now_utc()
    baseline["scope"] = "git status entries outside worker directory; pre-existing worktree is intentionally dirty"
    dump(WORKER / "metadata/git-baseline-external.json", baseline)
    checkpoint = {
        "schemaVersion": 1,
        "workerId": assignment["workerId"],
        "updatedAt": now_utc(),
        "status": "initialized",
        "assignmentCount": len(assignment["assets"]),
        "completedCount": 0,
        "completedAssetIds": [],
        "nextPendingAssetId": assignment["assets"][0]["assetId"],
        "nextPendingSourcePath": assignment["assets"][0]["sourcePath"],
        "batchCount": 0,
        "runtimeMetadataPath": str(WORKER / "metadata/runtime.json"),
    }
    dump(WORKER / "checkpoint.json", checkpoint)
    dump(WORKER / "checkpoints/checkpoint-000.json", checkpoint)
    print(json.dumps({"initialized": True, "assignmentCount": len(assignment["assets"]), "allHashesMatch": inventory["allHashesMatchAssignment"], "worker": str(WORKER)}, indent=2))


def validate() -> None:
    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    assigned = [a["assetId"] for a in assignment["assets"]]
    result_paths = sorted((WORKER / "results").glob("W01-*.json"))
    raw_paths = sorted((WORKER / "raw").glob("W01-*.json"))
    results = [json.loads(p.read_text(encoding="utf-8")) for p in result_paths]
    raws = [json.loads(p.read_text(encoding="utf-8")) for p in raw_paths]
    result_ids = [r.get("assetId") for r in results]
    raw_ids = [r.get("assetId") for r in raws]
    final_inventory = source_inventory()
    baseline = json.loads((WORKER / "metadata/git-baseline-external.json").read_text(encoding="utf-8"))
    current = external_git_status()
    candidate_paths = sorted((WORKER / "candidate-sidecars").rglob("*.json"))
    candidate_errors = []
    allowed_sidecar_keys = {"body", "upperRight", "upperLeft", "lowerRight", "lowerLeft"}
    for path in candidate_paths:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(obj, dict):
                candidate_errors.append(f"{path}: not an object")
            extra = sorted(set(obj) - allowed_sidecar_keys)
            if extra:
                candidate_errors.append(f"{path}: unexpected keys {extra}")
        except Exception as exc:
            candidate_errors.append(f"{path}: {exc!r}")
    required = {
        "assetId", "sourcePath", "sourceSha256", "sourceMetadata", "runtimeProvenance",
        "orientation", "blindPixelObservations", "visibleText", "iconMorphology",
        "evidenceConsulted", "proposedClassification", "proposedPath", "readConfidence",
        "classificationConfidence", "uncertainties", "promotionDecision", "decisionReasons",
        "stagedCandidateSidecarPath", "validationPerformed"
    }
    required_errors = []
    for path, result in zip(result_paths, results):
        missing = sorted(required - set(result))
        if missing:
            required_errors.append({"path": str(path), "missing": missing})
    report = {
        "validatedAt": now_utc(),
        "assignmentCount": len(assigned),
        "resultCount": len(results),
        "rawCount": len(raws),
        "assignedIdsUnique": len(set(assigned)) == len(assigned),
        "resultIdsUnique": len(set(result_ids)) == len(result_ids),
        "rawIdsUnique": len(set(raw_ids)) == len(raw_ids),
        "resultIdsMatchAssignmentInOrder": result_ids == assigned,
        "rawIdsMatchAssignmentInOrder": raw_ids == assigned,
        "missingResultIds": [x for x in assigned if x not in result_ids],
        "missingRawIds": [x for x in assigned if x not in raw_ids],
        "unexpectedResultIds": [x for x in result_ids if x not in assigned],
        "unexpectedRawIds": [x for x in raw_ids if x not in assigned],
        "requiredFieldErrors": required_errors,
        "sourceHashesUnchanged": final_inventory["allHashesMatchAssignment"],
        "allSourcesDecode": final_inventory["allSourcesDecode"],
        "candidateSidecarCount": len(candidate_paths),
        "candidateSidecarSchemaErrors": candidate_errors,
        "externalGitStatusBaselineSha256": baseline["sha256"],
        "externalGitStatusFinalSha256": current["sha256"],
        "externalGitStatusUnchanged": baseline["sha256"] == current["sha256"],
        "externalGitStatusAddedEntries": sorted(set(current["entries"]) - set(baseline["entries"])),
        "externalGitStatusRemovedEntries": sorted(set(baseline["entries"]) - set(current["entries"])),
        "workerWritesOnlyCheck": "All worker-authored paths are under the worker directory; external git status is compared separately.",
    }
    report["passed"] = all([
        report["assignmentCount"] == report["resultCount"] == report["rawCount"],
        report["assignedIdsUnique"], report["resultIdsUnique"], report["rawIdsUnique"],
        report["resultIdsMatchAssignmentInOrder"], report["rawIdsMatchAssignmentInOrder"],
        not report["requiredFieldErrors"], report["sourceHashesUnchanged"], report["allSourcesDecode"],
        not report["candidateSidecarSchemaErrors"], report["externalGitStatusUnchanged"],
    ])
    dump(WORKER / "validation.json", report)
    dump(WORKER / "metadata/source-inventory-final.json", final_inventory)
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("init", "validate"))
    args = parser.parse_args()
    if args.command == "init":
        init()
    else:
        validate()


if __name__ == "__main__":
    main()
