#!/usr/bin/env python3
"""Create the one-time external Git lock after the setup baseline commit."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs/qa/implementation-readiness/correctness-audit"
LOCK = AUDIT / "audit-lock.json"
MANIFEST = AUDIT / "manifest.json"
PROGRESS = AUDIT / "progress.json"
REQUIREMENTS = AUDIT / "requirements-audit.txt"
STATIC_LOCKED_FILES = [
    "docs/qa/implementation-readiness/correctness-audit/audit-lock-v1.json",
    "docs/qa/implementation-readiness/correctness-audit/baseline-v1-supersession.md",
    "docs/qa/implementation-readiness/correctness-audit/manifest.json",
    "docs/qa/implementation-readiness/correctness-audit/methodology.md",
    "docs/qa/implementation-readiness/correctness-audit/source-packet.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/packet-completeness-review.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/blind-derivation.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/comparison.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/audit-result.schema.json",
    "docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt",
    "docs/qa/implementation-readiness/correctness-audit/prompts/packet-completeness-instructions.txt",
    "docs/qa/implementation-readiness/correctness-audit/prompts/blind-derivation-instructions.txt",
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
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-v2-deepseek-controls-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-v2-focused-deepseek-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-v2-focused-glm-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-v2-glm-provenance-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-v2-micro-glm-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/deepseek-v4-pro-0813-max-setup-v2-controls.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/deepseek-v4-pro-0813-max-setup-v2-focused.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/glm-5.3-max-setup-v2-focused.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/glm-5.3-max-setup-v2-micro.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/glm-5.3-max-setup-v2-provenance.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/setup-v2-lock-creator-deepseek-prompt.txt",
    "docs/qa/implementation-readiness/correctness-audit/reviews/deepseek-v4-pro-0813-max-setup-v2-lock-creator.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/deepseek-v4-pro-0813-max-setup-v2-lock-creator-retry.json",
    "docs/qa/implementation-readiness/correctness-audit/reviews/prelock-review-candidate-1-disposition.md",
    "scripts/advance_correctness_audit_progress.py",
    "scripts/build_correctness_audit_prompt.py",
    "scripts/build_correctness_audit_manifest.py",
    "scripts/create_correctness_audit_lock.py",
    "scripts/evaluate_correctness_audit.py",
    "scripts/run_ollama_audit_review.py",
    "scripts/stage_correctness_audit_sources.py",
    "scripts/test_correctness_audit_decision.py",
    "scripts/test_correctness_audit_mutations.py",
    "scripts/test_correctness_audit_source_only_cli.py",
    "scripts/validate_correctness_audit.py",
]
LANE_OUTPUT_ROOTS = [
    "docs/qa/implementation-readiness/correctness-audit/packets",
    "docs/qa/implementation-readiness/correctness-audit/blind",
    "docs/qa/implementation-readiness/correctness-audit/comparisons",
    "docs/qa/implementation-readiness/correctness-audit/adjudications",
    "docs/qa/implementation-readiness/correctness-audit/reviews/raw",
]


def required_locked_files(*, root: Path = ROOT) -> list[str]:
    reviews_root = root / "docs/qa/implementation-readiness/correctness-audit/reviews"
    review_files = []
    if reviews_root.is_dir():
        for path in reviews_root.rglob("*"):
            if path == reviews_root / "raw" or (reviews_root / "raw") in path.parents:
                continue
            if path.is_file() or path.is_symlink():
                review_files.append(path.relative_to(root).as_posix())
    return sorted(set(STATIC_LOCKED_FILES) | set(review_files))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str, text: bool = True, root: Path = ROOT) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, text=text, capture_output=True, check=False)


def require_clean_worktree(*, root: Path = ROOT) -> None:
    status = git("status", "--porcelain=v2", "-z", "--untracked-files=all", root=root)
    if status.returncode != 0:
        raise SystemExit("cannot determine audit baseline worktree status")
    if status.stdout:
        raise SystemExit("audit lock requires a clean tracked, staged, and untracked worktree")


def historical_lane_files(starting: str, baseline: str, *, root: Path = ROOT) -> list[str]:
    return sorted(
        {
            row
            for row in git(
                "log",
                "--full-history",
                "--format=",
                "--name-only",
                f"{starting}..{baseline}",
                "--",
                *LANE_OUTPUT_ROOTS,
                root=root,
            ).stdout.splitlines()
            if row
        }
    )


def starting_head_failures(starting: str, baseline: str, *, root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    if git("cat-file", "-e", f"{starting}^{{commit}}", root=root).returncode != 0:
        failures.append("lockedStartingHead is not a Git commit")
        return failures
    if git("merge-base", "--is-ancestor", starting, baseline, root=root).returncode != 0:
        failures.append("lockedStartingHead is not an ancestor of baseline")
        return failures
    merges = git("rev-list", "--merges", f"{starting}..{baseline}", root=root)
    if merges.returncode != 0 or merges.stdout.split():
        failures.append("prebaseline audit history contains a merge commit")
    return failures


def prelock_validation_command(uv_executable: str) -> list[str]:
    return [
        uv_executable,
        "run",
        "--isolated",
        "--with-requirements",
        str(REQUIREMENTS),
        "python3",
        str(ROOT / "scripts/validate_correctness_audit.py"),
        "--prelock",
    ]


def main() -> int:
    if LOCK.exists():
        raise SystemExit("refusing to overwrite existing audit-lock.json")
    require_clean_worktree()
    baseline = git("rev-parse", "HEAD").stdout.strip()
    lane_files = sorted(
        str(path.relative_to(ROOT))
        for relative in LANE_OUTPUT_ROOTS
        for path in (ROOT / relative).rglob("*")
        if path.is_file() or path.is_symlink()
    )
    if lane_files:
        raise SystemExit(
            "audit lock requires empty lane-output roots; found: " + ", ".join(lane_files)
        )
    baseline_lane_files = git(
        "ls-tree",
        "-r",
        "--name-only",
        baseline,
        "--",
        *LANE_OUTPUT_ROOTS,
    ).stdout.splitlines()
    if baseline_lane_files:
        raise SystemExit(
            "audit baseline already contains lane artifacts: " + ", ".join(baseline_lane_files)
        )

    builder_check = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build_correctness_audit_manifest.py"), "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if builder_check.returncode != 0:
        raise SystemExit("manifest builder check failed:\n" + builder_check.stdout + builder_check.stderr)

    uv_executable = shutil.which("uv")
    if uv_executable is None:
        raise SystemExit("uv is required for isolated correctness-audit validation")
    prelock = subprocess.run(
        prelock_validation_command(uv_executable),
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if prelock.returncode != 0:
        raise SystemExit("clean pre-lock validation failed:\n" + prelock.stdout + prelock.stderr)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    starting = str(manifest.get("lockedStartingHead", ""))
    starting_failures = starting_head_failures(starting, baseline)
    if starting_failures:
        raise SystemExit("; ".join(starting_failures))
    lane_history = historical_lane_files(starting, baseline)
    if lane_history:
        raise SystemExit(
            "lane artifacts appeared in Git history before the v2 baseline: "
            + ", ".join(lane_history)
        )
    progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
    if any(row["status"] != "pending-blind-derivation" for row in progress["units"]):
        raise SystemExit("audit lock must be created before the first derivation")
    locked: dict[str, str] = {}
    for relative in required_locked_files():
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise SystemExit(f"locked file missing, non-regular, or symlinked: {relative}")
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
    require_clean_worktree()
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
