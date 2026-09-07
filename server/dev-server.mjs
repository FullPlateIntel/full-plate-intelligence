// Local API server for tests and for VPS-style hosting: POST /api/subscribe only.
// /__logs exists only when ENABLE_DEBUG_ENDPOINTS=1 (tests); never set that in production.
import http from 'node:http';
import { makeNodeHandler } from './adapters/node-http.mjs';
const env = { ...process.env };
const logs = [];
const handler = makeNodeHandler(env, { log: (o) => { logs.push(o); if (process.env.LOG_STDOUT) console.log(JSON.stringify(o)); } });
const server = http.createServer(async (req, res) => {
  if (req.url === '/__logs' && process.env.ENABLE_DEBUG_ENDPOINTS === '1') { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(logs.splice(0))); return; }
  if (req.url.startsWith('/api/subscribe')) return handler(req, res);
  res.statusCode = 404; res.end('not found');
});
server.listen(Number(process.env.PORT || 8780), '127.0.0.1', () => console.log('api on', server.address().port));
