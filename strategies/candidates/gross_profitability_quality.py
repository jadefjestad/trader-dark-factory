"""Hypothesis (issue #30): gross profitability, trailing-four-quarter gross profit over total assets
(Novy-Marx 2013, "The other side of value"), predicts returns as well as book-to-market and is nearly
uncorrelated with momentum. Holding the eight most profitable large caps, sized to a 10% volatility
target and rebalanced monthly, should give a positive validation Sharpe from a base signal the factory
has not used yet, which makes it a candidate sleeve for an ensemble with the momentum champion.

Fundamentals are point-in-time from SEC EDGAR: each value is usable only from the bar its 10-Q or
10-K was accepted, first-filed values only. Banks and card networks report no cost of revenue, so
they have no score and are never held.

One change versus the factory's other candidates: the ranking signal is a fundamental, not a price.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class GrossProfitabilityQuality(Strategy):
    name = "gross_profitability_quality"
    lookback = 80
    extra_data = ("gross_profitability",)
    params = {"top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        score = md.extra["gross_profitability"].reindex(columns=c.columns)
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
