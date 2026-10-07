"""Hypothesis: the champion residual_lowcorr_blend (PR #132) holds two separate 8-name sleeves, so a
stock that is both a residual-momentum winner and weakly correlated with the market gets no extra
weight. Ranking every stock on the average of its two cross-sectional percentile ranks (residual
momentum high, correlation low) and holding the top 8 at a 10% vol target, rebalanced monthly,
should pick names strong on both traits and keep the blend's validation and holdout strength with
one concentrated book.

One change versus residual_lowcorr_blend: one composite ranking replaces the two 50/50 sleeves.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualLowCorrComposite(Strategy):
    name = "residual_lowcorr_composite"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60}

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

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        L, S, C, n = int(p["lookback"]), int(p["skip"]), int(p["corr_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        mom = win.sum() / win.std()
        corr = rets.rolling(C, min_periods=C).corr(mkt)
        score = (mom.rank(axis=1, pct=True) + (-corr).rank(axis=1, pct=True)) / 2
        score = score.where(mom.notna() & corr.notna())
        rank = score.rank(axis=1, ascending=False, method="first")
        w = self.vol_scaled((rank <= n) & score.notna(), rets)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
