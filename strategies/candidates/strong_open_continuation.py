import numpy as np
import pandas as pd

from strategies.base import Strategy


class StrongOpenContinuation(Strategy):
    """Intraday (15Min): on days the universe opens strongly, ride the strongest names into the close.

    Intraday momentum (Gao, Han, Li and Zhou, 2018): the market's return from the prior close through
    the first half hour predicts the rest of the day. Round trips cost ~35 bps here, so the strategy
    trades only on strong opens: when the equal-weight universe is up more than `min_open_move` from
    the prior close by the end of the first `open_bars` bars, it buys the `names` stocks with the
    biggest moves at that point and holds them until the backtester flattens before the close.
    Every other day it stays in cash.
    """
    name = "strong_open_continuation"
    timeframe = "15Min"
    lookback = 60            # two full sessions, so the prior close is always in the window
    params = {"open_bars": 4, "min_open_move": 0.005, "names": 6}

    def target_weights(self, md):
        c = md.close
        day = pd.Series(c.index.date, index=c.index)
        first_of_day = day != day.shift(1)
        prev_close = c.shift(1).where(first_of_day).groupby(day.values).transform("first")
        bar_no = day.groupby(day.values).cumcount()
        k = int(self.params["open_bars"])

        move = c / prev_close - 1                                   # move since the prior close, as of each bar
        at_signal = (bar_no == k - 1).values                        # the bar that closes the opening window
        market = move.mean(axis=1)
        strong = (market > self.params["min_open_move"]) & at_signal
        n = int(self.params["names"])
        top = move.rank(axis=1, ascending=False, method="first") <= n
        pick = (top & (move > 0)).astype(float).where(strong, 0.0)

        # carry the signal-bar pick through the rest of that session; earlier bars stay flat
        keep = pd.Series(at_signal | (bar_no.values < k - 1), index=c.index)
        pick = pick.where(keep, np.nan, axis=0)
        pick = pick.groupby(day.values).ffill().fillna(0.0)
        return pick / max(n, 1) * 0.9
