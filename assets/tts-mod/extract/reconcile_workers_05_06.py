#!/usr/bin/env python3
"""Reconcile the completed overlapping worker-05/worker-06 vision shards."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
W05 = EXTRACT / "vision-workers/sol-max-worker-05"
W06 = EXTRACT / "vision-workers/sol-max-worker-06"
PROGRESS = EXTRACT / "vision-progress.json"
QUEUE = EXTRACT / "low-confidence-review.json"
AUDIT = EXTRACT / "vision-workers/supervisor-reconciliation-workers-05-06.json"
OVERLAP_HOLD = W05 / "metadata/supervisor-overlap-hold-adjudication.json"

OVERLAPS = [
    ("W04-009", "W06-001", "card-11.png", "CHAIN OF COMMAND"),
    ("W04-010", "W06-002", "card-12.png", "CONTINUOUS FIRE"),
    ("W04-011", "W06-003", "card-13.png", "DEMOLITION"),
]
W06_ONLY = ("W06-004", "card-15.png", "FORCING FIRE")
NEXT_PATH = "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-045_cards/card-16.png"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_text(value: str) -> str:
    return " ".join(value.split()).upper()


def result(worker: Path, asset_id: str) -> dict[str, Any]:
    return load(worker / "results" / f"{asset_id}.json")


def evidence_paths(w05_id: str) -> list[str]:
    return [
        f"assets/tts-mod/extract/vision-workers/sol-max-worker-05/results/{w05_id}.json",
        f"assets/tts-mod/extract/vision-workers/sol-max-worker-05/raw/{w05_id}.json",
        f"assets/tts-mod/extract/vision-workers/sol-max-worker-05/contact-sheets/{w05_id}-icons-verdict.json",
    ]


def main() -> int:
    recorded_at = now_utc()
    tracked = [PROGRESS, QUEUE, W05 / "assignment.json", W06 / "assignment.json"]
    before_hashes = {str(path.relative_to(REPO)): sha(path) for path in tracked}

    progress = load(PROGRESS)
    queue = load(QUEUE)
    records = {item["sourcePath"]: item for item in progress["records"]}
    entries = {item["sourcePath"]: item for item in queue["entries"]}
    comparisons: list[dict[str, Any]] = []

    combined_reasons = {
        "card-11.png": (
            "Exact generated-cell GUID/selector and unique cell-specific paired-side provenance remain unresolved; "
            "the existing canonical target differs from this TTS source and cannot be overwritten without approval."
        ),
        "card-12.png": (
            "Exact generated-cell GUID/selector and unique cell-specific paired-side provenance remain unresolved."
        ),
        "card-13.png": (
            "Exact generated-cell GUID/selector and unique cell-specific paired-side provenance remain unresolved; "
            "the existing canonical sidecar wording conflicts with this TTS source and cannot be overwritten without approval."
        ),
        "card-15.png": (
            "The red inline glyph remains unresolved between ammoToken and ammoSlot; exact generated-cell GUID/selector "
            "and unique cell-specific paired-side provenance also remain unresolved."
        ),
    }

    for w05_id, w06_id, filename, expected_title in OVERLAPS:
        r05 = result(W05, w05_id)
        r06 = result(W06, w06_id)
        source_path = r06["sourcePath"]
        source = REPO / source_path
        assert r05["sourcePath"] == source_path
        assert r05["sourceSha256"] == r06["sourceSha256"] == sha(source)
        with Image.open(source) as image:
            image.verify()
        assert r05["promotionDecision"] == r06["promotionDecision"] == "defer"
        title05 = r05["visibleText"]["title"]
        title06 = r06["visibleText"]["title"]
        assert normalize_text(title05) == normalize_text(title06) == expected_title
        assert normalize_text(r05["visibleText"]["footer"]) == normalize_text(r06["visibleText"]["footer"]) == "HEAVY GUN OPERATOR"
        assert all(item.get("directGlossaryVerification", {}).get("status") == "passed" for item in r05["iconMorphology"])

        rec = records[source_path]
        entry = entries[source_path]
        reexamination = rec.get("reexamination") or {}
        assert reexamination.get("workerId") == "sol-max-worker-06"
        assert reexamination.get("assetId") == w06_id
        corroborating = {
            "workerId": "sol-max-worker-05",
            "sessionId": r05["runtimeProvenance"]["sessionId"],
            "assetId": w05_id,
            "decision": "defer",
            "agreement": ["source tuple", "title", "printed owner", "material text", "defer decision"],
            "additionalEvidence": "Worker 05 directly compared every claimed icon against the authoritative 49-crop glossary set and passed.",
            "paths": evidence_paths(w05_id),
        }
        reexamination["corroboratingEvidence"] = [corroborating]
        rec["reexamination"] = reexamination
        rec["supervisorAdjudication"] = {
            "recordedAt": recorded_at,
            "primaryLineage": "sol-max-worker-06",
            "corroboratingLineage": "sol-max-worker-05",
            "iconStatus": "resolved by direct worker-05 authoritative-crop comparisons",
            "promotionDecision": "defer",
            "remainingReason": combined_reasons[filename],
            "auditPath": str(AUDIT.relative_to(REPO)),
        }
        rec["deferReason"] = combined_reasons[filename]
        entry["reasonSkipped"] = combined_reasons[filename]
        entry["uncertainties"] = [combined_reasons[filename]]
        entry["vision"]["workerId"] = "sol-max-worker-06"
        entry["vision"]["corroboratingEvidence"] = [corroborating]
        entry["supervisorAdjudication"] = rec["supervisorAdjudication"]
        comparisons.append({
            "sourcePath": source_path,
            "sourceSha256": r06["sourceSha256"],
            "worker05AssetId": w05_id,
            "worker06AssetId": w06_id,
            "title": expected_title,
            "sourceTupleMatched": True,
            "titleAndOwnerMatched": True,
            "materialTextMatched": True,
            "decisionMatched": True,
            "selectedSharedLedgerLineage": "sol-max-worker-06",
            "worker05Use": "corroborating direct icon-crop evidence",
            "combinedDecision": "defer",
            "remainingReason": combined_reasons[filename],
        })

    w06_id, filename, expected_title = W06_ONLY
    r06 = result(W06, w06_id)
    source_path = r06["sourcePath"]
    assert source_path.endswith(filename)
    assert normalize_text(r06["visibleText"]["title"]) == expected_title
    assert r06["promotionDecision"] == "defer"
    assert r06["sourceSha256"] == sha(REPO / source_path)
    rec = records[source_path]
    entry = entries[source_path]
    assert (rec.get("reexamination") or {}).get("assetId") == w06_id
    rec["supervisorAdjudication"] = {
        "recordedAt": recorded_at,
        "primaryLineage": "sol-max-worker-06",
        "corroboratingLineage": None,
        "promotionDecision": "defer",
        "remainingReason": combined_reasons[filename],
        "auditPath": str(AUDIT.relative_to(REPO)),
    }
    rec["deferReason"] = combined_reasons[filename]
    entry["reasonSkipped"] = combined_reasons[filename]
    entry["uncertainties"] = [combined_reasons[filename]]
    entry["vision"]["workerId"] = "sol-max-worker-06"
    entry["supervisorAdjudication"] = rec["supervisorAdjudication"]

    assert progress["counts"]["complete"] == 134
    assert progress["counts"]["deferred"] == 398
    assert len(queue["entries"]) == 398
    progress["updatedAt"] = recorded_at
    queue["updatedAt"] = recorded_at
    reexam = progress["deferredReexamination"]
    reexam["updatedAt"] = recorded_at
    reexam["nextPosition"] = NEXT_PATH
    events = [event for event in reexam.get("reconciliationEvents", []) if event.get("kind") != "workers-05-06-overlap"]
    events.append({
        "kind": "workers-05-06-overlap",
        "at": recorded_at,
        "primaryWorkerId": "sol-max-worker-06",
        "corroboratingWorkerId": "sol-max-worker-05",
        "overlapCount": 3,
        "primaryOnlyCount": 1,
        "mergedDecisionCounts": {"defer": 4},
        "auditPath": str(AUDIT.relative_to(REPO)),
    })
    reexam["reconciliationEvents"] = events

    atomic_json(PROGRESS, progress)
    atomic_json(QUEUE, queue)

    assignment05 = load(W05 / "assignment.json")
    assignment05.update({
        "status": "completed",
        "supersededBy": "sol-max-worker-06",
        "reconciledAt": recorded_at,
        "lifecycleClosureReason": "Three valid overlapping results were retained as corroborating icon-crop evidence; worker-06 is the sole shared-ledger lineage for the same source tuples.",
    })
    atomic_json(W05 / "assignment.json", assignment05)
    dispatch05 = load(W05 / "supervisor-dispatch.json")
    dispatch05.update({
        "status": "completed",
        "supersededBy": "sol-max-worker-06",
        "reconciledAt": recorded_at,
        "lifecycleClosureReason": assignment05["lifecycleClosureReason"],
    })
    atomic_json(W05 / "supervisor-dispatch.json", dispatch05)
    final05 = load(W05 / "supervisor-final-status.json")
    final05.update({
        "status": "completed",
        "supersededBy": "sol-max-worker-06",
        "reconciledAt": recorded_at,
        "reason": assignment05["lifecycleClosureReason"],
        "assignmentSha256AfterReconciliation": sha(W05 / "assignment.json"),
        "reconciliationAuditPath": str(AUDIT.relative_to(REPO)),
    })
    atomic_json(W05 / "supervisor-final-status.json", final05)

    assignment06 = load(W06 / "assignment.json")
    assignment06.update({
        "status": "completed",
        "mergedResultCount": 4,
        "remainingAssetCount": 0,
        "reconciledAt": recorded_at,
        "lifecycleClosureReason": "All four validated deferred results were merged into the shared ledgers; three overlapping worker-05 results remain linked as corroborating evidence.",
    })
    atomic_json(W06 / "assignment.json", assignment06)
    dispatch06 = load(W06 / "supervisor-dispatch.json")
    dispatch06.update({
        "status": "completed",
        "reconciledAt": recorded_at,
        "lifecycleClosureReason": assignment06["lifecycleClosureReason"],
    })
    atomic_json(W06 / "supervisor-dispatch.json", dispatch06)
    final06 = load(W06 / "supervisor-final-status.json")
    final06.update({
        "status": "completed",
        "mergedResultCount": 4,
        "reconciledAt": recorded_at,
        "reason": assignment06["lifecycleClosureReason"],
        "assignmentSha256AfterReconciliation": sha(W06 / "assignment.json"),
        "reconciliationAuditPath": str(AUDIT.relative_to(REPO)),
    })
    atomic_json(W06 / "supervisor-final-status.json", final06)

    hold = load(OVERLAP_HOLD)
    hold.update({
        "workerStatus": "completed",
        "resolvedAt": recorded_at,
        "mergeApplied": True,
        "canonicalWrites": False,
        "sharedLedgersChanged": True,
        "reconciliationAuditPath": str(AUDIT.relative_to(REPO)),
        "nextAction": f"Resume at {NEXT_PATH}.",
    })
    hold["overlap"]["resolution"] = "Worker 06 is the sole shared-ledger lineage; worker 05 is retained as corroborating direct icon-crop evidence for the three overlaps."
    atomic_json(OVERLAP_HOLD, hold)

    after_hashes = {str(path.relative_to(REPO)): sha(path) for path in tracked}
    audit = {
        "schemaVersion": 1,
        "kind": "workers-05-06-overlap-reconciliation",
        "recordedAt": recorded_at,
        "primaryWorker": {
            "workerId": "sol-max-worker-06",
            "sessionId": "20260815_224527_5f5db3",
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
            "nativeVision": True,
            "mergedAssetIds": ["W06-001", "W06-002", "W06-003", "W06-004"],
        },
        "corroboratingWorker": {
            "workerId": "sol-max-worker-05",
            "sessionId": "20260815_222507_ce8f8a",
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
            "nativeVision": True,
            "corroboratingAssetIds": ["W04-009", "W04-010", "W04-011"],
        },
        "comparisons": comparisons,
        "primaryOnly": {
            "sourcePath": source_path,
            "assetId": w06_id,
            "title": expected_title,
            "decision": "defer",
            "remainingReason": combined_reasons[filename],
        },
        "result": {
            "reexamined": 4,
            "newlyCompleted": 0,
            "stillDeferred": 4,
            "sidecarsCreated": 0,
            "assetsCategorizedOrRenamed": 0,
            "canonicalWrites": False,
            "sourceFilesChanged": False,
            "postMergeCounts": {"complete": 134, "deferred": 398, "unaccounted": 0},
            "queueEntries": 398,
            "nextReexaminationPath": NEXT_PATH,
        },
        "beforeHashes": before_hashes,
        "afterHashes": after_hashes,
        "mergeEvidencePath": "assets/tts-mod/extract/vision-workers/sol-max-worker-06/supervisor-merges/merge-001.json",
    }
    atomic_json(AUDIT, audit)
    print(json.dumps(audit["result"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
