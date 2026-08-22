#!/usr/bin/env python3
"""Focused direct card-to-glossary icon verification for clear reads."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

import vision_batch as vb

GLOSSARY = vb.REPO / "docs/rules/icon-glossary.md"
QA_DIR = vb.REPO / "docs/qa/card-icon-comparisons"
ROTATE = {
    "rotate90cw": Image.Transpose.ROTATE_270,
    "rotate90ccw": Image.Transpose.ROTATE_90,
    "rotate180": Image.Transpose.ROTATE_180,
}
PROMPT_VERSION = 1


def icon_map() -> dict[str, Path]:
    text = GLOSSARY.read_text()
    pairs = re.findall(r"\*\*([A-Za-z][A-Za-z0-9]*)\*\*.*?\(`(assets/icons/[^`]+)`\)", text)
    result = {name: vb.REPO / path for name, path in pairs}
    if len(result) != 50:
        raise RuntimeError(f"expected 50 approved icon files (49 page-40 plus Number of Characters), found {len(result)}")
    missing = [str(p) for p in result.values() if not p.exists()]
    if missing:
        raise RuntimeError(f"missing icon files: {missing}")
    return result


def claims(parsed: dict) -> list[str]:
    combined = " ".join(str(parsed.get(k, "")) for k in ("body", "upperRight", "lowerCenter"))
    found = set(re.findall(r"\[([A-Za-z][A-Za-z0-9]*)\]", combined))
    for key in ("upperRight", "lowerCenter"):
        if parsed.get(key):
            found.add(parsed[key])
    return sorted(found)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def contain(im: Image.Image, width: int, height: int) -> Image.Image:
    out = im.copy()
    out.thumbnail((width, height), Image.Resampling.LANCZOS)
    return out


def make_sheet(source: Path, correction: str | None, icons: dict[str, Path], claimed: list[str], dest: Path) -> None:
    left_w, right_w, h = 1120, 900, 1550
    sheet = Image.new("RGB", (left_w + right_w, h), "#ececec")
    draw = ImageDraw.Draw(sheet)
    title_font = load_font(24)
    label_font = load_font(16)
    with Image.open(source) as raw:
        card = raw.convert("RGBA")
        if correction in ROTATE:
            card = card.transpose(ROTATE[correction])
        card = contain(card, left_w - 40, h - 80)
        x=(left_w-card.width)//2; y=60+(h-80-card.height)//2
        sheet.paste(Image.new("RGB", card.size, "white"), (x,y))
        sheet.paste(card, (x,y), card if "A" in card.getbands() else None)
    draw.text((20, 18), "ACTUAL CARD PIXELS", fill="black", font=title_font)
    draw.text((left_w + 15, 18), "49 VERIFIED RULEBOOK GLOSSARY CROPS", fill="black", font=title_font)
    draw.text((left_w + 15, 45), "Claims: " + ", ".join(claimed), fill="#7a0000", font=label_font)
    cols, cell_w, cell_h = 5, right_w // 5, 145
    for i,(name,path) in enumerate(sorted(icons.items())):
        row,col=divmod(i,cols)
        x0=left_w+col*cell_w; y0=75+row*cell_h
        draw.rectangle((x0+2,y0+2,x0+cell_w-3,y0+cell_h-3),outline="#888",width=1)
        with Image.open(path) as raw:
            icon=raw.convert("RGBA")
            icon=contain(icon,100,90)
            ix=x0+(cell_w-icon.width)//2; iy=y0+8+(90-icon.height)//2
            sheet.paste(Image.new("RGB",icon.size,"white"),(ix,iy))
            sheet.paste(icon,(ix,iy),icon if "A" in icon.getbands() else None)
        color="#8b0000" if name in claimed else "black"
        bbox=draw.textbbox((0,0),name,font=label_font)
        tx=x0+(cell_w-(bbox[2]-bbox[0]))//2
        draw.text((tx,y0+105),name,fill=color,font=label_font)
    sheet.save(dest,format="PNG",optimize=False)


def extract_verification(stdout: str) -> dict:
    decoder=json.JSONDecoder()
    starts=[m.start() for m in re.finditer(r"\{",stdout)]
    for start in reversed(starts):
        try: obj,_=decoder.raw_decode(stdout[start:])
        except json.JSONDecodeError: continue
        if isinstance(obj,dict) and "claims" in obj and "allClaimsMatch" in obj:
            return obj
    raise ValueError("no icon-verification JSON found")


def verify_one(rec: dict, icons: dict[str, Path]) -> dict:
    result_file=vb.REPO/rec["vision"]["resultPath"]
    result=json.loads(result_file.read_text())
    parsed=result["parsed"]
    claimed=claims(parsed)
    if not claimed:
        result["iconVerification"]={
            "status":"notRequired","reason":"no canonical icon claims in minimal sidecar fields",
            "promptVersion":PROMPT_VERSION,
        }
        vb.atomic_json(result_file,result)
        return {"ok":True,"sha":rec["sha256"],"status":"notRequired"}
    unknown=sorted(set(claimed)-set(icons))
    if unknown:
        return {"ok":False,"sha":rec["sha256"],"error":f"unknown claimed tokens: {unknown}"}
    with tempfile.TemporaryDirectory(prefix="nemesis-icon-check-") as td:
        contact=Path(td)/f"{rec['sha256']}.png"
        make_sheet(vb.REPO/rec["sourcePath"],result.get("orientationCorrection"),icons,claimed,contact)
        prompt=f"""This ONE contact sheet contains the actual card pixels on the left and all 49 verified official rulebook glossary crops on the right. The first blind read claimed these canonical identifiers: {', '.join(claimed)}.
Compare internal glyph morphology directly, not surrounding rule semantics, labels, color alone, or filename/path. For every claimed identifier, locate every occurrence on the actual card and determine whether it matches the labeled glossary crop. The documented notInCombat exception is allowed: a card may use a crossed-out white gun while the glossary crop uses a crossed-out Intruder; both are the official notInCombat semantic icon. Do not force a match. If a claim is wrong but another labeled crop is a clear match, name the correction. If the card glyph is absent, clipped, too small, or a local non-glossary action glyph, say uncertain/mismatch.
Return JSON only: {{"claims":[{{"claimed":"token","verdict":"match|mismatch|uncertain","actual":"correctToken or empty","evidence":"concise morphology"}}],"allClaimsMatch":true|false,"confidence":"high|medium|low","uncertainties":[]}}. allClaimsMatch may be true only if every claim is a high-confidence match (including the documented notInCombat artwork variant)."""
        proc=subprocess.run([
            "hermes","chat","--provider",vb.PROVIDER,"--model",vb.MODEL,"--image",str(contact),
            "--reasoning","low",
            "--max-turns","2","--pass-session-id","--source","tool","-Q","-q",prompt,
        ],cwd=vb.REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600)
        if proc.returncode!=0:
            return {"ok":False,"sha":rec["sha256"],"error":f"CLI exit {proc.returncode}","cliOutput":proc.stdout}
        try:
            verification=extract_verification(proc.stdout)
            session=vb.extract_session(proc.stdout)
            if not session: raise ValueError("missing session_id")
        except Exception as exc:
            return {"ok":False,"sha":rec["sha256"],"error":str(exc),"cliOutput":proc.stdout}
        evidence_path=None
        if not verification.get("allClaimsMatch"):
            QA_DIR.mkdir(parents=True,exist_ok=True)
            evidence=QA_DIR/f"auto-{rec['sha256']}.png"
            shutil.copy2(contact,evidence)
            evidence_path=evidence.relative_to(vb.REPO).as_posix()
        result["iconVerification"]={
            "status":"passed" if verification.get("allClaimsMatch") and verification.get("confidence")=="high" else "failed",
            "provider":vb.PROVIDER,"model":vb.MODEL,"sessionId":session,
            "promptVersion":PROMPT_VERSION,"completedAt":vb.utc_now(),"claimed":claimed,
            "parsed":verification,"cliOutput":proc.stdout,"evidencePath":evidence_path,
        }
        vb.atomic_json(result_file,result)
        return {"ok":True,"sha":rec["sha256"],"status":result["iconVerification"]["status"],
                "sessionId":session,"evidencePath":evidence_path}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--workers",type=int,default=6); args=ap.parse_args()
    progress=json.loads(vb.PROGRESS.read_text()); icons=icon_map(); prelim=[]
    known_complete = {
        "assets/tts-mod/extract/v2-dl/tree/cards/character/combat-engineer-012.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/character/contractor-044.jpg",
        "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-025.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-035.png",
        "assets/tts-mod/extract/v2-dl/tree/cards/character/heavy-gun-operator-038.png",
    }
    for rec in progress["records"]:
        if rec["status"]!="visionRead" or not rec["sourcePath"].startswith("assets/tts-mod/extract/v2-dl/tree/cards/"):
            continue
        if rec["sourcePath"] in known_complete:
            continue
        result=json.loads((vb.REPO/rec["vision"]["resultPath"]).read_text()); p=result["parsed"]
        if result.get("iconVerification", {}).get("status") in {"passed", "failed", "notRequired"}:
            continue
        if not (p.get("cardSide")=="face" and p.get("confidence")=="high" and not p.get("uncertainties")):
            continue
        if p.get("visibleText") or not p.get("title") or not p.get("body") or not p.get("proposedSlug"):
            continue
        category=p.get("proposedCategory") or ""
        claimed=claims(p)
        if not category.startswith("cards/") or not claimed or not set(claimed) <= set(icons):
            continue
        clean_category="/".join(re.sub(r"[^a-z0-9]+","-",part.lower()).strip("-") for part in category.split("/"))
        clean_slug=re.sub(r"[^a-z0-9]+","-",p["proposedSlug"].lower()).strip("-")
        target_sidecar=(vb.REPO/clean_category/f"{clean_slug}.json")
        prelim.append((rec,target_sidecar))
    target_counts={p:sum(1 for _,q in prelim if q==p) for _,p in prelim}
    records=[rec for rec,target in prelim if target_counts[target]==1 and not target.exists()]
    by_sha={r["sha256"]:r for r in progress["records"]}; counts={"passed":0,"failed":0,"notRequired":0,"toolFailure":0}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(verify_one,r,icons):r for r in records}
        for future in concurrent.futures.as_completed(futures):
            out=future.result(); rec=by_sha[out["sha"]]
            if out["ok"]:
                counts[out["status"]]+=1
                rec["vision"]["iconVerification"]={"status":out["status"],"sessionId":out.get("sessionId"),"evidencePath":out.get("evidencePath")}
            else:
                counts["toolFailure"]+=1
                rec["vision"]["iconVerification"]={"status":"toolFailure","error":out}
            vb.checkpoint(progress)
            print(json.dumps({"processed":sum(counts.values()),**counts}),flush=True)
    vb.checkpoint(progress)
    print(json.dumps({"done":True,"candidates":len(records),**counts},indent=2),flush=True)
    return 0 if counts["toolFailure"]==0 else 1


if __name__=="__main__":
    raise SystemExit(main())
