from pathlib import Path
cpp=Path('script/residue_search.cpp').read_text().replace('%100000==0','%1000000==0')
header='''#!/usr/bin/env python3
"""Offline solver for the supplied Chimera archive.

Run with SageMath's Python: sage solver/solve.py
Requires g++, GMP headers/library, and SageMath. No network access is used.
The C++ helper is embedded here and built under script/.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
from zipfile import ZipFile

from sage.all import ZZ, QQ, gcd, identity_matrix, matrix, prime_range

M = 31721752939659896617792337171084495768312741523809821454149295955199893657462682088273
ORDER = 21621600
ROOT = Path(__file__).resolve().parents[1]

'''
body='''

def recover_modulus(samples, work):
    """Cancel all 129 coefficients of the XOR exponents over the integers."""
    count = len(samples)
    bits = matrix(ZZ, [[1] + [(c >> j) & 1 for j in range(128)]
                       for c, _ in samples])
    basis = identity_matrix(ZZ, count).augment(bits * 2**32)
    reduced = basis.LLL()
    relations = [list(row[:count]) for row in reduced
                 if not any(row[count:])]
    modulus = ZZ(0)
    evidence = []
    small_primes = list(prime_range(10000))
    for weights in relations:
        assert not any(matrix(ZZ, [weights]) * bits)
        left, right = ZZ(1), ZZ(1)
        for weight, (_, value) in zip(weights, samples):
            if weight > 0:
                left *= ZZ(value) ** weight
            elif weight < 0:
                right *= ZZ(value) ** (-weight)
        modulus = gcd(modulus, left - right)
        evidence.append([int(w) for w in weights])
        if len(evidence) >= 2:
            for ell in small_primes:
                while modulus and modulus % ell == 0:
                    modulus //= ell
        print(f"Modulus relation {len(evidence)}: {modulus.nbits()} bits", flush=True)
        if modulus.nbits() == 768:
            break
    assert modulus.nbits() == 768, "Modulus recovery did not converge"
    assert all(0 < value < modulus for _, value in samples)
    (work / 'modulus.json').write_text(json.dumps({
        'N': int(modulus), 'relations': evidence}, indent=2) + '\\n')
    return modulus


def recover_token(samples, modulus, base):
    """Invert the bit matrix; test each bit's positive or negative exponent."""
    selected = samples[:129]
    bits = matrix(QQ, [[1] + [(c >> j) & 1 for j in range(128)]
                       for c, _ in selected])
    assert bits.rank() == 129
    inverse = bits.inverse()
    token = 0
    for j in range(128):
        row = inverse[j + 1]
        denominator = row.denominator()
        value = ZZ(1)
        for coefficient, (_, observed) in zip(row, selected):
            weight = ZZ(coefficient * denominator)
            value = value * pow(ZZ(observed), weight, modulus) % modulus
        positive = pow(ZZ(base), ZZ(denominator) * 2**j, modulus)
        negative = pow(positive, -1, modulus)
        assert positive != negative, "Bit sign is ambiguous"
        if value == negative:
            token |= 1 << j
        else:
            assert value == positive, f"Inconsistent token bit {j}"
    assert all(pow(base, token ^ c, modulus) == value for c, value in samples)
    print(f"Verified all {len(samples)} attestations", flush=True)
    return token


def recover_factors(modulus, work):
    """Enumerate subgroup residues and solve the bounded 2D congruence."""
    source = work / 'residue_search.cpp'
    executable = work / 'residue_search'
    output = work / 'factors.json'
    source.write_text(CPP_SOURCE)
    subprocess.run(['g++', '-O3', '-o', str(executable), str(source),
                    '-lgmpxx', '-lgmp'], check=True)
    result = subprocess.run([str(executable), str(modulus), '0', str(ORDER),
                             str(output)], capture_output=True, text=True)
    (work / 'residue_search.log').write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(f"Residue search failed; see {work / 'residue_search.log'}")
    found = json.loads(output.read_text())
    p, q, a = ZZ(found['p']), ZZ(found['q']), int(found['a'])
    assert 0 <= a < ORDER
    assert p * q == modulus
    assert p.nbits() == q.nbits() == 384
    assert p.is_prime(proof=True) and q.is_prime(proof=True)
    assert p % M == pow(17, a, M)
    print(f"Verified prime factors at a={a}", flush=True)
    return p, q, a


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, default=ROOT / 'challenge/here')
    parser.add_argument('--url', help='Unsupported: this challenge is offline')
    parser.add_argument('--remote', metavar='HOST:PORT',
                        help='Unsupported: this challenge is offline')
    args = parser.parse_args()
    if args.url or args.remote:
        parser.error('This solver uses the recorded offline data only')
    started = time.monotonic()
    work = ROOT / 'script'
    work.mkdir(exist_ok=True)
    with ZipFile(args.archive) as archive:
        data = json.loads(archive.read('chimera_student/output_chimera.txt'))
    samples = data['attestations']
    assert len(samples) == 200
    assert all(0 <= c < 2**128 for c, _ in samples)
    modulus = recover_modulus(samples, work)
    token = recover_token(samples, modulus, data['base_c'])
    print('Searching the 21,621,600 allowed residues...', flush=True)
    p, q, a = recover_factors(modulus, work)
    d = pow(ZZ(data['e']), -1, (p - 1) * (q - 1))
    plaintext = pow(ZZ(data['flag_ct']), d, modulus)
    assert pow(plaintext, data['e'], modulus) == data['flag_ct']
    flag = int(plaintext).to_bytes((plaintext.nbits() + 7) // 8, 'big')
    assert flag.startswith(b'CSCV{') and flag.endswith(b'}')
    (ROOT / 'flag.txt').write_bytes(flag + b'\\n')
    evidence = {
        'N': int(modulus), 'p': int(p), 'q': int(q), 'a': a,
        'token': token, 'verified_attestations': len(samples),
        'prime_factors_verified': True, 'residue_verified': True,
        'rsa_reencryption_verified': True, 'flag_status': 'VERIFIED',
        'archive_sha256': hashlib.sha256(args.archive.read_bytes()).hexdigest(),
        'elapsed_seconds': round(time.monotonic() - started, 3),
    }
    (work / 'verification.json').write_text(json.dumps(evidence, indent=2) + '\\n')
    (work / 'worker-report.json').write_text(json.dumps({
        'local_verification': 'passed',
        'summary': 'Recovered N, verified 200 attestations, proved both 384-bit '
                   'factors prime, checked the subgroup residue and RSA reencryption.',
        'flag_status': 'VERIFIED', 'submitted': False,
    }, indent=2) + '\\n')
    print(flag.decode(), flush=True)
    print(f"Completed in {evidence['elapsed_seconds']} seconds; saved flag.txt", flush=True)


if __name__ == '__main__':
    main()
'''
Path('solver/solve.py').write_text(header+'CPP_SOURCE = '+repr(cpp)+'\n'+body)
