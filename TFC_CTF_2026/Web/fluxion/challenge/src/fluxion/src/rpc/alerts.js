'use strict';


const alerts = require('../models/alerts');
const world = require('../world');

const handlers = {
  listAlertRules: () => ({ rules: alerts.list() }),
  createAlertRule: (p) => alerts.create(p || {}),
  toggleAlertRule: (p) => alerts.toggle(p && p.id, p && p.enabled),
  evaluateAlerts: () => ({ results: alerts.evaluate([...world.runs.values()].map(world.publicRun)) }),
};

module.exports = { handlers };
