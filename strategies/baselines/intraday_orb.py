import pandas as pd

from strategies.base import Strategy


class OpeningRangeBreakout(Strategy):
    """Intraday: go long a stock once it closes above its opening-range high; flat by the close."""
    name = "opening_range_breakout"
    timeframe = "15Min"
    lookback = 30
    params = {"range_bars": 2, "max_names": 8}

    def target_weights(self, md):
        c, h = md.close, md.high
        day = pd.Series(c.index.date, index=c.index)
        bar_no = day.groupby(day).cumcount()
        in_range = bar_no < int(self.params["range_bars"])
        range_high = h[in_range].groupby(day[in_range]).max()          # one row per session
        rh = range_high.reindex(day.values).set_axis(c.index)
        rh[in_range] = float("nan")                                     # no signal inside the range
        broke = (c > rh).astype(int)
        held = broke.groupby(day.values).cummax().astype(bool)          # stay in for the session
        n = held.sum(axis=1).clip(lower=int(self.params["max_names"]))
        return held.astype(float).div(n, axis=0)
