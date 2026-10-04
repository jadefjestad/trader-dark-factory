"""Hypothesis (issue #51): absolute (time-series) trend gives momentum a built-in crash brake
(Moskowitz, Ooi & Pedersen 2012). Holding every stock whose 12-1 month return is positive, sized by
inverse 60-day volatility and scaled to a 10% portfolio vol target, earns validation Sharpe above 0.3
with shallower drawdowns than cross-sectional picks.

A new base signal: no cross-sectional ranking; the book shrinks toward cash when few stocks trend up.
Monthly, calendar-anchored rebalances; each name capped at the 15% position limit.
"""
import numpy as np

from strategies.base import Strategy, hold_between_rebalances, rebalance_mask


class TimeSeriesTrendInvVol(Strategy):
    name = "ts_trend_invvol"
    lookback = 320
    params = {"lookback": 252, "skip": 21, "vol_window": 60, "vol_target": 0.10, "rebalance_every": 21}

    def target_weights(self, md):
        p = self.params
        c = md.close
        L, S, vw = int(p["lookback"]), int(p["skip"]), int(p["vol_window"])
        rets = c.pct_change()
        trend = c.shift(S) / c.shift(L) - 1
        vol = rets.rolling(vw, min_periods=vw).std()
        inv = (1.0 / vol.where(vol > 0)).where(trend > 0, 0.0).fillna(0.0)
        w = inv.div(inv.sum(axis=1).where(lambda s: s > 0), axis=0).fillna(0.0)
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            bvol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(bvol) and bvol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / bvol)
        return hold_between_rebalances(w.clip(upper=0.15), int(p["rebalance_every"]))
