// JS bridge: use minecraft-protocol to serialize chat, forward raw bytes
const mc = require('minecraft-protocol');
const { createSerializer, states } = mc;

// Create serializers for v775 PLAY state
const ser = createSerializer({state: states.PLAY, isServer: false, version: 775});

// Serialize chat_command (0x06 by v770, 0x07 by v775)
const methods = ['chat_command', 'chat_command_signed', 'chat_message'];
for (const name of methods) {
  try {
    let params;
    if (name === 'chat_command') {
      params = {command: 'coins'};
    } else if (name === 'chat_command_signed') {
      params = {
        command: 'coins',
        timestamp: BigInt(Date.now()),
        salt: 0n,
        argumentSignatures: [],
        messageCount: 0,
        acknowledged: Buffer.alloc(3, 0),
        checksum: 0
      };
    } else if (name === 'chat_message') {
      params = {
        message: '/coins',
        timestamp: BigInt(Date.now()),
        salt: 0n,
        signature: null,
        offset: 0,
        acknowledged: Buffer.alloc(3, 0),
        checksum: 0
      };
    }
    const buf = ser.createPacketBuffer({name, params});
    console.log(`${name}: ${buf.toString('hex')}`);
    console.log(`  pid=${buf[0]} string_len=${buf[1]} cmd=${buf.slice(2).toString()}`);
  } catch(e) {
    console.log(`${name}: error - ${e.message.substring(0,60)}`);
  }
}

// Also check what the library sends when we call client.write
const states2 = mc.states;
// Create protocol YAML for inspection
console.log('\nAll C->S PLAY packets for v775:');
const mcdata = require('minecraft-data');
try {
  const types = mcdata('1.21.5').protocol.play.toServer.types;
  const map = types.packet[1][0].type[1].mappings;
  const sorted = Object.entries(map).sort((a,b) => a[1]-b[1]);
  for (const [name, id] of sorted) {
    if (id <= 0x20) {
      const ptype = types['packet_' + name];
      let fields = '';
      if (ptype && Array.isArray(ptype) && ptype[0] === 'container') {
        fields = ptype[1].map(f => f.name + ':' + f.type).join(' ');
      }
      console.log(`0x${id.toString(16).padStart(2,'0')} ${name} [${fields.substring(0,80)}]`);
    }
  }
} catch(e) {
  console.log('Data error:', e.message.substring(0,60));
}
