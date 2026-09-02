# Scanwich Station local analysis log

## Files inspected
- `Dockerfile`
- `app/app.py`
- `app/helpers/config.py`
- `app/helpers/decoder.py`
- `app/helpers/image.py`
- `app/helpers/job.py`
- `app/helpers/upload.py`
- `src/qrscan.c`
- `src/read_flag.c`
- `vendor/quirc/lib/*`

## Build result in sandbox
Docker is not installed in this sandbox, so I could not run the exact containerized Flask service here. I compiled the native scanner locally instead:

```bash
clang -O2 -DNDEBUG -Ivendor/quirc/lib -D_FORTIFY_SOURCE=3 \
  -fPIE -fstack-protector-all -fstack-clash-protection -fcf-protection=full \
  src/qrscan.c vendor/quirc/lib/quirc.c vendor/quirc/lib/decode.c \
  vendor/quirc/lib/identify.c vendor/quirc/lib/version_db.c \
  -pie -Wl,-z,relro -Wl,-z,noexecstack -Wl,-z,separate-code \
  -o /tmp/scanwich/build/qrscan -lm
```

## Confirmed behavior
The web route `/scan` accepts an uploaded image. If form field `station=kitchen` is supplied, it uses the C binary `qrscan`; otherwise it uses `pyzbar`.

The C binary accepts frames on stdin in this format:

```text
uint32_le width
uint32_le height
width * height bytes of grayscale image data
```

I verified `qrscan` decodes a generated QR payload:

```text
input payload: HELLO
qrscan stdout: HELLO
return code: 0
```

## Security notes found
- `/read_flag` is SUID root and reads `/flag`.
- The Python app does not call `/read_flag` directly.
- The hidden `station=kitchen` path can be reached by adding form field `station=kitchen`.
- The custom PNG-to-frame writer allows concatenated PNG images and sparse frame output.
- `MAX_PIXELS = 5 * 1024 * 1024 * 1024`, which is larger than signed 32-bit range.
- Vendored `quirc` uses signed `int` math in multiple places, including `q->w * q->h` in `otsu()` and `pixels_setup()`. This is suspicious for an integer-overflow path, but I did not complete a reliable RCE/flag exploit in the sandbox.

## Current status
Local compilation and decoder behavior are confirmed. Full flag extraction is not completed yet. No remote host/port was provided for this challenge.
