"""Hypothesis: post-earnings-announcement drift (Bernard and Thomas 1989). Prices under-react to
earnings news, so stocks whose latest quarterly EPS beat the same quarter a year earlier by the most,
relative to how noisy that change usually is, keep outperforming for weeks after the filing. The
factory's earnings candidates so far use the price reaction around the announcement; this one uses the
reported numbers themselves, through the point-in-time `eps_sue` panel (SEC EDGAR, first-filed values,
usable only from the bar the filing became public).

Hold the 8 large caps with the highest standardized unexpected earnings, equal weight, 10% vol target,
rebalanced weekly so new filings enter quickly. Row t uses closes and filings public by bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class SueDrift(Strategy):
    name = "sue_drift"
    lookback = 80
    extra_data = ("eps_sue",)
    params = {"top_n": 8, "rebalance_every": 5, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        score = md.extra["eps_sue"].reindex(columns=c.columns)
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
