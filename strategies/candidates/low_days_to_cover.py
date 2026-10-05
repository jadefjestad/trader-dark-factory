"""Hypothesis (issue #65): stocks that short sellers find cheap to exit, low days to cover (short
interest over average daily volume), outperform crowded shorts. Hong, Li, Ni, Scheinkman and Sraer
(2016, "Days to cover and stock returns") find days to cover predicts returns better than short
interest alone. Holding the eight large caps with the lowest days to cover, sized to a 10% volatility
target and rebalanced monthly, should give a positive validation Sharpe from a signal the factory has
not used yet.

FINRA short interest is point-in-time: each settlement is usable only from the business day after
settlement plus seven business days (publication lag), via the short_interest_days panel.

One change versus the factory's other candidates: the ranking signal is days to cover.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowDaysToCover(Strategy):
    name = "low_days_to_cover"
    lookback = 80
    extra_data = ("short_interest_days",)
    params = {"top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        score = md.extra["short_interest_days"].reindex(columns=c.columns)
        rank = score.rank(axis=1, ascending=True, method="first")
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
