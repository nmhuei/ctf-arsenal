import hashlib

def check(flag):
    h = hashlib.md5(flag.encode()).hexdigest()
    if h == '0b95495176f49f2dab8a2d9c26a41ecc':
        print(f"FOUND MATCH: {flag}")
        return True
    return False

def main():
    # Fragments:
    # 1. SeKaiCTF{lol
    # 2. _fl2g_ (or fl2g)
    # 3. _rb_R2_ (or variations)
    # Let's try different variations of rb, R2, rb_R2, fl2g, etc.
    
    variations_rb = [
        "rb_R2", "rb_r2", "rB_R2", "Rb_R2", "RB_R2",
        "_rb_R2", "_rb_r2", "rb_R2_", "rb_r2_", "_rb_R2_", "_rb_r2_"
    ]
    
    for v in variations_rb:
        # SeKaiCTF{lol + fl2g + v
        candidates = [
            f"SeKaiCTF{{lol_{v}_fl2g_}}",
            f"SeKaiCTF{{lol_fl2g_{v}}}",
            f"SeKaiCTF{{lol_fl2g_{v}_}}",
            f"SeKaiCTF{{lol_{v}_fl2g}}",
            f"SeKaiCTF{{lol_{v}}}"
        ]
        # Clean underscores
        cleaned = []
        for c in candidates:
            # replace double underscores
            while "__" in c:
                c = c.replace("__", "_")
            cleaned.append(c)
            # also try with final brace
            if not c.endswith("}"):
                cleaned.append(c + "}")
        
        for c in set(cleaned):
            if check(c):
                return

    # What if the flag has other words?
    # Let's check "SeKaiCTF{lol_rts_deadgame2}" permutations
    print("Done checking variations.")

if __name__ == '__main__':
    main()
