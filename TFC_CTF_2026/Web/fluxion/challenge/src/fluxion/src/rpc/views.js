'use strict';


const views = require('../models/views');
const audit = require('../models/audit');

const handlers = {
  listViews: () => ({ views: views.list() }),
  getView: (p) => {
    const v = views.get(p && p.name);
    return v ? { view: v } : { error: 'no such view' };
  },
  saveView: (p) => {
    const res = views.save(p && p.name, (p && p.view) || {});
    if (res.ok) audit.record('view.save', (p && p.name) || '', '');
    return res;
  },
  deleteView: (p) => views.remove(p && p.name),
};

module.exports = { handlers };
