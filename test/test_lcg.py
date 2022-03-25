import pytest

from namegen.utils import generate_next, get_word_file, read_initial_values

MAX = 9999
MIN = 0


def test_full_cycle():
    data = set()

    last = 0
    for _ in range(0, MAX + 1):
        last = generate_next(last)
        data.add(last)

    assert len(data) == MAX + 1

    for i in range(0, MAX + 1):
        assert i in data


def test_generate_stays_in_range():
    last = 0
    for _ in range(0, 1_000_000):
        last = generate_next(last)
        assert MIN <= last <= MAX


def test_start_produces_whole_range():
    for i in range(0, MAX + 1):
        assert MIN <= generate_next(i) <= MAX


def test_back_to_range():
    assert MIN <= generate_next(MAX + 1) <= MAX


@pytest.fixture
def custom_file():
    import os
    file = 'abc.csv'
    env = os.environ
    os.environ = dict()
    os.environ['NAMEGEN_FILE'] = file
    assert get_word_file() == file
    yield file
    os.environ = env


def test_initial_values_no_header(custom_file):
    with open(custom_file, 'w') as f:
        f.write('\n'.join(['aaA,b', 'c,d']))
    s, e = read_initial_values()
    assert list(s) == ['AaA', 'C']
    assert list(e) == ['B', 'D']


def test_initial_values_no_end(custom_file):
    with open(custom_file, 'w') as f:
        f.write('\n'.join(['a,b', 'c']))
    s, e = read_initial_values()
    assert list(s) == ['A', 'C']
    assert list(e) == ['B']


def test_initial_values_no_end_with_comma(custom_file):
    with open(custom_file, 'w') as f:
        f.write('\n'.join(['aa,b', 'c,']))
    s, e = read_initial_values()
    assert list(s) == ['Aa', 'C']
    assert list(e) == ['B']


def test_empty_end(custom_file):
    with open(custom_file, 'w') as f:
        f.write('\n'.join(['aa,', 'c,']))
    s, e = read_initial_values()
    assert list(s) == ['Aa', 'C']
    assert list(e) == []


def test_header(custom_file):
    with open(custom_file, 'w') as f:
        f.write('\n'.join(['start,end', 'c,b']))
    s, e = read_initial_values()
    assert list(s) == ['C']
    assert list(e) == ['B']
