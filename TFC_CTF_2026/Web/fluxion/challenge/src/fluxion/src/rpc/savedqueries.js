'use strict';



const sq = require('../models/savedqueries');
const world = require('../world');

const FIELDS = ['runId', 'workflowName', 'status'];

const handlers = {
  saveQuery: (p) => sq.save(p && p.name, (p && p.query) || {}),
  getQuery: (p) => { const q = sq.get(p && p.name); return q ? { query: q } : { error: 'no such query' }; },
  listQueries: () => ({ queries: sq.list() }),
  deleteQuery: (p) => sq.remove(p && p.name),

  
  runQuery: (p) => {
    const q = sq.get(p && p.name);
    if (!q) return { error: 'no such query' };
    let rows = [...world.runs.values()].map(world.publicRun).filter((r) =>
      Object.entries(q.filter).every(([k, v]) => FIELDS.includes(k) && String(r[k] ?? '').includes(String(v))));
    rows = rows.sort((a, b) => String(a[q.sort]).localeCompare(String(b[q.sort]))).slice(0, q.limit);
    return { name: q.name, total: rows.length, results: rows };
  },
};

module.exports = { handlers };
