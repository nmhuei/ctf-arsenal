import json
import os
import re
import subprocess
from pathlib import Path

ROOT = Path("cryptohack_challenges")
STATE_PATH = Path("cryptohack_flags.json")

# Load existing state
with open(STATE_PATH, "r") as f:
    state = json.load(f)
entries = state.get("entries", {})

# Find all solve folders
solve_folders = []
for p in sorted(ROOT.rglob("solve")):
    key = p.parent.relative_to(ROOT).as_posix()
    entry = entries.get(key, {})
    if not entry.get("solved") or not entry.get("flag"):
        solve_folders.append((key, p))

print(f"Found {len(solve_folders)} unsolved challenges with a solve directory.")

flag_pattern = re.compile(r"([a-zA-Z0-9_#-]+{[^{}]+})")

python_exe = "/home/light/miniforge3/envs/sage/bin/python"
sage_exe = "/home/light/miniforge3/envs/sage/bin/sage"

for key, solve_dir in solve_folders:
    # Find scripts
    scripts = []
    for ext in ["*.py", "*.sage"]:
        scripts.extend(list(solve_dir.glob(ext)))
    
    if not scripts:
        print(f"[-] No scripts found in {solve_dir}")
        continue
    
    # Sort scripts to try the most specific ones first
    scripts.sort(key=lambda x: len(x.name), reverse=True)
    
    print(f"\n==================================================")
    print(f"[*] Processing {key}...")
    print(f"[*] Scripts available: {[s.name for s in scripts]}")
    
    for script in scripts:
        script_name = script.name
        
        # Skip pycache or generated files that are not original solvers
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
                flag = matches[0].strip()
                print(f"[+] Found Flag: {flag}")
                
                challenge_dir = solve_dir.parent
                flag_path = challenge_dir / "flag.txt"
                flag_path.write_text(flag + "\n", encoding="utf-8")
                print(f"[+] Wrote flag to {flag_path}")
                
                manage_cmd = [python_exe, "manage_flags.py", "set", key, flag]
                subprocess.run(manage_cmd, check=True)
                print(f"[+] Registered flag in state.")
                break
            else:
                print(f"[-] No flag found in output of {script_name}.")
                if result.returncode != 0:
                    print(f"[!] Exit code: {result.returncode}")
                    print(f"[!] Stderr: {result.stderr.strip()}")
                else:
                    print(f"[!] Stdout: {result.stdout.strip()}")
        except subprocess.TimeoutExpired:
            print(f"[!] Timeout expired running {script_name}")
        except Exception as e:
            print(f"[!] Error running {script_name}: {e}")
