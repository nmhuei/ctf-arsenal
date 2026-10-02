# ZIP writer and password formation audit

## Result

The original password construction is still unknown. The recovered value
`1788885121` is an effective glibc header-PRNG seed; it is not evidence of the
password itself or of a particular password formula.

## Independent observations

Reproduce with `python -B script/offline_audit/agent_archive/zip_writer_fingerprint.py`.
The script uses `pte_archive.zip` and `pte_known.bin`, which contain observed RAM
bytes. It deliberately excludes later synthesized encryption headers.

- Exactly 33 independently observed headers: member indices 0..31 and 38.
- All 363 bytes in their first 11 header positions equal the low byte of glibc
  `rand()` starting with seed 1788885121, at output index `11 * member_index`.
  A separate pure Python implementation of the glibc default generator confirms
  this; the audit does not execute the collector.
- Every twelfth header byte equals the member CRC32's most significant byte.
- The next-highest CRC byte differs from the eleventh header byte in all 33 cases.
  Example member 0: decrypted header `d534070c1972f229fcfec458`, CRC `58e4cad4`.
  A two-CRC-byte header would end `e458`, while the observed header ends `c458`.
- Indices 32..37 are not independently observed. Header 38 nevertheless agrees
  with the uninterrupted output index 418. Under the simple continuous PRNG
  model, those six headers account for the intervening 66 draws.
- All 39 central-directory records have identical writer metadata: made-by=20
  (version 2.0, host OS 0/DOS), needed=20, flags=1 (encryption; no descriptor),
  method=0 (stored), no extra fields/comments, zero attributes. All timestamps
  encode 2022-09-01 13:00:00 (`date=0x5521`, `time=0x6800`), unrelated to the
  effective seed's Unix time 2026-09-08 16:32:01 UTC.
- The validated ELF dynamic symbol table has 32 entries, including rand, srand,
  time, getenv, gethostname, fgets, snprintf, printf and ordinary filesystem I/O.
  No imported ZIP, zlib, or cryptographic API appears in that complete dynsym.
  This does not exclude statically included or modified library code.

## What the PRNG evidence constrains

An observational model consistent with the bytes is:

```
initialize header RNG with effective seed 1788885121
for each archive member:
    header[0:11] = next 11 glibc rand outputs, reduced modulo 256
    header[11] = CRC32(member) >> 24
    encrypt header and stored data with the password-derived ZIPCrypto state
```

This is a model of observed behavior, not recovered source code. It does not
prove where srand appears in the program, whether time(NULL) supplied its input,
or how the password was obtained.

A conventional single-global-RNG program that calls srand(S), consumes a
positive number of rand calls to construct a password, and then immediately
uses the same uninterrupted state for these headers predicts a shifted first
header. The observed first header starts at draw zero, strongly excluding that
simple construction. Reinitializing with the same seed for every member also
predicts identical random header prefixes, which the archive contradicts.

The following remain compatible: password construction before a later srand;
password generation from another state/source; construction directly from a
seed or identity data without rand calls; a fixed or externally read password;
or reuse of already generated values. Arbitrary state restoration or unusual
control flow cannot be excluded from output bytes alone. Additional rand calls
between the observed headers are inconsistent with the straightforward
continuous-state model.

## Library fingerprint comparison

Classic minizip's unmodified crypthead is incompatible with these headers:
it uses 10 random bytes and two high CRC bytes, rather than 11 random bytes and
one CRC byte. Its random-byte transformation also uses `(rand() >> 7) & 255`
and a preliminary ZIPCrypto pass. It seeds once inside crypthead with
`time(NULL) ^ ZCR_SEED2`, which illustrates why an observed header seed alone
cannot exclude an earlier password-generation RNG phase.

Primary source (crypthead, init_keys):
https://raw.githubusercontent.com/madler/zlib/v1.2.11/contrib/minizip/crypt.h
https://raw.githubusercontent.com/madler/zlib/v1.3.1/contrib/minizip/crypt.h

The sparse ZIP metadata, fixed historical timestamp, raw rand bytes, and lack
of dynamic ZIP imports support a small bespoke writer or modified embedded
code. They do not identify a particular library, author, or password formula.
The program may still reuse standard ZIPCrypto key-update code.

## Most direct missing evidence

Collector code/rodata around password construction or its original 60-byte
audit log could distinguish these compatible models. Recovered ZIPCrypto state
`670e8462 306591b4 8372919d` verifies candidate password bytes, but an arbitrary
equivalent preimage would not establish the original password.
