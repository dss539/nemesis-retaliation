#!/usr/bin/env python3
"""Strict, worker-local source identity and staging utilities."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path("/home/smithers/nemesis-retaliation")
WORKER = Path(__file__).resolve().parent
ASSIGNMENT = WORKER / "assignment.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_json(path: Path, payload: Any) -> None:
    resolved = path.resolve()
    root = WORKER.resolve()
    if root not in (resolved, *resolved.parents):
        raise ValueError(f"refusing write outside worker root: {resolved}")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=resolved.name + ".", suffix=".tmp", dir=resolved.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, resolved)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def contract() -> dict[str, Any]:
    return json.loads(ASSIGNMENT.read_text(encoding="utf-8"))


def assigned(asset_id: str) -> dict[str, Any]:
    rows = [row for row in contract()["assets"] if row["assetId"] == asset_id]
    if len(rows) != 1:
        raise ValueError(f"expected one assignment row for {asset_id}; got {len(rows)}")
    return rows[0]


def source_state(asset_id: str) -> dict[str, Any]:
    row = assigned(asset_id)
    path = REPO / row["sourcePath"]
    digest = sha256(path)
    if digest != row["sourceSha256"]:
        raise ValueError(
            f"{asset_id}: source SHA mismatch: assigned={row['sourceSha256']} actual={digest}"
        )
    with Image.open(path) as image:
        width, height = image.size
        image_format = image.format
        mode = image.mode
        frames = getattr(image, "n_frames", 1)
        image.verify()
    return {
        "assetId": asset_id,
        "sourcePath": row["sourcePath"],
        "absoluteSourcePath": str(path.resolve()),
        "sourceSha256": digest,
        "sourceMetadata": {
            "width": width,
            "height": height,
            "format": image_format,
            "mode": mode,
            "frames": frames,
            "byteSize": path.stat().st_size,
            "decodeVerified": True,
        },
    }


def verify_all() -> dict[str, Any]:
    assignment = contract()
    states = [source_state(row["assetId"]) for row in assignment["assets"]]
    report = {
        "schemaVersion": 1,
        "workerId": assignment["workerId"],
        "verifiedAt": now_utc(),
        "assignmentCount": len(states),
        "uniqueAssetIdCount": len({row["assetId"] for row in states}),
        "uniqueSourcePathCount": len({row["sourcePath"] for row in states}),
        "allHashesMatchAssignment": True,
        "allSourcesDecode": True,
        "assets": states,
    }
    atomic_json(WORKER / "metadata/source-inventory-initial.json", report)
    return report


def with_identity(asset_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    state = source_state(asset_id)
    identity = {
        "assetId": state["assetId"],
        "sourcePath": state["sourcePath"],
        "sourceSha256": state["sourceSha256"],
        "sourceMetadata": state["sourceMetadata"],
    }
    for key, expected in identity.items():
        if key in payload and payload[key] != expected:
            raise ValueError(f"{asset_id}: caller supplied mismatched {key}")
    return {"schemaVersion": 1, **identity, **payload}


def write_raw(asset_id: str, payload: dict[str, Any]) -> Path:
    path = WORKER / "raw" / f"{asset_id}.json"
    atomic_json(path, with_identity(asset_id, payload))
    return path


def write_result(asset_id: str, payload: dict[str, Any]) -> Path:
    path = WORKER / "results" / f"{asset_id}.json"
    atomic_json(path, with_identity(asset_id, payload))
    return path


def write_batch(batch_id: str, payload: dict[str, Any]) -> Path:
    path = WORKER / "batches" / f"{batch_id}.json"
    atomic_json(path, {"schemaVersion": 1, "batchId": batch_id, **payload})
    return path


def write_checkpoint(payload: dict[str, Any]) -> None:
    final = {"schemaVersion": 1, **payload}
    atomic_json(WORKER / "checkpoint.json", final)
    atomic_json(WORKER / "checkpoints" / f"checkpoint-{int(payload.get('batchCount', 0)):03d}.json", final)


def validate_staging(require_complete: bool = False) -> dict[str, Any]:
    assignment = contract()
    assigned_ids = [row["assetId"] for row in assignment["assets"]]
    raw = {}
    results = {}
    errors = []
    for asset_id in assigned_ids:
        raw_path = WORKER / "raw" / f"{asset_id}.json"
        result_path = WORKER / "results" / f"{asset_id}.json"
        if raw_path.exists():
            raw[asset_id] = json.loads(raw_path.read_text())
        if result_path.exists():
            results[asset_id] = json.loads(result_path.read_text())
        for kind, obj in (("raw", raw.get(asset_id)), ("result", results.get(asset_id))):
            if obj is None:
                continue
            state = source_state(asset_id)
            for key in ("assetId", "sourcePath", "sourceSha256"):
                if obj.get(key) != state[key]:
                    errors.append(f"{asset_id} {kind}: {key} mismatch")
    if require_complete:
        errors.extend(f"{asset_id}: missing raw" for asset_id in assigned_ids if asset_id not in raw)
        errors.extend(f"{asset_id}: missing result" for asset_id in assigned_ids if asset_id not in results)
    report = {
        "schemaVersion": 1,
        "validatedAt": now_utc(),
        "assignmentCount": len(assigned_ids),
        "rawCount": len(raw),
        "resultCount": len(results),
        "missingRawIds": [asset_id for asset_id in assigned_ids if asset_id not in raw],
        "missingResultIds": [asset_id for asset_id in assigned_ids if asset_id not in results],
        "identityErrors": errors,
        "allCurrentSourcesMatchAndDecode": True,
        "passed": not errors,
    }
    atomic_json(WORKER / "validation.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("verify", "source", "validate"))
    parser.add_argument("asset_id", nargs="?")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    if args.command == "verify":
        print(json.dumps(verify_all(), indent=2))
    elif args.command == "source":
        if not args.asset_id:
            raise SystemExit("source requires asset_id")
        print(json.dumps(source_state(args.asset_id), indent=2))
    else:
        print(json.dumps(validate_staging(args.require_complete), indent=2))


if __name__ == "__main__":
    main()
