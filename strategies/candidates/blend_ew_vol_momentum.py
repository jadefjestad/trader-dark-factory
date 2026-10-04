"""Hypothesis: vol_target_momentum_10 (PR #19) passed every gate with validation Sharpe 0.94 and
max drawdown 21%, but did not beat the equal-weight champion on the combined validation + holdout
score. The two are only partly correlated (momentum holds 8 names at ~60% gross; equal weight holds all
25 fully invested), so a 50/50 blend of them should score above both on Sharpe while keeping
drawdown under the 25% gate.

One change versus vol_target_momentum_10: half the capital goes to the equal-weight portfolio.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class BlendEqualWeightVolMomentum(Strategy):
    name = "blend_ew_vol_momentum"
    lookback = 260
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10,
              "vol_window": 60, "ew_share": 0.5}

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
        live = c.notna()
        ew = live.astype(float).div(live.sum(axis=1).replace(0, 1), axis=0)
        s = float(p["ew_share"])
        return hold_between_rebalances(s * ew + (1 - s) * w, int(p["rebalance_every"]))
