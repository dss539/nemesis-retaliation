#!/usr/bin/env python3
"""Build a provenance-rich, non-canonical corpus of all in-scope card text."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path

import analyze_card_extraction_coverage as coverage

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
PROGRESS = EXTRACT / "vision-progress.json"
QUEUE = EXTRACT / "low-confidence-review.json"
GLOSSARY = REPO / "docs/rules/icon-glossary.md"
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
    if len(result) != 49:
        raise ValueError(f"expected 49 glossary identifiers, found {len(result)}")
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    progress = load(PROGRESS)
    queue = load(QUEUE)
    deferred = {entry["sourcePath"]: entry for entry in queue["entries"]}
    known = glossary_ids()
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
            text_data = queue_entry.get("visibleText")
            if text_data is None:
                text_data = queue_entry.get("semanticRead") or {}
            extraction_state, _ = coverage.extraction_state(queue_entry)
            text_evidence = "native vision draft; not canonical promotion"
            uncertainties = queue_entry.get("uncertainties") or []
            reason = queue_entry.get("reasonSkipped")
            vision = queue_entry.get("vision") or {}
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
        elif extraction_state == "non-rules-or-reference":
            rules_readiness = "not-rules-bearing-or-reference"
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
            },
        })
    records.sort(key=lambda row: row["sourcePath"])
    payload = {
        "schemaVersion": 1,
        "status": "extracted evidence corpus; canonical and draft states are explicitly separated",
        "generatedFrom": {
            "visionProgressUpdatedAt": progress.get("updatedAt"),
            "reviewQueueUpdatedAt": queue.get("updatedAt"),
            "iconGlossary": "docs/rules/icon-glossary.md",
            "iconGlossaryIdentifierCount": len(known),
        },
        "counts": {
            "records": len(records),
            "rulesTextPresent": rules_bearing,
            "extractionStates": dict(sorted(extraction_states.items())),
            "rulesInformationReadiness": dict(sorted(readiness.items())),
        },
        "records": records,
    }
    output = args.output if args.output.is_absolute() else REPO / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"output": str(output.relative_to(REPO)), **payload["counts"]}, indent=2))


if __name__ == "__main__":
    main()
