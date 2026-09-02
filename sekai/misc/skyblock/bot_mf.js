// Skyblock bot using Mineflayer
const mineflayer = require('mineflayer');
const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const ts = Date.now();
const USERNAME = 'Fb' + (ts % 10000);
const PASSWORD = 'fb' + (ts % 1000);

const bot = mineflayer.createBot({
  host: HOST,
  port: PORT,
  username: USERNAME,
  password: PASSWORD,
  auth: 'offline',
  version: '26.1.2',
});

bot.on('login', () => {
  console.log('[LOGIN] OK, version:', bot.version);
});

bot.on('spawn', () => {
  console.log('[SPAWN] In game');

  // Send commands after a delay
  setTimeout(() => {
    console.log('[CMD] /skyblock');
    bot.chat('/skyblock');
  }, 3000);

  setTimeout(() => {
    console.log('[CMD] /coins');
    bot.chat('/coins');
  }, 6000);

  setTimeout(() => {
    console.log('[CMD] /hub');
    bot.chat('/hub');
  }, 10000);
});

bot.on('message', (message, position, sender) => {
  const txt = message.toString().replace(/[§\xa7][0-9a-fklmnor]/g, '').trim();
  if (txt) console.log('[MSG/' + position + ']', txt.substring(0, 300));
});

bot.on('kicked', (reason) => {
  console.log('[KICK]', reason.toString().substring(0, 300));
});

bot.on('error', (err) => {
  console.log('[ERR]', err.message.substring(0, 100));
});

bot.on('end', () => {
  console.log('[END]');
});

// Watch for dialog (AuthMe)
bot.on('packet', (data, meta) => {
  if (meta.name === 'show_dialog') {
    console.log('[DIALOG] AuthMe');
    bot._client.write('dialog_response', {
      dialogId: data.dialogId || '',
      action: 'register',
      data: { password: PASSWORD, confirm: PASSWORD }
    });
  }
});

setTimeout(() => process.exit(0), 25000);
