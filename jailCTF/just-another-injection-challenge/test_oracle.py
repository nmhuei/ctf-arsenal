import check_remote

def test_expr(expr):
    res = check_remote.query(expr)
    print(f"[{res}] {expr}")
    return res

if __name__ == "__main__":
    # Test length 122
    test_expr("env|flatten|sort|last|length|acos|atanh|error") # Should be ok if length != 1
    
    # Test prefix "jail{"
    # position 0 is 'j' (106)
    # position 1 is 'a' (97)
    # position 2 is 'i' (105)
    # position 3 is 'l' (108)
    # position 4 is '{' (123)
