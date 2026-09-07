#!/usr/bin/env python3
"""Colour fidelity: compare computed colours of colour-bearing elements in each dist page against the
same selectors in the read-only ORIGINAL reference file. Run with dist served at BASE (default :8080)."""
import asyncio, pathlib, sys, json
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8080'
ORIG = 'file://' + str(ROOT / 'ORIGINAL_index_8_3_0_INDEX_REWORKED_5_14_0_2_1.html')
PAGES = ['/', '/weekly/', '/show/', '/restaurant-intelligence-index/', '/benchmark/', '/steve/', '/privacy/', '/terms/', '/contact/']
JS = '''() => {
  const out = {}; const seen = {};
  const props = ['color','backgroundColor','borderTopColor','stroke','fill','textDecorationColor'];
  for (const el of document.querySelectorAll('body *')) {
    if (el.closest('svg') && el.tagName !== 'svg' && !el.closest('symbol')) {}
    const s = getComputedStyle(el);
    const cls = [...el.classList].filter(c => !/^st-\\d+$/.test(c)).sort().join('.');
    const key = el.tagName.toLowerCase() + (cls ? '.' + cls : '');
    if (!cls || seen[key]) continue; seen[key] = 1;  // class-bearing elements only; bare tags are ambiguous
    const v = {}; for (const p of props) { const x = s[p]; if (x && x !== 'none' && !/rgba\\(0, 0, 0, 0\\)/.test(x)) v[p] = x; }
    out[key] = v;
  }
  return out;
}'''
BRAND = {'rgb(242, 106, 33)', 'rgb(217, 83, 30)', 'rgb(216, 164, 65)', 'rgb(184, 137, 47)', 'rgb(183, 66, 15)', 'rgb(134, 96, 19)', 'rgb(156, 112, 25)', 'rgb(233, 97, 27)'}
def is_brand(v): return v in BRAND
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        await pg.goto(ORIG); await pg.wait_for_timeout(500); ref = await pg.evaluate(JS)
        diffs = []; compared = 0
        for r in PAGES:
            await pg.goto(BASE + r); await pg.wait_for_timeout(300); cur = await pg.evaluate(JS)
            for key, v in cur.items():
                if key not in ref: continue
                for prop, val in v.items():
                    if prop in ref[key]:
                        compared += 1
                        if ref[key][prop] != val and (is_brand(ref[key][prop]) or is_brand(val)): diffs.append((r, key, prop, ref[key][prop], val))
        await b.close()
    print(json.dumps({'compared': compared, 'differences': diffs}, indent=1))
    return 0 if not diffs else 1
sys.exit(asyncio.run(main()))
