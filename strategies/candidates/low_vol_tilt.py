"""Hypothesis (issue #15): the low-volatility anomaly holds in large caps. Holding the 10 names with
the lowest 126-day realised volatility, inverse-volatility weighted and capped at 15% each (any excess
stays in cash), rebalanced monthly, beats the equal-weight champion's validation Sharpe (0.67) with
smaller drawdowns.

One change versus strategies/baselines/buy_hold.py: select and weight by low trailing volatility.
"""
import numpy as np

from strategies.base import Strategy, hold_between_rebalances


class LowVolTilt(Strategy):
    name = "low_vol_tilt"
    lookback = 140
    params = {"vol_window": 126, "n": 10, "cap": 0.15, "rebalance_every": 21}

    def target_weights(self, md):
        p = self.params
        c = md.close
        vol = c.pct_change().rolling(int(p["vol_window"]), min_periods=int(p["vol_window"])).std()
        rank = vol.rank(axis=1, ascending=True, method="first")
        inv = (1.0 / vol).where(rank <= int(p["n"]))
        w = inv.div(inv.sum(axis=1).replace(0, np.nan), axis=0).clip(upper=p["cap"]).fillna(0.0)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
