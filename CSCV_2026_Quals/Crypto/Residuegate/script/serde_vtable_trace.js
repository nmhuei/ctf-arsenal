'use strict';
const base = Process.getModuleByName('residuegate-hard').base;
function ptrDump(p) { try { return hexdump(p, {length: 64, header:false, ansi:false}); } catch (_) { return ''; } }
for (const off of ['9d8b8', '9d99f']) {
  Interceptor.attach(base.add(ptr('0x' + off)), {
    onEnter() {
      const r12 = this.context.r12;
      let target = ptr(0);
      try { target = r12.add(0x18).readPointer(); } catch (_) {}
      console.log(JSON.stringify({off:off, r12:r12.toString(), target:target.toString(), r13:this.context.r13.toString(), rdx:this.context.rdx.toString()}));
      console.log(ptrDump(r12));
    }
  });
}
