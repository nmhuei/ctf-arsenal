# Authenticator Firebird solver - AVX2 build

This version does not require AVX512. It requires AVX2 and OpenMP/GCC.

Check CPU flags:

```bash
grep -m1 avx2 /proc/cpuinfo
```

Run:

```bash
python3 solve_authenticator_avx2.py archive.cryptohack.org 40156 --threads 4 --seconds 7 --random-start
```

If it is slow, increase threads or run on bare metal instead of a VM:

```bash
python3 solve_authenticator_avx2.py archive.cryptohack.org 40156 --threads $(nproc) --seconds 8 --random-start
```

The challenge password changes every connection, so each attempt is probabilistic. A typical AVX2 CPU may need many attempts.
