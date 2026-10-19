"""Champion (15/70/15) with inverse-volatility weights in the low-corr sleeve.

The low-corr sleeve equal-weights its 7 picks, so its most volatile name drives the
sleeve's risk and its 126-day hold. Weighting picks by 1/63-day volatility spreads risk
more evenly; each pick is capped at 15% of the sleeve, leftover stays in cash.

One change versus e126_wts_15_70_15: low-corr picks are weighted by inverse 63-day
volatility (capped at 0.15 each) before the same vol-target scaling.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class W157015LowcorrInvvol(Strategy):
    name = "w157015_lowcorr_invvol"
    lookback = 545
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 20,
              "reversal_window": 21, "reversal_every": 5}

    def vol_scaled(self, picks, rets, every=None, base=None):
        p = self.params
        every = int(every or p["rebalance_every"])
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n) if base is None else base
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
        down = mkt < -0.005
        score = rets.where(down, axis=0).rolling(L, min_periods=L // 4).corr(mkt.where(down))
        rank = score.rank(axis=1, ascending=True, method="first")
        picks = (rank <= n) & score.notna()
        inv = 1.0 / rets.rolling(63, min_periods=63).std()
        raw = inv.where(picks).fillna(0.0)
        base = raw.div(raw.sum(axis=1).replace(0.0, np.nan), axis=0).fillna(0.0).clip(upper=0.15)
        return self.vol_scaled(picks, rets, 126, base=base)

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
        w = 0.15 * self.residual_sleeve(rets) + 0.7 * self.low_corr_sleeve(rets) + 0.15 * self.reversal_sleeve(rets)
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
