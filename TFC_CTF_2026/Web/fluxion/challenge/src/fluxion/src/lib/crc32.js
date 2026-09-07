'use strict';

//
// CRC-32 (IEEE 802.3, reflected, poly 0xEDB88320) — byte-for-byte compatible with
// zlib.crc32 / Python's zlib.crc32. Used by the Fluxion Control Protocol frame codec
// to detect corruption on the wire. Implemented locally so the codec has no runtime
// dependency on the zlib native binding version shipped by the host.
//

let TABLE = null;

function buildTable() {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n >>> 0;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    }
    t[n] = c >>> 0;
  }
  return t;
}

function crc32(buf, seed = 0) {
  if (!TABLE) TABLE = buildTable();
  let crc = (~seed) >>> 0;
  for (let i = 0; i < buf.length; i++) {
    crc = (TABLE[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8)) >>> 0;
  }
  return (~crc) >>> 0;
}

// Convenience helpers mirrored from the reference spec; kept for the telemetry module.
function crc32Hex(buf) {
  return crc32(buf).toString(16).padStart(8, '0');
}

module.exports = { crc32, crc32Hex };
