"""Collect recovered member plaintext; verify CRC, size, and available ciphertext.

This does not claim recovery of the original ZIP password or missing files.
"""
from pathlib import Path
import ctypes, hashlib, json, re, struct, sys, zlib
HERE = Path(__file__).resolve().parent
BASE = HERE.parent
sys.path.insert(0, str(BASE))
from verify_zip_evidence import INITIAL, TABLE


def encrypt(data):
    a, b, c = INITIAL
    result = bytearray()
    for value in data:
        temporary = (c & 65535) | 2
        result.append(value ^ ((temporary * (temporary ^ 1) >> 8) & 255))
        a = (a >> 8) ^ TABLE[(a ^ value) & 255]
        b = ((b + (a & 255)) * 134775813 + 1) & 0xffffffff
        c = (c >> 8) ^ TABLE[(c ^ (b >> 24)) & 255]
    return bytes(result)


def main():
    entries = json.loads((BASE / 'archive_central_records.json').read_text())
    archive = (BASE / 'agent_archive/pte_archive.zip').read_bytes()
    mask = (BASE / 'agent_archive/pte_known.bin').read_bytes()
    sources = [BASE / 'agent_archive', HERE,
               BASE / 'agent_password/recovered_files', BASE / 'agent_collector/recovered_files']
    output = BASE / 'recovered39'
    output.mkdir(exist_ok=True)
    libc = ctypes.CDLL('libc.so.6')
    libc.srand(1788885121)
    headers = [bytes(libc.rand() & 255 for _ in range(11)) for _ in entries]
    central = (BASE / 'archive_central_directory.bin').read_bytes()
    central_position = 0
    results = []
    for index, entry in enumerate(entries):
        ch = struct.unpack_from('<4s6H3I5H2I', central, central_position)
        assert ch[0] == b'PK\x01\x02' and ch[16] == entry['local_offset']
        assert ch[4] == 0 and ch[11] == 0, 'Handle compression/extras explicitly'
        central_position += 46 + ch[10] + ch[11] + ch[12]
        result = dict(index=index, **entry, status='missing', sources=[])
        result['recovery_method'] = ('Firefox reference plus memory ciphertext, full CRC verified' if index == 27
                                     else 'memory ciphertext decrypted' if index <= 30 or index == 38
                                     else 'known prefix completed with Firefox default' if index == 31
                                     else 'Firefox default reconstructed and CRC checked' if 32 <= index <= 35
                                     else 'pending')
        expected_name = f'{index:02d}_{Path(entry["name"]).name}'
        for source in sources:
            path = source / expected_name
            if not path.exists():
                continue
            data = path.read_bytes()
            if len(data) != entry['plain_size'] or zlib.crc32(data) != int(entry['crc32'], 16):
                raise ValueError(f'Invalid purported recovery: {path}')
            # The custom collector uses no local extras; directory and known
            # local offsets verify this layout on all complete recovered entries.
            start = entry['local_offset'] + 30 + ch[10]
            header = headers[index] + bytes([int(entry['crc32'], 16) >> 24])
            encrypted = encrypt(header + data)
            covered = 0
            for j, value in enumerate(encrypted, start):
                if mask[j]:
                    assert archive[j] == value, f'Ciphertext mismatch for entry {index} at {j}'
                    covered += 1
            result.update(status='verified', crc_valid=True, size_valid=True,
                          known_ciphertext_bytes_matched=covered,
                          sha256=hashlib.sha256(data).hexdigest(), output=expected_name)
            result['sources'].append(str(path.relative_to(BASE)))
            destination = output / expected_name
            if destination.exists():
                assert destination.read_bytes() == data
            else:
                destination.write_bytes(data)
        results.append(result)
    report = {'verified_files': sum(r['status'] == 'verified' for r in results),
              'total_files': len(results), 'password_recovered': False, 'entries': results}
    (output / 'manifest.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'verified_files': report['verified_files'],
                      'missing': [r['name'] for r in results if r['status'] == 'missing']}))


if __name__ == '__main__':
    main()
