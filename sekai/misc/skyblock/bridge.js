// Minecraf bot — JS bridge with correct settings
const mc = require('minecraft-protocol');
const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const ts = Date.now();
const USERNAME = 'Rb' + (ts % 10000);
const PASSWORD = 'rb' + (ts % 1000);

const client = mc.createClient({
  host: HOST, port: PORT,
  username: USERNAME, password: PASSWORD,
  protocolVersion: 775,
  auth: 'offline', skipValidation: true, version: false,
});

// Override settings to match Paper 26.1.2 with particleStatus
// Remove default settings handler, add ours
client.on('packet', (data, meta, raw) => {
  if (meta.name === 'finish_configuration') {
    console.log('[CONFIG] sending settings...');
    // Send settings with particleStatus (0=all)
    client.write('settings', {
      locale: 'en_US',
      viewDistance: 12,
      chatFlags: 0,
      chatColors: true,
      skinParts: 0x7F,
      mainHand: 1,
      enableTextFiltering: false,
      enableServerListing: true,
      particleStatus: 0,
    });
  }
  if (meta.name === 'show_dialog') {
    console.log('[DIALOG] registering...');
    client.write('dialog_response', {
      dialogId: data.dialogId || '',
      action: 'register',
      data: { password: PASSWORD, confirm: PASSWORD }
    });
  }
  if (meta.name === 'login') {
    console.log('[LOGIN] PLAY state');
    setTimeout(() => {
      console.log('[CMD] /help');
      client.write('chat_command', { command: 'help' });
    }, 5000);
    setTimeout(() => {
      console.log('[CMD] /hub');
      client.write('chat_command', { command: 'hub' });
    }, 10000);
  }
  if (meta.name === 'player_chat' || meta.name === 'system_chat' || meta.name === 'profileless_chat') {
    let txt = '';
    if (typeof data.message === 'object') {
      try { txt = data.message.text || JSON.stringify(data.message); } catch(e) { txt = String(data.message); }
    } else {
      txt = String(data.message || data.content || '');
    }
    txt = txt.replace(/[§\xa7][0-9a-fklmnor]/g, '').replace(/[^\x20-\x7e]/g, '').trim();
    if (txt) console.log('[CHAT]', txt.substring(0, 300));
  }
  if (meta.name === 'keep_alive') {
    client.write('keep_alive', { keepAliveId: data.keepAliveId });
  }
  if (meta.name === 'position') {
    client.write('teleport_confirm', { teleportId: data.teleportId });
  }
  if (meta.name === 'ping') {
    client.write('pong', {});
  }
  if (meta.name === 'map_chunk') {
    client.write('chunk_batch_received', { chunksPerTick: 1.0 });
  }
});

client.on('disconnect', (packet) => {
  console.log('[KICK]', JSON.stringify(packet).substring(0, 300));
});

client.on('error', (err) => {
  console.log('[ERR]', err.message.substring(0, 100));
});

client.on('end', () => console.log('[END]'));

setTimeout(() => process.exit(0), 20000);
