"""Order budget (design 3.4/3.5): a token bucket, per-symbol spacing, a daily cap and restart-safe order ids."""
from __future__ import annotations

import datetime as dt


class OrderThrottle:
    def __init__(self, per_minute: int = 30, per_day: int = 500, min_seconds_per_symbol: float = 30):
        self.capacity = float(per_minute)
        self.rate = per_minute / 60.0             # tokens per second
        self.tokens = float(per_minute)
        self.per_day = per_day
        self.spacing = dt.timedelta(seconds=min_seconds_per_symbol)
        self.last_t: dt.datetime | None = None
        self.last_symbol: dict[str, dt.datetime] = {}
        self.day: dt.date | None = None
        self.today = 0

    def _refill(self, now: dt.datetime) -> None:
        if self.last_t is not None:
            self.tokens = min(self.capacity, self.tokens + (now - self.last_t).total_seconds() * self.rate)
        self.last_t = now
        if self.day != now.date():
            self.day, self.today = now.date(), 0

    def allow(self, symbol: str, now: dt.datetime) -> tuple[bool, str]:
        """Consume budget for one order if every limit allows it; otherwise say which limit refused."""
        self._refill(now)
        if self.today >= self.per_day:
            return False, "daily order cap"
        if symbol in self.last_symbol and now - self.last_symbol[symbol] < self.spacing:
            return False, "symbol traded too recently"
        if self.tokens < 1:
            return False, "per-minute order budget"
        self.tokens -= 1
        self.today += 1
        self.last_symbol[symbol] = now
        return True, "ok"


def client_order_id(bar_end: dt.datetime, symbol: str) -> str:
    """One id per (bar, symbol): a restart that re-decides the same bar sends the same id, which the
    broker rejects as a duplicate, while later bars get fresh ids."""
    return f"stream-{bar_end:%Y%m%d-%H%M%S}-{symbol}"
