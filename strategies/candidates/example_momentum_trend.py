"""Example candidate (hand-written seed): 12-1 momentum, but only names above their 200-day SMA,
and hold cash when SPY-like breadth is weak (fewer than half the universe in an uptrend)."""
from strategies.base import Strategy, equal_weight, hold_between_rebalances


class MomentumWithTrendFilter(Strategy):
    name = "momentum_trend_filter"
    lookback = 260
    params = {"lookback": 252, "skip": 21, "top_n": 8, "trend": 200, "breadth": 0.5, "rebalance_every": 21}

    def target_weights(self, md):
        p = self.params
        c = md.close
        mom = c.shift(int(p["skip"])) / c.shift(int(p["lookback"])) - 1
        up = c > c.rolling(int(p["trend"])).mean()
        rank = mom.where(up).rank(axis=1, ascending=False)
        w = equal_weight(rank <= int(p["top_n"]), slots=int(p["top_n"]))
        breadth_ok = up.mean(axis=1) >= p["breadth"]
        w = w.mul(breadth_ok.astype(float), axis=0)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
