#!/usr/bin/env python3
"""Validate and atomically merge staged deferred-asset re-examination results."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from PIL import Image

REPO = Path("/home/smithers/nemesis-retaliation")
EXTRACT = REPO / "assets/tts-mod/extract"
PROGRESS_PATH = EXTRACT / "vision-progress.json"
QUEUE_PATH = EXTRACT / "low-confidence-review.json"
RUN_ID = "sol-max-deferred-reexamination-2026-08-15"
EXPECTED_ROUTE = {
    "provider": "openai-codex",
    "model": "gpt-5.6-sol",
    "reasoningEffort": "max",
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(value, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def confidence_level(value: Any) -> Any:
    """Accept both legacy {level: ...} and normalized string confidence forms."""
    if isinstance(value, dict):
        value = value.get("level") or value.get("overall")
    if isinstance(value, str):
        lowered = value.lower()
        for level in ("high", "medium", "low"):
            if lowered.startswith(level):
                return level
    return value


def normalized_runtime_provenance(result: dict[str, Any]) -> dict[str, Any]:
    """Normalize equivalent sealed worker runtime schemas for shared-ledger use."""
    provenance = dict(result.get("runtimeProvenance") or {})
    if "nativeVision" not in provenance:
        provenance["nativeVision"] = (
            provenance.get("nativeImageRouteState") == "exercisedVerified"
            and provenance.get("runtimeVerificationState") == "verified"
        )
    provenance.setdefault("auxiliaryVisionUsed", False)
    return provenance


def orientation_status(result: dict[str, Any]) -> Any:
    orientation = result.get("orientation") or {}
    return orientation.get("status") or orientation.get("observed") or orientation.get("pixelOrientation")


def validate_result(worker: Path, assignment_item: dict[str, Any], result: dict[str, Any]) -> None:
    asset_id = assignment_item["assetId"]
    source = REPO / assignment_item["sourcePath"]
    if result.get("assetId") != asset_id:
        raise ValueError(f"{asset_id}: result assetId mismatch")
    if result.get("sourcePath") != assignment_item["sourcePath"]:
        raise ValueError(f"{asset_id}: sourcePath mismatch")
    if result.get("sourceSha256") != assignment_item["sourceSha256"]:
        raise ValueError(f"{asset_id}: result SHA-256 mismatch")
    if not source.exists() or sha256(source) != assignment_item["sourceSha256"]:
        raise ValueError(f"{asset_id}: live source missing or changed")
    with Image.open(source) as image:
        image.verify()
    raw = worker / "raw" / f"{asset_id}.json"
    if not raw.exists():
        raise ValueError(f"{asset_id}: missing raw pixel record")
    raw_data = load_json(raw)
    if raw_data.get("assetId") != asset_id or raw_data.get("sourceSha256") != assignment_item["sourceSha256"]:
        raise ValueError(f"{asset_id}: raw/result identity mismatch")
    provenance = normalized_runtime_provenance(result)
    for key, expected in EXPECTED_ROUTE.items():
        if provenance.get(key) != expected:
            raise ValueError(f"{asset_id}: runtime {key}={provenance.get(key)!r}, expected {expected!r}")
    if provenance.get("nativeVision") is not True or provenance.get("auxiliaryVisionUsed") is not False:
        raise ValueError(f"{asset_id}: unverified native-image route")
    if not (provenance.get("sessionId") or provenance.get("sessionProvenanceHandle")):
        raise ValueError(f"{asset_id}: missing session ID/provenance handle")
    decision = result.get("promotionDecision")
    if decision not in {"non-card-complete", "defer", "promote"}:
        raise ValueError(f"{asset_id}: unsupported decision {decision!r}")
    if decision == "non-card-complete":
        if confidence_level(result.get("classificationConfidence")) != "high":
            raise ValueError(f"{asset_id}: non-card classification confidence is not high")
        if confidence_level(result.get("readConfidence")) not in {"high", "medium"}:
            raise ValueError(f"{asset_id}: non-card read confidence is below medium")
        uncertainties = result.get("uncertainties") or []
        if uncertainties:
            decision_text = " ".join(result.get("decisionReasons") or []).lower()
            uncertainty_text = " ".join(str(item) for item in uncertainties).lower()
            classification_text = str(result.get("proposedClassification") or "").lower()
            combined_text = decision_text + " " + uncertainty_text + " " + classification_text
            incidental = any(term in combined_text for term in (
                "incidental", "decorative", "non-material", "nonmaterial"
            ))
            scope_limited = (
                any(term in decision_text + " " + classification_text for term in (
                    "no narrower", "not asserted", "does not rely", "without requiring"
                ))
                and any(term in uncertainty_text for term in ("exact", "narrower", "functional"))
            )
            material_terms = any(term in uncertainty_text for term in (
                "identity", "component role", "category", "ownership", "icon", "rules", "orientation"
            ))
            if (not incidental and not scope_limited) or (material_terms and not scope_limited):
                raise ValueError(f"{asset_id}: material uncertainty blocks non-card completion")
        if result.get("stagedCandidateSidecarPath"):
            raise ValueError(f"{asset_id}: non-card result unexpectedly stages a sidecar")


def queue_entry_from_result(record: dict[str, Any], result: dict[str, Any], result_rel: str, raw_rel: str) -> dict[str, Any]:
    provenance = normalized_runtime_provenance(result)
    visible = list(result.get("blindPixelObservations") or [])
    for span in result.get("visibleText") or []:
        if isinstance(span, dict) and span.get("text"):
            visible.append(f"Visible text at {span.get('location', 'unspecified location')}: {span['text']}")
    reason = "; ".join(result.get("decisionReasons") or []) or "Sol Max re-examination retained material uncertainty"
    return {
        "sourcePath": record["sourcePath"],
        "sourceKind": record["sourceKind"],
        "sourceUrl": (record.get("provenance") or {}).get("sourceUrl") or record.get("sourceUrl"),
        "sourceSha256": record["sha256"],
        "provenance": record.get("provenance") or {},
        "orientation": orientation_status(result),
        "confidentlyVisible": visible,
        "visibleText": result.get("visibleText") or [],
        "uncertainties": result.get("uncertainties") or [],
        "reasonSkipped": reason,
        "vision": {
            "provider": provenance["provider"],
            "model": provenance["model"],
            "reasoningEffort": provenance["reasoningEffort"],
            "workerId": provenance.get("workerId") or result_rel.split("/vision-workers/", 1)[1].split("/", 1)[0],
            "sessionId": provenance.get("sessionId"),
            "sessionProvenanceHandle": provenance.get("sessionProvenanceHandle"),
            "nativeVision": provenance.get("nativeVision"),
            "resultPath": result_rel,
            "rawResultPath": raw_rel,
            "evidencePath": None,
        },
        "status": "open",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", required=True)
    parser.add_argument("--superseded-by")
    parser.add_argument(
        "--worker-status",
        choices=("in-progress", "completed", "stopped-partial"),
        help="Lifecycle state to record; partial workers default to in-progress.",
    )
    parser.add_argument(
        "--exclude-asset",
        action="append",
        default=[],
        help="Hold a staged asset for separate supervisor adjudication without discarding its files.",
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    worker = EXTRACT / "vision-workers" / args.worker
    assignment_path = worker / "assignment.json"
    assignment = load_json(assignment_path)
    progress = load_json(PROGRESS_PATH)
    queue = load_json(QUEUE_PATH)
    records = {record["sourcePath"]: record for record in progress["records"]}
    queue_by_path = {entry["sourcePath"]: entry for entry in queue["entries"]}
    if len(queue_by_path) != len(queue["entries"]):
        raise ValueError("canonical review queue contains duplicate paths")

    result_paths = sorted((worker / "results").glob("*.json"))
    results_by_id: dict[str, tuple[Path, dict[str, Any]]] = {}
    assignment_by_id = {item["assetId"]: item for item in assignment["assets"]}
    for result_path in result_paths:
        result = load_json(result_path)
        asset_id = result.get("assetId")
        if asset_id in args.exclude_asset:
            continue
        if asset_id in results_by_id:
            raise ValueError(f"duplicate staged result for {asset_id}")
        if asset_id not in assignment_by_id:
            raise ValueError(f"unassigned staged result {asset_id}")
        validate_result(worker, assignment_by_id[asset_id], result)
        results_by_id[asset_id] = (result_path, result)

    if not results_by_id:
        raise ValueError("worker has no staged results")

    merged_at = now_utc()
    accepted = Counter()
    candidate_ids: list[str] = []
    for item in assignment["assets"]:
        asset_id = item["assetId"]
        if asset_id not in results_by_id:
            continue
        result_path, result = results_by_id[asset_id]
        record = records.get(item["sourcePath"])
        if record is None:
            raise ValueError(f"{asset_id}: source missing from canonical progress ledger")
        prior_reexamination = record.get("reexamination") or {}
        if (
            prior_reexamination.get("runId") == RUN_ID
            and prior_reexamination.get("workerId") == args.worker
            and prior_reexamination.get("assetId") == asset_id
        ):
            continue
        if record["status"] != "deferred" or item["sourcePath"] not in queue_by_path:
            raise ValueError(f"{asset_id}: expected exactly one current deferred/queue record")
        result_rel = result_path.relative_to(REPO).as_posix()
        raw_rel = (worker / "raw" / f"{asset_id}.json").relative_to(REPO).as_posix()
        runtime = normalized_runtime_provenance(result)
        previous_vision = record.get("vision")
        reexamination = {
            "runId": RUN_ID,
            "mergedAt": merged_at,
            "workerId": args.worker,
            "batchId": load_json(worker / "raw" / f"{asset_id}.json").get("batchId"),
            "assetId": asset_id,
            "provider": runtime["provider"],
            "model": runtime["model"],
            "reasoningEffort": runtime["reasoningEffort"],
            "nativeVision": runtime["nativeVision"],
            "auxiliaryVisionUsed": runtime["auxiliaryVisionUsed"],
            "sessionId": runtime.get("sessionId"),
            "sessionProvenanceHandle": runtime.get("sessionProvenanceHandle"),
            "resultPath": result_rel,
            "rawResultPath": raw_rel,
            "decision": result["promotionDecision"],
            "previousVision": previous_vision,
        }
        record["reexamination"] = reexamination
        record["vision"] = {
            "provider": runtime["provider"],
            "model": runtime["model"],
            "reasoningEffort": runtime["reasoningEffort"],
            "workerId": args.worker,
            "sessionId": runtime.get("sessionId"),
            "sessionProvenanceHandle": runtime.get("sessionProvenanceHandle"),
            "nativeVision": runtime["nativeVision"],
            "resultPath": result_rel,
            "confidence": confidence_level(result.get("classificationConfidence")),
        }
        decision = result["promotionDecision"]
        if decision == "non-card-complete":
            record["status"] = "complete"
            record["canonicalPath"] = record["sourcePath"]
            record["sidecarPath"] = None
            record["completionBasis"] = "; ".join(result.get("decisionReasons") or [])
            record["semanticRead"] = {
                "componentType": result.get("proposedClassification"),
                "cardSide": "notCard",
                "title": "",
                "typeLine": "",
                "body": "",
                "footer": "",
                "upperRight": "",
                "lowerCenter": "",
                "visibleText": result.get("visibleText") or [],
                "confidentlyVisible": result.get("blindPixelObservations") or [],
                "proposedCategory": None,
                "proposedSlug": None,
                "confidence": "high",
                "uncertainties": result.get("uncertainties") or [],
                "orientation": (
                    (result.get("orientation") or {}).get("status")
                    or (result.get("orientation") or {}).get("finalReadStatus")
                ),
            }
            record.pop("reviewQueuePath", None)
            record.pop("deferReason", None)
            queue_by_path.pop(record["sourcePath"])
            accepted[decision] += 1
        elif decision == "defer":
            record["status"] = "deferred"
            record["canonicalPath"] = None
            record["sidecarPath"] = None
            entry = queue_entry_from_result(record, result, result_rel, raw_rel)
            record["deferReason"] = entry["reasonSkipped"]
            record["reviewQueuePath"] = QUEUE_PATH.relative_to(REPO).as_posix()
            queue_by_path[record["sourcePath"]] = entry
            accepted[decision] += 1
        else:
            candidate_ids.append(asset_id)

    if candidate_ids:
        raise ValueError(
            "promote candidates require explicit supervisor-side sidecar/icon/provenance adjudication: "
            + ", ".join(candidate_ids)
        )

    queue["entries"] = sorted(queue_by_path.values(), key=lambda entry: entry["sourcePath"])
    queue["updatedAt"] = merged_at
    counts = Counter(record["status"] for record in progress["records"])
    progress["counts"] = {
        key: counts.get(key, 0)
        for key in ("complete", "deferred", "visionRead", "visionFailed", "pending")
    }
    progress["updatedAt"] = merged_at
    progress["nextPosition"] = None
    baseline = progress["baseline"]
    progress.setdefault("deferredReexamination", {
        "schemaVersion": 1,
        "runId": RUN_ID,
        "startedAt": (load_json(worker / "metadata/runtime.json")).get("recordedAt", merged_at),
        "startingComplete": counts["complete"] - accepted["non-card-complete"],
        "startingDeferred": counts["deferred"] + accepted["non-card-complete"],
        "sidecarsCreated": 0,
        "assetsCategorizedOrRenamed": 0,
        "workerContexts": [],
    })
    current_run_records = [
        record for record in progress["records"]
        if (record.get("reexamination") or {}).get("runId") == RUN_ID
    ]
    reexam = progress["deferredReexamination"]
    reexam.update({
        "updatedAt": merged_at,
        "reexamined": len(current_run_records),
        "newlyCompleted": sum(record["status"] == "complete" for record in current_run_records),
        "stillDeferred": counts["deferred"],
        "nextPosition": next(
            (entry["sourcePath"] for entry in queue["entries"]
             if (records[entry["sourcePath"]].get("reexamination") or {}).get("runId") != RUN_ID),
            None,
        ),
    })
    lifecycle_status = args.worker_status or (
        "completed" if len(results_by_id) == len(assignment["assets"]) else "in-progress"
    )
    first_runtime = normalized_runtime_provenance(next(iter(results_by_id.values()))[1])
    worker_context = {
        "workerId": args.worker,
        "status": lifecycle_status,
        "assigned": len(assignment["assets"]),
        "reexamined": len(results_by_id),
        "provider": EXPECTED_ROUTE["provider"],
        "model": EXPECTED_ROUTE["model"],
        "reasoningEffort": EXPECTED_ROUTE["reasoningEffort"],
        "sessionId": first_runtime.get("sessionId"),
        "sessionProvenanceHandle": first_runtime.get("sessionProvenanceHandle"),
        "rotationReason": (
            "same persistent context continues its assigned shard"
            if lifecycle_status == "in-progress"
            else "worker finished its shard" if lifecycle_status == "completed"
            else "worker context was no longer live; completed staged batches were merged before a disjoint replacement assignment"
        ),
        "supersededBy": args.superseded_by,
    }
    contexts = []
    for context in reexam.get("workerContexts", []):
        context = dict(context)
        context_worker = context.get("workerId")
        if context_worker == args.worker:
            continue
        final_status_path = EXTRACT / "vision-workers" / str(context_worker) / "supervisor-final-status.json"
        if final_status_path.exists():
            final_status = json.loads(final_status_path.read_text())
            context["status"] = final_status.get("status", context.get("status"))
            context["rotationReason"] = final_status.get(
                "rotationReason",
                "worker stopped after supervisor-recorded provenance or context rotation",
            )
            context["supersededBy"] = final_status.get("supersededBy", context.get("supersededBy"))
        contexts.append(context)
    contexts.append(worker_context)
    reexam["workerContexts"] = contexts

    progress["runSummary"].update({
        "newlyCompleted": counts["complete"] - baseline["previouslyComplete"],
        "newlyDeferred": counts["deferred"] - baseline["previouslyDeferred"],
        "totalComplete": counts["complete"],
        "totalDeferred": counts["deferred"],
        "remainingUnaccounted": len(progress["records"]) - counts["complete"] - counts["deferred"],
        "sidecarsCreated": len(list((REPO / "cards").rglob("*.json"))) - baseline["approvedCardSidecars"],
    })

    assignment["status"] = worker_context["status"]
    assignment["mergedResultCount"] = len(results_by_id)
    assignment["remainingAssetCount"] = len(assignment["assets"]) - len(results_by_id)
    assignment["supersededBy"] = args.superseded_by
    assignment["updatedAt"] = merged_at
    checkpoint_path = worker / "checkpoint.json"
    if not checkpoint_path.exists():
        checkpoint_path = worker / "checkpoints" / "checkpoint-final.json"
    checkpoint = load_json(checkpoint_path)
    checkpoint["status"] = worker_context["status"]
    checkpoint["updatedAt"] = merged_at
    checkpoint["mergedResultCount"] = len(results_by_id)
    checkpoint["supersededBy"] = args.superseded_by

    report = {
        "schemaVersion": 1,
        "workerId": args.worker,
        "validatedAt": merged_at,
        "applyRequested": args.apply,
        "stagedResultCount": len(results_by_id),
        "excludedAssetIds": list(args.exclude_asset),
        "acceptedDecisions": dict(accepted),
        "candidateIds": candidate_ids,
        "postMergeCounts": dict(counts),
        "postMergeQueueEntries": len(queue["entries"]),
        "nextReexaminationPath": reexam["nextPosition"],
        "route": EXPECTED_ROUTE | {"nativeVision": True, "auxiliaryVisionUsed": False},
        "passed": True,
    }

    if args.apply:
        atomic_json(PROGRESS_PATH, progress)
        atomic_json(QUEUE_PATH, queue)
        if lifecycle_status != "in-progress":
            atomic_json(assignment_path, assignment)
            atomic_json(checkpoint_path, checkpoint)
        merge_dir = worker / "supervisor-merges"
        merge_index = len(list(merge_dir.glob("merge-*.json"))) + 1 if merge_dir.exists() else 1
        atomic_json(merge_dir / f"merge-{merge_index:03d}.json", report)
        atomic_json(worker / "supervisor-merge-latest.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
