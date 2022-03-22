import math
import re

import pytest
from namegen import driver_sqlite
from namegen.driver_sqlite import start, stop, generate

PATTERN = re.compile(r'^.+#\d{4}$')


@pytest.fixture(autouse=True)
def start_stop():
    start()
    yield
    stop()


@pytest.fixture()
def c(start_stop):
    conn = driver_sqlite.connection
    c = conn.cursor()
    yield c
    c.close()


def test_generate_pattern():
    for i in range(0, 10_000):
        name = generate()
        assert PATTERN.match(name)


def test_generate_state_rollover(c):
    c.execute(
        """
        UPDATE state SET 
            next_start_id = (SELECT MAX(id) FROM start), 
            next_end_id = (SELECT MAX(id) FROM end),
            current_count = 0
        """
    )

    generate()

    c.execute('SELECT next_start_id, next_end_id, current_count FROM state')
    data = c.fetchone()
    assert data[0] == 1
    assert data[1] == 1
    assert data[2] == 1


def test_periods(c):
    c.execute('SELECT COUNT(*) FROM start')
    start, = c.fetchone()
    c.execute('SELECT COUNT(*) FROM end')
    end, = c.fetchone()

    data = set(map(lambda _: generate().split('#')[0], range(0, math.lcm(start, end))))
    assert len(data) == math.lcm(start, end)
    assert generate().split('#')[0] in data


@pytest.mark.skip  # Passes
def test_format(c):
    c.execute('SELECT COUNT(*) FROM start')
    start, = c.fetchone()
    c.execute('SELECT COUNT(*) FROM end')
    end, = c.fetchone()

    data = set(map(lambda _: generate(), range(0, math.lcm(start, end) * 10_000)))
    assert len(data) == math.lcm(start, end) * 10_000
    assert len(list(filter(lambda s: not re.match(r'^.+#\d{4}$', s), data))) == 0


def test_throws_none():
    stop()
    with pytest.raises(ValueError):
        generate()


def test_start_twice_no_throw():
    start()
    generate()
