'use strict';






const { seededJitter } = require('../prng');

function clampNum(v, lo, hi, dflt) {
  const n = Number(v);
  if (!Number.isFinite(n)) return dflt;
  return Math.min(hi, Math.max(lo, n));
}

function schedule(policy) {
  const p = policy || {};
  const attempts = clampNum(p.maxAttempts, 1, 20, 5);
  const base = clampNum(p.baseDelayMs, 10, 60_000, 500);
  const factor = clampNum(p.factor, 1, 10, 2);
  const cap = clampNum(p.capMs, base, 3_600_000, 60_000);
  const jitter = clampNum(p.jitter, 0, 1, 0.2);

  const delays = [];
  for (let i = 0; i < attempts; i++) {
    const raw = Math.min(cap, base * Math.pow(factor, i));
    const j = jitter ? raw * jitter * seededJitter(`${base}:${factor}:${i}`) : 0;
    delays.push(Math.round(raw + j));
  }
  return { attempts, base, factor, cap, jitter, delaysMs: delays, totalMs: delays.reduce((a, b) => a + b, 0) };
}

module.exports = { schedule };
