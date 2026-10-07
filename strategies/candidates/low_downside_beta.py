"""Hypothesis: what hurts investors is co-movement in falling markets, so downside beta (Ang, Chen and
Xing 2006, "Downside risk") separates defensive stocks better than full-sample beta. Among large caps,
holding the eight stocks with the lowest beta to the equal-weight universe measured only on days the
universe fell, over the last 252 days, sized to a 10% volatility target and rebalanced monthly, should
beat low_beta's validation Sharpe (PR #125: 1.03) with a smaller drawdown.

One change versus low_beta: beta is estimated on down-market days only.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowDownsideBeta(Strategy):
    name = "low_downside_beta"
    lookback = 300
    params = {"beta_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        L = int(p["beta_window"])
        down = mkt < 0
        mkt_d = mkt.where(down)
        rets_d = rets.where(down, axis=0)
        m = L // 4   # need at least ~63 down days in the window
        score = rets_d.rolling(L, min_periods=m).cov(mkt_d).div(mkt_d.rolling(L, min_periods=m).var(), axis=0)
        score = score.where(mkt.rolling(L, min_periods=L).count().ge(L), axis=0)
        rank = score.rank(axis=1, ascending=True, method="first")
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
