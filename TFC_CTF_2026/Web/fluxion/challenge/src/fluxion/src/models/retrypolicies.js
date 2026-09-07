'use strict';






const { safeAssign } = require('../config/merge');
const { schedule } = require('../lib/backoff');

const policies = new Map(); 
const KEYS = ['maxAttempts', 'baseDelayMs', 'factor', 'capMs', 'jitter'];

function base(workflowName) {
  return { workflowName, maxAttempts: 5, baseDelayMs: 500, factor: 2, capMs: 60_000, jitter: 0.2, updatedAt: Date.now() };
}

function coerce(patch) {
  const out = {};
  if (!patch || typeof patch !== 'object') return out;
  for (const k of KEYS) {
    if (Object.prototype.hasOwnProperty.call(patch, k)) {
      const n = Number(patch[k]);
      if (Number.isFinite(n)) out[k] = n;
    }
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
  return { ok: true, policy: { ...pol }, preview: schedule(pol) };
}

function list() { return [...policies.values()].map((p) => ({ ...p })); }

function seedRetryPolicies() {
  set('ingest-csv-batch', { maxAttempts: 8, baseDelayMs: 1000, factor: 2, capMs: 120_000 });
  set('github-deploy-notify', { maxAttempts: 3, baseDelayMs: 250 });
}

module.exports = { get, set, list, seedRetryPolicies };
