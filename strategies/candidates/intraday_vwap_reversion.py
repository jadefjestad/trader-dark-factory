"""Hypothesis (Jade, 2026-10-05: more intraday activity): large caps that stretch well below their
session VWAP during the day tend to drift back toward it within the session, as liquidity providers
and VWAP-benchmarked execution lean against the move. Buy a stock on a 15-minute close at least 0.5%
under its session VWAP; sell when it closes back at or above VWAP. Up to 5 names at 10% each (50%
gross, so costs and drawdowns stay modest), flat every night.

Expected activity: a few round trips a day across the 25 names. One change versus the earlier
intraday tests (strong_open_continuation, opening_range_breakout): it fades moves instead of chasing
them, and it measures the move against VWAP rather than the open.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy


def _bar_no(index, minutes):
    """Bar number within the regular session from the clock (09:30 = 0), robust to partial history."""
    t = pd.DatetimeIndex(index)
    return np.asarray((t.hour * 60 + t.minute - 570) // minutes)


def _held(enter, leave, score, day_start, slots):
    """Hysteresis book: enter on `enter` (lowest score first while slots are free), leave on `leave`,
    empty at the start of every session."""
    n, k = enter.shape
    out = np.zeros((n, k), dtype=bool)
    cur = np.zeros(k, dtype=bool)
    for t in range(n):
        if day_start[t]:
            cur[:] = False
        cur &= ~leave[t]
        free = slots - int(cur.sum())
        if free > 0:
            cand = np.flatnonzero(enter[t] & ~cur)
            if len(cand):
                cur[cand[np.argsort(score[t, cand], kind="stable")][:free]] = True
        out[t] = cur
    return out


class IntradayVwapReversion(Strategy):
    name = "intraday_vwap_reversion"
    timeframe = "15Min"
    lookback = 60
    params = {"entry_gap": 0.005, "slots": 5, "weight": 0.10, "first_bar": 2, "last_entry_bar": 23}

    def target_weights(self, md):
        p = self.params
        c = md.close
        tp = (md.high + md.low + c) / 3
        v = md.volume.fillna(0.0)
        day = pd.Series(c.index.date, index=c.index)
        vwap = (tp * v).groupby(day.values).cumsum() / v.groupby(day.values).cumsum().replace(0, np.nan)
        gap = (c / vwap - 1).to_numpy()
        bar = _bar_no(c.index, 15)
        can_enter = ((bar >= int(p["first_bar"])) & (bar <= int(p["last_entry_bar"])))[:, None]
        with np.errstate(invalid="ignore"):
            enter = can_enter & (gap <= -float(p["entry_gap"]))
            leave = gap >= 0.0
        day_start = np.r_[True, day.values[1:] != day.values[:-1]]
        held = _held(enter, leave, np.nan_to_num(gap), day_start, int(p["slots"]))
        return pd.DataFrame(held * float(p["weight"]), index=c.index, columns=c.columns)
