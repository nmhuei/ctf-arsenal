'use strict';






const world = require('../world');
const { assertRunId, optString } = require('../lib/validate');


function projection(r) {
  return {
    runId: r.runId,
    workflow: r.workflowName,
    status: r.status,
    steps: String((r.steps || []).length),
    startedAt: new Date(Math.floor(r.startedAt / 1000) * 1000).toISOString(),
  };
}


function renderTemplate(tpl, fields) {
  return String(tpl).replace(/\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g, (_, k) =>
    Object.prototype.hasOwnProperty.call(fields, k) ? String(fields[k]) : '');
}

const DEFAULT_CARD = 'Run {{runId}} ({{workflow}}) is {{status}} with {{steps}} steps.';

const handlers = {
  
  renderRunCard: (p) => {
    const r = world.getRun(assertRunId(p.runId));
    if (!r) return { error: 'no such run' };
    const tpl = optString(p.template, DEFAULT_CARD);
    return { runId: r.runId, card: renderTemplate(tpl, projection(r)) };
  },

  
  summarizeRun: (p) => {
    const r = world.getRun(assertRunId(p.runId));
    if (!r) return { error: 'no such run' };
    return { runId: r.runId, summary: projection(r) };
  },

  
  exportRunReport: (p) => {
    const r = world.getRun(assertRunId(p.runId));
    if (!r) return { error: 'no such run' };
    const proj = projection(r);
    if (optString(p.format, 'json') === 'text') {
      return { runId: r.runId, report: renderTemplate(DEFAULT_CARD, proj) };
    }
    return { runId: r.runId, report: proj };
  },
};

module.exports = { handlers, renderTemplate, projection };
