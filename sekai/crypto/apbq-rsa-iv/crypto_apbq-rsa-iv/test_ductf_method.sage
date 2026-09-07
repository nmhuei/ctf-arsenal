with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

V = hints
k = 2^2000
M = Matrix.column([k * v for v in V]).augment(Matrix.identity(len(V)))
B = [b[1:] for b in M.LLL()]
print("B length:", len(B))
print("B rows norms:", [vector(b).norm().n().log(2) for b in B])

# The relation vector orthogonal to V:
# len(V) - 2 = 1 vector
rel = B[0]
print("rel * V == 0:", sum(r * v for r, v in zip(rel, V)) == 0)

# Now orthogonal complement of rel:
M2 = (k * Matrix([rel])).T.augment(Matrix.identity(len(V)))
L2 = M2.LLL()
B2 = [b[-len(V):] for b in L2 if set(b[:-len(V)]) == {0}]
print("B2 length:", len(B2))
print("B2 rows norms:", [vector(b).norm().n().log(2) for b in B2])

for b in B2:
    print("b * rel == 0:", sum(x * y for x, y in zip(b, rel)) == 0)
