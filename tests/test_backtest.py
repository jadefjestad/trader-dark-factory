import numpy as np
import pandas as pd

from factory import backtest, metrics
from factory.data import synthetic

COSTS = {"slippage_bps": 5, "half_spread_bps": 2, "sell_fee_bps": 0.3}


def test_full_weight_tracks_open_to_open_minus_entry_cost():
    md = synthetic(["A", "B"], "2020-01-01", "2020-12-31")
    w = pd.DataFrame({"A": 1.0, "B": 0.0}, index=md.index)
    res = backtest.run(w, md, COSTS, 100_000)
    expected = 100_000 * (1 - 7e-4) * md.open["A"].iloc[-1] / md.open["A"].iloc[1]
    assert np.isclose(res.equity.iloc[-1], expected, rtol=1e-9)


def test_costs_reduce_returns():
    md = synthetic(["A", "B", "C"], "2020-01-01", "2021-12-31")
    rng = np.random.default_rng(0)
    w = pd.DataFrame(rng.dirichlet([1, 1, 1], len(md.index)) * 0.9, index=md.index, columns=md.symbols)
    free = backtest.run(w, md, {}, 100_000)
    costly = backtest.run(w, md, COSTS, 100_000)
    assert costly.equity.iloc[-1] < free.equity.iloc[-1]
    assert metrics.summarize(costly)["cost_drag"] > 0


def test_signal_on_last_bar_is_never_filled():
    md = synthetic(["A"], "2020-01-01", "2020-03-31")
    w = pd.DataFrame(0.0, index=md.index, columns=["A"])
    w.iloc[-1] = 1.0
    res = backtest.run(w, md, COSTS, 100_000)
    assert res.equity.iloc[-1] == 100_000


def test_intraday_is_flat_overnight():
    md = synthetic(["A"], "2024-01-01", "2024-01-10", timeframe="15Min")
    w = pd.DataFrame(1.0, index=md.index, columns=["A"])
    res = backtest.run(w, md, COSTS, 100_000)
    days = pd.Series(res.weights.index.date, index=res.weights.index)
    last_bars = days != days.shift(-1)
    assert (res.weights[last_bars.values] == 0).all().all()


def test_tiny_drift_trades_are_skipped():
    md = synthetic(["A", "B"], "2020-01-01", "2020-12-31")
    w = pd.DataFrame(0.5, index=md.index, columns=md.symbols)
    every_day = backtest.run(w, md, COSTS, 100_000)
    thresholded = backtest.run(w, md, COSTS, 100_000, min_trade_weight=0.01)
    assert thresholded.trades < every_day.trades / 3


def test_small_positions_still_flatten_at_session_end():
    md = synthetic(["A"], "2024-01-01", "2024-01-10", timeframe="15Min")
    bar = pd.Series(md.index.date, index=md.index).groupby(md.index.date).cumcount()
    w = pd.DataFrame({"A": (bar < 5).map({True: 0.03, False: 0.01}).values}, index=md.index)
    res = backtest.run(w, md, COSTS, 100_000, min_trade_weight=0.015)   # 0.01 left before the close
    assert (res.holdings["A"] > 0).any()
    days = pd.Series(res.holdings.index.date, index=res.holdings.index)
    last_bars = days != days.shift(-1)
    assert (res.holdings[last_bars.values] == 0).all().all()
