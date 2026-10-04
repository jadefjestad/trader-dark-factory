from strategies.base import Strategy, equal_weight, hold_between_rebalances


class ShortTermReversal(Strategy):
    """Own the N worst 5-day performers that are still above their 200-day SMA, weekly."""
    name = "short_term_reversal"
    lookback = 210
    params = {"window": 5, "bottom_n": 8, "trend": 200, "rebalance_every": 5}

    def target_weights(self, md):
        p = self.params
        c = md.close
        ret = c / c.shift(int(p["window"])) - 1
        uptrend = c > c.rolling(int(p["trend"])).mean()
        rank = ret.where(uptrend).rank(axis=1, ascending=True)
        w = equal_weight(rank <= int(p["bottom_n"]), slots=int(p["bottom_n"]))
        return hold_between_rebalances(w, int(p["rebalance_every"]))
