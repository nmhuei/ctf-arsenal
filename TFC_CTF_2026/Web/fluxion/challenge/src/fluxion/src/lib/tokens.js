'use strict';






const crypto = require('crypto');
const seedrandom = require('seedrandom');
const { customRandom, customAlphabet, urlAlphabet } = require('nanoid');


function secureToken(bytes = 24) {
  return crypto.randomBytes(bytes).toString('base64url');
}


const secureId = customAlphabet('0123456789abcdefghijklmnopqrstuvwxyz', 20);


const _deliveryKey = crypto.randomBytes(32);
function signDelivery(body) {
  return crypto.createHmac('sha256', _deliveryKey).update(String(body)).digest('hex');
}
function verifyDelivery(body, sig) {
  const expect = signDelivery(body);
  try { return crypto.timingSafeEqual(Buffer.from(expect), Buffer.from(String(sig))); }
  catch { return false; }
}



function cosmeticId(label) {
  const rng = seedrandom('ui:' + label);
  const gen = customRandom(urlAlphabet, 16, (n) => new Uint8Array(n).map(() => 256 * rng()));
  return gen();
}

module.exports = { secureToken, secureId, signDelivery, verifyDelivery, cosmeticId };
