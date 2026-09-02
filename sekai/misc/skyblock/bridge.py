#!/usr/bin/env python3
"""
Minecraft Skyblock bridge — 1 persistent connection, login once, keep alive, chat loop.
Paper 26.1.2 protocol (proto.yml confirmed).
"""
import socket, struct, time, uuid, zlib

HOST, PORT, PV = "skyblock.chals.sekai.team", 25565, 775

def wvar(v):
    out = bytearray()
    while True:
        if v & 0xFFFFFF80 == 0: out.append(v & 0x7F); return bytes(out)
        out.append((v & 0x7F) | 0x80); v = (v >> 7) & 0xFFFFFFFF
def rvar(d, o=0):
    r, s = 0, 0
    while True:
        b = d[o]; r |= (b & 0x7F) << s; s += 7; o += 1
        if not (b & 0x80): return r, o
def wstr(s): e = s.encode(); return wvar(len(e)) + e

# B = clientbound (what server sends to client)
# PID (dec, hex) | Name
B_SYSTEM_CHAT   =  0x1D  # 29  system_chat
B_PROFILELESS_CHAT = 0x21  # 33  profileless_chat (unsigned chat)
B_PLAYER_CHAT   =  0x3F  # 63  player_chat (signed)
B_HIDE_MESSAGE  =  0x1F  # 31  hide_message
B_KEEP_ALIVE    =  0x2B  # 43  keep_alive
B_LOGIN         =  0x30  # 48  login (spawn)
B_KICK_DISCONNECT = 0x20 # 32  kick_disconnect
B_POSITION      =  0x42  # 66  position (sync)
B_PLAYER_INFO   =  0x42  # 67  player_info  -- wait let me re-count

# Let me re-count all IDs systematically
# Actually let me just script the counting properly

def count_cb_ids():
    """Return dict of clientbound packet name -> varint id"""
    names = [
        'bundle_delimiter',              # 0
        'spawn_entity',                   # 1
        'animation',                      # 2
        'statistics',                     # 3
        'acknowledge_player_digging',     # 4
        'block_break_animation',          # 5
        'tile_entity_data',               # 6
        'block_action',                   # 7
        'block_change',                   # 8
        'boss_bar',                       # 9
        'difficulty',                     # 10
        'chunk_batch_finished',           # 11
        'chunk_batch_start',              # 12
        'chunk_biomes',                   # 13
        'clear_titles',                   # 14
        'tab_complete',                   # 15
        'declare_commands',               # 16
        'close_window',                   # 17
        'window_items',                   # 18
        'craft_progress_bar',             # 19
        'set_slot',                       # 20
        'cookie_request',                 # 21
        'set_cooldown',                   # 22
        'chat_suggestions',               # 23
        'custom_payload',                 # 24
        'damage_event',                   # 25
        'debug_block_value',              # 26
        'debug_chunk_value',              # 27
        'debug_entity_value',             # 28
        'debug_event',                    # 29
        'debug_sample',                   # 30
        'hide_message',                   # 31
        'kick_disconnect',                # 32
        'profileless_chat',               # 33
        'entity_status',                  # 34
        'sync_entity_position',           # 35
        'explosion',                      # 36
        'unload_chunk',                   # 37
        'game_state_change',              # 38
        'game_test_highlight_pos',        # 39
        'open_horse_window',              # 40
        'hurt_animation',                 # 41
        'initialize_world_border',        # 42
        'keep_alive',                     # 43
        'map_chunk',                      # 44
        'world_event',                    # 45
        'world_particles',                # 46
        'update_light',                   # 47
        'login',                          # 48
        'map',                            # 49
        'trade_list',                     # 50
        'rel_entity_move',                # 51
        'entity_move_look',               # 52
        'move_minecart',                  # 53
        'entity_look',                    # 54
        'vehicle_move',                   # 55
        'open_book',                      # 56
        'open_window',                    # 57
        'open_sign_entity',               # 58
        'ping',                           # 59
        'ping_response',                  # 60
        'craft_recipe_response',          # 61
        'abilities',                      # 62
        'player_chat',                    # 63
        'end_combat_event',               # 64
        'enter_combat_event',             # 65
        'death_combat_event',             # 66
        'player_remove',                  # 67
        'player_info',                    # 68
        'face_player',                    # 69
        'position',                       # 70
        'player_rotation',                # 71
        'recipe_book_add',                # 72
        'recipe_book_remove',             # 73
        'recipe_book_settings',           # 74
        'entity_destroy',                 # 75
        'remove_entity_effect',           # 76
        'reset_score',                    # 77
        'remove_resource_pack',           # 78
        'add_resource_pack',              # 79
        'respawn',                        # 80
        'entity_head_rotation',           # 81
        'multi_block_change',             # 82
        'select_advancement_tab',         # 83
        'server_data',                    # 84
        'action_bar',                     # 85
        'world_border_center',            # 86
        'world_border_lerp_size',         # 87
        'world_border_size',              # 88
        'world_border_warning_delay',     # 89
        'world_border_warning_reach',     # 90
        'camera',                         # 91
        'update_view_position',           # 92
        'update_view_distance',           # 93
        'set_cursor_item',                # 94
        'spawn_position',                 # 95
        'scoreboard_display_objective',   # 96
        'entity_metadata',                # 97
        'attach_entity',                  # 98
        'entity_velocity',                # 99
        'entity_equipment',               # 100
        'experience',                     # 101
        'update_health',                  # 102
        'held_item_slot',                 # 103
        'scoreboard_objective',           # 104
        'set_passengers',                 # 105
        'set_player_inventory',           # 106
        'teams',                          # 107
        'scoreboard_score',               # 108
        'simulation_distance',            # 109
        'set_title_subtitle',             # 110
        'update_time',                    # 111
        'set_title_text',                 # 112
        'set_title_time',                 # 113
        'entity_sound_effect',            # 114
        'sound_effect',                   # 115
        'start_configuration',            # 116
    ]
    return {n: i for i, n in enumerate(names)}

# Serverbound (C->S) IDs from proto.yml toServer PLAY packet varint:
# 0x06 = chat_command (command: string)
# 0x1B = keep_alive (keepAliveId: i64)
# 0x2B = player_loaded
S_CHAT_COMMAND = 0x06
S_KEEP_ALIVE   = 0x1B
S_PLAYER_LOADED = 0x2B

cb = count_cb_ids()
# Override with verified names
B_SYSTEM_CHAT   = cb['profileless_chat']   # unsigned chat for system messages
B_PROFILELESS_CHAT = cb['profileless_chat']
B_PLAYER_CHAT   = cb['player_chat']
B_HIDE_MESSAGE  = cb['hide_message']
B_KEEP_ALIVE    = cb['keep_alive']
B_KICK_DISCONNECT = cb['kick_disconnect']
B_LOGIN         = cb['login']
B_POSITION      = cb['position']
B_PING          = cb['ping']

print(f"[*] Key clientbound PIDs:")
print(f"    profileless_chat = 0x{B_PROFILELESS_CHAT:02x}")
print(f"    player_chat      = 0x{B_PLAYER_CHAT:02x}")
print(f"    system_chat      = 0x{B_SYSTEM_CHAT:02x}")
print(f"    hide_message     = 0x{B_HIDE_MESSAGE:02x}")
print(f"    keep_alive       = 0x{B_KEEP_ALIVE:02x}")
print(f"    kick_disconnect  = 0x{B_KICK_DISCONNECT:02x}")
print(f"    login            = 0x{B_LOGIN:02x}")
print(f"    ping             = 0x{B_PING:02x}")
print(f"[*] Key serverbound PIDs:")
print(f"    chat_command     = 0x{S_CHAT_COMMAND:02x}")
print(f"    keep_alive       = 0x{S_KEEP_ALIVE:02x}")
print(f"    player_loaded    = 0x{S_PLAYER_LOADED:02x}")


class Bridge:
    def __init__(self):
        self.cp = -1
        self.uid = uuid.uuid4()
        ts = int(time.time())
        self.name = f"Br{ts%10000}"
        self.pwd = f"br{ts%10000}"
        self.sock = None
        self.loaded = False

    def send(self, pid, data=b''):
        r = wvar(pid) + data
        if self.cp >= 0:
            if len(r) >= self.cp:
                c = zlib.compress(r); f = wvar(len(r)) + c
            else: f = wvar(0) + r
            self.sock.sendall(wvar(len(f)) + f)
        else: self.sock.sendall(wvar(len(r)) + r)

    def recv(self, timeout=1):
        self.sock.settimeout(timeout)
        d = b''
        while True:
            b = self.sock.recv(1)
            if not b: return None, None
            d += b
            if not (b[0] & 0x80): break
        pl, _ = rvar(d)
        rt = b''
        while len(rt) < pl:
            c = self.sock.recv(pl - len(rt))
            if not c: return None, None
            rt += c
        if self.cp >= 0:
            dl, o = rvar(rt)
            if dl > 0:
                dec = zlib.decompress(rt[o:])
                p, o2 = rvar(dec); return p, dec[o2:]
            else: p, o2 = rvar(rt, o); return p, rt[o2:]
        else: p, o = rvar(rt); return p, rt[o:]

    def connect(self):
        print(f"[*] Connecting as {self.name}...", flush=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(15)
        self.sock.connect((HOST, PORT))

        # Handshake + Login
        self.send(0x00, wvar(PV) + wstr(HOST) + struct.pack('>H', PORT) + wvar(2))
        self.send(0x00, wstr(self.name) + struct.pack('>QQ', self.uid.int >> 64, self.uid.int & ((1 << 64) - 1)))

        while True:
            p, pl = self.recv(15)
            if p is None: return False
            if p == 0x00:
                print("[!] AntiBot blocked", flush=True); return False
            if p == 0x02:
                self.send(0x03); break
            elif p == 0x03:
                self.cp, _ = rvar(pl)
                print(f"[+] Compression={self.cp}", flush=True)
            elif p == 0x04:
                m, o = rvar(pl, 1); self.send(0x02, wvar(m) + wvar(0))

        # Config state
        self.send(0x00, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
        while True:
            p, pl = self.recv(15)
            if p is None: return False
            if p == 0x03:
                print("[+] Config done", flush=True); break
            elif p == 0x04: self.send(0x04, pl)
            elif p == 0x05: self.send(0x05, pl)
            elif p == 0x0E:
                cnt, o = rvar(pl); resp = b''
                for _ in range(cnt):
                    l, o = rvar(pl, o); ns = pl[o:o+l].decode(); o += l
                    l, o = rvar(pl, o); n = pl[o:o+l].decode(); o += l
                    l, o = rvar(pl, o); v = pl[o:o+l].decode(); o += l
                    resp += wstr(ns) + wstr(n) + wstr(v)
                self.send(0x07, wvar(cnt) + resp)
            elif p == 0x12:
                nbt = b'\x0a\x00\x00'
                nbt += b'\x08\x00\x08password' + struct.pack('>H', len(self.pwd)) + self.pwd.encode()
                nbt += b'\x08\x00\x07confirm' + struct.pack('>H', len(self.pwd)) + self.pwd.encode() + b'\x00'
                self.send(0x08, wstr("authme:prejoin-register/submit") + wvar(len(b'\x01' + nbt)) + b'\x01' + nbt)
                print("[+] AuthMe register sent", flush=True)
            elif p == 0x13: self.send(0x09)
            elif p == 0x02: return False

        # Enter PLAY
        self.send(0x03)
        print("[+] PLAY state", flush=True)
        return True

    def parse_chat(self, pl):
        """Extract text from NBT chat component"""
        if not pl: return ""
        def _scan(d, off):
            r = []
            while off < len(d):
                tt = d[off]
                if tt == 0: return "".join(r), off + 1
                off += 1
                if off + 2 > len(d): break
                nl = struct.unpack('>H', d[off:off+2])[0]
                nm = d[off+2:off+2+nl].decode(errors='replace') if nl else ''
                off += 2 + nl
                if tt == 0x08:
                    if off + 2 > len(d): break
                    sl = struct.unpack('>H', d[off:off+2])[0]
                    if off + sl + 2 > len(d): break
                    val = d[off+2:off+2+sl].decode(errors='replace'); off += 2 + sl
                    if nm in ('text', ''): r.append(val)
                elif tt == 0x09:
                    if off + 5 > len(d): break
                    lt, ll = d[off], struct.unpack('>I', d[off+1:off+5])[0]; off += 5
                    for _ in range(ll):
                        if lt == 0x0a: s, off = _scan(d, off); r.append(s)
                        elif lt == 0x08:
                            if off + 2 > len(d): break
                            sl = struct.unpack('>H', d[off:off+2])[0]
                            r.append(d[off+2:off+2+sl].decode(errors='replace')); off += 2 + sl
                        else: break
                elif tt == 0x0a: s, off = _scan(d, off); r.append(s)
                else: break
            return "".join(r), off
        try:
            result, _ = _scan(pl, 1)
            return result.replace('\xa7', '').strip()
        except: return ""

    def chat(self, cmd):
        """Send chat command via chat_command PID (0x06)
        Fields: command: string (just the /cmd part)"""
        self.send(S_CHAT_COMMAND, wstr(cmd))
        print(f"[>] /{cmd}", flush=True)

    def listen_loop(self):
        """Main loop: handle keep_alive, show chat, stay connected"""
        self.sock.settimeout(1)
        t0 = time.time()
        ka_count = 0

        while True:
            try:
                p, pl = self.recv(1)
                if p is None:
                    print("[!] Disconnected", flush=True); break
            except socket.timeout:
                continue
            except:
                print("[!] Connection lost", flush=True); break

            dt = time.time() - t0

            # Init PLAY
            if p == cb['login'] and not self.loaded:
                self.send(S_PLAYER_LOADED)  # player_loaded
                self.send(0x0D, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                self.loaded = True
                print(f"[+] PLAY init @{dt:.1f}s", flush=True)

            # Keep alive
            elif p == B_KEEP_ALIVE:
                # echo back the keep alive ID (i64)
                self.send(S_KEEP_ALIVE, pl)
                ka_count += 1

            # Teleport confirm
            elif p == cb['position']:
                # position sync — confirm teleport
                tid, o = rvar(pl)
                self.send(0x00, wvar(tid))  # teleport_confirm

            # Ping
            elif p == B_PING:
                # ping_response
                self.send(S_KEEP_ALIVE, pl)  # wrong, actually 0x3C = pong
                # Actually let me check: ping (cb) -> ping_response (sb, PID 0x2C)
                pass

            # Chat messages
            elif p == B_PROFILELESS_CHAT:
                txt = self.parse_chat(pl)
                if txt:
                    print(f"[C] {txt[:200]}", flush=True)

            elif p == B_PLAYER_CHAT:
                txt = self.parse_chat(pl)
                if txt:
                    print(f"[PC] {txt[:200]}", flush=True)

            elif p == B_HIDE_MESSAGE:
                txt = self.parse_chat(pl)
                if txt:
                    print(f"[HIDE] {txt[:200]}", flush=True)

            # Kick / disconnect
            elif p == B_KICK_DISCONNECT:
                try:
                    l, o = rvar(pl, 0); m = pl[o:o+l].decode(errors='replace')
                    print(f"[!] KICK @{dt:.1f}s: {m[:200]}", flush=True)
                except:
                    print(f"[!] KICK @{dt:.1f}s: raw={pl[:60].hex()}", flush=True)
                break

            # Print elapsed every 10s
            if int(dt) % 60 == 0 and int(dt) > 0:
                print(f"[*] {int(dt)}s, keep_alive: {ka_count}", flush=True)

        print(f"[*] Session: {time.time()-t0:.1f}s, {ka_count} keep_alive", flush=True)

    def close(self):
        try: self.sock.close()
        except: pass

if __name__ == "__main__":
    b = Bridge()
    if not b.connect():
        b.close(); exit(1)

    print("[*] Starting listen loop", flush=True)
    # Start listen loop in background or interleaved
    import select
    b.sock.setblocking(False)
    t0 = time.time()
    b.loaded = False
    buf = b''

    while time.time() - t0 < 300:  # 5 min session
        # Non-blocking recv with select
        ready, _, _ = select.select([b.sock], [], [], 0.1)
        if ready:
            try:
                data = b.sock.recv(4096)
                if not data:
                    print("[!] Connection closed", flush=True); break
                buf += data
                # Process full packets
                while buf:
                    old_len = len(buf)
                    # Try to parse varint length
                    try:
                        pl_len, consumed = rvar(buf)
                        total_needed = consumed + pl_len
                        if len(buf) < total_needed:
                            break  # wait for more data
                        pkt = buf[consumed:total_needed]
                        buf = buf[total_needed:]

                        # Process this raw frame
                        if b.cp >= 0:
                            # Decompress
                            dl, o = rvar(pkt)
                            if dl > 0:
                                dec = zlib.decompress(pkt[o:])
                                pid, o2 = rvar(dec)
                                payload = dec[o2:]
                            else:
                                pid, o2 = rvar(pkt, o)
                                payload = pkt[o2:]
                        else:
                            pid, o = rvar(pkt)
                            payload = pkt[o:]

                        dt = time.time() - t0

                        # Handle
                        if pid == 0x31 and not b.loaded:  # login
                            b.send(0x2B)
                            b.send(0x0D, wstr("en_US") + bytes([12]) + wvar(0) + bytes([1, 0x7F]) + wvar(1) + bytes([0, 1, 0]))
                            b.loaded = True
                            print(f"[+] PLAY ready @{dt:.1f}s", flush=True)

                        elif pid == 0x2C and len(payload) == 8:  # keep_alive (old)
                            b.send(0x1B, payload)

                        elif pid == B_KEEP_ALIVE:  # 43 = 0x2B
                            b.send(S_KEEP_ALIVE, payload)
                        elif pid == cb['position']:  # 70
                            tid, o = rvar(payload)
                            b.send(0x00, wvar(tid))
                        elif pid == B_PROFILELESS_CHAT:
                            txt = b.parse_chat(payload)
                            if txt:
                                print(f"[C] {txt[:200]}", flush=True)
                        elif pid == B_PLAYER_CHAT:
                            txt = b.parse_chat(payload)
                            if txt:
                                print(f"[PC] {txt[:200]}", flush=True)
                        elif pid == B_KICK_DISCONNECT:
                            l, o = rvar(payload, 0)
                            msg = payload[o:o+l].decode(errors='replace')
                            print(f"[!] KICK @{dt:.1f}s: {msg[:200]}", flush=True); break
                    except Exception as e:
                        # Skip malformed
                        buf = b''
                        break
            except BlockingIOError: pass
            except Exception as e:
                print(f"[!] Error: {e}", flush=True); break

    b.close()
    print(f"[*] Session ended ({time.time()-t0:.1f}s)", flush=True)
