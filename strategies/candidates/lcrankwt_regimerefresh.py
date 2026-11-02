"""Champion invvolresid_lcrankwt with low-corr picks refreshed when the market regime flips.

One change: the low-corr sleeve still re-picks on its 126-bar calendar, and now also re-picks
(names, inverse-vol rank weights and basket vol target) on any bar where the calm flag (fewer than
a quarter of the last 252 bars were market down days) changes value, so a sleeve picked in calm
markets is rebuilt from the latest downside correlations when stress starts, and vice versa.
Everything else is unchanged.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LcRankWtRegimeRefresh(Strategy):
    name = "lcrankwt_regimerefresh"
    lookback = 545
    extra_data = ("gross_profitability",)
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 7, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 20,
              "reversal_window": 21, "reversal_every": 5}

    def vol_scaled(self, picks, rets, every=None, mask=None):
        p = self.params
        every = int(every or p["rebalance_every"])
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(p["vol_window"])
        m = rebalance_mask(w.index, every) if mask is None else mask
        for i in np.flatnonzero(m):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return w.where(pd.Series(m, index=w.index), other=float("nan"), axis=0).ffill().fillna(0.0)

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
        calm = pd.Series(down.astype(float).rolling(L, min_periods=L).sum() < L // 4, index=rets.index)
        m = rebalance_mask(rets.index, 126) | (calm != calm.shift(1)).to_numpy()
        m[0] = True
        w = self.vol_scaled((rank <= n) & score.notna(), rets, 126, mask=m)
        iv = (1.0 / rets.rolling(63, min_periods=63).std()).where(w > 0)
        iv = iv * (n + 1 - rank).where(w > 0)
        scale = iv.div(iv.mean(axis=1), axis=0)
        scale = scale.fillna(0.0).where(pd.Series(m, index=scale.index), other=float("nan"), axis=0)
        scale = scale.ffill().fillna(0.0)
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
