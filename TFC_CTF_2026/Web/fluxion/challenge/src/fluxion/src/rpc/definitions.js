'use strict';



const defs = require('../models/definitions');
const activities = require('../models/activities');
const audit = require('../models/audit');

const handlers = {
  
  listActivities: () => ({ activities: activities.list() }),

  
  listDefinitions: () => ({ definitions: defs.listNames() }),

  
  getDefinition: (p) => {
    const d = defs.get(p && p.name, p && p.version);
    return d ? { name: String(p.name), definition: d } : { error: 'no such definition' };
  },

  
  saveDefinition: (p) => {
    const res = defs.save(p && p.name, (p && p.body) || {});
    if (res.ok) audit.record('definition.save', res.name, `v${res.version}`);
    return res;
  },

  
  getTopology: (p) => {
    const t = defs.topology(p && p.name, p && p.version);
    return t || { error: 'no such definition' };
  },
};

module.exports = { handlers };
