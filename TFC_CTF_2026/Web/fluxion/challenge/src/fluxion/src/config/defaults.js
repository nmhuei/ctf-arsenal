'use strict';




const engineDefaults = {
  concurrency: 8,
  stepTimeoutMs: 900_000,
  retry: { max: 5, backoff: 'exponential', jitter: true, baseMs: 250 },
  hooks: { deliveryTimeoutMs: 4_000, signatureHeader: 'x-fluxion-signature', maxPending: 256 },
  retention: { completedDays: 30, failedDays: 90, eventsPerRun: 5_000 },
  observability: { streamBufferKb: 64, sampleRate: 1.0, redactSecrets: true },
};

const viewDefaults = {
  columns: ['run', 'workflow', 'status'],
  density: 'comfortable',
  theme: 'system',
  timezone: 'UTC',
  refreshMs: 4_000,
};


const tunableEngineKeys = [
  'concurrency', 'stepTimeoutMs', 'retry', 'observability',
];


const tunableViewKeys = [
  'columns', 'density', 'theme', 'timezone', 'refreshMs',
];

function cloneDefaults() {
  return {
    engine: JSON.parse(JSON.stringify(engineDefaults)),
    view: JSON.parse(JSON.stringify(viewDefaults)),
  };
}

module.exports = {
  engineDefaults, viewDefaults, tunableEngineKeys, tunableViewKeys, cloneDefaults,
};
