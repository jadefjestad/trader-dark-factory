"""Hypothesis (issue #14): ranking by closeness to the 52-week high (George & Hwang 2004) instead of
12-1 return selects steadier winners with less crash risk. Top 8 by close / 252-day max close,
monthly rebalance, gives validation Sharpe at or above the momentum baseline (0.91) with in-sample
max drawdown under 25%.

One change versus strategies/baselines/momentum.py: the ranking signal.
"""
from strategies.base import Strategy, equal_weight, hold_between_rebalances


class High52Momentum(Strategy):
    name = "high52_momentum"
    lookback = 260
    params = {"window": 252, "top_n": 8, "rebalance_every": 21}

    def target_weights(self, md):
        p = self.params
        c = md.close
        hi = c.rolling(int(p["window"]), min_periods=int(p["window"])).max()
        score = c / hi
        rank = score.rank(axis=1, ascending=False, method="first")
        w = equal_weight((rank <= int(p["top_n"])) & score.notna(), slots=int(p["top_n"]))
        return hold_between_rebalances(w, int(p["rebalance_every"]))
