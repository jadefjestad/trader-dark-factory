"""Hypothesis (issue #27): PR #26 blended the champion residual_vol_momentum 50/50 with equal weight.
That steadied in-sample Sharpe (0.41 to 1.06) but failed the in-sample drawdown gate at 25.8%. A 30%
equal-weight share keeps most of the steadiness with drawdown under 25%.

One change versus residual_vol_momentum: 30% of capital goes to the equal-weight portfolio.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class BlendEqualWeight30Residual(Strategy):
    name = "blend_ew30_residual"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60,
              "ew_share": 0.3}

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
        live = c.notna()
        ew = live.astype(float).div(live.sum(axis=1).replace(0, 1), axis=0)
        s = float(p["ew_share"])
        return hold_between_rebalances(s * ew + (1 - s) * w, int(p["rebalance_every"]))
