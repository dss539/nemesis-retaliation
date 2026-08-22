#!/usr/bin/env python3
"""Validate the extracted card-text corpus against live evidence and sources."""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

import card_text_evidence_registry as selected_evidence
import build_card_text_corpus as corpus_builder

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
CORPUS = EXTRACT / "card-text-corpus.json"
REGISTRY = EXTRACT / "selected-card-text-evidence.json"
PROGRESS = EXTRACT / "vision-progress.json"
QUEUE = EXTRACT / "low-confidence-review.json"
GLOSSARY = REPO / "docs/rules/icon-glossary.md"
REPORT = EXTRACT / "card-text-corpus-validation.json"
TOKEN_RE = re.compile(r"\[([^\]]+)\]")
ICON_ID_RE = re.compile(r"^- \*\*([A-Za-z][A-Za-z0-9]*)\*\* —")


def load(path: Path):
    return json.loads(path.read_text())


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)


def main() -> None:
    corpus = load(CORPUS)
    progress = load(PROGRESS)
    queue = load(QUEUE)
    known = {m.group(1) for line in GLOSSARY.read_text().splitlines() if (m := ICON_ID_RE.match(line))}
    failures = []
    try:
        resolution_payload, resolution_index = corpus_builder.semantic_icon_resolution_index(known)
    except (OSError, ValueError, TypeError) as exc:
        resolution_payload = None
        resolution_index = {}
        failures.append({"check": "semantic icon resolution registry schema", "error": str(exc)})
    try:
        registry = selected_evidence.load_registry(REGISTRY)
    except selected_evidence.RegistryError as exc:
        registry = None
        failures.append({"check": "selected evidence registry schema", "error": str(exc)})
    rows = corpus.get("records", [])
    paths = [row.get("sourcePath") for row in rows]
    ledger_cards = [row for row in progress["records"] if "/tree/cards/" in row["sourcePath"]]
    ledger_by_path = {row["sourcePath"]: row for row in ledger_cards}
    queue_card_paths = {row["sourcePath"] for row in queue["entries"] if "/tree/cards/" in row["sourcePath"]}
    if len(known) != 49:
        failures.append({"check": "glossary", "expected": 49, "actual": len(known)})
    if len(paths) != len(set(paths)):
        failures.append({"check": "unique corpus paths"})
    if paths != sorted(paths):
        failures.append({"check": "stable sorted corpus paths"})
    if set(paths) != set(ledger_by_path):
        failures.append({"check": "corpus/ledger path equality", "corpusOnly": sorted(set(paths)-set(ledger_by_path)), "ledgerOnly": sorted(set(ledger_by_path)-set(paths))})
    states = collections.Counter()
    readiness = collections.Counter()
    canonical_sidecars = set()
    deferred_corpus_paths = set()
    rules_text = 0
    for row in rows:
        path = row["sourcePath"]
        ledger = ledger_by_path.get(path)
        if ledger is None:
            continue
        source = REPO / path
        actual_sha = hashlib.sha256(source.read_bytes()).hexdigest() if source.is_file() else None
        if actual_sha != row.get("sourceSha256"):
            failures.append({"check": "source hash", "path": path, "expected": row.get("sourceSha256"), "actual": actual_sha})
        if row.get("ledgerStatus") != ledger.get("status"):
            failures.append({"check": "ledger status", "path": path})
        if ledger["status"] == "deferred":
            deferred_corpus_paths.add(path)
        state = row.get("extractionState")
        ready = row.get("rulesInformationReadiness")
        states[state] += 1
        readiness[ready] += 1
        if row.get("rulesTextPresent"):
            rules_text += 1
        token_set = {token for text in strings(row.get("printedData")) for token in TOKEN_RE.findall(text)}
        canonical = set((row.get("symbols") or {}).get("canonicalGlossaryTokens") or [])
        unresolved = set((row.get("symbols") or {}).get("unresolvedOrLocalTokens") or [])
        if canonical & unresolved or canonical | unresolved != token_set:
            failures.append({"check": "token partition", "path": path, "parsed": sorted(token_set), "canonical": sorted(canonical), "unresolved": sorted(unresolved)})
        if not canonical <= known or unresolved & known:
            failures.append({"check": "glossary partition", "path": path})
        if state == "verified-canonical":
            sidecar_path = (row.get("identity") or {}).get("sidecarPath")
            if not sidecar_path:
                failures.append({"check": "canonical sidecar path", "path": path})
            else:
                canonical_sidecars.add(sidecar_path)
                sidecar = load(REPO / sidecar_path)
                if row.get("printedData") != sidecar:
                    failures.append({"check": "canonical sidecar payload", "path": path, "sidecar": sidecar_path})
            if unresolved:
                failures.append({"check": "canonical unresolved token", "path": path})
        if state == "draft-full":
            printed = row.get("printedData") if isinstance(row.get("printedData"), dict) else {}
            rule_fragments = [
                printed.get(key) for key in ("body", "firstEffect", "secondEffect", "commandPanel", "reactionPanel")
                if isinstance(printed.get(key), str) and printed.get(key).strip()
            ]
            if not rule_fragments:
                failures.append({"check": "draft-full rules text", "path": path})
    expected_sidecars = {row["sidecarPath"] for row in ledger_cards if row.get("sidecarPath")}
    if canonical_sidecars != expected_sidecars:
        failures.append({"check": "canonical sidecar coverage", "missing": sorted(expected_sidecars-canonical_sidecars), "extra": sorted(canonical_sidecars-expected_sidecars)})
    if deferred_corpus_paths != queue_card_paths:
        failures.append({"check": "deferred card queue equality", "corpusOnly": sorted(deferred_corpus_paths-queue_card_paths), "queueOnly": sorted(queue_card_paths-deferred_corpus_paths)})
    corpus_by_tuple = {(row.get("sourcePath"), row.get("sourceSha256")): row for row in rows}
    for key, resolutions in resolution_index.items():
        source = REPO / key[0]
        if not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != key[1]:
            failures.append({"check": "semantic icon resolution source tuple", "sourceTuple": key})
            continue
        row = corpus_by_tuple.get(key)
        if row is None:
            failures.append({"check": "semantic icon resolution corpus tuple", "sourceTuple": key})
            continue
        actual = (row.get("evidence") or {}).get("semanticIconResolutions")
        if actual != resolutions:
            failures.append({"check": "semantic icon resolution corpus projection", "sourceTuple": key, "expected": resolutions, "actual": actual})
    unexpected_resolution_rows = sorted(
        key for key, row in corpus_by_tuple.items()
        if (row.get("evidence") or {}).get("semanticIconResolutions") is not None and key not in resolution_index
    )
    if unexpected_resolution_rows:
        failures.append({"check": "unregistered semantic icon resolutions", "sourceTuples": unexpected_resolution_rows})
    registry_entry_count = 0
    registry_run_count = 0
    if registry is not None:
        registry_entry_count = len(registry["entries"])
        registry_run_count = sum(len(entry["runs"]) for entry in registry["entries"])
        registry_by_tuple = {(entry["sourcePath"], entry["sourceSha256"]): entry for entry in registry["entries"]}
        selected_rows = {
            (row.get("sourcePath"), row.get("sourceSha256")): row
            for row in rows
            if row.get("selectedExtraction") is not None
            or (row.get("evidence") or {}).get("selectedExtraction") is not None
            or row.get("evidenceRuns") is not None
        }
        corpus_registry_keys = set(registry_by_tuple) & set(corpus_by_tuple)
        corpus_paths = {key[0] for key in corpus_by_tuple}
        mismatched_corpus_paths = sorted(
            key for key in registry_by_tuple
            if key[0] in corpus_paths and key not in corpus_by_tuple
        )
        if mismatched_corpus_paths:
            failures.append({
                "check": "selected evidence registry corpus-path SHA mismatch",
                "sourceTuples": mismatched_corpus_paths,
            })
        if corpus_registry_keys != set(selected_rows):
            failures.append({
                "check": "selected evidence registry/corpus intersection equality",
                "registryCorpusIntersectionOnly": sorted(corpus_registry_keys-set(selected_rows)),
                "corpusOnly": sorted(set(selected_rows)-corpus_registry_keys),
            })
        for key in sorted(corpus_registry_keys):
            entry = registry_by_tuple[key]
            row = corpus_by_tuple[key]
            projected = selected_evidence.project_entry(entry)
            if row.get("selectedExtraction") != projected["selectedExtraction"]:
                failures.append({"check": "selected extraction registry projection", "sourceTuple": key})
            if (row.get("evidence") or {}).get("selectedExtraction") != projected["evidenceSelectedExtraction"]:
                failures.append({"check": "evidence selected extraction registry projection", "sourceTuple": key})
            if row.get("evidenceRuns") != projected["evidenceRuns"]:
                failures.append({"check": "evidence runs registry projection", "sourceTuple": key})
            selected = row.get("selectedExtraction") or {}
            if (selected.get("sourcePath"), selected.get("sourceSha256")) != key:
                failures.append({"check": "selected extraction source tuple", "sourceTuple": key})
            for evidence_run in row.get("evidenceRuns") or []:
                if evidence_run.get("sourceSha256") != key[1]:
                    failures.append({"check": "evidence run source tuple", "sourceTuple": key, "runIdentity": evidence_run.get("runIdentity")})
        expected_metadata = {
            "selectedEvidenceRegistry": "assets/tts-mod/extract/selected-card-text-evidence.json",
            "selectedEvidenceRegistrySchemaVersion": registry["schemaVersion"],
            "selectedEvidenceRegistrySha256": selected_evidence.sha256_bytes(selected_evidence.canonical_json_bytes(registry)),
            "selectedEvidenceTupleDigest": selected_evidence.registry_tuple_digest(registry),
            "selectedEvidenceEntryCount": registry_entry_count,
            "selectedEvidenceRunCount": registry_run_count,
            "semanticIconResolutionRegistrySha256": selected_evidence.sha256_bytes(selected_evidence.canonical_json_bytes(resolution_payload)),
        }
        if corpus.get("metadata") != expected_metadata:
            failures.append({"check": "deterministic selected evidence metadata", "expected": expected_metadata, "actual": corpus.get("metadata")})
    recomputed = {
        "records": len(rows),
        "rulesTextPresent": rules_text,
        "extractionStates": dict(sorted(states.items())),
        "rulesInformationReadiness": dict(sorted(readiness.items())),
    }
    if corpus.get("counts") != recomputed:
        failures.append({"check": "embedded counts", "embedded": corpus.get("counts"), "recomputed": recomputed})
    report = {
        "schemaVersion": 1,
        "passed": not failures,
        "sourceProgressUpdatedAt": progress.get("updatedAt"),
        "sourceQueueUpdatedAt": queue.get("updatedAt"),
        "checks": {
            **recomputed,
            "sourceHashesVerified": len(rows),
            "glossaryIdentifiers": len(known),
            "canonicalSidecarsCovered": len(canonical_sidecars),
            "deferredCardQueueEntries": len(queue_card_paths),
            "selectedEvidenceRegistryEntries": registry_entry_count,
            "selectedEvidenceRegistryRuns": registry_run_count,
            "semanticIconResolutionSources": len(resolution_index),
            "semanticIconResolutions": sum(len(items) for items in resolution_index.values()),
        },
        "failureCount": len(failures),
        "failures": failures,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
