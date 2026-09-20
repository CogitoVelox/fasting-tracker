from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.streak import credited_days, compute_streak

tz = ZoneInfo("America/New_York")


class FakeFast:
    def __init__(self, started_at, ended_at):
        self.started_at = started_at
        self.ended_at = ended_at


def test_short_fast_credits_nothing():
    start = datetime(2026, 9, 17, 20, 0, tzinfo=tz)
    end = datetime(2026, 9, 18, 6, 0, tzinfo=tz)
    assert credited_days(start, end, 16, "America/New_York") == set()


def test_fast_reaching_goal_exactly_credits_one_day():
    start = datetime(2026, 9, 17, 19, 0, tzinfo=tz)
    end = datetime(2026, 9, 18, 11, 0, tzinfo=tz)
    days = credited_days(start, end, 16, "America/New_York")
    assert days == {datetime(2026, 9, 18).date()}


def test_long_fast_credits_multiple_days():
    start = datetime(2026, 9, 14, 23, 0, tzinfo=tz)
    end = datetime(2026, 9, 16, 23, 0, tzinfo=tz)
    days = credited_days(start, end, 16, "America/New_York")
    assert days == {
        datetime(2026, 9, 15).date(),
        datetime(2026, 9, 16).date(),
    }


def test_naive_timestamps_from_sqlite_are_treated_as_utc():
    start = datetime(2026, 9, 17, 19, 0)  # no tzinfo
    end = datetime(2026, 9, 18, 11, 0)    # no tzinfo
    days = credited_days(start, end, 16, "America/New_York")
    assert days == {datetime(2026, 9, 18).date()}


def test_streak_counts_consecutive_days_and_stops_at_gap():
    fasts = [
        FakeFast(
            datetime(2026, 9, 13, 19, 0, tzinfo=tz),
            datetime(2026, 9, 14, 12, 0, tzinfo=tz),
        ),
        FakeFast(
            datetime(2026, 9, 14, 19, 0, tzinfo=tz),
            datetime(2026, 9, 15, 12, 0, tzinfo=tz),
        ),
        FakeFast(
            datetime(2026, 9, 15, 19, 0, tzinfo=tz),
            datetime(2026, 9, 16, 12, 0, tzinfo=tz),
        ),
    ]
    now = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)
    assert compute_streak(fasts, 16, "America/New_York", now=now) == 3


def test_streak_is_zero_with_no_fasts():
    now = datetime(2026, 9, 17, 8, 0, tzinfo=timezone.utc)
    assert compute_streak([], 16, "America/New_York", now=now) == 0
