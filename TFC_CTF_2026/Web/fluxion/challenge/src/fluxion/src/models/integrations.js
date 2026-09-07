'use strict';







const KINDS = new Set(['webhook', 'pushgateway', 'status-mirror', 'pager']);

const integrations = new Map(); 
let counter = 500;

function nextId() { return 'int_' + (++counter); }

function view(x) {
  return {
    id: x.id, name: x.name, kind: x.kind, url: x.url,
    connectionRef: x.connectionRef, health: x.health, lastCheckedAt: x.lastCheckedAt,
    createdAt: x.createdAt,
  };
}

function create(body) {
  const name = String((body && body.name) || '').trim();
  const kind = String((body && body.kind) || '').trim();
  if (!name) return { ok: false, error: 'name required' };
  if (!KINDS.has(kind)) return { ok: false, error: 'unknown integration kind' };
  const id = nextId();
  const x = {
    id, name, kind,
    url: String((body && body.url) || ''),
    connectionRef: String((body && body.connectionRef) || ''),
    health: 'unknown', lastCheckedAt: null, createdAt: Date.now(),
  };
  integrations.set(id, x);
  return { ok: true, integration: view(x) };
}

function get(id) { const x = integrations.get(String(id)); return x ? x : null; }

function setUrl(id, url) {
  const x = integrations.get(String(id));
  if (!x) return { ok: false, error: 'no such integration' };
  x.url = String(url || '');
  x.health = 'unknown';
  return { ok: true, integration: view(x) };
}

function recordHealth(id, health) {
  const x = integrations.get(String(id));
  if (!x) return;
  x.health = health;
  x.lastCheckedAt = Date.now();
}

function list() { return [...integrations.values()].map(view); }

function seedIntegrations() {
  create({ name: 'ops-alert-webhook', kind: 'webhook', url: 'https://hooks.example.com/ops', connectionRef: 'ops-slack' });
  create({ name: 'public-status-mirror', kind: 'status-mirror', url: 'https://status.example.com/ingest' });
  create({ name: 'metrics-push', kind: 'pushgateway', url: 'https://push.example.com/metrics/job/fluxion' });
}

module.exports = { create, get, setUrl, recordHealth, list, view, seedIntegrations };
