"""Replay a trading day through the live streaming engine (issue #75).

Historical trades and quotes (factory/stream/history.py) are fed to the same StreamEngine the
container runs, message by message in time order, with a tick every `tick_seconds`. Orders go to a
SimBroker that fills them with the quote fill model (factory/stream/fills.py): at the first quote at or
after the decision plus latency, buys at the ask, sells at the bid, size-capped. Nothing here touches a
real broker or the network.

Simplification: the simulated position changes at the decision tick, while its price comes from the
later quote; with latencies of a second or two this only matters to strategies that re-trade a symbol
within that window, which the order throttle already forbids (30 s per symbol).
"""
from __future__ import annotations

import datetime as dt

import pandas as pd

from factory.stream.engine import StreamEngine
from factory.stream.fills import fill_order


class SimBroker:
    def __init__(self, quotes: pd.DataFrame, cash: float, latency: dt.timedelta, **fill_kw):
        self.quotes = quotes.sort_values("time").reset_index(drop=True)
        self.cash = float(cash)
        self.latency, self.fill_kw = latency, fill_kw
        self.positions: dict[str, int] = {}
        self.last: dict[str, float] = {}
        self.now: pd.Timestamp | None = None
        self.fills: list[dict] = []
        self.unfilled: list[dict] = []

    def submit_order(self, symbol, qty, side, client_order_id):
        fills, left = fill_order(self.quotes, symbol, side, qty, self.now, self.latency, **self.fill_kw)
        sign = 1 if side == "buy" else -1
        for f in fills:
            q = int(f.qty)          # whole shares, as the paper account trades
            if q <= 0:
                continue
            self.positions[symbol] = self.positions.get(symbol, 0) + sign * q
            self.cash -= sign * q * f.price
            self.fills.append({"decided_at": self.now, "time": f.quote_at, "symbol": symbol, "side": side,
                               "qty": q, "price": f.price, "client_order_id": client_order_id})
        if left > 0:
            self.unfilled.append({"decided_at": self.now, "symbol": symbol, "side": side, "qty": left})

    def equity(self) -> float:
        return self.cash + sum(q * self.last.get(s, 0.0) for s, q in self.positions.items())


def _messages(trades: pd.DataFrame, quotes: pd.DataFrame) -> list[tuple[pd.Timestamp, dict]]:
    out = [(r.time, {"T": "t", "S": r.symbol, "p": r.price, "s": r.size, "t": r.time.isoformat()})
           for r in trades.itertuples(index=False)]
    out += [(r.time, {"T": "q", "S": r.symbol, "bp": r.bid, "ap": r.ask, "t": r.time.isoformat()})
            for r in quotes.itertuples(index=False)]
    return sorted(out, key=lambda x: (x[0], x[1]["T"] != "q"))   # a quote and a trade at once: quote first


def replay(trades: pd.DataFrame, quotes: pd.DataFrame, decide, symbols: list[str], seconds: int,
           limits: dict, stream: dict, latency: dt.timedelta = dt.timedelta(seconds=1),
           cash: float = 100_000.0, tick_seconds: float = 1.0, **fill_kw) -> dict:
    """Run one session. Returns equity per tick, every fill, unfilled remainders and the engine's log."""
    broker = SimBroker(quotes, cash, latency, **fill_kw)
    log: list[dict] = []
    engine = StreamEngine(symbols, seconds, decide, broker, limits, stream, shadow=False, log=log.append)
    engine.start_equity = cash          # the paper account check belongs to the live app, not a replay
    msgs = _messages(trades, quotes)
    if not msgs:
        return {"equity": pd.Series(dtype=float), "fills": pd.DataFrame(), "unfilled": pd.DataFrame(), "log": log}
    step = pd.Timedelta(seconds=tick_seconds)
    t, end, i, curve = msgs[0][0].ceil(step), msgs[-1][0] + pd.Timedelta(seconds=seconds) + step, 0, {}
    while t <= end:
        while i < len(msgs) and msgs[i][0] <= t:
            ts, m = msgs[i]
            engine.on_message(m, ts.to_pydatetime())
            if m["T"] == "t":
                broker.last[m["S"]] = float(m["p"])
            i += 1
        broker.now = t
        engine.tick(t.to_pydatetime(), dict(broker.positions), broker.equity(), market_open=True)
        curve[t] = broker.equity()
        t += step
    return {"equity": pd.Series(curve), "fills": pd.DataFrame(broker.fills),
            "unfilled": pd.DataFrame(broker.unfilled), "log": log}
