# Writeup: Min beste venn

| Property | Value |
| :--- | :--- |
| **Category** | `forensics` |
| **Points** | `478` |
| **Author** | `0xle` |
| **Solves** | `2` |

---

## 📝 Challenge Overview

Signal wasn't secure enough so we moved to something else. I heard about
something called chatflare, and it seemed interesting.

File: `forensics_min-beste-venn.tar.gz` → `capture.pcap` (3662 packets, 1135x `HEAD http://static.notion-static.com/cf1787417395/...css`, all `404` from Cloudflare).

Title "Min beste venn" = Norwegian "My best friend".

---

## 🔍 Reconnaissance & Vulnerability Analysis

All requests are `HEAD` for non-existent `.css` files:

- signalling: `/cf<chat_id>/h/s<timestamp>.css`, `/cf<chat_id>/c/s<timestamp>.css`
- data: `/cf<chat_id>/d/<dir>/<seq>/<byte><bit>.css` with `dir=h|c`, `seq=0,1,...`

Responses carry `cf-cache-status: MISS/HIT` (+ `Age` on HIT), `Server: cloudflare`.
This is [beescuit/chatflare](https://github.com/beescuit/chatflare): "Chat with your friends via Cloudflare cache hits".

Protocol (from `src/client.rs` / `src/util.rs`):

- `current_slot() = epoch_seconds`; polling every 1s probes counterparty signalling `c/s<slot>` or `h/s<slot>`. `HIT` = new message pending.
- `bit_paths_for_message(msg)`: prepend length byte, then for each byte `byte_to_bitmap` (`bit[i] = (byte>>(7-i))&1`), emit `{byte_idx}{bit_idx}.css` only for `1` bits.
- send: `send_message` warms all `1`-bit data paths `d/<own_dir>/<seq>/...`, then `send_signal` warms own `s<slot+offset>.css` (offset++ on collision/HIT).
- recv: `recv_message` probes 8 size paths `d/<peer_dir>/<seq>/0<bit>`, decodes size, then probes `size*8` payload paths. `HIT=1`, `MISS=0`.

Request census in pcap:

| channel | reqs | unique | HIT | MISS |
|---|---|---|---|---|
| `d/c/1` | 680 | 440 | 240 | 440 |
| `d/h/0` | 193 | 128 | 65 | 128 |
| `d/h/1` | 184 | 128 | 56 | 128 |
| `d/c/0` | 47 | 32 | 15 | 32 |
| `c/s`, `h/s` | 31 | — | — | — |

Key observation: `MISS == unique`, `HIT == total - unique`. Capture holds **both** peers (anonymized to `192.0.2.2`): sender's warming (`MISS`) + receiver's full probe (`HIT` for 1-bits, `MISS` for 0-bits). So `bit=1 ⟺ URI seen ≥2 times (has HIT)`.

---

## 💻 Exploitation Strategy & PoC

No need for cache headers — duplicates alone decode bits:

1. Regex raw pcap for `HEAD (/cf[^ ]+?)\.css` (1135 hits, 755 unique — matches tshark).
2. Group `d/<dir>/<seq>`; `1`-set = URIs with count ≥ 2.
3. For bytes `0..maxbyte`, bits = `[f"{b}{i}" in ones for i in 0..7]`, `bitmap_to_byte` = MSB-first (`byte_to_bitmap` inverse).
4. Byte 0 = length; assert `unique == 8+size*8`.

Exploit script is located at [`../solver/solve.py`](../solver/solve.py).

```bash
python3 ../solver/solve.py
```

Output:

```
[+] d/c/0: size=3 msg='ja?'
[+] d/c/1: size=54 msg='NNS{1_l0v3_ch4tt1ng_w1th_m1n_b3st3_v3nn_1n_th3_cl0ud5}'
[+] d/h/0: size=15 msg='min beste venn?'
[+] d/h/1: size=15 msg='can i haz flag?'
```

Conversation: host `min beste venn?` → client `ja?` → host `can i haz flag?` → client sends flag.

---

## 🚩 Flag

- Status: `- [x] Solved`
- Flag: `NNS{1_l0v3_ch4tt1ng_w1th_m1n_b3st3_v3nn_1n_th3_cl0ud5}`
