#!/usr/bin/env python3
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[5]
ROOT = Path(__file__).resolve().parent
SOURCE = REPO / "assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-22-20260820T080700Z-p176060-79e991/direct_isolated_runner.py"
TARGET = ROOT / "direct_isolated_runner.py"
FORBIDDEN = [
    "W22", "W21", "worker-22", "worker-21",
    "sol-max-persistent-worker-22-20260820T080700Z-p176060-79e991",
    "e4350bb5eec7f88381c4c4aa8c493e5476ddcb8c",
    "c27ff5c141363354032b03606378a4166a85255e",
    "greenitem-181_cards", "missionTaskDeck-023", "missionTaskDeck-056",
    "missionTaskDeck-101", "missionTaskDeck-110",
    "EMERGENCY LIFE SUPPORT CODES", "FACILITY RESTART", "ERADICATION",
    "RECONNAISSANCE", "ESCORT MISSION",
    "queueIndex\": 105", "queueIndex\": 106", "queueIndex\": 107", "queueIndex\": 108",
    "queueIndex\": 109", "queueIndex\": 110", "queueIndex\": 111", "queueIndex\": 112",
    "Qwen", "qwen", "tesseract", "OCR", "vision_analyze",
]
REQUIRED = [
    "W23-", "openai-codex", "gpt-5.6-sol", "reasoningEffort': 'max",
    "'--reasoning', 'max'", "'--toolsets', 'none'", "'--pass-session-id'",
    "'--resume'", "'--image'", "assignment drift before turn",
    "source tuple/metadata drift before attachment", "stable asset ID", "native image pixels",
    "False promotion is worse than deferral", "semantic/canonical icon name",
    "metadata/smoke-audit.json", "supervisor-dispatch.json",
]


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


def main() -> None:
    text = TARGET.read_text()
    ast.parse(text)
    forbidden_hits = [marker for marker in FORBIDDEN if marker in text]
    missing_required = [marker for marker in REQUIRED if marker not in text]
    assignment = json.loads((ROOT / "assignment.json").read_text())
    preflight = json.loads((ROOT / "metadata/preflight.json").read_text())
    smoke = json.loads((ROOT / "metadata/smoke-audit.json").read_text())
    checks = {
        "pythonAstValid": True,
        "noStaleWorkerOrShardMarkers": not forbidden_hits,
        "allRequiredRuntimeAndIsolationMarkersPresent": not missing_required,
        "assignmentHasEightW23Ids": [row["assetId"] for row in assignment["assets"]] == [f"W23-{index:03d}" for index in range(1, 9)],
        "runnerContainsNoAssignedSourcePaths": all(row["sourcePath"] not in text for row in assignment["assets"]),
        "preflightPassed": preflight.get("overallPassed") is True,
        "smokePassed": smoke.get("overallPassed") is True,
        "smokeZeroTools": smoke.get("session", {}).get("toolCallCount") == 0,
        "sourceAndTargetDiffer": sha(SOURCE) != sha(TARGET),
        "rawAndResultsEmpty": not any((ROOT / "raw").iterdir()) and not any((ROOT / "results").iterdir()),
        "sealedAndPayloadDirsEmpty": not any((ROOT / "sealed-clean-raw").iterdir()) and not any((ROOT / "isolated-raw-output").iterdir()),
    }
    report = {
        "schemaVersion": 1,
        "recordType": "blindRunnerStaticAdaptationAudit",
        "recordedAt": now(),
        "workerId": ROOT.name,
        "sourceStructuralReference": SOURCE.relative_to(REPO).as_posix(),
        "sourceSha256": sha(SOURCE),
        "targetPath": TARGET.relative_to(REPO).as_posix(),
        "targetSha256": sha(TARGET),
        "forbiddenMarkersChecked": FORBIDDEN,
        "forbiddenHits": forbidden_hits,
        "requiredMarkersChecked": REQUIRED,
        "missingRequiredMarkers": missing_required,
        "checks": checks,
        "overallPassed": all(checks.values()),
    }
    immutable_json(ROOT / "metadata/blind-runner-adaptation-audit.json", report)
    print(json.dumps(report, indent=2))
    if not report["overallPassed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
