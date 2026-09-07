'use strict';

//
// Control-plane transport: POST /fcp speaks the binary Fluxion Control Protocol (FCP/1).
// A single request body is one frame; the response body is one reply frame. See lib/fcp.js
// for the wire format. GET /fcp returns a human-readable protocol banner for operators
// wiring up tooling.
//

const express = require('express');
const fcp = require('../lib/fcp');

const router = express.Router();

// Raw octet body for the binary transport (independent of the global json parser).
router.post('/', express.raw({ type: () => true, limit: '64kb' }), (req, res) => {
  const buf = Buffer.isBuffer(req.body) ? req.body : Buffer.alloc(0);
  let out;
  try {
    out = fcp.handle(buf);
  } catch (e) {
    // Never leak stack traces on the transport; emit a generic framed error.
    out = fcp.encodeFrame({ type: fcp.T_ERR, seq: 0, sid: 0, payload: Buffer.from('E_INTERNAL') });
  }
  res.set('content-type', 'application/octet-stream');
  res.status(200).send(out);
});

router.get('/', (req, res) => {
  res.json({
    proto: 'FCP/1',
    transport: 'application/octet-stream, one frame per request',
    frames: ['HELLO(0x01)', 'KEX(0x02)', 'TICK(0x04)', 'ARM(0x03)'],
    note: 'binary arming handshake for privileged provisioning runs; enrolled operator devices only. '
      + 'Arming requires completing a paced attestation ladder (TICK/TOCK) between KEX and ARM: '
      + 'a chained anti-abuse proof-of-presence with a mandatory minimum interval per rung.',
  });
});

module.exports = router;
