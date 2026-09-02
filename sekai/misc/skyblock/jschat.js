// Direct minecraft-protocol chat test with AuthMe bypass
const mc = require('minecraft-protocol');

const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const ts = Date.now();
const USERNAME = 'J' + (ts % 10000);
const PASSWORD = 'pw' + (ts % 1000);

const client = mc.createClient({
  host: HOST,
  port: PORT,
  username: USERNAME,
  password: PASSWORD,
  protocolVersion: 775,  // Paper 26.1.2
  auth: 'offline',
  skipValidation: true,
  version: false,
  // Work around unknown packets
});

// Track state
let configDone = false;
let registered = false;

// Handle raw packets in config state
client.on('packet', (data, meta, raw) => {
  if (meta.name === 'show_dialog') {
    console.log('[DIALOG] AuthMe dialog received');
    // Respond with registration
    setTimeout(() => {
      client.write('dialog_response', {
        dialogId: data.dialogId || '',
        action: 'register',
        data: {
          password: PASSWORD,
          confirm: PASSWORD
        }
      });
    }, 500);
  }
  if (meta.name === 'login') {
    console.log('[LOGIN] Entered PLAY state');
    configDone = true;
    setTimeout(() => {
      console.log('[CHAT] Sending /coins');
      client.chat('/coins');
    }, 3000);
  }
  if (meta.name === 'finish_configuration') {
    console.log('[CONFIG] Done');
  }
  if (meta.name === 'system_chat' || meta.name === 'chat') {
    const text = typeof data === 'object' ? JSON.stringify(data).substring(0, 200) : String(data).substring(0, 200);
    console.log('[CHAT]', text);
  }
});

// Handle disconnect
client.on('disconnect', (packet) => {
  console.log('[DISCONNECT]', JSON.stringify(packet).substring(0, 200));
  process.exit(1);
});

client.on('error', (err) => {
  console.log('[ERROR]', err.message.substring(0, 100));
});

client.on('end', () => {
  console.log('[END]');
  process.exit(0);
});

// Timeout
setTimeout(() => {
  console.log('[TIMEOUT]');
  process.exit(0);
}, 20000);
