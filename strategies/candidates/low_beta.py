"""Hypothesis: leverage-constrained investors bid up high-beta stocks, so low-beta stocks earn higher
risk-adjusted returns (Frazzini and Pedersen 2014, "Betting against beta"). Among large caps, holding
the eight stocks with the lowest 252-day beta to the equal-weight universe, sized to a 10% volatility
target and rebalanced monthly, should earn a positive validation Sharpe. Beta measures co-movement with
the market rather than total volatility, so it differs from low_vol_tilt.

One change versus the factory's other candidates: the ranking signal is the trailing market beta,
lowest first.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowBeta(Strategy):
    name = "low_beta"
    lookback = 300
    params = {"beta_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        L = int(p["beta_window"])
        score = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
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
