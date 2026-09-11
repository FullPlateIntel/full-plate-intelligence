# Brand favicon assets

Source: Steve Dillberg attached hand-drawn fork + plate + knife mark (white background, orange center), 2026-09-11.

`build/brand_favicon.py` decodes embeds into `dist/assets/img/`.
- Prefer numeric chunks: `favicon-48.png.b64.part01` … (and apple-touch `part01`–`part42`)
- Fallback: monolithic `.b64` when no parts exist
- Ignores `.hex` / other sidecars

`build/apply_brand_favicon_html.py` runs after `build/build.py` and rewrites HTML icon links.

Primary browser icon: favicon-48 → `/assets/img/favicon-brand.png`
Apple touch: apple-touch-180 → `/assets/img/apple-touch-icon.png`
