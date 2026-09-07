'use strict';







const express = require('express');
const world = require('../world');
const incidents = require('../models/incidents');
const router = express.Router();


const OPS_KEY = process.env.OPS_KEY || 'fluxion-ops';


router.use((req, res, next) => {
  res.set('Access-Control-Allow-Origin', req.headers.origin || '*');
  res.set('Access-Control-Allow-Credentials', 'true');
  res.set('Vary', 'Origin');
  if (req.method === 'OPTIONS') return res.sendStatus(204);
  next();
});

router.get('/summary', (req, res) => {
  const byStatus = {};
  for (const r of world.runs.values()) byStatus[r.status] = (byStatus[r.status] || 0) + 1;
  res.json({ engine: 'fluxion', runs: world.runs.size, hooks: world.hooks.size, byStatus, uptime: process.uptime() });
});

router.get('/incidents', (req, res) => {
  const open = incidents.list({}).filter((i) => i.status !== 'resolved');
  res.json({ open: open.length, bySeverity: open.reduce((m, i) => ((m[i.severity] = (m[i.severity] || 0) + 1), m), {}) });
});


router.get('/rollup', (req, res) => {
  const k = String(req.headers['x-ops-key'] || req.query.key || '');
  if (k !== OPS_KEY) return res.status(401).json({ error: 'ops key required' });
  const runs = [...world.runs.values()];
  res.json({
    runs: runs.length,
    completed: runs.filter((r) => r.status === 'completed').length,
    failed: runs.filter((r) => r.status === 'failed').length,
    awaiting: runs.filter((r) => String(r.status).startsWith('awaiting')).length,
    withOutput: runs.filter((r) => r.output !== null).length,
    incidentsOpen: incidents.list({}).filter((i) => i.status !== 'resolved').length,
  });
});

module.exports = router;
