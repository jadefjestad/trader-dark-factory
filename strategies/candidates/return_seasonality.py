"""Hypothesis: stocks tend to repeat their relative performance in the same calendar month across years
(Heston and Sadka 2008, "Seasonality in the cross-section of stock returns"), likely from recurring
flows such as earnings timing, dividends and fiscal-year rebalancing. Ranking large caps on how they did
over the coming 21 trading days in each of the past three years, and holding the top eight sized to a
10% volatility target and rebalanced monthly, should earn a positive validation Sharpe from a signal
unrelated to the momentum champion.

One change versus the factory's other candidates: the ranking signal is same-season past return.
Row t uses closes up to bar t only (the most recent price used is 231 bars old).
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ReturnSeasonality(Strategy):
    name = "return_seasonality"
    lookback = 780
    params = {"years": 3, "horizon": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        h, year = int(p["horizon"]), 252
        past = [c.shift(year * k - h) / c.shift(year * k) - 1 for k in range(1, int(p["years"]) + 1)]
        score = pd.concat(past).groupby(level=0).mean().reindex(c.index)
        rank = score.rank(axis=1, ascending=False, method="first")
        n = int(p["top_n"])
        w = equal_weight((rank <= n) & score.notna(), slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, int(p["rebalance_every"]))):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
