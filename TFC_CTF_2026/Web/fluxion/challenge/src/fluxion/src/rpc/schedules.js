'use strict';



const schedules = require('../models/schedules');
const { nextRun } = require('../lib/cron');
const audit = require('../models/audit');

const handlers = {
  listSchedules: () => ({ schedules: schedules.list() }),

  createSchedule: (p) => {
    const res = schedules.create(p || {});
    if (res.ok) audit.record('schedule.create', res.id, (p && p.workflow) || '');
    return res;
  },

  updateSchedule: (p) => schedules.update(p && p.id, (p && p.patch) || {}),

  deleteSchedule: (p) => schedules.remove(p && p.id),

  
  previewSchedule: (p) => {
    const cron = String((p && p.cron) || '');
    const out = [];
    let from = Date.now();
    try {
      for (let i = 0; i < Math.min(10, Number((p && p.count) || 3)); i++) {
        const t = nextRun(cron, from);
        if (t == null) break;
        out.push(t);
        from = t + 60_000;
      }
    } catch (e) { return { error: String(e.message || e) }; }
    return { cron, fireTimes: out };
  },
};

module.exports = { handlers };
