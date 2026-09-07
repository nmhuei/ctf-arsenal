'use strict';

const express = require('express');
const incidents = require('../models/incidents');
const router = express.Router();

router.get('/', (req, res) => res.json({ incidents: incidents.list(req.query || {}) }));

router.post('/', (req, res) => res.json(incidents.open(req.body || {})));

router.get('/:id', (req, res) => {
  const i = incidents.get(req.params.id);
  if (!i) return res.status(404).json({ error: 'no such incident' });
  res.json({ incident: i });
});

router.post('/:id/ack', (req, res) => res.json(incidents.acknowledge(req.params.id)));
router.post('/:id/resolve', (req, res) => res.json(incidents.resolve(req.params.id)));

module.exports = router;
