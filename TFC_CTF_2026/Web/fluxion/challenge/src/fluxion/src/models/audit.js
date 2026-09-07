'use strict';






const MAX = 500;
const entries = [];
let seq = 0;

function redact(s) {
  
  return String(s == null ? '' : s)
    .replace(/[A-Za-z0-9_-]{40,}/g, '[trimmed]')
    .slice(0, 160);
}

function record(action, subject, detail) {
  const e = { seq: ++seq, ts: Date.now(), action: String(action), subject: String(subject || ''), detail: redact(detail) };
  entries.push(e);
  if (entries.length > MAX) entries.shift();
  return e;
}

function tail(n = 50) {
  const k = Math.max(1, Math.min(MAX, Number(n) || 50));
  return entries.slice(-k);
}

module.exports = { record, tail };
