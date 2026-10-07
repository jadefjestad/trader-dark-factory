"""Hypothesis: the low-beta premium (PR #125: validation Sharpe 1.03) comes mostly from correlation, not
volatility (Asness, Frazzini, Gormsen and Pedersen 2020, "Betting against correlation"). Among large
caps, holding the eight stocks with the lowest 252-day correlation to the equal-weight universe, sized
to a 10% volatility target and rebalanced monthly, should earn a validation Sharpe at least as high as
low_beta's, since beta mixes correlation with relative volatility.

One change versus low_beta: the ranking signal is trailing correlation to the market instead of beta.
Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class LowCorrelation(Strategy):
    name = "low_correlation"
    lookback = 300
    params = {"corr_window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        L = int(p["corr_window"])
        score = rets.rolling(L, min_periods=L).corr(mkt)
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
