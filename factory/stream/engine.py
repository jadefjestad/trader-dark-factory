"""The streaming decision loop (design 3.3 to 3.6), with the websocket and broker passed in.

The container feeds `on_message` with Alpaca stream messages and calls `tick` on a timer. Each tick
closes finished bars, asks the strategy for target weights on the bar history, and turns the change
into paper orders that pass the stream limits and the order throttle. It fails closed: any doubt
means no new orders, and the conditions in `_halt_reason` flatten the book instead.

Shadow mode (the default) logs the orders it would place and submits nothing (design 4.4).
"""
from __future__ import annotations

import datetime as dt
import math
import os
from zoneinfo import ZoneInfo

import pandas as pd

from factory.data import MarketData
from factory.execute import plan_orders
from factory.risk import RiskError, check_account
from factory.stream.bars import BarBuilder
from factory.stream.feed import FeedGuard
from factory.stream.throttle import OrderThrottle, client_order_id

NY = ZoneInfo("America/New_York")


class StreamEngine:
    def __init__(self, symbols, seconds, decide, broker, limits: dict, stream: dict, window: int = 720,
                 shadow: bool = True, log=print):
        self.symbols = list(symbols)
        self.decide = decide                  # MarketData -> {symbol: weight}; raises or returns junk = hold
        self.broker = broker
        self.limits, self.stream = limits, stream
        self.window = window
        self.shadow = shadow
        self.log = log
        self.bars = BarBuilder(self.symbols, seconds)
        self.guard = FeedGuard(self.symbols, stream["max_stream_gap_seconds"], stream.get("max_feed_gap_seconds", 10))
        self.throttle = OrderThrottle(stream["max_orders_per_minute"], stream["max_orders_per_day"],
                                      stream["min_seconds_between_trades_per_symbol"])
        self.seconds = seconds
        self.history: list = []
        self.start_equity: float | None = None
        self.halted: str | None = None
        self.bad_decisions = 0
        self.seq = 0

    # ---------------------------------------------------------------- setup and feed
    def start(self, account: dict) -> None:
        check_account(account, self.limits)          # paper account, active, not blocked; raises RiskError
        self.start_equity = float(account["equity"])

    def on_message(self, msg: dict, received: dt.datetime) -> None:
        kind, sym = msg.get("T"), msg.get("S")
        try:
            ts = pd.Timestamp(msg["t"]).to_pydatetime()
            if kind == "t" and self.guard.accept_trade(sym, float(msg["p"]), float(msg["s"]), received):
                self.bars.on_trade(sym, float(msg["p"]), float(msg["s"]), ts)
            elif kind == "q" and self.guard.accept_quote(sym, float(msg["bp"]), float(msg["ap"]), received):
                self.bars.on_quote(sym, float(msg["bp"]), float(msg["ap"]), ts)
        except (KeyError, TypeError, ValueError):
            self.guard.rejected += 1

    # ---------------------------------------------------------------- decisions
    def _market_data(self) -> MarketData:
        df = pd.DataFrame([vars(b) for b in self.history[-self.window * len(self.symbols):]])
        wide = {f: df.pivot_table(index="end", columns="symbol", values=f, aggfunc="last")
                .reindex(columns=self.symbols) for f in ("open", "high", "low", "close", "volume")}
        return MarketData(**wide, timeframe=f"{self.seconds}s", source="alpaca:iex-stream")

    def _targets(self) -> dict | None:
        try:
            raw = self.decide(self._market_data())
            t = {s: float(raw.get(s, 0.0)) for s in self.symbols}
            if not all(math.isfinite(w) for w in t.values()):
                raise ValueError("non-finite weight")
        except Exception as e:  # junk from the strategy is a hold, three in a row stops the day
            self.bad_decisions += 1
            self.log({"event": "bad_decision", "error": f"{type(e).__name__}: {e}"[:200]})
            if self.bad_decisions >= 3:
                self.halted = "strategy failed three decisions in a row"
            return None
        self.bad_decisions = 0
        return t

    def _check_targets(self, t: dict) -> None:
        cap, gross_cap = self.stream["max_position_weight"], self.stream["max_gross_exposure"]
        for s, w in t.items():
            if w < -1e-9 and not self.limits["allow_short"]:
                raise RiskError(f"short weight for {s}")
            if abs(w) > cap + 1e-9:
                raise RiskError(f"{s} weight {w:.3f} > stream cap {cap}")
        if sum(abs(w) for w in t.values()) > gross_cap + 1e-9:
            raise RiskError(f"gross exposure above stream cap {gross_cap}")

    def _halt_reason(self, now: dt.datetime, equity: float) -> str | None:
        if self.halted:
            return self.halted
        if os.environ.get("STREAM_KILL") == "1" or not self.limits.get("trading_enabled", False):
            return "kill switch"
        h, m = map(int, self.stream["flatten_at"].split(":"))
        if now.astimezone(NY).time() >= dt.time(h, m):
            return "flatten time"
        if self.start_equity and equity < self.start_equity * (1 - self.stream["max_daily_loss"]):
            self.halted = "daily loss limit"
            return self.halted
        return None

    def tick(self, now: dt.datetime, positions: dict, equity: float, market_open: bool) -> list[dict]:
        """Close finished bars and act on them. Returns the orders submitted (or, in shadow mode, planned)."""
        new = self.bars.close_until(now)
        self.history.extend(new)
        del self.history[:-self.window * len(self.symbols)]
        if not new:
            return []
        if not market_open:                     # orders sent while closed would queue for the next open
            return []
        prices = {b.symbol: b.close for b in new}
        halt = self._halt_reason(now, equity)
        if halt:
            targets, allowed = {s: 0.0 for s in self.symbols}, set(self.symbols)   # flatten whatever is held
        else:
            if self.start_equity is None:
                return []
            stale = self.guard.stale_symbols(now)
            if len(stale) == len(self.symbols):
                self.log({"event": "no_orders", "reason": "feed stale", "at": now.isoformat()})
                return []
            targets = self._targets()
            if targets is None:
                return []
            try:
                self._check_targets(targets)
            except RiskError as e:
                self.log({"event": "no_orders", "reason": str(e), "at": now.isoformat()})
                return []
            allowed = set(self.symbols) - stale
        priced = {s: t for s, t in targets.items() if s in prices and s in allowed}
        orders = plan_orders(priced, positions, prices, equity * (1 - self.limits.get("cash_buffer", 0.0)),
                             self.limits["min_order_notional"])
        sent = []
        for o in orders:
            if not halt:
                ok, why = self.throttle.allow(o["symbol"], now)
                if not ok:
                    self.log({"event": "order_skipped", "symbol": o["symbol"], "reason": why, "at": now.isoformat()})
                    continue
            self.seq += 1
            o = {**o, "client_order_id": client_order_id(now.astimezone(NY).date(), self.seq),
                 "expected_price": prices[o["symbol"]], "reason": halt or "signal"}
            if not self.shadow:
                self.broker.submit_order(o["symbol"], o["qty"], o["side"], o["client_order_id"])
            self.log({"event": "shadow_order" if self.shadow else "order", **o, "at": now.isoformat()})
            sent.append(o)
        return sent
