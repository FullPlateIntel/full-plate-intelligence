# TEST_RESULTS.md — FPI_SUBSCRIBER_LAUNCH_RC5

Evidence is separated into three tiers. Only tier 1 was performed. No earlier package's counts are reused; every number below comes from the run recorded in `tests/results/results.json`.

| Tier | Status |
|---|---|
| 1. Local automated tests (this file) | **Performed** — final run 2026-09-07T17:47:37Z (187.7 s), `tests/run_tests.py` → **623 PASS, 0 FAIL, 37 INFO, 0 NOT_TESTED**; includes `tests/core_unit_test.mjs` (32 rows incl. exit status) and `tests/netlify_entry_test.mjs` (13 rows incl. exit status). Separately: `tests/color_fidelity.py` 1,949 computed colours compared with the ORIGINAL reference, 0 brand-colour changes (5 `svg.arrow-doodle` first-instance mismatches are reproduced identically on the untouched RC3 dist in this environment: the comparison keys on the first element per selector while the arrows are individually coloured; not a change). Netlify function bundled with esbuild 0.24 (`--bundle --platform=node --format=esm`, 18.4 kB) and invoked from the bundle. |
| 2. Netlify preview/production deployment checks (routes, redirects, HTTPS, headers, GET rejection, API routing, native rate limit, browsers) | **Not performed** — no access to the Netlify project; steps in START_HERE.md part B and LAUNCH_RUNBOOK.md §4 |
| 3. Live Kit journey (form membership, fields/tags, confirmation e-mail, activation, welcome, re-send, unsubscribe handling, deliverability, sender footer) | **Not performed** — no Kit account access, no e-mail sent; steps in LAUNCH_RUNBOOK.md §5–6 |

Full table with evidence per check: `tests/results/results.md` (and `results.json`). Screenshots: `tests/results/shots/` (nine pages at 1440/1280/768/390/320 with the brand fonts; `fallbackfont_*` with the font files blocked; `steve_section_1280.png` and `steve_section_390.png` for the RC5 component). Before/after for the Steve section: `evidence/steve_rc5/` (RC3 sticky-note version) vs `tests/results/shots/steve_section_*.png`.

## Environment (what these results do and do not prove)

| Item | Value |
|---|---|
| Machine | Linux sandbox, no external network to api.kit.com or fonts.googleapis.com |
| Python / Node | 3.11.15 / v22.22.2 |
| Browser | Playwright bundled Chromium (headless); contexts at 1440, 1280, 1024, 901, 899, 768, 561, 559, 390, 320 px, plus 375/400/401 for the Steve word-spacing checks; reduced-motion and JavaScript-disabled contexts |
| Fonts | Caveat 500/600/700 and Patrick Hand 400 self-hosted woff2 from `dist/assets/fonts` (verified loaded via `document.fonts` on every page) |
| Static server | `tests/serve.py` (clean URLs, 404 status, headers from `hosting/headers.json`, streamed proxy to the API with a distinct client address per request); a second instance on :8766 proxies to the raw-socket stub (:8791) for the stalled-body/no-headers/late-response cases |
| Subscription API | `server/dev-server.mjs` with `tests/test.env` (V3 form workflow, mock secret, debug endpoint on) against `server/mock-kit.mjs`; extra instances for no-credentials, TRUST_XFF, V3-without-secret, newsletter-only-tag, SIGNUPS_DISABLED and V4 cases; the Netlify entry point in-process by `tests/netlify_entry_test.mjs` |
| Accessibility engine | axe-core 4.10.3 (`tests/vendor/axe.min.js`), tags wcag2a, wcag2aa, wcag22aa, best-practice |

These are **local, automated results**. They establish behaviour of the code and the built pages. They do **not** establish: real e-mail delivery, Kit's live behaviour or tag/field mapping, production response headers, the platform's GET rejection, native rate-limit enforcement, DNS/HTTPS, Safari/iPhone rendering, Core Web Vitals field data, or legal compliance.

## Coverage by group (final run)

| Group | Checks | What was verified |
|---|---|---|
| assets | 13 PASS | 99 original images byte-identical to the ORIGINAL data URIs (sha256 manifest); 2 RC5 artwork files byte-identical to build/assets/img; every referenced /assets/* file exists |
| html | 84 PASS | per page: size < 200 KB, one h1, main + skip link, absolute canonical, OG/Twitter/description, no inline rasters, no em dashes/TODO, no inline style; exactly one id="fpi-config" in each of the 12 built HTML files |
| seo | 16 PASS | distinct titles/canonicals, JSON-LD parses, sitemap = nine URLs, robots rules, noindex on 404 and subscribe result pages |
| links | 9 PASS | all internal hrefs resolve |
| perf | 18 PASS + 9 INFO | width/height on every img, one eager hero per product page; first-load transfer per route (INFO) |
| steve | 13 PASS + 2 INFO | RC5 component in the paired grid, no cards/sticky notes, no CPA/nickname, absolute asset URLs with dimensions, real space after the hidden breaks, scoped CSS; in the browser: 320/375/390/400 break hidden + "pattern. The"/"Intelligence was", 401/1280 two-line breaks kept, illustration at natural proportions; section heights (INFO) |
| preview | 2 PASS | standalone preview: one fpi-config, noindex, banner, legacyRoutes empty, not inside dist/ |
| security | 4 PASS | no credential patterns; .env.example names only; CSP/nosniff/X-Frame-Options/Referrer-Policy served; zero console errors under the enforced CSP |
| a11y | 36 PASS + 11 INFO | axe-core 4.10: no serious/critical rule other than colour contrast on any page (contrast = INFO, accepted brand deviation B9); heading order; aria-current; skip link; keyboard signup; reduced motion |
| fonts | 12 PASS | self-hosted Caveat/Patrick Hand loaded on every page, OFL licences shipped, no googleapis |
| contrast | 5 INFO + 5 PASS | token ratios below (brand exceptions recorded as INFO, not passes) |
| design | 11 PASS + 9 INFO | no darkened substitutes; primary buttons rgb(242,106,33)/white; no stretched images; page heights vs the ORIGINAL at 1280 (INFO; legal pages not gated) |
| backend | 46 PASS | V3 form contract, legacy path alias, uniform responses, invalid inputs, allowlists, honeypot, origin/method/content-type/size, provider failures and timeout, per-address limiter, no-JS redirects, not-configured 503, TRUST_XFF, V3 without secret, RC5: newsletter-only tag -> interest_recorded:false, calculator via its own tag, SIGNUPS_DISABLED (JSON 503 / form 303 error), V4 partial-tag cases |
| core-unit | 32 PASS | tests/core_unit_test.mjs: all six interests with/without mappings, generic tags never counting, invalid values, interest field, suppressed/failed requests, disable switch on both providers, log hygiene |
| netlify-entry | 13 PASS | tests/netlify_entry_test.mjs: real entry point in-process (import path, config, origin rules, context.ip limiter, form fallback, in-process GET 405, SIGNUPS_DISABLED for JSON and form) |
| routing | 20 PASS | direct loads, 404 status, legacy hash migration with query, anchors, back/forward, deep link |
| forms | 91 PASS | header SUBSCRIBE FREE on all nine pages (six on-page forms scrolled into view + email focused; legal pages → /#signup); seven placements (labels, hidden fields, honeypot, live regions, POST fallback, empty/malformed, triple submit -> one request, focus, messages); Benchmark CTA interests reach Kit; client 500/429/malformed/200-without-ok/network; pending/subscribed/accepted messages; 12 s timeout (route delay); RC5: stalled body, no headers, late 200 ignored, retry |
| analytics | 3 PASS | events without email; no third-party requests; first-touch utm in session storage |
| nojs | 3 PASS + 1 INFO | product page renders, form POST -> /subscribe/thanks/ reaching the mock provider; legacy hash limitation (INFO) |
| responsive | 192 PASS | nine pages at 1440/1280/1024/901/899/768/561/559/390/320: no overflow, no element past the viewport, 24 px targets at 390; fallback-font sweeps at 901/1024/390 |

## Steve section footprint (Chromium, brand fonts loaded)

| Width | RC3 (sticky notes) Founder/Why section | RC5 (approved component) | Page height RC3 → RC5 |
|---|---|---|---|
| 1440 | 517 px | 618 px (+101) | 2256 → 2357 px |
| 1280 | 517 px | 618 px (+101) | 2256 → 2357 px |
| 390 | 1324 px | 1448 px (+124) | 5275 → 5374 px |

Section order after the component unchanged (hero → principles → founder grid → three columns → CTA); family illustration rendered at its natural ratio (design-lock check); no horizontal overflow at any width.

## Contrast (approved brand tokens kept unchanged; INFO rows are accepted deviations, not WCAG passes)

| Pair | Status |
|---|---|
| brand orange #F26A21 text on cream: 2.73:1 (WCAG AA needs 4.5:1) | INFO |
| brand orange #F26A21 text on the peach card #F6EBDD: 2.60:1 (WCAG AA needs 4.5:1) | INFO |
| deep orange #D9531E text on cream: 3.59:1 (WCAG AA needs 4.5:1) | INFO |
| deep orange #D9531E as large text on cream: 3.59:1 (WCAG AA needs 3.0:1) | PASS |
| gold #D8A441 text on cream: 2.01:1 (WCAG AA needs 4.5:1) | INFO |
| white labels on brand-orange buttons #F26A21: 3.06:1 (WCAG AA needs 4.5:1) | INFO |
| green #355E3B on cream: 6.64:1 (needs 4.5:1) | PASS |
| blue #2F6F9F on cream: 4.80:1 (needs 4.5:1) | PASS |
| muted ink #4B4A43 on cream: 7.92:1 (needs 4.5:1) | PASS |
| ink #1F1F1B on cream: 14.72:1 (needs 4.5:1) | PASS |

## Page height at 1280 px vs the ORIGINAL file (fallback fonts for the original)

| Route | Original | Build | Delta |
|---|---|---|---|
| / | 2321 px | 2230 px | -3.9% |
| /weekly/ | 1561 px | 1531 px | -1.9% |
| /show/ | 1734 px | 1742 px | +0.5% |
| /restaurant-intelligence-index/ | 3537 px | 3550 px | +0.4% |
| /benchmark/ | 3673 px | 3779 px | +2.9% |
| /steve/ | 2165 px | 2357 px | +8.9% |
| /privacy/ | 1694 px | 2032 px | +20.0% |
| /terms/ | 1460 px | 1541 px | +5.5% |
| /contact/ | 900 px | 900 px | +0.0% |

## First-load transfer at 390 px (local server, uncompressed, lazy images excluded; not a CWV score)

| Route | Measured |
|---|---|
| / first load at 390px | 665 KB total, HTML 33 KB, images 347 KB, 23 requests |
| /weekly/ first load at 390px | 974 KB total, HTML 28 KB, images 711 KB, 30 requests |
| /show/ first load at 390px | 867 KB total, HTML 28 KB, images 605 KB, 27 requests |
| /restaurant-intelligence-index/ first load at 390px | 1682 KB total, HTML 37 KB, images 1411 KB, 28 requests |
| /benchmark/ first load at 390px | 952 KB total, HTML 44 KB, images 673 KB, 23 requests |
| /steve/ first load at 390px | 633 KB total, HTML 30 KB, images 319 KB, 23 requests |
| /privacy/ first load at 390px | 464 KB total, HTML 25 KB, images 154 KB, 16 requests |
| /terms/ first load at 390px | 462 KB total, HTML 23 KB, images 154 KB, 16 requests |
| /contact/ first load at 390px | 410 KB total, HTML 21 KB, images 154 KB, 15 requests |

## Not tested / limitations (honest list)

- No deployment to Netlify: response headers, redirects, 404 status, HTTPS, the platform-level GET rejection for the POST-only function, native `config.rateLimit` validation and enforcement timing, and function cold-start behaviour are unobserved.
- No Kit account access: form membership, `source`/`signup_page` population, tag/field mapping, confirmation e-mail, activation, welcome message, re-send cadence, resubscribe handling, SPF/DKIM/DMARC, `List-Unsubscribe`, sender footer.
- Browsers: Chromium only. Safari/iPhone, Firefox and assistive-technology sessions were not run.
- Performance: local uncompressed transfer sizes only; no Lighthouse or field data.
- Legal: privacy/terms wording is aligned with the implementation but not reviewed by counsel; operator legal name and postal address are still unconfirmed (`site.config.json`).
- Colour fidelity: 5 `svg.arrow-doodle` rows are a known limitation of the comparison method (see tier 1), present on RC3 too.
