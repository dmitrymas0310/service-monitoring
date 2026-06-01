from datetime import datetime, timezone

import pytest

from app.utils.datetime_utils import get_current_month_bounds


def test_month_bounds_returns_tuple_of_two_datetimes():
    start, end = get_current_month_bounds()
    assert isinstance(start, datetime)
    assert isinstance(end, datetime)


def test_month_start_is_first_day():
    start, _ = get_current_month_bounds()
    assert start.day == 1


def test_month_start_is_midnight():
    start, _ = get_current_month_bounds()
    assert start.hour == 0
    assert start.minute == 0
    assert start.second == 0
    assert start.microsecond == 0


def test_month_end_is_first_day_of_next_month():
    start, end = get_current_month_bounds()
    assert end.day == 1
    if start.month == 12:
        assert end.month == 1
        assert end.year == start.year + 1
    else:
        assert end.month == start.month + 1
        assert end.year == start.year


def test_month_bounds_are_timezone_aware():
    start, end = get_current_month_bounds()
    assert start.tzinfo is not None
    assert end.tzinfo is not None


def test_month_bounds_with_explicit_january():
    now = datetime(2025, 1, 15, 12, 30, tzinfo=timezone.utc)
    start, end = get_current_month_bounds(now=now)
    assert start == datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    assert end == datetime(2025, 2, 1, 0, 0, 0, 0, tzinfo=timezone.utc)


def test_month_bounds_with_explicit_december():
    now = datetime(2024, 12, 25, tzinfo=timezone.utc)
    start, end = get_current_month_bounds(now=now)
    assert start == datetime(2024, 12, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
    assert end == datetime(2025, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)


def test_month_bounds_with_naive_datetime():
    now = datetime(2025, 6, 10, 8, 0, 0)
    start, end = get_current_month_bounds(now=now)
    assert start.day == 1
    assert start.month == 6
    assert end.month == 7


def test_month_bounds_end_greater_than_start():
    start, end = get_current_month_bounds()
    assert end > start


def test_month_bounds_span_exactly_one_month():
    now = datetime(2025, 3, 20, tzinfo=timezone.utc)
    start, end = get_current_month_bounds(now=now)
    assert start.month == 3
    assert end.month == 4
    delta_days = (end - start).days
    assert 28 <= delta_days <= 31


def test_month_bounds_for_february_non_leap():
    now = datetime(2025, 2, 14, tzinfo=timezone.utc)
    start, end = get_current_month_bounds(now=now)
    assert (end - start).days == 28


def test_month_bounds_for_february_leap():
    now = datetime(2024, 2, 14, tzinfo=timezone.utc)
    start, end = get_current_month_bounds(now=now)
    assert (end - start).days == 29
