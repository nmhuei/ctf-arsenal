'use strict';





const express = require('express');
const world = require('../world');
const router = express.Router();

const DEBUG_KEY = process.env.DEBUG_KEY || 'fluxion-diagnostics';

function requireDebugKey(req, res, next) {
  const k = String(req.headers['x-debug-key'] || '');
  if (k !== DEBUG_KEY) return res.status(401).json({ error: 'diagnostics key required' });
  next();
}

router.use(requireDebugKey);

router.get('/status', (req, res) => {
  const mem = process.memoryUsage();
  res.json({
    engine: 'fluxion',
    runs: world.runs.size,
    hooks: world.hooks.size,
    uptime: process.uptime(),
    rssMb: Math.round(mem.rss / 1048576),
    node: process.version,
  });
});

router.get('/runs', (req, res) => {
  
  const byStatus = {};
  for (const r of world.runs.values()) byStatus[r.status] = (byStatus[r.status] || 0) + 1;
  res.json({ total: world.runs.size, byStatus });
});

module.exports = router;
