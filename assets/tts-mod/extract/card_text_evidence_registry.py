#!/usr/bin/env python3
"""Strict schema and deterministic projection for selected reviewed evidence."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
REGISTRY_STATUS = "selected-reviewed-evidence"
ENTRY_STATUS = "selected-evidence-deferred"
SUPPORTED_PROMOTION_DECISIONS = {"defer"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RUNTIME_KEYS = {
    "provider",
    "model",
    "reasoningEffort",
    "nativeImageRoute",
    "blindSessionId",
    "adjudicationSessionId",
    "auxiliaryVisionUsed",
    "qwenUsed",
    "ocrCanonicalEvidenceUsed",
    "modelDowngradeUsed",
}
RUN_KEYS = {
    "runIdentity",
    "runId",
    "workerId",
    "assetId",
    "assignmentSha256",
    "orderedTupleDigest",
    "runtime",
    "artifactPaths",
    "visibleText",
    "verifiedIconOccurrences",
    "unresolvedIconOccurrences",
    "canonicalTokensEmitted",
    "allMaterialTextReadable",
    "allMaterialIconsAuthoritativelyMatched",
    "promotionDecision",
    "decisionReasons",
    "conflictsWithPriorSnapshot",
}
ICON_OCCURRENCE_KEYS = {
    "cardLocation",
    "referenceLabel",
    "matchDecision",
    "canonicalToken",
    "closestAlternative",
    "visibleDiscriminator",
    "evidenceRun",
}
CONFLICT_KEYS = {"field", "priorValue", "currentStatus", "resolution"}
ARTIFACT_PATH_KEYS = {"blindObservationPath", "resultPath", "contactSheetPath"}


class RegistryError(ValueError):
    """Raised when the durable selected-evidence registry is invalid."""


def canonical_json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def stable_run_identity(run_id: str, worker_id: str, asset_id: str) -> str:
    return f"{run_id}/{worker_id}/{asset_id}"


def _fail(location: str, message: str) -> None:
    raise RegistryError(f"{location}: {message}")


def _exact_keys(value: Any, expected: set[str], location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(location, "must be an object")
    actual = set(value)
    if actual != expected:
        _fail(location, f"keys mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    return value


def _nonempty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(location, "must be a non-empty string")
    return value


def _string_list(value: Any, location: str, *, nonempty: bool = False, sorted_unique: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        _fail(location, "must be a list of non-empty strings")
    if nonempty and not value:
        _fail(location, "must not be empty")
    if sorted_unique and value != sorted(set(value)):
        _fail(location, "must be sorted and contain no duplicates")
    return value


def _validate_runtime(value: Any, location: str) -> dict[str, Any]:
    runtime = _exact_keys(value, RUNTIME_KEYS, location)
    for key in ("provider", "model", "reasoningEffort", "nativeImageRoute", "blindSessionId"):
        _nonempty_string(runtime[key], f"{location}.{key}")
    adjudication_session = runtime["adjudicationSessionId"]
    if adjudication_session is not None and (not isinstance(adjudication_session, str) or not adjudication_session):
        _fail(f"{location}.adjudicationSessionId", "must be null or a non-empty string")
    for key in ("auxiliaryVisionUsed", "qwenUsed", "ocrCanonicalEvidenceUsed", "modelDowngradeUsed"):
        if not isinstance(runtime[key], bool):
            _fail(f"{location}.{key}", "must be boolean")
    return runtime


def _validate_artifact_paths(value: Any, location: str) -> dict[str, Any]:
    paths = _exact_keys(value, ARTIFACT_PATH_KEYS, location)
    for key, path in paths.items():
        if path is not None and (not isinstance(path, str) or not path):
            _fail(f"{location}.{key}", "must be null or a non-empty string")
    return paths


def _validate_occurrences(value: Any, location: str, worker_id: str, *, verified: bool) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _fail(location, "must be a list")
    for index, item in enumerate(value):
        item_location = f"{location}[{index}]"
        occurrence = _exact_keys(item, ICON_OCCURRENCE_KEYS, item_location)
        for key in ("cardLocation", "referenceLabel", "matchDecision", "closestAlternative", "visibleDiscriminator", "evidenceRun"):
            _nonempty_string(occurrence[key], f"{item_location}.{key}")
        if occurrence["evidenceRun"] != worker_id:
            _fail(f"{item_location}.evidenceRun", "must equal workerId")
        token = occurrence["canonicalToken"]
        if verified:
            if occurrence["matchDecision"] != "match" or not isinstance(token, str) or not token:
                _fail(item_location, "verified occurrence requires matchDecision=match and a canonical token")
        else:
            if occurrence["matchDecision"] not in {"match", "no-match", "uncertain"} or token is not None:
                _fail(item_location, "unresolved occurrence requires a supported decision and null canonicalToken")
    return value


def _validate_conflicts(value: Any, location: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        _fail(location, "must be a list")
    for index, item in enumerate(value):
        conflict = _exact_keys(item, CONFLICT_KEYS, f"{location}[{index}]")
        for key in CONFLICT_KEYS:
            _nonempty_string(conflict[key], f"{location}[{index}].{key}")
    return value


def validate_run(run: Any, location: str = "run") -> dict[str, Any]:
    run = _exact_keys(run, RUN_KEYS, location)
    for key in ("runIdentity", "runId", "workerId", "assetId"):
        _nonempty_string(run[key], f"{location}.{key}")
    for key in ("assignmentSha256", "orderedTupleDigest"):
        if not isinstance(run[key], str) or not SHA256_RE.fullmatch(run[key]):
            _fail(f"{location}.{key}", "must be a lowercase SHA-256")
    expected_identity = stable_run_identity(run["runId"], run["workerId"], run["assetId"])
    if run["runIdentity"] != expected_identity:
        _fail(f"{location}.runIdentity", f"must equal {expected_identity!r}")
    _validate_runtime(run["runtime"], f"{location}.runtime")
    _validate_artifact_paths(run["artifactPaths"], f"{location}.artifactPaths")
    if not isinstance(run["visibleText"], dict) or not run["visibleText"]:
        _fail(f"{location}.visibleText", "must be a non-empty object")
    verified = _validate_occurrences(run["verifiedIconOccurrences"], f"{location}.verifiedIconOccurrences", run["workerId"], verified=True)
    _validate_occurrences(run["unresolvedIconOccurrences"], f"{location}.unresolvedIconOccurrences", run["workerId"], verified=False)
    tokens = _string_list(run["canonicalTokensEmitted"], f"{location}.canonicalTokensEmitted", sorted_unique=True)
    if tokens != sorted({item["canonicalToken"] for item in verified}):
        _fail(f"{location}.canonicalTokensEmitted", "must exactly match verified occurrence tokens")
    for key in ("allMaterialTextReadable", "allMaterialIconsAuthoritativelyMatched"):
        if not isinstance(run[key], bool):
            _fail(f"{location}.{key}", "must be boolean")
    if run["promotionDecision"] not in SUPPORTED_PROMOTION_DECISIONS:
        _fail(f"{location}.promotionDecision", f"unsupported status {run['promotionDecision']!r}")
    _string_list(run["decisionReasons"], f"{location}.decisionReasons", nonempty=True)
    _validate_conflicts(run["conflictsWithPriorSnapshot"], f"{location}.conflictsWithPriorSnapshot")
    return run


def validate_registry(doc: Any) -> dict[str, Any]:
    doc = _exact_keys(doc, {"schemaVersion", "status", "entries"}, "registry")
    if doc["schemaVersion"] != SCHEMA_VERSION:
        _fail("registry.schemaVersion", f"unsupported version {doc['schemaVersion']!r}")
    if doc["status"] != REGISTRY_STATUS:
        _fail("registry.status", f"unsupported status {doc['status']!r}")
    entries = doc["entries"]
    if not isinstance(entries, list):
        _fail("registry.entries", "must be a list")
    tuple_keys: set[tuple[str, str]] = set()
    paths: set[str] = set()
    run_identities: set[str] = set()
    order: list[tuple[str, str]] = []
    for entry_index, entry in enumerate(entries):
        location = f"registry.entries[{entry_index}]"
        entry = _exact_keys(entry, {"sourcePath", "sourceSha256", "status", "selectedRunIdentity", "runs"}, location)
        source_path = _nonempty_string(entry["sourcePath"], f"{location}.sourcePath")
        source_sha = entry["sourceSha256"]
        if not isinstance(source_sha, str) or not SHA256_RE.fullmatch(source_sha):
            _fail(f"{location}.sourceSha256", "must be a lowercase SHA-256")
        if entry["status"] != ENTRY_STATUS:
            _fail(f"{location}.status", f"unsupported status {entry['status']!r}")
        key = (source_path, source_sha)
        if key in tuple_keys:
            _fail(location, f"duplicate source tuple {key!r}")
        if source_path in paths:
            _fail(location, f"source path appears with multiple tuples: {source_path}")
        tuple_keys.add(key)
        paths.add(source_path)
        order.append(key)
        runs = entry["runs"]
        if not isinstance(runs, list) or not runs:
            _fail(f"{location}.runs", "must be a non-empty list")
        identities = []
        for run_index, run in enumerate(runs):
            run = validate_run(run, f"{location}.runs[{run_index}]")
            identity = run["runIdentity"]
            if identity in run_identities:
                _fail(f"{location}.runs[{run_index}].runIdentity", "duplicate stable run identity")
            run_identities.add(identity)
            identities.append(identity)
        if identities != sorted(identities) or len(identities) != len(set(identities)):
            _fail(f"{location}.runs", "must be sorted by unique runIdentity")
        if entry["selectedRunIdentity"] not in identities:
            _fail(f"{location}.selectedRunIdentity", "must identify exactly one stored run")
    if order != sorted(order):
        _fail("registry.entries", "must be sorted by exact source tuple")
    return doc


def load_registry(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError(f"cannot load registry {path}: {exc}") from exc
    return validate_registry(doc)


def registry_tuple_digest(doc: dict[str, Any]) -> str:
    tuples = [(entry["sourcePath"], entry["sourceSha256"], entry["selectedRunIdentity"]) for entry in doc["entries"]]
    return hashlib.sha256(json.dumps(tuples, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def selected_run(entry: dict[str, Any]) -> dict[str, Any]:
    return next(run for run in entry["runs"] if run["runIdentity"] == entry["selectedRunIdentity"])


def project_entry(entry: dict[str, Any]) -> dict[str, Any]:
    selected = selected_run(entry)
    artifacts = selected["artifactPaths"]
    overlay = {
        "overlayVersion": 1,
        "status": entry["status"],
        "runIdentity": selected["runIdentity"],
        "runId": selected["runId"],
        "workerId": selected["workerId"],
        "assetId": selected["assetId"],
        "sourcePath": entry["sourcePath"],
        "sourceSha256": entry["sourceSha256"],
        "runtime": selected["runtime"],
        "blindObservationPath": artifacts["blindObservationPath"],
        "resultPath": artifacts["resultPath"],
        "contactSheetPath": artifacts["contactSheetPath"],
        "visibleText": selected["visibleText"],
        "verifiedIconOccurrences": selected["verifiedIconOccurrences"],
        "unresolvedIconOccurrences": selected["unresolvedIconOccurrences"],
        "canonicalTokensEmitted": selected["canonicalTokensEmitted"],
        "allMaterialTextReadable": selected["allMaterialTextReadable"],
        "allMaterialIconsAuthoritativelyMatched": selected["allMaterialIconsAuthoritativelyMatched"],
        "promotionDecision": selected["promotionDecision"],
        "decisionReasons": selected["decisionReasons"],
        "conflictsWithPriorSnapshot": selected["conflictsWithPriorSnapshot"],
    }
    evidence_selected = {
        "runIdentity": selected["runIdentity"],
        "runId": selected["runId"],
        "workerId": selected["workerId"],
        "assetId": selected["assetId"],
        "resultPath": artifacts["resultPath"],
        "rawResultPath": artifacts["blindObservationPath"],
        "contactSheetPath": artifacts["contactSheetPath"],
        "promotionDecision": selected["promotionDecision"],
        "runtime": selected["runtime"],
    }
    evidence_runs = []
    for run in entry["runs"]:
        run_artifacts = run["artifactPaths"]
        evidence_runs.append({
            "runIdentity": run["runIdentity"],
            "runId": run["runId"],
            "workerId": run["workerId"],
            "assetId": run["assetId"],
            "sourceSha256": entry["sourceSha256"],
            "blindSessionId": run["runtime"]["blindSessionId"],
            "adjudicationSessionId": run["runtime"]["adjudicationSessionId"],
            "promotionDecision": run["promotionDecision"],
            "resultPath": run_artifacts["resultPath"],
            "selected": run["runIdentity"] == entry["selectedRunIdentity"],
        })
    return {
        "selectedExtraction": overlay,
        "evidenceSelectedExtraction": evidence_selected,
        "evidenceRuns": evidence_runs,
    }


def apply_registry(records: list[dict[str, Any]], registry: dict[str, Any]) -> None:
    """Project selected evidence onto corpus members without fabricating rows.

    The selected-evidence registry covers the full 532-image review queue, while
    this corpus intentionally contains only card/reference records. Registry
    entries outside the corpus remain globally validated and counted in corpus
    metadata, but they do not create synthetic corpus records.
    """
    validate_registry(registry)
    record_by_tuple: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        source_path = record.get("sourcePath")
        source_sha = record.get("sourceSha256")
        if not isinstance(source_path, str) or not isinstance(source_sha, str):
            raise RegistryError("generated corpus record has a malformed source tuple")
        key = (source_path, source_sha)
        if key in record_by_tuple:
            raise RegistryError(f"duplicate corpus source tuple while applying registry: {key!r}")
        record_by_tuple[key] = record
    record_paths = {record["sourcePath"] for record in records}
    for entry in registry["entries"]:
        key = (entry["sourcePath"], entry["sourceSha256"])
        record = record_by_tuple.get(key)
        if record is None:
            if entry["sourcePath"] in record_paths:
                raise RegistryError(
                    f"registry source path matches a corpus member but its SHA-256 does not: {key!r}"
                )
            continue
        projected = project_entry(entry)
        record["selectedExtraction"] = projected["selectedExtraction"]
        record.setdefault("evidence", {})["selectedExtraction"] = projected["evidenceSelectedExtraction"]
        record["evidenceRuns"] = projected["evidenceRuns"]


def atomic_write_registry(path: Path, registry: dict[str, Any]) -> None:
    validate_registry(registry)
    data = canonical_json_bytes(registry)
    if path.is_file() and path.read_bytes() == data:
        return
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
