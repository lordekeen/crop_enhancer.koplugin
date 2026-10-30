"""Generate the synthetic edge-case pages used by the crop harness."""
import os
import struct
import sys

from PIL import Image, ImageDraw

PAGES = "pages"
RAW = "raw"


def save(im, name):
    try:
        os.makedirs(PAGES, exist_ok=True)
        os.makedirs(RAW, exist_ok=True)
        im.save(os.path.join(PAGES, name + ".png"))
        with open(os.path.join(RAW, name + ".gray"), "wb") as f:
            f.write(struct.pack("<II", im.width, im.height))
            f.write(im.tobytes())
    except OSError as exc:
        sys.exit(f"failed to write {name}: {exc}")
    print(name, im.size)


def text_block(d):
    for y in range(300, 900, 24):
        d.rectangle([200, y, 800, y + 12], fill=20)


page = Image.new("L", (1000, 1400), 255)
draw = ImageDraw.Draw(page)
text_block(draw)
for x, y in [(30, 40), (960, 50), (20, 1350), (980, 1370), (500, 20)]:
    draw.rectangle([x, y, x + 3, y + 3], fill=0)
save(page, "SYN")

page = Image.new("L", (1000, 1400), 255)
draw = ImageDraw.Draw(page)
draw.rectangle([0, 0, 999, 1399], outline=0, width=2)
text_block(draw)
save(page, "FRAME")

page = Image.new("L", (1000, 1400), 255)
draw = ImageDraw.Draw(page)
draw.rectangle([0, 0, 999, 14], fill=0)
text_block(draw)
save(page, "EDGEBAND")

page = Image.new("L", (1000, 1400), 255)
draw = ImageDraw.Draw(page)
text_block(draw)
for x in range(80, 700, 20):
    draw.rectangle([x, 0, x + 15, 11], fill=20)
    draw.rectangle([x + 4, 3, x + 11, 8], fill=255)
save(page, "EDGETEXT")

page = Image.new("L", (1000, 1400), 255)
draw = ImageDraw.Draw(page)
text_block(draw)
for x in range(100, 420, 18):
    draw.rectangle([x, 1300, x + 8, 1310], fill=30)
save(page, "FOOTER")

# A paragraph that starts on the top edge and stays one connected component:
# the bars are fused by a vertical stem, so the block is far thicker than
# thin_edge_frac and the frame-fill branch decides. At ~0.27 ink fill it is
# kept at the 0.20 cap and would be dropped without the cap.
page = Image.new("L", (1000, 1400), 255)
draw = ImageDraw.Draw(page)
for y in range(0, 620, 48):
    draw.rectangle([40, y, 960, y + 12], fill=20)
draw.rectangle([498, 0, 501, 588], fill=20)
save(page, "EDGEPARA")
