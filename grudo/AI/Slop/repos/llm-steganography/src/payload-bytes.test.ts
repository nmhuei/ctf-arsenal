import { describe, expect, test } from "bun:test";
import { bitsToPayloadBytes, payloadBytesToBits } from "./payload-bytes.ts";

function expectBytesEqual(a: Uint8Array, b: Uint8Array) {
  expect(a.length).toBe(b.length);
  for (let i = 0; i < a.length; i++) {
    expect(a[i]).toBe(b[i]);
  }
}

describe("payloadBytesToBits / bitsToPayloadBytes", () => {
  test("empty payload: header only (32 bits)", () => {
    const bits = payloadBytesToBits(new Uint8Array(0));
    expect(bits.length).toBe(32);
    expect(bits.every((b) => b === 0)).toBe(true);
    expectBytesEqual(bitsToPayloadBytes(bits), new Uint8Array(0));
  });

  test("round-trip ASCII", () => {
    const raw = new TextEncoder().encode("hello world");
    const bits = payloadBytesToBits(raw);
    expectBytesEqual(bitsToPayloadBytes(bits), raw);
  });

  test("round-trip UTF-8 (multi-byte)", () => {
    const raw = new TextEncoder().encode("café 🌙");
    const bits = payloadBytesToBits(raw);
    expectBytesEqual(bitsToPayloadBytes(bits), raw);
  });

  test("round-trip arbitrary bytes", () => {
    const raw = new Uint8Array([0, 255, 128, 1, 42]);
    const bits = payloadBytesToBits(raw);
    expectBytesEqual(bitsToPayloadBytes(bits), raw);
  });

  test("bit count = 32 + 8 * byteLength", () => {
    const raw = new Uint8Array(100);
    for (let i = 0; i < raw.length; i++) raw[i] = i & 255;
    const bits = payloadBytesToBits(raw);
    expect(bits.length).toBe(32 + 8 * raw.length);
  });

  test("bitsToPayloadBytes: too few bits for header", () => {
    expect(() => bitsToPayloadBytes([])).toThrow("Need at least 32 bits");
    expect(() => bitsToPayloadBytes(new Array(31).fill(0) as (0 | 1)[])).toThrow(
      "Need at least 32 bits"
    );
  });

  test("bitsToPayloadBytes: truncated payload", () => {
    const bits = payloadBytesToBits(new Uint8Array([1, 2, 3]));
    const truncated = bits.slice(0, bits.length - 4);
    expect(() => bitsToPayloadBytes(truncated)).toThrow("Expected");
  });

  test("bitsToPayloadBytes: extra bits after payload", () => {
    const bits = payloadBytesToBits(new Uint8Array([9]));
    const extra = [...bits, 0, 1] as (0 | 1)[];
    expect(() => bitsToPayloadBytes(extra)).toThrow("Expected exactly");
  });
});
