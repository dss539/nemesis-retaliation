#!/usr/bin/env python3
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
bga_path = REPO / "docs/rules/source-extraction/secondary/bga-staticData-260622-1220.js"
text = bga_path.read_text(encoding="utf-8")

# Find top-level object declarations like const FOO = { ... }
consts = re.findall(r"const\s+([A-Z0-9_]+)\s*=", text)
print("BGA constants found:", consts)
