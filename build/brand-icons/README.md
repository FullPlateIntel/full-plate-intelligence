# Brand favicon assets

Source: Steve Dillberg attached hand-drawn fork + plate + knife mark (white background, orange center), 2026-09-11.

`build/brand_favicon.py` decodes the `.b64` PNGs into `dist/assets/img/`.
`build/apply_brand_favicon_html.py` runs after `build/build.py` and rewrites HTML icon links.

Primary browser icon: `favicon-48.png.b64` → `/assets/img/favicon-brand.png`
Apple touch: `apple-touch-icon-180.png.b64` → `/assets/img/apple-touch-icon.png`
