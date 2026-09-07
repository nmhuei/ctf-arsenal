'use strict';






const queries = new Map(); 
const FIELDS = ['runId', 'workflowName', 'status'];

function sanitizeFilter(f) {
  const out = {};
  if (!f || typeof f !== 'object') return out;
  for (const k of FIELDS) {
    if (Object.prototype.hasOwnProperty.call(f, k)) out[k] = String(f[k]);
  }
  return out;
}

function save(name, body) {
  const key = String((name || '')).trim();
  if (!key) return { ok: false, error: 'query name required' };
  const rec = {
    name: key,
    filter: sanitizeFilter(body && body.filter),
    sort: FIELDS.includes(body && body.sort) ? body.sort : 'startedAt',
    limit: Math.min(500, Math.max(1, Number(body && body.limit) || 100)),
    createdAt: Date.now(),
  };
  queries.set(key, rec);
  return { ok: true, query: { ...rec } };
}

function get(name) { const q = queries.get(String(name)); return q ? { ...q } : null; }
function remove(name) { return { ok: queries.delete(String(name)) }; }
function list() { return [...queries.values()].map((q) => ({ ...q })); }

function seedSavedQueries() {
  save('all-failures', { filter: { status: 'failed' } });
  save('awaiting-approval', { filter: { status: 'awaiting-approval' } });
}

module.exports = { save, get, remove, list, seedSavedQueries };
