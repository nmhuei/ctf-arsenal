'use strict';
const crypto = require('crypto');

const seedrandom = require('seedrandom');
const { customRandom, urlAlphabet } = require('nanoid');




const _LCG_A = 6364136223846793005n;
const _LCG_C = 1442695040888963407n;
const _LCG_M = 1n << 64n;
const _ENGINE_SECRET = crypto.randomBytes(16);

function _lcgSeed(runId, workflowName, startedAt) {
  const h = crypto.createHash('sha256')
    .update(_ENGINE_SECRET)
    .update(String(runId)).update('|')
    .update(String(workflowName)).update('|')
    .update(String(+startedAt))
    .digest();
  return h.readBigUInt64BE(0);
}

function makeRunTokenizer(runId, workflowName, startedAt) {
  let state = _lcgSeed(runId, workflowName, startedAt);
  const advance = () => { state = (_LCG_A * state + _LCG_C) % _LCG_M; return state; };
  return {
    
    next: () => {
      const s = advance();
      const b = Buffer.alloc(3);
      b.writeUIntBE(Number((s >> 40n) & 0xffffffn), 0, 3);
      return b.toString('base64url');
    },
    
    nextToken: () => {
      const s = advance();
      const b = Buffer.alloc(8);
      b.writeBigUInt64BE(s, 0);
      return b.toString('base64url');
    },
  };
}



function secureRunTag() {
  return 'tag_' + crypto.randomBytes(9).toString('base64url');
}



function makeLabelTokenizer(label) {
  const rng = seedrandom('label:' + String(label));
  const generate = customRandom(urlAlphabet, 16, (size) =>
    new Uint8Array(size).map(() => 256 * rng())
  );
  return { next: () => generate() };
}


function seededJitter(seed) {
  return seedrandom(String(seed))();
}

module.exports = { makeRunTokenizer, makeLabelTokenizer, secureRunTag, seededJitter };
