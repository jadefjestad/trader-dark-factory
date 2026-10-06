"""Hypothesis: in Lou, Polk and Skouras (2019, "A tug of war"), the overnight and intraday legs of
momentum pull in opposite directions: stocks with high past overnight returns keep earning overnight,
while past intraday winners partly reverse. overnight_momentum (PR #115: validation Sharpe 0.84)
ranks on the overnight leg alone. Ranking instead on the spread, trailing 252-day overnight return
minus trailing 252-day intraday (open to close) return, should favour names bid at the open but sold
during the day and raise validation Sharpe.

One change versus overnight_momentum: the score subtracts cumulative intraday return.
Row t uses opens and closes up to bar t only.
"""
import numpy as np

from strategies.base import Strategy, equal_weight, hold_between_rebalances, rebalance_mask


class OvernightIntradaySpread(Strategy):
    name = "overnight_intraday_spread"
    lookback = 260
    params = {"window": 252, "top_n": 8, "rebalance_every": 21, "vol_target": 0.10, "vol_window": 60}

    def target_weights(self, md):
        p = self.params
        c, o = md.close, md.open
        rets = c.pct_change()
        win = int(p["window"])
        overnight = np.log(o / c.shift(1))
        intraday = np.log(c / o)
        score = (overnight - intraday).rolling(win, min_periods=win).sum()
        rank = score.rank(axis=1, ascending=False, method="first")
        n = int(p["top_n"])
        w = equal_weight((rank <= n) & score.notna(), slots=n)
        vw = int(p["vol_window"])
        keep = rebalance_mask(w.index, int(p["rebalance_every"]))
        for i in np.flatnonzero(keep):
            row = w.iloc[i]
            if row.sum() <= 0 or i < vw:
                continue
            basket = rets.iloc[i - vw + 1:i + 1].mul(row, axis=1).sum(axis=1, min_count=1)
            vol = float(basket.std()) * np.sqrt(252)
            if np.isfinite(vol) and vol > 0:
                w.iloc[i] = row * min(1.0, p["vol_target"] / vol)
        return hold_between_rebalances(w, int(p["rebalance_every"]))
