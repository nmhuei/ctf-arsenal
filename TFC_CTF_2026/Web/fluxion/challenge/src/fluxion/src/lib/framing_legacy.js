'use strict';

//
// Legacy framing (FCP/0) — RETIRED.
//
// The first control-plane iteration used a simpler 2-byte-length, checksum-less framing
// with an ASCII opcode. It shipped briefly in 1.2.x and is retained only so the telemetry
// module can classify stray FCP/0 frames still emitted by very old agents in the field.
// Nothing in the live arming path uses this codec; new tooling MUST use lib/fcp.js (FCP/1).
//
//   off  size  field
//   0    3     magic   = 'FX0'
//   3    1     opcode  (ASCII 'H'/'K'/'A')
//   4    2     length  (16-bit BE)
//   6    len   payload
//
// FCP/0 had no CRC and no transcript binding; that is exactly why it was replaced.
//

const L_MAGIC = Buffer.from('FX0', 'ascii');

function encodeLegacy(opcode, payload) {
  const body = payload || Buffer.alloc(0);
  const buf = Buffer.alloc(6 + body.length);
  L_MAGIC.copy(buf, 0);
  buf[3] = String(opcode).charCodeAt(0) & 0xff;
  buf.writeUInt16BE(body.length & 0xffff, 4);
  body.copy(buf, 6);
  return buf;
}

function decodeLegacy(buf) {
  if (!Buffer.isBuffer(buf) || buf.length < 6) return null;
  if (buf[0] !== L_MAGIC[0] || buf[1] !== L_MAGIC[1] || buf[2] !== L_MAGIC[2]) return null;
  const len = buf.readUInt16BE(4);
  if (buf.length !== 6 + len) return null;
  return { opcode: String.fromCharCode(buf[3]), payload: buf.subarray(6, 6 + len) };
}

function isLegacyFrame(buf) {
  return Buffer.isBuffer(buf) && buf.length >= 3 &&
    buf[0] === L_MAGIC[0] && buf[1] === L_MAGIC[1] && buf[2] === L_MAGIC[2];
}

module.exports = { encodeLegacy, decodeLegacy, isLegacyFrame };
