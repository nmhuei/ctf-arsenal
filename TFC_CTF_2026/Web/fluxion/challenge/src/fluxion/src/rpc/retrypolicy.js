'use strict';


const rp = require('../models/retrypolicies');
const { schedule } = require('../lib/backoff');

const handlers = {
  getRetryPolicy: (p) => ({ policy: rp.get((p && p.workflowName) || '') }),
  listRetryPolicies: () => ({ policies: rp.list() }),
  setRetryPolicy: (p) => rp.set((p && p.workflowName) || '', (p && p.patch) || {}),

  
  previewBackoff: (p) => {
    const policy = (p && p.policy) || rp.get((p && p.workflowName) || '');
    return { schedule: schedule(policy) };
  },
};

module.exports = { handlers };
