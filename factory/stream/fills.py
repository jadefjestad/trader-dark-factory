"""Quote-based fill model for the streaming tiers (issue #75).

Instead of filling at the next bar's open, an order decided at time d fills against the first quote
stamped at or after d + latency: buys at the ask, sells at the bid. An order larger than
`max_size_multiple` times the displayed size at that quote fills only that much; the rest is carried to
the following quotes until it fills or `max_wait` passes, and anything left then is reported unfilled.
A quote stamped before d + latency is never used (leakage test in tests/test_stream_fills.py).

Pure functions over pandas frames, so the same code serves historical replays and shadow-mode checks.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

import pandas as pd

QUOTE_COLUMNS = ["time", "symbol", "bid", "ask", "bid_size", "ask_size"]


@dataclass
class Fill:
    symbol: str
    side: str
    decided_at: pd.Timestamp
    quote_at: pd.Timestamp
    qty: float
    price: float


def fill_order(quotes: pd.DataFrame, symbol: str, side: str, qty: float, decided_at, latency: dt.timedelta,
               max_size_multiple: float = 1.0, max_wait: dt.timedelta = dt.timedelta(seconds=30)
               ) -> tuple[list[Fill], float]:
    """Fills for one order against `quotes` (QUOTE_COLUMNS, sorted by time) and the quantity left unfilled."""
    if side not in ("buy", "sell") or qty <= 0:
        raise ValueError(f"bad order {side} {qty}")
    first = pd.Timestamp(decided_at) + pd.Timedelta(latency)
    last = first + pd.Timedelta(max_wait)
    q = quotes[(quotes["symbol"] == symbol) & (quotes["time"] >= first) & (quotes["time"] <= last)]
    price_col, size_col = ("ask", "ask_size") if side == "buy" else ("bid", "bid_size")
    fills, left = [], float(qty)
    for row in q.itertuples(index=False):
        price, size = getattr(row, price_col), getattr(row, size_col)
        if not (price > 0 and size > 0) or row.bid >= row.ask:   # crossed, locked or empty quotes are skipped
            continue
        take = min(left, size * max_size_multiple)
        fills.append(Fill(symbol, side, pd.Timestamp(decided_at), row.time, take, float(price)))
        left -= take
        if left <= 1e-9:
            return fills, 0.0
    return fills, left


def replay(orders: pd.DataFrame, quotes: pd.DataFrame, latency: dt.timedelta, **kw) -> pd.DataFrame:
    """Fill every order (columns time, symbol, side, qty). One row per order: filled qty, average price,
    unfilled qty and the delay from decision to last fill."""
    quotes = quotes.sort_values("time")
    rows = []
    for o in orders.itertuples(index=False):
        fills, left = fill_order(quotes, o.symbol, o.side, o.qty, o.time, latency, **kw)
        filled = sum(f.qty for f in fills)
        rows.append({"time": o.time, "symbol": o.symbol, "side": o.side, "qty": o.qty, "filled": filled,
                     "avg_price": sum(f.qty * f.price for f in fills) / filled if filled else float("nan"),
                     "unfilled": left,
                     "delay_s": (fills[-1].quote_at - pd.Timestamp(o.time)).total_seconds() if fills else float("nan")})
    return pd.DataFrame(rows)
