import numpy as np
import pandas as pd

from strategies.base import Strategy


class GapDownReversal(Strategy):
    """Intraday (15Min): buy large caps that gap down hard versus the market, hold to the close.

    Overnight and intraday returns are negatively related across stocks (Lou, Polk and Skouras 2019;
    Branch and Ma 2012): stocks pushed down overnight by liquidity demand tend to recover during the
    session. At the close of the first 15-minute bar, buy every stock whose overnight gap
    (open / prior close - 1) is more than `min_gap` below the universe's average gap and that has not
    fallen further in the first bar, up to `max_names` at 15% each, and hold until the backtester
    flattens before the close. Cash otherwise, so it trades only on a minority of days.
    """
    name = "gap_down_reversal"
    timeframe = "15Min"
    lookback = 60            # two full sessions, so the prior close is always in the window
    params = {"min_gap": 0.015, "max_names": 6}

    def target_weights(self, md):
        o, c = md.open, md.close
        day = pd.Series(c.index.date, index=c.index)
        first = pd.Series((day != day.shift(1)).values, index=c.index)
        prev_close = c.shift(1).where(first, axis=0)
        gap = (o / prev_close - 1).where(first, axis=0)
        rel = gap.sub(gap.mean(axis=1), axis=0)
        held_up = c >= o                                         # first bar did not extend the drop
        pick = (rel < -self.params["min_gap"]) & held_up
        n = int(self.params["max_names"])
        worst = rel.where(pick).rank(axis=1, method="first") <= n
        w = (pick & worst).astype(float) * 0.15
        w = w.where(first, np.nan, axis=0)                       # decide on the first bar only
        return w.groupby(day.values).ffill().fillna(0.0)
