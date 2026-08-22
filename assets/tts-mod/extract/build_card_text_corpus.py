#!/usr/bin/env python3
"""Build a provenance-rich, non-canonical corpus of all in-scope card text."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import analyze_card_extraction_coverage as coverage
import card_text_evidence_registry as selected_evidence

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
PROGRESS = EXTRACT / "vision-progress.json"
QUEUE = EXTRACT / "low-confidence-review.json"
GLOSSARY = REPO / "docs/rules/icon-glossary.md"
REGISTRY = EXTRACT / "selected-card-text-evidence.json"
SEMANTIC_RESOLUTIONS = REPO / "docs/qa/card-symbol-semantic-resolutions.json"
DEFAULT_OUTPUT = EXTRACT / "card-text-corpus.json"
TOKEN_RE = re.compile(r"\[([^\]]+)\]")
ICON_ID_RE = re.compile(r"^- \*\*([A-Za-z][A-Za-z0-9]*)\*\* —")


def load(path: Path):
    return json.loads(path.read_text())


def glossary_ids() -> set[str]:
    result = set()
    for line in GLOSSARY.read_text().splitlines():
        match = ICON_ID_RE.match(line)
        if match:
            result.add(match.group(1))
    if len(result) != 50:
        raise ValueError(f"expected 50 approved icon identifiers (49 page-40 plus Number of Characters), found {len(result)}")
    return result


def all_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)


def semantic_icon_resolution_index(known: set[str]) -> tuple[dict[str, Any], dict[tuple[str, str], list[dict[str, Any]]]]:
    payload = load(SEMANTIC_RESOLUTIONS)
    if payload.get("schemaVersion") != 1 or not isinstance(payload.get("entries"), list):
        raise ValueError("invalid semantic icon resolution registry")
    index: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for entry in payload["entries"]:
        canonical = entry.get("canonicalToken")
        if canonical not in known:
            raise ValueError(f"semantic icon resolution uses unknown canonical token: {canonical}")
        for source in entry.get("sources") or []:
            key = (source.get("sourcePath"), source.get("sourceSha256"))
            if not all(isinstance(value, str) and value for value in key):
                raise ValueError(f"semantic icon resolution has invalid source tuple: {entry.get('id')}")
            resolution = {
                "resolutionId": entry.get("id"),
                "canonicalToken": canonical,
                "resolutionType": entry.get("resolutionType"),
                "literalArt": entry.get("literalArt"),
                "literalTokens": list(source.get("literalTokens") or []),
                "selectedOccurrenceIndexes": list(source.get("selectedOccurrenceIndexes") or []),
                "evidencePath": "docs/qa/card-symbol-semantic-resolutions.json",
            }
            index.setdefault(key, []).append(resolution)
    return payload, index


def normalize_semantic_icons(value: Any, resolutions: list[dict[str, Any]]) -> Any:
    if isinstance(value, str):
        for resolution in resolutions:
            replacement = f"[{resolution['canonicalToken']}]"
            for literal in resolution["literalTokens"]:
                value = value.replace(f"[{literal}]", replacement)
        return value
    if isinstance(value, list):
        return [normalize_semantic_icons(item, resolutions) for item in value]
    if isinstance(value, dict):
        return {key: normalize_semantic_icons(item, resolutions) for key, item in value.items()}
    return value


def normalized_family(path: str) -> str:
    tail = path.split("/tree/cards/", 1)[1]
    parts = tail.split("/")
    head = parts[0]
    candidate = parts[1] if len(parts) > 1 else "unknown"
    candidate = Path(candidate).stem
    candidate = re.sub(r"-\d+(?:_cards)?$", "", candidate)
    if head == "character":
        return f"character/{candidate}"
    if head == "game":
        return f"game/{candidate}"
    return head


def canonical_payload(record: dict) -> tuple[dict, dict]:
    sidecar_path = record.get("sidecarPath")
    if not sidecar_path:
        return {}, {}
    sidecar = load(REPO / sidecar_path)
    slug = Path(sidecar_path).stem
    identity = {
        "canonicalSlug": slug,
        "titleFromCanonicalSlug": slug.replace("-", " "),
        "canonicalPath": record.get("canonicalPath"),
        "sidecarPath": sidecar_path,
    }
    return sidecar, identity


def build_payload(*, registry: dict[str, Any] | None = None, registry_path: Path = REGISTRY) -> dict[str, Any]:
    progress = load(PROGRESS)
    queue = load(QUEUE)
    if registry is None:
        registry = selected_evidence.load_registry(registry_path)
    else:
        selected_evidence.validate_registry(registry)
    deferred = {entry["sourcePath"]: entry for entry in queue["entries"]}
    known = glossary_ids()
    resolution_payload, resolution_index = semantic_icon_resolution_index(known)
    records = []
    readiness = collections.Counter()
    extraction_states = collections.Counter()
    rules_bearing = 0
    for ledger in progress["records"]:
        source_path = ledger["sourcePath"]
        if "/tree/cards/" not in source_path:
            continue
        source_sha = ledger.get("sha256") or ledger.get("sourceSha256")
        source = REPO / source_path
        if not source.is_file():
            raise FileNotFoundError(source)
        if hashlib.sha256(source.read_bytes()).hexdigest() != source_sha:
            raise ValueError(f"source hash mismatch: {source_path}")
        queue_entry = deferred.get(source_path)
        icon_resolutions = resolution_index.get((source_path, source_sha), [])
        manual_review = ledger.get("manualReview")
        identity = {}
        if ledger["status"] == "complete":
            text_data, identity = canonical_payload(ledger)
            if text_data:
                extraction_state = "verified-canonical"
                text_evidence = "human-reviewed or supervisor-validated canonical sidecar"
            else:
                result = {}
                result_path = (ledger.get("vision") or {}).get("resultPath")
                if result_path and (REPO / result_path).is_file():
                    result = load(REPO / result_path)
                parsed = result.get("parsed") if isinstance(result, dict) else None
                text_data = parsed if isinstance(parsed, dict) else {}
                extraction_state = "complete-non-rules-or-reference"
                text_evidence = ledger.get("completionBasis")
            uncertainties = []
            reason = None
            vision = ledger.get("vision") or {}
        else:
            if queue_entry is None:
                raise ValueError(f"deferred card missing queue entry: {source_path}")
            manual_review = queue_entry.get("manualReview") or manual_review
            text_data = queue_entry.get("visibleText")
            if text_data is None:
                text_data = queue_entry.get("semanticRead") or {}
            extraction_state, _ = coverage.extraction_state(queue_entry)
            text_evidence = "native vision draft; not canonical promotion"
            uncertainties = queue_entry.get("uncertainties") or []
            reason = queue_entry.get("reasonSkipped")
            vision = queue_entry.get("vision") or {}
        text_data = normalize_semantic_icons(text_data, icon_resolutions)
        strings = list(all_strings(text_data))
        tokens = sorted(set(token for text in strings for token in TOKEN_RE.findall(text)))
        canonical_tokens = sorted(token for token in tokens if token in known)
        unresolved_tokens = sorted(token for token in tokens if token not in known)
        rules_text_fragments = []
        if isinstance(text_data, dict):
            for key in ("body", "firstEffect", "secondEffect", "commandPanel", "reactionPanel"):
                value = text_data.get(key)
                if isinstance(value, str) and value.strip():
                    rules_text_fragments.append(value)
        body_present = bool(rules_text_fragments)
        if body_present:
            rules_bearing += 1
        if extraction_state == "verified-canonical":
            rules_readiness = "canonical"
        elif extraction_state == "draft-full" and not unresolved_tokens:
            rules_readiness = "draft-text-complete"
        elif extraction_state == "draft-full":
            rules_readiness = "draft-text-complete-symbols-unresolved"
        elif extraction_state == "draft-partial":
            rules_readiness = "draft-partial"
        elif extraction_state == "no-transcription":
            rules_readiness = "missing-transcription"
        else:
            rules_readiness = "not-rules-bearing-or-reference"
        readiness[rules_readiness] += 1
        extraction_states[extraction_state] += 1
        records.append({
            "sourcePath": source_path,
            "sourceSha256": source_sha,
            "sourceKind": ledger.get("sourceKind"),
            "componentFamily": normalized_family(source_path),
            "ledgerStatus": ledger["status"],
            "extractionState": extraction_state,
            "rulesInformationReadiness": rules_readiness,
            "rulesTextPresent": body_present,
            "identity": identity,
            "printedData": text_data,
            "symbols": {
                "canonicalGlossaryTokens": canonical_tokens,
                "unresolvedOrLocalTokens": unresolved_tokens,
            },
            "uncertainties": uncertainties,
            "canonicalPromotionBlocker": reason,
            "evidence": {
                "textBasis": text_evidence,
                "visionProvider": vision.get("provider"),
                "visionModel": vision.get("model"),
                "reasoningEffort": vision.get("reasoningEffort"),
                "workerId": vision.get("workerId"),
                "sessionId": vision.get("sessionId"),
                "resultPath": vision.get("resultPath"),
                "rawResultPath": vision.get("rawResultPath"),
                "ledgerPath": "assets/tts-mod/extract/vision-progress.json",
                "queuePath": "assets/tts-mod/extract/low-confidence-review.json" if ledger["status"] == "deferred" else None,
                **({"manualReview": manual_review} if manual_review else {}),
                **({"semanticIconResolutions": icon_resolutions} if icon_resolutions else {}),
            },
        })
    records.sort(key=lambda row: row["sourcePath"])
    selected_evidence.apply_registry(records, registry)
    registry_bytes = selected_evidence.canonical_json_bytes(registry)
    payload = {
        "schemaVersion": 1,
        "status": "extracted evidence corpus; canonical and draft states are explicitly separated",
        "generatedFrom": {
            "visionProgressUpdatedAt": progress.get("updatedAt"),
            "reviewQueueUpdatedAt": queue.get("updatedAt"),
            "iconGlossary": "docs/rules/icon-glossary.md",
            "iconGlossaryIdentifierCount": len(known),
            "semanticIconResolutions": "docs/qa/card-symbol-semantic-resolutions.json",
            "semanticIconResolutionSourceCount": len(resolution_index),
            "semanticIconResolutionCount": sum(len(rows) for rows in resolution_index.values()),
        },
        "metadata": {
            "selectedEvidenceRegistry": "assets/tts-mod/extract/selected-card-text-evidence.json",
            "selectedEvidenceRegistrySchemaVersion": registry["schemaVersion"],
            "selectedEvidenceRegistrySha256": selected_evidence.sha256_bytes(registry_bytes),
            "selectedEvidenceTupleDigest": selected_evidence.registry_tuple_digest(registry),
            "selectedEvidenceEntryCount": len(registry["entries"]),
            "selectedEvidenceRunCount": sum(len(entry["runs"]) for entry in registry["entries"]),
            "semanticIconResolutionRegistrySha256": selected_evidence.sha256_bytes(selected_evidence.canonical_json_bytes(resolution_payload)),
        },
        "counts": {
            "records": len(records),
            "rulesTextPresent": rules_bearing,
            "extractionStates": dict(sorted(extraction_states.items())),
            "rulesInformationReadiness": dict(sorted(readiness.items())),
        },
        "records": records,
    }
    return payload


def write_corpus(output: Path = DEFAULT_OUTPUT, *, registry: dict[str, Any] | None = None, registry_path: Path = REGISTRY) -> dict[str, Any]:
    payload = build_payload(registry=registry, registry_path=registry_path)
    data = selected_evidence.canonical_json_bytes(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not output.is_file() or output.read_bytes() != data:
        tmp = output.with_suffix(output.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(output)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else REPO / args.output
    registry_path = args.registry if args.registry.is_absolute() else REPO / args.registry
    payload = write_corpus(output, registry_path=registry_path)
    try:
        output_label = str(output.relative_to(REPO))
    except ValueError:
        output_label = str(output)
    print(json.dumps({"output": output_label, **payload["counts"], "selectedEvidence": payload["metadata"]}, indent=2))


if __name__ == "__main__":
    main()
