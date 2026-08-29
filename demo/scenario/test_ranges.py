from ranges import parse_range


def test_pair():
    assert parse_range('2-7') == (2, 7)


def test_single():
    assert parse_range('5') == (5, 5)


def test_rejects_junk():
    assert parse_range('abc') is None
