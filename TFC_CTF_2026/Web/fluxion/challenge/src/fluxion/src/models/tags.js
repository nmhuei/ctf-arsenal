'use strict';







const { safeAssign } = require('../config/merge');

const tagsByRun = new Map(); 
const MAX_LABELS = 32;

function flatten(patch) {
  const out = {};
  if (!patch || typeof patch !== 'object') return out;
  let n = 0;
  for (const k of Object.keys(patch)) {
    if (n >= MAX_LABELS) break;
    const v = patch[k];
    if (v && typeof v === 'object') continue; 
    out[String(k)] = String(v);
    n++;
  }
  return out;
}

function set(runId, patch) {
  const id = String(runId || '');
  if (!id) return { ok: false, error: 'runId required' };
  const doc = tagsByRun.get(id) || {};
  safeAssign(doc, flatten(patch));
  tagsByRun.set(id, doc);
  return { ok: true, runId: id, labels: { ...doc } };
}

function get(runId) { return { ...(tagsByRun.get(String(runId)) || {}) }; }

function unset(runId, key) {
  const doc = tagsByRun.get(String(runId));
  if (doc) delete doc[String(key)];
  return { ok: true, runId: String(runId), labels: { ...(doc || {}) } };
}

function search(key, value) {
  const out = [];
  for (const [runId, doc] of tagsByRun) {
    if (Object.prototype.hasOwnProperty.call(doc, key) && String(doc[key]) === String(value)) {
      out.push({ runId, labels: { ...doc } });
    }
  }
  return out;
}

module.exports = { set, get, unset, search };
