#!/usr/bin/env python3
"""Preserve exact real-CLI identifier-key admission examples."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

REPO = Path("/home/smithers/projects/nemesis-c5-r03/repos/nemesis-retaliation")
AUDIT = REPO / "docs/qa/implementation-readiness/correctness-audit"
SCRIPT = REPO / "scripts/build_correctness_audit_prompt.py"
EVIDENCE = Path("/home/smithers/projects/nemesis-c5-r03/review-output/c5-r03/admitted-examples")
IDENTIFIER = "rootCauseId"
RENDERED_KEY = f"leak:{IDENTIFIER}:field"
SENTINEL = b"c5-r03-reproduction-sentinel\x00\xff\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    lexical = re.search(
        rf"(?<![A-Za-z0-9_]){re.escape(IDENTIFIER)}(?![A-Za-z0-9_])",
        RENDERED_KEY,
    )
    packets = AUDIT / "packets"
    prompts = packets / "prompts"
    packets_existed = packets.exists()
    prompts_existed = prompts.exists()
    input_root = packets / f".c5-r03-admission-repro-{os.getpid()}"
    output_root = prompts / f".c5-r03-admission-repro-{os.getpid()}"
    packet_path = input_root / "packet.json"
    review_path = input_root / "completeness.json"
    output_path = output_root / "prompt.txt"
    output_rel = output_path.relative_to(REPO).as_posix()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []

    def invoke(location: str, initial: str) -> None:
        payload = {"outer": [{"path": {RENDERED_KEY: "post-reveal-value"}}]}
        packet = payload if location == "packet" else {"safe": "safe"}
        review = payload if location == "completeness" else {"safe": "safe"}
        input_root.mkdir(parents=True, exist_ok=True)
        packet_bytes = (json.dumps(packet, ensure_ascii=False, sort_keys=True) + "\n").encode()
        review_bytes = (json.dumps(review, ensure_ascii=False, sort_keys=True) + "\n").encode()
        packet_path.write_bytes(packet_bytes)
        review_path.write_bytes(review_bytes)
        output_root.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            output_path.unlink()
        if initial == "sentinel":
            output_path.write_bytes(SENTINEL)
        before = output_path.read_bytes() if output_path.exists() else None
        command = [
            sys.executable,
            str(SCRIPT),
            "--mode",
            "blind",
            "--packet",
            str(packet_path),
            "--completeness",
            str(review_path),
            "--output",
            output_rel,
        ]
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        completed = subprocess.run(
            command,
            cwd=REPO,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        emitted = output_path.read_bytes() if output_path.exists() else None
        needle = json.dumps(RENDERED_KEY).encode("utf-8")
        offset = emitted.find(needle) if emitted is not None else -1
        preserved_name = f"{location}-{initial}.prompt.txt"
        preserved_path = EVIDENCE / preserved_name
        if emitted is not None:
            preserved_path.write_bytes(emitted)
        start = max(0, offset - 100)
        end = min(len(emitted or b""), offset + len(needle) + 120)
        rows.append(
            {
                "location": location,
                "initialOutput": initial,
                "command": command,
                "exit": completed.returncode,
                "stdout": completed.stdout.decode(errors="replace"),
                "stderr": completed.stderr.decode(errors="replace"),
                "beforeExists": before is not None,
                "beforeSha256": sha(before) if before is not None else None,
                "afterExists": emitted is not None,
                "afterSha256": sha(emitted) if emitted is not None else None,
                "sentinelOverwritten": initial == "sentinel" and emitted != SENTINEL,
                "serializedExactKey": offset >= 0,
                "serializedOffset": offset,
                "serializedContextUtf8": (emitted or b"")[start:end].decode("utf-8", errors="replace"),
                "preservedPrompt": str(preserved_path),
                "packetSha256": sha(packet_bytes),
                "completenessSha256": sha(review_bytes),
            }
        )

    cleanup_error = None
    try:
        for location in ("packet", "completeness"):
            for initial in ("absent", "sentinel"):
                invoke(location, initial)
    finally:
        for root in (input_root, output_root):
            if root.exists():
                shutil.rmtree(root)
        try:
            if not prompts_existed and prompts.exists():
                prompts.rmdir()
            if not packets_existed and packets.exists():
                packets.rmdir()
        except OSError as exc:
            cleanup_error = str(exc)

    result = {
        "schemaVersion": 1,
        "recordType": "candidate5-blind-cli-admitted-example",
        "candidateHead": "d78e91e9f0d29eab7e9d838d4fc043ba73518cec",
        "identifier": IDENTIFIER,
        "renderedKey": RENDERED_KEY,
        "lexicalTokenPattern": r"(?<![A-Za-z0-9_])rootCauseId(?![A-Za-z0-9_])",
        "isLexicalToken": lexical is not None,
        "lexicalSpan": list(lexical.span()) if lexical else None,
        "sentinelSha256": sha(SENTINEL),
        "allExitedZero": all(row["exit"] == 0 for row in rows),
        "allSerializedExactKey": all(row["serializedExactKey"] for row in rows),
        "allSentinelsOverwritten": all(
            row["sentinelOverwritten"]
            for row in rows
            if row["initialOutput"] == "sentinel"
        ),
        "cleanupError": cleanup_error,
        "rows": rows,
    }
    result_path = EVIDENCE / "reproduction.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["allExitedZero"] and result["allSerializedExactKey"] and not cleanup_error else 1


if __name__ == "__main__":
    raise SystemExit(main())
