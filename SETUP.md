# Full Plate Intelligence — Pre-Launch Site Setup Guide

This folder is a complete, deploy-ready Netlify site:

```
fullplate-site/
├── index.html                        ← the website (all pages in one file)
├── netlify.toml                      ← Netlify configuration
├── netlify/functions/subscribe.mjs   ← secure serverless endpoint for Kit signups
└── SETUP.md                          ← this guide
```

No build step is required. Netlify serves `index.html` and automatically deploys
the function at `POST /api/subscribe`.

---

## 1. What you need to configure in Kit

Log in at https://app.kit.com and do these three things:

### a. Create (or pick) the Full Plate Weekly form
All three website signup forms feed **one** Kit form (one audience).

1. In Kit go to **Grow → Landing Pages & Forms** and create a simple form
   named e.g. "Full Plate Weekly" (design doesn't matter — it's never shown;
   the website only uses its ID as the subscription target).
2. Find the **form ID**: open the form in the editor and look at the URL —
   `https://app.kit.com/forms/designers/XXXXXXX/edit` → the number `XXXXXXX`
   is your form ID.
3. Decide whether the form uses **double opt-in** (Settings → Incentive in the
   form editor). If double opt-in is on, subscribers must click a confirmation
   email before becoming "confirmed" — recommended for list quality and
   deliverability, and it matches the site's "headed to your inbox" message.

### b. Create two custom fields (for source tracking)
In Kit go to **Subscribers**, open any subscriber (or use the field manager),
and add these two custom fields ([Kit guide](https://help.kit.com/en/articles/2502504-how-to-add-custom-fields-to-subscribers)):

- `source` — which signup form was used
- `signup_page` — the page path where they signed up

Field keys must be exactly `source` and `signup_page` (lowercase).
The site records these values per subscriber:

| Signup location            | `source` value        |
|----------------------------|-----------------------|
| Homepage hero form         | `homepage-hero`       |
| Homepage bottom CTA form   | `homepage-bottom-cta` |
| Meet Steve page form       | `steve-page`          |

You can segment or tag by these fields inside Kit (e.g. an automation that
tags subscribers where `source = steve-page`). The function also sends a
`referrer` URL with `utm_campaign=<source>`, so Kit's own subscriber-source
display shows meaningful data too.

> If you skip creating the custom fields, signups still work — the function
> detects the missing fields and retries without them, so no subscriber is
> ever lost over tracking metadata.

### c. Create a V4 API key
1. Go to **Settings → Developer** (https://app.kit.com/account_settings/developer_settings)
2. Under **V4 Keys**, click **Add a new key**, give it a name like
   `fullplate-website`, and **copy the key immediately** — Kit only shows it
   once.

---

## 2. Environment variables (Netlify)

In the Netlify dashboard: **Site configuration → Environment variables →
Add a variable**. Add exactly these two:

| Variable name | Value                                        |
|---------------|----------------------------------------------|
| `KIT_API_KEY` | the V4 API key you created in Kit            |
| `KIT_FORM_ID` | the numeric ID of your Full Plate Weekly form |

Set them for all scopes/contexts (at minimum "Functions" and "Production").
After adding or changing variables, **redeploy the site** so the function
picks them up.

Credentials live **only** in these environment variables — they are never in
the repository or in any browser-visible code.

---

## 3. Deploying to Netlify

Option A — Git-based (recommended):
1. Push this folder to a GitHub/GitLab repo.
2. In Netlify: **Add new site → Import an existing project**, pick the repo.
3. Build command: none. Publish directory: `.` (already set in `netlify.toml`).
4. Add the environment variables (step 2), then deploy.

Option B — Netlify CLI:
```
npm install -g netlify-cli
cd fullplate-site
netlify deploy --prod
```
(Drag-and-drop deploys in the web UI do NOT deploy functions — use A or B.)

---

## 4. Contact email

The Contact page, Privacy Policy, and Terms currently use
**Steve@FullPlateIntel.com**. If that address changes, search `index.html`
for `Steve@FullPlateIntel.com` and replace all occurrences.

---

## 5. How to test after deploying

1. **Valid signup:** open the live site, enter a real email in the hero form,
   click GET FULL PLATE WEEKLY. You should see the "You're in!" message, and
   the subscriber should appear in Kit (Subscribers) within a few seconds,
   with `source = homepage-hero`. With double opt-in enabled they show as
   unconfirmed until they click the confirmation email.
2. **All three forms:** repeat from the bottom CTA and from the Meet Steve
   page (different email addresses, or the same one — both are fine) and
   check the `source` values in Kit.
3. **Duplicate:** submit the same email twice — the second attempt should
   still show the normal success message.
4. **Invalid email:** try `foo@bar` — you should see "Please enter a valid
   email address." and nothing should reach Kit.
5. **Failure handling:** temporarily set `KIT_API_KEY` to a wrong value and
   redeploy — submissions should show a friendly "didn't go through" message
   (and NOT the success message). Restore the correct key afterwards.
6. **Function logs:** Netlify dashboard → **Logs → Functions → subscribe**
   shows detailed errors if anything misbehaves (details are logged
   server-side only; visitors only ever see friendly messages).

---

## 6. Notes

- The success message ("You're in! Full Plate Weekly is headed to your
  inbox.") is only displayed after Kit has accepted the subscriber — or when
  the person is already subscribed, which is treated as a normal success.
- The endpoint validates and sanitizes everything server-side, never exposes
  Kit errors to visitors, and times out gracefully if Kit is slow.
- Optional hardening later: Netlify's built-in rate limiting or a CAPTCHA if
  bot signups ever become a problem. Kit's double opt-in already prevents
  fake addresses from becoming confirmed subscribers.
