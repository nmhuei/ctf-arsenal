'use strict';

//
// Capability catalogue.
//
// Read-only introspection over what the control plane can grant and how. This is purely
// descriptive: it advertises the arming policy and lets operators sanity-check an arm
// ticket's *shape* (never validating it against the secret key — that only happens inside
// resumeHook). Handy for tooling authors wiring up the FCP handshake.
//

const policy = require('../lib/policy');
const armlog = require('../models/armlog');

// A catalogue entry describes one grantable capability and its issuance path.
const CATALOGUE = [
  {
    id: 'cap.arm',
    aud: 'arm',
    description: 'Short-lived ticket that arms a privileged provisioning run for resume.',
    issuedBy: 'FCP arming handshake (POST /fcp)',
    ttlMs: policy.POLICY.armTicketTtlMs,
    boundTo: ['runId', 'nonce', 'exp'],
  },
  {
    id: 'cap.preview',
    aud: 'approvals',
    description: 'Self-signed read-only preview grant (see previewApprovalGrant).',
    issuedBy: 'previewApprovalGrant RPC',
    ttlMs: null,
    boundTo: ['runId', 'nonce', 'act'],
  },
  {
    id: 'cap.enroll.operator',
    aud: 'enroll',
    description: 'Operator-tier device enrollment required to open an arming session.',
    issuedBy: 'requestOperatorEnrollment RPC (operator token required)',
    ttlMs: null,
    boundTo: ['deviceId', 'tier'],
  },
];

function shapeOf(tok) {
  const parts = String(tok || '').split('.');
  if (parts.length !== 2) return { valid: false, reason: 'expected <payload>.<mac>' };
  let payload = null;
  try {
    payload = JSON.parse(Buffer.from(parts[0], 'base64url').toString('utf8'));
  } catch { return { valid: false, reason: 'payload is not base64url JSON' }; }
  return {
    valid: true,
    fields: Object.keys(payload),
    aud: payload.aud || null,
    hasExp: typeof payload.exp === 'number',
    note: 'shape only; MAC is verified server-side at use time',
  };
}

const handlers = {
  listCapabilities: () => ({ catalogue: CATALOGUE }),
  describeControlPolicy: () => ({ policy: policy.describe() }),
  inspectCapabilityShape: (p) => shapeOf(p && p.token),
  armingAudit: (p) => ({ recent: armlog.list(p && p.limit), summary: armlog.summary() }),
};

module.exports = { handlers };
