#!/usr/bin/env python3
"""Decode brand favicon embeds into dist/assets/img/.

Source: Steve Dillberg hand-drawn fork + plate + knife mark (white background).
Supports a single `.b64` file or ordered `.b64.partNN` chunks (joined in order).
Numeric part suffix only — ignores `.hex` / other sidecars.
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DIST_IMG = ROOT.parent / "dist" / "assets" / "img"
DEFAULT_ICONS = ROOT / "brand-icons"

# logical stem -> output filename under assets/img
MAP = {
    "favicon-48.png": "favicon-brand.png",
    "apple-touch-icon-180.png": "apple-touch-icon.png",
    "favicon-32.png": "favicon-32.png",
    "favicon-16.png": "favicon-16.png",
}

_PART_RE = re.compile(r"\.b64\.part(\d+)$")


def _part_files(icons: Path, stem: str) -> list[Path]:
    """Return numeric .b64.partNN files only, sorted by part number."""
    found: list[tuple[int, Path]] = []
    for p in icons.glob(f"{stem}.b64.part*"):
        m = _PART_RE.search(p.name)
        if not m:
            continue
        found.append((int(m.group(1)), p))
    found.sort(key=lambda t: t[0])
    return [p for _, p in found]


def load_b64(stem: str, icons: Path | None = None) -> bytes:
    """stem like favicon-48.png — join numeric .b64.partNN or load .b64."""
    icons = icons or DEFAULT_ICONS
    parts = _part_files(icons, stem)
    if parts:
        text = "".join(p.read_text().strip() for p in parts)
        return base64.b64decode(text, validate=True)
    single = icons / f"{stem}.b64"
    if single.exists():
        text = single.read_text().strip()
        return base64.b64decode(text, validate=True)
    raise FileNotFoundError(f"No embed for {stem}")


def apply_brand_favicon(build_dir: Path, dist_dir: Path) -> str:
    """Write favicon (+ optional sizes) into dist and return primary icon href.

    Called by apply_brand_favicon_html.py after build/build.py.
    """
    icons = Path(build_dir) / "brand-icons"
    dist_img = Path(dist_dir) / "assets" / "img"
    dist_img.mkdir(parents=True, exist_ok=True)
    primary_href = "/assets/img/favicon-brand.png"
    for stem, out_name in MAP.items():
        try:
            raw = load_b64(stem, icons=icons)
        except FileNotFoundError:
            continue
        (dist_img / out_name).write_bytes(raw)
    return primary_href


def main() -> int:
    apply_brand_favicon(ROOT, ROOT.parent / "dist")
    print("brand favicon assets written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
