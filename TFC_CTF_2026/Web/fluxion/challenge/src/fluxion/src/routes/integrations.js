'use strict';





const express = require('express');
const integrations = require('../models/integrations');
const { requirePublicTarget } = require('../lib/nethost');
const router = express.Router();

router.get('/', (req, res) => res.json({ integrations: integrations.list() }));

router.post('/', (req, res) => res.json(integrations.create(req.body || {})));

router.get('/:id', (req, res) => {
  const x = integrations.get(req.params.id);
  if (!x) return res.status(404).json({ error: 'no such integration' });
  res.json({ integration: integrations.view(x) });
});

router.post('/:id/health', async (req, res) => {
  const x = integrations.get(req.params.id);
  if (!x) return res.status(404).json({ error: 'no such integration' });
  const guard = requirePublicTarget(x.url);
  if (guard.error) return res.status(400).json(guard);
  try {
    const r = await fetch(guard.url, { method: 'GET' });
    integrations.recordHealth(x.id, r.ok ? 'healthy' : 'degraded');
    res.json({ id: x.id, url: guard.url, status: r.status, health: r.ok ? 'healthy' : 'degraded' });
  } catch (e) {
    integrations.recordHealth(x.id, 'unreachable');
    res.status(502).json({ id: x.id, url: guard.url, health: 'unreachable', error: String((e && e.message) || e) });
  }
});

module.exports = router;
