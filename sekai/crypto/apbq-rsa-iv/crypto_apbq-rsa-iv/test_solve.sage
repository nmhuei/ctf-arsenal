from Crypto.Util.number import bytes_to_long, long_to_bytes

with open('apbq-rsa-iv.py') as f:
    text = f.read()
exec(text.split("'''")[1])

h0, h1, h2 = hints

A1 = (h1 * pow(h0, -1, n)) % n
A2 = (h2 * pow(h0, -1, n)) % n

print("A1 bits:", A1.bit_length())
print("A2 bits:", A2.bit_length())
