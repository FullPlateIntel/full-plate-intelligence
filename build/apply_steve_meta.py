#!/usr/bin/env python3
"""Post-build: apply Steve-locked /steve/ title + meta/social descriptions.

Runs after build/build.py. Keeps the large build.py untouched.
Review-only / Steve-approved wording — do not invent personal CPA credentials.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

TITLE = "Steve Dillberg | Founder of Full Plate Intelligence"
DESC = (
    "Meet Steve Dillberg, founder of Full Plate Intelligence and founding partner "
    "of Schofer Dillberg & Company, a boutique CPA firm serving restaurants and "
    "hospitality businesses."
)

STEVE_HTML = DIST / "steve" / "index.html"


def replace_attr(html: str, attr: str, value: str) -> str:
    # Replace content="..." for a given attribute name occurrence patterns used in head
    patterns = [
        rf'(<meta\s+name="{re.escape(attr)}"\s+content=")([^"]*)(")',
        rf'(<meta\s+property="{re.escape(attr)}"\s+content=")([^"]*)(")',
        rf'(<meta\s+name="{re.escape(attr)}"\s+content=\')([^\']*)(\')',
        rf'(<meta\s+property="{re.escape(attr)}"\s+content=\')([^\']*)(\')',
    ]
    out = html
    for pat in patterns:
        out, n = re.subn(pat, rf"\g<1>{value}\g<3>", out, count=1)
        if n:
            return out
    return out


def replace_title(html: str, title: str) -> str:
    out, n = re.subn(r"<title>[^<]*</title>", f"<title>{title}</title>", html, count=1)
    if not n:
        raise SystemExit("title tag not found in steve/index.html")
    return out


def patch_json_ld(html: str, title: str, desc: str) -> str:
    """Best-effort: update ProfilePage name/description in ld+json if present."""
    # Keep surgical — only replace the known old description string if present,
    # and ensure title appears in ld+json name fields for the webpage.
    old = (
        "Meet Steve Dillberg, restaurant accountant and advisor, founder of Full Plate "
        "Intelligence and founding partner of Schofer Dillberg & Company, with more than "
        "25 years advising restaurant owners and operators."
    )
    if old in html:
        html = html.replace(old, desc)
    # Also replace if a prior proposed short line is present
    short = (
        "Meet Steve Dillberg, founder of Full Plate Intelligence and founding partner "
        "of Schofer Dillberg & Company, a boutique CPA firm."
    )
    if short in html and desc not in html:
        html = html.replace(short, desc)
    return html


def main() -> int:
    if not STEVE_HTML.exists():
        print(f"skip: {STEVE_HTML} missing (run build first)", file=sys.stderr)
        return 0
    html = STEVE_HTML.read_text(encoding="utf-8")
    html = replace_title(html, TITLE)
    # meta description + og/twitter (build uses description from PAGES into these)
    for attr in ("description", "og:description", "twitter:description"):
        html = replace_attr(html, attr, DESC)
    for attr in ("og:title", "twitter:title"):
        html = replace_attr(html, attr, TITLE)
    html = patch_json_ld(html, TITLE, DESC)
    if "restaurant accountant" in html.lower():
        # Fail closed if personal mislabel remains in head-ish content
        head = html.split("</head>", 1)[0]
        if "restaurant accountant" in head.lower():
            raise SystemExit("restaurant accountant still present in <head> after patch")
    STEVE_HTML.write_text(html, encoding="utf-8")
    print(f"steve meta applied -> {STEVE_HTML}")
    print(f"title: {TITLE}")
    print(f"desc:  {DESC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
