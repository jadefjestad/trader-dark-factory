"""Champion with a longer 378-bar down-day correlation window in the low-corr sleeve.

gpfilter_lowcorr_blendwin (#402) mixed in a 126-bar window and lost validation Sharpe (1.83 vs 2.21):
shorter windows add noise to the down-day correlation estimate. On an older base, downside_corr378
edged out the 252-bar window in validation (1.44 vs 1.42). Down days are only a fraction of bars, so
a longer window should give a steadier estimate of which names stay apart from the market in selloffs.

One change versus gpfilter_wts_10_80_10 (champion): corr_window 378 instead of 252 (min_periods stays
corr_window // 4). lookback stays 545, which covers 378 bars plus the vol window.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class GpfilterCorr378(Strategy):
    name = "gpfilter_corr378"
    lookback = 545
    extra_data = ("gross_profitability",)
    params = {"lookback": 252, "skip": 21, "corr_window": 378, "top_n": 7, "rebalance_every": 21,
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

    def low_corr_sleeve(self, md, rets):
        p = self.params
        L, n = int(p["corr_window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        down = mkt < -0.005
        score = rets.where(down, axis=0).rolling(L, min_periods=L // 4).corr(mkt.where(down))
        gp = md.extra["gross_profitability"].reindex(index=rets.index, columns=rets.columns)
        score = score.where(~(gp.rank(axis=1, pct=True) <= 1 / 3))
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
        w = 0.10 * self.residual_sleeve(rets) + 0.8 * self.low_corr_sleeve(md, rets) + 0.10 * self.reversal_sleeve(rets)
        keep = rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
        return w.fillna(0.0).where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
