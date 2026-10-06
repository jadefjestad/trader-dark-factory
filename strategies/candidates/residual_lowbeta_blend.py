"""Hypothesis: low_beta (PR #125: validation Sharpe 1.03, in-sample 1.23, drawdown 7%, turnover 1.4x)
and the residual-momentum champion (validation 0.88) rank on unrelated traits: one on how little a stock
moves with the market, the other on its market-neutral trend. Holding half the book in each, both
rebalanced monthly at a 10% vol target, should diversify the champion and beat its validation Sharpe.

Sleeve 1 is residual_vol_momentum unchanged; sleeve 2 is low_beta unchanged. One change versus the
champion: half the capital moves to the low-beta sleeve.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualLowBetaBlend(Strategy):
    name = "residual_lowbeta_blend"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "beta_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60, "low_beta_share": 0.5}

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

    def low_beta_sleeve(self, rets):
        p = self.params
        L, n = int(p["beta_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        score = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        share = float(p["low_beta_share"])
        w = self.residual_sleeve(rets) * (1 - share) + self.low_beta_sleeve(rets) * share
        return hold_between_rebalances(w, int(p["rebalance_every"]))
