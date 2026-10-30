"""Write the curated manga pages used by the crop harness.

SAMPLES_DIR must hold one subdirectory per chapter, extracted from a chapter
archive, plus a manifest that maps each role below to one page of one chapter:

    unzip "$DOWNLOAD_DIR/<chapter>.cbz" -d "$SAMPLES_DIR/<chapter>"

    # $SAMPLES_DIR/manifest.txt
    P01_bleed=<chapter>/01.jpg
    P02_bleed=<chapter>/04.jpg
    ...

The roles cover the cases the component filter has to tell apart: dense
full-bleed art, spreads, square pages, credits pages (dark, edge-touching
text) and plain interior pages across four aspect ratios. The manifest is
deliberately not committed: which chapters to point it at is a local choice.
"""
from PIL import Image
import os
import struct
import sys

SAMPLES = os.environ.get("SAMPLES_DIR")
if not SAMPLES:
    sys.exit("set SAMPLES_DIR to a directory of extracted chapters")

ROLES = [
    "P01_bleed",
    "P02_bleed",
    "P03_edgeband",
    "P04_spread",
    "P05_spread",
    "P06_square",
    "P07_credits",
    "P08_credits",
    "P09_credits",
    "P10_regular",
    "P11_regular",
    "P12_regular",
]

MANIFEST = os.path.join(SAMPLES, "manifest.txt")


def read_manifest(path):
    entries = {}
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError as exc:
        sys.exit(
            f"cannot read {path}: {exc}\n"
            "expected one '<role>=<chapter>/<page image>' per line, roles: "
            + ", ".join(ROLES)
        )
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        role, _, page = line.partition("=")
        if role in ROLES and page:
            entries[role] = page
    missing = [role for role in ROLES if role not in entries]
    if missing:
        sys.exit(f"{path} has no entry for: {', '.join(missing)}")
    return entries


try:
    os.makedirs("pages", exist_ok=True)
    os.makedirs("raw", exist_ok=True)
except OSError as exc:
    sys.exit(f"cannot create output directories: {exc}")

for role, page in read_manifest(MANIFEST).items():
    src = os.path.join(SAMPLES, page)
    if not os.path.isfile(src):
        sys.exit(f"missing page {src}")
    try:
        im = Image.open(src).convert("L")
        im.save(os.path.join("pages", role + ".png"))
        with open(os.path.join("raw", role + ".gray"), "wb") as f:
            f.write(struct.pack("<II", im.width, im.height))
            f.write(im.tobytes())
    except (OSError, ValueError) as exc:
        sys.exit(f"failed to write page {role}: {exc}")
    print(role, im.size)
