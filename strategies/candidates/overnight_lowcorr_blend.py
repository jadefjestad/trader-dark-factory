"""Hypothesis: the champion residual_lowcorr_blend (PR #132) pairs low correlation with residual
momentum. Overnight momentum (PR #115: validation 0.84, holdout about 1.2, 252-day sum of
close-to-open log returns) is a different return source from both. Pairing it with low correlation
50/50, each sleeve top 8 at a 10% vol target rebalanced monthly, tests whether the defensive sleeve
combines better with overnight momentum than with residual momentum.

One change versus residual_lowcorr_blend: the momentum sleeve ranks on 252-day overnight returns.
Row t uses opens and closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class OvernightLowCorrBlend(Strategy):
    name = "overnight_lowcorr_blend"
    lookback = 520
    params = {"window": 252, "corr_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60, "low_corr_share": 0.5}

    def vol_scaled(self, picks, rets):
        p = self.params
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, int(p["rebalance_every"]))):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"])).ffill().fillna(0.0)

    def overnight_sleeve(self, md, rets):
        p = self.params
        win, n = int(p["window"]), int(p["top_n"])
        overnight = np.log(md.open / md.close.shift(1))
        score = overnight.rolling(win, min_periods=win).sum()
        rank = score.rank(axis=1, ascending=False, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def low_corr_sleeve(self, rets):
        p = self.params
        L, n = int(p["corr_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        score = rets.rolling(L, min_periods=L).corr(mkt)
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        share = float(p["low_corr_share"])
        w = self.overnight_sleeve(md, rets) * (1 - share) + self.low_corr_sleeve(rets) * share
        return hold_between_rebalances(w, int(p["rebalance_every"]))
