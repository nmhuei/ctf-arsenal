'use strict';







const { mergeConfig } = require('../config/merge');


const layout = {
  grid: { columns: 12, rowHeight: 32, gap: 8 },
  panels: {
    runs: { x: 0, y: 0, w: 8, h: 6, collapsed: false },
    alerts: { x: 8, y: 0, w: 4, h: 3, collapsed: false },
    timeline: { x: 8, y: 3, w: 4, h: 3, collapsed: false },
  },
  pinned: ['runs', 'alerts'],
};

const handlers = {
  getDashboardLayout: () => ({ layout }),

  
  saveDashboardLayout: (p) => {
    mergeConfig(layout, (p && p.layout) || {});
    return { ok: true, layout };
  },
};

module.exports = { handlers, layout };
