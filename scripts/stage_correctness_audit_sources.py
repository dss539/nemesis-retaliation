#!/usr/bin/env python3
"""Stage and verify gitignored audit sources in an isolated worktree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import stat
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_TREES = (
    Path("docs/rulebooks"),
    Path("assets/tts-mod/extract"),
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def open_directory(root: Path, parts: tuple[str, ...], *, create: bool = False) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(root, flags)
    try:
        for part in parts:
            if create:
                try:
                    os.mkdir(part, mode=0o755, dir_fd=fd)
                except FileExistsError:
                    pass
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except Exception:
        os.close(fd)
        raise


def read_regular_file(root: Path, relative: Path, label: str) -> tuple[bytes, int]:
    parent_fd = None
    file_fd = None
    try:
        parent_fd = open_directory(root, relative.parts[:-1])
        file_fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise SystemExit(f"{label} is not a regular file: {relative.as_posix()}")
        chunks = []
        while chunk := os.read(file_fd, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(file_fd)
        current = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
        stable = (
            before.st_dev,
            before.st_ino,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        ) == (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        if not stable or (current.st_dev, current.st_ino) != (after.st_dev, after.st_ino):
            raise SystemExit(f"{label} changed while being read: {relative.as_posix()}")
        return b"".join(chunks), stat.S_IMODE(after.st_mode)
    except FileNotFoundError as exc:
        raise SystemExit(f"{label} missing: {relative.as_posix()}") from exc
    except OSError as exc:
        raise SystemExit(f"cannot safely read {label}: {relative.as_posix()}: {exc}") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if parent_fd is not None:
            os.close(parent_fd)


def read_regular_file_if_present(
    root: Path,
    relative: Path,
    label: str,
) -> tuple[bytes, int] | None:
    try:
        return read_regular_file(root, relative, label)
    except SystemExit as exc:
        if str(exc).startswith(f"{label} missing:"):
            return None
        raise


def write_regular_file_atomic(relative: Path, data: bytes, mode: int) -> None:
    parent_fd = open_directory(ROOT, relative.parts[:-1], create=True)
    temporary_name = f".{relative.name}.tmp-{os.getpid()}-{secrets.token_hex(8)}"
    temp_fd = None
    try:
        temp_fd = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            mode & 0o777,
            dir_fd=parent_fd,
        )
        view = memoryview(data)
        while view:
            written = os.write(temp_fd, view)
            view = view[written:]
        os.fchmod(temp_fd, mode & 0o777)
        os.fsync(temp_fd)
        os.close(temp_fd)
        temp_fd = None
        try:
            current = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            current = None
        if current is not None and not stat.S_ISREG(current.st_mode):
            raise SystemExit(
                f"refusing non-regular or symlink target: {(ROOT / relative)}"
            )
        os.replace(
            temporary_name,
            relative.name,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
        )
        os.fsync(parent_fd)
    finally:
        if temp_fd is not None:
            os.close(temp_fd)
        try:
            os.unlink(temporary_name, dir_fd=parent_fd)
        except FileNotFoundError:
            pass
        os.close(parent_fd)


def require_regular_tree(root: Path, relative: Path) -> list[Path]:
    tree = root / relative
    reject_symlink_components(tree, "source tree")
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


def reject_symlink_components(path: Path, label: str) -> None:
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise SystemExit(f"{label} contains a symlink component: {current}")


def target_path(relative: Path) -> Path:
    if (
        relative.is_absolute()
        or "\\" in relative.as_posix()
        or ".." in relative.parts
        or "." in relative.parts
    ):
        raise SystemExit(f"noncanonical source-relative path: {relative}")
    target = ROOT / relative
    current = ROOT
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
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

    source_argument = args.source_root.expanduser()
    reject_symlink_components(source_argument, "--source-root")
    source_root = source_argument.resolve(strict=True)
    if not source_root.is_dir() or source_root.is_symlink():
        raise SystemExit("--source-root must be a regular directory")

    copied = 0
    checked = 0
    copied_bytes = 0
    tracked = tracked_paths()
    for tree in SOURCE_TREES:
        for source in require_regular_tree(source_root, tree):
            relative = source.relative_to(source_root)
            target_path(relative)
            source_data, source_mode = read_regular_file(
                source_root,
                relative,
                "candidate source",
            )
            source_hash = sha256_bytes(source_data)
            relative_posix = relative.as_posix()
            current = read_regular_file_if_present(ROOT, relative, "staged target")
            if relative_posix in tracked:
                if current is None:
                    raise SystemExit(f"tracked candidate source is missing: {relative_posix}")
                if sha256_bytes(current[0]) != source_hash:
                    raise SystemExit(
                        f"tracked candidate differs from source root; refusing overwrite: {relative_posix}"
                    )
                checked += 1
                continue
            if args.check:
                if current is None:
                    raise SystemExit(f"staged source missing: {relative_posix}")
                if sha256_bytes(current[0]) != source_hash:
                    raise SystemExit(f"staged source hash mismatch: {relative_posix}")
                checked += 1
                continue
            if current is not None and sha256_bytes(current[0]) == source_hash:
                checked += 1
                continue
            write_regular_file_atomic(relative, source_data, source_mode)
            verified, _ = read_regular_file(ROOT, relative, "staged target")
            if sha256_bytes(verified) != source_hash:
                raise SystemExit(f"copy verification failed: {relative_posix}")
            copied += 1
            copied_bytes += len(source_data)

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
