load('test_sol2_w0.sage')

w0 = ZZ(w0_from_x3 * 2) # check if scaled by 2
w1_int = ZZ(w1)
w2_int = ZZ(w2)

print("w0 bit length:", w0.bit_length())
print("w1 bit length:", w1_int.bit_length())
print("w2 bit length:", w2_int.bit_length())
print("c bit lengths:", [abs(x).bit_length() for x in c])

# Check if there is a common scaling factor between w0, w1, w2:
# Remember x1 = w1^2 was 627 bits, but W1^2 is 572 bits!
# 627 - 572 = 55 bits!
# So x was scaled by a common factor S^2!
# Let's find S:
print("x1 / W1^2 approx:", RR(x1 / (W1^2)))
print("log2(x1 / W1^2):", RR(x1 / (W1^2)).log(2).n())

