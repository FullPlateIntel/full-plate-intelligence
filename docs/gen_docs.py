#!/usr/bin/env python3
"""Generate COPY_CHANGES.md and SEO_MAP.md from the build report (single source of truth)."""
import json, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.loads((ROOT / 'build' / 'build-report.json').read_text())
CFG = json.loads((ROOT / 'site.config.json').read_text())

def strip(s): return html.unescape(s).replace('|', '\\|').replace('\n', ' ')

# ------------------------------------------------------------------ COPY_CHANGES.md
out = ['# COPY_CHANGES.md', '', f'Build {R["build_time"]}. Launch state: weekly={R["launch"]["weekly"]}, show={R["launch"]["show"]}, index={R["launch"]["index"]}, benchmark={R["launch"]["benchmark"]}.',
       '', 'Every change below is applied by `build/copy_edits.py` as an exact-match replacement on the approved 5_14_0_2_1 text. "Approval needed" lists the factual claim an owner must confirm before or after launch; changes without one are editorial and need no sign-off.', '',
       '## Page copy', '', '| Page | Original | Replacement | Reason | Approval needed |', '|---|---|---|---|---|']
for c in R['copy_changes']:
    out.append(f"| {c['page']} | {strip(c['original'])[:260]} | {strip(c['replacement'])[:320]} | {strip(c['reason'])} | {strip(c['approval'] or '')} |")
out += ['', '## Form-adjacent helper text (new)', '', '| Placement (data-source) | Text |', '|---|---|']
import sys; sys.path.insert(0, str(ROOT / 'build')); import copy_edits
for k, v in copy_edits.FORM_HELP.items(): out.append(f'| {k} | {v or "(hero uses the launch-state help line below)"} |')
st = copy_edits.STATE_COPY[R['launch']['weekly']]
out += ['', '## Launch-state copy (weekly = ' + R['launch']['weekly'] + ')', '', '| Key | Text |', '|---|---|'] + [f'| {k} | {v} |' for k, v in st.items()]
out += ['', '## Thank-you / status messages shown by the browser', '', '| Server status | Message |', '|---|---|',
        f'| accepted (default; used for new, existing and suppressed addresses alike so list membership is never revealed) | {st["thanks_generic"]} |',
        f'| pending_confirmation (only when Kit reports a brand-new inactive subscriber) | {st["thanks_pending"]} |',
        f'| subscribed (reserved for a verified single-opt-in flow; not returned by the RC1 handler) | {st["thanks_subscribed"]} |',
        '| invalid_email | Please enter a valid email address. |', '| rate_limited (429) | Too many attempts from this connection. Please wait a minute and try again. |',
        f'| any other failure | Signups are temporarily unavailable. Please try again in a few minutes, or email {CFG["contact_email"]}. |',
        '', '## Policy pages', '', 'Privacy Policy and Terms of Use were rewritten to describe only the subscriber release (see `build/legal/privacy.html` and `terms.html`; originals remain in the ORIGINAL file). Revision date: ' + CFG['policy_revision_date'] + '. Both need legal review (see the verification register in AUDIT_AND_FIXES.md).',
        '', '## Claims left unchanged and why', '',
        '- "more than 25 years" advising restaurant owners (Weekly, Index, Steve): supported by the approved biography; kept.',
        '- "a boutique CPA firm specializing in restaurants, hospitality, and high-net-worth individuals" (Steve, RC5 owner wording) and "more than 25 years": approved biography; kept.',
        '- Steve is described without a CPA credential (owner instruction 2026-09-07); the firm remains described as a CPA firm.',
        '- Homepage cost percentages (28/30/9/15/10/8): kept as artwork with the new visible qualifier; not a benchmark.',
        '- "No spam. Unsubscribe anytime." (home, Steve): accurate for the Kit list with a working unsubscribe link; kept.',
        '- Social handles (@fullplateintel on Instagram, LinkedIn, TikTok): carried over; owner to confirm the profiles are live before launch.',
        ]
(ROOT / 'docs' / 'COPY_CHANGES.md').write_text('\n'.join(out) + '\n')

# ------------------------------------------------------------------ SEO_MAP.md
intent = {'home': 'Full Plate Intelligence, Full Plate Intel, restaurant financial insights, restaurant business intelligence',
          'weekly': 'restaurant newsletter, restaurant financial newsletter, food cost / labor cost / cash flow / profitability education',
          'show': 'restaurant podcast, restaurant-business conversations',
          'index': 'restaurant industry report, independent restaurant data, restaurant financial trends, food and beverage costs, labor and productivity',
          'benchmark': 'restaurant benchmarking, restaurant financial benchmarks, food cost / labor / prime cost topics',
          'steve': 'Steve Dillberg, restaurant accountant and advisor, Schofer Dillberg & Company, Full Plate Intelligence founder',
          'privacy': '(utility page)', 'terms': '(utility page)', 'contact': '(utility page)'}
sd = {'home': 'Organization (#organization), Person (#person), WebSite (#website), WebPage', 'steve': 'ProfilePage with mainEntity -> Person (#person); Organization; WebSite', }
out = ['# SEO_MAP.md', '', f'Production origin (CONFIRM): `{R["origin"]}`. Sitemap: `/sitemap.xml`. Robots: `/robots.txt` (staging variant in `hosting/robots.staging.txt`, to be paired with an `X-Robots-Tag: noindex` header and HTTP auth).', '',
       'Trailing-slash URLs are canonical; the host must 301 the bare path to the slash form (rules included in `hosting/candidates/`). Canonical host (apex vs www) must be chosen before DNS; the build refuses localhost/staging origins.', '',
       '| Page | URL | Search intent | Title | Meta description | Share image | Structured data |', '|---|---|---|---|---|---|---|']
for pid, p in R['pages'].items():
    out.append(f"| {pid} | {p['path']} | {intent[pid]} | {strip(p['title'])} | {strip(p['description'])} | {p['og_image']} (1200x630) | {sd.get(pid, 'WebPage; Organization; Person; WebSite (@graph)')} |")
out += ['', '## Old route -> new URL (client-side allowlist in `assets/js/site.js`; fragments never reach the server)', '', '| Legacy hash | New URL |', '|---|---|'] + [f'| `{k}` | `{v}` |' for k, v in R['legacy_routes'].items()]
out += ['', 'Section anchors (`#signup`, `#ecosystem`, `#show-join`, `#weekly-join`, `#index-join`, `#benchmark-join`, `#signup-steve`) are preserved. A legacy hash with tracking appended (`#/index?utm_source=x`) is migrated with the tracking kept. Without JavaScript a legacy hash link shows the homepage (documented limitation).',
        '', '## Not in the sitemap / noindex', '', '- `/subscribe/thanks/` and `/subscribe/error/` (no-JavaScript form results): `noindex, nofollow`, also disallowed in robots.txt.', '- `/404.html`: noindex; served with a real 404 status for unknown paths.', '- `/api/subscribe`: POST only (`config.method` in the Netlify function); a GET is rejected by the platform before the handler runs — observe the actual deployed response (runbook §4.3).',
        '', '## Founder discoverability', '', 'Visible text on /steve/: `Steve Dillberg. Founder of Full Plate Intelligence and founding partner of Schofer Dillberg & Company.` plus the existing biography. Person JSON-LD uses `name: Steve Dillberg`, `affiliation: Schofer Dillberg & Company` (no credential; owner instruction). No SDC link is rendered because no verified URL was supplied (`site.config.json: sdc_url`). No bookkeeping-service wording was added.',
        '', '## AI-search note', '', 'Discoverability by AI answer engines relies on the same crawlable HTML, clear titles, descriptive body copy and structured data above; no separate speculative work was done.']
(ROOT / 'docs' / 'SEO_MAP.md').write_text('\n'.join(out) + '\n')
print('docs written')
