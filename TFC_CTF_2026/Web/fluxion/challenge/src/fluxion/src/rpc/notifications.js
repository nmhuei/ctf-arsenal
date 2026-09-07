'use strict';







const world = require('../world');
const integrations = require('../models/integrations');
const { requirePublicTarget } = require('../lib/nethost');
const { optString } = require('../lib/validate');


function fields(r) {
  return {
    runId: r.runId,
    workflow: r.workflowName,
    status: r.status,
    steps: String((r.steps || []).length),
    startedAt: new Date(Math.floor(r.startedAt / 1000) * 1000).toISOString(),
  };
}


function expand(tpl, vals) {
  return String(tpl).replace(/\{\{\s*([a-zA-Z0-9_]+)\s*\}\}/g, (_, k) =>
    Object.prototype.hasOwnProperty.call(vals, k) ? String(vals[k]) : '');
}

const DEFAULT_TPL = '[{{status}}] {{workflow}} ({{runId}})';

const handlers = {
  
  renderNotification: (p) => {
    const r = world.getRun(String((p && p.runId) || ''));
    if (!r) return { error: 'no such run' };
    const tpl = optString(p && p.template, DEFAULT_TPL);
    return { runId: r.runId, message: expand(tpl, fields(r)) };
  },

  
  previewNotification: (p) => {
    const sample = { runId: 'run_SAMPLE', workflow: 'demo-workflow', status: 'completed', steps: '3',
                     startedAt: new Date(0).toISOString() };
    return { message: expand(optString(p && p.template, DEFAULT_TPL), sample) };
  },

  
  testNotificationChannel: async (p) => {
    const x = integrations.get(p && p.integrationId);
    if (!x) return { error: 'no such integration' };
    const guard = requirePublicTarget(x.url);
    if (guard.error) return guard;
    const message = expand(optString(p && p.template, DEFAULT_TPL),
      { runId: 'run_TEST', workflow: 'connectivity-test', status: 'ok', steps: '0',
        startedAt: new Date().toISOString() });
    try {
      const r = await fetch(guard.url, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ text: message }),
      });
      return { integrationId: x.id, url: guard.url, status: r.status, delivered: r.ok };
    } catch (e) { return { error: String((e && e.message) || e) }; }
  },
};

module.exports = { handlers, expand };
