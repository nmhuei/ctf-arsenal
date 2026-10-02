'use strict';

const base = Process.getModuleByName('residuegate-hard').base;
const offsets = ['9f040', 'b4e40', 'b79e0', 'b4cd0', 'a26d0'];
const counts = new Map();

function printable(ptr) {
  try {
    const raw = ptr.readByteArray(48);
    const u = new Uint8Array(raw);
    let out = '';
    for (const c of u) out += c >= 32 && c < 127 ? String.fromCharCode(c) : '.';
    return out;
  } catch (_) { return ''; }
}

for (const off of offsets) {
  Interceptor.attach(base.add(ptr('0x' + off)), {
    onEnter(args) {
      const n = counts.get(off) || 0;
      if (n >= 30) return;
      counts.set(off, n + 1);
      let indirect = '';
      try { indirect = printable(args[1].readPointer()); } catch (_) {}
      console.log(JSON.stringify({off: off, rdi: args[0].toString(), rsi: args[1].toString(), rdx: args[2].toString(), direct: printable(args[1]), indirect: indirect}));
    }
  });
}
