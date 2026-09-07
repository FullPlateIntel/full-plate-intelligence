# Full Plate Intelligence — FPI_SUBSCRIBER_LAUNCH_RC5

Production release candidate of the Full Plate Intelligence website for the subscriber-acquisition launch,
built from the approved single-file design `ORIGINAL_index_8_3_0_INDEX_REWORKED_5_14_0_2_1.html` (kept unchanged).

- **Status:** IMPLEMENTATION COMPLETE, LOCALLY VERIFIED (`docs/TEST_RESULTS.md`). Not deployment-verified; not subscriber-launch-ready (`START_HERE.md`, `docs/LAUNCH_RUNBOOK.md` §9).
- **RC5 changes:** `docs/CHANGELOG_RC5.md` (approved Steve component as a durable build override, signup timeout, interest recording, `SIGNUPS_DISABLED` emergency stop, privacy wording, preview generator, runbook corrections).
- **Build:** `make build` → `dist/` (nine static pages, 404, no-JS subscribe result pages, hashed assets, sitemap, robots).
- **Host:** the existing Netlify project. Root `netlify.toml` publishes `dist/`; the function is `netlify/functions/subscribe.mjs` (Kit V3 form workflow by default); env names in `.env.example`; steps in `docs/DEPLOY_NETLIFY.md`.
- **Headers/redirects:** generated from `hosting/headers.json` into `dist/_headers` and `dist/_redirects`.
- **Tests:** `tests/README.md`; results in `docs/TEST_RESULTS.md` and `tests/results/`.
- **Documents:** `docs/AUDIT_AND_FIXES.md`, `docs/COPY_CHANGES.md`, `docs/SEO_MAP.md`, `docs/TEST_RESULTS.md`, `docs/LAUNCH_RUNBOOK.md`, `docs/EMAIL_COPY.md`, `docs/DEPLOY_NETLIFY.md`, `docs/CHANGELOG_RC2.md`, `docs/CHANGELOG_RC3.md`, `docs/CHANGELOG_RC5.md`. Release inventory: `RELEASE_MANIFEST.json`.
- **Configuration:** `site.config.json` (origin, launch state, analytics; values marked CONFIRM need the owner).

Requirements: Python 3.11 with Pillow, numpy and Playwright (Chromium); Node 18+.
