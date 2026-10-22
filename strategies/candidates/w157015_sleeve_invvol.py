"""Champion sleeves combined with inverse-volatility sleeve weights instead of fixed 15/70/15.

The fixed split ignores that each sleeve's risk changes over time. Weighting each sleeve by the
inverse of its trailing 63-day realised volatility (risk parity across sleeves) leans toward
whichever sleeve is currently calmest. Weights are clipped to [0.10, 0.75] so no sleeve vanishes
and per-name weight stays under the position limit.

One change versus e126_wts_15_70_15: on each 21-day rebalance date, sleeve weights are set
proportional to 1 / (63-day volatility of that sleeve's daily return, using the previous day's
sleeve weights), clipped to [0.10, 0.75] and renormalised, then held until the next 21-day date.
Until 63 days of sleeve returns exist the weights are 15/70/15. lookback rises from 545 to 650 so the
sleeve-volatility window sees fully formed sleeves. Row t uses closes up to bar t only.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class W157015SleeveInvvol(Strategy):
    name = "w157015_sleeve_invvol"
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
        mix = mix.where(pd.Series(rebalance_mask(w_index := rets.index, int(p["rebalance_every"])), index=w_index), axis=0).ffill()
        mix = mix.fillna(pd.Series([0.15, 0.7, 0.15], index=mix.columns))
        w = sum(sleeves[k].mul(mix.iloc[:, k], axis=0) for k in range(3))
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
