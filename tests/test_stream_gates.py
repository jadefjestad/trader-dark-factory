import pandas as pd

from factory import config, evaluate
from factory.data import synthetic


def _md():
    return synthetic(["AAA", "BBB"], start="2024-01-02", end="2024-01-12", timeframe="15Min")


def test_stream_gates_configured_for_intraday_only():
    g = config.evaluation()["gates"]
    for name in ("latency_robustness", "order_budget"):
        assert "1Day" not in g[name]["timeframes"] and "15Min" in g[name]["timeframes"]
    assert g["latency_robustness"]["delay_bars"] >= 1


def test_latency_hurts_a_strategy_that_knows_the_next_bar():
    md = _md()
    cfg = config.evaluation()
    pers = {"validation": (md.index[0], md.index[-1])}
    nxt = md.open.shift(-2) / md.open.shift(-1) - 1     # the return of the bar the decision fills into
    w = (nxt > 0).astype(float) * 0.1
    base = evaluate.metrics.summarize(evaluate.backtest_weights(w, md, cfg), *pers["validation"])["sharpe"]
    assert base > 0 and evaluate.latency_sharpe(w, md, cfg, pers) < base


def test_order_budget_counts_orders_per_bar_and_day():
    idx = pd.date_range("2026-10-01 09:45", periods=4, freq="15min").append(
        pd.date_range("2026-10-02 09:45", periods=2, freq="15min"))
    res = type("R", (), {"fills": pd.Series([0, 3, 2, 1, 5, 0], idx)})()
    ok, detail = evaluate.order_budget(res, {"max_orders_per_minute": 5, "max_orders_per_day": 10})
    assert ok and "peak 5 orders" in detail and "peak 6 a day" in detail
    assert not evaluate.order_budget(res, {"max_orders_per_minute": 4, "max_orders_per_day": 10})[0]
    assert not evaluate.order_budget(res, {"max_orders_per_minute": 5, "max_orders_per_day": 5})[0]


def test_order_budget_uses_the_protected_stream_limits():
    stream = config.risk_limits()["stream"]
    assert stream["max_orders_per_minute"] > 0 and stream["max_orders_per_day"] > 0
