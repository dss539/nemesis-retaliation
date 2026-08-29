#!/usr/bin/env python3
"""Create the one-time external Git lock after the setup baseline commit."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/qa/implementation-readiness/correctness-audit"
LOCK = AUDIT / "audit-lock.json"
MANIFEST = AUDIT / "manifest.json"
PROGRESS = AUDIT / "progress.json"
LOCKED_FILES = [
    "docs/qa/implementation-readiness/correctness-audit/manifest.json",
    "docs/qa/implementation-readiness/correctness-audit/methodology.md",
    "docs/qa/implementation-readiness/correctness-audit/source-packet.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/packet-completeness-review.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/blind-derivation.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/audit-result.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-review-instructions.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-review-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/deepseek-v4-pro-0813-max-setup-review.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/glm-5.3-max-setup-review.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-review-disposition.md",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-instructions.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-manifest-summary.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-attempt-1-failure.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-test-summary.md",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-prompt-reduced.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-prompt-deepseek-short.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/deepseek-v4-pro-0813-max-setup-rereview.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/glm-5.3-max-setup-rereview.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-rereview-disposition.md",
    "scripts/advance_correctness_audit_progress.py",
    "scripts/build_correctness_audit_manifest.py",
    "scripts/create_correctness_audit_lock.py",
    "scripts/evaluate_correctness_audit.py",
    "scripts/run_ollama_audit_review.py",
    "scripts/test_correctness_audit_decision.py",
    "scripts/test_correctness_audit_mutations.py",
    "scripts/validate_correctness_audit.py",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=ROOT, text=text, capture_output=True, check=False)


def main() -> int:
    if LOCK.exists():
        raise SystemExit("refusing to overwrite existing audit-lock.json")
    baseline = git("rev-parse", "HEAD").stdout.strip()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
    if any(row["status"] != "pending-blind-derivation" for row in progress["units"]):
        raise SystemExit("audit lock must be created before the first derivation")
    locked: dict[str, str] = {}
    for relative in LOCKED_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"locked file missing: {relative}")
        current = path.read_bytes()
        shown = git("show", f"{baseline}:{relative}", text=False)
        if shown.returncode != 0:
            raise SystemExit(f"locked file is not in baseline commit: {relative}")
        if shown.stdout != current:
            raise SystemExit(f"locked file differs from baseline commit: {relative}")
        locked[relative] = hashlib.sha256(current).hexdigest()
    baseline_progress = git("show", f"{baseline}:{PROGRESS.relative_to(ROOT)}", text=False)
    if baseline_progress.returncode != 0 or baseline_progress.stdout != PROGRESS.read_bytes():
        raise SystemExit("initial progress differs from baseline commit")
    record = {
        "schemaVersion": 1,
        "recordType": "stage-1-correctness-audit-git-lock",
        "auditVersion": manifest["auditVersion"],
        "baselineCommit": baseline,
        "lockedStartingHead": manifest["lockedStartingHead"],
        "manifestSha256": sha(MANIFEST),
        "initialProgressSha256": sha(PROGRESS),
        "lockedFiles": locked,
        "changePolicy": "Any locked-file change requires a new audit version and explicit disposition of this baseline. Progress and result artifacts advance in later commits without changing locked harness bytes.",
    }
    LOCK.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"baselineCommit": baseline, "lockedFiles": len(locked), "lockPath": str(LOCK.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
