import datetime as dt

import numpy as np
import pandas as pd

from factory.stream.replay import replay

T0 = pd.Timestamp("2026-10-05 14:00:00", tz="UTC")       # 10:00 New York
LIMITS = {"paper_only": True, "trading_enabled": True, "allow_short": False, "min_order_notional": 50,
          "cash_buffer": 0.0}
STREAM = {"max_gross_exposure": 0.5, "max_position_weight": 0.25, "max_orders_per_minute": 30,
          "max_orders_per_day": 500, "min_seconds_between_trades_per_symbol": 30, "max_daily_loss": 0.5,
          "max_stream_gap_seconds": 30, "flatten_at": "15:55"}


def _tape(n=120, drift=0.01):
    """One AAPL trade and quote a second, price rising `drift` per second, spread 2 cents."""
    times = [T0 + pd.Timedelta(seconds=s) for s in range(n)]
    px = 100 + drift * np.arange(n)
    trades = pd.DataFrame({"time": times, "symbol": "AAPL", "price": px, "size": 100.0})
    quotes = pd.DataFrame({"time": [t + pd.Timedelta(milliseconds=500) for t in times], "symbol": "AAPL",
                           "bid": px - 0.01, "ask": px + 0.01, "bid_size": 50.0, "ask_size": 50.0})
    return trades, quotes


def test_buy_and_hold_fills_at_the_ask_after_latency_and_profits():
    trades, quotes = _tape()
    out = replay(trades, quotes, lambda md: {"AAPL": 0.25}, ["AAPL"], 5, LIMITS, STREAM,
                 latency=dt.timedelta(seconds=1))
    f = out["fills"]
    first = f.iloc[0]
    assert first["side"] == "buy" and f[f["decided_at"] == first["decided_at"]]["qty"].sum() == 249
    assert len(f[f["decided_at"] == first["decided_at"]]) == 5       # 50 shares a quote: walks five quotes
    assert first["time"] >= first["decided_at"] + pd.Timedelta(seconds=1)
    q = quotes.set_index("time").loc[first["time"]]
    assert first["price"] == q["ask"]
    assert out["equity"].iloc[-1] > 100_000


def test_strategy_never_sees_a_bar_before_it_closes():
    trades, quotes = _tape(60)
    seen = []

    def decide(md):
        seen.append(md.close.index.max())
        return {"AAPL": 0.1}
    out = replay(trades, quotes, decide, ["AAPL"], 5, LIMITS, STREAM)
    # the first decision came at the tick a bar closed, and its latest bar ended no later than that tick
    first = out["fills"]["decided_at"].min()
    assert seen[0] <= first and seen[0] == T0 + pd.Timedelta(seconds=5)


def test_kill_switch_means_no_buys():
    trades, quotes = _tape(60)
    out = replay(trades, quotes, lambda md: {"AAPL": 0.25}, ["AAPL"], 5, {**LIMITS, "trading_enabled": False}, STREAM)
    assert out["fills"].empty and out["equity"].iloc[-1] == 100_000


def test_thin_quotes_leave_unfilled_size():
    trades, quotes = _tape(40)
    quotes["ask_size"] = 1.0
    out = replay(trades, quotes, lambda md: {"AAPL": 0.25}, ["AAPL"], 5, LIMITS, STREAM,
                 max_wait=dt.timedelta(seconds=2))
    assert not out["unfilled"].empty


def test_probe_buys_then_sells_and_cost_is_measured():
    from factory.stream.replay import cost_bps, probe_strategy, summarize
    trades, quotes = _tape(240, drift=0.0)
    half = T0 + pd.Timedelta(seconds=120)
    out = replay(trades, quotes, probe_strategy(["AAPL"], half), ["AAPL"], 5, LIMITS, STREAM)
    sides = set(out["fills"]["side"])
    assert sides == {"buy", "sell"}
    c = cost_bps(out["fills"])
    assert (c > 0).all() and abs(c.median() - 1.0) < 0.01     # 1 cent half-spread on $100 = 1 bp
    s = summarize(out, 100_000.0)
    assert s["fills"] == len(out["fills"]) and s["cost_bps_median"] == round(float(c.median()), 2)


def test_main_fails_closed_without_data(monkeypatch, capsys):
    from factory.stream import history, replay as R
    monkeypatch.setattr(history, "fetch", lambda *a, **k: (_ for _ in ()).throw(history.DataError("401")))
    assert R.main(["--day", "2026-10-02"]) == 1
    assert "::error" in capsys.readouterr().out
