import collections
import sqlite3
import threading
import time
import typing

from .driver import Driver


def sqlite_init(database: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database, check_same_thread=False)
    with connection:
        c = connection.cursor()
        c.execute(f'PRAGMA mmap_size = {get_expected_mmap_size(database)}')
        c.execute('PRAGMA journal_mode = WAL')
        c.execute('PRAGMA synchronous = normal')
        c.execute('PRAGMA temp_store = memory')
        c.execute('PRAGMA optimize')
        c.close()
    return connection


def get_expected_mmap_size(file: str) -> int:
    import pathlib
    return int(pathlib.Path(file).stat().st_size * 1.2)


class Item:
    __slots__ = ['id', 'value']

    def __init__(self, _id: int, _value: str):
        self.id = _id
        self.value = _value[0].upper() + _value[1:]


class Counter:
    __slots__ = ['start', 'end', 'value']
    start: Item
    end: Item
    value: int

    def __init__(self, _start: Item, _end: Item, _count: int):
        self.value = _count
        self.start = _start
        self.end = _end

    def inc(self) -> int:
        v = self.value
        v = (21 * v + 1) % 10_000
        self.value = v
        return v


class HybridDriver(Driver):
    DB_NAME = 'namegen.db'

    __slots__ = [
        'connection',
        'max_start',
        'max_end',
        'queue',
        'event_queue',
        'running'
    ]

    connection: typing.Optional[sqlite3.Connection]
    max_start: int
    max_end: int
    queue: typing.Deque[Counter]

    def __init__(self):
        self.connection = None
        self.disk = None
        self.queue = collections.deque()
        self.worker = threading.Thread(
            target=self._watch,
            daemon=True,
            name='Event Queue Processor',
        )
        self.event_queue = collections.deque()
        self.running = False

    def _watch(self):
        self.running = True
        conn = self.connection
        q = self.event_queue
        max_start = self.max_start
        max_end = self.max_end

        def handler():
            start, end, next_value = q.popleft()
            conn.execute(
                """
                UPDATE sequences SET 
                    next_value = ?,
                    count = count + 1
                WHERE start_id = ? AND end_id = ?
                """,
                (next_value, start, end)
            )
            conn.execute(
                """
                UPDATE state SET
                    next_start_id = ?,
                    next_end_id = ?,
                    current_count = current_count + 1
                """,
                (min((start + 1, max_start)), min((end + 1, max_end)))
            )

        while self.running:
            try:
                handler()
            except IndexError:
                time.sleep(10E-3)

        try:
            while True:
                handler()
        except IndexError:
            pass

    def start(self):
        conn = self.connection
        if conn is None:
            conn = sqlite_init(self.DB_NAME)
            with conn:
                c = conn.cursor()

                c.execute('SELECT MAX(id) FROM start ORDER BY id ASC')
                max_start = int(c.fetchone()[0])

                c.execute('SELECT MAX(id) FROM end ORDER BY id ASC')
                max_end = int(c.fetchone()[0])

                self.max_start, self.max_end = max_start, max_end

                c.execute(
                    """
                    SELECT 
                        s.id,
                        s.value,
                        e.id,
                        e.value, 
                        sq.count 
                    FROM sequences sq
                        JOIN start s ON s.id = sq.start_id
                        JOIN end e ON e.id = sq.end_id
                    ORDER BY sq.start_id, sq.end_id ASC
                    """
                )
                for start_id, start, end_id, end, count in c.fetchall():
                    self.queue.append(
                        Counter(
                            Item(int(start_id), start),
                            Item(int(end_id), end),
                            int(count)
                        )
                    )

                c.execute('SELECT next_start_id, next_end_id FROM state')
                next_start, next_end = c.fetchone()
                next_start, next_end = int(next_start), int(next_end)

                while self.queue[0].start.id != next_start or self.queue[0].end.id != next_end:
                    self.queue.rotate(-1)

                c.close()
            self.connection = conn
        self.worker.start()

    def stop(self):
        self.running = False
        self.worker.join()
        conn = self.connection
        self.connection = None
        if conn is not None:
            conn.close()

    def generate(self):
        o = self.queue.popleft()
        try:
            return f'{o.start.value}{o.end.value}#{o.value:04d}'
        finally:
            self.event_queue.append((o.start.id, o.end.id, o.inc()))
            self.queue.append(o)


__all__ = ['HybridDriver']
