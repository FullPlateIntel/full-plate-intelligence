#!/usr/bin/env python3
"""Decode brand favicon embeds into dist/assets/img/.

Source: Steve Dillberg hand-drawn fork + plate + knife mark (white background).
Supports a single `.b64` file or ordered `.b64.partNN` chunks (joined in order).
"""
from __future__ import annotations

import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST_IMG = ROOT.parent / "dist" / "assets" / "img"
ICONS = ROOT / "brand-icons"

# logical name -> output filename
MAP = {
    "favicon-48.png": "favicon-brand.png",
    "apple-touch-icon-180.png": "apple-touch-icon.png",
    "favicon-32.png": "favicon-32.png",
    "favicon-16.png": "favicon-16.png",
}


def load_b64(stem: str) -> bytes:
    """stem like favicon-48.png — load .b64 or join .b64.part*."""
    parts = sorted(ICONS.glob(f"{stem}.b64.part*"))
    if parts:
        text = "".join(p.read_text().strip() for p in parts)
        return base64.b64decode(text, validate=True)
    single = ICONS / f"{stem}.b64"
    if single.exists():
        text = single.read_text().strip()
        return base64.b64decode(text, validate=True)
    raise FileNotFoundError(f"No embed for {stem}")


def main() -> int:
    DIST_IMG.mkdir(parents=True, exist_ok=True)
    for stem, out_name in MAP.items():
        try:
            raw = load_b64(stem)
        except FileNotFoundError:
            continue
        out = DIST_IMG / out_name
        out.write_bytes(raw)
        print(f"wrote {out} ({len(raw)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
