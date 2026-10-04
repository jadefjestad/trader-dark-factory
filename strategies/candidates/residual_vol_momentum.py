"""Hypothesis (issue #17): ranking on residual momentum (Blitz, Huij & Martens 2011), the 12-1 month
sum of each stock's returns after removing its rolling beta to the market, divided by the residuals'
volatility, avoids the beta-driven crashes of raw momentum. Swapping it into vol_target_momentum_10
(PR #19: validation Sharpe 0.94) raises validation Sharpe while keeping drawdown under 25%.
The market is the equal-weight universe (strategies don't see SPY).

One change versus vol_target_momentum_10: the ranking signal.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualVolMomentum(Strategy):
    name = "residual_vol_momentum"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        L, S = int(p["lookback"]), int(p["skip"])
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=False)
        w = equal_weight((rank <= int(p["top_n"])) & score.notna(), slots=int(p["top_n"]))
        vw = int(p["vol_window"])
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
