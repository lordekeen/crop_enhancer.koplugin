# Crop comparison harness

Runs three auto-crop implementations on the same page bitmap:

- `stock` — KOReader's built-in `k2pdfopt_crop_bmp`, called directly from the
  bundled `libk2pdfopt` (same KOPTContext settings KOReader uses: trim=1,
  margin=0.10, 1072x1448 @ 300dpi).
- `upstream` — `crop_enhancer_detect.lua` as of commit 2121319 (inverts the
  binary image before connected components).
- `patched` — the current working tree.

`upstream_detect.lua` must be a copy of the pre-patch file:

```sh
git show 2121319:crop_enhancer_detect.lua > bench/upstream_detect.lua
```

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
