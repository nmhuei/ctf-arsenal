'use strict';





const express = require('express');
const world = require('../world');
const router = express.Router();

function snapshot() {
  const runs = [...world.runs.values()].map(world.publicRun);
  const byStatus = {};
  for (const r of runs) byStatus[r.status] = (byStatus[r.status] || 0) + 1;
  return { at: Date.now(), runs: runs.length, byStatus };
}


router.get('/events', (req, res) => {
  res.set({
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    Connection: 'keep-alive',
  });
  res.flushHeaders && res.flushHeaders();
  res.write(`event: hello\ndata: ${JSON.stringify({ engine: 'fluxion' })}\n\n`);

  let ticks = 0;
  const timer = setInterval(() => {
    ticks++;
    res.write(`event: snapshot\ndata: ${JSON.stringify(snapshot())}\n\n`);
    if (ticks >= 30) { clearInterval(timer); res.end(); }   
  }, 2_000);

  req.on('close', () => clearInterval(timer));
});


router.get('/snapshot', (req, res) => res.json(snapshot()));

module.exports = router;
