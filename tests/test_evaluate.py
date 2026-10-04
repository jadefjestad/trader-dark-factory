import pandas as pd

from factory import evaluate
from factory.data import synthetic
from strategies.base import Strategy


class Cheater(Strategy):
    name = "cheater"
    lookback = 5
    params = {}

    def target_weights(self, md):
        tomorrow = md.open.shift(-2) / md.open.shift(-1) - 1     # peeks at the future
        best = tomorrow.rank(axis=1, ascending=False) <= 1
        return best.astype(float) * 0.1


class Honest(Strategy):
    name = "honest"
    lookback = 20
    params = {"window": 20}

    def target_weights(self, md):
        return (md.close > md.close.rolling(self.params["window"]).mean()).astype(float) * 0.1


def test_lookahead_detected():
    md = synthetic(["A", "B", "C"], "2020-01-01", "2021-12-31")
    s = Cheater()
    assert evaluate.causality_check(s, md, s.target_weights(md), 5)


def test_honest_strategy_passes_causality():
    md = synthetic(["A", "B", "C"], "2020-01-01", "2021-12-31")
    s = Honest()
    assert not evaluate.causality_check(s, md, s.target_weights(md), 5)


def test_weight_violations():
    limits = {"allow_short": False, "max_gross_exposure": 1.0, "max_position_weight": 0.15}
    w = pd.DataFrame({"A": [0.5, -0.1]})
    v = evaluate.weight_violations(w, limits)
    assert any("negative" in x for x in v) and any("position weight" in x for x in v)


def test_full_evaluation_on_synthetic_is_never_promotable():
    r = evaluate.evaluate("strategies/candidates/example_momentum_trend.py", "synthetic", "t", include_baselines=False)
    gates = {g["gate"]: g["passed"] for g in r["gates"]}
    assert gates["data_not_synthetic"] is False
    assert r["promote"] is False
    assert set(r["metrics"]["holdout"]) == {"sharpe", "max_drawdown"}   # holdout stays coarse
