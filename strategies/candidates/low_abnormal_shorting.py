"""Hypothesis (issue #65): heavy short selling predicts lower returns (Boehmer, Jones and Zhang 2008;
Boehmer, Huszar and Jordan 2010). FINRA's daily short-volume ratio is noisy in level (market makers
short to fill buy orders), so the signal is *abnormal* shorting: each stock's 20-day mean ratio minus
its own 250-day mean, scaled by the 250-day standard deviation. Monthly, hold the 8 names with the least
abnormal shorting, vol-targeted to 10% like the champion. Until enough FINRA history exists (data
starts 2019) it holds the equal-weight universe, so in-sample mostly measures the fallback.

One measurable change: a new base signal (abnormal short-volume ratio), not a filter on the champion.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowAbnormalShorting(Strategy):
    name = "low_abnormal_shorting"
    lookback = 320          # 250-day baseline + 20-day signal + 60-day vol window, with margin
    extra_data = ("short_volume_ratio",)
    params = {"signal_days": 20, "baseline_days": 250, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        svr = md.extra["short_volume_ratio"].reindex_like(c)
        B, s = int(p["baseline_days"]), int(p["signal_days"])
        recent = svr.rolling(s, min_periods=s).mean()
        base = svr.rolling(B, min_periods=B).mean()
        spread = svr.rolling(B, min_periods=B).std()
        z = (recent - base) / spread.where(spread > 0)
        n = int(p["top_n"])
        rank = z.rank(axis=1, ascending=True, method="first")
        picked = equal_weight((rank <= n) & z.notna(), slots=n)
        enough = z.notna().sum(axis=1) >= 2 * n
        fallback = equal_weight(c.notna())
        w = picked.where(enough, fallback, axis=0)
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
