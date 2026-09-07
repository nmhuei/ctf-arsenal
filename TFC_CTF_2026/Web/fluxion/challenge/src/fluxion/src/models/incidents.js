'use strict';








const RESERVED_KEYS = new Set(['__proto__', 'prototype', 'constructor']);

const incidents = new Map(); 
let counter = 1000;

function nextId() { return 'inc_' + (++counter); }



function mergeAnnotations(dst, src) {
  if (!src || typeof src !== 'object' || Array.isArray(src)) return dst;
  for (const k of Object.keys(src)) {
    if (RESERVED_KEYS.has(k)) continue;
    const v = src[k];
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      if (!dst[k] || typeof dst[k] !== 'object') dst[k] = {};
      mergeAnnotations(dst[k], v);
    } else {
      dst[k] = v;
    }
  }
  return dst;
}

function view(i) {
  return {
    id: i.id, runId: i.runId, workflowName: i.workflowName, severity: i.severity,
    status: i.status, title: i.title, openedAt: i.openedAt,
    acknowledgedAt: i.acknowledgedAt, resolvedAt: i.resolvedAt,
    annotations: i.annotations,
  };
}

const SEVERITIES = new Set(['sev1', 'sev2', 'sev3', 'sev4']);

function open(body) {
  const id = nextId();
  const inc = {
    id,
    runId: String((body && body.runId) || ''),
    workflowName: String((body && body.workflowName) || 'unknown'),
    severity: SEVERITIES.has(body && body.severity) ? body.severity : 'sev3',
    status: 'open',
    title: String((body && body.title) || 'incident').slice(0, 160),
    openedAt: Date.now(),
    acknowledgedAt: null,
    resolvedAt: null,
    annotations: {},
  };
  incidents.set(id, inc);
  return { ok: true, incident: view(inc) };
}

function acknowledge(id) {
  const i = incidents.get(String(id));
  if (!i) return { ok: false, error: 'no such incident' };
  if (i.status === 'open') { i.status = 'acknowledged'; i.acknowledgedAt = Date.now(); }
  return { ok: true, incident: view(i) };
}

function resolve(id) {
  const i = incidents.get(String(id));
  if (!i) return { ok: false, error: 'no such incident' };
  i.status = 'resolved';
  i.resolvedAt = Date.now();
  return { ok: true, incident: view(i) };
}


function annotate(id, patch) {
  const i = incidents.get(String(id));
  if (!i) return { ok: false, error: 'no such incident' };
  mergeAnnotations(i.annotations, (patch && typeof patch === 'object') ? patch : {});
  return { ok: true, incident: view(i) };
}

function get(id) { const i = incidents.get(String(id)); return i ? view(i) : null; }
function list(filter) {
  const f = filter || {};
  return [...incidents.values()]
    .filter((i) => (!f.status || i.status === f.status) && (!f.severity || i.severity === f.severity))
    .map(view);
}

function seedIncidents() {
  const a = open({ workflowName: 'ingest-csv-batch', severity: 'sev2', title: 'ingest failing on malformed rows' });
  acknowledge(a.incident.id);
  open({ workflowName: 'slack-digest', severity: 'sev4', title: 'digest delivery delayed' });
}

module.exports = { open, acknowledge, resolve, annotate, get, list, seedIncidents };
