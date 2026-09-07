'use strict';


const express = require('express');
const world = require('../world');
const { assertRunId } = require('../lib/validate');
const router = express.Router();

router.get('/runs', (req, res) => {
  res.json({ runs: [...world.runs.values()].map(world.publicRun) });
});

router.get('/runs/:id', (req, res) => {
  let id;
  try { id = assertRunId(req.params.id); } catch { return res.status(400).json({ error: 'malformed runId' }); }
  const r = world.getRun(id);
  if (!r) return res.status(404).json({ error: 'no such run' });
  res.json(world.publicRun(r));
});

router.get('/runs/:id/events', (req, res) => {
  let id;
  try { id = assertRunId(req.params.id); } catch { return res.status(400).json({ error: 'malformed runId' }); }
  const r = world.getRun(id);
  if (!r) return res.status(404).json({ error: 'no such run' });
  res.json({ runId: r.runId, events: world.eventsFor(r) });
});

module.exports = router;
