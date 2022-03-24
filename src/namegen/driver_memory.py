import base64
import gzip
import hashlib
import json
import random
from collections import deque
from typing import TextIO

from .driver import Driver


def generate_next(previous: int) -> int:
    return (21 * previous + 1) % 10_000


def hashit(file: str) -> str:
    with open(file, 'rb') as wf:
        return base64.b64encode(
            hashlib.sha256(
                wf.read(),
                usedforsecurity=False
            ).digest()
        ).decode('ascii')


class MemoryDriver(Driver):
    STATE_FILE = 'namegen-state'
    WORD_FILE = 'wordlist.txt'

    serial_min = 0
    serial_max = 9999

    words_start = deque()
    words_end = deque()
    words_cnt = deque()

    def to_json(self) -> str:
        return base64.b64encode(gzip.compress(json.dumps(dict(
            start=list(self.words_start),
            end=list(self.words_end),
            counts=list(self.words_cnt),
        )).encode('utf-8'))).decode('ascii')

    def from_json(self, f: TextIO):
        data = json.loads(gzip.decompress(base64.b64decode(f.readline().strip().encode('ascii'))))
        self.words_start.extend(data['start'])
        self.words_end.extend(data['end'])
        self.words_cnt.extend(data['counts'])

    def load_state(self):
        try:
            with open(self.STATE_FILE, 'r') as f:
                file_hash = f.readline().strip()
                if file_hash == hashit(self.WORD_FILE):
                    self.words_start.clear()
                    self.words_end.clear()
                    self.words_cnt.clear()
                    self.from_json(f)
                    return True
        except FileNotFoundError:
            pass
        return False

    def start(self):
        if not self.load_state():
            import math
            with open('wordlist.txt', 'r') as f:
                data = f.read().splitlines()
            split = data.index('#split')
            self.words_start.extend(set(w[0].upper() + w[1:] for w in data[:split]))
            self.words_end.extend(set(w[0].upper() + w[1:] for w in data[split + 1:]))
            self.words_cnt.extend(
                random.randint(self.serial_min, self.serial_max)
                for _ in range(0, math.lcm(len(self.words_start), len(self.words_end)))
            )

    def stop(self):
        with open(self.STATE_FILE, 'w') as f:
            f.write(hashit(self.WORD_FILE))
            f.write('\n')
            f.write(self.to_json())

    def generate_name(self):
        start = self.words_start.popleft()
        end = self.words_end.popleft()
        cnt = self.words_cnt.popleft()
        try:
            return f'{start}{end}', cnt
        finally:
            self.words_start.append(start)
            self.words_end.append(end)
            self.words_cnt.append(generate_next(cnt))

    def generate(self):
        name, count = self.generate_name()
        return f'{name}#{count:04d}'


__all__ = ['MemoryDriver']
