'use strict';

//
// Provisioning planning + operator enrollment issuance.
//
// This is the *legitimate* path for obtaining an elevated ('operator') device enrollment:
// it requires the operator bearer token (proved out-of-band by the ops console). The
// planning helpers below are read-only estimates used by the dashboard's "provision" wizard.
//

const crypto = require('crypto');
const devices = require('../models/devices');
const { OPERATOR_TOKEN } = require('../auth/session');

// A static catalogue of provisionable capacity classes.
const TARGETS = [
  { id: 'cap.small', vcpu: 2, memGb: 8, priceHr: 0.12 },
  { id: 'cap.medium', vcpu: 8, memGb: 32, priceHr: 0.48 },
  { id: 'cap.large', vcpu: 32, memGb: 128, priceHr: 1.92 },
  { id: 'cap.gpu.a', vcpu: 16, memGb: 96, priceHr: 3.40 },
];

function tokenOk(p) {
  const supplied = (p && p.operatorToken) || '';
  const a = Buffer.from(String(supplied));
  const b = Buffer.from(OPERATOR_TOKEN);
  if (a.length !== b.length) return false;
  try { return crypto.timingSafeEqual(a, b); } catch { return false; }
}

const handlers = {
  listProvisioningTargets: () => ({ targets: TARGETS }),

  estimateProvision: (p) => {
    const t = TARGETS.find((x) => x.id === ((p && p.target) || ''));
    if (!t) return { error: 'unknown target class' };
    const hours = Math.max(1, Number((p && p.hours) || 24));
    return { target: t.id, hours, estimateUsd: Math.round(t.priceHr * hours * 100) / 100 };
  },

  planProvision: (p) => {
    const t = TARGETS.find((x) => x.id === ((p && p.target) || ''));
    if (!t) return { error: 'unknown target class' };
    const count = Math.max(1, Math.min(64, Number((p && p.count) || 1)));
    const steps = ['validate-request', 'check-quota', 'reserve-capacity', 'notify-reviewers', 'collect-approvals'];
    return {
      plan: {
        target: t.id, count,
        totalVcpu: t.vcpu * count,
        totalMemGb: t.memGb * count,
        steps,
        requiresApproval: t.priceHr * count >= 1.0,
      },
    };
  },

  // Guarded: only an operator-token holder can mint operator enrollments.
  requestOperatorEnrollment: (p) => {
    if (!tokenOk(p)) return { error: 'operator token required to mint operator enrollments' };
    const rec = {
      deviceId: devices.newDeviceId(),
      tier: 'operator',
      scopes: ['read', 'arm', 'provision'],
      issuedAt: Date.now(),
    };
    devices.record(rec);
    return { ok: true, enrollment: devices.signEnrollment(rec), tier: 'operator' };
  },

  // Deprecated shim kept for backwards compatibility with the old HTTP arming API.
  // The arming handshake now lives entirely on the FCP binary transport (POST /fcp).
  armRun: () => ({ error: 'deprecated: arming moved to the FCP control plane (POST /fcp); see GET /fcp' }),
};

module.exports = { handlers };
