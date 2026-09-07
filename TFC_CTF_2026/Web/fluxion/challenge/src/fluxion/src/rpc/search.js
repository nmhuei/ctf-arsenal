'use strict';






const world = require('../world');
const { toCsv } = require('../lib/csv');
const { clampInt } = require('../lib/validate');

const PUBLIC_FIELDS = ['runId', 'workflowName', 'status', 'startedAt'];

function publicRows() { return [...world.runs.values()].map(world.publicRun); }

const handlers = {
  
  queryRuns: (p) => {
    const filter = (p && p.filter) || {};
    const limit = clampInt(p && p.limit, 1, 500, 100);
    const offset = clampInt(p && p.offset, 0, 100000, 0);
    let rows = publicRows().filter((r) =>
      Object.entries(filter).every(([k, v]) =>
        PUBLIC_FIELDS.includes(k) && String(r[k] ?? '').includes(String(v))));
    if (p && p.sort && PUBLIC_FIELDS.includes(p.sort)) {
      rows = rows.sort((a, b) => String(a[p.sort]).localeCompare(String(b[p.sort])));
    }
    return { total: rows.length, results: rows.slice(offset, offset + limit) };
  },

  
  aggregateRuns: (p) => {
    const by = PUBLIC_FIELDS.includes(p && p.groupBy) ? p.groupBy : 'status';
    const buckets = {};
    for (const r of publicRows()) {
      const key = String(r[by] ?? 'unknown');
      buckets[key] = (buckets[key] || 0) + 1;
    }
    return { groupBy: by, buckets };
  },

  
  runManifest: (p) => {
    const r = world.getRun(String((p && p.runId) || ''));
    if (!r) return { error: 'no such run' };
    return { manifest: world.serializeRun(r) };
  },

  
  exportRunsCsv: (p) => {
    const filter = (p && p.filter) || {};
    const rows = publicRows().filter((r) =>
      Object.entries(filter).every(([k, v]) =>
        PUBLIC_FIELDS.includes(k) && String(r[k] ?? '').includes(String(v))));
    return { format: 'csv', rows: rows.length, csv: toCsv(rows, PUBLIC_FIELDS) };
  },
};

module.exports = { handlers };
