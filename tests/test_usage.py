import datetime as dt

from factory.usage import plan

POLICY = {"max_runs_per_day": 5, "max_runs_per_5h": 3, "tasks_per_run": {"start": 1, "min": 1, "max": 3},
          "cooldown_after_limit_hours": 5, "unfinished_after_minutes": 90}
NOW = dt.datetime(2026, 10, 5, 20, 0, tzinfo=dt.timezone.utc)


def ev(run, kind, hours_ago, **kw):
    return {"event": kind, "run_id": run, "at": (NOW - dt.timedelta(hours=hours_ago)).isoformat(), **kw}


def test_fresh_start():
    assert plan([], POLICY, NOW) == {"go": True, "reason": "within budget", "tasks": 1, "runs_today": 0, "runs_5h": 0}


def test_cooldown_after_unfinished_run():
    p = plan([ev("a", "start", 2, tasks_allowed=2)], POLICY, NOW)
    assert not p["go"] and "cooling down" in p["reason"]


def test_batch_grows_after_clean_runs():
    events = [ev("a", "start", 12, tasks_allowed=1), ev("a", "end", 11.5, tasks=1),
              ev("b", "start", 8, tasks_allowed=2), ev("b", "end", 7.5, tasks=2)]
    assert plan(events, POLICY, NOW)["tasks"] == 3


def test_daily_cap():
    events = []
    for i in range(5):
        events += [ev(str(i), "start", 19 - i, tasks_allowed=1), ev(str(i), "end", 18.9 - i, tasks=1)]
    assert not plan(events, POLICY, NOW)["go"]
