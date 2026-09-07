'use strict';




const { optString } = require('../lib/validate');

function httpOnly(u) { return /^https?:\/\//i.test(u); }



const BLOCKED_HOST = /^(localhost|0\.0\.0\.0|127\.|10\.|192\.168\.|169\.254\.|::1|\[::1\]|metadata\.google\.internal)/i;
function publicTarget(u) {
  try {
    const host = new URL(u).hostname;
    if (BLOCKED_HOST.test(host)) return false;
    const m = /^172\.(\d+)\./.exec(host);
    if (m && Number(m[1]) >= 16 && Number(m[1]) <= 31) return false;
    if (/^\d+$/.test(host)) return false;   
    return true;
  } catch { return false; }
}

const handlers = {
  
  pingTarget: async (p) => {
    const u = optString(p.url);
    if (!httpOnly(u)) return { error: 'only http(s) targets' };
    if (!publicTarget(u)) return { error: 'target host is not routable' };
    try {
      const r = await fetch(u, { method: 'GET' });
      return { url: u, status: r.status, ok: r.ok };
    } catch (e) { return { error: String((e && e.message) || e) }; }
  },

  
  fetchManifest: async (p) => {
    const u = optString(p.url);
    if (!httpOnly(u)) return { error: 'only http(s) targets' };
    if (!publicTarget(u)) return { error: 'target host is not routable' };
    try {
      const r = await fetch(u, { method: 'GET' });
      const body = (await r.text()).slice(0, 512);
      return { url: u, status: r.status, preview: body };
    } catch (e) { return { error: String((e && e.message) || e) }; }
  },
};

module.exports = { handlers };
