'use strict';


function isPlainObject(v) {
  return v && typeof v === 'object' && !Array.isArray(v);
}
function assertString(v, name) {
  if (typeof v !== 'string') throw new Error(`${name} must be a string`);
  return v;
}
function assertRunId(v) {
  const s = assertString(v, 'runId');
  if (!/^run_[0-9A-Z]{26}$/.test(s)) throw new Error('malformed runId');
  return s;
}
function optString(v, dflt = '') {
  return typeof v === 'string' ? v : dflt;
}
function clampInt(v, lo, hi, dflt) {
  const n = Number.parseInt(v, 10);
  if (Number.isNaN(n)) return dflt;
  return Math.min(hi, Math.max(lo, n));
}

module.exports = { isPlainObject, assertString, assertRunId, optString, clampInt };
