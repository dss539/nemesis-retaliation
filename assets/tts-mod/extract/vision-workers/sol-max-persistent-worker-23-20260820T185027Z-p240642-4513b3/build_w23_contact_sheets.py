#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO = Path('/home/smithers/projects/nemesis-card-corpus/repos/nemesis-retaliation').resolve()
ROOT = REPO / 'assets/tts-mod/extract/vision-workers/sol-max-persistent-worker-23-20260820T185027Z-p240642-4513b3'
OUT = ROOT / 'qa/contact-sheets'
PAGE = ROOT / 'qa/official-objectives-render/page-1.png'
OBJECTIVES_PDF = REPO / 'docs/rulebooks/Nemesis_RT_Objectives_Sheet.pdf'
FONT_PATH = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
BOLD_PATH = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
OFFICIAL_PAGE_SIZE_POINTS = (824.882, 824.882)
OFFICIAL = {
    'the-supply-route': {
        'cardPoints': [535, 342, 680, 458],
        'playerPoints': [556, 343, 597, 376],
        'title': 'THE SUPPLY ROUTE',
    },
    'essential-data': {
        'cardPoints': [392, 342, 537, 458],
        'playerPoints': [413, 343, 454, 376],
        'title': 'ESSENTIAL DATA',
    },
    'primary-samples': {
        'cardPoints': [678, 365, 824, 458],
        'playerPoints': [696, 365, 738, 398],
        'title': 'PRIMARY SAMPLES',
    },
    'perimeter-clearing': {
        'cardPoints': [392, 614, 537, 722],
        'playerPoints': [413, 615, 454, 648],
        'title': 'PERIMETER CLEARING',
    },
}
ASSET_OFFICIAL = {
    'W23-001': 'the-supply-route',
    'W23-002': 'essential-data',
    'W23-003': 'primary-samples',
    'W23-004': 'primary-samples',
    'W23-005': 'perimeter-clearing',
    'W23-006': 'the-supply-route',
    'W23-007': None,
    'W23-008': 'essential-data',
}
MATERIAL_GLOSSARY = {
    'W23-001': {0: ['general/character.png']},
    'W23-002': {0: ['general/character.png'], 1: ['general/character.png'], 2: ['map/lander.png']},
    'W23-003': {0: ['general/character.png']},
    'W23-004': {0: ['general/character.png']},
    'W23-005': {0: ['general/character.png']},
    'W23-006': {0: ['general/character.png']},
    'W23-007': {1: ['general/character.png']},
    'W23-008': {0: ['general/character.png']},
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font(size: int, bold: bool = False) -> Any:
    path = BOLD_PATH if bold else FONT_PATH
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def fit(img: Image.Image, max_w: int, max_h: int, *, upscale: bool = True) -> Image.Image:
    out = img.convert('RGB')
    ratio = min(max_w / out.width, max_h / out.height)
    if not upscale:
        ratio = min(1.0, ratio)
    return out.resize((max(1, round(out.width * ratio)), max(1, round(out.height * ratio))), Image.Resampling.LANCZOS)


def padded_crop(img: Image.Image, bbox: list[int], frac: float = 0.18, minimum: int = 16) -> tuple[Image.Image, list[int]]:
    x1, y1, x2, y2 = bbox
    px = max(minimum, round((x2 - x1) * frac))
    py = max(minimum, round((y2 - y1) * frac))
    box = [max(0, x1 - px), max(0, y1 - py), min(img.width, x2 + px), min(img.height, y2 + py)]
    return img.crop((box[0], box[1], box[2], box[3])), box


def point_crop(page: Image.Image, points: list[float]) -> tuple[Image.Image, list[int]]:
    sx = page.width / OFFICIAL_PAGE_SIZE_POINTS[0]
    sy = page.height / OFFICIAL_PAGE_SIZE_POINTS[1]
    pixels = [round(points[0] * sx), round(points[1] * sy), round(points[2] * sx), round(points[3] * sy)]
    return page.crop((pixels[0], pixels[1], pixels[2], pixels[3])), pixels


def panel(title: str, img: Image.Image, width: int, height: int, subtitle: str = '') -> Image.Image:
    canvas = Image.new('RGB', (width, height), '#171a20')
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width - 1, height - 1), outline='#6f7785', width=3)
    draw.text((18, 14), title, font=font(28, True), fill='white')
    if subtitle:
        draw.text((18, 52), subtitle, font=font(18), fill='#c8ced8')
        top = 82
    else:
        top = 58
    fitted = fit(img, width - 36, height - top - 18)
    x = (width - fitted.width) // 2
    y = top + (height - top - fitted.height) // 2
    canvas.paste(fitted, (x, y))
    return canvas


def glossary_sheet() -> tuple[Image.Image, list[dict[str, Any]]]:
    paths = sorted((REPO / 'assets/icons').rglob('*.png'))
    cols, cell_w, cell_h = 7, 230, 190
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cell_w, rows * cell_h + 72), '#11151b')
    draw = ImageDraw.Draw(sheet)
    draw.text((20, 16), 'AUTHORITATIVE 49-ICON RULEBOOK p.40 GLOSSARY', font=font(28, True), fill='white')
    records = []
    for i, path in enumerate(paths):
        col, row = i % cols, i // cols
        x, y = col * cell_w, 72 + row * cell_h
        draw.rectangle((x + 4, y + 4, x + cell_w - 4, y + cell_h - 4), outline='#485160', width=2)
        with Image.open(path) as im:
            icon = fit(ImageOps.contain(im.convert('RGBA'), (115, 105)), 115, 105)
        bg = Image.new('RGB', (125, 115), '#313843')
        rgba = im.convert('RGBA') if False else None
        # Reopen to preserve alpha during compositing.
        with Image.open(path) as raw:
            raw_rgba = ImageOps.contain(raw.convert('RGBA'), (115, 105), Image.Resampling.LANCZOS)
        bx, by = x + (cell_w - bg.width) // 2, y + 10
        sheet.paste(bg, (bx, by))
        sheet.paste(raw_rgba, (bx + (bg.width - raw_rgba.width) // 2, by + (bg.height - raw_rgba.height) // 2), raw_rgba)
        label = str(path.relative_to(REPO / 'assets/icons')).replace('.png', '')
        draw.multiline_text((x + 10, y + 132), label.replace('/', '/\n'), font=font(16), fill='white', spacing=2)
        records.append({'label': label, 'path': str(path.relative_to(REPO)), 'sha256': sha(path)})
    return sheet, records


def main() -> None:
    if OUT.exists() and any(OUT.iterdir()):
        raise RuntimeError(f'contact output not empty: {OUT}')
    OUT.mkdir(parents=True, exist_ok=True)
    assignment = json.loads((ROOT / 'assignment.json').read_text())
    by_id = {x['assetId']: x for x in assignment['assets']}
    with Image.open(PAGE) as p:
        page = p.convert('RGB')
    official_records: dict[str, Any] = {}
    for key, spec in OFFICIAL.items():
        card, card_box = point_crop(page, spec['cardPoints'])
        player, player_box = point_crop(page, spec['playerPoints'])
        card_path = OUT / f'official-{key}-card.png'
        player_path = OUT / f'official-{key}-player-symbol.png'
        card.save(card_path)
        player.save(player_path)
        official_records[key] = {
            'title': spec['title'],
            'cardPath': str(card_path.relative_to(REPO)),
            'cardPixelBox': card_box,
            'cardSha256': sha(card_path),
            'playerSymbolPath': str(player_path.relative_to(REPO)),
            'playerSymbolPixelBox': player_box,
            'playerSymbolSha256': sha(player_path),
        }
    all_glossary, glossary_records = glossary_sheet()
    glossary_path = OUT / 'authoritative-all-49-glossary.png'
    all_glossary.save(glossary_path)
    assets_out = []
    for asset_id in sorted(by_id):
        asset = by_id[asset_id]
        wrapper_path = (ROOT / 'adjudication/bbox-raw-retry-01' / f'{asset_id}.json') if asset_id == 'W23-001' else (ROOT / 'adjudication/bbox-raw-retry-02' / f'{asset_id}.json')
        wrapper = json.loads(wrapper_path.read_text())
        payload = wrapper['payload']
        blind = json.loads((ROOT / 'isolated-raw-output' / f'{asset_id}.json').read_text())
        source_path = REPO / asset['sourcePath']
        with Image.open(source_path) as raw_source:
            source = raw_source.convert('RGB')
        occurrence_records = []
        occurrence_panels = []
        for occurrence in payload['occurrences']:
            idx = occurrence['sourceIconMorphologyIndex']
            bbox = occurrence['bbox']
            if bbox is None:
                continue
            crop, padded = padded_crop(source, bbox)
            crop_path = OUT / f'{asset_id}-occurrence-{idx}.png'
            crop.save(crop_path)
            occurrence_records.append({
                'sourceIconMorphologyIndex': idx,
                'category': occurrence['category'],
                'modelBbox': bbox,
                'paddedCropBox': padded,
                'cropPath': str(crop_path.relative_to(REPO)),
                'cropSha256': sha(crop_path),
                'blindMorphology': blind['iconMorphology'][idx],
            })
            occurrence_panels.append(panel(
                f'SOURCE {asset_id} morphology #{idx}', crop, 520, 430,
                f"bbox={bbox} | {occurrence['category']}",
            ))
        source_full = panel(f'SOURCE {asset_id}', source, 700, 980, Path(asset['sourcePath']).name)
        official_key = ASSET_OFFICIAL[asset_id]
        if official_key:
            official_card_path = REPO / official_records[official_key]['cardPath']
            with Image.open(official_card_path) as im:
                official_panel = panel('CURRENT OFFICIAL OBJECTIVES HELP SHEET', im.convert('RGB'), 1000, 650, OFFICIAL[official_key]['title'])
            player_path = REPO / official_records[official_key]['playerSymbolPath']
            with Image.open(player_path) as im:
                official_player_panel = panel('OFFICIAL NUMBER-OF-CHARACTERS SYMBOL', im.convert('RGB'), 520, 430, OFFICIAL[official_key]['title'])
        else:
            blank = Image.new('RGB', (850, 400), '#22262d')
            d = ImageDraw.Draw(blank)
            d.multiline_text((40, 80), 'NO CURRENT OFFICIAL MISSION TASK\nCOUNTERPART TITLED “SABOTAGE”\nFOUND ON THE 2-PAGE OBJECTIVES HELP SHEET', font=font(28, True), fill='white', spacing=14)
            official_panel = panel('CURRENT OFFICIAL OBJECTIVES HELP SHEET', blank, 1000, 650, 'No title counterpart')
            official_player_panel = panel('OFFICIAL NUMBER-OF-CHARACTERS REFERENCE', page.crop((1700, 1420, 1900, 1590)), 520, 430, 'Essential Data 2+ example')
        relevant = []
        for idx, paths in MATERIAL_GLOSSARY.get(asset_id, {}).items():
            for rel in paths:
                icon_path = REPO / 'assets/icons' / rel
                with Image.open(icon_path) as im:
                    relevant.append(panel(f'GLOSSARY {rel.removesuffix(".png")}', im.convert('RGBA'), 360, 360, f'candidate for morphology #{idx}'))
        while len(relevant) < 3:
            relevant.append(Image.new('RGB', (360, 360), '#11151b'))
        width, height = 2200, 2860
        sheet = Image.new('RGB', (width, height), '#0d1015')
        draw = ImageDraw.Draw(sheet)
        draw.text((35, 24), f'{asset_id} — CARD ↔ AUTHORITATIVE SOURCE CONTACT SHEET', font=font(38, True), fill='white')
        draw.text((35, 76), f"SOURCE SHA-256 {asset['sourceSha256']}", font=font(20), fill='#bfc7d3')
        sheet.paste(source_full, (35, 120))
        sheet.paste(official_panel, (765, 120))
        sheet.paste(official_player_panel, (1670, 120))
        x, y = 35, 1130
        for op in occurrence_panels:
            sheet.paste(op, (x, y))
            x += 540
            if x + 520 > width:
                x = 35
                y += 450
        gy = max(2050, y + 470)
        draw.text((35, gy - 48), 'AUTHORITATIVE p.40 GLOSSARY CANDIDATES', font=font(30, True), fill='white')
        for i, gp in enumerate(relevant[:3]):
            sheet.paste(gp, (35 + i * 380, gy))
        if asset_id == 'W23-007':
            small_glossary = fit(all_glossary, 980, 760)
            sheet.paste(small_glossary, (1190, gy))
        else:
            note = Image.new('RGB', (980, 560), '#171a20')
            nd = ImageDraw.Draw(note)
            nd.rectangle((0, 0, 979, 559), outline='#6f7785', width=3)
            nd.multiline_text((35, 35),
                'ADJUDICATION RULES\n\n• Compare visible morphology, not filename semantics.\n• Require a pixel discriminator against the closest alternative.\n• A matched title does not override source-text conflicts.\n• False promotion is worse than a no-match or deferral.\n• Decorative/artwork occurrences remain non-semantic.',
                font=font(25), fill='white', spacing=10)
            sheet.paste(note, (1190, gy))
        sheet_path = OUT / f'{asset_id}-contact-sheet.png'
        sheet.save(sheet_path)
        assets_out.append({
            'assetId': asset_id,
            'sourcePath': asset['sourcePath'],
            'sourceSha256': asset['sourceSha256'],
            'bboxWrapperPath': str(wrapper_path.relative_to(REPO)),
            'bboxWrapperSha256': sha(wrapper_path),
            'officialCounterpart': official_key,
            'contactSheetPath': str(sheet_path.relative_to(REPO)),
            'contactSheetSha256': sha(sheet_path),
            'contactSheetDimensions': [sheet.width, sheet.height],
            'occurrences': occurrence_records,
            'relevantGlossaryPaths': MATERIAL_GLOSSARY.get(asset_id, {}),
        })
    index = {
        'schemaVersion': 1,
        'generatedAt': now(),
        'sourceObjectivesPdf': str(OBJECTIVES_PDF.relative_to(REPO)),
        'sourceObjectivesPdfSha256': sha(OBJECTIVES_PDF),
        'sourceObjectivesPdfBytes': OBJECTIVES_PDF.stat().st_size,
        'renderPath': str(PAGE.relative_to(REPO)),
        'renderSha256': sha(PAGE),
        'renderDimensions': list(page.size),
        'renderDpi': 300,
        'officialCrops': official_records,
        'glossary': {
            'count': len(glossary_records),
            'allContactSheetPath': str(glossary_path.relative_to(REPO)),
            'allContactSheetSha256': sha(glossary_path),
            'entries': glossary_records,
        },
        'assets': assets_out,
    }
    index_path = OUT / 'index.json'
    index_path.write_bytes((json.dumps(index, indent=2, ensure_ascii=False) + '\n').encode())
    print(json.dumps({'status': 'built', 'assetSheets': len(assets_out), 'glossaryCount': len(glossary_records), 'indexSha256': sha(index_path)}))


if __name__ == '__main__':
    main()
