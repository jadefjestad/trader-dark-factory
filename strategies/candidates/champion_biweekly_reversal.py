"""Hypothesis: the champion's residual-reversal sleeve trades weekly and drives most of its cost
(about 9x turnover a year). Rebalancing that sleeve every 10 bars instead of every 5 should cut its
trading costs roughly in half while keeping most of the reversal signal, lifting net validation
Sharpe.

One change versus residual_lowcorr_reversal (champion): reversal_every 5 -> 10. lookback is 545
instead of 520 so the 520-bar shortfall documented in strategies/candidates/README.md does not fail
lookback_sufficient. Row t uses closes up to bar t only.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ChampionBiweeklyReversal(Strategy):
    name = "champion_biweekly_reversal"
    lookback = 545
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60,
              "reversal_window": 21, "reversal_every": 10}

    def vol_scaled(self, picks, rets, every=None):
        p = self.params
        every = int(every or p["rebalance_every"])
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, every)):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, every).ffill().fillna(0.0)

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

    def reversal_sleeve(self, rets):
        p = self.params
        B, W, n = int(p["lookback"]), int(p["reversal_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(B, min_periods=B).cov(mkt).div(mkt.rolling(B, min_periods=B).var(), axis=0)
        resid = rets - beta.shift(W).mul(mkt, axis=0)
        win = resid.rolling(W, min_periods=W)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets, int(p["reversal_every"]))

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        w = (self.residual_sleeve(rets) + self.low_corr_sleeve(rets) + self.reversal_sleeve(rets)) / 3
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
