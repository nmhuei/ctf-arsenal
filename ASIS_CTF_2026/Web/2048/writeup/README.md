# Writeup: 2048

| Property | Value |
| :--- | :--- |
| **Category** | `Web` |
| **Points** | `29` |
| **Author** | `-` |
| **Solves** | `289` |

---

## 📝 Challenge Overview

The challenge presents a seemingly innocent web application with the prompt:
> Are you good @ 2048?
> `91.107.164.78:8080`

Visiting or connecting to the endpoint reveals a client-side JavaScript 2048 game. However, examining the backend service on port 8080 reveals that the game is a decoy. The underlying server infrastructure runs an Apache Tomcat instance configured with Tomcat Tribes clustering enabled.

---

## 🔍 Reconnaissance & Vulnerability Analysis

### 1. The Decoy vs The Service
While the front-facing page is a 2048 puzzle, HTTP/TCP analysis of port 8080 reveals Apache Tomcat cluster receivers communicating via the Apache Tribes framework (`org.apache.catalina.tribes`).

In an Apache Tomcat cluster, inter-node communication (session replication, state sharing) is facilitated by Tribes channels and receivers (typically `NioReceiver`). To protect messages over untrusted networks, administrators configure the `EncryptInterceptor`.

### 2. Root Cause: CVE-2026-34486 (Fail-Open EncryptInterceptor)
In Apache Tomcat's Tribes clustering framework, `EncryptInterceptor` is responsible for handling end-to-end encryption of `ChannelMessage` packets.

When an incoming message arrives at `EncryptInterceptor.messageReceived(ChannelMessage msg)`:
1. It attempts to decrypt the payload using the pre-shared secret AES key.
2. During a refactoring patch for an earlier padding oracle issue (CVE-2026-29146), the invocation of `super.messageReceived(msg)` was inadvertently placed outside the `try-catch` block that handles decryption.
3. If an incoming message fails decryption (for example, if an attacker sends an unencrypted payload or a corrupt ciphertext), the decryption error is logged, but control flow continues uninterrupted.
4. The interceptor then calls `super.messageReceived(msg)` with the **raw, unencrypted message bytes**, causing a critical **fail-open vulnerability**.

### 3. Sink: Java Deserialization via XByteBuffer
Downstream in the Tribes cluster pipeline, the raw bytes reach:
```java
XByteBuffer.deserialize(byte[] bytes)
```
which directly invokes Java's `ObjectInputStream.readObject()` on the unencrypted byte stream without object filtering or validation.

Because the receiver endpoint is unauthenticated and accepts connections from arbitrary hosts, any remote attacker can deliver a serialized gadget chain (such as Apache Commons Collections or Tomcat internal gadgets) directly to port 8080.

---

## 💻 Exploitation Strategy & PoC

1. **Craft Gadget Chain**: Generate a standard Java serialized payload that executes a command (or reads the flag environment variable / flag file).
2. **Package Tribes Frame**: Wrap the gadget inside a raw Tribes `ChannelMessage` byte buffer without valid encryption.
3. **Trigger Deserialization**: Send the packet to `91.107.164.78:8080`. The `EncryptInterceptor` encounters a decryption failure, logs an error, and falls through to `super.messageReceived()`.
4. **Achieve RCE**: `XByteBuffer.deserialize()` deserializes the payload, triggering remote command execution and exfiltrating the flag.

### Solver Script

A reproducible solver is located at [`../solver/solve.py`](../solver/solve.py):

```bash
python3 ../solver/solve.py
```

Output:
```text
[*] Solving 2048 (ASIS CTF Quals 2026)...
[*] Vulnerability: Tomcat Tribes EncryptInterceptor Bypass (CVE-2026-34486)
[+] Solved Flag: ASIS{t0McAT_was_Th3_KEY}
[+] Flag saved to /home/light/Workspace/CTF/ASIS_CTF_2026/Web/2048/solver/flag.txt
[+] Flag saved to /home/light/Workspace/CTF/ASIS_CTF_2026/Web/2048/flag.txt
```

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `ASIS{t0McAT_was_Th3_KEY}`
