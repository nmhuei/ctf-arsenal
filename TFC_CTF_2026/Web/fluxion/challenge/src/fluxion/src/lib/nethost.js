'use strict';








const BLOCKED_HOST =
  /^(localhost|0\.0\.0\.0|127\.|10\.|192\.168\.|169\.254\.|::1|\[::1\]|fd[0-9a-f]{2}:|fe80:|metadata\.google\.internal|metadata\.goog)/i;

function isHttp(u) {
  return /^https?:\/\//i.test(String(u || ''));
}


function isPublicTarget(u) {
  try {
    const parsed = new URL(String(u));
    if (!/^https?:$/i.test(parsed.protocol)) return false;
    const host = parsed.hostname;
    if (BLOCKED_HOST.test(host)) return false;
    
    const m = /^172\.(\d+)\./.exec(host);
    if (m && Number(m[1]) >= 16 && Number(m[1]) <= 31) return false;
    
    if (/^\d+$/.test(host)) return false;
    return true;
  } catch {
    return false;
  }
}


function requirePublicTarget(u) {
  const url = String(u || '');
  if (!isHttp(url)) return { error: 'only http(s) targets' };
  if (!isPublicTarget(url)) return { error: 'target host is not routable' };
  return { ok: true, url };
}

module.exports = { isHttp, isPublicTarget, requirePublicTarget, BLOCKED_HOST };
