'use strict';
const mod = Process.getModuleByName('residuegate-hard');
const allocs = new Map();
function save(name) {
  const f = Module.getGlobalExportByName(name);
  Interceptor.attach(f, {
    onEnter(args) { this.size = args[0].toInt32(); this.ret = this.returnAddress; },
    onLeave(ret) {
      if (this.size > 0 && this.size <= 256 && !ret.isNull()) {
        allocs.set(ret.toString(), { name: name, size: this.size, ret: this.ret, bt: Thread.backtrace(this.context, Backtracer.FUZZY).slice(0, 12).map(x => x.toString()) });
      }
    }
  });
}
save('malloc');
Interceptor.attach(Module.getGlobalExportByName('writev'), {
  onEnter(args) {
    const iov = args[1]; const n = args[2].toInt32();
    if (n < 2) return;
    const p = iov.add(Process.pointerSize * 2).readPointer();
    const len = iov.add(Process.pointerSize * 3).readU64().toNumber();
    if (len > 0 && len < 512) {
      const a = allocs.get(p.toString());
      const text = p.readUtf8String(len);
      console.log(JSON.stringify({body:p.toString(),len:len,text:text,alloc:a||null}));
    }
  }
});
