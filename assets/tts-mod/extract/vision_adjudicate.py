#!/usr/bin/env python3
"""Conservatively adjudicate persisted vision reads and promote clear card faces."""
from __future__ import annotations

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import shutil

from PIL import Image

import vision_batch as vb

TREE = vb.REPO / "assets/tts-mod/extract/v2-dl/tree"
MANIFEST = TREE / "manifest.json"
OBJECTS = vb.REPO / "assets/tts-mod/extract/v2/classification.json"
ROLES = vb.REPO / "assets/tts-mod/extract/v2/lua_roles.json"
QUEUE = vb.REPO / "assets/tts-mod/extract/low-confidence-review.json"

ICON_TOKENS = {
    "shootDie2", "shootDie3", "shootDie4", "shootDie5", "shootDieAmmoLoss", "shootDieCritical",
    "burstDie1", "burstDie2", "burstDie3", "burstDie4", "burstDieAdditionalEffects",
    "noiseDie1", "noiseDie2", "noiseDie3", "noiseDie4", "noiseDieHazard",
    "redItem", "yellowItem", "greenItem", "computer", "fire", "malfunction", "noise", "secure",
    "corridorEW", "corridorNESW", "corridorNWSE", "lifeSupportActive", "lifeSupportInactive",
    "hibernatoriumActive", "hibernatoriumInactive", "lander", "autodestruction",
    "oxygenToken", "ammoToken", "grenadeToken", "medpackToken", "ammoSlot", "grenadeSlot",
    "oxygenSlot", "medpackSlot", "anySlot", "character", "oxygen", "characterHealth",
    "actionCard", "robot", "notInCombat", "intruder",
}

KNOWN_COMPLETE = {
    "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-012.png": {
        "classification": "Automatic Shotgun BackURL; obsolete/misnested STARTING ITEM — COMBAT ENGINEER provenance, not an independent card",
        "evidence": ["docs/qa/card-source-audits/automatic-shotgun-source-fidelity.md"],
    },
    "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-044.jpg": {
        "classification": "conflicting Bulletproof Vest BackURL variant; provenance only, not the canonical face",
        "evidence": ["docs/qa/card-source-audits/bulletproof-vest-face-back.md"],
    },
    "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-025.png": {
        "classification": "obsolete/prototype BF Gun face; excluded from canonical card data",
        "evidence": ["docs/qa/card-source-audits/bf-gun-source-fidelity.md"],
    },
    "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-035.png": {
        "classification": "obsolete/prototype Continuous Fire action tied to BF Gun; excluded from canonical card data",
        "evidence": ["docs/qa/card-source-audits/continuous-fire-source-fidelity.md"],
    },
    "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-038.png": {
        "classification": "BF Gun BackURL (STARTING ITEM — HEAVY GUN OPERATOR); obsolete/prototype provenance",
        "evidence": ["docs/qa/card-source-audits/bf-gun-source-fidelity.md"],
    },
}

ROTATE = {
    "rotate90cw": Image.Transpose.ROTATE_270,
    "rotate90ccw": Image.Transpose.ROTATE_90,
    "rotate180": Image.Transpose.ROTATE_180,
}


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def tokens(value: str) -> set[str]:
    return {x for x in norm(value).split() if len(x) >= 3 and x not in {
        "the", "and", "with", "card", "custom", "image", "texture", "game", "component",
        "visible", "artwork", "asset", "object", "room", "token", "model", "bag",
    }}


def slug(value: str) -> str | None:
    s = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return s or None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structured_visible(parsed: dict) -> dict:
    return {k: parsed.get(k, "") for k in (
        "title", "typeLine", "body", "footer", "upperRight", "lowerCenter", "visibleText"
    ) if parsed.get(k, "")}


def build_provenance(progress: dict) -> dict[str, dict]:
    manifest = json.loads(MANIFEST.read_text())
    by_path = {f"assets/tts-mod/extract/v2-dl/tree/{e['file']}": e for e in manifest}
    url_path = {e["url"]: f"assets/tts-mod/extract/v2-dl/tree/{e['file']}" for e in manifest}
    objects = json.loads(OBJECTS.read_text())
    roles_by_guid = defaultdict(list)
    for item in json.loads(ROLES.read_text()):
        roles_by_guid[item["guid"].lower()].append(item["role"])
    refs_by_url = defaultdict(list)
    object_by_guid = {}
    for obj in objects:
        object_by_guid[obj["guid"].lower()] = obj
        for key, url in obj.get("urls", []):
            if url:
                refs_by_url[url].append((key, obj))
    result = {}
    for rec in progress["records"]:
        source_path = rec["sourcePath"]
        entry = by_path.get(source_path)
        source_sheet = None
        cell = None
        if not entry and rec.get("generatedFrom"):
            source_sheet = rec["generatedFrom"]["sourceSheetPath"]
            cell = rec["generatedFrom"]["cellIndex"]
            entry = by_path.get(source_sheet)
        refs = []
        paired = []
        if entry:
            for key, obj in refs_by_url.get(entry["url"], []):
                ref = {
                    "urlRole": key,
                    "ttsGuid": obj["guid"],
                    "objectType": obj["type"],
                    "nickname": obj.get("nickname", ""),
                    "description": obj.get("description", ""),
                    "gmnotes": obj.get("gmnotes", ""),
                    "cardId": obj.get("card_id", ""),
                    "roles": sorted(set(roles_by_guid.get(obj["guid"].lower(), []))),
                    "parent": obj.get("parent", []),
                }
                refs.append(ref)
                for other_key, other_url in obj.get("urls", []):
                    if other_url and other_url != entry["url"] and other_key in {"FaceURL", "BackURL"}:
                        paired.append({
                            "ttsGuid": obj["guid"], "urlRole": other_key, "url": other_url,
                            "path": url_path.get(other_url),
                        })
        result[source_path] = {
            "sourceUrl": entry["url"] if entry else None,
            "sourceSheetPath": source_sheet,
            "cellIndex": cell,
            "objectRefs": refs,
            "pairedSides": sorted(paired, key=lambda x: (x["ttsGuid"], x["urlRole"], x["url"])),
        }
    return result


def metadata_terms(provenance: dict) -> set[str]:
    values = []
    for ref in provenance.get("objectRefs", []):
        values.extend([ref.get("nickname", ""), ref.get("description", ""), ref.get("gmnotes", ""),
                       ref.get("objectType", ""), " ".join(ref.get("roles", []))])
        values.extend(p[2] for p in ref.get("parent", []) if len(p) >= 3)
    return tokens(" ".join(values))


def source_roles(provenance: dict) -> set[str]:
    return {r["urlRole"] for r in provenance.get("objectRefs", [])}


def uncertain_text(parsed: dict) -> str:
    return " ".join(str(x) for x in parsed.get("uncertainties", []))


def sidecar_for(parsed: dict) -> tuple[dict | None, str | None]:
    body = parsed.get("body", "")
    if not body:
        return None, "individual rules face has no exact body transcription"
    combined = " ".join(str(parsed.get(k, "")) for k in ("typeLine", "body", "upperRight", "lowerCenter"))
    lowered = combined.lower()
    if "[icon:" in lowered or "[illegible" in lowered or "[clipped" in lowered:
        return None, "transcription contains an unresolved literal icon, illegible text, or clipped text"
    found = set(re.findall(r"\[([A-Za-z][A-Za-z0-9]*)\]", combined))
    unknown = sorted(found - ICON_TOKENS)
    if unknown:
        return None, f"sidecar contains non-glossary icon token(s): {', '.join(unknown)}"
    for key in ("upperRight", "lowerCenter"):
        value = parsed.get(key, "")
        if value and value not in ICON_TOKENS:
            return None, f"{key} is not a normalized glossary identifier"
    result = {}
    if parsed.get("typeLine", ""):
        result["typeLine"] = parsed["typeLine"]
    result["body"] = body
    if parsed.get("upperRight", ""):
        result["upperRight"] = parsed["upperRight"]
    if parsed.get("lowerCenter", ""):
        result["lowerCenter"] = parsed["lowerCenter"]
    return result, None


def safe_category(value: str | None) -> str | None:
    if not value or not value.startswith("cards/"):
        return None
    parts = [slug(p) for p in value.split("/")]
    if any(not p for p in parts) or parts[0] != "cards":
        return None
    return "/".join(parts)


def acceptable_noncard_medium(parsed: dict, provenance: dict) -> bool:
    proposed = tokens(" ".join([parsed.get("proposedSlug") or "", parsed.get("title") or "",
                                 " ".join(parsed.get("confidentlyVisible", []))]))
    overlap = proposed & metadata_terms(provenance)
    if not parsed.get("proposedSlug") or not overlap:
        return False
    bad = ("identity", "name", "illegible", "clipped", "glyph", "icon", "text", "orientation",
           "cannot be determined", "not determinable", "unclear whether")
    uncertainty = uncertain_text(parsed).lower()
    return not any(word in uncertainty for word in bad)


def queue_entry(rec: dict, parsed: dict | None, provenance: dict, reason: str) -> dict:
    vision = rec.get("vision") or {}
    entry = {
        "sourcePath": rec["sourcePath"],
        "sourceKind": rec["sourceKind"],
        "sourceUrl": provenance.get("sourceUrl"),
        "sourceSha256": rec["sha256"],
        "provenance": provenance,
        "orientation": parsed.get("orientation") if parsed else None,
        "confidentlyVisible": parsed.get("confidentlyVisible", []) if parsed else [],
        "visibleText": structured_visible(parsed) if parsed else {},
        "uncertainties": list(parsed.get("uncertainties", [])) if parsed else [],
        "reasonSkipped": reason,
        "vision": {
            "provider": vision.get("provider"), "model": vision.get("model"),
            "sessionId": vision.get("sessionId"), "resultPath": vision.get("resultPath"),
            "iconVerification": vision.get("iconVerification"),
            "evidencePath": (vision.get("iconVerification") or {}).get("evidencePath"),
        },
        "status": "open",
    }
    failure = vision.get("uprightVerificationFailure") or vision.get("failure")
    if failure:
        entry["uncertainties"].append(f"Vision tooling/orientation verification failure: {failure}")
    return entry


def promote_image(source: Path, target: Path, correction: str | None) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if correction in ROTATE:
        with Image.open(source) as im:
            im.transpose(ROTATE[correction]).save(target, format="PNG", optimize=False)
    else:
        shutil.copy2(source, target)


def main() -> int:
    progress = json.loads(vb.PROGRESS.read_text())
    queue = json.loads(QUEUE.read_text())
    existing_queue = {e["sourcePath"]: e for e in queue["entries"]}
    provenance_by_path = build_provenance(progress)
    baseline_complete = progress["baseline"]["previouslyComplete"]
    previous_deferred = progress["baseline"]["previouslyDeferred"]
    decisions = {}
    candidates = []

    for rec in progress["records"]:
        provenance = provenance_by_path[rec["sourcePath"]]
        rec["provenance"] = provenance
        if rec["status"] in {"complete", "deferred"}:
            continue
        if rec["sourcePath"] in KNOWN_COMPLETE:
            item = KNOWN_COMPLETE[rec["sourcePath"]]
            decisions[rec["sourcePath"]] = ("completeKnown", item)
            continue
        if rec["status"] == "visionFailed":
            decisions[rec["sourcePath"]] = ("defer", "native vision or upright-verification failed")
            continue
        if rec["status"] != "visionRead":
            decisions[rec["sourcePath"]] = ("defer", f"unexpected processing state {rec['status']}")
            continue
        result = json.loads((vb.REPO / rec["vision"]["resultPath"]).read_text())
        parsed = result["parsed"]
        if result.get("iconVerification"):
            rec["vision"]["iconVerification"] = {
                k: result["iconVerification"].get(k)
                for k in ("status", "sessionId", "evidencePath", "claimed", "promptVersion")
            }
        rec["vision"]["confidence"] = parsed.get("confidence")
        rec["semanticRead"] = {k: parsed.get(k) for k in (
            "componentType", "cardSide", "title", "typeLine", "body", "footer", "upperRight",
            "lowerCenter", "visibleText", "confidentlyVisible", "proposedCategory", "proposedSlug",
            "confidence", "uncertainties", "orientation"
        )}
        is_card = rec["sourcePath"].startswith("assets/tts-mod/extract/v2-dl/tree/cards/")
        confidence = parsed.get("confidence")
        uncertainties = parsed.get("uncertainties") or []
        if is_card:
            card_side = parsed.get("cardSide")
            roles = source_roles(provenance)
            if card_side == "face":
                if roles == {"BackURL"}:
                    decisions[rec["sourcePath"]] = ("defer", "pixels look like a face but TTS provenance identifies only BackURL; side role conflicts")
                    continue
                if confidence != "high" or uncertainties:
                    decisions[rec["sourcePath"]] = ("defer", "exact card identity/transcription/icon/category is not uniformly high-confidence")
                    continue
                if parsed.get("visibleText", ""):
                    decisions[rec["sourcePath"]] = ("defer", "meaningful visible text falls outside the established minimal sidecar fields")
                    continue
                category = safe_category(parsed.get("proposedCategory"))
                stem = slug(parsed.get("proposedSlug") or "")
                if not category or not stem or not parsed.get("title"):
                    decisions[rec["sourcePath"]] = ("defer", "canonical title, category, or filename is not materially established")
                    continue
                sidecar, error = sidecar_for(parsed)
                if error:
                    decisions[rec["sourcePath"]] = ("defer", error)
                    continue
                assert sidecar is not None
                claimed_icons = set(re.findall(
                    r"\[([A-Za-z][A-Za-z0-9]*)\]",
                    " ".join(str(sidecar.get(k, "")) for k in ("typeLine", "body", "upperRight", "lowerCenter")),
                ))
                for position in ("upperRight", "lowerCenter"):
                    if sidecar.get(position):
                        claimed_icons.add(sidecar[position])
                verification = result.get("iconVerification", {})
                if claimed_icons and verification.get("status") != "passed":
                    decisions[rec["sourcePath"]] = (
                        "defer",
                        "claimed glossary icons did not all pass a focused direct card-to-glossary crop comparison",
                    )
                    continue
                correction = result.get("orientationCorrection")
                ext = ".png" if correction else Path(rec["sourcePath"]).suffix.lower()
                target = f"{category}/{stem}{ext}"
                candidates.append({"record": rec, "parsed": parsed, "sidecar": sidecar,
                                   "target": target, "correction": correction})
                decisions[rec["sourcePath"]] = ("candidate", target)
            elif card_side in {"back", "referenceSheet", "artOnly"}:
                if confidence == "high" and not uncertainties:
                    decisions[rec["sourcePath"]] = ("completeInPlace", "high-confidence non-rules card/reference classification; no minimal rules sidecar applies")
                else:
                    decisions[rec["sourcePath"]] = ("defer", "card back/reference/art-only identity or exact visible content is not uniformly high-confidence")
            elif card_side == "notCard" and confidence == "high" and not uncertainties and parsed.get("proposedSlug"):
                decisions[rec["sourcePath"]] = ("completeInPlace", "pixels establish a non-card asset misfiled under cards; semantic read retained in progress")
            else:
                decisions[rec["sourcePath"]] = ("defer", "card face/back/component role is materially uncertain")
        else:
            if confidence == "high" and not uncertainties and parsed.get("proposedSlug") and parsed.get("proposedCategory"):
                decisions[rec["sourcePath"]] = ("completeInPlace", "high-confidence pixel identity/category; source image remains manifest-backed in place")
            elif confidence == "medium" and acceptable_noncard_medium(parsed, provenance):
                decisions[rec["sourcePath"]] = ("completeInPlace", "pixel identity is corroborated by exact TTS object/GUID role metadata; only physical container/texture function was uncertain")
            else:
                decisions[rec["sourcePath"]] = ("defer", "identity, canonical filename/category, transcription, icon mapping, or component function remains materially low-confidence")

    # Any two different sources that want the same canonical path are a source-fidelity conflict.
    groups = defaultdict(list)
    for item in candidates:
        groups[item["target"]].append(item)
    accepted = []
    for target, items in groups.items():
        if len(items) > 1:
            for item in items:
                decisions[item["record"]["sourcePath"]] = ("defer", f"multiple distinct source images claim canonical path {target}; variants require review")
        else:
            accepted.append(items[0])

    created_sidecars = copied_images = 0
    for item in accepted:
        rec = item["record"]
        source = vb.REPO / rec["sourcePath"]
        target = vb.REPO / item["target"]
        sidecar_path = target.with_suffix(".json")
        if target.exists() or sidecar_path.exists():
            # Never overwrite existing canonical work, including approved entries.
            decisions[rec["sourcePath"]] = ("defer", f"canonical destination already exists: {target.relative_to(vb.REPO)}")
            continue
        promote_image(source, target, item["correction"])
        vb.atomic_json(sidecar_path, item["sidecar"])
        created_sidecars += 1
        copied_images += 1
        rec["canonicalPath"] = target.relative_to(vb.REPO).as_posix()
        rec["sidecarPath"] = sidecar_path.relative_to(vb.REPO).as_posix()
        rec["completionBasis"] = "native GPT-5.6 pixel read: uniformly high-confidence individual face; validated minimal sidecar and canonical path"
        rec["orientation"] = {
            "sourceOrientation": item["correction"] or "upright",
            "canonicalOrientation": "upright",
        }
        rec["canonicalSha256"] = sha256(target)
        decisions[rec["sourcePath"]] = ("promoted", rec["canonicalPath"])

    newly_complete = 0
    newly_deferred = 0
    for rec in progress["records"]:
        if rec["status"] in {"complete", "deferred"}:
            continue
        decision, detail = decisions[rec["sourcePath"]]
        provenance = provenance_by_path[rec["sourcePath"]]
        parsed = None
        if rec.get("vision", {}).get("resultPath"):
            result_path = vb.REPO / rec["vision"]["resultPath"]
            if result_path.exists():
                result = json.loads(result_path.read_text())
                parsed = result.get("parsed")
        if decision == "promoted":
            rec["status"] = "complete"
            newly_complete += 1
        elif decision == "completeKnown":
            rec["status"] = "complete"
            rec["canonicalPath"] = rec["sourcePath"]
            rec["sidecarPath"] = None
            rec["completionBasis"] = detail["classification"]
            rec["evidence"] = detail["evidence"]
            newly_complete += 1
        elif decision == "completeInPlace":
            rec["status"] = "complete"
            rec["canonicalPath"] = rec["sourcePath"]
            rec["sidecarPath"] = None
            rec["completionBasis"] = detail
            newly_complete += 1
        else:
            reason = detail if decision == "defer" else f"unresolved adjudication state: {decision} {detail}"
            rec["status"] = "deferred"
            rec["canonicalPath"] = None
            rec["sidecarPath"] = None
            rec["reviewQueuePath"] = QUEUE.relative_to(vb.REPO).as_posix()
            rec["deferReason"] = reason
            existing_queue[rec["sourcePath"]] = queue_entry(rec, parsed, provenance, reason)
            newly_deferred += 1

    queue["entries"] = sorted(existing_queue.values(), key=lambda x: x["sourcePath"])
    queue["updatedAt"] = vb.utc_now()
    vb.atomic_json(QUEUE, queue)
    vb.checkpoint(progress)
    counts = progress["counts"]
    assert counts.get("pending", 0) == 0 and counts.get("visionRead", 0) == 0 and counts.get("visionFailed", 0) == 0, counts
    assert len(queue["entries"]) == counts["deferred"], (len(queue["entries"]), counts)
    progress["runSummary"] = {
        "baselinePreviouslyComplete": baseline_complete,
        "baselinePreviouslyDeferred": previous_deferred,
        "newlyCompleted": newly_complete,
        "newlyDeferred": newly_deferred,
        "totalComplete": counts["complete"],
        "totalDeferred": counts["deferred"],
        "remainingUnaccounted": 0,
        "sidecarsCreated": created_sidecars,
        "imagesCopiedToCanonicalCatalog": copied_images,
        "sourceFilesMovedOrRenamed": 0,
        "completedAt": vb.utc_now(),
    }
    vb.atomic_json(vb.PROGRESS, progress)
    print(json.dumps(progress["runSummary"] | {"queueEntries": len(queue["entries"])}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
