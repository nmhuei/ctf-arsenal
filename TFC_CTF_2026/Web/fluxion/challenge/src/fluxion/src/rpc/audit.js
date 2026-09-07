'use strict';


const audit = require('../models/audit');
const { clampInt } = require('../lib/validate');

const handlers = {
  fetchAuditLog: (p) => ({ entries: audit.tail(clampInt(p && p.limit, 1, 200, 50)) }),
};

module.exports = { handlers };
