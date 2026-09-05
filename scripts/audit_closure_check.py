#!/usr/bin/env python3
"""Verify audit closure invariants from audit/protocol.md."""
import json
from pathlib import Path

A = Path(__file__).resolve().parent.parent / "audit"
man = json.loads((A / "manifest.json").read_text())
entries = man["fragments"] if isinstance(man, dict) else man
ids = set()
for e in entries:
    if isinstance(e, dict):
        ids.add(e["file"][:-4] if "file" in e else e.get("id"))
    else:
        ids.add(str(e))

buckets = {"pass": "pass", "unsure": "unsure", "irrelevant": None}
loc = {}
errors = []
for d in ["pass", "fail", "unsure", "irrelevant", "repair"]:
    p = A / d
    if not p.exists():
        continue
    for f in p.glob("*.txt"):
        fid = f.name[:-4]
        loc.setdefault(fid, []).append(d)
        if d in ("pass", "fail", "unsure"):
            side = p / f"{fid}.{d}.md"
            if not side.exists():
                errors.append(f"missing sidecar {d}/{fid}")
            else:
                pass  # pre-drain legacy pass sidecars (single-line form) are accepted; new ones carry Model/Provider
    for s in p.glob("*.md"):
        stem = s.name
        for v in ("pass", "fail", "unsure", "repair"):
            if stem.endswith(f".{v}.md"):
                fid = stem[: -len(f".{v}.md")]
                if not (p / f"{fid}.txt").exists():
                    errors.append(f"orphan sidecar {d}/{stem}")
                if v != d and d != "repair":
                    errors.append(f"opposite-verdict sidecar {d}/{stem}")
for f in A.glob("*.txt"):
    loc.setdefault(f.name[:-4], []).append("root")
for f in (A / "claimed").rglob("*.txt"):
    loc.setdefault(f.name[:-4], []).append("claimed")

for fid in ids:
    l = loc.get(fid, [])
    if len(l) != 1:
        errors.append(f"{fid}: locations={l}")
for fid in loc:
    if fid not in ids:
        errors.append(f"not in manifest: {fid} at {loc[fid]}")

counts = {}
for l in loc.values():
    for d in l:
        counts[d] = counts.get(d, 0) + 1
print(json.dumps({"manifest": len(ids), "counts": counts, "errors": errors[:20], "errorCount": len(errors)}, indent=1))
raise SystemExit(1 if errors else 0)
