'use strict';






const sla = require('../models/slapolicies');
const incidents = require('../models/incidents');
const world = require('../world');
const { attainment } = require('../lib/sla');

const handlers = {
  getSlaPolicy: (p) => ({ policy: sla.get((p && p.workflowName) || '') }),
  listSlaPolicies: () => ({ policies: sla.list() }),
  setSlaPolicy: (p) => sla.set((p && p.workflowName) || '', (p && p.patch) || {}),

  
  slaReport: (p) => {
    const wf = String((p && p.workflowName) || '');
    const runs = [...world.runs.values()].map(world.publicRun);
    const policy = sla.get(wf);
    const open = incidents.list({}).filter((i) => i.workflowName === wf && i.status !== 'resolved').length;
    return { report: attainment(wf, runs, policy), openIncidents: open };
  },

  
  slaOverview: () => {
    const runs = [...world.runs.values()].map(world.publicRun);
    return { reports: sla.list().map((pol) => attainment(pol.workflowName, runs, pol)) };
  },
};

module.exports = { handlers };
