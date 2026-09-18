from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo


def credited_days(
    started_at: datetime,
    ended_at: datetime | None,
    goal_hours: float,
    tz_name: str,
    now: datetime | None = None,
) -> set:
    tz = ZoneInfo(tz_name)
    now = now or datetime.now(started_at.tzinfo)
    effective_end = ended_at or now

    goal_reached_at = started_at + timedelta(hours=goal_hours)
    if goal_reached_at > effective_end:
        return set()

    days = set()
    local_reached = goal_reached_at.astimezone(tz)
    days.add(local_reached.date())

    checkpoint = datetime.combine(
        local_reached.date() + timedelta(days=1), time(6, 0), tzinfo=tz
    )
    while checkpoint <= effective_end.astimezone(tz):
        days.add(checkpoint.date())
        checkpoint += timedelta(days=1)

    return days

def compute_streak(
    facts: list,
    goal_hours: float,
    tz_name: str,
    now: datetime | None = None,
) -> int:
    tz = ZoneInfo(tz_name)
    now = now or datetime.now(timezone.utc)

    all_credited = set()
    for fast in fasts:
        all_credited |= credited_days(
            fast.started_at, fast.ended_at, goal_hours, tz_name, now
        )

    streak = 0
    day = now.astimezone(tz).date() - timedelta(days=1)
    while day in all_credited:
        streak += 1
        day -= timedelta(days=1)

    return streak
