'use strict';






const defs = require('../models/definitions');
const { simulate } = require('../lib/dagsim');

const handlers = {
  
  simulateDefinition: (p) => {
    const d = defs.get(p && p.name, p && p.version);
    if (!d) return { error: 'no such definition' };
    return { name: String((p && p.name) || ''), version: d.version, ...simulate(d) };
  },

  
  simulatePlan: (p) => {
    const body = (p && p.definition) || {};
    const v = defs.validate(body);
    if (!v.ok) return { error: v.error };
    return simulate({ activities: v.activities, edges: v.edges });
  },
};

module.exports = { handlers };
