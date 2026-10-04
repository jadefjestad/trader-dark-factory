"""Hypothesis: vol_target_momentum (PR #12, rejected) passed every gate except in-sample max drawdown,
25.2% against the 25% limit, with validation Sharpe 0.94. Lowering the volatility target from 12% to
10% scales drawdowns down by roughly a sixth, which should clear the gate while keeping validation
Sharpe above 0.9 (Sharpe is largely unchanged by leverage).

One change versus vol_target_momentum: vol_target 0.12 -> 0.10.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class VolTargetMomentum10(Strategy):
    name = "vol_target_momentum_10"
    lookback = 260
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        mom = c.shift(int(p["skip"])) / c.shift(int(p["lookback"])) - 1
        rank = mom.rank(axis=1, ascending=False)
        w = equal_weight((rank <= int(p["top_n"])) & mom.notna(), slots=int(p["top_n"]))
        rets = c.pct_change()
        win = int(p["vol_window"])
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < win:
                continue
            basket = rets.iloc[i - win + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
