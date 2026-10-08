"""Hypothesis: stocks whose recent trading activity has dropped well below their own norm are being
neglected; attention-driven buyers have moved on, so prices sit below fair value and drift up as
attention returns (Gervais, Kaniel and Mingelgrin's high-volume return premium, read in reverse, and
Lee and Swaminathan's low-volume value effect). High abnormal volume marks glamour names that tend
to underperform. Buy the 8 large caps with the lowest abnormal dollar volume.

Signal: mean log dollar volume over the last 21 days minus its mean over the last 252 days.
Monthly rebalance, equal weight, 10% vol target. Row t uses closes and volumes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowAbnormalVolume(Strategy):
    name = "low_abnormal_volume"
    lookback = 300
    params = {"short_window": 21, "long_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        logdv = np.log((c * md.volume).where(md.volume > 0))
        S, L = int(p["short_window"]), int(p["long_window"])
        score = logdv.rolling(S, min_periods=S).mean() - logdv.rolling(L, min_periods=L).mean()
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
