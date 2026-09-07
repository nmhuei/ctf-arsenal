'use strict';






const { safeAssign } = require('../config/merge');

const policies = new Map(); 
const KEYS = ['target', 'ackWindowMins', 'description', 'enabled'];

function base(workflowName) {
  return { workflowName, target: 0.99, ackWindowMins: 30, description: '', enabled: true, updatedAt: Date.now() };
}

function coerce(patch) {
  const out = {};
  if (!patch || typeof patch !== 'object') return out;
  for (const k of KEYS) {
    if (!Object.prototype.hasOwnProperty.call(patch, k)) continue;
    const v = patch[k];
    if (v && typeof v === 'object') continue; 
    if (k === 'target') out.target = Math.min(1, Math.max(0, Number(v) || 0));
    else if (k === 'ackWindowMins') out.ackWindowMins = Math.max(1, Number(v) || 30);
    else if (k === 'enabled') out.enabled = Boolean(v);
    else out[k] = String(v).slice(0, 200);
  }
  return out;
}

function get(workflowName) {
  const key = String(workflowName || '');
  if (!policies.has(key)) policies.set(key, base(key));
  return { ...policies.get(key) };
}

function set(workflowName, patch) {
  const key = String(workflowName || '');
  const pol = policies.get(key) || base(key);
  safeAssign(pol, coerce(patch));
  pol.updatedAt = Date.now();
  policies.set(key, pol);
  return { ok: true, policy: { ...pol } };
}

function list() { return [...policies.values()].map((p) => ({ ...p })); }

function seedSlaPolicies() {
  set('nightly-report-export', { target: 0.995, ackWindowMins: 15, description: 'nightly export SLO' });
  set('ingest-csv-batch', { target: 0.95, ackWindowMins: 60 });
}

module.exports = { get, set, list, seedSlaPolicies };
