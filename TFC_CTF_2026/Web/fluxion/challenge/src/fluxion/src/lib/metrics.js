'use strict';




function percentile(sorted, p) {
  if (!sorted.length) return 0;
  const idx = Math.min(sorted.length - 1, Math.floor((p / 100) * sorted.length));
  return sorted[idx];
}



function estimateDurationMs(run) {
  const steps = (run.steps || []).length;
  return 1_000 + steps * 750;
}

function summarize(runs) {
  const byStatus = {};
  const durations = [];
  for (const r of runs) {
    byStatus[r.status] = (byStatus[r.status] || 0) + 1;
    durations.push(estimateDurationMs(r));
  }
  durations.sort((a, b) => a - b);
  return {
    total: runs.length,
    byStatus,
    duration: {
      p50: percentile(durations, 50),
      p90: percentile(durations, 90),
      p99: percentile(durations, 99),
      max: durations.length ? durations[durations.length - 1] : 0,
    },
  };
}


function timeline(runs, buckets = 12) {
  if (!runs.length) return [];
  const times = runs.map((r) => r.startedAt);
  const lo = Math.min(...times);
  const hi = Math.max(...times) + 1;
  const width = Math.max(1, (hi - lo) / buckets);
  const out = Array.from({ length: buckets }, (_, i) => ({ from: Math.floor(lo + i * width), count: 0 }));
  for (const t of times) {
    const b = Math.min(buckets - 1, Math.floor((t - lo) / width));
    out[b].count++;
  }
  return out;
}

module.exports = { percentile, estimateDurationMs, summarize, timeline };
