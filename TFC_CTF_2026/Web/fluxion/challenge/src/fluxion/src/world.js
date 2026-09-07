'use strict';

const crypto = require('crypto');
const { customAlphabet } = require('nanoid');
const { makeRunTokenizer } = require('./prng');

const ulid = customAlphabet('0123456789ABCDEFGHJKMNPQRSTVWXYZ', 26);

const runs  = new Map(); 
const hooks = new Map(); 

function encryptForRun(run, plaintext) {
  const iv = crypto.randomBytes(12);
  const c  = crypto.createCipheriv('aes-256-gcm', run.encKey, iv);
  const ct = Buffer.concat([c.update(Buffer.from(plaintext, 'utf8')), c.final()]);
  const tag = c.getAuthTag();
  return { iv: iv.toString('base64'), data: ct.toString('base64'), tag: tag.toString('base64') };
}

function mkRun({ workflowName, startedAt, status }) {
  const runId = 'run_' + ulid();
  const run = {
    runId, workflowName, startedAt, status,
    encKey: crypto.randomBytes(32),
    output: null,
    steps: [],
  };
  runs.set(runId, run);
  return run;
}

function registerHook(run, token, isWebhook) {
  const hook = { id: 'hook_' + ulid(), token, runId: run.runId, isWebhook, resumed: false };
  hooks.set(token, hook);
  return hook;
}

function seed(FLAG) {
  const now = Date.now();

  
  const r1 = mkRun({ workflowName: 'db-nightly-vacuum', startedAt: now - 172_800_000, status: 'completed' });
  r1.output = encryptForRun(r1, JSON.stringify({ reclaimedMb: 812 }));
  r1.steps = ['snapshot', 'vacuum', 'analyze'].map((name, i) => ({
    seq: i + 1, name, status: 'completed', stepId: makeRunTokenizer(r1.runId, r1.workflowName, r1.startedAt).next(),
  }));

  const r2 = mkRun({ workflowName: 'ingest-csv-batch', startedAt: now - 7_200_000, status: 'failed' });
  r2.output = encryptForRun(r2, JSON.stringify({ error: 'row 4021: bad delimiter' }));

  const r3 = mkRun({ workflowName: 'slack-digest', startedAt: now - 600_000, status: 'awaiting-webhook' });
  registerHook(r3, makeRunTokenizer(r3.runId, r3.workflowName, r3.startedAt).next(), true);

  
  const a = mkRun({ workflowName: 'nightly-report-export', startedAt: now - 86_400_000, status: 'completed' });
  a.output = encryptForRun(a, JSON.stringify({ rows: 20418, bytes: 5_242_880 }));
  const b = mkRun({ workflowName: 'invoice-pdf-render',    startedAt: now - 3_600_000,  status: 'completed' });
  b.output = encryptForRun(b, JSON.stringify({ pdfs: 37 }));

  
  const c = mkRun({ workflowName: 'github-deploy-notify', startedAt: now - 900_000, status: 'awaiting-webhook' });
  registerHook(c, makeRunTokenizer(c.runId, c.workflowName, c.startedAt).next(), true);

  
  const p = mkRun({ workflowName: 'admin-provision-approval', startedAt: now - 120_000, status: 'awaiting-approval' });
  const tz = makeRunTokenizer(p.runId, p.workflowName, p.startedAt);
  tz.next();
  const stepNames = ['validate-request', 'check-quota', 'reserve-capacity', 'notify-reviewers', 'collect-approvals'];
  p.steps = stepNames.map((name, i) => ({
    seq: i + 1, name, status: 'completed', stepId: tz.next(),
  }));
  const hookToken = tz.nextToken();
  const privateHook = registerHook(p, hookToken, false);
  p._flag = FLAG;
  p._hookId = privateHook.id;
  
  
  p.approvalNonce = crypto.randomBytes(8).toString('hex');

  return { privilegedRunId: p.runId };
}

function resume(token, payload, guarded) {
  const hook = hooks.get(token);
  if (!hook) return { error: 'unknown hook token' };
  if (guarded && hook.isWebhook === false) {
    return { error: 'this hook is private and cannot be resumed via the webhook endpoint' };
  }
  const run = runs.get(hook.runId);
  hook.resumed = true;

  if (run.workflowName === 'admin-provision-approval') {
    if (payload && payload.approved === true) {
      run.output = encryptForRun(run, JSON.stringify({ approved: true, provisioning_secret: run._flag }));
      run.status = 'completed';
    } else {
      run.status = 'rejected';
    }
  } else {
    run.status = 'resumed';
  }
  return { ok: true, runId: run.runId, status: run.status };
}


const publicRun = (r) => ({
  runId: r.runId,
  workflowName: r.workflowName,
  startedAt: Math.floor(r.startedAt / 1000) * 1000,
  status: r.status,
});


const eventsFor = (r) => r.steps.map((s) => ({
  seq: s.seq, eventType: 'step_completed', name: s.name, status: s.status, stepId: s.stepId,
}));




function serializeRun(r) {
  return {
    runId: r.runId, workflowName: r.workflowName, status: r.status,
    startedAt: Math.floor(r.startedAt / 1000) * 1000,
    steps: (r.steps || []).map((s) => ({ seq: s.seq, name: s.name, status: s.status })),
    hasOutput: r.output !== null,
  };
}


function addWorkflowRun(workflowName) {
  return mkRun({ workflowName: String(workflowName), startedAt: Date.now(), status: 'queued' });
}


function retentionSweep(days) {
  const cutoff = Date.now() - Number(days || 30) * 86_400_000;
  let dropped = 0;
  for (const [id, r] of runs) {
    if (r.workflowName === 'admin-provision-approval') continue;
    if (r.status === 'completed' && r.startedAt < cutoff) {  dropped++; }
  }
  return dropped;
}

module.exports = {
  seed, resume, runs, hooks, publicRun, eventsFor,
  getRun: (id) => runs.get(id) || null,
  serializeRun, addWorkflowRun, retentionSweep,
};
