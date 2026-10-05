"""Hypothesis: overnight returns (previous close to today's open) are persistent across stocks, while
intraday returns are not (Lou, Polk and Skouras 2019, "A tug of war: overnight versus intraday
expected returns"). Investors who trade at the open keep bidding the same names, so a stock's past
year of overnight returns predicts its next month. Holding the eight large caps with the highest
trailing 252-day overnight return, sized to a 10% volatility target and rebalanced monthly, should
give a positive validation Sharpe from a signal the factory has not used (it splits each day's
return, where every other candidate uses close to close).

One change versus the factory's other candidates: the ranking signal is cumulative overnight return.
Row t uses opens and closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class OvernightMomentum(Strategy):
    name = "overnight_momentum"
    lookback = 260
    params = {"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c, o = md.close, md.open
        rets = c.pct_change()
        win = int(p["window"])
        overnight = np.log(o / c.shift(1))
        score = overnight.rolling(win, min_periods=win).sum()
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
