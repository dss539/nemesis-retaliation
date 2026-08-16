#!/usr/bin/env python3
"""Derive assignment-local TTS provenance without prior vision output."""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path, PurePosixPath
import re
import sys

import worker_utils as u

REPO = u.REPO
TREE_PREFIX = PurePosixPath("assets/tts-mod/extract/v2-dl/tree")
MANIFEST = REPO / TREE_PREFIX / "manifest.json"
OBJECTS = REPO / "assets/tts-mod/extract/v2/classification.json"
ROLES = REPO / "assets/tts-mod/extract/v2/lua_roles.json"


def derive(asset_id: str) -> dict:
    state = u.source_state(asset_id)
    rel = PurePosixPath(state["sourcePath"]).relative_to(TREE_PREFIX)
    match = re.fullmatch(r"card-(\d+)\.png", rel.name)
    if not match or not rel.parent.name.endswith("_cards"):
        raise ValueError(f"{asset_id}: not a generated card cell path")
    cell_index = int(match.group(1))
    sheet_stem = str(rel.parent)[:-6]

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hits = [entry for entry in manifest if str(PurePosixPath(entry["file"]).with_suffix("")) == sheet_stem]
    if len(hits) != 1:
        raise ValueError(f"{asset_id}: expected one source-sheet manifest hit, got {len(hits)}")
    sheet_entry = hits[0]
    source_url = sheet_entry["url"]
    source_sheet_path = str(TREE_PREFIX / sheet_entry["file"])
    url_to_path = {entry["url"]: str(TREE_PREFIX / entry["file"]) for entry in manifest}

    roles_by_guid: dict[str, list[str]] = defaultdict(list)
    for role in json.loads(ROLES.read_text(encoding="utf-8")):
        roles_by_guid[role["guid"].lower()].append(role["role"])

    refs = []
    exact_index_refs = []
    common_back_counts: dict[tuple[str, str | None], int] = defaultdict(int)
    source_roles = set()
    for obj in json.loads(OBJECTS.read_text(encoding="utf-8")):
        urls = [(key, url) for key, url in obj.get("urls", []) if url]
        matching_roles = sorted({key for key, url in urls if url == source_url})
        if not matching_roles:
            continue
        source_roles.update(matching_roles)
        card_id = obj.get("card_id")
        card_index = card_id % 100 if isinstance(card_id, int) else None
        ref = {
            "ttsGuid": obj.get("guid"),
            "objectType": obj.get("type"),
            "nickname": obj.get("nickname", ""),
            "description": obj.get("description", ""),
            "gmnotes": obj.get("gmnotes", ""),
            "cardId": card_id,
            "derivedCardIndex": card_index,
            "matchingUrlRoles": matching_roles,
            "luaRoles": sorted(set(roles_by_guid.get(str(obj.get("guid", "")).lower(), []))),
            "parent": obj.get("parent", []),
        }
        refs.append(ref)
        if card_index == cell_index:
            exact_index_refs.append(ref)
            for key, url in urls:
                if key == "BackURL" and url != source_url:
                    common_back_counts[(url, url_to_path.get(url))] += 1
        elif obj.get("type") == "Card":
            for key, url in urls:
                if key == "BackURL" and url != source_url:
                    common_back_counts[(url, url_to_path.get(url))] += 1

    paired = [
        {"urlRole": "BackURL", "url": key[0], "path": key[1], "supportingCardRefCount": count}
        for key, count in sorted(common_back_counts.items(), key=lambda item: (-item[1], item[0][0]))
    ]
    direct_pairs = paired if exact_index_refs else []
    generic_pairs = [] if exact_index_refs else paired

    return {
        "schemaVersion": 1,
        "assetId": asset_id,
        "derivedAt": u.now_utc(),
        "derivationSources": [
            str(MANIFEST.relative_to(REPO)),
            str(OBJECTS.relative_to(REPO)),
            str(ROLES.relative_to(REPO)),
        ],
        "priorVisionOutputRead": False,
        "sourcePath": state["sourcePath"],
        "sourceSha256": state["sourceSha256"],
        "sourceKind": "generated",
        "sourceSheetPath": source_sheet_path,
        "sourceSheetUrl": source_url,
        "sourceSheetManifestByteSize": sheet_entry.get("size"),
        "cellIndex": cell_index,
        "sourceUrlRoles": sorted(source_roles),
        "exactCardIndexRefs": exact_index_refs,
        "exactCardIndexRefCount": len(exact_index_refs),
        "allSharedSheetObjectRefs": refs,
        "allSharedSheetObjectRefCount": len(refs),
        "pairedSideEvidence": {
            "directFromExactCardIndexRefs": direct_pairs,
            "genericAcrossOtherCardsUsingSameFaceSheet": generic_pairs,
            "caveat": (
                "No object record selects this exact cell index; generic shared-deck backs do not prove a unique paired side."
                if not exact_index_refs
                else "Paired side(s) are from object records selecting this exact cell index."
            ),
        },
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: extract_provenance.py ASSET_ID")
    asset_id = sys.argv[1]
    payload = derive(asset_id)
    path = u.WORKER / "provenance" / f"{asset_id}.json"
    u.atomic_json(path, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
