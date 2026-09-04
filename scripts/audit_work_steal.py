#!/usr/bin/env python3
"""Race-safe work stealing for the fragment-coverage audit."""

from __future__ import annotations

import argparse
import ctypes
import errno
import fcntl
import json
import os
import random
import re
import stat
import sys
import time
from pathlib import Path
from typing import Any

VERDICTS = ("pass", "fail", "unsure")
ALL_LOCATIONS = ("pass", "fail", "unsure", "repair", "irrelevant")
WORKER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
RENAME_NOREPLACE = 1
AT_FDCWD = -100


def emit(**payload: Any) -> None:
    print(json.dumps(payload, sort_keys=True))


def load_manifest(audit_root: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    data = json.loads((audit_root / "manifest.json").read_text(encoding="utf-8"))
    rows = data.get("fragments")
    if not isinstance(rows, list):
        raise RuntimeError("manifest.json has no fragments list")
    by_id: dict[str, dict[str, Any]] = {}
    seen_files: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not isinstance(row.get("file"), str):
            raise RuntimeError("invalid manifest row")
        fragment_id = row["id"]
        filename = row["file"]
        if fragment_id in by_id or filename in seen_files:
            raise RuntimeError("manifest IDs and files must be unique")
        if Path(filename).name != filename or not filename.endswith(".txt"):
            raise RuntimeError(f"unsafe manifest filename: {filename!r}")
        by_id[fragment_id] = row
        seen_files.add(filename)
    return rows, by_id


def validate_worker(worker: str) -> str:
    if not WORKER_RE.fullmatch(worker):
        raise RuntimeError(f"invalid worker identifier: {worker!r}")
    return worker


def sidecar_name(filename: str, verdict: str) -> str:
    if not filename.endswith(".txt"):
        raise RuntimeError(f"not a fragment text file: {filename}")
    return filename[:-4] + f".{verdict}.md"


def fsync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def rename_noreplace(source: Path, destination: Path) -> None:
    """Same-filesystem atomic rename that refuses to overwrite."""
    if source.parent.stat().st_dev != destination.parent.stat().st_dev:
        raise RuntimeError("claim/finalize rename would cross filesystems")
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    if renameat2 is not None:
        renameat2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        renameat2.restype = ctypes.c_int
        rc = renameat2(
            AT_FDCWD,
            os.fsencode(source),
            AT_FDCWD,
            os.fsencode(destination),
            RENAME_NOREPLACE,
        )
        if rc == 0:
            return
        err = ctypes.get_errno()
        if err != errno.ENOSYS:
            raise OSError(err, os.strerror(err), str(destination))
    if destination.exists():
        raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), str(destination))
    os.rename(source, destination)


def ensure_layout(audit_root: Path, worker: str | None = None) -> Path | None:
    root_dev = audit_root.stat().st_dev
    for verdict in ALL_LOCATIONS:
        target = audit_root / verdict
        target.mkdir(mode=0o755, exist_ok=True)
        if target.stat().st_dev != root_dev:
            raise RuntimeError(f"{target} is not on the audit filesystem")
    claimed_root = audit_root / "claimed"
    claimed_root.mkdir(mode=0o755, exist_ok=True)
    if claimed_root.stat().st_dev != root_dev:
        raise RuntimeError("audit/claimed is not on the audit filesystem")
    if worker is None:
        return None
    worker_dir = claimed_root / validate_worker(worker)
    worker_dir.mkdir(mode=0o755, exist_ok=True)
    if worker_dir.stat().st_dev != root_dev:
        raise RuntimeError("worker claim directory is not on the audit filesystem")
    return worker_dir


def try_claim_path(source: Path, destination: Path) -> str:
    """Open, flock, revalidate, and rename before releasing the fd."""
    flags = os.O_RDONLY | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(source, flags)
    except FileNotFoundError:
        return "lost"
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return "busy"
        opened = os.fstat(fd)
        if not stat.S_ISREG(opened.st_mode):
            return "lost"
        try:
            current = os.lstat(source)
        except FileNotFoundError:
            return "lost"
        if stat.S_ISLNK(current.st_mode) or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino):
            return "lost"
        if source.parent.stat().st_dev != opened.st_dev or destination.parent.stat().st_dev != opened.st_dev:
            raise RuntimeError("claim rename would cross filesystems")
        rename_noreplace(source, destination)
        fsync_dir(source.parent)
        fsync_dir(destination.parent)
        return "claimed"
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)


def claim_one(audit_root: Path, worker: str, rounds: int = 5) -> dict[str, Any]:
    rows, _ = load_manifest(audit_root)
    worker_dir = ensure_layout(audit_root, worker)
    assert worker_dir is not None
    saw_busy = False
    for round_index in range(max(1, rounds)):
        candidates = [row for row in rows if (audit_root / row["file"]).is_file()]
        random.SystemRandom().shuffle(candidates)
        if not candidates:
            return {"status": "empty", "worker": worker}
        for row in candidates:
            source = audit_root / row["file"]
            destination = worker_dir / row["file"]
            result = try_claim_path(source, destination)
            if result == "claimed":
                return {
                    "status": "claimed",
                    "worker": worker,
                    "id": row["id"],
                    "file": str(destination.relative_to(audit_root.parent)),
                }
            saw_busy = saw_busy or result == "busy"
        if round_index + 1 < rounds:
            time.sleep(random.uniform(0.015, 0.12))
    return {"status": "busy" if saw_busy else "retry", "worker": worker}


def clean_field(label: str, value: str, maximum: int) -> str:
    cleaned = " ".join(value.split())
    if not cleaned:
        raise RuntimeError(f"{label} must not be empty")
    if len(cleaned) > maximum:
        raise RuntimeError(f"{label} exceeds {maximum} characters")
    return cleaned


def existing_fragment_locations(audit_root: Path, filename: str) -> list[Path]:
    locations: list[Path] = []
    root_path = audit_root / filename
    if root_path.exists():
        locations.append(root_path)
    for name in ALL_LOCATIONS:
        path = audit_root / name / filename
        if path.exists():
            locations.append(path)
    claimed_root = audit_root / "claimed"
    if claimed_root.exists():
        for worker_dir in claimed_root.iterdir():
            path = worker_dir / filename
            if worker_dir.is_dir() and path.exists():
                locations.append(path)
    return locations


def write_staged_sidecar(path: Path, content: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(path, flags, 0o644)
    try:
        data = content.encode("utf-8")
        written = 0
        while written < len(data):
            written += os.write(fd, data[written:])
        os.fsync(fd)
    finally:
        os.close(fd)


def finalize_claim(
    audit_root: Path,
    worker: str,
    fragment_id: str,
    verdict: str,
    model: str,
    provider: str,
    evidence: str,
) -> dict[str, Any]:
    if verdict not in VERDICTS:
        raise RuntimeError(f"invalid verifier verdict: {verdict}")
    _, by_id = load_manifest(audit_root)
    row = by_id.get(fragment_id)
    if row is None:
        raise RuntimeError(f"unknown manifest ID: {fragment_id}")
    worker_dir = ensure_layout(audit_root, worker)
    assert worker_dir is not None
    filename = row["file"]
    claimed = worker_dir / filename
    locations = existing_fragment_locations(audit_root, filename)
    if locations != [claimed]:
        raise RuntimeError(f"claim is not uniquely owned by {worker}: {[str(p) for p in locations]}")
    if claimed.is_symlink() or not claimed.is_file():
        raise RuntimeError("claimed fragment is not a regular file")

    model = clean_field("model", model, 200)
    provider = clean_field("provider", provider, 200)
    evidence = clean_field("evidence", evidence, 2000)
    target_dir = audit_root / verdict
    target_fragment = target_dir / filename
    target_sidecar = target_dir / sidecar_name(filename, verdict)
    if target_fragment.exists() or target_sidecar.exists():
        raise RuntimeError("canonical verdict target already exists")

    sidecar_content = f"Model: `{model}`\nProvider: `{provider}`\nEvidence: {evidence}\n"
    staged = worker_dir / f".{target_sidecar.name}.tmp.{os.getpid()}"
    write_staged_sidecar(staged, sidecar_content)
    sidecar_installed = False
    try:
        rename_noreplace(staged, target_sidecar)
        sidecar_installed = True
        fsync_dir(target_dir)
        rename_noreplace(claimed, target_fragment)
        fsync_dir(worker_dir)
        fsync_dir(target_dir)
    except Exception:
        if sidecar_installed and target_sidecar.exists() and not target_fragment.exists():
            try:
                rename_noreplace(target_sidecar, staged)
            except Exception:
                pass
        raise
    return {
        "status": "finalized",
        "worker": worker,
        "id": fragment_id,
        "verdict": verdict,
        "fragment": str(target_fragment.relative_to(audit_root.parent)),
        "sidecar": str(target_sidecar.relative_to(audit_root.parent)),
        "model": model,
        "provider": provider,
    }


def recover_worker(audit_root: Path, worker: str) -> dict[str, Any]:
    rows, _ = load_manifest(audit_root)
    worker_dir = ensure_layout(audit_root, worker)
    assert worker_dir is not None
    actions: list[dict[str, str]] = []
    errors: list[str] = []
    manifest_files = {row["file"]: row["id"] for row in rows}
    for claimed in sorted(p for p in worker_dir.iterdir() if p.is_file() and p.name in manifest_files):
        filename = claimed.name
        fragment_id = manifest_files[filename]
        routed: list[tuple[str, Path, Path]] = []
        for verdict in VERDICTS:
            fragment = audit_root / verdict / filename
            sidecar = audit_root / verdict / sidecar_name(filename, verdict)
            if fragment.exists() or sidecar.exists():
                routed.append((verdict, fragment, sidecar))
        if len(routed) > 1:
            errors.append(f"{fragment_id}: multiple verdict residues")
            continue
        if routed:
            verdict, fragment, sidecar = routed[0]
            if sidecar.exists() and not fragment.exists():
                try:
                    rename_noreplace(claimed, fragment)
                    fsync_dir(worker_dir)
                    fsync_dir(fragment.parent)
                    actions.append({"id": fragment_id, "action": f"completed-{verdict}"})
                except Exception as exc:
                    errors.append(f"{fragment_id}: {exc}")
            else:
                errors.append(f"{fragment_id}: conflicting routed fragment state")
            continue
        root_target = audit_root / filename
        try:
            rename_noreplace(claimed, root_target)
            fsync_dir(worker_dir)
            fsync_dir(audit_root)
            actions.append({"id": fragment_id, "action": "requeued"})
        except Exception as exc:
            errors.append(f"{fragment_id}: {exc}")
    for staged in sorted(worker_dir.glob(".*.tmp.*")):
        try:
            staged.unlink()
            actions.append({"id": staged.name, "action": "removed-staged-sidecar"})
        except OSError as exc:
            errors.append(f"{staged.name}: {exc}")
    try:
        worker_dir.rmdir()
    except OSError:
        pass
    return {"status": "recovered" if not errors else "error", "worker": worker, "actions": actions, "errors": errors}


def audit_status(audit_root: Path) -> dict[str, Any]:
    rows, _ = load_manifest(audit_root)
    counts: dict[str, int] = {"root": 0, "claimed": 0, **{name: 0 for name in ALL_LOCATIONS}}
    errors: list[str] = []
    claimed_root = audit_root / "claimed"
    for row in rows:
        filename = row["file"]
        locations = existing_fragment_locations(audit_root, filename)
        if len(locations) != 1:
            errors.append(f"{row['id']}: {len(locations)} fragment locations")
            continue
        path = locations[0]
        if path.parent == audit_root:
            counts["root"] += 1
        elif path.parent.parent == claimed_root:
            counts["claimed"] += 1
        else:
            counts[path.parent.name] += 1
        if path.parent.name in VERDICTS:
            expected = path.parent / sidecar_name(filename, path.parent.name)
            if not expected.is_file():
                errors.append(f"{row['id']}: missing {path.parent.name} sidecar")
    counts["total"] = sum(counts[name] for name in ("root", "claimed", *ALL_LOCATIONS))
    return {"status": "ok" if not errors else "error", "counts": counts, "errors": errors}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-root", type=Path, default=Path(__file__).resolve().parents[1] / "audit")
    sub = parser.add_subparsers(dest="command", required=True)

    claim = sub.add_parser("claim")
    claim.add_argument("--worker", required=True)
    claim.add_argument("--rounds", type=int, default=5)

    finalize = sub.add_parser("finalize")
    finalize.add_argument("--worker", required=True)
    finalize.add_argument("--id", required=True)
    finalize.add_argument("--verdict", choices=VERDICTS, required=True)
    finalize.add_argument("--model", required=True)
    finalize.add_argument("--provider", required=True)
    finalize.add_argument("--evidence", required=True)

    recover = sub.add_parser("recover")
    recover.add_argument("--worker", required=True)

    sub.add_parser("status")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    audit_root = args.audit_root.resolve()
    try:
        if args.command == "claim":
            result = claim_one(audit_root, args.worker, args.rounds)
        elif args.command == "finalize":
            result = finalize_claim(audit_root, args.worker, args.id, args.verdict, args.model, args.provider, args.evidence)
        elif args.command == "recover":
            result = recover_worker(audit_root, args.worker)
        else:
            result = audit_status(audit_root)
        emit(**result)
        return 0 if result.get("status") not in {"error"} else 1
    except Exception as exc:
        emit(status="error", error=f"{type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
