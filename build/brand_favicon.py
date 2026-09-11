"""Decode Nina brand favicon assets into dist/ during build."""
from __future__ import annotations
import base64
from pathlib import Path

def apply_brand_favicon(build_dir: Path, dist_dir: Path) -> str:
    brand = build_dir / "brand-icons"
    def b64png(name: str, dest_name: str) -> str:
        raw = base64.b64decode((brand / f"{name}.b64").read_text().strip())
        out = dist_dir / "assets" / "img" / dest_name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw)
        return f"/assets/img/{dest_name}"
    favicon = b64png("favicon-48.png", "favicon-brand.png")
    b64png("apple-touch-icon-180.png", "apple-touch-icon.png")
    b64png("favicon-32.png", "favicon-brand-32.png")
    return favicon
