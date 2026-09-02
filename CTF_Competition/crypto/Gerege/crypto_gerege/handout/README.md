# Gerege — handout

    Haruul Zangi 2026 · crypto · UB-CENTRAL / Parity Registry

A gerege is the tablet of authority the Registry issues to those who move on the
Commons. Instead of handing its signature across the wire, a bearer proves in
zero knowledge that their tablet carries the Khan's authority. The proof is a
Chaum-Pedersen proof of discrete-log equality, made non-interactive with
Fiat-Shamir and bound to a live gate session.

You are issued an **envoy** tablet. No one is issued a Khan tablet, and the Khan
pairing is a hard discrete log away. Open the Khan archive anyway.

## What is attached

- `gate/gerege.py` — the seal scheme, exactly as the gate runs it. Curve,
  generators, point encoding, the Fiat-Shamir seal challenge, and verification.
  This is the ground truth; read it closely.

The gate itself is live at the challenge endpoint. It is otherwise blackbox: the
scheme above is everything it will tell you about how a seal is built.

## The gate API

    GET  /api/gerege/params
         curve, generators G and K, the published Khan pairing (T_khan, Y_khan),
         and the seal-context formula.

    GET  /api/gerege/session
         a fresh, single-use session id (hex). It expires; a stale seal is
         refused. Returns the Khan pairing too.

    GET  /api/gerege/demo?session=<hex>
         a fully worked ENVOY attestation for a tablet the gate throws away, so
         you can check your own point encoder byte-for-byte against a seal the
         gate accepts. Returns { tablet:{T,Y}, seal:{A,B,z,c} }.

    POST /api/gerege/attest
         Content-Type: application/json
         { "session":"<hex>", "tier":"khan",
           "T":"04..","Y":"04..","A":"04..","B":"04..","z":"0x.." }
         An envoy attestation is acknowledged. A Khan attestation over the
         published Khan pairing opens the archive and returns the flag.

## Flag

Dynamic `HZ{...}` flag.

## Setup for the reference solver

    python3 -m pip install ecdsa
    python3 solve.py https://gerege.<domain>
