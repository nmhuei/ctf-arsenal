#!/usr/local/bin/python3
"""
SUR KHARVAA :: the target

An archer looses one arrow. The range inspects it, again and again, before it
is allowed to strike the target, and the target itself is bare - it holds no
tools an arrow could pick up.

    the DRAW   - the arrow is read as text and must be plain and quiet
    the AIM    - the arrow's shape is checked; only still figures are allowed
    the NOCK   - the fletched arrow is read; no forbidden name may be engraved
                 on it, not even in the compiled arrowhead
    the LOOSE  - the arrow strikes a target that carries nothing of its own

This file is the whole target. Nothing about it is hidden: what you can read
here is exactly what runs. The arrow arrives on stdin as raw bytes and whatever
it prints on stdout is what the range reports back to you.

Hitting the target is only the first half. The range is run by the keeper, and
only the keeper may read the day's record. An archer is not a keeper.
"""
import ast
import subprocess  # loaded so the target has a process API to refuse
import sys

MAX_ARROW = 8192

# --- events the target refuses to witness -----------------------------------
# The loose happens on a bare target (no builtins), so the ordinary ways out
# are already gone. These are the ways that remain worth refusing. A refusal
# is loud: the archer is told exactly which one they touched.
REFUSED = {
    "os.system",
    "os.exec",
    "os.fork",
    "os.forkpty",
    "os.spawn",
    "os.posix_spawn",
    "subprocess.Popen",
    "import",
    "open",
    "ctypes.dlopen",
    "ctypes.dlsym",
    "ctypes.call_function",
    "ctypes.addressof",
    "socket.socket",
    "socket.getaddrinfo",
    "code.__new__",
    "cpython.run_module",
    "pty.spawn",
}


class Refused(Exception):
    pass


# --- the DRAW: the arrow, read as text, must be plain and quiet --------------
def draw(arrow: bytes) -> str:
    if len(arrow) > MAX_ARROW:
        raise Refused(f"draw: the arrow is too long ({len(arrow)} > {MAX_ARROW})")
    try:
        text = arrow.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refused(f"draw: the arrow is not clean text: {exc}")
    for ch in text:
        if ch in "\n\t":
            continue
        if not (" " <= ch <= "~"):
            raise Refused(f"draw: the arrow carries a wild mark {ch!r}")
        if ch == "_":
            raise Refused("draw: an arrow may not carry the under-mark '_'")
        if ch == "\\":
            raise Refused("draw: an arrow may not carry the back-mark '\\'")
    return text


# --- the AIM: only still figures are allowed --------------------------------
# A drawn arrow is a picture. A picture that can reach for anything is not a
# still figure. So the aim allows only shapes that sit there: names, numbers
# and text, laid out and added up. Nothing that calls, nothing that reaches
# into a thing, nothing that fetches from elsewhere.
STILL = {
    ast.Module,
    ast.Expr,
    ast.Assign,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Tuple,
    ast.List,
    ast.BinOp,
    ast.UnaryOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.Mod,
    ast.UAdd,
    ast.USub,
}


def aim(text: str) -> None:
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        raise Refused(f"aim: the arrow is not a figure at all - {exc.msg}")
    for node in ast.walk(tree):
        if type(node) not in STILL:
            raise Refused(f"aim: the figure moves - {type(node).__name__} is not still")


# --- the NOCK: read the fletched (compiled) arrow ---------------------------
# A name the target refuses to see spelled out - even in the compiled arrow's
# own names and constants, nested code objects included. Spelling any of these
# out engraves the arrowhead and the shot is refused; a name you cannot spell,
# you must build.
FORBIDDEN = {
    "system", "popen",
    "posix_spawn", "spawn", "spawnv", "spawnve", "spawnvp",
    "fork_exec", "_fork_exec", "_posixsubprocess",
    "execv", "execve", "execvp", "execvpe",
}


def nock(shot) -> None:
    stack = [shot]
    while stack:
        code = stack.pop()
        for name in code.co_names:
            if name in FORBIDDEN:
                raise Refused(f"nock: the arrowhead is engraved {name!r}")
        for const in code.co_consts:
            if isinstance(const, str) and const in FORBIDDEN:
                raise Refused(f"nock: the arrowhead is engraved {const!r}")
            if isinstance(const, type(shot)):
                stack.append(const)


# --- the LOOSE: strike a bare target ----------------------------------------
def keeper(event: str, args) -> None:
    if event in REFUSED:
        raise Refused(f"loose: the target refuses to witness {event!r}")


def loose(arrow: bytes) -> None:
    # The arrow is compiled from its own bytes. The range read it as text; the
    # target reads it as it pleases, then reads what it compiled to.
    shot = compile(arrow, "<target>", "exec")
    nock(shot)
    sys.addaudithook(keeper)
    exec(shot, {"__builtins__": {}})


def main() -> int:
    arrow = sys.stdin.buffer.read()
    try:
        text = draw(arrow)
        aim(text)
    except Refused as exc:
        sys.stdout.write(f"{exc}\n")
        sys.stdout.flush()
        return 1
    # Past the draw and the aim. Whatever the target does now, it does on its
    # own, with empty hands.
    try:
        loose(arrow)
    except Refused as exc:
        sys.stdout.write(f"{exc}\n")
        sys.stdout.flush()
        return 1
    except SystemExit:
        raise
    except BaseException as exc:  # a missed shot is still a shot
        sys.stdout.write(f"loose: the arrow fell short - {type(exc).__name__}: {exc}\n")
        sys.stdout.flush()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
