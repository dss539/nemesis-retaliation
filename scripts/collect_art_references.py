#!/usr/bin/env python3
"""Collect and catalogue public Nemesis: Retaliation visual references.

Downloads are intentionally stored under gitignored art-references/. Metadata is
written to docs/art-reference/. This is a research/reference collector, not a
license grant or a production-asset importer.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "docs/art-reference/source-plan.json"
REQ_PATH = ROOT / "docs/art-reference/asset-requirements.yml"
ART = ROOT / "art-references"
UA = "Mozilla/5.0 (compatible; HermesAgent art-reference research; +https://github.com/dss539/nemesis-retaliation)"
MAX_EDGE = 3000
JPEG_QUALITY = 88


def get(url: str, *, referer: str | None = None, retries: int = 3) -> bytes:
    headers = {"User-Agent": UA, "Accept": "*/*"}
    if referer:
        headers["Referer"] = referer
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read()
        except Exception as exc:
            last = exc
            time.sleep(0.5 * (2 ** attempt))
    raise RuntimeError(f"download failed after {retries} attempts: {url}: {last}")


def slug(value: str, max_len: int = 80) -> str:
    value = html.unescape(value).lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value[:max_len] or "asset"


def html_title(raw: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", raw, re.I | re.S)
    if not m:
        return "Untitled"
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()


def infer_tags(text: str, base_tags: list[str] | None = None) -> list[str]:
    t = text.lower()
    tags = set(base_tags or [])
    keywords = {
        "character": ["character", "crew", "officer", "medic", "medical support", "recon", "engineer", "gunner", "sharpshooter", "uav operator", "bioenhancement"],
        "intruders": ["intruder", "primeblood", "prime blood", "drone", "adult", "queen", "xeno", "alien"],
        "models": ["model", "mini", "miniature", "sundrop", "painted", "sculpt"],
        "cards": ["card", "deck"],
        "items": ["item", "weapon", "armor", "equipment", "ammo"],
        "map": ["map", "board", "playmat", "setup", "room", "corridor", "landing zone"],
        "rooms": ["room", "nest", "landing zone"],
        "corridors": ["corridor"],
        "doors": ["door"],
        "tokens": ["token", "marker", "acrylic"],
        "dashboard": ["dashboard", "character board", "player board"],
        "icons": ["icon", "symbol", "marker"],
        "terrain": ["terrain", "door", "nest", "egg", "terminal", "corpse"],
        "objectives": ["objective", "mission", "task"],
        "concept-art": ["concept", "artwork", "illustration", "vote"],
        "prototype": ["prototype", "beta", "tts", "development"],
        "final-components": ["production", "unboxed", "final", "retail", "components"],
        "paint-reference": ["painted", "sundrop", "slapchop", "dry brush", "osl"],
    }
    for tag, words in keywords.items():
        if any(w in t for w in words):
            tags.add(tag)
    specific_phrases = [
        "officer", "medical support", "medic", "recon", "combat engineer",
        "bioenhancement expert", "heavy gunner", "uav operator", "sharpshooter",
        "primeblood drone", "primeblood adult", "prime blood", "primeblood queen",
        "security robot", "neoflesh", "xyrians", "sangrevores", "insider",
        "landing zone", "life support", "reactor", "anti-aircraft", "autodestruction",
        "action cards", "item cards", "event cards", "exploration cards",
        "objective cards", "contamination", "serious wound", "noise die", "combat dice",
    ]
    for phrase in specific_phrases:
        if phrase in t:
            tags.add(slug(phrase))
    return sorted(tags)


def normalize_image(data: bytes, dest: Path) -> tuple[int, int, int, str]:
    with Image.open(io.BytesIO(data)) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        im.thumbnail((MAX_EDGE, MAX_EDGE), Image.Resampling.LANCZOS)
        if im.mode == "RGBA":
            bg = Image.new("RGB", im.size, "#101418")
            bg.paste(im, mask=im.getchannel("A"))
            im = bg
        else:
            im = im.convert("RGB")
        dest.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        width, height = im.size
    payload = dest.read_bytes()
    return width, height, len(payload), hashlib.sha256(payload).hexdigest()


def add_image(rows: list[dict], seen: dict[str, str], *, data: bytes, dest: Path,
              source_type: str, source_page: str, direct_url: str, title: str,
              creator: str, rights: str, tags: list[str], notes: str = "") -> None:
    try:
        width, height, size, sha = normalize_image(data, dest)
    except Exception as exc:
        rows.append({
            "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": source_type,
            "source_page": source_page, "direct_url": direct_url, "title": title,
            "creator": creator, "rights": rights, "tags": ";".join(sorted(set(tags))),
            "status": "error", "width": "", "height": "", "bytes": "", "sha256": "",
            "duplicate_of": "", "notes": f"{notes}; {type(exc).__name__}: {exc}".strip("; ")
        })
        return
    rel = dest.relative_to(ROOT).as_posix()
    duplicate = seen.get(sha, "")
    if duplicate:
        dest.unlink(missing_ok=True)
        rel = duplicate
        status = "duplicate"
    else:
        seen[sha] = rel
        status = "downloaded"
    rows.append({
        "id": f"ref-{len(rows)+1:04d}", "file": rel, "source_type": source_type,
        "source_page": source_page, "direct_url": direct_url, "title": title,
        "creator": creator, "rights": rights, "tags": ";".join(sorted(set(tags))),
        "status": status, "width": width, "height": height, "bytes": size,
        "sha256": sha, "duplicate_of": duplicate, "notes": notes
    })


def collect_manuals(plan: dict, rows: list[dict], seen: dict[str, str]) -> None:
    try:
        import fitz  # type: ignore[import-not-found]  # PyMuPDF is supplied temporarily.
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required to render manual pages (pip install pymupdf)") from exc
    for item in plan["manuals"]:
        pdf = ROOT / "docs/rulebooks" / item["file"]
        if not pdf.exists():
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "official-manual",
                "source_page": plan["official_download_page"], "direct_url": "", "title": item["file"],
                "creator": "Awaken Realms", "rights": "Copyright Awaken Realms; reference only; no reuse license identified",
                "tags": ";".join(item["tags"]), "status": "missing", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": "Local source PDF not found"
            })
            continue
        doc = fitz.open(pdf)
        group = slug(pdf.stem)
        for index, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(1.55, 1.55), alpha=False)
            data = pix.tobytes("png")
            title = f"{pdf.stem} — page {index + 1}"
            page_text = page.get_text("text")
            tags = infer_tags(title + " " + page_text + " " + " ".join(item["tags"]),
                              item["tags"] + ["official", "manual-page"])
            dest = ART / "official-manual" / group / f"page-{index+1:03d}.jpg"
            add_image(rows, seen, data=data, dest=dest, source_type="official-manual",
                      source_page=plan["official_download_page"], direct_url="",
                      title=title, creator="Awaken Realms",
                      rights="Copyright Awaken Realms; reference only; no reuse license identified",
                      tags=tags, notes=f"Rendered from local {pdf.relative_to(ROOT)}")
        doc.close()


def extract_image_urls(raw: str, allowed_domains: tuple[str, ...]) -> list[str]:
    raw = raw.replace("\\/", "/").replace("\\u0026", "&")
    candidates = re.findall(r"https?://[^\"'<>\\\s]+", raw)
    out = []
    for candidate in candidates:
        candidate = html.unescape(candidate).rstrip(",);]")
        host = urllib.parse.urlparse(candidate).netloc.lower()
        path = urllib.parse.urlparse(candidate).path.lower()
        if any(host.endswith(d) for d in allowed_domains) and re.search(r"\.(?:png|jpe?g|webp|gif|avif)$", path):
            out.append(candidate)
    return list(dict.fromkeys(out))


def collect_gamefound(plan: dict, rows: list[dict], seen: dict[str, str]) -> None:
    for item in plan["gamefound_updates"]:
        update_id = item["id"]
        page_url = f"https://gamefound.com/en/projects/awaken-realms/nemesis-retaliation/updates/{update_id}"
        try:
            raw = get(page_url).decode("utf-8", "ignore")
            title = html_title(raw).replace("Nemesis: Retaliation by Awaken Realms - ", "").replace(" - Gamefound", "")
            urls = [u for u in extract_image_urls(raw, ("imgcdn.gamefound.com",))
                    if "/richtextimage/" in u or "/projectupdate/" in u]
            for seq, url in enumerate(urls, 1):
                data = get(url, referer=page_url)
                ext_title = f"Update {update_id}: {title} — image {seq}"
                tags = infer_tags(ext_title, item["tags"] + ["official", "gamefound"])
                dest = ART / "official-gamefound" / f"update-{update_id:02d}" / f"{seq:03d}-{slug(title,45)}.jpg"
                add_image(rows, seen, data=data, dest=dest, source_type="official-gamefound",
                          source_page=page_url, direct_url=url, title=ext_title,
                          creator="Awaken Realms",
                          rights="Copyright Awaken Realms; reference only; no reuse license identified",
                          tags=tags)
        except Exception as exc:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "official-gamefound",
                "source_page": page_url, "direct_url": "", "title": f"Update {update_id}",
                "creator": "Awaken Realms", "rights": "Copyright Awaken Realms; reference only",
                "tags": ";".join(item["tags"]), "status": "error", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": f"{type(exc).__name__}: {exc}"
            })


def collect_publisher(plan: dict, rows: list[dict], seen: dict[str, str]) -> None:
    explicit_urls = {item["url"] for item in plan.get("publisher_assets", [])}
    for seq, item in enumerate(plan.get("publisher_assets", []), 1):
        page_url = plan["publisher_pages"][0]
        url = item["url"]
        try:
            data = get(url, referer=page_url)
            dest = ART / "official-publisher" / f"{seq:03d}-{slug(item['title'],50)}.jpg"
            add_image(rows, seen, data=data, dest=dest, source_type="official-publisher",
                      source_page=page_url, direct_url=url, title=item["title"],
                      creator="Awaken Realms",
                      rights="Copyright Awaken Realms; reference only; no reuse license identified",
                      tags=infer_tags(item["title"], item["tags"]))
        except Exception as exc:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "official-publisher",
                "source_page": page_url, "direct_url": url, "title": item["title"],
                "creator": "Awaken Realms", "rights": "Copyright Awaken Realms; reference only",
                "tags": ";".join(item["tags"]), "status": "error", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": f"{type(exc).__name__}: {exc}"
            })
    for page_url in plan["publisher_pages"]:
        try:
            raw = get(page_url).decode("utf-8", "ignore")
            title = html_title(raw)
            urls = extract_image_urls(raw, ("awakenrealms.com", "amazonaws.com", "cloudfront.net"))
            # Avoid tracking pixels and unrelated page chrome where filenames make that clear.
            urls = [u for u in urls if u not in explicit_urls and not any(
                x in u.lower() for x in ("logo", "icon", "avatar", "flag", "payment"))]
            for seq, url in enumerate(urls, 1):
                data = get(url, referer=page_url)
                item_title = f"Publisher gallery: {title} — image {seq}"
                dest = ART / "official-publisher" / f"{seq:03d}-{slug(Path(urllib.parse.urlparse(url).path).stem,50)}.jpg"
                add_image(rows, seen, data=data, dest=dest, source_type="official-publisher",
                          source_page=page_url, direct_url=url, title=item_title,
                          creator="Awaken Realms",
                          rights="Copyright Awaken Realms; reference only; no reuse license identified",
                          tags=infer_tags(item_title, ["official", "publisher", "key-art"]))
        except Exception as exc:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "official-publisher",
                "source_page": page_url, "direct_url": "", "title": "Publisher page",
                "creator": "Awaken Realms", "rights": "Copyright Awaken Realms; reference only",
                "tags": "official;publisher", "status": "error", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": f"{type(exc).__name__}: {exc}"
            })


def bgg_catalog() -> dict[str, dict]:
    catalog = {}
    endpoint = ("https://api.geekdo.com/api/images?ajax=1&gallery=all&nosession=1"
                "&objectid=381248&objecttype=thing&showcount=50&pageid={page}&sort={sort}")
    for sort_order in ("hot", "recent"):
        for page in range(1, 12):
            try:
                payload = json.loads(get(endpoint.format(page=page, sort=sort_order)).decode("utf-8"))
                for image in payload.get("images", []):
                    catalog[str(image["imageid"])] = image
            except Exception:
                pass
    return catalog


def collect_bgg(plan: dict, rows: list[dict], seen: dict[str, str]) -> None:
    catalog = bgg_catalog()
    for image_id in plan["bgg_image_ids"]:
        image = catalog.get(str(image_id))
        page_url = f"https://boardgamegeek.com/image/{image_id}/nemesis-retaliation"
        if not image:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "community-bgg",
                "source_page": page_url, "direct_url": "", "title": f"BGG image {image_id}",
                "creator": "Unknown", "rights": "Assume all rights reserved; reference only",
                "tags": "community;bgg", "status": "missing", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": "Selected image absent from current API catalog"
            })
            continue
        caption = image.get("caption") or f"BGG image {image_id}"
        creator = (image.get("user") or {}).get("username") or "Unknown BGG user"
        direct = str(image.get("imageurl_lg") or image.get("imageurl") or "")
        if not direct:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "community-bgg",
                "source_page": page_url, "direct_url": "", "title": caption,
                "creator": creator, "rights": "Assume all rights reserved; reference only",
                "tags": "community;bgg", "status": "missing", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": "BGG API returned no image URL"
            })
            continue
        try:
            data = get(direct, referer=page_url)
            dest = ART / "community-bgg" / f"{image_id}-{slug(caption,60)}.jpg"
            add_image(rows, seen, data=data, dest=dest, source_type="community-bgg",
                      source_page=page_url, direct_url=direct, title=caption,
                      creator=creator, rights="Assume all rights reserved; reference only; verify on image page",
                      tags=infer_tags(caption, ["community", "bgg", "photo", "final-state-reference"]),
                      notes=f"BGG recommendations at collection: {image.get('numrecommend', 0)}")
        except Exception as exc:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "community-bgg",
                "source_page": page_url, "direct_url": direct or "", "title": caption,
                "creator": creator, "rights": "Assume all rights reserved; reference only",
                "tags": "community;bgg", "status": "error", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": f"{type(exc).__name__}: {exc}"
            })


def collect_forums(plan: dict, rows: list[dict], seen: dict[str, str]) -> None:
    for item in plan["forum_pages"]:
        page_url = item["url"]
        try:
            # Public old.reddit HTML is easier to catalogue than app-shell markup.
            parsed = urllib.parse.urlparse(page_url)
            old_url: str = str(urllib.parse.urlunparse(parsed._replace(netloc="old.reddit.com")))
            raw = get(old_url).decode("utf-8", "ignore")
            title = html_title(raw)
            urls = extract_image_urls(raw, ("redd.it", "redditmedia.com", "reddit.com"))
            # Prefer originals; suppress thumbnails and avatars.
            urls = [u for u in urls if urllib.parse.urlparse(u).netloc.lower() in
                    ("i.redd.it", "preview.redd.it") and "avatar" not in u]
            successes = 0
            for seq, url in enumerate(urls[:12], 1):
                try:
                    data = get(url, referer=page_url)
                    dest = ART / "community-forums" / f"{slug(title,45)}-{seq:02d}.jpg"
                    before = len(rows)
                    add_image(rows, seen, data=data, dest=dest, source_type="community-forum",
                              source_page=page_url, direct_url=url, title=f"{title} — image {seq}",
                              creator="Reddit contributor (see source page)",
                              rights="Assume all rights reserved; reference only; attribution/permission required",
                              tags=infer_tags(title, item["tags"]), notes="Public forum image; creator identity remains on source page")
                    if len(rows) > before and rows[-1]["status"] in ("downloaded", "duplicate"):
                        successes += 1
                except Exception:
                    continue
            if not successes:
                rows.append({
                    "id": f"ref-{len(rows)+1:04d}", "file": "", "source_type": "community-forum",
                    "source_page": page_url, "direct_url": "", "title": title,
                    "creator": "Reddit contributor (see source page)",
                    "rights": "Assume all rights reserved; reference only",
                    "tags": ";".join(item["tags"]), "status": "linked-only", "width": "", "height": "",
                    "bytes": "", "sha256": "", "duplicate_of": "", "notes": "No direct public image URL exposed to collector"
                })
        except Exception as exc:
            rows.append({
                "id": f"error-{len(rows)+1:04d}", "file": "", "source_type": "community-forum",
                "source_page": page_url, "direct_url": "", "title": "Forum reference",
                "creator": "Unknown", "rights": "Assume all rights reserved; reference only",
                "tags": ";".join(item["tags"]), "status": "error", "width": "", "height": "",
                "bytes": "", "sha256": "", "duplicate_of": "", "notes": f"{type(exc).__name__}: {exc}"
            })


def make_contact_sheets(rows: list[dict]) -> list[str]:
    sheets = []
    groups = defaultdict(list)
    for row in rows:
        if row["status"] != "downloaded" or not row["file"]:
            continue
        groups[row["source_type"]].append(row)
    font = ImageFont.load_default()
    tile_w, tile_h, columns, page_size = 260, 220, 4, 40
    for group, items in groups.items():
        for page_no, start in enumerate(range(0, len(items), page_size), 1):
            chunk = items[start:start + page_size]
            rows_n = (len(chunk) + columns - 1) // columns
            sheet = Image.new("RGB", (columns * tile_w, rows_n * tile_h), "#15191e")
            draw = ImageDraw.Draw(sheet)
            for index, row in enumerate(chunk):
                x = (index % columns) * tile_w
                y = (index // columns) * tile_h
                try:
                    with Image.open(ROOT / row["file"]) as im:
                        im = ImageOps.exif_transpose(im).convert("RGB")
                        im.thumbnail((tile_w - 16, 166), Image.Resampling.LANCZOS)
                        px = x + (tile_w - im.width) // 2
                        py = y + 6 + (166 - im.height) // 2
                        sheet.paste(im, (px, py))
                except Exception:
                    pass
                label = f"{row['id']} {row['title']}"
                lines = [label[i:i+40] for i in range(0, min(len(label), 120), 40)][:3]
                draw.multiline_text((x + 8, y + 176), "\n".join(lines), fill="#e3e7eb", font=font, spacing=1)
                draw.rectangle((x, y, x + tile_w - 1, y + tile_h - 1), outline="#39434d")
            out = ART / "contact-sheets" / f"{group}-{page_no:02d}.jpg"
            out.parent.mkdir(parents=True, exist_ok=True)
            sheet.save(out, "JPEG", quality=88, optimize=True)
            sheets.append(out.relative_to(ROOT).as_posix())
    return sheets


def write_catalog(rows: list[dict], sheets: list[str]) -> None:
    fields = ["id", "file", "source_type", "source_page", "direct_url", "title", "creator", "rights",
              "tags", "status", "width", "height", "bytes", "sha256", "duplicate_of", "notes"]
    local_csv = ART / "catalogue.csv"
    public_csv = ROOT / "docs/art-reference/source-catalogue.csv"
    for path in (local_csv, public_csv):
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "policy": "Reference only. A public URL is not a reuse license.",
        "rows": rows,
        "contact_sheets": sheets,
    }
    (ART / "catalogue.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def read_requirements() -> list[tuple[str, str, str]]:
    text = REQ_PATH.read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("- {id:"):
            mid = re.search(r"id:\s*([^,}]+)", line)
            cat = re.search(r"category:\s*([^,}]+)", line)
            name = re.search(r"name:\s*([^,}]+)", line)
            if mid and cat and name:
                out.append((mid.group(1).strip(), cat.group(1).strip(), name.group(1).strip()))
    return out


def coverage_status(req_id: str, category: str, name: str, rows: list[dict]) -> tuple[str, int, str]:
    stop = {"char", "intruder", "room", "tiles", "tile", "card", "token", "icon", "dashboard",
            "player", "game", "section", "markers", "marker", "symbols", "symbol", "components",
            "component", "area", "information", "states", "state", "variants", "and", "with"}
    tokens = {x for x in re.split(r"[^a-z0-9]+", f"{req_id} {name}".lower())
              if len(x) > 2 and x not in stop}
    aliases = {
        "character": {"character", "crew", "models", "dashboard"},
        "entity": {"intruders", "models", "entities"},
        "map": {"map", "rooms", "corridors", "playmat"},
        "board-ui": {"map", "board-ui", "components", "rules"},
        "card": {"cards", "rulebook"},
        "dashboard": {"dashboard", "cards", "components"},
        "icon": {"icons", "tokens", "rules"},
        "token": {"tokens", "components"},
        "dice": {"dice", "components", "rules"},
        "ui": {"board-ui", "components", "rules"},
        "fx": {"official-art", "illustration", "gameplay"},
        "presentation": {"key-art", "official-art", "publisher"},
    }
    category_terms = aliases.get(category, set())
    exact_matches = []
    category_matches = []
    for row in rows:
        hay = f"{row['title']} {row['tags']}".lower()
        if row["status"] not in ("downloaded", "duplicate"):
            continue
        if any(term in hay for term in category_terms):
            category_matches.append(row)
        if tokens and any(token in hay for token in tokens):
            exact_matches.append(row)
    if len(exact_matches) >= 3:
        return "covered-reference", len(exact_matches), "Multiple specifically tagged references; variants still need review"
    if exact_matches:
        return "partial-reference", len(exact_matches), "Specific reference found, but coverage is thin"
    if category_matches:
        return "partial-reference", len(category_matches), "Only category-level references found; exact variants need review"
    return "missing-reference", 0, "No confidently tagged reference collected"


def write_reports(rows: list[dict], sheets: list[str]) -> None:
    counts = Counter(row["status"] for row in rows)
    by_source = Counter(row["source_type"] for row in rows if row["status"] == "downloaded")
    reqs = read_requirements()
    coverage = []
    for req_id, category, name in reqs:
        status, count, note = coverage_status(req_id, category, name, rows)
        coverage.append((req_id, category, name, status, count, note))
    cov_counts = Counter(x[3] for x in coverage)
    lines = [
        "# Art-reference coverage report", "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}", "",
        "This measures collected reference coverage, not finished/licensed production-asset coverage.", "",
        "## Collection summary", "",
        f"- Catalogue rows: {len(rows)}",
        f"- Downloaded unique files: {counts['downloaded']}",
        f"- Deduplicated references: {counts['duplicate']}",
        f"- Linked-only references: {counts['linked-only']}",
        f"- Missing/error rows: {counts['missing'] + counts['error']}",
        f"- Contact sheets: {len(sheets)}", "",
    ]
    for source, count in sorted(by_source.items()):
        lines.append(f"- {source}: {count} unique files")
    lines += ["", "## Requirement coverage", "",
              f"- Covered reference: {cov_counts['covered-reference']}",
              f"- Partial reference: {cov_counts['partial-reference']}",
              f"- Missing reference: {cov_counts['missing-reference']}", "",
              "| Requirement | Category | Status | References | Note |",
              "|---|---|---:|---:|---|"]
    for req_id, category, name, status, count, note in coverage:
        lines.append(f"| {req_id}: {name} | {category} | {status} | {count} | {note} |")
    lines += ["", "## Rights gate", "",
              "Every collected image defaults to reference-only unless a specific license is documented.",
              "Do not ship these files in the game or use recognizably copied characters/compositions without permission.",
              "Production art should be newly authored from high-level visual traits and mechanics, then reviewed for substantial similarity."]
    (ROOT / "docs/art-reference/coverage-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-manuals", action="store_true")
    parser.add_argument("--skip-gamefound", action="store_true")
    parser.add_argument("--skip-publisher", action="store_true")
    parser.add_argument("--skip-bgg", action="store_true")
    parser.add_argument("--skip-forums", action="store_true")
    parser.add_argument("--reports-only", action="store_true",
                        help="Rebuild reports from the existing local catalogue without network access")
    args = parser.parse_args()
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    ART.mkdir(parents=True, exist_ok=True)
    if args.reports_only:
        with (ART / "catalogue.csv").open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        payload = json.loads((ART / "catalogue.json").read_text(encoding="utf-8"))
        sheets = payload.get("contact_sheets", [])
        write_reports(rows, sheets)
        print(json.dumps({"rows": len(rows), "contact_sheets": len(sheets), "mode": "reports-only"}))
        return 0
    rows: list[dict] = []
    seen: dict[str, str] = {}
    if not args.skip_manuals:
        print("Collecting manual page references...", flush=True)
        collect_manuals(plan, rows, seen)
    if not args.skip_gamefound:
        print("Collecting official Gamefound references...", flush=True)
        collect_gamefound(plan, rows, seen)
    if not args.skip_publisher:
        print("Collecting publisher gallery references...", flush=True)
        collect_publisher(plan, rows, seen)
    if not args.skip_bgg:
        print("Collecting selected BGG community references...", flush=True)
        collect_bgg(plan, rows, seen)
    if not args.skip_forums:
        print("Collecting forum references...", flush=True)
        collect_forums(plan, rows, seen)
    print("Generating contact sheets and reports...", flush=True)
    sheets = make_contact_sheets(rows)
    write_catalog(rows, sheets)
    write_reports(rows, sheets)
    counts = Counter(row["status"] for row in rows)
    print(json.dumps({"rows": len(rows), "statuses": counts, "contact_sheets": len(sheets)}, default=dict))
    return 0 if counts["downloaded"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
