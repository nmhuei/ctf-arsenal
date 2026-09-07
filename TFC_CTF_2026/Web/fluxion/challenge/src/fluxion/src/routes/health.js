'use strict';

const express = require('express');
const world = require('../world');
const router = express.Router();

router.get('/health', (req, res) => res.json({ status: 'ok', engine: 'fluxion' }));
router.get('/live',   (req, res) => res.json({ live: true }));
router.get('/ready',  (req, res) => res.json({ ready: true, runs: world.runs.size }));
router.get('/version', (req, res) => res.json({
  engine: 'fluxion', version: '1.4.0', node: process.version, uptime: process.uptime(),
}));

module.exports = router;
