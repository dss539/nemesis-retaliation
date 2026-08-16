#!/usr/bin/env python3
"""Validate the extracted card-text corpus against live evidence and sources."""
from __future__ import annotations

import collections
import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
CORPUS = EXTRACT / "card-text-corpus.json"
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
