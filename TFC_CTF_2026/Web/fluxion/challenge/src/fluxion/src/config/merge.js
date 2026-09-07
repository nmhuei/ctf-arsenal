'use strict';






const RESERVED_KEYS = new Set(['__proto__', 'prototype', 'constructor']);


function mergeConfig(dst, src) {
  if (!src || typeof src !== 'object') return dst;
  for (const k of Object.keys(src)) {
    if (RESERVED_KEYS.has(k)) continue;
    const v = src[k];
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      if (!dst[k] || typeof dst[k] !== 'object') dst[k] = {};
      mergeConfig(dst[k], v);
    } else {
      dst[k] = v;
    }
  }
  return dst;
}


function pickTunable(src, allow) {
  const out = {};
  if (!src || typeof src !== 'object') return out;
  for (const k of allow) if (Object.prototype.hasOwnProperty.call(src, k)) out[k] = src[k];
  return out;
}


function safeAssign(dst, src) {
  if (!src || typeof src !== 'object') return dst;
  for (const k of Object.keys(src)) {
    if (RESERVED_KEYS.has(k)) continue;
    dst[k] = src[k];
  }
  return dst;
}

module.exports = { mergeConfig, pickTunable, safeAssign };
