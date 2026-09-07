'use strict';





const { nextRun, parseCron } = require('../lib/cron');
const { safeAssign } = require('../config/merge');

const schedules = new Map(); 
let seq = 0;

function create(body) {
  const workflow = String((body && body.workflow) || '').trim();
  const cron = String((body && body.cron) || '').trim();
  if (!workflow) return { ok: false, error: 'workflow required' };
  try { parseCron(cron); } catch (e) { return { ok: false, error: String(e.message || e) }; }
  const id = 'sch_' + (++seq).toString(36).padStart(4, '0');
  schedules.set(id, { id, workflow, cron, enabled: true, createdAt: Date.now() });
  return { ok: true, id, nextRun: nextRun(cron) };
}

function update(id, patch) {
  const s = schedules.get(String(id));
  if (!s) return { ok: false, error: 'no such schedule' };
  
  const allowed = {};
  if (patch && 'enabled' in patch) allowed.enabled = !!patch.enabled;
  if (patch && typeof patch.cron === 'string') {
    try { parseCron(patch.cron); } catch (e) { return { ok: false, error: String(e.message || e) }; }
    allowed.cron = patch.cron;
  }
  safeAssign(s, allowed);
  return { ok: true, schedule: view(s) };
}

function remove(id) {
  return { ok: schedules.delete(String(id)) };
}

function view(s) {
  return { id: s.id, workflow: s.workflow, cron: s.cron, enabled: s.enabled,
           nextRun: s.enabled ? nextRun(s.cron) : null };
}

function list() { return [...schedules.values()].map(view); }

function seedSchedules() {
  create({ workflow: 'nightly-report-export', cron: '0 2 * * *' });
  create({ workflow: 'db-nightly-vacuum', cron: '30 3 * * 0' });
  create({ workflow: 'slack-digest', cron: '0 */4 * * *' });
}

module.exports = { create, update, remove, list, view, seedSchedules };
