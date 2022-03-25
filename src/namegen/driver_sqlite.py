import sqlite3
import typing

from .driver import Driver


def camel(w: str):
    return w[0].upper() + w[1:]


def get_expected_mmap_size(file: str) -> int:
    import pathlib
    return int(pathlib.Path(file).stat().st_size * 1.2)


class SQLiteDriver(Driver):
    DB_NAME = 'namegen.db'

    __slots__ = ['connection', 'max_start', 'max_end']
    connection: typing.Optional[sqlite3.Connection]
    max_start: int
    max_end: int

    def __init__(self):
        self.connection = None
        self.disk = None

    def start(self):
        conn = self.connection
        if conn is None:
            conn = sqlite3.connect(self.DB_NAME, check_same_thread=False)
            with conn:
                c = conn.cursor()
                c.execute(f'PRAGMA mmap_size = {get_expected_mmap_size(self.DB_NAME)}')
                c.execute('PRAGMA journal_mode = WAL')
                c.execute('PRAGMA synchronous = normal')
                c.execute('PRAGMA temp_store = memory')
                c.execute('PRAGMA optimize')
                c.execute('SELECT (SELECT MAX(id) FROM start) + 1, (SELECT MAX(id) FROM end) + 1')
                self.max_start, self.max_end = c.fetchone()
                c.close()
            self.connection = conn

    def stop(self):
        conn = self.connection
        self.connection = None
        if conn is not None:
            conn.close()

    def generate(self):
        new_start_id: int
        new_start: str
        new_end_id: int
        new_end: str

        conn = self.connection
        if conn is None:
            raise ValueError('Connection Unavailable')

        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT s.value, e.value, sq.next_value
                FROM state st
                    JOIN sequences sq 
                        ON sq.start_id = st.next_start_id
                        AND sq.end_id = st.next_end_id
                    JOIN start s ON s.id = sq.start_id
                    JOIN end e ON e.id = sq.end_id
                """
            )
            start_part, end_part, sequence = cur.fetchone()
            cur.execute(
                """
                UPDATE sequences SET 
                    next_value = ((21 * next_value + 1) % 10000),
                    count = count + 1
                FROM state st
                WHERE start_id = st.next_start_id AND end_id = st.next_end_id
                """
            )
            cur.execute(
                """
                UPDATE state SET
                    next_start_id = CASE WHEN next_start_id + 1 < ? THEN next_start_id + 1 ELSE 1 END,
                    next_end_id = CASE WHEN next_end_id + 1 < ? THEN next_end_id + 1 ELSE 1 END,
                    current_count = current_count + 1
                """,
                (self.max_start, self.max_end)
            )
            cur.close()
        return f'{camel(start_part)}{camel(end_part)}#{sequence:04d}'


__all__ = ['SQLiteDriver']
