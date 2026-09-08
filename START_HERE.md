# START_HERE — FPI_SUBSCRIBER_LAUNCH_RC5 (build RC5_1)

**Use this one project root:** `FPI_SUBSCRIBER_LAUNCH_RC5/` (the folder containing this file, `netlify.toml`, `dist/`, `netlify/functions/subscribe.mjs`, `server/subscribe-core.mjs`, `build/`, `tests/`, `docs/`). It is complete on its own: no merge with RC3 or the RC4 partial archive is needed. `RELEASE_MANIFEST.json` lists the sha256 of every file.

**What RC5 is:** the RC3 production project with the owner-approved Steve section (question cards intentionally removed — final), the signup-timeout fix, correct product-interest recording, a real emergency-stop switch, accurate privacy wording, and the corrected runbook. Details: `docs/CHANGELOG_RC5.md`. Local evidence: `docs/TEST_RESULTS.md`, `tests/results/`.

**Status:** locally verified, **not deployed, not live-verified**. Do not announce a subscriber launch until part B below is done.

## Netlify settings (existing project — do not create a new site, form or audience)

| Setting | Value |
|---|---|
| Base directory | `FPI_SUBSCRIBER_LAUNCH_RC5/` (where `netlify.toml` is) |
| Build command | `python3 build/extract.py && python3 build/build.py` |
| Publish directory | `dist` |
| Functions directory | `netlify/functions` (esbuild; the function imports `../../server/subscribe-core.mjs`) |
| Runtime | Python 3.11 (+ `requirements.txt`: Pillow, numpy), Node 20 |

If the Netlify build image cannot install the Python dependencies, commit the shipped `dist/` (reproducible; hashes in the manifest), leave the build command empty, keep publish `dist` and the functions directory. **A drag-and-drop upload of `dist/` alone does not deploy the function** — use the Git/CLI deploy of the whole project root.

**Environment variables (Functions scope).** Required: `KIT_V3_API_KEY`, `KIT_FORM_ID` (existing values), `SITE_ORIGIN=https://<canonical host>`, `LOG_HASH_SECRET=<long random string>`. Optional: `KIT_V3_API_SECRET`, `KIT_V3_INTEREST_FIELD`, `KIT_TAG_NEWSLETTER`, `KIT_TAG_SHOW`, `KIT_TAG_INDEX`, `KIT_TAG_BENCHMARK`, `KIT_TAG_BENCHMARK_CALCULATOR`, `KIT_TAG_BENCHMARK_REPORT`, `ALLOW_PREVIEW_ORIGINS=1` (deploy-preview context only), `SIGNUPS_DISABLED` (emergency only). Leave `KIT_PROVIDER` at `v3-form`; do not set V4 keys. Names and explanations: `.env.example`. **Every environment change needs a new deploy.**

## Deploy, roll back, stop

- **Deploy:** push the project root to the connected repository (or `netlify deploy --build --prod` from it) → deploy preview first → run part B → "Publish deploy" to production. Steps: `docs/DEPLOY_NETLIFY.md`.
- **Roll back:** Netlify → Deploys → last known-good deploy → "Publish deploy" (site and function together). Note that deploy id before promoting RC5.
- **Emergency stop:** set `SIGNUPS_DISABLED=1` → trigger a new deploy. Every submission then shows the visible "temporarily unavailable" message (JSON 503 `disabled`; no-JS posts go to `/subscribe/error/`); nothing reaches Kit. Clear it and deploy again to resume. (Unsetting `KIT_API_KEY` does nothing on the V3 workflow.)

## A. Done in this package (local)

- Two clean builds with the exact `netlify.toml` command: identical output (132 files). Steve override, artwork, copy and privacy changes survive a clean build; no manual post-build patch.
- `tests/run_tests.py`: **623 PASS, 0 FAIL, 37 INFO** (2026-09-07; INFO = accepted brand-contrast exceptions, height/transfer records, reviewed minor axe notes). Includes: nine pages × ten widths (1440…320) with no overflow; Steve at 320/375/390/400/401 (word spacing) and 1280; seven signup placements; header SUBSCRIBE FREE reaching each page's own email box (focused); both Benchmark CTA paths; success, empty/invalid, duplicate submits, 500/429/malformed/200-without-ok/network, stalled headers, stalled body, late response, retry; keyboard, reduced motion, no-JavaScript submission; strict CSP with zero console errors; SIGNUPS_DISABLED for JS and no-JS; interest recording for all six interests; one `fpi-config` per page and in the preview.
- `tests/core_unit_test.mjs` 31/31; `tests/netlify_entry_test.mjs` 12/12 (inside the suite); function bundled with esbuild (as Netlify does) and invoked successfully; `tests/color_fidelity.py` 1,949 colours compared, 0 brand-colour changes (the 5 `svg.arrow-doodle` first-instance mismatches are identical on the untouched RC3 dist in this environment — a test artefact, not a change).
- Accepted contrast exceptions unchanged and disclosed: orange text 2.73:1, gold 2.01:1, white-on-orange 3.06:1 (not WCAG AA passes).

## B. Live activation checklist (not performed — needs the Netlify/Kit accounts and your authorization)

1. **Deployed routes:** every sitemap URL 200; `/show` → `/show/` 301 (all bare paths); `/index.html` → `/`; unknown path → HTTP 404 branded; `/#/benchmark` and `/#/index?utm_source=x` migrate; HTTPS on apex and www with the non-canonical host redirecting.
2. **Headers/API:** `curl -I` shows CSP, nosniff, X-Frame-Options, Referrer-Policy, Permissions-Policy, HSTS; `/assets/*` immutable; `/api/*` no-store. POST from another origin → 403. **GET `/api/subscribe`**: record the platform's actual rejection (POST-only function). **Native rate limit**: confirm in the deploy log, then >10 requests/min from one IP → 429s within Netlify's ~10 s enforcement delay (request 11 need not be the first 429).
3. **Kit mapping:** confirm `KIT_FORM_ID`, custom fields `source`/`signup_page`, and whichever `KIT_TAG_*` / `KIT_V3_INTEREST_FIELD` you set. Check the function log `subscribe.result` line shows `interest_recorded:true` with `interest_via` for a Benchmark CTA test; `utm_*` values appear in the log's `attribution` only (never in Kit on this workflow).
4. **Owner-controlled signups:** homepage (JS), Benchmark "Notify Me About the Benchmark Report", and one with JavaScript off (lands on `/subscribe/thanks/`). Confirm in Kit: on the form, `inactive` until confirmed, correct source/page/interest.
5. **E-mail journey:** confirmation received → link clicked → `active` → intended welcome message with the confirmed sender name, postal address and unsubscribe link. Repeat an unconfirmed address (note re-send behaviour); unsubscribe then re-submit (no re-add with `KIT_V3_API_SECRET`; otherwise record Kit's behaviour). Check SPF/DKIM/DMARC and `List-Unsubscribe`.
6. **Operator identity:** `operator_legal_name` and postal address confirmed and present in the privacy policy, Kit sender profile and footer; social links live; owner-specific claims and launch dates confirmed (COPY_CHANGES.md "Approval needed"). None of these were invented here.
7. **Browsers:** iPhone Safari and a desktop browser on the deployed candidate: `/`, `/steve/` (Steve section at phone width), `/benchmark/`, one test signup; real mobile load feel.
8. **Rollback/monitoring:** known-good deploy id noted; monitoring/escalation owner named (`docs/LAUNCH_RUNBOOK.md` §7).
9. **Prelaunch states:** keep `launch.weekly` and the products at `coming_soon` until the newsletter actually sends.

An accepted API response is not evidence of delivered e-mail or a confirmed subscriber. Analytics stays disabled and image optimisation is deferred by owner decision; neither is a launch blocker.
