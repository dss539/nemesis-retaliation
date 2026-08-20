#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
EXPECTED_ROOT = "sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3"
EXPECTED_HEAD = "48854fdd86478c1f74b614e9daa8faaa6d0beee1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def immutable_json(path: Path, value: Any) -> None:
    content = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
    try:
        os.write(fd, content)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(path, 0o400)


def image_decode(path: Path) -> None:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        image.load()


def ancestry() -> set[int]:
    result: set[int] = set()
    pid = os.getpid()
    while pid > 1 and pid not in result:
        result.add(pid)
        try:
            lines = (Path("/proc") / str(pid) / "status").read_text().splitlines()
            pid = int(next(line.split()[1] for line in lines if line.startswith("PPid:")))
        except Exception:
            break
    return result


def overlap() -> list[dict[str, Any]]:
    parents = ancestry()
    result = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) in parents:
            continue
        try:
            raw = (proc / "cmdline").read_bytes()
            cmd = raw.replace(b"\0", b" ").decode(errors="replace").lower()
            cwd = os.readlink(proc / "cwd")
        except Exception:
            continue
        if "direct_isolated_runner.py" in cmd or "hermes chat --image" in cmd or ("nemesis-card-corpus" in cwd and "vision-workers/sol-max" in cmd):
            result.append({"pid": int(proc.name), "executable": raw.split(b"\0", 1)[0].decode(errors="replace"), "cwd": cwd})
    return sorted(result, key=lambda row: row["pid"])


def main() -> None:
    if ROOT.name != EXPECTED_ROOT:
        raise RuntimeError("root mismatch")
    baseline = json.loads((ROOT / "metadata/baseline.json").read_text())
    baseline_validation = json.loads((ROOT / "metadata/baseline-validation.json").read_text())
    smoke = json.loads((ROOT / "metadata/smoke-audit.json").read_text())
    assignment = json.loads((ROOT / "assignment.json").read_text())
    assignment_sha = sha(ROOT / "assignment.json")
    source_checks = []
    for asset in assignment["assets"]:
        source = REPO / asset["sourcePath"]
        live_sha = sha(source)
        image_decode(source)
        source_checks.append({"assetId": asset["assetId"], "sourcePath": asset["sourcePath"], "expectedSha256": asset["sourceSha256"], "liveSha256": live_sha, "decode": True, "passed": live_sha == asset["sourceSha256"]})
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=REPO, check=True, stdout=subprocess.PIPE, text=True).stdout
    lock_rows = json.loads(subprocess.run(["lslocks", "--json", "--output", "COMMAND,PID,TYPE,MODE,PATH"], check=True, stdout=subprocess.PIPE, text=True).stdout)["locks"]
    lock_path = "/home/smithers/projects/nemesis-card-corpus/.workspace.lock"
    exact_locks = [row for row in lock_rows if row.get("path") == lock_path]
    live_overlap = overlap()
    checks = {
        "gitHeadExact": head == EXPECTED_HEAD,
        "worktreeClean": not status,
        "workspaceLockExact": len(exact_locks) == 1 and exact_locks[0].get("type") == "FLOCK" and exact_locks[0].get("mode") == "WRITE" and int(exact_locks[0]["pid"]) in ancestry(),
        "noLiveOverlap": not live_overlap,
        "neutralSmokePassed": smoke.get("overallPassed") is True,
        "neutralSmokeOneApiTwoMessagesZeroTools": smoke.get("session", {}).get("apiCallCount") == 1 and smoke.get("session", {}).get("messageCount") == 2 and smoke.get("session", {}).get("toolCallCount") == 0,
        "neutralSmokeNoToolsPromptMarkers": smoke.get("checks", {}).get("noSystemToolsSection") is True and smoke.get("checks", {}).get("noSystemToolName") is True,
        "baselineValidationPassed": baseline_validation.get("overallPassed") is True,
        "assignmentImmutable": assignment_sha == baseline["assignmentSha256"] == sha(ROOT / "assignment.immutable.json"),
        "orderedTupleDigestFrozen": baseline["orderedTupleDigest"] == baseline_validation["orderedTupleDigest"],
        "eightLiveSourceHashesAndDecodesExact": len(source_checks) == 8 and all(row["passed"] for row in source_checks),
        "freshWorkerRoot": baseline.get("freshWorkerRoot") is True,
        "emptyRawResultStaging": all(not any((ROOT / name).iterdir()) for name in ("raw", "results", "sealed-clean-raw", "isolated-raw-output")),
    }
    report = {
        "schemaVersion": 1,
        "checkedAt": now(),
        "workerId": ROOT.name,
        "checks": checks,
        "evidence": {
            "gitHead": head,
            "lock": baseline["lock"],
            "liveLockRow": exact_locks,
            "contention": "busy-as-expected; read-only inspection only, no reacquisition attempted",
            "liveOverlap": live_overlap,
            "smokeSessionId": smoke["session"]["sessionId"],
            "smokeAuditPath": "metadata/smoke-audit.json",
            "smokeAuditSha256": sha(ROOT / "metadata/smoke-audit.json"),
            "assignmentSha256": assignment_sha,
            "orderedTupleDigest": baseline["orderedTupleDigest"],
            "counts": baseline["counts"],
            "orderedTuples": baseline["orderedTuples"],
            "skippedSelectedTuples": baseline["skippedSelectedTuples"],
            "sourceChecks": source_checks,
            "recoveriesBeforeVision": [
                {
                    "stage": "lock visibility probe",
                    "outcome": "terminal child did not inherit FD 3; outer supervisor holder FD/inode and exclusive lslocks row verified read-only",
                    "evidenceChanged": False,
                },
                {
                    "stage": "baseline runner pre-command guard",
                    "outcome": "fixed iterator truthiness bug before any validation command executed",
                    "evidenceChanged": False,
                },
            ],
        },
        "overallPassed": all(checks.values()),
    }
    immutable_json(ROOT / "metadata/preflight.json", report)
    print(json.dumps({"checks": checks, "smokeSessionId": smoke["session"]["sessionId"], "orderedTuples": baseline["orderedTuples"], "overallPassed": report["overallPassed"]}, indent=2))
    if not report["overallPassed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
