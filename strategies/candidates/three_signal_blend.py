"""Hypothesis: three signals that passed every gate on their own rank stocks on unrelated information:
residual momentum (champion, validation Sharpe 0.88), overnight-return momentum (PR #115, 0.84) and
same-season return seasonality (PR #119, 0.72). The 50/50 residual + overnight blend (PR #117) reached
0.89 with the lowest validation drawdown so far (8.6%). Adding seasonality as a third equal sleeve
should diversify further and lift validation Sharpe past the champion by the promotion margin.

Each sleeve is unchanged (top 8, 10% vol target, monthly). One change versus PR #117: capital is split
in thirds and the seasonality sleeve is added.
Row t uses opens and closes up to bar t only.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ThreeSignalBlend(Strategy):
    name = "three_signal_blend"
    lookback = 780
    params = {"lookback": 252, "skip": 21, "window": 252, "top_n": 8, "rebalance_every": 21,
              "vol_target": 0.10, "vol_window": 60, "years": 3, "horizon": 21}

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

    def seasonal_sleeve(self, md, rets):
        p = self.params
        c, h, n = md.close, int(p["horizon"]), int(p["top_n"])
        past = [c.shift(252 * k - h) / c.shift(252 * k) - 1 for k in range(1, int(p["years"]) + 1)]
        score = pd.concat(past).groupby(level=0).mean().reindex(c.index)
        rank = score.rank(axis=1, ascending=False, method="first")
        return self.vol_scaled((rank <= n) & score.notna(), rets)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        w = (self.residual_sleeve(rets) + self.overnight_sleeve(md, rets) + self.seasonal_sleeve(md, rets)) / 3
        return hold_between_rebalances(w, int(p["rebalance_every"]))
