"""Bars built from live trades and quotes (design 3.2).

Bars sit on fixed boundaries (e.g. every 5 s from midnight New York). A bar is emitted only once the
clock has passed its end, and carries `available_at`, the local time it was closed, which is the
earliest moment a strategy may act on it (same rule as the backtester: decide on bar t, fill after).
An interval with no trade repeats the previous close with volume 0 and filled=False.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass
class Bar:
    symbol: str
    start: dt.datetime
    end: dt.datetime
    available_at: dt.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    bid: float | None
    ask: float | None
    filled: bool


class BarBuilder:
    def __init__(self, symbols: list[str], seconds: int):
        if seconds <= 0 or 86400 % seconds:
            raise ValueError("bar length must divide a day evenly")
        self.seconds = seconds
        self.symbols = list(symbols)
        self._open: dict[tuple, dict] = {}        # (symbol, start) -> bar being built
        self._last_close: dict[str, float] = {}
        self._quote: dict[str, tuple[float, float]] = {}
        self._next_start: dt.datetime | None = None

    def _floor(self, ts: dt.datetime) -> dt.datetime:
        midnight = ts.replace(hour=0, minute=0, second=0, microsecond=0)
        n = int((ts - midnight).total_seconds()) // self.seconds
        return midnight + dt.timedelta(seconds=n * self.seconds)

    def on_trade(self, symbol: str, price: float, size: float, ts: dt.datetime) -> None:
        start = self._floor(ts)
        if self._next_start is not None and start < self._next_start:
            return                                # late print for a bar already emitted: never rewrite history
        if self._next_start is None:
            self._next_start = start
        b = self._open.get((symbol, start))
        if b is None:
            self._open[(symbol, start)] = {"o": price, "h": price, "l": price, "c": price, "v": size}
            return
        b["h"], b["l"], b["c"], b["v"] = max(b["h"], price), min(b["l"], price), price, b["v"] + size

    def on_quote(self, symbol: str, bid: float, ask: float, ts: dt.datetime) -> None:
        self._quote[symbol] = (bid, ask)
        if self._next_start is None:
            self._next_start = self._floor(ts)

    def close_until(self, now: dt.datetime) -> list[Bar]:
        """Emit every bar whose end is at or before `now`, oldest first, one per symbol per interval."""
        out = []
        while self._next_start is not None and self._next_start + dt.timedelta(seconds=self.seconds) <= now:
            start = self._next_start
            end = start + dt.timedelta(seconds=self.seconds)
            for s in self.symbols:
                b = self._open.pop((s, start), None)
                bid, ask = self._quote.get(s, (None, None))
                if b is not None:
                    out.append(Bar(s, start, end, now, b["o"], b["h"], b["l"], b["c"], b["v"], bid, ask, True))
                    self._last_close[s] = b["c"]
                elif s in self._last_close:
                    c = self._last_close[s]
                    out.append(Bar(s, start, end, now, c, c, c, c, 0.0, bid, ask, False))
            self._next_start = end
        return out
