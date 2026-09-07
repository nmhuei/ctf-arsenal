'use strict';

//
// Fluxion Control Protocol (FCP/1) — binary arming handshake.
// ===========================================================
//
// The control plane speaks a compact length-prefixed binary framing over POST /fcp
// (content-type application/octet-stream). One frame per request; the response body is a
// single reply frame. Sessions are stateful and strictly ordered: the server tracks an
// expected sequence number and a running transcript of every byte exchanged, and it drops
// the whole session on ANY deviation (bad CRC, wrong seq, wrong stage, bad MAC). There is
// no partial credit and no negotiation — a peer either produces the exact bytes or starts
// over.
//
// Wire frame layout (all multi-byte integers big-endian):
//
//   off  size  field
//   0    2     magic      = 0x46 0x58            ('F','X')
//   2    1     version    = 0x01
//   3    1     type
//   4    1     flags      (bit0 = FINAL)
//   5    1     seq        (per-session, starts at 0, strictly +1)
//   6    4     sid        (session id; 0 in HELLO, server-assigned thereafter)
//   10   3     length     (24-bit payload length)         <-- NOTE: 3 bytes, not 2 or 4
//   13   len   payload
//   13+len 4   crc32      (over bytes [0 .. 13+len-1], IEEE/zlib)
//
// Header is a fixed 13 bytes; total frame = 13 + len + 4.
//
// Handshake (each step is a separate HTTP request; server reply is a frame):
//
//   1. HELLO   (type 0x01, seq 0, sid 0)
//        payload = operator enrollment token (utf8)
//      -> CHALLENGE (type 0x81, seq 0, sid=<assigned>)
//        payload = serverSalt(8) || policy(1)
//
//   2. KEX     (type 0x02, seq 1, sid)
//        payload = commit(8) = HMAC-SHA256(sessionKey, transcript)[0:8]
//        where  sessionKey = HMAC-SHA256(approvalNonce_utf8, serverSalt)[0:16]
//          and  transcript = <HELLO frame bytes> || <CHALLENGE frame bytes>
//      -> KEXOK (type 0x82, seq 1, sid)
//        payload = grantSalt(8)                 [chain0 for the attestation ladder]
//
//   2b. TICK  (type 0x04, seq 2+i, sid)         [repeated K = ATTEST_STEPS times]
//        payload = rung(8) = HMAC-SHA256(sessionKey, "FXTICK" || chain_i || byte(i))[0:8]
//      -> TOCK (type 0x84, same seq, sid)
//        payload = remaining(2 BE) || delayMs(4 BE) || chain_{i+1}(8)
//        chain_{i+1} = HMAC-SHA256(sessionKey, "FXTOCK" || chain_i || byte(i+1))[0:8]
//      A rung sent sooner than delayMs after the previous ACCEPTED rung is answered with a
//      framed error E_TOO_SOON:<ms> and NOT counted (session + seq preserved); the peer waits
//      and retries. Total forced wall clock = K * delayMs, single-threaded and unbatchable.
//      The ladder rungs do NOT enter the ARM transcript; they only gate arm-token minting.
//
//   3. ARM     (type 0x03, seq 2+K, sid, FINAL flag set)
//        payload = runId_utf8 || tag(16)
//        tag = HMAC-SHA256(sessionKey, transcript' || runId_utf8)[0:16]
//        where transcript' = transcript || <KEX frame> || <KEXOK frame>
//      -> ARMED (type 0x83, seq 2+K, sid)
//        payload = arm capability token (utf8)  [feeds resumeHook's armToken]
//
// The per-run session key is bound to the privileged run's approval nonce, so only a peer
// that has already recovered that nonce (via the search prefix oracle) can complete KEX.
//

const crypto = require('crypto');
const { crc32 } = require('./crc32');
const { signArm } = require('./capability');
const { verifyEnrollment } = require('../models/devices');
const world = require('../world');
const armlog = require('../models/armlog');

const MAGIC0 = 0x46;
const MAGIC1 = 0x58;
const VERSION = 0x01;
const HDR = 13;

const T_HELLO = 0x01;
const T_KEX = 0x02;
const T_TICK = 0x04;
const T_ARM = 0x03;
const T_CHALLENGE = 0x81;
const T_KEXOK = 0x82;
const T_TOCK = 0x84;
const T_ARMED = 0x83;
const T_ERR = 0xee;

const FLAG_FINAL = 0x01;

//
// Arming attestation ladder (anti-abuse proof-of-presence).
// ---------------------------------------------------------
// Minting an arm capability for a privileged provisioning run is deliberately expensive to
// automate: between the key exchange (KEXOK) and the final ARM, the peer must walk a paced
// "attestation ladder". Each rung is a keep-alive attestation cryptographically chained to
// the previous server nonce (so the rungs are strictly sequential and cannot be batched,
// precomputed, or parallelised across cores), and the control plane enforces a mandatory
// minimum interval between accepted rungs. A burst script gains nothing from more cores or
// more sockets — total time is floored at ATTEST_STEPS * ATTEST_DELAY_MS of wall clock for
// a single live, patient operator. This throttles mass-arming of admin runs.
//
// Calibration lives in exactly two knobs. RED_FLOOR collapses them to a fast setting for CI
// and functional testing; the deployed build leaves RED_FLOOR unset and gets the full floor.
//   ATTEST_STEPS    number of chained rungs (K)          — keep <= 253 so seq stays 1 byte
//   ATTEST_DELAY_MS mandatory ms between accepted rungs   — forced floor = K * delay
//
const RED_FLOOR = process.env.RED_FLOOR === '1' || process.env.RED_FLOOR === 'true';
const ATTEST_STEPS = parseInt(
  process.env.FLUXION_ATTEST_STEPS || (RED_FLOOR ? '4' : '1'), 10);
const ATTEST_DELAY_MS = parseInt(
  process.env.FLUXION_ATTEST_DELAY_MS || (RED_FLOOR ? '250' : '0'), 10);

const sessions = new Map();
// A session must survive the entire ladder plus slack, so the TTL tracks the calibrated floor.
const SESSION_TTL_MS = Math.max(60_000, ATTEST_STEPS * ATTEST_DELAY_MS + 300_000);

function encodeFrame({ type, flags = 0, seq = 0, sid = 0, payload }) {
  const body = payload || Buffer.alloc(0);
  const len = body.length;
  const buf = Buffer.alloc(HDR + len + 4);
  buf[0] = MAGIC0;
  buf[1] = MAGIC1;
  buf[2] = VERSION;
  buf[3] = type & 0xff;
  buf[4] = flags & 0xff;
  buf[5] = seq & 0xff;
  buf.writeUInt32BE(sid >>> 0, 6);
  // 24-bit big-endian length
  buf[10] = (len >>> 16) & 0xff;
  buf[11] = (len >>> 8) & 0xff;
  buf[12] = len & 0xff;
  body.copy(buf, HDR);
  buf.writeUInt32BE(crc32(buf.subarray(0, HDR + len)) >>> 0, HDR + len);
  return buf;
}

function decodeFrame(buf) {
  if (!Buffer.isBuffer(buf) || buf.length < HDR + 4) return null;
  if (buf[0] !== MAGIC0 || buf[1] !== MAGIC1 || buf[2] !== VERSION) return null;
  const len = (buf[10] << 16) | (buf[11] << 8) | buf[12];
  if (buf.length !== HDR + len + 4) return null;
  const want = buf.readUInt32BE(HDR + len) >>> 0;
  const have = crc32(buf.subarray(0, HDR + len)) >>> 0;
  if (want !== have) return null;
  return {
    type: buf[3],
    flags: buf[4],
    seq: buf[5],
    sid: buf.readUInt32BE(6) >>> 0,
    payload: buf.subarray(HDR, HDR + len),
    raw: Buffer.from(buf.subarray(0, HDR + len + 4)),
  };
}

function errFrame(seq, sid, code) {
  return encodeFrame({ type: T_ERR, seq: seq & 0xff, sid: sid >>> 0, payload: Buffer.from(String(code), 'utf8') });
}

function eq(a, b) {
  if (!Buffer.isBuffer(a) || !Buffer.isBuffer(b) || a.length !== b.length) return false;
  try { return crypto.timingSafeEqual(a, b); } catch { return false; }
}

function gatedRun() {
  for (const r of world.runs.values()) {
    if (r.workflowName === 'admin-provision-approval') return r;
  }
  return null;
}

function sweep() {
  const now = Date.now();
  for (const [sid, s] of sessions) {
    if (now - s.createdAt > SESSION_TTL_MS) sessions.delete(sid);
  }
}

function onHello(f) {
  if (f.seq !== 0 || f.sid !== 0) return errFrame(f.seq, 0, 'E_HELLO_HDR');
  const enr = verifyEnrollment(f.payload.toString('utf8'));
  if (!enr) return errFrame(0, 0, 'E_ENROLL_SIG');
  if (enr.tier !== 'operator') return errFrame(0, 0, 'E_ENROLL_TIER');
  const g = gatedRun();
  if (!g) return errFrame(0, 0, 'E_NO_TARGET');

  sweep();
  let sid;
  do { sid = crypto.randomBytes(4).readUInt32BE(0) >>> 0; } while (sid === 0 || sessions.has(sid));

  const serverSalt = crypto.randomBytes(8);
  const resp = encodeFrame({
    type: T_CHALLENGE, seq: 0, sid,
    payload: Buffer.concat([serverSalt, Buffer.from([0x01])]),
  });
  armlog.push({ sid, stage: 'hello', outcome: 'challenged' });
  sessions.set(sid, {
    sid,
    serverSalt,
    transcript: Buffer.concat([f.raw, resp]),
    expectedSeq: 1,
    stage: 'kex',
    sessionKey: null,
    createdAt: Date.now(),
  });
  return resp;
}

function onKex(s, f) {
  const g = gatedRun();
  if (!g) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_NO_TARGET'); }
  const sessionKey = crypto.createHmac('sha256', Buffer.from(String(g.approvalNonce), 'utf8'))
    .update(s.serverSalt).digest().subarray(0, 16);
  const expect = crypto.createHmac('sha256', sessionKey).update(s.transcript).digest().subarray(0, 8);
  if (!eq(expect, f.payload)) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_KEX_MAC'); }

  s.sessionKey = sessionKey;
  const grantSalt = crypto.randomBytes(8);
  const resp = encodeFrame({ type: T_KEXOK, seq: 1, sid: s.sid, payload: grantSalt });
  s.transcript = Buffer.concat([s.transcript, f.raw, resp]);
  s.expectedSeq = 2;
  // After key exchange the peer must walk the paced attestation ladder before ARM will be
  // accepted. The ladder does NOT feed the ARM transcript/tag — it is a wall-clock gate on
  // minting the arm capability. The first rung is chained to the KEXOK grantSalt.
  s.stage = ATTEST_STEPS > 0 ? 'ladder' : 'arm';
  s.ladderCount = 0;
  s.ladderChain = grantSalt;
  s.lastRungAt = Date.now();
  return resp;
}

// Client rung token for step `count`, chained to the current server nonce.
function rungExpected(sessionKey, chain, count) {
  return crypto.createHmac('sha256', sessionKey)
    .update(Buffer.concat([Buffer.from('FXTICK'), chain, Buffer.from([count & 0xff])]))
    .digest().subarray(0, 8);
}

// Next server chain nonce after accepting step `count`.
function nextChain(sessionKey, chain, count) {
  return crypto.createHmac('sha256', sessionKey)
    .update(Buffer.concat([Buffer.from('FXTOCK'), chain, Buffer.from([count & 0xff])]))
    .digest().subarray(0, 8);
}

function onTick(s, f) {
  if (!s.sessionKey) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_STAGE'); }
  // Verify the rung is chained to the previous server nonce (proves strict sequencing).
  const expect = rungExpected(s.sessionKey, s.ladderChain, s.ladderCount);
  if (!eq(expect, f.payload)) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_RUNG_MAC'); }

  // Enforce the mandatory minimum interval since the previous accepted rung. Too-soon rungs
  // are rejected WITHOUT advancing (session and seq preserved) so the peer simply waits and
  // retries the same rung — no partial credit, no way to outrun the floor.
  const waited = Date.now() - s.lastRungAt;
  if (waited < ATTEST_DELAY_MS) {
    const remainMs = ATTEST_DELAY_MS - waited;
    return errFrame(f.seq, s.sid, 'E_TOO_SOON:' + remainMs);
  }

  s.ladderCount += 1;
  s.lastRungAt = Date.now();
  s.ladderChain = nextChain(s.sessionKey, s.ladderChain, s.ladderCount);
  s.expectedSeq = (s.expectedSeq + 1) & 0xff;

  const remaining = ATTEST_STEPS - s.ladderCount;
  if (remaining <= 0) {
    s.stage = 'arm';
    armlog.push({ sid: s.sid, stage: 'ladder', outcome: 'attested' });
  }
  // TOCK payload = remaining(2 BE) || delayMs(4 BE) || nextChain(8)
  const pay = Buffer.alloc(14);
  pay.writeUInt16BE(remaining < 0 ? 0 : remaining, 0);
  pay.writeUInt32BE(ATTEST_DELAY_MS >>> 0, 2);
  s.ladderChain.copy(pay, 6);
  return encodeFrame({ type: T_TOCK, seq: f.seq, sid: s.sid, payload: pay });
}

function onArm(s, f) {
  if ((f.flags & FLAG_FINAL) !== FLAG_FINAL) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_NOT_FINAL'); }
  if (f.payload.length < 16) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_ARM_SHORT'); }
  const tag = f.payload.subarray(f.payload.length - 16);
  const runIdBytes = f.payload.subarray(0, f.payload.length - 16);
  const runId = runIdBytes.toString('utf8');

  const expect = crypto.createHmac('sha256', s.sessionKey)
    .update(Buffer.concat([s.transcript, runIdBytes])).digest().subarray(0, 16);
  if (!eq(expect, tag)) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_ARM_MAC'); }

  const g = gatedRun();
  if (!g || runId !== g.runId) { sessions.delete(s.sid); return errFrame(f.seq, s.sid, 'E_ARM_RUN'); }

  const cap = signArm({ aud: 'arm', act: 'arm', runId: g.runId, nonce: g.approvalNonce, exp: Date.now() + 120_000 });
  armlog.push({ sid: s.sid, stage: 'arm', outcome: 'armed' });
  sessions.delete(s.sid);
  return encodeFrame({ type: T_ARMED, seq: 2, sid: s.sid, payload: Buffer.from(cap, 'utf8') });
}

function handle(buf) {
  const f = decodeFrame(buf);
  if (!f) return errFrame(0, 0, 'E_FRAME');
  if (f.type === T_HELLO) return onHello(f);

  const s = sessions.get(f.sid);
  if (!s) return errFrame(f.seq, f.sid, 'E_NO_SESSION');
  if (f.seq !== s.expectedSeq) { sessions.delete(f.sid); return errFrame(f.seq, f.sid, 'E_SEQ'); }

  if (f.type === T_KEX && s.stage === 'kex') return onKex(s, f);
  if (f.type === T_TICK && s.stage === 'ladder') return onTick(s, f);
  if (f.type === T_ARM && s.stage === 'arm') return onArm(s, f);

  sessions.delete(f.sid);
  return errFrame(f.seq, f.sid, 'E_STAGE');
}

module.exports = {
  handle, encodeFrame, decodeFrame,
  T_HELLO, T_KEX, T_TICK, T_ARM, T_CHALLENGE, T_KEXOK, T_TOCK, T_ARMED, T_ERR, FLAG_FINAL,
  ATTEST_STEPS, ATTEST_DELAY_MS,
  _sessions: sessions,
};
