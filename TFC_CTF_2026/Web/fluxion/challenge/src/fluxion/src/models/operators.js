'use strict';

//
// Operator roster (display metadata for the ops console). Purely informational — access
// control is enforced by the operator bearer token, not by this list.
//

const roster = new Map();

function seedOperators() {
  const seed = [
    { handle: 'sre-oncall', name: 'On-call SRE', canApprove: true, region: 'us-east' },
    { handle: 'platform-lead', name: 'Platform Lead', canApprove: true, region: 'eu-west' },
    { handle: 'dashboard-viewer', name: 'Read-only Dashboard', canApprove: false, region: 'global' },
  ];
  for (const o of seed) roster.set(o.handle, Object.assign({ enrolledAt: Date.now() }, o));
}

function list() {
  return [...roster.values()].map((o) => ({ handle: o.handle, name: o.name, canApprove: o.canApprove, region: o.region }));
}

function approvers() {
  return list().filter((o) => o.canApprove).map((o) => o.handle);
}

module.exports = { seedOperators, list, approvers, roster };
