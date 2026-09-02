import hashlib

target_hash = '0b95495176f49f2dab8a2d9c26a41ecc'

def check(flag):
    h = hashlib.md5(flag.encode()).hexdigest()
    if h == target_hash:
        print(f"FOUND MATCH: {flag}")
        return True
    return False

def main():
    # Fragments and their variations
    lols = ["lol", "LOL", "l0l"]
    fl2gs = ["fl2g", "fl4g", "flag", "_fl2g_", "_fl4g_", "_flag_"]
    rbs = ["rb", "RB", "rts", "RTS", "deadgame", "deadgame2"]
    r2s = ["R2", "r2", "R1", "r1"]
    exes = ["exe", "EXE"]
    
    # We will test all permutations of:
    # lol, fl2g, rb, r2, exe
    # joined by underscores, with/without double underscores, etc.
    
    found = False
    for lol in lols:
        for fl2g in fl2gs:
            for rb in rbs:
                for r2 in r2s:
                    for exe in exes:
                        # Let's try different combinations of order
                        # Common order: lol -> fl2g -> rb -> R2 -> exe
                        # Candidate flags:
                        
                        # Strip underscores from fl2g for clean joining
                        f_clean = fl2g.strip('_')
                        
                        candidates = [
                            f"SeKaiCTF{{{lol}_{f_clean}_{rb}_{r2}_{exe}}}",
                            f"SeKaiCTF{{{lol}_{f_clean}_{rb}_{r2}_{exe}_}}",
                            f"SeKaiCTF{{{lol}_{fl2g}_{rb}_{r2}_{exe}}}",
                            f"SeKaiCTF{{{lol}_{fl2g}_{rb}_{r2}_{exe}_}}",
                            f"SeKaiCTF{{{lol}_{f_clean}_{rb}_{r2}}}",
                            f"SeKaiCTF{{{lol}_{f_clean}_{rb}_{r2}_exe}}",
                            f"SeKaiCTF{{{lol}_{f_clean}_{rb}_{r2}_EXE}}",
                            f"SeKaiCTF{{{lol}_{fl2g}_{rb}_{r2}}}"
                        ]
                        
                        for c in candidates:
                            # Clean double underscores if they arise, but also test them
                            if check(c):
                                found = True
                                return
                            c_clean = c
                            while "__" in c_clean:
                                c_clean = c_clean.replace("__", "_")
                            if check(c_clean):
                                found = True
                                return
                                
    if not found:
        print("No match found with standard variations.")

if __name__ == '__main__':
    main()
