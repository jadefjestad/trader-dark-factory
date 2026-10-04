"""Hypothesis (issue #7): the short_term_reversal baseline (validation Sharpe 0.47) gives equal weight to
every pick, so its most volatile losers dominate risk. Weighting picks by inverse 20-day volatility,
at the same total exposure, cuts that noise and raises validation Sharpe above the baseline.

One change versus short_term_reversal: inverse-volatility weights instead of equal weights
(each name capped at 15%, the risk limit).
"""
from strategies.base import Strategy, hold_between_rebalances


class InverseVolReversal(Strategy):
    name = "invvol_reversal"
    lookback = 210
    params = {"window": 5, "bottom_n": 8, "trend": 200, "rebalance_every": 5, "vol_window": 20}

    def target_weights(self, md):
        p = self.params
        c = md.close
        n = int(p["bottom_n"])
        ret = c / c.shift(int(p["window"])) - 1
        uptrend = c > c.rolling(int(p["trend"])).mean()
        rank = ret.where(uptrend).rank(axis=1, ascending=True)
        pick = (rank <= n).fillna(False)
        vol = c.pct_change().rolling(int(p["vol_window"]), min_periods=int(p["vol_window"])).std()
        inv = (1.0 / vol.where(vol > 0)).where(pick, 0.0).fillna(0.0)
        gross = pick.sum(axis=1) / n                      # same total exposure as equal weight with n slots
        w = inv.div(inv.sum(axis=1).where(lambda s: s > 0), axis=0).mul(gross, axis=0).fillna(0.0)
        return hold_between_rebalances(w.clip(upper=0.15), int(p["rebalance_every"]))
