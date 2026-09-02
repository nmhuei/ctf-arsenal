import hashlib
import itertools

target_hash = '0b95495176f49f2dab8a2d9c26a41ecc'

def check(flag):
    h = hashlib.md5(flag.encode()).hexdigest()
    if h == target_hash:
        print(f"FOUND MATCH: {flag}")
        return True
    return False

def main():
    parts_pool = [
        # lol variations
        ["lol", "LOL", "l0l"],
        # fl2g variations
        ["fl2g", "fl4g", "flag"],
        # rb_R2 variations
        ["rb_R2", "rb_r2", "RB_R2", "Rb_R2", "rB_R2", "rb", "RB", "r2", "R2", "rb_R1", "rb_r1"],
        # exe variations
        ["exe", "EXE"]
    ]
    
    # We will try all permutations of the 4 categories:
    # 1. lol
    # 2. fl2g
    # 3. rb/R2/rb_R2/etc
    # 4. exe
    
    # But wait, what if rb and R2 are separate parts?
    # Let's define the parts list as:
    # ["lol", "fl2g", "rb", "R2", "exe"] (5 parts!)
    # That gives 120 permutations, 5 gaps, each 0-3 underscores.
    # 120 * 4^5 = 122,880 candidates. Still extremely fast in Python!
    
    part_groups = [
        # Group 1: lol
        ["lol", "LOL", "l0l"],
        # Group 2: fl2g
        ["fl2g", "fl4g", "flag"],
        # Group 3: rb
        ["rb", "RB", "rts", "RTS"],
        # Group 4: R2
        ["R2", "r2", "R1", "r1"],
        # Group 5: exe
        ["exe", "EXE"]
    ]
    
    # Generate all combinations of picking one from each group
    choices = list(itertools.product(*part_groups))
    print(f"Total choices of words: {len(choices)}")
    
    found = False
    count = 0
    for choice in choices:
        # choice is e.g. ("lol", "fl2g", "rb", "R2", "exe")
        # We try all permutations of these 5 words
        for perm in itertools.permutations(choice):
            # We have 4 gaps. Let's try 0 to 3 underscores in each gap
            for g0 in range(4):
                u0 = "_" * g0
                for g1 in range(4):
                    u1 = "_" * g1
                    for g2 in range(4):
                        u2 = "_" * g2
                        for g3 in range(4):
                            u3 = "_" * g3
                            # Construct candidate
                            flag = f"SeKaiCTF{{{perm[0]}{u0}{perm[1]}{u1}{perm[2]}{u2}{perm[3]}{u3}{perm[4]}}}"
                            count += 1
                            if check(flag):
                                found = True
                                return
                                
    print(f"Checked {count} candidates. No match.")

if __name__ == '__main__':
    main()
