"use strict";
const crypto = require("crypto");

const SERVER_SECRET = process.env.SERVER_SECRET;
const FLAG_TEMPLATE = process.env.FLAG_TEMPLATE;
const MAX_HANDLE_LENGTH = 64;
const TEAM_CACHE_MAX = parseInt(process.env.LIKENESS_TEAM_CACHE_MAX || "512", 10);

if (!SERVER_SECRET) {
  throw new Error("SERVER_SECRET must be set");
}
if (!FLAG_TEMPLATE || !FLAG_TEMPLATE.includes("$1")) {
  throw new Error("FLAG_TEMPLATE must be set and contain $1");
}

const RESERVED_HANDLES = ["archivist"];

/**
 * Deterministic, not random: the same team always gets the same value back
 * across reconnects and across this team's registration being evicted and
 * needing to be redone later.
 */
function flagForTeam(team) {
  const token = crypto
    .createHmac("sha256", SERVER_SECRET)
    .update(`${team}|flag`)
    .digest("hex")
    .slice(0, 32);
  return FLAG_TEMPLATE.replace("$1", token);
}

function isReservedForRegistration(handle) {
  return RESERVED_HANDLES.includes(handle.toLowerCase());
}

function isRecognizedAsArchivist(handle) {
  return RESERVED_HANDLES.includes(handle.normalize("NFKC").toLowerCase());
}

// Bounded FIFO cache -- Map preserves insertion order, so the oldest entry
// is always registry.keys().next().value.
const registry = new Map();

function registerHandle(team, handle) {
  if (typeof handle !== "string" || handle.length === 0 || handle.length > MAX_HANDLE_LENGTH) {
    return { ok: false, error: `handle must be 1-${MAX_HANDLE_LENGTH} characters` };
  }
  if (isReservedForRegistration(handle)) {
    return { ok: false, error: "that handle is reserved" };
  }
  if (!registry.has(team) && registry.size >= TEAM_CACHE_MAX) {
    const oldestKey = registry.keys().next().value;
    registry.delete(oldestKey);
  }
  registry.set(team, handle);
  return { ok: true };
}

function getHandle(team) {
  return registry.get(team) || null;
}

module.exports = {
  flagForTeam,
  registerHandle,
  getHandle,
  isRecognizedAsArchivist,
};
