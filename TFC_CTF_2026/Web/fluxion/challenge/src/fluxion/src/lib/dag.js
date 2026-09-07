'use strict';







function adjacency(nodes, edges) {
  const adj = new Map();
  for (const n of nodes) adj.set(n, []);
  for (const [from, to] of edges) {
    if (!adj.has(from)) adj.set(from, []);
    if (!adj.has(to)) adj.set(to, []);
    adj.get(from).push(to);
  }
  return adj;
}


function topoSort(nodes, edges) {
  const adj = adjacency(nodes, edges);
  const indeg = new Map([...adj.keys()].map((n) => [n, 0]));
  for (const [, tos] of adj) for (const to of tos) indeg.set(to, (indeg.get(to) || 0) + 1);
  const queue = [...indeg.entries()].filter(([, d]) => d === 0).map(([n]) => n);
  const order = [];
  while (queue.length) {
    const n = queue.shift();
    order.push(n);
    for (const to of adj.get(n) || []) {
      indeg.set(to, indeg.get(to) - 1);
      if (indeg.get(to) === 0) queue.push(to);
    }
  }
  return { order, cyclic: order.length !== adj.size };
}


function hasCycle(nodes, edges) {
  return topoSort(nodes, edges).cyclic;
}


function criticalPathDepth(nodes, edges) {
  const { order, cyclic } = topoSort(nodes, edges);
  if (cyclic) return -1;
  const adj = adjacency(nodes, edges);
  const depth = new Map(order.map((n) => [n, 1]));
  for (const n of order) {
    for (const to of adj.get(n) || []) {
      depth.set(to, Math.max(depth.get(to) || 1, depth.get(n) + 1));
    }
  }
  return Math.max(0, ...depth.values());
}


function levels(nodes, edges) {
  const { order, cyclic } = topoSort(nodes, edges);
  if (cyclic) return {};
  const adj = adjacency(nodes, edges);
  const lvl = new Map(order.map((n) => [n, 0]));
  for (const n of order) {
    for (const to of adj.get(n) || []) lvl.set(to, Math.max(lvl.get(to) || 0, lvl.get(n) + 1));
  }
  return Object.fromEntries(lvl);
}

module.exports = { adjacency, topoSort, hasCycle, criticalPathDepth, levels };
