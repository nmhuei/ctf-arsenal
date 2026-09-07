'use strict';



const { secureToken, secureId } = require('../lib/tokens');

const handlers = {
  
  mintApiKey: () => ({ apiKey: 'fx_' + secureToken(24), id: secureId() }),

  
  rotateWebhookSecret: () => ({ secret: secureToken(32), rotatedAt: Date.now() }),

  
  issueResumeGrant: () => ({ grant: secureToken(18), expiresInMs: 300_000 }),
};

module.exports = { handlers };
