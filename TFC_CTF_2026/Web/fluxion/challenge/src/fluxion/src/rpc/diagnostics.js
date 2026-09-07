'use strict';






const world = require('../world');



const ENV_ALLOW = ['NODE_ENV', 'TZ', 'LANG', 'HOSTNAME', 'PORT'];

function envProjection() {
  const out = {};
  for (const k of ENV_ALLOW) {
    if (Object.prototype.hasOwnProperty.call(process.env, k)) out[k] = String(process.env[k]);
  }
  return out;
}

const handlers = {
  
  
  describeHooks: (p) => {
    const runId = p && p.runId ? String(p.runId) : null;
    const rows = [...world.hooks.values()]
      .filter((h) => !runId || h.runId === runId)
      .map((h) => ({ id: h.id, runId: h.runId, isWebhook: h.isWebhook, resumed: h.resumed }));
    return { hooks: rows };
  },

  
  storeHealth: () => {
    const runs = [...world.runs.values()];
    return {
      runs: runs.length,
      hooks: world.hooks.size,
      withOutput: runs.filter((r) => r.output !== null).length,
      pending: runs.filter((r) => String(r.status).startsWith('awaiting')).length,
    };
  },

  
  getRuntimeInfo: () => {
    const mem = process.memoryUsage();
    return {
      engine: 'fluxion',
      version: '1.4.0',
      node: process.version,
      platform: process.platform,
      arch: process.arch,
      pid: process.pid,
      uptime: process.uptime(),
      rssMb: Math.round(mem.rss / 1048576),
      heapUsedMb: Math.round(mem.heapUsed / 1048576),
      env: envProjection(),
    };
  },
};

module.exports = { handlers };
