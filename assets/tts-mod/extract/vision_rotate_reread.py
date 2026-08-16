#!/usr/bin/env python3
"""Rotate non-upright reads to lossless staging PNGs and re-read them."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
from pathlib import Path
import subprocess
import tempfile

from PIL import Image

import vision_batch as vb

TRANSPOSE = {
    "rotate90cw": Image.Transpose.ROTATE_270,
    "rotate90ccw": Image.Transpose.ROTATE_90,
    "rotate180": Image.Transpose.ROTATE_180,
}


def rerun(record: dict) -> dict:
    result_file = vb.REPO / record["vision"]["resultPath"]
    result = json.loads(result_file.read_text())
    initial = result["parsed"]
    orientation = initial.get("orientation")
    if orientation not in TRANSPOSE:
        return {"ok": True, "skipped": True, "sha": record["sha256"]}
    source = vb.REPO / record["sourcePath"]
    with tempfile.TemporaryDirectory(prefix="nemesis-upright-") as td:
        staged = Path(td) / f"{record['sha256']}.png"
        with Image.open(source) as im:
            im.transpose(TRANSPOSE[orientation]).save(staged, format="PNG", optimize=False)
        prompt = vb.BASE_PROMPT.format(glossary=vb.ICON_GLOSSARY)
        proc = subprocess.run([
            "hermes", "chat", "--provider", vb.PROVIDER, "--model", vb.MODEL,
            "--reasoning", "low",
            "--image", str(staged), "--max-turns", "2", "--pass-session-id",
            "--source", "tool", "-Q", "-q", prompt,
        ], cwd=vb.REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
           timeout=600)
        if proc.returncode != 0:
            return {"ok": False, "sha": record["sha256"], "error": f"CLI exit {proc.returncode}",
                    "cliOutput": proc.stdout}
        try:
            parsed = vb.extract_json(proc.stdout)
            session = vb.extract_session(proc.stdout)
        except Exception as exc:
            return {"ok": False, "sha": record["sha256"], "error": str(exc),
                    "cliOutput": proc.stdout}
        if parsed.get("orientation") not in {"upright", "rotationIrrelevant"}:
            return {"ok": False, "sha": record["sha256"],
                    "error": f"upright verification returned {parsed.get('orientation')}",
                    "cliOutput": proc.stdout, "parsed": parsed, "sessionId": session}
        result["initialParsed"] = initial
        result["initialSessionId"] = result["sessionId"]
        result["orientationCorrection"] = orientation
        result["uprightRead"] = {
            "provider": vb.PROVIDER,
            "model": vb.MODEL,
            "sessionId": session,
            "completedAt": vb.utc_now(),
            "parsed": parsed,
            "cliOutput": proc.stdout,
        }
        result["parsed"] = parsed
        result["sessionId"] = session
        result["completedAt"] = vb.utc_now()
        vb.atomic_json(result_file, result)
        return {"ok": True, "skipped": False, "sha": record["sha256"],
                "sessionId": session, "orientationCorrection": orientation,
                "resultPath": record["vision"]["resultPath"], "confidence": parsed.get("confidence")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    progress = json.loads(vb.PROGRESS.read_text())
    records=[]
    for r in progress["records"]:
        if r["status"] != "visionRead":
            continue
        result = json.loads((vb.REPO / r["vision"]["resultPath"]).read_text())
        if result["parsed"].get("orientation") in TRANSPOSE:
            records.append(r)
    by_sha={r["sha256"]:r for r in progress["records"]}
    failures=corrected=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(rerun,r):r for r in records}
        for future in concurrent.futures.as_completed(futures):
            outcome=future.result()
            rec=by_sha[outcome["sha"]]
            if outcome["ok"]:
                if not outcome["skipped"]:
                    corrected += 1
                    rec["vision"]["initialSessionId"] = rec["vision"]["sessionId"]
                    rec["vision"]["sessionId"] = outcome["sessionId"]
                    rec["vision"]["orientationCorrection"] = outcome["orientationCorrection"]
                    rec["vision"]["confidence"] = outcome["confidence"]
            else:
                failures += 1
                rec["status"] = "visionFailed"
                rec["vision"]["uprightVerificationFailure"] = outcome
            vb.checkpoint(progress)
            print(json.dumps({"checked":corrected+failures,"corrected":corrected,
                              "failed":failures}),flush=True)
    vb.checkpoint(progress)
    print(json.dumps({"done":True,"nonUpright":len(records),"corrected":corrected,
                      "failed":failures,"counts":progress["counts"]},indent=2),flush=True)
    return 0 if failures==0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
