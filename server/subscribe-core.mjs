/**
 * Full Plate Intelligence – subscription handler (host-neutral core).
 *
 * `handleSubscribe(request, env, deps)` takes a Web-standard Request and returns a Web-standard Response.
 * The Netlify entry point is netlify/functions/subscribe.mjs; other adapters live in ./adapters.
 *
 * Provider workflows (KIT_PROVIDER):
 *   "v3-form" (DEFAULT, matches the previously deployed launch function)
 *     POST https://api.convertkit.com/v3/forms/{KIT_FORM_ID}/subscribe
 *          { api_key: KIT_V3_API_KEY, email, fields: { source, signup_page[, <KIT_V3_INTEREST_FIELD>] }, tags: [ids] }
 *     Documented (developers.kit.com, V3 reference, read 2026-09-07): api_key + email required; `fields` keys must
 *     already exist as custom fields; `tags` is an array of tag ids; response { subscription: { id, state: inactive|active, subscriber } }.
 *     The form's own confirmation (double opt-in) settings apply to this endpoint. Optional suppression lookup:
 *     GET /v3/subscribers?api_secret=KIT_V3_API_SECRET&email_address=… (only when the secret is configured).
 *   "v4"  (opt-in; requires explicit approval + live verification)
 *     X-Kit-Api-Key; GET /v4/subscribers?email_address; POST /v4/subscribers {email_address, state:"inactive"};
 *     POST /v4/forms/{id}/subscribers; POST /v4/tags/{id}/subscribers. Tagging is optional and never fails the signup.
 *
 * Frontend contract (JSON or form-encoded): email, source (allowlist), interest (allowlist), page (allowlist; the
 * legacy `path` field is accepted as an alias), fpi_ref (honeypot), attribution.utm_* (allowlist).
 *
 * Emergency stop: SIGNUPS_DISABLED=1 (or true) makes every submission return the visible unavailable response
 * (503 JSON / 303 to /subscribe/error/) before any provider call, for the active provider whichever it is.
 * Changing environment variables on Netlify takes effect only after a new deploy (see docs/LAUNCH_RUNBOOK.md).
 *
 * interest_recorded (log field): true only when the requested interest was actually carried by the accepted
 * provider request: newsletter = accepted membership of KIT_FORM_ID; a product interest = its own valid
 * KIT_TAG_* id on the accepted call, or the configured KIT_V3_INTEREST_FIELD. A generic newsletter tag never
 * counts as a product interest. Suppressed, failed and disabled requests never report a recorded interest.
 */

const EMAIL_RE = /^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]{1,64}@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$/;
const SOURCES = new Set(['homepage-hero', 'homepage-bottom-cta', 'show-page', 'weekly-page-bottom', 'index-page', 'benchmark-page', 'steve-page']);
const INTERESTS = new Set(['newsletter', 'show', 'index', 'benchmark', 'benchmark-calculator', 'benchmark-report']);
const PAGES = new Set(['/', '/show/', '/weekly/', '/restaurant-intelligence-index/', '/benchmark/', '/steve/']);
const ATTR_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content'];
const SAFE = /^[A-Za-z0-9_.-]{1,64}$/;
const MAX_BODY = 4096;
const PROVIDER_TIMEOUT_MS = 4000;      // per provider call
const TOTAL_BUDGET_MS = 9000;          // whole request; fits a 10 s serverless limit and the 12 s browser bound
const RATE = { windowMs: 60_000, max: 5 };
const SUPPRESSED = new Set(['cancelled', 'bounced', 'complained', 'unsubscribed']);

export const MESSAGES = {
  generic: 'Thanks. If this address is new to our list, a confirmation email is on its way.',
  invalid_email: 'Please enter a valid email address.',
  bad_request: 'That request could not be read.',
  rate_limited: 'Too many attempts from this connection. Please wait a minute and try again.',
  not_configured: 'Signups are not configured on this deployment.',
  disabled: 'Signups are temporarily unavailable. Please try again in a few minutes.',
  provider_unavailable: 'Signups are temporarily unavailable. Please try again in a few minutes.',
};

function json(status, body, extra = {}) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...extra } });
}
function redirect(location) {
  return new Response(null, { status: 303, headers: { Location: location, 'Cache-Control': 'no-store' } });
}
export function requestId() {
  return (globalThis.crypto && crypto.randomUUID) ? crypto.randomUUID().slice(0, 8) : Math.random().toString(36).slice(2, 10);
}

/** Best-effort limiter over a get/set store. In-memory Map = per instance only; on Netlify the durable control is
 *  the function's own `config.rateLimit` (netlify/functions/subscribe.mjs). */
export function makeRateLimiter(store, opts = RATE) {
  return async function check(key) {
    try {
      const now = Date.now();
      const raw = await store.get(key);
      let rec = raw ? JSON.parse(raw) : { start: now, count: 0 };
      if (now - rec.start > opts.windowMs) rec = { start: now, count: 0 };
      rec.count += 1;
      await store.set(key, JSON.stringify(rec), Math.ceil(opts.windowMs / 1000));
      return { allowed: rec.count <= opts.max, retryAfter: Math.ceil((rec.start + opts.windowMs - now) / 1000) };
    } catch (e) {
      return { allowed: true, degraded: true };
    }
  };
}
export function memoryStore() {
  const m = new Map();
  return {
    async get(k) { const v = m.get(k); if (!v) return null; if (v.exp < Date.now()) { m.delete(k); return null; } return v.val; },
    async set(k, val, ttl) { m.set(k, { val, exp: Date.now() + ttl * 1000 }); },
  };
}

async function hmacHex(key, s) {
  const k = await crypto.subtle.importKey('raw', new TextEncoder().encode(key), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('HMAC', k, new TextEncoder().encode(s));
  return Array.from(new Uint8Array(sig)).map(b => b.toString(16).padStart(2, '0')).join('');
}

/** Client address. Order: platform-verified value passed by the adapter (Netlify context.ip), Cloudflare's
 *  cf-connecting-ip, X-Forwarded-For only with TRUST_XFF=1, else the adapter's socket address. */
function clientAddress(request, env, deps) {
  if (deps.clientIp) return deps.clientIp;
  const h = request.headers;
  if (h.get('cf-connecting-ip')) return h.get('cf-connecting-ip');
  if (env.TRUST_XFF === '1' && h.get('x-forwarded-for')) return h.get('x-forwarded-for').split(',')[0].trim();
  return h.get('x-fpi-remote-addr') || 'unknown';
}

/** Allowed origins: SITE_ORIGIN (canonical), Netlify's runtime URL, and, only with ALLOW_PREVIEW_ORIGINS=1,
 *  this site's Netlify deploy-preview/branch subdomains. */
export function allowedOrigins(env) {
  const list = new Set();
  for (const v of [env.SITE_ORIGIN, env.URL]) if (v && /^https?:\/\//.test(v)) list.add(v.replace(/\/$/, ''));
  return list;
}
function originAllowed(origin, env) {
  if (!origin) return false;
  if (allowedOrigins(env).has(origin)) return true;
  if (env.ALLOW_PREVIEW_ORIGINS === '1' && env.SITE_NAME) {
    const name = env.SITE_NAME.replace(/[^a-z0-9-]/gi, '');
    return new RegExp(`^https://([a-z0-9-]+--)?${name}\\.netlify\\.app$`, 'i').test(origin);
  }
  return false;
}
function sameOrigin(request, env) {
  const origin = request.headers.get('origin');
  if (origin) return originAllowed(origin, env);
  const ref = request.headers.get('referer') || '';
  try { const u = new URL(ref); return originAllowed(u.origin, env); } catch { return false; }
}

async function readBody(request) {
  const ct = (request.headers.get('content-type') || '').toLowerCase();
  const len = Number(request.headers.get('content-length') || 0);
  if (len > MAX_BODY) return { error: 'too_large' };
  const text = await request.text();
  if (text.length > MAX_BODY) return { error: 'too_large' };
  if (ct.startsWith('application/json')) {
    try { const j = JSON.parse(text); return { fields: (j && typeof j === 'object' && !Array.isArray(j)) ? j : {}, mode: 'json' }; }
    catch { return { error: 'bad_json' }; }
  }
  if (ct.startsWith('application/x-www-form-urlencoded')) {
    const p = new URLSearchParams(text); const f = {};
    for (const [k, v] of p) f[k] = v;
    return { fields: f, mode: 'form' };
  }
  return { error: 'bad_content_type' };
}

function sanitize(fields) {
  const out = { errors: [] };
  const email = typeof fields.email === 'string' ? fields.email.trim().toLowerCase() : '';
  if (!EMAIL_RE.test(email) || email.length > 254) out.errors.push('invalid_email');
  out.email = email;
  out.source = SOURCES.has(fields.source) ? fields.source : 'website';
  out.interest = INTERESTS.has(fields.interest) ? fields.interest : 'newsletter';
  const pageRaw = typeof fields.page === 'string' ? fields.page : (typeof fields.path === 'string' ? fields.path.split('#')[0].split('?')[0] : '');
  out.page = PAGES.has(pageRaw) ? pageRaw : '/';
  out.honeypot = typeof fields.fpi_ref === 'string' && fields.fpi_ref.length > 0;
  out.attribution = {};
  const attr = (fields.attribution && typeof fields.attribution === 'object') ? fields.attribution : fields;
  for (const k of ATTR_KEYS) { const v = attr[k]; if (typeof v === 'string' && SAFE.test(v)) out.attribution[k] = v; }
  return out;
}

function timedFetch(fetchImpl, deadline) {
  return async function call(url, init) {
    const remaining = deadline - Date.now();
    if (remaining <= 0) throw Object.assign(new Error('budget exhausted'), { code: 'provider_timeout' });
    const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), Math.min(PROVIDER_TIMEOUT_MS, remaining));
    try {
      const res = await fetchImpl(url, { ...init, signal: ctl.signal });
      let data = null; try { data = await res.json(); } catch { data = null; }
      return { status: res.status, data };
    } finally { clearTimeout(t); }
  };
}
const fail = (code, status) => Object.assign(new Error(code + ' ' + (status || '')), { code, status });
const shape = (r, key) => r.data && typeof r.data === 'object' && r.data[key];

/** Kit V3 client (form subscribe + optional secret lookup). */
export function kitV3Client(env, fetchImpl = fetch, deadline = Date.now() + TOTAL_BUDGET_MS) {
  const base = env.KIT_V3_API_BASE || 'https://api.convertkit.com';
  const call = timedFetch(fetchImpl, deadline);
  return {
    canLookup: !!env.KIT_V3_API_SECRET,
    findByEmail: (email) => call(`${base}/v3/subscribers?api_secret=${encodeURIComponent(env.KIT_V3_API_SECRET)}&email_address=${encodeURIComponent(email)}`, { method: 'GET', headers: { Accept: 'application/json' } }),
    formSubscribe: (email, fields, tags) => call(`${base}/v3/forms/${env.KIT_FORM_ID}/subscribe`, {
      method: 'POST', headers: { 'Content-Type': 'application/json; charset=utf-8', Accept: 'application/json' },
      body: JSON.stringify({ api_key: env.KIT_V3_API_KEY, email, fields, ...(tags.length ? { tags } : {}) }),
    }),
  };
}
/** Kit V4 client. */
export function kitClient(env, fetchImpl = fetch, deadline = Date.now() + TOTAL_BUDGET_MS) {
  const base = env.KIT_API_BASE || 'https://api.kit.com';
  const headers = { 'X-Kit-Api-Key': env.KIT_API_KEY, 'Content-Type': 'application/json', 'Accept': 'application/json' };
  const call = timedFetch(fetchImpl, deadline);
  return {
    findByEmail: (email) => call(base + '/v4/subscribers?email_address=' + encodeURIComponent(email) + '&status=all', { method: 'GET', headers }),
    upsert: (email) => call(base + '/v4/subscribers', { method: 'POST', headers, body: JSON.stringify({ email_address: email, state: 'inactive' }) }),
    addToForm: (formId, email, referrer) => call(`${base}/v4/forms/${formId}/subscribers`, { method: 'POST', headers, body: JSON.stringify(referrer ? { email_address: email, referrer } : { email_address: email }) }),
    tag: (tagId, email) => call(`${base}/v4/tags/${tagId}/subscribers`, { method: 'POST', headers, body: JSON.stringify({ email_address: email }) }),
  };
}

const TAG_ENV = { newsletter: 'KIT_TAG_NEWSLETTER', show: 'KIT_TAG_SHOW', index: 'KIT_TAG_INDEX', benchmark: 'KIT_TAG_BENCHMARK',
                  'benchmark-calculator': 'KIT_TAG_BENCHMARK_CALCULATOR', 'benchmark-report': 'KIT_TAG_BENCHMARK_REPORT' };
/** The configured Kit tag id for one interest, or null when unset / not a positive integer (an invalid value is
 *  ignored so it can never break a valid signup). Each interest maps only to its own variable: calculator and
 *  report requests are never satisfied by the generic KIT_TAG_BENCHMARK. */
export function tagIdFor(env, interest) {
  const v = env[TAG_ENV[interest]];
  return (v !== undefined && v !== null && /^\d+$/.test(String(v).trim())) ? Number(String(v).trim()) : null;
}
/** Tag ids sent with a signup: the newsletter tag (if any) plus the requested interest's own tag (if any). */
export function tagIdsFor(env, interest) {
  return [...new Set([tagIdFor(env, 'newsletter'), tagIdFor(env, interest)].filter(v => v !== null))];
}
/** How the requested interest is carried, given what will actually be sent. Returns { recorded, via }. */
export function interestCapture(env, interest, tagsSent, appliedTags) {
  const ok = appliedTags || tagsSent;
  if (interest === 'newsletter') return { recorded: true, via: 'form' };          // accepted form membership IS the newsletter interest
  const own = tagIdFor(env, interest);
  if (own !== null && ok.includes(own)) return { recorded: true, via: 'tag' };
  if (env.KIT_V3_INTEREST_FIELD && appliedTags === undefined) return { recorded: true, via: 'field' };   // v3 only: the field rides on the same call
  return { recorded: false, via: 'none' };
}
export function signupsDisabled(env) {
  const v = String(env.SIGNUPS_DISABLED || '').trim().toLowerCase();
  return v === '1' || v === 'true' || v === 'yes' || v === 'on';
}

export function providerOf(env) {
  return (env.KIT_PROVIDER || 'v3-form').toLowerCase() === 'v4' ? 'v4' : 'v3-form';
}
export function isConfigured(env) {
  return providerOf(env) === 'v4' ? !!(env.KIT_API_KEY && env.KIT_FORM_ID) : !!(env.KIT_V3_API_KEY && env.KIT_FORM_ID);
}

/**
 * Main handler. deps: { rateLimit?, clientIp?, kit?, kitV3?, log?, fetch? }
 * env (v3-form): SITE_ORIGIN or URL, KIT_V3_API_KEY, KIT_FORM_ID, optional KIT_V3_API_SECRET, KIT_V3_INTEREST_FIELD, KIT_TAG_*, LOG_HASH_SECRET
 * env (v4):      KIT_PROVIDER=v4, KIT_API_KEY, KIT_FORM_ID, optional KIT_TAG_*, KIT_SKIP_FORM_FOR_INACTIVE
 */
export async function handleSubscribe(request, env, deps = {}) {
  const log = deps.log || ((o) => console.log(JSON.stringify(o)));
  const rid = requestId();
  if (request.method !== 'POST') return json(405, { ok: false, error: 'method_not_allowed' }, { Allow: 'POST' });

  const parsed = await readBody(request);
  const wantsHtml = parsed.mode === 'form';
  const reject = (status, code, extra) => wantsHtml ? redirect('/subscribe/error/') : json(status, { ok: false, error: code, message: MESSAGES[code] || MESSAGES.bad_request, ...(extra || {}) });
  const accept = () => wantsHtml ? redirect('/subscribe/thanks/') : json(200, { ok: true, status: 'accepted', message: MESSAGES.generic });

  if (parsed.error) { log({ rid, event: 'subscribe.reject', reason: parsed.error }); return reject(parsed.error === 'too_large' ? 413 : 400, 'bad_request'); }
  if (signupsDisabled(env)) { log({ rid, event: 'subscribe.disabled', note: 'SIGNUPS_DISABLED is set; no provider call made' }); return reject(503, 'disabled'); }
  if (!sameOrigin(request, env)) { log({ rid, event: 'subscribe.reject', reason: 'origin', allowed: [...allowedOrigins(env)] }); return reject(403, 'bad_request'); }

  const f = sanitize(parsed.fields);
  if (f.errors.length) { log({ rid, event: 'subscribe.reject', reason: 'invalid_email', source: f.source }); return reject(400, 'invalid_email'); }

  const ip = clientAddress(request, env, deps);
  const rl = deps.rateLimit ? await deps.rateLimit('sub:' + (await hmacHex(env.LOG_HASH_SECRET || 'fpi-rl', ip)).slice(0, 32)) : { allowed: true };
  if (!rl.allowed) { log({ rid, event: 'subscribe.rate_limited', source: f.source }); return wantsHtml ? redirect('/subscribe/error/') : json(429, { ok: false, error: 'rate_limited', message: MESSAGES.rate_limited }, { 'Retry-After': String(rl.retryAfter || 60) }); }

  if (f.honeypot) { log({ rid, event: 'subscribe.honeypot', source: f.source }); return accept(); }

  const provider = providerOf(env);
  if (!isConfigured(env)) { log({ rid, event: 'subscribe.not_configured', provider }); return reject(503, 'not_configured'); }
  if (!env.LOG_HASH_SECRET) log({ rid, event: 'subscribe.config_warning', message: 'LOG_HASH_SECRET unset; log hashes are unkeyed' });

  const emailHash = (await hmacHex(env.LOG_HASH_SECRET || 'fpi-unkeyed-set-LOG_HASH_SECRET', f.email)).slice(0, 16);
  const tags = tagIdsFor(env, f.interest);
  const outcome = { rid, event: 'subscribe.result', provider, source: f.source, interest: f.interest, page: f.page, emailHash, attribution: f.attribution, tags_requested: tags.length };
  const deadline = Date.now() + TOTAL_BUDGET_MS;

  try {
    if (provider === 'v3-form') {
      const kit = deps.kitV3 || kitV3Client(env, deps.fetch, deadline);
      // 1. Optional suppression lookup (needs the V3 API secret). Without it, Kit's own form rules apply.
      if (kit.canLookup) {
        const found = await kit.findByEmail(f.email);
        if (found.status === 429) throw fail('provider_rate_limited', 429);
        if (found.status === 401) throw fail('provider_auth', 401);
        if (found.status !== 200 || !shape(found, 'subscribers') || !Array.isArray(found.data.subscribers)) throw fail('provider_error', found.status);
        const existing = found.data.subscribers.find(s => (s.email_address || '').toLowerCase() === f.email) || null;
        if (existing && SUPPRESSED.has(String(existing.state))) {
          outcome.internal_state = 'suppressed'; outcome.provider_state = existing.state; log(outcome);
          return accept();   // identical public response; nothing written
        }
      } else {
        outcome.lookup = 'skipped (KIT_V3_API_SECRET not set)';
      }
      // 2. Form subscribe: preserves the existing custom fields (source, signup_page) and the form's own confirmation rules.
      const fields = { source: f.source, signup_page: f.page };
      if (env.KIT_V3_INTEREST_FIELD) fields[env.KIT_V3_INTEREST_FIELD] = f.interest;
      const r = await kit.formSubscribe(f.email, fields, tags);
      if (r.status === 429) throw fail('provider_rate_limited', 429);
      if (r.status === 401 || r.status === 403) throw fail('provider_auth', r.status);
      if (r.status !== 200 || !shape(r, 'subscription')) throw fail('provider_error', r.status);
      outcome.provider_state = r.data.subscription.state || 'unknown';
      outcome.internal_state = outcome.provider_state === 'inactive' ? 'pending' : 'accepted';
      // Tags and the optional interest field ride on the same accepted call, so what was sent is what was recorded.
      const cap = interestCapture(env, f.interest, tags);
      outcome.interest_recorded = cap.recorded; outcome.interest_via = cap.via;
      if (!cap.recorded) outcome.interest_note = `no Kit mapping for interest "${f.interest}" (${TAG_ENV[f.interest]} or KIT_V3_INTEREST_FIELD); interest kept in this log only`;
      log(outcome);
      return accept();
    }

    // ---------------------------------------------------------------- v4 (opt-in)
    const kit = deps.kit || kitClient(env, deps.fetch, deadline);
    const found = await kit.findByEmail(f.email);
    if (found.status === 429) throw fail('provider_rate_limited', 429);
    if (found.status === 401) throw fail('provider_auth', 401);
    if (found.status !== 200 || !shape(found, 'subscribers') || !Array.isArray(found.data.subscribers)) throw fail('provider_error', found.status);
    const existing = found.data.subscribers[0] || null;
    if (existing && SUPPRESSED.has(existing.state)) { outcome.internal_state = 'suppressed'; outcome.provider_state = existing.state; log(outcome); return accept(); }
    const up = await kit.upsert(f.email);
    if (up.status === 429) throw fail('provider_rate_limited', 429);
    if (![200, 201, 202].includes(up.status) || !shape(up, 'subscriber')) throw fail('provider_error', up.status);
    const created = up.status === 201 || up.status === 202;
    const referrer = [...allowedOrigins(env)][0] + f.page + (Object.keys(f.attribution).length ? '?' + new URLSearchParams(f.attribution).toString() : '');
    const skipForm = env.KIT_SKIP_FORM_FOR_INACTIVE === '1' && existing && existing.state === 'inactive';
    const added = skipForm ? { status: 200, data: { subscriber: existing } } : await kit.addToForm(env.KIT_FORM_ID, f.email, referrer);
    if (added.status === 429) throw fail('provider_rate_limited', 429);
    if (![200, 201].includes(added.status) || !shape(added, 'subscriber')) throw fail('provider_error', added.status);
    const state = added.data.subscriber.state || (existing && existing.state) || 'unknown';
    outcome.internal_state = created ? (state === 'inactive' ? 'pending' : 'accepted') : (added.status === 200 ? 'deduplicated' : 'accepted');
    outcome.provider_state = state;
    // The signup is accepted from here on. Tagging is optional and must never turn it into a failure.
    outcome.tags_ok = true;
    const applied = [];
    for (const id of tags) {
      try {
        const r = await kit.tag(id, f.email);
        if (![200, 201].includes(r.status)) { outcome.tags_ok = false; outcome.tag_failure = { id, status: r.status }; } else applied.push(id);
      } catch (err) {
        outcome.tags_ok = false; outcome.tag_failure = { id, code: err && err.name === 'AbortError' ? 'provider_timeout' : (err.code || 'network') };
        break;
      }
    }
    const cap4 = interestCapture(env, f.interest, tags, applied);
    outcome.interest_recorded = cap4.recorded; outcome.interest_via = cap4.via;
    if (!outcome.tags_ok) log({ ...outcome, event: 'subscribe.partial', note: 'signup accepted; interest tag not saved, reconcile from Kit form attribution' });
    else log(outcome);
    return accept();
  } catch (err) {
    const code = (err && err.name === 'AbortError') ? 'provider_timeout' : (typeof err.code === 'string' ? err.code : 'provider_error');
    log({ ...outcome, event: 'subscribe.provider_failure', code, status: err.status, message: String(err.message).slice(0, 120) });
    return wantsHtml ? redirect('/subscribe/error/') : json(503, { ok: false, error: 'provider_unavailable', message: MESSAGES.provider_unavailable }, { 'Retry-After': '60' });
  }
}
