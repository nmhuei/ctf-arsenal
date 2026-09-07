'use strict';






const retention = require('../models/retention');
const audit = require('../models/audit');
const world = require('../world');

const handlers = {
  getRetentionPolicy: (p) => ({ policy: retention.get((p && p.workflowName) || '') }),

  listRetentionPolicies: () => ({ policies: retention.list() }),

  
  updateRetentionPolicy: (p) => {
    const res = retention.update((p && p.workflowName) || '', (p && p.patch) || {});
    if (res.ok) audit.record('retention.update', res.policy.workflowName, `runs=${res.policy.runs.days}d`);
    return res;
  },

  
  projectRetentionSweep: (p) => {
    const runs = [...world.runs.values()].map(world.publicRun);
    return retention.projectSweep((p && p.workflowName) || '', runs);
  },
};

module.exports = { handlers };
