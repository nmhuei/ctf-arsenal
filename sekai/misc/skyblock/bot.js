const mineflayer = require('mineflayer');

const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const PASSWORD = process.argv[2] || 'botpass123';
const USERNAME = process.argv[3] || 'Bot' + Math.floor(Math.random() * 9999);
const BASE_VERSION = '1.21.11';

const log = (msg) => process.stdout.write(msg + '\n');

function createBot(name, pass) {
  const bot = mineflayer.createBot({
    host: HOST,
    port: PORT,
    username: name,
    version: BASE_VERSION,
    hideErrors: false,
    forcedProtocolVersion: 775,
  });

  let registered = false;

  setImmediate(() => {
    bot._client.on('connect', () => log('[TCP] Connected'));
    bot._client.on('state', (s) => log(`[STATE] ${s}`));
    bot._client.on('packet', (data, meta) => {
      if (['disconnect', 'show_dialog', 'finish_configuration', 'login'].includes(meta.name)) {
        log(`[PKT] ${meta.name}`);
      }

      // Handle registration dialog
      if (meta.name === 'show_dialog') {
        const actions = data?.dialog?.value?.actions?.value?.value || [];
        const inputs = data?.dialog?.value?.inputs?.value?.value || [];
        const title = data?.dialog?.value?.title?.value?.text?.value || 'Unknown';
        log(`[DIALOG] Title: ${title}`);
        log(`[DIALOG] Actions: ${actions.map(a => a?.label?.value?.text?.value || a?.action?.value?.id?.value).join(', ')}`);
        log(`[DIALOG] Inputs: ${inputs.map(i => i?.key?.value).join(', ')}`);

        // If there's a Register action with password inputs
        const registerAction = actions.find(a =>
          a?.action?.value?.id?.value?.includes('register/submit') ||
          a?.action?.value?.id?.value?.includes('register')
        );

        if (registerAction && inputs.length > 0 && !registered) {
          log('[DIALOG] Registering...');
          registered = true;

          // Build NBT form data
          const nbtValue = {};
          for (const input of inputs) {
            const key = input?.key?.value;
            const label = input?.label?.value?.text?.value || key;
            log(`[DIALOG] Input field: ${key} (${label})`);
            nbtValue[key] = { type: 'string', value: pass };
          }

          bot._client.write('custom_click_action', {
            id: registerAction.action.value.id.value,
            nbt: {
              type: 'compound',
              value: nbtValue
            }
          });
          log('[DIALOG] Registration submitted, waiting for response...');
        } else if (registered) {
          log('[DIALOG] Already registered, maybe success dialog');
          // Try sending finish_configuration
          bot._client.write('finish_configuration', {});
        }
      }

      if (meta.name === 'finish_configuration') {
        log('[CONFIG] Finish config received!');
      }

      if (meta.name === 'disconnect') {
        try {
          const reason = data?.reason;
          const text = reason?.value?.text?.value || reason?.value?.translate || JSON.stringify(reason).slice(0, 500);
          log(`[DC] Reason: ${text}`);
        } catch(e) {
          log(`[DC] Raw: ${JSON.stringify(data).slice(0, 300)}`);
        }
      }
    });
    bot._client.on('error', (err) => log(`[CLIENT_ERR] ${err.message}`));
  });

  bot.on('login', () => log(`[${name}] Logged in!`));
  bot.once('spawn', () => {
    log(`[${name}] SPAWNED! Pos: ${bot.entity?.position}`);
    setTimeout(() => bot.chat('/tradebook'), 2000);
    setTimeout(() => bot.chat('/tradebook help'), 4000);
    setTimeout(() => bot.chat('/tradebook list'), 6000);
    setTimeout(() => bot.chat('/bal'), 8000);
    setTimeout(() => bot.chat('/money'), 10000);
  });

  bot.on('chat', (username, message) => {
    if (username !== name) log(`[${name}] <${username}> ${message}`);
  });

  bot.on('message', (json) => {
    try {
      const text = json?.toString?.() || '';
      if (text && !text.startsWith('<') && !text.startsWith('[')) {
        log(`[${name}] MSG: ${text.slice(0, 300)}`);
        if (/flag|SEKAI|ctf/i.test(text)) log(`[${name}] FLAG?: ${text}`);
      }
    } catch(e) {}
  });

  bot.on('error', (err) => log(`[${name}] Error: ${err.message}`));
  bot.on('kicked', (reason) => {
    let msg = 'N/A';
    try {
      if (typeof reason === 'object') {
        const text = reason?.text || reason?.extra?.[0]?.text || reason?.translate || JSON.stringify(reason);
        msg = text;
      } else {
        msg = reason?.toString?.() || 'N/A';
      }
    } catch(e) {}
    log(`[${name}] Kicked: ${msg}`);
  });
  bot.on('end', (reason) => log(`[${name}] DC: ${reason}`));

  return bot;
}

const bot = createBot(USERNAME, PASSWORD);
setInterval(() => { try { bot.chat(''); } catch(e) {} }, 30000);
