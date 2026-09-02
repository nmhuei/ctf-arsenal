// Serialize chat commands for Paper 26.1.2
const mc = require('minecraft-protocol');
const ser = mc.createSerializer({state: mc.states.PLAY, isServer: false, version: 775});

// Serialize a chat_command packet
const cmd = process.argv[2] || 'help';
const buf = ser.createPacketBuffer({name: 'chat_command', params: {command: cmd}});
// Output as hex for Python to consume
process.stdout.write(buf.toString('hex'));
