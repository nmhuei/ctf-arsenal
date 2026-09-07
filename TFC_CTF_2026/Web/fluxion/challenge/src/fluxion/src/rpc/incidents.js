'use strict';







const incidents = require('../models/incidents');
const audit = require('../models/audit');
const world = require('../world');
const { attainment } = require('../lib/sla');

const handlers = {
  openIncident: (p) => {
    const res = incidents.open(p || {});
    if (res.ok) audit.record('incident.open', res.incident.id, res.incident.workflowName);
    return res;
  },

  ackIncident: (p) => incidents.acknowledge(p && p.id),

  resolveIncident: (p) => {
    const res = incidents.resolve(p && p.id);
    if (res.ok) audit.record('incident.resolve', res.incident.id, res.incident.severity);
    return res;
  },

  
  annotateIncident: (p) => incidents.annotate(p && p.id, (p && p.note) || {}),

  getIncident: (p) => {
    const i = incidents.get(p && p.id);
    return i ? { incident: i } : { error: 'no such incident' };
  },

  listIncidents: (p) => ({ incidents: incidents.list((p && p.filter) || {}) }),

  
  incidentSlaReport: (p) => {
    const wf = String((p && p.workflowName) || '');
    const runs = [...world.runs.values()].map(world.publicRun);
    const open = incidents.list({}).filter((i) => i.workflowName === wf && i.status !== 'resolved');
    return { workflowName: wf, openIncidents: open.length, sla: attainment(wf, runs, (p && p.policy) || {}) };
  },
};

module.exports = { handlers };
