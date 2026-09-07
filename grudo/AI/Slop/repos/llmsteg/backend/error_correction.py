# Hamming(7,4) Error Correction Code Implementation
def hamming_encode(data_bits):
    # Split data bits into chunks of 4 bits
    chunks = [data_bits[i : i + 4] for i in range(0, len(data_bits), 4)]
    encoded_bits = ""
    for chunk in chunks:
        while len(chunk) < 4:
            chunk += "0"  # Pad with zeros if necessary
        d = [int(b) for b in chunk]
        # Calculate parity bits
        p1 = d[0] ^ d[1] ^ d[3]
        p2 = d[0] ^ d[2] ^ d[3]
        p3 = d[1] ^ d[2] ^ d[3]
        # Arrange bits in the order: p1, p2, d0, p3, d1, d2, d3
        encoded_chunk = f"{p1}{p2}{d[0]}{p3}{d[1]}{d[2]}{d[3]}"
        encoded_bits += encoded_chunk
    return encoded_bits


def hamming_decode(encoded_bits):
    # Split encoded bits into chunks of 7 bits
    chunks = [encoded_bits[i : i + 7] for i in range(0, len(encoded_bits), 7)]
    data_bits = ""
    for chunk in chunks:
        if len(chunk) < 7:
            continue  # Discard incomplete chunks
        bits = [int(b) for b in chunk]
        # Calculate syndrome bits
        s1 = bits[0] ^ bits[2] ^ bits[4] ^ bits[6]
        s2 = bits[1] ^ bits[2] ^ bits[5] ^ bits[6]
        s3 = bits[3] ^ bits[4] ^ bits[5] ^ bits[6]
        error_position = s1 * 1 + s2 * 2 + s3 * 4
        # Correct single-bit error if detected
        if error_position != 0:
            error_position -= 1  # Adjust for zero-based index
            bits[error_position] ^= 1
        # Extract data bits: bits at positions 2,4,5,6
        data_chunk = f"{bits[2]}{bits[4]}{bits[5]}{bits[6]}"
        data_bits += data_chunk
    return data_bits
