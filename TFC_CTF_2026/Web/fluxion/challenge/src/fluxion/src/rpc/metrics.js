'use strict';


const world = require('../world');
const { summarize, timeline } = require('../lib/metrics');
const { clampInt } = require('../lib/validate');

const handlers = {
  
  runMetrics: () => ({ metrics: summarize([...world.runs.values()]) }),

  
  runTimeline: (p) => ({ buckets: timeline([...world.runs.values()], clampInt(p && p.buckets, 4, 48, 12)) }),

  
  statusRollup: () => {
    const byStatus = {};
    for (const r of world.runs.values()) byStatus[r.status] = (byStatus[r.status] || 0) + 1;
    return { byStatus };
  },
};

module.exports = { handlers };
