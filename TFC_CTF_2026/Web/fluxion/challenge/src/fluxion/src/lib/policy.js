'use strict';

//
// Control-plane policy.
//
// Static policy knobs for the arming control plane. These are surfaced read-only through
// the capabilities RPC so operator tooling can discover current limits without guessing.
// Changing them here changes the advertised policy; enforcement lives in lib/fcp.js.
//

const POLICY = {
  proto: 'FCP/1',
  maxFrameBytes: 65536,
  sessionTtlMs: 60_000,
  // Handshake stages, in the exact order the server expects them.
  stages: ['hello', 'kex', 'arm'],
  // Only these enrollment tiers may open an arming session.
  armTiers: ['operator'],
  // Minted arm capabilities are short-lived.
  armTicketTtlMs: 120_000,
  // Frame types (informational mirror of lib/fcp.js constants).
  frameTypes: {
    HELLO: 0x01, KEX: 0x02, ARM: 0x03,
    CHALLENGE: 0x81, KEXOK: 0x82, ARMED: 0x83, ERR: 0xee,
  },
};

function describe() {
  // Shallow copy so callers cannot mutate the live policy object.
  return JSON.parse(JSON.stringify(POLICY));
}

function stageIndex(stage) {
  return POLICY.stages.indexOf(String(stage));
}

module.exports = { POLICY, describe, stageIndex };
