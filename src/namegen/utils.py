import typing


def get_word_file() -> str:
    import os
    return os.getenv('NAMEGEN_FILE', 'wordlist.csv')


def get_database_file() -> str:
    import os
    return os.getenv('NAMEGEN_DB_FILE', 'namegen.db')


def get_state_file() -> str:
    import os
    return os.getenv('NAMEGEN_MEMORY_STATE', 'namegen-memory-state')


def read_initial_values() -> typing.Tuple[typing.List[str], typing.List[str]]:
    start_data = list()
    end_data = list()
    with open(get_word_file(), 'r') as f:
        maybe_header = f.readline().split(',')
        if maybe_header[0].strip().lower() != 'start':
            if len(maybe_header) >= 1:
                camel_add(start_data, maybe_header[0])
            if len(maybe_header) == 2:
                camel_add(end_data, maybe_header[1])
        for row in map(lambda s: s.split(','), f):
            if len(row) >= 1:
                camel_add(start_data, row[0])
            if len(row) == 2:
                camel_add(end_data, row[1])
    return start_data, end_data


def camel_add(q: typing.List, w: str):
    w = w.strip()
    if w != '':
        q.append(f'{w[0].upper()}{w[1:]}')


def generate_next(previous: int) -> int:
    return (21 * previous + 1) % 10_000


def get_random() -> int:
    import random
    return random.randint(0, 10_000)


def get_expected_mmap_size() -> int:
    import pathlib
    return int(pathlib.Path(get_database_file()).stat().st_size * 1.2)


try:
    from math import lcm
except ImportError:
    def lcm(a, b):
        import math
        return int(a * b / math.gcd(a, b))


def hash_file(file: str) -> str:
    import hashlib
    import base64
    read_size = 128 * 4
    h = hashlib.sha256()
    with open(file, 'rb') as wf:
        part = wf.read(read_size)
        while part:
            h.update(part)
            part = wf.read(read_size)
    return base64.b64encode(h.digest()).decode('ascii')


try:
    import sqlite3


    def sqlite_init() -> sqlite3.Connection:
        connection = sqlite3.connect(get_database_file(), check_same_thread=False)
        with connection:
            c = connection.cursor()
            c.execute(f'PRAGMA mmap_size = {get_expected_mmap_size()}')
            c.execute('PRAGMA journal_mode = WAL')
            c.execute('PRAGMA synchronous = normal')
            c.execute('PRAGMA temp_store = memory')
            c.close()
        with connection:
            c = connection.cursor()
            c.execute('SELECT COUNT(*) FROM start')
            if not int(c.fetchone()[0]):
                s, e = read_initial_values()
                connection.executemany('INSERT INTO start (value) VALUES (?)', map(lambda o: (o,), s))
                connection.executemany('INSERT INTO end (value) VALUES (?)', map(lambda o: (o,), e))
                i = 1
                j = 1
                cnt = 0
                max_s = len(s)
                max_e = len(e)
                while cnt < lcm(max_s, max_e):
                    c.execute('INSERT INTO sequences (start_id, end_id) VALUES (?,?)', (i, j))
                    i = i + 1 if i < max_s else 1
                    j = j + 1 if j < max_e else 1
                    cnt += 1
            c.close()
        with connection:
            c = connection.cursor()
            c.execute('PRAGMA optimize')
            c.close()
        return connection
except ImportError:  # pragma nocover
    """Fails gracefully"""
