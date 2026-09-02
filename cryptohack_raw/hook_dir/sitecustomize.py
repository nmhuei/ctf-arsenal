import builtins
import os
import sys
from pathlib import Path

# Prevent recursive hooks or infinite loops
_hooking = False

original_open = builtins.open
original_stat = os.stat
original_lstat = os.lstat
original_listdir = os.listdir
original_scandir = os.scandir
original_os_open = os.open

REAL_ROOT = Path("/home/light/Workspace/CTF/cryptohack_raw/cryptohack_challenges/ctf-archive")
PATH_CACHE = {}

def get_real_path(path_str):
    global _hooking
    if _hooking:
        return path_str
        
    if not isinstance(path_str, str):
        try:
            path_str = str(path_str)
        except:
            return path_str
            
    if not path_str.startswith("/mnt/data/"):
        return path_str
        
    _hooking = True
    try:
        parts = path_str.split("/")
        if len(parts) < 5:
            return path_str
            
        fullname = parts[4]
        
        if fullname not in PATH_CACHE:
            # We want to find the directory named fullname under REAL_ROOT
            found = []
            for root, dirs, files in os.walk(str(REAL_ROOT)):
                if fullname in dirs:
                    found.append(Path(root) / fullname)
                    break
            if found:
                PATH_CACHE[fullname] = found[0]
            else:
                PATH_CACHE[fullname] = None
                
        real_dir = PATH_CACHE.get(fullname)
        if real_dir:
            subpath = "/".join(parts[5:])
            new_path = real_dir / subpath
            res = str(new_path)
            sys.stderr.write(f"[Hook] Mapped {path_str} -> {res}\n")
            sys.stderr.flush()
            return res
    except Exception as e:
        sys.stderr.write(f"[Hook Error] {e}\n")
        sys.stderr.flush()
    finally:
        _hooking = False
        
    return path_str

def hooked_open(file, *args, **kwargs):
    if isinstance(file, (str, Path)):
        file = get_real_path(str(file))
    return original_open(file, *args, **kwargs)

def hooked_stat(path, *args, **kwargs):
    return original_stat(get_real_path(path), *args, **kwargs)

def hooked_lstat(path, *args, **kwargs):
    return original_lstat(get_real_path(path), *args, **kwargs)

def hooked_listdir(path=None):
    if path is not None:
        path = get_real_path(path)
    return original_listdir(path)

def hooked_scandir(path=None):
    if path is not None:
        path = get_real_path(path)
    return original_scandir(path)

def hooked_os_open(path, *args, **kwargs):
    return original_os_open(get_real_path(path), *args, **kwargs)

builtins.open = hooked_open
os.stat = hooked_stat
os.lstat = hooked_lstat
os.listdir = hooked_listdir
os.scandir = hooked_scandir
os.open = hooked_os_open
