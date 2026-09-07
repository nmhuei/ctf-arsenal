'use strict';






const modules = [
  require('./workflows'),
  require('./reports'),
  require('./prefs'),
  require('./net'),
  require('./tokens'),
  require('./definitions'),
  require('./schedules'),
  require('./alerts'),
  require('./metrics'),
  require('./audit'),
  require('./connections'),
  require('./views'),
  require('./history'),
  require('./layout'),
  require('./diagnostics'),
  require('./incidents'),
  require('./retention'),
  require('./integrations'),
  require('./notifications'),
  require('./insights'),
  require('./tags'),
  require('./search'),
  require('./simulate'),
  require('./sla'),
  require('./savedqueries'),
  require('./retrypolicy'),
  require('./enrollment'),
  require('./provisioning'),
  require('./telemetry'),
  require('./capabilities'),
];

function auxHandlers() {
  const out = {};
  for (const m of modules) Object.assign(out, m.handlers);
  return out;
}

module.exports = { auxHandlers };
