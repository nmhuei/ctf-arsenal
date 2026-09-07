'use strict';








const integrations = require('../models/integrations');
const audit = require('../models/audit');
const { requirePublicTarget } = require('../lib/nethost');

const handlers = {
  listIntegrations: () => ({ integrations: integrations.list() }),

  createIntegration: (p) => {
    const res = integrations.create(p || {});
    if (res.ok) audit.record('integration.create', res.integration.id, res.integration.kind);
    return res;
  },

  getIntegration: (p) => {
    const x = integrations.get(p && p.id);
    return x ? { integration: integrations.view(x) } : { error: 'no such integration' };
  },

  
  setIntegrationUrl: (p) => integrations.setUrl(p && p.id, p && p.url),

  
  checkIntegration: async (p) => {
    const x = integrations.get(p && p.id);
    if (!x) return { error: 'no such integration' };
    const guard = requirePublicTarget(x.url);
    if (guard.error) return guard;
    try {
      const r = await fetch(guard.url, { method: 'GET' });
      const health = r.ok ? 'healthy' : 'degraded';
      integrations.recordHealth(x.id, health);
      return { id: x.id, url: guard.url, status: r.status, health };
    } catch (e) {
      integrations.recordHealth(x.id, 'unreachable');
      return { id: x.id, url: guard.url, health: 'unreachable', error: String((e && e.message) || e) };
    }
  },

  
  probeIntegrationEndpoint: async (p) => {
    const guard = requirePublicTarget(p && p.url);
    if (guard.error) return guard;
    try {
      const r = await fetch(guard.url, { method: 'GET' });
      const body = (await r.text()).slice(0, 256);
      return { url: guard.url, status: r.status, bytes: body.length, preview: body };
    } catch (e) { return { error: String((e && e.message) || e) }; }
  },
};

module.exports = { handlers };
