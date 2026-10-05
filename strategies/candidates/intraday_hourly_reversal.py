"""Hypothesis (Jade, 2026-10-05: more intraday activity): over horizons of an hour or two, the large caps
that fell most relative to the others tend to recover part of the gap later in the same session
(intraday cross-sectional reversal, as liquidity demand from big orders is absorbed; Heston, Korajczyk
and Sadka 2010 find return patterns at half-hour horizons). Every 6 bars (90 minutes: decisions on the
10:45, 12:15 and 13:45 closes) hold the 5 stocks with the worst return over the previous 6 bars, at 10%
each (50% gross). Flat before the first decision and every night.

The daily reversal family failed on this universe (PR #42); the intraday horizon is the one change.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy


def _bar_no(index, minutes):
    t = pd.DatetimeIndex(index)
    return np.asarray((t.hour * 60 + t.minute - 570) // minutes)


class IntradayHourlyReversal(Strategy):
    name = "intraday_hourly_reversal"
    timeframe = "15Min"
    lookback = 40
    params = {"window": 6, "names": 5, "weight": 0.10}

    def target_weights(self, md):
        p = self.params
        c = md.close
        k = int(p["window"])
        bar = _bar_no(c.index, 15)
        ret = (c / c.shift(k) - 1).to_numpy()
        day = c.index.date
        same_day = np.r_[np.zeros(k, dtype=bool), day[k:] == day[:-k]] if len(day) > k else np.zeros(len(day), bool)
        decide = (bar >= k) & (bar % k == 0) & same_day
        rank = pd.DataFrame(np.where(np.isfinite(ret), ret, np.inf), index=c.index).rank(axis=1, method="first")
        losers = (rank.to_numpy() <= int(p["names"])) & np.isfinite(ret)
        w = np.where(losers, float(p["weight"]), 0.0)
        w[~decide & (bar >= k)] = np.nan     # hold between decisions
        w[bar < k] = 0.0                      # flat until the first decision of the session
        return pd.DataFrame(w, index=c.index, columns=c.columns)
