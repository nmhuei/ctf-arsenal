#!/usr/bin/env python3
import math, random, re, socket, subprocess, sys, os, time
from collections import deque

N=624; M=397; MATRIX_A=0x9908b0df; UPPER_MASK=0x80000000; LOWER_MASK=0x7fffffff
NVARS=N*32
# From random.random() we observe only the high 27/26 bits of each pair of MT outputs.
# The observable stream reaches rank 19964; the remaining 4 dimensions do not affect
# future random.random() values, so any assignment for them is fine.
TARGET_RANK=19964
RHS_BIT = 1 << NVARS

# ----- exact conversion from random.random() output to known MT output high bits -----
def float_to_53(s):
    # Python prints random.random() with round-trip repr precision; parsing back recovers exact binary64
    return int(float(s) * (1<<53))

def split_random_float(s):
    k = float_to_53(s)
    a = k >> 26           # top 27 bits of first 32-bit MT output (output >> 5)
    b = k & ((1<<26)-1)   # top 26 bits of second 32-bit MT output (output >> 6)
    return a, b

# ----- MT19937 symbolic linear engine over GF(2) -----
def xor_words(*words):
    out = [0]*32
    for w in words:
        for i in range(32): out[i] ^= w[i]
    return out

def temper_symbolic(word):
    y = word[:]
    old = y[:]
    # y ^= y >> 11
    for i in range(32):
        y[i] = old[i] ^ (old[i+11] if i+11 < 32 else 0)
    # y ^= (y << 7) & 0x9d2c5680
    old = y[:]
    mask = 0x9d2c5680
    for i in range(32):
        y[i] = old[i] ^ (old[i-7] if i-7 >= 0 and ((mask>>i)&1) else 0)
    # y ^= (y << 15) & 0xefc60000
    old = y[:]
    mask = 0xefc60000
    for i in range(32):
        y[i] = old[i] ^ (old[i-15] if i-15 >= 0 and ((mask>>i)&1) else 0)
    # y ^= y >> 18
    old = y[:]
    for i in range(32):
        y[i] = old[i] ^ (old[i+18] if i+18 < 32 else 0)
    return y

def twist_symbolic(state):
    # CPython twists the array in-place. The wraparound references in the
    # second part of the twist therefore use already-updated words; model the
    # same sequential mutation, not a simultaneous transition.
    mt = [w[:] for w in state]
    for i in range(N):
        y = [0]*32
        y[31] = mt[i][31]
        nxt = mt[(i+1)%N]
        for b in range(31):
            y[b] = nxt[b]
        yshr = [0]*32
        for b in range(31):
            yshr[b] = y[b+1]
        mag = [0]*32
        low = y[0]
        for b in range(32):
            if (MATRIX_A >> b) & 1:
                mag[b] = low
        mt[i] = xor_words(mt[(i+M)%N], yshr, mag)
    return mt

class LinearMTRecover:
    def __init__(self):
        self.state = [[1 << (i*32 + b) for b in range(32)] for i in range(N)]
        self.index = 0
        self.basis = {}  # pivot -> (coeff_int, rhs_bit)
        self.rank = 0
        self.word_count = 0
        self.float_count = 0
    def next_word_expr(self):
        if self.index >= N:
            self.state = twist_symbolic(self.state)
            self.index = 0
        expr = temper_symbolic(self.state[self.index])
        self.index += 1
        self.word_count += 1
        return expr
    def add_equation(self, coeff, rhs):
        c = coeff
        r = rhs & 1
        while c:
            p = c.bit_length() - 1
            if p in self.basis:
                bc, br = self.basis[p]
                c ^= bc
                r ^= br
            else:
                self.basis[p] = (c, r)
                self.rank += 1
                return True
        if r:
            raise ValueError('inconsistent equations')
        return False
    def add_known_high(self, expr, shift, value):
        # known: output >> shift == value; output bit j known for j in shift..31
        for j in range(shift, 32):
            bit = (value >> (j-shift)) & 1
            self.add_equation(expr[j], bit)
    def add_float(self, s):
        a,b = split_random_float(s)
        e1 = self.next_word_expr()
        self.add_known_high(e1, 5, a)
        e2 = self.next_word_expr()
        self.add_known_high(e2, 6, b)
        self.float_count += 1
    def is_solved(self):
        return self.rank >= TARGET_RANK
    def solve_bits(self):
        if not self.is_solved():
            raise ValueError(f'not enough rank: {self.rank}/{TARGET_RANK}')
        sol = 0
        # pivots are highest set bit; equations only have lower bits besides pivot after elimination
        for p in sorted(self.basis):
            c, r = self.basis[p]
            v = ( (c & sol).bit_count() & 1 ) ^ r
            if v:
                sol |= 1 << p
        return sol
    def recover_state_words(self):
        sol = self.solve_bits()
        words=[]
        for i in range(N):
            w=0
            for b in range(32):
                if (sol >> (i*32+b)) & 1:
                    w |= 1 << b
            words.append(w)
        return words

# ----- concrete MT predictor -----
def temper(y):
    y ^= (y >> 11)
    y &= 0xffffffff
    y ^= (y << 7) & 0x9d2c5680
    y &= 0xffffffff
    y ^= (y << 15) & 0xefc60000
    y &= 0xffffffff
    y ^= (y >> 18)
    return y & 0xffffffff

class MT19937Predictor:
    def __init__(self, state_words, index=0):
        self.mt = [x & 0xffffffff for x in state_words]
        self.index = index
    def twist(self):
        mt = self.mt
        for i in range(N):
            y = (mt[i] & UPPER_MASK) | (mt[(i+1)%N] & LOWER_MASK)
            mt[i] = (mt[(i+M)%N] ^ (y >> 1) ^ (MATRIX_A if (y & 1) else 0)) & 0xffffffff
        self.index = 0
    def getrandbits32(self):
        if self.index >= N:
            self.twist()
        y = temper(self.mt[self.index])
        self.index += 1
        return y
    def random(self):
        a = self.getrandbits32() >> 5
        b = self.getrandbits32() >> 6
        return ((a << 26) + b) / float(1<<53)
    def clone(self):
        c = MT19937Predictor(self.mt[:], self.index)
        return c

# ----- deterministic lookahead policy -----
def stand_outcome(pred, p1):
    # returns (win_bool, draws_consumed, dealer_total)
    p = pred.clone()
    p2 = 0.0
    cnt=0
    while p2 <= p1:
        p2 += p.random(); cnt += 1
    return (p2 >= 1.0), cnt, p2

def find_winning_action(pred, p1, depth=12, memo=None):
    # At a decision point after player's current total p1, pred points to next random if hit or dealer draw.
    # Return 's' or 'h' if a forced current-round win is found; otherwise stand/hit based on fallback.
    if memo is None: memo = {}
    key = (pred.index, tuple(pred.mt) if False else None, round(p1, 15), depth)  # unused heavy state key avoided
    win,_,_ = stand_outcome(pred, p1)
    if win:
        return 's'
    if depth <= 0:
        return None
    p = pred.clone()
    u = p.random()
    if p1 + u >= 1.0:
        return None
    # Recursively see whether after consuming one player hit a winning choice exists.
    nxt = find_winning_action(p, p1+u, depth-1)
    if nxt is not None:
        return 'h'
    return None

def choose_action(pred, p1):
    # Try to guarantee this round. If impossible within depth, use a known-good threshold fallback.
    act = find_winning_action(pred, p1, depth=18)
    if act:
        return act
    # fallback: optimal no-prediction threshold ~0.5705565283; but if stand loses, hit unless very risky
    if p1 >= 0.570556528295196:
        return 's'
    # If the immediate hit would bust, stand.
    pc = pred.clone()
    if p1 + pc.random() >= 1.0:
        return 's'
    return 'h'


# ----- finite-horizon planner after PRNG recovery -----
def build_plan_from_decision(pred, p1_current, rounds_remaining, current_wins, target_wins=800, lookahead_floats=50000):
    """Return (actions, max_future_wins) from the current prompt.

    pred points at the next random.random() value. p1_current is the already-drawn
    player total for the current round. rounds_remaining includes the current
    incomplete round.
    """
    import functools
    sys.setrecursionlimit(10000)
    pc = pred.clone()
    xs = [pc.random() for _ in range(lookahead_floats)]

    @functools.lru_cache(maxsize=None)
    def transitions_start(k):
        # Start of a future round: xs[k] is the mandatory first player draw.
        res = []
        p1 = xs[k]
        h = 0
        while True:
            # Stand now after h extra hits.
            idx = k + 1 + h
            p2 = 0.0
            while p2 <= p1:
                p2 += xs[idx]
                idx += 1
            res.append((1 if p2 >= 1.0 else 0, idx, h, 's'))

            # Or take one more hit. If it busts, the round ends immediately.
            p1 += xs[k + 1 + h]
            h += 1
            if p1 >= 1.0:
                res.append((0, k + 1 + h, h, 'b'))
                break
        return tuple(res)

    @functools.lru_cache(maxsize=None)
    def F(r, k):
        if current_wins + (rounds_remaining - r) >= target_wins:
            # Not used for pruning in reconstruction; keep recurrence simple.
            pass
        if r == 0:
            return 0
        best = -10**9
        for w, nk, _h, _kind in transitions_start(k):
            val = w + F(r - 1, nk)
            if val > best:
                best = val
        return best

    def transitions_decision(p1_initial, k=0):
        res = []
        p1 = p1_initial
        h = 0
        while True:
            idx = k + h
            p2 = 0.0
            while p2 <= p1:
                p2 += xs[idx]
                idx += 1
            res.append((1 if p2 >= 1.0 else 0, idx, h, 's'))
            p1 += xs[k + h]
            h += 1
            if p1 >= 1.0:
                res.append((0, k + h, h, 'b'))
                break
        return tuple(res)

    actions = []
    future_wins = 0

    # Pick transition for the current incomplete round.
    best = None
    for tr in transitions_decision(p1_current, 0):
        w, nk, h, kind = tr
        val = w + F(rounds_remaining - 1, nk)
        # Tie-break toward fewer hits/less consumption, then wins now.
        key = (val, w, -nk)
        if best is None or key > best[0]:
            best = (key, tr)
    _key, (w, k, h, kind) = best
    future_wins += w
    actions.extend(['h'] * h)
    if kind == 's':
        actions.append('s')

    # Reconstruct future full rounds.
    for r in range(rounds_remaining - 1, 0, -1):
        best = None
        for tr in transitions_start(k):
            w, nk, h, kind = tr
            val = w + F(r - 1, nk)
            key = (val, w, -nk)
            if best is None or key > best[0]:
                best = (key, tr)
        _key, (w, nk, h, kind) = best
        future_wins += w
        actions.extend(['h'] * h)
        if kind == 's':
            actions.append('s')
        k = nk
        if current_wins + future_wins >= target_wins:
            break

    max_future = best[0][0] if False else None
    return actions, (best[0][0] if False else F(rounds_remaining, 0) if False else future_wins), F.cache_info()

DRAW_RE = re.compile(rb'\[([0-9]+(?:\.[0-9]*)?(?:e[-+]?\d+)?)\]')
SCORE_RE = re.compile(rb'Score: (\d+)-(\d+)')
FLAG_RE = re.compile(rb'(crypto\{[^\r\n]*\}|SEE\{[^\r\n]*\}|SEETF\{[^\r\n]*\}|flag\{[^\r\n]*\}|Here is your flag:.*)')

class Tube:
    def __init__(self, host=None, port=None, local=False):
        self.buf = b''
        if local:
            env=os.environ.copy(); env['FLAG']='LOCALFLAG{test_flag}'
            self.p = subprocess.Popen([sys.executable, '/mnt/data/probability-seetf/files/probability_b87be2ad09e5a7895a19cc3d3510731b.py'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
            self.sock=None
        else:
            self.sock = socket.create_connection((host, port), timeout=10)
            self.sock.settimeout(10)
            self.p=None
    def recv_some(self, timeout=10):
        if self.sock:
            self.sock.settimeout(timeout)
            try: return self.sock.recv(4096)
            except socket.timeout: return b''
        else:
            import select
            fd=self.p.stdout.fileno()
            r,_,_=select.select([fd],[],[],timeout)
            if not r: return b''
            return os.read(fd,4096)
    def sendline(self, s):
        if isinstance(s,str): s=s.encode()
        if self.sock:
            self.sock.sendall(s+b'\n')
        else:
            self.p.stdin.write(s+b'\n'); self.p.stdin.flush()
    def close(self):
        try:
            if self.sock: self.sock.close()
            else: self.p.kill()
        except Exception: pass

def run_game(local=False, host='archive.cryptohack.org', port=59737, collect_min=624, verbose=True, pre_threshold=0.70, echo=False):
    t=Tube(host,port,local=local)
    rec=LinearMTRecover()
    pred=None
    action_queue=[]
    planned=False
    observed=[]
    scores=(0,0)
    p1=None
    pending_prediction_check=[]
    rounds=0
    start=time.time()
    try:
        while True:
            data=t.recv_some(timeout=20)
            if not data:
                print('\n[!] timeout/no data')
                break
            if echo:
                sys.stdout.buffer.write(data); sys.stdout.buffer.flush()
            # parse draws in arrival order
            for m in DRAW_RE.finditer(data):
                fs=m.group(1).decode()
                observed.append(fs)
                if pred is None:
                    rec.add_float(fs)
                    if verbose and rec.float_count % 25 == 0:
                        print(f"\n[collector] floats={rec.float_count}, rank={rec.rank}/{TARGET_RANK}", flush=True)
                    if rec.float_count >= collect_min and rec.is_solved():
                        words=rec.recover_state_words()
                        pred=MT19937Predictor(words, index=0)
                        for _ in range(rec.word_count):
                            pred.getrandbits32()
                        # verify predictor against future server draws as they arrive
                        print(f"[+] recovered MT after {rec.float_count} floats ({rec.word_count} 32-bit outputs), rank={rec.rank}", flush=True)
                else:
                    # Consume and check against predictor for every server draw observed.
                    exp=pred.random()
                    got=float(fs)
                    if abs(exp-got)>0:
                        # str/float exact should match, but display decimal use equality of repr? use tolerance
                        if abs(exp-got)>1e-18:
                            print(f"\n[!] predictor mismatch exp={exp!r} got={got!r}", flush=True)
                            raise SystemExit
                # update p1 crudely based on text prefix? We'll reset from printed p1 when needing input.
            sm=SCORE_RE.findall(data)
            if sm:
                scores=tuple(map(int, sm[-1])); rounds=sum(scores)
                if verbose:
                    print(f"\n[score] {scores[0]}-{scores[1]} after {rounds}", flush=True)
            fm=FLAG_RE.search(data)
            if fm:
                print('\n[+] FLAG:', fm.group(1).decode(errors='replace'))
                return fm.group(1).decode(errors='replace')
            # Handle prompts. Need determine p1 from latest prompt text: line contains '(p1 = value)' before prompt.
            while b'Do you want to hit or stand? ' in data or b'Do you want to hit or stand? ' in t.buf:
                # Simpler: accumulated current buffer from data? use all received in self buf? We'll maintain external buf.
                break
            # Maintain global buffer for prompt processing
            t.buf += data
            while b'Do you want to hit or stand? ' in t.buf:
                before, t.buf = t.buf.split(b'Do you want to hit or stand? ', 1)
                # latest p1 in text before prompt
                mlist = list(re.finditer(rb'p1 = ([0-9]+(?:\.[0-9]*)?(?:e[-+]?\d+)?)', before))
                if not mlist:
                    # maybe p1 exactly? fallback stand
                    p1_val=0.0
                else:
                    p1_val=float(mlist[-1].group(1))
                if pred is None:
                    # Before recovery, use a draw-farming threshold strategy: it collects
                    # MT outputs faster than standing immediately while still winning some rounds.
                    action = 'h' if p1_val < pre_threshold else 's'
                else:
                    if not planned:
                        completed = scores[0] + scores[1]
                        rounds_remaining = 1337 - completed
                        print(f"[*] planning from score {scores[0]}-{scores[1]} with {rounds_remaining} rounds remaining...", flush=True)
                        action_queue, planned_wins, info = build_plan_from_decision(pred, p1_val, rounds_remaining, scores[0])
                        print(f"[+] plan can add about {planned_wins} wins; projected total {scores[0] + planned_wins}; states={info.currsize}", flush=True)
                        if scores[0] + planned_wins < 800:
                            print('[!] this run is mathematically short of 800; reconnecting/retrying is better', flush=True)
                            return None
                        planned = True
                    if not action_queue:
                        print('[!] action queue exhausted unexpectedly', flush=True)
                        return None
                    action = action_queue.pop(0)
                    if verbose:
                        print(f"[act] p1={p1_val:.17g} -> {action}", flush=True)
                t.sendline(action)
    finally:
        # don't close immediately on return? ok
        pass

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv)>1 else 'local'
    if mode == 'test':
        r=random.Random(123456)
        rec=LinearMTRecover()
        for i in range(700):
            v = r.random()
            rec.add_float(repr(v))
            if rec.is_solved():
                print('solved at', i+1)
                break
        print('rank', rec.rank)
        words=rec.recover_state_words()
        pred=MT19937Predictor(words, index=0)
        for _ in range(rec.word_count):
            pred.getrandbits32()
        ok=True
        for i in range(1000):
            a=r.random(); b=pred.random()
            if a!=b:
                print('mismatch', i, a, b); ok=False; break
        print('predict ok', ok)
    elif mode == 'local':
        attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        for a in range(1, attempts + 1):
            print(f'=== local attempt {a}/{attempts} ===', flush=True)
            flag = run_game(local=True, collect_min=624)
            if flag:
                break
    elif mode == 'remote':
        attempts = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        for a in range(1, attempts + 1):
            print(f'=== remote attempt {a}/{attempts} ===', flush=True)
            try:
                flag = run_game(local=False, host='archive.cryptohack.org', port=59737, collect_min=624)
            except OSError as e:
                print(f'[!] connection failed: {e}', flush=True)
                break
            if flag:
                break
