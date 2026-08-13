// =============================================================
// Full Plate Intelligence — Kit (ConvertKit) subscribe endpoint
// Netlify Function, served at POST /api/subscribe
//
// Credentials are read from environment variables — never
// hard-code them in this file or anywhere in the repo:
//   KIT_API_KEY  — Kit v4 API key (Kit → Settings → Developer → V4 Keys)
//   KIT_FORM_ID  — numeric ID of the Full Plate Weekly form in Kit
//
// Flow (Kit v4 API):
//   1. POST /v4/subscribers            — upsert subscriber + source fields
//   2. POST /v4/forms/{id}/subscribers — add them to the Full Plate
//      Weekly form/audience. Kit returns 201 (added) or 200 (already
//      on the form) — both are treated as success, so duplicate
//      subscribers get a normal success response.
// =============================================================

const KIT_API_BASE = "https://api.kit.com/v4";

// Pragmatic email check; Kit performs its own validation as well.
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function json(status, body) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

async function kitPost(path, apiKey, body) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    return await fetch(`${KIT_API_BASE}${path}`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "X-Kit-Api-Key": apiKey,
      },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timer);
  }
}

export default async (req) => {
  if (req.method !== "POST") {
    return json(405, { ok: false, error: "method_not_allowed" });
  }

  const apiKey = process.env.KIT_API_KEY;
  const formId = process.env.KIT_FORM_ID;
  if (!apiKey || !formId) {
    console.error("Missing KIT_API_KEY and/or KIT_FORM_ID environment variables.");
    return json(500, { ok: false, error: "not_configured" });
  }

  let payload;
  try {
    payload = await req.json();
  } catch {
    return json(400, { ok: false, error: "bad_request" });
  }

  const email = String(payload.email || "").trim().toLowerCase();
  if (!EMAIL_RE.test(email) || email.length > 254) {
    return json(400, { ok: false, error: "invalid_email" });
  }

  // --- Source tracking (sanitized server-side; email-only form) ---
  // e.g. "homepage-hero", "homepage-bottom-cta", "steve-page"
  const source =
    String(payload.source || "")
      .toLowerCase()
      .replace(/[^a-z0-9_-]/g, "")
      .slice(0, 50) || "website";
  const pagePath =
    String(payload.path || "")
      .replace(/[^\w\-\/#.]/g, "")
      .slice(0, 100) || "/";

  // Build a referrer URL from the actual site origin so Kit's own
  // "subscriber source" UI shows something meaningful too.
  let origin = "https://fullplateintelligence.netlify.app";
  try {
    const o = req.headers.get("origin") || req.headers.get("referer");
    if (o) origin = new URL(o).origin;
  } catch {
    /* keep fallback */
  }
  const referrer = `${origin}/?utm_source=website&utm_medium=signup-form&utm_campaign=${source}`;

  try {
    // Step 1 — create or update the subscriber, stamping source fields.
    let createRes = await kitPost("/subscribers", apiKey, {
      email_address: email,
      fields: { source, signup_page: pagePath },
    });

    // If the Kit account doesn't have the custom fields yet, retry
    // without them so signups never get lost over tracking metadata.
    if (createRes.status === 422) {
      const detail = await createRes.text();
      console.warn("Kit rejected create-with-fields (422); retrying without fields:", detail);
      createRes = await kitPost("/subscribers", apiKey, { email_address: email });
    }

    if (createRes.status === 422) {
      // Kit itself rejected the email address.
      return json(400, { ok: false, error: "invalid_email" });
    }
    if (!createRes.ok) {
      console.error("Kit create-subscriber failed:", createRes.status, await createRes.text());
      return json(502, { ok: false, error: "subscribe_failed" });
    }

    // Step 2 — add the subscriber to the Full Plate Weekly form.
    // 201 = newly added, 200 = already subscribed → both are success.
    const formRes = await kitPost(`/forms/${formId}/subscribers`, apiKey, {
      email_address: email,
      referrer,
    });

    if (formRes.ok) {
      return json(200, { ok: true });
    }

    console.error("Kit add-to-form failed:", formRes.status, await formRes.text());
    return json(502, { ok: false, error: "subscribe_failed" });
  } catch (err) {
    console.error("Subscribe function error:", err);
    return json(502, { ok: false, error: "subscribe_failed" });
  }
};

export const config = {
  path: "/api/subscribe",
};
