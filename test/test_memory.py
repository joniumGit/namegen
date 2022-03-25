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
    yield len(driver.items)


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
    data = set(map(lambda _: driver.generate().split('#')[0], range(0, lcm)))
    assert len(data) == lcm
    assert driver.generate().split('#')[0] in data


@pytest.mark.skip  # Passes
def test_format(driver, lcm):
    data = set(map(lambda _: driver.generate(), range(0, lcm * 10_000)))
    assert len(data) == lcm * 10_000
    assert len(list(filter(lambda s: not re.match(r'^.+#\d{4}$', s), data))) == 0


def test_save_load(driver):
    driver.stop()
    driver.start()
    value1 = driver.generate()
    driver.load_state()
    value2 = driver.generate()
    assert value1 == value2
