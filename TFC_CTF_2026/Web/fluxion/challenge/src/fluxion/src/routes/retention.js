'use strict';

const express = require('express');
const retention = require('../models/retention');
const world = require('../world');
const router = express.Router();

router.get('/', (req, res) => res.json({ policies: retention.list() }));

router.get('/:workflowName', (req, res) => res.json({ policy: retention.get(req.params.workflowName) }));

router.get('/:workflowName/sweep', (req, res) => {
  const runs = [...world.runs.values()].map(world.publicRun);
  res.json(retention.projectSweep(req.params.workflowName, runs));
});

module.exports = router;
