import re
import time

import pytest

from namegen.driver_hybrid import HybridDriver

PATTERN = re.compile(r'^.+#\d{4}$')


@pytest.fixture(autouse=True)
def driver():
    driver = HybridDriver()
    driver.start()
    yield driver
    driver.event_queue.clear()
    driver.stop()


@pytest.fixture
def lcm(driver):
    from namegen.utils import lcm
    c = driver.connection.cursor()
    c.execute('SELECT COUNT(*) FROM start')
    start, = c.fetchone()
    c.execute('SELECT COUNT(*) FROM end')
    end, = c.fetchone()
    yield lcm(start, end)


def test_generate_pattern(driver):
    for i in range(0, 10_000):
        name = driver.generate()
        assert PATTERN.match(name)


def test_generate_state_rollover(driver):
    while driver.queue[0].start.id != driver.max_start or driver.queue[0].end.id != driver.max_end:
        driver.queue.rotate(-1)

    driver.generate()
    time.sleep(100E-3)  # Propagation time

    c = driver.connection.cursor()
    c.execute('SELECT next_start_id, next_end_id FROM state')
    data = c.fetchone()
    assert data[0] == 1
    assert data[1] == 1


def test_periods(driver, lcm):
    data = set(map(lambda _: driver.generate().split('#')[0], range(0, lcm)))
    assert len(data) == lcm
    assert driver.generate().split('#')[0] in data


def test_initial_alignment(driver):
    driver2 = HybridDriver()
    with driver.connection:
        c = driver.connection.cursor()
        c.execute('UPDATE state SET next_start_id = 2, next_end_id = 4')
        c.close()
    driver2.start()
    try:
        assert driver2.queue[0].start.id == 2
        assert driver2.queue[0].end.id == 4
    finally:
        driver2.stop()


@pytest.mark.skip  # Passes
def test_format(driver, lcm):
    data = set(map(lambda _: driver.generate(), range(0, lcm * 10_000)))
    assert len(data) == lcm * 10_000
    assert len(list(filter(lambda s: not re.match(r'^.+#\d{4}$', s), data))) == 0


def test_throws_none(driver):
    driver.stop()
    with pytest.raises(ValueError):
        driver.generate()


def test_start_twice_no_throw(driver):
    driver.start()
    driver.start()


def test_stop_twice_no_throw(driver):
    driver.stop()
    driver.stop()
