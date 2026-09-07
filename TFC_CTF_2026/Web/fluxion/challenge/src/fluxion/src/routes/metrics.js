'use strict';

const express = require('express');
const world = require('../world');
const { summarize, timeline } = require('../lib/metrics');
const alerts = require('../models/alerts');
const { clampInt } = require('../lib/validate');
const router = express.Router();

router.get('/', (req, res) => res.json({ metrics: summarize([...world.runs.values()]) }));
router.get('/timeline', (req, res) =>
  res.json({ buckets: timeline([...world.runs.values()], clampInt(req.query.buckets, 4, 48, 12)) }));
router.get('/alerts', (req, res) =>
  res.json({ results: alerts.evaluate([...world.runs.values()].map(world.publicRun)) }));

module.exports = router;
