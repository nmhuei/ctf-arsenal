'use strict';






const world = require('../world');
const { assertRunId, optString } = require('../lib/validate');
const history = require('../models/history');



const GATED = 'admin-provision-approval';

function transition(runId, to, allowed) {
  const r = world.getRun(runId);
  if (!r) return { error: 'no such run' };
  if (r.workflowName === GATED) {
    return { error: 'this run is gated on reviewer approval and cannot be transitioned directly' };
  }
  if (!allowed.includes(r.status)) {
    return { error: `cannot ${to} a run in status ${r.status}` };
  }
  r.status = to;
  return { ok: true, runId: r.runId, status: r.status };
}

const handlers = {
  listWorkflows: () => {
    const names = new Set([...world.runs.values()].map((r) => r.workflowName));
    return { workflows: [...names].map((name) => ({ name, kind: 'durable' })) };
  },

  
  cancelRun: (p) => transition(assertRunId(p.runId), 'canceled', ['queued', 'running', 'awaiting-webhook']),

  
  pauseRun: (p) => transition(assertRunId(p.runId), 'paused', ['running']),

  
  replayRun: (p) => {
    const id = assertRunId(p.runId);
    const res = transition(id, 'queued', ['completed', 'failed', 'canceled']);
    if (res.ok) history.record('replay', id, 'requeued from terminal state');
    return res;
  },

  
  retryStep: (p) => {
    const r = world.getRun(assertRunId(p.runId));
    if (!r) return { error: 'no such run' };
    const seq = Number.parseInt(p.seq, 10);
    const step = (r.steps || []).find((s) => s.seq === seq);
    if (!step) return { error: 'no such step' };
    history.record('retry', r.runId, 'step ' + seq);
    return { ok: true, runId: r.runId, seq, status: step.status, note: 'retry queued' };
  },

  
  
  signalRun: (p) => {
    const r = world.getRun(assertRunId(p.runId));
    if (!r) return { error: 'no such run' };
    if (r.workflowName === GATED) {
      return { runId: r.runId, status: r.status, note: 'awaiting reviewer approval; signal ignored' };
    }
    if (r.status === 'awaiting-webhook') r.status = 'resumed';
    return { ok: true, runId: r.runId, status: r.status };
  },

  
  describeRun: (p) => {
    const r = world.getRun(assertRunId(p.runId));
    if (!r) return { error: 'no such run' };
    return {
      runId: r.runId, workflowName: r.workflowName, kind: 'durable',
      dependsOn: optString(p.parent) || null, stepCount: (r.steps || []).length,
    };
  },
};

module.exports = { handlers };
