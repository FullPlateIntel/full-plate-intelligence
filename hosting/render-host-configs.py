#!/usr/bin/env python3
"""Turn hosting/headers.json into the Netlify _headers and _redirects files (hosting/candidates/), which
build/build.py copies into dist/ where Netlify reads them."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
H = json.loads((ROOT / 'hosting' / 'headers.json').read_text())
OUT = ROOT / 'hosting' / 'candidates'; OUT.mkdir(exist_ok=True)
all_h = H['all']; html_h = H['html']; asset_h = H['assets']

# ---- Cloudflare Pages / Netlify: _headers + _redirects
lines = ['# Generated from hosting/headers.json. Cloudflare Pages and Netlify both read this file.', '/*']
for k, v in {**all_h, **html_h}.items(): lines.append(f'  {k}: {v}')
lines += ['', '/assets/*']
for k, v in asset_h.items(): lines.append(f'  {k}: {v}')
lines += ['', '/api/*', '  Cache-Control: no-store', '']
# note: the HTML-only headers (CSP, X-Frame-Options) are harmless on assets, so nothing is "unset" (neither platform has a portable unset syntax)
(OUT / '_headers').write_text('\n'.join(lines))
(OUT / '_redirects').write_text('# Netlify: clean URLs are native; unknown paths fall through to the 404 page with a real 404 status.\n# Trailing-slash canonical: redirect the bare path to the slash form (Netlify does this by default with "Pretty URLs"; keep both rules explicit).\n/show            /show/            301\n/weekly          /weekly/          301\n/restaurant-intelligence-index /restaurant-intelligence-index/ 301\n/benchmark       /benchmark/       301\n/steve           /steve/           301\n/privacy         /privacy/         301\n/terms           /terms/           301\n/contact         /contact/         301\n/index.html      /                 301\n/*               /404.html         404\n')
print('wrote', sorted(p.name for p in OUT.iterdir()))
