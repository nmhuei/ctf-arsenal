# stego — layered, source-only steganography

Hides a string (or arbitrary bytes) inside an image so that it is recoverable,
visually invisible, and practically impossible to reverse-engineer **without
this source tree**. There is **no passphrase** — by design, all security lives
in the algorithm and its baked-in secrets.

## Usage

```bash
# hide
python3 -m stego embed   sekai.png out.png "your secret text"
python3 -m stego embed   sekai.png out.png --infile message.bin

# recover
python3 -m stego extract out.png
python3 -m stego extract out.png --out recovered.bin
```

Output is always PNG (lossless — re-encoding to JPEG would destroy the
payload). Only Pillow is required.

## How it works

The payload passes through a stack of layers on the way in, reversed on the way
out:

| Step | Layer | Module |
|------|-------|--------|
| 1 | Frame: `MAGIC \| VER \| LEN \| DATA \| CRC32` | `coding/frame.py` |
| 2 | ChaCha20 stream encryption | `crypto/chacha20.py` |
| 3 | Keyed bijective 8-bit S-box (confusion) | `coding/sbox.py` |
| 4 | Position-dependent whitening (diffusion) | `coding/whiten.py` |
| 5 | Truncated HMAC-SHA256 authentication tag | `crypto/mac.py` |
| 6 | Multi-round keyed scatter of carrier slots (block-interleave → rotate → Feistel → Fisher–Yates) | `image/scatter.py` |
| 7 | ±1 matched LSB embedding (alpha untouched) | `image/embed.py` |

Every key is derived by an **HKDF key schedule bound to the image geometry**
(`crypto/kdf.py`) from the 64-byte `ROOT_SECRET` in `secret.py`. Because the
schedule mixes in width × height × channels, a payload embedded in one image
cannot be re-derived against another, and the entire cipher/nonce/S-box/scatter
configuration changes for every distinct image size.

## Package layout

```
stego/
  __init__.py        public API: embed(), extract()
  __main__.py        command-line interface
  pipeline.py        orchestrates all layers
  secret.py          baked-in root secret, salts, labels
  bits.py            bit (de)serialization
  crypto/
    kdf.py           HKDF-SHA256 key schedule (image-bound)
    chacha20.py      ChaCha20 stream cipher (RFC 8439)
    mac.py           HMAC-SHA256 authentication
    csprng.py        ChaCha20-based deterministic CSPRNG
  coding/
    frame.py         payload framing + CRC
    sbox.py          keyed bijective S-box
    whiten.py        positional whitening
  image/
    carrier.py       flat RGB carrier view over a Pillow image
    scatter.py       keyed slot ordering
    embed.py         ±1 matched LSB read/write
```

## Properties (measured on `sekai.png`, 828×449 RGBA)

- Alpha channel never modified → transparency preserved exactly
- Maximum per-channel change: **±1**
- ~0.06% of RGB samples altered for a ~140-byte message
- **PSNR ≈ 80 dB** (visually indistinguishable)
- Tampering with any carrier bit, or feeding a resized/different-geometry
  image, fails authentication and is cleanly rejected.

> The security model is *security through the secrecy of this source*. Anyone
> with these files can recover any payload; anyone without them cannot.
