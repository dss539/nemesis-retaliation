#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

repo = Path("/home/smithers/nemesis-retaliation")
worker = repo / "assets/tts-mod/extract/vision-workers/sol-max-worker-02"
source = repo / "assets/tts-mod/extract/v2-dl/tree/bags/secureBag-029.jpg"
contact_path = worker / "contact-sheets/W01-022-glyph-v-glossary.png"
entries = [
    ("SOURCE W01-022 literal glyph", source),
    ("secure", repo / "assets/icons/map/secure.png"),
    ("autodestruction", repo / "assets/icons/map/autodestruction.png"),
    ("malfunction", repo / "assets/icons/map/malfunction.png"),
    ("computer", repo / "assets/icons/map/computer.png"),
    ("robot", repo / "assets/icons/general/robot.png"),
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
    draw.text((col * cell_w + 10, row * (image_h + label_h) + image_h + 8), label, fill="black", font=font)
sheet.save(contact_path)
print(contact_path)
