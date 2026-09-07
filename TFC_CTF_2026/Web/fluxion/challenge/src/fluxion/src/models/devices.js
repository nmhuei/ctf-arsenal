'use strict';

//
// Device enrollment registry.
//
// The control plane (FCP) only talks to *enrolled* devices, and only devices holding an
// enrollment at the 'operator' tier may drive the arming handshake. Enrollments are
// stateless, signed blobs so a horizontally-scaled fleet doesn't need shared session
// storage: base64url(JSON record) + '.' + HMAC-SHA256(ENROLL_KEY, b64record).
//
// Legitimate operator enrollments are supposed to be minted through
// rpc/provisioning.requestOperatorEnrollment, which is guarded by the operator bearer
// token. Self-service enrollments (rpc/enrollment.enrollDevice) are meant to hand out
// read-only 'viewer' devices for the live dashboard.
//

const crypto = require('crypto');
const { customAlphabet } = require('nanoid');

const ENROLL_KEY = crypto.randomBytes(32);
const devId = customAlphabet('0123456789abcdefghijklmnopqrstuvwxyz', 18);

// In-memory registry of issued device ids (audit/telemetry only; the token itself is the
// source of truth, the registry is just so the ops dashboard can count fleet size).
const devices = new Map();

const KNOWN_TIERS = ['viewer', 'operator', 'auditor'];

const b64u = (b) => Buffer.from(b).toString('base64url');

function emac(raw) {
  return crypto.createHmac('sha256', ENROLL_KEY).update(raw).digest('base64url');
}

function signEnrollment(record) {
  const raw = b64u(JSON.stringify(record));
  return raw + '.' + emac(raw);
}

function verifyEnrollment(tok) {
  const parts = String(tok || '').split('.');
  if (parts.length !== 2) return null;
  const expect = emac(parts[0]);
  let ok = false;
  try {
    ok = crypto.timingSafeEqual(Buffer.from(expect), Buffer.from(String(parts[1])));
  } catch { return null; }
  if (!ok) return null;
  try {
    return JSON.parse(Buffer.from(parts[0], 'base64url').toString('utf8'));
  } catch { return null; }
}

function newDeviceId() {
  return 'dev_' + devId();
}

function record(rec) {
  devices.set(rec.deviceId, { deviceId: rec.deviceId, tier: rec.tier, issuedAt: rec.issuedAt });
  return rec;
}

function seedDevices() {
  // A couple of long-lived fleet devices so /api/ops and telemetry look populated.
  for (const tier of ['viewer', 'viewer', 'auditor']) {
    const rec = { deviceId: newDeviceId(), tier, scopes: tier === 'auditor' ? ['read', 'audit'] : ['read'], issuedAt: Date.now() - 86_400_000 };
    signEnrollment(rec);
    record(rec);
  }
}

function fleetSummary() {
  const byTier = {};
  for (const d of devices.values()) byTier[d.tier] = (byTier[d.tier] || 0) + 1;
  return { total: devices.size, byTier };
}

module.exports = {
  KNOWN_TIERS,
  signEnrollment,
  verifyEnrollment,
  newDeviceId,
  record,
  seedDevices,
  fleetSummary,
  devices,
};
