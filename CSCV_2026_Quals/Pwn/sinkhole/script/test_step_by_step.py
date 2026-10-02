import subprocess, tempfile

def test_code(name, body, args="x", call_arg="i"):
    html = f"""<!DOCTYPE html><html><body><script>
function create_fn() {{
  let lines = [];
  lines.push("function {name}({args}) {{");
  for (let i = 0; i < 650; i++) lines.push(`  if (x === ${{i}}) return ${{i}};`);
  lines.push(`{body}`);
  lines.push("}}");
  lines.push("return {name};");
  let fn = new Function(lines.join("\\n"))();
  return fn;
}}

let dummy = {{ a: 1 }};
let stable = [dummy, 2.2, 3.3];
let farr = [1.1, 2.2, 3.3];

async function run() {{
  let fn = create_fn();
  for (let i = 0; i < 20000; i++) {{
    fn({call_arg});
  }}
  await new Promise(r => setTimeout(r, 500));
  console.log("Done {name}");
}}
run();
</script></body></html>"""
    with open(f"script/{name}.html", "w") as f:
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
        f"http://127.0.0.1:8000/{name}.html"
    ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=8)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
    comp = [line for line in out.splitlines() if f"<{name}>" in line or f"<JSFunction {name}" in line]
    print(f"[{name}] Compiled: {len(comp) > 0}")
    for c in comp:
        print("  ", c)

test_code("step1_base", "return x + 1;")
test_code("step2_args", "return x + arr.length;", "x, arr", "i, stable")
test_code("step3_store", "arr[0] = obj; return arr[1];", "x, arr, obj", "i, stable, dummy")
test_code("step4_loop", "arr[0] = obj; let r = 0; while (r < 1) { r = arr[1]; break; } return r;", "x, arr, obj", "i, stable, dummy")
test_code("step5_cond_loop", "arr[0] = obj; let res = null; while ((res = arr[1]) !== null) { break; } return res;", "x, arr, obj", "i, stable, dummy")
