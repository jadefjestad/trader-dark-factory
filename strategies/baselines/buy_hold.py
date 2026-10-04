from strategies.base import Strategy, hold_between_rebalances


class EqualWeightBuyHold(Strategy):
    name = "equal_weight_buy_hold"
    lookback = 30
    params = {"rebalance_every": 21}

    def target_weights(self, md):
        live = md.close.notna()
        w = live.astype(float).div(live.sum(axis=1).replace(0, 1), axis=0)
        return hold_between_rebalances(w, int(self.params["rebalance_every"]))
