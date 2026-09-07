'use strict';

const express = require('express');
const path = require('path');
const world = require('./world');
const { auxHandlers } = require('./rpc');
const healthRoutes = require('./routes/health');
const workflowRoutes = require('./routes/workflows');
const adminRoutes = require('./routes/admin');
const streamRoutes = require('./routes/stream');
const definitionRoutes = require('./routes/definitions');
const metricsRoutes = require('./routes/metrics');
const debugRoutes = require('./routes/debug');
const defsModel = require('./models/definitions');
const schedulesModel = require('./models/schedules');
const alertsModel = require('./models/alerts');
const connectionsModel = require('./models/connections');
const viewsModel = require('./models/views');
const incidentsModel = require('./models/incidents');
const retentionModel = require('./models/retention');
const integrationsModel = require('./models/integrations');
const slaModel = require('./models/slapolicies');
const savedQueriesModel = require('./models/savedqueries');
const retryPoliciesModel = require('./models/retrypolicies');
const opsRoutes = require('./routes/ops');
const incidentRoutes = require('./routes/incidents');
const integrationRoutes = require('./routes/integrations');
const retentionRoutes = require('./routes/retention');

const FLAG = process.env.FLAG || 'TFC{set-the-FLAG-environment-variable}';
world.seed(FLAG);



defsModel.seedDefinitions();
schedulesModel.seedSchedules();
alertsModel.seedAlerts();
connectionsModel.seedConnections();
viewsModel.seedViews();
incidentsModel.seedIncidents();
retentionModel.seedRetention();
integrationsModel.seedIntegrations();
slaModel.seedSlaPolicies();
savedQueriesModel.seedSavedQueries();
retryPoliciesModel.seedRetryPolicies();

const devicesModel = require('./models/devices');
const operatorsModel = require('./models/operators');
devicesModel.seedDevices();
operatorsModel.seedOperators();

const controlRoutes = require('./routes/control');

const crypto = require('crypto');


const { signPreviewGrant, verifyGrant } = require('./lib/approvals');
const { armTicketValidFor } = require('./lib/capability');

const app = express();
app.disable('x-powered-by');


const viewPrefs = { columns: ['run', 'workflow', 'status'], density: 'comfortable' };


const reportDefaults = {};




function resolveScopePath(scope, pathStr) {
  const parts = String(pathStr).split('.');
  let cur = scope;
  for (let i = 0; i < parts.length; i++) {
    const key = parts[i];
    if (cur === null || cur === undefined) {
      throw new Error(`E_PATH: '${parts.slice(0, i).join('.')}' is not an object`);
    }

    cur = (cur instanceof Map) ? cur.get(key) : cur[key];
  }
  return cur;
}



function renderCaption(tmpl, scope) {
  return String(tmpl).replace(/\$\{([^}]*)\}/g, (_, raw) => {
    const expr = raw.trim();
    const val = resolveScopePath(scope, expr);
    if (val === undefined) {
      throw new Error(`E_UNDEF: '${expr}' is undefined`);
    }
    if (val !== null && typeof val === 'object') {
      throw new Error(`E_NODE: '${expr}' resolved to a container (${Object.keys(val).join(',')})`);
    }
    const s = String(val);

    if (!/^-?[0-9]+(\.[0-9]+)?$/.test(s)) {
      throw new Error(`E_SCALAR: '${expr}' is not a renderable metric: ${s}`);
    }
    return s;
  });
}

function mergeDeep(dst, src) {
  for (const k of Object.keys(src)) {

    if (k === '__proto__') continue;
    const v = src[k];
    if (v && typeof v === 'object' && !Array.isArray(v)) {

      const cur = dst[k];
      const traversable = cur !== null && (typeof cur === 'object' || typeof cur === 'function');
      if (!traversable) dst[k] = {};
      mergeDeep(dst[k], v);
    } else {
      dst[k] = v;
    }
  }
  return dst;
}


app.use('/api/rpc', express.raw({ type: () => true, limit: '1mb' }));
app.use(express.json());


const handlers = {
  fetchRuns: () => [...world.runs.values()].map(world.publicRun),

  fetchHooks: () =>
    [...world.hooks.values()]
      .filter((h) => h.isWebhook === true)
      .map((h) => ({ id: h.id, runId: h.runId, token: h.token, isWebhook: h.isWebhook })),

  
  previewApprovalGrant: (p) => signPreviewGrant(p.document !== undefined ? p.document : (p.doc || {})),

  resumeHook: async (p) => {
    const hook = world.hooks.get(p.token);
    if (!hook) return { error: 'unknown hook token' };
    const run = world.getRun(hook.runId);
    
    if (run && run.workflowName === 'admin-provision-approval') {
      const g = verifyGrant(p.grant);
      if (!g || g.aud !== 'approvals' || g.act !== 'resume' || g.runId !== run.runId || g.nonce !== run.approvalNonce) {
        return { error: 'this run requires a signed approval grant (aud=approvals, act=resume, bound runId)' };
      }
      // Privileged provisioning also requires a live arm capability minted by the control
      // plane (FCP arming handshake over POST /fcp). A preview grant alone is insufficient.
      if (!armTicketValidFor(p.armToken, run)) {
        return { error: 'this run is not armed: complete the control-plane arming handshake (POST /fcp) and pass the resulting armToken' };
      }
    }
    return world.resume(p.token, p.payload, false);
  },

  
  saveViewPreferences: (p) => {
    mergeDeep(viewPrefs, p.prefs || {});
    return { ok: true, prefs: viewPrefs };
  },

  fetchRunOutput: (p) => {
    const r = world.getRun(p.runId);
    if (!r) return { error: 'no such run' };
    return { runId: r.runId, status: r.status, output: r.output };
  },

  renderRunReport: (p) => {
    const r = world.getRun(p.runId);
    if (!r) return { error: 'no such run' };
    if (r.workflowName !== 'admin-provision-approval' || r.status !== 'completed') {
      return { runId: r.runId, report: `run ${r.runId} is ${r.status}` };
    }
    const rc = reportDefaults.presentation;
    const caption = rc && rc.caption;
    if (caption) {
      if (rc.token !== r.approvalNonce) {
        return { runId: r.runId, report: 'presentation profile not authorised for this run' };
      }


      const scope = {
        run: { id: r.runId, workflowName: r.workflowName, status: r.status,
               startedAt: Math.floor(r.startedAt / 1000) * 1000 },
        engine: require('./world'),
        metrics: { steps: r.steps.length },
      };
      try {
        renderCaption(caption, scope);

        return { runId: r.runId, report: 'presentation rendered' };
      } catch (e) {

        return { runId: r.runId, report: 'render diagnostic', diagnostic: String(e && e.message || e) };
      }
    }
    return { runId: r.runId, report: 'provisioning complete' };
  },

  fetchEvents: (p) => {
    const r = world.getRun(p.runId);
    if (!r) return { error: 'no such run' };
    return { runId: r.runId, events: world.eventsFor(r) };
  },

  
  inspectRun: (p) => {
    const r = world.getRun(p.runId);
    if (!r) return { error: 'no such run' };
    const hookIds = [...world.hooks.values()].filter((h) => h.runId === r.runId).map((h) => h.id);
    return { runId: r.runId, workflowName: r.workflowName, status: r.status,
             stepCount: r.steps.length, hasOutput: r.output !== null, hookIds };
  },

  
  getWorkspaceConfig: () => {
    const cfg = {};
    return { theme: cfg.theme || 'light', density: cfg.density || 'comfortable' };
  },

  
  
  
  searchRuns: (p) => {
    const f = p.filter || {};
    
    const INDEXED = ['runId', 'workflowName', 'status', 'startedAt', 'approvalNonce'];
    
    const RESTRICTED = { approvalNonce: ['$startsWith'] };
    const cmp = (field, spec, key) => {
      const s = String(field ?? '');
      const allow = RESTRICTED[key] || null;
      if (spec && typeof spec === 'object' && !Array.isArray(spec)) {
        return Object.entries(spec).every(([op, val]) => {
          if (allow && !allow.includes(op)) return false;
          const v = String(val);
          switch (op) {
            case '$eq':         return s === v;
            case '$ne':         return s !== v;
            case '$startsWith': return s.startsWith(v);
            case '$endsWith':   return s.endsWith(v);
            case '$contains':   return s.includes(v);
            case '$gt':         return s > v;
            case '$lt':         return s < v;
            case '$regex':      return new RegExp(v).test(s);
            default:            return false;
          }
        });
      }
      
      if (allow) return s === String(spec);
      return s.includes(String(spec));
    };
    const runs = [...world.runs.values()].filter((r) =>
      Object.entries(f).every(([k, spec]) => INDEXED.includes(k) && cmp(r[k], spec, k)));
    return { results: runs.map(world.publicRun), count: runs.length };
  },

  
  exportMetrics: () => {
    const runs = [...world.runs.values()];
    return {
      runs: runs.length,
      hooks: world.hooks.size,
      completed: runs.filter((r) => r.status === 'completed').length,
      awaiting: runs.filter((r) => String(r.status).startsWith('awaiting')).length,
    };
  },

  
  probeTarget: async (p) => {
    const u = String(p.url || '');
    if (!/^https?:\/\//i.test(u)) return { error: 'only http(s) targets' };
    try {
      const host = new URL(u).hostname;
      const m = /^172\.(\d+)\./.exec(host);
      if (/^(localhost|127\.|10\.|192\.168\.|169\.254\.|0\.|::1|\[?::1\]?|metadata\.google\.internal)/i.test(host)
          || (m && +m[1] >= 16 && +m[1] <= 31)) {
        return { error: 'target host is not routable' };
      }
    } catch { return { error: 'invalid target' }; }
    try {
      const r = await fetch(u, { method: 'GET' });
      const body = (await r.text()).slice(0, 256);
      return { status: r.status, bytes: body.length, preview: body };
    } catch (e) { return { error: String(e && e.message || e) }; }
  },
};



for (const [name, fn] of Object.entries(auxHandlers())) {
  if (!(name in handlers)) handlers[name] = fn;
}

app.post('/api/rpc', async (req, res) => {
  let body;
  try {
    const buf = Buffer.isBuffer(req.body) ? req.body : Buffer.from('');
    body = JSON.parse(buf.toString('utf8') || '{}');
  } catch {
    return res.status(400).json({ error: 'bad body' });
  }
  const { method, params } = body || {};
  const fn = handlers[method];
  if (!fn) return res.status(404).json({ error: 'unknown method: ' + method });
  try {
    return res.json({ result: await fn(params || {}) });
  } catch (e) {
    return res.status(500).json({ error: String(e && e.message || e) });
  }
});


app.post('/webhook/:token', (req, res) => {
  const out = world.resume(req.params.token, req.body, true);
  if (out.error) return res.status(403).json(out);
  res.json(out);
});


app.get('/api/status', (req, res) => {
  res.set('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.set('Access-Control-Allow-Credentials', 'true');
  res.json({ engine: 'fluxion', version: '1.4.0', runs: world.runs.size, uptime: process.uptime() });
});


app.use('/fcp', controlRoutes);

app.use('/api', healthRoutes);
app.use('/api/workflows', workflowRoutes);
app.use('/api/admin', adminRoutes);
app.use('/api/stream', streamRoutes);
app.use('/api/definitions', definitionRoutes);
app.use('/api/metrics', metricsRoutes);
app.use('/api/debug', debugRoutes);
app.use('/api/ops', opsRoutes);
app.use('/api/incidents', incidentRoutes);
app.use('/api/integrations', integrationRoutes);
app.use('/api/retention', retentionRoutes);

app.use(express.static(path.join(__dirname, 'public')));

// The Node app is fronted by an in-container nginx reverse proxy that owns the public
// port (3000). The app itself binds an internal loopback port only; all external traffic
// arrives via nginx.
const PORT = process.env.PORT || 8001;
const BIND = process.env.BIND_ADDR || '127.0.0.1';
app.listen(PORT, BIND, () => console.log(`fluxion listening on ${BIND}:${PORT}`));
