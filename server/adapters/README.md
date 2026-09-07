# Adapters

The production entry point is **`netlify/functions/subscribe.mjs`** (Netlify Functions 2.0; bundled by esbuild
from `server/subscribe-core.mjs`). It uses `process.env`, Netlify's trusted `context.ip`, and the function-level
`config.rateLimit`.

`node-http.mjs` is only used by `server/dev-server.mjs` for local tests (and would serve a plain Node host if one
were ever chosen). Other hosts are out of scope for this release.

## Timeouts

Up to four sequential provider calls in the V4 workflow (one in the V3 form workflow). Each call is capped at
4 s and the whole request at 9 s, inside Netlify's 10 s synchronous function limit and the browser's 12 s bound.
