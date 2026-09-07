# CHANGELOG — FPI_SUBSCRIBER_LAUNCH_RC2 (targeted integration pass over RC1)

Only actual changes are listed. Layout, artwork, page structure, metadata, accessibility markup and the RC1 copy edits are unchanged unless named here.

## A. Primary buttons back to brand orange
- `build/a11y.css`: `--fpi-orange-control` is `#F26A21` again; labels are ink `#1F1F1B` (5.40:1) instead of white; hover `#E9611B` with ink (4.87:1); disabled/busy keep ink labels. Applied to `.btn` (header Subscribe Free, all signup submits), `.rii-btn-primary` / `#page-index .rii-btn-primary` (Index) and `.bm-btn-primary` (Benchmark). Shapes, borders, sketch shadows, sizes, fonts and focus rings untouched. The deeper orange/gold *text* tokens for small text on cream remain.
- Verified: rendered buttons on home, Index and Benchmark are `rgb(242,106,33)` / `rgb(31,31,27)`; axe color-contrast still 0 violations at 1280/768/390.

## B. Kit integration reconciled with the existing V3 form workflow
- `server/subscribe-core.mjs`: default provider is now **`v3-form`**, i.e. `POST https://api.convertkit.com/v3/forms/{KIT_FORM_ID}/subscribe` with `api_key` (`KIT_V3_API_KEY`), `email`, `fields.source`, `fields.signup_page` (the page path; the legacy `path` field is accepted as an alias), optional `fields.<KIT_V3_INTEREST_FIELD>` and optional `tags` (KIT_TAG_* ids) on the same call. The form's existing confirmation (double opt-in) rules apply; nothing is marked active by the handler.
- Optional suppression lookup `GET /v3/subscribers?api_secret=…&email_address=…` when `KIT_V3_API_SECRET` is set; cancelled/bounced/complained addresses get the same public response and no write. Without the secret the lookup is skipped and logged as skipped.
- V4 workflow kept behind `KIT_PROVIDER=v4` (explicit approval + separate live verification required).
- Frontend (`build/site.js`) sends both `page` and `path`.
- Credential names are distinct (`KIT_V3_API_KEY` vs `KIT_API_KEY`); missing credentials for the selected provider return 503 `not_configured`, never fake success.
- Interest recording is only claimed in logs when a tag id or interest field is configured (`interest_recorded`); otherwise it is documented as not recorded.

## C. Netlify-specific packaging
- Root `netlify.toml`: `publish = "dist"` (deliberate change from the earlier root publish), build command runs the two build scripts, functions dir `netlify/functions`, esbuild bundler.
- `netlify/functions/subscribe.mjs`: real entry point importing `../../server/subscribe-core.mjs` (resolves from the repo layout; verified by `tests/netlify_entry_test.mjs`), `process.env` for configuration, Netlify's trusted `context.ip` for address-based limiting, `config = { path: '/api/subscribe', method: ['POST'], rateLimit: { windowLimit: 10, windowSize: 60, aggregateBy: ['ip'], action: 'rate_limit' } }`.
- Origin policy: `SITE_ORIGIN` and Netlify's runtime `URL` are always allowed; deploy-preview/branch origins (`https://<branch>--<SITE_NAME>.netlify.app`) only with `ALLOW_PREVIEW_ORIGINS=1`.
- `build/build.py` now writes `dist/_headers` and `dist/_redirects` (generated from `hosting/headers.json`), so Netlify reads them from the publish directory.
- Removed the Vercel/Cloudflare/nginx adapters and candidate configs; `server/adapters/node-http.mjs` remains only for the local test server. Mock Kit, test settings and debug endpoints live outside `dist/`.
- Existing content-version query strings on CSS/JS are unchanged.

## D. Partial-success handling (V4 path)
- Tag calls run after the form add inside their own try/catch. HTTP errors, thrown network errors and timeouts on tagging leave the signup **accepted**, log `subscribe.partial` with `tags_ok:false` and the failing tag id, and never claim the interest was saved. Failures before acceptance still return 503. In the V3 workflow tags travel on the single form call, so there is no partial state.
- Regression tests: `tagerror@` (500), `tagreset@` (socket reset), `tagtimeout@` (hang), plus repeat-submission idempotence.

## E. Copy closeout
- Generic success message shortened to "Thanks. If this address is new to our list, a confirmation email is on its way." with the rejoin/support line moved to a secondary help element under it.
- Helper lines under the Show, Index and Benchmark forms shortened; Index hero micro line shortened. All other copy unchanged.
- Steve page sticky notes: **not changed**; no approved replacement was supplied.

## F. Tests and documentation
- `tests/run_tests.py`: V3 contract checks, no-secret variant, V4 partial-tag cases, Netlify entry-point run, rendered button colour check, secondary-help check. Final run: 549 PASS, 0 FAIL, 20 INFO.
- New: `tests/netlify_entry_test.mjs`, `docs/DEPLOY_NETLIFY.md`, this changelog. Updated: `.env.example`, `tests/test.env`, `docs/AUDIT_AND_FIXES.md`, `docs/TEST_RESULTS.md`, `docs/LAUNCH_RUNBOOK.md`, `README.md`.
