'use strict';







const { safeAssign } = require('../config/merge');

const conns = new Map(); 
const TYPES = new Set(['postgres', 'http', 'slack', 's3', 'smtp']);


function mask(v) {
  const s = String(v || '');
  if (s.length <= 4) return '••••';
  return '••••' + s.slice(-4);
}

function create(body) {
  const name = String((body && body.name) || '').trim();
  const type = String((body && body.type) || '').trim();
  if (!name) return { ok: false, error: 'name required' };
  if (!TYPES.has(type)) return { ok: false, error: 'unknown connection type' };
  
  const hint = mask((body && body.secret) || (body && body.value) || '');
  conns.set(name, { name, type, hint, createdAt: Date.now() });
  return { ok: true, name, type, hint };
}

function view(c) { return { name: c.name, type: c.type, hint: c.hint, createdAt: c.createdAt }; }


function get(name) {
  const c = conns.get(String(name));
  return c ? view(c) : null;
}

function update(name, patch) {
  const c = conns.get(String(name));
  if (!c) return { ok: false, error: 'no such connection' };
  const allowed = {};
  if (patch && typeof patch.type === 'string' && TYPES.has(patch.type)) allowed.type = patch.type;
  if (patch && ('secret' in patch || 'value' in patch)) allowed.hint = mask(patch.secret || patch.value);
  safeAssign(c, allowed);
  return { ok: true, connection: view(c) };
}

function list() { return [...conns.values()].map(view); }

function seedConnections() {
  create({ name: 'prod-postgres', type: 'postgres', secret: 'pg://redacted-at-rest' });
  create({ name: 'ops-slack', type: 'slack', secret: 'xoxb-redacted' });
  create({ name: 'archive-s3', type: 's3', secret: 'AKIA-redacted' });
}

module.exports = { create, get, update, list, seedConnections };
