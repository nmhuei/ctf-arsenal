'use strict';



function tokenBucket({ capacity = 30, refillPerSec = 1 } = {}) {
  const buckets = new Map();
  return function limit(key) {
    const now = Date.now();
    let b = buckets.get(key);
    if (!b) { b = { tokens: capacity, ts: now }; buckets.set(key, b); }
    const elapsed = (now - b.ts) / 1000;
    b.tokens = Math.min(capacity, b.tokens + elapsed * refillPerSec);
    b.ts = now;
    if (b.tokens < 1) return false;
    b.tokens -= 1;
    return true;
  };
}

module.exports = { tokenBucket };
