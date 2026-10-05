"""Hypothesis: anchoring makes investors slow to bid stocks through their 52-week high, so names
trading closest to that high keep outperforming (George and Hwang 2004, "The 52-week high and
momentum investing"). They report the effect explains most of classic momentum profits and does not
reverse. Holding the eight large caps whose close is nearest their trailing 252-day high, sized to a
10% volatility target and rebalanced monthly, should give a positive validation Sharpe from a
price signal the factory has not used.

One change versus the factory's other candidates: the ranking signal is close / 252-day high.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class Near52wHigh(Strategy):
    name = "near_52w_high"
    lookback = 260
    params = {"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        win = int(p["window"])
        score = c / c.rolling(win, min_periods=win).max()
        rank = score.rank(axis=1, ascending=False, method="first")
        n = int(p["top_n"])
        w = equal_weight((rank <= n) & score.notna(), slots=n)
        vw = int(p["vol_window"])
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
