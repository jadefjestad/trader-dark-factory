"""Hypothesis (issue #31): momentum crashes cluster in credit stress (2008, 2020, 2022). When the US
Baa corporate spread (FRED BAA10Y) sits above its own one-year 80th percentile, halving the residual
momentum champion's exposure cuts drawdown without giving up much return, raising validation Sharpe.
The spread is lagged one bar, so a rebalance only sees values published by its close.

One change versus residual_vol_momentum: exposure is scaled by stress_exposure on high-spread rebalances.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class CreditStressResidualMomentum(Strategy):
    name = "credit_stress_residual"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    extra_data = ("macro",)
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60,
              "stress_quantile": 0.8, "stress_exposure": 0.5}

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
        hy = md.extra["macro"]["BAA10Y"]
        stressed = hy > hy.rolling(252, min_periods=252).quantile(min(float(p["stress_quantile"]), 0.99))
        vw = int(p["vol_window"])
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                row = row * min(1.0, p["vol_target"] / vol)
            w.iloc[i] = row * (float(p["stress_exposure"]) if stressed.iloc[i] else 1.0)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
