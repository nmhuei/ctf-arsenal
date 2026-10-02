import subprocess, tempfile

html = """<!DOCTYPE html><html><body>
<script>
let lines = [];
lines.push("function cond_test(x, arr, obj) {");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
lines.push("  arr[0] = obj;");
lines.push("  let res = null;");
lines.push("  while ((res = arr[1]) !== null) {");
lines.push("    break;");
lines.push("  }");
lines.push("  return res;");
lines.push("}");
lines.push("return cond_test;");

window.target_fn = new Function(lines.join("\\n"))();
let fn = window.target_fn;
let dummy = { a: 1 };
let dummy_arr = [1.1, 2.2, 3.3];

for (let i = 0; i < 20000; i++) {
  fn(i, dummy_arr, dummy);
}
console.log("Script 1 complete: Warmup done!");
</script>

<script>
console.log("Script 2 starting: testing window.target_fn...");
let fn2 = window.target_fn;
let dummy2 = { a: 1 };
for (let attempt = 0; attempt < 50; attempt++) {
  let t0 = Date.now();
  while (Date.now() - t0 < 20); // 20ms
  let farr = [1.1, 2.2, 3.3];
  let res = fn2(1000, farr, dummy2);
  if (typeof res === "object") {
    console.log("🔥🔥🔥 SUCCESS! Object on attempt " + attempt + ":", res);
    break;
  }
  if (attempt === 0 || attempt % 20 === 0) {
    console.log("Attempt " + attempt + ": " + typeof res + " " + res);
  }
}
</script>
</body></html>"""

with open("script/test_two_scripts.html", "w") as f:
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
    "http://127.0.0.1:8000/test_two_scripts.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if "cond_test" in line or "Attempt" in line or "SUCCESS" in line or "Script" in line:
        print(line)
