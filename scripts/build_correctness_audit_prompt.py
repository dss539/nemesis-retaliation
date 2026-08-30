#!/usr/bin/env python3
"""Build byte-reproducible source-only correctness-audit prompts."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath

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


def source_only_forbidden_inventory() -> tuple[set[str], set[str]]:
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


def source_only_payload_failures(value, location: str = "<root>") -> list[str]:
    failures = []
    if isinstance(value, dict):
        for key, child in value.items():
            failures.extend(source_only_payload_failures(child, f"{location}/{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            failures.extend(source_only_payload_failures(child, f"{location}/{index}"))
    elif isinstance(value, str):
        forbidden_paths, forbidden_identifiers = source_only_forbidden_inventory()
        for token in sorted(forbidden_paths):
            if re.search(
                rf"(?<![A-Za-z0-9_.-]){re.escape(token)}",
                value,
            ):
                failures.append(f"source-only payload {location} contains forbidden path {token}")
        for identifier in sorted(forbidden_identifiers):
            if re.search(
                rf"(?<![A-Za-z0-9_]){re.escape(identifier)}(?![A-Za-z0-9_])",
                value,
            ):
                failures.append(
                    f"source-only payload {location} contains forbidden identifier {identifier}"
                )
    return failures


SOURCE_ONLY_FORBIDDEN_TOKENS = tuple(
    sorted(SOURCE_ONLY_FIXED_PATH_TOKENS | SOURCE_ONLY_FIXED_IDENTIFIERS)
)


def validate_source_only_json(path: Path) -> None:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_pairs)
    failures = source_only_payload_failures(value)
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
    validate_source_only_json(packet_path)
    payloads: list[tuple[str, Path]] = [("SOURCE PACKET", packet_path)]
    if mode == "blind":
        if completeness_path is None:
            raise ValueError("blind prompt requires completeness review")
        completeness_path = canonical_repo_file(completeness_path, AUDIT_DIR / "packets")
        validate_source_only_json(completeness_path)
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
