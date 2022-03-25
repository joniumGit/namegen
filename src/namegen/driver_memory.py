import base64
import collections
import gzip
import json
import typing

from .driver import Driver
from .utils import hash_file, read_initial_values, generate_next, get_random, get_state_file, get_word_file, lcm


class Item:
    __slots__ = ['start', 'end', 'value']
    start: str
    end: str
    value: int

    def __init__(self, start: str, end: str, value: int):
        self.start = start
        self.end = end
        self.value = value

    def next(self):
        self.value = generate_next(self.value)
        return self

    def to_dict(self):
        return {
            'start': self.start,
            'end': self.end,
            'value': self.value
        }

    @staticmethod
    def from_dict(item: typing.Dict) -> 'Item':
        return Item(start=item['start'], end=item['end'], value=int(item['value']))


class MemoryDriver(Driver):
    items: typing.Deque[Item] = collections.deque()

    def to_json(self) -> str:
        return base64.b64encode(gzip.compress(json.dumps(dict(
            items=list(map(lambda i: i.to_dict(), self.items))
        )).encode('utf-8'))).decode('ascii')

    def from_json(self, f: typing.TextIO):
        self.items.clear()
        self.items.extend(map(
            lambda o: Item.from_dict(o),
            json.loads(gzip.decompress(base64.b64decode(f.readline().strip().encode('ascii'))))['items']
        ))

    def load_state(self):
        try:
            with open(get_state_file(), 'r') as f:
                file_hash = f.readline().strip()
                if file_hash == hash_file(get_word_file()):
                    self.from_json(f)
                    return True
        except FileNotFoundError:
            pass
        return False

    def start(self):
        if not self.load_state():
            starts, ends = read_initial_values()
            i = 0
            j = 0
            cnt = 0
            max_s = len(starts) - 1
            max_e = len(ends) - 1
            while cnt != lcm(max_s, max_e):
                self.items.append(Item(start=starts[i], end=ends[j], value=get_random()))
                i = i + 1 if i < max_s else 0
                j = j + 1 if j < max_e else 0
                cnt += 1

    def stop(self):
        with open(get_state_file(), 'w') as f:
            f.write(hash_file(get_word_file()))
            f.write('\n')
            f.write(self.to_json())

    def generate(self):
        item = self.items.popleft()
        try:
            return f'{item.start}{item.end}#{item.value:04d}'
        finally:
            self.items.append(item.next())


__all__ = ['MemoryDriver']
