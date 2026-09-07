load('test_u_modn.sage')

V01 = vector(ZZ, [x // n for x in u01])
V02 = vector(ZZ, [x // n for x in u02])
V12 = vector(ZZ, [x // n for x in u12])

print("V01:", V01)
print("V02:", V02)
print("V12:", V12)

print("V01 bit lengths:", [abs(x).bit_length() for x in V01])
print("V02 bit lengths:", [abs(x).bit_length() for x in V02])
print("V12 bit lengths:", [abs(x).bit_length() for x in V12])

# Check: Kc . V01 == 0:
# Because Kc . u01 = h0 * (Kc . col1) - h1 * (Kc . col0) = h0 * h1 - h1 * h0 = 0!
print("Kc . V01 == 0:", Kc * V01 == 0)
print("Kc . V02 == 0:", Kc * V02 == 0)
print("Kc . V12 == 0:", Kc * V12 == 0)

# Check linear dependence among V01, V02, V12:
# h2 * V01 - h1 * V02 + h0 * V12 == 0?
print("h2*V01 - h1*V02 + h0*V12 == 0:", h2 * V01 - h1 * V02 + h0 * V12 == 0)
