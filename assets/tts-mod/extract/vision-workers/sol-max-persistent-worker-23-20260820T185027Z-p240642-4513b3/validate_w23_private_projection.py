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


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    content = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        os.write(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o400)


def counts(progress: dict[str, Any], queue: dict[str, Any], registry: dict[str, Any], corpus: dict[str, Any]) -> dict[str, int]:
    return {
        "complete": sum(row["status"] == "complete" for row in progress["records"]),
        "deferred": sum(row["status"] == "deferred" for row in progress["records"]),
        "queue": len(queue["entries"]),
        "registry": len(registry["entries"]),
        "corpus": len(corpus["records"]),
        "sidecars": len(list(REPO.glob("cards/**/*.json"))),
    }


def strip_selection(record: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(record)
    value.pop("selectedExtraction", None)
    value.pop("evidenceRuns", None)
    if isinstance(value.get("evidence"), dict):
        value["evidence"].pop("selectedExtraction", None)
    return value


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("worker-root mismatch")
    output_path = ROOT / "validation/private-projection-validation.json"
    if output_path.exists():
        raise RuntimeError("private projection validation already exists")
    report = load(PROJECTION / "report.json")
    plan = load(PROJECTION / "merge-plan.json")
    preimage = load(PROJECTION / "preimage/snapshot.json")
    if not report["overallPassed"] or not plan["overallPassed"]:
        raise RuntimeError("projection report/merge plan failed")
    if report["promotionIds"] or plan["promotionIds"] or plan["canonicalCandidates"]:
        raise RuntimeError("projection is not defer-only")
    if report["deferIds"] != IDS or plan["deferIds"] != IDS:
        raise RuntimeError("defer-ID set/order mismatch")
    if report["preCounts"] != EXPECTED_PRE_COUNTS or report["postCounts"] != EXPECTED_POST_COUNTS:
        raise RuntimeError("projection count contract mismatch")
    if preimage["counts"] != EXPECTED_PRE_COUNTS:
        raise RuntimeError("sealed preimage count mismatch")

    for name, shared_path in SHARED.items():
        copied_path = PROJECTION / "preimage" / shared_path.name
        if sha(shared_path) != preimage["shared"][name]["sha256"]:
            raise RuntimeError(f"{name}: shared bytes changed before merge")
        if copied_path.read_bytes() != shared_path.read_bytes():
            raise RuntimeError(f"{name}: sealed preimage copy mismatch")
        if (copied_path.stat().st_mode & 0o777) != 0o400:
            raise RuntimeError(f"{name}: sealed preimage mode mismatch")

    projected_paths = {
        name: REPO / report["projectedOutputPaths"][name]
        for name in SHARED
    }
    for name, path in projected_paths.items():
        if not path.exists() or sha(path) != report["projectedOutputSha256"][name]:
            raise RuntimeError(f"{name}: projected output hash mismatch")
        if (path.stat().st_mode & 0o777) != 0o400:
            raise RuntimeError(f"{name}: projected output mode mismatch")
        if plan["projectedOutputSha256"][name] != report["projectedOutputSha256"][name]:
            raise RuntimeError(f"{name}: report/plan hash mismatch")

    pre_progress = load(PROJECTION / "preimage" / SHARED["progress"].name)
    pre_queue = load(PROJECTION / "preimage" / SHARED["queue"].name)
    pre_registry = load(PROJECTION / "preimage" / SHARED["registry"].name)
    pre_corpus = load(PROJECTION / "preimage" / SHARED["corpus"].name)
    progress = load(projected_paths["progress"])
    queue = load(projected_paths["queue"])
    registry = load(projected_paths["registry"])
    corpus = load(projected_paths["corpus"])
    if counts(pre_progress, pre_queue, pre_registry, pre_corpus) != EXPECTED_PRE_COUNTS:
        raise RuntimeError("independent preimage count mismatch")
    if counts(progress, queue, registry, corpus) != EXPECTED_POST_COUNTS:
        raise RuntimeError("independent projected count mismatch")

    deferred = {
        row["sourcePath"]
        for row in progress["records"]
        if row["status"] == "deferred"
    }
    queue_paths = {row["sourcePath"] for row in queue["entries"]}
    if deferred != queue_paths or len(queue_paths) != 384:
        raise RuntimeError("projected deferred/queue bijection failed")
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
        raise RuntimeError(f"projected lifecycle mismatch: {lifecycle}")

    sys.path.insert(0, str(REPO / "assets/tts-mod/extract"))
    import card_text_evidence_registry as selected_evidence  # type: ignore
    import build_card_text_corpus as corpus_builder  # type: ignore

    selected_evidence.validate_registry(registry)
    assignment = load(ROOT / "assignment.json")
    assets = assignment["assets"]
    assigned_paths = {row["sourcePath"] for row in assets}
    pre_selected_paths = {row["sourcePath"] for row in pre_registry["entries"]}
    added_entries = [
        row for row in registry["entries"] if row["sourcePath"] in assigned_paths
    ]
    if len(added_entries) != 8 or any(row["sourcePath"] in pre_selected_paths for row in added_entries):
        raise RuntimeError("selected-evidence addition scope mismatch")

    match_count = 0
    no_match_count = 0
    selected_run_identities = []
    for asset in assets:
        aid = asset["assetId"]
        result = load(ROOT / "results" / f"{aid}.json")
        entry = next(
            row for row in added_entries
            if row["sourcePath"] == asset["sourcePath"]
        )
        if entry["sourceSha256"] != asset["sourceSha256"] or len(entry["runs"]) != 1:
            raise RuntimeError(f"{aid}: selected tuple/run cardinality mismatch")
        run = entry["runs"][0]
        if run["promotionDecision"] != "defer" or run["assetId"] != aid:
            raise RuntimeError(f"{aid}: selected run terminal-state mismatch")
        if run["visibleText"] != result["visibleText"]:
            raise RuntimeError(f"{aid}: visible-text overlay mismatch")
        if run["allMaterialTextReadable"] != result["allMaterialTextReadable"]:
            raise RuntimeError(f"{aid}: material-readability mismatch")
        result_matches = sum(
            row["matchDecision"] == "match"
            for row in result["authoritativeComparisons"]
        )
        result_no_matches = sum(
            row["matchDecision"] == "no-match"
            for row in result["authoritativeComparisons"]
        )
        if len(run["verifiedIconOccurrences"]) != result_matches:
            raise RuntimeError(f"{aid}: verified-occurrence overlay mismatch")
        if len(run["unresolvedIconOccurrences"]) != result_no_matches:
            raise RuntimeError(f"{aid}: unresolved-occurrence overlay mismatch")
        for row in run["unresolvedIconOccurrences"]:
            if row["matchDecision"] != "no-match" or row["canonicalToken"] is not None:
                raise RuntimeError(f"{aid}: malformed projected no-match")
        match_count += result_matches
        no_match_count += result_no_matches
        selected_run_identities.append(run["runIdentity"])
    if (match_count, no_match_count) != (2, 8):
        raise RuntimeError(f"selected occurrence count mismatch: {(match_count, no_match_count)}")
    if sorted(selected_run_identities) != sorted(report["selectedEvidenceRunIdentities"]):
        raise RuntimeError("selected run-identity set mismatch")

    old_progress = corpus_builder.PROGRESS
    old_queue = corpus_builder.QUEUE
    corpus_builder.PROGRESS = projected_paths["progress"]
    corpus_builder.QUEUE = projected_paths["queue"]
    try:
        rebuilt = corpus_builder.build_payload(registry=registry)
    finally:
        corpus_builder.PROGRESS = old_progress
        corpus_builder.QUEUE = old_queue
    rebuilt_bytes = (json.dumps(rebuilt, indent=2, ensure_ascii=False) + "\n").encode()
    if rebuilt_bytes != projected_paths["corpus"].read_bytes():
        raise RuntimeError("independent corpus rebuild is not byte-identical")

    projected_by_path = {row["sourcePath"]: row for row in corpus["records"]}
    pre_by_path = {row["sourcePath"]: row for row in pre_corpus["records"]}
    changed = sorted(
        path
        for path, record in projected_by_path.items()
        if strip_selection(record) != strip_selection(pre_by_path[path])
    )
    expected_changed = sorted(assigned_paths)
    if changed != expected_changed or changed != report["changedCorpusBasePaths"]:
        raise RuntimeError("projected corpus base-record scope mismatch")

    next_tuple = report["nextEligibleTuple"]
    if next_tuple != plan["nextEligibleTuple"]:
        raise RuntimeError("report/plan next-tuple mismatch")
    if next_tuple != {
        "originalQueueIndex": 121,
        "projectedQueueIndex": 121,
        "sourcePath": "assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-05.png",
        "sourceSha256": "6876c41ee8d1f660f4c2ba8012c8caf0f2ccb55ca7677dfcccfb2a69e4c43e42",
    }:
        raise RuntimeError(f"unexpected next tuple: {next_tuple}")
    queue_row = queue["entries"][next_tuple["projectedQueueIndex"]]
    if (queue_row["sourcePath"], queue_row["sourceSha256"]) != (
        next_tuple["sourcePath"], next_tuple["sourceSha256"]
    ):
        raise RuntimeError("next tuple does not index projected queue")

    if subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout:
        raise RuntimeError("tracked worktree changed during private validation")
    validation = {
        "schemaVersion": 1,
        "recordType": "w23IndependentPrivateProjectionValidation",
        "validatedAt": now(),
        "workerId": ROOT.name,
        "projectionReportPath": (PROJECTION / "report.json").relative_to(REPO).as_posix(),
        "projectionReportSha256": sha(PROJECTION / "report.json"),
        "mergePlanPath": (PROJECTION / "merge-plan.json").relative_to(REPO).as_posix(),
        "mergePlanSha256": sha(PROJECTION / "merge-plan.json"),
        "preCounts": EXPECTED_PRE_COUNTS,
        "postCounts": EXPECTED_POST_COUNTS,
        "selectedEvidenceAddedCount": 8,
        "matchedOccurrenceCount": match_count,
        "unresolvedNoMatchOccurrenceCount": no_match_count,
        "authoritativeNoMatchComparisonCount": no_match_count,
        "changedCorpusBasePaths": changed,
        "nextEligibleTuple": next_tuple,
        "checks": {
            "sealedPreimageMatchesShared": True,
            "projectedHashesMatch": True,
            "deferOnlyPlan": True,
            "registrySchemaPassed": True,
            "selectedRunScopeExact": True,
            "oneToOneNoMatchRowsPreserved": True,
            "independentCorpusRebuildByteIdentical": True,
            "deferredQueueBijectionPassed": True,
            "canonicalChangesZero": True,
            "sharedBytesUnchanged": True,
            "trackedWorktreeClean": True,
        },
        "overallPassed": True,
    }
    atomic_json(output_path, validation)
    print(
        json.dumps(
            {
                "preCounts": EXPECTED_PRE_COUNTS,
                "postCounts": EXPECTED_POST_COUNTS,
                "selectedEvidenceAddedCount": 8,
                "matchedOccurrences": match_count,
                "unresolvedNoMatchOccurrences": no_match_count,
                "independentCorpusRebuildByteIdentical": True,
                "changedCorpusBasePathCount": len(changed),
                "nextEligibleTuple": next_tuple,
                "sharedBytesUnchanged": True,
                "overallPassed": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
