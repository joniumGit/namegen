from namegen.driver_memory import generate_next, LCG_MIN as MIN, LCG_MAX as MAX


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
