#!/usr/bin/env python3
"""Build byte-reproducible source-only correctness-audit prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import stat
from pathlib import Path, PurePosixPath

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - exercised by the documented runner
    raise SystemExit(
        "jsonschema is required; run with uv and requirements-audit.txt"
    ) from exc

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "docs/qa/implementation-readiness/correctness-audit"
INSTRUCTION_PATHS = {
    "completeness": AUDIT_DIR / "prompts/packet-completeness-instructions.txt",
    "blind": AUDIT_DIR / "prompts/blind-derivation-instructions.txt",
}


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key in prompt payload: {key}")
        result[key] = value
    return result


SOURCE_ONLY_FIXED_PATH_TOKENS = {
    "docs/rules/00-foundations.md",
    "docs/rules/01-round-and-turns.md",
    "docs/rules/02-character-actions.md",
    "docs/rules/03-intruders-and-survival.md",
    "docs/rules/04-items-and-equipment.md",
    "docs/rules/semantics/",
    "docs/rules/ontology/",
    "docs/rules/vocabulary/",
    "docs/rules/implementation-readiness.md",
    "docs/design/",
    "archive/design/",
    "index.html",
    "js/",
    "css/",
}
SOURCE_ONLY_FIXED_IDENTIFIERS = {
    "downstreamPath",
    "extractionPath",
    "revealedArtifacts",
    "semanticRecordIds",
    "questionIds",
    "conflictIds",
    "discrepancies",
    "blindDerivationRef",
    "comparisonRef",
    "verificationReviews",
    "repairPaths",
    "physicalClass",
    "batchDisposition",
    "equipmentStratum",
}
SOURCE_ONLY_SHARED_IDENTIFIERS = {
    "schemaVersion",
    "recordType",
    "auditUnitId",
    "sealedAtUtc",
    "sealedAtGitHead",
    "reviewer",
    "reviewId",
    "kind",
    "reviewerId",
    "provider",
    "requestedModel",
    "responseModel",
    "requestedReasoning",
    "requestMode",
    "promptPath",
    "promptSha256",
    "responsePath",
    "responseSha256",
    "thinkingRetained",
    "path",
    "sha256",
    "role",
    "evidenceRefs",
}
ALLOWED_SOURCE_PATH_PREFIXES = (
    "docs/rulebooks/",
    "docs/rules/source-extraction/",
    "assets/tts-mod/extract/",
)
SOURCE_ONLY_SCHEMA_NAMES = {
    "source-packet": "source-packet.schema.json",
    "packet-completeness-review": "packet-completeness-review.schema.json",
}


def schema_property_names(value) -> set[str]:
    names: set[str] = set()
    if isinstance(value, dict):
        properties = value.get("properties")
        if isinstance(properties, dict):
            names.update(str(key) for key in properties)
        for child in value.values():
            names.update(schema_property_names(child))
    elif isinstance(value, list):
        for child in value:
            names.update(schema_property_names(child))
    return names


def source_only_forbidden_key_inventory() -> tuple[set[str], set[str]]:
    forbidden_paths = set(SOURCE_ONLY_FIXED_PATH_TOKENS)
    forbidden_identifiers = set(SOURCE_ONLY_FIXED_IDENTIFIERS)
    manifest_path = AUDIT_DIR / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(
            manifest_path.read_text(encoding="utf-8"),
            object_pairs_hook=strict_pairs,
        )
        for section in (
            "frozenSemanticHashes",
            "frozenConciseRuleHashes",
            "selectionInputHashes",
        ):
            mapping = manifest.get(section, {})
            if isinstance(mapping, dict):
                forbidden_paths.update(
                    str(path)
                    for path in mapping
                    if not str(path).startswith(ALLOWED_SOURCE_PATH_PREFIXES)
                )
        for unit in manifest.get("units", []):
            if not isinstance(unit, dict):
                continue
            for field in ("downstreamPath", "extractionPath"):
                path = unit.get(field)
                if isinstance(path, str) and not path.startswith(ALLOWED_SOURCE_PATH_PREFIXES):
                    forbidden_paths.add(path)
    for schema_name in ("comparison.schema.json", "audit-result.schema.json"):
        schema_path = AUDIT_DIR / schema_name
        if schema_path.is_file():
            schema = json.loads(
                schema_path.read_text(encoding="utf-8"),
                object_pairs_hook=strict_pairs,
            )
            forbidden_identifiers.update(schema_property_names(schema))
    forbidden_identifiers.difference_update(SOURCE_ONLY_SHARED_IDENTIFIERS)
    return forbidden_paths, forbidden_identifiers


def source_only_forbidden_inventory() -> tuple[set[str], set[str]]:
    return source_only_forbidden_key_inventory()


def identifier_occurs(value: str, identifier: str) -> bool:
    return bool(
        re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(identifier)}(?![A-Za-z0-9_])",
            value,
        )
    )


def source_only_payload_failures(
    value,
    location: str = "<root>",
    *,
    allowed_identifier_keys: frozenset[str] = frozenset(),
) -> list[str]:
    failures = []
    if isinstance(value, dict):
        forbidden_paths, forbidden_identifiers = source_only_forbidden_key_inventory()
        for key, child in value.items():
            if key not in allowed_identifier_keys:
                for identifier in sorted(forbidden_identifiers):
                    if identifier_occurs(key, identifier):
                        failures.append(
                            f"source-only payload {location} contains forbidden identifier key {identifier}"
                        )
            if any(path_token in key for path_token in forbidden_paths):
                failures.append(
                    f"source-only payload {location} contains forbidden path key {key}"
                )
            failures.extend(
                source_only_payload_failures(
                    child,
                    f"{location}/{key}",
                    allowed_identifier_keys=allowed_identifier_keys,
                )
            )
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(
                source_only_payload_failures(
                    child,
                    f"{location}/{index}",
                    allowed_identifier_keys=allowed_identifier_keys,
                )
            )
    elif isinstance(value, str):
        forbidden_paths, forbidden_identifiers = source_only_forbidden_inventory()
        for token in sorted(forbidden_paths):
            if re.search(
                rf"(?<![A-Za-z0-9_.-]){re.escape(token)}",
                value,
            ):
                failures.append(f"source-only payload {location} contains forbidden path {token}")
        for identifier in sorted(forbidden_identifiers):
            if identifier_occurs(value, identifier):
                failures.append(
                    f"source-only payload {location} contains forbidden identifier {identifier}"
                )
    return failures


SOURCE_ONLY_FORBIDDEN_TOKENS = tuple(
    sorted(SOURCE_ONLY_FIXED_PATH_TOKENS | SOURCE_ONLY_FIXED_IDENTIFIERS)
)


def _open_repo_directory(parts: tuple[str, ...], *, create: bool = False) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(ROOT, flags)
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


def read_repo_regular_bytes(path: Path) -> bytes:
    try:
        relative = path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"path escapes repository: {path}") from exc
    parent_fd = _open_repo_directory(relative.parts[:-1])
    file_fd = None
    try:
        file_fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_fd)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise ValueError(f"file is not regular: {path}")
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
            raise ValueError(f"file changed while being read: {path}")
        return b"".join(chunks)
    except OSError as exc:
        raise ValueError(f"cannot safely read regular file: {path}: {exc}") from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(parent_fd)


def validate_source_only_json(data: bytes, schema_name: str) -> None:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=strict_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid source-only JSON: {exc}") from exc
    schema_path = AUDIT_DIR / SOURCE_ONLY_SCHEMA_NAMES[schema_name]
    schema = json.loads(
        read_repo_regular_bytes(schema_path).decode("utf-8"),
        object_pairs_hook=strict_pairs,
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        detail = "; ".join(error.message for error in errors)
        raise ValueError(f"source-only {schema_name} schema validation failed: {detail}")
    failures = source_only_payload_failures(
        value,
        allowed_identifier_keys=frozenset(schema_property_names(schema)),
    )
    if failures:
        raise ValueError("; ".join(failures))


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


def framed_section(label: str, path: Path, data: bytes) -> bytes:
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
    instruction_data = read_repo_regular_bytes(instruction_path)
    packet_path = canonical_repo_file(packet_path, AUDIT_DIR / "packets")
    packet_data = read_repo_regular_bytes(packet_path)
    validate_source_only_json(packet_data, "source-packet")
    payloads: list[tuple[str, Path, bytes]] = [("SOURCE PACKET", packet_path, packet_data)]
    if mode == "blind":
        if completeness_path is None:
            raise ValueError("blind prompt requires completeness review")
        completeness_path = canonical_repo_file(completeness_path, AUDIT_DIR / "packets")
        completeness_data = read_repo_regular_bytes(completeness_path)
        validate_source_only_json(completeness_data, "packet-completeness-review")
        payloads.append(("ACCEPTED COMPLETENESS REVIEW", completeness_path, completeness_data))
    elif completeness_path is not None:
        raise ValueError("completeness prompt does not accept completeness review")

    header = {
        "schemaVersion": 1,
        "recordType": "stage-1-canonical-review-prompt",
        "mode": mode,
        "instructionsPath": instruction_path.relative_to(ROOT).as_posix(),
        "instructionsSha256": sha256(instruction_data),
        "payloads": [
            {
                "label": label,
                "path": path.relative_to(ROOT).as_posix(),
                "sha256": sha256(data),
            }
            for label, path, data in payloads
        ],
    }
    output = (json.dumps(header, indent=2, ensure_ascii=False) + "\n").encode()
    output += framed_section("FIXED INSTRUCTIONS", instruction_path, instruction_data)
    for label, path, data in payloads:
        output += framed_section(label, path, data)
    return output


def write_repo_file_atomic(path: Path, data: bytes) -> None:
    relative = path.relative_to(ROOT)
    parent_fd = _open_repo_directory(relative.parts[:-1], create=True)
    temporary_name = f".{relative.name}.tmp-{os.getpid()}-{secrets.token_hex(8)}"
    temp_fd = None
    try:
        temp_fd = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_fd,
        )
        view = memoryview(data)
        while view:
            written = os.write(temp_fd, view)
            view = view[written:]
        os.fsync(temp_fd)
        os.close(temp_fd)
        temp_fd = None
        try:
            existing = os.stat(relative.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and not stat.S_ISREG(existing.st_mode):
            raise ValueError(f"refusing non-regular or symlink output: {path}")
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


def canonical_output_path(value: str) -> Path:
    lexical = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or lexical.is_absolute()
        or lexical.as_posix() != value
        or any(part in {".", ".."} for part in lexical.parts)
    ):
        raise ValueError("output is not a canonical repository-relative POSIX path")
    output = ROOT.joinpath(*lexical.parts)
    prompt_root = AUDIT_DIR / "packets" / "prompts"
    try:
        output.relative_to(prompt_root)
    except ValueError as exc:
        raise ValueError("output must be under correctness-audit/packets/prompts") from exc
    current = ROOT
    for part in lexical.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"output path contains a symlink component: {value}")
    try:
        output.resolve(strict=False).relative_to(prompt_root.resolve())
    except ValueError as exc:
        raise ValueError("output must resolve under correctness-audit/packets/prompts") from exc
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=sorted(INSTRUCTION_PATHS), required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--completeness", type=Path)
    parser.add_argument("--output", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        output = canonical_output_path(args.output)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    expected = canonical_prompt_bytes(args.mode, args.packet, args.completeness)
    if args.check:
        try:
            current = read_repo_regular_bytes(output)
        except ValueError:
            current = None
        if current != expected:
            raise SystemExit("canonical audit prompt is stale")
        print(f"canonical audit prompt is current: {output.relative_to(ROOT)}")
        return 0
    write_repo_file_atomic(output, expected)
    print(json.dumps({"output": output.relative_to(ROOT).as_posix(), "sha256": sha256(expected), "mode": args.mode}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
