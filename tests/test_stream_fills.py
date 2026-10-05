import datetime as dt

import pandas as pd
import pytest

from factory.stream.fills import fill_order, replay

T0 = pd.Timestamp("2026-10-05 14:30:00", tz="UTC")


def _quotes():
    rows = [  # time offset s, bid, ask, bid_size, ask_size
        (0.0, 99.0, 99.2, 5, 5),     # before the decision: must never be used
        (1.0, 99.9, 100.1, 2, 3),
        (1.5, 99.9, 100.1, 0, 0),    # empty
        (2.0, 100.0, 100.0, 4, 4),   # locked
        (3.0, 100.1, 100.3, 10, 10),
    ]
    return pd.DataFrame([{"time": T0 + pd.Timedelta(seconds=s), "symbol": "AAPL", "bid": b, "ask": a,
                          "bid_size": bs, "ask_size": as_} for s, b, a, bs, as_ in rows])


def test_buy_fills_at_ask_after_latency_and_walks_size():
    fills, left = fill_order(_quotes(), "AAPL", "buy", 5, T0, dt.timedelta(milliseconds=500))
    assert [(f.qty, f.price) for f in fills] == [(3, 100.1), (2, 100.3)] and left == 0


def test_sell_fills_at_bid():
    fills, left = fill_order(_quotes(), "AAPL", "sell", 2, T0, dt.timedelta(milliseconds=500))
    assert [(f.qty, f.price) for f in fills] == [(2, 99.9)] and left == 0


def test_no_quote_before_decision_plus_latency_is_used():
    # leakage test: shifting every quote earlier than decided_at + latency must never change a fill
    q = _quotes()
    for lat_s in (0.0, 0.5, 1.0, 2.5):
        first = T0 + pd.Timedelta(seconds=lat_s)
        fills, _ = fill_order(q, "AAPL", "buy", 50, T0, dt.timedelta(seconds=lat_s))
        assert all(f.quote_at >= first for f in fills)
        tampered = q.copy()
        early = tampered["time"] < first
        tampered.loc[early, ["bid", "ask"]] = [1.0, 1.01]   # absurd prices that would show if used
        assert fill_order(tampered, "AAPL", "buy", 50, T0, dt.timedelta(seconds=lat_s))[0] == fills


def test_partial_fill_reports_unfilled_after_max_wait():
    fills, left = fill_order(_quotes(), "AAPL", "buy", 50, T0, dt.timedelta(milliseconds=500),
                             max_wait=dt.timedelta(seconds=2))
    assert sum(f.qty for f in fills) == 3 and left == 47


def test_size_multiple_caps_each_quote():
    fills, _ = fill_order(_quotes(), "AAPL", "buy", 5, T0, dt.timedelta(milliseconds=500), max_size_multiple=0.5)
    assert [f.qty for f in fills] == [1.5, 3.5]


def test_bad_orders_raise():
    with pytest.raises(ValueError):
        fill_order(_quotes(), "AAPL", "hold", 1, T0, dt.timedelta(0))


def test_replay_summarises_each_order():
    orders = pd.DataFrame([{"time": T0, "symbol": "AAPL", "side": "buy", "qty": 5},
                           {"time": T0, "symbol": "MSFT", "side": "sell", "qty": 1}])
    out = replay(orders, _quotes(), dt.timedelta(milliseconds=500))
    a, m = out.iloc[0], out.iloc[1]
    assert a["filled"] == 5 and a["avg_price"] == pytest.approx((3 * 100.1 + 2 * 100.3) / 5) and a["delay_s"] == 3.0
    assert m["filled"] == 0 and m["unfilled"] == 1
