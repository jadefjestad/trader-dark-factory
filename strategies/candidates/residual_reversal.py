"""Hypothesis: plain short-term reversal (baseline: buy the 5-day losers) earns little after costs
(validation 0.47) because much of a stock's recent loss is just the market or its beta moving.
Residual reversal (Blitz et al. 2013) ranks on the last 21 days of beta-adjusted residual returns,
scaled by their volatility, so it buys stocks that fell for stock-specific reasons, which tend to
revert. Buy the 8 lowest, 10% vol target, rebalanced weekly.

Beta is estimated over the prior 252 days against the equal-weight universe, as in the champion's
residual sleeve. Row t uses closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class ResidualReversal(Strategy):
    name = "residual_reversal"
    lookback = 340
    params = {"beta_window": 252, "window": 21, "top_n": 8, "rebalance_every": 5,
              "vol_target": 0.10, "vol_window": 60}

    def vol_scaled(self, picks, rets):
        p = self.params
        n = int(p["top_n"])
        w = equal_weight(picks, slots=n)
        vw = int(p["vol_window"])
        for i in np.flatnonzero(rebalance_mask(w.index, int(p["rebalance_every"]))):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"])).ffill().fillna(0.0)

    def target_weights(self, md):
        p = self.params
        rets = md.close.pct_change()
        B, W, n = int(p["beta_window"]), int(p["window"]), int(p["top_n"])
        mkt = rets.mean(axis=1)
        beta = rets.rolling(B, min_periods=B).cov(mkt).div(mkt.rolling(B, min_periods=B).var(), axis=0)
        resid = rets - beta.shift(W).mul(mkt, axis=0)
        win = resid.rolling(W, min_periods=W)
        score = win.sum() / win.std()
        rank = score.rank(axis=1, ascending=True, method="first")
        w = self.vol_scaled((rank <= n) & score.notna(), rets)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
