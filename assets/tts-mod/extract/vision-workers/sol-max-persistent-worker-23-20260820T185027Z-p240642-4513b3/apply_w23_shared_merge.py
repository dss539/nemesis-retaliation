#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
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
EXPECTED_DIFF = sorted(path.relative_to(REPO).as_posix() for path in SHARED.values())


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


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def replace_bytes(path: Path, content: bytes, mode: int, label: str) -> None:
    temp = path.with_name(path.name + f".w23-{label}-tmp-{os.getpid()}")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    try:
        view = memoryview(content)
        while view:
            view = view[os.write(fd, view):]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(temp, mode)
    os.replace(temp, path)
    fsync_dir(path.parent)


def hashes() -> dict[str, str]:
    return {name: sha(path) for name, path in SHARED.items()}


def state(plan: dict[str, Any]) -> str:
    current = hashes()
    if all(current[name] == plan["preimage"]["shared"][name]["sha256"] for name in SHARED):
        return "preimage"
    if all(current[name] == plan["projectedOutputSha256"][name] for name in SHARED):
        return "projected"
    return "mixed-or-foreign"


def restore_preimage(plan: dict[str, Any], label: str) -> dict[str, Any]:
    before = hashes()
    actions = []
    for name, destination in SHARED.items():
        source = PROJECTION / "preimage" / destination.name
        mode = stat.S_IMODE(destination.stat().st_mode)
        replace_bytes(destination, source.read_bytes(), mode, label)
        expected = plan["preimage"]["shared"][name]["sha256"]
        actual = sha(destination)
        if actual != expected:
            raise RuntimeError(f"{name}: preimage restoration hash mismatch")
        actions.append({"name": name, "path": destination.relative_to(REPO).as_posix(), "sha256": actual})
    if state(plan) != "preimage":
        raise RuntimeError("preimage restoration did not produce sealed state")
    return {
        "stateBefore": "projected" if before == plan["projectedOutputSha256"] else "other",
        "writesPerformed": 4,
        "actions": actions,
        "stateAfter": "preimage",
    }


def apply_projected(plan: dict[str, Any], label: str) -> dict[str, Any]:
    before = hashes()
    initial_state = state(plan)
    if initial_state == "projected":
        return {
            "stateBefore": "already-projected",
            "writesPerformed": 0,
            "sharedBefore": before,
            "sharedAfter": dict(before),
            "idempotentNoOp": True,
        }
    if initial_state != "preimage":
        raise RuntimeError(f"cannot apply projected state from {initial_state}")
    for name, destination in SHARED.items():
        projected = REPO / plan["projectedOutputPaths"][name]
        mode = stat.S_IMODE(destination.stat().st_mode)
        replace_bytes(destination, projected.read_bytes(), mode, label)
        if sha(destination) != plan["projectedOutputSha256"][name]:
            raise RuntimeError(f"{name}: projected hash mismatch after write")
    if state(plan) != "projected":
        raise RuntimeError("projected postcondition failed")
    return {
        "stateBefore": "sealed-preimage",
        "writesPerformed": 4,
        "sharedBefore": before,
        "sharedAfter": hashes(),
        "idempotentNoOp": False,
    }


def git_paths() -> list[str]:
    output = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout
    return sorted(line for line in output.splitlines() if line)


def write_failure(exc: BaseException, rollback: dict[str, Any] | None) -> None:
    index = 1
    while (ROOT / f"metadata/failures/shared-merge-attempt-{index:02d}.json").exists():
        index += 1
    atomic_json(
        ROOT / f"metadata/failures/shared-merge-attempt-{index:02d}.json",
        {
            "schemaVersion": 1,
            "recordedAt": now(),
            "errorType": type(exc).__name__,
            "error": str(exc),
            "rollback": rollback,
        },
    )


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("worker-root mismatch")
    if (ROOT / "metadata/shared-merge-report.json").exists():
        raise RuntimeError("shared merge report already exists")
    text = Path(__file__).read_text()
    stale = [f"W{number}-" for number in range(16, 23) if f"W{number}-" in text]
    if stale:
        raise RuntimeError(f"prior-shard marker in merge script: {stale}")
    plan = load(PROJECTION / "merge-plan.json")
    validation = load(ROOT / "validation/private-projection-validation.json")
    if not plan["overallPassed"] or not validation["overallPassed"]:
        raise RuntimeError("merge plan/private validation failed")
    if plan["canonicalCandidates"] or plan["promotionIds"] or plan["deferIds"] != IDS:
        raise RuntimeError("merge plan is not exact defer-only W23 scope")
    if state(plan) != "preimage":
        raise RuntimeError("shared state differs from sealed preimage")
    if git_paths():
        raise RuntimeError("tracked diff exists before merge")
    atomic_json(
        ROOT / "metadata/shared-merge-transaction-prepared.json",
        {
            "schemaVersion": 1,
            "recordedAt": now(),
            "stage": "prepared-before-shared-writes",
            "workerId": ROOT.name,
            "mergePlanPath": (PROJECTION / "merge-plan.json").relative_to(REPO).as_posix(),
            "mergePlanSha256": sha(PROJECTION / "merge-plan.json"),
            "privateValidationPath": (ROOT / "validation/private-projection-validation.json").relative_to(REPO).as_posix(),
            "privateValidationSha256": sha(ROOT / "validation/private-projection-validation.json"),
            "preimage": plan["preimage"],
            "projectedOutputSha256": plan["projectedOutputSha256"],
            "canonicalChanges": 0,
        },
    )

    trial = rollback_test = committed = identical = None
    try:
        trial = apply_projected(plan, "trial")
        if state(plan) != "projected" or git_paths() != EXPECTED_DIFF:
            raise RuntimeError("trial projected state/scope mismatch")
        trial_hashes = hashes()

        rollback_test = restore_preimage(plan, "rollback-test")
        if hashes() != {
            name: plan["preimage"]["shared"][name]["sha256"]
            for name in SHARED
        }:
            raise RuntimeError("rollback did not restore exact preimage hashes")
        if git_paths():
            raise RuntimeError("rollback did not restore clean tracked diff")

        committed = apply_projected(plan, "commit")
        committed_hashes = hashes()
        identical = apply_projected(plan, "idempotence")
        identical_hashes = hashes()
        if committed_hashes != identical_hashes:
            raise RuntimeError("identical re-merge changed shared bytes")
        if identical["writesPerformed"] != 0 or not identical["idempotentNoOp"]:
            raise RuntimeError("identical re-merge was not a no-op")
        if trial_hashes != committed_hashes:
            raise RuntimeError("trial and committed projections differ")

        progress = load(SHARED["progress"])
        queue = load(SHARED["queue"])
        registry = load(SHARED["registry"])
        corpus = load(SHARED["corpus"])
        merged_counts = {
            "complete": sum(row["status"] == "complete" for row in progress["records"]),
            "deferred": sum(row["status"] == "deferred" for row in progress["records"]),
            "queue": len(queue["entries"]),
            "registry": len(registry["entries"]),
            "corpus": len(corpus["records"]),
            "sidecars": len(list(REPO.glob("cards/**/*.json"))),
        }
        expected_counts = {
            "complete": 148,
            "deferred": 384,
            "queue": 384,
            "registry": 110,
            "corpus": 390,
            "sidecars": 78,
        }
        if merged_counts != expected_counts:
            raise RuntimeError(f"postmerge count mismatch: {merged_counts}")
        deferred = {
            row["sourcePath"]
            for row in progress["records"]
            if row["status"] == "deferred"
        }
        queue_paths = {row["sourcePath"] for row in queue["entries"]}
        if deferred != queue_paths:
            raise RuntimeError("postmerge deferred/queue partition mismatch")
        next_tuple = plan["nextEligibleTuple"]
        row = queue["entries"][next_tuple["projectedQueueIndex"]]
        if (row["sourcePath"], row["sourceSha256"]) != (
            next_tuple["sourcePath"],
            next_tuple["sourceSha256"],
        ):
            raise RuntimeError("postmerge next tuple mismatch")

        assigned = load(ROOT / "assignment.json")["assets"]
        assigned_paths = {row["sourcePath"] for row in assigned}
        merged_entries = [
            row for row in registry["entries"]
            if row["sourcePath"] in assigned_paths
        ]
        if len(merged_entries) != 8:
            raise RuntimeError("postmerge selected W23 entry count mismatch")
        match_count = 0
        no_match_count = 0
        for entry in merged_entries:
            if len(entry["runs"]) != 1:
                raise RuntimeError("postmerge W23 entry has wrong run cardinality")
            run = entry["runs"][0]
            if run["promotionDecision"] != "defer":
                raise RuntimeError("postmerge W23 run is not deferred")
            match_count += len(run["verifiedIconOccurrences"])
            no_match_count += len(run["unresolvedIconOccurrences"])
            for occurrence in run["unresolvedIconOccurrences"]:
                if occurrence["matchDecision"] != "no-match" or occurrence["canonicalToken"] is not None:
                    raise RuntimeError("postmerge unresolved occurrence malformed")
        if (match_count, no_match_count) != (2, 8):
            raise RuntimeError("postmerge occurrence count mismatch")
        if git_paths() != EXPECTED_DIFF:
            raise RuntimeError(f"postmerge Git scope mismatch: {git_paths()}")
    except BaseException as exc:
        rollback = None
        try:
            if state(plan) != "preimage":
                rollback = restore_preimage(plan, "exception-rollback")
        except BaseException as rollback_exc:
            rollback = {
                "errorType": type(rollback_exc).__name__,
                "error": str(rollback_exc),
                "stateAfter": state(plan),
            }
        write_failure(exc, rollback)
        raise

    report = {
        "schemaVersion": 1,
        "recordType": "w23DeferOnlySharedMergeRollbackAndIdempotenceAudit",
        "recordedAt": now(),
        "workerId": ROOT.name,
        "mergePlanPath": (PROJECTION / "merge-plan.json").relative_to(REPO).as_posix(),
        "mergePlanSha256": sha(PROJECTION / "merge-plan.json"),
        "trialMerge": trial,
        "intentionalRollbackVerification": rollback_test,
        "committedMerge": committed,
        "identicalRemerge": identical,
        "rollbackRestoredExactPreimage": True,
        "byteIdempotencePassed": True,
        "counts": merged_counts,
        "promotionIds": [],
        "deferIds": IDS,
        "matchedOccurrenceCount": match_count,
        "unresolvedNoMatchOccurrenceCount": no_match_count,
        "authoritativeNoMatchComparisonCount": no_match_count,
        "nextEligibleTuple": next_tuple,
        "canonicalChanges": 0,
        "sourceFilesMovedOrRenamed": 0,
        "gitDiffPathsAfterMerge": git_paths(),
        "overallPassed": True,
    }
    atomic_json(ROOT / "metadata/shared-merge-report.json", report)
    atomic_json(
        ROOT / "metadata/shared-merge-transaction-committed.json",
        {
            "schemaVersion": 1,
            "recordedAt": now(),
            "workerId": ROOT.name,
            "reportPath": (ROOT / "metadata/shared-merge-report.json").relative_to(REPO).as_posix(),
            "reportSha256": sha(ROOT / "metadata/shared-merge-report.json"),
            "state": (
                "trial-applied-rolled-back-exactly-committed-and-identical-"
                "remerge-byte-idempotent"
            ),
            "overallPassed": True,
        },
    )
    print(
        json.dumps(
            {
                "counts": merged_counts,
                "promotionCount": 0,
                "deferCount": 8,
                "matchedOccurrences": match_count,
                "unresolvedNoMatchOccurrences": no_match_count,
                "trialMergeWrites": trial["writesPerformed"],
                "rollbackWrites": rollback_test["writesPerformed"],
                "committedMergeWrites": committed["writesPerformed"],
                "identicalRemergeWrites": identical["writesPerformed"],
                "rollbackRestoredExactPreimage": True,
                "byteIdempotencePassed": True,
                "nextEligibleTuple": next_tuple,
                "gitDiffPaths": git_paths(),
                "overallPassed": True,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
