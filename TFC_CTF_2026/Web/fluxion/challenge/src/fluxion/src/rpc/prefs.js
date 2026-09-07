'use strict';






const { cloneDefaults, tunableEngineKeys, tunableViewKeys } = require('../config/defaults');
const { mergeConfig, pickTunable } = require('../config/merge');


const settings = cloneDefaults();

const handlers = {
  getSettings: () => ({ settings }),

  
  saveSettings: (p) => {
    const patch = (p && p.settings) || {};
    if (patch.engine) mergeConfig(settings.engine, pickTunable(patch.engine, tunableEngineKeys));
    if (patch.view)   mergeConfig(settings.view,   pickTunable(patch.view, tunableViewKeys));
    return { ok: true, settings };
  },

  
  resetSettings: (p) => {
    const which = (p && p.section) || 'all';
    const d = cloneDefaults();
    if (which === 'engine' || which === 'all') settings.engine = d.engine;
    if (which === 'view' || which === 'all') settings.view = d.view;
    return { ok: true, settings };
  },
};

module.exports = { handlers, settings };
