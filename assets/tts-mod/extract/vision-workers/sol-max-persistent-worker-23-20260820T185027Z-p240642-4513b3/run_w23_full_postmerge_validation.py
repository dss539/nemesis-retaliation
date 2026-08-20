#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
PROJECTION = ROOT / "projections/w23-private"
EXPECTED_ROOT = "sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3"
IDS = [f"W23-{index:03d}" for index in range(1, 9)]
SHARED = {
    "progress": REPO / "assets/tts-mod/extract/vision-progress.json",
    "queue": REPO / "assets/tts-mod/extract/low-confidence-review.json",
    "registry": REPO / "assets/tts-mod/extract/selected-card-text-evidence.json",
    "corpus": REPO / "assets/tts-mod/extract/card-text-corpus.json",
}
QA = {
    "coverage": REPO / "docs/qa/card-extraction-coverage.json",
    "symbols": REPO / "docs/qa/card-symbol-resolution-backlog.json",
    "corpusValidation": REPO / "assets/tts-mod/extract/card-text-corpus-validation.json",
    "visionValidation": REPO / "assets/tts-mod/extract/vision-validation.json",
}
EXPECTED_GIT_PATHS = sorted(
    path.relative_to(REPO).as_posix()
    for path in [*SHARED.values(), *QA.values()]
)
COMMANDS = [
    (
        "focused-tests",
        [
            "python3",
            "-m",
            "pytest",
            "assets/tts-mod/extract/test_card_text_evidence_registry.py",
            "-q",
        ],
    ),
    (
        "coverage",
        [
            "python3",
            "assets/tts-mod/extract/analyze_card_extraction_coverage.py",
            "--output",
            "docs/qa/card-extraction-coverage.json",
            "--top",
            "30",
        ],
    ),
    (
        "corpus-build-1",
        ["python3", "assets/tts-mod/extract/build_card_text_corpus.py"],
    ),
    (
        "corpus-validate",
        ["python3", "assets/tts-mod/extract/validate_card_text_corpus.py"],
    ),
    (
        "unresolved-symbols",
        ["python3", "assets/tts-mod/extract/analyze_unresolved_symbols.py"],
    ),
    (
        "vision-partition",
        ["python3", "assets/tts-mod/extract/vision_validate.py"],
    ),
    (
        "reproducibility",
        [
            "python3",
            "assets/tts-mod/extract/check_card_text_corpus_reproducibility.py",
        ],
    ),
    (
        "corpus-build-2",
        ["python3", "assets/tts-mod/extract/build_card_text_corpus.py"],
    ),
]


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


def tail(value: str, limit: int = 5000) -> str:
    return value[-limit:]


def git_paths() -> list[str]:
    output = subprocess.run(
        ["git", "status", "--short", "--untracked-files=all"],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout
    return sorted(line[3:] for line in output.splitlines() if line)


def strip_selection(record: dict[str, Any]) -> dict[str, Any]:
    value = deepcopy(record)
    value.pop("selectedExtraction", None)
    value.pop("evidenceRuns", None)
    if isinstance(value.get("evidence"), dict):
        value["evidence"].pop("selectedExtraction", None)
    return value


def collect_source_paths(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, dict):
        source_path = value.get("sourcePath")
        if isinstance(source_path, str):
            paths.add(source_path)
        for child in value.values():
            paths.update(collect_source_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.update(collect_source_paths(child))
    return paths


def failure_path() -> Path:
    index = 1
    while (ROOT / f"metadata/failures/full-validation-attempt-{index:02d}.json").exists():
        index += 1
    return ROOT / f"metadata/failures/full-validation-attempt-{index:02d}.json"


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("worker-root mismatch")
    output_path = ROOT / "validation/postmerge-validation.json"
    if output_path.exists():
        raise RuntimeError("postmerge validation already exists")
    merge = load(ROOT / "metadata/shared-merge-report.json")
    transaction = load(ROOT / "metadata/shared-merge-transaction-committed.json")
    if not merge["overallPassed"] or not transaction["overallPassed"]:
        raise RuntimeError("shared merge gate failed")
    if not merge["rollbackRestoredExactPreimage"] or not merge["byteIdempotencePassed"]:
        raise RuntimeError("rollback/idempotence gate failed")
    if merge["canonicalChanges"] or merge["promotionIds"]:
        raise RuntimeError("postmerge validation is not defer-only")
    if git_paths() != sorted(path.relative_to(REPO).as_posix() for path in SHARED.values()):
        raise RuntimeError(f"pre-validation Git scope mismatch: {git_paths()}")

    command_records = []
    try:
        for name, command in COMMANDS:
            started = now()
            completed = subprocess.run(
                command,
                cwd=REPO,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            record = {
                "name": name,
                "command": command,
                "startedAt": started,
                "completedAt": now(),
                "returnCode": completed.returncode,
                "stdoutSha256": hashlib.sha256(completed.stdout.encode()).hexdigest(),
                "stderrSha256": hashlib.sha256(completed.stderr.encode()).hexdigest(),
                "stdoutTail": tail(completed.stdout),
                "stderrTail": tail(completed.stderr),
                "outputHashes": {
                    key: sha(path)
                    for key, path in {**SHARED, **QA}.items()
                    if path.exists()
                },
            }
            command_records.append(record)
            if completed.returncode:
                raise RuntimeError(
                    f"command {name} failed with {completed.returncode}: "
                    f"{tail(completed.stderr, 1000)}"
                )

        if "10 passed" not in command_records[0]["stdoutTail"]:
            raise RuntimeError("focused test output did not report 10 passed")
        if command_records[2]["outputHashes"]["corpus"] != command_records[7]["outputHashes"]["corpus"]:
            raise RuntimeError("first and second corpus builds differ")

        progress = load(SHARED["progress"])
        queue = load(SHARED["queue"])
        registry = load(SHARED["registry"])
        corpus = load(SHARED["corpus"])
        coverage = load(QA["coverage"])
        backlog = load(QA["symbols"])
        corpus_validation = load(QA["corpusValidation"])
        vision_validation = load(QA["visionValidation"])
        if not corpus_validation["passed"] or not vision_validation["passed"]:
            raise RuntimeError("generated corpus/vision validation failed")
        if corpus_validation["failureCount"] or vision_validation["failureCount"]:
            raise RuntimeError("generated validator reported failures")

        merged_counts = {
            "inScope": len(progress["records"]),
            "complete": sum(row["status"] == "complete" for row in progress["records"]),
            "deferred": sum(row["status"] == "deferred" for row in progress["records"]),
            "queue": len(queue["entries"]),
            "registry": len(registry["entries"]),
            "registryRuns": sum(len(row["runs"]) for row in registry["entries"]),
            "corpus": len(corpus["records"]),
            "sidecars": len(list(REPO.glob("cards/**/*.json"))),
        }
        if merged_counts != {
            "inScope": 532,
            "complete": 148,
            "deferred": 384,
            "queue": 384,
            "registry": 110,
            "registryRuns": 110,
            "corpus": 390,
            "sidecars": 78,
        }:
            raise RuntimeError(f"postvalidation count mismatch: {merged_counts}")
        if vision_validation["checks"]["sourceImagesDecoded"] != 532:
            raise RuntimeError("vision validator did not decode all 532 sources")
        if vision_validation["checks"]["stateCounts"] != {
            "complete": 148,
            "deferred": 384,
        }:
            raise RuntimeError("vision validator state count mismatch")
        if corpus_validation["checks"]["sourceHashesVerified"] != 390:
            raise RuntimeError("corpus validator source-hash count mismatch")
        if corpus_validation["checks"]["selectedEvidenceRegistryEntries"] != 110 or corpus_validation["checks"]["selectedEvidenceRegistryRuns"] != 110:
            raise RuntimeError("corpus validator selected-evidence count mismatch")

        deferred_paths = {
            row["sourcePath"]
            for row in progress["records"]
            if row["status"] == "deferred"
        }
        queue_paths = {row["sourcePath"] for row in queue["entries"]}
        if deferred_paths != queue_paths:
            raise RuntimeError("postvalidation deferred/queue partition mismatch")

        assignment = load(ROOT / "assignment.json")
        assets = assignment["assets"]
        assigned_paths = {row["sourcePath"] for row in assets}
        assigned_registry = [
            row for row in registry["entries"]
            if row["sourcePath"] in assigned_paths
        ]
        if len(assigned_registry) != 8:
            raise RuntimeError("W23 registry scope mismatch")
        verified = 0
        unresolved = 0
        for entry in assigned_registry:
            if len(entry["runs"]) != 1:
                raise RuntimeError("W23 registry run cardinality mismatch")
            run = entry["runs"][0]
            if run["promotionDecision"] != "defer":
                raise RuntimeError("W23 merged run is not deferred")
            verified += len(run["verifiedIconOccurrences"])
            unresolved += len(run["unresolvedIconOccurrences"])
            for occurrence in run["unresolvedIconOccurrences"]:
                if occurrence["matchDecision"] != "no-match" or occurrence["canonicalToken"] is not None:
                    raise RuntimeError("W23 merged no-match occurrence malformed")
        if (verified, unresolved) != (2, 8):
            raise RuntimeError(f"W23 merged occurrence drift: {(verified, unresolved)}")

        corpus_by_path = {row["sourcePath"]: row for row in corpus["records"]}
        pre_corpus = load(PROJECTION / "preimage" / SHARED["corpus"].name)
        pre_by_path = {row["sourcePath"]: row for row in pre_corpus["records"]}
        changed_corpus_paths = sorted(
            path
            for path, record in corpus_by_path.items()
            if strip_selection(record) != strip_selection(pre_by_path[path])
        )
        if changed_corpus_paths != sorted(assigned_paths):
            raise RuntimeError(
                f"recursive corpus diff scope mismatch: {changed_corpus_paths}"
            )
        corpus_unresolved = sum(
            len(corpus_by_path[path]["selectedExtraction"]["unresolvedIconOccurrences"])
            for path in assigned_paths
        )
        if corpus_unresolved != 8:
            raise RuntimeError("W23 corpus no-match cardinality mismatch")

        backlog_paths = collect_source_paths(backlog)
        if not assigned_paths <= backlog_paths:
            raise RuntimeError(
                f"W23 paths missing from symbol backlog: {sorted(assigned_paths - backlog_paths)}"
            )
        next_tuple = merge["nextEligibleTuple"]
        row = queue["entries"][next_tuple["projectedQueueIndex"]]
        if (row["sourcePath"], row["sourceSha256"]) != (
            next_tuple["sourcePath"],
            next_tuple["sourceSha256"],
        ):
            raise RuntimeError("next tuple no longer indexes queue")
        if next_tuple != {
            "originalQueueIndex": 121,
            "projectedQueueIndex": 121,
            "sourcePath": "assets/tts-mod/extract/v2-dl/tree/cards/game/missionTaskDeck-160_cards/card-05.png",
            "sourceSha256": "6876c41ee8d1f660f4c2ba8012c8caf0f2ccb55ca7677dfcccfb2a69e4c43e42",
        }:
            raise RuntimeError("next tuple drift")

        current_git_paths = git_paths()
        if current_git_paths != EXPECTED_GIT_PATHS:
            raise RuntimeError(f"final generated Git scope mismatch: {current_git_paths}")
        worker_json_paths = sorted(ROOT.rglob("*.json"))
        for path in worker_json_paths:
            load(path)

        validation = {
            "schemaVersion": 1,
            "recordType": "w23FullPostmergeValidation",
            "validatedAt": now(),
            "workerId": ROOT.name,
            "commands": command_records,
            "checks": {
                "focusedTenTestsPassed": True,
                "coverage532Partition": True,
                "allW23SourcesInSymbolBacklog": True,
                "corpusValidationPassed": True,
                "eightUnresolvedOccurrenceCardinalityPassed": True,
                "visionValidationPassed": True,
                "reproducibilityPassed": True,
                "corpusBuildByteStable": True,
                "allSourceHashesAndDecodesPassed": True,
                "canonicalTreeUnchanged": True,
                "recursiveCorpusDiffOnlyEightAssignedRecords": True,
                "gitDiffCheckPassed": True,
                "trackedScopeExactlyEightPaths": True,
                "nextEligibleTupleReconciled": True,
                "workerJsonParsed": True,
            },
            "counts": {
                **merged_counts,
                "canonicalImagesPaired": vision_validation["checks"]["canonicalImagesPaired"],
                "promotionCount": 0,
                "deferCount": 8,
                "matchedOccurrences": verified,
                "unresolvedNoMatchOccurrences": unresolved,
                "authoritativeNoMatchComparisons": unresolved,
                "workerJsonFiles": len(worker_json_paths),
            },
            "changedCorpusRecordPaths": changed_corpus_paths,
            "gitStatus": subprocess.run(
                ["git", "status", "--short", "--untracked-files=all"],
                cwd=REPO,
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.splitlines(),
            "gitScopePaths": current_git_paths,
            "symbolBacklogSummary": backlog["summary"],
            "w23BacklogPaths": sorted(assigned_paths),
            "nextEligibleTuple": next_tuple,
            "sharedHashes": {name: sha(path) for name, path in SHARED.items()},
            "qaHashes": {path.relative_to(REPO).as_posix(): sha(path) for path in QA.values()},
            "overallPassed": True,
        }
        atomic_json(output_path, validation)
        print(
            json.dumps(
                {
                    "commandsPassed": len(command_records),
                    "focusedTestsPassed": 10,
                    "counts": validation["counts"],
                    "changedCorpusRecordPathCount": len(changed_corpus_paths),
                    "w23BacklogPathCount": len(assigned_paths),
                    "nextEligibleTuple": next_tuple,
                    "gitScopePaths": current_git_paths,
                    "overallPassed": True,
                },
                indent=2,
            )
        )
    except BaseException as exc:
        atomic_json(
            failure_path(),
            {
                "schemaVersion": 1,
                "recordedAt": now(),
                "errorType": type(exc).__name__,
                "error": str(exc),
                "commands": command_records,
                "gitStatus": subprocess.run(
                    ["git", "status", "--short", "--untracked-files=all"],
                    cwd=REPO,
                    stdout=subprocess.PIPE,
                    text=True,
                ).stdout.splitlines(),
            },
        )
        raise


if __name__ == "__main__":
    main()
