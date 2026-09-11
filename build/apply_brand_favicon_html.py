#!/usr/bin/env python3
"""Post-build: install fork+knife favicon assets and rewrite HTML head links.

Runs after build/build.py. Keeps the large build.py untouched.
"""
from __future__ import annotations
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BUILD, DIST = ROOT / "build", ROOT / "dist"
sys.path.insert(0, str(BUILD))
from brand_favicon import apply_brand_favicon  # noqa: E402

favicon = apply_brand_favicon(BUILD, DIST)
apple = '/assets/img/apple-touch-icon.png'
icon_re = re.compile(r'<link rel="icon"[^>]*>')
apple_re = re.compile(r'<link rel="apple-touch-icon"[^>]*>\s*')

def patch(html: str) -> str:
    html = apple_re.sub('', html)
    repl = f'<link rel="icon" type="image/png" href="{favicon}">\n<link rel="apple-touch-icon" href="{apple}">'
    if icon_re.search(html):
        return icon_re.sub(repl, html, count=1)
    # Fallback: insert before stylesheet if icon link missing
    return html.replace(
        '<link rel="stylesheet"',
        repl + '\n<link rel="stylesheet"',
        1,
    )

n = 0
for path in DIST.rglob('*.html'):
    text = path.read_text(encoding='utf-8')
    new = patch(text)
    if new != text:
        path.write_text(new, encoding='utf-8')
        n += 1
print(f'brand favicon applied to {n} html files -> {favicon}')
