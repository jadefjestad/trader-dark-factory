"""Hypothesis: overnight-return momentum (PR #115: validation Sharpe 0.84, in-sample 0.90, turnover 3x)
ranks stocks on a different part of each day's return than the residual-momentum champion (validation
0.88), which ranks on close-to-close residuals. If the two pick partly different names at different
times, holding half the book in each, both rebalanced monthly, should beat the champion's validation
Sharpe through diversification while keeping turnover low.

Sleeve 1 is residual_vol_momentum unchanged (monthly, 10% vol target); sleeve 2 is overnight_momentum
unchanged. One change versus the champion: half the capital moves to the overnight-momentum sleeve.
Row t uses opens and closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualOvernightBlend(Strategy):
    name = "residual_overnight_blend"
    lookback = 520
    params = {"lookback": 252, "skip": 21, "window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60, "overnight_share": 0.5}

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

    def overnight_sleeve(self, md, rets):
        p = self.params
        win, n = int(p["window"]), int(p["top_n"])
        score = np.log(md.open / md.close.shift(1)).rolling(win, min_periods=win).sum()
        rank = score.rank(axis=1, ascending=False, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        share = float(p["overnight_share"])
        w = self.residual_sleeve(rets) * (1 - share) + self.overnight_sleeve(md, rets) * share
        return hold_between_rebalances(w, int(p["rebalance_every"]))
