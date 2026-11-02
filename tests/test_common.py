"""tools/common.py — 시간 문자열 변환"""
import pytest
from common import ts


@pytest.mark.parametrize("s, sec", [
    ("4:31", 271.0),
    ("1:02:05", 3725.0),
    ("271.5", 271.5),
    (" 0:07 ", 7.0),
    (12, 12.0),
    ("0:00.5", 0.5),
])
def test_ts(s, sec):
    assert ts(s) == pytest.approx(sec)
