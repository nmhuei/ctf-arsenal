// Direct socket: handshake, config (raw), then PLAY chat
const mc = require('minecraft-protocol');
const net = require('net');
const zlib = require('zlib');

const HOST = 'skyblock.chals.sekai.team';
const PORT = 25565;
const PV = 775;
const USERNAME = 'Cb' + (Date.now() % 10000);
const PASSWORD = 'cb' + (Date.now() % 1000);

// Just need PLAY serializer for chat
const playSer = mc.createSerializer({state: mc.states.PLAY, isServer: false, version: PV});
const playDeser = mc.createDeserializer({state: mc.states.PLAY, isServer: true, version: PV});
const loginSer = mc.createSerializer({state: mc.states.LOGIN, isServer: false, version: PV});
const loginDeser = mc.createDeserializer({state: mc.states.LOGIN, isServer: true, version: PV});
const configSer = mc.createSerializer({state: mc.states.CONFIGURATION, isServer: false, version: PV});
const configDeser = mc.createDeserializer({state: mc.states.CONFIGURATION, isServer: true, version: PV});

let compression = -1;
let state = 'LOGIN';
let loaded = false;
const sock = new net.Socket();

function wvar(v) {
  const out = [];
  while (true) {
    if ((v & 0xFFFFFF80) === 0) { out.push(v & 0x7F); return Buffer.from(out); }
    out.push((v & 0x7F) | 0x80);
    v = (v >>> 7);
  }
}

function sendRaw(data) {
  if (compression >= 0 && data.length >= compression) {
    const comp = zlib.deflateSync(data);
    const header = wvar(data.length);
    sock.write(Buffer.concat([wvar(header.length + comp.length), header, comp]));
  } else if (compression >= 0) {
    sock.write(Buffer.concat([wvar(1 + data.length), Buffer.alloc(1, 0), data]));
  } else {
    sock.write(Buffer.concat([wvar(data.length), data]));
  }
}

function sendPacket(name, params) {
  let buf;
  try {
    if (state === 'PLAY') buf = playSer.createPacketBuffer({name, params});
    else throw new Error('Wrong state: ' + state);
    sendRaw(buf);
  } catch(e) {
    console.log('[SEND ERR]', name, e.message.substring(0, 100));
  }
}

let buf = Buffer.alloc(0);
sock.on('data', (data) => {
  buf = Buffer.concat([buf, data]);
  while (buf.length > 0) {
    let pos = 0, len = 0, shift = 0;
    while (pos < buf.length) {
      const b = buf[pos];
      len |= (b & 0x7F) << shift;
      shift += 7; pos++;
      if ((b & 0x80) === 0) break;
    }
    if (pos + len > buf.length) break;
    const rest = buf.slice(pos, pos + len);
    buf = buf.slice(pos + len);

    let pid, payload;
    if (compression >= 0) {
      let dv = 0, ds = 0, dp = 0;
      while (dp < rest.length) {
        const b = rest[dp];
        dv |= (b & 0x7F) << ds; ds += 7; dp++;
        if ((b & 0x80) === 0) break;
      }
      if (dv > 0) {
        const dec = zlib.inflateSync(rest.slice(dp));
        let pv = 0, ps = 0, pp = 0;
        while (pp < dec.length) {
          const b = dec[pp];
          pv |= (b & 0x7F) << ps; ps += 7; pp++;
          if ((b & 0x80) === 0) break;
        }
        pid = pv;
        payload = dec.slice(pp);
      } else {
        let pv = 0, ps = 0, pp = dp;
        while (pp < rest.length) {
          const b = rest[pp];
          pv |= (b & 0x7F) << ps; ps += 7; pp++;
          if ((b & 0x80) === 0) break;
        }
        pid = pv;
        payload = rest.slice(pp);
      }
    } else {
      let pv = 0, ps = 0, pp = 0;
      while (pp < rest.length) {
        const b = rest[pp];
        pv |= (b & 0x7F) << ps; ps += 7; pp++;
        if ((b & 0x80) === 0) break;
      }
      pid = pv;
      payload = rest.slice(pp);
    }
    handlePacket(pid, payload);
  }
});

function handlePacket(pid, payload) {
  let packet;
  try {
    if (state === 'LOGIN') {
      packet = loginDeser.parsePacketBuffer({data: payload, name: null});
    } else if (state === 'CONFIG') {
      packet = configDeser.parsePacketBuffer({data: payload, name: null});
    } else {
      packet = playDeser.parsePacketBuffer({data: payload, name: null});
    }
  } catch(e) {
    if (pid !== 0x79 && pid !== 0x2C) {
      console.log('  [0x' + pid.toString(16) + '] parse err:', e.message.substring(0, 60));
    }
    return;
  }
  const name = packet.data.name;
  const data = packet.data.params;

  if (name === 'compress') { compression = data.threshold; }
  else if (name === 'success') { /* login OK */ }
  else if (name === 'login') {
    state = 'PLAY';
    console.log('[PLAY]');
    // Init
    sendPacket('player_loaded', {});
    // Use JS serializer for settings
    const settingsBuf = configSer.createPacketBuffer({name: 'settings', params: {
      locale: 'en_US', viewDistance: 12, chatFlags: 0, chatColors: true,
      skinParts: 0x7F, mainHand: 1, enableTextFiltering: false, enableServerListing: true, particleStatus: 0,
    }});
    sendRaw(settingsBuf);

    setTimeout(() => {
      console.log('[CMD] /help');
      sendPacket('chat_command', { command: 'help' });
    }, 4000);
    setTimeout(() => {
      console.log('[CMD] /hub');
      sendPacket('chat_command', { command: 'hub' });
    }, 10000);
  }
  else if (name === 'finish_configuration') {
    state = 'CONFIG';
    const settingsBuf = configSer.createPacketBuffer({name: 'settings', params: {
      locale: 'en_US', viewDistance: 12, chatFlags: 0, chatColors: true,
      skinParts: 0x7F, mainHand: 1, enableTextFiltering: false, enableServerListing: true, particleStatus: 0,
    }});
    sendRaw(settingsBuf);
    // Finish config
    const finishBuf = configSer.createPacketBuffer({name: 'finish_configuration', params: {}});
    sendRaw(finishBuf);
  }
  else if (name === 'show_dialog') {
    console.log('[DIALOG]');
    sendPacket('dialog_response', {
      dialogId: data.dialogId || '',
      action: 'register',
      data: { password: PASSWORD, confirm: PASSWORD }
    });
  }
  else if (name === 'keep_alive') {
    sendPacket('keep_alive', { keepAliveId: data.keepAliveId });
  }
  else if (name === 'position') {
    sendPacket('teleport_confirm', { teleportId: data.teleportId });
  }
  else if (name === 'system_chat' || name === 'player_chat' || name === 'profileless_chat') {
    let txt = '';
    if (data && data.message) {
      if (typeof data.message === 'object') {
        try { txt = data.message.text || data.message.translate || JSON.stringify(data.message); } catch(e) {}
      } else { txt = String(data.message); }
    }
    if (data && data.content) {
      try { txt = data.content.text || data.content.translate || JSON.stringify(data.content); } catch(e) {}
    }
    txt = txt.replace(/[§\xa7][0-9a-fklmnor]/g, '').replace(/[^\x20-\x7e]/g, '').trim();
    if (txt) console.log('[CHAT/' + name + ']', txt.substring(0, 300));
  }
  else if (name === 'disconnect' || name === 'kick_disconnect') {
    console.log('[KICK]', JSON.stringify(data).substring(0, 300));
  }
  else if (name === 'ping') { sendPacket('pong', {}); }
  else if (name === 'map_chunk') { sendPacket('chunk_batch_received', { chunksPerTick: 1.0 }); }
}

sock.connect(PORT, HOST, () => {
  console.log('[+] Connected');
  // Handshake + Login Start
  sendRaw(loginSer.createPacketBuffer({name: 'set_protocol', params: {protocolVersion: PV, serverHost: HOST, serverPort: PORT, nextState: 2}}));
  sendRaw(loginSer.createPacketBuffer({name: 'login_start', params: {username: USERNAME, uuid: '00000000-0000-0000-0000-000000000000'}}));
});

sock.on('close', () => console.log('[END]'));
sock.on('error', (e) => console.log('[ERR]', e.message.substring(0, 100)));
setTimeout(() => process.exit(0), 25000);
