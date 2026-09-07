'use strict';








const crypto = require('crypto');
const world = require('../world');
const { makeLabelTokenizer } = require('../prng');


function b64len(s) {
  if (typeof s !== 'string' || !s) return 0;
  return Buffer.from(s, 'base64').length;
}

const handlers = {
  
  runOutputEnvelope: (p) => {
    const r = world.getRun(String((p && p.runId) || ''));
    if (!r) return { error: 'no such run' };
    if (!r.output) return { runId: r.runId, hasOutput: false };
    return {
      runId: r.runId,
      hasOutput: true,
      cipher: 'aes-256-gcm',
      ivBytes: b64len(r.output.iv),
      tagBytes: b64len(r.output.tag),
      dataBytes: b64len(r.output.data),
    };
  },

  
  
  
  runFingerprint: (p) => {
    const r = world.getRun(String((p && p.runId) || ''));
    if (!r) return { error: 'no such run' };
    const h = crypto.createHash('sha256')
      .update(r.runId).update('|')
      .update(r.workflowName).update('|')
      .update(String(r.status)).update('|')
      .update(r.output ? String(r.output.data) : '');
    return { runId: r.runId, fingerprint: h.digest('hex').slice(0, 32) };
  },

  
  
  previewRowKeys: (p) => {
    const label = String((p && p.label) || 'dashboard');
    const n = Math.max(1, Math.min(16, Number((p && p.count) || 5)));
    const tz = makeLabelTokenizer(label);
    const keys = [];
    for (let i = 0; i < n; i++) keys.push(tz.next());
    return { label, keys };
  },

  
  stepShape: (p) => {
    const r = world.getRun(String((p && p.runId) || ''));
    if (!r) return { error: 'no such run' };
    return {
      runId: r.runId,
      steps: (r.steps || []).map((s) => ({ seq: s.seq, nameLen: String(s.name).length, status: s.status })),
    };
  },
};

module.exports = { handlers };
