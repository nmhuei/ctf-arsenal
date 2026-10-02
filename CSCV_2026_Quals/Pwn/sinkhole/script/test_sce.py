import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let lines = [];
lines.push("function test_sce(x, arr, idx) {");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
lines.push("  return arr[idx];");
lines.push("}");
lines.push("return test_sce;");

let fn = new Function(lines.join("\\n"))();
let arr = new Array(1000000);
arr.fill(1.1);
arr[10] = 2.2;

console.log("Warmup starting...");
for (let i = 0; i < 20000; i++) {
  fn(i, arr, 10);
}
console.log("Warmup done!");

// Now test with an object or non-smi!
let obj = { a: 1 };
let res = fn(1000, arr, obj);
console.log("res with obj index:", typeof res, res);
</script></body></html>"""

with open("script/test_sce.html", "w") as f:
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
    "http://127.0.0.1:8000/test_sce.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=8)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if "test_sce" in line or "CONSOLE" in line:
        print(line)
