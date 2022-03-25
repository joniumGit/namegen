import re

import pytest

from namegen.driver_memory import MemoryDriver


@pytest.fixture(scope='session', autouse=True)
def driver():
    driver = MemoryDriver()
    driver.start()
    driver.stop()
    yield driver


@pytest.fixture(scope='function', autouse=True)
def driver_load(driver):
    driver.load_state()
    yield


@pytest.fixture
def lcm(driver):
    from namegen.driver_memory import lcm
    yield lcm(len(driver.words_start), len(driver.words_end))


@pytest.mark.parametrize('n', [
    100,
    1000,
    10_000,
    50_000
])
def test_namegen(driver, n):
    for _ in range(0, 100):
        data = set(map(lambda _: driver.generate(), range(0, n)))
        assert len(data) == n


def test_periods(driver, lcm):
    data = set(map(lambda _: driver.generate_name()[0], range(0, lcm)))
    assert len(data) == lcm
    assert driver.generate_name()[0] in data


@pytest.mark.skip  # Passes
def test_format(driver, lcm):
    data = set(map(lambda _: driver.generate(), range(0, lcm)))
    assert len(data) == lcm * (driver.serail_max - driver.serial_min)
    assert len(list(filter(lambda s: not re.match(r'^.+#\d{4}$', s), data))) == 0


def test_save_load(driver):
    cnt = driver.words_cnt
    for _ in range(0, len(cnt)):
        cnt.append(int(cnt.popleft() * 0))
    cnt[0] = 1
    driver.stop()
    value1 = driver.generate()
    cnt[0] = 2
    driver.start()
    assert cnt[0] == 1
    value2 = driver.generate()
    assert value1 == value2
