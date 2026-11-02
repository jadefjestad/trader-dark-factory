"""Champion invvolresid_lcrankwt with a 63-bar basket-vol window for the low-corr sleeve.

One change: when the low-corr sleeve scales its basket to the 10% vol target at each 126-bar
rebalance, basket volatility is measured over the last 63 bars instead of 20, so one quiet or
noisy month does not set the sleeve size for half a year. The residual and reversal sleeves keep
the 20-bar window. Everything else is unchanged.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LcRankWtLcVw63(Strategy):
    name = "lcrankwt_lcvw63"
    lookback = 545
    extra_data = ("gross_profitability",)
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 20,
              "reversal_window": 21, "reversal_every": 5}

    def vol_scaled(self, picks, rets, every=None, vw=None):
        p = self.params
        every = int(every or p["rebalance_every"])
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(vw or p["vol_window"])
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
        C = int(p["corr_window"])
        calm = (mkt < -0.005).astype(float).rolling(C, min_periods=C).sum() < C // 4
        picks = (rank <= n) & score.notna()
        w = self.vol_scaled(picks & calm.to_numpy()[:, None], rets)
        every = int(p["rebalance_every"])
        iv = (1.0 / rets.rolling(63, min_periods=63).std()).where(w > 0)
        scale = iv.div(iv.mean(axis=1), axis=0)
        scale = hold_between_rebalances(scale, every).ffill().fillna(0.0)
        return (w * scale).clip(upper=0.15)

    def low_corr_sleeve(self, md, rets):
        p = self.params
        L, n = int(p["corr_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        down = mkt < -0.005
        score = rets.where(down, axis=0).rolling(L, min_periods=L // 4).corr(mkt.where(down))
        gp = md.extra["gross_profitability"].reindex(index=rets.index, columns=rets.columns)
        score = score.where(~(gp.rank(axis=1, pct=True) <= 1 / 3))
        rank = score.rank(axis=1, ascending=True, method="first")
        w = self.vol_scaled((rank <= n) & score.notna(), rets, 126, vw=63)
        iv = (1.0 / rets.rolling(63, min_periods=63).std()).where(w > 0)
        iv = iv * (n + 1 - rank).where(w > 0)
        scale = iv.div(iv.mean(axis=1), axis=0)
        scale = hold_between_rebalances(scale, 126).ffill().fillna(0.0)
        return (w * scale).clip(upper=0.15)

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
        C = int(p["corr_window"])
        calm = (rets.mean(axis=1) < -0.005).astype(float).rolling(C, min_periods=C).sum() < C // 4
        lc_wt = pd.Series(np.where(calm, 0.8, 0.9), index=rets.index)
        lc = self.low_corr_sleeve(md, rets).mul(lc_wt, axis=0)
        w = 0.10 * self.residual_sleeve(rets) + lc + 0.10 * self.reversal_sleeve(rets)
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
