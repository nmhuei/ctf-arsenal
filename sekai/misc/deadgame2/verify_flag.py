import hashlib

def check(flag):
    h = hashlib.md5(flag.encode()).hexdigest()
    if h == '0b95495176f49f2dab8a2d9c26a41ecc':
        print(f"FOUND MATCH: {flag}")
        return True
    return False

def main():
    candidates = [
        "SeKaiCTF{lol_rts_deadgame2}",
        "SeKaiCTF{lol_rts_deadgame2_fl2g}",
        "SeKaiCTF{lol_rts_deadgame2_fl2g_}",
        "SeKaiCTF{lol_rts_deadgame2_fl2g_}",
        "SeKaiCTF{lol_deadgame2}",
        "SeKaiCTF{lol_fl2g_deadgame2}",
        "SeKaiCTF{lol_deadgame2_fl2g}",
        "SeKaiCTF{lol_deadgame2_fl2g_}",
        "SeKaiCTF{lol_rts_deadgame2_fl2g_}"
    ]
    
    # Let's generate permutations of parts:
    # "lol", "rts", "deadgame2", "fl2g", "_", "R2", "rb", "rts_deadgame2"
    # Wait, the user said:
    # "recover the new flag fragments"
    # Chat had: "SeKaiCTF{lol" at frame 4662
    # and "_fl2g_" at frame 11897
    # and Player 1 sent:
    # "_" at 73100
    # "_" at 73312
    # "_" at 73588
    # "}" at 73931
    # This means the chat messages are:
    # 1. SeKaiCTF{lol
    # 2. _fl2g_
    # 3. _
    # 4. _
    # 5. _
    # 6. }
    # So the flag starts with "SeKaiCTF{lol", then has "_fl2g_" somewhere, then has other parts separated by underscores!
    # Wait, the 8 bytes we decoded from the 8 waves of Base 3, 4:
    # "_", "_", "r", "b", "_", "R", "2", "_"
    # Wait!
    # "r", "b", "_", "R", "2" -> "rb_R2"?
    # What if they are "rb_R2"?
    # Let's check "SeKaiCTF{lol_fl2g_rb_R2}"
    # Let's try many combinations!
    
    parts = ["lol", "fl2g", "rb", "R2", "rts", "deadgame2", "deadgame"]
    # We can try all combinations of these with underscores
    import itertools
    for p in itertools.permutations(["lol", "fl2g", "rb", "R2"]):
        flag = "SeKaiCTF{" + "_".join(p) + "}"
        if check(flag): return
        
    for p in itertools.permutations(["lol", "fl2g", "rb", "R2", "rts"]):
        flag = "SeKaiCTF{" + "_".join(p) + "}"
        if check(flag): return

    for p in itertools.permutations(["lol", "fl2g", "rb", "R2", "deadgame2"]):
        flag = "SeKaiCTF{" + "_".join(p) + "}"
        if check(flag): return

    # Let's print if none matched
    print("Done checking standard permutations.")

if __name__ == '__main__':
    main()
