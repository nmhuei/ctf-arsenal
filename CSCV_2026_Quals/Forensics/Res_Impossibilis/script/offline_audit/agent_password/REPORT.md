# Password model audit

The original archive password remains unknown. No matching candidate was found.
All new files from this audit are confined to this directory.

## Cryptographic model and interpretation

The existing C verifier computes the ordinary three ZIPCrypto password states
from `12345678 23456789 34567890` and compares all three words to the recovered
`670e8462 306591b4 8372919d`. The source uses unsigned 32-bit arithmetic, so its
updates have the required modulo-2^32 behavior. `setup()` is called before either
candidate driver uses it. `find_password` tests every byte substring up to 128
bytes, using the first key as an efficient rejection check before checking all
three words.

A state match proves the byte sequence derives equivalent archive keys. It
does not prove that sequence was the original password used by the collector.
This distinction matters for the flag's answer 3. The state has only 96 bits;
there are more 95-character printable strings of length 15 than possible states.
Thus the map cannot identify original passwords uniquely across unrestricted
passwords. This pigeonhole observation does not by itself say that this target
has a particular number of preimages or that their distribution is uniform.

The C verifier accepts explicit lengths and therefore accepts NUL bytes. A
collector using a usual C string password API would stop at the first NUL.
The RNG search includes every prefix before NUL and marks hypothetical matches
containing NUL separately. No matches of either kind occurred.

The archive agent independently reported that all recovered encryption headers
follow `rand()` bytes starting at index 11 * entry_index from `srand(1788885121)`.
This excludes extra random draws between those headers under that generator
model. It does not exclude password generation before reseeding, from a
different RNG, or from identity/static data.

## Bounded generation tests

Run:

```sh
python script/offline_audit/agent_password/bounded_hypotheses.py
```

`bounded_hypotheses_results.json` records zero matches for:

| Family | Sequences checked |
|---|---:|
| Raw glibc RNG bytes/words and encodings |29952|
| Host/machine/boot/time identity encodings |21168|
| MD5/SHA1/SHA256/SHA512 identity digest encodings |84672|
| Inlined FNV1/FNV1a/djb2/sdbm 64 identity hashes |28224|
| Truncated machine/boot identifiers with hostname/user |15120|

Every sequence is checked for all substrings up to 128 bytes. The RNG family
uses 416 explicit seeds: the already bounded time interval 1788884900..1788885300,
0 and1, observed machine/boot 32-bit chunks, and CRC32 of observed identity
strings. Each produces 96 rand outputs. New representations include raw byte
lanes, little/big-endian 16/32-bit words, Base32/Base64/Base85, ASCII85 and hex.
The default glibc state is covered by seed 1.

There are 2352 identity input strings built only from the stated machine ID,
boot ID, hostname, user, time and collector/archive names. Exact atoms,
delimiters, hashes and truncation bounds are preserved in the source.
Hash hypotheses are speculative: absence of imported crypto functions argues
against library digest generation but permits inlined digest/simple-hash code.

## UTF-8 memory test

Run:

```sh
cc -O3 -Wall -Wextra -o script/offline_audit/agent_password/scan_utf8 script/offline_audit/agent_password/scan_utf8.c
script/offline_audit/agent_password/scan_utf8 script/evidence/mem.clean
```

`utf8_results.log` records the complete 8589332605-byte image scan. There were
261722 valid UTF-8 runs of 13..4096 bytes containing at least one nonASCII scalar,
totalling 12767858 bytes. All their substrings up to 128 bytes were checked with
zero matches. The scanner accepts printable ASCII plus tab/CR/LF and strict
UTF-8 scalar encodings, including accented characters and emoji.

Explicit coverage gaps: 1554 valid Unicode runs longer than 4096 bytes were
skipped; runs shorter than 13 bytes were skipped; malformed UTF-8, UTF-16
conversions, nontext binary bytes and fragmented buffers are not covered by
this scanner. The earlier printable-ASCII search does not exclude short
nonASCII passwords.

## Most useful next evidence

Recover collector code/read-only data around password construction or the
60-byte audit log, and use it to constrain original-password generation.
These would discriminate among original and equivalent passwords and provide
much stronger direction than extending unconstrained printable inversion.
An extended UTF-8 pass covering the explicit short/long gaps is also a bounded
remaining experiment, but presently lacks a clue favoring a Unicode password.
