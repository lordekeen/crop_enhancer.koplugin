"""Generate the synthetic edge-case pages used by the crop harness."""
from PIL import Image, ImageDraw
import os, struct


def save(im, name, pages="pages", raw="raw"):
    os.makedirs(pages, exist_ok=True)
    os.makedirs(raw, exist_ok=True)
    im.save(os.path.join(pages, name + ".png"))
    with open(os.path.join(raw, name + ".gray"), "wb") as f:
        f.write(struct.pack("<II", im.width, im.height))
        f.write(im.tobytes())
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
for x in range(100, 420, 18):
    draw.rectangle([x, 1300, x + 8, 1310], fill=30)
save(page, "FOOTER")
