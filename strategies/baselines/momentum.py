from strategies.base import Strategy, equal_weight, hold_between_rebalances


class CrossSectionalMomentum(Strategy):
    """Own the top-N stocks by 12-1 month return, rebalanced monthly."""
    name = "cross_sectional_momentum"
    lookback = 260
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21}

    def target_weights(self, md):
        p = self.params
        c = md.close
        mom = c.shift(int(p["skip"])) / c.shift(int(p["lookback"])) - 1
        rank = mom.rank(axis=1, ascending=False)
        w = equal_weight((rank <= int(p["top_n"])) & mom.notna(), slots=int(p["top_n"]))
        return hold_between_rebalances(w, int(p["rebalance_every"]))
