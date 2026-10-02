'use strict';

const mod = Process.getModuleByName('residuegate-hard');
const base = mod.base;
const end = base.add(mod.size);
const active = new Map();
function inside(p) { return p.compare(base) >= 0 && p.compare(end) < 0; }
for (const name of ['read', 'recv', 'recvfrom']) {
  try { Interceptor.attach(Module.getGlobalExportByName(name), { onLeave(ret) {
    if (ret.toInt32() <= 0) return;
    const tid = Process.getCurrentThreadId(); if (active.has(tid)) return;
    active.set(tid, []);
    Stalker.follow(tid, {events:{call:true}, onReceive(events) {
      for (const e of Stalker.parse(events, {annotate:false,stringify:false})) {
        const seq = active.get(tid); if (!seq) break;
        if (inside(e[0]) && inside(e[1]) && seq.length < 500) seq.push(e[0].sub(base).toString() + '>' + e[1].sub(base).toString());
      }
    }});
  }}); } catch (_) {}
}
Interceptor.attach(Module.getGlobalExportByName('writev'), {onEnter() {
  const tid=Process.getCurrentThreadId(), seq=active.get(tid); if (!seq) return;
  Stalker.flush(); Stalker.unfollow(tid); Stalker.garbageCollect();
  console.log(seq.join('\n')); active.delete(tid);
}});
