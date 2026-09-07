load('solve_7x7_real.sage')

print("Inspecting rows of L_kan:")
for idx in range(len(L_kan.rows())):
    r = L_kan.rows()[idx]
    if vector(r).norm() == 0: continue
    print(f"\n--- Row {idx} (norm = {vector(r).norm().n().log(2):.1f} bits) ---")
    cand_const = r[7] // X_bound
    print(f"  const entry: {r[7]}, const // X_bound = {cand_const}")
    cand_x = [r[1 + i] // X_bound for i in range(6)]
    print(f"  cand_x bits: {[abs(x).bit_length() for x in cand_x]}")
    print(f"  cand_x: {cand_x}")
    # If const == 0, this is a relation in the kernel!
    # A vector in the kernel gives: sum(vec_M[i] * x[i]) = 0 mod M_total!
