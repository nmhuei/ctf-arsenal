'use strict';


const express = require('express');
const world = require('../world');
const { requireOperator } = require('../auth/session');
const { settings } = require('../rpc/prefs');
const router = express.Router();

router.use(requireOperator);

router.get('/settings', (req, res) => res.json({ settings }));

router.post('/drain', (req, res) => {
  
  let n = 0;
  for (const r of world.runs.values()) {
    if (r.status === 'queued' || r.status === 'running') { r.status = 'draining'; n++; }
  }
  res.json({ ok: true, drained: n });
});

router.get('/hooks', (req, res) => {
  
  const hooks = [...world.hooks.values()].map((h) => ({
    id: h.id, runId: h.runId, isWebhook: h.isWebhook, resumed: h.resumed,
  }));
  res.json({ hooks });
});

router.post('/retention/sweep', (req, res) => {
  res.json({ ok: true, swept: 0, note: 'retention sweep is a no-op in single-node mode' });
});

module.exports = router;
