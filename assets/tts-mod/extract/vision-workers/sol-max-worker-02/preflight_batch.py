#!/usr/bin/env python3
"""Re-read live assignment and verify selected source bytes before vision."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path("/home/smithers/nemesis-retaliation")
WORKER = REPO / "assets/tts-mod/extract/vision-workers/sol-max-worker-02"
ASSIGNMENT = WORKER / "assignment.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


parser = argparse.ArgumentParser()
parser.add_argument("batch_id")
parser.add_argument("asset_ids", nargs="+")
args = parser.parse_args()
assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
assets = assignment["assets"]
by_id = {row["assetId"]: row for row in assets}
assigned_order = [row["assetId"] for row in assets]
positions = [assigned_order.index(asset_id) for asset_id in args.asset_ids if asset_id in by_id]
if len(positions) != len(args.asset_ids):
    missing = [asset_id for asset_id in args.asset_ids if asset_id not in by_id]
    raise SystemExit(f"IDs absent from current assignment: {missing}")
if positions != list(range(positions[0], positions[0] + len(positions))):
    raise SystemExit(f"Batch IDs are not a contiguous ordered assignment slice: {args.asset_ids}")
ordered_tuples = [
    {
        "assignmentIndex": index,
        "assetId": row["assetId"],
        "sourcePath": row["sourcePath"],
        "sourceSha256": row["sourceSha256"],
    }
    for index, row in enumerate(assets, 1)
]
tuple_hash = hashlib.sha256(json.dumps(ordered_tuples, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
rows = []
for asset_id in args.asset_ids:
    asset = by_id[asset_id]
    source = REPO / asset["sourcePath"]
    actual = sha256(source)
    with Image.open(source) as im:
        width, height = im.size
        fmt, mode, frames = im.format, im.mode, getattr(im, "n_frames", 1)
        im.verify()
    row = {
        "assetId": asset_id,
        "sourcePath": asset["sourcePath"],
        "assignedSha256": asset["sourceSha256"],
        "verifiedSha256": actual,
        "hashMatchesAssignment": actual == asset["sourceSha256"],
        "width": width,
        "height": height,
        "format": fmt,
        "mode": mode,
        "frames": frames,
        "decodeVerified": True,
    }
    rows.append(row)
if not all(row["hashMatchesAssignment"] for row in rows):
    payload = {
        "schemaVersion": 1,
        "batchId": args.batch_id,
        "verifiedAt": now_utc(),
        "status": "blocked-source-hash-mismatch",
        "assignmentFileSha256": sha256(ASSIGNMENT),
        "orderedTupleSha256": tuple_hash,
        "assets": rows,
    }
    dump(WORKER / "batches" / f"preflight-{args.batch_id}.json", payload)
    raise SystemExit(2)
payload = {
    "schemaVersion": 1,
    "batchId": args.batch_id,
    "verifiedAt": now_utc(),
    "status": "ready",
    "assignmentFileSha256": sha256(ASSIGNMENT),
    "orderedTupleSha256": tuple_hash,
    "assignmentCount": len(assets),
    "submittedCount": len(rows),
    "submittedAssetIds": args.asset_ids,
    "assets": rows,
}
dump(WORKER / "batches" / f"preflight-{args.batch_id}.json", payload)
print(json.dumps(payload, indent=2))
