// Netlify Functions 2.0 entry point for POST /api/subscribe.
// Lives at netlify/functions/subscribe.mjs; the core is bundled from ../../server/subscribe-core.mjs by Netlify's
// esbuild bundler (netlify.toml [functions] node_bundler = "esbuild"). Environment variables come from process.env
// (Netlify docs), the client address from Netlify's trusted context.ip, and rate limiting from the function config.
import { handleSubscribe, makeRateLimiter, memoryStore } from '../../server/subscribe-core.mjs';

const limiter = makeRateLimiter(memoryStore());   // per-instance best effort; the durable control is config.rateLimit below

export default async (request, context) => {
  return handleSubscribe(request, process.env, { rateLimit: limiter, clientIp: context && context.ip ? String(context.ip) : undefined });
};

export const config = {
  path: '/api/subscribe',
  method: ['POST'],
  // Netlify-native rate limiting (verify it is active on the account's plan during the preview check).
  rateLimit: { windowLimit: 10, windowSize: 60, aggregateBy: ['ip'], action: 'rate_limit' },
};
