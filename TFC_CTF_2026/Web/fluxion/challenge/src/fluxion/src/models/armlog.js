'use strict';

//
// Arming audit log.
//
// Every FCP handshake outcome is appended here so the ops console can show a timeline of
// arming attempts (who tried to arm which run, and whether it succeeded). The log records
// only non-sensitive metadata — a session id, the stage reached, and a coarse outcome code.
// It deliberately never stores payloads, salts, session keys, nonces, or minted tickets.
//

const MAX_ENTRIES = 500;
const entries = [];

function push(evt) {
  const rec = {
    at: Date.now(),
    sid: (evt && evt.sid) || 0,
    stage: (evt && evt.stage) || 'unknown',
    outcome: (evt && evt.outcome) || 'unknown',
  };
  entries.push(rec);
  if (entries.length > MAX_ENTRIES) entries.splice(0, entries.length - MAX_ENTRIES);
  return rec;
}

function list(limit) {
  const n = Math.max(1, Math.min(MAX_ENTRIES, Number(limit || 50)));
  return entries.slice(-n);
}

function summary() {
  const byOutcome = {};
  const byStage = {};
  for (const e of entries) {
    byOutcome[e.outcome] = (byOutcome[e.outcome] || 0) + 1;
    byStage[e.stage] = (byStage[e.stage] || 0) + 1;
  }
  return { total: entries.length, byOutcome, byStage };
}

module.exports = { push, list, summary };
