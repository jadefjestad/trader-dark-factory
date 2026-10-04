"""Hypothesis (issue #50): residual momentum (the champion, validation Sharpe 0.88) and low volatility
(low_vol_tilt, validation 0.38) are weakly correlated factors. Ranking on the average of the two
percentile ranks picks steadier winners, lowering drawdown and raising validation Sharpe.

One change versus residual_vol_momentum: the ranking score is the mean of the residual-momentum
percentile rank and the low-60-day-volatility percentile rank.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class MomentumLowVolComposite(Strategy):
    name = "momentum_lowvol_composite"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        L, S = int(p["lookback"]), int(p["skip"])
        rets = c.pct_change()
        mkt = rets.mean(axis=1)
        beta = rets.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = rets - beta.mul(mkt, axis=0)
        win = resid.shift(S).rolling(L - S, min_periods=L - S)
        mom = (win.sum() / win.std()).rank(axis=1, pct=True)
        quiet = (-rets.rolling(int(p["vol_window"]), min_periods=int(p["vol_window"])).std()).rank(axis=1, pct=True)
        score = (mom + quiet) / 2
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
        return hold_between_rebalances(w, int(p["rebalance_every"]))
