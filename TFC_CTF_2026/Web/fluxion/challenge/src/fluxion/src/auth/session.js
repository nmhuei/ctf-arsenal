'use strict';






const crypto = require('crypto');
const { tokenBucket } = require('../lib/ratelimit');


const OPERATOR_TOKEN = process.env.OPERATOR_TOKEN || crypto.randomBytes(24).toString('base64url');
const limit = tokenBucket({ capacity: 20, refillPerSec: 0.5 });

function bearer(req) {
  const h = String(req.headers['authorization'] || '');
  const m = /^Bearer\s+(.+)$/.exec(h);
  return m ? m[1] : null;
}

function requireOperator(req, res, next) {
  if (!limit(req.ip || 'anon')) return res.status(429).json({ error: 'rate limited' });
  const tok = bearer(req);
  if (!tok) return res.status(401).json({ error: 'operator bearer token required' });
  const a = Buffer.from(tok), b = Buffer.from(OPERATOR_TOKEN);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
    return res.status(403).json({ error: 'invalid operator token' });
  }
  next();
}

module.exports = { requireOperator, OPERATOR_TOKEN };
