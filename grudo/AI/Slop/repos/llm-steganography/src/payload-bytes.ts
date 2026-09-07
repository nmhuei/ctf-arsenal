export type Bit = 0 | 1;

/**
 * 32-bit BE **byte length** + UTF-8 payload bytes, **8 bits per byte** (MSB-first per byte).
 */
export function payloadBytesToBits(payload: Uint8Array): Bit[] {
  const len = payload.length;
  const header = new Uint8Array(4);
  new DataView(header.buffer).setUint32(0, len, false);
  // Helper to push bits msb-first for a byte array
  const bytesToBits = (bytes: Uint8Array): Bit[] =>
    Array.from(bytes, (byte) =>
      Array.from({ length: 8 }, (_, i) => ((byte >> (7 - i)) & 1) as Bit)
    ).flat();

  return [...bytesToBits(header), ...bytesToBits(payload)];
}

function bitsToUint32BE(bits: readonly Bit[]): number {
  let v = 0;
  for (let i = 0; i < 32; i++) {
    v = (v << 1) | bits[i]!;
  }
  return v >>> 0;
}

/** Inverse of `payloadBytesToBits`: full bit stream → raw UTF-8 bytes. */
export function bitsToPayloadBytes(bits: readonly Bit[]): Uint8Array {
  if (bits.length < 32)
    throw new Error("Need at least 32 bits for length header");
  const byteLength = bitsToUint32BE(bits);
  const need = 32 + 8 * byteLength;
  if (bits.length !== need)
    throw new Error(`Expected exactly ${need} bits, got ${bits.length}`);

  const out = new Uint8Array(byteLength);
  for (let i = 0; i < byteLength; i++) {
    let byte = 0;
    for (let j = 0; j < 8; j++) {
      byte = (byte << 1) | bits[32 + i * 8 + j]!;
    }
    out[i] = byte;
  }
  return out;
}
