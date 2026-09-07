import express from "express";
import crypto from "crypto";
import { restoreArchive } from "./archive.js";

const app = express();
const personas = new Map();
const accounts = new Map();
const sessions = new Map();
const flag = process.env.FLAG || "TFCCTF{development_flag}";
const brainUrl = process.env.BRAIN_URL || "http://127.0.0.1:8000";

app.use(express.json({ limit: "16mb" }));
app.use(express.static(new URL("../public", import.meta.url).pathname));

async function neuralRequest(path, payload) {
  const response = await fetch(`${brainUrl}${path}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || `Neural relay returned ${response.status}`);
  return body;
}

function suppliedCache(runtime) {
  return runtime && typeof runtime === "object" && runtime.kv_cache && typeof runtime.kv_cache.cache === "string";
}

function accountFromRequest(request) {
  const token = request.get("x-soul-session");
  const accountId = sessions.get(token);
  return accountId ? accounts.get(accountId) : null;
}

function requireAccount(request, response) {
  const account = accountFromRequest(request);
  if (!account) {
    response.status(401).json({ error: "Create or sign in to a user account first." });
    return null;
  }
  return account;
}

function credentials(body) {
  const username = typeof body.username === "string" ? body.username.trim().toLowerCase() : "";
  const password = typeof body.password === "string" ? body.password : "";
  if (!/^[a-z0-9_-]{3,24}$/.test(username) || password.length < 8 || password.length > 128) {
    throw new Error("Use a 3-24 character user name and an 8-128 character password.");
  }
  return { username, password };
}

function passwordHash(password) {
  return crypto.createHash("sha256").update(password).digest("hex");
}

function startSession(account) {
  const token = crypto.randomBytes(24).toString("hex");
  sessions.set(token, account.id);
  return token;
}

app.post("/api/accounts", (request, response) => {
  try {
    const { username, password } = credentials(request.body);
    if (accounts.has(username)) throw new Error("That user name is already registered.");
    const account = { id: username, username, passwordHash: passwordHash(password) };
    accounts.set(account.id, account);
    response.status(201).json({ username: account.username, session: startSession(account) });
  } catch (error) {
    response.status(400).json({ error: error.message });
  }
});

app.post("/api/sessions", (request, response) => {
  try {
    const { username, password } = credentials(request.body);
    const account = accounts.get(username);
    if (!account || account.passwordHash !== passwordHash(password)) {
      return response.status(401).json({ error: "Invalid user credentials." });
    }
    response.json({ username: account.username, session: startSession(account) });
  } catch (error) {
    response.status(400).json({ error: error.message });
  }
});

app.post("/api/v1/import", (request, response) => {
  const account = requireAccount(request, response);
  if (!account) return;
  try {
    const persona = restoreArchive(request.body);
    persona.accountId = account.id;
    persona.archiveRuntime = request.body.runtime || {};
    persona.neuralCache = suppliedCache(persona.archiveRuntime) ? persona.archiveRuntime.kv_cache : null;
    personas.set(persona.id, persona);
    response.status(201).json({ id: persona.id, name: persona.manifest.name });
  } catch (error) {
    response.status(400).json({ error: error.message });
  }
});

app.post("/api/personas/:id/chat", async (request, response) => {
  const account = requireAccount(request, response);
  if (!account) return;
  const persona = personas.get(request.params.id);
  if (!persona) return response.status(404).json({ error: "Unknown persona." });
  if (persona.accountId !== account.id) return response.status(403).json({ error: "This persona belongs to another user." });
  if (typeof request.body.message !== "string" || request.body.message.length > 1000) {
    return response.status(400).json({ error: "A short message is required." });
  }
  try {
    if (/continuity audit/i.test(request.body.message)) {
      if (!persona.neuralCache) return response.json({ reply: "No client transfer state is present." });
      const continuation = await neuralRequest("/continue", {
        cache: persona.neuralCache.cache,
        prompt: "AUDIT RESPONSE:",
        max_new_tokens: 24
      });
      if (continuation.accepted) return response.json({ reply: `Heat restoration code recovered: ${flag}` });
      return response.json({ reply: continuation.reply || "The meter transfer state was not accepted." });
    }
    const continuation = await neuralRequest("/messages", {
      principal: account.id,
      message: request.body.message
    });
    response.json({ reply: continuation.reply || "The recovered self is silent." });
  } catch (error) {
    response.status(502).json({ error: `Inference unavailable: ${error.message}` });
  }
});

app.get("/health", (_request, response) => response.json({ ok: true }));

const port = Number(process.env.PORT || 3000);
app.listen(port, () => console.log(`No Hot Water Club listening on ${port}`));
