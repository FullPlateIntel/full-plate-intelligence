// Exercises the actual Netlify entry point (netlify/functions/subscribe.mjs) in-process, with the same import
// path Netlify's bundler resolves, against the mock Kit server. Run: node tests/netlify_entry_test.mjs
import { readFileSync } from 'node:fs';
for (const line of readFileSync(new URL('./test.env', import.meta.url), 'utf8').split('\n')) {
  const m = line.match(/^([A-Z_0-9]+)=(.*)$/); if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
}
process.env.URL = 'https://fpi-test.netlify.app'; process.env.SITE_NAME = 'fpi-test';
const mod = await import('../netlify/functions/subscribe.mjs');
const handler = mod.default; const config = mod.config;
const results = [];
const check = (name, ok, ev) => { results.push({ name, ok, ev }); console.log(`[${ok ? 'PASS' : 'FAIL'}] netlify-entry: ${name}${ok ? '' : ' -- ' + JSON.stringify(ev)}`); };
const req = (body, extra = {}, ct = 'application/json') => new Request('https://fpi-test.netlify.app/api/subscribe', { method: extra.method || 'POST', headers: { 'Content-Type': ct, Origin: extra.origin === null ? undefined : (extra.origin || 'http://127.0.0.1:8765'), ...(extra.headers || {}) }, body: extra.method === 'GET' ? undefined : (typeof body === 'string' ? body : JSON.stringify(body)) });
const ctx = (ip) => ({ ip });
check('config exports path /api/subscribe, POST only, and Netlify rateLimit', config.path === '/api/subscribe' && config.method.includes('POST') && config.rateLimit && config.rateLimit.aggregateBy.includes('ip'), config);
let r = await handler(req({ email: 'new@example.com', source: 'benchmark-page', interest: 'benchmark-report', page: '/benchmark/' }), ctx('203.0.113.1'));
let j = await r.json();
check('valid signup through the Netlify handler: 200 accepted', r.status === 200 && j.status === 'accepted', j);
r = await handler(req({ email: 'new@example.com' }, { origin: 'https://fpi-test.netlify.app' }), ctx('203.0.113.2'));
check('Origin equal to the Netlify runtime URL is accepted', r.status === 200, r.status);
r = await handler(req({ email: 'new@example.com' }, { origin: 'https://deploy-preview-12--fpi-test.netlify.app' }), ctx('203.0.113.3'));
check('deploy-preview origin rejected unless ALLOW_PREVIEW_ORIGINS=1', r.status === 403, r.status);
process.env.ALLOW_PREVIEW_ORIGINS = '1';
r = await handler(req({ email: 'new@example.com' }, { origin: 'https://deploy-preview-12--fpi-test.netlify.app' }), ctx('203.0.113.4'));
check('deploy-preview origin accepted with ALLOW_PREVIEW_ORIGINS=1', r.status === 200, r.status);
r = await handler(req({ email: 'new@example.com' }, { origin: 'https://evil--fpi-test.netlify.app.attacker.example' }), ctx('203.0.113.5'));
check('look-alike preview origin rejected', r.status === 403, r.status);
delete process.env.ALLOW_PREVIEW_ORIGINS;
const codes = []; for (let i = 0; i < 7; i++) { const rr = await handler(req({ email: `x${i}@example.com` }, { headers: { 'X-Forwarded-For': `198.51.100.${i}` } }), ctx('203.0.113.9')); codes.push(rr.status); }
check('rate limit keyed on context.ip, not on X-Forwarded-For (6th request 429)', codes[5] === 429, codes);
r = await handler(req('email=new%40example.com&source=show-page&page=%2Fshow%2F', {}, 'application/x-www-form-urlencoded'), ctx('203.0.113.10'));
check('form-encoded fallback: 303 to /subscribe/thanks/', r.status === 303 && r.headers.get('location') === '/subscribe/thanks/', [r.status, r.headers.get('location')]);
r = await handler(req(null, { method: 'GET' }), ctx('203.0.113.11'));
check('GET reaching the handler in-process: 405 (config.method is POST-only, so on Netlify a GET is rejected by the platform before the handler; the deployed GET response is a live check, see LAUNCH_RUNBOOK 4.3)', r.status === 405, r.status);
process.env.SIGNUPS_DISABLED = '1';
r = await handler(req({ email: 'new@example.com', source: 'homepage-hero' }), ctx('203.0.113.12')); j = await r.json();
check('SIGNUPS_DISABLED=1 through the Netlify entry: 503 error "disabled" (visible unavailable message), never apparent acceptance', r.status === 503 && j.ok === false && j.error === 'disabled', j);
r = await handler(req('email=new%40example.com&source=show-page', {}, 'application/x-www-form-urlencoded'), ctx('203.0.113.13'));
check('SIGNUPS_DISABLED=1, no-JavaScript form post through the Netlify entry: 303 to /subscribe/error/', r.status === 303 && r.headers.get('location') === '/subscribe/error/', [r.status, r.headers.get('location')]);
delete process.env.SIGNUPS_DISABLED;
r = await handler(req({ email: 'new@example.com', source: 'homepage-hero' }), ctx('203.0.113.14'));
check('switch cleared: signups accepted again (env change needs a redeploy on Netlify; in-process it is immediate)', r.status === 200, r.status);
const failed = results.filter(x => !x.ok).length;
console.log(`netlify-entry summary: ${results.length - failed} PASS, ${failed} FAIL`);
process.exit(failed ? 1 : 0);
