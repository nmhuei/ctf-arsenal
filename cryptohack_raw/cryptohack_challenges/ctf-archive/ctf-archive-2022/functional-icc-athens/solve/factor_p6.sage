p = 5575186299632655785383929568162090376494993
val = p^6 + p^5 + p^4 + p^3 + p^2 + p + 1
print("Factors:")
try:
    # Let's find small factors of val
    for prim in [3, 7, 29, 43]: # wait, we can just use factor() with a limit
        pass
    print(factor(val, limit=10^8))
except Exception as e:
    print("Error:", e)
