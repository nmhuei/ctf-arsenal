#!/usr/local/bin/python3
import json
import random
import signal
from interpreter import Interpreter

TIMEOUT = 20
MAX_CODE_SIZE = 4096
MAX_SCORE = 1_000_000
MEMORY_SIZE = 1_000_000
MAX_CYCLES = 1_000_000


def run_challenge():
    try:
        data = json.loads(input())
    except json.JSONDecodeError:
        return {'ok': False, 'error': 'invalid json'}

    try:
        code = data['code']
        score = int(data['score'])
    except (KeyError, ValueError):
        return {'ok': False, 'error': 'invalid data'}

    if len(code) > MAX_CODE_SIZE:
        return {'ok': False, 'error': f'code is too long ({len(code)} > {MAX_CODE_SIZE})'}
    if not 0 <= score <= MAX_SCORE:
        return {'ok': False, 'error': f'score must be between 0 and {MAX_SCORE}'}

    random.seed(67)
    nums = [random.getrandbits(64) for _ in range(score)]

    def alarm_handler(signum, frame):
        raise TimeoutError(f'program timed out after {TIMEOUT}s')

    signal.signal(signal.SIGALRM, alarm_handler)
    signal.alarm(TIMEOUT)

    try:
        interpreter = Interpreter(memory_size=MEMORY_SIZE, max_cycles=MAX_CYCLES)
        memory = interpreter.run(code, nums)
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}

    if memory.data[:score] != sorted(nums):
        return {'ok': False, 'error': 'wrong answer (array is not sorted)'}

    return {'ok': True, 'cycles': memory.ctx.cycles}


if __name__ == '__main__':
    try:
        response = run_challenge()
    except Exception as exc:
        # catch any unhandled exceptions
        response = {'ok': False, 'error': str(exc)}

    print(json.dumps(response))
