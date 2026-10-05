"""Hypothesis (Jade, 2026-10-05: more intraday activity): short, sharp 15-minute pullbacks in large caps
that are trending up over the last session tend to bounce within hours (short-horizon reversal inside
a trend, the classic RSI-pullback setup moved to 15-minute bars). Buy when a 6-bar RSI drops under 25
while the close is above its 26-bar (one session) average; sell when the RSI recovers above 55. Up to
5 names at 10% each (50% gross), flat every night.

RSI uses plain rolling means (Cutler's RSI), not Wilder's smoothing, so a signal depends only on the
last few bars and the live executor's short history reproduces it exactly. One change versus
intraday_vwap_reversion: the stretch is measured by recent bar-to-bar momentum, with a trend filter.
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


class IntradayRsiPullback(Strategy):
    name = "intraday_rsi_pullback"
    timeframe = "15Min"
    lookback = 80
    params = {"rsi_bars": 6, "trend_bars": 26, "entry_rsi": 25.0, "exit_rsi": 55.0, "slots": 5, "weight": 0.10,
              "first_bar": 1, "last_entry_bar": 23}

    def target_weights(self, md):
        p = self.params
        c = md.close
        n = int(p["rsi_bars"])
        d = c.diff()
        gain = d.clip(lower=0).rolling(n).mean()
        loss = (-d).clip(lower=0).rolling(n).mean()
        rsi = (100 * gain / (gain + loss).replace(0, np.nan)).to_numpy()
        trend = (c > c.rolling(int(p["trend_bars"])).mean()).to_numpy()
        bar = _bar_no(c.index, 15)
        can_enter = ((bar >= int(p["first_bar"])) & (bar <= int(p["last_entry_bar"])))[:, None]
        with np.errstate(invalid="ignore"):
            enter = can_enter & trend & (rsi < float(p["entry_rsi"]))
            leave = rsi > float(p["exit_rsi"])
        day = c.index.date
        day_start = np.r_[True, day[1:] != day[:-1]]
        held = _held(enter, leave, np.nan_to_num(rsi, nan=100.0), day_start, int(p["slots"]))
        return pd.DataFrame(held * float(p["weight"]), index=c.index, columns=c.columns)
