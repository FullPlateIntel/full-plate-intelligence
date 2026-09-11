# Brand icons (favicon fix 2026-09-11)

Fork + plate + knife mark for favicon / apple-touch (replaces plate-only ORIGINAL favicon).
Source: Nina favicon-v2 from live `#fpi-logo-plate` geometry.

- `*.png.b64` — base64 of PNG deliverables (decoded at build time)
- `fpi-logo-plate-favicon.svg` — master SVG
- See `ASSETS.md` for sizes and notes

build/build.py writes `/assets/img/favicon-brand.png` and `/assets/img/apple-touch-icon.png` into dist and points `<link rel="icon">` / apple-touch at them.
