#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

repo = Path("/home/smithers/nemesis-retaliation")
worker = repo / "assets/tts-mod/extract/vision-workers/sol-max-worker-02"
source = repo / "assets/tts-mod/extract/v2-dl/tree/bags/roomICBag-039.jpg"
crop_path = worker / "crops/W01-020-small-glyph.png"
contact_path = worker / "contact-sheets/W01-020-small-glyph-v-glossary.png"
with Image.open(source) as image:
    crop = image.crop((1320, 730, 1640, 1050)).convert("RGB")
    crop.save(crop_path)
entries = [
    ("SOURCE W01-020 literal glyph", crop_path),
    ("autodestruction", repo / "assets/icons/map/autodestruction.png"),
    ("lander", repo / "assets/icons/map/lander.png"),
    ("intruder", repo / "assets/icons/general/intruder.png"),
    ("robot", repo / "assets/icons/general/robot.png"),
    ("computer", repo / "assets/icons/map/computer.png"),
]
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
label_h, cell_w, image_h = 48, 360, 320
sheet = Image.new("RGB", (cell_w * 3, (image_h + label_h) * 2), "white")
draw = ImageDraw.Draw(sheet)
for index, (label, path) in enumerate(entries):
    row, col = divmod(index, 3)
    with Image.open(path) as image:
        image = image.convert("RGBA")
        bg = Image.new("RGBA", image.size, "#202020")
        bg.alpha_composite(image)
        fitted = ImageOps.contain(bg.convert("RGB"), (cell_w - 30, image_h - 30))
    x = col * cell_w + (cell_w - fitted.width) // 2
    y = row * (image_h + label_h) + (image_h - fitted.height) // 2
    sheet.paste(fitted, (x, y))
    tx = col * cell_w + 10
    ty = row * (image_h + label_h) + image_h + 8
    draw.text((tx, ty), label, fill="black", font=font)
sheet.save(contact_path)
print(crop_path)
print(contact_path)
