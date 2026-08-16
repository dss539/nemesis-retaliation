#!/usr/bin/env python3
"""Record live assignment drift and lock the direct 12-asset scope."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/smithers/nemesis-retaliation")
WORKER = REPO / "assets/tts-mod/extract/vision-workers/sol-max-worker-02"
ASSIGNMENT = WORKER / "assignment.json"
INITIAL = WORKER / "metadata/assignment-snapshot-initial.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


initial = json.loads(INITIAL.read_text(encoding="utf-8"))
current = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
current_hash = sha256(ASSIGNMENT)
if current_hash == initial["assignmentFileSha256"]:
    raise SystemExit("No assignment drift detected; refusing to manufacture a drift record")
old_rows = initial["orderedTuples"]
new_rows = current["assets"]
if len(old_rows) != 12:
    raise SystemExit(f"Direct delegated scope was expected to contain 12 assets, found {len(old_rows)}")
if len(new_rows) < 12:
    raise SystemExit(f"Revised assignment has fewer than the direct 12-asset scope: {len(new_rows)}")
old_pairs = [(row["sourcePath"], row["sourceSha256"]) for row in old_rows]
new_prefix_pairs = [(row["sourcePath"], row["sourceSha256"]) for row in new_rows[:12]]
if old_pairs != new_prefix_pairs:
    raise SystemExit("Revised assignment's first 12 source path/hash tuples do not exactly match direct delegated scope")
rebindings = [
    {
        "oldAssetId": old["assetId"],
        "newAssetId": new["assetId"],
        "sourcePath": old["sourcePath"],
        "sourceSha256": old["sourceSha256"],
        "requiresFreshNativeRead": True,
    }
    for old, new in zip(old_rows, new_rows[:12])
]
invalidated_dir = WORKER / "checkpoints/invalidated-assignment-drift-001"
invalidated_dir.mkdir(parents=True, exist_ok=True)
invalidated_paths = []
for folder in ("raw", "results"):
    for path in sorted((WORKER / folder).glob("W01-*.json")):
        destination = invalidated_dir / f"{folder}-{path.name}"
        path.replace(destination)
        invalidated_paths.append(str(destination.relative_to(WORKER)))
active_scope = [
    {
        "assignmentIndex": index,
        "assetId": row["assetId"],
        "sourcePath": row["sourcePath"],
        "sourceSha256": row["sourceSha256"],
        "sourceKind": row.get("sourceKind"),
        "retryOf": row.get("retryOf"),
    }
    for index, row in enumerate(new_rows[:12], 1)
]
excluded = [
    {
        "assetId": row["assetId"],
        "sourcePath": row["sourcePath"],
        "sourceSha256": row["sourceSha256"],
    }
    for row in new_rows[12:]
]
drift = {
    "schemaVersion": 1,
    "driftId": "assignment-drift-001",
    "detectedAt": now_utc(),
    "initialAssignmentFileSha256": initial["assignmentFileSha256"],
    "revisedAssignmentFileSha256": current_hash,
    "initialAssignmentCount": len(old_rows),
    "revisedAssignmentCount": len(new_rows),
    "initialAssignmentRevision": 1,
    "revisedAssignmentRevision": current.get("assignmentRevision"),
    "rebindings": rebindings,
    "invalidatedWorkerLocalPaths": invalidated_paths,
    "resolution": {
        "decision": "lock to the first 12 revised tuples and freshly re-read all rebound IDs",
        "basis": [
            "The direct delegated task requires exactly the clean 12-asset replacement shard and explicitly forbids scope expansion.",
            "The revised assignment preserves those same 12 source path/hash tuples in the same order as its first 12 entries but rebinds every stable ID.",
            "The eight appended entries are outside the direct delegated scope and remain pending for supervisor reassignment.",
            "No pre-drift semantic output is reused; all 12 current IDs require fresh native reads."
        ],
        "activeScopedCount": 12,
        "excludedAppendedCount": len(excluded)
    }
}
scope_lock = {
    "schemaVersion": 1,
    "createdAt": now_utc(),
    "directTaskScopeCount": 12,
    "sourceAssignmentRevision": current.get("assignmentRevision"),
    "sourceAssignmentFileSha256": current_hash,
    "activeScope": active_scope,
    "excludedAppendedAssets": excluded,
    "nextAfterScopedCompletionAssetId": excluded[0]["assetId"] if excluded else None,
    "nextAfterScopedCompletionSourcePath": excluded[0]["sourcePath"] if excluded else None,
}
dump(WORKER / "metadata/assignment-drift-001.json", drift)
dump(WORKER / "metadata/scope-lock.json", scope_lock)
runtime_path = WORKER / "metadata/runtime.json"
runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
runtime["assignmentRevisionAtRouteVerification"] = current.get("assignmentRevision")
runtime["scopedAssignmentPath"] = str(WORKER / "metadata/scope-lock.json")
runtime["runtimeContractVerified"] = bool(
    runtime.get("provider") == "openai-codex"
    and runtime.get("model") == "gpt-5.6-sol"
    and runtime.get("reasoningEffort") == "max"
    and runtime.get("runtimeVerification", {}).get("nativeImageRouteStatus") == "verified-native-attachment"
    and not runtime.get("auxiliaryVisionUsed")
    and not runtime.get("qwenUsed")
)
dump(runtime_path, runtime)
checkpoint = {
    "schemaVersion": 1,
    "workerId": current["workerId"],
    "updatedAt": now_utc(),
    "status": "assignment-drift-resolved-fresh-retry-required",
    "assignmentCount": 12,
    "liveAssignmentCount": len(new_rows),
    "completedCount": 0,
    "completedAssetIds": [],
    "nextPendingAssetId": active_scope[0]["assetId"],
    "nextPendingSourcePath": active_scope[0]["sourcePath"],
    "batchCount": 0,
    "counts": {"promote": 0, "defer": 0, "non-card-complete": 0},
    "blockers": [],
    "driftRecordPath": str(WORKER / "metadata/assignment-drift-001.json"),
    "scopeLockPath": str(WORKER / "metadata/scope-lock.json"),
    "runtimeMetadataPath": str(WORKER / "metadata/runtime.json"),
}
dump(WORKER / "checkpoint.json", checkpoint)
dump(WORKER / "checkpoints/checkpoint-drift-001.json", checkpoint)
print(json.dumps({
    "driftRecorded": True,
    "oldCount": len(old_rows),
    "newCount": len(new_rows),
    "activeScopeCount": len(active_scope),
    "reboundIds": [{"old": row["oldAssetId"], "new": row["newAssetId"]} for row in rebindings],
    "invalidatedPaths": invalidated_paths,
    "excludedAppendedIds": [row["assetId"] for row in excluded],
}, indent=2))
