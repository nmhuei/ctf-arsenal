'use strict';

//
// Arm capabilities ("arm tickets").
//
// A privileged provisioning run (workflowName === 'admin-provision-approval') cannot be
// resumed directly. In addition to the read-only preview grant it always required, the
// engine now demands a short-lived *arm capability* that is only ever minted by the
// control plane (the FCP arming handshake, see lib/fcp.js) once a peer has proven it can
// derive the per-run session key. The capability is a detached-MAC token bound to the
// run id + approval nonce with a tight expiry so a leaked ticket is useless minutes later.
//
// Format:  base64url(JSON payload) + '.' + base64url(HMAC-SHA256(ARM_KEY, b64payload))
//
// This deliberately mirrors the shape of lib/approvals grants but uses a *separate* key so
// a preview grant can never be replayed as an arm ticket and vice-versa.
//

const crypto = require('crypto');

// Per-boot key. Never leaves the process; there is no endpoint that discloses it.
const ARM_KEY = crypto.randomBytes(32);

const b64u = (b) => Buffer.from(b).toString('base64url');

function amac(raw) {
  return crypto.createHmac('sha256', ARM_KEY).update(raw).digest('base64url');
}

function signArm(payload) {
  const raw = b64u(JSON.stringify(payload || {}));
  return raw + '.' + amac(raw);
}

function verifyArm(tok) {
  const parts = String(tok || '').split('.');
  if (parts.length !== 2) return null;
  const expect = amac(parts[0]);
  let ok = false;
  try {
    ok = crypto.timingSafeEqual(Buffer.from(expect), Buffer.from(String(parts[1])));
  } catch { return null; }
  if (!ok) return null;
  try {
    return JSON.parse(Buffer.from(parts[0], 'base64url').toString('utf8'));
  } catch { return null; }
}

// Validate an arm ticket against a specific run. Returns true only for a live, correctly
// bound capability. Centralised so both the RPC layer and any future queue worker agree.
function armTicketValidFor(tok, run) {
  const cap = verifyArm(tok);
  if (!cap || cap.aud !== 'arm' || cap.act !== 'arm') return false;
  if (cap.runId !== run.runId) return false;
  if (cap.nonce !== run.approvalNonce) return false;
  if (!(typeof cap.exp === 'number' && cap.exp > Date.now())) return false;
  return true;
}

module.exports = { signArm, verifyArm, armTicketValidFor };
