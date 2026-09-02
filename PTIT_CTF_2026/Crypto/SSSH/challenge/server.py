#!/usr/bin/env python3
import base64
import binascii
import hashlib
import json
import os
import secrets
import shlex
import shutil
import socket
import socketserver
import tempfile
import threading
import time
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from urllib.parse import unquote, urlparse


PORT = int(os.environ.get("PORT", "6205"))
HTTP_PEEK_TIMEOUT = float(os.environ.get("HTTP_PEEK_TIMEOUT", "0.15"))
SESSION_DIR = os.environ.get("SESSION_DIR", "")
CLEANUP_GRACE_SECONDS = int(os.environ.get("CLEANUP_GRACE_SECONDS", "600"))
TCP_IDLE_TIMEOUT = int(os.environ.get("TCP_IDLE_TIMEOUT", "900"))
PASSWORD_FILE = os.environ.get("PASSWORD_FILE", "/app/passwords.txt")

DH_P = (1 << 521) - 1
DH_G = 5
MAX_LINE = 65536
CRYPT_B64 = "./0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class ProtocolError(Exception):
    pass


class DerReader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def _read(self, size):
        if self.pos + size > len(self.data):
            raise ValueError("truncated DER")
        out = self.data[self.pos:self.pos + size]
        self.pos += size
        return out

    def _read_length(self):
        first = self._read(1)[0]
        if first < 0x80:
            return first
        count = first & 0x7F
        if count == 0 or count > 4:
            raise ValueError("unsupported DER length")
        return int.from_bytes(self._read(count), "big")

    def read_tlv(self, tag):
        got = self._read(1)[0]
        if got != tag:
            raise ValueError("unexpected DER tag")
        length = self._read_length()
        return self._read(length)

    def read_sequence(self):
        return DerReader(self.read_tlv(0x30))

    def read_integer(self):
        raw = self.read_tlv(0x02)
        if not raw:
            raise ValueError("empty integer")
        return int.from_bytes(raw, "big")

    def read_bit_string(self):
        raw = self.read_tlv(0x03)
        if not raw or raw[0] != 0:
            raise ValueError("unsupported bit string")
        return raw[1:]


def is_probable_prime(value):
    if value < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for prime in small_primes:
        if value % prime == 0:
            return value == prime

    d = value - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for base in small_primes:
        if base >= value - 2:
            continue
        x = pow(base, d, value)
        if x == 1 or x == value - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, value)
            if x == value - 1:
                break
        else:
            return False
    return True


def generate_prime(bits, e):
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1
        if (candidate - 1) % e == 0:
            continue
        if is_probable_prime(candidate):
            return candidate


def der_len(size):
    if size < 128:
        return bytes([size])
    data = size.to_bytes((size.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(data)]) + data


def der_int(value):
    data = value.to_bytes((value.bit_length() + 7) // 8, "big") or b"\x00"
    if data[0] & 0x80:
        data = b"\x00" + data
    return b"\x02" + der_len(len(data)) + data


def der_seq(*items):
    body = b"".join(items)
    return b"\x30" + der_len(len(body)) + body


def der_oid(value):
    parts = [int(part) for part in value.split(".")]
    out = bytes([40 * parts[0] + parts[1]])
    for part in parts[2:]:
        stack = [part & 0x7F]
        part >>= 7
        while part:
            stack.append(0x80 | (part & 0x7F))
            part >>= 7
        out += bytes(reversed(stack))
    return b"\x06" + der_len(len(out)) + out


def public_key_pem(n, e):
    rsa_pub = der_seq(der_int(n), der_int(e))
    algorithm = der_seq(der_oid("1.2.840.113549.1.1.1"), b"\x05\x00")
    bit_string = b"\x03" + der_len(len(rsa_pub) + 1) + b"\x00" + rsa_pub
    spki = der_seq(algorithm, bit_string)
    body = base64.b64encode(spki).decode()
    wrapped = "\n".join(body[index:index + 64] for index in range(0, len(body), 64))
    return f"-----BEGIN PUBLIC KEY-----\n{wrapped}\n-----END PUBLIC KEY-----\n"


def generate_session_public_key():
    e = 3
    p = generate_prime(512, e)
    q = generate_prime(512, e)
    while q == p:
        q = generate_prime(512, e)
    n = p * q
    return n, e, public_key_pem(n, e)


def challenge_text_from_pem(pem, token):
    encoded = base64.b64encode(pem.encode("ascii")).decode()
    chunks = [encoded[index:index + 52] for index in range(0, len(encoded), 52)]
    lines = [
        "SSSH session host material",
        "==========================",
        "",
        f"Session: {token}",
        "",
        "Join the chunk payloads in order, base64-decode the result, and store",
        "the decoded data as the server public key used by this SSSH session.",
        "",
    ]
    lines.extend(f"{index:02d}: {chunk}" for index, chunk in enumerate(chunks, start=1))
    lines.append("")
    return "\n".join(lines)


def load_rsa_public_key(path):
    with open(path, "r", encoding="ascii") as handle:
        body = "".join(
            line.strip()
            for line in handle
            if not line.startswith("-----")
        )
    der = base64.b64decode(body)
    top = DerReader(der).read_sequence()
    top.read_sequence()
    public_bits = top.read_bit_string()
    rsa = DerReader(public_bits).read_sequence()
    return rsa.read_integer(), rsa.read_integer()


class SignatureVerifier:
    def __init__(self, n, e):
        self.n = n
        self.e = e

    def verify(self, message, signature_hex):
        try:
            signature = int(signature_hex, 16)
        except (TypeError, ValueError):
            return False
        if signature <= 0 or signature >= self.n:
            return False

        recovered = pow(signature, self.e, self.n)
        expected = hashlib.sha256(message).digest()
        return (recovered & 0xFFFF) == int.from_bytes(expected[-2:], "big")


class KeyExchange:
    def __init__(self):
        self.private = secrets.randbelow(DH_P - 3) + 2
        self.server_nonce = secrets.token_bytes(16)
        self.server_public = pow(DH_G, self.private, DH_P)

    def banner(self):
        return {
            "type": "banner",
            "proto": "SSSH-2.0",
            "kex": "diffie-hellman-group-sssh-sha256",
            "auth": "rsa-cache-v1",
            "p": format(DH_P, "x"),
            "g": format(DH_G, "x"),
        }

    def accept(self, packet):
        if packet.get("type") != "kex_init":
            raise ProtocolError("expected kex_init")
        try:
            client_public = int(packet["client_pub"], 16)
            client_nonce = base64.b64decode(packet["client_nonce"], validate=True)
        except (KeyError, TypeError, ValueError, binascii.Error) as exc:
            raise ProtocolError("bad kex_init") from exc
        if not (0 < client_public < DH_P):
            raise ProtocolError("bad client public value")

        shared = pow(client_public, self.private, DH_P)
        shared_bytes = int_to_bytes(shared)
        session_id = hashlib.sha256(
            b"SSSH session|" + shared_bytes + client_nonce + self.server_nonce
        ).hexdigest()
        reply = {
            "type": "kex_reply",
            "server_pub": format(self.server_public, "x"),
            "server_nonce": base64.b64encode(self.server_nonce).decode(),
        }
        return reply, session_id


def int_to_bytes(value):
    size = max(1, (value.bit_length() + 7) // 8)
    return value.to_bytes(size, "big")


def xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


def to64(value, length):
    result = []
    for _ in range(length):
        result.append(CRYPT_B64[value & 0x3F])
        value >>= 6
    return "".join(result)


def md5crypt(password, setting):
    if isinstance(password, str):
        password = password.encode()
    if setting.startswith("$1$"):
        salt = setting.split("$")[2]
    else:
        salt = setting
    salt = salt[:8]
    salt_bytes = salt.encode()

    ctx = hashlib.md5(password + b"$1$" + salt_bytes)
    alt = hashlib.md5(password + salt_bytes + password).digest()

    remaining = len(password)
    while remaining > 0:
        ctx.update(alt[:min(16, remaining)])
        remaining -= 16

    i = len(password)
    while i > 0:
        if i & 1:
            ctx.update(b"\x00")
        else:
            ctx.update(password[:1])
        i >>= 1

    final = ctx.digest()
    for i in range(1000):
        ctx = hashlib.md5()
        if i & 1:
            ctx.update(password)
        else:
            ctx.update(final)
        if i % 3:
            ctx.update(salt_bytes)
        if i % 7:
            ctx.update(password)
        if i & 1:
            ctx.update(final)
        else:
            ctx.update(password)
        final = ctx.digest()

    encoded = (
        to64((final[0] << 16) | (final[6] << 8) | final[12], 4) +
        to64((final[1] << 16) | (final[7] << 8) | final[13], 4) +
        to64((final[2] << 16) | (final[8] << 8) | final[14], 4) +
        to64((final[3] << 16) | (final[9] << 8) | final[15], 4) +
        to64((final[4] << 16) | (final[10] << 8) | final[5], 4) +
        to64(final[11], 2)
    )
    return f"$1${salt}${encoded}"


class AccountDB:
    def __init__(self, password_path):
        self.passwords = self._load_passwords(password_path)
        self.failures = 0
        self.rotate_root_password()

    def _load_passwords(self, path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                passwords = [line.strip() for line in handle if line.strip() and not line.startswith("#")]
        except OSError:
            passwords = []
        if not passwords:
            passwords = ["password", "dragon", "football", "letmein", "sunshine"]
        return passwords

    def _salt(self):
        return "".join(secrets.choice(CRYPT_B64) for _ in range(8))

    def rotate_root_password(self):
        self.root_password = secrets.choice(self.passwords)
        self.root_hash = md5crypt(self.root_password, self._salt())
        self.failures = 0

    def passwd(self):
        return "\n".join([
            "root:x:0:0:root:/root:/bin/sh",
            "ctf:x:1000:1000:ctf:/home/ctf:/bin/sh",
            "",
        ])

    def shadow(self):
        return "\n".join([
            f"root:{self.root_hash}:19842:0:99999:7:::",
            "ctf:*:19842:0:99999:7:::",
            "",
        ])

    def check_root_password(self, password):
        return secrets.compare_digest(md5crypt(password, self.root_hash), self.root_hash)


class Shell:
    def __init__(self, accounts):
        self.accounts = accounts
        self.user = "ctf"
        self.cwd = "/"
        self.awaiting_sudo = False
        self.dirs = {
            "/": ["etc", "home", "root", "usr"],
            "/etc": ["passwd", "shadow"],
            "/home": ["ctf"],
            "/home/ctf": [],
            "/root": [],
            "/usr": ["local"],
            "/usr/local": ["sbin"],
            "/usr/local/sbin": [],
        }
        self.dir_perms = {"/root": "root", "/usr/local/sbin": "root"}
        self.files = {
            "/etc/passwd": ("all", self.accounts.passwd),
            "/etc/shadow": ("all", self.accounts.shadow),
        }

    def prompt(self):
        return f"{self.user}@sssh:{self.cwd}$ "

    def _normalize(self, path):
        if not path:
            return self.cwd
        if path.startswith("/"):
            raw = path
        else:
            raw = self.cwd.rstrip("/") + "/" + path
        parts = []
        for part in raw.split("/"):
            if part in ("", "."):
                continue
            if part == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(part)
        return "/" + "/".join(parts)

    def _can_access_dir(self, path):
        return self.dir_perms.get(path, "all") == "all" or self.user == "root"

    def _can_read_file(self, path):
        if path not in self.files:
            return False
        return self.files[path][0] == "all" or self.user == "root"

    def execute(self, line):
        line = line.strip()
        if self.awaiting_sudo:
            return self._handle_sudo_password(line)
        if not line:
            return "", self.prompt()
        try:
            parts = shlex.split(line)
        except ValueError as exc:
            return f"parse error: {exc}\n", self.prompt()
        if not parts:
            return "", self.prompt()

        command = parts[0]
        if command == "help":
            return "help pwd ls cd cat id whoami sudo su\n", self.prompt()
        if command == "pwd":
            return self.cwd + "\n", self.prompt()
        if command == "ls":
            return self._cmd_ls(parts[1:]), self.prompt()
        if command == "cd":
            return self._cmd_cd(parts[1:]), self.prompt()
        if command == "cat":
            return self._cmd_cat(parts[1:]), self.prompt()
        if command == "id":
            if self.user == "root":
                return "uid=0(root) gid=0(root) groups=0(root)\n", self.prompt()
            return "uid=1000(ctf) gid=1000(ctf) groups=1000(ctf)\n", self.prompt()
        if command == "whoami":
            return self.user + "\n", self.prompt()
        if command == "sudo" and parts[1:] == ["su"]:
            self.awaiting_sudo = True
            return "Password:", ""
        return "Command not found\n", self.prompt()

    def _cmd_ls(self, args):
        path = self._normalize(args[0] if args else self.cwd)
        if path in self.files:
            if not self._can_read_file(path):
                return f"ls: cannot access '{path}': Permission denied\n"
            return path.rsplit("/", 1)[-1] + "\n"
        if path not in self.dirs:
            return f"ls: cannot access '{path}': No such file or directory\n"
        if not self._can_access_dir(path):
            return f"ls: cannot open directory '{path}': Permission denied\n"
        return "\n".join(self.dirs[path]) + ("\n" if self.dirs[path] else "")

    def _cmd_cd(self, args):
        target = args[0] if args else ("/root" if self.user == "root" else "/home/ctf")
        path = self._normalize(target)
        if path not in self.dirs:
            return f"cd: {target}: No such file or directory\n"
        if not self._can_access_dir(path):
            return f"cd: {target}: Permission denied\n"
        self.cwd = path
        return ""

    def _cmd_cat(self, args):
        if not args:
            return "cat: missing operand\n"
        output = []
        for item in args:
            path = self._normalize(item)
            if path not in self.files:
                output.append(f"cat: {item}: No such file or directory\n")
                continue
            if not self._can_read_file(path):
                output.append(f"cat: {item}: Permission denied\n")
                continue
            output.append(self.files[path][1]())
        return "".join(output)

    def _handle_sudo_password(self, password):
        self.awaiting_sudo = False
        if self.accounts.check_root_password(password):
            self.user = "root"
            self.cwd = "/root"
            self.accounts.failures = 0
            return "root session opened\n", self.prompt()
        self.accounts.failures += 1
        if self.accounts.failures >= 3:
            self.accounts.rotate_root_password()
            return "sudo: 3 incorrect password attempts\nroot password rotated\n", self.prompt()
        return "Sorry, try again.\n", self.prompt()


class Session:
    def __init__(self, request, verifier, accounts):
        self.request = request
        self.verifier = verifier
        self.accounts = accounts
        self.rfile = request.makefile("rb")
        self.wfile = request.makefile("wb")
        self.session_id = None

    def read_line(self):
        line = self.rfile.readline(MAX_LINE + 1)
        if not line:
            raise EOFError
        if len(line) > MAX_LINE:
            raise ProtocolError("line too long")
        return line.decode("utf-8", errors="replace").rstrip("\r\n")

    def read_json(self):
        try:
            packet = json.loads(self.read_line())
        except json.JSONDecodeError as exc:
            raise ProtocolError("bad json") from exc
        if not isinstance(packet, dict):
            raise ProtocolError("json must be an object")
        return packet

    def send_text(self, text):
        self.wfile.write(text.encode("utf-8"))
        self.wfile.flush()

    def send_json(self, packet):
        self.send_text(json.dumps(packet, sort_keys=True, separators=(",", ":")) + "\n")

    def send_menu(self):
        self.send_text(
            "\n"
            "[1] Show server banner\n"
            "[2] Submit kex_init JSON\n"
            "[3] Submit auth JSON\n"
            "[4] Open shell\n"
            "[0] Exit\n"
            "choice>\n"
        )

    def run_shell(self):
        shell = Shell(self.accounts)
        self.send_text("opening plaintext shell\n")
        self.send_text(shell.prompt() + "\n")
        while True:
            line = self.read_line()
            output, prompt = shell.execute(line)
            if output:
                self.send_text(output)
                if not output.endswith("\n"):
                    self.send_text("\n")
            if prompt:
                self.send_text(prompt + "\n")

    def run(self):
        kex = KeyExchange()
        kex_done = False
        auth_done = False
        while True:
            self.send_menu()
            choice = self.read_line().strip()
            if choice == "0":
                self.send_text("bye\n")
                return
            if choice == "1":
                self.send_json(kex.banner())
                continue
            if choice == "2":
                self.send_text("kex_init json>\n")
                try:
                    reply, self.session_id = kex.accept(self.read_json())
                except ProtocolError as exc:
                    self.send_text(f"kex failed: {exc}\n")
                    continue
                kex_done = True
                self.send_text("kex accepted\n")
                self.send_json(reply)
                continue
            if choice == "3":
                if not kex_done:
                    self.send_text("run kex first\n")
                    continue
                self.send_text("auth json>\n")
                try:
                    auth = self.read_json()
                except ProtocolError as exc:
                    self.send_text(f"auth failed: {exc}\n")
                    continue
                if auth.get("action") != "auth":
                    self.send_text("auth failed: expected action=auth\n")
                    continue
                user = str(auth.get("user", ""))
                message = f"SSSH-AUTH|{self.session_id}|user={user}".encode()
                if user != "ctf" or not self.verifier.verify(message, str(auth.get("signature", ""))):
                    self.send_text("authentication failed\n")
                    continue
                auth_done = True
                self.send_text("auth accepted\n")
                continue
            if choice == "4":
                if not auth_done:
                    self.send_text("authenticate first\n")
                    continue
                self.run_shell()
                return
            self.send_text("invalid option\n")


@dataclass
class SessionInfo:
    path: Path
    created_at: float


class SessionRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._sessions = {}

    def add(self, token, path):
        with self._lock:
            self._sessions[token] = SessionInfo(path=path, created_at=time.time())

    def get(self, token):
        with self._lock:
            return self._sessions.get(token)

    def pop(self, token):
        with self._lock:
            return self._sessions.pop(token, None)


REGISTRY = SessionRegistry()
SESSION_ROOT = None


def can_write(directory):
    try:
        directory.mkdir(parents=True, exist_ok=True)
        probe = directory / f".write_test_{secrets.token_hex(6)}"
        probe.write_text("ok", encoding="ascii")
        probe.unlink()
        return True
    except OSError:
        return False


def choose_session_root():
    candidates = []
    if SESSION_DIR:
        candidates.append(Path(SESSION_DIR))
    candidates.extend([
        Path(tempfile.gettempdir()) / "sssh_sessions",
        Path("/app/sessions"),
    ])
    seen = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if can_write(resolved):
            return resolved
    raise RuntimeError("no writable session directory found")


def cleanup_session(token):
    info = REGISTRY.pop(token)
    if info is None:
        return
    shutil.rmtree(info.path, ignore_errors=True)
    print(f"[cleanup] removed session {token}: {info.path}", flush=True)


def schedule_cleanup(token):
    if CLEANUP_GRACE_SECONDS <= 0:
        cleanup_session(token)
        return
    timer = threading.Timer(CLEANUP_GRACE_SECONDS, cleanup_session, args=(token,))
    timer.daemon = True
    timer.start()


def challenge_url_template(token):
    return f"http://<same-host>:<same-port>/download/{token}/challenge.txt"


def connection_starts_with_http(conn):
    old_timeout = conn.gettimeout()
    conn.settimeout(HTTP_PEEK_TIMEOUT)
    try:
        data = conn.recv(8, socket.MSG_PEEK)
    except socket.timeout:
        return False
    finally:
        conn.settimeout(old_timeout)
    return data.startswith((b"GET ", b"HEAD "))


def read_http_headers(rfile):
    for _ in range(64):
        line = rfile.readline(MAX_LINE + 1)
        if not line or line in {b"\r\n", b"\n"}:
            return True
        if len(line) > MAX_LINE:
            return False
    return False


def send_http_response(conn, status, body=b"", content_type="text/plain; charset=utf-8", method="GET"):
    if isinstance(status, HTTPStatus):
        code = status.value
        reason = status.phrase
    else:
        code = int(status)
        reason = "OK"
    headers = [
        f"HTTP/1.1 {code} {reason}\r\n",
        "Server: SSSHHTTP/1.0\r\n",
        "Connection: close\r\n",
        f"Content-Type: {content_type}\r\n",
        f"Content-Length: {len(body)}\r\n",
    ]
    if status == HTTPStatus.OK:
        headers.append('Content-Disposition: attachment; filename="challenge.txt"\r\n')
    headers.append("\r\n")
    conn.sendall("".join(headers).encode("ascii"))
    if method != "HEAD":
        conn.sendall(body)


def handle_download_request(conn):
    rfile = conn.makefile("rb")
    request_line = rfile.readline(MAX_LINE + 1)
    if not request_line:
        return
    try:
        parts = request_line.decode("iso-8859-1").strip().split()
    except UnicodeDecodeError:
        send_http_response(conn, HTTPStatus.BAD_REQUEST, b"Bad Request\n")
        return
    if len(parts) < 3:
        read_http_headers(rfile)
        send_http_response(conn, HTTPStatus.BAD_REQUEST, b"Bad Request\n")
        return

    method, raw_path, _version = parts[0].upper(), parts[1], parts[2]
    headers_ok = read_http_headers(rfile)
    if method not in {"GET", "HEAD"}:
        send_http_response(conn, HTTPStatus.METHOD_NOT_ALLOWED, b"Method Not Allowed\n", method=method)
        return
    if not headers_ok:
        send_http_response(conn, HTTPStatus.BAD_REQUEST, b"Bad Request\n", method=method)
        return

    path_parts = [unquote(part) for part in urlparse(raw_path).path.strip("/").split("/")]
    if len(path_parts) != 3 or path_parts[0] != "download":
        send_http_response(conn, HTTPStatus.NOT_FOUND, b"Not Found\n", method=method)
        return
    _, token, filename = path_parts
    if filename != "challenge.txt":
        send_http_response(conn, HTTPStatus.NOT_FOUND, b"Not Found\n", method=method)
        return

    info = REGISTRY.get(token)
    if info is None:
        send_http_response(conn, HTTPStatus.NOT_FOUND, b"Not Found\n", method=method)
        return
    target = info.path / "challenge.txt"
    try:
        resolved = target.resolve()
        resolved.relative_to(info.path.resolve())
    except ValueError:
        send_http_response(conn, HTTPStatus.FORBIDDEN, b"Forbidden\n", method=method)
        return
    if not resolved.is_file():
        send_http_response(conn, HTTPStatus.NOT_FOUND, b"Not Found\n", method=method)
        return

    send_http_response(conn, HTTPStatus.OK, resolved.read_bytes(), method=method)


class Handler(socketserver.BaseRequestHandler):
    accounts = None

    def handle(self):
        assert SESSION_ROOT is not None
        self.request.settimeout(TCP_IDLE_TIMEOUT)
        if connection_starts_with_http(self.request):
            handle_download_request(self.request)
            return

        self.handle_sssh()

    def handle_sssh(self):
        token = secrets.token_urlsafe(18).replace("-", "").replace("_", "")
        session_path = SESSION_ROOT / token
        registered = False
        try:
            session_path.mkdir(parents=True, exist_ok=True)
            n, e, pem = generate_session_public_key()
            (session_path / "challenge.txt").write_text(challenge_text_from_pem(pem, token), encoding="utf-8")
            REGISTRY.add(token, session_path)
            registered = True

            intro = (
                "SSSH - Super Secure Shell\n\n"
                "A fresh challenge.txt has been generated for this connection.\n\n"
                "Download it using the SAME host and port you used for nc:\n\n"
                f"  {challenge_url_template(token)}\n\n"
                "After downloading challenge.txt, come back here and type 'start'\n"
            )
            self.request.sendall(intro.encode("utf-8"))
            while True:
                data = self.request.recv(1024)
                if not data:
                    return
                command = data.strip().lower()
                if command == b"start":
                    break
                if command in {b"quit", b"exit", b"done"}:
                    self.request.sendall(b"bye\n")
                    return
                self.request.sendall(b"type 'start' to begin SSSH\n")

            verifier = SignatureVerifier(n, e)
            Session(self.request, verifier, self.accounts).run()
        except (EOFError, TimeoutError, ConnectionError, ProtocolError, OSError):
            return
        finally:
            if registered:
                schedule_cleanup(token)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    global SESSION_ROOT
    SESSION_ROOT = choose_session_root()
    Handler.accounts = AccountDB(PASSWORD_FILE)
    print(f"SSSH session root: {SESSION_ROOT}", flush=True)
    with ThreadedTCPServer(("0.0.0.0", PORT), Handler) as server:
        print(f"SSSH TCP/HTTP listening on {PORT}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
