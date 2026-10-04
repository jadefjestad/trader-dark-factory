import datetime as dt
from zoneinfo import ZoneInfo

import pytest

from factory.stream.engine import StreamEngine

NY = ZoneInfo("America/New_York")
T0 = dt.datetime(2026, 10, 5, 10, 0, 0, tzinfo=NY)
LIMITS = {"paper_only": True, "trading_enabled": True, "allow_short": False, "min_order_notional": 50,
          "cash_buffer": 0.0}
STREAM = {"max_gross_exposure": 0.5, "max_position_weight": 0.25, "max_orders_per_minute": 30,
          "max_orders_per_day": 500, "min_seconds_between_trades_per_symbol": 30, "max_daily_loss": 0.01,
          "max_stream_gap_seconds": 30, "flatten_at": "15:55"}
ACCOUNT = {"account_number": "PA123", "status": "ACTIVE", "equity": "100000"}


class FakeBroker:
    def __init__(self):
        self.orders = []

    def submit_order(self, symbol, qty, side, client_order_id):
        self.orders.append((symbol, qty, side, client_order_id))


def at(s):
    return T0 + dt.timedelta(seconds=s)


def trade(sym, p, s):
    return {"T": "t", "S": sym, "p": p, "s": 100, "t": at(s).isoformat()}


def engine(decide, shadow=False, **kw):
    e = StreamEngine(["AAPL", "MSFT"], 5, decide, FakeBroker(), {**LIMITS, **kw.pop("limits", {})},
                     {**STREAM, **kw.pop("stream", {})}, shadow=shadow, log=lambda r: None)
    e.start(ACCOUNT)
    return e


def feed(e, s, aapl=200.0, msft=400.0):
    e.on_message(trade("AAPL", aapl, s), at(s))
    e.on_message(trade("MSFT", msft, s), at(s))


def test_signal_becomes_orders_only_after_the_bar_closes():
    e = engine(lambda md: {"AAPL": 0.2})
    feed(e, 1)
    assert e.tick(at(4), {}, 100_000, True) == []                  # bar still open
    [o] = e.tick(at(5.1), {}, 100_000, True)
    assert (o["symbol"], o["side"], o["qty"]) == ("AAPL", "buy", 100)
    assert e.broker.orders[0][3] == "stream-20261005-100005-AAPL"


def test_shadow_mode_submits_nothing():
    e = engine(lambda md: {"AAPL": 0.2}, shadow=True)
    feed(e, 1)
    assert len(e.tick(at(5.1), {}, 100_000, True)) == 1 and e.broker.orders == []


def test_no_orders_when_market_closed_or_feed_stale():
    e = engine(lambda md: {"AAPL": 0.2})
    feed(e, 1)
    assert e.tick(at(5.1), {}, 100_000, False) == []
    feed(e, 6)
    assert e.tick(at(40), {}, 100_000, True) == []                 # nothing heard for 34 s
    assert e.broker.orders == []


def test_breaching_stream_caps_places_nothing():
    e = engine(lambda md: {"AAPL": 0.3})                           # cap is 0.25
    feed(e, 1)
    assert e.tick(at(5.1), {}, 100_000, True) == []


def test_daily_loss_and_flatten_time_flatten_the_book():
    e = engine(lambda md: {"AAPL": 0.2})
    feed(e, 1)
    [o] = e.tick(at(5.1), {"AAPL": 100}, 98_000, True)            # down 2% on the day
    assert (o["side"], o["qty"], o["reason"]) == ("sell", 100, "daily loss limit")
    late = engine(lambda md: {"AAPL": 0.2})
    t = dt.datetime(2026, 10, 5, 15, 55, 1, tzinfo=NY)
    late.on_message({"T": "t", "S": "AAPL", "p": 200.0, "s": 100, "t": t.isoformat()}, t)
    [o] = late.tick(t + dt.timedelta(seconds=5), {"AAPL": 50}, 100_000, True)
    assert o["side"] == "sell" and o["reason"] == "flatten time"


def test_kill_switch_flattens(monkeypatch):
    monkeypatch.setenv("STREAM_KILL", "1")
    e = engine(lambda md: {"AAPL": 0.2})
    feed(e, 1)
    [o] = e.tick(at(5.1), {"MSFT": 10}, 100_000, True)
    assert (o["symbol"], o["side"]) == ("MSFT", "sell")


def test_three_bad_decisions_stop_the_day():
    def broken(md):
        raise ValueError("boom")
    e = engine(broken)
    for k in range(3):
        feed(e, 1 + 5 * k)
        assert e.tick(at(5.1 + 5 * k), {}, 100_000, True) == []
    assert e.halted


def test_throttle_spaces_repeat_orders_per_symbol():
    w = iter([0.1, 0.2])
    e = engine(lambda md: {"AAPL": next(w)})
    feed(e, 1)
    assert len(e.tick(at(5.1), {}, 100_000, True)) == 1
    feed(e, 6)
    assert e.tick(at(10.1), {"AAPL": 50}, 100_000, True) == []     # 5 s later: too soon for AAPL again


def test_refuses_a_live_account():
    e = StreamEngine(["AAPL"], 5, lambda md: {}, FakeBroker(), LIMITS, STREAM, log=lambda r: None)
    with pytest.raises(Exception):
        e.start({**ACCOUNT, "account_number": "LIVE1"})
