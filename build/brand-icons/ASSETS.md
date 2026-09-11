# Full Plate Intelligence — favicon-v2 (fork + plate + knife)

**For:** Nina (Brand & Creative) / Evan (implementation)  
**Date:** 2026-09-11  
**Purpose:** Replace the live plate-only favicon (`favicon-fa91169a.png`) with the full brand mark.

## Source

- Live site: https://fullplateintel.com
- SVG symbol: `#fpi-logo-plate` (viewBox `0 0 52 34`)
- Geometry: fork left · concentric plate rings + orange center · knife right  
  Path data taken from live HTML (same as `src/partials/symbols.html` in repo).
- Brand orange: CSS `--fpi-orange: #F26A21` from `/assets/css/site.css`
- Field: black `#000000`; linework: white `#FFFFFF`
- These assets are **not** plate-only; they replace `favicon-fa91169a.png`.

## Build notes

1. Extracted `#fpi-logo-plate` paths from live HTML.
2. Wrapped mark in a square SVG (`viewBox 0 0 56 56`), centered with padding (`translate(2,11)`).
3. Removed `vector-effect="non-scaling-stroke"` so strokes scale; slightly thickened for favicon legibility.
4. Rasterized with cairosvg → PNG; small sizes (16/32) use a thickened stroke variant and oversized render + LANCZOS downscale.
5. Source SVGs kept alongside PNGs for re-export.

## Deliverables

| File | Size | Notes |
|------|------|--------|
| `favicon-16.png` | 16×16 | Thickened strokes; utensils still readable |
| `favicon-32.png` | 32×32 | Primary browser tab size |
| `favicon-48.png` | 48×48 | Useful for Google / Windows |
| `apple-touch-icon-180.png` | 180×180 | Apple touch / mobile candidates |
| `favicon-512.png` | 512×512 | Master for Evan to resize / convert in PR |
| `fpi-logo-plate-favicon.svg` | 56×56 SVG | Faithful geometry (master source) |
| `fpi-logo-plate-favicon-sm.svg` | 56×56 SVG | Thickened variant used for 16/32 |

## For Evan (PR)

- Swap hashed favicon asset so `<link rel="icon">` points at the utensil mark (not plate-only).
- Add `<link rel="apple-touch-icon" href="…">` using the 180 PNG.
- Optional: derive `.ico` / manifest icons from `favicon-512.png`.
- Do not change header wordmark or Organization schema logo (already correct with utensils).
- After deploy: hard-refresh; Google SERP favicon cache may take days–weeks.

## Caveats

- Original mark is wider than tall (`52×34`); square canvases add black letterbox padding top/bottom — intentional.
- At 16×16, fork tines merge somewhat; silhouette still reads as fork | plate | knife.
- Antialiasing on small sizes slightly shifts orange edge pixels away from exact `#F26A21`; solid center on 180/512 is exact.
