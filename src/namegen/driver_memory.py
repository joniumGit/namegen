import base64
import gzip
import hashlib
import json
import random
from collections import deque

LCG_MIN = 0
LCG_MAX = 9999


def generate_next(previous: int) -> int:
    return (21 * previous + 1) % 10_000


START = deque()
END = deque()
COUNTS = deque()

STATE_FILE = 'namegen-state'
WORD_FILE = 'wordlist.txt'


def to_json() -> str:
    return base64.b64encode(gzip.compress(json.dumps(dict(
        start=list(START),
        end=list(END),
        counts=list(COUNTS),
    )).encode('utf-8'))).decode('ascii')


def hashit() -> str:
    with open(WORD_FILE, 'rb') as wf:
        return base64.b64encode(
            hashlib.sha256(
                wf.read(),
                usedforsecurity=False
            ).digest()
        ).decode('ascii')


def load_state():
    try:
        with open(STATE_FILE, 'r') as f:
            file_hash = f.readline().strip()
            if file_hash == hashit():
                START.clear()
                END.clear()
                COUNTS.clear()
                data = json.loads(gzip.decompress(base64.b64decode(f.readline().strip().encode('ascii'))))
                START.extend(data['start'])
                END.extend(data['end'])
                COUNTS.extend(data['counts'])
                return True
    except FileNotFoundError:
        pass
    return False


def stop():
    with open(STATE_FILE, 'w') as f:
        f.write(hashit())
        f.write('\n')
        f.write(to_json())


def start():
    if not load_state():
        import math
        with open('wordlist.txt', 'r') as f:
            data = f.read().splitlines()
            split = data.index('#split')
            START.extend(set(w[0].upper() + w[1:] for w in data[:split]))
            END.extend(set(w[0].upper() + w[1:] for w in data[split + 1:]))
            COUNTS.extend(random.randint(LCG_MIN, LCG_MAX) for _ in range(0, math.lcm(len(START), len(END))))


def generate_name():
    start = START.popleft()
    end = END.popleft()
    cnt = COUNTS.popleft()
    try:
        return f'{start}{end}', cnt
    finally:
        START.append(start)
        END.append(end)
        COUNTS.append(generate_next(cnt))


def generate():
    name, count = generate_name()
    return f'{name}#{count:04d}'


__all__ = ['generate', 'start', 'stop']
