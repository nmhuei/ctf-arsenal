'use strict';

//
// Control-plane telemetry.
//
// Counters and helpers the ops dashboard uses to visualise the arming transport. Read-only.
// Also exposes a couple of framing utilities so support engineers can sanity-check frames
// they captured with a packet sniffer without needing to reimplement the codec.
//

const { crc32Hex } = require('../lib/crc32');
const legacy = require('../lib/framing_legacy');
const operators = require('../models/operators');
const devices = require('../models/devices');

// Rolling in-memory counters (reset on boot).
const counters = {
  helloFrames: 0,
  kexFrames: 0,
  armFrames: 0,
  legacyFrames: 0,
  rejected: 0,
  startedAt: Date.now(),
};

function classifyFrame(hex) {
  let buf;
  try { buf = Buffer.from(String(hex || ''), 'hex'); } catch { return { error: 'bad hex' }; }
  if (legacy.isLegacyFrame(buf)) {
    const f = legacy.decodeLegacy(buf);
    return { proto: 'FCP/0', valid: !!f, opcode: f && f.opcode, note: 'legacy framing (retired)' };
  }
  if (buf.length >= 3 && buf[0] === 0x46 && buf[1] === 0x58 && buf[2] === 0x01) {
    const len = buf.length >= 13 ? ((buf[10] << 16) | (buf[11] << 8) | buf[12]) : -1;
    return {
      proto: 'FCP/1',
      type: buf.length >= 4 ? buf[3] : null,
      seq: buf.length >= 6 ? buf[5] : null,
      declaredLen: len,
      wireLen: buf.length,
      crcOfHeader: buf.length >= 13 ? crc32Hex(buf.subarray(0, 13)) : null,
      note: 'live framing; server validates crc32 over header+payload',
    };
  }
  return { proto: 'unknown' };
}

const handlers = {
  controlPlaneStatus: () => ({
    proto: 'FCP/1',
    uptimeMs: Date.now() - counters.startedAt,
    fleet: devices.fleetSummary(),
    approvers: operators.approvers(),
  }),

  controlPlaneCounters: () => ({ counters: Object.assign({}, counters) }),

  // Offline frame inspector. Does NOT touch session state; purely a decode helper.
  inspectFrame: (p) => classifyFrame(p && p.hex),

  listApprovers: () => ({ approvers: operators.approvers() }),
};

module.exports = { handlers, counters };
