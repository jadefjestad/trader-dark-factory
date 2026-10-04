"""Hypothesis (issue #5): the equal-weight champion's drawdowns come from broad bear markets. Holding
it only while more than half the universe trades above its 200-day average, and moving to cash the
day breadth drops below that (re-entering the day it recovers), cuts max drawdown below 25% in every
period at a Sharpe cost under 0.2.

One change versus strategies/baselines/buy_hold.py: the breadth regime switch.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy, rebalance_mask


class BreadthRegimeEqualWeight(Strategy):
    name = "breadth_regime_equal_weight"
    lookback = 260
    params = {"rebalance_every": 21, "trend": 200, "breadth": 0.5}

    def target_weights(self, md):
        p = self.params
        c = md.close
        live = c.notna()
        w = live.astype(float).div(live.sum(axis=1).replace(0, 1), axis=0)
        sma = c.rolling(int(p["trend"])).mean()
        breadth = (c > sma).sum(axis=1) / sma.notna().sum(axis=1).replace(0, np.nan)
        risk_on = (breadth > p["breadth"]).fillna(False)
        w = w.mul(risk_on.astype(float), axis=0)
        flip = risk_on.ne(risk_on.shift(1)).to_numpy()
        trade = rebalance_mask(w.index, int(p["rebalance_every"])) | flip
        return w.where(pd.Series(trade, index=w.index), other=np.nan, axis=0)
