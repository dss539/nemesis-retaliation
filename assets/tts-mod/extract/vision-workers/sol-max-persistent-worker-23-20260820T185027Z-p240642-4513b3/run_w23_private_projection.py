#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
PROJECTION = ROOT / "projections/w23-private"
EXPECTED_ROOT = "sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3"
RUN_ID = "w23-card-extraction-20260820T185027Z-p240642-4513b3"
IDS = [f"W23-{index:03d}" for index in range(1, 9)]
EXPECTED_PRE_COUNTS = {
    "complete": 148,
    "deferred": 384,
    "queue": 384,
    "registry": 102,
    "corpus": 390,
    "sidecars": 78,
}
EXPECTED_POST_COUNTS = {**EXPECTED_PRE_COUNTS, "registry": 110}
SHARED = {
    "progress": REPO / "assets/tts-mod/extract/vision-progress.json",
    "queue": REPO / "assets/tts-mod/extract/low-confidence-review.json",
    "registry": REPO / "assets/tts-mod/extract/selected-card-text-evidence.json",
    "corpus": REPO / "assets/tts-mod/extract/card-text-corpus.json",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        view = memoryview(content)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o400)


def atomic_json(path: Path, value: Any) -> None:
    atomic_bytes(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def strip_selection(record: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(record)
    value.pop("selectedExtraction", None)
    value.pop("evidenceRuns", None)
    if isinstance(value.get("evidence"), dict):
        value["evidence"].pop("selectedExtraction", None)
    return value


def counts(progress: dict[str, Any], queue: dict[str, Any], registry: dict[str, Any], corpus: dict[str, Any]) -> dict[str, int]:
    return {
        "complete": sum(row["status"] == "complete" for row in progress["records"]),
        "deferred": sum(row["status"] == "deferred" for row in progress["records"]),
        "queue": len(queue["entries"]),
        "registry": len(registry["entries"]),
        "corpus": len(corpus["records"]),
        "sidecars": len(list(REPO.glob("cards/**/*.json"))),
    }


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("worker-root mismatch")
    if PROJECTION.exists():
        raise RuntimeError("projection already exists")
    text = Path(__file__).read_text()
    stale = [f"W{number}-" for number in range(16, 23) if f"W{number}-" in text]
    if stale:
        raise RuntimeError(f"prior-shard marker in projection generator: {stale}")
    if subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout:
        raise RuntimeError("tracked worktree dirty before private projection")

    final_validation = load(ROOT / "validation/final-validation.json")
    closure_audit = load(ROOT / "validation/closure-audit.json")
    material_normalization = load(ROOT / "metadata/material-field-normalization.json")
    source_reconciliation = load(ROOT / "metadata/source-reconciliation.json")
    if not all(
        record["overallPassed"]
        for record in (
            final_validation,
            closure_audit,
            material_normalization,
            source_reconciliation,
        )
    ):
        raise RuntimeError("worker closure/source gate failed")
    if closure_audit["auditOutput"]["errors"] or closure_audit["auditOutput"]["warnings"]:
        raise RuntimeError("standard worker auditor emitted findings")

    assignment = load(ROOT / "assignment.json")
    assets = assignment["assets"]
    if [row["assetId"] for row in assets] != IDS:
        raise RuntimeError("assignment ID/order mismatch")
    results = {aid: load(ROOT / "results" / f"{aid}.json") for aid in IDS}
    if any(result["promotionDecision"] != "defer" for result in results.values()):
        raise RuntimeError("all W23 decisions must be defer")

    pre_progress = load(SHARED["progress"])
    pre_queue = load(SHARED["queue"])
    pre_registry = load(SHARED["registry"])
    pre_corpus = load(SHARED["corpus"])
    pre_counts = counts(pre_progress, pre_queue, pre_registry, pre_corpus)
    if pre_counts != EXPECTED_PRE_COUNTS:
        raise RuntimeError(f"shared pre-count drift: {pre_counts}")
    selected_preimage_tuples = {
        (row["sourcePath"], row["sourceSha256"])
        for row in pre_registry["entries"]
    }
    assigned_tuples = {
        (row["sourcePath"], row["sourceSha256"])
        for row in assets
    }
    if assigned_tuples & selected_preimage_tuples:
        raise RuntimeError("one or more W23 tuples already selected")
    deferred_paths = {
        row["sourcePath"]
        for row in pre_progress["records"]
        if row["status"] == "deferred"
    }
    queue_paths = {row["sourcePath"] for row in pre_queue["entries"]}
    if deferred_paths != queue_paths:
        raise RuntimeError("preimage deferred/queue partition mismatch")

    sealed_at = now()
    PROJECTION.mkdir(parents=True, mode=0o700)
    for name, path in SHARED.items():
        atomic_bytes(PROJECTION / "preimage" / path.name, path.read_bytes())
    preimage = {
        "schemaVersion": 1,
        "sealedAt": sealed_at,
        "workerId": ROOT.name,
        "shared": {
            name: {
                "path": rel(path),
                "sha256": sha(path),
                "bytes": path.stat().st_size,
            }
            for name, path in SHARED.items()
        },
        "counts": pre_counts,
        "canonicalChangesProposed": 0,
        "overallPassed": True,
    }
    atomic_json(PROJECTION / "preimage/snapshot.json", preimage)

    progress = deepcopy(pre_progress)
    queue = deepcopy(pre_queue)
    registry = deepcopy(pre_registry)
    progress_by_path = {row["sourcePath"]: row for row in progress["records"]}
    queue_by_path = {row["sourcePath"]: row for row in queue["entries"]}
    pre_corpus_by_path = {row["sourcePath"]: row for row in pre_corpus["records"]}

    sys.path.insert(0, str(REPO / "assets/tts-mod/extract"))
    import card_text_evidence_registry as selected_evidence  # type: ignore
    import build_card_text_corpus as corpus_builder  # type: ignore

    runs = []
    verified_total = 0
    unresolved_total = 0
    for asset in assets:
        aid = asset["assetId"]
        result = results[aid]
        ledger = progress_by_path[asset["sourcePath"]]
        if ledger["status"] != "deferred" or asset["sourcePath"] not in queue_by_path:
            raise RuntimeError(f"{aid}: source is not deferred/queued")
        reason = "; ".join(result["decisionReasons"])
        result_path = ROOT / "results" / f"{aid}.json"
        raw_path = ROOT / "raw" / f"{aid}.json"
        vision = {
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
            "workerId": ROOT.name,
            "sessionId": result["runtimeProvenance"]["blindSessionId"],
            "resultPath": rel(result_path),
            "rawResultPath": rel(raw_path),
            "contactSheetPath": result["contactSheetPath"],
            "confidence": "high-evidence-deferred-source/identity",
        }
        ledger["canonicalPath"] = None
        ledger["sidecarPath"] = None
        ledger["reviewQueuePath"] = "assets/tts-mod/extract/low-confidence-review.json"
        ledger["deferReason"] = reason
        ledger["vision"] = vision
        ledger["semanticRead"] = {
            "componentType": result["proposedClassification"]["componentType"],
            "cardSide": "face",
            "title": result["visibleText"]["title"],
            "typeLine": result["visibleText"]["typeLine"],
            "body": result["visibleText"]["body"],
            "footer": result["visibleText"]["footer"],
            "upperRight": result["visibleText"]["upperRight"],
            "lowerCenter": result["visibleText"].get("lowerCenter", ""),
            "visibleText": "\n".join(result["visibleText"].get("sections") or []),
            "confidentlyVisible": result["blindPixelObservations"],
            "proposedCategory": "",
            "proposedSlug": "",
            "confidence": "high-evidence-deferred-source/identity",
            "uncertainties": result["uncertainties"],
            "orientation": "upright",
        }
        matched_for_asset = sum(
            row["matchDecision"] == "match"
            for row in result["authoritativeComparisons"]
        )
        queue_by_path[asset["sourcePath"]] = {
            "sourcePath": asset["sourcePath"],
            "sourceKind": ledger["sourceKind"],
            "sourceUrl": ledger["sourceUrl"],
            "sourceSha256": asset["sourceSha256"],
            "provenance": ledger["provenance"],
            "orientation": "upright",
            "confidentlyVisible": result["blindPixelObservations"],
            "visibleText": result["visibleText"],
            "uncertainties": result["uncertainties"],
            "reasonSkipped": reason,
            "vision": {
                **vision,
                "iconVerification": {
                    "status": (
                        f"{matched_for_asset}-matched-occurrences-with-"
                        f"{len(result['unresolvedLocalTokens'])}-explicit-no-match-occurrences"
                    ),
                    "evidencePath": rel(ROOT / "metadata/adjudication-summary.json"),
                },
            },
            "status": "open",
        }

        verified = []
        unresolved = []
        for comparison in result["authoritativeComparisons"]:
            occurrence = {
                "cardLocation": comparison["cardLocation"],
                "referenceLabel": comparison["referenceLabel"],
                "matchDecision": comparison["matchDecision"],
                "canonicalToken": comparison["canonicalToken"],
                "closestAlternative": comparison["closestAlternative"],
                "visibleDiscriminator": comparison["visibleDiscriminator"],
                "evidenceRun": ROOT.name,
            }
            if comparison["matchDecision"] == "match":
                verified.append(occurrence)
            else:
                unresolved.append(occurrence)
        verified_total += len(verified)
        unresolved_total += len(unresolved)
        prior_body = pre_corpus_by_path[asset["sourcePath"]]["printedData"].get("body", "")
        runtime = {
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
            "nativeImageRoute": (
                "direct persistent smoke-proven zero-tool blind session plus "
                "direct post-blind native validation"
            ),
            "blindSessionId": result["runtimeProvenance"]["blindSessionId"],
            "adjudicationSessionId": result["runtimeProvenance"]["adjudicationSessionId"],
            "auxiliaryVisionUsed": False,
            "qwenUsed": False,
            "ocrCanonicalEvidenceUsed": False,
            "modelDowngradeUsed": False,
        }
        run = {
            "runIdentity": selected_evidence.stable_run_identity(RUN_ID, ROOT.name, aid),
            "runId": RUN_ID,
            "workerId": ROOT.name,
            "assetId": aid,
            "assignmentSha256": sha(ROOT / "assignment.json"),
            "orderedTupleDigest": final_validation["orderedTupleDigest"],
            "runtime": runtime,
            "artifactPaths": {
                "blindObservationPath": rel(raw_path),
                "resultPath": rel(result_path),
                "contactSheetPath": result["contactSheetPath"],
            },
            "visibleText": result["visibleText"],
            "verifiedIconOccurrences": verified,
            "unresolvedIconOccurrences": unresolved,
            "canonicalTokensEmitted": sorted(result["canonicalTokensEmitted"]),
            "allMaterialTextReadable": result["allMaterialTextReadable"],
            "allMaterialIconsAuthoritativelyMatched": not unresolved,
            "promotionDecision": "defer",
            "decisionReasons": result["decisionReasons"],
            "conflictsWithPriorSnapshot": [
                {
                    "field": "printedData.body",
                    "priorValue": prior_body or "[no prior body]",
                    "currentStatus": (
                        "superseded in selected evidence by direct-pixel normalized "
                        "text and per-occurrence morphology"
                    ),
                    "resolution": (
                        "preserve historical base snapshot; selected overlay carries "
                        "exact current evidence without overwriting approved canonical data"
                    ),
                }
            ],
        }
        selected_evidence.validate_run(run, f"{aid} projected run")
        registry["entries"].append(
            {
                "sourcePath": asset["sourcePath"],
                "sourceSha256": asset["sourceSha256"],
                "status": selected_evidence.ENTRY_STATUS,
                "selectedRunIdentity": run["runIdentity"],
                "runs": [run],
            }
        )
        runs.append(run)

    if (verified_total, unresolved_total) != (2, 8):
        raise RuntimeError(
            f"projection occurrence drift: {(verified_total, unresolved_total)}"
        )
    queue["entries"] = sorted(queue_by_path.values(), key=lambda row: row["sourcePath"])
    queue["updatedAt"] = sealed_at
    registry["entries"].sort(
        key=lambda row: (row["sourcePath"], row["sourceSha256"])
    )
    selected_evidence.validate_registry(registry)

    lifecycle = {
        status: sum(row["status"] == status for row in progress["records"])
        for status in ("complete", "deferred", "visionRead", "visionFailed", "pending")
    }
    if lifecycle != {
        "complete": 148,
        "deferred": 384,
        "visionRead": 0,
        "visionFailed": 0,
        "pending": 0,
    }:
        raise RuntimeError(f"lifecycle drift: {lifecycle}")
    progress["counts"] = lifecycle
    progress["updatedAt"] = sealed_at
    progress["nextPosition"] = None
    progress["runSummary"] = {
        **progress["runSummary"],
        "totalComplete": 148,
        "totalDeferred": 384,
        "remainingUnaccounted": 0,
        "completedAt": sealed_at,
    }
    reexamination = progress["deferredReexamination"]
    reexamination["updatedAt"] = sealed_at
    reexamination["reexamined"] += 8
    reexamination["stillDeferred"] = 384
    reexamination["workerContexts"].append(
        {
            "workerId": ROOT.name,
            "status": "completed-private-projection-passed",
            "assigned": 8,
            "reexamined": 8,
            "provider": "openai-codex",
            "model": "gpt-5.6-sol",
            "reasoningEffort": "max",
            "sessionId": results["W23-001"]["runtimeProvenance"]["blindSessionId"],
            "postBlindSessionIds": sorted({result["runtimeProvenance"]["adjudicationSessionId"] for result in results.values()}),
            "postBlindSessionIdState": "db-verified-split-session",
            "rotationReason": (
                "worker finished exact mission-task shard"
            ),
            "promotionCount": 0,
            "deferredCount": 8,
        }
    )

    pre_selected = {
        (row["sourcePath"], row["sourceSha256"])
        for row in pre_registry["entries"]
    }
    next_tuple = None
    first_later_index = max(row["queueIndex"] for row in assets) + 1
    for queue_index in range(first_later_index, len(pre_queue["entries"])):
        row = pre_queue["entries"][queue_index]
        if (row["sourcePath"], row["sourceSha256"]) not in pre_selected:
            next_tuple = {
                "originalQueueIndex": queue_index,
                "projectedQueueIndex": queue_index,
                "sourcePath": row["sourcePath"],
                "sourceSha256": row["sourceSha256"],
            }
            break
    if next_tuple is None:
        raise RuntimeError("no next eligible queue tuple")
    reexamination["nextPosition"] = next_tuple["sourcePath"]

    output_dir = PROJECTION / "output"
    progress_path = output_dir / SHARED["progress"].name
    queue_path = output_dir / SHARED["queue"].name
    registry_path = output_dir / SHARED["registry"].name
    corpus_path = output_dir / SHARED["corpus"].name
    atomic_json(progress_path, progress)
    atomic_json(queue_path, queue)
    atomic_json(registry_path, registry)

    old_progress = corpus_builder.PROGRESS
    old_queue = corpus_builder.QUEUE
    corpus_builder.PROGRESS = progress_path
    corpus_builder.QUEUE = queue_path
    try:
        corpus = corpus_builder.build_payload(registry=registry)
    finally:
        corpus_builder.PROGRESS = old_progress
        corpus_builder.QUEUE = old_queue
    atomic_json(corpus_path, corpus)

    projected_counts = counts(progress, queue, registry, corpus)
    if projected_counts != EXPECTED_POST_COUNTS:
        raise RuntimeError(f"projected count drift: {projected_counts}")
    projected_deferred = {
        row["sourcePath"]
        for row in progress["records"]
        if row["status"] == "deferred"
    }
    projected_queue_paths = {row["sourcePath"] for row in queue["entries"]}
    if projected_deferred != projected_queue_paths:
        raise RuntimeError("projected deferred/queue partition mismatch")

    corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    pre_by_path = {row["sourcePath"]: row for row in pre_corpus["records"]}
    for asset, run in zip(assets, runs):
        record = corpus_by_path[asset["sourcePath"]]
        selected = record["selectedExtraction"]
        if selected["runIdentity"] != run["runIdentity"]:
            raise RuntimeError(f"{asset['assetId']}: selected run identity mismatch")
        if len(selected["unresolvedIconOccurrences"]) != len(
            run["unresolvedIconOccurrences"]
        ):
            raise RuntimeError(f"{asset['assetId']}: unresolved overlay mismatch")
        if record["printedData"]["body"] != results[asset["assetId"]]["visibleText"]["body"]:
            raise RuntimeError(f"{asset['assetId']}: printed body mismatch")
    changed_base_paths = sorted(
        path
        for path, row in corpus_by_path.items()
        if strip_selection(row) != strip_selection(pre_by_path[path])
    )
    expected_changed = sorted(row["sourcePath"] for row in assets)
    if changed_base_paths != expected_changed:
        raise RuntimeError(
            f"corpus base-record scope mismatch: {changed_base_paths}"
        )

    projected_hashes = {
        "progress": sha(progress_path),
        "queue": sha(queue_path),
        "registry": sha(registry_path),
        "corpus": sha(corpus_path),
    }
    shared_unchanged = all(
        sha(path) == preimage["shared"][name]["sha256"]
        for name, path in SHARED.items()
    )
    if not shared_unchanged:
        raise RuntimeError("shared bytes changed during private projection")
    report = {
        "schemaVersion": 1,
        "recordType": "w23PrivateDeferOnlyProjection",
        "recordedAt": sealed_at,
        "workerId": ROOT.name,
        "runId": RUN_ID,
        "materialFieldNormalizationPath": rel(
            ROOT / "metadata/material-field-normalization.json"
        ),
        "materialFieldNormalizationSha256": sha(
            ROOT / "metadata/material-field-normalization.json"
        ),
        "sourceReconciliationPath": rel(
            ROOT / "metadata/source-reconciliation.json"
        ),
        "sourceReconciliationSha256": sha(
            ROOT / "metadata/source-reconciliation.json"
        ),
        "preimagePath": rel(PROJECTION / "preimage/snapshot.json"),
        "preimageSha256": sha(PROJECTION / "preimage/snapshot.json"),
        "projectedOutputPaths": {
            "progress": rel(progress_path),
            "queue": rel(queue_path),
            "registry": rel(registry_path),
            "corpus": rel(corpus_path),
        },
        "projectedOutputSha256": projected_hashes,
        "preCounts": pre_counts,
        "postCounts": projected_counts,
        "promotionIds": [],
        "deferIds": IDS,
        "matchedOccurrenceCount": verified_total,
        "unresolvedNoMatchOccurrenceCount": unresolved_total,
        "authoritativeNoMatchComparisonCount": unresolved_total,
        "selectedEvidenceAddedCount": 8,
        "selectedEvidenceRunIdentities": [run["runIdentity"] for run in runs],
        "changedCorpusBasePaths": changed_base_paths,
        "nextEligibleTuple": next_tuple,
        "sharedBytesUnchanged": True,
        "canonicalChanges": 0,
        "overallPassed": True,
    }
    atomic_json(PROJECTION / "report.json", report)
    atomic_json(
        PROJECTION / "merge-plan.json",
        {
            "schemaVersion": 1,
            "sealedAt": sealed_at,
            "workerId": ROOT.name,
            "runId": RUN_ID,
            "preimage": preimage,
            "projectedOutputPaths": report["projectedOutputPaths"],
            "projectedOutputSha256": projected_hashes,
            "canonicalCandidates": [],
            "promotionIds": [],
            "deferIds": IDS,
            "expectedPostCounts": {
                "complete": 148,
                "deferred": 384,
                "registry": 110,
                "corpus": 390,
                "sidecars": 78,
            },
            "expectedQueueEntryCount": 384,
            "nextEligibleTuple": next_tuple,
            "overallPassed": True,
        },
    )
    print(
        json.dumps(
            {
                "projection": rel(PROJECTION),
                "preCounts": pre_counts,
                "postCounts": projected_counts,
                "promotionCount": 0,
                "deferCount": 8,
                "selectedEvidenceAddedCount": 8,
                "matchedOccurrences": verified_total,
                "unresolvedNoMatchOccurrences": unresolved_total,
                "nextEligibleTuple": next_tuple,
                "sharedBytesUnchanged": True,
                "overallPassed": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
