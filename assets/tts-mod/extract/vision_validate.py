#!/usr/bin/env python3
"""End-to-end validation and count reconciliation for vision extraction."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
EXTRACT = REPO / "assets/tts-mod/extract"
PROGRESS = EXTRACT / "vision-progress.json"
QUEUE = EXTRACT / "low-confidence-review.json"
TREE = EXTRACT / "v2-dl/tree"
MANIFEST = TREE / "manifest.json"
CATALOG = TREE / "catalog.md"
REPORT = EXTRACT / "vision-validation.json"
ALLOWED_SIDECAR_KEYS = {"typeLine", "body", "upperRight", "lowerCenter"}
ICON_TOKENS = {
    "shootDie2", "shootDie3", "shootDie4", "shootDie5", "shootDieAmmoLoss", "shootDieCritical",
    "burstDie1", "burstDie2", "burstDie3", "burstDie4", "burstDieAdditionalEffects",
    "noiseDie1", "noiseDie2", "noiseDie3", "noiseDie4", "noiseDieHazard",
    "redItem", "yellowItem", "greenItem", "computer", "fire", "malfunction", "noise", "secure",
    "corridorEW", "corridorNESW", "corridorNWSE", "lifeSupportActive", "lifeSupportInactive",
    "hibernatoriumActive", "hibernatoriumInactive", "lander", "autodestruction", "oxygenToken",
    "ammoToken", "grenadeToken", "medpackToken", "ammoSlot", "grenadeSlot", "oxygenSlot",
    "medpackSlot", "anySlot", "character", "oxygen", "characterHealth", "actionCard", "robot",
    "notInCombat", "intruder",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    tmp.replace(path)


def main() -> int:
    failures: list[dict] = []
    checks: dict[str, object] = {}
    def fail(check: str, detail: object) -> None:
        failures.append({"check": check, "detail": detail})

    progress = json.loads(PROGRESS.read_text())
    queue = json.loads(QUEUE.read_text())
    manifest = json.loads(MANIFEST.read_text())
    records = progress["records"]
    entries = queue["entries"]
    baseline_total = sum(
        progress["baseline"][key]
        for key in ("previouslyComplete", "previouslyDeferred", "pending")
    )

    # Inventory closure and exact state partition.
    paths = [r["sourcePath"] for r in records]
    shas = [r["sha256"] for r in records]
    states = Counter(r["status"] for r in records)
    checks["inScopeRecords"] = len(records)
    checks["stateCounts"] = dict(states)
    if len(records) != baseline_total:
        fail("in-scope count", {"records": len(records), "baseline": baseline_total})
    if len(paths) != len(set(paths)):
        fail("duplicate progress paths", [p for p,c in Counter(paths).items() if c > 1])
    if len(shas) != len(set(shas)):
        fail("duplicate progress SHA-256", [s for s,c in Counter(shas).items() if c > 1])
    unexpected = sorted(set(states) - {"complete", "deferred"})
    if unexpected:
        fail("remaining unaccounted states", {s: states[s] for s in unexpected})
    if len(records) != states["complete"] + states["deferred"]:
        fail("two-state partition", dict(states))

    # Underlying assets must exist, decode, and retain source hash/dimensions.
    decode_failures=[]; hash_failures=[]; dimension_failures=[]
    for rec in records:
        path=REPO/rec["sourcePath"]
        if not path.exists():
            decode_failures.append({"path":rec["sourcePath"],"error":"missing"}); continue
        try:
            with Image.open(path) as im:
                im.verify()
            with Image.open(path) as im:
                dims=[im.width,im.height]
        except Exception as exc:
            decode_failures.append({"path":rec["sourcePath"],"error":str(exc)}); continue
        expected_dimensions = rec.get("dimensions")
        if expected_dimensions is not None and dims != expected_dimensions:
            dimension_failures.append({"path":rec["sourcePath"],"expected":expected_dimensions,"actual":dims})
        actual=sha256(path)
        if actual != rec["sha256"]:
            hash_failures.append({"path":rec["sourcePath"],"expected":rec["sha256"],"actual":actual})
    checks["sourceImagesDecoded"] = len(records)-len(decode_failures)
    if decode_failures: fail("source image decode/existence", decode_failures)
    if hash_failures: fail("source hash preservation", hash_failures)
    if dimension_failures: fail("source dimension preservation", dimension_failures)

    # Queue is exact, durable, and one-to-one with deferred state.
    qpaths=[e["sourcePath"] for e in entries]
    deferred_paths={r["sourcePath"] for r in records if r["status"]=="deferred"}
    if len(qpaths) != len(set(qpaths)):
        fail("duplicate review entries", [p for p,c in Counter(qpaths).items() if c>1])
    if set(qpaths) != deferred_paths:
        fail("queue/deferred mismatch", {"queueOnly":sorted(set(qpaths)-deferred_paths),"deferredOnly":sorted(deferred_paths-set(qpaths))})
    required_queue={"sourcePath","sourceKind","sourceSha256","provenance","confidentlyVisible","visibleText","uncertainties","reasonSkipped","vision","status"}
    malformed=[]
    for entry in entries:
        missing=sorted(required_queue-set(entry))
        if missing or not entry.get("reasonSkipped") or entry.get("status")!="open":
            malformed.append({"path":entry.get("sourcePath"),"missing":missing,"status":entry.get("status")})
        evidence=entry.get("vision",{}).get("evidencePath")
        if evidence and not (REPO/evidence).exists():
            malformed.append({"path":entry.get("sourcePath"),"missingEvidence":evidence})
    if malformed: fail("review entry schema/evidence", malformed)
    checks["reviewEntries"] = len(entries)

    # Extraction manifest and catalog remain closed and mutually consistent.
    mfiles=[e["file"] for e in manifest]; murls=[e["url"] for e in manifest]
    if len(mfiles)!=len(set(mfiles)): fail("duplicate manifest paths", [p for p,c in Counter(mfiles).items() if c>1])
    if len(murls)!=len(set(murls)): fail("duplicate manifest URLs", [u for u,c in Counter(murls).items() if c>1])
    manifest_bad=[]
    for entry in manifest:
        path=TREE/entry["file"]
        if not path.exists(): manifest_bad.append({"file":entry["file"],"error":"missing"}); continue
        if path.stat().st_size != entry["size"]:
            manifest_bad.append({"file":entry["file"],"expectedSize":entry["size"],"actualSize":path.stat().st_size})
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            try:
                with Image.open(path) as im: im.verify()
            except Exception as exc: manifest_bad.append({"file":entry["file"],"error":str(exc)})
    if manifest_bad: fail("manifest existence/size/decode", manifest_bad)
    catalog_text=CATALOG.read_text()
    total_match=re.search(r"Manifest assets:\s*(\d+)",catalog_text)
    catalog_total=int(total_match.group(1)) if total_match else None
    catalog_sections = {
        name: int(count)
        for name, count in re.findall(r"^## (.+?) \((\d+) files\)$", catalog_text, re.M)
    }
    manifest_sections = Counter(str(Path(name).parent) for name in mfiles)
    expected_catalog_sections = manifest_sections.copy()
    tree_prefix = "assets/tts-mod/extract/v2-dl/tree/"
    for rec in records:
        if rec["sourceKind"] != "generated" or not rec["sourcePath"].startswith(tree_prefix):
            continue
        relative = rec["sourcePath"][len(tree_prefix):]
        parent = str(Path(relative).parent)
        if "_cards" not in parent and parent in catalog_sections:
            expected_catalog_sections[parent] += 1
    expected_catalog_sections.setdefault("unsorted", 0)
    if catalog_sections != dict(expected_catalog_sections):
        fail("catalog/manifest section mismatch", {
            "catalog": catalog_sections,
            "manifestPlusCataloguedGenerated": dict(sorted(expected_catalog_sections.items())),
        })
    if catalog_total != len(manifest):
        fail("catalog total", {"catalog":catalog_total,"manifest":len(manifest)})
    checks["manifestEntries"] = len(manifest)
    checks["manifestUniqueUrls"] = len(set(murls))
    checks["catalogEntries"] = catalog_total
    checks["catalogSections"] = len(catalog_sections)

    # Canonical card pairs and established minimal schema.
    sidecars=sorted((REPO/"cards").rglob("*.json"))
    sidecar_bad=[]; canonical_images=set(); sidecar_paths=set()
    for sidecar in sidecars:
        rel=sidecar.relative_to(REPO).as_posix(); sidecar_paths.add(rel)
        try: data=json.loads(sidecar.read_text())
        except Exception as exc: sidecar_bad.append({"path":rel,"error":str(exc)}); continue
        extra=sorted(set(data)-ALLOWED_SIDECAR_KEYS)
        if extra or "body" not in data or any(not isinstance(v,str) for v in data.values()):
            sidecar_bad.append({"path":rel,"extraKeys":extra,"keys":sorted(data)})
        combined=" ".join(data.values())
        unknown=sorted(set(re.findall(r"\[([A-Za-z][A-Za-z0-9]*)\]",combined))-ICON_TOKENS)
        positions=[data[k] for k in ("upperRight","lowerCenter") if data.get(k) and data[k] not in ICON_TOKENS]
        if unknown or positions: sidecar_bad.append({"path":rel,"unknownInline":unknown,"unknownPositions":positions})
        matches=[p for p in sidecar.parent.glob(sidecar.stem+".*") if p.suffix.lower() in {".png",".jpg",".jpeg"}]
        if len(matches)!=1:
            sidecar_bad.append({"path":rel,"pairedImages":[p.relative_to(REPO).as_posix() for p in matches]})
        else:
            image=matches[0]; canonical_images.add(image.relative_to(REPO).as_posix())
            try:
                with Image.open(image) as im: im.verify()
            except Exception as exc: sidecar_bad.append({"path":image.relative_to(REPO).as_posix(),"error":str(exc)})
    if sidecar_bad: fail("canonical sidecar/image validation", sidecar_bad)
    checks["canonicalSidecars"] = len(sidecars)
    checks["canonicalImagesPaired"] = len(canonical_images)

    # Completed records with canonical/sidecar paths must resolve; deferred records must not claim them.
    record_bad=[]
    claimed_canonical=[]
    for rec in records:
        if rec["status"]=="complete":
            cp=rec.get("canonicalPath")
            if not cp or not (REPO/cp).exists(): record_bad.append({"path":rec["sourcePath"],"canonicalPath":cp})
            else: claimed_canonical.append(cp)
            sp=rec.get("sidecarPath")
            if sp and (sp not in sidecar_paths or not (REPO/sp).exists()):
                record_bad.append({"path":rec["sourcePath"],"sidecarPath":sp})
        else:
            if rec.get("canonicalPath") or rec.get("sidecarPath"):
                record_bad.append({"path":rec["sourcePath"],"deferredClaimsCanonical":rec.get("canonicalPath"),"sidecar":rec.get("sidecarPath")})
    if record_bad: fail("progress canonical references",record_bad)
    checks["completeCanonicalReferences"] = len(claimed_canonical)

    summary=progress.get("runSummary",{})
    expected_new_complete=states["complete"]-progress["baseline"]["previouslyComplete"]
    expected_new_deferred=states["deferred"]-progress["baseline"]["previouslyDeferred"]
    expected_sidecars=len(sidecars)-progress["baseline"]["approvedCardSidecars"]
    reconciliation={
        "baselineInScope":baseline_total,
        "baselinePreviouslyComplete":progress["baseline"]["previouslyComplete"],
        "baselinePreviouslyDeferred":progress["baseline"]["previouslyDeferred"],
        "newlyCompleted":expected_new_complete,
        "newlyDeferred":expected_new_deferred,
        "totalComplete":states["complete"],
        "totalDeferred":states["deferred"],
        "remainingUnaccounted":len(records)-states["complete"]-states["deferred"],
        "sidecarsCreated":expected_sidecars,
        "totalSidecars":len(sidecars),
        "sourceFilesMovedOrRenamed":summary.get("sourceFilesMovedOrRenamed"),
    }
    for key in ("newlyCompleted","newlyDeferred","totalComplete","totalDeferred","remainingUnaccounted","sidecarsCreated"):
        if summary.get(key)!=reconciliation[key]: fail("run summary reconciliation",{"field":key,"summary":summary.get(key),"actual":reconciliation[key]})
    checks["reconciliation"] = reconciliation
    report={
        "schemaVersion":1,
        "validatedProgressUpdatedAt":progress.get("updatedAt"),
        "passed":not failures,
        "checks":checks,
        "failureCount":len(failures),
        "failures":failures,
    }
    atomic_json(REPORT,report)
    print(json.dumps(report,indent=2))
    return 0 if not failures else 1


if __name__=="__main__":
    raise SystemExit(main())
