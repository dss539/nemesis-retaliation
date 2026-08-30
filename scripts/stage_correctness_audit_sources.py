#!/usr/bin/env python3
"""Stage and verify gitignored audit sources in an isolated worktree."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TREES = (
    Path("docs/rulebooks"),
    Path("assets/tts-mod/extract"),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def require_regular_tree(root: Path, relative: Path) -> list[Path]:
    tree = root / relative
    if not tree.is_dir() or tree.is_symlink():
        raise SystemExit(f"source tree missing or not a regular directory: {tree}")
    files: list[Path] = []
    for path in sorted(tree.rglob("*")):
        relative_to_tree = path.relative_to(tree)
        if "__pycache__" in relative_to_tree.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise SystemExit(f"source tree contains a symlink: {path}")
        if path.is_file():
            files.append(path)
    if not files:
        raise SystemExit(f"source tree is empty: {tree}")
    return files


def target_path(relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        raise SystemExit(f"noncanonical source-relative path: {relative}")
    target = ROOT / relative
    current = ROOT
    for part in relative.parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise SystemExit(f"target path contains a symlink: {current}")
    return target


def tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("cannot enumerate tracked worktree paths")
    return {
        value.decode("utf-8")
        for value in result.stdout.split(b"\0")
        if value
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source_root = args.source_root.resolve(strict=True)
    if not source_root.is_dir() or source_root.is_symlink():
        raise SystemExit("--source-root must be a regular directory")

    copied = 0
    checked = 0
    copied_bytes = 0
    tracked = tracked_paths()
    for tree in SOURCE_TREES:
        for source in require_regular_tree(source_root, tree):
            relative = source.relative_to(source_root)
            target = target_path(relative)
            source_hash = sha256(source)
            relative_posix = relative.as_posix()
            if relative_posix in tracked:
                if not target.is_file() or target.is_symlink():
                    raise SystemExit(f"tracked candidate source is missing: {relative_posix}")
                if sha256(target) != source_hash:
                    raise SystemExit(
                        f"tracked candidate differs from source root; refusing overwrite: {relative_posix}"
                    )
                checked += 1
                continue
            if args.check:
                if not target.is_file() or target.is_symlink():
                    raise SystemExit(f"staged source missing: {relative.as_posix()}")
                if sha256(target) != source_hash:
                    raise SystemExit(f"staged source hash mismatch: {relative.as_posix()}")
                checked += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and (not target.is_file() or target.is_symlink()):
                raise SystemExit(f"refusing non-regular target: {target}")
            if target.is_file() and sha256(target) == source_hash:
                checked += 1
                continue
            shutil.copy2(source, target)
            if sha256(target) != source_hash:
                raise SystemExit(f"copy verification failed: {relative.as_posix()}")
            copied += 1
            copied_bytes += source.stat().st_size

    print(
        json.dumps(
            {
                "sourceRoot": str(source_root),
                "worktreeRoot": str(ROOT),
                "mode": "check" if args.check else "stage",
                "copiedFiles": copied,
                "alreadyCurrentOrCheckedFiles": checked,
                "copiedBytes": copied_bytes,
                "sourceTrees": [path.as_posix() for path in SOURCE_TREES],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
