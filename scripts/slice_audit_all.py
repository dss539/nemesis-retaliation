#!/usr/bin/env python3
"""Slice all base-game source material into audit fragments.

Sources (all already-extracted, audited text; no PDFs, no images, no OCR):
- Rulebook: per-page fragments from rulebook-visual-obligations.json census
  plus per-page text extracted from the existing rulebook_text.txt dump by
  printed page markers where available.
- FAQ v1.2: per-unit fragments from faq-v1.2-source-extraction.json.
- Room Help Sheet: per-entry fragments from room-help-sheet.json.
- Intruder Help Sheet: per-side fragments from intruder-help-sheet.json.
- Objective Help Sheet: per-unit fragments from objective-help-sheet.json.
- Player Help sheets: per-front fragments from player-help-source-extraction.json.
- Cards: per-family fragments from assets/tts-mod/extract/card-text-corpus.json.

Writes plain-text fragment files into audit/ named <ID>.txt plus a manifest
audit/manifest.json. RB-12 is skipped (already audited and passed).
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTRACT = REPO / "docs/rules/source-extraction"
AUDIT = REPO / "audit"
CORPUS = REPO / "assets/tts-mod/extract/card-text-corpus.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_fragment(fid, text, manifest):
    fid = fid.replace("/", "-").replace(" ", "-")
    path = AUDIT / f"{fid}.txt"
    path.write_text(text, encoding="utf-8")
    manifest.append({"id": fid, "file": path.name, "chars": len(text)})


def slice_rulebook(manifest):
    census = load(EXTRACT / "rulebook-visual-obligations.json")
    pages_dir = EXTRACT / "rulebook-pages"
    n = 0
    for page in census["pages"]:
        idx = page["pdfPageIndex"]
        fid = f"RB-{idx:02d}"
        if fid == "RB-12":
            continue  # already audited and passed
        lines = []
        lines.append(f"RULEBOOK PAGE {idx}")
        printed = page.get("visiblePrintedPageNumber")
        lines.append(f"Printed page: {printed}")
        headings = page.get("headings") or []
        lines.append("Headings: " + ", ".join(headings))
        lines.append(f"Page role: {page.get('pageRole')}")
        lines.append("")
        lines.append("-- Visual obligations (normative meaning from the page graphics) --")
        for unit in page.get("visualUnits") or []:
            lines.append(f"* {unit.get('occurrenceId')} [{unit.get('obligationClass')}]")
            lines.append(f"  type: {unit.get('type')}")
            if unit.get("visibleLabels"):
                lines.append("  labels: " + ", ".join(unit["visibleLabels"]))
            lines.append(f"  description: {unit.get('description')}")
            if unit.get("spatialRelationshipLostInPlainText"):
                lines.append(f"  spatial meaning: {unit['spatialRelationshipLostInPlainText']}")
            lines.append("")
        lines.append("-- Decorative or non-normative content (do not treat as rules) --")
        for dec in page.get("decorativeOrNonNormative") or []:
            lines.append(f"* {dec.get('description')} [{dec.get('classification')}]")
        if not (page.get("decorativeOrNonNormative") or []):
            lines.append("* none")
        write_fragment(f"{fid}.a.census", "\n".join(lines), manifest)
        prose = pages_dir / f"page-{idx:02d}.txt"
        if prose.is_file():
            text = prose.read_text(encoding="utf-8")
            header = [f"RULEBOOK PAGE {idx} — prose text layer", ""]
            write_fragment(f"{fid}.b.textlayer", "\n".join(header) + text, manifest)
        n += 1
    return n


def slice_faq(manifest):
    faq = load(EXTRACT / "faq-v1.2-source-extraction.json")
    n = 0
    for page in faq["pages"]:
        for unit in page.get("units") or []:
            uid = unit.get("sourceUnitId")
            fid = f"FAQ-{uid}" if uid else f"FAQ-P{page['pdfPageIndex']}-{unit.get('pageLocalNumber')}"
            lines = []
            lines.append(f"FAQ v1.2 — {unit.get('section')} — unit {uid}")
            lines.append(f"Kind: {unit.get('unitKind')}; applicability: {unit.get('applicability')}")
            lines.append(f"Printed page: {page.get('visiblePrintedPageNumber')}")
            lines.append("")
            if unit.get("questionText"):
                lines.append("Q: " + unit["questionText"].strip())
            if unit.get("answerText"):
                lines.append("A: " + unit["answerText"].strip())
            if not (unit.get("questionText") or unit.get("answerText")) and unit.get("printedLines"):
                lines.extend(unit["printedLines"])
            write_fragment(fid, "\n".join(lines), manifest)
            n += 1
    return n


def slice_room_help(manifest):
    data = load(EXTRACT / "room-help-sheet.json")
    n = 0
    for entry in data.get("entries") or []:
        ident = entry.get("entryId") or entry.get("id") or n
        fid = f"ROOM-{ident}"
        lines = [f"ROOM HELP SHEET — entry {ident}"]
        for key in ("printedSectionMarker", "roomName", "room", "name"):
            if entry.get(key):
                lines.append(f"{key}: {entry[key]}")
        for key, value in entry.items():
            if key in ("entryId", "id", "printedSectionMarker", "roomName", "room", "name"):
                continue
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, list) and value and isinstance(value[0], (str, int, float)):
                lines.append(f"{key}: " + " | ".join(str(v) for v in value))
            elif isinstance(value, dict):
                for k2, v2 in value.items():
                    if isinstance(v2, (str, int, float, bool)):
                        lines.append(f"{key}.{k2}: {v2}")
        write_fragment(fid, "\n".join(lines), manifest)
        n += 1
    return n


def slice_intruder_help(manifest):
    data = load(EXTRACT / "intruder-help-sheet.json")
    n = 0
    for side in data.get("sides") or []:
        ident = side.get("sideId") or side.get("id") or n
        fid = f"INTR-{ident}"
        lines = [f"INTRUDER HELP SHEET — side {ident}"]
        for key, value in side.items():
            if key in ("sideId", "id"):
                continue
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        ident2 = item.get("instructionId") or item.get("id") or ""
                        text = item.get("text") or item.get("instruction") or json.dumps(item, ensure_ascii=False)
                        lines.append(f"- {ident2}: {text}")
                    else:
                        lines.append(f"- {item}")
            elif isinstance(value, dict):
                lines.append(json.dumps(value, ensure_ascii=False, indent=1))
        write_fragment(fid, "\n".join(lines), manifest)
        n += 1
    return n


def slice_objective_help(manifest):
    data = load(EXTRACT / "objective-help-sheet.json")
    n = 0
    for unit in data.get("units") or []:
        ident = unit.get("unitId") or unit.get("id") or n
        fid = f"OBJ-{ident}"
        lines = [f"OBJECTIVE HELP SHEET — unit {ident}"]
        for key, value in unit.items():
            if key in ("unitId", "id"):
                continue
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"{key}: {value}")
            elif isinstance(value, list) and value and isinstance(value[0], (str, int, float)):
                lines.append(f"{key}: " + " | ".join(str(v) for v in value))
            else:
                lines.append(json.dumps({key: value}, ensure_ascii=False))
        write_fragment(fid, "\n".join(lines), manifest)
        n += 1
    return n


def slice_player_help(manifest):
    data = load(EXTRACT / "player-help-source-extraction.json")
    n = 0
    for front in data.get("fronts") or []:
        ident = front.get("playerNumber") or front.get("frontId") or n
        fid = f"PHS-{ident}"
        lines = [f"PLAYER HELP SHEET — front {ident}"]
        for key, value in front.items():
            if isinstance(value, (str, int, float, bool)):
                lines.append(f"{key}: {value}")
            else:
                lines.append(json.dumps({key: value}, ensure_ascii=False))
        write_fragment(fid, "\n".join(lines), manifest)
        n += 1
    back = data.get("sharedBack")
    if back:
        lines = ["PLAYER HELP SHEET — shared back"]
        lines.append(json.dumps(back, ensure_ascii=False, indent=1))
        write_fragment("PHS-BACK", "\n".join(lines), manifest)
        n += 1
    return n


def slice_cards(manifest):
    data = load(CORPUS)
    n = 0
    for record in data.get("records", []):
        fam = record.get("componentFamily") or "unknown"
        source = record.get("sourcePath", "")
        tail = source.split("/cards/")[-1] if "/cards/" in source else source
        stem = tail.replace("/", "-")
        fid = f"CARD-{fam}-{stem}"
        printed = record.get("printedData") or {}
        lines = [f"CARD CORPUS RECORD — {fam} / {stem}"]
        readiness = record.get("rulesInformationReadiness")
        if readiness:
            lines.append(f"extraction state: {record.get('extractionState')}; readiness: {readness}") if False else lines.append(f"extraction state: {record.get('extractionState')}; readiness: {readiness}")
        lines.append(f"rules text present: {record.get('rulesTextPresent')}")
        lines.append("")
        for key in ("title", "typeLine", "body"):
            if printed.get(key):
                lines.append(f"{key}: {printed[key]}")
        for sec in printed.get("sections") or []:
            if isinstance(sec, dict):
                text = sec.get("text") or ""
                if text:
                    lines.append(f"section: {text}")
        lines.append(f"source: {source}")
        write_fragment(fid, "\n".join(lines), manifest)
        n += 1
    return n


def main():
    AUDIT.mkdir(exist_ok=True)
    manifest = []
    counts = {}
    counts["rulebook"] = slice_rulebook(manifest)
    counts["faq"] = slice_faq(manifest)
    counts["room"] = slice_room_help(manifest)
    counts["intruder"] = slice_intruder_help(manifest)
    counts["objective"] = slice_objective_help(manifest)
    counts["player"] = slice_player_help(manifest)
    counts["cardFamilies"] = slice_cards(manifest)
    payload = {
        "total": len(manifest),
        "bySource": counts,
        "fragments": manifest,
    }
    (AUDIT / "manifest.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(counts, indent=2))
    print("total fragments:", len(manifest))


if __name__ == "__main__":
    main()