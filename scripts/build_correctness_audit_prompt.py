#!/usr/bin/env python3
"""Build byte-reproducible source-only correctness-audit prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "docs/qa/implementation-readiness/correctness-audit"
INSTRUCTION_PATHS = {
    "completeness": AUDIT_DIR / "prompts/packet-completeness-instructions.txt",
    "blind": AUDIT_DIR / "prompts/blind-derivation-instructions.txt",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_repo_file(path: Path, parent: Path) -> Path:
    path = path if path.is_absolute() else ROOT / path
    try:
        relative = path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"path escapes repository: {path}") from exc
    lexical = PurePosixPath(relative.as_posix())
    if (
        "\\" in relative.as_posix()
        or lexical.is_absolute()
        or any(part in {".", ".."} for part in lexical.parts)
    ):
        raise ValueError(f"noncanonical path: {path}")
    current = ROOT
    for part in lexical.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink path component: {path}")
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(parent.resolve())
    except ValueError as exc:
        raise ValueError(f"path is outside required root {parent}: {path}") from exc
    if not resolved.is_file():
        raise ValueError(f"file missing: {path}")
    return path


def framed_section(label: str, path: Path) -> bytes:
    data = path.read_bytes()
    try:
        data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"prompt payload is not UTF-8: {path}") from exc
    relative = path.relative_to(ROOT).as_posix()
    prefix = f"\n=== BEGIN {label} | {relative} | {len(data)} bytes | sha256:{sha256(data)} ===\n".encode()
    suffix = f"\n=== END {label} ===\n".encode()
    return prefix + data + (b"" if data.endswith(b"\n") else b"\n") + suffix


def canonical_prompt_bytes(
    mode: str,
    packet_path: Path,
    completeness_path: Path | None = None,
) -> bytes:
    if mode not in INSTRUCTION_PATHS:
        raise ValueError(f"unknown prompt mode: {mode}")
    instruction_path = canonical_repo_file(INSTRUCTION_PATHS[mode], AUDIT_DIR / "prompts")
    packet_path = canonical_repo_file(packet_path, AUDIT_DIR / "packets")
    payloads: list[tuple[str, Path]] = [("SOURCE PACKET", packet_path)]
    if mode == "blind":
        if completeness_path is None:
            raise ValueError("blind prompt requires completeness review")
        completeness_path = canonical_repo_file(completeness_path, AUDIT_DIR / "packets")
        payloads.append(("ACCEPTED COMPLETENESS REVIEW", completeness_path))
    elif completeness_path is not None:
        raise ValueError("completeness prompt does not accept completeness review")

    header = {
        "schemaVersion": 1,
        "recordType": "stage-1-canonical-review-prompt",
        "mode": mode,
        "instructionsPath": instruction_path.relative_to(ROOT).as_posix(),
        "instructionsSha256": sha256(instruction_path.read_bytes()),
        "payloads": [
            {
                "label": label,
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(path.read_bytes()),
            }
            for label, path in payloads
        ],
    }
    output = (json.dumps(header, indent=2, ensure_ascii=False) + "\n").encode()
    output += framed_section("FIXED INSTRUCTIONS", instruction_path)
    for label, path in payloads:
        output += framed_section(label, path)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=sorted(INSTRUCTION_PATHS), required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--completeness", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        output.resolve(strict=False).relative_to((AUDIT_DIR / "packets" / "prompts").resolve())
    except ValueError as exc:
        raise SystemExit("output must be under correctness-audit/packets/prompts") from exc
    expected = canonical_prompt_bytes(args.mode, args.packet, args.completeness)
    if args.check:
        if not output.is_file() or output.read_bytes() != expected:
            raise SystemExit("canonical audit prompt is stale")
        print(f"canonical audit prompt is current: {output.relative_to(ROOT)}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    print(json.dumps({"output": output.relative_to(ROOT).as_posix(), "sha256": sha256(expected), "mode": args.mode}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
