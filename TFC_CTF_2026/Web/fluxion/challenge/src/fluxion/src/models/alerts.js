'use strict';






const { summarize } = require('../lib/metrics');
const { safeAssign } = require('../config/merge');

const rules = new Map(); 
let seq = 0;

const METRICS = new Set(['failed', 'awaiting', 'completed', 'total', 'p90ms']);
const OPS = { gt: (a, b) => a > b, gte: (a, b) => a >= b, lt: (a, b) => a < b, lte: (a, b) => a <= b };

function create(body) {
  const name = String((body && body.name) || 'rule').slice(0, 64);
  const metric = String((body && body.metric) || '');
  const op = String((body && body.op) || 'gt');
  const threshold = Number((body && body.threshold) || 0);
  if (!METRICS.has(metric)) return { ok: false, error: 'unknown metric' };
  if (!(op in OPS)) return { ok: false, error: 'unknown op' };
  const id = 'alr_' + (++seq).toString(36).padStart(4, '0');
  rules.set(id, { id, name, metric, op, threshold, enabled: true });
  return { ok: true, id };
}

function toggle(id, enabled) {
  const r = rules.get(String(id));
  if (!r) return { ok: false, error: 'no such rule' };
  safeAssign(r, { enabled: !!enabled });
  return { ok: true, rule: { ...r } };
}

function metricValue(name, runs) {
  const s = summarize(runs);
  if (name === 'total') return s.total;
  if (name === 'p90ms') return s.duration.p90;
  return s.byStatus[name] || 0;
}

function evaluate(runs) {
  const out = [];
  for (const r of rules.values()) {
    if (!r.enabled) { out.push({ id: r.id, name: r.name, state: 'disabled' }); continue; }
    const val = metricValue(r.metric, runs);
    const firing = OPS[r.op](val, r.threshold);
    out.push({ id: r.id, name: r.name, metric: r.metric, value: val, threshold: r.threshold, state: firing ? 'firing' : 'ok' });
  }
  return out;
}

function list() { return [...rules.values()].map((r) => ({ ...r })); }

function seedAlerts() {
  create({ name: 'high-failure-rate', metric: 'failed', op: 'gt', threshold: 3 });
  create({ name: 'approval-backlog', metric: 'awaiting', op: 'gte', threshold: 2 });
}

module.exports = { create, toggle, evaluate, list, seedAlerts };
