"""Hypothesis (issue #47): momentum profits are earned on intraday (open-to-close) returns while
overnight returns tend to reverse (Lou, Polk & Skouras 2019, "A tug of war"). Computing the champion's
residual-momentum score from open-to-close returns only isolates the persistent part and raises
validation Sharpe.

One change versus residual_vol_momentum: the score uses close/open - 1 instead of close-to-close returns
(vol targeting still uses close-to-close returns).
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class IntradayResidualMomentum(Strategy):
    name = "intraday_residual_momentum"
    lookback = 520   # beta (252) + residual window (231) + skip (21) + margin
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c = md.close
        L, S = int(p["lookback"]), int(p["skip"])
        rets = c.pct_change()
        day = c / md.open - 1                      # open-to-close return of bar t, known at t's close
        mkt = day.mean(axis=1)
        beta = day.rolling(L, min_periods=L).cov(mkt).div(mkt.rolling(L, min_periods=L).var(), axis=0)
        resid = day - beta.mul(mkt, axis=0)
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
        return hold_between_rebalances(w, int(p["rebalance_every"]))
