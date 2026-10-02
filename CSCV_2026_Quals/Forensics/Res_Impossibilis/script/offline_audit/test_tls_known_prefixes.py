"""Verify AES schedule candidates against offline TLS records and protocol prefixes."""
from pathlib import Path
from itertools import permutations
import struct
import json
from Crypto.Cipher import AES

HERE = Path(__file__).resolve().parent
stream = (HERE / 'tls75_server.bin').read_bytes()
records = []
offset = 0
while offset + 5 <= len(stream):
    length = int.from_bytes(stream[offset+3:offset+5], 'big')
    if stream[offset] == 23:
        records.append((offset, stream[offset:offset+5], stream[offset+5:offset+5+length]))
    offset += 5 + length

prefixes = {b'HTTP/1.1 200 OK\r\n', b'HTTP/1.1 206 Par', b'HTTP/1.1 404 Not '}
# HTTP/2 server SETTINGS: length, type, flags, stream id, first setting, next id byte.
for length in range(6, 73, 6):
    for setting in range(1, 7):
        for value in [0, 1, 16, 32, 64, 100, 128, 256, 1000, 1024, 4096,
                      16384, 32768, 65535, 65536, 131072, 262144, 1048576,
                      4194304, 6291456, 16777216, 2147483647]:
            prefixes.add(length.to_bytes(3, 'big') + b'\x04\x00' + bytes(4)
                         + struct.pack('>HI', setting, value) + b'\x00')

# TLS 1.3 EncryptedExtensions with conventional ALPN and optional SNI acknowledgement.
for protocol in [b'h2', b'http/1.1']:
    alpn_data = struct.pack('>H', len(protocol)+1) + bytes([len(protocol)]) + protocol
    alpn = b'\x00\x10' + struct.pack('>H', len(alpn_data)) + alpn_data
    for extensions in [(alpn,), (alpn, b'\x00\x00\x00\x00')]:
        for ordered in permutations(extensions):
            body = b''.join(ordered)
            message = b'\x08' + (len(body)+2).to_bytes(3, 'big') + struct.pack('>H', len(body)) + body
            for certificate_length in range(32, 8192):
                certificate = (b'\x0b' + certificate_length.to_bytes(3, 'big') + b'\x00'
                               + (certificate_length-4).to_bytes(3, 'big') + b'\x00\x00')
                prefixes.add((message + certificate)[:16])
for certificate_length in range(32, 8192):
    prefixes.add(b'\x08\x00\x00\x02\x00\x00' + b'\x0b'
                 + certificate_length.to_bytes(3, 'big') + b'\x00'
                 + (certificate_length-4).to_bytes(3, 'big') + b'\x00\x00')
prefixes = sorted(p for p in prefixes if len(p) == 16)

keys = set()
for line in (HERE / 'aes_scan/aes_keys.txt').read_text().splitlines():
    if line.startswith('#'):
        continue
    key = bytes.fromhex(line.split('\t')[1])
    # This connection selected TLS_AES_128_GCM_SHA256.
    if len(key) != 16:
        continue
    keys.update([key, key[::-1], b''.join(key[i:i+4][::-1] for i in range(0, 16, 4))])

hits = []
counter_matches = 0
for position, aad, data in records:
    blocks = b''.join(bytes(a ^ b for a, b in zip(data[:16], prefix)) for prefix in prefixes)
    for key in keys:
        counters = AES.new(key, AES.MODE_ECB).decrypt(blocks)
        for i, prefix in enumerate(prefixes):
            counter = counters[16*i:16*i+16]
            if counter[12:] != b'\x00\x00\x00\x02':
                continue
            counter_matches += 1
            cipher = AES.new(key, AES.MODE_GCM, nonce=counter[:12])
            cipher.update(aad)
            try:
                plain = cipher.decrypt_and_verify(data[:-16], data[-16:])
            except ValueError:
                continue
            hits.append({'record_offset': position, 'key': key.hex(), 'nonce': counter[:12].hex(),
                         'prefix': prefix.hex(), 'plaintext': plain.hex()})
report = {'keys': len(keys), 'prefixes': len(prefixes), 'records': len(records),
          'counter_matches': counter_matches, 'authenticated_matches': hits}
(HERE / 'tls_protocol_prefix_results.json').write_text(json.dumps(report, indent=2) + '\n')
print({k: v for k, v in report.items() if k != 'authenticated_matches'})
print('Authenticated matches:', len(hits))
