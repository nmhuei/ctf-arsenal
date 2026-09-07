'use strict';

//
// Self-service device enrollment for the live dashboard.
//
// The public dashboard enrolls itself as a read-only ('viewer') device so it can subscribe
// to the run stream without an operator token. Operators are supposed to obtain elevated
// ('operator') enrollments through the guarded provisioning path instead.
//

const devices = require('../models/devices');

const handlers = {
  // Enroll a device for the observability dashboard. Callers may pass a `profile` object
  // with cosmetic fields (label, theme, timezone, ...). Defaults keep new devices at the
  // read-only viewer tier.
  enrollDevice: (p) => {
    const profile = (p && p.profile) || {};
    const base = {
      deviceId: devices.newDeviceId(),
      tier: 'viewer',
      scopes: ['read'],
      issuedAt: Date.now(),
    };
    // Merge caller-supplied profile fields over the defaults so the dashboard can persist
    // its display preferences alongside the enrollment.
    const rec = Object.assign(base, profile);
    devices.record(rec);
    const enrollment = devices.signEnrollment(rec);
    return { ok: true, deviceId: rec.deviceId, tier: rec.tier, enrollment };
  },

  // Introspect an enrollment token (does not require holding it to be operator).
  describeEnrollment: (p) => {
    const rec = devices.verifyEnrollment((p && p.enrollment) || '');
    if (!rec) return { error: 'invalid or unsigned enrollment' };
    return { valid: true, deviceId: rec.deviceId, tier: rec.tier, scopes: rec.scopes || [] };
  },

  // Fleet size for the ops widgets.
  fleetSummary: () => devices.fleetSummary(),
};

module.exports = { handlers };
