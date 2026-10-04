"""Feed validation (design 3.1). Anything suspicious means no new orders, never a guess."""
from __future__ import annotations

import datetime as dt


class FeedGuard:
    def __init__(self, symbols: list[str], max_symbol_gap_s: float = 30, max_feed_gap_s: float = 10,
                 max_jump: float = 0.05):
        self.symbols = list(symbols)
        self.max_symbol_gap = dt.timedelta(seconds=max_symbol_gap_s)
        self.max_feed_gap = dt.timedelta(seconds=max_feed_gap_s)
        self.max_jump = max_jump                  # a trade this far from the last good price is rejected
        self.last_seen: dict[str, dt.datetime] = {}
        self.last_price: dict[str, float] = {}
        self.last_any: dt.datetime | None = None
        self.rejected = 0

    def _seen(self, symbol, received):
        self.last_seen[symbol] = received
        self.last_any = received

    def accept_trade(self, symbol: str, price: float, size: float, received: dt.datetime) -> bool:
        if symbol not in self.symbols or not (price > 0) or not (size > 0):
            self.rejected += 1
            return False
        ref = self.last_price.get(symbol)
        if ref is not None and abs(price / ref - 1) > self.max_jump:
            self.rejected += 1
            return False
        self.last_price[symbol] = price
        self._seen(symbol, received)
        return True

    def accept_quote(self, symbol: str, bid: float, ask: float, received: dt.datetime) -> bool:
        if symbol not in self.symbols or not (bid > 0) or not (ask > bid):   # crossed or locked
            self.rejected += 1
            return False
        self._seen(symbol, received)
        return True

    def feed_stale(self, now: dt.datetime) -> bool:
        return self.last_any is None or now - self.last_any > self.max_feed_gap

    def stale_symbols(self, now: dt.datetime) -> set[str]:
        if self.feed_stale(now):
            return set(self.symbols)
        return {s for s in self.symbols if s not in self.last_seen or now - self.last_seen[s] > self.max_symbol_gap}
