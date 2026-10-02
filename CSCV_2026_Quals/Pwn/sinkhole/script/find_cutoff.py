import subprocess, tempfile

def test_variant(name, body, extra_warmup=""):
    html = f"""<!DOCTYPE html><html><body><script>
let dummy = {{ a: 1 }};
let stable = [dummy, 2.2, 3.3];

function create_and_warmup() {{
  let lines = [];
  lines.push("function {name}(x, arr, obj) {{");
  for (let i = 0; i < 650; i++) lines.push(`  if (x === ${{i}}) return ${{i}};`);
  lines.push(`{body}`);
  lines.push("}}");
  lines.push("return {name};");
  let fn = new Function(lines.join("\\n"))();
  {extra_warmup}
  for (let i = 0; i < 20000; i++) {{
    fn(i, stable, dummy);
  }}
  return fn;
}}

async function main() {{
  let fn = create_and_warmup();
  await new Promise(r => setTimeout(r, 500));
}}
main();
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
        out, _ = p.communicate(timeout=4)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
    maglev_lines = [l for l in out.splitlines() if name in l and "MAGLEV" in l]
    print(f"{name:15}: {'COMPILED' if maglev_lines else 'NOT COMPILED'}")
    for l in maglev_lines:
        print("  ", l)

test_variant("v1_args", "return x + arr.length;")
test_variant("v2_store", "arr[0] = obj; return arr[1];")
test_variant("v3_for_in", "for (let k in obj) { return arr[1]; } return 0;")
test_variant("v4_while", "let i = 0; while (i < 1) { i++; } return arr[1];")
test_variant("v5_cond_while", "let r = null; while ((r = arr[1]) !== null) break; return r;")
