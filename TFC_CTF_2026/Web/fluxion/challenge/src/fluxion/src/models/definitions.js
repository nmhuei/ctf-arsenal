'use strict';







const activities = require('./activities');
const { topoSort, hasCycle, criticalPathDepth, levels } = require('../lib/dag');

const defs = new Map(); 

function nodesOf(def) { return (def.activities || []).map((a) => a.id); }


function validate(body) {
  const acts = Array.isArray(body && body.activities) ? body.activities : [];
  const edges = Array.isArray(body && body.edges) ? body.edges : [];
  if (!acts.length) return { ok: false, error: 'definition needs at least one activity' };
  for (const a of acts) {
    if (!a || typeof a.id !== 'string') return { ok: false, error: 'each activity needs a string id' };
    if (!activities.exists(a.type)) return { ok: false, error: `unknown activity type: ${a && a.type}` };
  }
  const ids = new Set(acts.map((a) => a.id));
  for (const e of edges) {
    if (!Array.isArray(e) || e.length !== 2) return { ok: false, error: 'edge must be [from,to]' };
    if (!ids.has(e[0]) || !ids.has(e[1])) return { ok: false, error: `edge references unknown node: ${e}` };
  }
  if (hasCycle([...ids], edges)) return { ok: false, error: 'definition graph has a cycle' };
  return { ok: true, activities: acts, edges };
}

function save(name, body) {
  const v = validate(body);
  if (!v.ok) return v;
  const key = String(name);
  if (!defs.has(key)) defs.set(key, { name: key, versions: [] });
  const rec = defs.get(key);
  const version = rec.versions.length + 1;
  rec.versions.push({ version, activities: v.activities, edges: v.edges, createdAt: Date.now() });
  return { ok: true, name: key, version };
}

function get(name, version) {
  const rec = defs.get(String(name));
  if (!rec) return null;
  if (version == null) return rec.versions[rec.versions.length - 1] || null;
  return rec.versions.find((x) => x.version === Number(version)) || null;
}

function listNames() {
  return [...defs.values()].map((r) => ({ name: r.name, versions: r.versions.length }));
}

function topology(name, version) {
  const d = get(name, version);
  if (!d) return null;
  const nodes = d.activities.map((a) => a.id);
  const { order, cyclic } = topoSort(nodes, d.edges);
  return { name: String(name), version: d.version, order, cyclic,
           depth: criticalPathDepth(nodes, d.edges), levels: levels(nodes, d.edges) };
}


function seedDefinitions() {
  save('nightly-report-export', {
    activities: [
      { id: 'query', type: 'db.query' },
      { id: 'render', type: 'render.pdf' },
      { id: 'store', type: 'storage.put' },
      { id: 'notify', type: 'notify.email' },
    ],
    edges: [['query', 'render'], ['render', 'store'], ['store', 'notify']],
  });
  save('invoice-pdf-render', {
    activities: [ { id: 'fetch', type: 'db.query' }, { id: 'pdf', type: 'render.pdf' }, { id: 'put', type: 'storage.put' } ],
    edges: [['fetch', 'pdf'], ['pdf', 'put']],
  });
  save('github-deploy-notify', {
    activities: [ { id: 'wait', type: 'wait.webhook' }, { id: 'slack', type: 'notify.slack' } ],
    edges: [['wait', 'slack']],
  });
  save('admin-provision-approval', {
    activities: [
      { id: 'validate-request', type: 'transform.map' },
      { id: 'reserve-capacity', type: 'http.request' },
      { id: 'notify-reviewers', type: 'notify.slack' },
      { id: 'approval', type: 'approval.human' },
    ],
    edges: [['validate-request', 'reserve-capacity'], ['reserve-capacity', 'notify-reviewers'], ['notify-reviewers', 'approval']],
  });
}

module.exports = { validate, save, get, listNames, topology, seedDefinitions, nodesOf };
