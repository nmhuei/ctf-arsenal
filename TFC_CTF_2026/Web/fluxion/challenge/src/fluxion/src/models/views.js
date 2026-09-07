'use strict';






const { safeAssign, pickTunable } = require('../config/merge');

const views = new Map(); 
const VIEW_KEYS = ['columns', 'filter', 'density'];
const FILTER_KEYS = ['workflowName', 'status', 'runId'];

function sanitizeFilter(f) {
  if (!f || typeof f !== 'object') return {};
  const out = {};
  for (const k of FILTER_KEYS) {
    if (Object.prototype.hasOwnProperty.call(f, k)) out[k] = String(f[k]);
  }
  return out;
}

function save(name, body) {
  const key = String(name || '').trim();
  if (!key) return { ok: false, error: 'view name required' };
  const patch = pickTunable(body || {}, VIEW_KEYS);
  const rec = views.get(key) || { name: key, columns: ['run', 'workflow', 'status'], filter: {}, createdAt: Date.now() };
  if (Array.isArray(patch.columns)) rec.columns = patch.columns.map(String).slice(0, 12);
  if (typeof patch.density === 'string') rec.density = patch.density;
  if (patch.filter) rec.filter = sanitizeFilter(patch.filter);
  
  safeAssign(rec, {});
  views.set(key, rec);
  return { ok: true, view: { ...rec } };
}

function get(name) { const v = views.get(String(name)); return v ? { ...v } : null; }
function remove(name) { return { ok: views.delete(String(name)) }; }
function list() { return [...views.values()].map((v) => ({ ...v })); }

function seedViews() {
  save('failures', { columns: ['run', 'workflow', 'status'], filter: { status: 'failed' } });
  save('awaiting', { columns: ['run', 'workflow', 'status'], filter: { status: 'awaiting' } });
}

module.exports = { save, get, remove, list, seedViews };
