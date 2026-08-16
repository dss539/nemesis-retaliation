#!/usr/bin/env python3
"""Extract metadata-only provenance after a raw blind record exists."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path("/home/smithers/nemesis-retaliation")
WORKER = REPO / "assets/tts-mod/extract/vision-workers/sol-max-worker-02"
ASSIGNMENT = WORKER / "assignment.json"
TREE = REPO / "assets/tts-mod/extract/v2-dl/tree"
MANIFEST = TREE / "manifest.json"
OBJECTS = REPO / "assets/tts-mod/extract/v2/objects.json"
CLASSIFICATION = REPO / "assets/tts-mod/extract/v2/classification.json"
LUA_ROLES = REPO / "assets/tts-mod/extract/v2/lua_roles.json"
LOW_CONFIDENCE = REPO / "assets/tts-mod/extract/low-confidence-review.json"


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


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_parent(value: Any) -> Any:
    if isinstance(value, list):
        return value
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("asset_ids", nargs="+")
    args = parser.parse_args()
    assignment = load(ASSIGNMENT)
    by_id = {row["assetId"]: row for row in assignment["assets"]}
    unknown = [asset_id for asset_id in args.asset_ids if asset_id not in by_id]
    if unknown:
        raise SystemExit(f"IDs not in current assignment: {unknown}")
    manifest = load(MANIFEST)
    manifest_by_file = {row["file"]: row for row in manifest}
    objects = load(OBJECTS)
    classification = {row["guid"]: row for row in load(CLASSIFICATION)}
    roles_by_guid: dict[str, list[str]] = defaultdict(list)
    for row in load(LUA_ROLES):
        roles_by_guid[row["guid"]].append(row["role"])
    queue_payload = load(LOW_CONFIDENCE)
    queue_entries = queue_payload.get("entries", []) if isinstance(queue_payload, dict) else queue_payload
    queue_by_path = {row.get("sourcePath"): row for row in queue_entries}
    outputs = []
    for asset_id in args.asset_ids:
        asset = by_id[asset_id]
        raw_path = WORKER / "raw" / f"{asset_id}.json"
        if not raw_path.is_file():
            raise SystemExit(f"Raw blind record must exist before metadata join: {raw_path}")
        raw = load(raw_path)
        if (raw.get("assetId"), raw.get("sourcePath"), raw.get("sourceSha256")) != (
            asset["assetId"], asset["sourcePath"], asset["sourceSha256"]
        ):
            raise SystemExit(f"Raw tuple mismatch for {asset_id}")
        source = REPO / asset["sourcePath"]
        actual_hash = sha256(source)
        if actual_hash != asset["sourceSha256"]:
            raise SystemExit(f"Live source hash mismatch for {asset_id}: {actual_hash}")
        tree_rel = source.relative_to(TREE).as_posix()
        source_kind = "manifest"
        source_url = None
        source_sheet_path = None
        source_sheet_url = None
        cell_index = None
        manifest_row = manifest_by_file.get(tree_rel)
        queue_provenance = None
        if manifest_row:
            source_url = manifest_row["url"]
        else:
            source_kind = "generated"
            queue_row = queue_by_path.get(asset["sourcePath"])
            if queue_row:
                provenance = queue_row.get("provenance") or {}
                queue_provenance = {
                    "sourceUrl": provenance.get("sourceUrl"),
                    "sourceSheetPath": provenance.get("sourceSheetPath"),
                    "cellIndex": provenance.get("cellIndex"),
                    "objectRefs": provenance.get("objectRefs"),
                }
                source_url = provenance.get("sourceUrl")
                source_sheet_path = provenance.get("sourceSheetPath")
                cell_index = provenance.get("cellIndex")
            if not source_url:
                parent = source.parent
                if parent.name.endswith("_cards") and source.stem.startswith("card-"):
                    sheet_stem = parent.name[:-6]
                    for ext in (".jpg", ".png", ".jpeg"):
                        candidate = parent.parent / f"{sheet_stem}{ext}"
                        if candidate.is_file():
                            source_sheet_path = candidate.relative_to(REPO).as_posix()
                            sheet_rel = candidate.relative_to(TREE).as_posix()
                            sheet_manifest = manifest_by_file.get(sheet_rel)
                            source_url = sheet_manifest.get("url") if sheet_manifest else None
                            source_sheet_url = source_url
                            cell_index = int(source.stem.split("-")[-1])
                            break
        if source_sheet_path and not source_sheet_url:
            sheet = REPO / source_sheet_path
            if sheet.is_file() and sheet.is_relative_to(TREE):
                sheet_manifest = manifest_by_file.get(sheet.relative_to(TREE).as_posix())
                source_sheet_url = sheet_manifest.get("url") if sheet_manifest else source_url
        object_refs = []
        if source_url:
            for obj in objects:
                matched_roles = sorted({role for role, url in obj.get("urls", []) if url == source_url})
                if not matched_roles:
                    continue
                cls = classification.get(obj["guid"], {})
                object_refs.append(
                    {
                        "guid": obj.get("guid"),
                        "type": obj.get("type"),
                        "nickname": obj.get("nickname"),
                        "description": obj.get("description"),
                        "gmnotes": obj.get("gmnotes"),
                        "cardId": obj.get("card_id"),
                        "parent": compact_parent(obj.get("parent")),
                        "urlRoles": matched_roles,
                        "luaRoles": sorted(roles_by_guid.get(obj.get("guid"), [])),
                        "classificationVerdict": cls.get("verdict"),
                        "classificationReason": cls.get("reason"),
                        "classificationGroup": cls.get("group"),
                    }
                )
        payload = {
            "schemaVersion": 1,
            "generatedAt": now_utc(),
            "assetId": asset_id,
            "sourcePath": asset["sourcePath"],
            "sourceSha256": actual_hash,
            "rawBlindRecordPath": str(raw_path.relative_to(WORKER)),
            "metadataConsultedOnlyAfterRawPersisted": True,
            "sourceKind": source_kind,
            "manifest": {
                "sourceUrl": source_url,
                "manifestFile": manifest_row.get("file") if manifest_row else None,
                "manifestByteSize": manifest_row.get("size") if manifest_row else None,
            },
            "generatedSource": {
                "sourceSheetPath": source_sheet_path,
                "sourceSheetUrl": source_sheet_url,
                "cellIndex": cell_index,
                "queueProvenanceSubset": queue_provenance,
            } if source_kind == "generated" else None,
            "objectReferenceCount": len(object_refs),
            "objectReferences": object_refs,
            "priorSemanticVisionEvidenceRead": False,
        }
        out_path = WORKER / "metadata/provenance" / f"{asset_id}.json"
        dump(out_path, payload)
        outputs.append({"assetId": asset_id, "path": str(out_path), "sourceKind": source_kind, "sourceUrl": source_url, "objectReferenceCount": len(object_refs)})
    print(json.dumps({"generated": outputs}, indent=2))


if __name__ == "__main__":
    main()
