/** Node.js http adapter: wraps handleSubscribe for a plain Node server (used by the local dev/test server
 *  and usable behind nginx/PM2 if the site is hosted on a VPS). */
import { handleSubscribe, makeRateLimiter, memoryStore } from '../subscribe-core.mjs';

export function toWebRequest(req, body) {
  const proto = req.headers['x-forwarded-proto'] || 'http';
  const host = req.headers['x-forwarded-host'] || req.headers.host || 'localhost';
  const headers = new Headers();
  for (const [k, v] of Object.entries(req.headers)) if (typeof v === 'string' && k !== 'x-fpi-remote-addr') headers.set(k, v);
  headers.set('x-fpi-remote-addr', (req.socket && req.socket.remoteAddress) || 'unknown');   // never client-supplied
  return new Request(`${proto}://${host}${req.url}`, { method: req.method, headers, body: ['GET', 'HEAD'].includes(req.method) ? undefined : body });
}
export async function sendWebResponse(res, webRes) {
  res.statusCode = webRes.status;
  webRes.headers.forEach((v, k) => res.setHeader(k, v));
  const buf = Buffer.from(await webRes.arrayBuffer());
  res.end(buf);
}
export function makeNodeHandler(env, deps = {}) {
  const rateLimit = deps.rateLimit || makeRateLimiter(memoryStore());
  return async function (req, res) {
    const chunks = []; for await (const c of req) { chunks.push(c); if (chunks.reduce((n, b) => n + b.length, 0) > 8192) break; }
    const webReq = toWebRequest(req, Buffer.concat(chunks));
    const webRes = await handleSubscribe(webReq, env, { ...deps, rateLimit });
    await sendWebResponse(res, webRes);
  };
}
