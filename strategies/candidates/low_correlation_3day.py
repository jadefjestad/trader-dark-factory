"""Hypothesis: low_correlation (PR #131, validation 1.12) ranks on the 252-day correlation of daily
returns with the equal-weight market. Daily correlations are understated for stocks that react to
market news with a lag, so some "low-correlation" picks are just slow. Frazzini and Pedersen (2014)
estimate correlation from overlapping 3-day log returns over a longer window for this reason.
Ranking on the 504-day correlation of 3-day returns should pick stocks that are truly less tied to
the market and keep the defensive edge with a steadier signal.

One change versus low_correlation: correlation of overlapping 3-day log returns over 504 days.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowCorrelation3Day(Strategy):
    name = "low_correlation_3day"
    lookback = 520
    params = {"corr_window": 504, "horizon": 3, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        L = int(p["corr_window"])
        logr = np.log1p(rets)
        H = int(p["horizon"])
        r3 = logr.rolling(H, min_periods=H).sum()
        m3 = logr.mean(axis=1).rolling(H, min_periods=H).sum()
        score = r3.rolling(L, min_periods=L).corr(m3)
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
