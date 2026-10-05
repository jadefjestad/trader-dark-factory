"""Hypothesis (Jade, 2026-10-05: more intraday activity): a large cap that is up on the session and holding
well above its session VWAP is being bought steadily (institutional VWAP programs work through the day),
so the move tends to continue for a while. Buy a stock on a 15-minute close at least 0.4% above its
session VWAP while it is also above the session's opening price; sell when it closes back under VWAP.
Up to 5 names at 10% each (50% gross), strongest first, flat every night.

One change versus intraday_vwap_reversion: it follows the stretch from VWAP instead of fading it, so the
two funds make a matched pair. Versus strong_open_continuation (PR #83): entries can come at any time of
day and the exit is VWAP, not the close.
"""
import numpy as np
import pandas as pd

from strategies.base import Strategy


def _bar_no(index, minutes):
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


class IntradayVwapTrend(Strategy):
    name = "intraday_vwap_trend"
    timeframe = "15Min"
    lookback = 60
    params = {"entry_gap": 0.004, "slots": 5, "weight": 0.10, "first_bar": 2, "last_entry_bar": 23}

    def target_weights(self, md):
        p = self.params
        c = md.close
        tp = (md.high + md.low + c) / 3
        v = md.volume.fillna(0.0)
        day = pd.Series(c.index.date, index=c.index)
        vwap = (tp * v).groupby(day.values).cumsum() / v.groupby(day.values).cumsum().replace(0, np.nan)
        session_open = md.open.groupby(day.values).transform("first")
        gap = (c / vwap - 1).to_numpy()
        up = (c > session_open).to_numpy()
        bar = _bar_no(c.index, 15)
        can_enter = ((bar >= int(p["first_bar"])) & (bar <= int(p["last_entry_bar"])))[:, None]
        with np.errstate(invalid="ignore"):
            enter = can_enter & up & (gap >= float(p["entry_gap"]))
            leave = gap < 0.0
        day_start = np.r_[True, day.values[1:] != day.values[:-1]]
        held = _held(enter, leave, -np.nan_to_num(gap), day_start, int(p["slots"]))
        return pd.DataFrame(held * float(p["weight"]), index=c.index, columns=c.columns)
