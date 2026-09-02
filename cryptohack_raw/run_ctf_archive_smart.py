import os
import re
import sys
import subprocess
from pathlib import Path

ROOT = Path("cryptohack_challenges/ctf-archive")
flag_pattern = re.compile(r"([a-zA-Z0-9_#-]+{[^{}]+})")

python_exe = "/home/light/miniforge3/envs/sage/bin/sage"
python_args = ["-python"]
sage_exe = "/home/light/miniforge3/envs/sage/bin/sage"
hook_dir = str(Path("hook_dir").resolve())

def is_fake_flag(flag_str):
    flag_str_lower = flag_str.lower()
    for word in ["local_test", "test_flag", "dummy_flag", "fake_flag", "placeholder"]:
        if word in flag_str_lower:
            return True
    
    m = re.match(r"^[a-zA-Z0-9_#-]+{([^{}]+)}$", flag_str)
    if m:
        inner = m.group(1).lower()
        if inner in ["abc", "test", "local", "dummy", "mock", "fake", "12345", "test12345"]:
            return True
    return False

def extract_ports_and_hosts(statement_path):
    if not statement_path.exists():
        return []
    content = statement_path.read_text(encoding="utf-8")
    
    hosts_and_ports = []
    
    matches = re.findall(r"archive\.cryptohack\.org\s+(\d+)", content)
    for port in matches:
        hosts_and_ports.append(("archive.cryptohack.org", int(port)))
        
    matches = re.findall(r"archive\.cryptohack\.org:(\d+)", content)
    for port in matches:
        hosts_and_ports.append(("archive.cryptohack.org", int(port)))
        
    matches = re.findall(r"nc\s+([a-zA-Z0-9.-]+)\s+(\d+)", content)
    for host, port in matches:
        if port.isdigit():
            hosts_and_ports.append((host, int(port)))
            
    matches = re.findall(r"`([a-zA-Z0-9.-]+)\s+(\d+)`", content)
    for host, port in matches:
        if port.isdigit():
            hosts_and_ports.append((host, int(port)))
            
    seen = set()
    unique_hosts_and_ports = []
    for host, port in hosts_and_ports:
        if (host, port) not in seen:
            seen.add((host, port))
            unique_hosts_and_ports.append((host, port))
            
    return unique_hosts_and_ports

def run_script(script_path, challenge_dir, args):
    script_rel = script_path.relative_to(challenge_dir)
    if script_path.suffix == ".sage":
        cmd = [sage_exe, str(script_rel)] + args
    else:
        cmd = [python_exe] + python_args + [str(script_rel)] + args
        
    env = os.environ.copy()
    env["PYTHONPATH"] = hook_dir
    
    print(f"[*] Executing: {' '.join(cmd)} in {challenge_dir}", flush=True)
    try:
        res = subprocess.run(
            cmd,
            cwd=challenge_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            text=True,
            errors="replace",
            env=env
        )
        return res
    except subprocess.TimeoutExpired as e:
        print(f"[!] Timeout after 120s", flush=True)
        stdout = e.stdout if e.stdout else ""
        stderr = e.stderr if e.stderr else ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return subprocess.CompletedProcess(cmd, -1, stdout, stderr)
    except Exception as e:
        print(f"[!] Error running script: {e}", flush=True)
        return None

def cleanup_solve_dir(solve_dir, success_script=None, all_scripts=None):
    if all_scripts is None:
        all_scripts = []
        for ext in ["*.py", "*.sage"]:
            all_scripts.extend(list(solve_dir.glob(ext)))
            
    if not all_scripts:
        return
        
    if success_script:
        success_content = success_script.read_text(encoding="utf-8", errors="replace")
        for script in all_scripts:
            if script == success_script:
                continue
            stem = script.stem
            import_pattern = rf"\b{re.escape(stem)}\b"
            if re.search(import_pattern, success_content):
                print(f"[*] Keeping helper/dependency: {script.name}", flush=True)
                continue
            
            print(f"[-] Deleting garbage solver: {script.name}", flush=True)
            try:
                script.unlink()
            except Exception as e:
                print(f"[!] Error deleting {script.name}: {e}", flush=True)
    else:
        primary = None
        for script in sorted(all_scripts, key=lambda x: len(x.name)):
            name_lower = script.name.lower()
            if not any(w in name_lower for w in ["copy", "backup", "old", "test", "fixed", "fast"]):
                primary = script
                break
        if not primary:
            primary = all_scripts[0]
            
        print(f"[*] Main solver kept: {primary.name}", flush=True)
        primary_content = primary.read_text(encoding="utf-8", errors="replace")
        
        for script in all_scripts:
            if script == primary:
                continue
            
            stem = script.stem
            import_pattern = rf"\b{re.escape(stem)}\b"
            if re.search(import_pattern, primary_content):
                print(f"[*] Keeping helper/dependency: {script.name}", flush=True)
                continue
                
            name_lower = script.name.lower()
            if any(w in name_lower for w in ["copy", "backup", "old", "test", "fixed", "fast"]):
                print(f"[-] Deleting garbage solver backup: {script.name}", flush=True)
                try:
                    script.unlink()
                except Exception as e:
                    print(f"[!] Error deleting {script.name}: {e}", flush=True)

def main():
    solved_count = 0
    newly_solved = []
    
    challenge_dirs = []
    for p in sorted(ROOT.rglob("solve")):
        challenge_dirs.append(p.parent)
        
    print(f"[*] Found {len(challenge_dirs)} challenges with solve scripts.")
    
    for chal_dir in challenge_dirs:
        flag_path = chal_dir / "flag.txt"
        
        existing_flag = None
        if flag_path.exists():
            content = flag_path.read_text(encoding="utf-8").strip()
            if content and not is_fake_flag(content):
                existing_flag = content
                
        solve_dir = chal_dir / "solve"
        scripts = []
        for ext in ["*.py", "*.sage"]:
            scripts.extend(list(solve_dir.rglob(ext)))
        scripts.sort(key=lambda x: len(x.name), reverse=True)
        
        if existing_flag:
            print(f"[*] Skipping {chal_dir.name} (already solved: {existing_flag})", flush=True)
            # Run cleanup keeping the first/main one as default
            cleanup_solve_dir(solve_dir, success_script=None, all_scripts=scripts)
            solved_count += 1
            continue
            
        print(f"\n==================================================", flush=True)
        print(f"[*] Solving: {chal_dir.name}", flush=True)
        
        remotes = extract_ports_and_hosts(chal_dir / "statement.md")
        print(f"[*] Extracted remotes from statement: {remotes}", flush=True)
        
        flag_found = False
        success_script = None
        for script in scripts:
            if "pycache" in script.name or script.name.endswith(".sage.py"):
                continue
                
            strategies = []
            for host, port in remotes:
                strategies.append(["remote", host, str(port)])
                strategies.append([host, str(port)])
                strategies.append(["--host", host, "--port", str(port)])
            strategies.append([])
            
            for args in strategies:
                res = run_script(script, chal_dir, args)
                if res is None:
                    continue
                
                stdout = res.stdout
                stderr = res.stderr
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")
                    
                output = stdout + "\n" + stderr
                matches = flag_pattern.findall(output)
                
                valid_flags = [f.strip() for f in matches if not is_fake_flag(f.strip())]
                if valid_flags:
                    flag = valid_flags[-1]
                    print(f"[+] SUCCESS! Found flag: {flag}", flush=True)
                    flag_path.write_text(flag + "\n", encoding="utf-8")
                    newly_solved.append((chal_dir.name, flag))
                    flag_found = True
                    success_script = script
                    break
                else:
                    if res.returncode != 0:
                        lines = [l for l in stderr.splitlines() if l.strip()]
                        last_err = "\n".join(lines[-3:]) if lines else "unknown error"
                        print(f"[-] Strategy {args} failed. Exit code {res.returncode}. Last error: {last_err}", flush=True)
                    else:
                        print(f"[-] Strategy {args} returned no flag.", flush=True)
                        
            if flag_found:
                break
                
        # Run cleanup based on whether we succeeded or not
        cleanup_solve_dir(solve_dir, success_script=success_script, all_scripts=scripts)
        if flag_found:
            solved_count += 1
                
    print(f"\n==================================================", flush=True)
    print(f"[*] Run finished.", flush=True)
    print(f"[*] Total solved challenges: {solved_count}", flush=True)
    print(f"[*] Newly solved in this run ({len(newly_solved)}):", flush=True)
    for name, flag in newly_solved:
        print(f"  - {name}: {flag}", flush=True)

if __name__ == "__main__":
    main()
