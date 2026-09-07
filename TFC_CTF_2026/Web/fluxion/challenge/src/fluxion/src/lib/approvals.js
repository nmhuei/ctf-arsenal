'use strict';



const crypto = require('crypto');

const APPROVAL_KEY = crypto.randomBytes(32);
const amac = (raw) => crypto.createHmac('sha256', APPROVAL_KEY).update(raw).digest('hex');


const BLOCKED_ACTS = new Set(['resume', 'approve', 'execute', 'provision']);



function signPreviewGrant(doc) {
  const raw = typeof doc === 'string' ? doc : JSON.stringify(doc || {});
  if (raw.length > 512) return { error: 'grant document too large' };
  const m = raw.match(/"act"\s*:\s*"([^"]*)"/);   
  const act = m ? m[1] : '';
  if (BLOCKED_ACTS.has(act)) return { error: 'only read-only preview grants may be self-signed' };
  return { grant: Buffer.from(raw).toString('base64url') + '.' + amac(raw) };
}


function verifyGrant(tok) {
  const parts = String(tok || '').split('.');
  if (parts.length !== 2) return null;
  const raw = Buffer.from(parts[0], 'base64url').toString('utf8');
  let ok = false;
  try { ok = crypto.timingSafeEqual(Buffer.from(amac(raw)), Buffer.from(String(parts[1]))); }
  catch { return null; }
  if (!ok) return null;
  try { return JSON.parse(raw); } catch { return null; }
}

module.exports = { signPreviewGrant, verifyGrant };
