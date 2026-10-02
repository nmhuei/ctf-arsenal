import subprocess, tempfile

def test_body(name, body_code, warmup_call):
    lines = []
    lines.append("<!DOCTYPE html><html><body><script>")
    lines.append(f"function {name}(x, arr, obj) {{")
    for i in range(650):
        lines.append(f"  if (x === {i}) return {i};")
    lines.append(body_code)
    lines.append("}")
    lines.append(f"return {name};")
    js_func = "\\n".join(lines)
    
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

{warmup_call}
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

test_body("testA", "return x + 1;", "for (let i = 0; i < 20000; i++) fn(i, dummy_arr, dummy);")
test_body("testB", "arr[0] = obj; return arr[1];", "for (let i = 0; i < 20000; i++) fn(i, dummy_arr, dummy);")
test_body("testC", "arr[0] = obj; let r = 0; while (r < 1) { r = arr[1]; break; } return r;", "for (let i = 0; i < 20000; i++) fn(i, dummy_arr, dummy);")
