"""Hypothesis: low_correlation (PR #131: validation Sharpe 1.12, the best single signal, holdout about
0.9) and the residual-momentum champion (validation 0.88, strong holdout) rank on unrelated traits.
Holding half the book in each, both rebalanced monthly at a 10% vol target, should combine the
validation strength of one with the holdout strength of the other, as the low-beta blend did (PR #126:
validation 1.05, holdout about 1.7), and beat it because correlation ranked better than beta alone.

Sleeve 1 is residual_vol_momentum unchanged; sleeve 2 is low_correlation unchanged. One change versus
residual_lowbeta_blend: the defensive sleeve ranks on correlation instead of beta.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualLowCorrBlend(Strategy):
    name = "residual_lowcorr_blend"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21,
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

    def residual_sleeve(self, rets):
        p = self.params
        L, S, n = int(p["lookback"]), int(p["skip"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=False)
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
        w = self.residual_sleeve(rets) * (1 - share) + self.low_corr_sleeve(rets) * share
        return hold_between_rebalances(w, int(p["rebalance_every"]))
