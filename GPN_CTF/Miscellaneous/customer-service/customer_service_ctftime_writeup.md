# GPN CTF 2024 — customer-service (Misc)

## Summary

This challenge exposed a proof-checking service built on top of **holpy**. The goal was to submit a hex-encoded JSON proof that convinced the service that we had derived `false` without assumptions.

The bug was that the service **validated that an attached proof was syntactically/semantically valid**, but **did not verify that the proof actually proved the theorem statement stored in the item**. As a result, we could submit:

- a theorem statement with proposition `false`, and
- an unrelated but valid proof, such as `|- x = x`.

That theorem was then inserted into the theory as if it were proved, and the checker awarded the flag.

---

## Files and initial analysis

The handout contained a service script that:

1. reads a hex string from stdin,
2. decodes it into JSON,
3. parses the content into holpy items,
4. checks proofs for theorem items,
5. extends the theory,
6. and finally checks whether a theorem with conclusion `false` and no assumptions exists.

The interesting logic was:

- theorem items (`ty == "thm"`) are sent through proof checking,
- then added to the theory,
- and the challenge is solved if the resulting theorem concludes `false`.

At first glance that sounds safe, but the implementation split the theorem into **two independent pieces**:

- the theorem statement: `item.prop`
- the attached proof: `item.proof`

The bug is that those two were never bound together properly.

---

## Root cause

### 1. The proof checker only validates the proof object itself

In the `proof` branch, the service constructs a proof state from `item.proof`, checks that it is a valid proof, and then returns `ProofOK`.

However, it does **not** compare the theorem obtained from the proof with `item.prop`.

So if the proof is valid, the checker accepts it, even if it proves something completely unrelated.

That means we can submit a theorem item like:

- claimed proposition: `false`
- attached proof: a valid proof of `x = x`

and it still passes proof validation.

---

### 2. The theorem extension is created from `item.prop`, not from the checked proof result

After proof checking, the service extends the theory with the theorem by calling the theorem item’s extension builder.

That extension is created using the theorem statement stored in the item itself:

```text
Thm(self.prop)
```

So the service inserts the **claimed proposition** into the theory, not the result of the attached proof.

In other words:

- proof checking says: “yes, this proof is valid”
- theory extension says: “great, I will now add the statement `false`”

This disconnect is the actual vulnerability.

---

### 3. The “one axiom only” safeguard is broken

There was also a broken safeguard around the extension report: the code compared the result of `get_axioms()` to the integer `1`, even though `get_axioms()` returns a list.

So that check can never behave as intended.

This is not the main primitive we need, but it confirms that the service’s defense layer around theorem/axiom handling is flawed.

---

## Exploit strategy

We only need to satisfy two conditions:

1. pass proof checking,
2. get a theorem with proposition `false` inserted into the theory.

So the payload is straightforward:

- create a theorem item with:
  - `prop = "false"`
- attach any valid proof in `proof`

For the valid proof, I used the primitive derivation:

- `reflexive x`

which proves:

- `|- x = x`

This is a minimal valid proof and does not depend on any assumptions.

So the final object effectively says:

- “Here is a theorem named `pwn`, whose proposition is `false`.”
- “Trust me, I also attached a valid proof.”
- The checker validates the proof, but never checks that it proves `false`.
- Then it inserts `false` as a theorem.
- The challenge condition is satisfied.

---

## Exploit payload

JSON payload:

```json
{"imports":[],"content":[{"ty":"thm","name":"pwn","vars":{"false":"bool","x":"bool"},"prop":"false","proof":[{"id":"0","rule":"reflexive","args":"x","prevs":[],"th":""}]}]}
```

Hex-encoded payload:

```text
7b22696d706f727473223a5b5d2c22636f6e74656e74223a5b7b227479223a2274686d222c226e616d65223a2270776e222c2276617273223a7b2266616c7365223a22626f6f6c222c2278223a22626f6f6c227d2c2270726f70223a2266616c7365222c2270726f6f66223a5b7b226964223a2230222c2272756c65223a227265666c6578697665222c2261726773223a2278222c227072657673223a5b5d2c227468223a22227d5d7d5d7d
```

---

## Solver

A compact solver looks like this:

```python
import json
import socket
import ssl
import sys

payload = {
    "imports": [],
    "content": [
        {
            "ty": "thm",
            "name": "pwn",
            "vars": {
                "false": "bool",
                "x": "bool"
            },
            "prop": "false",
            "proof": [
                {
                    "id": "0",
                    "rule": "reflexive",
                    "args": "x",
                    "prevs": [],
                    "th": ""
                }
            ]
        }
    ]
}

hex_payload = json.dumps(payload, separators=(",", ":")).encode().hex()

host = sys.argv[1]
port = int(sys.argv[2])

ctx = ssl.create_default_context()
with socket.create_connection((host, port)) as s:
    with ctx.wrap_socket(s, server_hostname=host) as ss:
        ss.recv(4096)
        ss.sendall(hex_payload.encode() + b"\n")
        data = b""
        while True:
            chunk = ss.recv(4096)
            if not chunk:
                break
            data += chunk

print(data.decode(errors="replace"))
```

---

## Remote proof / evidence

This is the real remote run transcript:

```text
┌──(light㉿Huei)-[~/…/CTF/GPN_CTF/Miscellaneous/customer-service]
└─$ python3 customer_service_solver.py remote pickled-tofu-under-candied-bread-0elv.gpn24.ctf.kitctf.de 443 --ssl
give me your hex proof✓ Proof check passed
Congratulations! You've found the flag: GPNCTF{Ex-Un4-l1nEa-vacu4-53qU17Ur-QUOdLibet}

[+] extracted flag: GPNCTF{Ex-Un4-l1nEa-vacu4-53qU17Ur-QUOdLibet}
```

This transcript is sufficient evidence that the flag is real:

- the exploit was sent to the official remote instance,
- the service explicitly printed `Congratulations! You've found the flag: ...`,
- and the solver extracted the same flag again from the response.

---

## Flag

```text
GPNCTF{Ex-Un4-l1nEa-vacu4-53qU17Ur-QUOdLibet}
```

---

## Takeaway

The challenge is a classic example of a **validation / use mismatch**:

- the system validates one object (the attached proof),
- but later trusts a different object (the claimed theorem statement).

As soon as those two are not cryptographically or structurally tied together, proof validation becomes meaningless.

In short: the service checked that **a** proof was valid, not that it was a proof **of the theorem being added**.

That one disconnect is enough to prove `false` and win the challenge.
