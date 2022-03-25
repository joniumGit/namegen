import collections
import sqlite3
import threading
import time
import typing

from .driver import Driver
from .utils import sqlite_init, generate_next


class Item:
    __slots__ = ['id', 'value']
    id: int
    value: str

    def __init__(self, _id: int, _value: str):
        self.id = _id
        self.value = _value


class Counter:
    __slots__ = ['start', 'end', 'value']
    start: Item
    end: Item
    value: int

    def __init__(self, _start: Item, _end: Item, _count: int):
        self.value = _count
        self.start = _start
        self.end = _end

    def next(self) -> typing.Tuple[int, int, int]:
        self.value = generate_next(self.value)
        return self.start.id, self.end.id, self.value


class HybridDriver(Driver):
    __slots__ = [
        'connection',
        'max_start',
        'max_end',
        'queue',
        'event_queue',
        'running',
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
        conn = self.connection
        q = self.event_queue
        max_start = self.max_start
        max_end = self.max_end

        def handler():
            with conn:
                start, end, next_value = q.popleft()
                next_start = start + 1 if start < max_start else 1
                next_end = end + 1 if end < max_end else 1
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
                    (next_start, next_end)
                )

        time.sleep(10E-3)  # Initial startup
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
        if self.running:
            return
        conn = self.connection
        if conn is None:
            conn = sqlite_init()
            with conn:
                c = conn.cursor()
                c.execute('SELECT MAX(id) FROM start')
                max_start = int(c.fetchone()[0])
                c.execute('SELECT MAX(id) FROM end')
                max_end = int(c.fetchone()[0])
                self.max_start, self.max_end = max_start, max_end
                c.execute(
                    """
                    SELECT 
                        s.id,
                        s.value,
                        e.id,
                        e.value, 
                        sq.next_value 
                    FROM sequences sq
                        JOIN start s ON s.id = sq.start_id
                        JOIN end e ON e.id = sq.end_id
                    ORDER BY sq.ROWID
                    """
                )
                for start_id, start, end_id, end, value in c.fetchall():
                    self.queue.append(
                        Counter(
                            Item(int(start_id), start),
                            Item(int(end_id), end),
                            int(value)
                        )
                    )
                c.execute('SELECT next_start_id, next_end_id FROM state')
                next_start, next_end = c.fetchone()
                next_start, next_end = int(next_start), int(next_end)

                # Regain state
                while next_start != self.queue[0].start.id or next_end != self.queue[0].end.id:
                    self.queue.rotate(-1)

                c.close()
            self.connection = conn
        self.running = True
        self.worker.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        self.worker.join()
        conn = self.connection
        self.connection = None
        if conn is not None:
            conn.close()

    def generate(self):
        if not self.running:
            raise ValueError('Not Running')
        o = self.queue.popleft()
        try:
            return f'{o.start.value}{o.end.value}#{o.value:04d}'
        finally:
            self.event_queue.append(o.next())
            self.queue.append(o)


__all__ = ['HybridDriver']
