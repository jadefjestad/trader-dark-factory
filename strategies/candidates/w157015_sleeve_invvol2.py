"""Inverse-volatility sleeve weights, fixed so the weights always sum to one.

w157015_sleeve_invvol (PR #333) was rejected on risk limits (gross 1.235, position 0.164): when one
sleeve had zero trailing volatility its inverse was NaN, the other two were normalised to one, and
the 15/70/15 fallback then filled only the missing column, so weights summed above one. Here a row
uses the 15/70/15 fallback as a whole whenever any sleeve's volatility is missing or zero.

Same idea as PR #333 versus e126_wts_15_70_15: on each 21-day rebalance date, sleeve weights are
proportional to 1 / (63-day volatility of that sleeve's daily return), clipped to [0.10, 0.75] and
renormalised, then held until the next 21-day date. Weights always sum to one, so gross exposure and
per-name weight stay within the champion's bounds. lookback 650. Row t uses closes up to bar t only.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class W157015SleeveInvvol2(Strategy):
    name = "w157015_sleeve_invvol2"
    lookback = 650
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 20,
              "reversal_window": 21, "reversal_every": 5}

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
        down = mkt < -0.005
        score = rets.where(down, axis=0).rolling(L, min_periods=L // 4).corr(mkt.where(down))
        rank = score.rank(axis=1, ascending=True, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets, 126)

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
        sleeves = [self.residual_sleeve(rets), self.low_corr_sleeve(rets), self.reversal_sleeve(rets)]
        sleeve_rets = pd.concat([(sl.shift(1) * rets).sum(axis=1, min_count=1) for sl in sleeves], axis=1)
        inv = 1.0 / sleeve_rets.rolling(63, min_periods=63).std().replace(0.0, np.nan)
        mix = inv.div(inv.sum(axis=1), axis=0).clip(0.10, 0.75)
        mix = mix.div(mix.sum(axis=1), axis=0)
        fallback = pd.DataFrame([[0.15, 0.7, 0.15]], index=mix.index, columns=mix.columns)
        mix = mix.where(mix.notna().all(axis=1), fallback, axis=0)
        on_rebalance = pd.Series(rebalance_mask(rets.index, int(p["rebalance_every"])), index=rets.index)
        mix = mix.where(on_rebalance, axis=0).ffill().fillna(fallback)
        w = sum(sleeves[k].mul(mix.iloc[:, k], axis=0) for k in range(3))
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
