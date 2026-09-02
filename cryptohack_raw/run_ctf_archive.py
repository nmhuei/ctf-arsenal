import os
import re
import subprocess
from pathlib import Path

ROOT = Path("cryptohack_challenges/ctf-archive")

flag_pattern = re.compile(r"([a-zA-Z0-9_#-]+{[^{}]+})")

python_exe = "/home/light/miniforge3/envs/sage/bin/python"
sage_exe = "/home/light/miniforge3/envs/sage/bin/sage"

for p in sorted(ROOT.rglob("solve")):
    challenge_dir = p.parent
    flag_path = challenge_dir / "flag.txt"
    if flag_path.exists():
        continue
    
    solve_dir = p
    scripts = []
    for ext in ["*.py", "*.sage"]:
        scripts.extend(list(solve_dir.glob(ext)))
    
    if not scripts:
        continue
        
    scripts.sort(key=lambda x: len(x.name), reverse=True)
    
    print(f"\n==================================================")
    print(f"[*] Processing {challenge_dir}...")
    
    for script in scripts:
        script_name = script.name
        if "pycache" in script_name or script_name.endswith(".sage.py"):
            continue
            
        if script_name.endswith(".sage"):
            cmd = [sage_exe, script_name]
        else:
            cmd = [python_exe, script_name]
            
        print(f"[*] Running: {' '.join(cmd)} in {solve_dir}")
        try:
            result = subprocess.run(
                cmd,
                cwd=solve_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=40,
                text=True,
                errors="replace"
            )
            
            output = result.stdout + "\n" + result.stderr
            matches = flag_pattern.findall(output)
            if matches:
                flag = matches[-1].strip() # Use the last match just in case there are multiple
                print(f"[+] Found Flag: {flag}")
                flag_path.write_text(flag + "\n", encoding="utf-8")
                print(f"[+] Wrote flag to {flag_path}")
                break
            else:
                print(f"[-] No flag found in output of {script_name}.")
                if result.returncode != 0:
                    print(f"[!] Exit code: {result.returncode}")
                    print(f"[!] Stderr:\n{result.stderr.strip()}")
                else:
                    print(f"[!] Stdout:\n{result.stdout.strip()}")
        except subprocess.TimeoutExpired:
            print(f"[!] Timeout expired running {script_name}")
        except Exception as e:
            print(f"[!] Error running {script_name}: {e}")
