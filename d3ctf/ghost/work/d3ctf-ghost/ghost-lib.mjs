const BASE = process.env.GHOST_BASE || "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf";
const enc = new TextEncoder();
const dec = new TextDecoder();

function canonical(value) {
  if (value === null || typeof value !== "object") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => canonical(item)).join(",")}]`;
  return `{${Object.keys(value)
    .sort()
    .filter((key) => value[key] !== undefined)
    .map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`)
    .join(",")}}`;
}

function b64url(bytes) {
  const buf = bytes instanceof ArrayBuffer ? Buffer.from(bytes) : Buffer.from(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  return buf.toString("base64url");
}

function unb64url(text) {
  return new Uint8Array(Buffer.from(text, "base64url"));
}

async function jsonFetch(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options);
  const text = await res.text();
  const body = text ? JSON.parse(text) : null;
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
    err.body = body;
    throw err;
  }
  return body;
}

async function deriveKey(bits, salt, info, usages) {
  const raw = await crypto.subtle.importKey("raw", bits, "HKDF", false, ["deriveKey"]);
  return crypto.subtle.deriveKey(
    { name: "HKDF", hash: "SHA-256", salt, info: enc.encode(info) },
    raw,
    { name: "AES-GCM", length: 256 },
    false,
    usages,
  );
}

export async function init() {
  const guest = await jsonFetch("/api/session/guest", {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  const pair = await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  const clientPublicKey = await crypto.subtle.exportKey("jwk", pair.publicKey);
  const boot = await jsonFetch("/api/transport/bootstrap", {
    method: "POST",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${guest.token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ clientPublicKey }),
  });
  const serverKey = await crypto.subtle.importKey("jwk", boot.serverPublicKey, { name: "ECDH", namedCurve: "P-256" }, true, []);
  const bits = await crypto.subtle.deriveBits({ name: "ECDH", public: serverKey }, pair.privateKey, 256);
  const salt = unb64url(boot.salt);
  return {
    token: guest.token,
    sid: boot.sid,
    c2sKey: await deriveKey(bits, salt, "ghost-packet:c2s", ["encrypt"]),
    s2cKey: await deriveKey(bits, salt, "ghost-packet:s2c", ["decrypt"]),
    sequence: 0,
  };
}

export async function send(session, target, body) {
  const seq = ++session.sequence;
  const ts = Date.now();
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const aad = enc.encode(canonical({ direction: "c2s", seq, sid: session.sid, ts, v: 1 }));
  const ct = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv, additionalData: aad, tagLength: 128 },
    session.c2sKey,
    enc.encode(canonical({ target, body })),
  );
  const packet = { v: 1, sid: session.sid, seq, ts, iv: b64url(iv), ct: b64url(ct) };
  const reply = await jsonFetch("/api/gateway", {
    method: "POST",
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${session.token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(packet),
  });
  const replyAad = enc.encode(canonical({ direction: "s2c", seq: reply.seq, sid: reply.sid, ts: reply.ts, v: reply.v }));
  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: unb64url(reply.iv), additionalData: replyAad, tagLength: 128 },
    session.s2cKey,
    unb64url(reply.ct),
  );
  return JSON.parse(dec.decode(plaintext));
}
