'use strict';

const mod = Process.getModuleByName('residuegate-hard');
const lo = mod.base;
const hi = mod.base.add(mod.size);
const runs = new Map();

function inside(p) { return p.compare(lo) >= 0 && p.compare(hi) < 0; }
function addHooks(name, onLeave) {
    try { Interceptor.attach(Module.getGlobalExportByName(name), { onLeave: onLeave }); }
    catch (_) { console.log('no ' + name); }
}

for (const name of ['read', 'recv', 'recvfrom']) {
    addHooks(name, function (ret) {
        if (ret.toInt32() <= 0) return;
        const tid = Process.getCurrentThreadId();
        if (runs.has(tid)) return;
        const seen = new Set();
        runs.set(tid, { seen: seen, total: 0, samples: [] });
        Stalker.follow(tid, {
            events: { call: true },
            onReceive(events) {
                for (const e of Stalker.parse(events, { annotate: false, stringify: false })) {
                    const run = runs.get(tid);
                    if (!run) break;
                    run.total++;
                    if (run.samples.length < 5) run.samples.push(JSON.stringify(e));
                    if (inside(e[1])) run.seen.add(e[1].sub(lo).toString());
                }
            }
        });
        console.log('FOLLOW ' + tid + ' after ' + name);
    });
}

addHooks('writev', function (_) {
    const tid = Process.getCurrentThreadId();
    const run = runs.get(tid);
    if (!run) return;
    Stalker.flush();
    Stalker.unfollow(tid);
    Stalker.garbageCollect();
    console.log('WRITEV ' + tid + ' total=' + run.total + ' blocks=' + run.seen.size);
    console.log('SAMPLES ' + run.samples.join(' '));
    console.log(Array.from(run.seen).sort((a,b)=>parseInt(a)-parseInt(b)).join(' '));
    runs.delete(tid);
});
