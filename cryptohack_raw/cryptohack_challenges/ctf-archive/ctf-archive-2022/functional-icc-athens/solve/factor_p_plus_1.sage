p = 5575186299632655785383929568162090376494993
print("p + 1 factorization:")
try:
    print(factor(p + 1))
except Exception as e:
    print("Factor failed:", e)
