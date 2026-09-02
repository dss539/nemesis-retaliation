#!/usr/bin/env python3
"""Slice one rulebook page from the existing pdftotext dump into audit/.

Usage: python3 scripts/slice_audit_fragment.py <page-number>
Reads docs/rulebooks/rulebook_text.txt (already-extracted text; no PDF access)
and writes audit/RB-<NN>.txt for the requested printed page.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path("/home/smithers/nemesis-retaliation")
SOURCE = REPO / "docs/rulebooks/rulebook_text.txt"
AUDIT = REPO / "audit"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: slice_audit_fragment.py <page-number>")
        return 2
    page = int(sys.argv[1])
    text = SOURCE.read_text(encoding="utf-8")
    pages = text.split("\f")
    if not 1 <= page <= len(pages):
        print(f"page {page} out of range (1-{len(pages)})")
        return 1
    chunk = pages[page - 1].strip()
    if not chunk:
        print(f"page {page} is empty in the text dump")
        return 1
    AUDIT.mkdir(parents=True, exist_ok=True)
    out = AUDIT / f"RB-{page:02d}.txt"
    out.write_text(chunk + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)} ({len(chunk.splitlines())} lines)")
    print(f"first line: {chunk.splitlines()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())