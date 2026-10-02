import subprocess, tempfile

def test_body(name, body_code):
    html = f"""<!DOCTYPE html><html><body><script>
let lines = [];
lines.push("function {name}(x, arr, obj) {{");
for (let i = 0; i < 650; i++) lines.push(`  if (x === ${{i}}) return ${{i}};`);
lines.push(`{body_code}`);
lines.push("}}");
lines.push("return {name};");

let fn = new Function(lines.join("\\n"))();
let dummy = {{ a: 1 }};
let dummy_arr = [1.1, 2.2, 3.3];

for (let i = 0; i < 20000; i++) fn(i, dummy_arr, dummy);
console.log("Warmup done for {name}");
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
        out, _ = p.communicate(timeout=6)
    except subprocess.TimeoutExpired:
        p.kill()
        out, _ = p.communicate()
        
    compiled = False
    for line in out.splitlines():
        if f"<JSFunction {name}" in line:
            print(f"[{name}] {line}")
            compiled = True
    if not compiled:
        print(f"[{name}] NOT COMPILED TO MAGLEV!")

# Test loops
test_body("loop_for", "arr[0] = obj; let r = 0; for (let j = 0; j < 5; j++) { r = arr[1]; } return r;")
test_body("loop_while", "arr[0] = obj; let r = 0; let j = 0; while (j < 5) { r = arr[1]; j++; } return r;")
test_body("loop_for_in", "arr[0] = obj; let r = 0; for (let k in [1]) { r = arr[1]; } return r;")
