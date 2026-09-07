'use strict';








const { topoSort, levels } = require('./dag');


const COST_BY_TYPE = {
  'db.query': 120, 'render.pdf': 340, 'storage.put': 90, 'notify.email': 40,
  'notify.slack': 30, 'wait.webhook': 0, 'http.request': 150, 'transform.map': 25,
  'approval.human': 0,
};

function costOf(activity) {
  return COST_BY_TYPE[activity && activity.type] != null ? COST_BY_TYPE[activity.type] : 100;
}


function simulate(def) {
  const acts = Array.isArray(def && def.activities) ? def.activities : [];
  const edges = Array.isArray(def && def.edges) ? def.edges : [];
  const ids = acts.map((a) => a.id);
  const { order, cyclic } = topoSort(ids, edges);
  if (cyclic) return { ok: false, error: 'definition graph has a cycle' };

  const lvl = levels(ids, edges);
  const costById = {};
  for (const a of acts) costById[a.id] = costOf(a);

  
  const parents = {};
  for (const id of ids) parents[id] = [];
  for (const [from, to] of edges) if (parents[to]) parents[to].push(from);

  const finish = {};
  for (const id of order) {
    const start = parents[id].reduce((mx, p) => Math.max(mx, finish[p] || 0), 0);
    finish[id] = start + (costById[id] || 0);
  }

  const makespan = Object.values(finish).reduce((mx, v) => Math.max(mx, v), 0);
  const schedule = order.map((id) => ({
    id, level: lvl[id] || 0, cost: costById[id] || 0, finishMs: finish[id] || 0,
  }));

  
  let tail = order.reduce((best, id) => (finish[id] > (finish[best] || -1) ? id : best), order[0]);
  const path = [];
  while (tail) {
    path.unshift(tail);
    tail = parents[tail].reduce((best, p) => ((finish[p] || 0) >= (finish[best] || -1) ? p : best), null);
    if (path.includes(tail)) break;
  }

  return { ok: true, nodes: ids.length, waves: Math.max(0, ...Object.values(lvl)) + 1,
           makespanMs: makespan, criticalPath: path, schedule };
}

module.exports = { simulate, costOf };
