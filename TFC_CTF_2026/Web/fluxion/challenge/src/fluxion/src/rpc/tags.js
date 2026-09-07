'use strict';






const tags = require('../models/tags');

const handlers = {
  setRunLabels: (p) => tags.set(p && p.runId, (p && p.labels) || {}),
  getRunLabels: (p) => ({ runId: String((p && p.runId) || ''), labels: tags.get(p && p.runId) }),
  removeRunLabel: (p) => tags.unset(p && p.runId, p && p.key),
  findRunsByLabel: (p) => ({ matches: tags.search(String((p && p.key) || ''), String((p && p.value) || '')) }),
};

module.exports = { handlers };
