#!/usr/bin/env python3
"""Validate a completed pair/single and write batch + checkpoint."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

import worker_utils as u


def tuple_digest(assignment: dict) -> str:
    tuples = [
        (row["assetId"], row["sourcePath"], row["sourceSha256"])
        for row in assignment["assets"]
    ]
    return hashlib.sha256(
        json.dumps(tuples, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: checkpoint_batch.py BATCH_ID COMPLETED_COUNT")
    batch_id = sys.argv[1]
    completed_count = int(sys.argv[2])
    match = re.fullmatch(r"W04-B(\d+)", batch_id)
    if not match:
        raise ValueError(f"unexpected batch id: {batch_id}")
    batch_count = int(match.group(1))

    assignment = u.contract()
    rows = assignment["assets"]
    ids = [row["assetId"] for row in rows]
    if not (1 <= completed_count <= len(ids)):
        raise ValueError("completed count out of range")

    prior_count = 0
    checkpoint_path = u.WORKER / "checkpoint.json"
    if checkpoint_path.exists():
        prior_count = int(json.loads(checkpoint_path.read_text(encoding="utf-8"))["completedCount"])
    if prior_count >= completed_count:
        prior_count = completed_count - (1 if completed_count == len(ids) and completed_count % 2 else 2)
    batch_ids = ids[prior_count:completed_count]
    if len(batch_ids) not in (1, 2):
        raise ValueError(f"expected one or two new IDs, got {batch_ids}")

    baseline = json.loads((u.WORKER / "metadata/assignment-identity-baseline.json").read_text(encoding="utf-8"))
    current_file_digest = u.sha256(u.ASSIGNMENT)
    current_tuple_digest = tuple_digest(assignment)
    if current_tuple_digest != baseline["orderedTupleDigest"]:
        raise ValueError("ordered assignment tuples drifted; stop for adjudication")

    completed_ids = ids[:completed_count]
    raws = {}
    results = {}
    for asset_id in completed_ids:
        u.source_state(asset_id)
        raw_path = u.WORKER / "raw" / f"{asset_id}.json"
        result_path = u.WORKER / "results" / f"{asset_id}.json"
        if not raw_path.exists() or not result_path.exists():
            raise ValueError(f"{asset_id}: missing raw/result")
        raws[asset_id] = json.loads(raw_path.read_text(encoding="utf-8"))
        results[asset_id] = json.loads(result_path.read_text(encoding="utf-8"))

    validation = u.validate_staging(False)
    if not validation["passed"] or validation["rawCount"] != completed_count or validation["resultCount"] != completed_count:
        raise ValueError(f"staging validation mismatch: {validation}")

    decisions = {asset_id: results[asset_id]["promotionDecision"] for asset_id in batch_ids}
    batch = {
        "workerId": assignment["workerId"],
        "createdAt": u.now_utc(),
        "assignmentFileSha256": current_file_digest,
        "baselineAssignmentFileSha256": baseline["assignmentFileSha256"],
        "orderedTupleDigest": current_tuple_digest,
        "assignmentDrift": current_file_digest != baseline["assignmentFileSha256"],
        "submittedAssetIds": batch_ids,
        "returnedAssetIds": batch_ids,
        "submittedCount": len(batch_ids),
        "returnedCount": len(batch_ids),
        "oneImageCalls": [
            {"assetId": asset_id, "imageCallId": raws[asset_id].get("imageCallId")}
            for asset_id in batch_ids
        ],
        "rawPersistedIds": batch_ids,
        "resultPersistedIds": batch_ids,
        "resultDecisions": decisions,
        "runtimeMetadataPath": "metadata/runtime.json",
        "validationSnapshot": validation,
        "nextPendingAssetId": ids[completed_count] if completed_count < len(ids) else None,
        "nextPendingSourcePath": rows[completed_count]["sourcePath"] if completed_count < len(rows) else None,
    }
    batch_path = u.write_batch(batch_id, batch)

    counts = Counter(result["promotionDecision"] for result in results.values())
    checkpoint = {
        "workerId": assignment["workerId"],
        "runId": assignment["runId"],
        "updatedAt": u.now_utc(),
        "status": "complete" if completed_count == len(ids) else "in_progress",
        "batchCount": batch_count,
        "completedCount": completed_count,
        "completedAssetIds": completed_ids,
        "pendingCount": len(ids) - completed_count,
        "nextPendingAssetId": ids[completed_count] if completed_count < len(ids) else None,
        "nextPendingSourcePath": rows[completed_count]["sourcePath"] if completed_count < len(rows) else None,
        "assignmentFileSha256": current_file_digest,
        "orderedTupleDigest": current_tuple_digest,
        "assignmentDriftObserved": current_file_digest != baseline["assignmentFileSha256"],
        "rawCount": validation["rawCount"],
        "resultCount": validation["resultCount"],
        "promotionDecisionCounts": {
            "promote": counts.get("promote", 0),
            "defer": counts.get("defer", 0),
            "non-card-complete": counts.get("non-card-complete", 0),
        },
        "lastBatchManifestPath": str(batch_path.relative_to(u.WORKER)),
    }
    u.write_checkpoint(checkpoint)
    print(json.dumps({"batchPath": str(batch_path), "checkpoint": checkpoint}, indent=2))


if __name__ == "__main__":
    main()
