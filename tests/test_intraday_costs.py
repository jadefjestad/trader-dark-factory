import numpy as np
import pandas as pd
import pytest

from factory import backtest, config, evaluate
from factory.data import synthetic


def _md():
    return synthetic(["AAA", "BBB"], start="2024-01-02", end="2024-01-10", timeframe="15Min")


def _flip(md):
    w = pd.DataFrame(0.0, index=md.index, columns=md.symbols)
    w.iloc[::2, 0] = 0.1          # trade every bar so costs dominate
    return w


def test_feed_mismatch_is_charged_per_side():
    md = _md()
    base = {"slippage_bps": 8, "half_spread_bps": 3}
    a = backtest.run(_flip(md), md, base)
    b = backtest.run(_flip(md), md, {**base, "feed_mismatch_bps": 5})
    assert np.allclose(b.costs, a.costs * 16 / 11)


def test_intraday_rules_carry_mismatch_and_stress_gate():
    cfg = config.evaluation()
    for tf in ("15Min", "5Min"):
        assert cfg["costs"][tf]["feed_mismatch_bps"] >= 4.7    # measured p95 gap, docs/intraday-data.md
    cs = cfg["gates"]["cost_stress"]
    assert "1Day" not in cs["timeframes"] and cs["multiple"] >= 2


def test_stressed_costs_scale_every_number():
    assert evaluate.stressed_costs({"slippage_bps": 8, "sell_fee_bps": 0.3, "note": "x"}, 2) == \
        {"slippage_bps": 16, "sell_fee_bps": 0.6, "note": "x"}


def test_cost_stress_sharpe_is_lower_than_base():
    md = _md()
    cfg = config.evaluation()
    pers = {"validation": (md.index[0], md.index[-1])}
    w = _flip(md)
    base = evaluate.metrics.summarize(evaluate.backtest_weights(w, md, cfg), *pers["validation"]).get("sharpe", 0.0)
    assert evaluate.cost_stress_sharpe(w, md, cfg, pers) < base


def test_impact_grows_with_participation():
    md = synthetic(["A", "B"], start="2026-01-05", end="2026-01-09", timeframe="15Min")
    w = pd.DataFrame(0.5, index=md.index, columns=md.symbols)
    base = {"slippage_bps": 8, "half_spread_bps": 3}
    cost = lambda c, cap: backtest.run(w, md, c, cap).costs.sum()
    with_impact = {**base, "impact_bps_per_sqrt_pct": 10}
    assert cost(with_impact, 1e5) > cost(base, 1e5)
    # the same weights on 100x the capital are a bigger share of each bar, so cost more per dollar
    assert cost(with_impact, 1e7) > cost(with_impact, 1e5)
    assert cost(base, 1e7) == pytest.approx(cost(base, 1e5))


def test_intraday_rules_charge_impact():
    cfg = config.evaluation()
    assert all(cfg["costs"][tf]["impact_bps_per_sqrt_pct"] > 0 for tf in ("15Min", "5Min"))
