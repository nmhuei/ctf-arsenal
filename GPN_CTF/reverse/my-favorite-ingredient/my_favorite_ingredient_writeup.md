# my-favorite-ingredient — Writeup

## Challenge type
Reverse engineering, ELF x86-64.

## Files
```text
my-favorite-ingredient.tar.gz
└── my-favorite-ingredient
    └── my-favorite-ingredient
```

## Recon
```bash
$ file my-favorite-ingredient
my-favorite-ingredient: ELF 64-bit LSB pie executable, x86-64, dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=014cdb93268fd4d0fbda59a4f70ca88f381c5524, for GNU/Linux 3.2.0, not stripped

$ nm -C my-favorite-ingredient | grep ' T '
0000000000001170 T verify_flag
00000000000015b0 t matvec_mul_vectorized
0000000000006c00 T main
0000000000006cf0 t matvec_mul_bitslice
```

Running the binary shows it expects one 64-character flag:

```bash
$ ./my-favorite-ingredient
Usage: ./my-favorite-ingredient <flag>

$ ./my-favorite-ingredient test
Flag must be 64 characters long.
```

## Reversing notes

`main()` copies:

- `0x1000` bytes from `.rodata+0x170`, used as a `64 x 64` byte matrix.
- `64` bytes from `.rodata+0x1170`, used as the check target.

Then it calls:

```c
verify_flag(input, 64, matrix, target)
```

Inside `verify_flag`, the input is first transformed byte-by-byte:

```text
x -> 197*x + 101 mod 256
```

Then `matvec_mul_vectorized()` immediately applies the inverse:

```text
y -> 13*y + 0xdf mod 256
```

because:

```text
13 * 197 = 2561 ≡ 1 mod 256
13 * 101 + 0xdf = 1536 ≡ 0 mod 256
```

So the two layers cancel and the actual unknown vector is the original 64-byte flag.

The final output is again affine-transformed before comparison:

```text
out = 197 * raw_result + 101 mod 256
```

The comparison target is `~target[i]`, so the RHS before the final affine layer is:

```text
rhs[i] = 13 * (~target[i]) + 0xdf mod 256
```

Testing the effective function showed it is linear over addition modulo `256`, not XOR:

```text
F(a + b mod 256) == F(a) + F(b) mod 256
```

Therefore the challenge reduces to solving:

```text
A * flag = rhs  (mod 256)
```

where `A` is recovered by querying the mapped `matvec_mul_vectorized()` with unit vectors.

## Solver idea

1. Manually map the PIE ELF into memory.
2. Call internal function `matvec_mul_vectorized` at offset `0x15b0`.
3. Recover the effective `64 x 64` matrix by evaluating basis vectors.
4. Invert the system over `Z/256Z` using only odd pivots.
5. Verify the recovered input using both the mapped function and the original binary.

## Solver run

```bash
$ python3 solve_my_favorite_ingredient.py ./my-favorite-ingredient
GPNCTF{juS7_One_0N57rucTion5_1S_4L1_Y0u_neeD_MAyb3123979AfKFNdh}
[+] local verify via mapped binary code: True
[+] local verify via original binary: Correct flag!
```

## Flag proof

The flag is 64 characters long and is accepted by the original challenge binary:

```bash
$ FLAG='GPNCTF{juS7_One_0N57rucTion5_1S_4L1_Y0u_neeD_MAyb3123979AfKFNdh}'
$ echo -n "$FLAG" | wc -c
64

$ ./my-favorite-ingredient "$FLAG"
Correct flag!
```

## Flag

```text
GPNCTF{juS7_One_0N57rucTion5_1S_4L1_Y0u_neeD_MAyb3123979AfKFNdh}
```

## Actual local log

```text
$ ls -l /mnt/data/my-favorite-ingredient.tar.gz
-rw-r--r-- 1 root oai_shared 46234 Jun  6 01:23 /mnt/data/my-favorite-ingredient.tar.gz

$ file /mnt/data/my-favorite-ingredient.tar.gz
/mnt/data/my-favorite-ingredient.tar.gz: gzip compressed data, original size modulo 2^32 215552

$ tar -xzf /mnt/data/my-favorite-ingredient.tar.gz -C /mnt/data/ctf_mfi

$ find /mnt/data/ctf_mfi -maxdepth 3 -type f -printf '%p\n' | sort
/mnt/data/ctf_mfi/my-favorite-ingredient/my-favorite-ingredient

$ file my-favorite-ingredient
my-favorite-ingredient: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=014cdb93268fd4d0fbda59a4f70ca88f381c5524, for GNU/Linux 3.2.0, not stripped

$ sha256sum my-favorite-ingredient
ce66a3812ed28d4799813de9e6be10c09e8991a409a7f4f627d798cd71daed7c  my-favorite-ingredient

$ ./my-favorite-ingredient
Usage: ./my-favorite-ingredient <flag>

$ ./my-favorite-ingredient test
Flag must be 64 characters long.

$ nm -C my-favorite-ingredient | grep ' T '
0000000000001170 T verify_flag
00000000000015b0 t matvec_mul_vectorized
0000000000006c00 T main
0000000000006cf0 t matvec_mul_bitslice

$ python3 solve_my_favorite_ingredient.py ./my-favorite-ingredient
GPNCTF{juS7_One_0N57rucTion5_1S_4L1_Y0u_neeD_MAyb3123979AfKFNdh}
[+] local verify via mapped binary code: True
[+] local verify via original binary: Correct flag!

$ FLAG='GPNCTF{juS7_One_0N57rucTion5_1S_4L1_Y0u_neeD_MAyb3123979AfKFNdh}'
$ echo -n "$FLAG" | wc -c
64
$ ./my-favorite-ingredient "$FLAG"
Correct flag!
```

## Remote/server note

No remote host/port was included in the uploaded archive or prompt. This challenge is a reverse-engineering binary that validates the flag locally, so the recovered flag above is ready to submit to the scoreboard. If a remote checker is provided, send exactly the same flag string.
