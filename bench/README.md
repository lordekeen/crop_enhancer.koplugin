# Crop comparison harness

Runs four auto-crop implementations on the same page bitmap:

- `stock` — KOReader's built-in `k2pdfopt_crop_bmp`, called directly from the
  bundled `libk2pdfopt` (same KOPTContext settings KOReader uses: trim=1,
  margin=0.10, 1072x1448 @ 300dpi).
- `upstream` — `crop_enhancer_detect.lua` as of commit 2121319 (inverts the
  binary image before connected components, then drops every edge-touching
  component).
- `invertfix` — `crop_enhancer_detect.lua` at 71dd1b1 (invert removed, same
  drop-everything-touching-the-edge filter).
- `patched` — the current working tree.

The reference files are copies from git history:

```sh
git show 2121319:crop_enhancer_detect.lua > bench/upstream_detect.lua
git show 71dd1b1:crop_enhancer_detect.lua > bench/invertfix_detect.lua
```

## Pages

`synthetic.py` writes the synthetic edge cases into `pages/` and `raw/`:

| page | what it plants |
|---|---|
| `SYN` | text block plus speckles in the margins |
| `FRAME` | 2 px hollow border around a text block |
| `EDGEBAND` | 15 px solid band on the top edge |
| `EDGETEXT` | text-height glyphs touching the top edge |
| `EDGEPARA` | paragraph fused into one edge-touching component (~29% ink fill) |
| `FOOTER` | small tick marks above the bottom edge |

`prep.py` writes twelve real manga pages (`P01_bleed` … `P12_regular`) from
`SAMPLES_DIR`. That directory needs one subdirectory per chapter, extracted
from whatever chapter archive you have, plus a manifest that maps each role to
one page:

```sh
mkdir -p "$SAMPLES_DIR/mychapter"
unzip some-chapter.cbz -d "$SAMPLES_DIR/mychapter"
printf 'P01_bleed=mychapter/01.jpg\n' >> "$SAMPLES_DIR/manifest.txt"
```

The manifest is not committed — which chapters you point it at is a local
choice — and `prep.py` lists any roles it is still missing.

The selection covers the cases the component filter has to tell apart: dense
full-bleed art (`P01`–`P03`), spreads (`P04`, `P05`), a square page (`P06`),
credits pages with dark edges (`P07`–`P09`) and plain interior pages across
four aspect ratios (`P10`–`P12`).

## Running

```sh
KDIR=~/Sources/koreader/base/build/x86_64-pc-linux-gnu-debug
cd "$KDIR"   # ffi.loadlib resolves libs/ relative to the cwd
KO_ROOT=~/Sources/koreader PLUGIN_DIR=~/Sources/crop_enhancer.koplugin \
  HARNESS_DIR=~/Sources/crop_enhancer.koplugin/bench \
  luajit ~/Sources/crop_enhancer.koplugin/bench/run.lua PAGE1,PAGE2 > results.txt
python3 bench/compare.py results.txt
python3 bench/timings.py results.txt
```

Environment knobs:

- `CE_REPEAT=3` — run each algorithm N times and report the median time, which
  is what you want for timings; the default of 1 is a single measurement.
- `CE_SETTINGS="frame_fill_max=0.05,thin_edge_frac=0.04"` — override the
  detector settings for a sweep (unset keys use `SETTINGS_DEFAULTS`).

Pages are raw 8-bit grayscale with a `<II` width/height header; both page
writers emit them next to the PNGs that `compare.py` uses for its visuals.

The harness needs a KOReader build tree because `ffi.loadlib` looks for
`libs/` relative to the working directory, and stock LuaJIT lacks
KOReader's `ffi.libc` extension (the harness sets it manually).

`newCtx` fills an identity grayscale palette: willus's `bmp_is_grayscale()`
checks it, and a zeroed palette sends the stock cropper down a conversion
path that yields an all-black `srcgrey`.

## Reading the numbers

`compare.py` prints `cut ink%` — the share of the page's ink that ends up
outside the crop — and `IoU` against the bounding box of *every* ink pixel.
Both assume that all ink should be kept, so on the synthetic pages they reward
keeping the planted artifact: a low `area%` on `FRAME`, `EDGEBAND` or `EDGEPARA`
is the filter doing its job. On the real pages every ink pixel is page content,
so `cut ink%` is the metric that matters there.

## Measured

Twelve real pages plus the six synthetic ones, `CE_REPEAT=3`, x86_64 Linux
(the ratios are what carries over to a Kindle, not the absolute numbers):

| page | stock | upstream | invertfix | patched |
|---|---|---|---|---|
| `P01_bleed` | 99.8% area, 0.2% cut | 76.6% area, **23.5% cut** | nil (nothing kept) | 99.8% area, 0.2% cut |
| `P02_bleed` | 99.8%, 0.3% | 32.5%, **81.9% cut** | 50.7%, **72.9% cut** | 99.8%, 0.3% |
| `P03_edgeband` | 99.5%, 0.2% | 37.7%, **82.7% cut** | 47.5%, **82.2% cut** | 99.8%, 0.2% |
| `P06_square` | 99.8%, 0.3% | 97.8%, 2.2% | 83.7%, **16.5% cut** | 99.8%, 0.3% |
| `P07_credits` | 90.4%, 9.3% | 81.9%, **18.9% cut** | 86.8%, **14.5% cut** | 99.7%, 0.3% |
| `EDGETEXT` | 47.5%, 0.0% | nil | 27.9%, **2.2% cut** | 48.5%, 0.0% |
| `EDGEPARA` | 40.6%, 0.0% | nil | nil | 41.0%, 0.0% |
| `FRAME` | 99.8%, 1.2% | nil | 27.9% (frame dropped) | 27.9% (frame dropped) |

Timings over 73 pages sampled across 18 downloaded chapters, `CE_REPEAT=7`:

| algo | median | p90 |
|---|---|---|
| `stock` | 22.2 ms | 37.8 ms |
| `upstream` | 9.1 ms | 17.0 ms |
| `invertfix` | 7.5 ms | 12.3 ms |
| `patched` | 9.2 ms | 17.5 ms |

Dropping `pixInvert` saved 18% and the per-component ink measurement of the new
filter costs 23% back, so the net change against `2121319` is +1%: in time terms
the rewrite is free, and every full-bleed page stops losing content.

`frame_fill_max` is capped at 0.20 (`SETTINGS_LIMITS`). Sweeping it over these
pages shows no result change between 0.10 and 0.20, but at 0.50 `P11_regular`
collapses from 95.6% to 73.5% of the page and `P10_regular` loses a 17 px band
off the top: high values start classifying body text that reaches the edge as a
hollow frame. `EDGEPARA` is the synthetic version of that failure — one fused
paragraph at ~29% ink fill whose top edge survives at 0.20 and would be dropped
at 0.50, so it fails if the cap is ever raised.
