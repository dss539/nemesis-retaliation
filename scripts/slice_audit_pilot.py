#!/usr/bin/env python3
"""Slice the audit pilot for rulebook page 12 from already-audited text.

Writes audit/RB-12.a.census.txt (visual-obligation census entry for page 12)
and audit/RB-12.b.textlayer.txt (the Game Round Structure prose from the
existing rulebook_text.txt dump). No PDF access, no new extraction.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path("/home/smithers/nemesis-retaliation")
AUDIT = REPO / "audit"
CENSUS = REPO / "docs/rules/source-extraction/rulebook-visual-obligations.json"
DUMP = REPO / "docs/rulebooks/rulebook_text.txt"


def main() -> int:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    page = next(p for p in census["pages"] if p["pdfPageIndex"] == 12)

    AUDIT.mkdir(parents=True, exist_ok=True)
    Path(AUDIT / "RB-12.a.census.txt").write_text(
        json.dumps(page, indent=2) + "\n", encoding="utf-8"
    )

    dump = DUMP.read_text(encoding="utf-8")
    start = dump.find("GAME ROUND STRUCTURE")
    # find the heading occurrence that begins the actual section (not the ToC);
    # the section body starts at the LAST occurrence before the Player Phase prose
    occurrences = [m.start() for m in re.finditer("GAME ROUND STRUCTURE", dump)]
    start = occurrences[-1]
    # page-12 prose ends where the next major section begins
    end = dump.find("PLAYING ACTION CARDS", start)
    if end == -1:
        end = start + 4000
    Path(AUDIT / "RB-12.b.textlayer.txt").write_text(
        dump[start:end].strip() + "\n", encoding="utf-8"
    )

    for f in sorted(AUDIT.glob("RB-12*")):
        print(f"{f.name}: {len(f.read_text(encoding='utf-8').splitlines())} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())