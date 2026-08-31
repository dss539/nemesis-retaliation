#!/usr/bin/env python3
"""Validate the frozen Stage 1 correctness-audit harness and artifacts.

Run through uv so JSON Schema 2020-12 and date-time formats are actually
validated:

    uv run --isolated --with-requirements \
      docs/qa/implementation-readiness/correctness-audit/requirements-audit.txt \
      python3 scripts/validate_correctness_audit.py
"""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by the documented runner
    raise SystemExit(
        "jsonschema is required; run with uv and requirements-audit.txt"
    ) from exc

from build_correctness_audit_prompt import (
    SOURCE_ONLY_FORBIDDEN_TOKENS,
    canonical_prompt_bytes,
)
from create_correctness_audit_lock import (
    historical_lane_files,
    required_locked_files,
    starting_head_failures,
)

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "docs/qa/implementation-readiness/correctness-audit"
MANIFEST_PATH = AUDIT_DIR / "manifest.json"
PROGRESS_PATH = AUDIT_DIR / "progress.json"
LOCK_PATH = AUDIT_DIR / "audit-lock.json"
REPORT_PATH = AUDIT_DIR / "validation.json"
SCHEMA_PATHS = {
    "packet": AUDIT_DIR / "source-packet.schema.json",
    "completeness": AUDIT_DIR / "packet-completeness-review.schema.json",
    "blind": AUDIT_DIR / "blind-derivation.schema.json",
    "comparison": AUDIT_DIR / "comparison.schema.json",
    "result": AUDIT_DIR / "audit-result.schema.json",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_FAMILIES = {
    "room": 5,
    "intruder-help": 4,
    "event": 4,
    "exploration": 3,
    "robot": 2,
    "intruder-attack": 2,
    "queen-health": 2,
    "serious-wound": 2,
    "green-item": 2,
    "red-item": 2,
    "yellow-item": 2,
    "action-card": 12,
    "objective-mission": 6,
    "equipment-starting": 8,
}
EXPECTED_UNIVERSES = {
    "room": 25,
    "intruder-help": 18,
    "event": 20,
    "exploration": 12,
    "robot": 6,
    "intruder-attack": 20,
    "queen-health": 10,
    "serious-wound": 9,
    "green-item": 8,
    "red-item": 7,
    "yellow-item": 4,
    "action-card": 60,
    "objective-mission": 27,
    "equipment-starting": 37,
}
EXPECTED_THRESHOLDS = {
    "criticalErrors": 0,
    "inventedAuthorityOverrides": 0,
    "hiddenDefaults": 0,
    "recurringDefectPatterns": 0,
    "maximumIsolatedMaterialErrorsInComponentSample": 2,
    "deterministicCleanMatchReviewSample": {
        "total": 23,
        "perUnitClass": {
            "concise-rule-record": 6,
            "base-applicable-faq-unit": 3,
        },
        "perComponentFamily": 1,
    },
    "sourceBlockedUnitsMustBeEnumerated": True,
    "readinessClaimMustEnumerateUnauditedComponentEffects": True,
}
STATUS_COUNT_KEYS = {
    "pending-blind-derivation": "pendingBlindDerivation",
    "blind-derived": "blindDerived",
    "compared": "compared",
    "accepted": "accepted",
    "material-error": "materialErrors",
    "critical-error": "criticalErrors",
    "source-blocked": "sourceBlocked",
}
ALLOWED_SOURCE_PREFIXES = (
    "docs/rulebooks/",
    "docs/rules/source-extraction/",
    "assets/tts-mod/extract/",
)
SEMANTIC_PROJECTION_PATHS = {
    "docs/rules/semantics/pilots.json",
    "docs/rules/semantics/review-gates.json",
    "docs/rules/semantics/contradictions.json",
}
REQUIRED_BEHAVIOR_PROJECTION_PATH = "docs/rules/semantics/pilots.json"
FORBIDDEN_PROMPT_TOKENS = SOURCE_ONLY_FORBIDDEN_TOKENS
TRACE_KEYS = {"thinking", "reasoningtrace", "chainofthought", "chain_of_thought"}


class DuplicateKeyError(ValueError):
    pass


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def strict_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def png_validation_failures(path: Path) -> list[str]:
    """Return structural failures for a rendered PNG evidence artifact."""
    try:
        data = path.read_bytes()
    except OSError as exc:
        return [f"cannot read PNG: {exc}"]
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        return ["missing PNG signature"]
    position = 8
    chunk_index = 0
    saw_ihdr = False
    saw_idat = False
    saw_iend = False
    width = height = 0
    failures: list[str] = []
    while position < len(data):
        if position + 12 > len(data):
            failures.append("truncated PNG chunk")
            break
        length = int.from_bytes(data[position : position + 4], "big")
        chunk_type = data[position + 4 : position + 8]
        end = position + 12 + length
        if end > len(data):
            failures.append("PNG chunk length exceeds file")
            break
        chunk_data = data[position + 8 : position + 8 + length]
        stored_crc = int.from_bytes(data[position + 8 + length : end], "big")
        calculated_crc = binascii.crc32(chunk_type + chunk_data) & 0xFFFFFFFF
        if stored_crc != calculated_crc:
            failures.append(f"PNG chunk {chunk_index} CRC mismatch")
        if chunk_index == 0:
            if chunk_type != b"IHDR" or length != 13:
                failures.append("first PNG chunk is not a 13-byte IHDR")
            else:
                saw_ihdr = True
                width = int.from_bytes(chunk_data[0:4], "big")
                height = int.from_bytes(chunk_data[4:8], "big")
        if chunk_type == b"IDAT":
            saw_idat = True
        if chunk_type == b"IEND":
            saw_iend = True
            if length != 0:
                failures.append("PNG IEND chunk is nonempty")
            if end != len(data):
                failures.append("PNG has trailing bytes after IEND")
            position = end
            break
        position = end
        chunk_index += 1
    if not saw_ihdr:
        failures.append("PNG lacks IHDR")
    if width < 32 or height < 32:
        failures.append("PNG dimensions are below 32x32")
    if not saw_idat:
        failures.append("PNG lacks IDAT")
    if not saw_iend:
        failures.append("PNG lacks IEND")
    return failures


@lru_cache(maxsize=128)
def rendered_pdf_page_sha256(source_path: str, source_sha256: str, page_index: int, dpi: int) -> str:
    source = ROOT / source_path
    if sha256_path(source) != source_sha256:
        raise ValueError("PDF source hash drift before rendering")
    with tempfile.TemporaryDirectory(prefix="correctness-audit-pdf-render-") as directory:
        prefix = Path(directory) / "page"
        result = subprocess.run(
            [
                "pdftoppm",
                "-f",
                str(page_index),
                "-l",
                str(page_index),
                "-singlefile",
                "-png",
                "-r",
                str(dpi),
                str(source),
                str(prefix),
            ],
            cwd=ROOT,
            capture_output=True,
            check=False,
        )
        rendered = prefix.with_suffix(".png")
        if result.returncode != 0 or not rendered.is_file():
            raise ValueError("deterministic PDF page render failed")
        return sha256_path(rendered)


def add(failures: list[str], condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def repo_path(value: Any, failures: list[str], label: str, parent: Path = ROOT) -> Path | None:
    if not isinstance(value, str) or not value:
        failures.append(f"{label}: missing path")
        return None
    lexical = PurePosixPath(value)
    if (
        "\\" in value
        or lexical.is_absolute()
        or lexical.as_posix() != value
        or any(part in {".", ".."} for part in lexical.parts)
    ):
        failures.append(f"{label}: path is not a canonical repository-relative POSIX path")
        return None
    path = ROOT.joinpath(*lexical.parts)
    try:
        resolved = path.resolve(strict=False)
        resolved.relative_to(parent.resolve())
    except (OSError, ValueError):
        failures.append(f"{label}: path escapes {parent.relative_to(ROOT) if parent != ROOT else 'repository'}")
        return None
    current = ROOT
    for part in lexical.parts:
        current = current / part
        if current.is_symlink():
            failures.append(f"{label}: symlink path component is forbidden")
            return None
    return path


def checked_file(
    value: Any,
    expected_hash: Any,
    failures: list[str],
    label: str,
    parent: Path = ROOT,
) -> Path | None:
    path = repo_path(value, failures, label, parent)
    if path is None:
        return None
    add(failures, path.is_file(), f"{label}: file missing")
    add(failures, isinstance(expected_hash, str) and bool(HEX64.fullmatch(expected_hash)), f"{label}: invalid SHA-256")
    if path.is_file() and isinstance(expected_hash, str):
        add(failures, sha256_path(path) == expected_hash, f"{label}: SHA-256 mismatch")
    return path


def schema_validators(failures: list[str]) -> dict[str, Draft202012Validator]:
    validators: dict[str, Draft202012Validator] = {}
    for name, path in SCHEMA_PATHS.items():
        try:
            schema = strict_load(path)
            Draft202012Validator.check_schema(schema)
            validators[name] = Draft202012Validator(schema, format_checker=FormatChecker())
        except Exception as exc:
            failures.append(f"{name} schema invalid: {exc}")
    return validators


def apply_schema(
    name: str,
    value: Any,
    validators: dict[str, Draft202012Validator],
    failures: list[str],
    label: str,
) -> bool:
    validator = validators.get(name)
    if validator is None:
        return False
    errors = sorted(validator.iter_errors(value), key=lambda err: list(err.absolute_path))
    for err in errors:
        location = "/".join(str(part) for part in err.absolute_path) or "<root>"
        failures.append(f"{label}: schema {location}: {err.message}")
    return not errors


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=root, capture_output=True)


def commit_changed_paths(root: Path, commit: str) -> set[str] | None:
    changed = git_bytes(
        root,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "-r",
        "-z",
        commit,
    )
    if changed.returncode != 0:
        return None
    return {
        item.decode("utf-8")
        for item in changed.stdout.split(b"\0")
        if item
    }


def merge_commits_after(root: Path, commit: str) -> list[str]:
    result = git_bytes(root, "rev-list", "--merges", f"{commit}..HEAD")
    if result.returncode != 0:
        return ["<git-error>"]
    return result.stdout.decode("ascii", errors="replace").split()


def commits_touching_path_after(root: Path, commit: str, relative: str) -> list[str]:
    result = git_bytes(root, "rev-list", "--full-history", f"{commit}..HEAD", "--", relative)
    if result.returncode != 0:
        return ["<git-error>"]
    return result.stdout.decode("ascii", errors="replace").split()


def validate_artifact_seal(
    record: dict[str, Any],
    artifact_path: Path | None,
    failures: list[str],
    label: str,
    root: Path = ROOT,
) -> str | None:
    """Derive and verify the immutable commit that seals a lane artifact.

    `sealedAtGitHead` is deliberately the pre-seal HEAD. The artifact must be
    introduced with its exact current bytes in the next non-merge first-parent
    commit. This avoids the impossible self-reference of embedding a commit ID
    inside the file whose bytes determine that same commit ID.
    """
    if artifact_path is None:
        return None
    try:
        relative = artifact_path.resolve(strict=False).relative_to(root.resolve()).as_posix()
    except ValueError:
        failures.append(f"{label}: artifact path escapes repository")
        return None

    preseal = record.get("sealedAtGitHead")
    if not isinstance(preseal, str) or not HEX40.fullmatch(preseal):
        failures.append(f"{label}: invalid pre-seal Git HEAD")
        return None
    if git_bytes(root, "cat-file", "-e", f"{preseal}^{{commit}}").returncode != 0:
        failures.append(f"{label}: seal Git HEAD does not exist")
        return None
    if git_bytes(root, "merge-base", "--is-ancestor", preseal, "HEAD").returncode != 0:
        failures.append(f"{label}: pre-seal Git HEAD is not an ancestor of current HEAD")
        return None

    descendants = git_bytes(root, "rev-list", "--first-parent", "--reverse", f"{preseal}..HEAD")
    commits = descendants.stdout.decode("ascii", errors="replace").split() if descendants.returncode == 0 else []
    if not commits:
        failures.append(f"{label}: artifact was not committed directly after its declared pre-seal HEAD")
        return None
    seal_commit = commits[0]
    parent_line = git_bytes(root, "rev-list", "--parents", "-n", "1", seal_commit)
    parents = parent_line.stdout.decode("ascii", errors="replace").split() if parent_line.returncode == 0 else []
    if len(parents) != 2 or parents[1] != preseal:
        failures.append(f"{label}: derived seal commit is not a direct non-merge child of pre-seal HEAD")
        return None

    existed_before = git_bytes(root, "cat-file", "-e", f"{preseal}:{relative}").returncode == 0
    if existed_before:
        failures.append(f"{label}: artifact path already existed at pre-seal HEAD; use a new versioned path")
        return None
    sealed = git_bytes(root, "show", f"{seal_commit}:{relative}")
    if sealed.returncode != 0:
        failures.append(f"{label}: artifact was not committed directly after its declared pre-seal HEAD")
        return None
    if not artifact_path.is_file():
        failures.append(f"{label}: current artifact file missing")
        return None
    if sealed.stdout != artifact_path.read_bytes():
        failures.append(f"{label}: current artifact bytes differ from its derived seal commit")
        return None
    head = git_bytes(root, "show", f"HEAD:{relative}")
    add(failures, head.returncode == 0, f"{label}: artifact is absent from current HEAD")
    if head.returncode == 0:
        add(failures, head.stdout == sealed.stdout, f"{label}: current HEAD bytes differ from its derived seal commit")
    add(
        failures,
        not commits_touching_path_after(root, seal_commit, relative),
        f"{label}: artifact path changed in Git history after its derived seal commit",
    )
    return seal_commit


def validate_file_at_commit(
    path: Path | None,
    commit: str | None,
    failures: list[str],
    label: str,
    root: Path = ROOT,
) -> None:
    if path is None or commit is None:
        return
    try:
        relative = path.resolve(strict=False).relative_to(root.resolve()).as_posix()
    except ValueError:
        failures.append(f"{label}: path escapes repository")
        return
    sealed = git_bytes(root, "show", f"{commit}:{relative}")
    add(failures, sealed.returncode == 0, f"{label}: file absent from required lane commit")
    if sealed.returncode == 0 and path.is_file():
        add(failures, sealed.stdout == path.read_bytes(), f"{label}: current bytes differ from required lane commit")
        head = git_bytes(root, "show", f"HEAD:{relative}")
        add(failures, head.returncode == 0, f"{label}: file absent from current HEAD")
        if head.returncode == 0:
            add(failures, head.stdout == sealed.stdout, f"{label}: current HEAD bytes differ from required lane commit")
        add(
            failures,
            not commits_touching_path_after(root, commit, relative),
            f"{label}: path changed in Git history after required lane commit",
        )


def require_lane_preseal(
    record: dict[str, Any],
    expected_preseal: str | None,
    failures: list[str],
    label: str,
) -> None:
    if expected_preseal is not None:
        add(
            failures,
            record.get("sealedAtGitHead") == expected_preseal,
            f"{label}: pre-seal HEAD does not equal the preceding lane commit",
        )


def require_preseal_at_or_after(
    record: dict[str, Any],
    minimum_commit: str | None,
    failures: list[str],
    label: str,
    root: Path = ROOT,
) -> None:
    if minimum_commit is None:
        return
    preseal = record.get("sealedAtGitHead")
    if not isinstance(preseal, str) or not HEX40.fullmatch(preseal):
        return
    add(
        failures,
        git_bytes(root, "merge-base", "--is-ancestor", minimum_commit, preseal).returncode == 0,
        f"{label}: pre-seal HEAD predates the audit-lock commit",
    )


def require_preseal_after_all(
    record: dict[str, Any],
    required_commits: tuple[str, ...],
    failures: list[str],
    label: str,
    root: Path = ROOT,
) -> None:
    preseal = record.get("sealedAtGitHead")
    if not isinstance(preseal, str) or not HEX40.fullmatch(preseal):
        return
    for required_commit in required_commits:
        add(
            failures,
            git_bytes(root, "merge-base", "--is-ancestor", required_commit, preseal).returncode == 0,
            f"{label}: adjudication predates a Stage 1 comparison commit",
        )


def validate_lock(manifest: dict[str, Any], failures: list[str], require_lock: bool) -> str | None:
    if not LOCK_PATH.is_file():
        add(failures, not require_lock, "audit-lock.json is required after setup checkpoint")
        return
    try:
        lock = strict_load(LOCK_PATH)
    except Exception as exc:
        failures.append(f"audit lock parse: {exc}")
        return
    expected_keys = {
        "schemaVersion",
        "recordType",
        "auditVersion",
        "baselineCommit",
        "lockedStartingHead",
        "manifestSha256",
        "initialProgressSha256",
        "lockedFiles",
        "changePolicy",
    }
    add(failures, set(lock) == expected_keys, "audit lock top-level keys drift")
    add(failures, lock.get("schemaVersion") == 1, "audit lock schemaVersion")
    add(failures, lock.get("recordType") == "stage-1-correctness-audit-git-lock", "audit lock recordType")
    add(failures, lock.get("auditVersion") == manifest.get("auditVersion"), "audit lock version mismatch")
    add(failures, lock.get("lockedStartingHead") == manifest.get("lockedStartingHead"), "audit lock starting HEAD mismatch")
    add(failures, lock.get("manifestSha256") == sha256_path(MANIFEST_PATH), "audit lock manifest hash mismatch")
    baseline = lock.get("baselineCommit")
    if not isinstance(baseline, str) or not HEX40.fullmatch(baseline):
        failures.append("audit lock baseline commit invalid")
        return
    add(failures, git("cat-file", "-e", f"{baseline}^{{commit}}").returncode == 0, "audit lock baseline commit missing")
    add(failures, git("merge-base", "--is-ancestor", baseline, "HEAD").returncode == 0, "audit baseline is not an ancestor of HEAD")
    add(
        failures,
        not merge_commits_after(ROOT, baseline),
        "audit history contains a merge commit after baseline",
    )
    lock_commit = validate_artifact_seal(
        {"sealedAtGitHead": baseline},
        LOCK_PATH,
        failures,
        "audit lock",
    )
    if lock_commit is not None:
        lock_relative = str(LOCK_PATH.relative_to(ROOT))
        changed_paths = commit_changed_paths(ROOT, lock_commit)
        add(
            failures,
            changed_paths == {lock_relative},
            "audit lock commit must change exactly audit-lock.json",
        )
    starting = str(lock.get("lockedStartingHead", ""))
    add(failures, bool(HEX40.fullmatch(starting)), "lockedStartingHead invalid")
    if HEX40.fullmatch(starting):
        for starting_failure in starting_head_failures(starting, baseline):
            failures.append(f"audit lock: {starting_failure}")
        add(failures, git("merge-base", "--is-ancestor", starting, baseline).returncode == 0, "starting HEAD is not an ancestor of baseline")
        add(
            failures,
            not historical_lane_files(starting, baseline),
            "lane artifacts appeared in Git history before the v2 baseline",
        )
    tracked = git("ls-files", "--error-unmatch", str(LOCK_PATH.relative_to(ROOT)))
    add(failures, tracked.returncode == 0, "audit lock is not tracked")
    add(failures, git("diff", "--quiet", "HEAD", "--", str(LOCK_PATH.relative_to(ROOT))).returncode == 0, "audit lock has uncommitted drift")

    locked_files = lock.get("lockedFiles", {})
    add(failures, isinstance(locked_files, dict) and bool(locked_files), "audit lock files absent")
    if isinstance(locked_files, dict):
        add(
            failures,
            set(locked_files) == set(required_locked_files()),
            "audit lock lockedFiles set differs from the canonical creator list",
        )
        for relative, expected_hash in locked_files.items():
            current = ROOT / relative
            add(failures, current.is_file(), f"locked file missing: {relative}")
            if current.is_file():
                add(failures, sha256_path(current) == expected_hash, f"locked file drift: {relative}")
            shown = git_bytes(ROOT, "show", f"{baseline}:{relative}")
            add(failures, shown.returncode == 0, f"locked file absent from baseline: {relative}")
            if shown.returncode == 0:
                add(failures, sha256_bytes(shown.stdout) == expected_hash, f"baseline hash mismatch: {relative}")
            add(
                failures,
                not commits_touching_path_after(ROOT, baseline, relative),
                f"locked file changed in Git history after baseline: {relative}",
            )

    frozen_baseline_hashes: dict[str, str] = {}
    for section in ("frozenSemanticHashes", "frozenConciseRuleHashes", "selectionInputHashes"):
        mapping = manifest.get(section, {})
        if not isinstance(mapping, dict):
            continue
        for relative, expected_hash in mapping.items():
            if not isinstance(relative, str) or not isinstance(expected_hash, str):
                continue
            prior_hash = frozen_baseline_hashes.get(relative)
            add(
                failures,
                prior_hash is None or prior_hash == expected_hash,
                f"frozen manifest maps disagree for path: {relative}",
            )
            frozen_baseline_hashes[relative] = expected_hash
    for relative, expected_hash in frozen_baseline_hashes.items():
        tracked = git("ls-files", "--error-unmatch", relative).returncode == 0
        if not tracked:
            add(
                failures,
                is_allowed_source(relative),
                f"untracked frozen path is not an allowed source input: {relative}",
            )
            current = ROOT / relative
            add(failures, current.is_file(), f"local frozen source missing: {relative}")
            if current.is_file():
                add(
                    failures,
                    sha256_path(current) == expected_hash,
                    f"local frozen source hash mismatch: {relative}",
                )
            continue
        shown = git_bytes(ROOT, "show", f"{baseline}:{relative}")
        add(failures, shown.returncode == 0, f"frozen file absent from baseline: {relative}")
        if shown.returncode == 0:
            add(
                failures,
                sha256_bytes(shown.stdout) == expected_hash,
                f"frozen baseline hash mismatch: {relative}",
            )
        add(
            failures,
            not commits_touching_path_after(ROOT, baseline, relative),
            f"frozen file changed in Git history after baseline: {relative}",
        )
    shown_progress = git_bytes(ROOT, "show", f"{baseline}:{PROGRESS_PATH.relative_to(ROOT)}")
    add(failures, shown_progress.returncode == 0, "initial progress absent from baseline")
    if shown_progress.returncode == 0:
        add(
            failures,
            sha256_bytes(shown_progress.stdout) == lock.get("initialProgressSha256"),
            "initial progress baseline hash mismatch",
        )
    return lock_commit


def contains_trace_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(str(key).lower() in TRACE_KEYS or contains_trace_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(contains_trace_key(child) for child in value)
    return False


def reviewer_identity(reviewer: Any) -> tuple[Any, ...]:
    if not isinstance(reviewer, dict):
        return (None,)
    kind = reviewer.get("kind")
    if kind == "model-assisted":
        response_model = reviewer.get("responseModel")
        return (
            kind,
            reviewer.get("provider"),
            response_model if isinstance(response_model, str) and response_model else None,
        )
    return (kind, reviewer.get("reviewerId"))

MODEL_RESPONSE_KEYS = {
    "schemaVersion",
    "recordType",
    "provider",
    "requestedModel",
    "responseModel",
    "requestedReasoning",
    "stream",
    "format",
    "promptPath",
    "promptSha256",
    "responseCreatedAt",
    "done",
    "doneReason",
    "review",
    "thinkingRetained",
}


def valid_model_response_envelope(body: Any, failures: list[str], label: str) -> bool:
    valid = True
    checks = (
        (isinstance(body, dict), "response envelope is not an object"),
        (isinstance(body, dict) and set(body) == MODEL_RESPONSE_KEYS, "response envelope keys drift"),
        (isinstance(body, dict) and type(body.get("schemaVersion")) is int and body.get("schemaVersion") == 1, "response envelope schemaVersion drift"),
        (isinstance(body, dict) and body.get("recordType") == "ollama-cloud-audit-review", "response envelope recordType drift"),
        (isinstance(body, dict) and body.get("stream") is False, "response envelope stream drift"),
        (isinstance(body, dict) and body.get("format") == "json", "response envelope format drift"),
        (isinstance(body, dict) and isinstance(body.get("responseCreatedAt"), str) and bool(body.get("responseCreatedAt")), "response envelope timestamp missing"),
        (isinstance(body, dict) and body.get("done") is True, "response envelope did not complete"),
        (isinstance(body, dict) and isinstance(body.get("doneReason"), str) and bool(body.get("doneReason")), "response envelope doneReason missing"),
        (isinstance(body, dict) and isinstance(body.get("review"), dict), "response envelope review missing"),
        (isinstance(body, dict) and body.get("thinkingRetained") is False, "response envelope retained thinking"),
    )
    for condition, message in checks:
        if not condition:
            failures.append(f"{label}: {message}")
            valid = False
    return valid


def validate_reviewer(
    reviewer: Any,
    failures: list[str],
    label: str,
    *,
    response_commit: str | None = None,
    prompt_commit: str | None = None,
    enforce_seals: bool = True,
) -> dict[str, Any] | None:
    if not isinstance(reviewer, dict):
        failures.append(f"{label}: reviewer missing")
        return None
    if reviewer.get("kind") == "model-assisted":
        add(
            failures,
            isinstance(reviewer.get("provider"), str) and bool(reviewer.get("provider")),
            f"{label}: model provider is empty",
        )
        add(
            failures,
            isinstance(reviewer.get("responseModel"), str) and bool(reviewer.get("responseModel")),
            f"{label}: resolved response model is empty",
        )
    has_prompt_path = isinstance(reviewer.get("promptPath"), str) and bool(reviewer.get("promptPath"))
    has_prompt_hash = isinstance(reviewer.get("promptSha256"), str) and bool(reviewer.get("promptSha256"))
    has_response_path = isinstance(reviewer.get("responsePath"), str) and bool(reviewer.get("responsePath"))
    has_response_hash = isinstance(reviewer.get("responseSha256"), str) and bool(reviewer.get("responseSha256"))
    add(failures, has_prompt_path == has_prompt_hash, f"{label}: prompt path/hash must be paired")
    add(failures, has_response_path == has_response_hash, f"{label}: response path/hash must be paired")
    prompt = checked_file(
        reviewer.get("promptPath"),
        reviewer.get("promptSha256"),
        failures,
        f"{label} prompt",
        AUDIT_DIR,
    )
    response = checked_file(
        reviewer.get("responsePath"),
        reviewer.get("responseSha256"),
        failures,
        f"{label} response",
        AUDIT_DIR / "reviews" / "raw",
    )
    if prompt is not None and prompt.is_file():
        add(failures, prompt.stat().st_size > 0, f"{label}: reviewer prompt is empty")
    if response is not None and response.is_file():
        add(failures, response.stat().st_size > 0, f"{label}: reviewer response is empty")
    if enforce_seals:
        validate_file_at_commit(prompt, prompt_commit, failures, f"{label} prompt")
        validate_file_at_commit(response, response_commit, failures, f"{label} response")
    if response and response.is_file():
        try:
            body = strict_load(response)
            add(failures, not contains_trace_key(body), f"{label}: retained provider reasoning trace")
            if reviewer.get("kind") != "model-assisted":
                add(failures, isinstance(body, dict), f"{label}: reviewer response is not an object")
                return body if isinstance(body, dict) else None
            if not valid_model_response_envelope(body, failures, label):
                return None
            if reviewer.get("provider") == "ollama-cloud":
                add(failures, reviewer.get("requestedReasoning") == "max", f"{label}: Ollama review was not max reasoning")
            add(failures, body.get("recordType") == "ollama-cloud-audit-review", f"{label}: response is not a successful review envelope")
            add(failures, body.get("provider") == reviewer.get("provider"), f"{label}: provider provenance mismatch")
            add(failures, body.get("requestedModel") == reviewer.get("requestedModel"), f"{label}: requested-model provenance mismatch")
            add(failures, body.get("responseModel") == reviewer.get("responseModel"), f"{label}: response-model provenance mismatch")
            add(failures, body.get("requestedReasoning") == reviewer.get("requestedReasoning"), f"{label}: reasoning provenance mismatch")
            add(failures, body.get("thinkingRetained") is False, f"{label}: response did not attest to discarded reasoning")
            provenance_prompt = checked_file(
                body.get("promptPath"),
                body.get("promptSha256"),
                failures,
                f"{label} prompt provenance",
                AUDIT_DIR,
            )
            if enforce_seals:
                validate_file_at_commit(provenance_prompt, prompt_commit, failures, f"{label} prompt provenance")
            add(failures, body.get("promptPath") == reviewer.get("promptPath"), f"{label}: reviewer prompt path mismatch")
            add(failures, body.get("promptSha256") == reviewer.get("promptSha256"), f"{label}: reviewer prompt hash mismatch")
            review_payload = body.get("review")
            add(failures, isinstance(review_payload, dict), f"{label}: model response review payload missing")
            return review_payload if isinstance(review_payload, dict) else None
        except Exception as exc:
            failures.append(f"{label}: response parse: {exc}")
    return None


def validate_canonical_prompt(
    mode: str,
    prompt_path: Path | None,
    packet_path: Path | None,
    completeness_path: Path | None,
    failures: list[str],
    label: str,
) -> None:
    if prompt_path is None or packet_path is None:
        return
    try:
        expected = canonical_prompt_bytes(mode, packet_path, completeness_path)
    except Exception as exc:
        failures.append(f"{label}: canonical prompt build failed: {exc}")
        return
    add(
        failures,
        prompt_path.read_bytes() == expected,
        f"{label}: prompt is not canonical for sealed payloads",
    )


def is_allowed_source(relative: str) -> bool:
    failures: list[str] = []
    path = repo_path(relative, failures, "source allowlist")
    if path is None or failures:
        return False
    resolved = path.resolve(strict=False)
    for prefix in ALLOWED_SOURCE_PREFIXES:
        allowed_root = (ROOT / prefix).resolve()
        try:
            resolved.relative_to(allowed_root)
            return True
        except ValueError:
            continue
    return False


def validate_packet(
    path: Path,
    validators: dict[str, Draft202012Validator],
    manifest_units: dict[str, dict[str, Any]],
    failures: list[str],
    enforce_seals: bool = True,
    minimum_preseal: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        packet = strict_load(path)
    except Exception as exc:
        failures.append(f"packet parse {path}: {exc}")
        return None, None
    if not apply_schema("packet", packet, validators, failures, str(path.relative_to(ROOT))):
        return None, None
    packet_commit = (
        validate_artifact_seal(packet, path, failures, f"{path}: packet")
        if enforce_seals
        else None
    )
    if enforce_seals:
        require_preseal_at_or_after(packet, minimum_preseal, failures, f"{path}: packet")
    packet_ids = packet.get("auditUnitIds", [])
    add(failures, set(packet_ids).issubset(set(manifest_units)), f"{path}: unknown audit unit")
    covered_unit_ids: set[str] = set()
    evidence_rows: list[dict[str, Any]] = []
    evidence_ids = [
        row.get("evidenceId")
        for row in packet.get("evidence", [])
        if isinstance(row, dict)
    ]
    add(
        failures,
        len(evidence_ids) == len(set(evidence_ids)),
        f"{path}: duplicate packet evidence ID",
    )
    for index, row in enumerate(packet.get("sourceDocuments", [])):
        relative = row.get("sourcePath", "") if isinstance(row, dict) else ""
        add(failures, is_allowed_source(relative), f"{path}: disallowed source document {relative}")
        checked_file(relative, row.get("sourceSha256") if isinstance(row, dict) else None, failures, f"{path}: sourceDocument[{index}]")
    for index, row in enumerate(packet.get("evidence", [])):
        if not isinstance(row, dict):
            continue
        evidence_rows.append(row)
        row_unit_ids = set(row.get("auditUnitIds", []))
        add(failures, row_unit_ids.issubset(set(packet_ids)), f"{path}: evidence[{index}] references a unit outside the packet")
        covered_unit_ids.update(row_unit_ids)
        relative = row.get("sourcePath", "")
        add(failures, is_allowed_source(relative), f"{path}: disallowed evidence source {relative}")
        checked_file(relative, row.get("sourceSha256"), failures, f"{path}: evidence[{index}]")
        visual = row.get("visualEvidencePath")
        pdf_exact_text = isinstance(row.get("exactText"), str) and relative.lower().endswith(".pdf")
        if pdf_exact_text:
            add(failures, visual is not None, f"{path}: PDF exactText evidence[{index}] lacks rendered visual evidence")
            add(
                failures,
                isinstance(row.get("pdfPageIndex"), int) and row.get("pdfPageIndex", 0) >= 1,
                f"{path}: PDF exactText evidence[{index}] lacks a page index",
            )
            add(
                failures,
                row.get("renderDpi") == 160,
                f"{path}: PDF exactText evidence[{index}] must use the locked 160 DPI render",
            )
        else:
            add(
                failures,
                row.get("pdfPageIndex") is None and row.get("renderDpi") is None,
                f"{path}: non-PDF evidence[{index}] has PDF render metadata",
            )
        if visual is not None:
            visual_path = checked_file(
                visual,
                row.get("visualEvidenceSha256"),
                failures,
                f"{path}: visualEvidence[{index}]",
                AUDIT_DIR / "packets",
            )
            if visual_path is not None and visual_path.is_file():
                add(
                    failures,
                    visual_path.suffix.lower() == ".png",
                    f"{path}: visualEvidence[{index}] is not a PNG",
                )
                for png_failure in png_validation_failures(visual_path):
                    failures.append(f"{path}: visualEvidence[{index}] {png_failure}")
                if pdf_exact_text and enforce_seals:
                    try:
                        expected_render_hash = rendered_pdf_page_sha256(
                            relative,
                            row.get("sourceSha256"),
                            row.get("pdfPageIndex"),
                            row.get("renderDpi"),
                        )
                        add(
                            failures,
                            sha256_path(visual_path) == expected_render_hash,
                            f"{path}: visualEvidence[{index}] is not the deterministic cited PDF page render",
                        )
                    except Exception as exc:
                        failures.append(f"{path}: visualEvidence[{index}] PDF render verification failed: {exc}")
            if enforce_seals:
                validate_file_at_commit(
                    visual_path,
                    packet_commit,
                    failures,
                    f"{path}: visualEvidence[{index}]",
                )
    for index, row in enumerate(packet.get("searchCoverage", {}).get("searchedSourcePaths", [])):
        if not isinstance(row, dict):
            continue
        relative = row.get("sourcePath", "")
        add(failures, is_allowed_source(relative), f"{path}: disallowed searched source {relative}")
        checked_file(relative, row.get("sourceSha256"), failures, f"{path}: searchedSource[{index}]")
    add(failures, packet.get("sourceOnlyAttestation") is True, f"{path}: no source-only attestation")
    add(failures, packet.get("forbiddenDownstreamSourcesIncluded") == [], f"{path}: downstream source included")
    add(failures, covered_unit_ids == set(packet_ids), f"{path}: packet unit lacks direct evidence")
    for unit_id in packet_ids:
        unit = manifest_units.get(unit_id, {})
        expected_path = unit.get("sourcePath") if isinstance(unit, dict) else None
        expected_sha256 = unit.get("sourceSha256") if isinstance(unit, dict) else None
        if not isinstance(expected_path, str) or not isinstance(expected_sha256, str):
            continue
        add(
            failures,
            any(
                unit_id in row.get("auditUnitIds", [])
                and row.get("sourcePath") == expected_path
                and row.get("sourceSha256") == expected_sha256
                for row in evidence_rows
            ),
            f"{path}: {unit_id} lacks manifest-bound source evidence",
        )
    return packet, packet_commit


def parse_time(value: Any, failures: list[str], label: str) -> datetime | None:
    if not isinstance(value, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z",
        value,
    ):
        failures.append(f"{label}: invalid UTC date-time")
        return None
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except Exception:
        failures.append(f"{label}: invalid UTC date-time")
        return None
    if parsed.tzinfo != timezone.utc:
        failures.append(f"{label}: date-time is not UTC")
        return None
    return parsed


PROGRESS_TRANSITIONS = {
    "pending-blind-derivation": {"blind-derived"},
    "blind-derived": {"compared"},
    "compared": {"accepted", "material-error", "critical-error", "source-blocked"},
    "accepted": set(),
    "material-error": set(),
    "critical-error": set(),
    "source-blocked": set(),
}
PROGRESS_TOP_KEYS = {
    "schemaVersion",
    "recordType",
    "manifestPath",
    "manifestSha256",
    "counts",
    "units",
}
PROGRESS_ROW_KEYS = {
    "auditUnitId",
    "status",
    "blindPath",
    "blindSha256",
    "blindUnitResultId",
    "comparisonPath",
    "comparisonSha256",
    "resultPath",
    "resultSha256",
    "lastUpdatedUtc",
}


def strict_json_bytes(data: bytes) -> dict[str, Any]:
    return json.loads(data.decode("utf-8"), object_pairs_hook=strict_pairs)


def canonical_progress_bytes(progress: dict[str, Any]) -> bytes:
    return (
        json.dumps(progress, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")


def committed_transition_artifact_failures(
    row: dict[str, Any],
    status: str,
    transition_commit: str,
    root: Path,
    label: str,
) -> list[str]:
    failures: list[str] = []
    if status == "blind-derived":
        path_key, hash_key = "blindPath", "blindSha256"
    elif status == "compared":
        path_key, hash_key = "comparisonPath", "comparisonSha256"
    else:
        path_key, hash_key = "resultPath", "resultSha256"
    relative = row.get(path_key)
    expected_hash = row.get(hash_key)
    if not isinstance(relative, str) or not isinstance(expected_hash, str):
        return [f"{label}: transition artifact fields missing"]
    lexical = PurePosixPath(relative)
    if lexical.is_absolute() or lexical.as_posix() != relative or any(
        part in {".", ".."} for part in lexical.parts
    ):
        return [f"{label}: transition artifact path is noncanonical"]
    shown = git_bytes(root, "show", f"{transition_commit}:{relative}")
    if shown.returncode != 0:
        return [f"{label}: transition artifact absent at progress commit"]
    if sha256_bytes(shown.stdout) != expected_hash:
        failures.append(f"{label}: transition artifact hash mismatch at progress commit")
        return failures
    try:
        artifact = strict_json_bytes(shown.stdout)
    except Exception as exc:
        return [f"{label}: transition artifact parse failed: {exc}"]
    unit_id = row.get("auditUnitId")
    if status == "blind-derived":
        ids = [
            item.get("auditUnitId")
            for item in artifact.get("unitResults", [])
            if isinstance(item, dict)
        ]
        if unit_id not in ids:
            failures.append(f"{label}: blind artifact lacks transition unit")
    else:
        if artifact.get("auditUnitId") != unit_id:
            failures.append(f"{label}: transition artifact unit mismatch")
        expected_status = "compared" if status == "compared" else status
        if artifact.get("status") != expected_status:
            failures.append(f"{label}: transition artifact status mismatch")
    preseal = artifact.get("sealedAtGitHead")
    if not isinstance(preseal, str) or not HEX40.fullmatch(preseal):
        failures.append(f"{label}: transition artifact pre-seal invalid")
        return failures
    descendants = git_bytes(
        root,
        "rev-list",
        "--first-parent",
        "--reverse",
        f"{preseal}..{transition_commit}",
    )
    commits = (
        descendants.stdout.decode("ascii", errors="replace").split()
        if descendants.returncode == 0
        else []
    )
    if not commits:
        failures.append(f"{label}: transition artifact seal does not precede progress commit")
        return failures
    seal_commit = commits[0]
    sealed = git_bytes(root, "show", f"{seal_commit}:{relative}")
    if sealed.returncode != 0 or sealed.stdout != shown.stdout:
        failures.append(f"{label}: transition artifact is not bound to its derived seal commit")
    return failures


def progress_snapshot_failures(
    previous: dict[str, Any],
    current: dict[str, Any],
    unit_ids: list[str],
    label: str,
    *,
    transition_commit: str | None = None,
    root: Path = ROOT,
) -> list[str]:
    failures: list[str] = []
    for name, snapshot in (("previous", previous), ("current", current)):
        if set(snapshot) != PROGRESS_TOP_KEYS:
            failures.append(f"{label}: {name} progress top-level fields drift")
        if snapshot.get("schemaVersion") != 2:
            failures.append(f"{label}: {name} progress schemaVersion drift")
        if snapshot.get("recordType") != "stage-1-correctness-audit-progress":
            failures.append(f"{label}: {name} progress recordType drift")
        rows = snapshot.get("units")
        if not isinstance(rows, list) or len(rows) != len(unit_ids):
            failures.append(f"{label}: {name} progress row count drift")
            continue
        if [row.get("auditUnitId") for row in rows if isinstance(row, dict)] != unit_ids:
            failures.append(f"{label}: {name} progress IDs/order drift")
        if any(not isinstance(row, dict) or set(row) != PROGRESS_ROW_KEYS for row in rows):
            failures.append(f"{label}: {name} progress row fields drift")

    previous_rows = previous.get("units", [])
    current_rows = current.get("units", [])
    if not isinstance(previous_rows, list) or not isinstance(current_rows, list):
        return failures
    if len(previous_rows) != len(unit_ids) or len(current_rows) != len(unit_ids):
        return failures

    for prior, row in zip(previous_rows, current_rows):
        if not isinstance(prior, dict) or not isinstance(row, dict):
            continue
        unit_id = row.get("auditUnitId")
        prior_status = prior.get("status")
        status = row.get("status")
        if status == prior_status:
            if row != prior:
                failures.append(f"{label}: unchanged status row mutated: {unit_id}")
            continue
        if status not in PROGRESS_TRANSITIONS.get(str(prior_status), set()):
            failures.append(f"{label}: invalid committed transition {prior_status} -> {status}: {unit_id}")
            continue
        prior_time = None
        if prior.get("lastUpdatedUtc") is not None:
            prior_time = parse_time(
                prior.get("lastUpdatedUtc"),
                failures,
                f"{label}: prior update timestamp: {unit_id}",
            )
        current_time = parse_time(
            row.get("lastUpdatedUtc"),
            failures,
            f"{label}: transition timestamp: {unit_id}",
        )
        if prior_time is not None and current_time is not None and current_time <= prior_time:
            failures.append(f"{label}: non-increasing transition timestamp: {unit_id}")

        blind_fields = ("blindPath", "blindSha256", "blindUnitResultId")
        comparison_fields = ("comparisonPath", "comparisonSha256")
        result_fields = ("resultPath", "resultSha256")
        if status == "blind-derived":
            if not all(isinstance(row.get(key), str) and row.get(key) for key in blind_fields):
                failures.append(f"{label}: blind transition lacks artifact fields: {unit_id}")
            if any(row.get(key) is not None for key in comparison_fields + result_fields):
                failures.append(f"{label}: blind transition has downstream fields: {unit_id}")
        elif status == "compared":
            if any(row.get(key) != prior.get(key) for key in blind_fields):
                failures.append(f"{label}: compared transition changed blind fields: {unit_id}")
            if not all(isinstance(row.get(key), str) and row.get(key) for key in comparison_fields):
                failures.append(f"{label}: compared transition lacks comparison fields: {unit_id}")
            if any(row.get(key) is not None for key in result_fields):
                failures.append(f"{label}: compared transition has result fields: {unit_id}")
        else:
            if any(row.get(key) != prior.get(key) for key in blind_fields + comparison_fields):
                failures.append(f"{label}: final transition changed upstream fields: {unit_id}")
            if not all(isinstance(row.get(key), str) and row.get(key) for key in result_fields):
                failures.append(f"{label}: final transition lacks result fields: {unit_id}")
        if transition_commit is not None:
            failures.extend(
                committed_transition_artifact_failures(
                    row,
                    str(status),
                    transition_commit,
                    root,
                    f"{label}: {unit_id}",
                )
            )

    status_counts = Counter(
        row.get("status")
        for row in current_rows
        if isinstance(row, dict)
    )
    expected_counts = {
        "total": len(unit_ids),
        **{
            count_key: status_counts.get(status, 0)
            for status, count_key in STATUS_COUNT_KEYS.items()
        },
    }
    if current.get("counts") != expected_counts:
        failures.append(f"{label}: progress counts drift")
    for key in ("manifestPath", "manifestSha256"):
        if current.get(key) != previous.get(key):
            failures.append(f"{label}: progress {key} changed")
    return failures


def validate_progress_history(
    current: dict[str, Any],
    unit_ids: list[str],
    failures: list[str],
    *,
    allow_uncommitted_progress: bool,
) -> None:
    if not LOCK_PATH.is_file():
        return
    try:
        lock = strict_load(LOCK_PATH)
        baseline = lock["baselineCommit"]
        relative = PROGRESS_PATH.relative_to(ROOT).as_posix()
        baseline_bytes = git_bytes(ROOT, "show", f"{baseline}:{relative}")
        if baseline_bytes.returncode != 0:
            failures.append("progress history: baseline progress missing")
            return
        previous = strict_json_bytes(baseline_bytes.stdout)
        if baseline_bytes.stdout != canonical_progress_bytes(previous):
            failures.append("progress history: baseline progress is not canonically serialized")
        history = git_bytes(
            ROOT,
            "rev-list",
            "--first-parent",
            "--reverse",
            f"{baseline}..HEAD",
            "--",
            relative,
        )
        if history.returncode != 0:
            failures.append("progress history: Git traversal failed")
            return
        commits = history.stdout.decode("ascii", errors="replace").split()
        for commit in commits:
            shown = git_bytes(ROOT, "show", f"{commit}:{relative}")
            if shown.returncode != 0:
                failures.append(f"progress history: progress missing at {commit}")
                return
            snapshot = strict_json_bytes(shown.stdout)
            if shown.stdout != canonical_progress_bytes(snapshot):
                failures.append(f"progress history: noncanonical progress bytes at {commit}")
            failures.extend(
                progress_snapshot_failures(
                    previous,
                    snapshot,
                    unit_ids,
                    f"progress history {commit}",
                    transition_commit=commit,
                    root=ROOT,
                )
            )
            previous = snapshot
        if allow_uncommitted_progress:
            if PROGRESS_PATH.read_bytes() != canonical_progress_bytes(current):
                failures.append("uncommitted progress is not canonically serialized")
            failures.extend(
                progress_snapshot_failures(previous, current, unit_ids, "uncommitted progress")
            )
        elif current != previous:
            failures.append("progress history: current progress differs from first-parent history")
    except Exception as exc:
        failures.append(f"progress history validation failed: {exc}")


def packet_evidence_indexes(
    packet: dict[str, Any],
    failures: list[str],
    label: str,
) -> tuple[dict[str, set[str]], dict[str, dict[str, str]]]:
    evidence_ids_by_unit: dict[str, set[str]] = {}
    source_hashes_by_unit: dict[str, dict[str, str]] = {}
    for evidence in packet.get("evidence", []):
        if not isinstance(evidence, dict):
            continue
        evidence_id = evidence.get("evidenceId")
        source_path = evidence.get("sourcePath")
        source_hash = evidence.get("sourceSha256")
        for evidence_unit_id in evidence.get("auditUnitIds", []):
            if not isinstance(evidence_unit_id, str):
                continue
            if isinstance(evidence_id, str):
                evidence_ids_by_unit.setdefault(evidence_unit_id, set()).add(evidence_id)
            if isinstance(source_path, str) and isinstance(source_hash, str):
                existing_hash = source_hashes_by_unit.setdefault(evidence_unit_id, {}).get(source_path)
                add(
                    failures,
                    existing_hash is None or existing_hash == source_hash,
                    f"{label}: conflicting source hashes for {evidence_unit_id}: {source_path}",
                )
                source_hashes_by_unit[evidence_unit_id][source_path] = source_hash
    return evidence_ids_by_unit, source_hashes_by_unit


def validate_blind(
    path: Path,
    validators: dict[str, Draft202012Validator],
    manifest_units: dict[str, dict[str, Any]],
    failures: list[str],
    enforce_seals: bool = True,
    minimum_packet_preseal: str | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, str | None]:
    try:
        blind = strict_load(path)
    except Exception as exc:
        failures.append(f"blind parse {path}: {exc}")
        return None, None, None
    if not apply_schema("blind", blind, validators, failures, str(path.relative_to(ROOT))):
        return None, None, None

    packet_path = checked_file(blind.get("packetPath"), blind.get("packetSha256"), failures, f"{path}: packet", AUDIT_DIR / "packets")
    packet: dict[str, Any] | None = None
    packet_commit: str | None = None
    if packet_path and packet_path.is_file():
        packet, packet_commit = validate_packet(
            packet_path,
            validators,
            manifest_units,
            failures,
            enforce_seals=enforce_seals,
            minimum_preseal=minimum_packet_preseal,
        )

    review_path = checked_file(
        blind.get("completenessReviewPath"),
        blind.get("completenessReviewSha256"),
        failures,
        f"{path}: completeness review",
        AUDIT_DIR / "packets",
    )
    review = None
    review_commit: str | None = None
    if review_path and review_path.is_file():
        try:
            review = strict_load(review_path)
            if not apply_schema("completeness", review, validators, failures, str(review_path.relative_to(ROOT))):
                return None, packet, None
            if enforce_seals:
                require_lane_preseal(review, packet_commit, failures, f"{path}: completeness review")
                review_commit = validate_artifact_seal(
                    review,
                    review_path,
                    failures,
                    f"{path}: completeness review",
                )
            finding_rows = [row for row in review.get("findings", []) if isinstance(row, dict)]
            finding_ids = [row.get("findingId") for row in finding_rows]
            add(failures, len(finding_ids) == len(set(finding_ids)), f"{path}: duplicate completeness finding ID")
            packet_evidence_ids = {
                row.get("evidenceId")
                for row in packet.get("evidence", [])
                if isinstance(row, dict)
            } if packet else set()
            for index, finding in enumerate(finding_rows):
                add(
                    failures,
                    set(finding.get("evidenceRefs", [])).issubset(packet_evidence_ids),
                    f"{path}: completeness finding {index} cites evidence outside the source packet",
                )
            unresolved_material = {
                row.get("findingId")
                for row in finding_rows
                if row.get("severity") in {"material", "critical"} and row.get("disposition") == "unresolved"
            }
            declared_unresolved = set(review.get("unresolvedMaterialFindingIds", []))
            add(failures, declared_unresolved == unresolved_material, f"{path}: unresolved material finding index mismatch")
            add(failures, review.get("accepted") is (not unresolved_material), f"{path}: completeness acceptance contradicts findings")
            add(failures, review.get("packetPath") == blind.get("packetPath"), f"{path}: completeness packet path mismatch")
            add(failures, review.get("packetSha256") == blind.get("packetSha256"), f"{path}: completeness packet hash mismatch")
            add(failures, review.get("accepted") is True, f"{path}: packet completeness not accepted")
            add(failures, review.get("unresolvedMaterialFindingIds") == [], f"{path}: unresolved packet findings")
            completeness_response = validate_reviewer(
                review.get("reviewer"),
                failures,
                f"{path}: completeness reviewer",
                response_commit=review_commit,
                prompt_commit=packet_commit,
                enforce_seals=enforce_seals,
            )
            add(
                failures,
                completeness_response
                == {
                    "findings": review.get("findings"),
                    "accepted": review.get("accepted"),
                    "unresolvedMaterialFindingIds": review.get("unresolvedMaterialFindingIds"),
                },
                f"{path}: completeness response content differs from sealed review",
            )
            review_prompt = checked_file(
                review.get("reviewer", {}).get("promptPath"),
                review.get("reviewer", {}).get("promptSha256"),
                failures,
                f"{path}: completeness canonical prompt",
                AUDIT_DIR / "packets",
            )
            validate_canonical_prompt(
                "completeness",
                review_prompt,
                packet_path,
                None,
                failures,
                f"{path}: completeness review",
            )
        except Exception as exc:
            failures.append(f"completeness review parse {review_path}: {exc}")

    blind_commit: str | None = None
    if enforce_seals:
        require_lane_preseal(blind, review_commit, failures, f"{path}: blind derivation")
        blind_commit = validate_artifact_seal(blind, path, failures, f"{path}: blind derivation")

    prompt_path = checked_file(blind.get("promptPath"), blind.get("promptSha256"), failures, f"{path}: prompt", AUDIT_DIR / "packets")
    if enforce_seals:
        validate_file_at_commit(prompt_path, blind_commit, failures, f"{path}: prompt")
    if prompt_path and prompt_path.is_file():
        text = prompt_path.read_text(encoding="utf-8")
        for token in FORBIDDEN_PROMPT_TOKENS:
            add(failures, token not in text, f"{path}: forbidden blind-prompt token {token}")
    validate_canonical_prompt(
        "blind",
        prompt_path,
        packet_path,
        review_path,
        failures,
        f"{path}: blind derivation",
    )
    add(
        failures,
        blind.get("reviewer", {}).get("promptPath") == blind.get("promptPath"),
        f"{path}: blind reviewer prompt path mismatch",
    )
    add(
        failures,
        blind.get("reviewer", {}).get("promptSha256") == blind.get("promptSha256"),
        f"{path}: blind reviewer prompt hash mismatch",
    )
    blind_response = validate_reviewer(
        blind.get("reviewer"),
        failures,
        f"{path}: blind reviewer",
        response_commit=blind_commit,
        prompt_commit=blind_commit,
        enforce_seals=enforce_seals,
    )
    add(
        failures,
        blind_response == {"unitResults": blind.get("unitResults")},
        f"{path}: blind response content differs from sealed derivation",
    )
    if review:
        blind["__completenessReviewerIdentity"] = reviewer_identity(review.get("reviewer"))
        add(
            failures,
            reviewer_identity(review.get("reviewer")) != reviewer_identity(blind.get("reviewer")),
            f"{path}: completeness and blind reviewer are not independent",
        )
    result_ids = [row.get("auditUnitId") for row in blind.get("unitResults", []) if isinstance(row, dict)]
    add(failures, len(result_ids) == len(set(result_ids)), f"{path}: duplicate blind unit result")
    if packet:
        add(failures, result_ids == packet.get("auditUnitIds"), f"{path}: submitted/returned unit IDs or order differ")
        packet_citations: dict[tuple[str, str], set[str]] = {}
        for evidence in packet.get("evidence", []):
            if not isinstance(evidence, dict):
                continue
            key = (str(evidence.get("sourcePath")), str(evidence.get("locator")))
            packet_citations.setdefault(key, set()).update(evidence.get("auditUnitIds", []))
        for unit_result in blind.get("unitResults", []):
            if not isinstance(unit_result, dict):
                continue
            unit_id = unit_result.get("auditUnitId")
            cited_rows: list[dict[str, Any]] = []
            for requirement in unit_result.get("requirements", []):
                if isinstance(requirement, dict):
                    cited_rows.extend(row for row in requirement.get("citations", []) if isinstance(row, dict))
            for ambiguity in unit_result.get("ambiguities", []):
                if isinstance(ambiguity, dict):
                    cited_rows.extend(row for row in ambiguity.get("citations", []) if isinstance(row, dict))
            for scenario in unit_result.get("acceptanceScenarios", []):
                if isinstance(scenario, dict):
                    cited_rows.extend(row for row in scenario.get("citations", []) if isinstance(row, dict))
            for citation in cited_rows:
                key = (str(citation.get("sourcePath")), str(citation.get("locator")))
                add(
                    failures,
                    unit_id in packet_citations.get(key, set()),
                    f"{path}: {unit_id} citation is not exact packet evidence: {key}",
                )
        evidence_ids_by_unit, source_hashes_by_unit = packet_evidence_indexes(
            packet,
            failures,
            str(path),
        )
        blind["__packetEvidenceIdsByUnit"] = evidence_ids_by_unit
        blind["__packetSourceHashesByUnit"] = source_hashes_by_unit
    packet_time = parse_time(packet.get("sealedAtUtc"), failures, f"{path}: packet time") if packet else None
    review_time = parse_time(review.get("sealedAtUtc"), failures, f"{path}: review time") if review else None
    blind_time = parse_time(blind.get("sealedAtUtc"), failures, f"{path}: blind time")
    if packet_time and review_time:
        add(failures, packet_time < review_time, f"{path}: completeness does not strictly follow packet seal")
    if review_time and blind_time:
        add(failures, review_time < blind_time, f"{path}: blind seal does not strictly follow completeness")
    blind["__packetCommit"] = packet_commit
    blind["__reviewCommit"] = review_commit
    blind["__blindCommit"] = blind_commit
    return blind, packet, blind_commit


def expected_family(unit: dict[str, Any]) -> str:
    if unit.get("unitClass") == "sampled-component-effect":
        return str(unit.get("family"))
    if unit.get("unitClass") == "concise-rule-record":
        return "concise-rule"
    return "faq"


def load_semantic_id_sets(failures: list[str]) -> dict[str, set[str]]:
    specs = {
        "semanticRecordIds": ("docs/rules/semantics/pilots.json", "records", "ruleId"),
        "questionIds": ("docs/rules/semantics/review-gates.json", "questions", "questionId"),
        "conflictIds": ("docs/rules/semantics/contradictions.json", "conflicts", "conflictId"),
    }
    result: dict[str, set[str]] = {}
    for label, (relative, collection, field) in specs.items():
        try:
            body = strict_load(ROOT / relative)
            rows = body.get(collection, [])
            values = [row.get(field) for row in rows if isinstance(row, dict)]
            add(
                failures,
                all(isinstance(value, str) and bool(value) for value in values),
                f"{relative}: invalid {field}",
            )
            add(failures, len(values) == len(set(values)), f"{relative}: duplicate {field}")
            result[label] = {value for value in values if isinstance(value, str) and value}
        except Exception as exc:
            failures.append(f"semantic ID index {relative}: {exc}")
            result[label] = set()
    return result


def validate_comparison(
    path: Path,
    blind: dict[str, Any],
    blind_commit: str | None,
    unit: dict[str, Any],
    reveal_hashes: dict[str, dict[str, str]],
    semantic_id_sets: dict[str, set[str]],
    validators: dict[str, Draft202012Validator],
    failures: list[str],
    enforce_seals: bool = True,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        comparison = strict_load(path)
    except Exception as exc:
        failures.append(f"comparison parse {path}: {exc}")
        return None, None
    if not apply_schema("comparison", comparison, validators, failures, str(path.relative_to(ROOT))):
        return None, None
    comparison_commit: str | None = None
    if enforce_seals:
        require_lane_preseal(comparison, blind_commit, failures, f"{path}: comparison")
        comparison_commit = validate_artifact_seal(
            comparison,
            path,
            failures,
            f"{path}: comparison",
        )
    unit_id = unit["auditUnitId"]
    add(failures, comparison.get("auditUnitId") == unit_id, f"{unit_id}: comparison ID mismatch")
    add(failures, comparison.get("family") == expected_family(unit), f"{unit_id}: comparison family mismatch")
    add(failures, comparison.get("status") == "compared", f"{unit_id}: comparison status mismatch")
    ref = comparison.get("blindDerivationRef", {})
    expected_blind_path = path_from_root_for(blind)
    add(failures, ref.get("path") == expected_blind_path, f"{unit_id}: blind path mismatch")
    checked_file(
        ref.get("path"),
        ref.get("sha256"),
        failures,
        f"{unit_id}: comparison blind reference",
        AUDIT_DIR / "blind",
    )
    add(failures, ref.get("auditUnitId") == unit_id, f"{unit_id}: blind unit ref mismatch")

    body = comparison.get("comparison", {})
    revealed = body.get("revealedArtifacts", []) if isinstance(body, dict) else []
    packet_sources = blind.get("__packetSourceHashesByUnit", {}).get(unit_id, {})
    semantic_hashes = reveal_hashes.get("frozenSemanticHashes", {})
    concise_hashes = reveal_hashes.get("frozenConciseRuleHashes", {})
    selection_hashes = reveal_hashes.get("selectionInputHashes", {})
    shared_paths = set(semantic_hashes) | set(concise_hashes) | set(selection_hashes)
    for relative in shared_paths:
        values = {
            mapping[relative]
            for mapping in (semantic_hashes, concise_hashes, selection_hashes)
            if relative in mapping
        }
        add(failures, len(values) == 1, f"{unit_id}: frozen manifest maps disagree for path: {relative}")
    target_path = unit.get("downstreamPath") or unit.get("extractionPath")
    revealed_paths: list[str] = []
    for index, artifact in enumerate(revealed):
        if not isinstance(artifact, dict):
            continue
        relative = artifact.get("path")
        declared_hash = artifact.get("sha256")
        role = artifact.get("role")
        checked_file(
            relative,
            declared_hash,
            failures,
            f"{unit_id}: revealed artifact {index}",
        )
        if isinstance(relative, str):
            revealed_paths.append(relative)
        expected_hash: str | None = None
        if role == "primary-source" and isinstance(relative, str):
            expected_hash = packet_sources.get(relative)
            add(failures, expected_hash is not None, f"{unit_id}: revealed primary source is absent from packet")
        elif role == "downstream-target" and isinstance(relative, str):
            target_maps = (
                (concise_hashes,)
                if unit.get("downstreamPath")
                else (selection_hashes, semantic_hashes)
            )
            target_values = {mapping[relative] for mapping in target_maps if relative in mapping}
            add(failures, len(target_values) == 1, f"{unit_id}: downstream target is not uniquely manifest-frozen")
            expected_hash = next(iter(target_values), None)
        elif role == "semantic-projection" and isinstance(relative, str):
            expected_hash = semantic_hashes.get(relative)
            add(failures, expected_hash is not None, f"{unit_id}: semantic projection is not frozen")
        elif role == "source-index" and isinstance(relative, str):
            index_values = {
                mapping[relative]
                for mapping in (selection_hashes, semantic_hashes)
                if relative in mapping
            }
            add(failures, len(index_values) == 1, f"{unit_id}: source index is not uniquely manifest-frozen")
            expected_hash = next(iter(index_values), None)
        if expected_hash is not None:
            add(failures, declared_hash == expected_hash, f"{unit_id}: revealed artifact hash differs from frozen source")
        if role == "downstream-target":
            add(failures, relative == target_path, f"{unit_id}: wrong downstream target revealed")
        elif role == "semantic-projection":
            add(
                failures,
                isinstance(relative, str)
                and relative in SEMANTIC_PROJECTION_PATHS
                and relative in reveal_hashes.get("frozenSemanticHashes", {}),
                f"{unit_id}: semantic-projection role names a non-projection artifact",
            )
        elif role == "source-index":
            add(
                failures,
                isinstance(relative, str)
                and (
                    "/source-extraction/" in relative
                    or relative.endswith("-source-index.json")
                ),
                f"{unit_id}: source-index role names a non-index artifact",
            )
    add(failures, len(revealed_paths) == len(set(revealed_paths)), f"{unit_id}: duplicate revealed artifact path")
    add(
        failures,
        isinstance(target_path, str)
        and any(
            isinstance(artifact, dict)
            and artifact.get("role") == "downstream-target"
            and artifact.get("path") == target_path
            for artifact in revealed
        ),
        f"{unit_id}: required downstream target was not revealed",
    )
    add(
        failures,
        any(
            isinstance(artifact, dict)
            and artifact.get("role") == "semantic-projection"
            and artifact.get("path") == REQUIRED_BEHAVIOR_PROJECTION_PATH
            for artifact in revealed
        ),
        f"{unit_id}: required behavior projection was not revealed",
    )
    for id_field, known_ids in semantic_id_sets.items():
        declared_ids = body.get(id_field, []) if isinstance(body, dict) else []
        if not isinstance(declared_ids, list):
            declared_ids = []
        declared_strings = [value for value in declared_ids if isinstance(value, str)]
        add(
            failures,
            len(declared_strings) == len(declared_ids)
            and set(declared_strings).issubset(known_ids),
            f"{unit_id}: unknown {id_field}",
        )

    comparator_response = validate_reviewer(
        comparison.get("comparator"),
        failures,
        f"{unit_id}: comparator",
        response_commit=comparison_commit,
        prompt_commit=comparison_commit,
        enforce_seals=enforce_seals,
    )
    add(
        failures,
        comparator_response
        == {
            "auditUnitId": unit_id,
            "comparison": body,
        },
        f"{unit_id}: comparator response content differs from sealed comparison",
    )
    add(
        failures,
        reviewer_identity(comparison.get("comparator")) != reviewer_identity(blind.get("reviewer")),
        f"{unit_id}: comparator is not independent of blind reviewer",
    )
    completeness_identity = blind.get("__completenessReviewerIdentity")
    if completeness_identity is not None:
        add(
            failures,
            reviewer_identity(comparison.get("comparator")) != completeness_identity,
            f"{unit_id}: comparator is not independent of completeness reviewer",
        )
    discrepancies = comparison.get("comparison", {}).get("discrepancies", [])
    if not isinstance(discrepancies, list):
        discrepancies = []
    packet_evidence_ids = blind.get("__packetEvidenceIdsByUnit", {}).get(unit_id, set())
    add(failures, isinstance(packet_evidence_ids, set) and bool(packet_evidence_ids), f"{unit_id}: packet evidence index absent")
    discrepancy_rows = [row for row in discrepancies if isinstance(row, dict)]
    discrepancy_ids = [
        row.get("discrepancyId")
        for row in discrepancy_rows
        if isinstance(row.get("discrepancyId"), str)
    ]
    add(
        failures,
        len(discrepancy_ids) == len(discrepancy_rows) == len(set(discrepancy_ids)),
        f"{unit_id}: invalid or duplicate discrepancy ID",
    )
    for index, row in enumerate(discrepancies):
        if not isinstance(row, dict):
            continue
        if row.get("severity") in {"material", "critical"}:
            add(failures, isinstance(row.get("rootCauseId"), str) and bool(row.get("rootCauseId")), f"{unit_id}: discrepancy {index} lacks root cause")
        if row.get("classification") == "authority-inversion":
            add(failures, row.get("authorityOverride") is True, f"{unit_id}: authority inversion flag false")
        if row.get("classification") == "hidden-default":
            add(failures, row.get("hiddenDefault") is True, f"{unit_id}: hidden-default flag false")
        add(
            failures,
            set(row.get("evidenceRefs", [])).issubset(packet_evidence_ids),
            f"{unit_id}: discrepancy {index} cites evidence outside the source packet",
        )
    blind_time = parse_time(blind.get("sealedAtUtc"), failures, f"{unit_id}: blind time")
    comparison_time = parse_time(comparison.get("sealedAtUtc"), failures, f"{unit_id}: comparison time")
    if blind_time and comparison_time:
        add(failures, blind_time < comparison_time, f"{unit_id}: comparison does not strictly follow blind seal")
    comparison["__validatedPath"] = str(path.relative_to(ROOT))
    return comparison, comparison_commit


def validate_result(
    path: Path,
    comparison: dict[str, Any],
    comparison_commit: str | None,
    blind: dict[str, Any],
    unit: dict[str, Any],
    validators: dict[str, Draft202012Validator],
    failures: list[str],
    enforce_seals: bool = True,
    required_comparison_commits: tuple[str, ...] = (),
) -> dict[str, Any] | None:
    try:
        result = strict_load(path)
    except Exception as exc:
        failures.append(f"result parse {path}: {exc}")
        return None
    if not apply_schema("result", result, validators, failures, str(path.relative_to(ROOT))):
        return None
    result_commit: str | None = None
    if enforce_seals:
        require_preseal_at_or_after(result, comparison_commit, failures, f"{path}: adjudication")
        require_preseal_after_all(
            result,
            required_comparison_commits,
            failures,
            f"{path}: adjudication",
        )
        result_commit = validate_artifact_seal(result, path, failures, f"{path}: adjudication")
    unit_id = unit["auditUnitId"]
    add(failures, result.get("auditUnitId") == unit_id, f"{unit_id}: result ID mismatch")
    add(failures, result.get("family") == expected_family(unit), f"{unit_id}: result family mismatch")
    ref = result.get("comparisonRef", {})
    expected_comparison_path = path_from_root_for(comparison)
    add(failures, ref.get("path") == expected_comparison_path, f"{unit_id}: comparison path mismatch")
    checked_file(
        ref.get("path"),
        ref.get("sha256"),
        failures,
        f"{unit_id}: adjudication comparison reference",
        AUDIT_DIR / "comparisons",
    )
    add(failures, ref.get("auditUnitId") == unit_id, f"{unit_id}: comparison unit ref mismatch")

    discrepancies = comparison.get("comparison", {}).get("discrepancies", [])
    if not isinstance(discrepancies, list):
        discrepancies = []
    packet_evidence_ids = blind.get("__packetEvidenceIdsByUnit", {}).get(unit_id, set())
    discrepancy_ids = {
        row.get("discrepancyId")
        for row in discrepancies
        if isinstance(row, dict) and isinstance(row.get("discrepancyId"), str)
    }
    severities = [row.get("severity") for row in discrepancies if isinstance(row, dict)]
    authority_override = any(row.get("authorityOverride") is True for row in discrepancies if isinstance(row, dict))
    hidden_default = any(row.get("hiddenDefault") is True for row in discrepancies if isinstance(row, dict))
    blind_unit = next(
        (
            row
            for row in blind.get("unitResults", [])
            if isinstance(row, dict) and row.get("auditUnitId") == unit_id
        ),
        {},
    )
    derivation_source_blocked = blind_unit.get("derivationStatus") == "source-blocked"
    if derivation_source_blocked:
        add(
            failures,
            "blocked" in severities,
            f"{unit_id}: source-blocked derivation lacks a blocked comparison row",
        )
    status = result.get("status")
    if derivation_source_blocked or "blocked" in severities:
        add(failures, status == "source-blocked", f"{unit_id}: blocked status mismatch")
    elif "critical" in severities or authority_override or hidden_default:
        add(failures, status == "critical-error", f"{unit_id}: critical/authority/default status mismatch")
    elif "material" in severities:
        add(failures, status == "material-error", f"{unit_id}: material status mismatch")
    elif all(severity in {"none", "minor"} for severity in severities):
        add(failures, status == "accepted", f"{unit_id}: clean status mismatch")
    else:
        failures.append(f"{unit_id}: unknown severity cannot be adjudicated")

    reviewed_ids: set[str] = set()
    verification_review_ids: set[str] = set()
    for review in result.get("verificationReviews", []):
        if not isinstance(review, dict):
            continue
        review_id = review.get("reviewId")
        add(
            failures,
            isinstance(review_id, str) and review_id not in verification_review_ids,
            f"{unit_id}: invalid or duplicate verification review ID",
        )
        if isinstance(review_id, str):
            verification_review_ids.add(review_id)
        verification_response = validate_reviewer(
            review.get("reviewer"),
            failures,
            f"{unit_id}: verification reviewer",
            response_commit=result_commit,
            prompt_commit=result_commit,
            enforce_seals=enforce_seals,
        )
        add(
            failures,
            verification_response
            == {
                key: value
                for key, value in review.items()
                if key != "reviewer"
            },
            f"{unit_id}: verification response content differs from sealed review",
        )
        identity = reviewer_identity(review.get("reviewer"))
        add(failures, identity != reviewer_identity(comparison.get("comparator")), f"{unit_id}: verification reviewer equals comparator")
        add(failures, identity != reviewer_identity(blind.get("reviewer")), f"{unit_id}: verification reviewer equals blind reviewer")
        completeness_identity = blind.get("__completenessReviewerIdentity")
        if completeness_identity is not None:
            add(failures, identity != completeness_identity, f"{unit_id}: verification reviewer equals completeness reviewer")
        ids = {
            value
            for value in review.get("reviewedDiscrepancyIds", [])
            if isinstance(value, str)
        }
        add(failures, ids.issubset(discrepancy_ids), f"{unit_id}: verification references unknown discrepancy")
        add(
            failures,
            {
                value
                for value in review.get("evidenceRefs", [])
                if isinstance(value, str)
            }.issubset(packet_evidence_ids),
            f"{unit_id}: verification cites evidence outside the source packet",
        )
        disposition = review.get("disposition")
        add(
            failures,
            disposition != "not-confirmed",
            f"{unit_id}: unconfirmed comparison requires a superseding comparison before adjudication",
        )
        add(
            failures,
            disposition != "source-blocked" or result.get("status") == "source-blocked",
            f"{unit_id}: source-blocked verification disposition/result mismatch",
        )
        reviewed_ids.update(ids)
    mandatory = {
        row.get("discrepancyId")
        for row in discrepancies
        if isinstance(row, dict)
        and (
            row.get("severity") in {"minor", "material", "critical", "blocked"}
            or row.get("classification")
            in {"source-ambiguity-preserved", "source-conflict-preserved", "presentation-only"}
        )
    }
    add(failures, mandatory.issubset(reviewed_ids), f"{unit_id}: mandatory discrepancy lacks independent verification")

    resolution = result.get("resolution", {})
    resolution_status = resolution.get("status")
    if status == "accepted":
        add(failures, resolution_status == "not-required", f"{unit_id}: accepted result has nontrivial resolution")
    elif status == "source-blocked":
        add(failures, resolution_status == "source-blocked", f"{unit_id}: source-blocked result resolution mismatch")
    else:
        add(failures, resolution_status == "pending", f"{unit_id}: error result resolution mismatch")
    resolution_refs = {
        value
        for value in resolution.get("verificationEvidenceRefs", [])
        if isinstance(value, str)
    }
    add(
        failures,
        resolution_refs.issubset(packet_evidence_ids | verification_review_ids),
        f"{unit_id}: resolution cites unknown verification evidence",
    )
    comparison_time = parse_time(comparison.get("sealedAtUtc"), failures, f"{unit_id}: comparison time")
    result_time = parse_time(result.get("sealedAtUtc"), failures, f"{unit_id}: result time")
    if comparison_time and result_time:
        add(failures, comparison_time < result_time, f"{unit_id}: adjudication does not strictly follow comparison")
    result["__sealCommit"] = result_commit
    return result


def path_from_root_for(value: dict[str, Any]) -> str:
    marker = value.get("__validatedPath")
    return str(marker) if isinstance(marker, str) else ""


def single_wave_failures(waves: dict[str, set[str]]) -> list[str]:
    return [
        f"{label} artifacts do not share one wave seal commit"
        for label, commits in waves.items()
        if len(commits) > 1
    ]


def validate(
    manifest_path: Path = MANIFEST_PATH,
    progress_path: Path = PROGRESS_PATH,
    check_builder: bool = True,
    require_lock: bool = True,
    enforce_seals: bool = True,
    allow_uncommitted_progress: bool = False,
) -> dict[str, Any]:
    failures: list[str] = []
    if check_builder:
        check = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_correctness_audit_manifest.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        add(failures, check.returncode == 0, f"manifest rebuild check failed: {check.stdout}{check.stderr}".strip())
    try:
        manifest = strict_load(manifest_path)
        progress = strict_load(progress_path)
    except Exception as exc:
        return {"passed": False, "failureCount": 1, "failures": [f"input parse: {exc}"]}
    if not isinstance(manifest, dict) or not isinstance(progress, dict):
        failures.append("manifest and progress must both be JSON objects")
        return {
            "passed": False,
            "failureCount": len(failures),
            "failures": failures,
        }
    if require_lock and not allow_uncommitted_progress:
        try:
            progress_relative = progress_path.resolve(strict=False).relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            failures.append("progress path escapes repository")
        else:
            head_progress = git_bytes(ROOT, "show", f"HEAD:{progress_relative}")
            add(failures, head_progress.returncode == 0, "progress is absent from current HEAD")
            if head_progress.returncode == 0:
                add(
                    failures,
                    head_progress.stdout == progress_path.read_bytes(),
                    "progress has uncommitted drift",
                )
    validators = schema_validators(failures)

    add(failures, manifest.get("schemaVersion") == 1, "manifest schemaVersion")
    add(failures, manifest.get("auditVersion") == "stage1-v2", "manifest auditVersion")
    add(failures, manifest.get("recordType") == "stage-1-blind-correctness-audit-manifest", "manifest recordType")
    units = manifest.get("units", [])
    add(failures, isinstance(units, list) and len(units) == 140, "manifest must have 140 units")
    unit_ids = [row.get("auditUnitId") for row in units if isinstance(row, dict)]
    add(failures, len(unit_ids) == len(set(unit_ids)) == 140, "manifest unit IDs not unique/complete")
    unit_map = {row["auditUnitId"]: row for row in units if isinstance(row, dict) and "auditUnitId" in row}
    classes = Counter(row.get("unitClass") for row in units if isinstance(row, dict))
    add(failures, classes == Counter({"concise-rule-record": 56, "base-applicable-faq-unit": 28, "sampled-component-effect": 56}), "audit class counts")
    families = Counter(row.get("family") for row in units if isinstance(row, dict) and row.get("unitClass") == "sampled-component-effect")
    add(failures, dict(families) == EXPECTED_FAMILIES, "component family distribution")
    counts = manifest.get("counts", {})
    add(failures, counts.get("totalAuditUnits") == 140, "declared total count")
    add(failures, counts.get("conciseRuleRecords") == 56, "declared concise count")
    add(failures, counts.get("baseApplicableFaqUnits") == 28, "declared FAQ count")
    add(failures, counts.get("sampledComponentEffects") == 56, "declared component count")
    add(failures, counts.get("componentFamilies") == EXPECTED_FAMILIES, "declared family counts")
    add(failures, counts.get("componentCandidateUniverses") == EXPECTED_UNIVERSES, "candidate universe counts")
    add(failures, manifest.get("passThreshold") == EXPECTED_THRESHOLDS, "pass threshold drift")

    seed = manifest.get("seedMaterial")
    coverage: dict[str, dict[str, int]] = {}
    for row in units:
        if not isinstance(row, dict) or row.get("unitClass") != "sampled-component-effect":
            continue
        selection = row.get("selection", {})
        stratum = selection.get("stratum")
        expected_score = hashlib.sha256(f"{seed}|{stratum}|{row.get('sourceIdentity')}".encode()).hexdigest()
        add(failures, selection.get("score") == expected_score, f"selection score drift: {row.get('auditUnitId')}")
        candidate_count = selection.get("candidateCount")
        bucket = coverage.setdefault(str(stratum), {"eligibleCandidates": candidate_count, "selectedUnits": 0})
        add(failures, bucket["eligibleCandidates"] == candidate_count, f"candidate count differs within stratum: {stratum}")
        bucket["selectedUnits"] += 1
        add(
            failures,
            isinstance(row.get("extractionPath"), str) and bool(row.get("extractionPath")),
            f"sampled component lacks comparison target: {row.get('auditUnitId')}",
        )
        checked_file(row.get("sourcePath"), row.get("sourceSha256"), failures, f"selected source: {row.get('auditUnitId')}")
    add(failures, manifest.get("selectionCoverage") == dict(sorted(coverage.items())), "selection coverage drift")

    reveal_hashes: dict[str, dict[str, str]] = {}
    for section in ("frozenSemanticHashes", "frozenConciseRuleHashes", "selectionInputHashes"):
        mapping = manifest.get(section, {})
        add(failures, isinstance(mapping, dict) and bool(mapping), f"{section} absent")
        if isinstance(mapping, dict):
            reveal_hashes[section] = {
                str(relative): str(expected_hash)
                for relative, expected_hash in mapping.items()
            }
            for relative, expected_hash in mapping.items():
                checked_file(relative, expected_hash, failures, f"{section}: {relative}")
    for row in units:
        if not isinstance(row, dict) or row.get("unitClass") != "sampled-component-effect":
            continue
        add(
            failures,
            any(row.get("extractionPath") in mapping for mapping in reveal_hashes.values()),
            f"sampled component target is not manifest-frozen: {row.get('auditUnitId')}",
        )
    semantic_id_sets = load_semantic_id_sets(failures)
    lock_commit = validate_lock(manifest, failures, require_lock)

    add(failures, progress.get("schemaVersion") == 2, "progress schemaVersion")
    add(failures, progress.get("recordType") == "stage-1-correctness-audit-progress", "progress recordType")
    add(failures, progress.get("manifestSha256") == sha256_path(manifest_path), "progress manifest hash")
    progress_units = progress.get("units", [])
    add(failures, isinstance(progress_units, list) and len(progress_units) == 140, "progress must have 140 units")
    progress_ids = [row.get("auditUnitId") for row in progress_units if isinstance(row, dict)]
    add(failures, progress_ids == unit_ids, "progress order/IDs differ from manifest")

    blind_cache: dict[str, tuple[dict[str, Any], str | None]] = {}
    packet_wave_commits: set[str] = set()
    review_wave_commits: set[str] = set()
    blind_wave_commits: set[str] = set()
    comparison_commits: list[str] = []
    adjudication_wave_commits: set[str] = set()
    comparison_paths: list[str] = []
    final_candidates: list[
        tuple[dict[str, Any], Path, dict[str, Any], dict[str, Any], str | None]
    ] = []
    status_counts = Counter()
    for row in progress_units:
        if not isinstance(row, dict):
            failures.append("non-object progress row")
            continue
        expected_keys = {
            "auditUnitId",
            "status",
            "blindPath",
            "blindSha256",
            "blindUnitResultId",
            "comparisonPath",
            "comparisonSha256",
            "resultPath",
            "resultSha256",
            "lastUpdatedUtc",
        }
        unit_id = row.get("auditUnitId")
        add(failures, set(row) == expected_keys, f"progress keys drift: {unit_id}")
        status = row.get("status")
        add(failures, status in STATUS_COUNT_KEYS, f"invalid status: {unit_id}")
        status_counts[status] += 1
        blind_values = (row.get("blindPath"), row.get("blindSha256"), row.get("blindUnitResultId"))
        comparison_values = (row.get("comparisonPath"), row.get("comparisonSha256"))
        result_values = (row.get("resultPath"), row.get("resultSha256"))
        if status == "pending-blind-derivation":
            add(
                failures,
                all(value is None for value in blind_values + comparison_values + result_values),
                f"pending artifact attached: {unit_id}",
            )
            add(failures, row.get("lastUpdatedUtc") is None, f"pending timestamp attached: {unit_id}")
            continue

        blind_path = checked_file(
            row.get("blindPath"),
            row.get("blindSha256"),
            failures,
            f"{unit_id}: blind",
            AUDIT_DIR / "blind",
        )
        blind = None
        blind_commit: str | None = None
        if blind_path and blind_path.is_file():
            relative = str(blind_path.relative_to(ROOT))
            cached = blind_cache.get(relative)
            if cached is None:
                blind, _, blind_commit = validate_blind(
                    blind_path,
                    validators,
                    unit_map,
                    failures,
                    enforce_seals=enforce_seals,
                    minimum_packet_preseal=lock_commit,
                )
                if blind is not None:
                    blind["__validatedPath"] = relative
                    blind_cache[relative] = (blind, blind_commit)
            else:
                blind, blind_commit = cached
        if blind:
            for field, bucket in (
                ("__packetCommit", packet_wave_commits),
                ("__reviewCommit", review_wave_commits),
                ("__blindCommit", blind_wave_commits),
            ):
                value = blind.get(field)
                if isinstance(value, str):
                    bucket.add(value)
            blind_ids = [item.get("auditUnitId") for item in blind.get("unitResults", []) if isinstance(item, dict)]
            add(failures, unit_id in blind_ids, f"{unit_id}: blind batch lacks unit")
            add(failures, row.get("blindUnitResultId") == unit_id, f"{unit_id}: blind unit result key mismatch")
        if status == "blind-derived":
            add(
                failures,
                all(value is None for value in comparison_values + result_values),
                f"blind-derived unit has downstream artifact: {unit_id}",
            )
            add(failures, isinstance(row.get("lastUpdatedUtc"), str), f"{unit_id}: update timestamp missing")
            if isinstance(row.get("lastUpdatedUtc"), str):
                parse_time(row.get("lastUpdatedUtc"), failures, f"{unit_id}: progress update time")
            continue

        comparison_path = checked_file(
            row.get("comparisonPath"),
            row.get("comparisonSha256"),
            failures,
            f"{unit_id}: comparison",
            AUDIT_DIR / "comparisons",
        )
        if comparison_path is not None:
            comparison_paths.append(str(comparison_path.relative_to(ROOT)))
        comparison = None
        comparison_commit: str | None = None
        if comparison_path and comparison_path.is_file() and blind:
            comparison, comparison_commit = validate_comparison(
                comparison_path,
                blind,
                blind_commit,
                unit_map[unit_id],
                reveal_hashes,
                semantic_id_sets,
                validators,
                failures,
                enforce_seals=enforce_seals,
            )
            if comparison_commit is not None:
                comparison_commits.append(comparison_commit)
        if status == "compared":
            add(
                failures,
                all(value is None for value in result_values),
                f"compared unit has final adjudication: {unit_id}",
            )
            add(failures, isinstance(row.get("lastUpdatedUtc"), str), f"{unit_id}: update timestamp missing")
            if isinstance(row.get("lastUpdatedUtc"), str):
                parse_time(row.get("lastUpdatedUtc"), failures, f"{unit_id}: progress update time")
            continue

        result_path = checked_file(
            row.get("resultPath"),
            row.get("resultSha256"),
            failures,
            f"{unit_id}: result",
            AUDIT_DIR / "adjudications",
        )
        if result_path and result_path.is_file() and blind and comparison:
            final_candidates.append((row, result_path, blind, comparison, comparison_commit))
        add(failures, isinstance(row.get("lastUpdatedUtc"), str), f"{unit_id}: update timestamp missing")
        if isinstance(row.get("lastUpdatedUtc"), str):
            parse_time(row.get("lastUpdatedUtc"), failures, f"{unit_id}: progress update time")

    if final_candidates and enforce_seals:
        add(
            failures,
            all(
                isinstance(candidate, dict)
                and candidate.get("status") not in {"pending-blind-derivation", "blind-derived"}
                for candidate in progress_units
            ),
            "final adjudication exists before every Stage 1 unit reached compared",
        )
        add(
            failures,
            len(comparison_commits) == 140,
            "final adjudication requires 140 valid comparison seal commits",
        )
        add(
            failures,
            len(comparison_paths) == len(set(comparison_paths)) == 140,
            "final adjudication requires 140 distinct comparison artifact paths",
        )
    required_comparison_commits = tuple(sorted(set(comparison_commits)))
    for row, result_path, blind, comparison, comparison_commit in final_candidates:
        unit_id = row.get("auditUnitId")
        result = validate_result(
            result_path,
            comparison,
            comparison_commit,
            blind,
            unit_map[unit_id],
            validators,
            failures,
            enforce_seals=enforce_seals,
            required_comparison_commits=required_comparison_commits,
        )
        if result:
            seal_commit = result.get("__sealCommit")
            if isinstance(seal_commit, str):
                adjudication_wave_commits.add(seal_commit)
            add(
                failures,
                result.get("status") == row.get("status"),
                f"{unit_id}: progress/result status mismatch",
            )

    comparison_wave_commits = set(comparison_commits)
    if enforce_seals:
        failures.extend(
            single_wave_failures(
                {
                    "packet": packet_wave_commits,
                    "completeness": review_wave_commits,
                    "blind": blind_wave_commits,
                    "comparison": comparison_wave_commits,
                    "adjudication": adjudication_wave_commits,
                }
            )
        )

    if require_lock:
        validate_progress_history(
            progress,
            unit_ids,
            failures,
            allow_uncommitted_progress=allow_uncommitted_progress,
        )

    declared = progress.get("counts", {})
    add(failures, declared.get("total") == 140, "progress declared total")
    for status, key in STATUS_COUNT_KEYS.items():
        add(failures, declared.get(key) == status_counts.get(status, 0), f"progress count mismatch: {key}")

    return {
        "passed": not failures,
        "failureCount": len(failures),
        "counts": {
            "manifestUnits": len(units),
            "progressUnits": len(progress_units),
            "statuses": dict(sorted(status_counts.items())),
            "componentFamilies": dict(sorted(families.items())),
        },
        "auditDecisionReady": len(progress_units) == 140
        and all(row.get("status") in {"accepted", "material-error", "critical-error", "source-blocked"} for row in progress_units if isinstance(row, dict)),
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prelock", action="store_true", help="allow the one setup run before audit-lock.json is committed")
    args = parser.parse_args()
    report = validate(require_lock=not args.prelock)
    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
