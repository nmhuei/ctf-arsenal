'use strict';

const express = require('express');
const defs = require('../models/definitions');
const activities = require('../models/activities');
const router = express.Router();

router.get('/activities', (req, res) => res.json({ activities: activities.list() }));
router.get('/', (req, res) => res.json({ definitions: defs.listNames() }));

router.get('/:name', (req, res) => {
  const d = defs.get(req.params.name, req.query.version);
  if (!d) return res.status(404).json({ error: 'no such definition' });
  res.json({ name: req.params.name, definition: d });
});

router.get('/:name/topology', (req, res) => {
  const t = defs.topology(req.params.name, req.query.version);
  if (!t) return res.status(404).json({ error: 'no such definition' });
  res.json(t);
});

module.exports = router;
