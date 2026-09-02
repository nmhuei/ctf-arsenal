#!/usr/bin/env python3
"""
CryptoHack AES / Paper Plane solver.

Local mode demonstrates the vulnerability on a self-contained AES-IGE service.
Remote mode uses the same padding-oracle attack against aes.cryptohack.org.

Usage:
  python3 solve_paper_plane.py --local
  python3 solve_paper_plane.py --remote
  python3 solve_paper_plane.py --remote --base https://aes.cryptohack.org/paper_plane
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Tuple
from urllib.parse import urljoin

try:
    import requests
except ImportError:  # remote mode only
    requests = None

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BLOCK = 16


def xor(a: bytes | bytearray, b: bytes | bytearray) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


def pkcs7_pad(m: bytes, block_size: int = BLOCK) -> bytes:
    p = block_size - (len(m) % block_size)
    return m + bytes([p]) * p


def pkcs7_unpad(m: bytes, block_size: int = BLOCK) -> bytes:
    if not m or len(m) % block_size:
        raise ValueError("bad padded length")
    p = m[-1]
    if p < 1 or p > block_size or m[-p:] != bytes([p]) * p:
        raise ValueError("bad padding")
    return m[:-p]


def aes_ecb_encrypt_block(key: bytes, block: bytes) -> bytes:
    enc = Cipher(algorithms.AES(key), modes.ECB()).encryptor()
    return enc.update(block) + enc.finalize()


def aes_ecb_decrypt_block(key: bytes, block: bytes) -> bytes:
    dec = Cipher(algorithms.AES(key), modes.ECB()).decryptor()
    return dec.update(block) + dec.finalize()


def ige_encrypt(key: bytes, plaintext: bytes, iv: bytes) -> bytes:
    """AES-IGE encryption with IV = C_0 || P_0."""
    if len(iv) != 2 * BLOCK:
        raise ValueError("IGE IV must be 32 bytes")
    plaintext = pkcs7_pad(plaintext)
    c_prev, p_prev = iv[:BLOCK], iv[BLOCK:]
    out = []
    for off in range(0, len(plaintext), BLOCK):
        p = plaintext[off : off + BLOCK]
        c = xor(aes_ecb_encrypt_block(key, xor(p, c_prev)), p_prev)
        out.append(c)
        c_prev, p_prev = c, p
    return b"".join(out)


def ige_decrypt_raw(key: bytes, ciphertext: bytes, iv: bytes) -> bytes:
    if len(iv) != 2 * BLOCK:
        raise ValueError("IGE IV must be 32 bytes")
    if len(ciphertext) == 0 or len(ciphertext) % BLOCK:
        raise ValueError("ciphertext length must be a positive multiple of 16")
    c_prev, p_prev = iv[:BLOCK], iv[BLOCK:]
    out = []
    for off in range(0, len(ciphertext), BLOCK):
        c = ciphertext[off : off + BLOCK]
        p = xor(aes_ecb_decrypt_block(key, xor(c, p_prev)), c_prev)
        out.append(p)
        c_prev, p_prev = c, p
    return b"".join(out)


def recover_block(
    oracle: Callable[[bytes, bytes], bool],
    prev_cipher: bytes,
    prev_plain: bytes,
    target_block: bytes,
) -> bytes:
    """
    Recover one original IGE plaintext block.

    In IGE decryption: P_i = D(C_i xor P_{i-1}) xor C_{i-1}.
    Submit a one-block ciphertext C_i with IV=(fake_C_{i-1} || known_P_{i-1}).
    Then P_test = D(C_i xor known_P_{i-1}) xor fake_C_{i-1}, so varying
    fake_C_{i-1} gives a standard CBC-style padding oracle.
    """
    if not (len(prev_cipher) == len(prev_plain) == len(target_block) == BLOCK):
        raise ValueError("all block inputs must be 16 bytes")

    intermediate = bytearray(BLOCK)  # D(C_i xor P_{i-1})
    fake = bytearray(os.urandom(BLOCK))

    for pad in range(1, BLOCK + 1):
        pos = BLOCK - pad

        for j in range(pos + 1, BLOCK):
            fake[j] = intermediate[j] ^ pad

        chosen: Optional[int] = None
        for guess in range(256):
            fake[pos] = guess
            test_iv = bytes(fake) + prev_plain
            if not oracle(test_iv, target_block):
                continue

            if pad == 1 and pos > 0:
                # Reject the false hit where an existing multi-byte padding was preserved.
                check = bytearray(fake)
                check[pos - 1] ^= 1
                if not oracle(bytes(check) + prev_plain, target_block):
                    continue

            chosen = guess
            break

        if chosen is None:
            raise RuntimeError(f"padding oracle failed at byte {pos} / pad {pad}")

        intermediate[pos] = chosen ^ pad

    return xor(intermediate, prev_cipher)


def recover_plaintext(
    oracle: Callable[[bytes, bytes], bool],
    iv: bytes,
    ciphertext: bytes,
    verbose: bool = True,
) -> bytes:
    if len(iv) != 2 * BLOCK:
        raise ValueError("IV must be 32 bytes")
    if len(ciphertext) == 0 or len(ciphertext) % BLOCK:
        raise ValueError("ciphertext must be a non-empty multiple of 16 bytes")

    prev_cipher, prev_plain = iv[:BLOCK], iv[BLOCK:]
    recovered = bytearray()
    blocks = [ciphertext[i : i + BLOCK] for i in range(0, len(ciphertext), BLOCK)]

    for idx, block in enumerate(blocks, 1):
        p = recover_block(oracle, prev_cipher, prev_plain, block)
        recovered.extend(p)
        if verbose:
            printable = bytes(recovered).decode("utf-8", "replace")
            print(f"[+] recovered block {idx}/{len(blocks)}: {p.hex()}  {printable!r}", flush=True)
        prev_cipher, prev_plain = block, p

    return pkcs7_unpad(bytes(recovered))


def local_demo() -> None:
    key = os.urandom(16)
    iv = os.urandom(32)
    secret = b"crypto{local_padding_oracle_demo_for_paper_plane}"
    ciphertext = ige_encrypt(key, secret, iv)

    queries = 0

    def oracle(test_iv: bytes, test_ct: bytes) -> bool:
        nonlocal queries
        queries += 1
        try:
            pkcs7_unpad(ige_decrypt_raw(key, test_ct, test_iv))
            return True
        except ValueError:
            return False

    print(f"[*] local iv = {iv.hex()}")
    print(f"[*] local ct = {ciphertext.hex()}")
    recovered = recover_plaintext(oracle, iv, ciphertext)
    print(f"[+] local recovered plaintext: {recovered!r}")
    print(f"[+] local oracle queries: {queries}")


@dataclass
class OracleEndpoint:
    name: str
    build_path: Callable[[bytes, bytes], str]
    invalid_signature: Tuple[int, str]


class RemotePaperPlane:
    def __init__(self, base: str, delay: float = 0.0):
        if requests is None:
            raise RuntimeError("requests is required for remote mode: pip install requests")
        self.base = base.rstrip("/") + "/"
        self.s = requests.Session()
        self.delay = delay
        self.endpoint: Optional[OracleEndpoint] = None
        self.calls = 0

    def get_json(self, path: str) -> dict:
        url = urljoin(self.base, path.lstrip("/"))
        r = self.s.get(url, timeout=20)
        r.raise_for_status()
        try:
            return r.json()
        except json.JSONDecodeError as e:
            raise RuntimeError(f"expected JSON from {url}, got: {r.text[:200]!r}") from e

    def fetch_encrypted_flag(self) -> Tuple[bytes, bytes]:
        data = self.get_json("encrypt_flag/")
        print(f"[*] encrypt_flag response keys: {sorted(data.keys())}")

        ct_hex = (
            data.get("ciphertext")
            or data.get("encrypted_flag")
            or data.get("ct")
            or data.get("flag")
        )
        iv_hex = data.get("iv") or data.get("nonce")

        if not ct_hex:
            raise RuntimeError(f"could not find ciphertext in response: {data}")

        ct = bytes.fromhex(ct_hex)
        if "c0" in data and "m0" in data:
            # Paper Plane exposes the two AES-IGE IV halves separately.
            # IGE uses IV = C_0 || P_0, and the API names these c0 and m0.
            iv = bytes.fromhex(data["c0"]) + bytes.fromhex(data["m0"])
        elif iv_hex:
            iv = bytes.fromhex(iv_hex)
        else:
            # Some CryptoHack endpoints prepend the IGE IV to the ciphertext.
            if len(ct) < 3 * BLOCK:
                raise RuntimeError("no IV field and ciphertext too short to contain a 32-byte IV")
            iv, ct = ct[: 2 * BLOCK], ct[2 * BLOCK :]

        if len(iv) != 2 * BLOCK:
            raise RuntimeError(f"unexpected IV length: {len(iv)} bytes")
        if len(ct) == 0 or len(ct) % BLOCK:
            raise RuntimeError(f"unexpected ciphertext length: {len(ct)} bytes")

        print(f"[*] iv = {iv.hex()}")
        print(f"[*] ct = {ct.hex()}")
        return iv, ct

    @staticmethod
    def _sig(r) -> Tuple[int, str]:
        text = r.text.strip()
        # Normalize minor JSON whitespace if possible.
        try:
            text = json.dumps(r.json(), sort_keys=True)
        except Exception:
            pass
        return r.status_code, text

    def _get_path(self, path: str):
        if self.delay:
            time.sleep(self.delay)
        self.calls += 1
        url = urljoin(self.base, path.lstrip("/"))
        return self.s.get(url, timeout=20)

    def discover_oracle(self, iv: bytes, ct: bytes) -> None:
        bad_ct = ct[:-1] + bytes([ct[-1] ^ 1])
        bad_iv = iv[:-1] + bytes([iv[-1] ^ 1])

        builders = []
        for endpoint_name in ("send_msg", "receive", "decrypt"):
            builders.extend(
                [
                    # Paper Plane's documented route is this exact shape:
                    # /send_msg/<ciphertext>/<m0>/<c0>/
                    # Internally this solver stores iv as c0 || m0, so pass
                    # tiv[BLOCK:] first, then tiv[:BLOCK].
                    (
                        f"{endpoint_name}/ct/m0/c0",
                        lambda tiv, tct, n=endpoint_name: (
                            f"{n}/{tct.hex()}/{tiv[BLOCK:].hex()}/{tiv[:BLOCK].hex()}/"
                        ),
                    ),
                    # Keep the older/wrong guesses below only as fallbacks for
                    # clones of the challenge with altered route parameter order.
                    (
                        f"{endpoint_name}/ct/c0/m0",
                        lambda tiv, tct, n=endpoint_name: (
                            f"{n}/{tct.hex()}/{tiv[:BLOCK].hex()}/{tiv[BLOCK:].hex()}/"
                        ),
                    ),
                    (
                        f"{endpoint_name}/c0/m0/ct",
                        lambda tiv, tct, n=endpoint_name: (
                            f"{n}/{tiv[:BLOCK].hex()}/{tiv[BLOCK:].hex()}/{tct.hex()}/"
                        ),
                    ),
                    (
                        f"{endpoint_name}/ct/iv",
                        lambda tiv, tct, n=endpoint_name: f"{n}/{tct.hex()}/{tiv.hex()}/",
                    ),
                    (
                        f"{endpoint_name}/iv/ct",
                        lambda tiv, tct, n=endpoint_name: f"{n}/{tiv.hex()}/{tct.hex()}/",
                    ),
                    (
                        f"{endpoint_name}/ivct",
                        lambda tiv, tct, n=endpoint_name: f"{n}/{(tiv + tct).hex()}/",
                    ),
                    (
                        f"{endpoint_name}/ctiv",
                        lambda tiv, tct, n=endpoint_name: f"{n}/{(tct + tiv).hex()}/",
                    ),
                ]
            )

        print("[*] discovering padding-oracle URL shape...")
        for name, builder in builders:
            try:
                good = self._get_path(builder(iv, ct))
                bad = self._get_path(builder(iv, bad_ct))
            except Exception as e:
                print(f"[-] {name}: request failed: {e}")
                continue

            good_sig = self._sig(good)
            bad_sig = self._sig(bad)
            if good.status_code == 404 and bad.status_code == 404:
                continue
            if good_sig == bad_sig:
                # Try IV mutation too; some endpoints may bundle or validate differently.
                try:
                    bad2 = self._get_path(builder(bad_iv, ct))
                    bad_sig = self._sig(bad2)
                except Exception:
                    pass
            if good_sig != bad_sig:
                self.endpoint = OracleEndpoint(name, builder, bad_sig)
                print(f"[+] using oracle format: {name}")
                print(f"[*] valid sample:   HTTP {good_sig[0]} {good_sig[1][:160]!r}")
                print(f"[*] invalid sample: HTTP {bad_sig[0]} {bad_sig[1][:160]!r}")
                return

        raise RuntimeError(
            "could not auto-detect send_msg/decrypt endpoint shape. "
            "Open the base URL in a browser and edit discover_oracle() with the shown route."
        )

    def oracle(self, iv: bytes, ct: bytes) -> bool:
        if self.endpoint is None:
            raise RuntimeError("oracle endpoint has not been discovered")
        r = self._get_path(self.endpoint.build_path(iv, ct))
        try:
            data = r.json()
            # Official Paper Plane response: {"msg": "Message received"}
            # Invalid padding response: {"error": "Can't decrypt the message."}
            if data.get("msg") == "Message received":
                return True
            if "error" in data:
                return False
        except Exception:
            pass
        return self._sig(r) != self.endpoint.invalid_signature


def remote_solve(base: str, delay: float) -> None:
    remote = RemotePaperPlane(base, delay=delay)
    iv, ct = remote.fetch_encrypted_flag()
    remote.discover_oracle(iv, ct)
    plaintext = recover_plaintext(remote.oracle, iv, ct)
    print(f"[+] remote recovered plaintext: {plaintext!r}")
    try:
        print(f"[+] as text: {plaintext.decode()}")
    except UnicodeDecodeError:
        pass
    print(f"[+] remote HTTP calls: {remote.calls}")


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--local", action="store_true", help="run self-contained local proof")
    mode.add_argument("--remote", action="store_true", help="attack the CryptoHack server")
    ap.add_argument("--base", default="https://aes.cryptohack.org/paper_plane", help="remote base URL")
    ap.add_argument("--delay", type=float, default=0.0, help="optional delay between remote requests")
    args = ap.parse_args(argv)

    if args.local:
        local_demo()
    else:
        remote_solve(args.base, args.delay)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
