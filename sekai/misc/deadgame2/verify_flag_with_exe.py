import hashlib
import itertools

def check(flag):
    h = hashlib.md5(flag.encode()).hexdigest()
    if h == '0b95495176f49f2dab8a2d9c26a41ecc':
        print(f"FOUND MATCH: {flag}")
        return True
    return False

def main():
    # We have candidate fragments:
    # 1. SeKaiCTF{lol
    # 2. _fl2g_
    # 3. _rb_R2_ (or variations like rb, R2, rb_R2)
    # 4. exe (or EXE)
    # 5. } at the end
    
    # Let's list variations of the middle parts
    fl2g_variants = ["_fl2g_", "fl2g", "_fl2g", "fl2g_"]
    rb_variants = ["rb_R2", "rb_r2", "rB_R2", "Rb_R2", "RB_R2", "rb_R2_", "rb_r2_"]
    exe_variants = ["exe", "EXE", "exe_", "EXE_"]
    
    # We also know Player 1 sent:
    # Frame 4662: SeKaiCTF{lol
    # Frame 11897: _fl2g_
    # Frame 73100: _
    # Frame 73312: _
    # Frame 73588: _
    # Frame 73931: }
    #
    # Wait! If we look at the underscores sent:
    # SeKaiCTF{lol + _fl2g_ + _ + _ + _ + }
    # Wait, the underscores are:
    # Between lol and fl2g: there's already an underscore.
    # Between fl2g and the next part: underscore.
    # Between the next part and the next part: underscore.
    # This matches: `SeKaiCTF{lol_fl2g_rb_R2_exe}`!
    # Let's try this exact structure:
    
    parts = ["lol", "fl2g", "rb_R2", "exe"]
    for p in itertools.permutations(parts):
        # We join them with underscores
        flag = "SeKaiCTF{" + "_".join(p) + "}"
        # Clean double underscores
        while "__" in flag:
            flag = flag.replace("__", "_")
        if check(flag): return
        
        # Try different casings for rb_R2 and exe
        for rb in ["rb_R2", "rb_r2", "Rb_R2", "RB_R2"]:
            for exe in ["exe", "EXE"]:
                p_custom = [x if x != "rb_R2" else rb for x in p]
                p_custom = [x if x != "exe" else exe for x in p_custom]
                flag_custom = "SeKaiCTF{" + "_".join(p_custom) + "}"
                while "__" in flag_custom:
                    flag_custom = flag_custom.replace("__", "_")
                if check(flag_custom): return

    print("Done checking all combinations with exe.")

if __name__ == '__main__':
    main()
