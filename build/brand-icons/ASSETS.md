# Full Plate Intelligence — brand favicon (Steve hand-drawn mark)

**Date:** 2026-09-11  
**Purpose:** Replace the live plate-only favicon with Steve Dillberg’s attached hand-drawn fork + plate + knife mark (white background, orange center).

## Source

- Steve’s attached desired logo (white background; fork left, plate with orange yolk/center, knife right)
- Not Nina’s black-square favicon-v2 pack
- Generated sizes under `steve-logo-favicons/` then embedded as `.b64` for the build

## Deliverables (embedded in this folder)

| File | Size | Ships as |
|------|------|----------|
| `favicon-16.png.b64` | 16×16 | optional |
| `favicon-32.png.b64` | 32×32 | optional |
| `favicon-48.png.b64` | 48×48 | `/assets/img/favicon-brand.png` (primary `rel=icon`) |
| `apple-touch-icon-180.png.b64` | 180×180 | `/assets/img/apple-touch-icon.png` |

## Build

1. `build/brand_favicon.py` decodes `.b64` → `dist/assets/img/`
2. `build/apply_brand_favicon_html.py` runs after `build/build.py` and rewrites HTML icon links
3. Wired from `netlify.toml` and `Makefile`

## Notes

- Google SERP favicon cache can lag days–weeks after deploy
- No merge / live publish without Steve approval
