// Mock of the Kit API v4 surface used by subscribe-core.mjs. Scenario is chosen per request by the
// email's local part so one server covers every test case:
//   new@…            -> not found; create 201 (state inactive); form 201  => pending_confirmation
//   active@…         -> found active; upsert 200; form 200 (already on form)
//   cancelled@…      -> found cancelled (unsubscribed)                     => suppressed, no writes
//   bounced@… complained@…                                                => suppressed
//   reject@…         -> upsert 422
//   ratelimit@…      -> 429 on first call
//   malformed@…      -> 200 with non-JSON body
//   timeout@…        -> never answers (handler times out)
//   auth@…           -> 401
//   tagerror@ tagtimeout@ tagreset@  -> v4 only: form add succeeds, then the tag call fails (500 / hangs / socket reset)
// V3: GET /v3/subscribers needs api_secret=test-secret; POST /v3/forms/{id}/subscribe needs api_key=test-v3-key
// Every request is recorded in `calls` (GET /__calls returns and clears them).
import http from 'node:http';
const calls = [];
let ids = 1000;
const server = http.createServer(async (req, res) => {
  let body = ''; for await (const c of req) body += c;
  if (req.url === '/__calls') { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(calls.splice(0))); return; }
  const url = new URL(req.url, 'http://x');
  const isV3 = url.pathname.startsWith('/v3/');
  let parsedBody = {}; try { parsedBody = JSON.parse(body || '{}'); } catch {}
  if (!isV3 && req.headers['x-kit-api-key'] !== 'test-key') { res.statusCode = 401; res.end('{"errors":["The access token is invalid"]}'); return; }
  let email = url.searchParams.get('email_address') || parsedBody.email_address || parsedBody.email || '';
  const local = email.split('@')[0];
  calls.push({ method: req.method, path: url.pathname, email, body });
  const sub = (state) => ({ id: ids++, first_name: null, email_address: email, state, created_at: '2026-09-07T00:00:00Z', fields: {} });
  const send = (status, obj, raw) => { res.statusCode = status; res.setHeader('Content-Type', 'application/json'); res.end(raw !== undefined ? raw : JSON.stringify(obj)); };
  if (local === 'timeout') return;                         // never respond
  if (local === 'auth') return send(401, { errors: ['The access token is invalid'] });
  if (local === 'ratelimit') return send(429, { errors: ['Rate limit exceeded'] });
  if (local === 'malformed') return send(200, null, 'this is not json');
  // ---- V3 (api.convertkit.com) surface used by the default v3-form workflow
  if (isV3 && req.method === 'GET' && url.pathname === '/v3/subscribers') {
    if (url.searchParams.get('api_secret') !== 'test-secret') return send(401, { error: 'Authorization Failed', message: 'API Secret not valid' });
    const known = { active: 'active', cancelled: 'cancelled', bounced: 'bounced', complained: 'complained', inactivev3: 'inactive' };
    return send(200, { total_subscribers: known[local] ? 1 : 0, page: 1, total_pages: 1, subscribers: known[local] ? [sub(known[local])] : [] });
  }
  if (isV3 && req.method === 'POST' && /^\/v3\/forms\/\d+\/subscribe$/.test(url.pathname)) {
    if (parsedBody.api_key !== 'test-v3-key') return send(401, { error: 'Authorization Failed', message: 'API Key not valid' });
    if (local === 'reject') return send(422, { error: 'Unprocessable', message: 'Email address is invalid' });
    return send(200, { subscription: { id: ids++, state: local === 'active' ? 'active' : 'inactive', created_at: '2026-09-07T00:00:00Z', source: null, referrer: null,
      subscribable_id: Number(url.pathname.split('/')[3]), subscribable_type: 'form', subscriber: { id: ids++ } }, _received: { fields: parsedBody.fields || null, tags: parsedBody.tags || null } });
  }
  if (req.method === 'GET' && url.pathname === '/v4/subscribers') {
    const known = { active: 'active', cancelled: 'cancelled', bounced: 'bounced', complained: 'complained', reject: 'active' };
    return send(200, { subscribers: known[local] ? [sub(known[local])] : [], pagination: { has_next_page: false } });
  }
  if (req.method === 'POST' && url.pathname === '/v4/subscribers') {
    if (local === 'reject') return send(422, { errors: ['Email address is invalid'] });
    if (local === 'active') return send(200, { subscriber: sub('active') });
    return send(201, { subscriber: sub('inactive') });
  }
  if (req.method === 'POST' && /^\/v4\/forms\/\d+\/subscribers$/.test(url.pathname)) {
    if (local === 'active') return send(200, { subscriber: { ...sub('active'), added_at: '2026-09-07T00:00:00Z' } });
    return send(201, { subscriber: { ...sub('inactive'), added_at: '2026-09-07T00:00:00Z' } });
  }
  if (req.method === 'POST' && /^\/v4\/tags\/\d+\/subscribers$/.test(url.pathname)) {
    if (local === 'tagerror') return send(500, { errors: ['boom'] });
    if (local === 'tagtimeout') return;                     // tag call hangs after a successful form add
    if (local === 'tagreset') { req.socket.destroy(); return; }   // network error on the tag call
    if (url.pathname.includes('/tags/999/')) return send(404, { errors: ['Tag not found'] });
    return send(201, { subscriber: { ...sub('inactive'), tagged_at: '2026-09-07T00:00:00Z' } });
  }
  send(404, { errors: ['not found'] });
});
server.listen(Number(process.env.PORT || 8790), '127.0.0.1', () => console.log('mock kit on', server.address().port));
