const mineflayer = require('mineflayer');

const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const USERNAME = 'ArbBot_' + Math.floor(Math.random() * 10000);

const bot = mineflayer.createBot({
  host: HOST,
  port: PORT,
  username: USERNAME,
  auth: 'offline',
  version: '26.1.2',
});

let chatMessages = [];

bot.on('login', () => {
  console.log('[LOGIN] Connected! Username:', bot.username);
  console.log('[GAME]', JSON.stringify(bot.game || {}));
});

bot.on('message', (message) => {
  const text = message.toString();
  chatMessages.push(text);
  console.log('[CHAT]', text);
});

bot.on('kicked', (reason) => {
  console.log('[KICKED]', JSON.stringify(reason));
});

bot.on('error', (err) => {
  console.log('[ERROR]', err);
});

bot.on('end', () => {
  console.log('[END] Disconnected');
  console.log('\n=== All chat messages received ===');
  chatMessages.forEach((m, i) => console.log(`  ${i+1}. ${m}`));
});

// Wait 4 seconds, then start exploring
setTimeout(async () => {
  console.log('\n=== Starting exploration ===\n');

  // Try various commands to understand the economy
  const commands = [
    '/tradebook',
    '/tradebook help',
    '/tradebook list',
    '/help',
    '/bal',
    '/balance',
    '/money',
    '/eco',
    '/trade',
    '/shop',
    '/shop help',
  ];

  for (let i = 0; i < commands.length; i++) {
    await new Promise(r => setTimeout(r, 2000));
    console.log(`\n[CMD ${i+1}/${commands.length}] Sending: ${commands[i]}`);
    bot.chat(commands[i]);
  }

  // Wait for responses
  await new Promise(r => setTimeout(r, 20000));
  console.log('\n=== Done with exploration ===');
  bot.end();
}, 5000);
