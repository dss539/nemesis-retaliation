#!/usr/bin/env python3
"""Resumable one-image-per-session native GPT-5.6 vision pass."""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time

from PIL import Image

REPO = Path("/home/smithers/nemesis-retaliation")
PROGRESS = REPO / "assets/tts-mod/extract/vision-progress.json"
RESULT_DIR = REPO / "assets/tts-mod/extract/vision-results"
PROVIDER = "openai-codex"
MODEL = "gpt-5.6-sol"
PROMPT_VERSION = 1

ICON_GLOSSARY = """Canonical icon identifiers (choose one only on a confident morphology match; this list may not include card-local action glyphs):
Shoot die: shootDie2 red triangle 2; shootDie3 red triangle 3; shootDie4 red triangle 4; shootDie5 red triangle 5; shootDieAmmoLoss red triangle with three cartridges; shootDieCritical red triangle with skull.
Burst die: burstDie1 purple square 1; burstDie2 purple square 2; burstDie3 purple square 3; burstDie4 purple square 4; burstDieAdditionalEffects purple square with four white corner marks.
Noise die: noiseDie1 yellow triangle 1; noiseDie2 yellow triangle 2; noiseDie3 yellow triangle 3; noiseDie4 yellow triangle 4; noiseDieHazard yellow hazard symbol.
Items: redItem red badge with cartridges; yellowItem yellow badge with wrench; greenItem green badge with cross.
Map: computer; fire; malfunction; noise; secure; corridorEW; corridorNESW; corridorNWSE; lifeSupportActive; lifeSupportInactive crossed out; hibernatoriumActive; hibernatoriumInactive crossed out; lander; autodestruction three-lobed warning.
Tactical Gear tokens: oxygenToken yellow; ammoToken red; grenadeToken purple; medpackToken green.
Tactical Gear slots: ammoSlot red; grenadeSlot purple; oxygenSlot yellow; medpackSlot green; anySlot grey.
General: character astronaut; oxygen supply; characterHealth cross with EKG; actionCard; robot; notInCombat prohibition (card art may show crossed-out gun or crossed-out Intruder); intruder curled white exoskeleton.
"""

BASE_PROMPT = """Inspect this ONE image's actual pixels from scratch. Ignore its filename and directory as semantic evidence. Do not infer identity from neighboring files, sheet position, or expected game inventory. First determine how the FILE would need to rotate to make all meaningful typography upright. Transcribe only visible pixels; never reconstruct clipped, hidden, or illegible content. Preserve capitalization, punctuation, headings, line/panel breaks, and misspellings. Embed confidently matched canonical icons inline as [camelCase]. For a bare corner icon, use a position field. If a glyph is not confidently in the glossary, write a literal [ICON: color shape glyph] in visibleText/body and record the uncertainty; do not guess its meaning.

{glossary}

Return exactly one JSON object and no Markdown with these keys:
- orientation: one of upright, rotate90cw, rotate90ccw, rotate180, rotationIrrelevant (the rotate value means rotate the FILE that way to make it upright)
- componentType: precise visual component type
- cardSide: one of face, back, referenceSheet, artOnly, notCard, uncertain
- title: exact printed title or empty string
- typeLine: exact printed type/trait line or empty string
- body: exact rules/effect text with meaningful line breaks and inline [iconTokens], or empty string
- footer: exact footer/owner label or empty string
- upperRight: canonical icon identifier, literal uncertain icon description, or empty string
- lowerCenter: canonical icon identifier, literal uncertain icon description, or empty string
- visibleText: other visible text not represented above, verbatim, or empty string
- confidentlyVisible: array of concise pixel facts
- proposedCategory: semantic slash path such as cards/character/<owner>/action, cards/game/event, cards/game/item/<type>, cards/game/objective, cards/reference, tokens/status, tokens/character, tokens/intruder, tiles/room, figures, models/texture, bags/texture; null if pixels do not support it
- proposedSlug: lowercase kebab-case semantic filename stem from a visible title or unmistakable depicted identity; null if materially uncertain
- confidence: high, medium, or low. Use high only when identity, orientation, every transcription, every icon mapping, category, and slug are all materially unambiguous.
- uncertainties: array listing every material uncertainty. Include illegible/clipped text, unknown icons, ambiguous face/back role, uncertain owner/category, source-art oddity, or uncertain filename identity.

A line-leading glyph followed by a colon can be a local action/ability glyph absent from the glossary. Do not force it into the list. A card back or art-only component must not receive invented rules text. Do not call unreadable tooling output an image uncertainty."""


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def extract_session(stdout: str) -> str | None:
    matches = re.findall(r"session_id:\s*([0-9A-Za-z_-]+)", stdout)
    return matches[-1] if matches else None


def extract_json(stdout: str) -> dict:
    # The CLI may print reasoning and a session_id before the final JSON.
    starts = [m.start() for m in re.finditer(r"\{", stdout)]
    decoder = json.JSONDecoder()
    for start in reversed(starts):
        try:
            obj, _ = decoder.raw_decode(stdout[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and "orientation" in obj and "confidence" in obj:
            return obj
    raise ValueError("no final vision JSON object found")


def result_path(record: dict) -> Path:
    return RESULT_DIR / f"{record['sha256']}.json"


def run_one(record: dict, attempts: int = 1) -> dict:
    image = REPO / record["sourcePath"]
    upload_image = image
    staging_note = None
    staged_path = None
    if image.stat().st_size > 15_000_000:
        suffix = ".png" if image.suffix.lower() == ".png" else ".jpg"
        handle = tempfile.NamedTemporaryFile(prefix="nemesis-vision-", suffix=suffix, delete=False)
        handle.close()
        staged_path = Path(handle.name)
        with Image.open(image) as raw:
            source_dimensions = [raw.width, raw.height]
            staged = raw.copy()
            staged.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
            uploaded_dimensions = [staged.width, staged.height]
            if suffix == ".png":
                staged.save(staged_path, format="PNG", optimize=False)
            else:
                staged.convert("RGB").save(staged_path, format="JPEG", quality=95, subsampling=0)
        upload_image = staged_path
        staging_note = {
            "transform": "high-quality 4096px-bounded staging derivative for provider upload",
            "sourceDimensions": source_dimensions,
            "uploadedDimensions": uploaded_dimensions,
            "sourcePreservedUnchanged": True,
        }
    prompt = BASE_PROMPT.format(glossary=ICON_GLOSSARY)
    errors = []
    for attempt in range(1, attempts + 1):
        started = utc_now()
        cmd = [
            "hermes", "chat",
            "--provider", PROVIDER,
            "--model", MODEL,
            "--reasoning", "low",
            "--image", str(upload_image),
            "--max-turns", "2",
            "--pass-session-id",
            "--source", "tool",
            "-Q", "-q", prompt,
        ]
        try:
            proc = subprocess.run(cmd, cwd=REPO, text=True, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, timeout=300)
        finally:
            if staged_path is not None:
                staged_path.unlink(missing_ok=True)
        stdout = proc.stdout
        try:
            if proc.returncode != 0:
                raise RuntimeError(f"CLI exit {proc.returncode}")
            parsed = extract_json(stdout)
            session = extract_session(stdout)
            if not session:
                raise ValueError("missing session_id")
            result = {
                "schemaVersion": 1,
                "sourcePath": record["sourcePath"],
                "sourceSha256": record["sha256"],
                "provider": PROVIDER,
                "model": MODEL,
                "sessionId": session,
                "promptVersion": PROMPT_VERSION,
                "startedAt": started,
                "completedAt": utc_now(),
                "attempt": attempt,
                "parsed": parsed,
                "cliOutput": stdout,
            }
            if staging_note:
                result["visionInputTransform"] = staging_note
            atomic_json(result_path(record), result)
            return {"ok": True, "result": result, "path": str(result_path(record).relative_to(REPO))}
        except Exception as exc:
            errors.append({"attempt": attempt, "at": utc_now(), "error": str(exc), "cliOutput": stdout})
            if attempt < attempts:
                time.sleep(2 ** attempt)
    failure = {
        "schemaVersion": 1,
        "sourcePath": record["sourcePath"],
        "sourceSha256": record["sha256"],
        "provider": PROVIDER,
        "model": MODEL,
        "promptVersion": PROMPT_VERSION,
        "failedAt": utc_now(),
        "errors": errors,
    }
    atomic_json(result_path(record), failure)
    return {"ok": False, "failure": failure, "path": str(result_path(record).relative_to(REPO))}


def checkpoint(progress: dict) -> None:
    counts = {}
    for status in ("complete", "deferred", "visionRead", "visionFailed", "pending"):
        counts[status] = sum(r["status"] == status for r in progress["records"])
    progress["counts"] = counts
    progress["updatedAt"] = utc_now()
    pending = [r["sourcePath"] for r in progress["records"] if r["status"] == "pending"]
    progress["nextPosition"] = pending[0] if pending else None
    atomic_json(PROGRESS, progress)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()
    progress = json.loads(PROGRESS.read_text())
    pending = [r for r in progress["records"] if r["status"] in {"pending", "visionFailed"}]
    if args.limit is not None:
        pending = pending[:args.limit]
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    by_sha = {r["sha256"]: r for r in progress["records"]}
    completed = failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run_one, r): r for r in pending}
        for fut in concurrent.futures.as_completed(futures):
            requested = futures[fut]
            try:
                outcome = fut.result()
            except Exception as exc:
                outcome = {"ok": False, "failure": {"error": str(exc)}, "path": None}
            rec = by_sha[requested["sha256"]]
            if outcome["ok"]:
                rec["status"] = "visionRead"
                rec["vision"] = {
                    "provider": PROVIDER,
                    "model": MODEL,
                    "sessionId": outcome["result"]["sessionId"],
                    "resultPath": outcome["path"],
                    "confidence": outcome["result"]["parsed"].get("confidence"),
                }
                completed += 1
            else:
                rec["status"] = "visionFailed"
                rec["vision"] = {"provider": PROVIDER, "model": MODEL, "resultPath": outcome.get("path"),
                                 "failure": outcome.get("failure")}
                failures += 1
            checkpoint(progress)
            total = completed + failures
            print(json.dumps({"processedThisRun": total, "visionRead": completed,
                              "visionFailed": failures, "nextPosition": progress["nextPosition"]}), flush=True)
    checkpoint(progress)
    print(json.dumps({"done": True, "requested": len(pending), "visionRead": completed,
                      "visionFailed": failures, "counts": progress["counts"],
                      "nextPosition": progress["nextPosition"]}, indent=2), flush=True)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
