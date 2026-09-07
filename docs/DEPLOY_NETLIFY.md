# DEPLOY_NETLIFY.md — deploying RC5 into the existing Netlify project

Scope: replaces the website in the existing Netlify site. Domain, DNS, Kit account, Kit form and confirmation workflow stay as they are. Nothing here creates a new site, form or audience.

## 1. Project settings (Site configuration → Build & deploy)

| Setting | Value |
|---|---|
| Base directory | the folder that contains `netlify.toml` (the `FPI_SUBSCRIBER_LAUNCH_RC5/` project root) |
| Build command | `python3 build/extract.py && python3 build/build.py` (from `netlify.toml`; needs Python 3.11 with `requirements.txt` — Pillow, numpy) |
| Publish directory | `dist` |
| Functions directory | `netlify/functions` (bundler `esbuild`, from `netlify.toml`) |
| Node version | 20 (`netlify.toml`) |

Alternative if the Netlify build image cannot install the Python dependencies: commit the `dist/` produced by this package (it is byte-reproducible; hashes in `RELEASE_MANIFEST.json`), set the build command to empty, keep publish `dist` and the functions directory as above. The function is still built and deployed by Netlify in that case; only the static generation is skipped. A drag-and-drop upload of `dist/` alone deploys **no function** and must not be used for production.

## 2. Environment variables (Functions scope)

Required: `KIT_V3_API_KEY`, `KIT_FORM_ID` (the existing values), `SITE_ORIGIN=https://<canonical host>`, `LOG_HASH_SECRET=<long random string>`.
Optional: `KIT_V3_API_SECRET` (enables suppression of cancelled/bounced/complained addresses), `KIT_V3_INTEREST_FIELD` (name of an existing Kit custom field), `KIT_TAG_NEWSLETTER`, `KIT_TAG_SHOW`, `KIT_TAG_INDEX`, `KIT_TAG_BENCHMARK`, `KIT_TAG_BENCHMARK_CALCULATOR`, `KIT_TAG_BENCHMARK_REPORT` (numeric tag ids), `ALLOW_PREVIEW_ORIGINS=1` (deploy-preview context only), `SIGNUPS_DISABLED` (emergency stop; see runbook §8).
Leave `KIT_PROVIDER` unset or `v3-form`. Do not set `KIT_API_KEY`/V4 variables. **Every environment change needs a new deploy to take effect.**

## 3. Steps

1. Compare `netlify/functions/subscribe.mjs` with the function currently deployed; confirm the live form id and that the custom fields `source` and `signup_page` exist in Kit. Decide the interest mapping (runbook §5).
2. Set the environment variables above. Note the current known-good deploy id for rollback.
3. Deploy preview first (branch or PR deploy). In the deploy-preview context only, set `ALLOW_PREVIEW_ORIGINS=1`. On the preview run runbook §4 (routes, 404, redirects, headers, GET `/api/subscribe` platform rejection, POST from another origin → 403, native rate limit with Netlify's enforcement delay) and §5 (one owner-controlled signup per path).
4. Promote to production ("Publish deploy" or merge). Re-run the header/redirect/404/API checks on the production host. Remove `ALLOW_PREVIEW_ORIGINS` from any non-preview context.
5. Run runbook §6 (confirmation e-mail, activation, welcome, repeat and unsubscribed behaviour, sender footer) with owner-controlled addresses before any public promotion.

## 4. Rollback

Deploys → last known-good deploy → "Publish deploy" restores the earlier site and function together. Environment variables are unaffected.

## 5. Not done in this package (needs the account)

No preview or production deploy was made, no header/redirect/rate-limit behaviour was observed on Netlify, no e-mail was sent, and Kit's live behaviour (form membership, tag/field mapping, confirmation send, re-send cadence, resubscribe handling) is unconfirmed. `docs/TEST_RESULTS.md` separates local evidence from these live items.
