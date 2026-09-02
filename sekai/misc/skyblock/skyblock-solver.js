/**
 * Full Skyblock solver using minecraft-protocol
 * Handles AuthMe registration, config state, PLAY state, and tradebook exploration
 */
const mc = require('minecraft-protocol');
const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const prefix = `B${Math.floor(Math.random() * 10000)}`;
const USERNAME = prefix;
const PASSWORD = `pw${Math.floor(Math.random() * 100000)}`;

let msgs = [];
let configDone = false;
let registered = false;

const client = mc.createClient({
  host: HOST,
  port: PORT,
  username: USERNAME,
  auth: 'offline',
  version: false,
});

client.on('session', () => {
  console.log(`[+] Connected as ${client.username}`);
});

client.on('keep_alive', () => {
  // auto-handled by library
});

client.on('login', (packet) => {
  console.log(`[+] Login OK`);
});

client.on('position', (packet) => {
  client.write('teleport_confirm', { teleportId: packet.teleportId });
});

// Handle AuthMe registration form
client.on('show_dialog', (packet) => {
  if (registered) return;
  registered = true;
  console.log(`[+] AuthMe form detected, registering with password: ${PASSWORD}`);

  // Build NBT manually (same format as working Python solve.py)
  function wvar(v) {
    const out = [];
    while (true) {
      if ((v & 0xFFFFFF80) === 0) { out.push(v & 0x7F); break; }
      out.push((v & 0x7F) | 0x80); v = (v >>> 7);
    }
    return Buffer.from(out);
  }
  function wstr(s) {
    const e = Buffer.from(s, 'utf-8');
    return Buffer.concat([wvar(e.length), e]);
  }

  const pwdBuf = Buffer.from(PASSWORD, 'utf-8');

  // Raw NBT: TAG_Compound(empty name) + password field + confirm field + TAG_End
  const nbtParts = [];
  nbtParts.push(Buffer.from([0x0a, 0x00, 0x00]));  // compound + empty name
  nbtParts.push(Buffer.from([0x08])); nbtParts.push(Buffer.from([0x00, 0x08])); nbtParts.push(Buffer.from('password'));
  nbtParts.push(Buffer.from([(pwdBuf.length >> 8) & 0xFF, pwdBuf.length & 0xFF])); nbtParts.push(pwdBuf);
  nbtParts.push(Buffer.from([0x08])); nbtParts.push(Buffer.from([0x00, 0x07])); nbtParts.push(Buffer.from('confirm'));
  nbtParts.push(Buffer.from([(pwdBuf.length >> 8) & 0xFF, pwdBuf.length & 0xFF])); nbtParts.push(pwdBuf);
  nbtParts.push(Buffer.from([0x00]));  // end
  const nbtBuf = Buffer.concat(nbtParts);

  const actionId = 'authme:prejoin-register/submit';
  // Full payload: actionId + varint(1+nbt_len) + 0x01 + nbt
  const payload = Buffer.concat([
    wstr(actionId),
    wvar(1 + nbtBuf.length),
    Buffer.from([0x01]),
    nbtBuf,
  ]);

  // Write raw packet: packet_id(0x08 varint) + payload
  client.writeRaw(Buffer.concat([wvar(0x08), payload]));
  console.log('[+] Registration submitted (raw format)');
});

client.on('system_chat', (packet) => {
  try {
    const msg = JSON.parse(packet.message);
    const text = extractText(msg);
    if (text) {
      msgs.push(text);
      console.log(`[C] ${text.slice(0, 400)}`);
    }
  } catch(e) {
    console.log(`[C RAW] ${packet.message.slice(0, 200)}`);
  }
});

client.on('chat', (packet) => {
  try {
    const msg = JSON.parse(packet.message);
    const text = extractText(msg);
    if (text) {
      msgs.push(text);
      console.log(`[P] ${text.slice(0, 400)}`);
    }
  } catch(e) {
    console.log(`[P RAW] ${packet.message.slice(0, 200)}`);
  }
});

client.on('action_bar', (packet) => {
  try {
    const msg = JSON.parse(packet.message);
    const text = extractText(msg);
    if (text) console.log(`[A] ${text.slice(0, 400)}`);
  } catch(e) {}
});

// Log ALL raw packets to understand what's happening
client.on('raw', (buffer, { name, state }) => {
  if (name === 'kick_disconnect') {
    console.log(`[RAW KICK] buffer hex=${buffer.slice(0, 100).toString('hex')}`);
    console.log(`[RAW KICK] buffer str=${buffer.slice(0, 100).toString('utf-8')}`);
  }
});

client.on('kick_disconnect', (packet) => {
  console.log(`[KICK] full packet keys: ${Object.keys(packet)}`);
  console.log(`[KICK] full packet json: ${JSON.stringify(packet, (k, v) => {
    if (k === 'reason' && v && typeof v === 'object') {
      try {
        const nbt = require('prismarine-nbt');
        return JSON.stringify(nbt.simplify(v));
      } catch(e) { return '[NBT:' + Object.keys(v).join(',') + ']'; }
    }
    return v;
  }).slice(0, 500)}`);
  try {
    if (typeof packet.reason === 'object') {
      const nbt = require('prismarine-nbt');
      const simple = nbt.simplify(packet.reason);
      console.log(`[KICK] NBT simplified: ${JSON.stringify(simple).slice(0, 400)}`);
    } else if (typeof packet.reason === 'string') {
      try {
        const msg = JSON.parse(packet.reason);
        console.log(`[KICK] ${extractText(msg)}`);
      } catch(e) {
        console.log(`[KICK] raw string: ${packet.reason.slice(0, 300)}`);
      }
    }
  } catch(e) {
    console.log(`[KICK] error: ${e.message}`);
  }
});

client.on('end', (reason) => {
  console.log(`[END] ${reason}`);
  showResults();
});

client.on('error', (err) => {
  console.log(`[ERR] ${err.message}`);
});

client.on('finish_configuration', () => {
  console.log('[+] finish_configuration received - entering PLAY state');
  configDone = true;
});

client.on('state', (newState) => {
  console.log(`[STATE] -> ${newState}`);
  if (newState === 'play') {
    configDone = true;
    // Send commands after a delay
    const cmds = ['coins', 'tradebook help', 'tradebook list', 'shop', 'leaderboard'];

    cmds.forEach((cmd, i) => {
      setTimeout(() => {
        if (client.state === 'play') {
          console.log(`[CMD] /${cmd}`);
          try {
            client.write('chat_command', { command: cmd });
            console.log(`  OK`);
          } catch(e) {
            console.log(`[ERR] ${cmd}: ${e.message}`);
          }
        }
      }, 10000 + i * 5000);
    });
  }
});

// Stay alive for 60s
setTimeout(() => {
  console.log(`\n=== Done: ${msgs.length} messages ===`);
  msgs.forEach(m => console.log(`  ${m.slice(0, 300)}`));
  client.end();
  process.exit(0);
}, 70000);

function extractText(node) {
  if (!node) return '';
  if (typeof node === 'string') return node;
  if (node.text) return node.text;
  if (Array.isArray(node.extra)) {
    return node.extra.map(extractText).join('');
  }
  if (node.translate) {
    const args = (node.with || []).map(extractText);
    return `${node.translate} ${args.join(' ')}`.trim();
  }
  return '';
}

function showResults() {
  console.log(`\n=== ${msgs.length} messages ===`);
  msgs.forEach(m => console.log(`  ${m.slice(0, 300)}`));
  for (const m of msgs) {
    const low = m.toLowerCase();
    if (low.includes('sekai') || low.includes('flag') || low.includes('tbctf') || low.includes('ctf{')) {
      console.log(`\n*** FLAG: ${m} ***`);
    }
  }
}
