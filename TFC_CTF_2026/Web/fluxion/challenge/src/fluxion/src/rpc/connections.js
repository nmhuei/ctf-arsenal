'use strict';



const conns = require('../models/connections');
const audit = require('../models/audit');

const handlers = {
  listConnections: () => ({ connections: conns.list() }),
  getConnection: (p) => {
    const c = conns.get(p && p.name);
    return c ? { connection: c } : { error: 'no such connection' };
  },
  createConnection: (p) => {
    const res = conns.create(p || {});
    if (res.ok) audit.record('connection.create', res.name, res.type);
    return res;
  },
  updateConnection: (p) => conns.update(p && p.name, (p && p.patch) || {}),
};

module.exports = { handlers };
