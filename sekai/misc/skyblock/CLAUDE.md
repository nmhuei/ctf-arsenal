# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Sekai CTF 2026 Minecraft Skyblock challenge solver. Connect to `skyblock.chals.sekai.team:25565`, bypass AntiBot, register via AuthMe, progress through custom Skyblock economy (mine/fish/farm → sell → earn coins), purchase `ctf_flag` from Flag Merchant.

Server: **Paper 26.1.2** (protocol version **775**). Not vanilla — custom packet ID mappings.

## Core Architecture

All Python files follow the same raw-socket pattern:

```
socket → handshake(0x00) → login_start(0x00) → LOGIN state → login_ack(0x03) → CONFIG state → finish_config(0x03) → PLAY state
```

### Key constant pattern across all scripts:
```python
HOST, PORT, PV = "skyblock.chals.sekai.team", 25565, 775
```

### Shared helper functions (copied in every file):
```python
def wvar(v)     # encode varint
def rvar(d, o)  # decode varint, returns (value, offset)
def wstr(s)     # encode string as varint-length-prefixed UTF-8
```

### Compression:
- Server sends compression threshold (PID `0x03` in LOGIN state) — stored as `cp`
- After compression enabled: each frame is `varint(decompressed_length) + zlib(data)` inside the `varint(frame_length) + frame` wrapper
- Uncompressed packets (len < threshold): `varint(0) + data`

### States struct map:
```
C->S 0x00 (handshake): protocol_version + host + port + next_state
C->S 0x00 (login_start): username + uuid
S->C 0x02 (login_success) → C->S 0x03 (login_acknowledged) → CONFIG
S->C 0x03 (set_compression) → store cp
S->C 0x04 (plugin_request) → C->S 0x02 (plugin_response)

CONFIG:
C->S 0x00 (settings): locale + viewDist + chatFlags + colors + skinParts + mainHand + textFiltering + serverListing + particleStatus
S->C 0x03 (finish_configuration) → C->S 0x03 (ack) → PLAY

PLAY:
S->C 0x31 (login/spawn) → C->S 0x2C (player_loaded) + C->S 0x0E (settings)
S->C 0x46 (position) → C->S 0x00 (teleport_confirm)
```

## Observed Packet IDs (Not Vanilla!)

### Clientbound (S→C) PLAY — empirically observed:

| PID | Name | Notes |
|-----|------|-------|
| `0x20` | kick_disconnect | NBT reason: TAG_List("with") + TAG_String("") |
| `0x21` | profileless_chat | unsigned chat |
| `0x2B` | keep_alive | 8 bytes (i64), **DO NOT RESPOND** — causes kick! |
| `0x2C` | map_chunk / keep_alive(?) | 8-byte variant observed |
| `0x31` | login/spawn | ~135 bytes, sends world data |
| `0x3F` | player_chat | signed player chat |
| `0x46` | position | varint teleportId, must confirm |
| `0x55` | action_bar | |
| `0x77` | system_chat | named system chat |
| `0x79` | **chat messages** | NBT component — empirically delivers ALL chat including welcome/guide |
| `0x66` | update_health | |
| `0x79` | nbt_query_response | short packets < 100 bytes, very frequent |

### Serverbound (C→S) PLAY:

| PID | Name | Payload | Notes |
|-----|------|---------|-------|
| `0x00` | teleport_confirm | varint(teleportId) | required after 0x46 |
| `0x06` | **chat_command** | wstr(cmd) | **likely correct PID, rarely works** |
| `0x07` | chat_command_signed | wstr(cmd)+i64+i64+args+ack | survives but no response |
| `0x0E` | settings | ...particleStatus(0) | sent after 0x31 |
| `0x1B` | keep_alive | i64(id) | **DON'T SEND** — causes kick |
| `0x2C` | player_loaded | empty | sent after 0x31 |

**Critical**: PID `0x1B` (keep_alive response) and sending chat commands cause a disconnect kick. Passive connections survive 20-30s with zero C→S packets after init.

## AuthMe Registration

In CONFIG state, server sends:
- `0x12` (show_dialog) — Formkit NBT dialog for registration
- Response: `0x08` (custom_payload) to `authme:prejoin-register/submit`
- Payload: varint(id) + NBT compound with `{password, confirm}` strings
- Then `0x13` (code_of_conduct) → respond `0x09`

## Known Blockers

1. **chat_command (0x06) sends work briefly but cause kick** within 3-4s — Paper likely enforces signed chat even in offline mode
2. **keep_alive response causes kick** — Paper's keep_alive is informational only; responding kicks the client
3. **minecraft-protocol library** sends `client_information` instead of `settings` for 26.1.2 — missing `particleStatus` field
4. **mineflayer** does not support 26.1.2 (latest: 1.21.11)
5. **Flag not in packet data** — confirmed by 6.6MB scan; requires active gameplay (mine/fish/farm → buy ctf_flag)
6. **AntiBot** — random IP blocks, retry loop required (60s cooldown)

## Running Scripts

```bash
# Passive listener — connects, registers, captures all chat for 25s
python3 final_solve.py

# One-shot version with detailed packet stats
python3 oneshot.py

# JS bridge (minecraft-protocol, has settings bug)
node bridge.js

# Direct socket + library serializers (UUID bug)
node direct_solve.js

# Probe chat PID (brute-force 0x02-0x1a)
python3 probe3.py

# Dump all serverbound PLAY packet IDs
python3 dump_ids.py

# Proxy rotator (bypass AntiBot)
python3 proxy_bot.py
```

## Challenge Mechanics

4 merchants with gold name color:
- **Miner Merchant** — mining resources
- **Farm Merchant** — farming resources
- **Fishing Merchant** — fishing resources
- **Flag Merchant** — sells `ctf_flag` item

Item system uses `PublicBukkitValues` with keys `skyblock:item_id` and `skyblock:effect_blocks_mined`. Items have custom stats (Damage, Strength, Mining Speed, Fishing Speed, Defense, etc.).

The `ctf_flag` item properties: name="Flag" (white), lore=["legendary stuff" (gray), "Mythic material" (light_purple)].

## NBT Chat Parsing

All Python scripts use a recursive `_scan()` function for NBT:
- `0x08` = TAG_String: varint(name_length) + name + varint(value_length) + value
- `0x09` = TAG_List: type_byte + varint(length) + items
- `0x0a` = TAG_Compound: items until 0x00 (TAG_End)
- Strip `\xa7` (section sign) for color code removal

## Key Technical Constraints

1. **Compression**: Once enabled (threshold=256), all packets use zlib. Python handles it; Node.js minecraft-protocol handles it internally.
2. **Burst rate-limit**: ~3-4 packets in <1s window triggers kick. Space commands 3+ seconds apart.
3. **Packet framing**: Every send is `varint(payload_length) + payload`. With compression: `varint(compressed_frame_length) + varint(decompressed_len) + zlib(data)`.
4. **NBT chat format**: Chat responses use NBT compound wrapping, not plain JSON strings.
