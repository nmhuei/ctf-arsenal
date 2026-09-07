'use strict';





const MAX = 1_000;
const entries = [];
let seq = 0;

function record(kind, runId, detail) {
  const e = { seq: ++seq, ts: Date.now(), kind: String(kind), runId: String(runId || ''), detail: String(detail || '').slice(0, 120) };
  entries.push(e);
  if (entries.length > MAX) entries.shift();
  return e;
}

function forRun(runId) {
  return entries.filter((e) => e.runId === String(runId));
}

function recent(n = 50) {
  const k = Math.max(1, Math.min(MAX, Number(n) || 50));
  return entries.slice(-k);
}

module.exports = { record, forRun, recent };
