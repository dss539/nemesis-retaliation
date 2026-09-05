#!/usr/bin/env python3
"""Coordinator disposition: convert listed fail claims to unsure with a coordinator note.

Usage: python3 scripts/audit_fail_to_unsure.py <ID> "<coordinator evidence>"
Moves audit/fail/<ID>.txt -> audit/unsure/<ID>.txt and rewrites the sidecar
as <ID>.unsure.md, preserving the verifier's Model/Provider lines and original evidence.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "audit"


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    fid, note = sys.argv[1], sys.argv[2]
    frag = ROOT / "fail" / f"{fid}.txt"
    side = ROOT / "fail" / f"{fid}.fail.md"
    if not frag.exists() or not side.exists():
        print(f"missing fail fragment or sidecar for {fid}")
        return 1
    lines = side.read_text(encoding="utf-8").splitlines()
    model = next((l for l in lines if l.startswith("Model:")), "Model: `unknown`")
    prov = next((l for l in lines if l.startswith("Provider:")), "Provider: `unknown`")
    orig = next((l for l in lines if l.startswith("Evidence:")), "Evidence: (none)")
    out = ROOT / "unsure"
    out.mkdir(exist_ok=True)
    dest_side = out / f"{fid}.unsure.md"
    dest_frag = out / f"{fid}.txt"
    if dest_side.exists() or dest_frag.exists():
        print(f"unsure residue already exists for {fid}")
        return 1
    dest_side.write_text(
        f"{model}\n{prov}\nEvidence: Coordinator review converted verifier fail to unsure: {note} "
        f"Verifier finding: {orig[len('Evidence: '):]}\n",
        encoding="utf-8",
    )
    frag.rename(dest_frag)
    side.unlink()
    print(f"unsure {fid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
