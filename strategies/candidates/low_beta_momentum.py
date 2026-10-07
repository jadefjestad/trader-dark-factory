"""Hypothesis: low_beta (PR #125: validation Sharpe 1.03, in-sample 1.23) holds the eight lowest-beta
large caps regardless of trend, so it can own defensive names that are falling. Taking the sixteen
lowest-beta stocks and keeping the eight with the best 12-1 month return, sized to a 10% volatility
target and rebalanced monthly, should keep the low-beta premium while avoiding losers, raising the
validation Sharpe above low_beta's.

One change versus low_beta: a 12-1 momentum screen picks 8 of the 16 lowest-beta names.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowBetaMomentum(Strategy):
    name = "low_beta_momentum"
    lookback = 300
    params = {"beta_window": 252, "pool": 16, "mom_lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        L = int(p["beta_window"])
        score = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        rank = score.rank(axis=1, ascending=True, method="first")
        pool = (rank <= int(p["pool"])) & score.notna()
        mom = c.shift(int(p["skip"])) / c.shift(int(p["mom_lookback"])) - 1
        mom_rank = mom.where(pool).rank(axis=1, ascending=False, method="first")
        n = int(p["top_n"])
        w = equal_weight((mom_rank <= n) & pool & mom.notna(), slots=n)
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
