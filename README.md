# Crop Enhancer Plugin for KOReader

Replaces KOReader's built-in page auto-crop algorithm with leptonica connected-component analysis. Better at ignoring thin borders, page-edge noise, and scan artifacts that fool the original pixel-counting approach.

## Features

- **Enhanced auto-crop** — leptonica connected-component analysis replaces the default `k2pdfopt_crop_bmp` pipeline. Detects content regions more accurately on scanned documents with thin borders or noise.
- **Panel zoom** — overrides `getPanelFromPage` with the same leptonica pipeline, finding the specific panel at the touch position.
- **Configurable** — threshold, border width, minimum content area, and margin are all adjustable via the bottom toolbar or Settings menu.
- **Dispatcher actions** — all settings are available as Dispatcher actions for key/gesture binding.
- **i18n** — English, Portuguese (Brazil), Vietnamese, Japanese, Simplified Chinese, Traditional Chinese.

## Screenshoot
| Before (Auto crop default) | After (With alogrimth) | After (With alogrimth + padding) |
| --- | -- | --- |
| <img width="435" height="740" alt="image" src="https://github.com/user-attachments/assets/1435ab1a-b0c4-42d5-b70c-64b47d37280e" /> | <img width="435" height="740" alt="image" src="https://github.com/user-attachments/assets/e3858865-b6f2-44cc-b3eb-ca1627c6db54" /> | <img width="435" height="740" alt="image" src="https://github.com/user-attachments/assets/8b41ef47-6fd5-4776-93c0-3156b8b11aec" /> | 
| <img width="435" height="740" alt="image" src="https://github.com/user-attachments/assets/8c48ab01-f0e6-40dc-9254-de00c8538c27" /> | <img width="435" height="740" alt="image" src="https://github.com/user-attachments/assets/762adbec-0430-4fdb-bf00-aab68838731b" /> | <img width="435" height="740" alt="image" src="https://github.com/user-attachments/assets/cdb16c91-ea0e-478e-80fa-a85eb89c2d8b" /> |

## Requirements

- KOReader (tested on Kindle PW3)
- Leptonica (bundled with KOReader)

## Installation

Copy `crop_enhancer.koplugin/` to `koreader/plugins/`:

```
koreader/plugins/crop_enhancer.koplugin/
```

## Settings

| Setting | Default | Description |
|---|---|---|
| Threshold | 180 | Grayscale threshold (0-255). Pixels below this are considered content. |
| Border max width | 5 | Distance from the page edge that counts as touching it. |
| Min content area | 50 | Minimum bounding-box area (px²) to count as content. |
| Frame fill | 0.10 | Edge-touching components whose ink fills less than this share of their bounding box are page frames. Capped at 0.20. |
| Thin edge | 0.02 | Edge-touching components thinner than this share of the page are lines. |
| Margin | 0.05 | Extra margin around detected content (fraction of DPI). |
| Debug log | off | Print timing and pipeline details to the log. |

Access via: **Bottom toolbar (crop panel) > Enhanced Crop** or **Tools > Enhanced Crop Settings**.

## How it works

```
bitmap2pix(kc.src)
  → pixConvertRGBToGrayFast     (32bpp → 8bpp)
  → pixThresholdToBinary        (1 = ink, 0 = paper)
  → pixConnCompPixa            (ink components, kept for fill checks)
  → filter: drop small components and thin/hollow page furniture;
            keep full-bleed artwork
  → merge kept boxes → bbox
```

### Component filter

A component is kept unless it is noise (smaller than `min_content_area`) or
page furniture: touching the page edge *and* either a solid line thinner than
`thin_edge_frac` of the page, or a hollow frame whose ink fills less than
`frame_fill_max` of its bounding box. Full-bleed artwork touches the edge too,
but it is dense, so it is kept; thin text-like components are kept as well.

`frame_fill_max` stops at 0.20 because body text that reaches the page edge has
about a quarter of its bounding box covered in ink: past that point the filter
starts cutting paragraphs instead of frames. The bench harness measures the
trade-off — see `bench/README.md`.

### Auto-crop (`getAutoBBox`)

Merges all kept components into a single bounding box. Falls back to the original KOPTContext method if leptonica finds nothing useful.

### Panel zoom (`getPanelFromPage`)

Returns the single connected component that contains the touch position. Falls back to the original KOReader panel detection if no matching component is found.

## License

This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed with this file, You can obtain one at https://www.mozilla.org/MPL/2.0/.
