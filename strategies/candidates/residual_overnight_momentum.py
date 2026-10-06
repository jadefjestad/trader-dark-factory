"""Hypothesis: overnight_momentum (PR #115: validation Sharpe 0.84) ranks on raw overnight returns, so
high-beta names win whenever the market gaps up overnight. Removing each stock's rolling beta to the
equal-weight market's overnight return, as the champion does for close-to-close returns, should isolate
the persistent stock-specific overnight demand that Lou, Polk and Skouras (2019) describe and raise
validation Sharpe.

One change versus overnight_momentum: the score sums beta-adjusted (residual) overnight returns.
Row t uses opens and closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualOvernightMomentum(Strategy):
    name = "residual_overnight_momentum"
    lookback = 520
    params = {"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c, o = md.close, md.open
        rets = c.pct_change()
        win = int(p["window"])
        overnight = np.log(o / c.shift(1))
        mkt = overnight.mean(axis=1)
        beta = overnight.rolling(win, min_periods=win).cov(mkt).div(mkt.rolling(win, min_periods=win).var(), axis=0)
        resid = overnight - beta.mul(mkt, axis=0)
        score = resid.rolling(win, min_periods=win).sum()
        rank = score.rank(axis=1, ascending=False, method="first")
        n = int(p["top_n"])
        w = equal_weight((rank <= n) & score.notna(), slots=n)
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
