'use strict';








const RESERVED_KEYS = new Set(['__proto__', 'prototype', 'constructor']);
const SECTIONS = ['runs', 'events', 'audit', 'metrics', 'incidents'];

const policies = new Map(); 

function basePolicy(workflowName) {
  return {
    workflowName,
    runs: { days: 30, keepFailed: true },
    events: { days: 14 },
    audit: { days: 90 },
    metrics: { days: 365, rollup: 'daily' },
    incidents: { days: 180 },
    updatedAt: Date.now(),
  };
}


function guardedMerge(dst, src) {
  if (!src || typeof src !== 'object' || Array.isArray(src)) return dst;
  for (const k of Object.keys(src)) {
    if (RESERVED_KEYS.has(k)) continue;
    const v = src[k];
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      if (!dst[k] || typeof dst[k] !== 'object') dst[k] = {};
      guardedMerge(dst[k], v);
    } else {
      dst[k] = v;
    }
  }
  return dst;
}


function pickSections(patch) {
  const out = {};
  if (!patch || typeof patch !== 'object') return out;
  for (const s of SECTIONS) {
    if (Object.prototype.hasOwnProperty.call(patch, s)) out[s] = patch[s];
  }
  return out;
}

function get(workflowName) {
  const key = String(workflowName || '');
  if (!policies.has(key)) policies.set(key, basePolicy(key));
  return policies.get(key);
}

function update(workflowName, patch) {
  const pol = get(workflowName);
  guardedMerge(pol, pickSections(patch));
  pol.updatedAt = Date.now();
  return { ok: true, policy: { ...pol } };
}

function list() { return [...policies.values()].map((p) => ({ ...p })); }


function projectSweep(workflowName, runs) {
  const pol = get(workflowName);
  const cutoff = Date.now() - Number(pol.runs.days) * 86_400_000;
  let candidates = 0;
  for (const r of runs) {
    if (r.workflowName !== workflowName) continue;
    if (r.status === 'failed' && pol.runs.keepFailed) continue;
    if (r.startedAt < cutoff) candidates++;
  }
  return { workflowName, cutoff, candidates, policyDays: pol.runs.days };
}

function seedRetention() {
  get('nightly-report-export');
  get('ingest-csv-batch');
  update('db-nightly-vacuum', { runs: { days: 7 }, events: { days: 3 } });
}

module.exports = { get, update, list, projectSweep, seedRetention };
