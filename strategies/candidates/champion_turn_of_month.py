"""Hypothesis: the turn-of-the-month effect (Ariel 1987; Lakonishok and Smidt 1988; McConnell and
Xu 2008): US equity returns are concentrated in the last few days of one month and the first few of
the next, when pension and payroll flows arrive. The champion residual_lowcorr_reversal (PR #137) is
equally exposed every day. Running it at full exposure only around month turns and at 60% otherwise
should keep most of the return while cutting risk, raising the Sharpe ratio.

One change versus residual_lowcorr_reversal: gross exposure is scaled to 0.6 except on calendar days
26-31 and 1-4. The window is fixed by the calendar date alone, so row t uses data up to bar t only.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ChampionTurnOfMonth(Strategy):
    name = "champion_turn_of_month"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "corr_window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60,
              "reversal_window": 21, "reversal_every": 5,
              "tom_start_day": 26, "tom_end_day": 4, "off_scale": 0.6}

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
        day = np.asarray(w.index.day)
        tom = (day >= int(p["tom_start_day"])) | (day <= int(p["tom_end_day"]))
        scale = np.where(tom, 1.0, float(p["off_scale"]))
        switch = np.r_[True, scale[1:] != scale[:-1]]
        keep = (rebalance_mask(w.index, int(p["rebalance_every"])) | rebalance_mask(w.index, int(p["reversal_every"]))
                | switch)
        w = w.fillna(0.0).mul(pd.Series(scale, index=w.index), axis=0)
        return w.where(pd.Series(keep, index=w.index), other=float("nan"), axis=0)
