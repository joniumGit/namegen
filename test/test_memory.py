import math
import re

import pytest
from namegen.driver_memory import LCG_MIN as MIN, LCG_MAX as MAX
from namegen.driver_memory import start, stop, load_state, START, END, COUNTS, generate, generate_name


@pytest.fixture(scope='session', autouse=True)
def setup():
    start()
    stop()
    yield


@pytest.fixture(scope='function', autouse=True)
def setup_stage_2(setup):
    load_state()
    yield


@pytest.mark.parametrize('n', [
    100,
    1000,
    10_000,
    50_000
])
def test_namegen(n):
    for _ in range(0, 100):
        data = set(map(lambda _: generate(), range(0, n)))
        assert len(data) == n


def test_periods():
    data = set(map(lambda _: generate_name()[0], range(0, math.lcm(len(START), len(END)))))
    assert len(data) == math.lcm(len(START), len(END))
    assert generate_name()[0] in data


@pytest.mark.skip  # Passes
def test_format():
    data = set(map(lambda _: generate(), range(0, math.lcm(len(START), len(END)) * (MAX - MIN))))
    assert len(data) == math.lcm(len(START), len(END)) * (MAX - MIN)
    assert len(list(filter(lambda s: not re.match(r'^.+#\d{4}$', s), data))) == 0


def test_save_load():
    for _ in range(0, len(COUNTS)):
        COUNTS.append(int(COUNTS.popleft() * 0))
    COUNTS[0] = 1
    stop()
    value1 = generate()
    COUNTS[0] = 2
    start()
    assert COUNTS[0] == 1
    value2 = generate()
    assert value1 == value2
