import re

import pytest

from namegen.driver_sqlite import SQLiteDriver

PATTERN = re.compile(r'^.+#\d{4}$')


@pytest.fixture(autouse=True)
def driver():
    driver = SQLiteDriver()
    driver.start()
    yield driver
    driver.stop()


@pytest.fixture()
def c(driver):
    conn = driver.connection
    c = conn.cursor()
    yield c
    c.close()


@pytest.fixture
def lcm(driver, c):
    from namegen.driver_memory import lcm
    c.execute('SELECT COUNT(*) FROM start')
    start, = c.fetchone()
    c.execute('SELECT COUNT(*) FROM end')
    end, = c.fetchone()
    yield lcm(start, end)


def test_generate_pattern(driver):
    for i in range(0, 10_000):
        name = driver.generate()
        assert PATTERN.match(name)


def test_generate_state_rollover(driver, c):
    c.execute(
        """
        UPDATE state SET 
            next_start_id = (SELECT MAX(id) FROM start), 
            next_end_id = (SELECT MAX(id) FROM end),
            current_count = 0
        """
    )

    driver.generate()

    c.execute('SELECT next_start_id, next_end_id, current_count FROM state')
    data = c.fetchone()
    assert data[0] == 1
    assert data[1] == 1
    assert data[2] == 1


def test_periods(driver, lcm):
    data = set(map(lambda _: driver.generate().split('#')[0], range(0, lcm)))
    assert len(data) == lcm
    assert driver.generate().split('#')[0] in data


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
    driver.generate()
