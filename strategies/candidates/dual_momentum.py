"""Hypothesis (issue #16): cross-sectional momentum's drawdowns come from holding "winners" that are
themselves falling. Keeping the top-8 by 12-1 return but holding each name only while its own 12-1
return is positive (its slot sits in cash otherwise) keeps momentum's Sharpe (0.91 validation) and
cuts in-sample and holdout drawdown below the 25% gate.

One change versus strategies/baselines/momentum.py: the absolute-momentum filter per slot.
"""
from strategies.base import Strategy, equal_weight, hold_between_rebalances


class DualMomentum(Strategy):
    name = "dual_momentum"
    lookback = 260
    params = {"lookback": 252, "skip": 21, "top_n": 8, "rebalance_every": 21}

    def target_weights(self, md):
        p = self.params
        c = md.close
        mom = c.shift(int(p["skip"])) / c.shift(int(p["lookback"])) - 1
        rank = mom.rank(axis=1, ascending=False)
        w = equal_weight((rank <= int(p["top_n"])) & (mom > 0), slots=int(p["top_n"]))
        return hold_between_rebalances(w, int(p["rebalance_every"]))
