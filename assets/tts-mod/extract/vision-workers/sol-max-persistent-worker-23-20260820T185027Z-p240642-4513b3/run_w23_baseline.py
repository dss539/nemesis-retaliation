#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
EXPECTED_ROOT = "sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3"
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
COMMANDS = [
    (
        "focused-tests",
        ["python3", "-m", "pytest", "assets/tts-mod/extract/test_card_text_evidence_registry.py", "-q"],
    ),
    (
        "coverage",
        ["python3", "assets/tts-mod/extract/analyze_card_extraction_coverage.py", "--output", "docs/qa/card-extraction-coverage.json", "--top", "30"],
    ),
    ("corpus-build-1", ["python3", "assets/tts-mod/extract/build_card_text_corpus.py"]),
    ("corpus-validate", ["python3", "assets/tts-mod/extract/validate_card_text_corpus.py"]),
    ("unresolved-symbols", ["python3", "assets/tts-mod/extract/analyze_unresolved_symbols.py"]),
    ("vision-partition", ["python3", "assets/tts-mod/extract/vision_validate.py"]),
    ("reproducibility", ["python3", "assets/tts-mod/extract/check_card_text_corpus_reproducibility.py"]),
    ("corpus-build-2", ["python3", "assets/tts-mod/extract/build_card_text_corpus.py"]),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load(path: Path) -> Any:
    return json.loads(path.read_text())


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha(path: Path) -> str:
    return sha_bytes(path.read_bytes())


def immutable_bytes(path: Path, value: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        os.write(fd, value)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o400)


def immutable_json(path: Path, value: Any) -> None:
    immutable_bytes(path, (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode())


def tail(value: str, limit: int = 5000) -> str:
    return value[-limit:]


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("worker root mismatch")
    baseline = load(ROOT / "metadata/baseline.json")
    assignment_sha = sha(ROOT / "assignment.json")
    if assignment_sha != baseline["assignmentSha256"] or assignment_sha != sha(ROOT / "assignment.immutable.json"):
        raise RuntimeError("assignment drift before baseline validation")
    if any(any((ROOT / name).iterdir()) for name in ("raw", "results", "sealed-clean-raw", "isolated-raw-output")):
        raise RuntimeError("vision staging is not empty before baseline validation")
    if subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout:
        raise RuntimeError("worktree dirty before baseline validation")

    shared_before = {name: sha(path) for name, path in SHARED.items()}
    qa_before = {name: sha(path) for name, path in QA.items()}
    command_records: list[dict[str, Any]] = []
    overall = True
    for name, command in COMMANDS:
        started = now()
        run = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        completed = now()
        stdout_path = ROOT / "logs/baseline" / f"{name}.stdout.txt"
        stderr_path = ROOT / "logs/baseline" / f"{name}.stderr.txt"
        immutable_bytes(stdout_path, run.stdout.encode())
        immutable_bytes(stderr_path, run.stderr.encode())
        record = {
            "name": name,
            "command": command,
            "startedAt": started,
            "completedAt": completed,
            "returnCode": run.returncode,
            "stdoutPath": stdout_path.relative_to(ROOT).as_posix(),
            "stdoutSha256": sha(stdout_path),
            "stderrPath": stderr_path.relative_to(ROOT).as_posix(),
            "stderrSha256": sha(stderr_path),
            "stdoutTail": tail(run.stdout),
            "stderrTail": tail(run.stderr),
        }
        command_records.append(record)
        if run.returncode != 0:
            overall = False
            break

    progress = load(SHARED["progress"])
    queue = load(SHARED["queue"])
    registry = load(SHARED["registry"])
    corpus = load(SHARED["corpus"])
    vision = load(QA["visionValidation"])
    corpus_validation = load(QA["corpusValidation"])
    counts = {
        "complete": sum(row["status"] == "complete" for row in progress["records"]),
        "deferred": sum(row["status"] == "deferred" for row in progress["records"]),
        "queue": len(queue["entries"]),
        "registry": len(registry["entries"]),
        "corpus": len(corpus["records"]),
        "sidecars": len(list((REPO / "cards").rglob("*.json"))),
        "sourceImagesDecoded": vision.get("checks", {}).get("sourceImagesDecoded"),
        "corpusSourceHashesVerified": corpus_validation.get("checks", {}).get("sourceHashesVerified"),
    }
    expected_counts = {
        "complete": 148,
        "deferred": 384,
        "queue": 384,
        "registry": 102,
        "corpus": 390,
        "sidecars": 78,
        "sourceImagesDecoded": 532,
        "corpusSourceHashesVerified": 390,
    }
    checks = {
        "allEightCommandsPassed": overall and len(command_records) == len(COMMANDS),
        "focusedTenTestsPassed": bool(command_records and "10 passed" in command_records[0]["stdoutTail"]),
        "countsExact": counts == expected_counts,
        "visionValidationPassed": vision.get("passed") is True and vision.get("failureCount") == 0,
        "corpusValidationPassed": corpus_validation.get("passed") is True and corpus_validation.get("failureCount") == 0,
        "sharedHashesUnchanged": {name: sha(path) for name, path in SHARED.items()} == shared_before,
        "qaHashesUnchanged": {name: sha(path) for name, path in QA.items()} == qa_before,
        "assignmentUnchanged": sha(ROOT / "assignment.json") == assignment_sha,
        "worktreeStillClean": not bool(subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout),
    }
    overall = all(checks.values())
    report = {
        "schemaVersion": 1,
        "recordedAt": now(),
        "workerId": ROOT.name,
        "git": {
            "head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout.strip(),
            "cleanBefore": True,
            "cleanAfter": checks["worktreeStillClean"],
        },
        "assignmentSha256": assignment_sha,
        "orderedTupleDigest": baseline["orderedTupleDigest"],
        "counts": counts,
        "commands": command_records,
        "checks": checks,
        "overallPassed": overall,
    }
    immutable_json(ROOT / "metadata/baseline-validation.json", report)
    print(json.dumps({"counts": counts, "checks": checks, "commands": [{"name": r["name"], "returnCode": r["returnCode"], "stdoutTail": r["stdoutTail"][-300:]} for r in command_records], "overallPassed": overall}, indent=2))
    if not overall:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
