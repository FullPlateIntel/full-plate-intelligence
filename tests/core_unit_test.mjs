// Dependency-injected checks of server/subscribe-core.mjs: interest recording across all six interests, invalid
// tag values, the SIGNUPS_DISABLED emergency stop, and log hygiene. No network, no mock server needed.
// Run: node tests/core_unit_test.mjs
import { handleSubscribe, tagIdFor, tagIdsFor, interestCapture, signupsDisabled } from '../server/subscribe-core.mjs';

const results = [];
const check = (name, ok, ev) => { results.push({ name, ok, ev }); console.log(`[${ok ? 'PASS' : 'FAIL'}] core-unit: ${name}${ok ? '' : ' -- ' + JSON.stringify(ev)}`); };
const BASE = { SITE_ORIGIN: 'https://fullplateintel.com', KIT_PROVIDER: 'v3-form', KIT_V3_API_KEY: 'k', KIT_FORM_ID: '12345', LOG_HASH_SECRET: 's' };
const req = (body, ct = 'application/json') => new Request('https://fullplateintel.com/api/subscribe', { method: 'POST', headers: { 'Content-Type': ct, Origin: 'https://fullplateintel.com' }, body: typeof body === 'string' ? body : JSON.stringify(body) });

/** Fake Kit V3 that records the form-subscribe payload and answers like the real API. */
function fakeV3(state = 'inactive') {
  const sent = [];
  return { sent, kit: { canLookup: false, formSubscribe: async (email, fields, tags) => { sent.push({ email, fields, tags }); return { status: 200, data: { subscription: { id: 1, state } } }; } } };
}
async function run(env, body, kitState) {
  const logs = []; const f = fakeV3(kitState);
  const res = await handleSubscribe(req(body), env, { kitV3: f.kit, log: (o) => logs.push(o) });
  const result = logs.find(l => l.event === 'subscribe.result') || logs[logs.length - 1];
  return { status: res.status, json: res.headers.get('content-type')?.includes('json') ? await res.json() : null, location: res.headers.get('location'), sent: f.sent, logs, result };
}
const T = { KIT_TAG_NEWSLETTER: '1', KIT_TAG_SHOW: '5', KIT_TAG_INDEX: '4', KIT_TAG_BENCHMARK: '6', KIT_TAG_BENCHMARK_CALCULATOR: '2', KIT_TAG_BENCHMARK_REPORT: '3' };

// ---- helpers
check('tagIdFor: unset -> null; numeric string -> number; whitespace tolerated; non-numeric ignored',
  tagIdFor({}, 'show') === null && tagIdFor({ KIT_TAG_SHOW: '5' }, 'show') === 5 && tagIdFor({ KIT_TAG_SHOW: ' 7 ' }, 'show') === 7 && tagIdFor({ KIT_TAG_SHOW: 'abc' }, 'show') === null && tagIdFor({ KIT_TAG_SHOW: '12abc' }, 'show') === null);
check('tagIdsFor: newsletter tag + interest tag, deduplicated, invalid dropped',
  JSON.stringify(tagIdsFor({ ...T }, 'benchmark-report')) === '[1,3]' && JSON.stringify(tagIdsFor({ KIT_TAG_NEWSLETTER: '1', KIT_TAG_SHOW: '1' }, 'show')) === '[1]' && JSON.stringify(tagIdsFor({ KIT_TAG_NEWSLETTER: 'x', KIT_TAG_SHOW: '5' }, 'show')) === '[5]');
check('signupsDisabled: 1/true/yes/on enable it; unset/0/false do not',
  ['1', 'true', 'YES', 'on'].every(v => signupsDisabled({ SIGNUPS_DISABLED: v })) && ['', '0', 'false', undefined].every(v => !signupsDisabled({ SIGNUPS_DISABLED: v })));

// ---- v3 interest recording: every interest, no mappings
let r;
for (const interest of ['show', 'index', 'benchmark', 'benchmark-calculator', 'benchmark-report']) {
  r = await run({ ...BASE }, { email: 'a@example.com', source: 'benchmark-page', interest });
  check(`no mapping (${interest}): 200 accepted, no tags/field sent, interest_recorded=false, via=none, note names the missing variable`,
    r.status === 200 && r.json.ok === true && r.sent[0].tags.length === 0 && !('interest' in r.sent[0].fields) && r.result.interest_recorded === false && r.result.interest_via === 'none' && /KIT_TAG_/.test(r.result.interest_note || ''), r.result);
}
r = await run({ ...BASE }, { email: 'a@example.com', source: 'homepage-hero', interest: 'newsletter' });
check('newsletter interest, no tags at all: accepted form membership counts, interest_recorded=true via=form', r.status === 200 && r.result.interest_recorded === true && r.result.interest_via === 'form', r.result);

// ---- newsletter-only tag while a product interest is requested (the RC3 defect)
r = await run({ ...BASE, KIT_TAG_NEWSLETTER: '1' }, { email: 'a@example.com', source: 'benchmark-page', interest: 'benchmark-report' });
check('newsletter tag only + benchmark-report requested: tags [1] sent, interest_recorded=false (generic tag never counts)', JSON.stringify(r.sent[0].tags) === '[1]' && r.result.interest_recorded === false && r.result.interest_via === 'none', r.result);
r = await run({ ...BASE, KIT_TAG_NEWSLETTER: '1', KIT_TAG_BENCHMARK: '6' }, { email: 'a@example.com', source: 'benchmark-page', interest: 'benchmark-calculator' });
check('generic KIT_TAG_BENCHMARK does not satisfy benchmark-calculator: tags [1] only, interest_recorded=false', JSON.stringify(r.sent[0].tags) === '[1]' && r.result.interest_recorded === false, r.result);
r = await run({ ...BASE, KIT_TAG_BENCHMARK: '6' }, { email: 'a@example.com', source: 'benchmark-page', interest: 'benchmark-report' });
check('generic KIT_TAG_BENCHMARK does not satisfy benchmark-report: no tags, interest_recorded=false', r.sent[0].tags.length === 0 && r.result.interest_recorded === false, r.result);

// ---- matching product tags, each interest to its own variable
for (const [interest, id] of [['show', 5], ['index', 4], ['benchmark', 6], ['benchmark-calculator', 2], ['benchmark-report', 3]]) {
  r = await run({ ...BASE, ...T }, { email: 'a@example.com', source: 'benchmark-page', interest });
  check(`matching tag (${interest}): tags [1,${id}] sent, interest_recorded=true via=tag`, JSON.stringify(r.sent[0].tags) === `[1,${id}]` && r.result.interest_recorded === true && r.result.interest_via === 'tag', { tags: r.sent[0].tags, result: r.result });
}
r = await run({ ...BASE, KIT_TAG_BENCHMARK_CALCULATOR: '2', KIT_TAG_BENCHMARK_REPORT: '3' }, { email: 'a@example.com', source: 'benchmark-page', interest: 'benchmark-calculator' });
const r2 = await run({ ...BASE, KIT_TAG_BENCHMARK_CALCULATOR: '2', KIT_TAG_BENCHMARK_REPORT: '3' }, { email: 'a@example.com', source: 'benchmark-page', interest: 'benchmark-report' });
check('calculator and report are distinct: [2] vs [3], both recorded via their own tag', JSON.stringify(r.sent[0].tags) === '[2]' && JSON.stringify(r2.sent[0].tags) === '[3]' && r.result.interest_recorded && r2.result.interest_recorded, [r.sent[0].tags, r2.sent[0].tags]);

// ---- invalid tag values never break a valid signup
r = await run({ ...BASE, KIT_TAG_NEWSLETTER: 'not-a-number', KIT_TAG_SHOW: '5x' }, { email: 'a@example.com', source: 'show-page', interest: 'show' });
check('invalid tag values (non-numeric): ignored, no tags sent, 200 accepted, interest_recorded=false', r.status === 200 && r.json.ok === true && r.sent[0].tags.length === 0 && r.result.interest_recorded === false, r.result);
r = await run({ ...BASE, KIT_TAG_SHOW: '5' }, { email: 'a@example.com', source: 'show-page', interest: 'show' });
check('invalid newsletter tag absent, valid show tag present: tags [5], recorded via=tag', JSON.stringify(r.sent[0].tags) === '[5]' && r.result.interest_recorded === true, r.result);

// ---- interest custom field
r = await run({ ...BASE, KIT_V3_INTEREST_FIELD: 'interest' }, { email: 'a@example.com', source: 'index-page', interest: 'index' });
check('KIT_V3_INTEREST_FIELD configured, no tags: fields.interest=index sent, interest_recorded=true via=field', r.sent[0].fields.interest === 'index' && r.result.interest_recorded === true && r.result.interest_via === 'field', { fields: r.sent[0].fields, result: r.result });
r = await run({ ...BASE, KIT_V3_INTEREST_FIELD: 'interest', ...T }, { email: 'a@example.com', source: 'index-page', interest: 'index' });
check('field + matching tag: tag reported as the channel ([1,4] sent, via=tag)', JSON.stringify(r.sent[0].tags) === '[1,4]' && r.result.interest_via === 'tag', r.result);
r = await run({ ...BASE, KIT_V3_INTEREST_FIELD: 'interest' }, { email: 'a@example.com', source: 'homepage-hero', interest: 'newsletter' });
check('newsletter with a field configured: field carries "newsletter", recorded via=form', r.sent[0].fields.interest === 'newsletter' && r.result.interest_recorded === true && r.result.interest_via === 'form', r.result);

// ---- fields always carry source and signup_page (existing V3 contract), legacy path alias
r = await run({ ...BASE }, { email: 'a@example.com', source: 'show-page', path: '/show/#show-join' });
check('V3 contract kept: fields.source and fields.signup_page from the legacy path alias', r.sent[0].fields.source === 'show-page' && r.sent[0].fields.signup_page === '/show/', r.sent[0].fields);

// ---- suppressed / failed requests never report a recorded interest
{
  const logs = []; const kit = { canLookup: true, findByEmail: async () => ({ status: 200, data: { subscribers: [{ email_address: 'gone@example.com', state: 'cancelled' }] } }), formSubscribe: async () => { throw new Error('must not be called'); } };
  const res = await handleSubscribe(req({ email: 'gone@example.com', source: 'show-page', interest: 'show' }), { ...BASE, ...T, KIT_V3_API_SECRET: 'sec' }, { kitV3: kit, log: (o) => logs.push(o) });
  const j = await res.json(); const lg = logs.find(l => l.event === 'subscribe.result');
  check('suppressed (cancelled) address: uniform 200 accepted, nothing written, interest_recorded not reported', res.status === 200 && j.status === 'accepted' && lg.internal_state === 'suppressed' && !('interest_recorded' in lg), lg);
}
{
  const logs = []; const kit = { canLookup: false, formSubscribe: async () => ({ status: 500, data: null }) };
  const res = await handleSubscribe(req({ email: 'a@example.com', source: 'show-page', interest: 'show' }), { ...BASE, ...T }, { kitV3: kit, log: (o) => logs.push(o) });
  const j = await res.json(); const lg = logs.find(l => l.event === 'subscribe.provider_failure');
  check('provider failure: 503 provider_unavailable, failure logged, interest_recorded not reported', res.status === 503 && j.error === 'provider_unavailable' && lg && !('interest_recorded' in lg), lg);
}

// ---- SIGNUPS_DISABLED emergency stop
{
  const logs = []; let called = false; const kit = { canLookup: false, formSubscribe: async () => { called = true; return { status: 200, data: { subscription: { state: 'inactive' } } }; } };
  const res = await handleSubscribe(req({ email: 'a@example.com', source: 'homepage-hero' }), { ...BASE, SIGNUPS_DISABLED: '1' }, { kitV3: kit, log: (o) => logs.push(o) });
  const j = await res.json();
  check('SIGNUPS_DISABLED=1, JSON: 503 {ok:false,error:"disabled"} with the unavailable message, no provider call, disabled event logged', res.status === 503 && j.ok === false && j.error === 'disabled' && /temporarily unavailable/.test(j.message) && !called && logs.some(l => l.event === 'subscribe.disabled'), { status: res.status, j, called });
  const res2 = await handleSubscribe(req('email=a%40example.com&source=homepage-hero', 'application/x-www-form-urlencoded'), { ...BASE, SIGNUPS_DISABLED: 'true' }, { kitV3: kit, log: () => {} });
  check('SIGNUPS_DISABLED=true, no-JavaScript form post: 303 to /subscribe/error/ (visible failure, never the thanks page)', res2.status === 303 && res2.headers.get('location') === '/subscribe/error/' && !called, [res2.status, res2.headers.get('location')]);
  const res3 = await handleSubscribe(req({ email: 'a@example.com', source: 'homepage-hero' }), { ...BASE, SIGNUPS_DISABLED: '0' }, { kitV3: kit, log: () => {} });
  check('SIGNUPS_DISABLED=0: signups proceed normally', res3.status === 200 && called);
  const res4 = await handleSubscribe(req({ email: 'a@example.com' }), { ...BASE, KIT_PROVIDER: 'v4', KIT_API_KEY: 'k', SIGNUPS_DISABLED: '1' }, { kit: { findByEmail: async () => { throw new Error('must not be called'); } }, log: () => {} });
  check('switch applies to the V4 provider too', res4.status === 503);
}

// ---- log hygiene: no raw email, no keys, no provider bodies
{
  const logs = []; const f = fakeV3();
  await handleSubscribe(req({ email: 'Person.Name@Example.com', source: 'benchmark-page', interest: 'benchmark-report', attribution: { utm_source: 'linkedin' } }), { ...BASE, ...T, KIT_V3_API_KEY: 'SECRET-KEY-VALUE', KIT_V3_API_SECRET: 'SECRET-SECRET' }, { kitV3: { ...f.kit, canLookup: true, findByEmail: async () => ({ status: 200, data: { subscribers: [], secret_echo: 'SECRET-SECRET' } }) }, log: (o) => logs.push(o) });
  const dump = JSON.stringify(logs);
  check('logs carry a keyed hash, the attribution and the interest outcome, but never the address, the keys or provider bodies', !/example\.com/i.test(dump) && !/SECRET-/.test(dump) && /emailHash/.test(dump) && /"utm_source":"linkedin"/.test(dump) && /"interest_recorded":true/.test(dump), dump.slice(0, 300));
}

const failed = results.filter(x => !x.ok).length;
console.log(`core-unit summary: ${results.length - failed} PASS, ${failed} FAIL`);
process.exit(failed ? 1 : 0);
