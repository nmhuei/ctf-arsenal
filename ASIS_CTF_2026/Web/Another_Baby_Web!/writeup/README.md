# Another Baby Web! — ASIS CTF 2026

## Bug chain

The landing page exposes the Flask source. The vulnerable resolver does:

```python
cleaned = user_path.replace("../", "")
resolved = os.path.normpath("/app" + cleaned)
```

The replacement is not recursive, so `....//` becomes `../` after the single replacement. This gives arbitrary file read outside `/app`.

The endpoint also uses `send_file(..., conditional=True)` before checking:

```python
BLOCKED = (b"ASIS", b"lib")
```

Because conditional responses honor the HTTP `Range` header first, reading one byte at a time prevents either blocked marker from ever appearing in the body seen by `bad_data()`.

`/app/flag.txt` contains only a fake flag. The protected `/entrypoint.sh` hints that the real filename is randomized.

A useful readable system artifact is:

```text
/var/lib/plocate/plocate.db
```

Downloading it through adaptive Range requests and querying it with local `plocate -d` reveals:

```text
/app/485930ceb1d4ddd6cfd1b880998ae466/flag.txt
```

Reading that file byte-by-byte through `/inspect` yields the real flag.

## Flag

```text
ASIS{Baby_w3b_cha!!3nGe_$$$}
```

## Reproduction

Run:

```bash
python solver/solve.py
```
