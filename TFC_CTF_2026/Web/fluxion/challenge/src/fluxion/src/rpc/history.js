'use strict';


const history = require('../models/history');
const { assertRunId, clampInt } = require('../lib/validate');

const handlers = {
  runHistory: (p) => {
    let id;
    try { id = assertRunId(p && p.runId); } catch (e) { return { error: String(e.message || e) }; }
    return { runId: id, attempts: history.forRun(id) };
  },
  recentHistory: (p) => ({ attempts: history.recent(clampInt(p && p.limit, 1, 200, 50)) }),
};

module.exports = { handlers };
