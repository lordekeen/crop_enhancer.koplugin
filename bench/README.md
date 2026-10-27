# Crop comparison harness

Runs four auto-crop implementations on the same page bitmap:

- `stock` — KOReader's built-in `k2pdfopt_crop_bmp`, called directly from the
  bundled `libk2pdfopt` (same KOPTContext settings KOReader uses: trim=1,
  margin=0.10, 1072x1448 @ 300dpi).
- `upstream` — `crop_enhancer_detect.lua` as of commit 2121319 (inverts the
  binary image before connected components).
- `invertfix` — `crop_enhancer_detect.lua` at 71dd1b1 (invert removed, old
  border filter).
- `patched` — the current working tree.

The reference files are copies from git history:

```sh
git show 2121319:crop_enhancer_detect.lua > bench/upstream_detect.lua
git show 71dd1b1:crop_enhancer_detect.lua > bench/invertfix_detect.lua
```

`prep.py` writes real pages from a directory of images (`SAMPLES_DIR`),
`synthetic.py` writes the synthetic edge cases (frame, edge band, edge text, speckles, footer) into `pages/` and `raw/`.

Usage:

```sh
KDIR=~/Sources/koreader/base/build/x86_64-pc-linux-gnu-debug
cd "$KDIR"   # ffi.loadlib resolves libs/ relative to the cwd
KO_ROOT=~/Sources/koreader PLUGIN_DIR=~/Sources/crop_enhancer.koplugin \
  HARNESS_DIR=~/Sources/crop_enhancer.koplugin/bench \
  luajit ~/Sources/crop_enhancer.koplugin/bench/run.lua PAGE1,PAGE2 > results.txt
python3 bench/compare.py results.txt
```

Pages are raw 8-bit grayscale with a `<II` width/height header; `prep.py`
writes them from image files, together with the PNGs used for the visuals.

The harness needs a KOReader build tree because `ffi.loadlib` looks for
`libs/` relative to the working directory, and stock LuaJIT lacks
KOReader's `ffi.libc` extension (the harness sets it manually).

`newCtx` fills an identity grayscale palette: willus's `bmp_is_grayscale()`
checks it, and a zeroed palette sends the stock cropper down a conversion
path that yields an all-black `srcgrey`.
