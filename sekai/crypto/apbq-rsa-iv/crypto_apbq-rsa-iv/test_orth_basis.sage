with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h = vector(ZZ, hints)

W = 1 << 3000
# Orthogonal lattice to h mod n:
M_orth = Matrix(ZZ, [
    [hints[0] * W, 1, 0, 0],
    [hints[1] * W, 0, 1, 0],
    [hints[2] * W, 0, 0, 1],
    [n * W, 0, 0, 0]
]).LLL()

print('M_orth rows with weight:')
for idx, r in enumerate(M_orth.rows()):
    v = vector(ZZ, r[1:])
    norm_b = v.norm().n().log(2)
    print(f'Row {idx}: r[0]//W = {r[0]//W}, norm bits = {norm_b:.1f}')
    print(f'  v . h % n == 0: {(v * h) % n == 0}')
    if (v * h) % n == 0:
        print(f'  v = {v}')
        print(f'  (v . h) // n: {(v * h) // n}')
