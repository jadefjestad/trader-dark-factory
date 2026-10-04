import pandas as pd

from strategies.base import Strategy


class EqualWeightBuyHold(Strategy):
    name = "equal_weight_buy_hold"
    lookback = 1
    params = {"rebalance_every": 21}

    def target_weights(self, md):
        live = md.close.notna()
        w = live.astype(float).div(live.sum(axis=1).replace(0, 1), axis=0)
        keep = pd.Series(range(len(w)), index=w.index) % self.params["rebalance_every"] == 0
        return w.where(keep, other=float("nan")).ffill().fillna(0.0)
