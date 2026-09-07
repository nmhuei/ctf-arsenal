'use strict';






const FIELDS = [
  { name: 'minute', min: 0, max: 59 },
  { name: 'hour', min: 0, max: 23 },
  { name: 'dom', min: 1, max: 31 },
  { name: 'month', min: 1, max: 12 },
  { name: 'dow', min: 0, max: 6 },
];

function parseField(token, min, max) {
  const out = new Set();
  for (const part of String(token).split(',')) {
    let step = 1;
    let range = part;
    const slash = part.indexOf('/');
    if (slash !== -1) { step = parseInt(part.slice(slash + 1), 10); if (!Number.isInteger(step) || step < 1) step = 1; range = part.slice(0, slash); }
    let lo = min;
    let hi = max;
    if (range !== '*' && range !== '') {
      const dash = range.indexOf('-');
      if (dash !== -1) { lo = parseInt(range.slice(0, dash), 10); hi = parseInt(range.slice(dash + 1), 10); }
      else { lo = hi = parseInt(range, 10); }
    }
    if (Number.isNaN(lo) || Number.isNaN(hi)) throw new Error('bad cron field: ' + token);
    lo = Math.max(min, lo); hi = Math.min(max, hi);
    for (let v = lo; v <= hi; v += step) if (v >= min && v <= max) out.add(v);
  }
  return out;
}

function parseCron(expr) {
  const parts = String(expr).trim().split(/\s+/);
  if (parts.length !== 5) throw new Error('cron must have 5 fields');
  return FIELDS.map((f, i) => parseField(parts[i], f.min, f.max));
}

function matches(sets, date) {
  return (
    sets[0].has(date.getUTCMinutes()) &&
    sets[1].has(date.getUTCHours()) &&
    sets[2].has(date.getUTCDate()) &&
    sets[3].has(date.getUTCMonth() + 1) &&
    sets[4].has(date.getUTCDay())
  );
}



function nextRun(expr, fromMs = Date.now()) {
  const sets = parseCron(expr);
  const d = new Date(Math.ceil(fromMs / 60_000) * 60_000);
  const horizon = 366 * 24 * 60;
  for (let i = 0; i < horizon; i++) {
    if (matches(sets, d)) return d.getTime();
    d.setUTCMinutes(d.getUTCMinutes() + 1);
  }
  return null;
}

module.exports = { parseCron, nextRun };
