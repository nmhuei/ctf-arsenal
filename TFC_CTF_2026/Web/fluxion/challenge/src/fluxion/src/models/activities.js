'use strict';






const CATALOG = [
  { type: 'http.request', inputs: ['url', 'method', 'headers'], outputs: ['status', 'body'], timeoutMs: 30_000, retriable: true },
  { type: 'db.query', inputs: ['sql', 'params'], outputs: ['rows'], timeoutMs: 60_000, retriable: false },
  { type: 'transform.map', inputs: ['items', 'expr'], outputs: ['items'], timeoutMs: 15_000, retriable: true },
  { type: 'transform.reduce', inputs: ['items', 'seed'], outputs: ['value'], timeoutMs: 15_000, retriable: true },
  { type: 'notify.slack', inputs: ['channel', 'text'], outputs: ['ts'], timeoutMs: 10_000, retriable: true },
  { type: 'notify.email', inputs: ['to', 'subject', 'body'], outputs: ['messageId'], timeoutMs: 10_000, retriable: true },
  { type: 'storage.put', inputs: ['bucket', 'key', 'body'], outputs: ['etag'], timeoutMs: 45_000, retriable: true },
  { type: 'render.pdf', inputs: ['template', 'data'], outputs: ['bytes'], timeoutMs: 60_000, retriable: false },
  { type: 'approval.human', inputs: ['reviewers'], outputs: ['approved'], timeoutMs: 0, retriable: false },
  { type: 'wait.webhook', inputs: ['signature'], outputs: ['payload'], timeoutMs: 0, retriable: false },
];

const byType = new Map(CATALOG.map((a) => [a.type, a]));

function list() { return CATALOG.map((a) => ({ ...a })); }
function get(type) { const a = byType.get(String(type)); return a ? { ...a } : null; }
function exists(type) { return byType.has(String(type)); }

module.exports = { list, get, exists };
